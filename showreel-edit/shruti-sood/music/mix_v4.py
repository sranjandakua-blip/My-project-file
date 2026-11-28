"""Music track v3:
  B0085 instrumental intro (stretched to song A tempo, 4 bars ending on its drum fill)
  -> B0086 0:42.86 (punch-in on the downbeat after the fill)
  -> B0086 lyric line ends ~1:05.8, its drum fill plays, and song B (B0093) lands on the next downbeat
  -> B0093 0:58.37 ... line ends ~1:33.9, stop on the downbeat 1:34.69 + reverb tail."""
import json, numpy as np, soundfile as sf, pyloudnorm as pyln, librosa
from pedalboard import (Pedalboard, HighpassFilter, PeakFilter, HighShelfFilter, LowShelfFilter,
                        Compressor, Limiter, Reverb, Gain)

D = '/tmp/claude-0/-home-user-My-project-file/b8f68f35-e422-5be6-8710-30ffbc413c24/scratchpad/music'
SR = 48000
meter = pyln.Meter(SR)

def load(name):
    y, sr = sf.read(f'{D}/{name}.wav', always_2d=True); assert sr == SR
    return y.T.astype(np.float32)

src = {'B0085': load('B0085_st'), 'B0086': load('B0086'), 'B0093': load('B0093')}
clean = Pedalboard([HighpassFilter(38), LowShelfFilter(90, 1.0), PeakFilter(260, -2.5, 0.9),
                    PeakFilter(3200, 1.5, 0.8), HighShelfFilter(9500, 2.0)])
for n in src: src[n] = clean(src[n], SR)

def sec(n, a, b): return src[n][:, int(round(a * SR)):int(round(b * SR))].copy()

def snap(n, t, win=0.09):
    """Move a beat estimate onto the strongest drum transient within +-win."""
    x = librosa.to_mono(sec(n, t - win - 0.2, t + win + 0.2))
    o = librosa.onset.onset_strength(y=librosa.effects.percussive(x), sr=SR, hop_length=128)
    tt = librosa.frames_to_time(np.arange(len(o)), sr=SR, hop_length=128) + t - win - 0.2
    m = (tt >= t - win) & (tt <= t + win)
    return float(tt[m][np.argmax(o[m])])

def match(x, target=-18.0):
    return x * np.float32(10 ** ((target - meter.integrated_loudness(x.T)) / 20))

def ep(n):
    t = np.linspace(0, np.pi / 2, n, dtype=np.float32); return np.cos(t), np.sin(t)

def tail_of(x, room, seconds):
    return Pedalboard([Reverb(room_size=room, damping=0.4, wet_level=1.0, dry_level=0.0, width=1.0)])(
        np.concatenate([x, np.zeros((2, int(seconds * SR)), np.float32)], 1), SR)

# ---------------- anchor points (source seconds) ----------------
A_IBI, B_IBI = 0.6734, 0.418
T85_IN, T85_END = 3.073, 13.841 - 4 * 0.6734  # v4: 3 bars, ends a bar before 'Everyone, sing with me' (starts ~13.40 stretched)
T86_IN = snap('B0086', 42.86)                  # downbeat in a vocal gap (lines start right after)
T86_NEXT_BAR = snap('B0086', 67.18)            # downbeat the 1:06 drum fill leads into
T86_FADE_END = 66.85                           # before the next vocal pickup at ~66.9
T93_IN = snap('B0093', 58.37)                  # downbeat in a vocal gap
T93_END = snap('B0093', 94.475, 0.05)          # v4: end on the low 'thud' kick (was 1:11.19 in v3)
END_KEEP = 0.20                               # let the thud ring, out before the next downbeat (94.683)
XF1 = 0.08

out = np.zeros((2, int(90 * SR)), np.float32)
def add(x, t0):
    i0 = int(round(t0 * SR)); out[:, i0:i0 + x.shape[1]] += x

# 1) B0085 intro: clean start on the beat, ends where its fill lands
p = match(sec('B0085', T85_IN - 0.01, T85_END))
fi = int(0.012 * SR); p[:, :fi] *= np.linspace(0, 1, fi, dtype=np.float32)
p[:, -int(XF1 * SR):] *= ep(int(XF1 * SR))[0]
add(p, 0.0)
t_j1 = T85_END - T85_IN + 0.01

# 2) B0086: punch-in on its downbeat exactly where B0085's fill lands
a = match(sec('B0086', T86_IN - XF1, T86_FADE_END))
a[:, :int(XF1 * SR)] *= ep(int(XF1 * SR))[1]
fo = int(0.22 * SR); a[:, -fo:] *= ep(fo)[0]          # out during the drum fill, before the next vocal
add(a, t_j1 - XF1)
t_fill_end = t_j1 + (T86_FADE_END - T86_IN)
t_j2 = t_j1 + (T86_NEXT_BAR - T86_IN)                  # where song A's next downbeat would fall
# reverb wash over the last part of the fill so the hand-off never thins out
w = out[:, int((t_fill_end - 0.7) * SR):int(t_fill_end * SR)].copy()
add(tail_of(w, 0.8, 2.5) * np.float32(0.30), t_fill_end - 0.7)

# 3) B0093: rises in over one beat (high-pass sweep) and its downbeat lands on song A's next downbeat
pre = int(B_IBI * SR)
b = match(sec('B0093', T93_IN - B_IBI, T93_END + END_KEEP))
hp = HighpassFilter(1500); blk = 480; sw = np.zeros_like(b[:, :pre])
for i in range(0, pre, blk):
    j = min(i + blk, pre); hp.cutoff_frequency_hz = float(1500 * (30 / 1500) ** (i / pre))
    sw[:, i:j] = hp(b[:, i:j], SR, reset=False)
b[:, :pre] = sw * (np.sin(np.linspace(0, np.pi / 2, pre, dtype=np.float32)) ** 2)
fo2 = int(0.12 * SR); b[:, -fo2:] *= np.cos(np.linspace(0, np.pi / 2, fo2, dtype=np.float32))
add(b, t_j2 - B_IBI)
t_end_hit = t_j2 + (T93_END - T93_IN)

# 4) ending: stop on the downbeat after the last line, long reverb tail
last = out[:, int((t_end_hit - 0.05) * SR):int((t_end_hit + END_KEEP) * SR)].copy()
tl = tail_of(last, 0.8, 3.0); n15 = int(1.2 * SR)
tl[:, -n15:] *= np.linspace(1, 0, n15, dtype=np.float32)
add(tl * np.float32(0.35), t_end_hit - 0.05)
total = t_end_hit + 2.8
out = out[:, :int(total * SR)]

# ---------------- master ----------------
out = Pedalboard([Compressor(threshold_db=-20, ratio=2.5, attack_ms=12, release_ms=140), Gain(2.0)])(out, SR)
out *= np.float32(10 ** ((-14.0 - meter.integrated_loudness(out.T)) / 20))
out = Pedalboard([Limiter(threshold_db=-1.2, release_ms=80)])(out, SR)
out *= np.float32(10 ** ((-14.0 - meter.integrated_loudness(out.T)) / 20))
out = np.clip(out, -0.89, 0.89)
sf.write(f'{D}/track_v4.wav', out.T, SR, subtype='PCM_24')

info = dict(total=total,
            joins=dict(j1_85_to_86=t_j1, lyricA_end=t_j1 + (65.8 - T86_IN), j2_songB_downbeat=t_j2, end_hit=t_end_hit),
            segments={'B0085': [0.0, t_j1], 'B0086': [t_j1, t_fill_end], 'B0093': [t_j2, t_end_hit]},
            anchors=dict(T86_IN=T86_IN, T86_NEXT_BAR=T86_NEXT_BAR, T93_IN=T93_IN, T93_END=T93_END))
json.dump(info, open(f'{D}/track_v4.json', 'w'), indent=1)
print(json.dumps(info, indent=1))
print('LUFS', round(meter.integrated_loudness(out.T), 2), 'peak dBFS', round(20 * np.log10(np.abs(out).max()), 2))
