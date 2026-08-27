import pandas as pd
import argparse
from pathlib import Path
from sklearn.model_selection import train_test_split

def load_and_join_data(input_dir: str | Path) -> pd.DataFrame:
    input_dir = Path(input_dir)
    
    # Load CSVs
    consumers_df = pd.read_csv(input_dir / 'consumers.csv')
    pmt_monthly_df = pd.read_csv(input_dir / 'pmt_monthly.csv')
    feeder_monthly_df = pd.read_csv(input_dir / 'feeder_monthly.csv')
    monthly_readings_df = pd.read_csv(input_dir / 'monthly_readings.csv')
    
    # Join monthly_readings with consumers
    panel_df = pd.merge(monthly_readings_df, consumers_df, on='consumer_id', how='left')
    
    # Join PMT monthly on pmt_id, feeder_id and month
    panel_df = pd.merge(panel_df, pmt_monthly_df, on=['pmt_id', 'feeder_id', 'month'], how='left')
    
    # Join Feeder monthly on feeder_id and month
    # We rename the conflicting columns before merge or use suffixes
    panel_df = pd.merge(
        panel_df, 
        feeder_monthly_df, 
        on=['feeder_id', 'month'], 
        how='left', 
        suffixes=('', '_feeder')
    )
    
    # Note: injected_energy_kwh and avg_temp_c from pmt_monthly will not have a suffix.
    # The ones from feeder_monthly will be injected_energy_kwh_feeder and avg_temp_c_feeder.
    return panel_df

def three_way_split(panel_df: pd.DataFrame, train_frac=0.6, calibrate_frac=0.2, eval_frac=0.2, random_state=42):
    # 1. Gets the unique list of consumer_ids along with each consumer's theft_type
    consumer_theft = panel_df[['consumer_id', 'theft_type']].drop_duplicates()
    
    # Assert constant per consumer_id
    if consumer_theft['consumer_id'].duplicated().any():
        raise ValueError("A consumer_id has multiple theft_types across months!")
        
    consumer_ids = consumer_theft['consumer_id']
    theft_types = consumer_theft['theft_type']
    
    # 2. Performs a stratified split on consumer_id
    temp_frac = calibrate_frac + eval_frac
    
    try:
        train_ids, temp_ids, train_thefts, temp_thefts = train_test_split(
            consumer_ids, theft_types,
            test_size=temp_frac,
            stratify=theft_types,
            random_state=random_state
        )
        
        # Second split: calibrate vs eval
        relative_eval_frac = eval_frac / temp_frac
        calibrate_ids, eval_ids, cal_thefts, eval_thefts = train_test_split(
            temp_ids, temp_thefts,
            test_size=relative_eval_frac,
            stratify=temp_thefts,
            random_state=random_state
        )
    except ValueError as e:
        print(f"Warning during split: {e}. Falling back to non-stratified split.")
        train_ids, temp_ids = train_test_split(
            consumer_ids,
            test_size=temp_frac,
            random_state=random_state
        )
        calibrate_ids, eval_ids = train_test_split(
            temp_ids,
            test_size=eval_frac / temp_frac,
            random_state=random_state
        )
        
    # 3. Filters full panel
    train_df = panel_df[panel_df['consumer_id'].isin(train_ids)].copy()
    calibrate_df = panel_df[panel_df['consumer_id'].isin(calibrate_ids)].copy()
    eval_df = panel_df[panel_df['consumer_id'].isin(eval_ids)].copy()
    
    # 4. Prints a validation summary
    def print_summary(name, split_df):
        unique_consumers = split_df['consumer_id'].nunique()
        print(f"--- {name} Split ---")
        print(f"Total Consumers: {unique_consumers}")
        split_consumer_theft = split_df[['consumer_id', 'theft_type']].drop_duplicates()
        counts = split_consumer_theft['theft_type'].value_counts()
        pcts = split_consumer_theft['theft_type'].value_counts(normalize=True) * 100
        summary_df = pd.DataFrame({'Count': counts, '%': pcts}).round(2)
        print(summary_df)
        print()

    print_summary('Train', train_df)
    print_summary('Calibrate', calibrate_df)
    print_summary('Eval', eval_df)
    
    # 5. Asserts no consumer_id appears in more than one split
    train_set = set(train_ids)
    cal_set = set(calibrate_ids)
    eval_set = set(eval_ids)
    
    assert train_set.isdisjoint(cal_set), "Overlap between train and calibrate!"
    assert train_set.isdisjoint(eval_set), "Overlap between train and eval!"
    assert cal_set.isdisjoint(eval_set), "Overlap between calibrate and eval!"
    
    return train_df, calibrate_df, eval_df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data Assembly & Leak-Safe Three-Way Split")
    parser.add_argument('--input_dir', type=str, required=True, help="Directory containing input CSVs")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory to save output Parquet files")
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    panel_df = load_and_join_data(input_dir)
    train_df, calibrate_df, eval_df = three_way_split(panel_df)
    
    train_df.to_parquet(output_dir / 'train.parquet', index=False)
    calibrate_df.to_parquet(output_dir / 'calibrate.parquet', index=False)
    eval_df.to_parquet(output_dir / 'eval.parquet', index=False)
