#!/usr/bin/env python3
"""Procedural, royalty-free background music + sound effects for social videos.

Every track is synthesized from scratch (no samples, no licensing issues), so each
post can get its own variation of a mood. Moods:

  chill      lo-fi, warm electric piano, soft swung drums, vinyl crackle   (tips, checklists, saves)
  upbeat     bright pop, four-on-the-floor, plucky chords                  (listicles, wins, countdowns)
  tense      ticking clock, pulsing bass, dark pad, heartbeat kick         (POV disasters, deadlines)
  dramatic   slow cinematic hits, low strings, big toms                    (myth busting, reveals, hot takes)
  playful    bouncy marimba, light claps                                   (quizzes, relatable humour)
  confident  boom-bap hip-hop, minor 7th chords                            (hot takes, "here's the truth")

Usage (CLI):  python3 music.py <mood> <seconds> <out.wav> [seed]
"""
import sys, wave
import numpy as np
from scipy.signal import lfilter, fftconvolve

SR = 44100

# ----------------------------------------------------------------- helpers
def note_hz(n):  # MIDI note -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=np.float32)
    a_n = max(1, min(a_n, n)); e[:a_n] = np.linspace(0, 1, a_n)
    if a_n < n:
        dn = max(1, min(d_n, n - a_n)); e[a_n:a_n + dn] = np.linspace(1, s, dn)
    if r_n and r_n < n:
        e[-r_n:] *= np.linspace(1, 0, r_n)
    return e

def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([1 - a], [1, -a], x).astype(np.float32)

def highpass(x, cutoff):
    return (x - lowpass(x, cutoff)).astype(np.float32)

def t_arr(dur):
    return np.arange(int(dur * SR), dtype=np.float32) / SR

# ----------------------------------------------------------------- instruments
def epiano(f, dur):
    t = t_arr(dur)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
         + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
         + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 7))
    x *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    return x * env_adsr(len(t), 0.004, 0.05, 1, 0.08)

def pluck(f, dur, bright=10):
    t = t_arr(dur)
    x = np.zeros_like(t)
    for h in range(1, bright + 1):
        x += np.sin(2 * np.pi * f * h * t) / h * np.exp(-t * (3 + h * 1.6))
    return x * env_adsr(len(t), 0.002, 0.05, 1, 0.05)

def marimba(f, dur):
    t = t_arr(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.25 * np.sin(2 * np.pi * 3.93 * f * t) * np.exp(-t * 18)
    return x * env_adsr(len(t), 0.001, 0.02, 1, 0.03)

def pad(f, dur, attack=0.6, dark=False):
    t = t_arr(dur)
    x = np.zeros_like(t)
    for det in (-0.08, 0.0, 0.07):
        ff = note_hz(f) if False else f * 2 ** (det / 12)
        for h in range(1, 6 if not dark else 4):
            x += np.sin(2 * np.pi * ff * h * t + det * 7) / (h ** 1.4)
    return x / 3 * env_adsr(len(t), attack, 0.3, 0.85, min(0.8, dur / 2))

def bass(f, dur, growl=0.25):
    t = t_arr(dur)
    x = np.sin(2 * np.pi * f * t) + growl * np.sin(2 * np.pi * 2 * f * t) + growl * 0.4 * np.sin(2 * np.pi * 3 * f * t)
    return x * env_adsr(len(t), 0.004, 0.12, 0.7, 0.05)

def kick(punch=1.0, dur=0.35):
    t = t_arr(dur)
    f = 45 + 110 * np.exp(-t * 30) * punch
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)

def snare(dur=0.22, rng=None):
    t = t_arr(dur)
    n = rng.standard_normal(len(t)).astype(np.float32)
    n = highpass(n, 1200) * np.exp(-t * 18)
    return 0.7 * n + 0.4 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)

def clap(rng):
    t = t_arr(0.25)
    n = highpass(rng.standard_normal(len(t)).astype(np.float32), 900)
    e = np.exp(-t * 22)
    for off in (0.0, 0.011, 0.022):
        i = int(off * SR); e[i:i + 200] += 0.6
    return n * e * 0.6

def hat(rng, open_=False):
    dur = 0.25 if open_ else 0.05
    t = t_arr(dur)
    n = lowpass(highpass(rng.standard_normal(len(t)).astype(np.float32), 6000), 11000)
    return n * np.exp(-t * (12 if open_ else 70)) * 0.45

def tick():
    t = t_arr(0.04)
    return (np.sin(2 * np.pi * 2600 * t) + 0.5 * np.sin(2 * np.pi * 5200 * t)) * np.exp(-t * 140)

def tom(f, dur=0.6):
    t = t_arr(dur)
    ff = f * (1 + 0.6 * np.exp(-t * 12))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 5)

def boom(rng, dur=2.5):
    t = t_arr(dur)
    low = kick(1.4, dur) * 1.2
    n = lowpass(rng.standard_normal(len(t)).astype(np.float32), 400) * np.exp(-t * 2.5) * 0.8
    return low + n

# ----------------------------------------------------------------- sound effects
def sfx(name, rng):
    if name == "pop":
        t = t_arr(0.09)
        return np.sin(2 * np.pi * (500 + 900 * t / 0.09) * t) * np.exp(-t * 45) * 0.8
    if name == "ding":
        t = t_arr(1.2)
        return (np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 4) + 0.5 * np.sin(2 * np.pi * 1976 * t) * np.exp(-t * 5)) * 0.55
    if name == "whoosh":
        t = t_arr(0.45)
        n = rng.standard_normal(len(t)).astype(np.float32)
        e = np.sin(np.pi * t / 0.45) ** 2
        return (lowpass(n, 1500) * 0.6 + highpass(n, 3000) * 0.25) * e * 0.9
    if name == "tick":
        return tick() * 0.9
    if name == "send":
        t = t_arr(0.18)
        return np.sin(2 * np.pi * (700 + 1400 * t / 0.18) * t) * np.exp(-t * 20) * 0.5
    if name == "receive":
        t = t_arr(0.3)
        return (np.sin(2 * np.pi * 988 * t) * (t < 0.1) + np.sin(2 * np.pi * 1319 * t) * (t >= 0.1)) * np.exp(-t * 9) * 0.45
    if name == "correct":
        t = t_arr(0.6)
        x = np.zeros_like(t)
        for i, n in enumerate((72, 76, 79)):
            s = int(i * 0.08 * SR)
            x[s:] += marimba(note_hz(n), 0.6)[: len(x) - s]
        return x * 0.6
    if name == "wrong":
        t = t_arr(0.4)
        return np.sign(np.sin(2 * np.pi * 150 * t)) * np.exp(-t * 7) * 0.2
    if name == "boom":
        return boom(rng, 1.8) * 0.9
    if name == "riser":
        t = t_arr(1.0)
        n = rng.standard_normal(len(t)).astype(np.float32)
        return highpass(n, 2000) * (t / 1.0) ** 2 * 0.5
    return np.zeros(10, dtype=np.float32)

# ----------------------------------------------------------------- moods
MOODS = {
    #           bpm   root  mode     progressions (scale degrees as chord roots, 0-based)
    "chill":     dict(bpm=(78, 86),  root=(53, 57), minor=False, progs=[[3, 2, 1, 0], [0, 5, 3, 4], [1, 4, 0, 5]], sev=True),
    "upbeat":    dict(bpm=(116, 124), root=(55, 62), minor=False, progs=[[0, 4, 5, 3], [5, 3, 0, 4], [0, 3, 4, 4]], sev=False),
    "tense":     dict(bpm=(92, 100), root=(50, 53), minor=True,  progs=[[0, 0, 5, 4], [0, 5, 0, 6], [0, 1, 0, 6]], sev=False),
    "dramatic":  dict(bpm=(66, 74),  root=(48, 52), minor=True,  progs=[[0, 5, 2, 6], [0, 3, 5, 4], [0, 6, 5, 4]], sev=False),
    "playful":   dict(bpm=(104, 112), root=(57, 62), minor=False, progs=[[0, 3, 4, 0], [0, 5, 3, 4], [3, 4, 0, 0]], sev=False),
    "confident": dict(bpm=(88, 94),  root=(50, 55), minor=True,  progs=[[0, 3, 5, 4], [0, 5, 3, 4], [5, 3, 0, 0]], sev=True),
}
MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]

def mood_bpm(mood, seed=0):
    lo, hi = MOODS[mood]["bpm"]
    return lo + (seed * 7919) % (hi - lo + 1)

def chord_notes(root, scale, deg, sev):
    idx = [deg, deg + 2, deg + 4] + ([deg + 6] if sev else [])
    out = []
    for i in idx:
        out.append(root + scale[i % 7] + 12 * (i // 7))
    return out

def place(buf, x, start_s, gain=1.0, pan=0.0):
    s = int(start_s * SR)
    if s >= buf.shape[1] or s < 0:
        return
    n = min(len(x), buf.shape[1] - s)
    l, r = (1 - max(0, pan)), (1 + min(0, pan))
    buf[0, s:s + n] += x[:n] * gain * l
    buf[1, s:s + n] += x[:n] * gain * r

def render(mood, seconds, seed=0, sfx_events=None, music_on=True):
    """Return float32 stereo array (2, N) for `mood`, `seconds` long. sfx_events: [(time_s, name), ...]"""
    if mood not in MOODS:
        mood = "chill"
    m = MOODS[mood]
    rng = np.random.default_rng(seed)
    bpm = mood_bpm(mood, seed)
    beat = 60.0 / bpm
    lo, hi = m["root"]
    root = int(lo + (seed * 31) % (hi - lo + 1))
    scale = MINOR if m["minor"] else MAJOR
    prog = m["progs"][seed % len(m["progs"])]
    N = int((seconds + 1.5) * SR)
    mus = np.zeros((2, N), dtype=np.float32)
    drm = np.zeros((2, N), dtype=np.float32)
    bar = beat * 4
    nbars = int(seconds / bar) + 2
    arp_pat = [[0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3], [2, 1, 0, 1]][seed % 4]
    snare_s = snare(rng=rng)
    hat_c = hat(rng)
    for b in range(nbars):
        t0 = b * bar
        deg = prog[b % len(prog)]
        ch = chord_notes(root, scale, deg, m["sev"])
        broot = root + scale[deg % 7] - 24
        intro = b == 0  # sparse first bar so the hook lands clean
        if mood == "chill":
            for i, n in enumerate(ch):
                place(mus, epiano(note_hz(n), bar * 1.1), t0 + i * 0.012, 0.16, (i - 1.5) * 0.3)
            for k in (0, 2.5):
                place(mus, bass(note_hz(broot), beat * 1.4, 0.15), t0 + k * beat, 0.35)
            if not intro:
                for k in range(8):
                    sw = 0.06 * beat if k % 2 else 0
                    place(drm, hat_c, t0 + k * beat / 2 + sw, 0.10 if k % 2 else 0.16, 0.2)
                place(drm, kick(0.7), t0, 0.55); place(drm, kick(0.7), t0 + 2.5 * beat, 0.4)
                place(drm, snare_s, t0 + beat, 0.22); place(drm, snare_s, t0 + 3 * beat, 0.22)
        elif mood == "upbeat":
            for k in range(8):
                for i, n in enumerate(ch[:3]):
                    place(mus, pluck(note_hz(n + 12), beat * 0.45, 8), t0 + k * beat / 2, 0.075, (i - 1) * 0.35)
            for k in range(8):
                nn = broot + (12 if k % 2 else 0)
                place(mus, bass(note_hz(nn), beat * 0.45, 0.35), t0 + k * beat / 2, 0.3)
            if not intro:
                for k in range(4):
                    place(drm, kick(1.0), t0 + k * beat, 0.6)
                    place(drm, hat(rng, True), t0 + k * beat + beat / 2, 0.09, -0.2)
                place(drm, clap(rng), t0 + beat, 0.45); place(drm, clap(rng), t0 + 3 * beat, 0.45)
            mel = [ch[arp_pat[k % 4] % len(ch)] + 24 for k in range(4)]
            if b % 2 == 1:
                for k, n in enumerate(mel):
                    place(mus, pluck(note_hz(n), beat * 0.8, 5), t0 + k * beat, 0.05, 0.3)
        elif mood == "tense":
            place(mus, pad(note_hz(ch[0] + 12), bar * 1.05, 0.8, True), t0, 0.07)
            place(mus, pad(note_hz(ch[1] + 24), bar * 1.05, 1.2, True), t0, 0.035)
            for k in range(8):
                place(mus, bass(note_hz(broot + 12), beat * 0.4, 0.5), t0 + k * beat / 2, 0.22)
            for k in range(8):
                place(drm, tick(), t0 + k * beat / 2, 0.12 if k % 2 else 0.2, 0.4)
            if not intro:
                for k in (0, 2):
                    place(drm, kick(0.8), t0 + k * beat, 0.55)
                    place(drm, kick(0.6), t0 + k * beat + 0.18, 0.35)
        elif mood == "dramatic":
            place(mus, pad(note_hz(ch[0]), bar * 1.1, 1.0), t0, 0.1)
            place(mus, pad(note_hz(ch[1] + 12), bar * 1.1, 1.2), t0, 0.06)
            place(mus, pad(note_hz(ch[2] + 12), bar * 1.1, 1.4), t0, 0.05)
            place(mus, bass(note_hz(broot), bar, 0.1), t0, 0.3)
            if b % 2 == 0:
                place(drm, boom(rng), t0, 0.5)
            if not intro:
                for k, f in ((2, 110), (2.5, 95), (3, 80), (3.5, 70)):
                    if b % 2 == 1:
                        place(drm, tom(f), t0 + k * beat, 0.35)
        elif mood == "playful":
            for k in range(8):
                n = ch[arp_pat[k % 4] % len(ch)] + 12
                place(mus, marimba(note_hz(n), beat), t0 + k * beat / 2, 0.22, 0.25 if k % 2 else -0.25)
            for k in (0, 1.5, 2, 3.5):
                place(mus, bass(note_hz(broot + 12), beat * 0.4, 0.2), t0 + k * beat, 0.3)
            if not intro:
                place(drm, kick(0.8), t0, 0.45); place(drm, kick(0.8), t0 + 2 * beat, 0.45)
                place(drm, clap(rng), t0 + beat, 0.3); place(drm, clap(rng), t0 + 3 * beat, 0.3)
                for k in range(4):
                    place(drm, hat_c, t0 + k * beat + beat / 2, 0.1)
        elif mood == "confident":
            for i, n in enumerate(ch):
                place(mus, epiano(note_hz(n), beat * 2.2), t0 + i * 0.01, 0.13, (i - 1.5) * 0.3)
                place(mus, epiano(note_hz(n), beat * 1.6), t0 + 2.5 * beat + i * 0.01, 0.1, (i - 1.5) * 0.3)
            place(mus, bass(note_hz(broot), beat * 1.5, 0.5), t0, 0.4)
            place(mus, bass(note_hz(broot), beat * 0.7, 0.5), t0 + 2.75 * beat, 0.35)
            if not intro:
                place(drm, kick(1.1), t0, 0.7); place(drm, kick(1.1), t0 + 1.75 * beat, 0.5); place(drm, kick(1.1), t0 + 2.5 * beat, 0.6)
                place(drm, snare_s, t0 + beat, 0.45); place(drm, snare_s, t0 + 3 * beat, 0.45)
                for k in range(8):
                    place(drm, hat_c, t0 + k * beat / 2, 0.14 if k % 2 == 0 else 0.08)

    # room reverb on the music bus
    ir_t = t_arr(1.6 if mood in ("dramatic", "tense") else 0.9)
    ir = (rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 4)).astype(np.float32) * 0.02
    for c in range(2):
        mus[c] += fftconvolve(mus[c], ir)[:N].astype(np.float32) * (1.4 if mood == "dramatic" else 0.9)
    mix = mus + drm
    if mood == "chill":  # vinyl crackle + soften
        crack = (rng.random(N) > 0.9993).astype(np.float32) * rng.uniform(-0.25, 0.25, N).astype(np.float32)
        mix += crack * 0.4
        for c in range(2):
            mix[c] = lowpass(mix[c], 6000)
    else:
        for c in range(2):
            mix[c] = lowpass(mix[c], 9000)
    mix = mix[:, : int(seconds * SR)]
    mix /= (np.max(np.abs(mix)) + 1e-6)
    mix *= 0.55 if music_on else 0.0  # music sits under the effects; 0 = effects only (TikTok library track added on top)
    for when, name in sfx_events or []:
        place(mix, sfx(name, rng).astype(np.float32), when, 0.6)
    # fades
    fi, fo = int(0.05 * SR), int(min(1.2, seconds / 4) * SR)
    mix[:, :fi] *= np.linspace(0, 1, fi)
    mix[:, -fo:] *= np.linspace(1, 0, fo)
    peak = np.max(np.abs(mix))
    if peak > 0.95:
        mix *= 0.95 / peak
    return mix

def write_wav(path, stereo):
    data = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())

if __name__ == "__main__":
    mood, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    write_wav(out, render(mood, secs, seed))
    print(f"{mood} {secs}s bpm={mood_bpm(mood, seed)} -> {out}")
