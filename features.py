import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def build_features(panel_df: pd.DataFrame, n_clusters: int = 15) -> pd.DataFrame:
    """
    Builds engineered features for anomaly detection.
    """
    df = panel_df.copy()
    
    # Ensure month is datetime for sorting
    df['month'] = pd.to_datetime(df['month'])
    df = df.sort_values(by=['consumer_id', 'month']).reset_index(drop=True)
    
    # 1. pmt_loss_delta
    # Intent: Identifies raw energy loss at the PMT level. A large gap between injected 
    # energy and total billed energy on a PMT suggests potential theft shared among its consumers.
    pmt_billed = df.groupby(['pmt_id', 'month'])['billed_units_kwh'].sum().reset_index(name='pmt_total_billed')
    df = df.merge(pmt_billed, on=['pmt_id', 'month'], how='left')
    df['pmt_loss_delta'] = df['injected_energy_kwh'] - df['pmt_total_billed']
    df['pmt_loss_delta_pct'] = df['pmt_loss_delta'] / df['injected_energy_kwh']
    df.drop(columns=['pmt_total_billed'], inplace=True)
    
    # 2. usage_deviation
    # Intent: Detects sudden drops in a consumer's usage relative to their own recent baseline,
    # a classic indicator of meter tampering or bypassing.
    def get_rolling_mean(x):
        return x.shift(1).rolling(window=6, min_periods=2).mean()
        
    df['rolling_mean'] = df.groupby('consumer_id')['billed_units_kwh'].transform(get_rolling_mean)
    # Handle division by zero
    df['usage_deviation'] = np.where(
        (df['rolling_mean'].isna()) | (df['rolling_mean'] == 0),
        np.nan,
        (df['billed_units_kwh'] - df['rolling_mean']) / df['rolling_mean']
    )
    df.drop(columns=['rolling_mean'], inplace=True)
    
    # 3. peer_deviation
    # Intent: Compares a consumer's usage to similar peers (same feeder, similar load, same type).
    # This helps catch consumers who are consistently stealing and thus don't have sudden drops 
    # in their own history (defeating usage_deviation).
    static_df = df[['consumer_id', 'feeder_id', 'sanctioned_load_kw', 'consumer_type']].drop_duplicates('consumer_id').copy()
    
    # One-hot encode categorical features and scale numerical
    num_scaled = StandardScaler().fit_transform(static_df[['sanctioned_load_kw']])
    cat_encoded = pd.get_dummies(static_df[['feeder_id', 'consumer_type']], drop_first=False).astype(float).values
    features_for_clustering = np.hstack([num_scaled, cat_encoded])
    
    # For tiny test sets, reduce n_clusters to number of unique consumers
    n_clusters_actual = min(n_clusters, len(static_df))
    # Additionally, if we have identical rows, KMeans may reduce effective clusters
    kmeans = KMeans(n_clusters=n_clusters_actual, random_state=42, n_init=10)
    static_df['peer_cluster'] = kmeans.fit_predict(features_for_clustering)
    
    df = df.merge(static_df[['consumer_id', 'peer_cluster']], on='consumer_id', how='left')
    
    def z_score(x):
        # We need at least 2 samples to compute std deviation, otherwise z-score is 0
        if len(x) < 2 or x.std(ddof=1) == 0:
            return pd.Series(0.0, index=x.index)
        return (x - x.mean()) / x.std(ddof=1)
        
    df['peer_deviation'] = df.groupby(['peer_cluster', 'month'])['billed_units_kwh'].transform(z_score)
    df.drop(columns=['peer_cluster'], inplace=True)
    
    # 4. arrears_ratio
    # Intent: Identifies consumers with high unpaid balances relative to their typical usage.
    # High arrears can be correlated with theft or financial distress.
    consumer_mean_usage = df.groupby('consumer_id')['billed_units_kwh'].transform('mean')
    # Replace 0 with NaN to avoid division by zero
    denom = 12 * consumer_mean_usage.replace(0, np.nan)
    df['arrears_ratio'] = df['arrears_pkr'] / denom
    df['arrears_ratio'] = df['arrears_ratio'].clip(lower=0, upper=10)
    
    # 5. seasonal_residual
    # Intent: Removes regular seasonal patterns (e.g., summer AC usage) to isolate true anomalies.
    df['month_of_year'] = df['month'].dt.month
    seasonal_baseline = df.groupby(['consumer_id', 'month_of_year'])['billed_units_kwh'].transform('mean')
    df['seasonal_residual'] = df['billed_units_kwh'] - seasonal_baseline
    df.drop(columns=['month_of_year'], inplace=True)
    
    # 6. rolling_trend_3mo
    # Intent: Captures short-term trajectories. A sustained downward trend over 3 months 
    # might indicate gradual meter tampering (e.g., slowing down a mechanical meter).
    # using simple (current - 3-months-ago)/3
    def trend_3mo(x):
        return (x - x.shift(3)) / 3.0
    df['rolling_trend_3mo'] = df.groupby('consumer_id')['billed_units_kwh'].transform(trend_3mo)
    
    # 7. feeder_uptime_adj_deviation
    # Intent: Adjusts usage drops for PMT outages (load shedding). A 50% drop in usage isn't suspicious 
    # if the PMT was offline 50% of the time.
    uptime_divisor = (df['pmt_uptime_pct'] / 100.0).clip(lower=0.5)
    df['feeder_uptime_adj_deviation'] = df['usage_deviation'] / uptime_divisor
    
    # 8. prosumer_gated_usage_deviation
    # Intent: Controls for solar adopters (prosumers) whose usage drops are legitimate (they are 
    # generating their own power). We set this to 0 for prosumers so tree-based models can easily 
    # ignore their "drops" without needing complex splits.
    # Why 0? Setting to 0 explicitly tells the model "there is zero anomalous deviation here", 
    # anchoring them at a neutral baseline, whereas NaN might lead to unpredictable split behavior.
    df['prosumer_gated_usage_deviation'] = np.where(
        df['is_registered_prosumer'], 
        0.0, 
        df['usage_deviation']
    )
    
    return df
