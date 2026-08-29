import pandas as pd
import numpy as np
import os

def select_ami_population(
    consumers_path='data/consumers.csv',
    monthly_readings_path='data/monthly_readings.csv',
    output_ami_ids='ami_consumer_ids.csv',
    n_samples=2000,
    random_state=42
):
    """
    Selects a pilot subset of consumers for the Track 2 AMI rollout.
    Filters to residential consumers whose behavior is compatible with smart meter detection.
    """
    print("Loading consumer and billing data...")
    consumers_df = pd.read_csv(consumers_path)
    readings_df = pd.read_csv(monthly_readings_path, usecols=['consumer_id', 'theft_type']).drop_duplicates('consumer_id')
    
    # Join theft_type back to consumers to filter
    df = consumers_df.merge(readings_df, on='consumer_id', how='left')
    
    # The architecture doc specifies these are compatible with AMI detection
    # 'none' covers standard, solar_prosumer, seasonal_traveler, etc.
    ami_compatible_types = [
        'none', 
        'kunda', 
        'fixed_shunt', 
        'peak_hour_shaver', 
        'nighttime_ac'
    ]
    
    # Filter: Residential AND compatible archetype
    eligible_mask = (df['consumer_type'] == 'residential') & (df['theft_type'].isin(ami_compatible_types))
    eligible_consumers = df[eligible_mask].copy()
    
    print(f"Found {len(eligible_consumers)} eligible residential consumers.")
    
    n_select = min(n_samples, len(eligible_consumers))
    
    # Sample the subset
    rng = np.random.default_rng(random_state)
    selected_indices = rng.choice(eligible_consumers.index, size=n_select, replace=False)
    selected_consumers = eligible_consumers.loc[selected_indices, 'consumer_id'].values
    
    # Update the main consumers.csv with the has_ami flag
    consumers_df['has_ami'] = False
    consumers_df.loc[consumers_df['consumer_id'].isin(selected_consumers), 'has_ami'] = True
    
    # Save back to CSVs
    consumers_df.to_csv(consumers_path, index=False)
    
    ami_ids_df = pd.DataFrame({'consumer_id': selected_consumers})
    ami_ids_df.to_csv(output_ami_ids, index=False)
    
    print(f"Selected {n_select} consumers for Track 2 (AMI pilot).")
    print(f"Updated {consumers_path} with 'has_ami' flag.")
    print(f"Saved {output_ami_ids}.")

if __name__ == '__main__':
    select_ami_population()
