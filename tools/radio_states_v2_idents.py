#!/usr/bin/env python3
"""FM99 v2 — batch 1: the 4 station ident states (no DJ). Derived from the
night-booth illustration via crops + procedural FX."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from radio_booth_v2 import V2, cyc, render_all, N, font
from PIL import Image, ImageDraw

ASSETS = "/home/hatch/workspace/gif-station/fm99_v2/assets"
NIGHT = Image.open(ASSETS + "/booth_night.png").convert("RGB")


def crop_id(box):
    x0, y0, x1, y1 = box
    return NIGHT.crop((x0, y0, x1, y1)).resize((512, 512), Image.LANCZOS)


def on_air(v, i):
    img = crop_id((300, 60, 760, 520))
    img = v.glow(img, (255, 90, 80), 30 + int(22 * cyc(i, k=2)), (60, 80, 452, 320))
    m = i % 45
    if (30 <= m < 33) or (35 <= m < 38):  # signature double-blink
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([60, 80, 452, 310], fill=(8, 6, 8, 175))
    img = v.eq(img, i, y0=486, h=40, color=(255, 120, 100), nbars=30, energy=0.7)
    return img


def now_spinning(v, i):
    img = crop_id((0, 630, 650, 1280))
    img = v.vinyl(img, i, 165, 362, 118)  # signature spinning vinyl
    img = v.ticker(img, i, "NOW SPINNING   \u2022   99.9 FM   \u2022   ", y=476, size=21)
    return img


def station_ident(v, i):
    img = crop_id((730, 60, 1250, 580))
    img = v.glow(img, (150, 110, 255), 30 + int(22 * cyc(i, k=2)), (60, 110, 452, 340))
    m = i % 60
    if 40 <= m < 43:  # signature neon flicker dip
        img = v.dim(img, 95)
    img = v.eq(img, i, y0=482, h=54, color=(170, 130, 255), nbars=28, energy=0.9)
    return img


def signing_off(v, i):
    img = v.base("night")
    img = v.dim(img, int(150 * (i / (N - 1))))  # signature slow dim
    if i > 58:  # ON AIR sign goes dark
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([14, 54, 154, 134], fill=(10, 8, 12, 225))
    img = v.chip(img, i, mode="off" if i > 58 else "on")
    if i > 60:  # GOODNIGHT fade
        a = int(255 * (i - 60) / 29)
        d = ImageDraw.Draw(img, "RGBA")
        d.text((256, 190), "GOODNIGHT", font=font(46), fill=(235, 225, 255, a), anchor="mm")
        d.text((256, 244), "99.9 FM", font=font(28), fill=(160, 135, 255, a), anchor="mm")
    img = v.glow(img, (205, 205, 255), 22 + int(12 * cyc(i, k=1)), (300, 90, 430, 220))
    return img


STATES = {
    "on_air": on_air,
    "now_spinning": now_spinning,
    "station_ident": station_ident,
    "signing_off": signing_off,
}

if __name__ == "__main__":
    render_all(STATES)
