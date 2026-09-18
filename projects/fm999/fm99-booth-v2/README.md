# FM99 Booth v2 — Now Spinning 99.9 FM (detailed edition)

20-state animated set for the station's visual identity, rebuilt from scratch at
higher fidelity than the v1 8-bit set.

- **Calder** — elephant, day DJ (5:30 AM – 7 PM). Orange cap, amber headphones.
- **Mina** — crow, night DJ (7 PM – 5:30 AM). Iridescent feathers, purple
  headphones with cyan LED ring.

## States

| # | File | Description |
|---|------|-------------|
| 1 | fm99_on_air.gif | ON AIR sign close-up, double-blink |
| 2 | fm99_now_spinning.gif | Spinning vinyl + ticker |
| 3 | fm99_station_ident.gif | Neon 99.9 FM, flicker + EQ |
| 4 | fm99_signing_off.gif | Booth dims, sign off, goodnight |
| 5 | fm99_calder_hosting.gif | Warm welcome, floating notes |
| 6 | fm99_calder_taking_requests.gif | Ringing request line |
| 7 | fm99_calder_vibing.gif | Eyes-closed groove, beat-sync ears |
| 8 | fm99_calder_talking.gif | On-mic chatter, trunk gestures |
| 9 | fm99_calder_laughing.gif | Head back, big ear flap |
| 10 | fm99_calder_mic_check.gif | Trunk taps, VU spikes |
| 11 | fm99_calder_back_after_break.gif | High energy, light sweep |
| 12 | fm99_calder_technical_difficulties.gif | Holds the card, static |
| 13 | fm99_mina_hosting.gif | Smooth night welcome, LED pulse |
| 14 | fm99_mina_night_signal.gif | Paranormal fog + ? marks |
| 15 | fm99_mina_vibing.gif | Slow night groove |
| 16 | fm99_mina_talking.gif | Night chatter, beak motion |
| 17 | fm99_mina_laughing.gif | Beak open, wing flap |
| 18 | fm99_mina_taking_requests.gif | Night request line |
| 19 | fm99_mina_back_after_break.gif | Night energy, cyan sweep |
| 20 | fm99_mina_technical_difficulties.gif | Night card + static |

## Spec

- 512×512, 90 unique frames @ 24 fps, seamless loops
- Illustrated character/booth art → chroma-key → paper-doll part animation
  (ear flap, trunk bend, wing flutter, beak chatter, blinks)
- Booth FX: bouncing VU meters, ON AIR tally, vinyl spin, EQ bars, ticker,
  neon flicker, fog, light sweeps, ringing phone, TD card
- GIF recipe: `fps=24,scale=512:-1:flags=lanczos,split[s0][s1];
  [s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer`
- 20 chiptune stingers in `sounds/` (bright major-key day, darker minor-key night)

## Pipeline

`tools/radio_booth_v2.py` (rig) + `tools/radio_states_v2_{idents,calder,mina}.py`
(animators). Character/booth/prop art was illustrated, then keyed and animated
procedurally; see the tool headers for the part-rig definitions.
