"""
Track 2 — Feature Engineering (1-Hour Interval → Monthly Features)

Aggregates 1-hour interval data back into one row per (consumer_id, month)
matching Track 1's grain, so the features merge directly into the existing
XGBoost pipeline without architectural changes.

All features are RATIOS or FRACTIONS — they capture the *shape* of the load
curve, making them invariant to absolute consumption levels.
"""

import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════
# HOUR-WINDOW DEFINITIONS (NEPRA Pakistan TOU)
# ═══════════════════════════════════════════════════════════════════════════

PEAK_HOURS = {18, 19, 20, 21}            # 6 PM – 10 PM
OFFPEAK_HOURS = {23, 0, 1, 2, 3, 4, 5}  # 11 PM – 6 AM
MIDDAY_HOURS = {10, 11, 12, 13, 14}      # 10 AM – 3 PM
NIGHT_HOURS = {23, 0, 1, 2, 3, 4}        # 11 PM – 5 AM

# Flatline threshold: a 1-hour reading below this (kWh) is "near-zero"
# For a typical 200 kWh/month consumer: avg hourly ≈ 0.28 kWh
# 0.05 kWh = ~18% of average → catches genuine meter bypass
FLATLINE_THRESHOLD = 0.05


# ═══════════════════════════════════════════════════════════════════════════
# FEATURE COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════

def aggregate_interval_features(interval_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates 1-hour interval data into one row per (consumer_id, month).

    Features produced:
      peak_offpeak_ratio           — mean peak / mean off-peak load
      daily_load_factor            — monthly avg of daily (mean / max)
      flatline_fraction            — fraction of ALL hours below threshold
      peak_window_flatline_fraction — fraction of PEAK hours below threshold
      midday_dip_index             — midday load / overall daily mean
      nighttime_drop_index         — this month's night load / consumer's
                                     historical average night load
      tariff_boundary_alignment_score — minutes from largest load drop to
                                        official tariff boundary

    Parameters
    ----------
    interval_df : DataFrame with columns [consumer_id, timestamp, interval_kwh]

    Returns
    -------
    DataFrame with columns [consumer_id, month, <7 features>]
    """
    df = interval_df.copy()

    # Ensure datetime
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date
    df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()

    # Pre-compute boolean masks
    df['is_peak'] = df['hour'].isin(PEAK_HOURS)
    df['is_offpeak'] = df['hour'].isin(OFFPEAK_HOURS)
    df['is_midday'] = df['hour'].isin(MIDDAY_HOURS)
    df['is_night'] = df['hour'].isin(NIGHT_HOURS)

    # ── Per (consumer, month) aggregation ────────────────────────────────
    grouped = df.groupby(['consumer_id', 'month'])
    records = []

    for (consumer, month), grp in grouped:
        kwh = grp['interval_kwh']
        valid_count = kwh.notna().sum()
        if valid_count == 0:
            continue

        # 1. peak_offpeak_ratio
        mean_peak = grp.loc[grp['is_peak'], 'interval_kwh'].mean()
        mean_offpeak = grp.loc[grp['is_offpeak'], 'interval_kwh'].mean()
        if pd.isna(mean_peak):
            mean_peak = 0.0
        if pd.isna(mean_offpeak) or mean_offpeak == 0:
            peak_offpeak_ratio = 10.0 if mean_peak > 0 else 1.0
        else:
            peak_offpeak_ratio = mean_peak / mean_offpeak

        # 2. daily_load_factor (mean/max per day, averaged)
        daily_stats = grp.groupby('date')['interval_kwh'].agg(['mean', 'max'])
        daily_stats['lf'] = np.where(
            daily_stats['max'] > 0,
            daily_stats['mean'] / daily_stats['max'],
            0.0
        )
        daily_load_factor = daily_stats['lf'].mean()

        # 3. flatline_fraction (all hours)
        flat_count = (kwh < FLATLINE_THRESHOLD).sum()
        flatline_fraction = flat_count / valid_count

        # 4. peak_window_flatline_fraction
        peak_vals = grp.loc[grp['is_peak'], 'interval_kwh']
        peak_valid = peak_vals.notna().sum()
        if peak_valid > 0:
            peak_flat = (peak_vals < FLATLINE_THRESHOLD).sum()
            peak_window_flatline_fraction = peak_flat / peak_valid
        else:
            peak_window_flatline_fraction = 0.0

        # 5. midday_dip_index (midday mean / overall mean)
        mean_midday = grp.loc[grp['is_midday'], 'interval_kwh'].mean()
        mean_all = kwh.mean()
        if pd.isna(mean_midday):
            mean_midday = 0.0
        if pd.isna(mean_all) or mean_all == 0:
            midday_dip_index = 1.0
        else:
            midday_dip_index = mean_midday / mean_all

        # 6. night_mean_raw (used for nighttime_drop_index later)
        night_mean = grp.loc[grp['is_night'], 'interval_kwh'].mean()
        if pd.isna(night_mean):
            night_mean = 0.0

        # 7. tariff_boundary_alignment_score
        sorted_grp = grp.sort_values('timestamp')
        diffs = sorted_grp['interval_kwh'].diff()
        alignment_score = 60.0  # default: high = no suspicious alignment
        min_diff = diffs.min()
        if not pd.isna(min_diff) and min_diff < -0.1:
            drop_idx = diffs.idxmin()
            drop_ts = sorted_grp.loc[drop_idx, 'timestamp']
            drop_minutes = drop_ts.hour * 60 + drop_ts.minute
            # Distance to official tariff boundaries (18:00 and 22:00)
            dist_18 = abs(drop_minutes - 18 * 60)
            dist_22 = abs(drop_minutes - 22 * 60)
            alignment_score = float(min(dist_18, dist_22))

        records.append({
            'consumer_id': consumer,
            'month': month,
            'peak_offpeak_ratio': peak_offpeak_ratio,
            'daily_load_factor': daily_load_factor,
            'flatline_fraction': flatline_fraction,
            'peak_window_flatline_fraction': peak_window_flatline_fraction,
            'midday_dip_index': midday_dip_index,
            'night_mean_raw': night_mean,
            'tariff_boundary_alignment_score': alignment_score,
        })

    result = pd.DataFrame(records)

    if result.empty:
        return result

    # ── nighttime_drop_index (relative to consumer's own history) ────────
    result['avg_night'] = (result.groupby('consumer_id')['night_mean_raw']
                           .transform('mean'))
    result['nighttime_drop_index'] = np.where(
        result['avg_night'] > 0,
        result['night_mean_raw'] / result['avg_night'],
        1.0
    )
    result.drop(columns=['night_mean_raw', 'avg_night'], inplace=True)

    return result
