#!/usr/bin/env python3
"""99.9 FM batch 3: calder_back_after_break, calder_technical_difficulties,
mina_hosting, mina_night_signal, mina_vibing."""
import math
import os

from PIL import ImageDraw

import radio_booth as radio
from radio_booth import kf


def _day_base(d, P_room, i, t, **kw):
    radio.draw_booth(d, P_room, i, t, 'day', **kw)
    p = radio.default_pose()
    p['gy'] = int(round(1.5 * math.sin(2 * math.pi * t)))
    return p


def _night_base(d, P_room, i, t, **kw):
    radio.draw_booth(d, P_room, i, t, 'night', **kw)
    p = radio.default_pose()
    p['gy'] = int(round(1.5 * math.sin(2 * math.pi * t)))
    return p


def _candle(d, P, i, t, x=31, y_base=92):
    """Little candle on the console, flickering flame."""
    d.rectangle([x - 3, y_base - 14, x + 3, y_base], fill=(232, 220, 190))
    d.rectangle([x - 3, y_base - 14, x + 3, y_base - 11], fill=(200, 185, 150))
    fl = int(round(2 * math.sin(10 * math.pi * i / 60)))  # fast flicker
    lean = int(round(1.5 * math.sin(6 * math.pi * i / 60 + 1)))
    fx = x + lean
    d.rectangle([fx - 1, y_base - 20 + fl, fx + 1, y_base - 14],
                fill=(255, 200, 90))
    d.rectangle([fx, y_base - 22 + fl, fx, y_base - 20 + fl],
                fill=(255, 240, 180))
    if (i // 2) % 2 == 0:  # glow halo pulse
        d.rectangle([x - 6, y_base - 24, x + 6, y_base - 8],
                    outline=(120, 90, 60))


# ---------------------------------------------------------------- 1. back_after_break (calder)
def a_calder_back_after_break(img, P_room, P_dj, style, i, n):
    """WE'RE BACK: text pop x2, point at camera, big bounce."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _day_base(d, P_room, i, t, onair='blink', live=True)
    p['gy'] = int(round(2 * math.sin(6 * math.pi * t)))       # 3 bounces/loop
    p['mouth'] = 'grin'
    p['brow'] = 1
    p['blink'] = 1 if 28 <= (i % 32) < 30 else 0
    jab = int(round(2 * math.sin(8 * math.pi * t)))
    p['pawR'] = (p['hx'] + 24, p['hy'] + 14 + jab)            # point at viewer
    p['pawL'] = (p['hx'] - 18, 90)
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    radio.fx_text_pop(d, "WE'RE BACK", 64, 28, i, t, 2, P_room['led_g'],
                      bursts=2, bg=P_room['console_d'])


# ---------------------------------------------------------------- 2. technical_difficulties (calder)
def a_calder_technical_difficulties(img, P_room, P_dj, style, i, n):
    """Holds the apology card x2, shrugs, static crackles on the console."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _day_base(d, P_room, i, t, onair=True, live=False)
    p['mouth'] = '-'
    p['brow'] = 1
    p['tilt'] = int(round(math.sin(4 * math.pi * t)))
    shrug = int(round(2 * math.sin(4 * math.pi * t)))
    pawL, pawR = radio.fx_card(d, P_room, P_dj, p, i, t,
                               ['SORRY!', 'TECHNICAL', 'ISSUES'],
                               (232, 220, 190), bursts=2)
    if pawL:
        p['pawL'], p['pawR'] = pawL, pawR
        p['gy'] += shrug
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=False)
    for k in range(10):  # static crackle over the console
        if (i + k) % 3 == 0:
            x = 40 + ((i * 7 + k * 37) % 50)
            y = 94 + ((i * 11 + k * 23) % 14)
            d.rectangle([x, y, x, y], fill=P_room['white'])


# ---------------------------------------------------------------- 3. mina_hosting
def a_mina_hosting(img, P_room, P_dj, style, i, n):
    """Smooth night welcome: slow sway, warm smile, moonlit groove."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True)
    p['hx'] = 64 + int(round(2.5 * math.sin(2 * math.pi * t)))
    p['hy'] += int(round(1.5 * math.sin(4 * math.pi * t)))
    p['mouth'] = 'smile'
    p['tilt'] = int(round(math.sin(2 * math.pi * t + 0.8)))
    p['blink'] = 1 if 34 <= (i % 38) < 36 else 0
    sway = int(round(3 * math.sin(2 * math.pi * t)))
    p['pawL'] = (p['hx'] - 18, 94 + sway)
    p['pawR'] = (p['hx'] + 18, 94 - sway)
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    radio.fx_speech(d, P_room, 84, 62, i, P_dj['neon'])


# ---------------------------------------------------------------- 4. mina_night_signal
def a_mina_night_signal(img, P_room, P_dj, style, i, n):
    """Paranormal hour: candle, floating ?s, conspiratorial lean-ins."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True)
    cyc = (t * 2) % 1.0
    lean = kf(cyc, [(0, 0), (0.10, 1), (0.45, 1), (0.55, 0), (1, 0)])
    p['hy'] += int(round(3 * lean))       # lean toward the mic
    p['lookx'] = int(round(2 * lean))
    p['brow'] = 1
    p['mouth'] = 'o' if lean > 0.5 else '-'
    p['blink'] = 1 if (lean < 0.5 and 30 <= (i % 36) < 32) else 0
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    _candle(d, P_room, i, t)
    for k in range(3):  # floating ? glyphs, seamless rise
        u = ((i + k * 20) % 60) / 60.0
        x = 44 + k * 20 + int(round(3 * math.sin(4 * math.pi * t + k)))
        y = int(round(66 - u * 34))
        col = radio.mix(P_dj['accent'], P_room['wall'], u * 0.6)
        radio.text(d, '?', x, y, 1, col)
    if lean > 0.5:
        radio.fx_speech(d, P_room, 84, 62, i, P_dj['accent'])
    radio.fx_text_pop(d, 'NIGHT SIGNAL', 64, 28, i, t, 1, P_dj['neon'],
                      bursts=2)


# ---------------------------------------------------------------- 5. mina_vibing
def a_mina_vibing(img, P_room, P_dj, style, i, n):
    """Slow night groove, eyes closed, alternating snaps."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True)
    p['gy'] = int(round(2 * math.sin(4 * math.pi * t)))
    p['hx'] = 64 + int(round(2 * math.sin(2 * math.pi * t + 1)))
    p['blink'] = 1
    p['mouth'] = 'smile'
    p['tilt'] = int(round(math.sin(4 * math.pi * t + 0.5)))
    snapL = (p['hx'] - 20, p['hy'] + 16)
    snapR = (p['hx'] + 20, p['hy'] + 16)
    p['pawL'] = snapL
    p['pawR'] = snapR
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    radio.gag_snap_fx(d, P_room, *snapL, i, phase=0)
    radio.gag_snap_fx(d, P_room, *snapR, i, phase=15)
    # music-note ticks floating up, alternating sides
    for k in range(3):
        u = ((i + k * 20) % 60) / 60.0
        x = p['hx'] - 26 + (k % 2) * 52
        y = int(round(p['hy'] - 20 - u * 18))
        if u < 0.8:
            radio.text(d, '>', x, y, 1, P_dj['neon'])


# ---------------------------------------------------------------- run
JOBS = [('calder_back_after_break', a_calder_back_after_break),
        ('calder_technical_difficulties', a_calder_technical_difficulties),
        ('mina_hosting', a_mina_hosting),
        ('mina_night_signal', a_mina_night_signal),
        ('mina_vibing', a_mina_vibing)]

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
