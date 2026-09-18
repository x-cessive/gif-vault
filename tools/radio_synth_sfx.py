#!/usr/bin/env python3
"""Chiptune radio stingers for the 99.9 FM set: 20 mono 16-bit 22050 Hz WAVs.

Calder (day): bright major-key jingles. Mina (night): darker minor-key beds.
Idents: station jingle / vinyl stab / FM ident / sign-off lullaby.
"""
import math
import os
import struct
import wave

SR = 22050
OUT = os.path.expanduser('~/workspace/gif-station/fm99/sounds')

NOTES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def freq(name):
    n, octv = name[:-1], int(name[-1])
    midi = 12 * (octv + 1) + NOTES[n[0]] + (1 if '#' in n else 0)
    return 440.0 * 2 ** ((midi - 69) / 12)


def tone(f, dur, vol=0.5, kind='sq'):
    n = int(SR * dur)
    out = []
    for i in range(n):
        ph = f * i / SR
        if kind == 'sq':
            v = 1.0 if (ph % 1.0) < 0.5 else -1.0
        elif kind == 'tri':
            v = 4 * abs((ph % 1.0) - 0.5) - 1.0
        else:  # noise-ish for scratch fx
            v = ((int(ph * 7919) * 1103515245 + 12345) >> 16) & 1
            v = 1.0 if v else -1.0
        # 5 ms attack, exponential-ish decay tail
        a = min(1.0, i / (SR * 0.005))
        d = max(0.0, 1.0 - i / n)
        out.append(v * vol * a * (0.35 + 0.65 * d))
    return out


def seq(notes, gap=0.0):
    """notes: list of (name, dur, vol, kind). 'x' = rest (or noise if kind='nz')."""
    out = []
    for name, dur, vol, kind in notes:
        if name == 'x' and kind != 'nz':
            out += [0.0] * int(SR * dur)
        else:
            out += tone(440.0 if name == 'x' else freq(name), dur, vol, kind)
        if gap:
            out += [0.0] * int(SR * gap)
    return out


def chord(names, dur, vol=0.3, kind='sq'):
    parts = [tone(freq(x), dur, vol, kind) for x in names]
    return [sum(p[i] for p in parts) for i in range(len(parts[0]))]


def mix(*parts):
    n = max(len(p) for p in parts)
    out = [0.0] * n
    for p in parts:
        for i, v in enumerate(p):
            out[i] += v
    peak = max(1e-6, max(abs(v) for v in out))
    return [v / peak * 0.9 for v in out]


def save(name, samples):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f'fm99_{name}.wav')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(struct.pack('<%dh' % len(samples),
                                  *(int(max(-1, min(1, s)) * 32767)
                                    for s in samples)))
    print('wrote', path, f'{len(samples) / SR:.2f}s')


Q = 0.14  # eighth-ish beat

# ---- idents ---------------------------------------------------------------
save('on_air', mix(
    seq([('G4', Q, .5, 'sq'), ('C5', Q, .5, 'sq'), ('E5', Q, .5, 'sq'),
         ('G5', Q * 2, .5, 'sq')], gap=0.02),
    [0.0] * int(SR * 0.5) + tone(freq('C6'), 0.06, .35, 'sq')))
save('now_spinning', mix(
    seq([('x', 0.05, .25, 'nz'), ('x', 0.05, .18, 'nz'),
         ('x', 0.08, .25, 'nz')], gap=0.03),
    [0.0] * int(SR * 0.32) + chord(['C4', 'E4', 'G4'], 0.3, .35, 'sq')))
save('station_ident', mix(
    seq([('E5', Q, .5, 'sq'), ('G5', Q, .5, 'sq'), ('A5', Q, .5, 'sq'),
         ('C6', Q * 2.5, .55, 'sq')], gap=0.015),
    tone(freq('E3'), 0.9, .18, 'tri')))
save('signing_off', mix(
    seq([('G4', Q * 1.5, .45, 'tri'), ('E4', Q * 1.5, .45, 'tri'),
         ('C4', Q * 1.5, .45, 'tri'), ('G3', Q * 3, .4, 'tri')],
        gap=0.03)))

# ---- calder (day): bright, major ------------------------------------------
save('calder_hosting', mix(
    seq([('C5', Q, .5, 'sq'), ('D5', Q, .5, 'sq'), ('E5', Q * 2, .55, 'sq')],
        gap=0.02)))
save('calder_taking_requests', mix(
    seq([('A5', 0.09, .5, 'sq'), ('x', 0.09, 0, 'sq'),
         ('A5', 0.09, .5, 'sq'), ('x', 0.09, 0, 'sq'),
         ('A5', 0.18, .5, 'sq')], gap=0.0),
    [0.0] * int(SR * 0.55) + seq([('E5', Q, .5, 'sq'), ('G5', Q * 1.5, .5, 'sq')],
                                 gap=0.02)))
save('calder_vibing', mix(
    seq([('C4', Q, .4, 'sq'), ('E4', Q, .4, 'sq'), ('G4', Q, .4, 'sq'),
         ('E4', Q, .4, 'sq')] * 2, gap=0.01)))
save('calder_talking', mix(
    seq([('G4', 0.07, .4, 'sq'), ('A4', 0.07, .4, 'sq')] * 5, gap=0.02)))
save('calder_laughing', mix(
    seq([('E5', 0.09, .5, 'sq'), ('C5', 0.09, .5, 'sq')] * 3 +
        [('G5', 0.25, .55, 'sq')], gap=0.02)))
save('calder_mic_check', mix(
    seq([('x', 0.04, .4, 'nz'), ('x', 0.04, 0, 'sq'), ('x', 0.04, .4, 'nz'),
         ('x', 0.04, 0, 'sq'), ('x', 0.04, .4, 'nz')], gap=0.06),
    [0.0] * int(SR * 0.5) + seq([('C5', Q, .5, 'sq'), ('C5', Q * 1.5, .5, 'sq')],
                                gap=0.02)))
save('calder_back_after_break', mix(
    seq([('G4', Q, .5, 'sq'), ('C5', Q, .5, 'sq'), ('E5', Q, .5, 'sq'),
         ('G5', Q, .5, 'sq'), ('C6', Q * 2, .55, 'sq')], gap=0.015)))
save('calder_technical_difficulties', mix(
    seq([('x', 0.06, .3, 'nz')] * 6, gap=0.03),
    [0.0] * int(SR * 0.55) + seq([('E4', Q, .4, 'sq'), ('C4', Q * 2, .4, 'sq')],
                                 gap=0.02)))

# ---- mina (night): darker, minor ------------------------------------------
save('mina_hosting', mix(
    seq([('A3', Q * 1.5, .45, 'tri'), ('C4', Q * 1.5, .45, 'tri'),
         ('E4', Q * 2, .5, 'tri')], gap=0.02)))
save('mina_night_signal', mix(
    seq([('E4', Q * 2, .4, 'tri'), ('x', Q, 0, 'tri'),
         ('B3', Q * 2, .4, 'tri'), ('x', Q, 0, 'tri'),
         ('A3', Q * 3, .42, 'tri')], gap=0.04),
    tone(freq('A2'), 1.4, .15, 'tri')))
save('mina_vibing', mix(
    seq([('A3', Q, .4, 'sq'), ('C4', Q, .4, 'sq'), ('E4', Q, .4, 'sq'),
         ('C4', Q, .4, 'sq')] * 2, gap=0.01),
    tone(freq('A2'), 1.15, .12, 'tri')))
save('mina_talking', mix(
    seq([('D4', 0.07, .4, 'sq'), ('E4', 0.07, .4, 'sq')] * 5, gap=0.02)))
save('mina_laughing', mix(
    seq([('A4', 0.09, .5, 'sq'), ('F4', 0.09, .5, 'sq')] * 3 +
        [('C5', 0.25, .55, 'sq')], gap=0.02)))
save('mina_taking_requests', mix(
    seq([('E5', 0.09, .5, 'sq'), ('x', 0.09, 0, 'sq'),
         ('E5', 0.09, .5, 'sq'), ('x', 0.09, 0, 'sq'),
         ('E5', 0.18, .5, 'sq')], gap=0.0),
    [0.0] * int(SR * 0.55) + seq([('A4', Q, .5, 'tri'), ('C5', Q * 1.5, .5, 'tri')],
                                 gap=0.02)))
save('mina_back_after_break', mix(
    seq([('A3', Q, .5, 'tri'), ('C4', Q, .5, 'tri'), ('E4', Q, .5, 'tri'),
         ('A4', Q, .5, 'tri'), ('E5', Q * 2, .55, 'tri')], gap=0.015)))
save('mina_technical_difficulties', mix(
    seq([('x', 0.06, .3, 'nz')] * 6, gap=0.03),
    [0.0] * int(SR * 0.55) + seq([('A3', Q, .4, 'tri'), ('E3', Q * 2, .4, 'tri')],
                                 gap=0.02)))
