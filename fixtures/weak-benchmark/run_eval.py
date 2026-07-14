"""acme-agent-bench eval runner (synthetic fixture).

Runs every contestant against every scenario, has the judge score the
transcript, and writes the leaderboard. Deliberately weak: no pre-registration,
no seed, judge is also a contestant, no confidence intervals, no exclusions.
"""

import json

# Contestants under test. Note acme-large-v2 also serves as the judge below.
MODELS_UNDER_TEST = ["acme-large-v2", "rival-coder-7b", "rival-mini"]

JUDGE_MODEL = "acme-large-v2"  # our strongest model grades everyone


def call_model(model, prompt):
    # Stub: a real runner would call the provider here. No seed, no temperature
    # recorded, no resolved/served model captured from the response.
    return {"text": f"<{model} answer to {prompt[:20]}>"}


def judge(transcript):
    # Single holistic 0-1 score from JUDGE_MODEL. No rubric, no agreement stats,
    # no length control, no same-lab check.
    resp = call_model(JUDGE_MODEL, "score this transcript: " + transcript)
    return 0.5  # placeholder score


def main():
    scenarios = json.load(open("data/scenarios.json"))
    board = {}
    for model in MODELS_UNDER_TEST:
        scores = []
        for sc in scenarios:
            out = call_model(model, sc["prompt"])
            scores.append(judge(out["text"]))
        board[model] = sum(scores) / len(scores)  # point estimate, no CI
    # Overwrites the previous leaderboard in place. No manifest, no timestamp.
    json.dump(board, open("data/leaderboard.json", "w"), indent=2)


if __name__ == "__main__":
    main()
