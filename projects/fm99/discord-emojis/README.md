# fm99 — discord-emojis

Animated emoji set for the Now Spinning 99.9 FM Discord presence. 128x128,
~10fps, 1–8 KB each (well under Discord's 256 KB animated-emoji cap), all
passing the 32px downscale legibility test. Station palette + mascots
(Thumper, Calder, Mina, Zephyr) consistent with the wave-2 identity set.

- `gifs/` — 8 animated emojis: `emoji_eq_bounce`, `emoji_tuner_sweep`,
  `emoji_thumper_dance`, `emoji_typing_dots`, `emoji_alert_blink`,
  `emoji_vinyl_spin`, `emoji_signal_pulse`, `emoji_party_thumper`.
- Giphy: see `giphy_upload_results.json` (tags: `xcessive` first, then
  `fm99`, `999fm`, `nowspinning`, `discord`).

Note: `:alert:` blinks red/DIM as an attention cue — not a replacement for
a real urgent-alert tone. Pipeline: `~/workspace/apk-analysis/make_discord_pack.py`.
