# fm99 — fm99-traffic-desk

The Now Spinning 99.9 FM traffic desk: 30 states, one constant department room.
512x512, 96 frames @24fps, seamless loops. 8-bit pixel-art rig (128x128 grid,
NEAREST x4, solid colors, no AA), same recipe and QC gates as the standing
production standard.

Character: beaver (hi-vis vest). Room: road desk — traffic map, cones, cycling signal light, DETOUR poster.
Personality: industrious road-crew gnawer; communicates in tail slaps.

- `gifs/` — the 30 GIFs (`fm99_traffic_<state>.gif`)

States: working, idle, sleeping, thinking, celebrating, success, alert, panic, surprised, facepalm, shrugging, scheming, smug, laughing, dancing, drinking_coffee, eating_snack, tired, overheating, rebooting, debugging, deploying, pushing_to_github, gaming, listening, speaking, salute, flexing, bitching, goodbye.

Pipeline: `~/workspace/gif-station/fm99_traffic_set.py` (built on
`fm99_traffic_pilot.py` + `office_rig.py`).
