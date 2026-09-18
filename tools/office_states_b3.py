#!/usr/bin/env python3
"""GIGI office rig v2 — batch 3: facepalm, laughing, smug, drinking_coffee, eating_snack.

Extends office_rig_v2 + office_outfits (imported, never modified).

Animator signature: fn(img, P_room, P_char, style, i, n)
  - outfits.draw_room(d, P_room, i, t, mood) for the identical office.
  - P_room: room/desk/screens.  P_char: draw_gigi/arms/paws/mug.
  - style = outfits.style_for(state).

60 unique frames @24fps, seamless loops (every envelope = integer cycles
per 60 frames). 128px grid, NEAREST x4 -> 512x512, exact ffmpeg recipe.
"""
import math
import os

from PIL import ImageDraw

import office_rig_v2 as v2
import office_outfits as outfits
from office_rig_v2 import kf


# ---------------------------------------------------------------- shared bits
def anim_bits(p, i, t, blink_mod=30):
    """Ambient character life shared by all batch-3 states."""
    p['tail'] = int(round(2 * math.sin(2 * math.pi * t)))
    p['thump'] = 1 if (i // 5) % 4 == 0 else 0
    bi = i % blink_mod
    p['blink'] = 1 if bi in (blink_mod - 3, blink_mod - 2) else 0
    p['earL'] = 2 if 18 <= i < 21 else 0
    p['earR'] = 2 if 44 <= i < 47 else 0
    return p


def swivel(t, amp=1.5):
    return int(round(amp * math.sin(2 * math.pi * t)))


def smooth(s):
    return s * s * (3 - 2 * s)


def mouth_cx_cy(p):
    return (p['hx'] + p['gx'] + p['lookx'],
            p['hy'] + p['gy'] + 8 + p['looky'])


# ================================================================== 1. facepalm
def a_facepalm(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, outfits.OUTFITS['facepalm']['mood'])

    sw = swivel(t)
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['hx'] = 64
    p['hy'] = 60

    # snap envelope: fast hit at t~0.25, hold, release at 0.8
    s = smooth(kf(t, [(0, 0), (0.10, 0), (0.22, 1), (0.72, 1), (0.82, 0), (1, 0)]))
    held = s > 0.5

    if held:
        # head shakes slowly while held; dips into the paw
        p['hx'] += int(round(2 * math.sin(4 * math.pi * t)))
        p['hy'] += int(round(1.5 * s))
        p['blink'] = 1                                   # eyes squeezed
        p['brow'] = 1
    else:
        p = anim_bits(p, i, t)

    # right paw: rest -> forehead -> rest
    fx = p['hx'] + p['gx'] + 5
    fy = p['hy'] + p['gy'] - 7
    pawRx = 84 + p['gx'] + (fx - 84 - p['gx']) * s
    pawRy = 100 + p['gy'] + (fy - 100 - p['gy']) * s
    # left paw: frustrated desk tap while waiting for the snap
    tap = -3 if ((i // 5) % 2 == 0 and s < 0.5) else 0
    pawLx, pawLy = 44 + p['gx'], 102 + p['gy'] + tap

    v2.draw_gigi(d, P_char, p, style, i, t)

    # impact starburst at the exact snap moment
    imp = kf(t, [(0.17, 0), (0.22, 1), (0.30, 0)])
    if imp > 0.05:
        r = int(round(3 + 5 * imp))
        for a in range(8):
            ang = a * math.pi / 4 + t * 20
            x2 = fx + int(round(r * math.cos(ang)))
            y2 = fy + int(round(r * math.sin(ang)))
            d.line([fx, fy, x2, y2],
                   fill=P_char['white'] if a % 2 == 0 else P_char['accent'],
                   width=1)
    # radiating impact lines while held (flickering)
    if held and (i // 2) % 2 == 0:
        for a in range(8):
            ang = a * math.pi / 4
            x1 = fx + int(round(6 * math.cos(ang)))
            y1 = fy + int(round(6 * math.sin(ang)))
            x2 = fx + int(round(10 * math.cos(ang)))
            y2 = fy + int(round(10 * math.sin(ang)))
            d.line([x1, y1, x2, y2], fill=P_char['accent'], width=1)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawLx, pawLy, bend=1)
    v2.draw_paw(d, P_char, pawLx, pawLy)
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawRx, pawRy, bend=-1)
    v2.draw_paw(d, P_char, pawRx, pawRy)
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ================================================================== 2. laughing
def a_laughing(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, outfits.OUTFITS['laughing']['mood'])

    sw = swivel(t)
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    # fast shoulder shake (8 cycles/loop) + bounce
    p['gx'] = sw + int(round(2 * math.sin(16 * math.pi * t)))
    p['gy'] = -int(round(1 * abs(math.sin(8 * math.pi * t))))
    p['hx'] = 64
    p['hy'] = 57                                       # head tips back
    p['tilt'] = -1
    p['looky'] = -1
    p['lookx'] = int(round(2 * math.sin(16 * math.pi * t)))
    p = anim_bits(p, i, t, blink_mod=24)

    # paws on belly
    pawL = (50 + p['gx'], 106 + p['gy'])
    pawR = (78 + p['gx'], 106 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    # open laughing mouth (overdraw the fixed closed line)
    mcx, mcy = mouth_cx_cy(p)
    d.rectangle([mcx - 4, mcy - 2, mcx + 4, mcy + 2], fill=P_char['muzzle'])
    v2.ell(d, mcx, mcy, 4, 5, P_char['eye'])

    # laugh tears falling from the eyes (2 tears, 2 falls per loop)
    tear_col = (150, 210, 255)
    for k in (0, 1):
        zt = (2 * t + k * 0.5) % 1.0
        ex = p['hx'] + p['gx'] + p['lookx'] + (-7 if k == 0 else 5)
        sy = p['hy'] + p['gy'] + p['looky'] + 3
        ty = sy + int(round(zt * 20))
        fade = v2.mix(tear_col, P_room['wall'], zt * 0.7)
        d.rectangle([ex + 1, ty, ex + 1, ty + 2], fill=fade)

    # rising "HA"s in the signature pink
    for k in range(3):
        zt = (t + k / 3) % 1.0
        qx = p['hx'] + p['gx'] - 24 + k * 9 + int(round(3 * math.sin(10 * math.pi * t + k)))
        qy = p['hy'] + p['gy'] - 24 - int(round(zt * 26))
        col = v2.mix(P_char['accent'], P_room['wall'], zt * 0.65)
        v2.text(d, 'HA', qx, qy, 1, col)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ================================================================== 3. smug
def draw_trophy_monitor(d, P, i, t):
    """Main monitor showing a trophy + rising stats arrow (smug signature)."""
    v2.rr(d, 28, 74, 66, 100, P['bezel'], r=2)
    d.rectangle([30, 76, 64, 96], fill=P['screen'])
    # ascending bars with a gentle 2-cycle pulse, gold
    for b, h in enumerate((5, 8, 11, 14)):
        hh = h + int(round(1.5 * math.sin(4 * math.pi * t + b * 1.3)))
        x = 33 + b * 7
        d.rectangle([x, 93 - hh, x + 4, 93], fill=P['gold'])
    # upward stats arrow
    d.line([33, 90, 60, 79], fill=P['white'], width=1)
    d.polygon([60, 79, 55, 79, 59, 83], fill=P['white'])
    # scrolling ticker tape along the screen bottom (1px/frame, seamless)
    unit = 'GIGI+12% '
    uw = v2.text_w(unit, 1)
    x0 = 34 - (i % uw)
    while x0 < 64:
        v2.text(d, unit, x0, 94, 1, P['led_g'], clip=(30, 76, 64, 96))
        x0 += uw
    # tiny trophy top-left
    d.rectangle([33, 78, 37, 82], fill=P['gold'])
    d.rectangle([34, 82, 36, 84], fill=P['gold'])
    d.rectangle([33, 84, 37, 85], fill=P['gold'])
    tw = (i // 4) % 2
    v2.text(d, 'W', 55 + tw, 90, 1, P['led_g'])
    d.rectangle([45, 97, 47, 98], fill=P['led_g'])
    d.rectangle([46, 75, 47, 75], fill=P['led_r'])


def a_smug(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, outfits.OUTFITS['smug']['mood'])

    # confident rock: 4 rocks per loop, chair synced to the main rock
    rk = int(round(4 * math.sin(8 * math.pi * t)))
    sw = int(round(2 * math.sin(2 * math.pi * t)))
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw + rk
    p['gy'] = -2 + int(round(1.5 * math.sin(4 * math.pi * t + 1)))
    p['hx'] = 64
    p['hy'] = 58                                       # deep lean-back
    p['tilt'] = int(round(3 * math.sin(6 * math.pi * t + 1)))
    p['looky'] = -1
    p['lookx'] = int(round(2 * math.sin(4 * math.pi * t)))
    p = anim_bits(p, i, t, blink_mod=40)

    # paws behind head, riding the rock
    pawL = (p['hx'] + p['gx'] - 15 + rk // 2, p['hy'] + p['gy'] - 9)
    pawR = (p['hx'] + p['gx'] + 15 + rk // 2, p['hy'] + p['gy'] - 9)

    v2.draw_gigi(d, P_char, p, style, i, t)

    # sly grin: cover the default mouth line, draw a tilted smirk
    mcx, mcy = mouth_cx_cy(p)
    d.rectangle([mcx - 4, mcy - 1, mcx + 4, mcy + 1], fill=P_char['muzzle'])
    d.line([mcx - 4, mcy + 1, mcx + 3, mcy - 1], fill=P_char['eye'], width=1)

    # gold glint sparkle at her side: big/small alternating every 5 frames
    gx_, gy_ = p['hx'] + p['gx'] + 26, p['hy'] + p['gy'] - 16
    big = (i // 5) % 2 == 0
    r = 5 if big else 2
    glint = P_char['accent']
    core = P_char['white'] if big else glint
    d.line([gx_ - r, gy_, gx_ + r, gy_], fill=glint, width=1)
    d.line([gx_, gy_ - r, gx_, gy_ + r], fill=glint, width=1)
    d.rectangle([gx_, gy_, gx_, gy_], fill=core)
    if big:
        d.rectangle([gx_ - 3, gy_ - 3, gx_ - 3, gy_ - 3], fill=glint)
        d.rectangle([gx_ + 3, gy_ + 3, gx_ + 3, gy_ + 3], fill=glint)
    # second smaller glint on the left, flashing in bursts
    if (i // 10) % 3 == 0:
        lx_, ly_ = p['hx'] + p['gx'] - 24, p['hy'] + p['gy'] - 12
        d.line([lx_ - 2, ly_, lx_ + 2, ly_], fill=glint, width=1)
        d.line([lx_, ly_ - 2, lx_, ly_ + 2], fill=glint, width=1)
        d.rectangle([lx_, ly_, lx_, ly_], fill=P_char['white'])

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    draw_trophy_monitor(d, P_room, i, t)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_char, 92, 97, i, t)
    # arms to the paws behind her head
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ================================================================== 4. drinking_coffee
def a_drinking_coffee(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, outfits.OUTFITS['drinking_coffee']['mood'])

    sw = swivel(t)
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['hx'] = 64
    p['hy'] = 60

    # sip envelope: grab -> raise -> tip back & sip -> lower -> rest
    s = smooth(kf(t, [(0, 0), (0.12, 0), (0.28, 1), (0.52, 1), (0.68, 0), (1, 0)]))
    sipping = s > 0.55
    if sipping:
        p['tilt'] = -2                                 # head tips back
        p['hy'] -= 2
        p['blink'] = 1                                 # satisfied eye-close
        p['brow'] = 0
    else:
        p = anim_bits(p, i, t)

    # mug travels from desk to mouth and back
    mcx, mcy = mouth_cx_cy(p)
    mugx = 92 + (mcx - 3 - 92) * s
    mugy = 97 + (mcy - 97) * s
    if s > 0.02:
        pawR = (mugx + 6, mugy + 1)
    else:
        pawR = (84 + p['gx'], 100 + p['gy'])
    pawL = (44 + p['gx'], 102 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    # headphones OFF: parked on the desk, left side
    outfits.draw_headphones_desk(d, P_char, i, 28, 96)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    # mug drawn after the paw so the paw reads as holding it
    v2.draw_mug(d, P_char, mugx, mugy, i, t)
    # extra steam curls while the mug is up
    if s > 0.3:
        for k in range(2):
            sx = mugx - 2 + k * 4 + int(round(1.5 * math.sin(6 * math.pi * t + k * 2)))
            sy = mugy - 8 - ((i * 2 + k * 7) % 9)
            d.rectangle([sx, sy, sx + 1, sy + 2], fill=P_char['steam'])
    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


# ================================================================== 5. eating_snack
def draw_fish_snack(d, x, y, P, i, flip=False):
    x, y = int(round(x)), int(round(y))
    d.rectangle([x - 2, y - 1, x + 2, y + 1], fill=P['led_a'])
    wag = 1 if (i // 3) % 2 == 0 else -1
    if flip:
        d.polygon([x + 2, y - 1, x + 4, y + wag, x + 2, y + 1], fill=P['led_a'])
        d.rectangle([x - 1, y - 1, x - 1, y - 1], fill=P['ink'])
    else:
        d.polygon([x - 2, y - 1, x - 4, y + wag, x - 2, y + 1], fill=P['led_a'])
        d.rectangle([x + 1, y - 1, x + 1, y - 1], fill=P['ink'])


def a_eating_snack(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, outfits.OUTFITS['eating_snack']['mood'])

    sw = swivel(t)
    v2.draw_chair(d, P_room, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['hx'] = 64
    p['hy'] = 60

    # raise fish -> chomp -> lower
    s = smooth(kf(t, [(0, 0), (0.10, 0), (0.26, 1), (0.60, 1), (0.76, 0), (1, 0)]))
    chomping = s > 0.5

    # head dips with each bite: 4 dips per loop
    bite = (1 - math.cos(8 * math.pi * t)) / 2 if chomping else 0
    p['hy'] += int(round(1.5 * bite))
    p = anim_bits(p, i, t) if not chomping else p
    if chomping:
        p['blink'] = 1 if (i // 6) % 2 == 0 else 0

    mcx, mcy = mouth_cx_cy(p)
    # fish travels from rest to mouth
    fx = 84 + p['gx'] + (mcx - 2 - 84 - p['gx']) * s
    fy = 100 + p['gy'] + (mcy - 100 - p['gy']) * s
    pawR = (fx, fy + 2)
    pawL = (44 + p['gx'], 102 + p['gy'])

    v2.draw_gigi(d, P_char, p, style, i, t)

    # mouth chomps open/closed fast while biting
    if chomping and bite > 0.5:
        v2.ell(d, mcx, mcy, 3, 4, P_char['eye'])

    # crumbs fall below the mouth while chomping (3 falls per loop)
    if chomping:
        for k in range(4):
            zt = (3 * t + k * 0.25) % 1.0
            cx_ = mcx - 6 + k * 4 + int(round(2 * math.sin(12 * math.pi * t + k)))
            cy_ = mcy + 4 + int(round(zt * 20))
            fade = v2.mix(P_room['paper1'], P_room['wall'], zt * 0.6)
            d.rectangle([cx_, cy_, cx_ + 1, cy_], fill=fade)

    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    # headphones OFF: parked on the desk, left side
    outfits.draw_headphones_desk(d, P_char, i, 28, 96)
    v2.draw_mug(d, P_char, 92, 97, i, t)
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'], pawL[0], pawL[1], bend=1)
    v2.draw_paw(d, P_char, pawL[0], pawL[1])
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'], pawR[0], pawR[1], bend=-1)
    v2.draw_paw(d, P_char, pawR[0], pawR[1])
    # the fish, held in the right paw
    draw_fish_snack(d, fx + 2, fy - 2, P_room, i)


# ---------------------------------------------------------------- driver
ANIMATORS = {
    'facepalm': a_facepalm,
    'laughing': a_laughing,
    'smug': a_smug,
    'drinking_coffee': a_drinking_coffee,
    'eating_snack': a_eating_snack,
}


def render_all():
    results = {}
    for state, fn in ANIMATORS.items():
        gif = outfits.render_state(state, fn)
        qc = outfits.qc_state(state, gif)
        cs = outfits.contact_sheet(state)
        kb = os.path.getsize(gif) // 1024
        results[state] = dict(gif=gif, kb=kb, qc=qc, contact=cs)
        print(f"{state}: {kb} KB | motion {qc['active']}/{qc['total']} "
              f"min {qc['mind']:.2f} max {qc['maxd']:.2f} | colors {qc['colors']} "
              f"| legib cap={qc['cap']} phone={qc['phone']} | {cs}")
    return results


if __name__ == '__main__':
    render_all()
