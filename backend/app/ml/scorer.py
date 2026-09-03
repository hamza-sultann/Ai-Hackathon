"""Risk scoring model.

Faithful-in-spirit reproduction of the agentic pipeline
(Isolation Forest -> boosted classifier -> probability calibration -> additive
explanation) using only scikit-learn, so the backend runs with no XGBoost/SHAP
install. Swap in `xgb_scorer.py` later for the real thing; the public surface
(`score_panel`, `explain`, `RiskScore`) stays the same.
"""
from __future__ import annotations

import functools
import logging
from dataclasses import dataclass, field

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression

from app.config import get_settings
from app.data.loader import get_data
from app.ml.features import (
    BASE_FEATURES,
    FEATURE_DESCRIPTIONS,
    MODEL_FEATURES,
    build_features,
)

log = logging.getLogger("istikshaf.ml")

_MONTHLY_FEATURES = BASE_FEATURES + ["iso_forest_score"]
_MODEL_VERSION = 3


@dataclass
class Contribution:
    feature: str
    raw_value: float
    contribution: float
    direction: str  # "increases_risk" | "decreases_risk"
    description: str


@dataclass
class RiskScore:
    consumer_id: str
    month: str
    probability: float          # full model, calibrated
    monthly_probability: float   # billing-only model
    smart_meter_probability: float  # AMI model (0.0 if not an AMI consumer)
    is_ami: bool
    contributions: list[Contribution] = field(default_factory=list)


@functools.lru_cache(maxsize=1)
def get_scorer() -> "RiskScorer":
    return RiskScorer()


class RiskScorer:
    def __init__(self) -> None:
        settings = get_settings()
        self.data = get_data()
        self._features: pd.DataFrame | None = None

        if settings.model_path.exists() and not settings.force_retrain:
            bundle = joblib.load(settings.model_path)
            if bundle.get("version") == _MODEL_VERSION:
                log.info("Loading cached risk model from %s", settings.model_path)
                self._load_bundle(bundle)
                self._score_all()
                return
            log.info("Cached model version mismatch — retraining.")

        self._train()
        joblib.dump(self._bundle(), settings.model_path)
        log.info("Saved risk model to %s", settings.model_path)
        self._score_all()

    # -- training ---------------------------------------------------------
    def _feature_frame(self) -> pd.DataFrame:
        if self._features is None:
            log.info("Engineering features over %d consumer-months...", len(self.data.panel))
            self._features = build_features(self.data.panel, self.data.track2)
        return self._features

    def _train(self) -> None:
        df = self._feature_frame()
        y = df["is_theft_ground_truth"].fillna(False).astype(int).to_numpy()

        # Isolation Forest on imputed base features -> anomaly score feature.
        X_base = df[BASE_FEATURES]
        self.base_medians = X_base.median(numeric_only=True)
        X_base_imp = X_base.fillna(self.base_medians).to_numpy()
        self.iso = IsolationForest(n_estimators=150, random_state=42, n_jobs=-1)
        self.iso.fit(X_base_imp)
        df["iso_forest_score"] = -self.iso.score_samples(X_base_imp)

        log.info("Training calibrated classifiers (billing-only + full)...")
        self.model_monthly = _fit_calibrated(df[_MONTHLY_FEATURES], y)
        self.model_full = _fit_calibrated(df[MODEL_FEATURES], y)

        # Linear surrogate for additive, signed explanations.
        self.medians = df[MODEL_FEATURES].median(numeric_only=True)
        filled = df[MODEL_FEATURES].fillna(self.medians)
        self.stds = filled.std(ddof=0).replace(0, 1.0)
        Z = (filled - self.medians) / self.stds
        self.surrogate = LogisticRegression(max_iter=2000, class_weight="balanced")
        self.surrogate.fit(Z.to_numpy(), y)

    def _bundle(self) -> dict:
        return {
            "version": _MODEL_VERSION,
            "iso": self.iso,
            "base_medians": self.base_medians,
            "model_monthly": self.model_monthly,
            "model_full": self.model_full,
            "medians": self.medians,
            "stds": self.stds,
            "surrogate": self.surrogate,
        }

    def _load_bundle(self, b: dict) -> None:
        self.iso = b["iso"]
        self.base_medians = b["base_medians"]
        self.model_monthly = b["model_monthly"]
        self.model_full = b["model_full"]
        self.medians = b["medians"]
        self.stds = b["stds"]
        self.surrogate = b["surrogate"]

    # -- scoring ---------------------------------------------------------
    def _score_all(self) -> None:
        df = self._feature_frame().copy()
        X_base_imp = df[BASE_FEATURES].fillna(self.base_medians).to_numpy()
        df["iso_forest_score"] = -self.iso.score_samples(X_base_imp)

        df["monthly_probability"] = self.model_monthly.predict_proba(
            df[_MONTHLY_FEATURES].to_numpy()
        )[:, 1]
        df["probability"] = self.model_full.predict_proba(df[MODEL_FEATURES].to_numpy())[:, 1]

        ami_mask = df["consumer_id"].isin(self.data.ami_consumer_ids)
        df["smart_meter_probability"] = np.where(ami_mask, df["probability"], 0.0)
        df["is_ami"] = ami_mask

        self.scored = df
        self._by_consumer = df.set_index("consumer_id", drop=False).sort_index()
        self.latest = df[df["month"] == self.data.analysis_month].set_index("consumer_id")
        log.info(
            "Scored %d consumer-months; %d consumers in analysis month %s",
            len(df), len(self.latest), self.data.month_str(),
        )

    def score_panel(self) -> pd.DataFrame:
        return self.scored

    def latest_scores(self) -> pd.DataFrame:
        """One row per consumer for the analysis month."""
        return self.latest

    def scored_for(self, consumer_id: str) -> pd.DataFrame:
        """All monthly rows for one consumer (empty frame if unknown)."""
        if consumer_id not in self._by_consumer.index:
            return self._by_consumer.iloc[0:0]
        rows = self._by_consumer.loc[[consumer_id]]
        return rows

    def explain(self, consumer_id: str, month: pd.Timestamp | None = None) -> RiskScore | None:
        sub = self.scored_for(consumer_id)
        if sub.empty:
            return None
        row = sub[sub["month"] == (month or self.data.analysis_month)]
        row = row.iloc[0] if not row.empty else sub.sort_values("month").iloc[-1]

        z = {}
        for f in MODEL_FEATURES:
            std = self.stds.get(f, 1.0) or 1.0
            val = row[f]
            val = self.medians[f] if pd.isna(val) else val
            z[f] = (val - self.medians[f]) / std

        contribs: list[Contribution] = []
        for f, coef in zip(MODEL_FEATURES, self.surrogate.coef_[0]):
            c = float(coef * z[f])
            if abs(c) < 1e-6:
                continue
            contribs.append(
                Contribution(
                    feature=f,
                    raw_value=float(row[f]) if not pd.isna(row[f]) else float("nan"),
                    contribution=c,
                    direction="increases_risk" if c > 0 else "decreases_risk",
                    description=FEATURE_DESCRIPTIONS.get(f, f.replace("_", " ")),
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


def _fit_calibrated(X: pd.DataFrame, y: np.ndarray) -> CalibratedClassifierCV:
    base = HistGradientBoostingClassifier(
        max_depth=5, learning_rate=0.05, max_iter=300,
        l2_regularization=1.0, random_state=42,
    )
    calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=3)
    calibrated.fit(X.to_numpy(), y)
    return calibrated
