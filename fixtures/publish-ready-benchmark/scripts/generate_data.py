"""Scenario generation (synthetic fixture, publish-ready).

A FAMILY-AWARE hard assert bars a scenario's author (or any sibling snapshot of
it) from being a contestant, and every scenario is stamped with an immutable
author_model and its synthetic provenance.
"""

from eval.run import MODELS_UNDER_TEST

AUTHOR_MODEL = "gen-writer-x"  # synthetic generator, not a contestant


def family_key(model_id):
    # Normalize to vendor + base model so a sibling snapshot maps to the same key
    # (e.g. "acme-tool-1-0613" and "acme-tool-1-0301" -> "acme-tool-1").
    parts = model_id.split("-")
    return "-".join(parts[:3]) if len(parts) >= 3 else model_id


def assert_author_allowed(author, contestants):
    author_fam = family_key(author)
    banned = {family_key(c) for c in contestants}
    assert author_fam not in banned, f"author family {author_fam} is a contestant"


def make_scenario(scenario_id, prompt, ground_truth):
    assert_author_allowed(AUTHOR_MODEL, MODELS_UNDER_TEST)
    return {
        "id": scenario_id,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "author_model": AUTHOR_MODEL,   # immutable authorship stamp
        "provenance": "synthetic",
    }
