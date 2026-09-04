"""Runtime configuration, sourced from environment variables (or a .env file)."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    """Minimal .env loader so we don't need an extra dependency."""
    env_path = _BACKEND_ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def _resolve(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    return p if p.is_absolute() else (_BACKEND_ROOT / p).resolve()


class Settings:
    def __init__(self) -> None:
        data_env = os.environ.get("ISTIKSHAF_DATA_DIR")
        if data_env:
            self.data_dir = _resolve(data_env)
        elif (_BACKEND_ROOT / "data" / "consumers.csv").exists():
            self.data_dir = _BACKEND_ROOT / "data"
        elif (_BACKEND_ROOT.parent / "data" / "consumers.csv").exists():
            self.data_dir = _BACKEND_ROOT.parent / "data"
        else:
            self.data_dir = _BACKEND_ROOT / "data"
        self.cache_dir: Path = _resolve(os.environ.get("ISTIKSHAF_CACHE_DIR", "./.cache"))
        self.allowed_origins: list[str] = [
            o.strip()
            for o in os.environ.get(
                "ISTIKSHAF_ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if o.strip()
        ]
        # 0.50 is the operating point run_pipeline.py evaluates the calibrated
        # XGBoost model at. The scikit-learn fallback tolerates it too.
        self.risk_threshold: float = float(os.environ.get("ISTIKSHAF_RISK_THRESHOLD", "0.50"))
        self.force_retrain: bool = os.environ.get("ISTIKSHAF_FORCE_RETRAIN", "false").lower() == "true"
        self.analysis_month: str | None = os.environ.get("ISTIKSHAF_ANALYSIS_MONTH") or None

        # Where the real Track-1 pipeline (`run_pipeline.py`) writes its artifacts
        # (`xgboost_model.json`, `final_calibrator.joblib`, `isolation_forest_final.joblib`,
        # `iso_forest_imputer.joblib`). Defaults to the repo root that ships them.
        self.repo_root: Path = _BACKEND_ROOT.parent
        artifacts_env = os.environ.get("ISTIKSHAF_ARTIFACTS_DIR")
        self.artifacts_dir: Path = _resolve(artifacts_env) if artifacts_env else self.repo_root

        # "auto" (default): serve the XGBoost + TreeSHAP pipeline when its artifacts
        # and deps are present, else the scikit-learn fallback. "off" forces the
        # fallback; "on" requires the real pipeline (raises if unavailable).
        self.scorer_backend: str = os.environ.get("ISTIKSHAF_SCORER", "auto").lower()

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def xgb_artifacts(self) -> dict[str, Path]:
        d = self.artifacts_dir
        return {
            "booster": d / "xgboost_model.json",
            "calibrator": d / "final_calibrator.joblib",
            "iso_forest": d / "isolation_forest_final.joblib",
            "iso_imputer": d / "iso_forest_imputer.joblib",
        }

    def xgb_artifacts_present(self) -> bool:
        return all(p.exists() for p in self.xgb_artifacts.values())

    @property
    def track2_artifacts(self) -> dict[str, Path]:
        """Optional AMI-enhanced model (see train_track2_model.py). Absent by
        default — the backend runs fine without it, just with
        smart_meter_probability == monthly_probability for AMI consumers."""
        d = self.artifacts_dir
        return {
            "booster": d / "xgboost_model_track2.json",
            "calibrator": d / "final_calibrator_track2.joblib",
            "iso_forest": d / "isolation_forest_track2.joblib",
        }

    def track2_artifacts_present(self) -> bool:
        return all(p.exists() for p in self.track2_artifacts.values())

    @property
    def model_path(self) -> Path:
        return self.cache_dir / "risk_model.joblib"

    @property
    def db_path(self) -> Path:
        return self.cache_dir / "istikshaf.sqlite3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
