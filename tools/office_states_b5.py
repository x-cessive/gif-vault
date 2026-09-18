#!/usr/bin/env python3
"""Office GIFs batch 5: salute, celebrating, gaming, rebooting, overheating.

Animators only — the rig (office_rig_v2) and outfit system (office_outfits)
are imported, never modified.
Animator signature: fn(img, P_room, P_char, style, i, n).
"""
import math
import random
from PIL import Image, ImageDraw, ImageChops

import office_rig_v2 as v2
import office_outfits as outfits

N = v2.N


# ---------------------------------------------------------------- 1. SALUTE
def a_salute(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = -3                                    # sit up straight
    p['hx'] = 64
    p['hy'] = 60 + p['gy']
    p['looky'] = -1
    bi = i % 45
    p['blink'] = 1 if bi in (42, 43) else 0
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))

    # snap envelope: up fast at t~0.10, hold, down at t~0.92
    up_raw = v2.kf(t, [(0, 0), (0.06, 0), (0.11, 1), (0.88, 1), (0.95, 0), (1, 0)])
    up = up_raw * up_raw * (3 - 2 * up_raw)
    if up > 0.5:                                    # head lifts with salute
        p['hy'] -= 1
        p['gy'] -= int(round(1 * math.sin(8 * math.pi * t)))  # confident bob
        p['brow'] = 1

    # right paw: desk -> cap brim
    rest = (84 + p['gx'], 100 + p['gy'])
    brim = (p['hx'] + p['gx'] + 16, p['hy'] + p['gy'] - 7)
    pawR = (rest[0] + (brim[0] - rest[0]) * up,
            rest[1] + (brim[1] - rest[1]) * up)
    pawL = (44 + p['gx'], 100 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    # ---- desk ----
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)

    # shine tick lines near the paw while saluting
    if up > 0.5:
        ax = P_char['accent']
        px, py = pawR
        for k in range(3):
            a = math.pi * (0.9 + 0.2 * k)
            l = 3 + (k + (i // 4)) % 3
            x1, y1 = px + int(round(8 * math.cos(a))), py + int(round(8 * math.sin(a)))
            x2, y2 = px + int(round((8 + l) * math.cos(a))), py + int(round((8 + l) * math.sin(a)))
            d.line([x1, y1, x2, y2], fill=ax, width=1)


# ---------------------------------------------------------------- 2. CELEBRATING
CONF = random.Random(42)
CONF_PIECES = [(CONF.random() * 128, CONF.random() * 150,
                CONF.choice(('accent', 'led_a', 'gold', 'paper3', 'white')),
                CONF.randint(1, 2)) for _ in range(28)]


def a_celebrating(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(2 * math.sin(4 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = -int(round(6 * abs(math.sin(2 * math.pi * t))))   # jump
    p['hx'] = 64
    p['hy'] = 60 + p['gy']
    p['looky'] = -1
    p['brow'] = 1
    bi = i % 40
    p['blink'] = 1 if bi in (38, 39) else 0
    p['tail'] = int(round(2 * math.sin(6 * math.pi * t)))
    p['earL'] = 2 if 10 <= i < 13 else 0
    p['earR'] = 2 if 38 <= i < 41 else 0

    # paws thrown up high
    wob = int(round(3 * math.sin(4 * math.pi * t)))
    pawL = (p['hx'] + p['gx'] - 22 + wob, p['hy'] + p['gy'] - 30)
    pawR = (p['hx'] + p['gx'] + 22 - wob, p['hy'] + p['gy'] - 30)

    v2.draw_gigi(d, P_char, p, style, i, t)
    # mouth open (overdraw the fixed closed-mouth line)
    ell = v2.ell
    ell(d, p['hx'] + p['gx'] + p['lookx'], p['hy'] + p['gy'] + 9 + p['looky'],
        3, 3, P_char['eye'])

    # ---- desk ----
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    # party main monitor: flashing party colors
    cols = [P_char['accent'], P_room['led_g'], P_room['gold'], P_room['paper3']]
    v2.rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=cols[(i // 5) % 4])
    v2.text(d, "WOO", 33, 82, 2, P_room['ink'])
    if (i // 5) % 2 == 0:
        v2.text(d, "!!", 38, 92, 1, P_room['white'])
    v2.draw_term_monitor(d, P_room, i, t)
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)

    # ---- confetti rain ----
    cmap = {'accent': P_char['accent'], 'led_a': P_room['led_a'],
            'gold': P_room['gold'], 'paper3': P_room['paper3'],
            'white': P_room['white']}
    for (x0, y0, ckey, sz) in CONF_PIECES:
        x = int(x0 + 3 * math.sin(4 * math.pi * t + y0))
        y = int((y0 + i * 2.2) % 150) - 12
        d.rectangle([x, y, x + sz, y + sz], fill=cmap[ckey])

    # ---- two firework bursts: expanding pixel rings ----
    for bx, by, t0 in ((34, 22, 0.08), (96, 28, 0.55)):
        if t0 <= t <= t0 + 0.30:
            u = (t - t0) / 0.30
            r = int(14 * u)
            col = v2.mix(P_char['accent'], P_room['white'], u)
            for a in range(8):
                ang = math.pi * a / 4 + u
                fx = int(bx + r * math.cos(ang))
                fy = int(by + r * math.sin(ang))
                d.rectangle([fx, fy, fx + 1, fy + 1], fill=col)
            if u < 0.25:
                d.rectangle([bx - 1, by - 1, bx + 1, by + 1], fill=P_room['white'])


# ---------------------------------------------------------------- 3. GAMING
def a_gaming(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1 * math.sin(6 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = 2 + int(round(1 * math.sin(6 * math.pi * t)))   # lean forward
    p['hx'] = 64
    p['hy'] = 60 + 2                                          # toward the screen
    p['looky'] = 1
    p['lookx'] = int(round(2 * math.sin(8 * math.pi * t)))    # track the action
    p['brow'] = 1
    bi = i % 50
    p['blink'] = 1 if bi in (47, 48) else 0
    p['tail'] = int(round(2 * math.sin(6 * math.pi * t)))

    # gamepad at chest, thumbs mashing (paw jitter every 2 frames)
    jx = 1 if (i // 2) % 2 == 0 else -1
    jy = 1 if ((i // 2) + 1) % 2 == 0 else -1
    pad_cx, pad_cy = p['hx'] + p['gx'], p['hy'] + p['gy'] + 18
    pawL = (pad_cx - 10 + jx, pad_cy + jy)
    pawR = (pad_cx + 10 - jx, pad_cy - jy)

    v2.draw_gigi(d, P_char, p, style, i, t)

    # ---- desk ----
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)

    # ---- main monitor: top-down vertical racer ----
    v2.rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P_room['screen'])
    d.line([40, 76, 40, 96], fill=(60, 68, 80), width=1)      # road edges
    d.line([54, 76, 54, 96], fill=(60, 68, 80), width=1)
    for y0 in range(0, 22, 6):                                  # scrolling dashes
        oy = 76 + ((y0 + i * 3) % 22)
        d.line([47, oy, 47, oy + 2], fill=P_room['led_g'], width=1)
    for k in range(2):                                          # enemy cars
        oy = 76 + ((k * 18 + i * 3) % 22)
        ox = 43 + (k * 5)
        d.rectangle([ox, oy, ox + 4, oy + 5], fill=P_room['led_r'])
        d.rectangle([ox + 1, oy + 1, ox + 2, oy + 2], fill=P_room['screen'])
    cx = 47 + int(round(3 * math.sin(4 * math.pi * t)))         # player weaving
    d.rectangle([cx - 2, 88, cx + 2, 94], fill=P_char['accent'])
    d.rectangle([cx - 1, 89, cx + 1, 90], fill=P_room['screen'])
    v2.text(d, "LVL1", 31, 77, 1, P_room['code'])
    v2.draw_term_monitor(d, P_room, i, t)

    # arms + gamepad (gamepad drawn before paws so thumbs grip it)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.rr(d, pad_cx - 11, pad_cy - 4, pad_cx + 11, pad_cy + 5, P_char['phone'], r=2)
    d.rectangle([pad_cx + 4, pad_cy - 2, pad_cx + 5, pad_cy - 1], fill=P_char['accent'])
    d.rectangle([pad_cx + 7, pad_cy, pad_cx + 8, pad_cy + 1], fill=P_room['gold'])
    d.rectangle([pad_cx - 8, pad_cy - 1, pad_cx - 7, pad_cy], fill=P_room['white'])
    v2.draw_paw(d, P_char, pawL[0], pawL[1], press_finger=0 if (i // 2) % 2 == 0 else 1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1], press_finger=2 if (i // 2) % 2 == 0 else 0)
    # button mash flashes: alternating every 2 frames
    if (i // 2) % 2 == 0:
        d.rectangle([pad_cx + 4, pad_cy - 2, pad_cx + 5, pad_cy - 1], fill=P_room['white'])
        d.rectangle([pad_cx + 3, pad_cy - 4, pad_cx + 8, pad_cy - 4], fill=P_char['accent'])
    else:
        d.rectangle([pad_cx + 7, pad_cy, pad_cx + 8, pad_cy + 1], fill=P_room['white'])
        d.rectangle([pad_cx + 3, pad_cy - 4, pad_cx + 8, pad_cy - 4], fill=P_room['gold'])
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ---------------------------------------------------------------- 4. REBOOTING
BOOT_LINES = ["BIOS OK", "MEM 640K", "LOAD GIGI", "READY> _"]


def a_rebooting(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    step = (i // 8) % 8                                        # quantized: 8 steps
    p['tilt'] = step - 3                                       # -3..4
    p['gy'] = step % 2                                        # mechanical micro-bob
    p['hx'] = 64
    p['hy'] = 60 + p['gy']
    p['blink'] = 1 if (i // 3) % 2 == 0 else 0                # eye flicker
    p['tail'] = 0
    p['lookx'] = 0
    pawL = (44 + p['gx'], 100 + p['gy'])
    pawR = (84 + p['gx'], 100 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    # ---- desk ----
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    # boot-text main monitor
    v2.rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P_room['screen'])
    shown = min(len(BOOT_LINES), i // 12 + 1)
    for k in range(shown):
        v2.text(d, BOOT_LINES[k], 32, 78 + k * 5, 1, P_room['code'])
    if (i // 6) % 2 == 0 and shown >= 4:
        v2.text(d, "_", 52, 93, 1, P_room['code'])
    v2.draw_term_monitor(d, P_room, i, t)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)

    # ---- glitch slices: 3 horizontal bands with seeded x-offsets ----
    for k in range(3):
        y0 = 20 + (k * 29 + i * 37) % 80
        xoff = ((i * 13 + k * 47) % 9) - 4
        band = img.crop((0, y0, 128, y0 + 3))
        img.paste(ImageChops.offset(band, xoff, 0), (0, y0))
    if (i // 4) % 4 == 0:                                     # static sparkle
        for k in range(6):
            x = (i * 41 + k * 53) % 128
            y = (i * 29 + k * 61) % 128
            d.rectangle([x, y, x, y], fill=P_room['white'])


# ---------------------------------------------------------------- 5. OVERHEATING
def a_overheating(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'warm')

    sw = int(round(1.5 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = 1 + int(round(1 * math.sin(4 * math.pi * t)))   # slumped, breathing
    p['hx'] = 64
    p['hy'] = 60 + p['gy']
    p['tilt'] = 1
    p['looky'] = 1
    bi = i % 30
    p['blink'] = 1 if bi in (27, 28) else 0
    p['tail'] = int(round(1 * math.sin(4 * math.pi * t)))

    # right paw fans her face, fast oscillation
    fan = int(round(4 * math.sin(16 * math.pi * t)))
    pawR = (p['hx'] + p['gx'] + 17, p['hy'] + p['gy'] + 4 + fan)
    pawL = (44 + p['gx'], 100 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)
    # open panting mouth
    mx = p['hx'] + p['gx'] + p['lookx']
    my = p['hy'] + p['gy'] + 9 + p['looky']
    ry = 2 + (1 if (i // 4) % 2 == 0 else 0)
    v2.ell(d, mx, my, 3, ry, P_char['eye'])

    # ---- desk ----
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    # temperature-warning main monitor: climbing bars
    v2.rr(d, 28, 74, 66, 100, P_room['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P_room['screen'])
    for k in range(5):
        fill = ((i + k * 12) % 60) / 60.0
        bh = int(2 + 13 * fill)
        bx = 33 + k * 6
        col = P_room['led_r'] if fill > 0.7 else P_room['led_a']
        d.rectangle([bx, 95 - bh, bx + 3, 95], fill=col)
    if (i // 6) % 2 == 0:
        v2.text(d, "TEMP!", 36, 77, 1, P_room['led_r'])
    v2.draw_term_monitor(d, P_room, i, t)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_mug(d, P_char, 92, 97, i, t)
    outfits.draw_headphones_desk(d, P_room, i, 104, 97)      # off her head
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)

    # ---- sweat drops ----
    for k in range(4):
        sx = p['hx'] + p['gx'] - 14 + k * 9
        sy = 34 + ((i * 3 + k * 17) % 38)
        d.rectangle([sx, sy, sx, sy + 1], fill=P_room['led_c'])

    # ---- heat waves rising off her head ----
    for k in range(2):
        wx = p['hx'] + p['gx'] - 8 + k * 15
        for s in range(5):
            wy = p['hy'] + p['gy'] - 24 - s * 3 - ((i + k * 4) % 3)
            wxo = wx + int(round(math.sin(6 * math.pi * t + s * 1.3)))
            col = P_room['led_a'] if (i + s + k) % 2 == 0 else P_room['led_c']
            d.rectangle([wxo, wy, wxo, wy], fill=col)

    # ---- red shimmer border ----
    shim = v2.mix((255, 60, 60), (255, 160, 80), 0.5 + 0.5 * math.sin(8 * math.pi * t))
    d.rectangle([2, 2, 125, 125], outline=shim)


STATES = {
    'salute': a_salute,
    'celebrating': a_celebrating,
    'gaming': a_gaming,
    'rebooting': a_rebooting,
    'overheating': a_overheating,
}


if __name__ == '__main__':
    for state, fn in STATES.items():
        gif = outfits.render_state(state, fn)
        print('rendered', gif, __import__('os').path.getsize(gif) // 1024, 'KB')
        q = outfits.qc_state(state, gif)
        print(q)
        cs = outfits.contact_sheet(state)
        print('contact:', cs)
