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
    
    out_df = build_features(df, n_clusters=1)
    
    # 1. pmt_loss_delta & pmt_loss_rank checks
    assert 'pmt_loss_delta' in out_df.columns
    assert 'pmt_loss_delta_pct' in out_df.columns
    assert 'pmt_loss_rank' in out_df.columns
    
    # 2. usage_deviation & fixed_baseline_deviation checks
    assert 'usage_deviation' in out_df.columns
    assert 'fixed_baseline_deviation' in out_df.columns
    
    c1 = out_df[out_df['consumer_id'] == 'C1'].reset_index(drop=True)
    assert pd.isna(c1.loc[0, 'usage_deviation']) # Not enough history
    assert c1.loc[2, 'usage_deviation'] == 0.0 # (100 - 100)/100
    assert c1.loc[5, 'fixed_baseline_deviation'] == 0.0 # first 3 mean = 100, current = 100
    
    # 3. CUSUM checks
    assert 'cusum_max_deviation' in out_df.columns
    assert 'months_since_detected_break' in out_df.columns
    
    # 7. feeder_uptime_adj_deviation checks
    c2 = out_df[out_df['consumer_id'] == 'C2'].reset_index(drop=True)
    assert c2.loc[5, 'usage_deviation'] == -0.5
    assert c2.loc[5, 'feeder_uptime_adj_deviation'] == -1.0
    
    # 8. prosumer_gated_usage_deviation checks
    c3 = out_df[out_df['consumer_id'] == 'C3'].reset_index(drop=True)
    assert (c3['prosumer_gated_usage_deviation'].dropna() == 0).all()
    assert c3.loc[3, 'usage_deviation'] < 0
    
    # Check 3mo rolling trend & seasonal residual
    assert 'rolling_trend_3mo' in out_df.columns
    assert 'seasonal_residual' in out_df.columns
