"""Force a fresh model train and cache it, without booting the API.

    python scripts/train.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["ISTIKSHAF_FORCE_RETRAIN"] = "true"

from app.ml.scorer import get_scorer  # noqa: E402

if __name__ == "__main__":
    scorer = get_scorer()
    latest = scorer.latest_scores()
    print(f"Trained. Analysis month rows: {len(latest)}")
    print(latest["probability"].describe())
