# Judge validity — is the measuring instrument trustworthy?

**What this protects against:** the family of dismissals that attack the judge itself — "your judge drifted", "your judge favors its own lab", "your judge just rewards length", "one good sentence inflated the whole score", and "your docs describe scoring the code doesn't do". For an LLM-as-judge eval the judge *is* the instrument; an uncalibrated instrument produces uncalibrated numbers.

**How to score:** each sub-check is scored independently — `PRESENT` / `PARTIAL` / `ABSENT` / `N/A`. If there is no LLM judge (scoring is deterministic — exact match, unit tests, regex), the LLM-specific sub-checks are `N/A`; say so and score only what applies. Dimension rolls up: PRESENT only if every applicable sub-check is PRESENT; ABSENT if none are; PARTIAL otherwise.

**Concept-search rule:** grep patterns are one benchmark's vocabulary. A grep miss is weak evidence of ABSENT. Read the scoring/judge code under the target's own names ("grader", "evaluator", "rater", "critic") before scoring ABSENT.

---

## Sub-checks

### JV1 — The judge is pinned to the model actually served, not just the requested ID
**Checks:** each judge call records the model the provider *actually served* (a `resolved_model` returned by the API), not only the requested slug. Hosted model slugs get silently re-pointed to new snapshots; a requested ID alone cannot detect that drift, so a run's judge can change underfoot with no record.
**Satisfies (PRESENT):** a `resolved_model` (or served-model) field captured from each judge response and written into the judge artifact and the flat results row — cite where it is read from the response and where it is stored.
**PARTIAL:** only the requested judge ID is recorded; drift would be invisible.
**ABSENT:** the judge model is not recorded at all per call.
**Grep starting points:** `rg -n "resolved_model|served_model|response.model|actual_model|system_fingerprint"`; read the judge call and what it persists.
**Severity if gap:** not pinned to the served model is INVALIDATING (silent drift makes runs non-comparable).
**Fix:** read the served/resolved model id from each judge API response and persist it in the judge artifact and results row.

### JV2 — Multi-judge agreement is reported and chance-corrected
**Checks:** if a panel of judges is used, inter-judge agreement is reported, and it is *chance-corrected* (Krippendorff's alpha or Cohen's/Fleiss' kappa) rather than a raw "judges agreed within 0.2" rate, which is inflated by the base rate and says little about reliability.
**Satisfies (PRESENT):** a chance-corrected agreement statistic computed and published (per dimension and/or per model) — cite the computation. N/A if there is a single judge.
**PARTIAL:** agreement reported but only as a raw within-X or percent-agreement rate, not chance-corrected.
**ABSENT:** a multi-judge panel with no agreement statistic at all.
**Grep starting points:** `rg -ni "krippendorff|kappa|alpha|agreement|inter.?rater|reliability|concordance"`.
**Severity if gap:** multi-judge with no agreement stat is INVALIDATING (the panel's reliability is unknown). Agreement present but not chance-corrected is HARDENING.
**Fix:** compute Krippendorff's alpha (or kappa) over the per-judge scores and publish it; if a single judge, state that and skip.

### JV3 — Same-lab judge/contestant conflicts get a robustness check
**Checks:** when a contestant shares a lab/family with a judge, there is a same-lab robustness check — the ranking is recomputed with that judge excluded, and the result is compared, to show the ranking is not an artifact of a judge favoring its own family.
**Satisfies (PRESENT):** code that recomputes the board with same-lab judges dropped and reports the delta, plus a test — cite both.
**PARTIAL:** the conflict is acknowledged in prose but no recomputation is done.
**ABSENT:** no same-lab handling, with at least one contestant sharing a lab with a judge.
**Grep starting points:** `rg -ni "same.?lab|same_lab|judge.?family|exclude.?judge|leave.one.out|drop.*judge"`.
**Severity if gap:** a contestant sharing a lab with the (or a) judge and no same-lab check is INVALIDATING *for that contestant's ranking*. HARDENING if no contestant shares a lab with any judge (defense-in-depth only).
**Fix:** add a function that recomputes rankings excluding same-lab judges and reports the delta; add a test asserting it runs and flags a threshold breach.

### JV4 — Length / verbosity bias is measured or controlled
**Checks:** there is a control or regression testing whether longer answers systematically score higher independent of quality — the classic LLM-judge bias. Without it, a model that pads answers can climb the board on verbosity alone.
**Satisfies (PRESENT):** a regression (e.g. OLS of score on answer length) or an explicit length control, with the result reported — cite the computation.
**PARTIAL:** length bias mentioned as a known risk but not measured.
**ABSENT:** no length-bias analysis at all.
**Grep starting points:** `rg -ni "length.?bias|verbosity|word.?count|token.?count|char.?count|ols|regress|slope"`.
**Severity if gap:** HARDENING (weakens credibility; rarely invalidates on its own unless the ranking is known to track length).
**Fix:** add a length-vs-score regression over the scored answers and report the slope and its significance; flag if length explains meaningful variance.

### JV5 — Rubric criteria are atomic, not one global "how good was it" score
**Checks:** the rubric scores independent criteria separately rather than eliciting a single holistic score. A single global score lets a halo effect — one strong dimension inflating the rest — go undetected and unmeasured.
**Satisfies (PRESENT):** a rubric with multiple independently-scored criteria, aggregated after scoring — cite the rubric definition.
**PARTIAL:** multiple criteria named but collapsed into one score before aggregation, so they cannot be inspected separately.
**ABSENT:** a single global quality score with no criterion decomposition.
**Grep starting points:** `rg -ni "rubric|criteri|dimension|atomic|holistic|overall.score|per.criterion"`; read the rubric/prompt.
**Severity if gap:** HARDENING (a global score is weaker but not automatically invalid).
**Fix:** decompose the rubric into independently-scored atomic criteria and aggregate after scoring, so each criterion is inspectable.

### JV6 — Methodology docs describe the scoring the code actually performs
**Checks:** pick 2–3 load-bearing methodology claims about how scoring works (the consensus/aggregation rule, criterion weighting, tie-breaking) and trace each to the code that implements it. Docs that describe different scoring semantics than the code performs mislead every reader of the number.
**Satisfies (PRESENT):** each traced claim matches its implementation — cite the doc claim and the implementing line for each.
**PARTIAL:** most claims trace but at least one is stale or imprecise (e.g. docs say "mean of judges", code takes the median).
**ABSENT:** the docs describe scoring that the code does not perform, or there are no methodology claims to check against.
**Grep starting points:** read the methodology/scoring doc, list its concrete claims, then open the scoring code and match each.
**Severity if gap:** HARDENING at minimum; escalate to INVALIDATING if a published number is *interpreted through* the misdescribed semantics (e.g. the doc's aggregation rule is how a reader would reconstruct the score, and it is wrong).
**Fix:** correct the methodology doc to match the code (or fix the code to match the intended method), and add the traced claim→line mapping to the doc for future audits.

---

## Dimension roll-up
- **N/A:** no LLM judge (deterministic scoring only) — JV1–JV6 are N/A; note it and rely on the other dimensions.
- **PRESENT:** all applicable sub-checks PRESENT — the judge is pinned, reliable, bias-checked, and truthfully documented.
- **PARTIAL:** the judge works but at least one calibration/bias control is missing or unenforced.
- **ABSENT:** judge unpinned and uncalibrated — score ABSENT, flag INVALIDATING (JV1 alone forces this).
