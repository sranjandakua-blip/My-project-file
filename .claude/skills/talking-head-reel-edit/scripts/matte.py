"""Person matte for every output-body frame of an edit config (MODNet portrait matting).
Usage: python3 -I matte.py <edit.json> <modnet.onnx>   ->  <edit dir>/build/matte.npy  (N, 896, 512) uint8
Output frame i uses exactly the source frame reel.py uses (same keeps / speed mapping, frame-exact)."""
import json, os, sys, subprocess, time, math, numpy as np, onnxruntime as ort
cfg_path = os.path.abspath(sys.argv[1]); cfg = json.load(open(cfg_path)); os.chdir(os.path.dirname(cfg_path))
W, H, FPS, MW, MH = 1080, 1920, 30, 512, 896
KEEPS = cfg['keeps']; SPEED = cfg.get('speed', 1.0); CUM = []; c = 0.0
for s, e in KEEPS: CUM.append(c); c += (e - s) / SPEED
BODY = c; n = int(round(BODY * FPS))


def src_at(T):
    for (s, e), c0 in zip(KEEPS, CUM):
        if T < c0 + (e - s) / SPEED: return s + (T - c0) * SPEED
    return KEEPS[-1][1]


r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', cfg['source']],
                   capture_output=True, text=True).stdout.strip()
num, den = (r.split('/') + ['1'])[:2]; SRC_FPS = float(num) / float(den)
FILL = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}'
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', cfg['source'], '-vf', f'fps={SRC_FPS},{FILL},scale={MW}:{MH}:flags=area',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(sys.argv[2], so, providers=['CPUExecutionProvider'])
os.makedirs('build', exist_ok=True)
out = np.lib.format.open_memmap('build/matte.npy', mode='w+', dtype=np.uint8, shape=(n, MH, MW))
prev = None; read = 0; frame = None; t0 = time.time(); fs = MW * MH * 3
for i in range(n):
    k = int(math.floor(src_at(i / FPS) * SRC_FPS + .5))
    while read <= k:
        buf = p.stdout.read(fs)
        if len(buf) < fs: break
        read += 1
        if read > k: frame = np.frombuffer(buf, np.uint8).reshape(MH, MW, 3)
    x = frame.astype(np.float32) / 255
    a = sess.run(None, {'input': ((x - .5) / .5).transpose(2, 0, 1)[None]})[0][0, 0]
    a = np.clip((a - 0.12) / 0.78, 0, 1)                     # tighten soft edge -> less background halo
    if prev is not None:                                      # light temporal smoothing against flicker
        a = np.where(np.abs(a - prev) < .25, .55 * a + .45 * prev, a)
    prev = a; out[i] = (a * 255).astype(np.uint8)
    if (i + 1) % 150 == 0: print(f'{i + 1}/{n} {time.time() - t0:.0f}s', flush=True)
p.kill(); out.flush(); print('matte done', n)
