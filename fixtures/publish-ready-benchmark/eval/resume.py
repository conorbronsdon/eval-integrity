"""Resume + cost cap for expensive runs (synthetic fixture).

A crash mid-run should not force a full re-pay. Completed (model, scenario) keys
are checkpointed; a cost cap halts the run before it exceeds the configured
budget.
"""

import json
import os
from pathlib import Path

CHECKPOINT = Path("data/results/.checkpoint.json")
MAX_COST_USD = float(os.environ.get("ACME_MAX_COST_USD", "50"))


def load_completed():
    if CHECKPOINT.exists():
        return set(json.loads(CHECKPOINT.read_text()))
    return set()


def mark_completed(key):
    done = load_completed()
    done.add(key)
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(sorted(done)))


def assert_within_budget(spent_usd):
    # Cost cap: halt before exceeding the budget rather than silently overspending.
    if spent_usd > MAX_COST_USD:
        raise SystemExit(f"cost cap hit: ${spent_usd:.2f} > ${MAX_COST_USD:.2f}")
