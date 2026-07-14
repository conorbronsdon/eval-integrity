# acme-code-eval — Methodology

> Synthetic fixture. Describes the scoring the code in `eval/` actually performs,
> with two honestly-flagged gaps.

## Scoring

Each transcript is graded by a **three-judge panel** (`neutral-judge-a/b/c`). Each
judge scores three **atomic criteria** independently — correctness, safety,
clarity — implemented in `eval/scoring.py::score_transcript`. A judge's score is
the mean of its criteria; the transcript score is the mean across judges. This
matches the code: no single holistic score is elicited.

Each judge call records the **served model id** (`resolved_model`) so a silent
provider re-point is detectable.

## Statistics

The public leaderboard reports each model's score with a **95% bootstrap
confidence interval**, resampling **scenarios** (not per-run rows) with a fixed
seed (`eval/aggregate.py::bootstrap_ci`, seed 1234).

## Judge agreement

We report inter-judge agreement as a **within-0.2 rate**. This is not yet
chance-corrected (no Krippendorff's alpha / kappa) — a known limitation.

## Length bias

We consider length/verbosity bias a real judge risk but **do not yet regress
score on answer length**. Tracked as a rough edge, not yet controlled.

## Robustness table

A per-model **public-vs-holdout gap table** and a **same-lab robustness table**
are described here as the intended robustness surface. NOTE: neither table is
currently written by any pipeline step or shipped by the publish step — this
section describes intent, not a produced artifact.
