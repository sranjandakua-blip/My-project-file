"""Person matte for every output-body frame of an edit config (MODNet portrait matting).
Usage: python3 -I matte.py <edit.json> <modnet.onnx>   ->  <edit dir>/build/matte.npy  (N, 896, 512) uint8
Frames are decoded exactly like reel.py's base stream (keeps concatenated, 30 fps, 1080x1920)."""
import json, os, sys, subprocess, time, numpy as np, cv2, onnxruntime as ort
cfg_path = os.path.abspath(sys.argv[1]); cfg = json.load(open(cfg_path)); os.chdir(os.path.dirname(cfg_path))
W, H, FPS, MW, MH = 1080, 1920, 30, 512, 896
keeps = cfg['keeps']; body = sum(e - s for s, e in keeps); n = int(round(body * FPS))
FILL = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}'
fc = ''.join(f'[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps={FPS},{FILL},scale={MW}:{MH}:flags=area,setsar=1[v{i}];' for i, (s, e) in enumerate(keeps))
fc += ''.join(f'[v{i}]' for i in range(len(keeps))) + f'concat=n={len(keeps)}:v=1:a=0[out]'
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', cfg['source'], '-filter_complex', fc, '-map', '[out]', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                     stdout=subprocess.PIPE)
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(sys.argv[2], so, providers=['CPUExecutionProvider'])
os.makedirs('build', exist_ok=True)
out = np.lib.format.open_memmap('build/matte.npy', mode='w+', dtype=np.uint8, shape=(n, MH, MW))
prev = None; i = 0; t0 = time.time()
while i < n:
    buf = p.stdout.read(MW * MH * 3)
    if len(buf) < MW * MH * 3: break
    x = np.frombuffer(buf, np.uint8).reshape(MH, MW, 3).astype(np.float32) / 255
    a = sess.run(None, {'input': ((x - .5) / .5).transpose(2, 0, 1)[None]})[0][0, 0]
    a = np.clip((a - 0.12) / 0.78, 0, 1)                     # tighten soft edge -> less background halo
    if prev is not None:                                      # light temporal smoothing against flicker
        a = np.where(np.abs(a - prev) < .25, .55 * a + .45 * prev, a)
    prev = a; out[i] = (a * 255).astype(np.uint8); i += 1
    if i % 150 == 0: print(f'{i}/{n} {time.time() - t0:.0f}s', flush=True)
while i < n: out[i] = out[i - 1]; i += 1                        # pad if the decoder ended a frame early
out.flush(); print('matte done', n)
