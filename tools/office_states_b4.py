#!/usr/bin/env python3
"""Batch 4 office states: dancing, surprised, shrugging, scheming, panic.
Never touches office_rig_v2 or office_outfits — imports only."""
import math
import os
import random

from PIL import ImageDraw

import office_rig_v2 as v2
import office_outfits as outfits

# ------------------------------------------------------------------ helpers
def note(d, x, y, c):
    """Pixel eighth-note."""
    x, y = int(round(x)), int(round(y))
    d.line([x + 2, y - 6, x + 2, y], fill=c, width=1)
    d.rectangle([x - 1, y - 2, x + 2, y + 1], fill=c)
    d.rectangle([x + 2, y - 6, x + 5, y - 4], fill=c)


def sparkle(d, x, y, s, c, c2):
    x, y, s = int(round(x)), int(round(y)), int(round(s))
    d.line([x - s, y, x + s, y], fill=c, width=1)
    d.line([x, y - s, x, y + s], fill=c, width=1)
    d.rectangle([x, y, x, y], fill=c2)
    if s >= 3:
        d.line([x - 2, y - 2, x + 2, y + 2], fill=c2, width=1)
        d.line([x - 2, y + 2, x + 2, y - 2], fill=c2, width=1)


def base_pose(sw=0, breath=0):
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = breath
    p['hy'] = 60 + breath
    return p


def finish_char_and_desk(d, P_room, P_char, style, p, pawL, pawR, i, t,
                        mon_main=None, mug=(92, 97), ticks=None):
    """Draw character, arms, paws, desk stack, monitors."""
    v2.draw_chair(d, P_room, 0)
    v2.draw_gigi(d, P_char, p, style, i, t)
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    gx, gy = p['gx'], p['gy']
    v2.arm(d, P_char, 50 + gx, 88 + gy, pawL[0] + gx, pawL[1] + gy, bend=1)
    v2.draw_paw(d, P_char, pawL[0] + gx, pawL[1] + gy)
    v2.arm(d, P_char, 78 + gx, 88 + gy, pawR[0] + gx, pawR[1] + gy, bend=-1)
    v2.draw_paw(d, P_char, pawR[0] + gx, pawR[1] + gy)
    if mon_main is not None:
        mon_main(d, P_room, i, t)
    else:
        v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    if mug is not None:
        v2.draw_mug(d, P_room, mug[0], mug[1], i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)
    if ticks:  # shrug motion ticks: list of (x, y, h)
        for (x, y, h) in ticks:
            d.line([x, y, x, y - h], fill=P_char['white'], width=1)


def open_mouth(d, P_char, p):
    """Overdraw fixed closed mouth with an open oval (after draw_gigi)."""
    cx = p['hx'] + p['gx'] + p['lookx']
    cy = p['hy'] + p['gy'] + 8 + p['looky']
    v2.ell(d, cx, cy, 2, 3, (10, 10, 12))


# ------------------------------------------------------------------ 1. dancing
def mon_equalizer(d, P, i, t):
    v2.rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    bars = 8
    for b in range(bars):
        h = int(round(6 + 8 * abs(math.sin(i * 0.55 + b * 1.3))))
        x = 32 + b * 4
        col = [P['accent'], P['white'], P['led_g']][b % 3]
        d.rectangle([x, 94 - h, x + 2, 94], fill=col)
    d.rectangle([45, 97, 47, 98], fill=P['led_g'])
    v2.text(d, "MIX", 32, 78, 1, P['code_d'])


def a_dancing(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    mood = outfits.OUTFITS['dancing']['mood']
    outfits.draw_room(d, P_room, i, t, mood)

    ph = 2 * math.pi * 5 * t                     # 2 Hz bop, 5 cycles/loop
    sw = int(round(5 * math.sin(ph)))
    p = base_pose(sw, breath=int(round(1.5 * math.sin(ph))))
    p['hy'] = 60 + p['gy'] - 2
    p['tilt'] = int(round(2 * math.sin(ph + math.pi / 2)))
    p['lookx'] = int(round(2 * math.sin(ph)))
    bi = i % 20
    p['blink'] = 1 if bi in (17, 18) else 0
    p['tail'] = int(round(3 * math.sin(ph)))
    p['thump'] = 1 if (i // 3) % 4 == 0 else 0

    liftL = max(0.0, math.sin(ph))              # paws pump alternately
    liftR = max(0.0, -math.sin(ph))
    pawL = (44 + 4 * liftL, 100 - 56 * liftL)
    pawR = (84 - 4 * liftR, 100 - 56 * liftR)

    v2.draw_chair(d, P_room, sw)
    v2.draw_gigi(d, P_char, p, style, i, t)

    # 3 music notes rising, seamless wrap
    theme = P_char['accent']
    for k in range(3):
        phn = ((i + k * 20) % 60) / 60.0
        nx = 64 + sw - 16 + k * 7
        ny = 46 - phn * 26
        note(d, nx, ny, theme if k % 2 == 0 else P_char['white'])

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    gx, gy = p['gx'], p['gy']
    v2.arm(d, P_char, 50 + gx, 88 + gy, pawL[0] + gx, pawL[1] + gy, bend=1)
    v2.draw_paw(d, P_char, pawL[0] + gx, pawL[1] + gy)
    v2.arm(d, P_char, 78 + gx, 88 + gy, pawR[0] + gx, pawR[1] + gy, bend=-1)
    v2.draw_paw(d, P_char, pawR[0] + gx, pawR[1] + gy)
    mon_equalizer(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_room, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ------------------------------------------------------------------ 2. surprised
def mon_glitch(d, P, i, t):
    v2.rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    rnd = random.Random(i * 7 + 1)
    burst = i < 30                            # glitch bursts first half
    npx = 90 if burst else 12
    cols = [P['white'], P['accent'], P['code'], P['led_r'], P['led_a']]
    for _ in range(npx):
        x = rnd.randint(30, 64)
        y = rnd.randint(76, 96)
        d.rectangle([x, y, x + rnd.randint(0, 1), y], fill=rnd.choice(cols))
    if burst and (i // 4) % 2 == 0:
        y = rnd.randint(78, 94)
        d.rectangle([30, y, 64, y + 1], fill=P['white'])
    d.rectangle([45, 97, 47, 98], fill=P['led_g'])


def a_surprised(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    mood = outfits.OUTFITS['surprised']['mood']
    outfits.draw_room(d, P_room, i, t, mood)

    # one jolt per loop: fast back, settle by frame 60
    j = v2.kf(t, [(0, 0), (0.08, 1), (0.28, 1), (0.55, 0.35), (1, 0)])
    p = base_pose(breath=int(round(-5 * j + math.sin(2 * math.pi * 3 * t))))
    p['hy'] = 60 + p['gy']
    p['blink'] = 0                            # eyes wide
    p['brow'] = 1
    p['lookx'] = int(round(2 * math.sin(2 * math.pi * t)))
    p['earL'] = 2 if 2 <= i < 10 else 0
    p['earR'] = 2 if 2 <= i < 10 else 0
    pawL = (44 + p['gx'], 100 - 58 * j)
    pawR = (84 + p['gx'], 100 - 58 * j)

    v2.draw_chair(d, P_room, 0)
    v2.draw_gigi(d, P_char, p, style, i, t)
    open_mouth(d, P_char, p)                   # gasp

    # big "!" pops above head for ~0.5s (12 frames), little hop
    if 3 <= i < 15:
        e = (i - 3) / 12.0
        hop = int(round(4 * e * (1 - e) * 4))
        x = 64 + p['gx'] - v2.text_w("!", 2) // 2
        y = 22 - hop
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            v2.text(d, "!", x + ox, y + oy, 2, (10, 10, 12))
        v2.text(d, "!", x, y, 2, P_char['white'])

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    gx, gy = p['gx'], p['gy']
    v2.arm(d, P_char, 50 + gx, 88 + gy, pawL[0] + gx, pawL[1] + gy, bend=1)
    v2.draw_paw(d, P_char, pawL[0] + gx, pawL[1] + gy)
    v2.arm(d, P_char, 78 + gx, 88 + gy, pawR[0] + gx, pawR[1] + gy, bend=-1)
    v2.draw_paw(d, P_char, pawR[0] + gx, pawR[1] + gy)
    mon_glitch(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_room, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ------------------------------------------------------------------ 3. shrugging
def a_shrugging(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    mood = outfits.OUTFITS['shrugging']['mood']
    outfits.draw_room(d, P_room, i, t, mood)

    # double shrug: two bumps per loop
    e = v2.kf(t, [(0, 0), (0.10, 0), (0.15, 1), (0.22, 1), (0.27, 0),
                  (0.50, 0), (0.55, 1), (0.62, 1), (0.67, 0), (1, 0)])
    p = base_pose(breath=int(round(-1 * e)))
    p['hy'] = 60 + p['gy']
    p['tilt'] = int(round(2 * math.sin(2 * math.pi * 2 * t)))
    p['lookx'] = int(round(2 * math.sin(2 * math.pi * t)))
    bi = i % 30
    p['blink'] = 1 if bi in (27, 28, 30) else 0
    pawL = (44, 100 - 20 * e)
    pawR = (84, 100 - 20 * e)

    ticks = []
    if e > 0.5:                               # motion ticks above palms
        fl = (i // 2) % 2
        for px in (pawL[0] + p['gx'], pawR[0] + p['gx']):
            py = pawL[1] + p['gy'] - 6
            ticks += [(px - 4, py, 4 + fl), (px, py, 6 - fl), (px + 4, py, 4 + fl)]

    finish_char_and_desk(d, P_room, P_char, style, p, pawL, pawR, i, t,
                         ticks=ticks)


# ------------------------------------------------------------------ 4. scheming
def mon_flowchart(d, P, i, t):
    v2.rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    th = (150, 90, 230)                       # plan-purple, reads on screen
    pulse = (i // 5) % 2 == 0
    # boxes (middle one blinks as the "target")
    d.rectangle([32, 78, 42, 83], outline=th)
    d.rectangle([50, 78, 60, 83], outline=P['white'] if pulse else th)
    d.rectangle([41, 89, 51, 94], outline=th)
    # arrows
    d.line([43, 80, 49, 80], fill=th, width=1)
    d.line([46, 84, 46, 88], fill=th, width=1)
    d.line([52, 84, 52, 88], fill=th, width=1)
    # data packet racing along the top arrow, seamless wrap
    px = 43 + (i * 1.0 % 6)
    d.rectangle([int(px), 79, int(px) + 1, 81], fill=P['white'])
    # scheme progress bar fills + empties per loop
    bw = int(round(26 * ((i % 30) / 29.0 if (i // 30) % 2 == 0 else 1 - (i % 30) / 29.0)))
    d.rectangle([33, 93, 33 + bw, 94], fill=(255, 220, 120))
    v2.text(d, "PLAN", 33, 78, 1, th, clip=(30, 76, 64, 96))
    v2.text(d, "$$$", 51, 78, 1, (255, 220, 120), clip=(30, 76, 64, 96))
    d.rectangle([45, 97, 47, 98], fill=P['led_g'])


def a_scheming(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    mood = outfits.OUTFITS['scheming']['mood']
    outfits.draw_room(d, P_room, i, t, mood)

    p = base_pose(breath=int(round(1 * math.sin(2 * math.pi * 2 * t))))
    p['hy'] = 60 + p['gy']
    p['gx'] = int(round(3 * math.sin(2 * math.pi * 3 * t)))  # full-body lean
    p['lookx'] = 2 if (i // 15) % 2 == 0 else -2   # sidelong dart, seamless
    p['brow'] = 1
    p['tilt'] = int(round(3 * math.sin(2 * math.pi * 3 * t)))  # lean into it
    p['tail'] = int(round(3 * math.sin(2 * math.pi * 3 * t)))  # tail swish
    bi = i % 28
    p['blink'] = 1 if bi in (25, 26) else 0
    # narrowed-eye flicker: thin the eyes every ~15 frames for 3 frames
    flick = (i % 15) < 3

    rub = math.sin(2 * math.pi * 3 * t)       # 3 rub cycles per loop
    bounce = abs(math.sin(2 * math.pi * 3 * t))
    pawL = (60 - 6 * rub, 96 - 4 * bounce)
    pawR = (68 + 6 * rub, 96 - 4 * bounce)

    v2.draw_chair(d, P_room, 0)
    v2.draw_gigi(d, P_char, p, style, i, t)

    if flick:
        lx, ly = p['lookx'], p['looky']
        for x in (p['hx'] + p['gx'] - 7 + lx, p['hx'] + p['gx'] + 5 + lx):
            ey = p['hy'] + p['gy'] - 2 + ly
            d.rectangle([x, ey, x + 2, ey + 3], fill=P_char['fur'])
            d.line([x, ey + 1, x + 2, ey + 1], fill=(10, 10, 12), width=1)

    # sly grin overdraw
    hx = p['hx'] + p['gx'] + p['lookx']
    hy = p['hy'] + p['gy'] + p['looky']
    d.rectangle([hx - 4, hy + 6, hx + 4, hy + 10], fill=P_char['muzzle'])
    d.line([hx - 4, hy + 6, hx + 1, hy + 9], fill=(10, 10, 12), width=1)
    d.line([hx + 1, hy + 9, hx + 6, hy + 6], fill=(10, 10, 12), width=1)

    # purple sparkle orbiting between the rubbing paws (never rests)
    sp = 3 + 2 * abs(math.sin(2 * math.pi * 4 * t))
    oa = 2 * math.pi * 4 * t
    sparkle(d, 64 + p['gx'] + 7 * math.cos(oa), 90 + p['gy'] + 4 * math.sin(oa),
            sp, (150, 90, 230), P_char['white'])
    # scheming fingertip trail glints
    if (i // 4) % 2 == 0:
        for px in (pawL[0] + p['gx'], pawR[0] + p['gx']):
            d.rectangle([int(px) - 4, 92 + p['gy'], int(px) - 3, 92 + p['gy']],
                        fill=(150, 90, 230))

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    gx, gy = p['gx'], p['gy']
    v2.arm(d, P_char, 50 + gx, 88 + gy, pawL[0] + gx, pawL[1] + gy, bend=1)
    v2.draw_paw(d, P_char, pawL[0] + gx, pawL[1] + gy)
    v2.arm(d, P_char, 78 + gx, 88 + gy, pawR[0] + gx, pawR[1] + gy, bend=-1)
    v2.draw_paw(d, P_char, pawR[0] + gx, pawR[1] + gy)
    mon_flowchart(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_room, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ------------------------------------------------------------------ 5. panic
def mon_alert(d, P, i, t):
    v2.rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    yoff = i % 8                               # scrolling red alert lines
    for k in range(4):
        y = 78 + ((k * 8 + yoff) % 20)
        d.rectangle([32, y, 62, y + 2], fill=(255, 60, 60))
        d.rectangle([32, y, 38, y + 2], fill=(255, 180, 160))
    if (i // 6) % 2 == 0:
        v2.text(d, "!!", 44, 84, 1, (255, 255, 255))
    d.rectangle([45, 97, 47, 98], fill=P['led_r'])


def a_panic(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'red')

    rnd = random.Random(i * 3 + 11)
    jx = rnd.randint(-2, 2)                   # body shake jitter
    p = base_pose(sw=jx, breath=rnd.randint(-1, 0))
    p['hy'] = 60 + p['gy']
    p['blink'] = 0                            # eyes wide
    p['brow'] = 1
    p['earL'] = 2 if (i // 6) % 2 == 0 else 0
    p['earR'] = 2 if (i // 6) % 2 == 1 else 0

    fl = (i // 5) % 2                         # paws flail alternately
    pawL = (44, 100 - (40 if fl == 0 else 8))
    pawR = (84, 100 - (40 if fl == 1 else 8))

    v2.draw_chair(d, P_room, 0)
    v2.draw_gigi(d, P_char, p, style, i, t)
    open_mouth(d, P_char, p)                   # panic yelp

    # sweat drops flying off the head, seamless wrap
    for k in range(4):
        cyc = (i * 1.2 + k * 15) % 60
        sgn = 1 if k % 2 == 0 else -1
        sx = 64 + p['gx'] + sgn * (10 + cyc * 0.35)
        sy = (60 + p['gy']) - 12 - cyc * 0.30
        d.rectangle([int(sx), int(sy), int(sx) + 1, int(sy) + 1],
                    fill=(150, 210, 255))

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    gx, gy = p['gx'], p['gy']
    v2.arm(d, P_char, 50 + gx, 88 + gy, pawL[0] + gx, pawL[1] + gy, bend=1)
    v2.draw_paw(d, P_char, pawL[0] + gx, pawL[1] + gy)
    v2.arm(d, P_char, 78 + gx, 88 + gy, pawR[0] + gx, pawR[1] + gy, bend=-1)
    v2.draw_paw(d, P_char, pawR[0] + gx, pawR[1] + gy)
    mon_alert(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_room, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


STATES = {
    'dancing': a_dancing,
    'surprised': a_surprised,
    'shrugging': a_shrugging,
    'scheming': a_scheming,
    'panic': a_panic,
}


if __name__ == '__main__':
    for state, fn in STATES.items():
        gif = outfits.render_state(state, fn)
        qc = outfits.qc_state(state, gif)
        sheet = outfits.contact_sheet(state)
        print(f"{state}: {os.path.basename(gif)} "
              f"{os.path.getsize(gif)//1024}KB | "
              f"motion {qc['active']}/{qc['total']} "
              f"(min {qc['mind']:.2f} max {qc['maxd']:.2f}) | "
              f"colors {qc['colors']} | legib cap={qc['cap']} phone={qc['phone']} | "
              f"sheet {sheet}")
