"""Audio mix: voice (cleaned, levelled) + lo-fi bed + SFX -> build/mix.wav (-14 LUFS, -1 dBTP)."""
import sys, os, subprocess, json
WD = sys.argv[1]; P = lambda *a: os.path.join(WD, *a)
TOTAL = 91.82
MAIN_END = 89.62

reveals = [4.48, 7.45, 10.87, 19.21, 25.07, 29.45, 35.53, 41.58, 47.60, 58.04, 66.57, 75.59, 81.62]
EV = []  # (time, file, gain_db)
for i, t in enumerate(reveals):
    EV.append((t, '2380' if i % 2 == 0 else '1530', -10))
EV += [
    (61.27, '166', -12), (61.32, '2357', -9), (61.82, '2357', -10), (62.27, '2357', -9),   # bill cards
    (58.90, '3005', -8),                                                                    # khaanewali -> kaamwali swap
    (29.92, '2364', -13), (30.38, '2364', -13), (30.87, '1530', -12),                       # MINE / HERS / tape
    (66.68, '2354', -6),                                                                    # OTP banner
    (74.80, '2870', -13),                                                                   # Kotak 811
    (18.01, '2356', -10), (39.95, '166', -12), (52.62, '3115', -12), (71.93, '166', -14),   # punch-ins
    (MAIN_END - 0.05, '1490', -8),                                                          # follow card
    (MAIN_END + 1.45, '1133', -10),                                                         # cover
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
inputs = ['-i', P('build', 'voice.wav'), '-i', P('music', '764.mp3')]
fc = []
fc.append(f"[0:a]apad=whole_dur={TOTAL}[v]")
bed = f"0.11+(0.32-0.11)*clip((t-{MAIN_END - 0.3})/0.4,0,1)"
fc.append(f"[1:a]aresample=48000,atrim=0:{TOTAL},volume='{bed}':eval=frame,afade=t=in:d=0.4,"
          f"afade=t=out:st={TOTAL - 0.7}:d=0.7[m]")
labels = ['[v]', '[m]']
for k, (t, f, g) in enumerate(EV):
    inputs += ['-i', P('sfx', f + '.mp3')]
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
