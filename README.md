# GIF Vault

One home for every GIF project. Each project gets its own folder so sets never
mix — sovran GIFs stay sovran, NAFO GIFs stay NAFO, and so on.

## Layout

```
projects/
  sovran/               # everything sovran-branded
    gigi-office-v2/     # 30-state Gigi office set: gifs/ + sounds/ + giphy_upload_results.json
  nafo/                 # NAFO projects (empty — drop a set folder here)
  _template/            # copy this when starting a new project set
tools/                  # the production pipeline: rigs, animators, synth SFX, uploader
docs/                   # generated web gallery (GitHub Pages) — do not hand-edit
```

## Browse

The gallery is published with GitHub Pages and shows every GIF in the vault:
filter by project, search by name, click any GIF for the full-size view with
its Giphy page link (where one exists) and a copyable direct URL.

To rebuild it after adding or changing GIFs:

```bash
python3 tools/build_gallery.py
```

## Adding a new project set

1. Copy `projects/_template/` to `projects/<project>/<set-name>/`.
2. Drop finished GIFs in `gifs/` (and sounds in `sounds/` if the set has them).
3. Follow the production standard in `AGENTS.md` (same rig, same GIF recipe,
   same QC gates) so the vault stays visually consistent.
4. Run `python3 tools/build_gallery.py` and commit.

## Production standard (short version)

128x128 grid, NEAREST x4 to 512x512, 60 unique frames @24fps, seamless loop,
<=64 colors, one constant environment per set, per-state outfit variation.
Full spec and QC gates live in `AGENTS.md`.
