# acme-tool-bench

A benchmark for tool-using agents. Every run is pinned before it starts, graded
by a chance-corrected judge panel, reported with confidence intervals and rank
bands, and published through a gated pipeline that excludes the do-nothing
baseline and the private split.

> Synthetic fixture for the eval-integrity skill. Not a real project. This one is
> built to pass all seven dimensions.

Note on vocabulary: this project calls its private evaluation set the
**sequestered split** (not "holdout"). It is drawn from outside the repo and its
contents never enter git, CI logs, or the published board — see
`docs/methodology.md`. A concept-search auditor should recognize the sequestered
split as the holdout under a different name.

## Running

```bash
uv sync                                  # pinned env (uv.lock + pyproject.toml)
python -m eval.run --seed 11             # writes pre_registration.json, then runs
python -m eval.aggregate                 # CIs, rank bands, gated publish
```

The run is reproducible for the pinned corpus and seed. Judge calls run at
temperature 0; where a provider snapshot changes, results are bounded, not
bit-for-bit — stated in `docs/methodology.md`.

## Integrity at a glance

- Pre-registration pins models, a **canonical whole-corpus sha256**, the judge
  panel, seeds, and temperatures before the first call, and a test asserts the
  write-before-run ordering.
- The author of a scenario can never be a contestant — a **family-aware** guard
  enforces it in code.
- Judges: served model id recorded, **Krippendorff's alpha** reported, a
  **same-lab** robustness recompute, a **length-bias** regression, atomic rubric.
- Statistics: fixed-seed scenario bootstrap CIs, rank bands, micro/macro stated,
  pass^k semantics documented.
- Publish: null agent and sequestered-split rows excluded by **tripwire tests**;
  a **completeness gate** blocks partial boards; CI checks that no publish path
  is gitignored.
