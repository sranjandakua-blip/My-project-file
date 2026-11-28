"""Build the showreel music track from live camera audio:
B0085 (instrumental intro, stretched to match) -> B0084 -> B0086 (song A ending) -> B0093 (song B).
All joins are on downbeats; same-song joins are beat-locked equal-power crossfades,
the song change rises out of song A's ring-out with a high-pass sweep + reverb tail."""
import json, numpy as np, soundfile as sf, pyloudnorm as pyln, librosa
from pedalboard import (Pedalboard, HighpassFilter, PeakFilter, HighShelfFilter, LowShelfFilter,
                        Compressor, Limiter, Reverb, Gain)

D = '/tmp/claude-0/-home-user-My-project-file/b8f68f35-e422-5be6-8710-30ffbc413c24/scratchpad/music'
SR = 48000
STRETCH = 0.6385 / 0.6734          # B0085 tempo factor (rubberband), t' = t / STRETCH
meter = pyln.Meter(SR)

def load(name):
    y, sr = sf.read(f'{D}/{name}.wav', always_2d=True); assert sr == SR
    return y.T.astype(np.float32)                      # (2, n)

src = {n: load(n) for n in ['B0084', 'B0086', 'B0093']}
src['B0085'] = load('B0085_st')

# ---- per-source cleanup EQ (camera mic: rumble, boxy low-mids, dull top) ----
clean = Pedalboard([HighpassFilter(38), LowShelfFilter(90, 1.0), PeakFilter(260, -2.5, 0.9),
                    PeakFilter(3200, 1.5, 0.8), HighShelfFilter(9500, 2.0)])
for n in src: src[n] = clean(src[n], SR)

def sec(n, a, b):                                       # slice in seconds
    return src[n][:, int(round(a * SR)):int(round(b * SR))]

def onset_env(x):
    m = librosa.to_mono(x)
    return librosa.onset.onset_strength(y=librosa.effects.percussive(m), sr=SR, hop_length=240)

def refine(n_out, t_out, n_in, t_in, search=0.34):
    """Nudge t_in so the incoming beat transients line up with the outgoing ones (+-search s)."""
    w = 8.0
    eo = onset_env(sec(n_out, t_out - w, t_out + 0.3))
    ei = onset_env(sec(n_in, t_in - w, t_in + 0.3))
    L = min(len(eo), len(ei)); eo, ei = eo[:L] - eo[:L].mean(), ei[:L] - ei[:L].mean()
    hop = 240 / SR; best, bk = -1e9, 0
    for k in range(-int(search / hop), int(search / hop) + 1):
        c = np.dot(eo[max(0, k):L + min(0, k)], ei[max(0, -k):L - max(0, k)])
        if c > best: best, bk = c, k
    return t_in - bk * hop

# ---- segment plan (source seconds) ----
T85_END = 13.841                    # B0085 (stretched): beat after its drum fill
T84_IN, T84_OUT = 88.237, 99.08     # big kick+snare hit -> bar line between sung lines
T86_IN, T86_HIT, T86_END = 59.12, 80.64, 82.60   # 8 bars into the final hit + natural ring-out
T93_IN, T93_HIT = 97.96, 118.19     # 12 bars of song B, ends on a downbeat
XF = 0.6734                          # one-beat crossfade for the beat-locked join 2
XF1 = 0.08                           # join 1 is a punch-in on the hit after the fill

T86_IN = refine('B0084', T84_OUT, 'B0086', T86_IN)

def equal_power(n):
    t = np.linspace(0, np.pi / 2, n, dtype=np.float32)
    return np.cos(t), np.sin(t)

# loudness-match every section to -18 LUFS before joining so no level jumps
def match(x, target=-18.0):
    l = meter.integrated_loudness(x.T)
    return x * np.float32(10 ** ((target - l) / 20))

parts = {
    '85': match(sec('B0085', 0.0, T85_END)),
    '84': match(sec('B0084', T84_IN - XF1, T84_OUT)),
    '86': match(sec('B0086', T86_IN - XF, T86_END)),
    '93': match(sec('B0093', T93_IN - 2 * 0.418, T93_HIT + 0.45)),
}

out = np.zeros((2, int(80 * SR)), np.float32)
markers = {}
def place(x, t0, fade_in=0, fade_out=0):
    i0 = int(round(t0 * SR)); x = x.copy()
    if fade_in: x[:, :fade_in] *= equal_power(fade_in)[1]
    if fade_out: x[:, -fade_out:] *= equal_power(fade_out)[0]
    out[:, i0:i0 + x.shape[1]] += x

xfn = int(XF * SR); xf1n = int(XF1 * SR)
# 1) B0085 intro, short fade in
p = parts['85']; fi = int(0.25 * SR)
p[:, :fi] *= np.linspace(0, 1, fi, dtype=np.float32)
place(p, 0.0, fade_out=xf1n)
t_j1 = T85_END                                    # timeline time of join 1 (downbeat)
markers['B0085'] = (0.0, t_j1)
# 2) B0084: its hit T84_IN lands on t_j1 (next beat of B0085's grid); 80 ms punch-in,
#    then a one-beat equal-power fade out that ends exactly on join 2
place(parts['84'], t_j1 - XF1, fade_in=xf1n, fade_out=xfn)
t_j2 = t_j1 + (T84_OUT - T84_IN)
markers['B0084'] = (t_j1, t_j2)
# 3) B0086 up to the final hit + ring-out
place(parts['86'], t_j2 - XF, fade_in=xfn)
t_hit = t_j2 + (T86_HIT - T86_IN)
t_86end = t_j2 + (T86_END - T86_IN)
markers['B0086'] = (t_j2, t_hit)

# reverb tail on song A's final hit (wet only) so the change never drops to silence
hit = out[:, int((t_hit - 0.05) * SR):int((t_86end) * SR)].copy()
tail = Pedalboard([Reverb(room_size=0.85, damping=0.4, wet_level=1.0, dry_level=0.0, width=1.0)])(
    np.concatenate([hit, np.zeros((2, int(3.5 * SR)), np.float32)], 1), SR)
out[:, int((t_hit - 0.05) * SR):int((t_hit - 0.05) * SR) + tail.shape[1]] += tail * np.float32(0.35)

# 4) B0093: its downbeat lands 2 song-A beats after the final hit; it rises in over the
#    two beats before with a high-pass sweep 1800 Hz -> 30 Hz
t_93 = t_hit + 2 * XF
x = parts['93'].copy(); pre = int(2 * 0.418 * SR); blk = 480
hp = HighpassFilter(1800); swept = np.zeros_like(x[:, :pre])
for i in range(0, pre, blk):
    frac = i / pre
    hp.cutoff_frequency_hz = float(1800 * (30 / 1800) ** frac)
    j = min(i + blk, pre)
    swept[:, i:j] = hp(x[:, i:j], SR, reset=False)
ramp = np.sin(np.linspace(0, np.pi / 2, pre, dtype=np.float32)) ** 2
x[:, :pre] = swept * ramp
# end: stop on the downbeat hit, short fade, long reverb tail
end_i = x.shape[1]; fo = int(0.25 * SR)
x[:, end_i - fo:] *= np.cos(np.linspace(0, np.pi / 2, fo, dtype=np.float32))
place(x, t_93 - 2 * 0.418)
t_end_hit = t_93 + (T93_HIT - T93_IN)
markers['B0093'] = (t_93, t_end_hit)
last = out[:, int((t_end_hit - 0.05) * SR):int((t_end_hit + 0.45) * SR)].copy()
tail2 = Pedalboard([Reverb(room_size=0.9, damping=0.35, wet_level=1.0, dry_level=0.0, width=1.0)])(
    np.concatenate([last, np.zeros((2, int(4 * SR)), np.float32)], 1), SR)
tail2[:, -int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR), dtype=np.float32)
i0 = int((t_end_hit - 0.05) * SR); out[:, i0:i0 + tail2.shape[1]] += tail2 * np.float32(0.45)
total = t_end_hit + 3.8
out = out[:, :int(total * SR)]

# ---- master bus: glue compression, limiter, -14 LUFS / -1 dBTP ----
bus = Pedalboard([Compressor(threshold_db=-20, ratio=2.5, attack_ms=12, release_ms=140), Gain(2.0)])
out = bus(out, SR)
out *= np.float32(10 ** ((-14.0 - meter.integrated_loudness(out.T)) / 20))
out = Pedalboard([Limiter(threshold_db=-1.2, release_ms=80)])(out, SR)
out *= np.float32(10 ** ((-14.0 - meter.integrated_loudness(out.T)) / 20))
out = np.clip(out, -0.89, 0.89)                    # safety, ~ -1 dBFS
sf.write(f'{D}/track_v1.wav', out.T, SR, subtype='PCM_24')

json.dump(dict(total=total, joins=dict(j1=t_j1, j2=t_j2, hit_A=t_hit, songB_downbeat=t_93, end_hit=t_end_hit),
               segments=markers, refined=dict(T84_IN=T84_IN, T86_IN=T86_IN)),
          open(f'{D}/track_v1.json', 'w'), indent=1)
print(json.dumps(json.load(open(f'{D}/track_v1.json')), indent=1))
print('LUFS', round(meter.integrated_loudness(out.T), 2), 'peak dBFS', round(20 * np.log10(np.abs(out).max()), 2))
