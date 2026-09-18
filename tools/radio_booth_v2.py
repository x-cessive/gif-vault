#!/usr/bin/env python3
"""FM99 v2 rig — detailed illustrated DJ set.

Calder: elephant day DJ. Mina: crow night DJ.
AI-illustrated character/booth art -> chroma-key -> paper-doll part animation
(ears, trunk bend, wings, beak) -> booth FX (VU meters, ON AIR, vinyl, EQ,
ticker, props) -> 90 unique frames @24fps -> ffmpeg palette 256 + bayer.

Animator signature: fn(v, i) -> PIL RGB image (512x512), v = V2 context.
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.expanduser("~/workspace/gif-station/fm99_v2")
ASSETS = os.path.join(ROOT, "assets")
FRAMES = os.path.join(ROOT, "frames")
OUT = os.path.expanduser("~/workspace/your_files/fm999_v2")
for _d in (ROOT, ASSETS, FRAMES, OUT):
    os.makedirs(_d, exist_ok=True)

N = 90
FPS = 24
SZ = 512
FB = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
FBOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"


def cyc(i, k=1, ph=0.0, n=N):
    return math.sin(2 * math.pi * k * i / n + ph)


def font(sz, black=True):
    return ImageFont.truetype(FB if black else FBOLD, sz)


# ---------------------------------------------------------------- keying
def keyed(path):
    """Load image, chroma-key pure green -> RGBA with despill + edge clean."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = (g > 140) & (g > r + 60) & (g > b + 60)
    alpha = np.where(mask, 0, 255).astype(np.uint8)
    alpha = np.asarray(Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)))
    rgb = np.asarray(im).astype(np.int16)
    cap = np.maximum(rgb[..., 0], rgb[..., 2]) + 28
    rgb[..., 1] = np.minimum(rgb[..., 1], cap)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, alpha]), "RGBA")


def keep_poly(layer, poly_frac):
    """Keep only the polygon region of an RGBA layer (feathered 1.2px)."""
    W, H = layer.size
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(x * W, y * H) for x, y in poly_frac], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(layer).copy()
    m = np.asarray(mask).astype(np.float32) / 255.0
    a[..., 3] = (a[..., 3].astype(np.float32) * m).astype(np.uint8)
    return Image.fromarray(a)


def bend_x(layer, amt, top_f=0.15, power=1.6):
    """Bend a layer horizontally: pinned at top_f, max shift amt at bottom."""
    a = np.asarray(layer)
    h = a.shape[0]
    y0 = int(top_f * h)
    yy = np.arange(h)
    f = np.clip((yy - y0) / max(1, h - 1 - y0), 0, 1) ** power
    dx = np.round(amt * f).astype(int)
    out = np.empty_like(a)
    for y in range(h):
        out[y] = np.roll(a[y], dx[y], axis=0)
    return Image.fromarray(out)


# ---------------------------------------------------------------- characters
CALDER = dict(
    file="calder.png", w=368, cx=256, bottom=445,
    order=["earL", "earR", "body", "trunk", "head"],
    parts={
        "earL": dict(box=(0.00, 0.13, 0.42, 0.75), pivot=(0.335, 0.42),
                     keep=[(0.015, 0.24), (0.13, 0.175), (0.27, 0.185), (0.345, 0.27),
                           (0.365, 0.36), (0.36, 0.48), (0.315, 0.60), (0.225, 0.70),
                           (0.11, 0.675), (0.025, 0.56), (0.0, 0.40)]),
        "earR": dict(box=(0.58, 0.13, 1.00, 0.75), pivot=(0.665, 0.42),
                     keep=[(0.985, 0.24), (0.87, 0.175), (0.73, 0.185), (0.655, 0.27),
                           (0.635, 0.36), (0.64, 0.48), (0.685, 0.60), (0.775, 0.70),
                           (0.89, 0.675), (0.975, 0.56), (1.0, 0.40)]),
        "body": dict(box=(0.00, 0.55, 1.00, 1.00), pivot=(0.50, 0.80)),
        "trunk": dict(box=(0.40, 0.44, 0.88, 1.00), pivot=(0.52, 0.55), bend_top=0.19,
                      keep=[(0.455, 0.495), (0.565, 0.495), (0.585, 0.60), (0.62, 0.72),
                            (0.685, 0.825), (0.775, 0.89), (0.83, 0.885), (0.845, 0.835),
                            (0.80, 0.795), (0.735, 0.815), (0.695, 0.765),
                            (0.645, 0.655), (0.60, 0.555)]),
        "head": dict(box=(0.20, 0.05, 0.80, 0.60), pivot=(0.50, 0.585)),
    },
    eyes=[(0.410, 0.466), (0.625, 0.466)], eye_wh=(0.052, 0.034),
    lid_at=(0.410, 0.412),
)

MINA = dict(
    file="mina.png", w=320, cx=256, bottom=470,
    order=["wingL", "wingR", "body", "head", "beak"],
    parts={
        "wingL": dict(box=(0.00, 0.58, 0.42, 1.00), pivot=(0.30, 0.68),
                      keep=[(0.0, 0.68), (0.10, 0.625), (0.26, 0.63), (0.36, 0.70),
                            (0.42, 0.72), (0.42, 0.95), (0.30, 1.0), (0.0, 1.0)]),
        "wingR": dict(box=(0.58, 0.58, 1.00, 1.00), pivot=(0.70, 0.68),
                      keep=[(1.0, 0.68), (0.90, 0.625), (0.74, 0.63), (0.64, 0.70),
                            (0.58, 0.72), (0.58, 0.95), (0.70, 1.0), (1.0, 1.0)]),
        "body": dict(box=(0.00, 0.50, 1.00, 1.00), pivot=(0.50, 0.80)),
        "head": dict(box=(0.10, 0.00, 0.92, 0.58), pivot=(0.51, 0.55),
                     mouth=(0.545, 0.508, 0.085, 0.038)),
        "beak": dict(box=(0.44, 0.44, 0.78, 0.62), pivot=(0.52, 0.505),
                     keep=[(0.465, 0.488), (0.58, 0.50), (0.70, 0.525), (0.725, 0.545),
                           (0.68, 0.575), (0.58, 0.575), (0.49, 0.55), (0.455, 0.515)]),
    },
    eyes=[(0.400, 0.440), (0.648, 0.435)], eye_wh=(0.060, 0.035),
    lid_at=(0.400, 0.392),
)


class DJ:
    def __init__(self, cfg):
        self.cfg = cfg
        img = keyed(os.path.join(ASSETS, cfg["file"]))
        W = cfg["w"]
        H = int(round(W * img.height / img.width))
        img = img.resize((W, H), Image.LANCZOS)
        self.W, self.H = W, H
        self.parts = {}
        for pname in cfg["order"]:
            p = cfg["parts"][pname]
            fx0, fy0, fx1, fy1 = p["box"]
            x0, y0, x1, y1 = int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H)
            layer = img.crop((x0, y0, x1, y1))
            if "keep" in p:
                full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                full.alpha_composite(layer, (x0, y0))
                full = keep_poly(full, p["keep"])
                layer = full.crop((x0, y0, x1, y1))
            if "mouth" in p:  # dark mouth interior revealed when beak opens
                mx, my, mw, mh = p["mouth"]
                d = ImageDraw.Draw(layer)
                d.ellipse([((mx - mw / 2) * W - x0), ((my - mh / 2) * H - y0),
                           ((mx + mw / 2) * W - x0), ((my + mh / 2) * H - y0)],
                          fill=(46, 12, 22, 255))
            self.parts[pname] = dict(
                layer=layer, offset=(x0, y0),
                pivot=((p["pivot"][0] * W) - x0, (p["pivot"][1] * H) - y0),
                bend_top=p.get("bend_top", 0.15))
        lx, ly = cfg["lid_at"][0] * W, cfg["lid_at"][1] * H
        self.lid_color = img.convert("RGB").getpixel((int(lx), int(ly)))

    def blink_amt(self, i):
        m = i % 78
        if m < 4:
            return math.sin(math.pi * (m + 0.5) / 4)
        return 0.0

    def frame(self, i, bob=0.0, parts=None, blink=True, lids=0.0,
              head_dx=0.0, head_dy=0.0, head_rot=0.0):
        parts = parts or {}
        W, H = self.W, self.H
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for pname in self.cfg["order"]:
            p = self.parts[pname]
            layer = p["layer"]
            ox, oy = p["offset"]
            if pname == "trunk" and "bend" in parts:
                layer = bend_x(layer, parts["bend"], top_f=p["bend_top"])
            elif pname == "head" and (head_rot or head_dx or head_dy):
                if head_rot:
                    layer = layer.rotate(head_rot, resample=Image.BICUBIC, center=p["pivot"])
                ox, oy = ox + head_dx, oy + head_dy
            else:
                ang = parts.get(pname, 0)
                if ang:
                    layer = layer.rotate(ang, resample=Image.BICUBIC, center=p["pivot"])
            canvas.alpha_composite(layer, (int(ox), int(oy)))
        lid = max(self.blink_amt(i) if blink else 0.0, lids)
        if lid > 0.01:
            d = ImageDraw.Draw(canvas)
            ew, eh = self.cfg["eye_wh"][0] * W, self.cfg["eye_wh"][1] * H
            for ex, ey in self.cfg["eyes"]:
                cxp, cyp = ex * W, ey * H
                hh = max(1.5, eh * lid * 0.75)
                d.ellipse([cxp - ew * 0.62, cyp - hh, cxp + ew * 0.62, cyp + hh],
                          fill=self.lid_color + (255,))
        self._bob = bob
        return canvas


# ---------------------------------------------------------------- booths
BOOTH_CFG = {
    "day": dict(file="booth_day.png", crop=(40, 0, 1320, 1280), console_top=396,
                 screens=[(184, 396, 264, 448), (344, 396, 424, 448)]),
    "night": dict(file="booth_night.png", crop=(320, 0, 1600, 1280), console_top=368,
                   screens=[(104, 372, 168, 400), (212, 372, 276, 400)]),
}


class Booth:
    def __init__(self, which):
        cfg = BOOTH_CFG[which]
        im = Image.open(os.path.join(ASSETS, cfg["file"])).convert("RGB")
        x0, y0, x1, y1 = cfg["crop"]
        self.img = im.crop((x0, y0, x1, y1)).resize((SZ, SZ), Image.LANCZOS)
        self.cfg = cfg
        self.which = which


class V2:
    def __init__(self):
        self.booths = {"day": Booth("day"), "night": Booth("night")}
        self.djs = {"calder": DJ(CALDER), "mina": DJ(MINA)}
        self.mic = keyed(os.path.join(ASSETS, "prop_mic.png"))
        self.phone = keyed(os.path.join(ASSETS, "prop_phone.png"))

    # -- base layers -----------------------------------------------------
    def base(self, which):
        return self.booths[which].img.copy()

    def place_dj(self, img, dj_rgba, which, bob=0.0):
        cfg = self.djs[which].cfg
        x = int(cfg["cx"] - dj_rgba.width / 2)
        y = int(cfg["bottom"] - dj_rgba.height + bob)
        base = img.convert("RGBA")
        base.alpha_composite(dj_rgba, (x, y))
        return base.convert("RGB")

    def console(self, img, which):
        """Paste console strip over the DJ's lower body (DJ sits behind desk)."""
        b = self.booths[which]
        top = b.cfg["console_top"]
        img.paste(b.img.crop((0, top, SZ, SZ)), (0, top))
        return img

    # -- booth FX --------------------------------------------------------
    def meters(self, img, which, i, energy=1.0):
        d = ImageDraw.Draw(img)
        for (x0, y0, x1, y1) in self.booths[which].cfg["screens"]:
            d.rectangle([x0, y0, x1, y1], fill=(6, 8, 14))
            bw = x1 - x0
            for ch in (0, 1):
                lvl = energy * (0.45 + 0.38 * cyc(i, k=3 + ch * 2, ph=ch * 1.9)
                                + 0.17 * cyc(i, k=7 + ch, ph=ch))
                lvl = max(0.03, min(1.0, lvl))
                by = y0 + 6 + ch * ((y1 - y0 - 12) // 2)
                bh = (y1 - y0 - 18) // 2
                segs = 14
                on = int(lvl * segs)
                for sgi in range(segs):
                    col = (70, 230, 120) if sgi < 9 else ((255, 190, 80) if sgi < 12 else (255, 80, 70))
                    if sgi >= on:
                        col = (30, 36, 44)
                    sx = x0 + 5 + sgi * ((bw - 10) // segs)
                    d.rectangle([sx, by, sx + (bw - 10) // segs - 2, by + bh], fill=col)
        return img

    def chip(self, img, i, mode="on"):
        """Small ON AIR tally chip, top-center."""
        x0, y0, x1, y1 = 216, 14, 296, 46
        d = ImageDraw.Draw(img, "RGBA")
        if mode == "off":
            d.rounded_rectangle([x0, y0, x1, y1], 8, fill=(40, 18, 18, 255))
            d.text((256, 30), "ON AIR", font=font(13), fill=(110, 60, 60, 255), anchor="mm")
            return img
        glow = 1.0
        if mode == "blink":
            glow = 1.0 if (i // 12) % 2 == 0 else 0.15
        elif mode == "flicker":
            glow = 0.55 + 0.45 * cyc(i, k=5) * cyc(i, k=9, ph=1.0)
            glow = max(0.1, glow)
        gc = (int(255 * glow), int(70 * glow), int(60 * glow))
        d.rounded_rectangle([x0, y0, x1, y1], 8, fill=(int(30 * glow) + 8, 8, 10, 255),
                            outline=gc, width=2)
        d.text((256, 30), "ON AIR", font=font(13), fill=(255, 120, 110, 255), anchor="mm")
        return img

    def glow(self, img, color, alpha, box):
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse(box, fill=color + (alpha,))
        ov = ov.filter(ImageFilter.GaussianBlur(40))
        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    def notes(self, img, i, color=(255, 200, 120), n_notes=6, seed=0,
              area=(70, 90, 442, 300)):
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for m in range(n_notes):
            ph = ((i / N) + m / n_notes + seed * 0.13) % 1.0
            x = area[0] + ((m * 137 + seed * 61) % (area[2] - area[0]))
            y = area[3] - ph * (area[3] - area[1])
            a = int(210 * (1 - ph * 0.65))
            c = color + (a,)
            d.ellipse([x - 7, y - 5, x + 7, y + 5], fill=c)
            d.line([x + 6, y, x + 6, y - 24], fill=c, width=3)
            d.polygon([(x + 6, y - 24), (x + 16, y - 20), (x + 6, y - 14)], fill=c)
        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    def eq(self, img, i, y0=448, h=52, color=(120, 220, 255), nbars=26, energy=1.0):
        d = ImageDraw.Draw(img, "RGBA")
        bw = SZ // nbars
        for b in range(nbars):
            lvl = energy * (0.35 + 0.4 * cyc(i, k=2 + (b % 5), ph=b * 0.9)
                            + 0.25 * cyc(i, k=6, ph=b * 2.1))
            lvl = max(0.05, min(1.0, lvl))
            bh = int(lvl * h)
            x = b * bw + 3
            d.rectangle([x, y0 - bh, x + bw - 6, y0], fill=color + (200,))
        return img

    def ticker(self, img, i, text, y=482, size=20, color=(240, 240, 240)):
        f = font(size)
        tw = int(self._tw(text, f))
        x = SZ - ((i * 5) % (SZ + tw))
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([0, y - 4, SZ, y + size + 6], fill=(0, 0, 0, 160))
        d.text((x, y), text, font=f, fill=color + (255,))
        d.text((x + tw + 40, y), text, font=f, fill=color + (255,))
        return img

    @staticmethod
    def _tw(text, f):
        return f.getbbox(text)[2]

    def vinyl(self, img, i, cx, cy, r, label=(240, 170, 60)):
        d = ImageDraw.Draw(img)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 14, 18))
        for gr in range(3, 10):
            rr = r * gr / 10
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(40, 40, 52))
        ang = 2 * math.pi * 2 * i / N
        hx, hy = cx + math.cos(ang) * r * 0.75, cy + math.sin(ang) * r * 0.75
        d.line([cx, cy, hx, hy], fill=(90, 90, 110), width=max(2, r // 18))
        lr = r * 0.28
        d.ellipse([cx - lr, cy - lr, cx + lr, cy + lr], fill=label)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(20, 20, 26))
        return img

    def fog(self, img, i, color=(150, 110, 255)):
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for m in range(3):
            x = ((i * (6 + m * 3) + m * 220) % (SZ + 320)) - 160
            y = 120 + m * 110
            d.ellipse([x - 150, y - 60, x + 150, y + 60], fill=color + (26,))
        ov = ov.filter(ImageFilter.GaussianBlur(30))
        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    def qmarks(self, img, i, color=(190, 150, 255), n=4):
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        f = font(34)
        for m in range(n):
            ph = ((i / N) + m / n) % 1.0
            x = 90 + ((m * 173) % 330)
            y = 300 - ph * 220
            a = int(200 * (1 - ph * 0.6))
            d.text((x, y), "?", font=f, fill=color + (a,))
        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    def dim(self, img, amt):
        ov = Image.new("RGBA", img.size, (0, 0, 0, amt))
        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    def static(self, img, i, box=(0, 368, 512, 512), amt=900):
        rng = np.random.default_rng(i)
        a = np.asarray(img).copy()
        ys = rng.integers(box[1], box[3], amt)
        xs = rng.integers(box[0], box[2], amt)
        vals = rng.integers(120, 256, (amt, 3))
        a[ys, xs] = vals
        return Image.fromarray(a)

    # -- props -----------------------------------------------------------
    def mic_prop(self, img, i, pos, w=120, angle=-16, bob_amp=2.0, tap=0.0):
        m = self.mic.resize((w, int(w * self.mic.height / self.mic.width)), Image.LANCZOS)
        m = m.rotate(angle + tap, resample=Image.BICUBIC, expand=True)
        x, y = pos[0] - m.width // 2, pos[1] - m.height // 2 + int(bob_amp * cyc(i, k=2))
        base = img.convert("RGBA")
        base.alpha_composite(m, (x, y))
        return base.convert("RGB")

    def phone_prop(self, img, i, pos=(105, 448), w=130, ring=True):
        p = self.phone.resize((w, int(w * self.phone.height / self.phone.width)), Image.LANCZOS)
        if ring:
            p = p.rotate(5 * cyc(i, k=6), resample=Image.BICUBIC, expand=True)
        x, y = pos[0] - p.width // 2, pos[1] - p.height // 2
        base = img.convert("RGBA")
        base.alpha_composite(p, (x, y))
        img = base.convert("RGB")
        if ring:
            d = ImageDraw.Draw(img, "RGBA")
            for r in range(3):
                rr = 46 + r * 16 + int(6 * cyc(i, k=6, ph=r))
                a = int(160 - r * 40)
                d.arc([pos[0] - rr, pos[1] - rr - 10, pos[0] + rr, pos[1] + rr - 10],
                      200, 340, fill=(255, 220, 130, a), width=3)
            pulse = 0.6 + 0.4 * cyc(i, k=6)
            d.text((pos[0], pos[1] - 78), "RING", font=font(17),
                   fill=(255, int(200 * pulse) + 40, 90, 255), anchor="mm")
        return img

    def td_card(self, img, i, pos=(256, 296)):
        cw, chh = 300, 168
        card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([4, 4, cw - 4, chh - 4], 14, fill=(238, 232, 222, 255),
                            outline=(200, 40, 40), width=8)
        d.text((cw / 2, 52), "TECHNICAL", font=font(34), fill=(190, 30, 30, 255), anchor="mm")
        d.text((cw / 2, 94), "DIFFICULTIES", font=font(34), fill=(190, 30, 30, 255), anchor="mm")
        d.text((cw / 2, 134), "PLEASE STAND BY", font=font(18, black=False),
               fill=(90, 80, 70, 255), anchor="mm")
        card = card.rotate(3 * cyc(i, k=1), resample=Image.BICUBIC, expand=True)
        base = img.convert("RGBA")
        base.alpha_composite(card, (int(pos[0] - card.width / 2), int(pos[1] - card.height / 2)))
        return base.convert("RGB")

    def sweep(self, img, i, color=(255, 240, 210)):
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        x = ((i / N) * (SZ + 300)) - 150
        d.polygon([(x, 0), (x + 70, 0), (x - 60, SZ), (x - 130, SZ)], fill=color + (30,))
        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


# ---------------------------------------------------------------- render
def render(name, fn, v=None):
    v = v or V2()
    fdir = os.path.join(FRAMES, name)
    os.makedirs(fdir, exist_ok=True)
    for i in range(N):
        fn(v, i).save(os.path.join(fdir, "%03d.png" % i))
    out = os.path.join(OUT, "fm99_%s.gif" % name)
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(fdir, "%03d.png"),
           "-vf", ("fps=%d,scale=512:-1:flags=lanczos,split[s0][s1];"
                   "[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer" % FPS),
           out]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def render_all(states):
    v = V2()
    for name, fn in states.items():
        print("rendering", name, flush=True)
        render(name, fn, v)
    print("done", len(states))


# ---------------------------------------------------------------- QC
def color_count(path):
    im = Image.open(path)
    im = im.convert("RGB")
    return len(im.getcolors(1 << 20) or [])


def motion_audit(path, thresh=1.0):
    im = Image.open(path)
    frames = []
    try:
        while True:
            frames.append(np.asarray(im.convert("L").resize((64, 64))).astype(np.int16))
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    diffs = [np.abs(frames[k + 1] - frames[k]).mean() for k in range(len(frames) - 1)]
    diffs = np.array(diffs)
    return dict(mean=float(diffs.mean()), min=float(diffs.min()),
                active=float((diffs > thresh).mean()), n=len(frames))


def qc_report(paths):
    rep = {}
    for p in paths:
        name = os.path.basename(p)
        try:
            cc = color_count(p)
        except Exception:
            cc = -1
        try:
            ma = motion_audit(p)
        except Exception as e:
            ma = dict(error=str(e))
        size = os.path.getsize(p)
        rep[name] = dict(colors=cc, motion=ma, bytes=size)
    return rep


def contact_sheet(paths, out_path, cols=5, thumb=160):
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb, rows * (thumb + 22)), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    for k, p in enumerate(paths):
        im = Image.open(p)
        im.seek(0)
        th = im.convert("RGB").resize((thumb, thumb), Image.LANCZOS)
        x, y = (k % cols) * thumb, (k // cols) * (thumb + 22)
        sheet.paste(th, (x, y))
        d.text((x + 4, y + thumb + 3),
               os.path.basename(p).replace("fm99_", "").replace(".gif", "")[:20],
               font=font(13, black=False), fill=(200, 200, 210))
    sheet.save(out_path)
    return out_path
