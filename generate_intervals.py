import pandas as pd
import numpy as np
import os
from calendar import monthrange
from rewdp_templates import get_template
from tqdm import tqdm

def generate_ar1_noise(n, rho=0.7, sigma=0.02, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    noise = np.zeros(n)
    noise[0] = rng.normal(0, sigma)
    for i in range(1, n):
        noise[i] = rho * noise[i-1] + rng.normal(0, sigma)
    return noise

def apply_confounders(day_shape, is_summer, rng):
    """Applies AC cycling and morning geyser spikes."""
    shape = day_shape.copy()
    
    # 1. AC compressor cycling (summer only)
    if is_summer:
        # Duty cycle: e.g. on for 3 intervals, off for 1. 
        # Modulate the shape by 0.7 to 1.3
        phase = rng.integers(0, 4)
        for i in range(96):
            if (i + phase) % 4 == 0:
                shape[i] *= 0.7  # compressor off
            else:
                shape[i] *= 1.2  # compressor on
                
    # 2. Water heater/geyser spike (mostly morning 6 AM - 8 AM)
    if rng.random() < 0.3:  # 30% chance per day
        spike_start = rng.integers(24, 32) # 6 AM to 8 AM
        spike_len = rng.integers(2, 5) # 30 to 60 mins
        spike_mag = rng.uniform(2.0, 4.0)
        shape[spike_start : spike_start + spike_len] *= spike_mag
        
    return shape

def build_interval_data(
    ami_ids_path='ami_consumer_ids.csv',
    consumers_path='data/consumers.csv',
    readings_path='data/monthly_readings.csv',
    pmt_path='data/pmt_monthly.csv',
    output_path='interval_readings.csv',
    chunk_size=500
):
    print("Loading data for interval generation...")
    ami_ids = pd.read_csv(ami_ids_path)['consumer_id'].values
    
    # We only process AMI consumers to save memory/time
    readings = pd.read_csv(readings_path)
    readings = readings[readings['consumer_id'].isin(ami_ids)].copy()
    
    consumers = pd.read_csv(consumers_path)
    consumers = consumers[consumers['consumer_id'].isin(ami_ids)][['consumer_id', 'is_registered_prosumer', 'sanctioned_load_kw']]
    
    pmts = pd.read_csv(pmt_path)[['pmt_id', 'month', 'avg_temp_c']]
    # We need PMT temp, so get pmt_id for each consumer
    cons_pmt = pd.read_csv(consumers_path)[['consumer_id', 'pmt_id']]
    readings = readings.merge(cons_pmt, on='consumer_id', how='left')
    readings = readings.merge(pmts, on=['pmt_id', 'month'], how='left')
    readings = readings.merge(consumers, on='consumer_id', how='left')
    
    readings['month'] = pd.to_datetime(readings['month'])
    
    rng = np.random.default_rng(42)
    
    out_file = open(output_path, 'w')
    out_file.write("consumer_id,timestamp,interval_kwh\n")
    
    print(f"Generating 15-minute intervals for {len(ami_ids)} consumers...")
    
    # Process grouped by consumer to maintain state if needed
    for consumer_id, group in tqdm(readings.groupby('consumer_id')):
        archetype = group['theft_type'].iloc[0]
        is_prosumer = group['is_registered_prosumer'].iloc[0]
        sanctioned_load = group['sanctioned_load_kw'].iloc[0]
        
        consumer_rows = []
        
        for _, row in group.iterrows():
            month_dt = row['month']
            billed_kwh = float(row['billed_units_kwh'])
            temp = row['avg_temp_c']
            
            # Use 28C as summer threshold for Pakistan
            season = 'summer' if temp > 28 else 'winter'
            is_summer = (season == 'summer')
            
            days_in_month = monthrange(month_dt.year, month_dt.month)[1]
            n_intervals = days_in_month * 96
            
            month_shape = np.zeros(n_intervals)
            month_mask = np.ones(n_intervals)
            
            timestamps = pd.date_range(start=month_dt, periods=n_intervals, freq='15min')
            
            for d in range(days_in_month):
                day_dt = month_dt + pd.Timedelta(days=d)
                day_type = 'weekend' if day_dt.weekday() >= 5 else 'weekday'
                
                # 1. Base template
                t_d = get_template(sanctioned_load, season, day_type, rng)
                
                # 2. Confounders
                t_d = apply_confounders(t_d, is_summer, rng)
                
                # 3. Theft / Prosumer Mask logic for this day
                d_mask = np.ones(96)
                
                if is_prosumer:
                    # Midday solar duck curve (10 AM to 3 PM -> idx 40 to 60)
                    # Significant generation reduces grid draw to near zero
                    d_mask[40:61] = rng.uniform(0.05, 0.3, size=21)
                    
                if archetype == 'peak_hour_shaver':
                    # Shave on ~50% of days
                    if rng.random() < 0.5:
                        # 7 PM to 9 PM is idx 76 to 84. Add jitter.
                        jitter_start = rng.integers(-2, 3)
                        jitter_end = rng.integers(-2, 3)
                        start_idx = max(0, 76 + jitter_start)
                        end_idx = min(96, 84 + jitter_end)
                        d_mask[start_idx:end_idx] = rng.uniform(0.01, 0.1, size=(end_idx - start_idx))
                        
                elif archetype == 'nighttime_ac' and is_summer:
                    # 11 PM to 5 AM -> idx 92-96 and 0-20
                    if rng.random() < 0.7:
                        d_mask[92:96] = rng.uniform(0.1, 0.3, size=4)
                        d_mask[0:21] = rng.uniform(0.1, 0.3, size=21)
                
                idx_start = d * 96
                idx_end = (d + 1) * 96
                month_shape[idx_start:idx_end] = t_d
                month_mask[idx_start:idx_end] = d_mask
                
            # AR(1) noise across the whole month
            noise = generate_ar1_noise(n_intervals, rho=0.7, sigma=0.05, rng=rng)
            
            final_shape = month_shape * month_mask
            final_shape += noise
            final_shape = np.clip(final_shape, 0.001, None)
            
            # Scale to exactly match Track 1 billed_kwh
            if np.sum(final_shape) > 0 and billed_kwh > 0:
                final_kwh = (final_shape / np.sum(final_shape)) * billed_kwh
            else:
                final_kwh = np.zeros(n_intervals)
                
            # Missing interval injection (~1.5%)
            drop_mask = rng.random(n_intervals) < 0.015
            
            df_month = pd.DataFrame({
                'consumer_id': consumer_id,
                'timestamp': timestamps,
                'interval_kwh': np.where(drop_mask, np.nan, np.round(final_kwh, 4))
            })
            consumer_rows.append(df_month)
            
        # Write consumer by consumer to avoid massive memory explosion
        pd.concat(consumer_rows).to_csv(out_file, header=False, index=False, na_rep='')

        
    out_file.close()
    print(f"Interval data written to {output_path}.")

if __name__ == '__main__':
    build_interval_data()
