---
name: eval-integrity
description: Read-only audit of an LLM evaluation or benchmark repo for integrity and credibility. Use when asked to "audit my benchmark," "is my eval trustworthy," "check my leaderboard for contamination," "review this benchmark's methodology," or "what would a reviewer attack in my eval." Scores seven dimensions with file:line evidence, severity, and fixes; writes a result.json.
argument-hint: "[path-to-benchmark-repo]"
---

# eval-integrity — Benchmark Credibility Audit

Read-only auditor for LLM evaluation and benchmark repos. It answers one question: **if you published this benchmark's numbers, would they survive an adversarial reviewer?**

Most benchmark repos have a runner and a leaderboard but lack the integrity scaffolding that makes a published score mean what it appears to mean. This skill checks for that scaffolding across seven dimensions, names what is missing, rates whether each gap *invalidates published numbers* or is *nice-to-have*, and emits both a markdown report and a `result.json` for trend-tracking.

**Invocation:** deliberately model-invocable — it is a read-only audit. It reports and offers fixes; it never edits the benchmark, re-runs an eval, or touches a leaderboard.

**Read-only guarantee:** this skill does not modify the target repo as part of the audit. No `Edit`/`Write` to the target, no eval re-run, no leaderboard write, no git mutation. The only file it writes is the audit output (report + `result.json`), and only where the user asks it to.

## When to Use
- Before submitting a benchmark to a grant, conference, or public leaderboard.
- When someone says "I don't trust those numbers" and you need to know if they're right.
- After building an eval, before publishing the first headline result.
- Periodically, as a benchmark accretes models and the leaderboard becomes load-bearing.

## When NOT to Use
- A repo that is not an eval or benchmark (no scoring, no leaderboard, no judge). Nothing to grade.
- A toy eval with no published numbers and no intent to publish. Integrity scaffolding is overhead until someone relies on the score.

---

## The seven dimensions

Each maps to a way a benchmark's numbers get dismissed in review. Each has its own methodology file with individually-scoreable sub-checks — read the file for the dimension you are auditing.

| # | Dimension | Methodology file | The question it asks |
|---|-----------|------------------|----------------------|
| 1 | Pre-registration | [methodology/pre-registration.md](methodology/pre-registration.md) | Is the run's definition fixed on disk *before* results exist, so runs can't be cherry-picked? |
| 2 | Contamination | [methodology/contamination.md](methodology/contamination.md) | Are corpus authors (and their family) barred as contestants? Is there a private holdout with a published gap? |
| 3 | Holdout hygiene | [methodology/holdout-hygiene.md](methodology/holdout-hygiene.md) | Can holdout content leak — via CI logs, artifacts, committed transcripts, or error messages? |
| 4 | Judge validity | [methodology/judge-validity.md](methodology/judge-validity.md) | Is the judge pinned to the served model? Chance-corrected agreement? Same-lab, length, halo controls? |
| 5 | Statistical honesty | [methodology/statistical-honesty.md](methodology/statistical-honesty.md) | Do headline numbers carry CIs? Micro vs macro? pass@k vs pass^k? Multiple-comparison risk? |
| 6 | Reproducibility | [methodology/reproducibility.md](methodology/reproducibility.md) | Is there a deterministic re-run path, cost caps/resume, and a pinned environment? |
| 7 | Leaderboard & publishing | [methodology/leaderboard-publishing.md](methodology/leaderboard-publishing.md) | Are null-agent/holdout/non-default rows kept out by tripwire tests, and does the publish path ship what the docs promise? |

---

## Step 1 — Confirm the target is a benchmark and locate its parts

Target: **$ARGUMENTS** (path to the benchmark repo; if empty, use the current directory).

Establish the repo is gradable, then map where the audit will look. From the target repo root:

```bash
rg -l --hidden -g '!.git' "judge|rubric|score|grade|leaderboard|eval" .   # scoring/judging present?
rg -l "leaderboard|results|latest\.csv|\.parquet" .                        # where results live
rg -l -i "methodology|governance|contamination|pre.?registration" .        # stated methodology?
```

If none hit, the repo is probably not a benchmark. Stop and say so.

Record for the audit:
- Absolute repo path.
- Branch + HEAD commit SHA (`git rev-parse HEAD`; if the tree is dirty, note `uncommitted`).
- The scoring entry point(s), the results directory, and any methodology/governance docs.
- Open PRs (`gh pr list` when available). Verify any relevant PR against its actual diff. A finding an in-flight PR already fixes is reported as `KNOWN / IN-FLIGHT`, not a gap, and is excluded from gap counts.

## Step 2 — Audit each dimension (subagent per dimension, or sequential inline)

**Preferred (parallel):** spawn one subagent per dimension in a single tool-call batch so they run in parallel. Each subagent gets:
1. Repo path (absolute), branch, HEAD SHA.
2. The located scoring/results/docs from Step 1.
3. Its dimension's methodology file — the subagent **reads `methodology/<dimension>.md` and scores every sub-check in it**.
4. The report contract (Step 4), capped at ~400 words.

**Fallback (sequential inline):** if there is no subagent/Task tool, do not skip or thin the audit. Read each methodology file and run its sub-checks yourself, one dimension after another in dimension order. Same files, same evidence bar, same report contract. Note in the report that the audit ran sequentially with a single auditor.

Small repos (one scoring file, no CI, no leaderboard) can be audited inline even when subagents are available — parallelism pays off on a real benchmark with CI, a results pipeline, and a methodology doc.

## Step 3 — Scoring rule (applied to every sub-check)

Score each **sub-check** (not just each dimension) independently, then roll sub-checks up to a dimension status. This granularity is the point: a dimension is a roll-up of its sub-checks, never a single verdict.

- **PRESENT** — implemented AND enforced (code or a test, not just prose). Cite `file:line`.
- **PARTIAL** — documented or half-built. The intent exists; the enforcement does not.
- **ABSENT** — no evidence in code, tests, or docs.
- **N/A** — the sub-check does not apply (e.g. judge-validity sub-checks on a benchmark with no LLM judge).

Roll-up: a dimension is **PRESENT** only when every applicable sub-check is PRESENT; **ABSENT** when none are; **PARTIAL** otherwise. **N/A** when every sub-check is N/A.

**Evidence is mandatory.** A rating with no `file:line` (or an explicit "searched X, Y, Z — found nothing") is not a finding, it's a guess. Reject it.

**A grep miss alone does not establish ABSENT.** The methodology files' grep patterns carry one benchmark's vocabulary; the target may name the same concept differently (a holdout called a "sequestered split", a judge called a "grader"). **Search by concept** — read the scoring entry points, the CI workflows, and the docs under the target's own names — before rating any sub-check ABSENT. This rule is load-bearing; a false ABSENT is a false accusation.

## Step 4 — Severity (per gap)

Severity is about consequence, not effort:

- **INVALIDATING** — the gap means a published number could be wrong, gamed, or non-comparable, and a reviewer who finds it can dismiss the result. (No author-is-contestant guard; judge not pinned to the served model; holdout reachable in CI artifacts; no CIs on a headline ranking from few scenarios; a null-agent or holdout row on the public board with no tripwire test.)
- **HARDENING** — the gap weakens credibility or auditability but does not by itself invalidate a number. (Agreement present but not chance-corrected; no resume/cost-cap on an expensive run; environment pinned in prose but not a lockfile; multiple-comparison risk unacknowledged on an otherwise CI'd board.)

Each sub-check's methodology file states its severity rule; when unsure, ask: *can a critic use this gap to throw out the headline number?* If yes, INVALIDATING.

## Step 5 — Verification pass

Before writing the report, verify the collected findings — do not trust a sub-report's rating at face value:
- **Spot-check every ABSENT.** Re-open the cited search scope and confirm the concept search actually happened (not just a grep). A false ABSENT is the most damaging error this skill can make.
- **Confirm every non-PRESENT rating carries evidence** (a `file:line` or an explicit searched-and-found-nothing note). Drop any rating that doesn't.
- **Re-verify in-flight PR claims** against the actual diff, not the PR title.
- **Check the roll-up arithmetic:** dimension status follows from its sub-checks; the verdict follows from the dimensions.

## Step 6 — Emit the report AND result.json

Write **both** outputs.

**(a) Markdown report** — lead with the verdict and the invalidating gaps:

```
EVAL-INTEGRITY AUDIT — <repo> @ <short-sha> — <date>

VERDICT: <PUBLISH-READY | NOT PUBLISH-READY (N INVALIDATING) | GRADABLE WITH CAVEATS | NOT A BENCHMARK>
Sub-checks: <PRESENT>/<applicable> present, <PARTIAL> partial, <ABSENT> absent, <N/A> n/a

INVALIDATING GAPS (fix before publishing)
- [<dimension>/<sub-check id>] <one line>. Evidence: <file:line or "absent: searched X,Y,Z">. Fix: <concrete change>.

HARDENING GAPS (raise credibility)
- [<dimension>/<sub-check id>] <one line>. Evidence: <…>. Fix: <…>.

KNOWN / IN-FLIGHT (already fixed on an open PR — excluded from gap counts)
- [<dimension>] <one line>. PR #<n>, verified against diff.

PER-DIMENSION (each dimension's sub-check breakdown)
1. Pre-registration     — <STATUS>  — PR1 <s> / PR2 <s> / PR3 <s> / PR4 <s>
2. Contamination        — <STATUS>  — CT1 … CT5
3. Holdout hygiene      — <STATUS>  — HO1 … HO5
4. Judge validity       — <STATUS>  — JV1 … JV6
5. Statistical honesty  — <STATUS>  — ST1 … ST6
6. Reproducibility      — <STATUS>  — RE1 … RE3
7. Leaderboard & publ.  — <STATUS>  — LB1 … LB7

STRENGTHS (what's already solid — one line each)
- …
```

**Verdict mapping:** `NOT PUBLISH-READY` when any INVALIDATING gap exists → `not_publish_ready`. `GRADABLE WITH CAVEATS` when no INVALIDATING gaps but HARDENING gaps remain → `gradable_with_caveats`. `PUBLISH-READY` when no gaps → `publish_ready`.

**(b) result.json** — conforming to [schema/result.schema.json](schema/result.schema.json): `{audited_commit, date, verdict, repo, dimensions: {<name>: {status, severity, sub_checks: [{id, status, severity, evidence: [{file, line, note}], fix}]}}}`. Every sub-check appears with its status, its evidence, and (if not PRESENT) its fix. Write it next to the markdown report. This file is diffable — a benchmark can track its integrity trend across audits in CI.

Report rules:
- **Lead with what invalidates.** Hardening gaps below. Strengths last.
- **Every gap carries a concrete fix** — the file to add, the guard to write, the test to add. Not "consider improving X." No fix is "add more scenarios" unless low scenario count is the specific finding.
- **In-flight fixes are not gaps.** List them under `KNOWN / IN-FLIGHT`, name the PR, exclude from counts.
- **Plain and direct.** State the gap, the evidence, the fix.

## Step 7 — Offer the fixes (do not auto-apply)

Auditing is read-only. After the report, ask which gaps to fix. Applying a fix changes the target repo's methodology — that is the author's call, one gap at a time, with their approval. Do not edit the benchmark, re-run any eval, or touch a leaderboard as part of the audit.

---

## Why sub-check granularity

An older version of this framework scored one status per dimension, which forced a whole dimension to PARTIAL when a single check was missing and hid *which* check. Sub-checks fix that: contamination can be "CT1 PRESENT, CT5 ABSENT" — the author sees exactly the guard to add and the reviewer sees exactly the attack that still lands. The `result.json` records every sub-check so the trend line is per-check, not per-dimension.

## Cross-references
- `methodology/*.md` — one file per dimension, each with its sub-checks, evidence bar, severity rule, and fixes.
- `schema/result.schema.json` — the machine-readable result contract.
- `fixtures/` — three synthetic benchmarks (weak, hardened, publish-ready) with `expected-result.json` for each, so the audit's own calibration is checkable.
