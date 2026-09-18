# fm99 — fm99-programming-desk

The Now Spinning 99.9 FM programming desk: 30 states, one constant department room.
512x512, 96 frames @24fps, seamless loops. 8-bit pixel-art rig (128x128 grid,
NEAREST x4, solid colors, no AA), same recipe and QC gates as the standing
production standard.

Character: ant (clipboard + stopwatch). Room: schedule wall — giant grid clock, timetable boards.
Personality: six-limbed precision machine; antennae show the mood.

- `gifs/` — the 30 GIFs (`fm99_programming_<state>.gif`)

States: working, idle, sleeping, thinking, celebrating, success, alert, panic, surprised, facepalm, shrugging, scheming, smug, laughing, dancing, drinking_coffee, eating_snack, tired, overheating, rebooting, debugging, deploying, pushing_to_github, gaming, listening, speaking, salute, flexing, bitching, goodbye.

Pipeline: `~/workspace/gif-station/fm99_programming_set.py` (built on
`fm99_programming_pilot.py` + `office_rig.py`).
