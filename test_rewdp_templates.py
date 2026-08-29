import numpy as np
import os
import pytest
from rewdp_templates import build_shape_templates, get_template, generate_parametric_shape

def test_generate_parametric_shape():
    rng = np.random.default_rng(42)
    shape = generate_parametric_shape('summer', 'weekday', rng, time_jitter=0)
    
    assert len(shape) == 96
    assert np.isclose(np.sum(shape), 1.0)
    assert np.all(shape > 0)
    
    # Check that peaks exist
    # Morning peak around index 32
    assert shape[32] > shape[10]
    # Evening peak around index 80
    assert shape[80] > shape[50]

def test_build_and_get_template(tmp_path):
    pkl_path = tmp_path / 'test_templates.pkl'
    
    # Build a small set
    build_shape_templates(str(pkl_path), n_households=10)
    assert pkl_path.exists()
    
    rng = np.random.default_rng(99)
    
    # Test retrieval
    # Since we built 10, we must override the hardcoded 60 in get_template by mocking or we'll get a KeyError.
    # Actually, let's just build 60 so it matches the hardcoded assumption in the function.
    build_shape_templates(str(pkl_path), n_households=60)
    
    template = get_template(5.0, 'summer', 'weekday', rng, template_path=str(pkl_path))
    
    # Assertions
    assert len(template) == 96
    assert np.isclose(np.sum(template), 1.0)
    
    # Verify weekend/weekday differ for same consumer
    # To do this safely, we need to fix the RNG so it picks the SAME donor_hh_id
    rng_fixed_1 = np.random.default_rng(42)
    template_weekday = get_template(5.0, 'summer', 'weekday', rng_fixed_1, template_path=str(pkl_path))
    
    rng_fixed_2 = np.random.default_rng(42)
    template_weekend = get_template(5.0, 'summer', 'weekend', rng_fixed_2, template_path=str(pkl_path))
    
    # They should not be perfectly identical
    assert not np.allclose(template_weekday, template_weekend)
