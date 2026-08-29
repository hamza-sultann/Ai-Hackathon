import pandas as pd
import numpy as np
import gc
from track2_features import aggregate_interval_features
from tqdm import tqdm

def process_in_chunks(input_path='interval_readings.csv', output_path='track2_features.csv'):
    print(f"Reading {input_path} in chunks to extract features...")
    
    # We need to process by consumer. 
    # Since generate_intervals.py wrote consumer by consumer, all rows for a consumer are contiguous.
    # We can chunk by consumer_id.
    
    # First get list of all consumers in file to set up progress bar
    # Since it's large, we won't read it all. We'll just iterate chunks and group.
    
    chunksize = 1_000_000 # 1 million rows per chunk
    
    buffer_df = pd.DataFrame()
    results = []
    
    for chunk in tqdm(pd.read_csv(input_path, chunksize=chunksize)):
        # Append to buffer
        buffer_df = pd.concat([buffer_df, chunk])
        
        # Find the last consumer_id in the buffer. It might be cut off.
        last_consumer = buffer_df['consumer_id'].iloc[-1]
        
        # Extract all consumers EXCEPT the last one (which might be incomplete)
        ready_mask = buffer_df['consumer_id'] != last_consumer
        ready_df = buffer_df[ready_mask]
        
        if not ready_df.empty:
            features = aggregate_interval_features(ready_df)
            results.append(features)
            
            # Keep only the incomplete consumer in the buffer
            buffer_df = buffer_df[~ready_mask].copy()
            
        gc.collect()
        
    # Process whatever is left in the buffer (the very last consumer)
    if not buffer_df.empty:
        features = aggregate_interval_features(buffer_df)
        results.append(features)
        
    final_df = pd.concat(results, ignore_index=True)
    
    print(f"Computed features for {len(final_df)} consumer-months.")
    final_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == '__main__':
    process_in_chunks()
