# fm99 — fm99-news-desk

The Now Spinning 99.9 FM news desk: 30 states, one constant department room.
512x512, 96 frames @24fps, seamless loops. 8-bit pixel-art rig (128x128 grid,
NEAREST x4, solid colors, no AA), same recipe and QC gates as the standing
production standard.

Character: owl (press fedora). Room: newsroom — scrolling wire ticker, BREAKING poster, typewriter, PRESS mug.
Personality: wise, deliberate, sharp-eyed; the head-turn says everything.

- `gifs/` — the 30 GIFs (`fm99_news_<state>.gif`)

States: working, idle, sleeping, thinking, celebrating, success, alert, panic, surprised, facepalm, shrugging, scheming, smug, laughing, dancing, drinking_coffee, eating_snack, tired, overheating, rebooting, debugging, deploying, pushing_to_github, gaming, listening, speaking, salute, flexing, bitching, goodbye.

Pipeline: `~/workspace/gif-station/fm99_news_set.py` (built on
`fm99_news_pilot.py` + `office_rig.py`).
