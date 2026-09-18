"""30 chiptune SFX for Gigi otter states (one per state).

Replicates the repo's own synth framework (assets/gigi_pixel_preview/tools/sounds.py):
22050 Hz, mono, 16-bit WAV. Square/triangle/sine + pitch slides + noise only.
All clips <2s, peak vol family 0.35-0.45, seeded RNG for reproducibility.

Usage:
    python3 gigi_synth_sfx.py            # renders all 30 into ./gigi_sounds/
    python3 gigi_synth_sfx.py laughing   # renders one state
"""
import numpy as np
import wave, os, sys

SR = 22050
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gigi_sounds')


def env(n, a=0.008, r=0.08):
    e = np.ones(n)
    na, nr = int(SR * a), int(SR * r)
    if na > 0:
        e[:na] = np.linspace(0, 1, na)
    if nr > 0 and nr < n:
        e[-nr:] = np.linspace(1, 0, nr)
    return e


def osc(freq, dur, wave='square', vol=0.4, slide=None):
    n = int(SR * dur)
    t = np.arange(n) / SR
    if slide:
        f = np.linspace(freq, slide, n)
        ph = 2 * np.pi * np.cumsum(f) / SR
    else:
        ph = 2 * np.pi * freq * t
    if wave == 'square':
        s = np.sign(np.sin(ph)) * 0.8
    elif wave == 'triangle':
        s = 2 * np.abs(2 * (ph / (2 * np.pi) % 1) - 1) - 1
    else:
        s = np.sin(ph)
    return (s * env(n) * vol).astype(np.float32)


def noise(dur, vol=0.25, lowpass=4):
    n = int(SR * dur)
    s = np.random.default_rng(7).standard_normal(n)
    if lowpass > 1:
        s = np.convolve(s, np.ones(lowpass) / lowpass, mode='same')
    return (s * env(n, a=0.002, r=dur * 0.7) * vol).astype(np.float32)


def seq(notes, gap=0.02):
    parts = []
    for (freq, dur, wv, vol, *rest) in notes:
        slide = rest[0] if rest else None
        parts.append(osc(freq, dur, wv, vol, slide))
        if gap:
            parts.append(np.zeros(int(SR * gap), dtype=np.float32))
    return np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)


def save(name, samples):
    os.makedirs(OUT, exist_ok=True)
    s = np.asarray(samples, dtype=np.float32)
    # loudness family: every clip peaks at 0.40 (inside the 0.35-0.45 band)
    peak = float(np.abs(s).max())
    if peak > 0:
        s = s * (0.40 / peak)
    s = np.clip(s, -1, 1)
    pcm = (s * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, f'gigi_{name}.wav'), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def gap(dur):
    return np.zeros(int(SR * dur), dtype=np.float32)


def chord(freqs, dur, vol_each=0.18):
    """Stacked square voices at one vol so the sum peaks ~0.4."""
    return sum(osc(f, dur, 'square', vol_each) for f in freqs)


def trem(vol=0.42, freq=9.0, depth=0.35):
    """Square-buzz modulator for the bitching grumble."""
    n = int(SR * 0.55)
    return (vol * (1.0 - depth * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * freq * np.arange(n) / SR))))).astype(np.float32)


# Shorthand: S(freq, dur, wave='square', vol=0.4, slide=None)
S = lambda f, d, w='square', v=0.4, s=None: (f, d, w, v) if s is None else (f, d, w, v, s)

RECIPES = {
    # soft mechanical key clicks: three ticks + confirm blip
    'working': lambda: np.concatenate([
        noise(.04, .38), gap(.05), noise(.04, .38), gap(.05),
        noise(.04, .38), gap(.05), osc(990, .10, 'square', .35)]),
    # single warm sine blip
    'idle': lambda: osc(392, .28, 'sine', .40),
    # rising two-tone chime
    'listening': lambda: seq([S(660, .14, 'sine', .38), S(990, .24, 'sine', .38)], gap=0.03),
    # 3 quick pitch-wobbled talk squares
    'speaking': lambda: seq([
        S(300, .09, 'square', .36, 380), S(420, .09, 'square', .36, 340),
        S(500, .13, 'square', .36, 420)], gap=0.015),
    # slow ascending thoughtful triangle arpeggio
    'thinking': lambda: seq([
        S(330, .22, 'triangle', .36), S(370, .22, 'triangle', .36),
        S(415, .34, 'triangle', .36)], gap=0.06),
    # bright major arpeggio up
    'success': lambda: seq(
        [S(523, .10), S(659, .10), S(784, .10), S(1047, .30)], gap=0.015),
    # two-tone siren blip x2
    'alert': lambda: seq(
        [S(880, .12), S(660, .12), S(880, .12), S(660, .16)], gap=0.03),
    # descending sleepy sine slide
    'tired': lambda: osc(392, .70, 'sine', .38, slide=130),
    # grumbly low square buzz with tremolo
    'bitching': lambda: (osc(110, .55, 'square', 1.0) * trem()).astype(np.float32),
    # whoosh-up slide + commit pop
    'pushing_to_github': lambda: np.concatenate([
        noise(.30, .35, lowpass=16), osc(400, .30, 'square', .40, slide=1600),
        osc(1200, .12, 'sine', .40)]),
    # launch sweep up + soft noise boom
    'deploying': lambda: np.concatenate([
        osc(150, .50, 'square', .40, slide=900), noise(.40, .45, lowpass=10)]),
    # sonar ping + quieter echo
    'debugging': lambda: seq(
        [S(1000, .30, 'sine', .40), S(1000, .20, 'sine', .25)], gap=0.12),
    # descending sad trombone-ish slide
    'facepalm': lambda: osc(392, .50, 'square', .40, slide=196),
    # bouncy ha-ha: 4 quick ascending-descending notes
    'laughing': lambda: seq(
        [S(700, .08), S(900, .08), S(700, .08), S(900, .14)], gap=0.02),
    # smooth confident two-note (perfect fourth)
    'smug': lambda: seq(
        [S(494, .20, 'triangle', .38), S(587, .32, 'triangle', .38)], gap=0.03),
    # sip noise + satisfied upward blip
    'drinking_coffee': lambda: np.concatenate([
        noise(.18, .35, lowpass=3), osc(330, .20, 'sine', .38, slide=520)]),
    # 3 munchy chomps (square thump + click)
    'eating_snack': lambda: np.concatenate([
        osc(180, .07, 'square', .42), noise(.05, .40), gap(.05),
        osc(180, .07, 'square', .42), noise(.05, .40), gap(.05),
        osc(150, .09, 'square', .42), noise(.05, .40)]),
    # 4-on-the-floor: kick-ish sine thumps + hat ticks
    'dancing': lambda: np.concatenate([
        osc(60, .12, 'sine', .45), gap(.10), noise(.03, .30), gap(.10),
        osc(60, .12, 'sine', .45), gap(.10), noise(.03, .30), gap(.10),
        osc(60, .12, 'sine', .45), gap(.10), noise(.03, .30), gap(.10),
        osc(60, .12, 'sine', .45), gap(.10), noise(.03, .30),
        osc(880, .14, 'square', .38)]),
    # soft descending lullaby arpeggio
    'sleeping': lambda: seq([
        S(523, .30, 'sine', .36), S(440, .30, 'sine', .36),
        S(392, .30, 'sine', .36), S(330, .50, 'sine', .34)], gap=0.04),
    # quick gasp stab: fast pitch jump up
    'surprised': lambda: osc(300, .25, 'square', .42, slide=1100),
    # uncertain up-down wobble
    'shrugging': lambda: seq([
        S(440, .12, 'square', .36, 494), S(494, .12, 'square', .36, 440),
        S(440, .20, 'square', .36)], gap=0.03),
    # sneaky minor-key tiptoe: low triangle steps with quiet gaps
    'scheming': lambda: seq([
        S(196, .14, 'triangle', .38), S(220, .14, 'triangle', .38),
        S(196, .14, 'triangle', .38), S(165, .22, 'triangle', .38)], gap=0.06),
    # klaxon: fast alternating siren
    'panic': lambda: seq(
        [S(700, .10), S(500, .10)] * 3, gap=0.02),
    # snappy snare (noise) + trumpet-ish square stab
    'salute': lambda: np.concatenate([
        noise(.09, .42, lowpass=3), osc(587, .30, 'square', .40)]),
    # fanfare: major arp + final stacked chord
    'celebrating': lambda: np.concatenate([
        seq([S(523, .12), S(659, .12), S(784, .12), S(1047, .28)], gap=0.015),
        chord([523, 659, 784], .55)]),
    # 8-bit power-up arp up + laser slide down
    'gaming': lambda: np.concatenate([
        seq([S(262, .05), S(392, .05), S(523, .05), S(784, .05),
             S(1047, .18)], gap=0.008),
        osc(1600, .30, 'square', .40, slide=200)]),
    # power-down sweep + boot beep
    'rebooting': lambda: np.concatenate([
        osc(800, .50, 'sine', .40, slide=80), gap(.05),
        osc(880, .25, 'square', .40)]),
    # sizzle noise + warning blip
    'overheating': lambda: np.concatenate([
        noise(.50, .35, lowpass=2),
        seq([S(1200, .10), S(900, .12)], gap=0.03)]),
    # triumphant power-chord stab (stacked squares)
    'flexing': lambda: chord([110, 165, 220], .60),
    # cheerful wave melody: up then down
    'goodbye': lambda: seq([
        S(659, .12, 'triangle', .38), S(784, .12, 'triangle', .38),
        S(988, .12, 'triangle', .38), S(784, .12, 'triangle', .38),
        S(659, .26, 'triangle', .38)], gap=0.02),
}

if __name__ == '__main__':
    targets = sys.argv[1:] or list(RECIPES)
    for name in targets:
        if name not in RECIPES:
            print(f'unknown state: {name}')
            continue
        save(name, RECIPES[name]())
    # report durations + peak levels
    print(f'{"state":<18} {"file":<34} {"dur(s)":>7} {"peak":>5}')
    for name in targets:
        if name not in RECIPES:
            continue
        p = os.path.join(OUT, f'gigi_{name}.wav')
        with wave.open(p) as w:
            dur = w.getnframes() / w.getframerate()
            raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        print(f'{name:<18} gigi_{name}.wav {dur:>7.2f} {np.abs(raw).max()/32767:>5.2f}')
