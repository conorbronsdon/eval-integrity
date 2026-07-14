# Frame spec for the eval-integrity demo GIF.
# Rendered by scripts/render_demo.py (canonical path: demo.tape via vhs).
#
# The `cat ... | json.tool` beat shows the REAL head of
# fixtures/weak-benchmark/expected-result.json. The closing summary table
# SUMMARIZES the three fixtures' expected verdicts and per-dimension roll-ups —
# every status and verdict is read verbatim from the committed
# fixtures/*/expected-result.json files (weak -> not_publish_ready,
# hardened -> gradable_with_caveats, publish-ready -> publish_ready).

TITLE = "eval-integrity — benchmark auditor"

FRAMES = [
    ("out", [
        [("# Three synthetic benchmark repos, each with a committed expected-result.json", "dim")],
        [("# stating what a correct audit must find. This is how the auditor is calibrated.", "dim")],
    ], 1900),

    ("cmd", "cat fixtures/weak-benchmark/expected-result.json | python3 -m json.tool | head"),
    ("out", [
        [("{", "fg")],
        [('    "audited_commit": ', "fg"), ('"FIXTURE",', "yellow")],
        [('    "date": ', "fg"), ('"2026-07-13",', "yellow")],
        [('    "repo": ', "fg"), ('"fixtures/weak-benchmark (acme-agent-bench)",', "yellow")],
        [('    "verdict": ', "fg"), ('"not_publish_ready",', "red")],
        [('    "dimensions": {', "fg")],
        [('        "pre-registration": {', "fg")],
        [('            "status": ', "fg"), ('"ABSENT",', "red")],
        [('            "severity": ', "fg"), ('"INVALIDATING",', "red")],
    ], 2600),

    ("clear",),
    ("out", [
        [("# Roll-up across the seven dimensions for all three fixtures:", "dim")],
        "",
        [("  dimension              weak        hardened     publish-ready", "dim")],
        [("  ─────────────────────  ──────────  ───────────  ─────────────", "dim")],
        [("  pre-registration       ", "fg"), ("ABSENT      ", "red"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  contamination          ", "fg"), ("ABSENT      ", "red"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  holdout-hygiene        ", "fg"), ("N/A         ", "dim"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  judge-validity         ", "fg"), ("ABSENT      ", "red"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  statistical-honesty    ", "fg"), ("ABSENT      ", "red"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  reproducibility        ", "fg"), ("PARTIAL     ", "yellow"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  leaderboard-publishing ", "fg"), ("ABSENT      ", "red"), ("PARTIAL      ", "yellow"), ("PRESENT", "green")],
        [("  ─────────────────────  ──────────  ───────────  ─────────────", "dim")],
        [("  verdict                ", "fg"),
         ("not_publish  ", "red"), ("w/_caveats   ", "yellow"), ("publish_ready", "green")],
    ], 3400),
    ("out", [
        "",
        [("# Diff each result.json against its expected-result.json to prove the auditor "
          "is calibrated.", "dim")],
    ], 2600),
]
