"""Scoring: three-judge panel, atomic rubric (synthetic fixture).

Solid: atomic per-criterion rubric (correctness, safety, clarity) scored
independently, and each judge's served model id recorded. Half-built: inter-judge
agreement is a raw 'within 0.2' rate, NOT chance-corrected (no Krippendorff/kappa),
and there is no length-bias control.
"""

RUBRIC_CRITERIA = ["correctness", "safety", "clarity"]  # atomic, scored separately
JUDGE_PANEL = ["neutral-judge-a", "neutral-judge-b", "neutral-judge-c"]


def call_judge(judge_model, transcript, criterion):
    # Stub: returns a per-criterion score and the served judge model id.
    return {"score": 0.7, "resolved_model": f"{judge_model}-2026-07"}


def score_transcript(transcript):
    per_judge = {}
    for judge_model in JUDGE_PANEL:
        criteria = {c: call_judge(judge_model, transcript, c) for c in RUBRIC_CRITERIA}
        # aggregate atomic criteria into this judge's score AFTER independent scoring
        per_judge[judge_model] = {
            "criteria": {c: r["score"] for c, r in criteria.items()},
            "resolved_model": criteria[RUBRIC_CRITERIA[0]]["resolved_model"],
            "mean": sum(r["score"] for r in criteria.values()) / len(criteria),
        }
    means = [j["mean"] for j in per_judge.values()]
    return {"per_judge": per_judge, "mean": sum(means) / len(means)}


def agreement_within_02(all_judge_means):
    # HARDENING: raw within-0.2 agreement rate, not chance-corrected.
    hits = 0
    total = 0
    for means in all_judge_means:
        for i in range(len(means)):
            for j in range(i + 1, len(means)):
                total += 1
                if abs(means[i] - means[j]) <= 0.2:
                    hits += 1
    return hits / total if total else 0.0
