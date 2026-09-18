#!/usr/bin/env python3
"""FM99 v2 — batch 2: Calder the elephant, 8 day-booth states."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from radio_booth_v2 import V2, cyc, render_all, N, font
from PIL import ImageDraw


def booth_base(v, i, energy=0.75, chip_mode="on", glow_a=None):
    img = v.base("day")
    ga = 26 if glow_a is None else glow_a
    img = v.glow(img, (255, 190, 120), ga + int(14 * cyc(i, k=1)), (60, 60, 452, 420))
    return img


def finish(v, img, i, energy=0.75, chip_mode="on"):
    img = v.console(img, "day")
    img = v.meters(img, "day", i, energy=energy)
    img = v.chip(img, i, mode=chip_mode)
    return img


def calder_hosting(v, i):
    img = booth_base(v, i)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 6 * cyc(i, k=2), "earR": -6 * cyc(i, k=2, ph=0.6),
                  "bend": 14 * cyc(i, k=1, ph=1.0)},
        head_dy=3 * cyc(i, k=2), head_rot=2 * cyc(i, k=1))
    img = v.place_dj(img, dj, "calder", bob=6 * cyc(i, k=1))
    img = finish(v, img, i)
    return v.notes(img, i, color=(255, 200, 120))


def calder_taking_requests(v, i):
    img = booth_base(v, i, energy=0.6)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 4 + 3 * cyc(i, k=3), "earR": -4 - 3 * cyc(i, k=3, ph=0.4),
                  "bend": -12 + 9 * cyc(i, k=2, ph=0.8)},
        head_dx=-9, head_dy=2 * cyc(i, k=2), head_rot=-4)
    img = v.place_dj(img, dj, "calder", bob=4 * cyc(i, k=1))
    img = finish(v, img, i, energy=0.6)
    return v.phone_prop(img, i, pos=(100, 450), w=130, ring=True)


def calder_vibing(v, i):
    img = booth_base(v, i, energy=1.0, glow_a=34)
    dj = v.djs["calder"].frame(
        i, blink=False, lids=1.0,
        parts={"earL": 10 * cyc(i, k=4), "earR": -10 * cyc(i, k=4, ph=0.5),
               "bend": 18 * cyc(i, k=2, ph=0.7)},
        head_dy=5 * cyc(i, k=4), head_rot=4 * cyc(i, k=2))
    img = v.place_dj(img, dj, "calder", bob=9 * cyc(i, k=2))
    img = finish(v, img, i, energy=1.0)
    img = v.eq(img, i, y0=392, h=34, color=(255, 190, 110), nbars=30, energy=0.9)
    return v.notes(img, i, color=(255, 205, 130), n_notes=8, seed=1)


def calder_talking(v, i):
    chatter = max(0, cyc(i, k=5)) ** 1.5
    img = booth_base(v, i, energy=0.8)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 5 * cyc(i, k=2), "earR": -5 * cyc(i, k=2, ph=0.6),
                  "bend": 12 * chatter + 8 * cyc(i, k=1, ph=0.5)},
        head_dy=4 * cyc(i, k=5), head_rot=3 * cyc(i, k=3))
    img = v.place_dj(img, dj, "calder", bob=5 * cyc(i, k=1))
    img = v.mic_prop(img, i, pos=(168, 302), w=118, angle=-16)
    img = finish(v, img, i, energy=0.7 + 0.5 * chatter)
    return img


def calder_laughing(v, i):
    img = booth_base(v, i, energy=1.0, glow_a=36)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 14 * cyc(i, k=3), "earR": -14 * cyc(i, k=3, ph=0.5),
                  "bend": -16 + 12 * cyc(i, k=3, ph=1.2)},
        head_dy=4 * cyc(i, k=8), head_rot=-9 + 2 * cyc(i, k=8))
    img = v.place_dj(img, dj, "calder", bob=5 * cyc(i, k=6))
    img = v.mic_prop(img, i, pos=(168, 302), w=118, angle=-16)
    img = finish(v, img, i, energy=1.0)
    return v.notes(img, i, color=(255, 210, 140), n_notes=7, seed=2)


def calder_mic_check(v, i):
    tap = max(0, cyc(i, k=3)) ** 12  # 3 sharp taps per loop
    img = booth_base(v, i, energy=0.5)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 4 * cyc(i, k=2), "earR": -4 * cyc(i, k=2, ph=0.6),
                  "bend": -22 * tap + 6 * cyc(i, k=1)},
        head_dy=2 * cyc(i, k=2), head_rot=-2 * tap)
    img = v.place_dj(img, dj, "calder", bob=3 * cyc(i, k=1))
    img = v.mic_prop(img, i, pos=(168, 302), w=118, angle=-16, tap=7 * tap)
    img = finish(v, img, i, energy=0.35 + 0.65 * tap)
    if tap > 0.5:
        d = ImageDraw.Draw(img, "RGBA")
        d.text((168, 210), "TAP", font=font(20), fill=(255, 220, 130, int(220 * tap)),
               anchor="mm")
    return img


def calder_back_after_break(v, i):
    img = booth_base(v, i, energy=1.0, glow_a=38)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 12 * cyc(i, k=4), "earR": -12 * cyc(i, k=4, ph=0.5),
                  "bend": -8 + 20 * cyc(i, k=2, ph=0.9)},
        head_dy=4 * cyc(i, k=4), head_rot=4 * cyc(i, k=2))
    img = v.place_dj(img, dj, "calder", bob=8 * cyc(i, k=2))
    img = finish(v, img, i, energy=1.0, chip_mode="blink")
    img = v.sweep(img, i)
    return v.notes(img, i, color=(255, 205, 130), n_notes=8, seed=4)


def calder_technical_difficulties(v, i):
    img = booth_base(v, i, energy=0.25, glow_a=14)
    dj = v.djs["calder"].frame(
        i, parts={"earL": 9 + 2 * cyc(i, k=1), "earR": -9 - 2 * cyc(i, k=1, ph=0.7),
                  "bend": 6 * cyc(i, k=1, ph=2.0)},
        head_dy=2 * cyc(i, k=1), head_rot=5)
    img = v.place_dj(img, dj, "calder", bob=2 * cyc(i, k=1))
    img = v.td_card(img, i, pos=(256, 292))
    img = finish(v, img, i, energy=0.25, chip_mode="flicker")
    return v.static(img, i, box=(0, 396, 512, 512), amt=700)


STATES = {
    "calder_hosting": calder_hosting,
    "calder_taking_requests": calder_taking_requests,
    "calder_vibing": calder_vibing,
    "calder_talking": calder_talking,
    "calder_laughing": calder_laughing,
    "calder_mic_check": calder_mic_check,
    "calder_back_after_break": calder_back_after_break,
    "calder_technical_difficulties": calder_technical_difficulties,
}

if __name__ == "__main__":
    render_all(STATES)
