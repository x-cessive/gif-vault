# AGENTS.md — gif-vault

Operating manual for this repo. How the user works in general lives elsewhere;
this file is how work gets done here.

## What this repo is

The single organized home for GIF projects. Projects are strictly separated:
`sovran/` holds sovran-branded sets only; every other project gets its own
top-level folder under `projects/`. Never mix projects in one folder.

## Adding or updating a GIF set

1. New project: `mkdir projects/<project>`. New set: copy
   `projects/_template/` to `projects/<project>/<set-name>/` and fill it in.
2. Put finished GIFs in the set's `gifs/`, sounds (if any) in `sounds/`.
3. Rebuild the gallery: `python3 tools/build_gallery.py` (regenerates `docs/`).
4. Commit everything, including the regenerated `docs/`. Never hand-edit
   `docs/` — it is build output.

## GIF production standard

This is the standing bar for every set in the vault:

- Rig: `tools/office_outfits.py` (shared room + per-state outfit/theme system;
  animators in `tools/office_states_bN.py`; sounds via `tools/gigi_synth_sfx.py`).
- Spec: 128x128 grid, NEAREST x4 to 512x512 square, blocky 8-bit (solid
  colors, no AA, no gradients), 60 unique frames @24fps, seamless infinite loop.
- GIF recipe (exact): `fps=24,scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer`.
- QC gates (all must pass): <=64 colors; consecutive-pair motion audit at
  32x32 (large majority of pairs active, no slideshow); 18x12
  nearest-neighbor legibility (character + signature colors identifiable);
  contact-sheet eyeball pass.
- Design rules: one constant environment across the set; per-state outfit
  color variation; one signature accent effect per state; real per-frame
  motion everywhere.
- Character rule: Gigi is a river otter. No fox. No dog. An otter.

## Giphy uploads

- `tools/giphy_upload.py` posts a set's GIFs: `GIPHY_API_KEY=... python3
  tools/giphy_upload.py` (key from env only — never commit it).
- It writes `giphy_upload_results.json` (ids + page URLs, no key); keep a copy
  next to the set so the gallery can link each GIF to its Giphy page.
- Free beta keys are rate-limited (~100 calls/hour); the script paces itself.

## Gallery

- `tools/build_gallery.py` scans `projects/*/`, extracts first-frame
  thumbnails, and writes `docs/index.html` (+ `docs/data.json`).
- Published via GitHub Pages from `/docs` on `main`.
- Keep the viewer dependency-free (vanilla HTML/CSS/JS, no build step) so any
  worker can rebuild or patch it.

## Conventions

- File names: `gigi_<set>_<state>.gif` style — lowercase, underscores.
- Sounds are 22050 Hz mono 16-bit WAV, named to match their GIF's state.
- Large binaries belong here (this repo exists for them); never commit large
  binaries to code repos like sovran-cli — stage, QC, then wire via manifest.
