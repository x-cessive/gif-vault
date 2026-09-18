#!/usr/bin/env python3
"""GIGI office GIF set batch 1: idle, listening, speaking, success, alert.

Extends office_rig_v2 (imported, never modified) via the shared
office_outfits system (imported, never modified).

Animator signature: fn(img, P_room, P_char, style, i, n).
  - P_room: room/desk/screens/monitors (office stays pixel-identical).
  - P_char: draw_gigi / arms / paws / mug (the outfit lives here).
  - style: outfits.style_for(state) -> draw_gigi.

128px grid, NEAREST x4 -> 512x512. Solid colors only, no AA, no gradients.
60 unique frames @24fps, seamless loops. Frames land in
~/workspace/gif-station/otter_v2/<state>/; contact sheets + legibility
previews in ~/workspace/gif-station/otter_v2/; GIFs in
~/workspace/your_files/gigi_otter/gigi_office_<state>.gif.
"""
import math
import os

from PIL import ImageDraw

import office_rig_v2 as v2
from office_rig_v2 import mix, kf, text, ell, rr
import office_outfits as outfits


# ---------------------------------------------------------------- shared bits
def _base(d, P_room, i, t, mood):
    """The one true room + chair + fresh pose. Returns (sw, p)."""
    outfits.draw_room(d, P_room, i, t, mood)
    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    return sw, p


def _desk(d, P_room, P_char, p, i, t, main_fn, term_fn, mug=True):
    """Desk furniture + monitors + mug, before arms."""
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    main_fn(d, P_room, i, t)
    term_fn(d, P_room, i, t)
    if mug:
        v2.draw_mug(d, P_char, 92, 97, i, t)


def _arms(d, P_char, p, pawL, pawR, fingers=(-1, -1)):
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1], press_finger=fingers[0])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1], press_finger=fingers[1])


def _desk_fx(d, P_room, i, t):
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- custom monitors
def _main_std(d, P, i, t):
    v2.draw_main_monitor(d, P, i)


def _term_std(d, P, i, t):
    v2.draw_term_monitor(d, P, i, t)


def _term_listen(d, P_room, i, t, accent):
    """Term monitor: big LIVE waveform + sweep."""
    rr(d, 70, 76, 106, 100, P_room['bezel'], r=2)
    d.rectangle([72, 78, 104, 96], fill=P_room['screen'])
    text(d, 'LIVE', 74, 80, 1, accent)
    if (i // 12) % 2 == 0:                                  # rec dot
        d.rectangle([98, 80, 100, 82], fill=accent)
    for x in range(73, 104):                                # big waveform
        y = 88 + int(round(7 * math.sin(x * 0.45 + 6 * math.pi * i / 60)))
        d.rectangle([x, y, x, y], fill=accent)
    sx = 73 + (i * 31 // 60)                                # sweep, seamless
    d.line([sx, 79, sx, 95], fill=mix(accent, P_room['screen'], 0.5), width=1)


def _main_speech(d, P_room, i, t):
    """Main monitor: bouncing ON AIR level bars."""
    rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P_room['screen'])
    air_c = P_room['led_r'] if (i // 6) % 2 == 0 else P_room['white']
    text(d, 'ON AIR', 32, 78, 1, air_c)
    for k in range(9):
        h = 3 + int(round(10 * abs(math.sin(4 * math.pi * i / 60 + k * 0.7))))
        x = 33 + k * 3
        col = P_room['led_g'] if k < 6 else P_room['led_a']
        d.rectangle([x, 94 - h, x + 1, 94], fill=col)
    d.rectangle([45, 97, 47, 98], fill=P_room['led_g'])


def _main_check(d, P_room, i, t):
    """Main monitor: big check mark."""
    rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P_room['screen'])
    text(d, 'DONE', 32, 78, 1, P_room['led_g'])
    chk = P_room['led_g']
    d.line([38, 86, 47, 94], fill=chk, width=3)
    d.line([47, 94, 62, 78], fill=chk, width=3)
    d.rectangle([45, 97, 47, 98], fill=P_room['led_g'])


def _main_warn(d, P_room, i, t):
    """Main monitor: warning triangle + '!'."""
    rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P_room['screen'])
    yel = (255, 200, 60)
    d.polygon([47, 94, 60, 76, 73, 94], fill=yel)
    d.polygon([50, 91, 60, 79, 70, 91], fill=P_room['screen'])
    text(d, '!', 58, 82, 2, yel)
    if (i // 6) % 2 == 0:                                   # flashing top bar
        d.rectangle([30, 76, 64, 77], fill=P_room['led_r'])


# ---------------------------------------------------------------- 1. idle
def a_idle(img, P_room, P_char, style, i, n):
    """Relaxed lean-back, slow breathing, look-arounds, ear twitches."""
    t = i / n
    d = ImageDraw.Draw(img)
    sw, p = _base(d, P_room, i, t, 'day')
    p['gy'] = int(round(1.5 * math.sin(2 * math.pi * t)))     # breathing bob
    p['hy'] = 61 + p['gy']                                    # leaned back
    p['hx'] = 64
    look = math.sin(4 * math.pi * t)                          # 2 look-arounds
    p['hx'] += int(round(2 * look))
    p['lookx'] = int(round(3 * look))
    p['tilt'] = int(round(math.sin(4 * math.pi * t + 0.6)))
    p['blink'] = 1 if 26 <= (i % 28) < 28 else 0
    p['earL'] = 2 if 18 <= i < 21 else 0
    p['earR'] = 2 if 42 <= i < 45 else 0
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))
    pawL = (46 + p['gx'], 102 + p['gy'])
    pawR = (82 + p['gx'], 102 + p['gy'])
    v2.draw_gigi(d, P_char, p, style, i, t)
    _desk(d, P_room, P_char, p, i, t, _main_std, _term_std)
    _arms(d, P_char, p, pawL, pawR)
    _desk_fx(d, P_room, i, t)


# ---------------------------------------------------------------- 2. listening
def a_listening(img, P_room, P_char, style, i, n):
    """Leaned in, head cocked, fast LED ring pulse, sound arcs incoming."""
    t = i / n
    d = ImageDraw.Draw(img)
    sw, p = _base(d, P_room, i, t, 'day')
    p['gy'] = int(round(math.sin(2 * math.pi * t)))
    p['hy'] = 58 + p['gy']                                    # lean forward
    p['hx'] = 62
    p['tilt'] = 1                                             # head cocked
    p['lookx'] = 2
    p['looky'] = -1
    p['brow'] = 1
    p['blink'] = 1 if (i % 50) == 49 else 0                   # eyes wide
    p['earL'] = 2 if 12 <= i < 15 else 0
    p['earR'] = 2 if 36 <= i < 39 else 0
    p['tail'] = int(round(2 * math.sin(4 * math.pi * t)))
    pawL = (46 + p['gx'], 101 + p['gy'])
    pawR = (82 + p['gx'], 101 + p['gy'])
    v2.draw_gigi(d, P_char, p, style, i, t)
    hx_img = p['hx'] + p['gx']
    hy_img = p['hy'] + p['gy']
    # fast headphone LED ring pulse (right cup)
    ring_c = P_char['accent'] if (i // 3) % 2 == 0 else P_char['white']
    d.rectangle([hx_img + 12, hy_img - 7, hx_img + 21, hy_img + 10],
                outline=ring_c)
    # 3 sound-wave arcs traveling in from the right edge
    for k in range(3):
        u = ((i * 1.5 + k * 20) % 60) / 60.0
        x = 130 - u * 48
        if x > hx_img + 22:
            col = mix(P_char['accent'], P_room['wall'], u * 0.45)
            d.arc([int(round(x)) - 5, hy_img - 11, int(round(x)) + 5, hy_img + 11],
                  start=270, end=90, fill=col, width=1)
    _desk(d, P_room, P_char, p, i, t, _main_std,
          lambda dd, PP, ii, tt: _term_listen(dd, PP, ii, tt, P_char['accent']))
    _arms(d, P_char, p, pawL, pawR)
    _desk_fx(d, P_room, i, t)


# ---------------------------------------------------------------- 3. speaking
def a_speaking(img, P_room, P_char, style, i, n):
    """Mic boom, mouth open/close, speech lines, head bob, level bars."""
    t = i / n
    d = ImageDraw.Draw(img)
    sw, p = _base(d, P_room, i, t, 'day')
    bob = math.sin(8 * math.pi * t)                           # 4 head bobs
    p['gy'] = int(round(1.2 * math.sin(2 * math.pi * t)))
    p['hy'] = 58 + p['gy'] + int(round(1.5 * bob))
    p['hx'] = 64 + int(round(math.sin(6 * math.pi * t)))       # gentle sway
    p['lookx'] = int(round(2 * math.sin(6 * math.pi * t)))
    p['blink'] = 1 if 27 <= (i % 30) < 29 else 0
    p['brow'] = 1
    p['tail'] = int(round(2 * math.sin(4 * math.pi * t)))
    gesture = int(round(3 * math.sin(8 * math.pi * t + 1)))
    gesture2 = int(round(3 * math.sin(8 * math.pi * t + 2.5)))
    pawL = (50 + p['gx'] + gesture, 96 + p['gy'])
    pawR = (84 + p['gx'] + gesture2, 100 + p['gy'])
    v2.draw_gigi(d, P_char, p, style, i, t)
    hx_img = p['hx'] + p['gx']
    hy_img = p['hy'] + p['gy']
    cx, cy = hx_img + p['lookx'], hy_img + 8 + p['looky']
    # mic boom: small dark arm from the right headphone cup to the mouth
    d.line([hx_img + 16, hy_img + 2, cx - 4, cy], fill=P_char['phone_d'], width=2)
    tip_c = P_char['accent'] if (i // 4) % 2 == 0 else P_char['white']
    d.rectangle([cx - 6, cy - 1, cx - 4, cy + 1], fill=tip_c)   # blinking mic tip
    # mouth open/close, 4 frames per cycle
    open_m = (i // 2) % 2 == 0
    ell(d, cx, cy, 3, 3 if open_m else 1, P_char['eye'])
    if open_m:                                                # radiating lines
        for dx, dy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            L = 4 + (i // 2) % 3
            d.line([cx + dx * 4, cy + dy * 3,
                    cx + dx * (4 + L), cy + dy * (3 + L)],
                   fill=P_char['white'], width=1)
    _desk(d, P_room, P_char, p, i, t, _main_speech, _term_std)
    _arms(d, P_char, p, pawL, pawR)
    _desk_fx(d, P_room, i, t)


# ---------------------------------------------------------------- 4. success
def a_success(img, P_room, P_char, style, i, n):
    """Fist pump + hop, grin, sparkle burst, confetti, check on the monitor."""
    t = i / n
    d = ImageDraw.Draw(img)
    sw, p = _base(d, P_room, i, t, 'day')
    pump = kf(t, [(0, 0), (0.06, 0), (0.14, 1), (0.30, 1), (0.36, 0),
                 (0.56, 0), (0.62, 1), (0.78, 1), (0.84, 0), (1, 0)])
    bounce = int(round(1.5 * math.sin(6 * math.pi * t)))       # excited bounce, 3/loop
    p['gy'] = bounce - int(round(4 * pump))                    # bounce + hop
    p['hy'] = 60 + p['gy']
    p['hx'] = 64
    p['brow'] = 1
    p['blink'] = 1 if 38 <= (i % 40) < 40 else 0
    p['earL'] = 2 if pump > 0.5 and (i // 4) % 2 == 0 else 0
    p['tail'] = int(round(3 * math.sin(6 * math.pi * t)))
    pawL = (46 + p['gx'], 100 + p['gy'] - int(round(12 * pump)))
    shake = ((i // 2) % 2) * 2 if pump > 0.5 else 0            # fist shake
    pawR = (84 + p['gx'] + int(round((p['hx'] + 16 - 84) * pump)),
            100 + p['gy'] - int(round(36 * pump)) + shake)
    v2.draw_gigi(d, P_char, p, style, i, t)
    hx_img = p['hx'] + p['gx']
    hy_img = p['hy'] + p['gy']
    if pump > 0.5:
        # grin: wider mouth line
        d.line([hx_img + p['lookx'] - 5, hy_img + p['looky'] + 8,
                hx_img + p['lookx'] + 5, hy_img + p['looky'] + 8],
               fill=P_char['eye'], width=2)
        # 4-point sparkle burst above the fist
        for sx, sy, R in ((int(round(pawR[0])) + 2, int(round(pawR[1])) - 10, 4),
                          (int(round(pawR[0])) - 8, int(round(pawR[1])) - 16, 2),
                          (int(round(pawR[0])) + 10, int(round(pawR[1])) - 14, 2)):
            L = R if (i // 3) % 2 == 0 else R // 2 + 1
            col = P_char['white'] if (i // 3) % 2 == 0 else P_char['accent']
            d.line([sx - L, sy, sx + L, sy], fill=col, width=1)
            d.line([sx, sy - L, sx, sy + L], fill=col, width=1)
    # confetti all loop
    cols_c = (P_char['accent'], P_char['white'], P_room['led_a'], P_room['led_c'])
    for k in range(12):
        ct = ((i + k * 6) % 60) / 60.0
        x = 24 + (k * 37) % 84 + int(round(4 * math.sin(4 * math.pi * t + k)))
        y = 8 + ct * 84
        if 8 <= y <= 100:
            d.rectangle([int(round(x)), int(round(y)),
                         int(round(x)) + 1, int(round(y)) + 1],
                        fill=cols_c[k % 4])
    _desk(d, P_room, P_char, p, i, t, _main_check, _term_std)
    _arms(d, P_char, p, pawL, pawR)
    _desk_fx(d, P_room, i, t)


# ---------------------------------------------------------------- 5. alert
def a_alert(img, P_room, P_char, style, i, n):
    """Snap upright, eyes wide, paws up, pulsing red border, warning monitor."""
    t = i / n
    d = ImageDraw.Draw(img)
    sw, p = _base(d, P_room, i, t, 'red')
    snap = kf(t, [(0, 0), (0.04, 1), (0.5, 1), (0.56, 0), (1, 0)])
    shake = (2 if (i % 4) < 2 else -2) * int(round(snap))     # ±2px shake while up
    pant = int(round(2 * math.sin(8 * math.pi * t)))           # relieved panting
    p['gy'] = -int(round(8 * snap)) + shake + pant * (1 - int(round(snap)))
    p['hy'] = 60 + p['gy']                                     # snap upright
    p['hx'] = 64 + (((i % 2) * 2 - 1)) * int(round(snap))       # body jitter every frame
    p['brow'] = 1                                             # eyes wide
    p['blink'] = 1 if (snap < 0.5 and 30 <= (i % 60) < 32) else 0
    p['earL'] = 2 if (snap > 0.5 and (i // 6) % 2 == 0) else 0
    p['earR'] = 2 if (snap > 0.5 and (i // 6) % 2 == 1) else 0
    p['tail'] = int(round(3 * math.sin(10 * math.pi * t)))
    restL = (46 + p['gx'], 100 + p['gy'])
    restR = (84 + p['gx'], 100 + p['gy'])
    upL = (p['hx'] + p['gx'] - 24, p['hy'] + p['gy'] - 16)
    upR = (p['hx'] + p['gx'] + 24, p['hy'] + p['gy'] - 16)
    held = int(round(snap))
    paws_shake = (((i // 2) % 2) * 4 - 2) * held               # paws tremble
    pawL = (restL[0] + (upL[0] - restL[0]) * snap,
            restL[1] + (upL[1] - restL[1]) * snap + paws_shake)
    pawR = (restR[0] + (upR[0] - restR[0]) * snap,
            restR[1] + (upR[1] - restR[1]) * snap - paws_shake)
    v2.draw_gigi(d, P_char, p, style, i, t)
    hx_img = p['hx'] + p['gx']
    hy_img = p['hy'] + p['gy']
    if snap > 0.5:                                            # shocked "o" mouth
        ell(d, hx_img + p['lookx'], hy_img + p['looky'] + 8, 2, 2, P_char['eye'])
    _desk(d, P_room, P_char, p, i, t, _main_warn, _term_std)
    _arms(d, P_char, p, pawL, pawR)
    _desk_fx(d, P_room, i, t)
    # pulsing red border, inset, width oscillates 1-3px (faster pulse)
    w = 1 + (i // 4) % 3
    d.rounded_rectangle([1, 1, 126, 126], radius=5,
                        outline=P_room['led_r'], width=w)


# ---------------------------------------------------------------- run
JOBS = [('idle', a_idle), ('listening', a_listening), ('speaking', a_speaking),
        ('success', a_success), ('alert', a_alert)]

if __name__ == '__main__':
    import sys
    want = sys.argv[1:] or [s for s, _ in JOBS]
    for state, fn in JOBS:
        if state not in want:
            continue
        g = outfits.render_state(state, fn, workdir=state)
        q = outfits.qc_state(state, g)
        print('rendered', g, os.path.getsize(g) // 1024, 'KB')
        print(f"motion: {q['active']}/{q['total']} active, "
              f"min {q['mind']:.2f} max {q['maxd']:.2f}")
        print('colors:', q['colors'], 'legib cap/phone:', q['cap'], q['phone'])
        print('contact:', outfits.contact_sheet(state, workdir=state))
        print()
