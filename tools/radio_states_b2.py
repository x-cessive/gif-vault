#!/usr/bin/env python3
"""99.9 FM batch 2: calder_taking_requests, calder_vibing, calder_talking,
calder_laughing, calder_mic_check."""
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


# ---------------------------------------------------------------- 1. taking_requests
def a_calder_taking_requests(img, P_room, P_dj, style, i, n):
    """Request line rings; Calder grabs the handset x2, nods along."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _dj_base(d, P_room, i, t, onair='blink', live=True, ring=True)
    cyc = (t * 2) % 1.0
    pick = kf(cyc, [(0, 0), (0.10, 1), (0.45, 1), (0.55, 0), (1, 0)])
    p['mouth'] = 'smile'
    p['brow'] = 1
    p['blink'] = 1 if 40 <= (i % 44) < 42 else 0
    if pick > 0.5:  # handset to ear, nodding
        p['pawR'] = (p['hx'] + 14, p['hy'] + 1)
        p['hy'] += int(round(math.sin(12 * math.pi * t)))
        radio.fx_text_pop(d, 'ON THE LINE', 64, 30, i, t, 1,
                          P_room['led_g'], bursts=2)
    else:  # hand hovering over the ringing phone
        p['pawR'] = (104, 96 + int(round(3 * math.sin(8 * math.pi * t))))
    radio.draw_dj(d, P_dj, p, style, i, t)
    if pick > 0.5:  # handset at the ear, drawn over the headphone cup
        d.rectangle([p['hx'] + 10, p['hy'] - 6, p['hx'] + 18, p['hy'] + 6],
                    fill=P_dj['phone'])
    radio.draw_mic_boom(d, P_room, i, live=True)


# ---------------------------------------------------------------- 2. vibing
def a_calder_vibing(img, P_room, P_dj, style, i, n):
    """Eyes closed, head bopping, alternating finger snaps."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _dj_base(d, P_room, i, t, onair='blink', live=True)
    p['gy'] = int(round(2 * math.sin(4 * math.pi * t)))      # 2 bops/loop
    p['hx'] = 64 + int(round(2 * math.sin(2 * math.pi * t)))
    p['blink'] = 1                                          # eyes closed
    p['mouth'] = 'smile'
    p['tilt'] = int(round(math.sin(4 * math.pi * t)))
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
            radio.text(d, '>', x, y, 1, P_dj['accent'])


# ---------------------------------------------------------------- 3. talking
def a_calder_talking(img, P_room, P_dj, style, i, n):
    """On-mic chatter: mouth moves, hands gesture, speech arcs."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _dj_base(d, P_room, i, t, onair='blink', live=True)
    p['hx'] = 62 + int(round(1.5 * math.sin(6 * math.pi * t)))
    p['hy'] += int(round(1.5 * math.sin(8 * math.pi * t)))
    p['mouth'] = radio.gag_talk_mouth(i)
    p['brow'] = 1
    p['blink'] = 1 if 25 <= (i % 30) < 27 else 0
    g1 = int(round(4 * math.sin(8 * math.pi * t)))
    g2 = int(round(4 * math.sin(8 * math.pi * t + 2.2)))
    p['pawL'] = (p['hx'] - 18, 92 + g1)
    p['pawR'] = (p['hx'] + 18, 90 + g2)
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)
    radio.fx_speech(d, P_room, 84, 62, i, P_room['led_c'])


# ---------------------------------------------------------------- 4. laughing
def a_calder_laughing(img, P_room, P_dj, style, i, n):
    """Two big laugh bursts: head back, shoulders shaking, HA HA."""
    t = i / n
    d = ImageDraw.Draw(img)
    p = _dj_base(d, P_room, i, t, onair='blink', live=True)
    burst = radio.gag_laugh_burst(t, bursts=3)
    if burst > 0.5:
        p['hy'] -= 3
        p['tilt'] = -1
        p['mouth'] = 'open'
        p['gy'] += int(round(2 * math.sin(24 * math.pi * t)))  # shoulder shake
        p['pawL'] = (p['hx'] - 10, 90 + p['gy'])
        p['pawR'] = (p['hx'] + 10, 90 + p['gy'])
        ha = 'HA HA' if (i // 6) % 2 == 0 else 'HA!'
        radio.text_c(d, ha, p['hx'], p['hy'] - 30, 1, P_dj['accent'])
    else:
        p['mouth'] = 'smile'
        p['blink'] = 1 if 30 <= (i % 34) < 32 else 0
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True)


# ---------------------------------------------------------------- 5. mic_check
def a_calder_mic_check(img, P_room, P_dj, style, i, n):
    """Taps the mic 3x; every tap spikes the VU meters."""
    t = i / n
    d = ImageDraw.Draw(img)
    tap = 1 if (i % 20) < 2 else 0
    spike = 10 if (i % 20) < 5 else 4  # meters always dance, spike on taps
    p = _dj_base(d, P_room, i, t, onair='blink', live=True, vu_boost=spike)
    p['hx'] = 66  # leaning toward the mic
    p['mouth'] = 'o' if tap else '-'
    p['brow'] = 1
    p['lookx'] = 2
    p['blink'] = 1 if 35 <= (i % 40) < 37 else 0
    if tap:
        p['pawR'] = (80, 62)  # fingertip on the capsule
    else:
        p['pawR'] = (p['hx'] + 16, 92 + int(round(2 * math.sin(4 * math.pi * t))))
    radio.draw_dj(d, P_dj, p, style, i, t)
    radio.draw_mic_boom(d, P_room, i, live=True, tap=tap)
    radio.fx_text_pop(d, '1... 2...', 64, 30, i, t, 1, P_room['led_g'],
                      bursts=3)


# ---------------------------------------------------------------- run
JOBS = [('calder_taking_requests', a_calder_taking_requests),
        ('calder_vibing', a_calder_vibing),
        ('calder_talking', a_calder_talking),
        ('calder_laughing', a_calder_laughing),
        ('calder_mic_check', a_calder_mic_check)]

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
