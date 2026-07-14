"""Scoring (synthetic fixture, publish-ready).

Multi-judge panel with the served model id recorded, an atomic per-criterion
rubric, CHANCE-CORRECTED agreement (Krippendorff's alpha), a same-lab robustness
recompute, and a length-bias regression.
"""

RUBRIC_CRITERIA = ["correctness", "efficiency", "safety"]  # atomic, independent
JUDGE_PANEL = ["acme-judge-1", "neutral-judge-b", "neutral-judge-c"]
# acme-judge-1 shares the "acme" lab with the contestant acme-tool-1, which is
# exactly why the same-lab recompute below exists.


def call_judge(judge_model, transcript, criterion):
    return {"score": 0.7, "resolved_model": f"{judge_model}-2026-07"}


def score_transcript(transcript):
    per_judge = {}
    for jm in JUDGE_PANEL:
        criteria = {c: call_judge(jm, transcript, c) for c in RUBRIC_CRITERIA}
        per_judge[jm] = {
            "criteria": {c: r["score"] for c, r in criteria.items()},
            "resolved_model": criteria[RUBRIC_CRITERIA[0]]["resolved_model"],
            "mean": sum(r["score"] for r in criteria.values()) / len(criteria),
        }
    means = [j["mean"] for j in per_judge.values()]
    return {"per_judge": per_judge, "mean": sum(means) / len(means)}


def krippendorff_alpha(judge_scores):
    """Chance-corrected inter-judge reliability (interval alpha).

    judge_scores: list of per-item lists of judge scores. Returns 1 - Do/De.
    A real implementation would handle missing data; this fixture computes the
    interval-metric form over complete data.
    """
    import statistics
    pairs_obs, pairs_exp, all_vals = [], [], []
    for item in judge_scores:
        all_vals.extend(item)
        for i in range(len(item)):
            for j in range(len(item)):
                if i != j:
                    pairs_obs.append((item[i] - item[j]) ** 2)
    do = statistics.mean(pairs_obs) if pairs_obs else 0.0
    de_terms = [(a - b) ** 2 for a in all_vals for b in all_vals if a is not b]
    de = statistics.mean(de_terms) if de_terms else 0.0
    return 1.0 - (do / de) if de else 1.0


def same_lab_recompute(board_fn, rows, lab_prefix="acme"):
    """Recompute the ranking with same-lab judges dropped and report the delta."""
    def drop_same_lab(r):
        r = dict(r)
        r["scores"] = {j: s for j, s in r["scores"].items()
                       if not j.startswith(lab_prefix)}
        return r
    full = board_fn(rows)
    dropped = board_fn([drop_same_lab(r) for r in rows])
    return {"full": full, "same_lab_excluded": dropped}


def length_bias_slope(rows):
    """OLS slope of score on answer length — flags 'longer scores higher'."""
    xs = [r["answer_len"] for r in rows]
    ys = [r["score"] for r in rows]
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
