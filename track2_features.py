import pandas as pd
import numpy as np

def aggregate_interval_features(interval_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates 15-minute interval data back into one row per (consumer_id, month)
    matching Track 1's granularity. Computes AMI-specific load curve features.
    """
    df = interval_df.copy()
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date
    # Set 'month' to the first of the month to match Track 1 format
    df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()
    
    # Define time windows
    # NEPRA peak roughly 6 PM - 10 PM (18:00 - 22:00)
    df['is_peak'] = df['hour'].isin([18, 19, 20, 21])
    # Off-peak 11 PM - 6 AM (23:00 - 06:00)
    df['is_offpeak'] = df['hour'].isin([23, 0, 1, 2, 3, 4, 5])
    # Midday 10 AM - 3 PM (10:00 - 15:00)
    df['is_midday'] = df['hour'].isin([10, 11, 12, 13, 14])
    # Nighttime 11 PM - 5 AM (23:00 - 05:00)
    df['is_night'] = df['hour'].isin([23, 0, 1, 2, 3, 4])
    
    # Flatline threshold
    FLATLINE_THRESHOLD = 0.05
    
    # Group by (consumer_id, month) for monthly features
    grouped = df.groupby(['consumer_id', 'month'])
    
    features = []
    for (consumer, month), group in grouped:
        # 1. peak_offpeak_ratio
        mean_peak = group[group['is_peak']]['interval_kwh'].mean()
        mean_offpeak = group[group['is_offpeak']]['interval_kwh'].mean()
        # guard against divide-by-zero
        if pd.isna(mean_peak): mean_peak = 0
        if pd.isna(mean_offpeak) or mean_offpeak == 0:
            peak_offpeak_ratio = 1.0 if mean_peak == 0 else 10.0 # arbitrary high cap
        else:
            peak_offpeak_ratio = mean_peak / mean_offpeak
            
        # 2. daily_load_factor (mean/max per day)
        daily = group.groupby('date')['interval_kwh'].agg(['mean', 'max'])
        # if max is 0, load factor is 0
        daily['load_factor'] = np.where(daily['max'] > 0, daily['mean'] / daily['max'], 0)
        daily_load_factor = daily['load_factor'].mean()
        
        # 3. flatline_fraction
        flatline_count = (group['interval_kwh'] < FLATLINE_THRESHOLD).sum()
        total_count = len(group['interval_kwh'].dropna())
        flatline_fraction = flatline_count / total_count if total_count > 0 else 0
        
        # 4. peak_window_flatline_fraction
        peak_group = group[group['is_peak']]
        peak_flat_count = (peak_group['interval_kwh'] < FLATLINE_THRESHOLD).sum()
        peak_total_count = len(peak_group['interval_kwh'].dropna())
        peak_window_flatline_fraction = peak_flat_count / peak_total_count if peak_total_count > 0 else 0
        
        # 5. midday_dip_index
        mean_midday = group[group['is_midday']]['interval_kwh'].mean()
        mean_daily = group['interval_kwh'].mean()
        if pd.isna(mean_midday): mean_midday = 0
        if pd.isna(mean_daily) or mean_daily == 0:
            midday_dip_index = 1.0
        else:
            midday_dip_index = mean_midday / mean_daily
            
        # 6. nighttime average (used for drop index later)
        night_mean = group[group['is_night']]['interval_kwh'].mean()
        if pd.isna(night_mean): night_mean = 0
        
        # 7. tariff_boundary_alignment_score (simplified heuristic)
        # Look at the derivative (diff) of usage. If max drop happens exactly at 6:00 PM or 7:00 PM
        diffs = group.sort_values('timestamp')['interval_kwh'].diff()
        min_diff = diffs.min() # largest drop
        alignment_score = 60.0 # default high score (low alignment)
        if min_diff < -0.1: # substantial drop
            drop_idx = diffs.idxmin()
            drop_time = group.loc[drop_idx, 'timestamp']
            # Distance in minutes from 18:00 or 19:00
            dist_18 = abs(drop_time.hour * 60 + drop_time.minute - (18 * 60))
            dist_19 = abs(drop_time.hour * 60 + drop_time.minute - (19 * 60))
            alignment_score = min(dist_18, dist_19)
            
        features.append({
            'consumer_id': consumer,
            'month': month,
            'peak_offpeak_ratio': peak_offpeak_ratio,
            'daily_load_factor': daily_load_factor,
            'flatline_fraction': flatline_fraction,
            'peak_window_flatline_fraction': peak_window_flatline_fraction,
            'midday_dip_index': midday_dip_index,
            'night_mean_raw': night_mean,
            'tariff_boundary_alignment_score': alignment_score
        })
        
    res_df = pd.DataFrame(features)
    
    # 8. nighttime_drop_index
    # actual overnight vs consumer's own historical average
    res_df['avg_night'] = res_df.groupby('consumer_id')['night_mean_raw'].transform('mean')
    res_df['nighttime_drop_index'] = np.where(res_df['avg_night'] > 0, res_df['night_mean_raw'] / res_df['avg_night'], 1.0)
    res_df.drop(columns=['night_mean_raw', 'avg_night'], inplace=True)
    
    return res_df
