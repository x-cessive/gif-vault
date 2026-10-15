# XCSV animated emoji set 01

100 animated GIFs for the XCSV brand program — animated versions of the
neon gothic 8-bit emoji set. Chunky pixels, solid neon colors on black,
no anti-aliasing, no gradients.

- Canvas: 128x128, 14 frames @ ~12fps (84ms), seamless infinite loop.
- Motion templates (procedural, assigned per emoji):
  - glow-pulse — staff ranks, radio gear, treasures (brightness sine)
  - bob — mobs, sky items, floaters (vertical sine, +/-3px)
  - shake — weapons, reactions, tools (horizontal jitter)
  - neon-flicker — sign-like items: xcsv, radio89, neonmoon (buzzing-tube dips)
  - sparkle — events, loot, celebrations (twinkling overlay)
- Rigs: kept with the production workspace (5 per-batch animator rigs).
  QC: decode + frame count + dimensions + size + loop-continuity gates,
  plus contact-sheet eyeball pass per batch.
- Giphy: all 100 uploaded, tagged `xcessive`, `xcsv`, `<name>` — searchable
  as #xcsv on any platform with Giphy search. IDs + page URLs in
  `giphy_upload_results.json`.

## Contents

- `gifs/` — the 100 GIFs, `<name>.gif`
- `animated.json` (production workspace) — name/src/template manifest
- `giphy_upload_results.json` — Giphy id + page URL per file
