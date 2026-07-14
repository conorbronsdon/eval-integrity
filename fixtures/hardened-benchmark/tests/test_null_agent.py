"""Tripwire test: the null-agent baseline must never reach the public board.

Solid: this test guards the null-agent exclusion. Half-built: there is NO
equivalent tripwire test for holdout rows or non-default (smoke) configs, and no
test guards the pre-registration write-before-run ordering.
"""

from eval.aggregate import aggregate, NULL_AGENT


def test_null_agent_excluded_from_board():
    rows = [
        {"model": "rival-mini", "scenario_id": "pub-001", "is_holdout": False,
         "config": "default", "score": 0.6},
        {"model": NULL_AGENT, "scenario_id": "pub-001", "is_holdout": False,
         "config": "default", "score": 0.02},
    ]
    board = aggregate(rows)
    assert NULL_AGENT not in board, "null-agent leaked onto the public board"


def test_holdout_rows_excluded():
    rows = [
        {"model": "rival-mini", "scenario_id": "pub-001", "is_holdout": False,
         "config": "default", "score": 0.6},
        {"model": "rival-mini", "scenario_id": "hold-001", "is_holdout": True,
         "config": "default", "score": 0.9},
    ]
    board = aggregate(rows)
    # Passes today, but nothing asserts the holdout score is kept OUT of the
    # published public aggregate value — only that the model still appears.
    assert "rival-mini" in board
