"""Aggregation + publish (synthetic fixture).

Solid: scenario-level bootstrap CIs with a FIXED seed; the null-agent baseline
and holdout rows are excluded before the public aggregate. Half-built: smoke /
non-default configs are NOT filtered, micro-vs-macro is unstated, and there is no
completeness gate blocking a partial board.
"""

import json
import random
from collections import defaultdict

NULL_AGENT = "null-agent"        # deterministic do-nothing baseline, excluded
BOOTSTRAP_SEED = 1234
BOOTSTRAP_B = 2000


def exclude_non_contestants(rows):
    # Drop the null-agent baseline and holdout rows before public aggregation.
    return [r for r in rows if r["model"] != NULL_AGENT and not r["is_holdout"]]
    # NOTE: r["config"] (e.g. "smoke") is NOT filtered here — non-default runs
    # could enter the public aggregate.


def bootstrap_ci(scenario_scores, seed=BOOTSTRAP_SEED, b=BOOTSTRAP_B):
    # Resample SCENARIOS (not correlated per-run rows) with a fixed seed.
    rng = random.Random(seed)
    ids = list(scenario_scores.keys())
    means = []
    for _ in range(b):
        draw = [scenario_scores[rng.choice(ids)] for _ in ids]
        means.append(sum(draw) / len(draw))
    means.sort()
    return means[int(0.025 * b)], means[int(0.975 * b)]


def aggregate(rows):
    rows = exclude_non_contestants(rows)
    by_model = defaultdict(dict)
    for r in rows:
        by_model[r["model"]][r["scenario_id"]] = r["score"]
    board = {}
    for model, scen in by_model.items():
        point = sum(scen.values()) / len(scen)  # micro vs macro NOT stated
        lo, hi = bootstrap_ci(scen)
        board[model] = {"score": point, "ci_low": lo, "ci_high": hi}
    return board


def main():
    rows = json.load(open("data/results/rows.json"))
    board = aggregate(rows)
    # No completeness gate: publishes even if a model is missing.
    json.dump(board, open("data/results/leaderboard.json", "w"), indent=2)


if __name__ == "__main__":
    main()
