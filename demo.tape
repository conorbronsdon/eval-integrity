# demo.tape — canonical vhs recording script for docs/demo.gif
#
# Regenerate with vhs (https://github.com/charmbracelet/vhs):
#     vhs demo.tape
#
# vhs runs the commands in a real shell. The cat/json.tool beat and the verdict
# loop both read the committed fixtures/*/expected-result.json, so every status
# and verdict shown is live from those files. If vhs/ttyd/ffmpeg are
# unavailable, use the Pillow fallback renderer, which bakes in the same values:
#     python3 scripts/render_demo.py      # -> docs/demo.gif

Output docs/demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 460
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 45ms

# --- Beat 1: the weak fixture's expected result ------------------------------
Type "cat fixtures/weak-benchmark/expected-result.json | python3 -m json.tool | head"
Enter
Sleep 3s

# --- Beat 2: verdicts across the three calibration fixtures ------------------
Type `for f in weak hardened publish-ready; do python3 -c "import json,sys; d=json.load(open(f'fixtures/{sys.argv[1]}-benchmark/expected-result.json')); print(f'{sys.argv[1]:16} -> {d[\"verdict\"]}')" $f; done`
Enter
Sleep 4s
