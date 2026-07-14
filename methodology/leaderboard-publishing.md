# Leaderboard & publishing — the board must show only what it should, and ship what it promises

**What this protects against:** two dismissals. First, "a do-nothing agent ranks mid-board" / "you published your holdout" — the public leaderboard including rows that distort it (null-agent baselines, holdout rows, non-default configs) when they should be excluded. Second, "the table your docs promise is never actually written" — a publish path that dies silently, or a documented surface no pipeline commits. Exclusions stated as intent are not exclusions; they must be enforced by tests, and the publish step must actually ship what the docs describe.

**How to score:** each sub-check is scored independently — `PRESENT` / `PARTIAL` / `ABSENT` / `N/A`. Dimension rolls up: PRESENT only if every applicable sub-check is PRESENT; ABSENT if none are; PARTIAL otherwise.

**Concept-search rule:** grep patterns are one benchmark's vocabulary. A grep miss is weak evidence of ABSENT. Read the aggregation code, the publish/CI workflow, and the docs' description of the board under the target's own names ("scoreboard", "results table", "rankings") before scoring ABSENT.

---

## Sub-checks

### LB1 — A null-agent baseline exists and is excluded from the published board
**Checks:** there is a deterministic do-nothing agent (empty/refusal/echo responses) proving a trivial agent scores near zero on both the judges and any deterministic checks — and it is kept out of the published leaderboard. The null agent is the floor calibration; a mid-board null agent means the metric rewards nothing, and a null agent on the public board is just noise.
**Satisfies (PRESENT):** a null-agent provider run each cycle and dropped at the aggregation entry point, with its low score verifiable — cite the provider and the exclusion.
**PARTIAL:** a null agent exists but is not run regularly, or is run but manually removed from the board rather than excluded in code.
**ABSENT:** no null-agent baseline at all.
**Grep starting points:** `rg -ni "null.?agent|do.?nothing|baseline|echo.?agent|refusal.?agent|floor"`.
**Severity if gap:** no null-agent baseline is INVALIDATING for any "the metric measures real capability" / gameability claim. A null agent that reaches the public board (not excluded) is INVALIDATING.
**Fix:** add a deterministic null-agent provider, run it each cycle, exclude it at the single aggregation entry point, and check its score stays near the floor.

### LB2 — Holdout rows are split out before public aggregation
**Checks:** the public headline is computed over the public corpus only; holdout rows are tagged and separated before public aggregation so holdout scenarios do not silently enter the headline number (and so holdout content is not aggregated into a public surface).
**Satisfies (PRESENT):** holdout rows tagged and filtered out before the public aggregate is computed — cite the split. `N/A` if there is no holdout.
**PARTIAL:** holdout and public rows are mixed in aggregation, or split only by manual convention.
**ABSENT:** holdout rows flow into the public headline with no separation.
**Grep starting points:** `rg -ni "holdout|is_holdout|split|public.?only|filter.*holdout"` in the aggregation.
**Severity if gap:** holdout rows in the public headline is INVALIDATING (the public number is contaminated by private data and the headline is non-comparable).
**Fix:** tag each row public/holdout and filter to public before computing the headline; keep holdout numbers as a separate per-model aggregate.

### LB3 — Non-default configs are kept out of the public aggregate
**Checks:** smoke runs, partial runs, and alternate judge-panel runs are kept out of the public aggregate — a smoke run's tiny sample or an alternate panel's different judges must not silently mix into the headline.
**Satisfies (PRESENT):** runs are tagged by config and only default-config runs enter the public aggregate — cite the filter.
**PARTIAL:** the distinction exists in the data (a config field) but nothing filters on it before aggregation.
**ABSENT:** any run's rows can enter the public aggregate regardless of config.
**Grep starting points:** `rg -ni "smoke|partial|config|default|alternate.?panel|run_type|profile"` in the aggregation.
**Severity if gap:** non-default rows in the public aggregate is INVALIDATING (the headline mixes incomparable runs). If no non-default runs exist yet, HARDENING (defense for the future).
**Fix:** tag runs by config and restrict the public aggregate to default-config runs; add the filter at the aggregation entry point.

### LB4 — Exclusions are guarded by tripwire tests, not just intent
**Checks:** the LB1–LB3 exclusions are enforced by tests that *fail* if an excluded row (null agent, holdout, non-default) reaches the published board — not merely by a comment or a well-behaved code path. A comment is not a guard; the test is what stops a future refactor from silently publishing an excluded row.
**Satisfies (PRESENT):** tests asserting the null agent, holdout rows, and non-default rows never appear in the published board — cite the tests.
**PARTIAL:** exclusion done in code but with no test guarding it; a refactor could reintroduce the row.
**ABSENT:** exclusions are comments or conventions only.
**Grep starting points:** `rg -ln "test_null|test_holdout|test_exclu|test_publish|test_check_publish"` in the tests dir; read them.
**Severity if gap:** an excluded row reaching the board with no tripwire test is INVALIDATING (the board can silently include what it should not). Exclusion in code but untested is HARDENING.
**Fix:** add tests that construct a board including a null-agent/holdout/non-default row and assert the publish path drops it (the test fails if it appears).

### LB5 — A completeness gate blocks a partial leaderboard from publishing silently
**Checks:** if some models failed to run, a completeness gate blocks publication (or clearly marks the board partial) rather than silently shipping a leaderboard missing models — a partial board misleads by omission.
**Satisfies (PRESENT):** a check reading a `models_failed`/completeness signal that blocks or flags publication when the run is incomplete — cite the gate.
**PARTIAL:** completeness is computed but only warned, not gated.
**ABSENT:** a partial run publishes silently with no completeness check.
**Grep starting points:** `rg -ni "complete|models_failed|allow.?partial|check_publish|partial|missing.?model"`.
**Severity if gap:** HARDENING (a partial board is misleading but usually not a wrong number for the models present); rises toward INVALIDATING if the headline ranking is presented as complete when it is not.
**Fix:** add a publish gate that reads the failed-model count and blocks (or explicitly marks) publication when the run is incomplete.

### LB6 — The publish step's added paths actually commit (none are gitignored)
**Checks:** every path the publish/commit step adds is actually committable — none is gitignored. A CI `git add` of a gitignored file exits non-zero and the publish dies before anything ships, so a benchmark can believe it publishes while shipping nothing. Run `git check-ignore` on each path the publish step names.
**Satisfies (PRESENT):** `git check-ignore -v` returns nothing (exit 1) for every path the publish step adds, ideally asserted by a test or CI check — cite the publish step's paths and the check.
**PARTIAL:** paths appear committable by inspection but nothing guards against a future `.gitignore` entry shadowing a publish path.
**ABSENT:** at least one path the publish step adds is gitignored (the publish would die at `git add`).
**Grep starting points:** `rg -n "git add|git commit|git push" .github`; then `git check-ignore -v <each added path>`.
**Severity if gap:** a publish path that is gitignored (publish dies before committing) is INVALIDATING for the publish (nothing ships, or it ships silently broken). Committable-but-unguarded is HARDENING.
**Fix:** ensure no publish path is gitignored; add a CI/test check that runs `git check-ignore` over the publish paths and fails if any is ignored.

### LB7 — Documented surfaces match what CI writes and commits (both directions)
**Checks:** walk both directions between the docs and the pipeline. Every surface the docs promise (a file, a table, a JSON key) is written by some pipeline step *and* shipped by the publish step; and every file the publish step ships is one the docs account for. A computed-but-never-published table, or a doc-promised file CI never commits, is a finding.
**Satisfies (PRESENT):** each documented surface traces to a pipeline step that writes it and a publish step that commits it, and no orphan published file is undocumented — cite the doc surface and the writing/committing step for the load-bearing ones.
**PARTIAL:** most surfaces trace but at least one doc-promised surface is unwired (computed but never published, or never computed).
**ABSENT:** the docs describe a published board/table the pipeline does not actually produce or ship.
**Grep starting points:** list the surfaces the docs name; `rg -ni "leaderboard\.json|latest\.csv|history|robustness|table"` across docs, pipeline, and publish step; confirm each is both written and committed.
**Severity if gap:** a doc-promised surface that is never written or never committed is HARDENING (the docs overstate what exists); escalate to INVALIDATING if a reader would rely on a promised surface that silently does not exist.
**Fix:** wire every doc-promised surface to a pipeline step and the publish step, or remove the promise from the docs; add the surface→step mapping so future audits can walk it.

---

## Dimension roll-up
- **PRESENT:** all applicable sub-checks PRESENT — distorting rows are excluded and tested-out, and the publish path ships exactly the surfaces the docs promise.
- **PARTIAL:** exclusions or publish wiring exist but at least one is untested, unenforced, or unwired.
- **ABSENT:** no null-agent baseline and no exclusion enforcement (LB1/LB4 ABSENT) — score ABSENT, flag INVALIDATING.
