"""Pre-registration writer (synthetic fixture).

Writes the run definition to disk BEFORE the eval loop starts. Records models,
corpus hash, judge panel, seeds, and temperatures. Deliberately half-built: the
corpus hash is per-file, not a canonical whole-corpus hash, and no test guards
the write-before-run ordering.
"""

import hashlib
import json
import time
from pathlib import Path

JUDGE_PANEL = ["neutral-judge-a", "neutral-judge-b", "neutral-judge-c"]
TEMPERATURES = {"contestant": 0.0, "judge": 0.0}


def per_file_hashes(corpus_dir):
    # NOTE: per-file hashes only. A dropped scenario or a reordering of the set
    # is not detected — this should be a sha256 over the canonical serialized set.
    out = {}
    for p in sorted(Path(corpus_dir).glob("*.json")):
        out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def holdout_block(holdout_dir):
    # Correct: holdout recorded as hash + count only, no scenario IDs or index.
    scenarios = json.load(open(Path(holdout_dir) / "scenarios.json"))
    blob = json.dumps(scenarios, sort_keys=True).encode()
    return {"sha256": hashlib.sha256(blob).hexdigest(), "n_scenarios": len(scenarios)}


def write_pre_registration(models, corpus_dir, holdout_dir, seed, path):
    prereg = {
        "run_id": f"run-{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models_under_test": models,
        "corpus_file_hashes": per_file_hashes(corpus_dir),
        "holdout_set": holdout_block(holdout_dir) if holdout_dir else None,
        "judge_panel": JUDGE_PANEL,
        "seed": seed,
        "temperatures": TEMPERATURES,
    }
    Path(path).write_text(json.dumps(prereg, indent=2, sort_keys=True))
    return prereg
