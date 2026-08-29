import numpy as np
import pandas as pd
import pickle
import os

def _gaussian_curve(x, mu, sig):
    """Helper to generate smooth bell curves for peak hours."""
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def generate_parametric_shape(season, day_type, rng, time_jitter=0.0):
    """
    Generates a 96-point curve (15-min intervals) representing a daily load shape
    for a Pakistani residential consumer.
    """
    x = np.arange(96)
    
    # Base load (always-on appliances)
    base = np.ones(96) * 0.1
    
    # Base parameters for peak hours
    morning_peak_mu = 32 + time_jitter # ~8:00 AM (32 * 15m)
    evening_peak_mu = 80 + time_jitter # ~8:00 PM (80 * 15m)
    
    if day_type == 'weekend':
        morning_peak_mu += 4 # Shift later by 1 hour on weekends
        base[40:68] += 0.2 # Higher midday base (people at home)
        
    if season == 'summer':
        # High AC load
        base += 0.3
        night_ac = np.zeros(96)
        night_ac[:24] = 0.4 # Midnight to 6 AM
        night_ac[88:] = 0.4 # 10 PM to Midnight
        base += night_ac
        morning_mag, evening_mag = 0.6, 1.2
    else: 
        # Winter/mild: no AC, geysers/heaters dominate morning/evening
        morning_mag, evening_mag = 0.8, 1.0
        
    morning_peak = morning_mag * _gaussian_curve(x, morning_peak_mu, 6) # ~1.5 hour spread
    evening_peak = evening_mag * _gaussian_curve(x, evening_peak_mu, 8) # ~2 hour spread
    
    raw_curve = base + morning_peak + evening_peak
    
    # Add small random noise representing minor appliance use
    raw_curve += rng.normal(0, 0.05, 96)
    raw_curve = np.clip(raw_curve, 0.01, None) # Ensure strictly positive consumption
    
    # Normalize so the curve represents a *shape* summing to 1.0
    normalized_curve = raw_curve / np.sum(raw_curve)
    return normalized_curve

def build_shape_templates(output_path='shape_templates.pkl', n_households=60):
    """
    Builds the fallback shape templates across seasons and day-types
    and saves them to disk.
    """
    rng = np.random.default_rng(42)
    templates = {}
    
    for hh_id in range(n_households):
        # Give each household a slight unique structural offset (-4 to +4 intervals, i.e., ±1 hour)
        time_jitter = rng.uniform(-4, 4)
        
        for season in ['summer', 'winter']:
            for day_type in ['weekday', 'weekend']:
                shape = generate_parametric_shape(season, day_type, rng, time_jitter)
                templates[(hh_id, season, day_type)] = shape
                
    # Ensure output directory exists (if nested)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump(templates, f)
        
    print(f"Saved {len(templates)} templates ({n_households} donor households) to {output_path}")

_TEMPLATES_CACHE = None

def get_template(sanctioned_load_tier: float, season: str, day_type: str, rng: np.random.Generator, template_path='shape_templates.pkl') -> np.ndarray:
    """
    Retrieves a donor shape template scaled to 1.0.
    """
    global _TEMPLATES_CACHE
    if _TEMPLATES_CACHE is None:
        if not os.path.exists(template_path):
            build_shape_templates(template_path)
            
        with open(template_path, 'rb') as f:
            _TEMPLATES_CACHE = pickle.load(f)
            
    # We randomly pick one of the 60 donor households to supply the shape
    donor_hh_id = rng.integers(0, 60)
    
    return _TEMPLATES_CACHE[(donor_hh_id, season, day_type)].copy()

if __name__ == '__main__':
    build_shape_templates()
