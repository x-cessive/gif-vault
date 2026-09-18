# fm99 — fm99-audience-desk

The Now Spinning 99.9 FM audience desk: 30 states, one constant department room.
512x512, 96 frames @24fps, seamless loops. 8-bit pixel-art rig (128x128 grid,
NEAREST x4, solid colors, no AA), same recipe and QC gates as the standing
production standard.

Character: rabbit (teal headphones). Room: request desk — ringing phone bank, letters, shout-out cork board.
Personality: bouncy and warm; the long ears are the emotional instrument.

- `gifs/` — the 30 GIFs (`fm99_audience_<state>.gif`)

States: working, idle, sleeping, thinking, celebrating, success, alert, panic, surprised, facepalm, shrugging, scheming, smug, laughing, dancing, drinking_coffee, eating_snack, tired, overheating, rebooting, debugging, deploying, pushing_to_github, gaming, listening, speaking, salute, flexing, bitching, goodbye.

Pipeline: `~/workspace/gif-station/fm99_audience_set.py` (built on
`fm99_audience_pilot.py` + `office_rig.py`).
