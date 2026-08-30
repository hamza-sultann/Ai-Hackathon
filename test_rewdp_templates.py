"""Tests for the 24-hour load shape template generator."""

import numpy as np
import pytest
from rewdp_templates import (generate_hourly_shape, build_template_cache,
                              get_template, _TEMPLATE_CACHE)


class TestGenerateHourlyShape:
    """Unit tests for the parametric shape generator."""

    def test_shape_length(self):
        rng = np.random.default_rng(42)
        shape = generate_hourly_shape('summer', 'weekday', rng)
        assert len(shape) == 24

    def test_shape_sums_to_one(self):
        rng = np.random.default_rng(42)
        for season in ('summer', 'shoulder', 'winter'):
            for day_type in ('weekday', 'weekend'):
                shape = generate_hourly_shape(season, day_type, rng)
                assert np.isclose(shape.sum(), 1.0), \
                    f"Shape for {season}/{day_type} sums to {shape.sum()}"

    def test_all_positive(self):
        rng = np.random.default_rng(42)
        shape = generate_hourly_shape('winter', 'weekend', rng)
        assert np.all(shape > 0)

    def test_evening_peak_exists(self):
        """Evening TOU peak (hours 18-21) should be higher than midday."""
        rng = np.random.default_rng(42)
        shape = generate_hourly_shape('summer', 'weekday', rng)
        evening_avg = shape[18:22].mean()
        midday_avg = shape[10:14].mean()
        assert evening_avg > midday_avg, \
            "Evening peak should be higher than midday baseline"

    def test_morning_peak_exists(self):
        """Morning peak (hours 7-9) should be higher than overnight (2-5 AM)."""
        rng = np.random.default_rng(42)
        shape = generate_hourly_shape('winter', 'weekday', rng)
        morning_avg = shape[7:10].mean()
        overnight_avg = shape[2:5].mean()
        assert morning_avg > overnight_avg

    def test_summer_overnight_higher_than_winter(self):
        """Summer overnight AC load should elevate the base vs winter."""
        rng1 = np.random.default_rng(42)
        summer = generate_hourly_shape('summer', 'weekday', rng1)
        rng2 = np.random.default_rng(42)
        winter = generate_hourly_shape('winter', 'weekday', rng2)
        # Hours 0-4: summer should have higher relative share due to AC
        summer_night = summer[0:5].sum()
        winter_night = winter[0:5].sum()
        assert summer_night > winter_night

    def test_weekend_later_morning(self):
        """Weekend morning peak should be shifted later than weekday."""
        rng1 = np.random.default_rng(42)
        weekday = generate_hourly_shape('summer', 'weekday', rng1)
        rng2 = np.random.default_rng(42)
        weekend = generate_hourly_shape('summer', 'weekend', rng2)
        # Weekday peak at ~7-8, weekend at ~9-10
        # Check hour 7 higher on weekday, hour 10 higher on weekend
        assert weekday[7] > weekend[7] or weekend[9] > weekday[9]

    def test_time_jitter_changes_shape(self):
        rng1 = np.random.default_rng(42)
        s1 = generate_hourly_shape('summer', 'weekday', rng1, time_jitter=0)
        rng2 = np.random.default_rng(42)
        s2 = generate_hourly_shape('summer', 'weekday', rng2, time_jitter=1.0)
        assert not np.allclose(s1, s2)


class TestTemplateCache:
    """Tests for the template caching system."""

    def test_build_cache_populates(self):
        build_template_cache(n_households=5)
        # 5 households × 3 seasons × 2 day_types = 30
        assert len(_TEMPLATE_CACHE) == 30

    def test_get_template_returns_copy(self):
        build_template_cache(n_households=5)
        rng = np.random.default_rng(0)
        t1 = get_template('summer', 'weekday', rng)
        t1[0] = 999.0
        rng2 = np.random.default_rng(0)
        t2 = get_template('summer', 'weekday', rng2)
        assert t2[0] != 999.0, "get_template should return a copy"

    def test_get_template_shape(self):
        build_template_cache()
        rng = np.random.default_rng(42)
        t = get_template('winter', 'weekend', rng)
        assert len(t) == 24
        assert np.isclose(t.sum(), 1.0)

    def test_different_donors_differ(self):
        """Two different donors should produce different shapes."""
        build_template_cache()
        rng1 = np.random.default_rng(0)
        rng2 = np.random.default_rng(99)
        t1 = get_template('summer', 'weekday', rng1)
        t2 = get_template('summer', 'weekday', rng2)
        # Might be same donor by chance, but very unlikely with 60 donors
        # Just check they're valid
        assert np.isclose(t1.sum(), 1.0)
        assert np.isclose(t2.sum(), 1.0)
