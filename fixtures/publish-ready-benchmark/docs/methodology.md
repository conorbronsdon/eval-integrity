# acme-tool-bench — Methodology

> Synthetic fixture. Every claim below traces to code in `eval/` and `scripts/`.

## Vocabulary

This project calls its private evaluation set the **sequestered split**. It is
the holdout: drawn from outside the repo, recorded only as a hash + count in the
pre-registration, never committed, and never surfaced in CI or the published
board.

## Pre-registration

`eval/pre_registration.py::write_pre_registration` writes, before the first model
call: models under test, a **canonical whole-corpus sha256**
(`canonical_corpus_hash`), the sequestered split as `{sha256, n_scenarios}` only,
the judge panel, the seed, and the temperatures. The write-before-run ordering is
guarded by `tests/test_integrity.py::test_prereg_written_before_first_call`.

**Correction policy: append-only.** Runs are never silently re-run or deleted. A
correction is a new dated run with a new `run_id`; the prior run is retained.

## Contamination

`scripts/generate_data.py::assert_author_allowed` is a **family-aware** hard
assert: the author id and every contestant are normalized to a family key before
the membership check, so a sibling snapshot of an author cannot compete. Every
scenario carries an immutable `author_model` and `provenance: synthetic`. The
public-vs-sequestered **gap table** (`scripts/publish.py::write_gap_table`) is
published per model as an overfitting tripwire.

## Judging

Three judges (`acme-judge-1`, `neutral-judge-b`, `neutral-judge-c`). Each judge's
**served model id** (`resolved_model`) is recorded per call. The rubric is
**atomic** — correctness, efficiency, safety scored independently, aggregated
after scoring. Inter-judge reliability is reported as **Krippendorff's alpha**
(`eval/scoring.py::krippendorff_alpha`), a chance-corrected statistic. Because
`acme-judge-1` shares the `acme` lab with the contestant `acme-tool-1`, a
**same-lab recompute** (`same_lab_recompute`) reports the ranking with acme
judges dropped. A **length-bias** OLS slope (`length_bias_slope`) checks whether
longer answers score higher.

## Statistics

Headline scores carry a **95% bootstrap confidence interval**, resampling
**scenarios** with a fixed seed (`eval/aggregate.py::bootstrap_ci`, seed 1234).
Aggregation is **macro** — the mean of per-scenario means — stated here and
implemented in `aggregate()`. Models whose CIs overlap are clustered into **rank
bands** (`rank_bands`) rather than published as a strict order.

Reliability under repetition is reported as **pass^k** — the probability that
**all k** independent runs of a scenario succeed (`pass_hat_k`) — distinct from
pass@k (at least one of k succeeds). We report pass^k.

## Reproducibility

A single documented run sequence with inputs pinned to `data/public/`. Runs
**resume** from a checkpoint (`eval/resume.py`) and halt at a **cost cap**. The
environment is pinned (`pyproject.toml` == pins + `uv.lock`; runtime pinned in
CI). Judge calls run at temperature 0; where a provider snapshot changes, results
are bounded rather than bit-for-bit — stated, not implied away.

## Publishing

A single exclusion entry point (`exclude_non_contestants`) drops the null-agent
baseline, sequestered-split rows, and non-default configs before aggregation,
each guarded by a tripwire test. A **completeness gate** (`assert_complete`)
blocks a board missing an expected model. The publish step commits exactly three
surfaces — `leaderboard.json`, `gap_table.json`, `same_lab_table.json` — and
asserts none is gitignored before `git add`.
