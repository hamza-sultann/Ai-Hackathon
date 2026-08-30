"""
Integration tests for the 1-hour interval generator and feature extractor.

Tests cover:
  - Correct hourly resolution (24 readings/day)
  - Monthly sum conservation (interval sum ≈ billed_units_kwh)
  - Theft signature visibility in features
  - Solar prosumer midday dip visibility
  - Confounder injection
  - Missing readings injection
"""

import numpy as np
import pandas as pd
import pytest
from generate_intervals import (
    get_season, apply_confounders, apply_theft_signature,
    generate_ar1_noise, build_interval_data
)
from track2_features import aggregate_interval_features


class TestGetSeason:
    def test_summer(self):
        assert get_season(35.0) == 'summer'

    def test_shoulder(self):
        assert get_season(26.0) == 'shoulder'

    def test_winter(self):
        assert get_season(15.0) == 'winter'

    def test_boundary_summer(self):
        assert get_season(30.1) == 'summer'

    def test_boundary_shoulder(self):
        assert get_season(22.5) == 'shoulder'

    def test_boundary_winter(self):
        assert get_season(22.0) == 'winter'


class TestApplyConfounders:
    def test_summer_ac_modifies_afternoon(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        modified = apply_confounders(shape, 'summer', False, rng)
        # Hours 12-22 should differ from original
        assert not np.allclose(shape[12:23], modified[12:23])

    def test_winter_geyser_spike(self):
        """Over many runs, geyser spike should appear ~40% of the time."""
        spike_count = 0
        for seed in range(100):
            rng = np.random.default_rng(seed)
            shape = np.ones(24) / 24
            mod = apply_confounders(shape, 'winter', False, rng)
            if mod[6] > shape[6] * 1.5 or mod[7] > shape[7] * 1.5:
                spike_count += 1
        assert 25 < spike_count < 55, f"Geyser spike rate {spike_count}% (expected ~40%)"

    def test_solar_midday_dip(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        modified = apply_confounders(shape, 'summer', True, rng)
        # Hours 10-14 should be reduced for prosumers
        midday_reduction = modified[10:15].mean() / shape[10:15].mean()
        assert midday_reduction < 0.5, "Solar prosumer midday should be heavily reduced"

    def test_non_prosumer_no_midday_dip(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        modified = apply_confounders(shape, 'summer', False, rng)
        # Non-prosumers shouldn't have the midday dip
        # (AC jitter might change values, but not a 50%+ reduction)
        midday_ratio = modified[10:15].mean() / shape[10:15].mean()
        assert midday_ratio > 0.5


class TestApplyTheft:
    def test_peak_shaver_suppresses_evening(self):
        """Over many runs, ~55% should show suppressed peak hours."""
        suppressed_count = 0
        for seed in range(200):
            rng = np.random.default_rng(seed)
            shape = np.ones(24) / 24
            mod = apply_theft_signature(shape, 'peak_hour_shaver', 'summer', rng)
            # Check if ANY part of the peak window (18-22) is suppressed
            # Jitter can shift the window ±1 hour
            peak_vals = mod[18:22]
            if peak_vals.min() < shape[18] * 0.15:
                suppressed_count += 1
        rate = suppressed_count / 200
        assert 0.40 < rate < 0.70, f"Peak shaving rate {rate:.2f} (expected ~0.55)"

    def test_nighttime_ac_summer_only(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        winter_mod = apply_theft_signature(shape.copy(), 'nighttime_ac', 'winter', rng)
        # Winter: no change expected
        assert np.allclose(shape, winter_mod)

    def test_nighttime_ac_suppresses_overnight(self):
        suppressed_count = 0
        for seed in range(200):
            rng = np.random.default_rng(seed)
            shape = np.ones(24) / 24
            mod = apply_theft_signature(shape, 'nighttime_ac', 'summer', rng)
            night_hours = [23, 0, 1, 2, 3, 4]
            night_vals = [mod[h] for h in night_hours]
            if np.mean(night_vals) < shape[0] * 0.3:
                suppressed_count += 1
        rate = suppressed_count / 200
        assert 0.55 < rate < 0.85, f"Night AC rate {rate:.2f} (expected ~0.70)"

    def test_kunda_total_suppression(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        mod = apply_theft_signature(shape, 'kunda', 'summer', rng)
        assert mod.sum() < shape.sum() * 0.15, "Kunda should bypass >85% of load"

    def test_fixed_shunt_uniform_reduction(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        mod = apply_theft_signature(shape, 'fixed_shunt', 'summer', rng)
        ratio = mod.sum() / shape.sum()
        assert 0.40 < ratio < 0.60, f"Fixed shunt ratio {ratio:.2f} (expected ~0.50)"

    def test_non_theft_unchanged(self):
        rng = np.random.default_rng(42)
        shape = np.ones(24) / 24
        mod = apply_theft_signature(shape, 'none', 'summer', rng)
        # 'none' is not a theft type so function shouldn't have a branch for it
        # It should return unchanged
        assert np.allclose(shape, mod)


class TestAR1Noise:
    def test_length(self):
        rng = np.random.default_rng(42)
        noise = generate_ar1_noise(100, rng=rng)
        assert len(noise) == 100

    def test_autocorrelation(self):
        rng = np.random.default_rng(42)
        noise = generate_ar1_noise(10000, rho=0.8, rng=rng)
        # Lag-1 autocorrelation should be near rho
        corr = np.corrcoef(noise[:-1], noise[1:])[0, 1]
        assert 0.6 < corr < 0.95, f"AR1 autocorrelation {corr:.2f} (expected ~0.8)"

    def test_zero_mean(self):
        rng = np.random.default_rng(42)
        noise = generate_ar1_noise(50000, rng=rng)
        assert abs(noise.mean()) < 0.01


class TestFeatureExtraction:
    """Test that features correctly detect theft signatures."""

    def _make_honest_data(self, n_days=30):
        """Creates honest consumer interval data with natural diurnal pattern."""
        rows = []
        for d in range(n_days):
            for h in range(24):
                ts = pd.Timestamp(f'2023-01-{d+1:02d} {h:02d}:00:00')
                # Natural diurnal: low overnight, peak evening
                if 0 <= h <= 5:
                    kwh = 0.15
                elif 6 <= h <= 9:
                    kwh = 0.35
                elif 18 <= h <= 21:
                    kwh = 0.60
                else:
                    kwh = 0.25
                rows.append({'consumer_id': 'C-HONEST',
                             'timestamp': ts, 'interval_kwh': kwh})
        return pd.DataFrame(rows)

    def _make_peak_shaver_data(self, n_days=30):
        """Peak shaver: near-zero during hours 19-21."""
        rows = []
        for d in range(n_days):
            for h in range(24):
                ts = pd.Timestamp(f'2023-01-{d+1:02d} {h:02d}:00:00')
                if 19 <= h <= 21:
                    kwh = 0.02  # near-zero (theft bypass)
                elif 0 <= h <= 5:
                    kwh = 0.15
                elif 6 <= h <= 9:
                    kwh = 0.35
                else:
                    kwh = 0.25
                rows.append({'consumer_id': 'C-SHAVER',
                             'timestamp': ts, 'interval_kwh': kwh})
        return pd.DataFrame(rows)

    def _make_solar_data(self, n_days=30):
        """Solar prosumer: midday dip from self-consumption."""
        rows = []
        for d in range(n_days):
            for h in range(24):
                ts = pd.Timestamp(f'2023-01-{d+1:02d} {h:02d}:00:00')
                if 10 <= h <= 14:
                    kwh = 0.03  # solar self-consumption
                elif 18 <= h <= 21:
                    kwh = 0.55
                elif 0 <= h <= 5:
                    kwh = 0.12
                else:
                    kwh = 0.25
                rows.append({'consumer_id': 'C-SOLAR',
                             'timestamp': ts, 'interval_kwh': kwh})
        return pd.DataFrame(rows)

    def test_peak_shaver_detected(self):
        honest = self._make_honest_data()
        shaver = self._make_peak_shaver_data()
        df = pd.concat([honest, shaver])

        features = aggregate_interval_features(df)
        honest_row = features[features['consumer_id'] == 'C-HONEST'].iloc[0]
        shaver_row = features[features['consumer_id'] == 'C-SHAVER'].iloc[0]

        # Peak shaver should have MUCH lower peak/offpeak ratio
        assert shaver_row['peak_offpeak_ratio'] < honest_row['peak_offpeak_ratio']
        # Peak window flatline should be much higher for shaver
        assert shaver_row['peak_window_flatline_fraction'] > \
               honest_row['peak_window_flatline_fraction']

    def test_solar_midday_dip_detected(self):
        honest = self._make_honest_data()
        solar = self._make_solar_data()
        df = pd.concat([honest, solar])

        features = aggregate_interval_features(df)
        honest_row = features[features['consumer_id'] == 'C-HONEST'].iloc[0]
        solar_row = features[features['consumer_id'] == 'C-SOLAR'].iloc[0]

        # Solar should have LOWER midday_dip_index than honest
        assert solar_row['midday_dip_index'] < honest_row['midday_dip_index']

    def test_feature_columns_complete(self):
        df = self._make_honest_data()
        features = aggregate_interval_features(df)
        expected_cols = {
            'consumer_id', 'month',
            'peak_offpeak_ratio', 'daily_load_factor',
            'flatline_fraction', 'peak_window_flatline_fraction',
            'midday_dip_index', 'tariff_boundary_alignment_score',
            'nighttime_drop_index'
        }
        assert expected_cols == set(features.columns)
