#!/usr/bin/env python3
"""Shared outfit/theme system for the 30-state Gigi office GIF set.

Extends office_rig_v2 (imported, never modified). Every state gets:
  - a per-state OUTFIT: cap color, hoodie stripe color, signature theme color,
    headphones on/off, and room mood.
  - room_pal(mood): the office is IDENTICAL in every state (same geometry via
    draw_room); only lighting mood variants exist: day (default), red
    (alert/panic), warm (overheating), night (sleeping).
  - char_pal(state): character palette with outfit applied. draw_gigi reads
    the cap from style and the hoodie stripes from P['cyan'], so outfits are
    driven purely through palette + style — the rig itself is untouched.
  - render_state(state, animator): 60 frames @24fps, NEAREST x4 -> 512x512,
    the exact ffmpeg palette recipe, QC helpers.

Animator signature: fn(img, P_room, P_char, style, i, n)
  - P_room: for ALL room/desk/screen drawing (keeps the office identical).
  - P_char: for draw_gigi / arms / paws / mug (outfit lives here).
  - style: dict(headphones=bool, cap=..., cap_d=...) for draw_gigi.
"""
import math
import os
import subprocess
from PIL import Image, ImageDraw

import office_rig_v2 as v2
from office_rig_v2 import (G, N, WORK, OUTDIR, mix, kf, text, ell, rr,
                           TEAL, TEAL_D, PHONE, BROWN, BROWN_D, pal)
import office_rig_v2_states as st2  # noqa: F401  (night palette + neon)

# ---------------------------------------------------------------- outfit table
# cap/cap_d: flat cap colors. stripe: hoodie stripe color (via P['cyan']).
# theme: signature accent color for this state's effects + headphone LED ring.
# hp: headphones on/off. mood: day | red | warm | night.
OUTFITS = {
    'working':          dict(cap=(240,170,60),  cap_d=(150,105,35),  stripe=(62,200,210),  theme=(70,200,200),   hp=True,  mood='day',   desc='amber cap, cyan stripes — typing shift'),
    'idle':             dict(cap=(80,200,120),  cap_d=(50,130,75),   stripe=(240,220,120), theme=(90,210,140),   hp=True,  mood='day',   desc='green cap, yellow stripes — chilling'),
    'listening':        dict(cap=(150,110,235), cap_d=(95,70,155),   stripe=(62,200,210),  theme=(150,110,235),  hp=True,  mood='day',   desc='purple cap — all ears'),
    'speaking':         dict(cap=(235,120,70),  cap_d=(155,75,40),   stripe=(240,220,120), theme=(235,140,70),   hp=True,  mood='day',   desc='orange cap — on the mic'),
    'thinking':         dict(cap=(150,110,235), cap_d=(95,70,155),   stripe=(62,200,210),  theme=(150,110,235),  hp=True,  mood='day',   desc='purple cap — big thoughts'),
    'success':          dict(cap=(232,190,92),  cap_d=(150,120,55),  stripe=(80,200,120),  theme=(232,190,92),   hp=True,  mood='day',   desc='gold cap, green stripes — nailed it'),
    'alert':            dict(cap=(235,80,80),   cap_d=(155,50,50),   stripe=(240,200,80),  theme=(255,80,80),    hp=True,  mood='red',   desc='red cap — red alert'),
    'tired':            dict(cap=(110,130,180), cap_d=(70,85,120),    stripe=(150,160,190), theme=(110,130,180),  hp=True,  mood='day',   desc='slate-blue cap — running on fumes'),
    'bitching':         dict(cap=(180,60,70),   cap_d=(115,35,45),   stripe=(200,70,80),   theme=(220,80,70),    hp=False, mood='day',   desc='maroon cap — headphones thrown, arms crossed'),
    'pushing_to_github':dict(cap=(80,200,120),  cap_d=(50,130,75),   stripe=(236,236,236), theme=(80,220,120),   hp=True,  mood='day',   desc='green cap, white stripes — shipping it'),
    'deploying':        dict(cap=(240,150,60),  cap_d=(155,95,35),   stripe=(235,100,80),  theme=(240,150,60),   hp=True,  mood='day',   desc='orange cap — big red button energy'),
    'debugging':        dict(cap=(240,210,90),  cap_d=(155,135,55),  stripe=(150,110,235), theme=(240,210,90),   hp=True,  mood='day',   desc='yellow cap, purple stripes — bug hunt'),
    'facepalm':         dict(cap=(150,150,160), cap_d=(95,95,105),   stripe=(235,80,80),   theme=(200,80,80),    hp=True,  mood='day',   desc='grey cap, red stripes — why'),
    'laughing':         dict(cap=(240,130,170), cap_d=(155,80,110),  stripe=(62,200,210),  theme=(240,130,170),  hp=True,  mood='day',   desc='pink cap — losing it'),
    'smug':             dict(cap=(50,50,60),    cap_d=(25,25,30),    stripe=(232,190,92),  theme=(232,190,92),   hp=True,  mood='day',   desc='black cap, gold stripes — told you so'),
    'drinking_coffee':  dict(cap=(150,110,70),  cap_d=(95,70,40),    stripe=(226,200,170), theme=(200,150,90),   hp=False, mood='day',   desc='coffee-brown cap — break time'),
    'eating_snack':     dict(cap=(160,220,90),  cap_d=(105,145,55),  stripe=(240,150,60),  theme=(160,220,90),   hp=False, mood='day',   desc='lime cap — snack attack'),
    'dancing':          dict(cap=(235,90,200),  cap_d=(150,55,130),  stripe=(240,220,90),  theme=(235,90,200),   hp=True,  mood='day',   desc='magenta cap — groove mode'),
    'sleeping':         dict(cap=(60,90,220),   cap_d=(35,55,145),   stripe=(120,150,230), theme=(64,96,220),    hp=False, mood='night', desc='deep-blue cap — night shift over'),
    'surprised':        dict(cap=(230,230,235), cap_d=(150,150,160), stripe=(235,80,80),   theme=(255,255,255),  hp=True,  mood='day',   desc='white cap, red stripes — WHAT'),
    'shrugging':        dict(cap=(140,170,150), cap_d=(90,110,95),   stripe=(170,180,170), theme=(140,180,150),  hp=True,  mood='day',   desc='sage cap — dunno'),
    'scheming':         dict(cap=(110,70,180),  cap_d=(70,40,115),   stripe=(70,180,120),  theme=(150,90,230),   hp=True,  mood='day',   desc='dark-purple cap — plotting'),
    'panic':            dict(cap=(255,70,70),   cap_d=(165,40,40),   stripe=(60,60,70),    theme=(255,70,70),    hp=True,  mood='red',   desc='bright-red cap — everything is fine'),
    'salute':           dict(cap=(50,80,180),   cap_d=(30,50,115),   stripe=(232,190,92),  theme=(90,130,220),    hp=True,  mood='day',   desc='navy cap, gold stripes — yes sir'),
    'celebrating':      dict(cap=(235,80,90),   cap_d=(150,50,55),   stripe=(232,190,92),  theme=(255,200,90),   hp=True,  mood='day',   desc='party-red cap, gold stripes — WOO'),
    'gaming':           dict(cap=(90,255,130),  cap_d=(55,165,80),   stripe=(150,110,235), theme=(90,255,130),   hp=True,  mood='day',   desc='neon-green cap — locked in'),
    'rebooting':        dict(cap=(90,160,255),  cap_d=(55,100,165),  stripe=(62,200,210),  theme=(90,160,255),   hp=True,  mood='day',   desc='electric-blue cap — have you tried'),
    'overheating':      dict(cap=(200,60,60),   cap_d=(130,35,35),   stripe=(240,150,60),  theme=(255,120,60),   hp=False, mood='warm',  desc='dark-red cap — too hot, headphones off'),
    'flexing':          dict(cap=(200,60,70),   cap_d=(130,35,40),   stripe=(30,30,38),    theme=(255,90,90),    hp=True,  mood='day',   desc='red cap, black stripes — check it'),
    'goodbye':          dict(cap=(240,150,80),  cap_d=(155,95,50),   stripe=(62,200,210),  theme=(240,150,80),   hp=True,  mood='day',   desc='sunset cap — see you tomorrow'),
}
assert len(OUTFITS) == 30


# ---------------------------------------------------------------- palettes
def room_pal(mood='day'):
    """The office is identical in every state; only the lighting mood shifts."""
    if mood == 'night':
        return st2.night_pal()
    P = pal()
    if mood == 'red':
        P['wall'] = (20, 12, 14)
        P['wall_line'] = (30, 18, 22)
        P['floor'] = (12, 7, 9)
        P['accent'] = (255, 90, 80)
        P['led_g'] = (255, 120, 90)
        P['led_a'] = (255, 120, 80)
        P['led_c'] = (255, 110, 110)
        P['plate_tx'] = (255, 150, 140)
        P['neon_dim'] = (90, 25, 25)
    elif mood == 'warm':
        P['wall'] = (20, 16, 12)
        P['wall_line'] = (30, 24, 18)
        P['floor'] = (12, 10, 7)
        P['accent'] = (255, 170, 80)
        P['led_g'] = (255, 190, 110)
        P['led_a'] = (255, 160, 80)
        P['led_c'] = (255, 200, 130)
        P['plate_tx'] = (255, 210, 150)
        P['neon_dim'] = (90, 60, 25)
        P['glow'] = (255, 190, 110)
    return P


def char_pal(state):
    """Character palette with this state's outfit applied."""
    o = OUTFITS[state]
    P = pal()
    P['cyan'] = o['stripe']          # hoodie stripes (draw_gigi reads P['cyan'])
    P['accent'] = o['theme']         # headphone LED ring, face screen-glow
    P['mug'] = o['cap']              # her mug matches her cap
    P['fur'] = mix(BROWN, o['theme'], 0.25)
    P['fur_d'] = mix(BROWN_D, o['theme'], 0.25)
    return P


def style_for(state):
    o = OUTFITS[state]
    return dict(headphones=o['hp'], cap=o['cap'], cap_d=o['cap_d'])


# ---------------------------------------------------------------- the one true room
def draw_room(d, P, i, t, mood='day'):
    """Identical office geometry in every state. Animators MUST call this
    (not their own room sequence) so the office stays recognizable."""
    v2.draw_room_base(d, P)
    v2.draw_rack(d, P, i, 2)
    v2.draw_rack(d, P, i, 114)
    v2.draw_clock(d, P, i)
    v2.draw_fan(d, P, i)
    if mood == 'night':
        st2.draw_neon_night(d, P, i)
    else:
        v2.draw_neon(d, P, i)
    v2.draw_poster(d, P, 22, 22, 19, P['paper1'], ["HANG", "IN", "THERE"], 'otter')
    v2.draw_whiteboard(d, P)
    v2.draw_poster(d, P, 69, 22, 22, P['paper2'], ["IT", "WORKS", "ON MY", "MACHINE"])
    v2.draw_window(d, P, i)
    v2.draw_poster(d, P, 92, 56, 20, P['paper3'], ["GIT", "PUSH", "--FORCE"], 'rocket')
    v2.draw_medal(d, P)
    v2.draw_fishtank(d, P, i, t)
    v2.draw_bookshelf(d, P)
    v2.draw_led_strip(d, P, i)
    v2.draw_rug(d, P)


def draw_headphones_desk(d, P, i, x, y):
    """Headphones set down on the desk (for headphones-OFF day states)."""
    cup = P['phone']
    cup_d = P['phone_d']
    d.arc([x - 8, y - 10, x + 8, y + 4], start=180, end=360, fill=cup, width=4)
    rr(d, x - 10, y - 4, x - 4, y + 6, cup, r=2)
    rr(d, x + 4, y - 4, x + 10, y + 6, cup, r=2)
    rr(d, x - 8, y - 1, x - 6, y + 4, cup_d, r=1)
    rr(d, x + 6, y - 1, x + 8, y + 4, cup_d, r=1)
    if (i // 12) % 2 == 0:  # idle charge blink
        d.rectangle([x - 11, y - 5, x - 3, y + 7], outline=P['accent'])


# ---------------------------------------------------------------- render + QC
def render_state(state, animator, workdir=None):
    """Render one state: 60 frames @24fps, NEAREST x4, exact ffmpeg recipe."""
    o = OUTFITS[state]
    P_room = room_pal(o['mood'])
    P_char = char_pal(state)
    style = style_for(state)
    fdir = os.path.join(WORK, workdir or state)
    os.makedirs(fdir, exist_ok=True)
    for i in range(N):
        img = Image.new('RGB', (G, G), (0, 0, 0))
        animator(img, P_room, P_char, style, i, N)
        img = img.resize((G * 4, G * 4), Image.NEAREST)
        img.save(os.path.join(fdir, f'f{i:02d}.png'))
    mp4 = os.path.join(WORK, f'{workdir or state}.mp4')
    gif = os.path.join(OUTDIR, f'gigi_office_{state}.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24',
                    '-i', os.path.join(fdir, 'f%02d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', mp4], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf',
                    'fps=24,scale=512:-1:flags=lanczos,'
                    'split[s0][s1];[s0]palettegen=max_colors=64[p];'
                    '[s1][p]paletteuse=dither=bayer', gif], check=True)
    return gif


def qc_state(state, gif):
    """Motion audit + color count + outfit-aware 18x12 legibility."""
    diffs, active = v2.motion_audit(gif)
    colors = v2.color_count(gif)
    im = Image.open(gif)
    im.seek(im.n_frames // 2)
    tiny = im.convert('RGB').resize((18, 12), Image.NEAREST)
    px = list(tiny.getdata())
    cap = OUTFITS[state]['cap']

    def close(a, b, tol=70):
        return all(abs(a[i] - b[i]) < tol for i in range(3))

    cap_n = sum(1 for p in px if close(p, cap))
    phone_n = sum(1 for p in px if close(p, PHONE))
    tiny_big = tiny.resize((180, 120), Image.NEAREST)
    tiny_big.save(os.path.join(WORK, f'legib_{state}.png'))
    return dict(state=state, active=active, total=len(diffs),
                mind=min(diffs), maxd=max(diffs),
                colors=colors, cap=cap_n, phone=phone_n)


def contact_sheet(state, workdir=None, cols=10):
    fdir = os.path.join(WORK, workdir or state)
    files = sorted(os.listdir(fdir))[:N]
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * G, rows * G), (20, 20, 20))
    for k, fn in enumerate(files):
        fr = Image.open(os.path.join(fdir, fn)).resize((G, G), Image.NEAREST)
        sheet.paste(fr, ((k % cols) * G, (k // cols) * G))
    p = os.path.join(WORK, f'contact_{state}.png')
    sheet.save(p)
    return p
