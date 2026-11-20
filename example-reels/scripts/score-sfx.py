"""Soft score and paper/stamp effects for the Din Firmaadresse film ("Your post, handled.").

Marimba, plucked bass, a warm pad, shaker and soft kick at 120 BPM; effects are paper,
wood and rubber stamp, not 8-bit. Every event time mirrors compositions/film.html.
Writes a 48 kHz stereo WAV. Usage: python score.py <out.wav>
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 14.0
N = int(SR * DUR)
rng = np.random.default_rng(11)

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i] * gain
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i : i + len(sig), 0] += sig * left * 1.414
    buf[i : i + len(sig), 1] += sig * right * 1.414


def env(dur, attack=0.003, decay=8.0):
    x = tt(dur)
    e = np.exp(-x * decay) * np.minimum(1, x / attack)
    return e * np.clip((dur - x) / 0.01, 0, 1)


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def bp(sig, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), sig)


def lp(sig, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), sig)


def hp(sig, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), sig)


def sine(freq, dur):
    f = np.broadcast_to(freq, tt(dur).shape)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def sweep(f0, f1, dur, curve=1.0):
    u = tt(dur) / dur
    return f0 * (f1 / f0) ** (u**curve)


# ---------------- instruments ----------------
def marimba(n, dur=0.9, bright=1.0):
    f = hz(n)
    x = tt(dur)
    s = np.sin(2 * np.pi * f * x) * np.exp(-x * 5.5)
    s += 0.22 * bright * np.sin(2 * np.pi * 3.93 * f * x) * np.exp(-x * 22)
    s += 0.06 * bright * np.sin(2 * np.pi * 9.2 * f * x) * np.exp(-x * 45)
    click = lp(noise(0.006), 3000) * env(0.006, 0.0005, 300)
    s[: len(click)] += 0.15 * click
    return s * np.minimum(1, x / 0.002) * np.clip((dur - x) / 0.02, 0, 1)


def bass(n, dur=0.45):
    f = hz(n)
    x = tt(dur)
    s = np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x) * np.exp(-x * 8)
    return lp(s, 900) * env(dur, 0.005, 4.5)


def pad(notes, dur):
    x = tt(dur)
    s = np.zeros_like(x)
    for n in notes:
        for det in (-0.06, 0.06):
            ph = 2 * np.pi * hz(n + det) * x
            s += np.sin(ph) + 0.25 * np.sin(2 * ph)
    s = lp(s / len(notes), 1400)
    a = np.minimum(1, x / 0.35) * np.clip((dur - x) / 0.4, 0, 1)
    return s * a


def kick(t, g=0.5):
    add(music, t, sine(sweep(110, 42, 0.22), 0.22) * env(0.22, 0.002, 13), g)


def shaker(t, g=0.07, pan=0.3):
    add(music, t, hp(noise(0.05), 5000) * env(0.05, 0.008, 60), g, pan)


def rim(t, g=0.12):
    s = bp(noise(0.04), 1500, 4000) * env(0.04, 0.0005, 90)
    s += 0.5 * np.sin(2 * np.pi * 1700 * tt(0.04)) * env(0.04, 0.0005, 120)
    add(music, t, s, g, -0.1)


# ---------------- music ----------------
BEAT = 0.5
# bar start -> (bass root, chord)
CHORDS = {2.0: (41, [65, 69, 72]), 4.0: (43, [67, 71, 74]), 6.0: (45, [69, 72, 76]), 8.0: (41, [65, 69, 72]), 10.0: (43, [67, 71, 74])}

# Intro 0-2 s: shaker and a quiet marimba arpeggio (F).
for k in range(8):
    shaker(k * 0.25, 0.035 if k % 2 else 0.05)
for k, n in enumerate([65, 69, 72, 77, 72, 69]):
    add(music, 1.0 + k * 0.166, marimba(n, 0.5, 0.6), 0.05, -0.25 + k * 0.1)

for bar, (root, tones) in CHORDS.items():
    add(music, bar, pad([n - 12 for n in tones], 2.05), 0.05)
    for b in range(4):
        t = bar + b * BEAT
        if bar == 10.0 and b >= 1:
            break  # the leap home: groove drops out
        if b % 2 == 0:
            kick(t, 0.42)
        else:
            rim(t, 0.09)
        for h in range(2):
            shaker(t + h * 0.25, 0.05 if h else 0.035)
        add(music, t, bass(root + (7 if b == 2 else 0)), 0.32)
        # Marimba pattern on eighths.
        for e in range(2):
            n = tones[(b * 2 + e) % 3] + (12 if (b * 2 + e) % 4 == 3 else 0)
            add(music, t + e * 0.25, marimba(n, 0.5, 0.8), 0.06, -0.3 + 0.2 * e)

# 10.45-11.0: the leap home, soft rising swell.
sw = lp(noise(0.55), 1800) * np.linspace(0, 1, int(0.55 * SR)) ** 2
add(music, 10.45, sw, 0.18)
add(music, 10.45, sine(sweep(300, 900, 0.55), 0.55) * np.linspace(0, 1, int(0.55 * SR)) ** 2, 0.03)

# 11.0: home. C major chord rings out on marimba, pad and bass.
for k, (n, pan) in enumerate([(60, -0.3), (64, 0.3), (67, -0.1), (72, 0.1)]):
    add(music, 11.0 + k * 0.02, marimba(n, 2.6, 0.9), 0.09, pan)
add(music, 11.0, pad([48, 55, 60, 64], 3.0), 0.12)
add(music, 11.0, bass(36, 2.0), 0.35)
kick(11.0, 0.45)

# ---------------- effects ----------------
def knock(t, g=0.4):
    s = marimba(52, 0.12, 0.3) * env(0.12, 0.001, 30)
    s[: int(0.004 * SR)] += lp(noise(0.004), 2500) * 0.6
    add(sfx, t, s, g)


def whoop(t, f0=260, f1=560, dur=0.16, g=0.05):
    add(sfx, t, sine(sweep(f0, f1, dur), dur) * env(dur, 0.01, 12), g)


def land(t, g=0.32):
    """Soft paper thump."""
    s = sine(sweep(140, 60, 0.12), 0.12) * env(0.12, 0.001, 28)
    puff = bp(noise(0.08), 300, 2000) * env(0.08, 0.002, 40)
    s[: len(puff)] += 0.45 * puff
    add(sfx, t, s, g)


def paper(t, dur=0.18, g=0.12, pan=0.0):
    """Paper flap or swish."""
    s = bp(noise(dur), 1200, 6000) * np.hanning(int(dur * SR)) ** 0.7
    add(sfx, t, s, g, pan)


def key(t, g=0.09, pan=0.0):
    s = bp(noise(0.018), 2000, 7000) * env(0.018, 0.0005, 220)
    add(sfx, t, s, g, pan)


def chime(t, n, g=0.07, pan=0.0, dur=0.8):
    x = tt(dur)
    s = (np.sin(2 * np.pi * hz(n) * x) + 0.3 * np.sin(2 * np.pi * hz(n) * 2.76 * x) * np.exp(-x * 6)) * np.exp(-x * 4.5)
    add(sfx, t, s * np.minimum(1, x / 0.002), g, pan)


HOPS = [(0.95, 1.4), (1.5, 2.0), (2.1, 2.5), (2.6, 3.0), (3.5, 4.0), (4.1, 4.5), (4.6, 5.0), (5.1, 5.5), (5.6, 6.0),
        (6.1, 6.5), (7.6, 8.0), (8.1, 8.5), (8.6, 9.0), (9.5, 10.0), (10.45, 11.0)]
for i, (t0, t1) in enumerate(HOPS):
    whoop(t0, 240 + 20 * (i % 3), 520 + 40 * (i % 4), 0.16, 0.045)
    if t1 not in (2.0, 4.0, 9.0, 11.0):  # those get their own hits
        land(t1, 0.26)

# Knocks against the tab; eyes open.
knock(0.25)
knock(0.75)

# 1.93: crash through the loading card: paper crumple and falling letter ticks.
for k in range(7):
    paper(1.93 + k * 0.035, 0.09, 0.14, rng.uniform(-0.6, 0.6))
land(1.97, 0.4)
for k in range(8):
    add(sfx, 1.98 + rng.uniform(0, 0.4), marimba(int(rng.choice([84, 86, 88, 91, 93])), 0.25, 1.0), 0.03, rng.uniform(-0.7, 0.7))

# Typing the email, then the password dots.
for i in range(26):
    key(2.5 + i * 0.018, 0.07, rng.uniform(-0.3, 0.3))
for i in range(10):
    key(3.0 + i * 0.035, 0.06, 0.1)

# 4.0: stomp on Log in: deep press, then the dashboard opens with a swish.
add(sfx, 4.0, sine(sweep(120, 38, 0.4), 0.4) * env(0.4, 0.002, 7), 0.6)
add(sfx, 4.0, bp(noise(0.06), 400, 2500) * env(0.06, 0.001, 50), 0.25)
paper(4.02, 0.4, 0.10)
for k, n in enumerate([72, 76, 79]):
    chime(4.05 + k * 0.05, n, 0.035, -0.2 + 0.2 * k)

# Nav clicks.
for t in (4.5, 8.0):
    key(t, 0.16)

# Letters land, one per beat: paper flap + rising marimba.
for t, n in [(5.0, 79), (5.5, 81), (6.0, 84)]:
    paper(t - 0.1, 0.14, 0.12)
    add(sfx, t + 0.12, marimba(n, 0.6, 1.0), 0.07, 0.3)

# 6.6-7.0: the scanner passes over the hero: hum + sweep, then a done-beep.
x = tt(0.42)
hum = (np.sin(2 * np.pi * 110 * x) + 0.4 * np.sin(2 * np.pi * 220 * x)) * np.hanning(len(x))
add(sfx, 6.6, hum, 0.07)
add(sfx, 6.6, bp(noise(0.42), 800, 3000) * np.hanning(len(x)), 0.06)
chime(7.0, 88, 0.06)
chime(7.08, 93, 0.05)
add(sfx, 7.7, marimba(86, 0.4, 1.0), 0.05, 0.3)  # its pill pops

# Panel switch to invoices.
paper(8.02, 0.12, 0.08, -0.3)

# 9.0: the rubber stamp: low thud, rubber slap, then the Paid chime.
add(sfx, 9.0, sine(sweep(95, 45, 0.3), 0.3) * env(0.3, 0.001, 10), 0.75)
slap = bp(noise(0.05), 250, 1800) * env(0.05, 0.0008, 70)
add(sfx, 9.0, slap, 0.45)
add(sfx, 9.0, marimba(45, 0.2, 0.2), 0.12)
chime(9.06, 84, 0.06, -0.2)
chime(9.14, 91, 0.06, 0.2)

# 10.0-10.24: three status checks.
for k, n in enumerate([79, 84, 88]):
    chime(10.0 + k * 0.12, n, 0.06, -0.3 + 0.3 * k, 0.6)

# 11.0: back in the tab: click and the green badge pop.
key(11.0, 0.2)
chime(11.02, 96, 0.03)

# End line words and the arrow.
for i, n in enumerate([72, 76, 79]):
    add(sfx, 11.55 + i * 0.15, marimba(n + 12, 0.7, 1.0), 0.06, -0.2 + 0.2 * i)
land(12.35 + 0.15, 0.12)

# ---------------- mix ----------------
# Effects only: the music was dropped after review; add a track in the Reels editor.
MUSIC = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
mix = music * MUSIC + sfx
mix[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
fade = int(1.3 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
peak = np.max(np.abs(mix))
mix = mix / peak * 0.89
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print("wrote", sys.argv[1], "peak", round(float(peak), 3))
