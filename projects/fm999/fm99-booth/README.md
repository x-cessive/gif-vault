# fm999 — fm99-booth

The Now Spinning 99.9 FM station set: 20 states, one constant radio booth —
mixing console with bouncing VU meters, two turntables, broadcast mic on a
boom, big ON AIR sign, neon 99.9 FM plate, window. 512x512, 60 unique frames
@24fps, seamless loops.

Day booth (Calder, 5:30 AM–7 PM): warm lighting, sunlit window.
Night booth (Mina, 7 PM–5:30 AM): dark + neon purple/cyan, moonlit window.
Idents: sign/graphic close-ups.

- `gifs/` — the 20 GIFs (`fm99_<state>.gif`)
- `sounds/` — 20 matching chiptune radio stingers (`fm99_<state>.wav`,
  22050 Hz mono; Calder's are bright major-key, Mina's darker minor-key)

States: on_air, now_spinning, station_ident, signing_off,
calder_hosting, calder_taking_requests, calder_vibing, calder_talking,
calder_laughing, calder_mic_check, calder_back_after_break,
calder_technical_difficulties, mina_hosting, mina_night_signal, mina_vibing,
mina_talking, mina_laughing, mina_taking_requests, mina_back_after_break,
mina_technical_difficulties.

Pipeline: `~/workspace/gif-station/radio_booth.py` (shared booth rig +
day/night/ident themes + DJ characters), animators in
`radio_states_b1.py`…`radio_states_b4.py`, sounds via
`radio_synth_sfx.py`. Same GIF recipe and QC gates as the standing
production standard.
