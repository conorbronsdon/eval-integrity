"""Consistency checks for the calibration fixtures' expected-result.json files.

The fixtures are the oracle an audit is diffed against, so they must obey the
roll-up and verdict rules SKILL.md states (Step 3 and Step 6). Stdlib only.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = sorted(ROOT.glob("fixtures/*/expected-result.json"))
DIMENSIONS = {
    "pre-registration": "PR", "contamination": "CT", "holdout-hygiene": "HO",
    "judge-validity": "JV", "statistical-honesty": "ST",
    "reproducibility": "RE", "leaderboard-publishing": "LB",
}
STATUSES = {"PRESENT", "PARTIAL", "ABSENT", "N/A"}
SEVERITY_RANK = {"NONE": 0, "HARDENING": 1, "INVALIDATING": 2}


def rollup(statuses):
    applicable = [s for s in statuses if s != "N/A"]
    if not applicable:
        return "N/A"
    if all(s == "PRESENT" for s in applicable):
        return "PRESENT"
    if all(s == "ABSENT" for s in applicable):
        return "ABSENT"
    return "PARTIAL"


def methodology_ids(prefix, name):
    text = (ROOT / "methodology" / f"{name}.md").read_text(encoding="utf-8")
    return sorted(set(re.findall(rf"^###\s+({prefix}\d+)\b", text, re.M)))


class ExpectedResultTests(unittest.TestCase):
    def test_three_fixtures_exist(self):
        self.assertEqual(len(EXPECTED), 3)

    def test_dimension_status_is_the_rollup_of_its_sub_checks(self):
        for path in EXPECTED:
            data = json.loads(path.read_text(encoding="utf-8"))
            for name, dim in data["dimensions"].items():
                with self.subTest(fixture=path.parent.name, dimension=name):
                    statuses = [c["status"] for c in dim["sub_checks"]]
                    self.assertTrue(set(statuses) <= STATUSES)
                    self.assertEqual(dim["status"], rollup(statuses))

    def test_dimension_severity_is_the_worst_gap_severity(self):
        # schema/result.schema.json: "Worst severity across the dimension's
        # sub-check gaps"; NONE when the dimension has no gap.
        for path in EXPECTED:
            data = json.loads(path.read_text(encoding="utf-8"))
            for name, dim in data["dimensions"].items():
                gaps = [
                    c["severity"] for c in dim["sub_checks"]
                    if c["status"] in {"PARTIAL", "ABSENT"}
                ]
                expected = max(gaps, key=SEVERITY_RANK.__getitem__) if gaps else "NONE"
                with self.subTest(fixture=path.parent.name, dimension=name):
                    self.assertEqual(dim["severity"], expected)

    def test_every_methodology_sub_check_is_scored(self):
        for path in EXPECTED:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(data["dimensions"]), set(DIMENSIONS))
            for name, prefix in DIMENSIONS.items():
                with self.subTest(fixture=path.parent.name, dimension=name):
                    ids = sorted(c["id"] for c in data["dimensions"][name]["sub_checks"])
                    self.assertEqual(ids, methodology_ids(prefix, name))

    def test_verdict_follows_gap_severities(self):
        for path in EXPECTED:
            data = json.loads(path.read_text(encoding="utf-8"))
            gaps = [
                c["severity"]
                for dim in data["dimensions"].values()
                for c in dim["sub_checks"]
                if c["status"] in {"PARTIAL", "ABSENT"}
            ]
            if "INVALIDATING" in gaps:
                expected = "not_publish_ready"
            elif gaps:
                expected = "gradable_with_caveats"
            else:
                expected = "publish_ready"
            with self.subTest(fixture=path.parent.name):
                self.assertEqual(data["verdict"], expected)


if __name__ == "__main__":
    unittest.main()
