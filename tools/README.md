# tools

The GIF production pipeline. These are the actual scripts used to build the
sets in this vault (copies of the working originals in `~/workspace/gif-station/`).

- `office_outfits.py` — shared office room + per-state outfit/theme rig
- `office_states_b1.py` … `office_states_b6.py` — per-state animators (batches 1–6)
- `gigi_synth_sfx.py` — chiptune SFX synthesizer → `gigi_sounds/`
- `giphy_upload.py` — posts a set to Giphy (`GIPHY_API_KEY` from env only)
- `build_gallery.py` — regenerates the `docs/` web gallery from `projects/`

Run the gallery build from the repo root:

```bash
python3 tools/build_gallery.py
```

## FM99 station set pipeline
- `radio_booth.py` — radio booth rig (console with VU meters, turntables, boom mic, ON AIR sign, neon 99.9 FM plate, window), day/night/ident themes, Calder + Mina characters, shared gags/FX, render + QC helpers.
- `radio_states_b1.py` … `radio_states_b4.py` — animators, 5 states each (4 idents + 8 Calder day + 8 Mina night = 20 states).
- `radio_synth_sfx.py` — 20 chiptune radio stingers (bright major-key for Calder, darker minor-key for Mina), 22050 Hz mono WAVs.
