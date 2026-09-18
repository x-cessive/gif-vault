#!/usr/bin/env python3
"""99.9 FM batch 1: on_air, now_spinning, station_ident, signing_off, calder_hosting.

Animator signature: fn(img, P_room, P_dj, style, i, n).
128px grid, NEAREST x4 -> 512x512. Solid colors only, no AA, no gradients.
60 unique frames @24fps, seamless loops.
"""
import math
import os

from PIL import ImageDraw

import radio_booth as radio
from radio_booth import kf


def _dj_base(d, P_room, i, t, **kw):
    radio.draw_booth(d, P_room, i, t, 'day', **kw)
    p = radio.default_pose()
    p['gy'] = int(round(1.5 * math.sin(2 * math.pi * t)))
    return p


# ---------------------------------------------------------------- 1. on_air
def a_on_air(img, P_room, P_dj, style, i, n):
    """ON AIR sign close-up: blinking sign, glow rays, scrolling ticker."""
    t = i / n
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 128, 128], fill=radio.wall_fill(P_room, i, 7))
    on = (i // 15) % 2 == 0
    radio.draw_onair_sign(d, P_room, 10, 34, 118, 78, i, on=on, scale=2)
    if on:  # radiating light rays while lit
        for k, (x0, y0, dx, dy) in enumerate(
                ((10, 34, -1, -1), (118, 34, 1, -1),
                 (10, 78, -1, 1), (118, 78, 1, 1))):
            L = 8 + int(round(4 * math.sin(2 * math.pi * t + k)))
            d.line([x0, y0, x0 + dx * L, y0 + dy * L],
                   fill=P_room['sign_on'], width=2)
    radio.draw_neon_plate(d, P_room, 44, 86, 84, 102, i, ['99.9'])
    radio.draw_eq(d, P_room, 24, 104, 80, 12, i, t, P_room['sign_on'], bars=10)
    radio.fx_ticker(d, P_room, 'NOW SPINNING 99.9 FM * ON THE AIR * ', 120, i,
                    P_room['sign_on'] if on else P_room['sign_off'], speed=2)


# ---------------------------------------------------------------- 2. now_spinning
def a_now_spinning(img, P_room, P_dj, style, i, n):
    """Big spinning vinyl, tonearm, title ticker."""
    t = i / n
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 128, 128], fill=radio.wall_fill(P_room, i, 7))
    radio.text_c(d, 'NOW SPINNING', 64, 8, 2, P_room['label'])
    radio.draw_vinyl(d, P_room, 64, 62, 32, i, spin=2)
    # tonearm from top right
    rr = radio.rr
    rr(d, 104, 18, 110, 24, P_room['mic'], r=1)
    sway = int(round(2 * math.sin(2 * math.pi * t)))
    d.line([107, 21, 92, 44 + sway], fill=P_room['mic'], width=2)
    d.rectangle([90, 43 + sway, 94, 46 + sway], fill=P_room['knob'])
    radio.draw_eq(d, P_room, 24, 100, 80, 14, i, t, P_room['label'], bars=10)
    radio.fx_ticker(d, P_room, 'CALDER * MORNING DRIVE * REQUESTS OPEN * ',
                    118, i, P_room['white'])


# ---------------------------------------------------------------- 3. station_ident
def a_station_ident(img, P_room, P_dj, style, i, n):
    """Neon 99.9 FM logo, dancing EQ bars, light sweep."""
    t = i / n
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 128, 128], fill=radio.wall_fill(P_room, i, 7))
    radio.draw_neon_plate(d, P_room, 22, 26, 106, 62, i, ['99.9 FM'], scale=3)
    # light sweep across the logo, seamless
    sx = 22 + ((i * 84) // 60)
    d.line([sx, 27, sx, 61], fill=P_room['white'], width=2)
    radio.draw_eq(d, P_room, 24, 76, 80, 20, i, t, P_room['plate_tx'], bars=12)
    radio.text_c(d, 'NOW SPINNING', 64, 104, 1, P_room['neon_dim'])
    radio.text_c(d, '99.9 FM', 64, 112, 1, P_room['neon_dim'])


# ---------------------------------------------------------------- 4. signing_off
def a_signing_off(img, P_room, P_dj, style, i, n):
    """The sign dips dark, SIGNING OFF blinks, moon in the window."""
    t = i / n
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 128, 128], fill=radio.wall_fill(P_room, i, 7))
    on = (i // 20) % 3 != 2  # mostly lit, dips dark for 20 frames
    radio.draw_onair_sign(d, P_room, 14, 30, 114, 62, i, on=on)
    if (i // 12) % 2 == 0:
        radio.text_c(d, 'SIGNING OFF', 64, 72, 2, P_room['sign_on'])
    radio.draw_window(d, P_room, 92, 84, 124, 116, i, 'night')
    radio.draw_eq(d, P_room, 14, 96, 60, 12, i, t, P_room['neon_dim'], bars=8)


# ---------------------------------------------------------------- 5. calder_hosting
def a_calder_hosting(img, P_room, P_dj, style, i, n):
    """Warm welcome: wave x2, smile, head bob, live mic."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _dj_base(d, P_room, i, t, onair='blink', live=True)
    p['hx'] = 64 + int(round(1.5 * math.sin(4 * math.pi * t)))
    p['mouth'] = 'smile'
    p['brow'] = 1
    p['tilt'] = int(round(math.sin(4 * math.pi * t)))
    p['blink'] = 1 if 30 <= (i % 32) < 32 else 0
    paw, up = radio.gag_wave(p, i, t, side=1, bursts=2)
    if paw:
        p['pawR'] = paw
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    if up > 0.5:
        radio.fx_speech(d, P_room, 84, 62, i, P_room['led_c'])


# ---------------------------------------------------------------- run
JOBS = [('on_air', a_on_air), ('now_spinning', a_now_spinning),
        ('station_ident', a_station_ident), ('signing_off', a_signing_off),
        ('calder_hosting', a_calder_hosting)]

if __name__ == '__main__':
    import sys
    want = sys.argv[1:] or [s for s, _ in JOBS]
    for state, fn in JOBS:
        if state not in want:
            continue
        g = radio.render_state(state, fn, workdir=state)
        q = radio.qc_state(state, g)
        print('rendered', g, os.path.getsize(g) // 1024, 'KB')
        print(f"motion: {q['active']}/{q['total']} active, "
              f"min {q['mind']:.2f} max {q['maxd']:.2f}")
        print('colors:', q['colors'], 'legib sig:', q['sig'])
        print('contact:', radio.contact_sheet(state, workdir=state))
        print()
