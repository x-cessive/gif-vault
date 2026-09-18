#!/usr/bin/env python3
"""FM99 v2 — batch 3: Mina the crow, 8 night-booth states."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from radio_booth_v2 import V2, cyc, render_all, N, font
from PIL import ImageDraw


def led_pulse(img, i, color=(120, 230, 255), fast=False):
    """Glowing LED dots on Mina's headphone cups."""
    d = ImageDraw.Draw(img, "RGBA")
    a = int(150 + 90 * cyc(i, k=6 if fast else 2))
    for x, y in ((173, 192), (339, 192)):
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=color + (a,))
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(230, 250, 255, 255))
    return img


def booth_base(v, i, energy=0.85, chip_mode="on", glow_a=None):
    img = v.base("night")
    ga = 26 if glow_a is None else glow_a
    img = v.glow(img, (150, 110, 255), ga + int(14 * cyc(i, k=1)), (60, 40, 452, 400))
    return img


def finish(v, img, i, energy=0.85, chip_mode="on"):
    img = v.console(img, "night")
    img = v.meters(img, "night", i, energy=energy)
    img = v.chip(img, i, mode=chip_mode)
    return img


def mina_hosting(v, i):
    img = booth_base(v, i)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": 5 * cyc(i, k=2), "wingR": -5 * cyc(i, k=2, ph=0.5),
                  "beak": 0},
        head_dx=3 * cyc(i, k=1), head_rot=3 * cyc(i, k=1))
    img = v.place_dj(img, dj, "mina", bob=5 * cyc(i, k=1))
    img = finish(v, img, i)
    img = led_pulse(img, i)
    return v.notes(img, i, color=(190, 150, 255), seed=3)


def mina_night_signal(v, i):
    img = booth_base(v, i, energy=0.5, glow_a=40)
    img = v.dim(img, 30)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": 2 * cyc(i, k=1), "wingR": -2 * cyc(i, k=1, ph=0.6),
                  "beak": 0},
        head_dx=6 * cyc(i, k=1, ph=0.5), head_rot=2 * cyc(i, k=1))
    img = v.place_dj(img, dj, "mina", bob=3 * cyc(i, k=1))
    img = finish(v, img, i, energy=0.5)
    img = led_pulse(img, i, color=(170, 120, 255))
    img = v.fog(img, i)
    return v.qmarks(img, i)


def mina_vibing(v, i):
    img = booth_base(v, i, energy=1.0, glow_a=36)
    dj = v.djs["mina"].frame(
        i, blink=False, lids=1.0,
        parts={"wingL": 8 * cyc(i, k=4), "wingR": -8 * cyc(i, k=4, ph=0.5),
               "beak": 0},
        head_dy=4 * cyc(i, k=4), head_rot=4 * cyc(i, k=2))
    img = v.place_dj(img, dj, "mina", bob=8 * cyc(i, k=2))
    img = finish(v, img, i, energy=1.0)
    img = led_pulse(img, i, fast=True)
    img = v.eq(img, i, y0=364, h=32, color=(170, 130, 255), nbars=30, energy=0.9)
    return v.notes(img, i, color=(195, 155, 255), n_notes=8, seed=5)


def mina_talking(v, i):
    chatter = max(0, cyc(i, k=5)) ** 1.5
    img = booth_base(v, i, energy=0.85)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": 4 * cyc(i, k=2), "wingR": -4 * cyc(i, k=2, ph=0.6),
                  "beak": 13 * chatter},
        head_dx=4 * cyc(i, k=3), head_rot=3 * cyc(i, k=3))
    img = v.place_dj(img, dj, "mina", bob=4 * cyc(i, k=1))
    img = v.mic_prop(img, i, pos=(180, 300), w=112, angle=-18)
    img = finish(v, img, i, energy=0.7 + 0.5 * chatter)
    return led_pulse(img, i)


def mina_laughing(v, i):
    chatter = max(0, cyc(i, k=6)) ** 1.2
    img = booth_base(v, i, energy=1.0, glow_a=38)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": 13 * cyc(i, k=3), "wingR": -13 * cyc(i, k=3, ph=0.5),
                  "beak": 10 + 8 * chatter},
        head_dy=3 * cyc(i, k=8), head_rot=-8 + 2 * cyc(i, k=8))
    img = v.place_dj(img, dj, "mina", bob=4 * cyc(i, k=6))
    img = v.mic_prop(img, i, pos=(180, 300), w=112, angle=-18)
    img = finish(v, img, i, energy=1.0)
    img = led_pulse(img, i, fast=True)
    return v.notes(img, i, color=(200, 160, 255), n_notes=7, seed=6)


def mina_taking_requests(v, i):
    img = booth_base(v, i, energy=0.6)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": -8 + 3 * cyc(i, k=3), "wingR": 3 * cyc(i, k=3, ph=0.5),
                  "beak": 0},
        head_dx=-8, head_rot=-3 + 2 * cyc(i, k=2))
    img = v.place_dj(img, dj, "mina", bob=4 * cyc(i, k=1))
    img = finish(v, img, i, energy=0.6)
    img = led_pulse(img, i)
    return v.phone_prop(img, i, pos=(95, 442), w=125, ring=True)


def mina_back_after_break(v, i):
    img = booth_base(v, i, energy=1.0, glow_a=40)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": 11 * cyc(i, k=4), "wingR": -11 * cyc(i, k=4, ph=0.5),
                  "beak": 8 * max(0, cyc(i, k=4))},
        head_dy=4 * cyc(i, k=4), head_rot=4 * cyc(i, k=2))
    img = v.place_dj(img, dj, "mina", bob=7 * cyc(i, k=2))
    img = finish(v, img, i, energy=1.0, chip_mode="blink")
    img = led_pulse(img, i, fast=True)
    img = v.sweep(img, i, color=(190, 220, 255))
    return v.notes(img, i, color=(195, 155, 255), n_notes=8, seed=7)


def mina_technical_difficulties(v, i):
    img = booth_base(v, i, energy=0.25, glow_a=14)
    dj = v.djs["mina"].frame(
        i, parts={"wingL": 8 + 2 * cyc(i, k=1), "wingR": -8 - 2 * cyc(i, k=1, ph=0.7),
                  "beak": 0},
        head_dy=2 * cyc(i, k=1), head_rot=5)
    img = v.place_dj(img, dj, "mina", bob=2 * cyc(i, k=1))
    img = v.td_card(img, i, pos=(256, 292))
    img = finish(v, img, i, energy=0.25, chip_mode="flicker")
    return v.static(img, i, box=(0, 368, 512, 512), amt=700)


STATES = {
    "mina_hosting": mina_hosting,
    "mina_night_signal": mina_night_signal,
    "mina_vibing": mina_vibing,
    "mina_talking": mina_talking,
    "mina_laughing": mina_laughing,
    "mina_taking_requests": mina_taking_requests,
    "mina_back_after_break": mina_back_after_break,
    "mina_technical_difficulties": mina_technical_difficulties,
}

if __name__ == "__main__":
    render_all(STATES)
