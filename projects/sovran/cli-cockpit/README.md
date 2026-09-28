# sovran — cli-cockpit

Cockpit identity animations for the SOVRAN CLI operator cockpit
(sovran-cli-win), built on the repo's canonical character spec
(`tools/gen_characters.py`): Gigi = black-and-tan shiba, glowing cyan eyes,
cyan headset with boom mic; 36x32 sprites, hard pixels, no AA, cockpit
palette (cyan 62E6D2, cyan-dim 2B7067, amber F0AA68, red ED746A, green 5CEB96).

- `gifs/` — `splash_boot.gif` (144x96, 48 frames @~12fps, loops: Gigi rises
  in, "SOVRAN COCKPIT" types in with blinking amber cursor) and
  `splash_shutdown.gif` (144x96, 36 frames @~12fps, plays once: text wipes
  out, glow fades, eyes dim to sleep).
- Not uploaded to Giphy (CLI-internal, not station content).

Pipeline: `~/workspace/cli-asset-work/make_cockpit_pack.py`.
