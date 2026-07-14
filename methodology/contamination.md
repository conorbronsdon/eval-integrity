# Contamination — the author's model must not sit for the author's exam

**What this protects against:** the "the author's model graded the author's exam" dismissal, and the slower failure where a public corpus leaks into a contestant's training data and inflates its score. A model that helped build the scenarios (or shares weights with one that did) has an unfair prior; a corpus that is public on the internet may already be memorized. Both make a high score meaningless.

**How to score:** each sub-check is scored independently — `PRESENT` / `PARTIAL` / `ABSENT` / `N/A`. Dimension rolls up: PRESENT only if every applicable sub-check is PRESENT; ABSENT if none are; PARTIAL otherwise.

**Concept-search rule:** grep patterns are one benchmark's vocabulary. A grep miss is weak evidence of ABSENT. Read the data-generation code and the contestant list under the target's own names ("panel", "candidates", "systems under test", "generators") before scoring ABSENT.

---

## Sub-checks

### CT1 — Authors are barred from being contestants, enforced in code at generation
**Checks:** the model(s) that authored/generated a scenario cannot appear as contestants scored on it — and the bar is a hard assertion at generation time, not a convention in a README. A convention is not a guard; a guard fails the run when violated.
**Satisfies (PRESENT):** an assertion in the generation path that raises if the author id is in the contestant set (e.g. `assert author not in MODELS_UNDER_TEST`) — cite the assertion.
**PARTIAL:** the rule is documented ("we don't let authors compete") but no code enforces it; or a filter exists but only warns.
**ABSENT:** no separation of author and contestant anywhere.
**Grep starting points:** `rg -ni "author|assert.*author|contestant|under_test|MODELS_UNDER_TEST|generator"`; read the generation entry point.
**Severity if gap:** ABSENT or PARTIAL (unenforced) is INVALIDATING — the central contamination attack is open.
**Fix:** add a hard assert in the generation path that fails if the author model is (or family-matches) any contestant.

### CT2 — The author-vs-contestant guard is family-aware
**Checks:** the guard matches model *families*, not exact strings. A different snapshot or size of a contestant (e.g. `acme-large-0613` vs `acme-large-0301`, or `acme-large` vs `acme-small`) is still the same lineage and carries the same prior. Exact-string matching lets a sibling snapshot slip through.
**Satisfies (PRESENT):** the guard normalizes to a family/vendor prefix before comparing, with a test exercising the sibling-snapshot case — cite the normalization and the test.
**PARTIAL:** exact-id matching only (blocks `acme-large-0613` competing on its own scenarios but not `acme-large-0301`).
**ABSENT:** no guard at all (this sub-check is moot — score against CT1).
**Grep starting points:** `rg -ni "family|prefix|vendor|normali|snapshot|startswith"`; read the comparison in the CT1 guard.
**Severity if gap:** exact-match-only is INVALIDATING when contestants include multiple snapshots of an author's family; HARDENING when the corpus author is a family with no contestant siblings.
**Fix:** normalize author and contestant ids to a family key (vendor + base model) before the membership check; add a test for the sibling-snapshot case.

### CT3 — Per-scenario authorship is recorded and immutable
**Checks:** every scenario stamps which model authored it (an `author_model` field written at generation and never edited afterward), so the CT1/CT2 guards have ground truth to check against and reviewers can audit provenance.
**Satisfies (PRESENT):** an `author_model` (or equivalent) field present on every scenario record, written at generation — cite the field in the data and the code that stamps it.
**PARTIAL:** authorship recorded for some scenarios but not all, or recorded in a side file that can drift from the scenarios.
**ABSENT:** scenarios carry no authorship record.
**Grep starting points:** `rg -ni "author_model|authored_by|generator|provenance|created_by"` in the data and generation code.
**Severity if gap:** HARDENING on its own, but if CT1's guard depends on this field and it is missing, the guard is unverifiable — escalate to INVALIDATING.
**Fix:** stamp an `author_model` field on each scenario at generation and treat it as immutable (no post-hoc edits).

### CT4 — Corpus provenance is stated; scraped corpora carry a contamination check
**Checks:** the docs state whether the corpus is synthetic or scraped from real sources. If scraped, there is a check against known training sets / public sources for overlap. Synthetic corpora dodge the memorization risk; scraped ones must show they were not already in a contestant's training data.
**Satisfies (PRESENT):** a provenance statement plus, for scraped data, a documented contamination/decontamination check with results — cite both. For fully synthetic corpora, a clear synthetic-provenance statement satisfies this (the check is N/A).
**PARTIAL:** provenance stated but no contamination check on a scraped corpus.
**ABSENT:** provenance unstated — a reader cannot tell whether the corpus could be memorized.
**Grep starting points:** `rg -ni "synthetic|scraped|provenance|contaminat|decontaminat|n-?gram|overlap|training set"` in docs and generation code.
**Severity if gap:** unstated provenance is HARDENING; a scraped corpus with no contamination check is INVALIDATING for any "not memorized" claim.
**Fix:** state provenance in the methodology doc; for scraped data, add and report an n-gram/substring overlap check against known public sources.

### CT5 — A private holdout exists and the public-vs-holdout gap is published per model
**Checks:** when the public corpus is (or will be) on the internet, there is a private holdout drawn from outside the repo, and the leaderboard publishes each model's public score, holdout score, and the *gap* between them. A large gap is the overfitting tripwire — it catches a model that memorized the public set.
**Satisfies (PRESENT):** a holdout run alongside the public run, with per-model public/holdout/gap rows on the board, computed by code — cite the aggregation and a sample row.
**PARTIAL:** a holdout exists but the gap is not computed or not published; or the holdout is described but never actually run.
**ABSENT:** no holdout, on a corpus that is or will be public.
**Grep starting points:** `rg -ni "holdout|hold-out|held-out|sequester|private set|gap|public.vs"`; read the aggregation for a gap column.
**Severity if gap:** ABSENT on a public corpus is INVALIDATING for any generalization claim; HARDENING if the corpus is private-by-construction and stays that way. PARTIAL (holdout exists, gap unpublished) is HARDENING.
**Fix:** stand up a holdout drawn from outside the repo, run it each cycle, and publish a per-model public/holdout/gap row.

---

## Dimension roll-up
- **PRESENT:** CT1–CT5 all PRESENT (or CT4/CT5 genuinely N/A for a private synthetic corpus, documented as such).
- **PARTIAL:** a guard or holdout exists but is unenforced, exact-match-only, or unpublished.
- **ABSENT:** no author/contestant separation (CT1 ABSENT) — score ABSENT, flag INVALIDATING.
