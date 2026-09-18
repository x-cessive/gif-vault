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
