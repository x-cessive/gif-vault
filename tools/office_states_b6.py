#!/usr/bin/env python3
"""GIGI office batch 6: 2 NEW states (flexing, goodbye) + re-renders of
working / sleeping / thinking with their new per-state outfits.

Extends office_rig_v2, office_outfits, office_rig_v2_states (all imported,
NEVER modified). 128px grid, NEAREST x4 -> 512x512, solid colors only,
no AA, no gradients, no watermark. 60 unique frames @24fps, seamless loops.

  PART A (new animators, animator signature fn(img, P_room, P_char, style, i, n)):
    flexing — double bicep pump per loop: right paw curls to the shoulder
      twice (kf), chest puffs (gy-3 on pump), grin overdrawn after draw_gigi,
      sparkle arc + motion-arc flash on each pump. Signature: pump sparkle.
    goodbye — right-paw wave (side-to-side, first 40% of loop), then she
      stands and walks right +34px with a 2px bob, then fades out/in for a
      seamless loop (Image.blend toward black at the seam — the envelope is
      periodic, so all cycles are integer). Signature: wave + fade.
  PART B (re-renders, existing animators, new outfit palettes):
    working  — room_pal('day'), style_for('working') via v2.a_working_v2
    sleeping — st2.night_pal() + outfit overrides, style_for('sleeping')
      via st2.a_sleeping_v2
    thinking — v2.pal() + outfit overrides, style_for('thinking')
      via st2.a_thinking_v2
"""
import math
import os
import subprocess
from PIL import Image, ImageDraw

import office_rig_v2 as v2
from office_rig_v2 import G, N, WORK, OUTDIR, mix, kf
import office_outfits as outfits
import office_rig_v2_states as st2


def _ss(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def _grin(d, P_char, p):
    """Overdraw a wider grin after draw_gigi (covers the stock mouth)."""
    hx = p['hx'] + p['gx']
    hy = p['hy'] + p['gy']
    lx, ly = p['lookx'], p['looky']
    d.line([hx - 6 + lx, hy + 8 + ly, hx + 6 + lx, hy + 8 + ly],
           fill=P_char['eye'], width=2)
    d.line([hx - 6 + lx, hy + 8 + ly, hx - 8 + lx, hy + 6 + ly],
           fill=P_char['eye'], width=2)
    d.line([hx + 6 + lx, hy + 8 + ly, hx + 8 + lx, hy + 6 + ly],
           fill=P_char['eye'], width=2)


# ---------------------------------------------------------------- PART A: new animators
def a_flexing(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    # double bicep pump: 2 full cycles per loop (integer -> seamless)
    pump = kf(t, [(0, 0), (0.10, 0), (0.20, 1), (0.30, 0),
                  (0.36, 0), (0.46, 1), (0.56, 0), (1, 0)])
    se = pump * pump * (3 - 2 * pump)
    br = math.sin(2 * math.pi * t)

    sw = int(round(1.5 * br))
    v2.draw_chair(d, P_char, sw)
    p = v2.default_pose()
    p['gx'] = sw
    p['gy'] = int(round(1.5 * br)) - int(round(3 * se))   # chest puff on pump
    p['hx'] = 64 + int(round(2 * se))
    p['hy'] = 60 + p['gy'] - int(round(1 * se))
    p['tilt'] = int(round(2 * se))
    p['brow'] = 1 if se > 0.5 else 0
    bi = i % 24
    p['blink'] = 1 if bi in (20, 21) else 0
    p['earL'] = 2 if 30 <= i < 33 else 0
    p['tail'] = int(round(2 * br))

    v2.draw_gigi(d, P_char, p, style, i, t)
    _grin(d, P_char, p)

    # ---- desk ----
    v2.draw_desk_base(d, P_room)
    v2.draw_keyboard(d, P_room, p)
    v2.draw_lamp(d, P_room, i)
    # left paw planted on the keyboard
    v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'],
           44 + p['gx'], 100 + p['gy'], bend=1)
    v2.draw_paw(d, P_char, 44 + p['gx'], 100 + p['gy'])
    # right paw curls up to the shoulder on the pump
    pawR = (84 + (74 - 84) * se, 100 + (76 - 100) * se)
    v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'],
           pawR[0] + p['gx'], pawR[1] + p['gy'], bend=-1)
    v2.draw_paw(d, P_char, pawR[0] + p['gx'], pawR[1] + p['gy'])
    v2.draw_main_monitor(d, P_room, i)
    v2.draw_term_monitor(d, P_room, i, t)
    v2.draw_mug(d, P_char, 92, 97, i, t)

    # ---- pump sparkle: sparkle arc + motion-arc flash on each pump ----
    if se > 0.45:
        bx, by = 76 + p['gx'], 82 + p['gy']                # bicep mid
        for k, (ox, oy) in enumerate(((-7, -5), (-4, -8), (0, -9),
                                      (4, -8), (7, -5))):
            col = P_char['white'] if (i // 2 + k) % 2 == 0 else P_char['accent']
            d.rectangle([bx + ox, by + oy, bx + ox + 1, by + oy + 1], fill=col)
        for k in range(3):                                 # curl motion streaks
            d.rectangle([bx - 9 + k * 2, by - 11 - k,
                         bx - 8 + k * 2, by - 11 - k], fill=P_char['accent'])

    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)


def a_goodbye(img, P_room, P_char, style, i, n):
    t = i / n
    d = ImageDraw.Draw(img)
    outfits.draw_room(d, P_room, i, t, 'day')

    wave = t < 0.40
    br = math.sin(2 * math.pi * t)
    # walk: rise 0.40->0.70, hold to the end (return hidden under the fade)
    walk = _ss((t - 0.40) / 0.30) if t >= 0.40 else 0.0
    stand = _ss((t - 0.40) / 0.15) if t >= 0.40 else 0.0
    bob = (int(round(2 * math.sin(2 * math.pi * (t - 0.40) / 0.30 * 2)))
           if 0.40 <= t < 0.70 else 0)

    v2.draw_chair(d, P_char, 0)
    p = v2.default_pose()
    p['gx'] = int(round(34 * walk))
    if walk > 0:
        p['gy'] = -int(round(12 * stand)) + bob              # stands + walks
    else:
        p['gy'] = int(round(1.5 * br))                       # seated breathing
    p['hx'] = 64
    p['hy'] = 60
    p['tilt'] = int(round(1 * br)) if not walk else 0
    bi = i % 28
    p['blink'] = 1 if bi in (12, 13) else 0
    p['tail'] = int(round(2 * br))

    if wave:
        # --- seated at the desk, right paw waving side-to-side ---
        v2.draw_gigi(d, P_char, p, style, i, t)
        _grin(d, P_char, p)
        v2.draw_desk_base(d, P_room)
        v2.draw_keyboard(d, P_room, p)
        v2.draw_lamp(d, P_room, i)
        v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'],
               44 + p['gx'], 100 + p['gy'], bend=1)         # left paw rests
        v2.draw_paw(d, P_char, 44 + p['gx'], 100 + p['gy'])
        wx = int(round(7 * math.sin(2 * math.pi * t / 0.40 * 3)))   # 3 waves
        wy = int(round(2 * math.sin(2 * math.pi * t / 0.40 * 6)))   # 6 mini-bobs
        pawR = (88 + wx, 62 + wy)
        v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'],
               pawR[0] + p['gx'], pawR[1] + p['gy'], bend=-1)
        v2.draw_paw(d, P_char, pawR[0] + p['gx'], pawR[1] + p['gy'])
        v2.draw_main_monitor(d, P_room, i)
        v2.draw_term_monitor(d, P_room, i, t)
        v2.draw_mug(d, P_char, 92, 97, i, t)
    else:
        # --- walks right in front of the desk ---
        v2.draw_desk_base(d, P_room)
        v2.draw_keyboard(d, P_room, p)
        v2.draw_lamp(d, P_room, i)
        v2.draw_main_monitor(d, P_room, i)
        v2.draw_term_monitor(d, P_room, i, t)
        v2.draw_mug(d, P_char, 92, 97, i, t)
        v2.draw_gigi(d, P_char, p, style, i, t)
        swing = (int(round(4 * math.sin(2 * math.pi * (t - 0.40) / 0.30 * 2)))
                 if t < 0.70 else 0)
        v2.arm(d, P_char, 50 + p['gx'], 88 + p['gy'],
               48 + p['gx'] + swing, 100 + p['gy'], bend=1)
        v2.draw_paw(d, P_char, 48 + p['gx'] + swing, 100 + p['gy'])
        v2.arm(d, P_char, 78 + p['gx'], 88 + p['gy'],
               80 + p['gx'] - swing, 100 + p['gy'], bend=-1)
        v2.draw_paw(d, P_char, 80 + p['gx'] - swing, 100 + p['gy'])

    v2.draw_side_table(d, P_room, i, t)
    v2.draw_cables(d, P_room, i)

    # --- fade out/in at the loop seam (periodic envelope -> seamless) ---
    g = min(t, 1 - t)
    f = math.cos(g / 0.15 * math.pi / 2) ** 2 if g < 0.15 else 0.0
    if f > 0.0:
        img.paste(Image.blend(img, Image.new('RGB', (G, G), (0, 0, 0)), f))


# ---------------------------------------------------------------- PART B palettes
def working_pal():
    return outfits.room_pal('day')


def sleeping_pal():
    P = st2.night_pal()
    P['cyan'] = (120, 150, 230)
    P['accent'] = (64, 96, 220)
    P['mug'] = (60, 90, 220)
    return P


def thinking_pal():
    P = v2.pal()
    P['accent'] = (150, 110, 235)
    P['code'] = (150, 135, 235)
    P['code_d'] = (95, 75, 175)
    P['cyan'] = (62, 200, 210)
    P['mug'] = (150, 110, 235)
    return P


def render_custom(state, pal_fn, animator, workdir, gif_name):
    """render_state-like flow with a custom palette (same ffmpeg recipe)."""
    P = pal_fn()
    style = outfits.style_for(state)
    fdir = os.path.join(WORK, workdir)
    os.makedirs(fdir, exist_ok=True)
    for i in range(N):
        img = Image.new('RGB', (G, G), (0, 0, 0))
        animator(img, P, i, N, style)
        img = img.resize((G * 4, G * 4), Image.NEAREST)
        img.save(os.path.join(fdir, f'f{i:02d}.png'))
    mp4 = os.path.join(WORK, f'{workdir}.mp4')
    gif = os.path.join(OUTDIR, gif_name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24',
                    '-i', os.path.join(fdir, 'f%02d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', mp4], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf',
                    'fps=24,scale=512:-1:flags=lanczos,'
                    'split[s0][s1];[s0]palettegen=max_colors=64[p];'
                    '[s1][p]paletteuse=dither=bayer', gif], check=True)
    return gif


def _report(state, gif, workdir=None):
    q = outfits.qc_state(state, gif)
    cs = outfits.contact_sheet(state, workdir=workdir)
    print(f"{state}: {os.path.basename(gif)} "
          f"{os.path.getsize(gif)//1024}KB | "
          f"motion {q['active']}/{q['total']} min {q['mind']:.2f} "
          f"max {q['maxd']:.2f} | colors {q['colors']} | "
          f"cap {q['cap']} phone {q['phone']}")
    print(f"  contact: {cs}")
    return q


if __name__ == '__main__':
    # PART A — new states via outfits.render_state
    for state, anim in (('flexing', a_flexing), ('goodbye', a_goodbye)):
        gif = outfits.render_state(state, anim)
        _report(state, gif)

    # PART B — re-renders with outfit palettes (existing animators)
    customs = [
        ('working', working_pal, v2.a_working_v2, 'working_b6',
         'gigi_office_working.gif'),
        ('sleeping', sleeping_pal, st2.a_sleeping_v2, 'sleeping_b6',
         'gigi_office_sleeping.gif'),
        ('thinking', thinking_pal, st2.a_thinking_v2, 'thinking_b6',
         'gigi_office_thinking.gif'),
    ]
    for state, pal_fn, anim, workdir, gif_name in customs:
        gif = render_custom(state, pal_fn, anim, workdir, gif_name)
        _report(state, gif, workdir=workdir)
