# Statistical honesty — is sampling noise being sold as signal?

**What this protects against:** the "that ranking is just noise" dismissal. A benchmark that reports point estimates with no uncertainty, conflates different reliability metrics, or hides that its ranking flips under resampling is selling noise as signal. Honest statistics let a reader see how much of the gap between models is real.

**How to score:** each sub-check is scored independently — `PRESENT` / `PARTIAL` / `ABSENT` / `N/A`. Dimension rolls up: PRESENT only if every applicable sub-check is PRESENT; ABSENT if none are; PARTIAL otherwise.

**Concept-search rule:** grep patterns are one benchmark's vocabulary. A grep miss is weak evidence of ABSENT. Read the aggregation/reporting code under the target's own names ("intervals", "error bars", "resample", "spread") before scoring ABSENT.

---

## Sub-checks

### ST1 — Headline numbers carry confidence intervals from a fixed-seed bootstrap
**Checks:** every headline number (efficacy, composite score, ranking position) is published with a confidence interval, and the interval is computed reproducibly — a bootstrap with a fixed seed, not a one-off unseeded resample that changes each run.
**Satisfies (PRESENT):** a bootstrap (B replicates, fixed seed) producing `ci_low`/`ci_high` on each headline number, with the CI published — cite the bootstrap and the published interval.
**PARTIAL:** intervals computed but seed not fixed (CIs jitter run to run), or intervals computed but not published alongside the headline number.
**ABSENT:** point estimates only, no intervals.
**Grep starting points:** `rg -ni "bootstrap|confidence|ci_low|ci_high|percentile|interval|error.?bar|std.?err"`.
**Severity if gap:** no CIs on a headline ranking built from few scenarios is INVALIDATING (the ranking may be noise). CIs present but unseeded is HARDENING.
**Fix:** add a fixed-seed bootstrap over the scenarios producing `ci_low`/`ci_high` for each headline number and publish the intervals.

### ST2 — The bootstrap resamples the correct unit (scenarios, not correlated rows)
**Checks:** the bootstrap resamples the independent unit — scenarios — not per-run rows, which are correlated (multiple runs of the same scenario are not independent draws). Resampling correlated rows understates the interval and manufactures false precision.
**Satisfies (PRESENT):** the resampling unit is the scenario (resample scenario ids, then aggregate their runs), verified in code and ideally a test — cite the resampling code.
**PARTIAL:** a bootstrap exists but resamples rows/records directly, ignoring the scenario correlation structure.
**ABSENT:** no bootstrap (score against ST1).
**Grep starting points:** read the bootstrap; `rg -ni "resample|scenario|per.?run|per.?row|cluster|group"`.
**Severity if gap:** resampling correlated rows is INVALIDATING for the interval (it is too narrow); the published CI understates uncertainty.
**Fix:** resample at the scenario level (draw scenario ids with replacement, then aggregate within each drawn scenario) so the CI reflects scenario-level uncertainty.

### ST3 — Micro vs macro aggregation is stated
**Checks:** the docs state whether headline aggregation is micro (per-record mean) or macro (per-scenario mean), because they differ whenever scenarios have unequal run counts — and the choice changes the ranking. An unstated choice hides a methodological degree of freedom.
**Satisfies (PRESENT):** an explicit statement of micro vs macro in the methodology, matching what the code computes — cite both.
**PARTIAL:** the code clearly does one or the other but the docs do not say which.
**ABSENT:** neither stated nor discernible; aggregation is opaque.
**Grep starting points:** `rg -ni "micro|macro|per.?scenario|per.?row|per.?record|unweighted|weighted mean"`.
**Severity if gap:** HARDENING (a reviewer can reconstruct it from code), unless run counts are wildly unequal and the choice flips the ranking — then INVALIDATING.
**Fix:** state the aggregation level in the methodology doc and confirm the code matches; prefer macro (per-scenario) when run counts are unequal.

### ST4 — pass@k vs pass^k is disambiguated
**Checks:** if a reliability-under-repetition metric is reported, the docs disambiguate pass@k (at least one of k succeeds) from pass^k (all k succeed) and state which is used — they are different claims and conflating them misrepresents reliability. `N/A` if no such metric is reported.
**Satisfies (PRESENT):** the metric's semantics (at-least-one vs all-k) stated in the docs and matching the code — cite both.
**PARTIAL:** a pass-at-k style metric reported but its semantics not stated.
**ABSENT:** the metric is reported and its semantics are wrong or contradicted by the code.
**Grep starting points:** `rg -ni "pass@|pass\^|pass_at|pass_hat|at least one|all.?k|reliability|k.?runs"`.
**Severity if gap:** conflated or mislabeled pass@k/pass^k is INVALIDATING (different claim than the number supports). Semantics merely unstated is HARDENING.
**Fix:** state explicitly whether the metric is pass@k or pass^k, define it, and confirm the code computes the stated one.

### ST5 — Seeds are fixed and recorded; irreducible non-determinism is stated
**Checks:** seeds are fixed and recorded so a run is reproducible, and where determinism is impossible (temperature > 0, unseeded simulators) that is stated honestly rather than implied away.
**Satisfies (PRESENT):** seeds set and recorded in the run config/pre-registration, with an explicit caveat naming any irreducible non-determinism — cite the seed handling and the caveat.
**PARTIAL:** seeds set in code but not recorded in the run artifact, or non-determinism unacknowledged.
**ABSENT:** no seed control anywhere.
**Grep starting points:** `rg -n "seed|SEED|random_state|np.random|torch.manual_seed|PYTHONHASHSEED"`.
**Severity if gap:** HARDENING on its own (overlaps reproducibility RE1); escalate if the lack of seeds means the published number cannot be reproduced at all.
**Fix:** set and record all seeds in the run artifact; add a one-line caveat where non-determinism is irreducible.

### ST6 — Multiple-comparison risk is acknowledged
**Checks:** with many models × dimensions compared, the multiple-comparison risk (some gaps look significant by chance) is acknowledged — via rank bands that cluster models whose CIs overlap, or a minimum-scenario-count gate before a ranking publishes.
**Satisfies (PRESENT):** rank bands by CI overlap, or a documented minimum-N gate, or an explicit multiple-comparison correction — cite it.
**PARTIAL:** the risk is mentioned but nothing operationalizes it (no bands, no gate).
**ABSENT:** many comparisons published as a strict ranking with no acknowledgement.
**Grep starting points:** `rg -ni "rank.?band|multiple comparison|bonferroni|minimum.*scenario|min.?n|overlap|tie|cluster"`.
**Severity if gap:** HARDENING on an otherwise CI'd board; rises toward INVALIDATING if a strict ranking with no bands is the headline and the top gaps are within CI of each other.
**Fix:** cluster models into rank bands when their CIs overlap, and/or gate ranking publication on a minimum scenario count.

---

## Dimension roll-up
- **PRESENT:** all applicable sub-checks PRESENT — uncertainty is quantified, aggregation is stated, and reliability metrics are unambiguous.
- **PARTIAL:** some uncertainty reporting exists but at least one gap (unseeded CIs, unstated aggregation, unacknowledged multiplicity) remains.
- **ABSENT:** point estimates with no intervals (ST1 ABSENT) — score ABSENT, flag INVALIDATING when the ranking is the headline.
