#!/usr/bin/env python3
"""Shared booth/theme system for the 20-state Now Spinning 99.9 FM GIF set.

Same production standard as the Gigi office v2 set:
128x128 grid, NEAREST x4 -> 512x512, blocky 8-bit (solid colors, no AA,
no gradients), 60 unique frames @24fps, seamless infinite loop, exact
ffmpeg palette recipe (max_colors=64, dither=bayer).

One constant booth: mixing console with bouncing VU meters, two turntables,
broadcast mic on a boom, big ON AIR sign, neon 99.9 FM plate, window.
Lighting: 'day' (Calder, warm sunlit), 'night' (Mina, neon + moonlit),
'ident' (dark stage for the close-up ident loops).

Two DJ characters, blocky pixel style, headphones = the DJ signature:
  Calder — day DJ. Warm skin, backwards orange cap, amber headphones.
  Mina   — night DJ. Long dark-purple hair, purple headphones w/ LED ring.

Animator signature: fn(img, P_room, P_dj, style, i, n)
  - P_room: booth drawing (the booth stays pixel-identical).
  - P_dj:   draw_dj / arms / paws (None for ident states).
  - style:  dict(dj='calder'|'mina'|None, lighting='day'|'night'|'ident').
"""
import math
import os
import subprocess
from PIL import Image, ImageDraw

import office_rig_v2 as v2
from office_rig_v2 import (G, N, mix, kf, text, text_c, ell, rr,
                           motion_audit, color_count)

WORK = os.path.expanduser("~/workspace/gif-station/fm99")
OUTDIR = os.path.expanduser("~/workspace/your_files/fm999")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

# ---------------------------------------------------------------- themes
# sig: signature colors that must read at 18x12 (legibility gate).
THEMES = {
    'on_air':            dict(lighting='ident', dj=None,     accent=(255, 90, 80),
                              sig=[(255, 90, 80)], desc='ON AIR sign close-up, blinking'),
    'now_spinning':      dict(lighting='ident', dj=None,     accent=(255, 200, 90),
                              sig=[(255, 200, 90)], desc='spinning vinyl close-up + ticker'),
    'station_ident':     dict(lighting='ident', dj=None,     accent=(90, 220, 255),
                              sig=[(90, 220, 255)], desc='neon 99.9 FM logo + EQ bars'),
    'signing_off':       dict(lighting='ident', dj=None,     accent=(150, 110, 235),
                              sig=[(255, 90, 80)], desc='sign dimming, goodnight'),
    'calder_hosting':    dict(lighting='day', dj='calder',   accent=(255, 190, 80),
                              sig=[(240, 170, 60), (240, 150, 60)], desc='warm welcome wave'),
    'calder_taking_requests': dict(lighting='day', dj='calder', accent=(255, 190, 80),
                              sig=[(240, 170, 60), (255, 90, 80)], desc='request line ringing'),
    'calder_vibing':     dict(lighting='day', dj='calder',   accent=(255, 190, 80),
                              sig=[(240, 170, 60), (240, 150, 60)], desc='eyes-closed groove, snaps'),
    'calder_talking':    dict(lighting='day', dj='calder',   accent=(255, 190, 80),
                              sig=[(240, 170, 60), (90, 220, 255)], desc='on-mic chatter'),
    'calder_laughing':   dict(lighting='day', dj='calder',   accent=(255, 190, 80),
                              sig=[(240, 170, 60), (240, 240, 240)], desc='laugh bursts'),
    'calder_mic_check':  dict(lighting='day', dj='calder',   accent=(255, 190, 80),
                              sig=[(240, 170, 60), (80, 255, 140)], desc='mic taps, VU spikes'),
    'calder_back_after_break': dict(lighting='day', dj='calder', accent=(255, 190, 80),
                              sig=[(240, 170, 60), (80, 255, 140)], desc="we're back energy"),
    'calder_technical_difficulties': dict(lighting='day', dj='calder', accent=(255, 90, 80),
                              sig=[(240, 170, 60), (255, 90, 80)], desc='holds the card, shrugs'),
    'mina_hosting':      dict(lighting='night', dj='mina',   accent=(150, 110, 255),
                              sig=[(150, 100, 230), (150, 110, 255)], desc='smooth night welcome'),
    'mina_night_signal': dict(lighting='night', dj='mina',   accent=(150, 110, 255),
                              sig=[(150, 100, 230), (90, 220, 255)], desc='paranormal candle + ?'),
    'mina_vibing':       dict(lighting='night', dj='mina',   accent=(150, 110, 255),
                              sig=[(150, 100, 230), (150, 110, 255)], desc='slow night groove'),
    'mina_talking':      dict(lighting='night', dj='mina',   accent=(150, 110, 255),
                              sig=[(150, 100, 230), (90, 220, 255)], desc='night chatter'),
    'mina_laughing':     dict(lighting='night', dj='mina',   accent=(150, 110, 255),
                              sig=[(150, 100, 230), (240, 240, 240)], desc='night laugh bursts'),
    'mina_taking_requests': dict(lighting='night', dj='mina', accent=(150, 110, 255),
                              sig=[(150, 100, 230), (255, 90, 80)], desc='night request line'),
    'mina_back_after_break': dict(lighting='night', dj='mina', accent=(150, 110, 255),
                              sig=[(150, 100, 230), (80, 255, 140)], desc="we're back, night"),
    'mina_technical_difficulties': dict(lighting='night', dj='mina', accent=(255, 90, 80),
                              sig=[(150, 100, 230), (255, 90, 80)], desc='night card + static'),
}
assert len(THEMES) == 20


# ---------------------------------------------------------------- palettes
def booth_pal(lighting='day'):
    P = dict(
        floor=(10, 11, 16),
        foam=(30, 34, 46), foam_d=(20, 23, 33),
        console=(36, 40, 54), console_d=(22, 25, 36), console_e=(54, 60, 80),
        fader=(140, 150, 170), knob=(205, 210, 225), knob_d=(120, 128, 148),
        vu_bg=(8, 10, 16), vu_g=(80, 255, 140), vu_a=(255, 190, 80),
        vu_r=(255, 90, 80),
        sign_bg=(18, 8, 10), sign_off=(96, 42, 42), sign_on=(255, 90, 80),
        plate_bg=(8, 10, 18), plate_tx=(120, 225, 255), neon_dim=(30, 80, 100),
        vinyl=(18, 18, 24), vinyl_d=(8, 8, 12), label=(240, 170, 60),
        mic=(40, 44, 56), mic_d=(24, 26, 36), pop=(16, 18, 26),
        cable=(12, 12, 18),
        led_g=(80, 255, 140), led_a=(255, 190, 80), led_r=(255, 90, 80),
        led_c=(90, 220, 255),
        white=(236, 236, 236), ink=(16, 18, 26),
    )
    if lighting == 'day':
        P.update(wall=(64, 58, 52), wall_line=(82, 74, 66),
                 sky=(135, 200, 240), sun=(255, 220, 120), cloud=(240, 244, 250),
                 glow=(255, 210, 140))
    elif lighting == 'night':
        P.update(wall=(16, 16, 28), wall_line=(28, 28, 48),
                 sky=(8, 10, 26), moon=(230, 230, 245), star=(205, 205, 235),
                 glow=(150, 110, 255))
    else:  # ident: dark neutral stage
        P.update(wall=(12, 13, 20), wall_line=(24, 26, 38), glow=(255, 150, 120),
                 sky=(10, 12, 24), moon=(230, 230, 245), star=(205, 205, 235))
    return P


def dj_pal(dj):
    if dj == 'calder':
        return dict(skin=(238, 186, 142), skin_d=(190, 140, 105),
                    hair=(240, 150, 60), hair_d=(170, 100, 40),
                    shirt=(240, 200, 100), shirt_d=(180, 150, 70),
                    phone=(240, 170, 60), phone_d=(150, 100, 35),
                    accent=(255, 190, 80), eye=(20, 16, 14),
                    white=(240, 240, 240), brow=(120, 75, 40))
    return dict(skin=(232, 196, 170), skin_d=(185, 150, 130),
                hair=(52, 40, 80), hair_d=(30, 22, 50),
                shirt=(56, 48, 96), shirt_d=(34, 30, 62),
                phone=(150, 100, 230), phone_d=(90, 60, 150),
                accent=(150, 110, 255), neon=(90, 220, 255),
                eye=(16, 14, 20), white=(240, 240, 240), brow=(40, 30, 60))


def style_for(state):
    th = THEMES[state]
    return dict(dj=th['dj'], lighting=th['lighting'])


# ---------------------------------------------------------------- booth pieces
def draw_onair_sign(d, P, x0, y0, x1, y1, i, on=True, scale=1):
    """ON AIR sign; caller controls blink via `on`.

    When off, the sign body breathes between two dark reds every 3 frames
    so the loop never sits fully static."""
    bg = P['sign_bg'] if (on or (i // 3) % 2 == 0) else (30, 12, 14)
    rr(d, x0, y0, x1, y1, bg, r=2)
    col = P['sign_on'] if on else P['sign_off']
    if on:  # glow frame (solid, no gradient)
        d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=P['sign_on'])
    text_c(d, 'ON AIR', (x0 + x1) // 2, (y0 + y1) // 2 - 3 * scale, scale,
           col)


def draw_neon_plate(d, P, x0, y0, x1, y1, i, lines, scale=1):
    rr(d, x0, y0, x1, y1, P['plate_bg'], r=2)
    flick = (i // 3) % 2 == 0  # fast neon shimmer, seamless
    col = P['neon_dim'] if flick else P['plate_tx']
    if not flick:
        d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=P['plate_tx'])
    cy = (y0 + y1) // 2 - (len(lines) * 6 * scale) // 2
    for ln in lines:
        text_c(d, ln, (x0 + x1) // 2, cy, scale, col)
        cy += 6 * scale


def draw_window(d, P, x0, y0, x1, y1, i, lighting):
    rr(d, x0, y0, x1, y1, P['console_d'], r=1)
    gx0, gy0, gx1, gy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 2
    d.rectangle([gx0, gy0, gx1, gy1], fill=P['sky'])
    d.line([x0, (y0 + y1) // 2, x1, (y0 + y1) // 2], fill=P['console_d'], width=1)
    d.line([(x0 + x1) // 2, y0, (x0 + x1) // 2, y1], fill=P['console_d'], width=1)
    if lighting == 'day':
        ell(d, gx1 - 6, gy0 + 7, 5, 5, P['sun'])
        span = (gx1 - gx0) + 14
        cx = gx0 - 7 + ((i * span) // 60)  # seamless drift
        for ox in (0, -span):
            x = cx + ox
            if gx0 - 12 < x < gx1:
                rr(d, x, gy0 + 16, x + 12, gy0 + 21, P['cloud'], r=2)
                rr(d, x + 3, gy0 + 13, x + 9, gy0 + 17, P['cloud'], r=2)
    elif lighting == 'night':
        ell(d, gx1 - 7, gy0 + 7, 4, 4, P['moon'])
        d.rectangle([gx1 - 8, gy0 + 6, gx1 - 6, gy0 + 8], fill=P['sky'])
        for k, (sx, sy) in enumerate([(0, 4), (8, 12), (14, 2), (4, 18), (18, 16)]):
            if math.sin(4 * math.pi * i / 60 + k * 1.7) > -0.2:  # twinkle
                d.rectangle([gx0 + sx, gy0 + sy, gx0 + sx, gy0 + sy],
                            fill=P['star'])


def draw_vinyl(d, P, cx, cy, r, i, spin=3):
    """Spinning record. spin = rotations per loop."""
    ell(d, cx, cy, r, r, P['vinyl'])
    ell(d, cx, cy, r - 3, r - 3, P['vinyl'])  # edge ring
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2],
              outline=P['vinyl_d'])
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
              outline=P['vinyl_d'])
    a = 2 * math.pi * spin * i / 60
    mx = int(round(cx + (r - 2) * math.cos(a)))
    my = int(round(cy + (r - 2) * math.sin(a)))
    d.rectangle([mx - 2, my - 2, mx + 2, my + 2], fill=P['white'])
    ell(d, cx, cy, 4, 4, P['label'])
    d.rectangle([cx, cy, cx, cy], fill=P['ink'])


def draw_turntable(d, P, cx, i, t):
    y0 = 62
    rr(d, cx - 14, y0, cx + 14, y0 + 28, P['console_d'], r=2)
    draw_vinyl(d, P, cx, y0 + 14, 11, i, spin=3)
    rr(d, cx + 9, y0 + 2, cx + 14, y0 + 7, P['mic'], r=1)  # tonearm base
    sway = int(round(2 * math.sin(2 * math.pi * t)))
    d.line([cx + 11, y0 + 4, cx + 3, y0 + 12 + sway], fill=P['mic'], width=2)
    d.rectangle([cx + 1, y0 + 11 + sway, cx + 5, y0 + 13 + sway], fill=P['knob'])


def draw_vu(d, P, x0, i, t, phase=0.0, boost=0):
    """Dual bouncing VU bar meter."""
    rr(d, x0, 94, x0 + 22, 108, P['vu_bg'], r=1)
    for j in range(5):
        h = 2 + int(round(10 * abs(math.sin(6 * math.pi * i / 60 + phase + j * 0.7))))
        h = min(12, h + boost)
        x = x0 + 2 + j * 4
        col = P['vu_g'] if h < 6 else (P['vu_a'] if h < 10 else P['vu_r'])
        d.rectangle([x, 106 - h, x + 2, 106], fill=col)


def draw_faders(d, P, i, t):
    for j in range(4):
        x = 12 + j * 7
        d.line([x, 96, x, 118], fill=P['console_d'], width=2)
        ky = 107 + int(round(4 * math.sin(2 * math.pi * i / 60 + j * 1.3)))
        if j == 0:  # the DJ rides fader 0: quick 2-frame jitter
            ky += 2 if (i // 2) % 2 == 0 else -2
        d.rectangle([x - 2, ky, x + 2, ky + 3], fill=P['fader'])


def draw_led_strip(d, P, i):
    for k in range(10):  # fast chase: two lit LEDs stepping every 2 frames
        x = 40 + k * 7
        on = ((i // 2) + k) % 10 < 2
        d.rectangle([x, 112, x + 2, 114], fill=P['led_c'] if on else P['console_d'])


def draw_phone(d, P, i, ring=False):
    """Request-line phone on the console's right end."""
    rr(d, 94, 106, 118, 118, P['console_d'], r=1)
    rr(d, 96, 100, 116, 106, P['mic'], r=2)  # handset
    d.rectangle([99, 101, 113, 102], fill=P['mic_d'])
    if ring and (i // 4) % 2 == 0:
        d.rectangle([114, 101, 116, 103], fill=P['led_r'])
        for k in range(2):  # ring waves
            u = ((i * 2 + k * 30) % 60) / 60.0
            rr(d, 118 + int(round(u * 6)), 100 - int(round(u * 3)),
               122 + int(round(u * 6)), 106, P['led_r'], r=1)


def draw_mic_boom(d, P, i, live=True, tap=0):
    """Boom arm from upper right, capsule + pop filter beside the DJ's mouth."""
    rr(d, 98, 20, 106, 28, P['console_d'], r=1)
    d.line([102, 24, 90, 42], fill=P['mic'], width=3)
    d.line([90, 42, 82, 60], fill=P['mic'], width=3)
    ell(d, 90, 42, 2, 2, P['knob'])
    rr(d, 76, 58, 88, 66, P['mic_d'], r=2)  # capsule
    for gx in (80, 84):
        d.line([gx, 59, gx, 65], fill=P['mic'], width=1)
    d.ellipse([68, 56, 84, 72], outline=P['pop'])  # pop filter
    if live and (i // 8) % 2 == 0:
        d.rectangle([84, 59, 86, 61], fill=P['led_r'])
    if tap:  # mic-tap impact star
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            d.line([82 + dx * 5, 62 + dy * 5, 82 + dx * 9, 62 + dy * 9],
                   fill=P['white'], width=1)


def wall_fill(P, i, step=4):
    """Wall color with a subtle 3-phase electrical shimmer (room tone).

    Every consecutive frame pair differs, so the loop never sits static."""
    s = (i % 3) * step  # diffs of +s/+s/-2s between frames
    w = P['wall']
    return (min(255, w[0] + s), min(255, w[1] + s), min(255, w[2] + s))


def draw_booth(d, P, i, t, lighting, onair=True, live=True, ring=False,
               vu_boost=0):
    """The one true booth. Animators MUST call this so the room stays identical."""
    d.rectangle([0, 0, 128, 94], fill=wall_fill(P, i))
    d.rectangle([0, 94, 128, 128], fill=P['floor'])
    d.line([0, 94, 128, 94], fill=P['wall_line'], width=1)
    for x0, y0 in ((4, 30), (100, 30)):
        for dy in (0, 24):
            rr(d, x0, y0 + dy, x0 + 20, y0 + dy + 20, P['foam'], r=1)
            rr(d, x0 + 3, y0 + dy + 3, x0 + 17, y0 + dy + 17, P['foam_d'], r=1)
    draw_window(d, P, 92, 26, 124, 58, i, lighting)
    draw_neon_plate(d, P, 6, 6, 42, 22, i, ['99.9', 'FM'])
    draw_onair_sign(d, P, 46, 4, 86, 18, i,
                    on=onair if onair != 'blink' else (i // 15) % 2 == 0)
    draw_turntable(d, P, 22, i, t)
    draw_turntable(d, P, 106, i, t)
    # console
    rr(d, 6, 92, 122, 122, P['console'], r=2)
    d.line([6, 92, 122, 92], fill=P['console_e'], width=1)
    draw_vu(d, P, 40, i, t, phase=0.0, boost=vu_boost)
    draw_vu(d, P, 66, i, t, phase=1.1, boost=vu_boost)
    draw_faders(d, P, i, t)
    draw_led_strip(d, P, i)
    draw_phone(d, P, i, ring=ring)
    d.line([10, 120, 40, 120], fill=P['cable'], width=1)  # cable
    d.line([88, 120, 118, 120], fill=P['cable'], width=1)


# ---------------------------------------------------------------- the DJs
def default_pose():
    return dict(gx=0, gy=0, hx=64, hy=56, lookx=0, looky=0, tilt=0,
                blink=0, brow=0, mouth='-', pawL=None, pawR=None)


def _arm(d, P, sx, sy, px, py):
    ex, ey = (sx + px) // 2, (sy + py) // 2 + 4
    d.line([sx, sy, ex, ey], fill=P['shirt'], width=4)
    d.line([ex, ey, px, py], fill=P['skin'], width=3)
    rr(d, px - 3, py - 3, px + 3, py + 2, P['skin'], r=2)


def draw_dj(d, P, p, style, i, t):
    """Blocky DJ. p = pose dict. style['dj'] = 'calder' | 'mina'."""
    dj = style['dj']
    hx, hy = p['hx'] + p['gx'], p['hy'] + p['gy']
    if dj == 'mina':  # long hair behind everything
        rr(d, hx - 14, hy - 13, hx + 14, hy + 18, P['hair_d'], r=4)
        d.rectangle([hx - 14, hy + 2, hx - 9, hy + 28], fill=P['hair_d'])
        d.rectangle([hx + 9, hy + 2, hx + 14, hy + 28], fill=P['hair_d'])
    # body
    rr(d, hx - 19, 76 + p['gy'], hx + 19, 96 + p['gy'],
       P['shirt'], r=3)
    d.rectangle([hx - 5, 76 + p['gy'], hx + 5, 81 + p['gy']], fill=P['shirt_d'])
    if dj == 'mina':  # crescent pin
        d.rectangle([hx + 10, 84 + p['gy'], hx + 12, 88 + p['gy']],
                    fill=P['accent'])
    # head
    ell(d, hx, hy, 11, 10, P['skin'])
    if dj == 'calder':  # backwards cap
        rr(d, hx - 11, hy - 14, hx + 11, hy - 7, P['hair'], r=2)
        d.rectangle([hx + 9, hy - 12, hx + 17, hy - 9], fill=P['hair_d'])
        d.rectangle([hx - 1, hy - 15, hx + 1, hy - 13], fill=P['hair_d'])
    else:  # mina fringe
        rr(d, hx - 11, hy - 13, hx + 11, hy - 8, P['hair'], r=2)
    # headphones (the DJ signature)
    d.arc([hx - 13, hy - 17, hx + 13, hy + 1], start=180, end=360,
          fill=P['phone'], width=3)
    rr(d, hx - 16, hy - 5, hx - 10, hy + 6, P['phone'], r=2)
    rr(d, hx + 10, hy - 5, hx + 16, hy + 6, P['phone'], r=2)
    d.rectangle([hx - 14, hy - 2, hx - 12, hy + 3], fill=P['phone_d'])
    d.rectangle([hx + 12, hy - 2, hx + 14, hy + 3], fill=P['phone_d'])
    if (i // 6) % 2 == 0:  # cup LED pulse
        if dj == 'mina':
            d.rectangle([hx + 9, hy - 6, hx + 17, hy + 7], outline=P['neon'])
        else:
            d.rectangle([hx + 12, hy - 2, hx + 14, hy], fill=P['accent'])
    # face
    tilt = p['tilt']
    for sgn in (-1, 1):
        ex = hx + sgn * 4 + p['lookx']
        ey = hy + 1 + p['looky'] + tilt * sgn
        if p['blink']:
            d.line([ex - 1, ey, ex + 1, ey], fill=P['eye'], width=1)
        else:
            d.rectangle([ex - 1, ey - 2, ex + 1, ey + 1], fill=P['eye'])
        if p['brow']:
            d.rectangle([ex - 2, ey - 5, ex + 2, ey - 4], fill=P['brow'])
    d.rectangle([hx + p['lookx'], hy + 5, hx + p['lookx'], hy + 5],
                fill=P['skin_d'])
    my = hy + 9 + p['looky']
    mx = hx + p['lookx']
    if p['mouth'] == 'open':
        ell(d, mx, my, 3, 2, P['eye'])
    elif p['mouth'] == 'o':
        ell(d, mx, my, 2, 2, P['eye'])
    elif p['mouth'] == 'smile':
        d.line([mx - 4, my, mx + 4, my], fill=P['eye'], width=1)
        d.line([mx - 4, my - 1, mx - 4, my], fill=P['eye'], width=1)
        d.line([mx + 4, my - 1, mx + 4, my], fill=P['eye'], width=1)
    elif p['mouth'] == 'grin':
        d.rectangle([mx - 4, my - 1, mx + 4, my + 1], fill=P['white'])
        for gx in range(mx - 2, mx + 3, 2):
            d.line([gx, my - 1, gx, my + 1], fill=P['eye'], width=1)
    else:
        d.line([mx - 2, my, mx + 2, my], fill=P['eye'], width=1)
    # arms
    shL = (hx - 15, 80 + p['gy'])
    shR = (hx + 15, 80 + p['gy'])
    restL = (hx - 13, 97 + p['gy'])
    restR = (hx + 13, 97 + p['gy'])
    _arm(d, P, *shL, *(p['pawL'] or restL))
    _arm(d, P, *shR, *(p['pawR'] or restR))


# ---------------------------------------------------------------- shared gags
def gag_wave(p, i, t, side=1, bursts=2):
    """Raised paw waving beside the head, `bursts` times per loop."""
    cyc = (t * bursts) % 1.0
    up = kf(cyc, [(0, 0), (0.12, 1), (0.45, 1), (0.55, 0), (1, 0)])
    if up <= 0:
        return None, 0
    wig = int(round(3 * math.sin(24 * math.pi * t)))  # fast side wiggle
    return (p['hx'] + side * 22 + wig, p['hy'] - 16 - int(round(3 * up))), up


def gag_laugh_burst(t, bursts=2):
    cyc = (t * bursts) % 1.0
    return kf(cyc, [(0, 0), (0.06, 1), (0.38, 1), (0.48, 0), (1, 0)])


def gag_talk_mouth(i):
    return 'open' if (i // 2) % 2 == 0 else '-'


def gag_snap_fx(d, P, x, y, i, phase=0):
    """Finger-snap star, fires briefly on a 30-frame cadence."""
    if (i + phase) % 30 < 3:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            d.line([x + dx * 3, y + dy * 3, x + dx * 6, y + dy * 6],
                   fill=P['white'], width=1)


def fx_speech(d, P, x, y, i, color):
    """3 arcs radiating from the mic."""
    for k in range(3):
        u = ((i * 1.2 + k * 20) % 60) / 60.0
        xx = int(round(x + u * 22))
        col = mix(color, P['wall'], u * 0.5)
        d.arc([xx - 4, y - 9, xx + 4, y + 9], start=270, end=90, fill=col, width=1)


def fx_card(d, P_room, P_dj, p, i, t, lines, card_c, bursts=2):
    """DJ holds up a sign card overhead, `bursts` times per loop.
    Returns (pawL, pawR) targets while held."""
    cyc = (t * bursts) % 1.0
    pop = kf(cyc, [(0, 0), (0.08, 1), (0.42, 1), (0.5, 0), (1, 0)])
    if pop <= 0:
        return None, None
    hx, hy = p['hx'], p['hy']
    w = 44
    # nervous shake while held: 1px jitter on alternating frames
    shx = 1 if (i // 2) % 2 == 0 else -1
    shy = 1 if (i // 3) % 2 == 0 else 0
    cy = hy - 34 - int(round(2 * math.sin(6 * math.pi * t))) + shy
    rr(d, hx - w // 2 + shx, cy, hx + w // 2 + shx, cy + 18, card_c, r=2)
    d.rectangle([hx - w // 2 + shx, cy, hx + w // 2 + shx, cy + 18],
                outline=P_room['ink'])
    yy = cy + 3
    for ln in lines:
        text_c(d, ln, hx + shx, yy, 1, P_room['ink'])
        yy += 6
    return (hx - w // 2 + 3, cy + 18), (hx + w // 2 - 3, cy + 18)


def fx_text_pop(d, s, cx, y, i, t, scale, color, bursts=2, bg=None):
    cyc = (t * bursts) % 1.0
    pop = kf(cyc, [(0, 0), (0.08, 1), (0.42, 1), (0.5, 0), (1, 0)])
    if pop <= 0:
        return
    bounce = int(round(2 * math.sin(12 * math.pi * t)))
    if bg:
        wpx = len(s) * 4 * scale - scale + 6
        rr(d, cx - wpx // 2, y - 3 + bounce, cx + wpx // 2,
           y + 5 * scale + 2 + bounce, bg, r=2)
    text_c(d, s, cx, y + bounce, scale, color)


def fx_ticker(d, P, s, y, i, color, speed=1):
    """Seamless scrolling ticker along the bottom."""
    wpx = len(s) * 4 - 1 + 40
    off = (i * speed * wpx) // 60 % wpx
    for ox in (0, -wpx, wpx):
        text(d, s, 128 - off + ox, y, 1, color)


def draw_eq(d, P, x0, y0, w, h, i, t, color, bars=12):
    bw = w // bars
    for b in range(bars):
        bh = 2 + int(round((h - 2) * abs(math.sin(2 * math.pi * i / 60 * 2 +
                                                  b * 0.55))))
        x = x0 + b * bw
        d.rectangle([x, y0 + h - bh, x + bw - 2, y0 + h], fill=color)


# ---------------------------------------------------------------- render + QC
def render_state(state, animator, workdir=None):
    th = THEMES[state]
    P_room = booth_pal(th['lighting'])
    P_dj = dj_pal(th['dj']) if th['dj'] else None
    style = style_for(state)
    fdir = os.path.join(WORK, workdir or state)
    os.makedirs(fdir, exist_ok=True)
    for i in range(N):
        img = Image.new('RGB', (G, G), (0, 0, 0))
        animator(img, P_room, P_dj, style, i, N)
        img = img.resize((G * 4, G * 4), Image.NEAREST)
        img.save(os.path.join(fdir, f'f{i:02d}.png'))
    mp4 = os.path.join(WORK, f'{workdir or state}.mp4')
    gif = os.path.join(OUTDIR, f'fm99_{state}.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24',
                    '-i', os.path.join(fdir, 'f%02d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', mp4], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf',
                    'fps=24,scale=512:-1:flags=lanczos,'
                    'split[s0][s1];[s0]palettegen=max_colors=64[p];'
                    '[s1][p]paletteuse=dither=bayer', gif], check=True)
    return gif


def qc_state(state, gif):
    diffs, active = motion_audit(gif)
    colors = color_count(gif)
    im = Image.open(gif)
    im.seek(im.n_frames // 2)
    tiny = im.convert('RGB').resize((18, 12), Image.NEAREST)
    px = list(tiny.getdata())

    def close(a, b, tol=70):
        return all(abs(a[i] - b[i]) < tol for i in range(3))

    sig_n = sum(1 for p in px
                for s in THEMES[state]['sig'] if close(p, s))
    tiny_big = tiny.resize((180, 120), Image.NEAREST)
    tiny_big.save(os.path.join(WORK, f'legib_{state}.png'))
    return dict(state=state, active=active, total=len(diffs),
                mind=min(diffs), maxd=max(diffs),
                colors=colors, sig=sig_n)


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


def preview_all(states, out_name='preview_all20.png', cols=5):
    """Labeled contact sheet: one mid-loop frame per state."""
    cell, lab = G, 14
    rows = (len(states) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell, rows * (cell + lab)), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    for k, state in enumerate(states):
        gif = os.path.join(OUTDIR, f'fm99_{state}.gif')
        im = Image.open(gif)
        im.seek(im.n_frames // 2)
        fr = im.convert('RGB').resize((cell, cell), Image.NEAREST)
        x, y = (k % cols) * cell, (k // cols) * (cell + lab)
        sheet.paste(fr, (x, y))
        d.rectangle([x, y + cell, x + cell, y + cell + lab], fill=(20, 24, 34))
        nm = state.replace('_', ' ')
        text(d, nm[:16], x + 4, y + cell + 4, 1, (150, 200, 230))
    p = os.path.join(OUTDIR, out_name)
    sheet.save(p)
    return p
