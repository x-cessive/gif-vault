#!/usr/bin/env python3
"""GIGI office rig v2 — batch-2 animators: tired, bitching, pushing_to_github,
deploying, debugging.

Extends office_rig_v2 (imported, never modified) + office_outfits (imported,
never modified). Every state uses outfits.draw_room for the identical office
and outfits.render_state for the exact ffmpeg recipe.

  tired:            slate-blue cap, slumped (gy+3), slow droopy blink, big
                    mid-loop yawn (open-mouth overdraw + head tips back),
                    then a slow satisfied-ish nod. Signature: yawn + nod.
  bitching:         maroon cap, headphones OFF (on the desk, right side),
                    arms crossed with an impatient 6Hz paw tap, pulsing red
                    anger X above the head, head tilt, foot-tap ticks,
                    angry brows + frown overdraw. Main monitor: red ERR.
                    Signature: tap + anger mark.
  pushing_to_github: green cap/white stripes, both paws shove a glowing green
                    GIT box upward — rises, exits top, fades back in at the
                    bottom (seamless), motion trail ghosts, satisfied nod at
                    the end. Main monitor: animated forking branch diagram.
                    Signature: launch box + trail.
  deploying:        orange cap, big red button on the desk right that flashes
                    white when the right paw slaps it at t~0.3, then a chunky
                    rocket launches on the MAIN monitor (custom draw: rising
                    rocket, flickering flame, pad smoke; returns to pad by
                    loop end). Gigi leans in after the slap.
                    Signature: button flash + rocket launch.
  debugging:        yellow cap/purple stripes, head tilts side to side,
                    squint-scan (lookx oscillates, squint overdraw), right paw
                    traces a glowing trail in the air, bright scan line sweeps
                    the main monitor vertically. Signature: scan line sweep.

60 unique frames @24fps, seamless loops (all envelopes integer cycles),
solid colors only, <=64 colors, same ffmpeg recipe.
"""
import math
import os
from PIL import Image, ImageDraw

import office_rig_v2 as v2
import office_outfits as outfits
from office_rig_v2 import mix, kf, text, text_c, ell, rr


# ---------------------------------------------------------------- tired
def a_tired(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_char, sw)
    p = v2.default_pose()
    breathe = int(round(1.5 * math.sin(2 * math.pi * t)))       # slow breathing
    yawn = kf(t, [(0, 0), (0.32, 0), (0.44, 1), (0.58, 1), (0.70, 0), (1, 0)])
    nod_env = kf(t, [(0, 0), (0.62, 0), (0.72, 1), (0.94, 1), (1, 0)])
    nod = int(round(2 * math.sin(4 * math.pi * t)))             # 2 slow nods
    p['gx'] = sw
    p['gy'] = 3 + breathe                                       # the slump
    p['hx'] = 64
    p['hy'] = 60 + p['gy'] + nod_env * nod - int(round(2 * yawn))
    p['tilt'] = int(round(1 * math.sin(2 * math.pi * t))) - int(round(2 * yawn))
    bi = i % 40
    p['blink'] = 1 if bi in (30, 31, 32, 33) else 0             # droopy blink
    p['looky'] = 1
    if 12 <= i < 15:
        p['earL'] = 2
    if 40 <= i < 43:
        p['earR'] = 2
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))
    pawL = (40 + p['gx'], 103 + p['gy'])
    pawR = (88 + p['gx'], 103 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    if yawn > 0.25:                                            # the big yawn
        mx = p['hx'] + p['gx'] + p['lookx']
        my = p['hy'] + p['gy'] + 8 + p['looky']
        ell(d, mx, my, 4, int(round(2 + 3 * yawn)), (30, 12, 12))

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- bitching
def draw_err_monitor(d, P, i, t):
    rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    if (i // 8) % 2 == 0:                                      # red alert flash
        d.rectangle([30, 76, 64, 96], fill=mix(P['screen'], (160, 20, 20), 0.45))
    d.rectangle([30, 76, 64, 96], outline=(255, 80, 80))
    text_c(d, "ERR", 47, 79, 2, (255, 90, 90))
    text_c(d, "404", 47, 90, 1, (255, 150, 150))
    d.rectangle([46, 97, 48, 98], fill=P['led_r'])
    d.rectangle([46, 75, 47, 75], fill=P['led_r'])


def a_bitching(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_char, sw)
    p = v2.default_pose()
    rock = int(round(2 * math.sin(2 * math.pi * 3 * t)))        # angry rocking
    p['gx'] = sw + rock
    p['gy'] = int(round(1 * math.sin(2 * math.pi * t)))
    p['hx'] = 64 + int(round(2 * math.sin(2 * math.pi * 6 * t)))  # head shake
    p['hy'] = 60 + p['gy']
    p['tilt'] = 2 + int(round(1 * math.sin(4 * math.pi * t)))    # impatient tilt
    p['lookx'] = int(round(2 * math.sin(4 * math.pi * t)))
    p['brow'] = 0
    bi = i % 30
    p['blink'] = 1 if bi in (27, 28) else 0
    if 18 <= i < 21:
        p['earL'] = 2
    if 48 <= i < 51:
        p['earR'] = 2
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))
    p['thump'] = 1 if (i // 4) % 2 == 0 else 0                 # tail thumping

    tap = -3 if math.sin(2 * math.pi * 15 * t) > 0 else 0       # 6 Hz paw tap
    pawL = (58 + p['gx'], 91 + p['gy'])                        # arms crossed
    pawR = (70 + p['gx'], 93 + p['gy'] + tap)

    v2.draw_gigi(d, P_char, p, style, i, t)

    hx = p['hx'] + p['gx'] + p['lookx']
    hy = p['hy'] + p['gy'] + p['looky']
    d.line([hx - 9, hy - 7, hx - 3, hy - 5], fill=(10, 10, 12), width=1)
    d.line([hx + 9, hy - 7, hx + 3, hy - 5], fill=(10, 10, 12), width=1)
    d.line([hx - 3, hy + 8, hx + 3, hy + 8], fill=P_char['muzzle'], width=1)
    d.line([hx - 3, hy + 9, hx + 3, hy + 7], fill=(10, 10, 12), width=1)
    ax = hx + 16
    ay = hy - 30 + int(round(1.5 * math.sin(4 * math.pi * t)))
    acol = (255, 255, 255) if (i // 5) % 2 == 0 else (255, 60, 60)
    text(d, 'X', ax, ay, 2, acol)                              # anger mark
    for k in range(4):                                         # anger steam
        zt = (t + k / 4) % 1.0
        sgn = 1 if k % 2 == 0 else -1
        sx = hx + sgn * (13 + int(round(2 * math.sin(6 * math.pi * t + k))))
        sy = int(hy - 18 - 22 * zt)
        scol = P_room['steam'] if (k + i // 6) % 2 == 0 else (255, 130, 120)
        d.rectangle([sx, sy, sx + 1, sy + 1], fill=scol)
        d.rectangle([sx - 1, sy - 1, sx + 2, sy + 2], outline=scol)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    draw_err_monitor(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    # crossed arms drawn AFTER the monitors so they read in front
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    if tap == 0:                                               # tap impact ticks
        for k in range(2):
            d.line([pawR[0] - 5, 96 + k * 3, pawR[0] - 2, 95 + k * 3],
                   fill=P_char['accent'], width=1)
    if math.sin(2 * math.pi * 15 * t) > 0:                     # foot tap ticks
        fx = 44 + p['gx']
        d.line([fx, 117 + p['gy'], fx + 3, 117 + p['gy']],
               fill=P_char['accent'], width=1)
        d.line([fx + 1, 120 + p['gy'], fx + 4, 120 + p['gy']],
               fill=P_char['accent'], width=1)
    outfits.draw_headphones_desk(d, P_room, i, 98, 98)          # thrown on desk
    v2.draw_mug(d, P_char, 32, 96, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- pushing_to_github
def draw_fork_monitor(d, P, i, t):
    rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    d.line([38, 78, 38, 94], fill=P['code_d'], width=1)        # main branch
    prog = (i // 5) % 6                                       # 2 cycles/loop
    for k, y in enumerate((80, 85, 90)):                      # commit dots
        d.rectangle([37, y - 1, 39, y + 1],
                    fill=P['led_g'] if k < prog else P['code_d'])
    if prog >= 2:                                             # fork appears
        d.line([38, 85, 52, 85], fill=P['code'], width=1)
        d.line([52, 85, 52, 90], fill=P['code'], width=1)
    if prog >= 3:
        d.rectangle([51, 89, 53, 91], fill=P['led_g'])
    if prog >= 4:
        d.line([52, 90, 60, 90], fill=P['accent'], width=1)
        text(d, '>', 61, 88, 1, P['accent'])
    if prog >= 5:
        text(d, 'PUSH', 36, 92, 1, P['led_g'])
    d.rectangle([46, 97, 48, 98], fill=P['led_g'])
    d.rectangle([46, 75, 47, 75], fill=P['led_r'])


def a_pushing_to_github(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_char, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = int(round(1 * math.sin(2 * math.pi * t)))
    p['hx'] = 64
    p['hy'] = 60 + p['gy']
    nod_env = kf(t, [(0, 0), (0.68, 0), (0.78, 1), (0.95, 1), (1, 0)])
    p['hy'] += nod_env * int(round(1.5 * math.sin(4 * math.pi * t)))
    p['tilt'] = nod_env
    p['looky'] = -1
    bi = i % 30
    p['blink'] = 1 if bi in (27, 28) else 0
    if 22 <= i < 25:
        p['earL'] = 2
    if 50 <= i < 53:
        p['earR'] = 2
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))

    v2.draw_gigi(d, P_char, p, style, i, t)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    draw_fork_monitor(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)

    # ---- the glowing GIT box: rises, exits top, fades back in at the bottom
    box_col = (80, 220, 120)
    env = kf(t, [(0, 0), (0.06, 1), (0.86, 1), (1, 0)])
    bw, bh = 18, 14
    bx = 64 + p['gx'] - bw // 2
    by = int(round(100 - 125 * t))
    if env > 0:
        for k in range(4, 0, -1):                             # motion trail
            ty = by + k * 9
            if ty < 112:
                tc = mix(P_room['screen'], box_col, (5 - k) * 0.18 * env)
                d.rectangle([bx, ty, bx + bw, ty + bh], fill=tc)
        if env > 0.6:                                         # glow outline
            d.rectangle([bx - 1, by - 1, bx + bw + 1, by + bh + 1],
                        outline=(200, 255, 210))
        d.rectangle([bx, by, bx + bw, by + bh],
                    fill=mix(P_room['screen'], box_col, env))
        if env > 0.5:
            d.rectangle([bx + 2, by + 2, bx + bw - 2, by + 4], fill=box_col)
            text_c(d, 'GIT', bx + bw // 2, by + 6, 1, (10, 30, 15))

    # ---- paws: shove the box up, then drop back to the desk
    push = kf(t, [(0, 1), (0.55, 1), (0.68, 0), (0.94, 0), (1, 1)])
    pl_x = int(round(56 + (44 - 56) * (1 - push))) + p['gx']
    pl_y = int(round((by + bh + 4) + (100 - (by + bh + 4)) * (1 - push))) + p['gy']
    pr_x = int(round(72 + (84 - 72) * (1 - push))) + p['gx']
    pr_y = int(round((by + bh + 4) + (100 - (by + bh + 4)) * (1 - push))) + p['gy']
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pl_x, pl_y, bend=1)
    v2.draw_paw(d, P_char, pl_x, pl_y)
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pr_x, pr_y, bend=-1)
    v2.draw_paw(d, P_char, pr_x, pr_y)

    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- deploying
def draw_deploy_button(d, P, i, t, flash):
    rr(d, 90, 94, 108, 101, P['slate_d'], r=2)                 # base
    col = (255, 255, 255) if flash > 0.5 else (255, 60, 60)
    rr(d, 92, 90, 106, 99, col, r=4)                           # the big red one
    if flash > 0.5:                                            # impact flash rays
        for k in range(6):
            a = k * math.pi / 3 + 0.2 * math.sin(8 * math.pi * t)
            x1 = 99 + int(round(10 * math.cos(a)))
            y1 = 95 + int(round(6 * math.sin(a)))
            x2 = 99 + int(round(15 * math.cos(a)))
            y2 = 95 + int(round(10 * math.sin(a)))
            d.line([x1, y1, x2, y2], fill=(255, 255, 255), width=1)
    elif (i // 6) % 2 == 0:                                   # idle "press me" pulse
        d.rectangle([91, 89, 107, 100], outline=P['accent'])
    else:
        d.rectangle([91, 89, 107, 100], outline=(255, 140, 140))


def draw_rocket_monitor(d, P, i, t):
    rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    for k, (sx, sy) in enumerate(((34, 80), (58, 78), (44, 82), (60, 88), (36, 90))):
        if (i // 6 + k) % 2:
            d.rectangle([sx, sy, sx, sy], fill=P['white'])
    d.rectangle([42, 93, 52, 95], fill=P['slate'])             # launch pad
    env = kf(t, [(0, 0), (0.12, 0), (0.35, 1), (0.52, 0),       # two flights
                 (0.60, 0), (0.80, 1), (0.95, 0), (1, 0)])
    ry = 88 - int(round(14 * env))                             # rises, returns
    d.rectangle([45, ry - 6, 49, ry + 2], fill=P['white'])
    d.polygon([45, ry - 6, 49, ry - 6, 47, ry - 10], fill=(255, 80, 80))
    d.rectangle([46, ry - 4, 48, ry - 2], fill=P['led_c'])
    d.polygon([45, ry + 2, 43, ry + 5, 45, ry + 4], fill=(255, 80, 80))
    d.polygon([49, ry + 2, 51, ry + 5, 49, ry + 4], fill=(255, 80, 80))
    if env > 0.02:                                            # flame + pad smoke
        fl = 4 + int(round(3 * math.sin(30 * math.pi * t)))
        d.rectangle([45, ry + 3, 49, ry + 3 + fl], fill=(255, 180, 60))
        d.rectangle([46, ry + 3, 48, ry + 3 + fl + 3], fill=(255, 255, 200))
        for k in range(4):
            sx = 43 + k * 4 + int(round(2 * math.sin(8 * math.pi * t + k)))
            sy = 92 - int((i * 2 + k * 7) % 12)
            d.rectangle([sx, sy, sx + 1, sy + 1], fill=P['steam'])
            d.rectangle([sx - 1, sy - 1, sx + 2, sy + 2], outline=P['steam'])
    d.rectangle([46, 97, 48, 98], fill=P['led_g'])
    d.rectangle([46, 75, 47, 75], fill=P['led_r'])


def a_deploying(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_char, sw)
    p = v2.default_pose()
    lean = kf(t, [(0, 0), (0.35, 0), (0.48, 1), (0.95, 1), (1, 0)])
    renv = kf(t, [(0, 0), (0.12, 0), (0.35, 1), (0.52, 0),     # rocket flight env
                  (0.60, 0), (0.80, 1), (0.95, 0), (1, 0)])
    p['gx'] = sw + int(round(3 * lean)) \
        + int(round(1 * math.sin(4 * math.pi * t))) * lean     # leans in
    p['gy'] = int(round(1 * math.sin(2 * math.pi * t))) \
        + int(round(1 * math.sin(4 * math.pi * t)))            # ready bounce
    p['hx'] = 64
    p['hy'] = 60 + p['gy'] - lean - int(round(2 * renv))      # bobs with launch
    p['tilt'] = lean
    p['lookx'] = int(round(3 * lean))
    p['looky'] = -1                                          # eyes track up
    bi = i % 30
    p['blink'] = 1 if bi in (27, 28) else 0
    if 8 <= i < 11:
        p['earL'] = 2
    if 36 <= i < 39:
        p['earR'] = 2
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))

    v2.draw_gigi(d, P_char, p, style, i, t)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    draw_rocket_monitor(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    flash = kf(t, [(0, 0), (0.28, 0), (0.30, 1), (0.48, 1), (0.60, 0),
                  (0.64, 1), (0.75, 1), (0.84, 0), (1, 0)])
    draw_deploy_button(d, P_room, i, t, flash)

    # ---- right paw slaps the button at t~0.3, confirming tap at t~0.65
    pr_x = int(round(kf(t, [(0, 84), (0.16, 84), (0.24, 92), (0.30, 99),
                            (0.48, 84), (0.58, 84), (0.64, 96), (0.70, 99),
                            (0.80, 84), (1, 84)]))) + p['gx']
    pr_y = int(round(kf(t, [(0, 100), (0.16, 100), (0.24, 84), (0.30, 92),
                            (0.48, 100), (0.58, 100), (0.64, 90), (0.70, 92),
                            (0.80, 100), (1, 100)]))) + p['gy']
    pawL = (44 + p['gx'], 100 + p['gy'] - int(round(14 * renv)))  # fist pump
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pr_x, pr_y, bend=-1)
    v2.draw_paw(d, P_char, pr_x, pr_y)

    v2.draw_mug(d, P_char, 32, 96, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- debugging
def draw_scan_monitor(d, P, i, t):
    rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    pitch = 7
    yoff = i % pitch
    for k in range(-1, 5):                                     # dim scrolling code
        idx = (k + i // pitch) % len(v2.CODE_LINES)
        y = 76 + k * pitch - yoff + 1
        text(d, v2.CODE_LINES[idx], 32, y, 1, P['code_d'], clip=(30, 76, 64, 96))
    sy = 76 + int(round(16 * (0.5 + 0.5 * math.sin(2 * math.pi * t))))
    d.rectangle([30, sy, 64, sy + 3], fill=mix(P['accent'], P['screen'], 0.45))
    d.rectangle([30, sy, 64, sy], fill=P['white'])              # the scan line
    d.rectangle([46, 97, 48, 98], fill=P['led_g'])
    d.rectangle([46, 75, 47, 75], fill=P['led_r'])


def a_debugging(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_char, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = int(round(1 * math.sin(2 * math.pi * t)))
    p['hx'] = 64
    p['hy'] = 60 + p['gy']
    p['tilt'] = int(round(3 * math.sin(2 * math.pi * t)))       # side to side
    p['lookx'] = int(round(4 * math.sin(4 * math.pi * t)))      # squint-scan
    p['looky'] = 0
    bi = i % 40
    p['blink'] = 1 if bi in (37, 38) else 0
    if 10 <= i < 13:
        p['earL'] = 2
    if 42 <= i < 45:
        p['earR'] = 2
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))
    pawL = (44 + p['gx'], 100 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    hx = p['hx'] + p['gx'] + p['lookx']                        # squint overdraw
    hy = p['hy'] + p['gy'] + p['looky']
    for ex in (hx - 7, hx + 5):
        d.rectangle([ex, hy + 1, ex + 2, hy + 1], fill=P_char['fur'])

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    draw_scan_monitor(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)

    # ---- right paw traces lines in the air, glowing trail behind
    tx = int(round(8 * math.sin(4 * math.pi * t)))
    ty = int(round(6 * math.sin(8 * math.pi * t + 1)))
    pr_x = 80 + p['gx'] + tx
    pr_y = 84 + p['gy'] + ty
    for k in range(1, 5):
        tt = t - k / 60
        qx = 80 + p['gx'] + int(round(8 * math.sin(4 * math.pi * tt)))
        qy = 84 + p['gy'] + int(round(6 * math.sin(8 * math.pi * tt + 1)))
        d.rectangle([qx, qy, qx, qy],
                    fill=mix(P_char['accent'], P_room['screen'], k * 0.2))
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pr_x, pr_y, bend=-1)
    v2.draw_paw(d, P_char, pr_x, pr_y)

    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- driver
ANIMATORS = {
    'tired': a_tired,
    'bitching': a_bitching,
    'pushing_to_github': a_pushing_to_github,
    'deploying': a_deploying,
    'debugging': a_debugging,
}

if __name__ == '__main__':
    for state in ('tired', 'bitching', 'pushing_to_github', 'deploying', 'debugging'):
        g = outfits.render_state(state, ANIMATORS[state], workdir=state)
        print('rendered', g, os.path.getsize(g) // 1024, 'KB')
        q = outfits.qc_state(state, g)
        print(f"motion: {q['active']}/{q['total']} active pairs, "
              f"min {q['mind']:.2f} max {q['maxd']:.2f}")
        print('gif colors:', q['colors'], '| cap:', q['cap'], '| phone:', q['phone'])
        print('contact:', outfits.contact_sheet(state, workdir=state))
        print()
