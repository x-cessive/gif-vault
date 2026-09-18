# New-set template

Copy this folder to `projects/<project>/<set-name>/` and work through the
checklist. Delete this file's template wording and describe the actual set.

## Checklist

- [ ] GIFs rendered to the production standard (`AGENTS.md`): 128x128 grid,
      NEAREST x4 to 512x512, 60 unique frames @24fps, seamless loop, <=64 colors
- [ ] QC gates pass: color count, motion audit, 18x12 legibility, contact sheet
- [ ] GIFs in `gifs/`, named `gigi_<set>_<state>.gif` (lowercase, underscores)
- [ ] Sounds in `sounds/` if the set has them (22050 Hz mono 16-bit WAV,
      named to match their GIF's state)
- [ ] Set `README.md` written: what the set is, state list, source notes
- [ ] `python3 tools/build_gallery.py` run from the repo root
- [ ] (optional) uploaded to Giphy; `giphy_upload_results.json` saved here
- [ ] committed, gallery verified on the Pages site

## Layout

```
<set-name>/
  README.md
  gifs/
  sounds/
```
