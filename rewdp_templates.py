"""
Pakistani Residential Load Shape Templates (1-Hour Resolution)

Generates realistic 24-point normalized diurnal load curves grounded in
Pakistan's electricity usage patterns:
  - Morning chai/breakfast peak (7-9 AM weekday, 8-10 AM weekend)
  - Evening dinner/TV/AC peak aligned to NEPRA TOU window (6-10 PM)
  - Summer: elevated base from fans/AC, overnight AC for sleeping
  - Winter: morning geyser/heater spike, low overnight base
  - Weekend: later morning start, higher midday (people at home)

60 synthetic "donor households" with structural time jitter (±1 hour)
ensure population diversity without requiring external REWD-P data.
"""

import numpy as np

# ── In-memory template cache ─────────────────────────────────────────────
_TEMPLATE_CACHE = {}


def generate_hourly_shape(season: str, day_type: str,
                          rng: np.random.Generator,
                          time_jitter: float = 0.0) -> np.ndarray:
    """
    Generates a single 24-point normalized load curve.

    Parameters
    ----------
    season : 'summer' | 'shoulder' | 'winter'
    day_type : 'weekday' | 'weekend'
    rng : numpy Generator for reproducible randomness
    time_jitter : hours to shift peak timing (household structural offset)

    Returns
    -------
    np.ndarray of length 24, summing to 1.0
    """
    hours = np.arange(24, dtype=float)

    # ── Base load (fridge, standby, WiFi router, ceiling fans) ───────────
    base = np.ones(24) * 0.08

    # ── Morning peak centre ──────────────────────────────────────────────
    morning_mu = 7.5 + time_jitter          # weekday ~7:30 AM
    if day_type == 'weekend':
        morning_mu += 1.5                   # weekend  ~9:00 AM

    # ── Evening peak centre (NEPRA TOU 6-10 PM, peak ≈ 8 PM) ────────────
    evening_mu = 20.0 + time_jitter

    # ── Season-specific adjustments ──────────────────────────────────────
    if season == 'summer':
        base += 0.22                        # fans running 24/7
        for h in (23, 0, 1, 2, 3, 4, 5):   # overnight AC for sleeping
            base[h % 24] += 0.30
        for h in (12, 13, 14, 15):          # midday cooling
            base[h] += 0.12
        morning_mag, evening_mag = 0.45, 1.05
        morning_sig, evening_sig = 1.3, 1.8

    elif season == 'shoulder':              # transitional Apr-May, Oct-Nov
        base += 0.10
        morning_mag, evening_mag = 0.55, 0.90
        morning_sig, evening_sig = 1.2, 1.7

    else:                                   # winter
        morning_mag, evening_mag = 0.75, 0.85
        morning_sig, evening_sig = 1.0, 1.5
        for h in (18, 19, 20, 21):          # evening heater
            base[h] += 0.08

    # ── Weekend midday bump (people at home) ─────────────────────────────
    if day_type == 'weekend':
        for h in (10, 11, 12, 13, 14, 15):
            base[h] += 0.10

    # ── Compose from Gaussian peaks ──────────────────────────────────────
    morning = morning_mag * np.exp(-(hours - morning_mu)**2
                                   / (2 * morning_sig**2))
    evening = evening_mag * np.exp(-(hours - evening_mu)**2
                                   / (2 * evening_sig**2))

    shape = base + morning + evening

    # Small appliance-level randomness
    shape += rng.normal(0, 0.025, 24)
    shape = np.clip(shape, 0.01, None)

    # Normalize → pure *shape*, magnitude comes from billed_kwh downstream
    shape /= shape.sum()
    return shape


def build_template_cache(n_households: int = 60, seed: int = 42) -> None:
    """Pre-generate a pool of donor household load shapes."""
    global _TEMPLATE_CACHE
    _TEMPLATE_CACHE.clear()
    rng = np.random.default_rng(seed)

    for hh_id in range(n_households):
        jitter = rng.uniform(-1.0, 1.0)    # ±1 h structural offset
        for season in ('summer', 'shoulder', 'winter'):
            for day_type in ('weekday', 'weekend'):
                shape = generate_hourly_shape(season, day_type, rng, jitter)
                _TEMPLATE_CACHE[(hh_id, season, day_type)] = shape

    print(f"Built {len(_TEMPLATE_CACHE)} templates "
          f"({n_households} donor households × 3 seasons × 2 day-types)")


def get_template(season: str, day_type: str,
                 rng: np.random.Generator) -> np.ndarray:
    """Return a random donor template (lazy-initialises the cache)."""
    if not _TEMPLATE_CACHE:
        build_template_cache()
    # Derive donor pool size from cache keys
    n_donors = max(k[0] for k in _TEMPLATE_CACHE.keys()) + 1
    donor_id = rng.integers(0, n_donors)
    return _TEMPLATE_CACHE[(donor_id, season, day_type)].copy()


if __name__ == '__main__':
    build_template_cache()
    print("Sample summer weekday shape (24 hours):")
    rng = np.random.default_rng(0)
    t = get_template('summer', 'weekday', rng)
    for h, v in enumerate(t):
        bar = '█' * int(v * 300)
        print(f"  {h:02d}:00  {v:.4f}  {bar}")
