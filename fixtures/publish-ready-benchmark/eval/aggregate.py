"""Aggregation + gated publish (synthetic fixture, publish-ready).

Scenario-level bootstrap CIs (fixed seed), rank bands over overlapping CIs, a
pass^k reliability metric with documented semantics, and a single exclusion
entry point that drops the null agent, the sequestered split, and non-default
configs. A completeness gate blocks a partial board.
"""

import json
import random
from collections import defaultdict

NULL_AGENT = "null-agent"
BOOTSTRAP_SEED = 1234
BOOTSTRAP_B = 2000
EXPECTED_MODELS = {"rival-planner", "rival-mini", "acme-tool-1"}


def exclude_non_contestants(rows):
    # Single exclusion entry point: null agent, sequestered-split rows, and any
    # non-default config are all dropped before the public aggregate.
    return [
        r for r in rows
        if r["model"] != NULL_AGENT
        and not r.get("is_sequestered", False)
        and r.get("config", "default") == "default"
    ]


def bootstrap_ci(scenario_scores, seed=BOOTSTRAP_SEED, b=BOOTSTRAP_B):
    rng = random.Random(seed)                       # fixed seed
    ids = list(scenario_scores.keys())
    means = []
    for _ in range(b):
        draw = [scenario_scores[rng.choice(ids)] for _ in ids]  # resample SCENARIOS
        means.append(sum(draw) / len(draw))
    means.sort()
    return means[int(0.025 * b)], means[int(0.975 * b)]


def pass_hat_k(per_scenario_success, k):
    # pass^k = probability ALL k independent runs of a scenario succeed
    # (documented in docs/methodology.md; distinct from pass@k = at-least-one).
    return sum(p ** k for p in per_scenario_success) / len(per_scenario_success)


def rank_bands(board):
    # Cluster models whose CIs overlap into the same band (multiple-comparison
    # guard): a strict 1-2-3 order is not published when CIs overlap.
    ordered = sorted(board.items(), key=lambda kv: kv[1]["score"], reverse=True)
    bands, band = [], []
    for name, cell in ordered:
        if band and cell["ci_high"] < band[-1][1]["ci_low"]:
            bands.append(band)
            band = []
        band.append((name, cell))
    if band:
        bands.append(band)
    return [[n for n, _ in b] for b in bands]


def aggregate(rows):
    rows = exclude_non_contestants(rows)
    by_model = defaultdict(dict)
    for r in rows:
        by_model[r["model"]][r["scenario_id"]] = r["score"]
    board = {}
    for model, scen in by_model.items():
        # MACRO aggregation: mean over per-scenario means (stated in methodology).
        board[model] = {
            "score": sum(scen.values()) / len(scen),
            **dict(zip(("ci_low", "ci_high"), bootstrap_ci(scen))),
        }
    return board


def assert_complete(board):
    # Completeness gate: refuse to publish a board missing an expected model.
    missing = EXPECTED_MODELS - set(board)
    if missing:
        raise SystemExit(f"incomplete board, missing models: {sorted(missing)}")


def main():
    rows = json.load(open("data/results/rows.json"))
    board = aggregate(rows)
    assert_complete(board)                 # gate before publish
    out = {"leaderboard": board, "bands": rank_bands(board)}
    json.dump(out, open("data/results/leaderboard.json", "w"), indent=2)
    # Public-vs-sequestered gap + same-lab tables are written here too when a
    # sequestered run is present (see scripts/publish.py).


if __name__ == "__main__":
    main()
