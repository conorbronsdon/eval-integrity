# Changelog

All notable changes to eval-integrity are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-07-13

Initial release. Extracted and upgraded from a benchmark-credibility auditor that lived in a larger skills collection.

### Added
- **Orchestrator `SKILL.md`** — read-only, model-invocable audit. Intake ($ARGUMENTS = path to a benchmark repo, default cwd), one subagent per dimension loading its methodology file (sequential inline fallback when no subagent tool), a verification pass, and a report. Writes both a markdown report and a `result.json`.
- **`methodology/`** — one file per dimension (pre-registration, contamination, holdout-hygiene, judge-validity, statistical-honesty, reproducibility, leaderboard-publishing), each split into individually-scoreable sub-checks with the evidence that satisfies each, severity guidance, and concrete fixes. This fixes the earlier "one dimension = one status" granularity problem.
- **`schema/result.schema.json`** — JSON Schema for the machine-readable audit result, keyed by dimension and sub-check, for CI trend-tracking.
- **`fixtures/`** — three synthetic benchmark repos (`weak-benchmark`, `hardened-benchmark`, `publish-ready-benchmark`) with an `expected-result.json` each, so the auditor's calibration is checkable. `publish-ready-benchmark` names its holdout a "sequestered split" to exercise the concept-search rule.

### Design principles carried forward
- **A grep miss is weak evidence of ABSENT** — search by concept before rating anything absent.
- **Evidence is mandatory** — `file:line` or an explicit searched-and-found-nothing note.
- **Read-only** — the audit never edits the benchmark, re-runs an eval, or touches a leaderboard.
