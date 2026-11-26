"""Trim every SFX used in the mix to its onset (so the hit lands on the frame), cap its length, fade out.
Writes WD/sfx/t_<key>.wav and WD/sfx/levels.json (peak 100 ms RMS of each trimmed file, dBFS)."""
import sys, os, json, subprocess, numpy as np
WD = sys.argv[1]
LIB = os.path.join(WD, 'sfxlib', '1QarjMwh-0LglIk_nC2PE0lxj4dWjEXvM')   # 500+ SFX pack: "Funny Sound Effects"
MK = os.path.join(WD, 'sfx')                                              # Mixkit previews
PICK = {  # key: (path, max seconds)
    # Mixkit
    'paper': (f'{MK}/2380.mp3', 0.8), 'slide': (f'{MK}/1530.mp3', 0.9), 'sweep': (f'{MK}/166.mp3', 0.6),
    'pop': (f'{MK}/2357.mp3', 0.4), 'click': (f'{MK}/2364.mp3', 0.5), 'msg': (f'{MK}/2354.mp3', 1.0),
    'chime': (f'{MK}/2870.mp3', 1.6), 'boing': (f'{MK}/2894.mp3', 1.0),
    # 500+ pack
    'vineboom': (f'{LIB}/vine boom.mp3', 1.2), 'dundun': (f'{LIB}/dun dun dunn.mp3', 2.0), 'coin': (f'{LIB}/coin sound.mp3', 1.0),
    'rewind': (f'{LIB}/rewind.mp3', 1.0), 'mystery': (f'{LIB}/mystery accent.mp3', 1.6), 'tabla': (f'{LIB}/tabla 1.mp3', 0.7),
    'crickets': (f'{LIB}/crickets chirping.wav', 1.3), 'trombone': (f'{LIB}/Sad Trombone Wah Wah Wah Fail Sound Effect(MP3_160K).mp3', 2.2),
    'evillaugh': (f'{LIB}/Evil Laugh Sound Effect(MP3_160K).mp3', 1.2), 'giggle': (f'{LIB}/girl laugth.mp3', 1.1),
    'troll': (f'{LIB}/Troll Laugh Sound Effect(MP3_160K).mp3', 1.0), 'whatt': (f'{LIB}/whatt.mp3', 0.9), 'pakk': (f'{LIB}/pakk.mp3', 0.4),
    'bassdrop': (f'{LIB}/bass drop sound.mp3', 1.0), 'clock': (f'{LIB}/clock ticking.mp3', 1.8),
    'scratch': (f'{LIB}/Record Scratch Sound Effect(MP3_160K).mp3', 0.9), 'suspense': (f'{LIB}/suspence.mp3', 1.1),
}

def load(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '48000', '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.int16).astype(np.float32) / 32768

def peak_rms_db(a, win=4800):
    if len(a) < win: win = len(a)
    return 20 * np.log10(np.sqrt(np.convolve(a ** 2, np.ones(win) / win, 'valid').max()) + 1e-9)

levels = {}
for k, (p, mx) in PICK.items():
    a = load(p)
    env = np.sqrt(np.convolve(a ** 2, np.ones(480) / 480, 'same'))
    on = max(0.0, np.argmax(env > env.max() * 0.06) / 48000 - 0.005)
    out = os.path.join(MK, f't_{k}.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{on:.3f}', '-i', p, '-t', str(mx), '-af',
                    f'afade=t=in:d=0.004,afade=t=out:st={max(0, mx - 0.18):.2f}:d=0.18,aresample=48000', '-ac', '2', out], check=True)
    levels[k] = round(float(peak_rms_db(load(out))), 2)
    print(f'{k:10s} onset {on:.3f}s  len {mx}s  peak {levels[k]:6.1f} dBFS')
json.dump(levels, open(os.path.join(MK, 'levels.json'), 'w'), indent=1)
