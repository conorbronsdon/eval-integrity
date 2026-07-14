# Holdout hygiene — a private set that leaks is not private

**What this protects against:** the "your private set isn't private — it's in your CI logs" dismissal. Contamination (that dimension) establishes that a holdout *exists*; hygiene establishes that its *content* cannot escape. A holdout leaks the moment its scenarios, ground truth, or per-scenario scores land in a committed file, a public CI artifact, an error message, or a sample in the docs. Once leaked, the next model can train on it and the overfitting tripwire is dead.

**How to score:** each sub-check is scored independently — `PRESENT` / `PARTIAL` / `ABSENT` / `N/A`. If the benchmark has no holdout at all, this whole dimension is `N/A` (the holdout question lives in contamination CT5). Dimension rolls up: PRESENT only if every applicable sub-check is PRESENT; ABSENT if none are; PARTIAL otherwise.

**Concept-search rule:** grep patterns are one benchmark's vocabulary. A grep miss is weak evidence of ABSENT. The target may call the holdout a "sequestered split", "private eval", or "held-out set" — read `.gitignore`, the CI workflows, and the results files under those names before scoring ABSENT.

---

## Sub-checks

### HO1 — Full transcripts and per-evaluation artifacts are gitignored
**Checks:** raw model transcripts, per-scenario traces, and per-evaluation artifacts (which contain holdout text and ground truth) are gitignored so they can never be committed by accident.
**Satisfies (PRESENT):** `.gitignore` entries covering the transcript/artifact/trace directories, ideally with a comment naming the leak reason — cite the lines. A quick `git ls-files` over those paths returning nothing corroborates it.
**PARTIAL:** some artifact paths ignored but not all (e.g. transcripts ignored, traces not), or ignored without a comment so a future contributor removes the entry not knowing why.
**ABSENT:** transcripts/artifacts are committable (or already committed).
**Grep starting points:** `rg -ni "artifact|transcript|trace|raw|holdout" .gitignore`; `git ls-files | rg -i "artifact|transcript|trace"` to see what is actually tracked.
**Severity if gap:** artifacts committed or committable is INVALIDATING. Ignored but uncommented is HARDENING.
**Fix:** gitignore the transcript/artifact/trace directories with a comment naming the holdout-leak reason; remove any already-tracked artifacts with `git rm --cached`.

### HO2 — No public CI workflow exposes the holdout, and a guard refuses to run when it is configured
**Checks:** no public CI workflow sets the holdout directory/env var, and if any workflow uploads artifacts or verbose logs, there is an explicit step that fails the job when the holdout is configured (because the upload would publish holdout content).
**Satisfies (PRESENT):** either no CI touches the holdout at all, or a CI step that exits non-zero when the holdout env/dir is set on a workflow that uploads artifacts — cite the workflow step.
**PARTIAL:** the risk is noted in a comment but nothing enforces it; or the holdout is only run locally by convention.
**ABSENT:** a public workflow sets the holdout and uploads artifacts or logs with no guard.
**Grep starting points:** `rg -ni "holdout|HOLDOUT" .github`; `rg -n "upload-artifact|actions/upload|::group::|set -x" .github`.
**Severity if gap:** holdout reachable via a public artifact upload is INVALIDATING. Local-only-by-convention with no guard is HARDENING.
**Fix:** add a CI step asserting the holdout env/dir is unset before any artifact upload, exiting non-zero if it is set.

### HO3 — In the pre-registration, the holdout is recorded as hash + count only
**Checks:** the pre-registration records the holdout by hash and scenario *count* only — no scenario IDs, no per-scenario index — unlike the public set which can carry a full index. A per-scenario index of the holdout is itself a partial leak (it reveals structure and size distribution and gives a target to memorize against).
**Satisfies (PRESENT):** a holdout block in the pre-registration with a sha256 and `n_scenarios` and nothing else — cite the block; contrast with the public block that carries the index.
**PARTIAL:** the holdout block carries a count and hash but also scenario IDs, or is indexed identically to the public set.
**ABSENT:** holdout not represented in the pre-registration, or represented with full content/index.
**Grep starting points:** read the pre-registration artifact/code; `rg -ni "holdout.*hash|holdout.*count|n_scenarios|holdout_set"`.
**Severity if gap:** holdout scenario IDs/index in the pre-registration is INVALIDATING (leak). Holdout simply absent from the pre-registration is HARDENING (weakens auditability).
**Fix:** represent the holdout in the pre-registration as `{sha256, n_scenarios}` only; drop any per-scenario IDs or index for the holdout.

### HO4 — Published outputs carry no holdout scenario IDs, text, ground truth, or per-scenario scores
**Checks:** the published leaderboard/results files contain only per-model *aggregates* for the holdout — never holdout scenario IDs, prompt text, ground-truth answers, or per-scenario scores. Per-scenario holdout scores are a reconstruction vector.
**Satisfies (PRESENT):** the results files carry holdout numbers only as per-model aggregates; a scan of `leaderboard.json`/`latest.csv` shows no holdout scenario-level fields — cite the aggregate schema and note the scan.
**PARTIAL:** holdout aggregates published but the results schema *could* carry per-scenario holdout rows and nothing prevents it.
**ABSENT:** published files contain holdout scenario IDs, text, ground truth, or per-scenario scores.
**Grep starting points:** read the published results files; `rg -ni "holdout" data results *.json *.csv | rg -ni "id|text|prompt|ground_truth|per_scenario|scenario_id"`.
**Severity if gap:** any holdout scenario-level content in a published file is INVALIDATING.
**Fix:** restrict published holdout data to per-model aggregates; add a serialization guard that drops scenario-level fields for holdout rows before publish.

### HO5 — Holdout content cannot surface in error messages or committed samples
**Checks:** error paths and logging do not echo holdout scenario text or ground truth (a stack trace that prints the failing scenario is a leak into CI logs), and no "example scenario" committed in the docs is drawn from the holdout.
**Satisfies (PRESENT):** error/logging paths redact or reference holdout scenarios by opaque id/hash rather than content; doc examples are explicitly synthetic or drawn from the public set — cite the redaction and the example provenance.
**PARTIAL:** logging is generally safe but at least one error path prints scenario content; or example provenance is unclear.
**ABSENT:** error paths print holdout content, or a committed sample is from the holdout.
**Grep starting points:** `rg -n "raise|except|print\(|log\.(error|info).*scenario|f\".*{scenario"` in the run/scoring code; check doc examples against the holdout.
**Severity if gap:** holdout content in an error message that reaches public CI logs is INVALIDATING; an ambiguous doc example is HARDENING.
**Fix:** redact scenario content from error/log output for holdout scenarios (reference by hash), and label doc examples as synthetic or public-set-derived.

---

## Dimension roll-up
- **N/A:** no holdout exists — this dimension does not apply; the holdout-existence question is contamination CT5.
- **PRESENT:** HO1–HO5 all PRESENT — the holdout's content has no path out.
- **PARTIAL:** the holdout exists and some containment is in place, but at least one leak path is open or unenforced.
- **ABSENT:** artifacts committable and holdout content reachable — score ABSENT, flag INVALIDATING.
