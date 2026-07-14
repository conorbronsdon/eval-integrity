"""acme-tool-bench run harness (synthetic fixture, publish-ready).

Writes the pre-registration BEFORE any model call (guarded by
tests/test_integrity.py::test_prereg_written_before_first_call), sets and records
the seed, and captures the served model id per call. Supports resume so a crash
does not force a full re-pay.
"""

import argparse
import json
import os
import random
from pathlib import Path

from eval.pre_registration import write_pre_registration
from eval.scoring import score_transcript
from eval.resume import load_completed, mark_completed

MODELS_UNDER_TEST = ["rival-planner", "rival-mini", "acme-tool-1"]
PUBLIC_DIR = "data/public"
# Set to a private path OUTSIDE the repo. Named "sequestered split" here.
SEQUESTERED_DIR = os.environ.get("ACME_SEQUESTERED_DIR")


def call_model(model, prompt):
    return {"text": f"<{model}: {prompt[:16]}>", "resolved_model": f"{model}-2026-07"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()
    random.seed(args.seed)

    public = json.load(open(Path(PUBLIC_DIR) / "scenarios.json"))
    # Pre-registration written BEFORE the first model call.
    write_pre_registration(
        MODELS_UNDER_TEST, public, SEQUESTERED_DIR, args.seed, "pre_registration.json"
    )

    done = load_completed()
    rows = []
    for model in MODELS_UNDER_TEST:
        for sc in public:
            key = f"{model}:{sc['id']}"
            if key in done:
                continue  # resume: skip already-scored work
            out = call_model(model, sc["prompt"])
            result = score_transcript(out["text"])
            rows.append({
                "model": model,
                "resolved_model": out["resolved_model"],
                "scenario_id": sc["id"],
                "is_sequestered": False,
                "config": "default",
                "scores": result["per_judge"],
                "score": result["mean"],
                "answer_len": len(out["text"]),
            })
            mark_completed(key)
    Path("data/results").mkdir(parents=True, exist_ok=True)
    json.dump(rows, open("data/results/rows.json", "w"), indent=2)


if __name__ == "__main__":
    main()
