"""Chiptune score and sound effects for the favicon film.

Every event time below mirrors compositions/film.html (120 BPM, beat = 0.5 s).
Writes a 48 kHz stereo WAV. Usage: python score.py <out.wav>
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 13.5
N = int(SR * DUR)
rng = np.random.default_rng(7)

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def note_hz(n):
    """MIDI note to Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    left = np.cos((pan + 1) * np.pi / 4)
    right = np.sin((pan + 1) * np.pi / 4)
    buf[i : i + len(sig), 0] += sig * left * 1.414
    buf[i : i + len(sig), 1] += sig * right * 1.414


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env(dur, attack=0.004, decay=8.0):
    x = tt(dur)
    e = np.exp(-x * decay)
    a = np.minimum(1, x / attack)
    tail = np.minimum(1, (dur - x) / 0.01)
    return e * a * np.clip(tail, 0, 1)


def pulse(freq, dur, duty=0.5):
    """Pulse wave; freq may be an array for sweeps."""
    x = tt(dur)
    f = np.broadcast_to(freq, x.shape)
    phase = np.cumsum(f) / SR
    return np.where((phase % 1) < duty, 1.0, -1.0)


def tri(freq, dur):
    x = tt(dur)
    f = np.broadcast_to(freq, x.shape)
    phase = np.cumsum(f) / SR
    return 4 * np.abs((phase % 1) - 0.5) - 1


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def lp(sig, hz):
    return sosfilt(butter(2, hz, "low", fs=SR, output="sos"), sig)


def hp(sig, hz):
    return sosfilt(butter(2, hz, "high", fs=SR, output="sos"), sig)


def sweep(f0, f1, dur, curve=1.0):
    u = tt(dur) / dur
    return f0 * (f1 / f0) ** (u**curve)


# ---------------- music ----------------
BEAT = 0.5
CHORDS = {  # bar start -> (bass root, chord tones)
    2.0: (41, [65, 69, 72]),  # F
    4.0: (43, [67, 71, 74]),  # G
    6.0: (45, [69, 72, 76]),  # Am
    8.0: (48, [72, 76, 79]),  # C
}

# Intro: soft hats and a quiet arpeggio on F before the drop.
for k in range(16):
    t = k * 0.125
    add(music, t, hp(noise(0.03), 7000) * env(0.03, decay=90), 0.10 if k % 2 else 0.05, 0.3)
for k, n in enumerate([65, 69, 72, 77, 72, 69, 65, 69]):
    add(music, 1.0 + k * 0.125, pulse(note_hz(n), 0.11, 0.125) * env(0.11, decay=18), 0.035, -0.2)

for bar, (root, tones) in CHORDS.items():
    for b in range(4):
        t = bar + b * BEAT
        # Kick on 1 and 3, snare on 2 and 4.
        if b % 2 == 0:
            add(music, t, np.sin(2 * np.pi * np.cumsum(sweep(150, 45, 0.18)) / SR) * env(0.18, decay=14), 0.55)
        else:
            add(music, t, hp(noise(0.14), 1500) * env(0.14, decay=22), 0.22, 0.1)
        # Hats on eighths.
        for h in range(2):
            add(music, t + h * 0.25, hp(noise(0.03), 8000) * env(0.03, decay=90), 0.09, 0.3)
        # Triangle bass: root, octave on the off-beat.
        add(music, t, tri(note_hz(root), 0.22) * env(0.22, decay=5), 0.30)
        add(music, t + 0.25, tri(note_hz(root + 12), 0.2) * env(0.2, decay=6), 0.22)
        # 16th arpeggio, 25% pulse, kept under the effects.
        for s in range(4):
            n = tones[(b * 4 + s) % 3] + (12 if s == 3 else 0)
            add(music, t + s * 0.125, pulse(note_hz(n), 0.1, 0.25) * env(0.1, decay=20), 0.035, -0.25)

# 10.0-10.75: the leap back. Riser instead of the groove.
add(music, 10.0, lp(pulse(sweep(220, 880, 0.75, 1.5), 0.75, 0.5), 3000) * np.linspace(0.2, 1, int(0.75 * SR)), 0.06)

# 10.75: landing in the tab. C major stab, then the chord rings out.
for n, pan in [(48, 0), (60, -0.3), (64, 0.3), (67, -0.1), (72, 0.1)]:
    ring = pulse(note_hz(n), 2.7, 0.25 if n > 50 else 0.5) * env(2.7, attack=0.002, decay=1.3)
    add(music, 10.75, lp(ring, 4000), 0.07 if n > 50 else 0.12, pan)
add(music, 10.75, np.sin(2 * np.pi * np.cumsum(sweep(150, 40, 0.3)) / SR) * env(0.3, decay=9), 0.5)
for k, n in enumerate([72, 76, 79, 84, 79, 84, 88]):
    add(music, 11.0 + k * 0.125, pulse(note_hz(n), 0.12, 0.125) * env(0.12, decay=16), 0.04, 0.2)

# ---------------- effects ----------------
def knock(t):
    s = tri(sweep(260, 120, 0.06), 0.06) * env(0.06, decay=40)
    click = hp(noise(0.01), 2000) * env(0.01, attack=0.0005, decay=200)
    s[: len(click)] += 0.4 * click
    add(sfx, t, s, 0.45)


def boing(t, f0=180, f1=640, dur=0.16, gain=0.16):
    f = sweep(f0, f1, dur) * (1 + 0.04 * np.sin(2 * np.pi * 30 * tt(dur)))
    add(sfx, t, pulse(f, dur, 0.5) * env(dur, decay=10), gain)


def pomf(t, gain=0.4):
    thump = np.sin(2 * np.pi * np.cumsum(sweep(130, 55, 0.09)) / SR) * env(0.09, decay=30)
    puff = lp(noise(0.08), 900) * env(0.08, decay=35)
    thump[: len(puff)] += 0.6 * puff
    add(sfx, t, thump, gain)


def tick(t, gain=0.12, pan=0.0):
    add(sfx, t, hp(noise(0.012), 3000) * env(0.012, attack=0.0005, decay=300), gain, pan)


def blip(t, n, dur=0.06, gain=0.08, duty=0.25, pan=0.0):
    add(sfx, t, pulse(note_hz(n), dur, duty) * env(dur, decay=30), gain, pan)


# Knocks inside the tab, eyes open.
knock(0.25)
knock(0.75)
add(sfx, 1.0, pulse(sweep(600, 1300, 0.07), 0.07, 0.25) * env(0.07, decay=25), 0.08)

HOPS = [(1.5, 2.0), (2.5, 3.0), (3.5, 4.0), (4.5, 5.0), (5.5, 6.0), (6.1, 6.5), (6.6, 7.0), (7.5, 8.0), (9.0, 9.5), (10.05, 10.75)]
for i, (t0, t1) in enumerate(HOPS):
    if i == 9:
        boing(t0, 160, 900, 0.3, 0.18)
        add(sfx, t0, lp(noise(0.6), 2500) * np.hanning(int(0.6 * SR)), 0.2)
        continue
    boing(t0, 170 + 15 * (i % 3), 600 + 40 * (i % 4))
    if i not in (3,):
        pomf(t1)

# Crash through the placeholder.
add(sfx, 1.93, hp(noise(0.45), 1200) * env(0.45, decay=9), 0.32)
for k in range(9):
    blip(1.93 + rng.uniform(0, 0.3), int(rng.choice([84, 88, 91, 96, 100])), 0.05, 0.05, 0.125, rng.uniform(-0.7, 0.7))

# Typing lines 1-2, drop of line 3.
for i in range(26):
    tick(3.0 + i * 0.018, 0.10, rng.uniform(-0.3, 0.3))
for i, n in enumerate([72, 74, 76, 79, 81, 79, 76, 74, 72, 74, 76, 79, 81, 84, 81, 84]):
    blip(4.0 + i * 0.022 + 0.1, n, 0.05, 0.05, 0.5, -0.4 + i * 0.05)

# Ground pound: boom and a dither crackle.
add(sfx, 5.0, np.sin(2 * np.pi * np.cumsum(sweep(110, 32, 0.45)) / SR) * env(0.45, decay=6), 0.75)
add(sfx, 5.0, lp(noise(0.2), 2500) * env(0.2, decay=18), 0.3)
for k in range(70):
    t = 5.0 + rng.uniform(0, 0.5)
    add(sfx, t, np.sign(noise(0.006)) * env(0.006, decay=200), 0.05, rng.uniform(-0.8, 0.8))

# Project rows light: rising dings.
for t, n in [(6.0, 84), (6.5, 88), (7.0, 91)]:
    blip(t + 0.01, n, 0.35, 0.09, 0.125)
    blip(t + 0.01, n + 12, 0.2, 0.03, 0.5)

# Orange flood, the question typing, the outline zap.
add(sfx, 8.0, hp(noise(0.45), 400) * np.hanning(int(0.45 * SR)), 0.12)
for i in range(26):
    tick(8.25 + i * 0.012, 0.06, rng.uniform(-0.3, 0.3))
for t in (8.9, 8.98):
    add(sfx, t, pulse(sweep(1400, 300, 0.05), 0.05, 0.5) * env(0.05, decay=30), 0.07)

# Skyline rises in steps; windows light up.
for k in range(8):
    blip(9.0 + k * 0.04, 48 + [0, 4, 7, 12, 16, 19, 24, 28][k], 0.05, 0.07, 0.5)
for k in range(28):
    blip(9.5 + k * 0.017, int(rng.choice([84, 86, 88, 91, 93, 96])), 0.06, 0.035, 0.125, rng.uniform(-0.8, 0.8))

# Back in the tab: a click and a pop.
tick(10.75, 0.3)
add(sfx, 10.76, pulse(sweep(700, 1600, 0.08), 0.08, 0.25) * env(0.08, decay=20), 0.1)

# End line words and the arrow.
for i in range(5):
    blip(11.05 + i * 0.1, [72, 76, 79, 84, 88][i], 0.07, 0.06, 0.25)
for k, d in enumerate([0.0, 0.15, 0.27]):
    pomf(11.9 + d + 0.12, 0.25 / (k + 1))

# ---------------- mix ----------------
mix = music * 0.8 + sfx
mix[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
fade = int(1.2 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
peak = np.max(np.abs(mix))
mix = mix / peak * 0.89
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print("wrote", sys.argv[1], "peak", round(float(peak), 3))
