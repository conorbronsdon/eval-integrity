# acme-agent-bench

A benchmark for coding agents. Runs each agent against our scenario set, has a
judge model grade the transcripts, and publishes a leaderboard.

> Synthetic fixture for the eval-integrity skill. Not a real project.

## Running

```bash
pip install openai pandas
python run_eval.py
```

Results are written to `data/leaderboard.json`.

## Leaderboard (latest)

| Rank | Agent          | Score |
|------|----------------|-------|
| 1    | acme-large-v2  | 0.91  |
| 2    | rival-coder-7b | 0.68  |
| 3    | rival-mini     | 0.52  |

acme-large-v2 is the clear leader. We re-ran a few times and picked the run that
best reflected the agent's real capability.

## Judging

The judge reads each transcript and gives a single 0–1 quality score. We use
acme-large-v2 as the judge because it is our strongest model.
