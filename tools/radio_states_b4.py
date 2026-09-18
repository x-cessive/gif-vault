#!/usr/bin/env python3
"""99.9 FM batch 4: mina_talking, mina_laughing, mina_taking_requests,
mina_back_after_break, mina_technical_difficulties."""
import math
import os

from PIL import ImageDraw

import radio_booth as radio
from radio_booth import kf


def _night_base(d, P_room, i, t, **kw):
    radio.draw_booth(d, P_room, i, t, 'night', **kw)
    p = radio.default_pose()
    p['gy'] = int(round(1.5 * math.sin(2 * math.pi * t)))
    return p


# ---------------------------------------------------------------- 1. talking
def a_mina_talking(img, P_room, P_dj, style, i, n):
    """Night chatter: mouth moves, slow hand gestures, neon speech arcs."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True)
    p['hx'] = 62 + int(round(1.5 * math.sin(6 * math.pi * t)))
    p['hy'] += int(round(1.5 * math.sin(8 * math.pi * t)))
    p['mouth'] = radio.gag_talk_mouth(i)
    p['brow'] = 1
    p['blink'] = 1 if 25 <= (i % 30) < 27 else 0
    g1 = int(round(4 * math.sin(8 * math.pi * t + 1)))
    g2 = int(round(4 * math.sin(8 * math.pi * t + 3.1)))
    p['pawL'] = (p['hx'] - 18, 92 + g1)
    p['pawR'] = (p['hx'] + 18, 90 + g2)
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    radio.fx_speech(d, P_room, 84, 62, i, P_dj['neon'])


# ---------------------------------------------------------------- 2. laughing
def a_mina_laughing(img, P_room, P_dj, style, i, n):
    """Two night laugh bursts: head back, hair shake, HA HA."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True)
    burst = radio.gag_laugh_burst(t, bursts=3)
    if burst > 0.5:
        p['hy'] -= 3
        p['tilt'] = -1
        p['mouth'] = 'open'
        p['gy'] += int(round(2 * math.sin(24 * math.pi * t)))
        p['pawL'] = (p['hx'] - 10, 90 + p['gy'])
        p['pawR'] = (p['hx'] + 10, 90 + p['gy'])
        ha = 'HA HA' if (i // 6) % 2 == 0 else 'HA!'
        radio.text_c(d, ha, p['hx'], p['hy'] - 30, 1, P_dj['neon'])
    else:
        p['mouth'] = 'smile'
        p['blink'] = 1 if 30 <= (i % 34) < 32 else 0
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)


# ---------------------------------------------------------------- 3. taking_requests
def a_mina_taking_requests(img, P_room, P_dj, style, i, n):
    """Night request line: ring, handset to ear x2, slow nod."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True, ring=True)
    cyc = (t * 2) % 1.0
    pick = kf(cyc, [(0, 0), (0.10, 1), (0.45, 1), (0.55, 0), (1, 0)])
    p['mouth'] = 'smile'
    p['brow'] = 1
    p['blink'] = 1 if 40 <= (i % 44) < 42 else 0
    if pick > 0.5:
        p['pawR'] = (p['hx'] + 14, p['hy'] + 1)
        p['hy'] += int(round(math.sin(8 * math.pi * t)))  # slow nod
        radio.fx_text_pop(d, 'NIGHT LINE', 64, 30, i, t, 1,
                          P_dj['neon'], bursts=2)
    else:
        p['pawR'] = (104, 96 + int(round(3 * math.sin(8 * math.pi * t))))
    radio.draw_dj(d, P_dj, p, style, i, t)
    if pick > 0.5:
        d.rectangle([p['hx'] + 10, p['hy'] - 6, p['hx'] + 18, p['hy'] + 6],
                    fill=P_dj['phone'])
    radio.draw_mic_boom(d, P_room, i, live=True)


# ---------------------------------------------------------------- 4. back_after_break
def a_mina_back_after_break(img, P_room, P_dj, style, i, n):
    """WE'RE BACK, night edition: neon text pop x2, point, bounce."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair='blink', live=True)
    p['gy'] = int(round(2 * math.sin(6 * math.pi * t)))
    p['mouth'] = 'grin'
    p['brow'] = 1
    p['blink'] = 1 if 28 <= (i % 32) < 30 else 0
    jab = int(round(2 * math.sin(8 * math.pi * t)))
    p['pawR'] = (p['hx'] + 24, p['hy'] + 14 + jab)
    p['pawL'] = (p['hx'] - 18, 90)
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    radio.fx_text_pop(d, "WE'RE BACK", 64, 28, i, t, 2, P_dj['neon'],
                      bursts=2, bg=P_room['console_d'])


# ---------------------------------------------------------------- 5. technical_difficulties
def a_mina_technical_difficulties(img, P_room, P_dj, style, i, n):
    """Night apology card x2, static crackles, neon flicker."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _night_base(d, P_room, i, t, onair=True, live=False)
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
    for k in range(10):
        if (i + k) % 3 == 0:
            x = 40 + ((i * 7 + k * 37) % 50)
            y = 94 + ((i * 11 + k * 23) % 14)
            d.rectangle([x, y, x, y], fill=P_dj['neon'])


# ---------------------------------------------------------------- run
JOBS = [('mina_talking', a_mina_talking),
        ('mina_laughing', a_mina_laughing),
        ('mina_taking_requests', a_mina_taking_requests),
        ('mina_back_after_break', a_mina_back_after_break),
        ('mina_technical_difficulties', a_mina_technical_difficulties)]

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
