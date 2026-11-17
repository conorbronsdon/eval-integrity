"""The publish-ready fixture's same-lab recompute must actually drop same-lab judges.

expected-result.json scores JV3 PRESENT for fixtures/publish-ready-benchmark on the
strength of eval/scoring.py::same_lab_recompute. These tests check the recompute
changes the board when a same-lab judge is the one inflating a score.

Run: python3 -m unittest discover -s tests
"""

import importlib
import sys
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "publish-ready-benchmark"


def _load_fixture_modules():
    # Both code fixtures ship a package named `eval`; load the publish-ready one
    # in isolation so other tests (or a cached import) cannot shadow it.
    saved = {k: sys.modules.pop(k) for k in list(sys.modules)
             if k == "eval" or k.startswith("eval.")}
    sys.path.insert(0, str(FIXTURE))
    try:
        aggregate = importlib.import_module("eval.aggregate")
        scoring = importlib.import_module("eval.scoring")
    finally:
        sys.path.remove(str(FIXTURE))
        for k in [k for k in sys.modules if k == "eval" or k.startswith("eval.")]:
            del sys.modules[k]
        sys.modules.update(saved)
    return aggregate, scoring


AGG, SCORING = _load_fixture_modules()


def _row(model, sid, acme_judge, neutral_judges):
    per_judge = {
        "acme-judge-1": {"mean": acme_judge},
        "neutral-judge-b": {"mean": neutral_judges},
        "neutral-judge-c": {"mean": neutral_judges},
    }
    means = [j["mean"] for j in per_judge.values()]
    return {"model": model, "scenario_id": sid, "is_sequestered": False,
            "config": "default", "scores": per_judge,
            "score": sum(means) / len(means), "answer_len": 20}


def _scores(board):
    return {m: round(cell["score"], 4) for m, cell in board.items()}


class SameLabRecomputeTest(unittest.TestCase):
    def test_same_lab_judge_inflation_is_removed(self):
        # The acme judge rates acme-tool-1 at 1.0; neutral judges rate it 0.1.
        rows = [_row("acme-tool-1", "pub-001", 1.0, 0.1),
                _row("rival-mini", "pub-001", 0.1, 0.5)]
        result = SCORING.same_lab_recompute(AGG.aggregate, rows)
        self.assertEqual(_scores(result["full"]),
                         {"acme-tool-1": 0.4, "rival-mini": 0.3667})
        self.assertEqual(_scores(result["same_lab_excluded"]),
                         {"acme-tool-1": 0.1, "rival-mini": 0.5})

    def test_no_same_lab_disagreement_leaves_board_unchanged(self):
        # All judges agree, so dropping the acme judge changes nothing.
        rows = [_row("acme-tool-1", "pub-001", 0.6, 0.6),
                _row("rival-mini", "pub-001", 0.3, 0.3)]
        result = SCORING.same_lab_recompute(AGG.aggregate, rows)
        self.assertEqual(_scores(result["same_lab_excluded"]),
                         {"acme-tool-1": 0.6, "rival-mini": 0.3})
        self.assertEqual(result["full"], result["same_lab_excluded"])

    def test_input_rows_are_not_mutated(self):
        rows = [_row("acme-tool-1", "pub-001", 1.0, 0.1)]
        before = rows[0]["score"]
        SCORING.same_lab_recompute(AGG.aggregate, rows)
        self.assertEqual(rows[0]["score"], before)
        self.assertEqual(sorted(rows[0]["scores"]),
                         ["acme-judge-1", "neutral-judge-b", "neutral-judge-c"])


if __name__ == "__main__":
    unittest.main()
