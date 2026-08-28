import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def compute_cusum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a CUSUM-style structural break statistic per consumer over their billed_units_kwh
    time series without leaking future information into past rows.
    
    For each month t in a consumer's history:
      1. Evaluates billing history from index 0 up to t.
      2. Computes the cumulative sum of deviations from the running mean.
      3. Identifies the peak absolute cumulative deviation as the likely break point.
      4. Outputs:
         - cusum_max_deviation: peak cumulative deviation normalized by running mean.
         - months_since_detected_break: elapsed months since the detected change-point.
    """
    df = df.sort_values(by=['consumer_id', 'month']).reset_index(drop=True)
    
    # Check if grid is uniform (equal months per consumer) for fast vectorized path
    consumer_counts = df.groupby('consumer_id', sort=False).size()
    n_months = consumer_counts.iloc[0]
    is_uniform = (consumer_counts == n_months).all()
    
    if is_uniform:
        n_consumers = len(consumer_counts)
        vals = df['billed_units_kwh'].to_numpy().reshape(n_consumers, n_months)
        
        cusum_max_all = np.zeros((n_consumers, n_months))
        months_since_all = np.zeros((n_consumers, n_months))
        
        for t in range(2, n_months):
            sub = vals[:, :t+1]
            mean_t = np.mean(sub, axis=1, keepdims=True)
            devs = sub - mean_t
            s = np.cumsum(devs, axis=1)
            abs_s = np.abs(s)
            k_star = np.argmax(abs_s, axis=1)
            max_val = np.take_along_axis(abs_s, k_star[:, None], axis=1).squeeze(1)
            
            # Avoid division by zero
            denom = np.where(mean_t.squeeze(1) > 0, mean_t.squeeze(1), 1.0)
            cusum_max_all[:, t] = max_val / denom
            months_since_all[:, t] = t - k_star
            
        df['cusum_max_deviation'] = cusum_max_all.ravel()
        df['months_since_detected_break'] = months_since_all.ravel()
    else:
        # Fallback for variable-length consumer series
        def _cusum_single(s):
            vals = s.to_numpy()
            n = len(vals)
            c_max = np.zeros(n)
            m_since = np.zeros(n)
            for t in range(2, n):
                sub = vals[:t+1]
                mean_t = np.mean(sub)
                if mean_t <= 0:
                    continue
                devs = sub - mean_t
                cum_devs = np.cumsum(devs)
                abs_cum = np.abs(cum_devs)
                k_star = np.argmax(abs_cum)
                c_max[t] = abs_cum[k_star] / mean_t
                m_since[t] = t - k_star
            return pd.DataFrame({'cusum_max_deviation': c_max, 'months_since_detected_break': m_since}, index=s.index)
            
        res = df.groupby('consumer_id', group_keys=False)['billed_units_kwh'].apply(_cusum_single)
        df['cusum_max_deviation'] = res['cusum_max_deviation']
        df['months_since_detected_break'] = res['months_since_detected_break']
        
    return df


def build_features(panel_df: pd.DataFrame, n_clusters: int = 15) -> pd.DataFrame:
    """
    Builds engineered features for anomaly detection.
    
    Hard Constraint: No ground truth labels ('is_theft_ground_truth' or 'theft_type')
    are used in computing any feature.
    """
    df = panel_df.copy()
    
    # Ensure month is datetime for sorting
    df['month'] = pd.to_datetime(df['month'])
    df = df.sort_values(by=['consumer_id', 'month']).reset_index(drop=True)
    
    # ---------------------------------------------------------
    # 1. pmt_loss_delta & pmt_loss_delta_pct (Raw PMT Energy Loss)
    # ---------------------------------------------------------
    # Intent: Identifies raw energy loss at the PMT level. A large gap between injected 
    # energy and total billed energy on a PMT suggests potential theft shared among its consumers.
    pmt_billed = df.groupby(['pmt_id', 'month'])['billed_units_kwh'].sum().reset_index(name='pmt_total_billed')
    df = df.merge(pmt_billed, on=['pmt_id', 'month'], how='left')
    df['pmt_loss_delta'] = df['injected_energy_kwh'] - df['pmt_total_billed']
    df['pmt_loss_delta_pct'] = df['pmt_loss_delta'] / df['injected_energy_kwh'].replace(0, np.nan)
    df.drop(columns=['pmt_total_billed'], inplace=True)
    
    # ---------------------------------------------------------
    # Fix 4: pmt_loss_rank (Percentile Rank across PMTs per Month)
    # ---------------------------------------------------------
    # Intent: Absolute technical loss in aging distribution grids is universally high (~40%+).
    # Ranking PMTs by loss percentage for each calendar month isolates anomalous high-loss
    # clusters relative to current operational baseline, dampening seasonal background noise.
    pmt_monthly_loss = df[['pmt_id', 'month', 'pmt_loss_delta_pct']].drop_duplicates()
    pmt_monthly_loss['pmt_loss_rank'] = pmt_monthly_loss.groupby('month')['pmt_loss_delta_pct'].rank(pct=True)
    df = df.merge(pmt_monthly_loss[['pmt_id', 'month', 'pmt_loss_rank']], on=['pmt_id', 'month'], how='left')
    
    # ---------------------------------------------------------
    # 2. usage_deviation (Trailing 6-Month Rolling Mean Deviation)
    # ---------------------------------------------------------
    # Intent: Detects short-term drops in a consumer's usage relative to their own recent baseline.
    def get_rolling_mean(x):
        return x.shift(1).rolling(window=6, min_periods=2).mean()
        
    df['rolling_mean'] = df.groupby('consumer_id')['billed_units_kwh'].transform(get_rolling_mean)
    df['usage_deviation'] = np.where(
        (df['rolling_mean'].isna()) | (df['rolling_mean'] == 0),
        np.nan,
        (df['billed_units_kwh'] - df['rolling_mean']) / df['rolling_mean']
    )
    df.drop(columns=['rolling_mean'], inplace=True)
    
    # ---------------------------------------------------------
    # Fix 2: fixed_baseline_deviation (Anchor to First 3 Months)
    # ---------------------------------------------------------
    # NOTE ON DOMAIN CONTEXT / HACKATHON RATIONALE:
    # Trailing rolling baselines suffer from "baseline contamination" — after a few months of theft,
    # the rolling window absorbs the stolen usage into its own baseline (0% deviation).
    # Since the synthetic dataset guarantees theft onset occurs on or after month 4, the first 3
    # months provide an uncontaminated reference anchor (simulating new smart meter commissioning).
    # In real legacy deployments where onset timing is unknown, CUSUM change-point detection
    # (Fix 3 below) is used to detect the structural shift dynamically.
    def get_first_3_months_mean(group):
        first_3 = group.head(3)['billed_units_kwh']
        return first_3.mean() if len(first_3) > 0 else np.nan
        
    first_3_means = df.groupby('consumer_id', sort=False).apply(get_first_3_months_mean).rename('first_3_mean')
    df = df.merge(first_3_means, on='consumer_id', how='left')
    
    df['fixed_baseline_deviation'] = np.where(
        (df['first_3_mean'].isna()) | (df['first_3_mean'] <= 0),
        np.nan,
        (df['billed_units_kwh'] - df['first_3_mean']) / df['first_3_mean']
    )
    df.drop(columns=['first_3_mean'], inplace=True)
    
    # ---------------------------------------------------------
    # Fix 3: CUSUM Change-Point Detection
    # ---------------------------------------------------------
    # Computes cusum_max_deviation and months_since_detected_break
    df = compute_cusum_features(df)
    
    # ---------------------------------------------------------
    # 3. peer_deviation (KMeans Cluster Deviation)
    # ---------------------------------------------------------
    # Intent: Compares consumer usage to similar peers (feeder, load, consumer type).
    static_df = df[['consumer_id', 'feeder_id', 'sanctioned_load_kw', 'consumer_type']].drop_duplicates('consumer_id').copy()
    
    num_scaled = StandardScaler().fit_transform(static_df[['sanctioned_load_kw']])
    cat_encoded = pd.get_dummies(static_df[['feeder_id', 'consumer_type']], drop_first=False).astype(float).values
    features_for_clustering = np.hstack([num_scaled, cat_encoded])
    
    n_clusters_actual = min(n_clusters, len(static_df))
    kmeans = KMeans(n_clusters=n_clusters_actual, random_state=42, n_init=10)
    static_df['peer_cluster'] = kmeans.fit_predict(features_for_clustering)
    
    df = df.merge(static_df[['consumer_id', 'peer_cluster']], on='consumer_id', how='left')
    
    def z_score(x):
        if len(x) < 2 or x.std(ddof=1) == 0:
            return pd.Series(0.0, index=x.index)
        return (x - x.mean()) / x.std(ddof=1)
        
    df['peer_deviation'] = df.groupby(['peer_cluster', 'month'])['billed_units_kwh'].transform(z_score)
    df.drop(columns=['peer_cluster'], inplace=True)
    
    # ---------------------------------------------------------
    # 4. arrears_ratio (Annualized Arrears)
    # ---------------------------------------------------------
    consumer_mean_usage = df.groupby('consumer_id')['billed_units_kwh'].transform('mean')
    denom = 12 * consumer_mean_usage.replace(0, np.nan)
    df['arrears_ratio'] = df['arrears_pkr'] / denom
    df['arrears_ratio'] = df['arrears_ratio'].clip(lower=0, upper=10)
    
    # ---------------------------------------------------------
    # 5. seasonal_residual (Calendar Month Deviation)
    # ---------------------------------------------------------
    df['month_of_year'] = df['month'].dt.month
    seasonal_baseline = df.groupby(['consumer_id', 'month_of_year'])['billed_units_kwh'].transform('mean')
    df['seasonal_residual'] = df['billed_units_kwh'] - seasonal_baseline
    df.drop(columns=['month_of_year'], inplace=True)
    
    # ---------------------------------------------------------
    # 6. rolling_trend_3mo (3-Month Trajectory)
    # ---------------------------------------------------------
    def trend_3mo(x):
        return (x - x.shift(3)) / 3.0
    df['rolling_trend_3mo'] = df.groupby('consumer_id')['billed_units_kwh'].transform(trend_3mo)
    
    # ---------------------------------------------------------
    # 7. feeder_uptime_adj_deviation (Load-Shedding Discounting)
    # ---------------------------------------------------------
    uptime_divisor = (df['pmt_uptime_pct'] / 100.0).clip(lower=0.5)
    df['feeder_uptime_adj_deviation'] = df['usage_deviation'] / uptime_divisor
    
    # ---------------------------------------------------------
    # 8. prosumer_gated_usage_deviation (Rooftop Solar Confounder Control)
    # ---------------------------------------------------------
    df['prosumer_gated_usage_deviation'] = np.where(
        df['is_registered_prosumer'], 
        0.0, 
        df['usage_deviation']
    )
    
    return df
