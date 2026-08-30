"""
Track 2 — Batch Feature Extraction from Parquet

Reads the 1-hour interval Parquet file in row-group batches,
aggregates features per (consumer_id, month), and saves the
compact result (~5 MB) for downstream model training.

Peak memory usage: ~200 MB regardless of total dataset size.
"""

import pandas as pd
import pyarrow.parquet as pq
from track2_features import aggregate_interval_features
from tqdm import tqdm
import gc


def process_from_parquet(input_path: str = 'interval_readings.parquet',
                         output_path: str = 'track2_features.csv',
                         batch_size: int = 500_000):
    """
    Stream-reads the interval Parquet file in batches, computes
    Track 2 features for each batch, and concatenates the results.

    The trick: we must ensure all rows for a given consumer_id stay
    together within a batch. We do this by buffering the "tail"
    consumer from each chunk until the next chunk completes it.
    """
    print(f"Reading {input_path} and extracting features...")

    pf = pq.ParquetFile(input_path)
    total_rows = pf.metadata.num_rows
    print(f"  Total rows: {total_rows:,}")

    results = []
    buffer = pd.DataFrame()

    for batch in tqdm(pf.iter_batches(batch_size=batch_size),
                      desc="Batches"):
        chunk = batch.to_pandas()
        chunk = pd.concat([buffer, chunk], ignore_index=True)

        # Keep the last consumer_id aside (it may be split across batches)
        last_consumer = chunk['consumer_id'].iloc[-1]
        ready_mask = chunk['consumer_id'] != last_consumer
        ready = chunk[ready_mask]

        if not ready.empty:
            feats = aggregate_interval_features(ready)
            results.append(feats)

        # Buffer the incomplete tail consumer
        buffer = chunk[~ready_mask].copy()
        gc.collect()

    # Process the final buffered consumer
    if not buffer.empty:
        feats = aggregate_interval_features(buffer)
        results.append(feats)

    final = pd.concat(results, ignore_index=True)
    print(f"\nComputed features for {len(final)} consumer-months "
          f"({final['consumer_id'].nunique()} consumers)")

    final.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return final


if __name__ == '__main__':
    process_from_parquet()
