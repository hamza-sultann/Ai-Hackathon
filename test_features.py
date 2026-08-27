import pytest
import pandas as pd
import numpy as np
from features import build_features

def test_build_features():
    # 3 consumers, 6 months
    dates = pd.date_range(start='2022-01-01', periods=6, freq='MS')
    
    data = []
    for i, cid in enumerate(['C1', 'C2', 'C3']):
        for j, month in enumerate(dates):
            # Baseline usage 100
            usage = 100.0
            is_prosumer = (cid == 'C3')
            pmt_uptime = 100.0
            
            # C1 is normal, C2 has low uptime in month 6, C3 is prosumer
            if cid == 'C2' and j == 5:
                pmt_uptime = 50.0
                usage = 50.0 # dropped due to uptime
            elif cid == 'C3' and j >= 3:
                usage = 20.0 # dropped due to solar
                
            data.append({
                'consumer_id': cid,
                'month': month,
                'pmt_id': 'P1',
                'feeder_id': 'F1',
                'sanctioned_load_kw': 5.0,
                'consumer_type': 'residential',
                'meter_type': 'electronic',
                'is_registered_prosumer': is_prosumer,
                'billed_units_kwh': usage,
                'arrears_pkr': 0.0,
                'reader_id': 'R1',
                'injected_energy_kwh': 300.0, # fixed for simplicity
                'pmt_uptime_pct': pmt_uptime,
                'avg_temp_c': 25.0,
                'feeder_uptime_pct': 100.0
            })
            
    df = pd.DataFrame(data)
    
    # We use n_clusters=1 since they all have same static features.
    # In features.py n_clusters is capped at len(static_df).
    # Since they have identical static features, KMeans will likely just put them in 1-3 clusters.
    out_df = build_features(df, n_clusters=1)
    
    # 1. pmt_loss_delta checks
    assert 'pmt_loss_delta' in out_df.columns
    assert 'pmt_loss_delta_pct' in out_df.columns
    
    # In month 1 (j=0), sum of billed is 300, injected is 300 -> delta 0
    m1 = out_df[out_df['month'] == pd.to_datetime('2022-01-01')]
    assert (m1['pmt_loss_delta'] == 0).all()
    
    # 2. usage_deviation checks
    # For C1 at month 6 (j=5), rolling mean of last 6 (up to 5) should be 100
    c1 = out_df[out_df['consumer_id'] == 'C1'].reset_index(drop=True)
    assert pd.isna(c1.loc[0, 'usage_deviation']) # Not enough history
    assert pd.isna(c1.loc[1, 'usage_deviation']) # Only 1 previous month, min_periods=2
    assert c1.loc[2, 'usage_deviation'] == 0.0 # (100 - 100)/100
    
    # 7. feeder_uptime_adj_deviation checks
    c2 = out_df[out_df['consumer_id'] == 'C2'].reset_index(drop=True)
    # Month 6 (idx 5) usage dropped to 50, mean is 100. Usage dev is -0.5
    assert c2.loc[5, 'usage_deviation'] == -0.5
    # Uptime was 50, so divisor is max(0.5, 0.5) = 0.5. Adj deviation should be -0.5 / 0.5 = -1.0
    assert c2.loc[5, 'feeder_uptime_adj_deviation'] == -1.0
    
    # 8. prosumer_gated_usage_deviation checks
    c3 = out_df[out_df['consumer_id'] == 'C3'].reset_index(drop=True)
    # Prosumer gated should be exactly 0 for C3 (since they are a prosumer)
    assert (c3['prosumer_gated_usage_deviation'].dropna() == 0).all()
    # But usage deviation should be negative where it dropped (month 4, idx 3)
    assert c3.loc[3, 'usage_deviation'] < 0
    
    # Check 3mo rolling trend
    assert 'rolling_trend_3mo' in out_df.columns
    # Check seasonal residual
    assert 'seasonal_residual' in out_df.columns
