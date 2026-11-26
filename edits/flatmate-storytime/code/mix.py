"""Audio mix (v5): voice-led (no music bed) + SFX synced to on-screen events and level-matched to the voice.
Run code/prep_sfx.py first. Output: build/mix.wav at -14 LUFS / -1 dBTP, plus build/sfx_report.txt."""
import sys, os, subprocess, json
import numpy as np
WD = sys.argv[1]; P = lambda *a: os.path.join(WD, *a)
TOTAL = 89.95

# Loudness of each hit relative to the voice around it (peak 100 ms RMS, dB). Always under the voice.
TARGET = {'punch': -6, 'gag': -9, 'alert': -9, 'rewind': -11, 'laugh': -12, 'ui': -12, 'transition': -13, 'ambience': -15}

# (time, sfx key, role, visual anchor) -- every time is the frame the visual event starts in code/edit.py
EV = [
    # torn-paper B-roll reveals (INSERTS start)
    (4.48, 'paper', 'transition', 'reveal: friends walk in'), (7.45, 'slide', 'transition', 'reveal: gossip'),
    (10.87, 'paper', 'transition', 'reveal: new friend'), (19.21, 'slide', 'transition', 'reveal: shopping bags'),
    (25.07, 'paper', 'transition', 'reveal: spices'), (29.45, 'slide', 'transition', 'reveal: fridge'),
    (35.53, 'paper', 'transition', 'reveal: hair wash'), (41.58, 'slide', 'transition', 'reveal: soap bottle'),
    (47.60, 'paper', 'transition', 'reveal: passport'), (61.27, 'sweep', 'transition', 'bills card board'),
    (66.57, 'paper', 'transition', 'reveal: phone wake-up'), (75.59, 'slide', 'transition', 'reveal: card payment'),
    (81.62, 'paper', 'transition', 'reveal: sofa'),
    # graphics popping in
    (17.15, 'pop', 'ui', '"me" polaroid'), (17.40, 'pop', 'ui', '"her" polaroid'),
    (29.92, 'click', 'ui', 'MINE label'), (30.38, 'click', 'ui', 'HERS label'), (30.87, 'slide', 'ui', 'tape strip'),
    (61.32, 'pop', 'ui', 'electricity bill'), (61.82, 'pop', 'ui', 'wi-fi bill'), (62.27, 'pop', 'ui', 'gas bill'),
    (66.70, 'msg', 'alert', 'OTP banner'), (74.75, 'chime', 'alert', 'Kotak 811 zoom'),
    # comedy hits
    (3.08, 'vineboom', 'gag', 'punch-in on "kabhi bhi"'),
    (8.41, 'giggle', 'laugh', 'gossip clip whisper'),
    (11.30, 'troll', 'laugh', 'quote "naya dost dhoondhna padega"'),
    (15.07, 'mystery', 'ambience', 'quote "a whole different side"'),
    (18.01, 'scratch', 'punch', 'red "ex" on her photo'),
    (20.69, 'coin', 'gag', 'quote "kharchili aurat"'),
    (23.53, 'dundun', 'gag', 'picture shrinks (realise hua)'),
    (25.38, 'pakk', 'gag', 'quote "namak alag..."'), (26.20, 'pakk', 'gag', 'quote "masala alag..."'),
    (31.37, 'rewind', 'rewind', 'picture shrinks: flashback to the incident'),
    (38.67, 'suspense', 'ambience', 'jump cut "you know what she got..."'),
    (39.95, 'vineboom', 'punch', 'zoom on "annoyed"'),
    (44.72, 'whatt', 'laugh', 'picture shrinks after "kaise lagne diya?"'),
    (46.11, 'boing', 'gag', 'quote "bhai... shampoo bottle hi toh hai"'),
    (52.59, 'bassdrop', 'punch', 'zoom + quote "bhasad"'),
    (58.04, 'tabla', 'gag', 'reveal: cooking (khaanewali didi)'), (58.90, 'tabla', 'gag', 'swap to dishes (kaamwali didi)'),
    (63.53, 'clock', 'ambience', 'picture shrinks (zimma sar pe)'),
    (71.97, 'trombone', 'gag', 'quote "definitely not my thing"'),
    (82.41, 'crickets', 'ambience', 'quote "just live alone."'),
    (85.25, 'evillaugh', 'laugh', 'quote "most bizarre flatmate story?"'),
]

# measured attack of sounds that swell in (ms): start them early so the peak lands on the visual frame
LEAD = {'paper': 0.05, 'slide': 0.08, 'whatt': 0.11, 'trombone': 0.10, 'crickets': 0.22, 'tabla': 0.03, 'sweep': 0.03}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)
    return r

def load(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '48000', '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.int16).astype(np.float32) / 32768

os.makedirs(P('build'), exist_ok=True)
# 1) voice: clean + level (two-pass loudnorm to -15 LUFS)
pre = 'highpass=f=75,lowpass=f=15000,afftdn=nr=6:nf=-45,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2'
r = run(['ffmpeg', '-hide_banner', '-i', P('drive', 'IMG_3133.MP4'), '-vn', '-af', pre + ',loudnorm=I=-15:TP=-2:LRA=7:print_format=json', '-f', 'null', '-'])
js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
ln = (f"loudnorm=I=-15:TP=-2:LRA=7:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
run(['ffmpeg', '-v', 'error', '-y', '-i', P('drive', 'IMG_3133.MP4'), '-vn', '-af', pre + ',' + ln + ',aresample=48000',
     '-ac', '2', '-c:a', 'pcm_s16le', P('build', 'voice.wav')])

# 2) per-hit gain = target - sfx level + local voice level
lv = json.load(open(P('sfx', 'levels.json')))
v = load(P('build', 'voice.wav'))
vr = np.sqrt(np.convolve(v ** 2, np.ones(4800) / 4800, 'same'))
vdb = 20 * np.log10(vr + 1e-9)
speech_ref = float(np.percentile(vdb[vdb > -45], 75))          # typical speaking level, floor for quiet moments
rep = []; plan = []
for t, k, role, why in sorted(EV):
    a, b = int(max(0, t - 0.3) * 48000), int((t + 0.8) * 48000)
    local = max(float(vdb[a:b].max()), speech_ref - 3)
    g = TARGET[role] - lv[k] + local
    plan.append((t, k, g))
    rep.append(f'{t:6.2f}s  {k:9s} {role:10s} gain {g:+6.1f} dB -> {TARGET[role]:+d} dB vs voice   | {why}')
open(P('build', 'sfx_report.txt'), 'w').write('\n'.join(rep) + '\n')

inputs = ['-i', P('build', 'voice.wav')]
fc = [f"[0:a]apad=whole_dur={TOTAL}[v]"]; labels = ['[v]']
for i, (t, k, g) in enumerate(plan):
    inputs += ['-i', P('sfx', f't_{k}.wav')]
    ms = int(round(max(0, t - LEAD.get(k, 0)) * 1000))
    fc.append(f"[{i + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g:.2f}dB,adelay={ms}|{ms}[s{i}]")
    labels.append(f'[s{i}]')
fc.append(''.join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 0.25}:d=0.25[mx]")
fc.append("[mx]alimiter=limit=0.89:level=false[out]")
run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-c:a', 'pcm_s16le', P('build', 'premix.wav')])
# SFX-only stem for verification
fc2 = [x for x in fc if not x.startswith('[0:a]')]
fc2[-2] = ''.join(labels[1:]) + f"amix=inputs={len(labels) - 1}:normalize=0,apad=whole_dur={TOTAL},atrim=0:{TOTAL}[mx]"
fc2[-1] = "[mx]anull[out]"
run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc2), '-map', '[out]', '-c:a', 'pcm_s16le', P('build', 'sfxonly.wav')])

# 3) final loudness: -14 LUFS integrated, -1 dBTP (one linear gain -> relative levels kept)
r = run(['ffmpeg', '-hide_banner', '-i', P('build', 'premix.wav'), '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'])
js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
run(['ffmpeg', '-v', 'error', '-y', '-i', P('build', 'premix.wav'), '-af', ln + ',aresample=48000', '-c:a', 'pcm_s16le', P('build', 'mix.wav')])
r = run(['ffmpeg', '-hide_banner', '-i', P('build', 'mix.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'])
print('\n'.join(l for l in r.stderr.splitlines()[-12:] if 'I:' in l or 'Peak:' in l))
