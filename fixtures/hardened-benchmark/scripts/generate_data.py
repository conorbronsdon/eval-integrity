"""Scenario generation (synthetic fixture).

Solid: a hard assert bars a scenario's author from being a contestant, and every
scenario is stamped with an immutable author_model. Half-built: the guard is
EXACT-MATCH only (not family-aware) — a sibling snapshot of an author could slip
through if it were a contestant.
"""

from eval.run import MODELS_UNDER_TEST

AUTHOR_MODEL = "gen-writer-x"  # synthetic generator, not a contestant


def assert_author_allowed(author, contestants):
    # Exact-string membership only. A family-aware guard would normalize both
    # sides to a vendor/base key before comparing.
    assert author not in contestants, f"author {author} is a contestant"


def make_scenario(scenario_id, prompt, ground_truth):
    assert_author_allowed(AUTHOR_MODEL, MODELS_UNDER_TEST)
    return {
        "id": scenario_id,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "author_model": AUTHOR_MODEL,   # immutable authorship stamp
        "provenance": "synthetic",       # stated: synthetic, not scraped
    }
