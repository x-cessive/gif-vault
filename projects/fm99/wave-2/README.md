# fm99 — wave-2 (estate identity)

Second wave of the Now Spinning 99.9 FM station-identity set: Discord stickers,
loading screens, and reaction GIFs in the station 8-bit pixel-art rig
(solid colors, no AA; station palette only: BG 080C11, TEXT DCE6EE, DIM 748291,
CYAN 62E6D2, CYAN_DIM 2B7067, AMBER F0AA68, RED ED746A, GREEN 5CEB96,
BRIGHT 394858, RAISED 151D26). Mascots: Thumper the audience-desk rabbit
(light fur, one flopped ear, CYAN headphones), Calder (day DJ), Mina
(night DJ), Zephyr (weather-desk owl).

- `gifs/` — 10 GIFs: 6 stickers (`sticker_deadair`, `sticker_dj_bow`,
  `sticker_onair_hype`, `sticker_request_queued`, `sticker_signal_lost`,
  `sticker_thumper_dance`), 2 loading screens (`loading_tuner_sweep`,
  `loading_vinyl_spin`), 2 reactions (`reaction_mic_drop`, `reaction_signal_bars`).
- Giphy: see `giphy_upload_results.json` (tags: `xcessive` first, then
  `fm99`, `999fm`, `nowspinning`, `wave2`).

Pipeline: `~/workspace/apk-analysis/make_wave2.py`. QC passed on all ten;
note: `sticker_thumper_dance.gif` (860 KB) and `loading_tuner_sweep.gif`
(1.36 MB) exceed Discord's 500 KB sticker cap.
