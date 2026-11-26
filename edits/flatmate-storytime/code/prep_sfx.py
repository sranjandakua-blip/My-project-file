"""Trim library SFX to their onset, cap length, fade out -> WD/sfx/lib_<key>.wav"""
import sys, os, subprocess, numpy as np
WD = sys.argv[1]; LIB = os.path.join(WD, 'sfxlib', '1QarjMwh-0LglIk_nC2PE0lxj4dWjEXvM')
PICK = {  # key: (file, max seconds)
    'vineboom': ('vine boom.mp3', 1.4), 'dundun': ('dun dun dunn.mp3', 2.4), 'coin': ('coin sound.mp3', 1.2),
    'rewind': ('rewind.mp3', 1.6), 'mystery': ('mystery accent.mp3', 2.0), 'bell': ('bell.mp3', 1.1),
    'tabla': ('tabla 1.mp3', 0.9), 'crickets': ('crickets chirping.wav', 1.8),
    'trombone': ('Sad Trombone Wah Wah Wah Fail Sound Effect(MP3_160K).mp3', 2.4),
    'evillaugh': ('Evil Laugh Sound Effect(MP3_160K).mp3', 1.5), 'giggle': ('girl laugth.mp3', 1.3),
    'troll': ('Troll Laugh Sound Effect(MP3_160K).mp3', 1.2), 'whatt': ('whatt.mp3', 1.0), 'pakk': ('pakk.mp3', 0.5),
    'bassdrop': ('bass drop sound.mp3', 1.6), 'clock': ('clock ticking.mp3', 2.2),
    'scratch': ('Record Scratch Sound Effect(MP3_160K).mp3', 1.1), 'suspense': ('suspence.mp3', 1.2),
    'mario': ('mario tone.mp3', 1.2),
}
for k, (f, mx) in PICK.items():
    p = os.path.join(LIB, f)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '48000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    env = np.sqrt(np.convolve(a ** 2, np.ones(480) / 480, 'same'))
    on = np.argmax(env > env.max() * 0.06) / 48000
    on = max(0.0, on - 0.01)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{on:.3f}', '-i', p, '-t', str(mx), '-af',
                    f'afade=t=out:st={max(0, mx - 0.2):.2f}:d=0.2,aresample=48000', '-ac', '2',
                    os.path.join(WD, 'sfx', f'lib_{k}.wav')], check=True)
    print(f'{k:10s} onset {on:.2f}s  -> {mx}s')
