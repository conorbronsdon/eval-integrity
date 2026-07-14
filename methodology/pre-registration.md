# Pre-registration — fix the run's definition before the numbers exist

**What this protects against:** run cherry-picking. If a maintainer can re-run the eval until the numbers look good, or silently retract an unflattering run, the published score means nothing — it is the best of N hidden attempts, not a measurement. Pre-registration fixes the run's definition (models, corpus, judges, seeds, temperatures) on disk *before* any result exists, so the run that ships is the run that was declared.

**How to score:** each sub-check below is scored independently — `PRESENT` / `PARTIAL` / `ABSENT` / `N/A`. The dimension rolls up: `PRESENT` only if every applicable sub-check is PRESENT; `ABSENT` if none are; `PARTIAL` otherwise.

**Concept-search rule:** the grep patterns are one benchmark's vocabulary. A grep miss is weak evidence of ABSENT. Before scoring any sub-check ABSENT, read the run entry point, the CI workflows, and the governance/methodology docs under whatever names the target uses (a "run manifest", "run config frozen at start", or a committed `config.lock` can all be pre-registration).

---

## Sub-checks

### PR1 — Pre-registration artifact exists and records the run's full definition
**Checks:** a single artifact, written by the run, records: the models under test, the exact corpus, the judge panel, the seeds, and the temperatures. All five. A config that omits the corpus identity or the judges does not pin the run.
**Satisfies (PRESENT):** a `pre_registration.json` (or equivalent) that a reader can open and see every one of the five fields, written by the run harness — cite the file and the lines listing each field.
**PARTIAL:** an artifact that records some fields but not all (e.g. models and seeds but no corpus identity or no judge panel), or a config that is hand-maintained rather than emitted by the run.
**ABSENT:** no artifact captures the run definition; the run is defined only by whatever flags happened to be passed.
**Grep starting points:** `rg -i "pre.?regist|preregist|run.?manifest|run.?config|config\.lock"`; then read the run entry point to see what it writes at startup.
**Severity if gap:** ABSENT is INVALIDATING (the run can be re-run and cherry-picked with no record). PARTIAL is INVALIDATING if the missing field is the corpus or the judges (the two most gameable), HARDENING otherwise.
**Fix:** emit a `pre_registration.json` at the top of the run recording models, corpus hash, judge panel, seeds, and temperatures before the first model call.

### PR2 — Corpus is pinned by a canonical whole-corpus hash, not just per-file hashes
**Checks:** the corpus identity is a hash over the *canonically serialized whole scenario set* (e.g. a sha256 of the sorted, normalized scenario list), so that adding, removing, or reordering scenarios changes the hash. Per-file hashes miss set-level edits (a dropped scenario) and ordering.
**Satisfies (PRESENT):** code that serializes the scenario set deterministically (sorted keys, stable ordering) and hashes the whole thing, with the digest stored in the pre-registration artifact — cite the hashing function and the field it writes.
**PARTIAL:** per-file or per-scenario hashes only, or a hash computed over a non-canonical serialization (dict ordering not fixed), so the same corpus can hash differently across runs.
**ABSENT:** the corpus is referenced by path or count only, with no content hash.
**Grep starting points:** `rg -n "sha256|hashlib|blake2|canonical|sort_keys|sorted\("`; read the function that builds the corpus identity.
**Severity if gap:** ABSENT is INVALIDATING for any "same corpus" comparability claim. PARTIAL (per-file only) is HARDENING.
**Fix:** replace per-file hashing with a sha256 over `json.dumps(scenarios, sort_keys=True)` (or a stable canonical form) and store it as the corpus id.

### PR3 — The write-before-run ordering is enforced by a test, not just code layout
**Checks:** the pre-registration is written and flushed to disk *before* the first model or judge call — and that ordering is guarded by a test, because "the write happens to sit above the loop" is one refactor away from breaking silently.
**Satisfies (PRESENT):** a test that asserts the pre-registration file exists on disk at the moment the first model is dispatched (e.g. a fake provider that checks for the file, or a test that runs the harness and asserts the artifact's mtime precedes the first call) — cite the test.
**PARTIAL:** the write clearly precedes the loop in code, but no test guards the ordering.
**ABSENT:** the artifact is written after results are collected (so it can be back-filled to match the numbers), or ordering is unclear.
**Grep starting points:** read the run entry point top-to-bottom; `rg -ln "test_pre_regist|test_prereg|write.*before"` in the tests dir.
**Severity if gap:** written-after-results is INVALIDATING. Correct order but untested is HARDENING.
**Fix:** add a test that dispatches the first model through a stub which asserts the pre-registration file already exists on disk.

### PR4 — No-silent-retraction policy, and published runs are self-describing
**Checks:** a stated policy that runs are never silently re-run or deleted — corrections are a new, dated run — and each published run is timestamped and carries a manifest linking back to its pre-registration by path and hash, so a reader can verify the published numbers came from the declared run.
**Satisfies (PRESENT):** a governance/methodology section stating the append-only-correction policy, plus a published run manifest that references its pre-registration file and hash — cite both.
**PARTIAL:** the policy is stated but runs are not self-describing (no manifest linking numbers back to a pre-registration), or vice versa.
**ABSENT:** no policy and no manifest; nothing stops a maintainer from overwriting `leaderboard.json` in place.
**Grep starting points:** `rg -ni "retract|append.only|never deleted|superseded|immutable|run_id|timestamp" docs`; look for a manifest linking results to a pre-registration.
**Severity if gap:** HARDENING (weakens auditability; a determined reviewer can still ask for the raw run), unless combined with PR1 ABSENT, in which case the run history is unverifiable — treat as INVALIDATING.
**Fix:** add a governance section committing to append-only corrections, and write a per-run manifest that records the run timestamp, run id, and the pre-registration path + hash.

---

## Dimension roll-up
- **PRESENT:** PR1–PR4 all PRESENT — the run is pinned before it exists and the history is auditable.
- **PARTIAL:** an artifact exists (PR1 PRESENT or PARTIAL) but pinning or ordering guarantees are incomplete.
- **ABSENT:** no pre-registration artifact at all (PR1 ABSENT) — score the dimension ABSENT and flag INVALIDATING.
