"""Audio mix: voice (cleaned, levelled) + lo-fi bed + SFX -> build/mix.wav (-14 LUFS, -1 dBTP)."""
import sys, os, subprocess, json
WD = sys.argv[1]; P = lambda *a: os.path.join(WD, *a)
TOTAL = 89.95
MAIN_END = 89.95
MUSIC = False   # old-reference vibe: voice-led, no music bed

reveals = [4.48, 7.45, 10.87, 19.21, 25.07, 29.45, 35.53, 41.58, 47.60, 58.04, 66.57, 75.59, 81.62]
EV = []  # (time, file, gain_db)
for i, t in enumerate(reveals):
    EV.append((t, '2380' if i % 2 == 0 else '1530', -10))
EV += [
    (61.27, '166', -12.0), (61.32, '2357', -9.0), (61.82, '2357', -10.0), (62.27, '2357', -9.0),   # bill cards
    (58.90, '3005', -8.0),                                                                    # khaanewali -> kaamwali swap
    (29.92, '2364', -13.0), (30.38, '2364', -13.0), (30.87, '1530', -12.0),                       # MINE / HERS / tape
    (66.68, '2354', -6.0),                                                                    # OTP banner
    (74.80, '2870', -13.0),                                                                   # Kotak 811
    (17.15, '2357', -10.0), (17.40, '2357', -10.0),                                             # me / her photos
    # ---- comedy hits (client: "more funny and engaging sfx") from the 500+ SFX pack
    (3.08, 'lib_vineboom', -14.5),      # "kabhi bhi" (hook punch)
    (8.41, 'lib_giggle', -9.8),        # "gossip"
    (11.33, 'lib_troll', -13.9),        # "naya dost dhoondhna padega"
    (15.53, 'lib_mystery', -12.1),      # "whole different side"
    (18.01, 'lib_scratch', -2.3),      # "ex" best friend
    (21.18, 'lib_coin', -0.7),         # "kharchili aurat"
    (23.09, 'lib_dundun', -10.2),       # "realise hua"
    (25.69, 'lib_pakk', -12.2), (26.47, 'lib_pakk', -12.2),   # namak alag... masala alag...
    (32.23, 'lib_rewind', -3.8),       # "particular incident" (flashback)
    (38.90, 'lib_suspense', -9.7),     # "and you know what she got..."
    (39.95, 'lib_vineboom', -10.6),     # "ANNOYED"
    (44.56, 'lib_whatt', 0.7),        # "...kaise lagne diya?"
    (46.14, '2894', -12.6),             # "bhai... shampoo bottle hi toh hai" boing
    (52.62, 'lib_bassdrop', -12.2),     # "bhasad"
    (53.76, 'lib_bell', -23.3),         # "sorted"
    (58.18, 'lib_tabla', -13.4), (58.90, 'lib_tabla', -13.4), # khaanewali / kaamwali didi
    (63.29, 'lib_clock', -4.3),        # "on time"
    (72.00, 'lib_trombone', -13.0),     # "definitely not my thing"
    (77.25, 'lib_mario', -16.4),        # "hassle-free"
    (83.40, 'lib_crickets', -6.2),     # "just live alone"
    (85.76, 'lib_evillaugh', -8.6),    # "unhinged"
]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)
    return r

os.makedirs(P('build'), exist_ok=True)
# 1) voice: clean + level (two-pass loudnorm to -15 LUFS)
pre = 'highpass=f=75,lowpass=f=15000,afftdn=nr=6:nf=-45,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2'
r = run(['ffmpeg', '-hide_banner', '-i', P('drive', 'IMG_3133.MP4'), '-vn', '-af', pre + ',loudnorm=I=-15:TP=-2:LRA=7:print_format=json', '-f', 'null', '-'])
js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
ln = (f"loudnorm=I=-15:TP=-2:LRA=7:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
run(['ffmpeg', '-v', 'error', '-y', '-i', P('drive', 'IMG_3133.MP4'), '-vn', '-af', pre + ',' + ln + ',aresample=48000',
     '-ac', '2', '-c:a', 'pcm_s16le', P('build', 'voice.wav')])

# 2) graph: voice + music bed + sfx
inputs = ['-i', P('build', 'voice.wav'), '-i', P('music', '764.mp3')]  # music input kept for the graph; muted below
fc = []
fc.append(f"[0:a]apad=whole_dur={TOTAL}[v]")
bed = "0.11" if MUSIC else "0"
fc.append(f"[1:a]aresample=48000,atrim=0:{TOTAL},volume='{bed}':eval=frame,afade=t=in:d=0.4,"
          f"afade=t=out:st={TOTAL - 0.5}:d=0.5[m]")
labels = ['[v]', '[m]']
for k, (t, f, g) in enumerate(EV):
    inputs += ['-i', P('sfx', f + ('.wav' if f.startswith('lib_') else '.mp3'))]
    ms = int(t * 1000)
    fc.append(f"[{k + 2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{k}]")
    labels.append(f'[s{k}]')
fc.append(''.join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{TOTAL}[mx]")
fc.append("[mx]alimiter=limit=0.89:level=false[out]")
run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-c:a', 'pcm_s16le',
     P('build', 'premix.wav')])

# 3) final loudness: -14 LUFS integrated, -1 dBTP
r = run(['ffmpeg', '-hide_banner', '-i', P('build', 'premix.wav'), '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'])
js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
run(['ffmpeg', '-v', 'error', '-y', '-i', P('build', 'premix.wav'), '-af', ln + ',aresample=48000', '-c:a', 'pcm_s16le',
     P('build', 'mix.wav')])
r = run(['ffmpeg', '-hide_banner', '-i', P('build', 'mix.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'])
print('\n'.join(r.stderr.strip().splitlines()[-12:]))
