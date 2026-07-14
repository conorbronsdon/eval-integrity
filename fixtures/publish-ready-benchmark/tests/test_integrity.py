"""Tripwire tests (synthetic fixture, publish-ready).

Guards every exclusion and the pre-registration ordering. A refactor that lets a
null-agent, sequestered-split, or non-default row reach the board, or that writes
the pre-registration after the first call, fails here.
"""

import json
from pathlib import Path

from eval.aggregate import aggregate, exclude_non_contestants, assert_complete, NULL_AGENT


def _row(model, sid, **kw):
    base = {"model": model, "scenario_id": sid, "is_sequestered": False,
            "config": "default", "score": 0.6, "answer_len": 20}
    base.update(kw)
    return base


def test_null_agent_excluded():
    rows = [_row("rival-mini", "pub-001"), _row(NULL_AGENT, "pub-001", score=0.02)]
    assert NULL_AGENT not in aggregate(rows)


def test_sequestered_rows_excluded():
    rows = [_row("rival-mini", "pub-001"),
            _row("rival-mini", "seq-001", is_sequestered=True, score=0.99)]
    kept = exclude_non_contestants(rows)
    assert all(not r["is_sequestered"] for r in kept), "sequestered row reached the board"


def test_non_default_config_excluded():
    rows = [_row("rival-mini", "pub-001"),
            _row("rival-mini", "pub-002", config="smoke")]
    kept = exclude_non_contestants(rows)
    assert all(r["config"] == "default" for r in kept), "non-default config reached the board"


def test_completeness_gate_blocks_partial_board():
    rows = [_row("rival-mini", "pub-001")]  # missing rival-planner, acme-tool-1
    try:
        assert_complete(aggregate(rows))
        raised = False
    except SystemExit:
        raised = True
    assert raised, "completeness gate did not block a partial board"


def test_prereg_written_before_first_call(tmp_path, monkeypatch):
    # A stub 'first call' asserts the pre-registration file already exists.
    import eval.run as run
    prereg_path = tmp_path / "pre_registration.json"
    seen = {"exists_at_first_call": None}

    def stub_call(model, prompt):
        seen["exists_at_first_call"] = prereg_path.exists()
        return {"text": "x", "resolved_model": f"{model}-2026-07"}

    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "public").mkdir(parents=True)
    json.dump([{"id": "pub-001", "prompt": "p"}],
              open(tmp_path / "data/public/scenarios.json", "w"))
    monkeypatch.setattr(run, "call_model", stub_call)
    monkeypatch.setattr(run, "PUBLIC_DIR", "data/public")
    monkeypatch.setattr("sys.argv", ["run", "--seed", "1"])
    run.main()
    assert seen["exists_at_first_call"] is True, "prereg not on disk before first call"


def test_no_publish_path_gitignored():
    from scripts.publish import assert_no_publish_path_gitignored
    assert_no_publish_path_gitignored()  # raises SystemExit if any path is ignored
