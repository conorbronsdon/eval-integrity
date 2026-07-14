"""acme-code-eval run harness (synthetic fixture).

Writes the pre-registration BEFORE dispatching any model (correct ordering, but
no test guards it), sets and records the seed, and captures the served model id
from each provider response.
"""

import argparse
import json
import random
from pathlib import Path

from eval.pre_registration import write_pre_registration
from eval.scoring import score_transcript

MODELS_UNDER_TEST = ["rival-coder-7b", "rival-mini", "acme-fix-1"]
PUBLIC_DIR = "data/public"
HOLDOUT_DIR = None  # set to a private path outside the repo at run time


def call_model(model, prompt):
    # Stub. A real provider returns the served model id; we record it.
    return {"text": f"<{model}: {prompt[:16]}>", "resolved_model": f"{model}-2026-07"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()

    random.seed(args.seed)  # seed fixed and recorded in the pre-registration

    # Pre-registration written BEFORE the first model call.
    write_pre_registration(
        MODELS_UNDER_TEST, PUBLIC_DIR, HOLDOUT_DIR, args.seed, "pre_registration.json"
    )

    scenarios = json.load(open(Path(PUBLIC_DIR) / "scenarios.json"))
    rows = []
    for model in MODELS_UNDER_TEST:
        for sc in scenarios:
            out = call_model(model, sc["prompt"])
            result = score_transcript(out["text"])
            rows.append({
                "model": model,
                "resolved_model": out["resolved_model"],  # served model recorded
                "scenario_id": sc["id"],
                "is_holdout": False,
                "config": "default",
                "scores": result["per_judge"],
                "score": result["mean"],
            })
    Path("data/results").mkdir(parents=True, exist_ok=True)
    json.dump(rows, open("data/results/rows.json", "w"), indent=2)


if __name__ == "__main__":
    main()
