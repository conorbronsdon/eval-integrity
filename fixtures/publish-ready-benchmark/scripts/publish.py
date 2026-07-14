"""Publish step (synthetic fixture, publish-ready).

Writes every surface the docs promise AND commits it. The public-vs-sequestered
gap table and the same-lab robustness table are produced here, so nothing the
methodology names is left unwired. A guard asserts no publish path is gitignored
before committing (a gitignored path would kill `git add` and ship nothing).
"""

import json
import subprocess
from pathlib import Path

# Every path the publish step adds. docs/methodology.md accounts for each of
# these, and each is produced by a pipeline step (aggregate.py / this file).
PUBLISH_PATHS = [
    "data/results/leaderboard.json",     # board + rank bands (aggregate.py)
    "data/results/gap_table.json",       # public-vs-sequestered gap (this file)
    "data/results/same_lab_table.json",  # same-lab robustness (this file)
]


def write_gap_table(public_board, sequestered_board):
    gap = {m: {"public": public_board[m]["score"],
               "sequestered": sequestered_board.get(m, {}).get("score"),
               "gap": (public_board[m]["score"]
                       - sequestered_board.get(m, {}).get("score", public_board[m]["score"]))}
           for m in public_board}
    Path("data/results/gap_table.json").write_text(json.dumps(gap, indent=2))


def write_same_lab_table(recompute):
    Path("data/results/same_lab_table.json").write_text(json.dumps(recompute, indent=2))


def assert_no_publish_path_gitignored():
    # A publish path that is gitignored would make `git add` exit non-zero and
    # the publish would die before shipping. Fail loudly here instead.
    for p in PUBLISH_PATHS:
        r = subprocess.run(["git", "check-ignore", p], capture_output=True, text=True)
        if r.returncode == 0:  # returncode 0 means the path IS ignored
            raise SystemExit(f"publish path is gitignored: {p}")


def commit_publish():
    assert_no_publish_path_gitignored()
    subprocess.run(["git", "add", *PUBLISH_PATHS], check=True)
    subprocess.run(["git", "commit", "-m", "publish: update leaderboard"], check=True)
