# acme-code-eval

A benchmark for code-fixing agents. Pins the run before it starts, grades with a
three-judge panel, bootstraps confidence intervals, and excludes a null-agent
baseline from the public board.

> Synthetic fixture for the eval-integrity skill. Not a real project. This one is
> deliberately *mixed*: some integrity practices are solid, others are half-built.

## Running

```bash
uv sync                       # pinned environment (see pyproject.toml + uv.lock)
python -m eval.run --seed 7   # writes pre_registration.json, then runs
python -m eval.aggregate      # bootstraps CIs and writes data/results/leaderboard.json
```

Inputs are pinned to `data/public/scenarios.json`. The run is reproducible for
the pinned corpus and seed; judge calls at temperature 0 are close to but not
bit-for-bit deterministic across provider snapshots.

## What's covered

- **Pre-registration** — `eval/pre_registration.py` writes models, corpus hash,
  judge panel, seeds, and temperatures before the first call.
- **Contamination** — `scripts/generate_data.py` asserts a scenario's author is
  not a contestant, and stamps `author_model` on every scenario. A private
  holdout lives outside the repo.
- **Judging** — three judges; each judge's served model id is recorded. See
  `docs/methodology.md`.
- **Statistics** — `eval/aggregate.py` bootstraps scenario-level CIs with a fixed
  seed.
- **Leaderboard** — a null-agent baseline runs each cycle and is excluded from
  the public board; holdout rows are split out before aggregation.

## Known rough edges

We track length bias as a known judge risk but do not yet regress on it, and the
robustness table described in `docs/methodology.md` is not wired into the publish
step yet.
