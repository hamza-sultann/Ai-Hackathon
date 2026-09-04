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
        self.risk_threshold: float = float(os.environ.get("ISTIKSHAF_RISK_THRESHOLD", "0.55"))
        self.force_retrain: bool = os.environ.get("ISTIKSHAF_FORCE_RETRAIN", "false").lower() == "true"
        self.analysis_month: str | None = os.environ.get("ISTIKSHAF_ANALYSIS_MONTH") or None

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def model_path(self) -> Path:
        return self.cache_dir / "risk_model.joblib"

    @property
    def db_path(self) -> Path:
        return self.cache_dir / "istikshaf.sqlite3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
