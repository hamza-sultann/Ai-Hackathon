"""Unified risk scorer backed by the real Track-1 pipeline artifacts.

This serves the exact model produced by the repo-root `run_pipeline.py`:

    Isolation Forest (OOF anomaly score)  ->  XGBoost classifier
      ->  isotonic/sigmoid probability calibration  ->  TreeSHAP explanations

It reuses the root feature engineering (`features.build_features`) and the root
data assembly (`data_assembly.load_and_join_data`) so a consumer scored here is
scored identically to `agents/agent_loop.py`. The public surface
(`explain`, `score_panel`, `latest_scores`, `scored_for`, `RiskScore`) matches
the scikit-learn fallback in `scorer.py`, so nothing downstream changes.

Track-2 (AMI) features are *not* inputs to the main `probability` — the root
XGBoost model was trained on the 12 billing/PMT features + the Isolation
Forest score only, and `probability`/`monthly_probability` stay driven by
that one model for every consumer (AMI or not), so the primary queue is
apples-to-apples across all 10,000 consumers.

For the ~2,000 AMI consumers, `smart_meter_probability` is served by a
*second*, genuinely separate calibrated model — see `train_track2_model.py`
at the repo root, which is a servable version of `uplift_evaluation.py`'s
"Model 2" (Track-1 + Track-2 features), reusing its exact feature lists and
hyperparameters. When those artifacts aren't present, `smart_meter_probability`
falls back to a copy of `probability` (the pre-existing behaviour), which is
enough for the app to run but means the Pipeline Comparison page can never
show a "Smart Meter Only" detection.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.config import get_settings
from app.data.loader import get_data
from app.ml.features import FEATURE_DESCRIPTIONS
from app.ml.scorer import Contribution, RiskScore

log = logging.getLogger("istikshaf.ml")

# The 12 engineered features the root pipeline feeds to the Isolation Forest,
# plus the OOF anomaly score that the XGBoost model consumes. Order matters:
# it must match `feature_columns` in `run_pipeline.py`.
_BASE_FEATURES: list[str] = [
    "pmt_loss_delta_pct",
    "pmt_loss_rank",
    "usage_deviation",
    "fixed_baseline_deviation",
    "cusum_max_deviation",
    "months_since_detected_break",
    "peer_deviation",
    "arrears_ratio",
    "seasonal_residual",
    "rolling_trend_3mo",
    "feeder_uptime_adj_deviation",
    "prosumer_gated_usage_deviation",
]
_ISO_COL = "iso_forest_oof_score"
_MODEL_FEATURES: list[str] = _BASE_FEATURES + [_ISO_COL]

# All 7 Track-2 (AMI) aggregate columns — merged for display, and fed to the
# optional Track-2 model below. Verbatim list from uplift_evaluation.py.
_TRACK2_FEATURES: list[str] = [
    "peak_offpeak_ratio",
    "daily_load_factor",
    "flatline_fraction",
    "peak_window_flatline_fraction",
    "midday_dip_index",
    "tariff_boundary_alignment_score",
    "nighttime_drop_index",
]
# Trained with the same column name as the Track-1 iso score (see
# train_track2_model.py) — the two never coexist in the same X matrix, so no
# clash, but the name must match exactly for the booster to accept the input.
_TRACK2_MODEL_FEATURES: list[str] = _BASE_FEATURES + [_ISO_COL] + _TRACK2_FEATURES

_CACHE_VERSION = 3


class XGBUnavailable(RuntimeError):
    """Raised when the real pipeline can't be served (missing artifacts/deps)."""


def _add_repo_root_to_path() -> Path:
    root = get_settings().repo_root
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def artifacts_available() -> bool:
    settings = get_settings()
    if not settings.xgb_artifacts_present():
        return False
    try:
        import shap  # noqa: F401
        import xgboost  # noqa: F401
    except ImportError:
        return False
    # Root feature-engineering modules must be importable too.
    _add_repo_root_to_path()
    try:
        import data_assembly  # noqa: F401
        import features  # noqa: F401
    except ImportError:
        return False
    return True


def track2_available() -> bool:
    """Whether the optional AMI-enhanced model (train_track2_model.py) is
    installed. Purely additive — the app runs fine without it."""
    return get_settings().track2_artifacts_present()


class XGBRiskScorer:
    """Loads the root artifacts and scores the full consumer-month panel."""

    def __init__(self) -> None:
        if not artifacts_available():
            raise XGBUnavailable(
                "XGBoost pipeline artifacts or dependencies are missing. Run "
                "`python data_assembly.py --input_dir data --output_dir output` "
                "then `python run_pipeline.py`, and `pip install xgboost shap`."
            )
        import xgboost as xgb

        self._xgb = xgb
        self.data = get_data()
        settings = get_settings()
        paths = settings.xgb_artifacts

        self.booster = xgb.Booster()
        self.booster.load_model(str(paths["booster"]))
        self.calibrator = joblib.load(paths["calibrator"])
        self.iso = joblib.load(paths["iso_forest"])
        self.iso_imputer = joblib.load(paths["iso_imputer"])
        self._explainer = None  # lazily built TreeSHAP explainer

        self.has_track2_model = track2_available()
        if self.has_track2_model:
            t2_paths = settings.track2_artifacts
            self.booster_track2 = xgb.Booster()
            self.booster_track2.load_model(str(t2_paths["booster"]))
            self.calibrator_track2 = joblib.load(t2_paths["calibrator"])
            self.iso_track2 = joblib.load(t2_paths["iso_forest"])
            log.info("Track-2 (AMI-enhanced) model artifacts found — smart_meter_probability will use it.")
        else:
            log.info(
                "No Track-2 model artifacts (see train_track2_model.py) — "
                "smart_meter_probability will fall back to the Track-1 probability for AMI consumers."
            )

        self._score_all()

    # -- scoring --------------------------------------------------------
    def _artifact_fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(str(_CACHE_VERSION).encode())
        for key, p in sorted(get_settings().xgb_artifacts.items()):
            st = p.stat()
            h.update(f"{key}:{st.st_mtime_ns}:{st.st_size}".encode())
        if self.has_track2_model:
            for key, p in sorted(get_settings().track2_artifacts.items()):
                st = p.stat()
                h.update(f"t2:{key}:{st.st_mtime_ns}:{st.st_size}".encode())
        d = get_settings().data_dir
        for name in ("consumers.csv", "monthly_readings.csv", "pmt_monthly.csv", "feeder_monthly.csv"):
            fp = d / name
            if fp.exists():
                h.update(f"{name}:{fp.stat().st_mtime_ns}".encode())
        h.update(str(self.data.analysis_month).encode())
        return h.hexdigest()

    @property
    def _cache_path(self) -> Path:
        return get_settings().cache_dir / "xgb_scored.parquet"

    @property
    def _cache_meta_path(self) -> Path:
        return get_settings().cache_dir / "xgb_scored.meta.json"

    def _load_cached_frame(self) -> pd.DataFrame | None:
        meta_p, data_p = self._cache_meta_path, self._cache_path
        if not (meta_p.exists() and data_p.exists()):
            return None
        try:
            meta = json.loads(meta_p.read_text())
            if meta.get("fingerprint") != self._artifact_fingerprint():
                return None
            df = pd.read_parquet(data_p)
        except Exception as exc:  # pragma: no cover - defensive
            log.warning("Could not reuse XGB score cache: %s", exc)
            return None
        df["month"] = pd.to_datetime(df["month"])
        log.info("Loaded cached XGB scores (%d rows) from %s", len(df), data_p)
        return df

    def _save_cached_frame(self, df: pd.DataFrame) -> None:
        try:
            df.to_parquet(self._cache_path, index=False)
            self._cache_meta_path.write_text(
                json.dumps({"fingerprint": self._artifact_fingerprint()})
            )
        except Exception as exc:  # pragma: no cover - defensive
            log.warning("Could not write XGB score cache: %s", exc)

    def _build_scored_frame(self) -> pd.DataFrame:
        import data_assembly
        import features as root_features

        t0 = time.time()
        panel = data_assembly.load_and_join_data(get_settings().data_dir)
        log.info("Assembled panel (%d rows) in %.1fs", len(panel), time.time() - t0)

        t0 = time.time()
        df = root_features.build_features(panel)
        log.info("Engineered root features in %.1fs", time.time() - t0)

        # Isolation Forest OOF-style anomaly score (final model on full base set).
        X_base = df[_BASE_FEATURES]
        df[_ISO_COL] = self.iso.score_samples(self.iso_imputer.transform(X_base))
        df["iso_forest_score"] = df[_ISO_COL]  # alias for shared feature labels

        # Calibrated theft probability from the real XGBoost + calibrator.
        df["probability"] = self.calibrator.predict_proba(df[_MODEL_FEATURES])[:, 1]
        # The root model *is* the Track-1 monthly-billing model.
        df["monthly_probability"] = df["probability"]

        ami_mask = df["consumer_id"].isin(self.data.ami_consumer_ids)
        df["is_ami"] = ami_mask

        # Merge the full Track-2 (AMI) aggregate set — needed both for display
        # and, when available, as inputs to the second Track-2 model below.
        if self.data.track2 is not None:
            cols = ["consumer_id", "month"] + [
                c for c in _TRACK2_FEATURES if c in self.data.track2.columns
            ]
            df = df.merge(self.data.track2[cols], on=["consumer_id", "month"], how="left")
        for c in _TRACK2_FEATURES:
            if c not in df.columns:
                df[c] = np.nan

        if self.has_track2_model and ami_mask.any():
            df["smart_meter_probability"] = self._score_track2(df, ami_mask)
        else:
            # No AMI-enhanced model installed — same value as the Track-1
            # probability (pre-existing fallback; see module docstring).
            df["smart_meter_probability"] = np.where(ami_mask, df["probability"], 0.0)

        return df

    def _score_track2(self, df: pd.DataFrame, ami_mask: pd.Series) -> np.ndarray:
        """Score smart_meter_probability for AMI rows via the Track-2 model
        (uplift_evaluation.py's Model 2 recipe — see train_track2_model.py)."""
        out = np.where(ami_mask, df["probability"], 0.0)
        ami_rows = df.loc[ami_mask]
        if ami_rows.empty:
            return out

        X_base_ami = ami_rows[_BASE_FEATURES].fillna(0)
        iso_score = self.iso_track2.score_samples(X_base_ami)
        X_t2 = ami_rows[_BASE_FEATURES + _TRACK2_FEATURES].copy()
        X_t2[_TRACK2_FEATURES] = X_t2[_TRACK2_FEATURES].fillna(0)
        # Column name must match training exactly (see _TRACK2_MODEL_FEATURES).
        X_t2[_ISO_COL] = iso_score
        X_t2 = X_t2[_TRACK2_MODEL_FEATURES]

        proba = self.calibrator_track2.predict_proba(X_t2)[:, 1]
        out[ami_mask.to_numpy()] = proba
        return out

    def _score_all(self) -> None:
        df = self._load_cached_frame()
        if df is None:
            df = self._build_scored_frame()
            self._save_cached_frame(df)

        self.scored = df
        self._by_consumer = df.set_index("consumer_id", drop=False).sort_index()
        self.latest = df[df["month"] == self.data.analysis_month].set_index("consumer_id")
        log.info(
            "XGB-scored %d consumer-months; %d consumers in analysis month %s "
            "(prob max=%.3f, >=0.55: %d)",
            len(df), len(self.latest), self.data.month_str(),
            float(df["probability"].max()),
            int((self.latest["probability"] >= 0.55).sum()),
        )

    # -- public surface (mirrors scorer.RiskScorer) --------------------
    def score_panel(self) -> pd.DataFrame:
        return self.scored

    def latest_scores(self) -> pd.DataFrame:
        return self.latest

    def scored_for(self, consumer_id: str) -> pd.DataFrame:
        if consumer_id not in self._by_consumer.index:
            return self._by_consumer.iloc[0:0]
        return self._by_consumer.loc[[consumer_id]]

    def _tree_explainer(self):
        if self._explainer is None:
            import shap

            self._explainer = shap.TreeExplainer(self.booster)
        return self._explainer

    def explain(self, consumer_id: str, month: pd.Timestamp | None = None) -> RiskScore | None:
        sub = self.scored_for(consumer_id)
        if sub.empty:
            return None
        target = month or self.data.analysis_month
        row = sub[sub["month"] == target]
        row = row.iloc[0] if not row.empty else sub.sort_values("month").iloc[-1]

        X = pd.DataFrame([row[_MODEL_FEATURES].to_dict()])[_MODEL_FEATURES].astype(float)
        shap_row = np.asarray(self._tree_explainer().shap_values(X)).reshape(-1)

        contribs: list[Contribution] = []
        for feat, sv in zip(_MODEL_FEATURES, shap_row):
            c = float(sv)
            if abs(c) < 1e-6:
                continue
            label_key = "iso_forest_score" if feat == _ISO_COL else feat
            raw = row.get(feat, float("nan"))
            contribs.append(
                Contribution(
                    feature=label_key,
                    raw_value=float(raw) if pd.notna(raw) else float("nan"),
                    contribution=c,
                    direction="increases_risk" if c > 0 else "decreases_risk",
                    description=FEATURE_DESCRIPTIONS.get(label_key, label_key.replace("_", " ")),
                )
            )
        contribs.sort(key=lambda c: abs(c.contribution), reverse=True)

        return RiskScore(
            consumer_id=consumer_id,
            month=pd.Timestamp(row["month"]).strftime("%Y-%m"),
            probability=float(row["probability"]),
            monthly_probability=float(row["monthly_probability"]),
            smart_meter_probability=float(row["smart_meter_probability"]),
            is_ami=bool(row["is_ami"]),
            contributions=contribs,
        )
