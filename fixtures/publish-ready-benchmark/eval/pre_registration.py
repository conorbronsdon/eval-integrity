"""Pre-registration writer (synthetic fixture, publish-ready).

Writes the run definition BEFORE the eval loop. Uses a CANONICAL whole-corpus
sha256 (sorted, serialized set), records all five fields, and represents the
sequestered split (this project's name for the holdout) as hash + count only.
"""

import hashlib
import json
import time
from pathlib import Path

JUDGE_PANEL = ["acme-judge-1", "neutral-judge-b", "neutral-judge-c"]
TEMPERATURES = {"contestant": 0.0, "judge": 0.0}


def canonical_corpus_hash(scenarios):
    # Whole-corpus hash: sha256 over the canonically serialized set. Adding,
    # dropping, or reordering a scenario changes the digest.
    blob = json.dumps(sorted(scenarios, key=lambda s: s["id"]), sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def sequestered_block(split_dir):
    # The sequestered split (holdout) is recorded as hash + count ONLY.
    # No scenario IDs, no per-scenario index — unlike the public set.
    scenarios = json.load(open(Path(split_dir) / "scenarios.json"))
    blob = json.dumps(sorted(scenarios, key=lambda s: s["id"]), sort_keys=True).encode()
    return {"sha256": hashlib.sha256(blob).hexdigest(), "n_scenarios": len(scenarios)}


def write_pre_registration(models, public_scenarios, split_dir, seed, path):
    prereg = {
        "run_id": f"run-{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models_under_test": models,
        "corpus_sha256": canonical_corpus_hash(public_scenarios),
        "sequestered_split": sequestered_block(split_dir) if split_dir else None,
        "judge_panel": JUDGE_PANEL,
        "seed": seed,
        "temperatures": TEMPERATURES,
        # Append-only correction policy: see docs/methodology.md. Runs are never
        # silently re-run; a correction is a new dated run linked by run_id.
        "correction_policy": "append-only",
    }
    Path(path).write_text(json.dumps(prereg, indent=2, sort_keys=True))
    return prereg
