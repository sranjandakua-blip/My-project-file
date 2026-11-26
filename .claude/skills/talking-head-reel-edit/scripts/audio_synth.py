"""Synthesised SFX + music bed (no third-party audio needed).
  python3 -I audio_synth.py sfx <out_dir>
  python3 -I audio_synth.py music <out.wav> <duration> <full_from> <drop1,drop2,...> [bpm]
"""
import sys, numpy as np, wave
from scipy import signal
SR = 48000
rng = np.random.default_rng(3)


def write(path, x, stereo=False):
    x = np.asarray(x, np.float32)
    if not stereo: x = np.stack([x, x], 1)
    x = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())


def env(n, a, d, shape=4.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-shape * np.maximum(0, t - a) / max(d, 1e-4))
    return e


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band'); return signal.lfilter(b, a, x)


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2)); return signal.lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)


def sweep(f0, f1, n, curve='exp'):
    f = f0 * (f1 / f0) ** np.linspace(0, 1, n) if curve == 'exp' else np.linspace(f0, f1, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def norm(x, peak=0.9): return x / (np.abs(x).max() + 1e-9) * peak


def sfx(out):
    # whoosh: band-passed noise whose centre sweeps up then down, swelling envelope
    n = int(0.5 * SR); nz = rng.normal(0, 1, n); y = np.zeros(n)
    cs = np.concatenate([np.geomspace(350, 3200, n // 2), np.geomspace(3200, 700, n - n // 2)])
    for k in range(0, n, 1200):
        c = cs[k]; seg = bp(nz[max(0, k - 2400):k + 1200], c * .6, min(c * 1.6, 20000))[-(min(1200, n - k)):]
        y[k:k + len(seg)] = seg
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    write(f'{out}/whoosh.wav', norm(y * e, .8))
    # pop
    n = int(0.12 * SR); y = sweep(950, 320, n) * env(n, .002, .05, 3) + rng.normal(0, .25, n) * env(n, .0005, .004)
    write(f'{out}/pop.wav', norm(y, .8))
    # bass impact / boom
    n = int(1.6 * SR); y = sweep(120, 38, n) * env(n, .003, .55, 3.2)
    y += lp(rng.normal(0, 1, n), 900) * env(n, .001, .12, 4) * .8
    tail = lp(rng.normal(0, 1, n), 400) * env(n, .02, .9, 3) * .15
    write(f'{out}/boom.wav', norm(y + tail, .95))
    # error buzz: two short square pulses
    n1 = int(.14 * SR); g = int(.06 * SR); t = np.arange(n1) / SR
    p = (signal.square(2 * np.pi * 140 * t) * .6 + signal.square(2 * np.pi * 283 * t) * .4) * env(n1, .004, .2, 1)
    p = lp(p, 2500); y = np.concatenate([p, np.zeros(g), p])
    write(f'{out}/buzz.wav', norm(y, .7))
    # typing: random key clicks
    n = int(1.4 * SR); y = np.zeros(n); tt = 0.03
    while tt < 1.3:
        k = int(tt * SR); m = int(.03 * SR); c = bp(rng.normal(0, 1, m), 1800, 6000) * env(m, .0005, .008, 2)
        c += bp(rng.normal(0, 1, m), 300, 900) * env(m, .0005, .01, 2) * .6
        y[k:k + m] += c * rng.uniform(.6, 1); tt += rng.uniform(.06, .13)
    write(f'{out}/typing.wav', norm(y, .6))
    # riser
    n = int(1.2 * SR); nz = rng.normal(0, 1, n); y = np.zeros(n)
    for k in range(0, n, 2400):
        f = 300 * (12 ** (k / n)); seg = hp(nz[k:k + 2400], f); y[k:k + len(seg)] = seg
    y = y * np.linspace(0, 1, n) ** 2.2 + sweep(200, 900, n) * np.linspace(0, 1, n) ** 3 * .25
    write(f'{out}/riser.wav', norm(y, .6))
    # chime (approved / success)
    n = int(1.2 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for i, f in enumerate([1046.5, 1318.5, 1568.0]):
        d = int(i * .07 * SR); s = np.sin(2 * np.pi * f * t[:n - d]) * env(n - d, .003, .5, 4); y[d:] += s
    write(f'{out}/chime.wav', norm(y, .6))
    print('sfx done')


# ---------------- music ----------------
def music(out, dur, full_from, drops, bpm=104.0):
    beat = 60 / bpm; bar = 4 * beat; N = int((dur + 1) * SR)
    L = np.zeros(N); R = np.zeros(N)
    chords = [(110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 220.0, 261.63]),   # Am  F
              (130.81, [196.0, 261.63, 329.63]), (98.0, [196.0, 246.94, 293.66])]  # C   G

    def add(buf, x, t, g=1.0):
        k = int(t * SR)
        if k >= N or k < 0: return
        m = min(len(x), N - k); buf[k:k + m] += x[:m] * g

    def kick():
        n = int(.35 * SR); return sweep(150, 45, n) * env(n, .001, .16, 3) + rng.normal(0, .15, n) * env(n, .0005, .004)

    def clap():
        n = int(.25 * SR); return bp(rng.normal(0, 1, n), 900, 4000) * env(n, .001, .08, 3)

    def hat(open_=False):
        n = int((.18 if open_ else .05) * SR); return hp(rng.normal(0, 1, n), 7000) * env(n, .0005, .03 if not open_ else .1, 3)

    def pluck(f, d=.28):
        n = int(d * SR); t = np.arange(n) / SR
        x = signal.sawtooth(2 * np.pi * f * t) * .5 + np.sin(2 * np.pi * f * t)
        return lp(x * env(n, .002, d * .5, 3), 2600)

    def bass(f, d):
        n = int(d * SR); t = np.arange(n) / SR
        x = signal.sawtooth(2 * np.pi * f * t) * .6 + np.sin(2 * np.pi * f * t)
        return lp(x * env(n, .005, d * .8, 1.5), 420)

    def pad(fs, d):
        n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for f in fs:
            for det in (-0.12, 0.0, 0.11):
                x += signal.sawtooth(2 * np.pi * f * (1 + det / 100 * 6) * t + rng.uniform(0, 6))
        a = np.minimum(1, t / .35) * np.minimum(1, (d - t) / .3)
        return lp(x * a, 1100) / (len(fs) * 3)

    drop_set = sorted(drops)
    def muted(t):   # one beat of silence (except pad) right before each drop
        return any(d - beat <= t < d for d in drop_set)

    nbars = int(dur / bar) + 2
    for b in range(nbars):
        t0 = b * bar; root, tri = chords[b % 4]
        add(L, pad(tri, bar), t0, .22); add(R, pad([f * 1.003 for f in tri], bar), t0, .22)
        full = t0 >= full_from - 1e-6
        for s in range(16):               # 16th grid
            t = t0 + s * beat / 4
            if muted(t) or t > dur: continue
            if s % 4 == 0 and (full or s % 8 == 0): add(L, kick(), t, .9); add(R, kick(), t, .9)
            if full and s in (4, 12): add(L, clap(), t, .35); add(R, clap(), t, .35)
            if s % 4 == 2: add(L, hat(), t, .16); add(R, hat(), t, .12)
            if full and s % 2 == 1: add(R, hat(), t, .06)
            if s % 2 == 0:
                bf = root if s % 4 == 0 else root * 2
                if full or s % 8 == 0: add(L, bass(bf, beat / 2 * .95), t, .45); add(R, bass(bf, beat / 2 * .95), t, .45)
            arp = [tri[0], tri[1], tri[2], tri[1] * 2]
            if s % 2 == 0 or full:
                f = arp[s % 4] * (2 if (s // 4) % 2 else 1)
                g = .16 if full else .11
                add(L, pluck(f), t, g * (1.0 if s % 2 == 0 else .7)); add(R, pluck(f), t + .012, g * (.8 if s % 2 == 0 else .9))
    # crash + sub on each drop
    for d in drop_set:
        n = int(1.8 * SR); cr = hp(rng.normal(0, 1, n), 4500) * env(n, .001, .7, 3)
        add(L, cr, d, .22); add(R, hp(rng.normal(0, 1, n), 4500) * env(n, .001, .7, 3), d, .22)
    # sidechain-style pump from the kick grid
    t = np.arange(N) / SR; ph = (t % beat) / beat
    pump = 1 - .35 * np.exp(-ph * 9) * (t >= full_from)
    x = np.stack([L * pump, R * pump], 1)
    x[:int(.05 * SR)] *= np.linspace(0, 1, int(.05 * SR))[:, None]
    fo = int(1.2 * SR); e = int(dur * SR); x[e - fo:e] *= np.linspace(1, 0, fo)[:, None]; x[e:] = 0
    x = x[:e]
    write(out, norm(x, .85), stereo=True)
    print('music', out, dur)


if __name__ == '__main__':
    if sys.argv[1] == 'sfx': sfx(sys.argv[2])
    else:
        drops = [float(v) for v in sys.argv[5].split(',') if v]
        music(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), drops, float(sys.argv[6]) if len(sys.argv) > 6 else 104.0)
