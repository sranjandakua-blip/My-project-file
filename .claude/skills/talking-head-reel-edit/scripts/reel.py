"""Reference-style talking-head reel renderer.
  python3 -I reel.py <config.json>                 full render -> <out>
  python3 -I reel.py <config.json> --stills 1.0,5.2  review stills (output-timeline seconds) -> stills/
  python3 -I reel.py <config.json> --cards           print the text-card timeline (output seconds)
All times in the config are SOURCE (raw video) seconds unless noted; cuts are given as `keeps`.
"""
import json, os, sys, subprocess, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CFG_PATH = os.path.abspath(sys.argv[1]); cfg = json.load(open(CFG_PATH)); os.chdir(os.path.dirname(CFG_PATH))
W, H, FPS = 1080, 1920, 30
PNG = cfg['png_dir']; FONTS = cfg['fonts_dir']; SFXD = cfg['sfx_dir']
YEL = tuple(cfg.get('yellow', [255, 226, 52])); WHITE = (255, 255, 255)

# ---------------- time mapping ----------------
KEEPS = cfg['keeps']; CUM = []; _c = 0.0; SPEED = cfg.get('speed', 1.0)   # speed > 1: whole talk plays faster (pitch kept)
for s, e in KEEPS: CUM.append(_c); _c += (e - s) / SPEED
BODY = _c; END = cfg.get('end', {}).get('dur', 0.0); TOTAL = BODY + END
NF = int(round(TOTAL * FPS))


def o(t):
    """source time -> output time (times inside a removed span snap to the next kept frame)"""
    for (s, e), c0 in zip(KEEPS, CUM):
        if t < s: return c0
        if t <= e: return c0 + (t - s) / SPEED
    return BODY


def src_at(T):
    for (s, e), c0 in zip(KEEPS, CUM):
        if T < c0 + (e - s) / SPEED: return s + (T - c0) * SPEED
    return KEEPS[-1][1]


def ease_out(p): p = min(1, max(0, p)); return 1 - (1 - p) ** 3
def ease_io(p): p = min(1, max(0, p)); return p * p * (3 - 2 * p)
def back(p):
    p = min(1, max(0, p)); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


# ---------------- image helpers ----------------
_png_cache = {}
def load_png(name, crop=True):
    key = (name, crop)
    if key not in _png_cache:
        im = Image.open(name if os.path.isabs(name) else f'{PNG}/{name}').convert('RGBA')
        if crop:
            bb = im.getchannel('A').point(lambda v: 255 if v > 3 else 0).getbbox()
            if bb: im = im.crop((max(0, bb[0] - 4), max(0, bb[1] - 4), min(im.width, bb[2] + 4), min(im.height, bb[3] + 4)))
        _png_cache[key] = np.array(im)
    return _png_cache[key]


def blend(frame, rgba, cx, cy, alpha=1.0, scale=1.0):
    """alpha-composite rgba (np HxWx4) centred at (cx, cy) onto frame (np HxWx3 uint8) in place"""
    if alpha <= 0.003 or scale <= 0.01: return
    im = rgba
    if abs(scale - 1) > 1e-3:
        im = cv2.resize(rgba, (max(1, int(rgba.shape[1] * scale)), max(1, int(rgba.shape[0] * scale))),
                        interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
    h, w = im.shape[:2]; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb: return
    sub = im[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = sub[..., 3:4] / 255.0 * alpha
    reg = frame[ya:yb, xa:xb].astype(np.float32)
    frame[ya:yb, xa:xb] = (reg * (1 - a) + sub[..., :3] * a).astype(np.uint8)


def zoom_img(img, z, cx=W / 2, cy=H / 2, dx=0.0, dy=0.0):
    """scale img about (cx, cy) by z (>=1 crops in), translate by dx, dy (output px)"""
    M = np.float32([[z, 0, cx - z * cx + dx], [0, z, cy - z * cy + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------------- decoders ----------------
STILLS = '--stills' in sys.argv


class Stream:
    """sequential raw-RGB reader for an ffmpeg pipeline; in stills mode seeks per request."""
    def __init__(self, args_fn, still_fn):
        self.args_fn, self.still_fn = args_fn, still_fn; self.p = None; self.last = None; self.n = 0

    def get(self, idx):          # idx: frame index within this stream
        if STILLS: return self.still_fn(idx)
        if self.p is None: self.p = subprocess.Popen(self.args_fn(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        while self.n <= idx:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); self.n += 1
        return self.last

    def close(self):
        if self.p: self.p.kill(); self.p = None


def grab(file, t, vf):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(0, t):.3f}', '-i', file, '-frames:v', '1', '-vf', vf,
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(H, W, 3).copy() if len(r) >= W * H * 3 else np.zeros((H, W, 3), np.uint8)


SRC = cfg['source']
FILL = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}'
def base_args():
    fc = ''.join(f'[0:v]trim={s}:{e},setpts=(PTS-STARTPTS)/{SPEED},fps={FPS},{FILL},setsar=1[v{i}];' for i, (s, e) in enumerate(KEEPS))
    fc += ''.join(f'[v{i}]' for i in range(len(KEEPS))) + f'concat=n={len(KEEPS)}:v=1:a=0[out]'
    return ['ffmpeg', '-v', 'error', '-i', SRC, '-filter_complex', fc, '-map', '[out]', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
BASE = Stream(base_args, lambda i: grab(SRC, src_at(i / FPS), FILL))

# ---------------- zoom keys (punch-ins) ----------------
ZK = sorted([(o(t), z, cy) for t, z, cy in cfg['zooms']])
DRIFT = cfg.get('drift', 0.035)
def base_zoom(T):
    k = max([i for i, z in enumerate(ZK) if z[0] <= T + 1e-6], default=0)
    t0, z, cy = ZK[k]; t1 = ZK[k + 1][0] if k + 1 < len(ZK) else BODY
    p = (T - t0) / max(0.5, t1 - t0)
    return z * (1 + DRIFT * ease_io(p)), cy


# ---------------- inserts ----------------
class Insert:
    def __init__(self, d):
        self.d = d; self.T0 = o(d['t0']); self.T1 = o(d['t1']); self.kind = d['type']
        if self.kind == 'video':
            f, ss = d['file'], d.get('ss', 0); sw = int(round(H * 16 / 9 / 2) * 2)
            x = int(d.get('crop_x', .5) * (sw - W))
            vf = f'scale={sw}:{H}:flags=lanczos,crop={W}:{H}:{x}:0,setsar=1,fps={FPS}'
            if d.get('eq'): vf += ',' + d['eq']
            dur = self.T1 - self.T0 + .3
            self.s = Stream(lambda: ['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', f, '-t', f'{dur:.3f}', '-vf', vf, '-an',
                                     '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                            lambda i: grab(f, ss + i / FPS, vf.replace(f',fps={FPS}', '')))
        elif self.kind == 'image':
            self.img = load_png(d['file'], crop=False)[..., :3].copy()
        elif self.kind == 'seq':
            self.items = [(o(t), load_png(fn, crop=False)[..., :3].copy()) for fn, t in d['frames']]

    def active(self, T): return self.T0 - 1e-6 <= T < self.T1

    def render(self, T):
        d = self.d; dt = T - self.T0; p = dt / max(.1, self.T1 - self.T0)
        z0, z1 = d.get('kb', [1.0, 1.07])
        if self.kind == 'video':
            fr = self.s.get(int(round(dt * FPS)))
            return zoom_img(fr, z0 + (z1 - z0) * p) if fr is not None else None
        if self.kind == 'image':
            py = d.get('pan_y', 0) * ease_io(p)
            return zoom_img(self.img, z0 + (z1 - z0) * ease_io(p), cy=d.get('kb_cy', H / 2), dy=py)
        if self.kind == 'seq':
            k = max([i for i, (t, _) in enumerate(self.items) if t <= T + 1e-6], default=0)
            ts, img = self.items[k]; tn = self.items[k + 1][0] if k + 1 < len(self.items) else self.T1
            q = (T - ts) / max(.1, tn - ts); snap = 1 + .06 * (1 - ease_out((T - ts) / .25))
            return zoom_img(img, snap * (1 + .035 * q), cy=d.get('kb_cy', 1000))


INS = [Insert(d) for d in cfg.get('inserts', [])]

# ---------------- data-flow animation (v2) ----------------
class DataFlow:
    def __init__(self, d):
        self.d = d; self.T0 = o(d['t0']); self.T1 = o(d['t1'])
        self.bg = load_png(d['bg'], crop=False)[..., :3].copy(); self.box = load_png(d['box'])
        self.items = [(o(t), load_png(tile), load_png(chip)) for tile, chip, t in d['items']]
        self.out = (o(d['out_t']), load_png(d['out_chip']))
        self.bx, self.by = 540, d.get('box_y', 1180)

    def active(self, T): return self.T0 - 1e-6 <= T < self.T1

    def render(self, T):
        TS, CS = self.d.get('tile_scale', 1.3), self.d.get('chip_scale', .9)
        fr = zoom_img(self.bg, 1 + .03 * (T - self.T0) / (self.T1 - self.T0))
        pulse = 0
        for i, (t, tile, chip) in enumerate(self.items):
            dt = T - t
            if dt < 0: continue
            side = -1 if i % 2 == 0 else 1
            sx, sy = 540 + side * 330, 760 + (i % 3) * 40
            if dt < .45:   # pop in at the side
                blend(fr, tile, sx, sy, min(1, dt / .08), back(dt / .3) * TS)
            elif dt < 1.0:  # fly into the box
                q = ease_io((dt - .45) / .55)
                x = sx + (self.bx - sx) * q; y = sy + (self.by - sy) * q - math.sin(q * math.pi) * 120
                blend(fr, tile, x, y, 1 - .7 * q ** 3, TS * (1 - .65 * q))
            if 1.0 <= dt < 1.35: pulse = max(pulse, 1 - (dt - 1.0) / .35)
        blend(fr, self.box, self.bx, self.by, 1, 1 + .07 * pulse)
        # chip row (2 rows) at the top: INCOME → SPENDING → ...
        chips = [(t, c) for t, _, c in self.items] + [self.out]
        rows = [chips[:3], chips[3:]]
        for r, row in enumerate(rows):
            widths = [c.shape[1] * CS for _, c in row]; gap = 46
            x = (W - (sum(widths) + gap * (len(row) - 1))) / 2; y = self.d.get('chips_y', 300) + r * 125
            for j, ((t, c), w) in enumerate(zip(row, widths)):
                dt = T - t
                if dt >= 0: blend(fr, c, x + w / 2, y, min(1, dt / .08), CS * back(dt / .28))
                if j < len(row) - 1 and T >= row[j + 1][0]:
                    blend(fr, ARROW, x + w + gap / 2, y, 1, .8)
                x += w + gap
        return fr


DFS = [DataFlow(d) for d in cfg.get('dataflow', [])]

# ---------------- overlays: pops, chip rows, typing states ----------------
def _arrow():
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60); im = Image.new('RGBA', (90, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.text((45, 47), '→', font=f, fill=(0, 0, 0, 150), anchor='mm'); d.text((45, 44), '→', font=f, fill=YEL + (255,), anchor='mm')
    return np.array(im)
ARROW = _arrow()


class Overlay:
    def __init__(self, d):
        self.d = d; self.kind = d['type']; self.T0 = o(d['t0']); self.T1 = o(d['t1']) if 't1' in d else BODY
        if self.kind == 'pop': self.img = load_png(d['file'])
        if self.kind == 'chips': self.items = [(o(t), load_png(f)) for f, t in d['items']]
        if self.kind == 'states': self.items = [(o(t), load_png(f)) for f, t in d['items']]

    def rect(self):
        d = self.d; sc = d.get('scale', 1.0); pad = 40
        if self.kind == 'pop': h, w = self.img.shape[:2]
        elif self.kind == 'states': h, w = self.items[-1][1].shape[:2]
        else: return (0, d['y'] - 70, W, d['y'] + 70)
        return (d['x'] - w * sc / 2 - pad, d['y'] - h * sc / 2 - pad, d['x'] + w * sc / 2 + pad, d['y'] + h * sc / 2 + pad)

    def draw(self, fr, T):
        if not (self.T0 - 1e-6 <= T < self.T1): return
        d = self.d; dt = T - self.T0; out = 1 - ease_io((T - (self.T1 - .15)) / .15) if T > self.T1 - .15 else 1
        sc = d.get('scale', 1.0)
        if self.kind == 'pop':
            s = back(dt / .32) * sc * (0.92 + .08 * out)
            blend(fr, self.img, d['x'], d['y'], min(1, dt / .07) * out, s)
        elif self.kind == 'chips':
            vis = [(t, im) for t, im in self.items]; widths = [im.shape[1] * sc for _, im in vis]; gap = d.get('gap', 50)
            x = (W - (sum(widths) + gap * (len(vis) - 1))) / 2
            for j, ((t, im), w) in enumerate(zip(vis, widths)):
                q = T - t
                if q >= 0: blend(fr, im, x + w / 2, d['y'], min(1, q / .07) * out, back(q / .3) * sc)
                if d.get('arrows', True) and j < len(vis) - 1 and T >= vis[j + 1][0]:
                    blend(fr, ARROW, x + w + gap / 2, d['y'], out, .8)
                x += w + gap
        elif self.kind == 'states':
            k = max([i for i, (t, _) in enumerate(self.items) if t <= T + 1e-6], default=0)
            s = back(dt / .3) * sc
            blend(fr, self.items[k][1], d['x'], d['y'], min(1, dt / .07) * out, s)


OVS = [Overlay(d) for d in cfg.get('overlays', [])]

# ---------------- kinetic text cards ----------------
FSZ, BSZ = cfg.get('small_size', 60), cfg.get('big_size', 140)
def font(style, size): return ImageFont.truetype(f'{FONTS}/Mali_wght_600.ttf' if style == 's' else f'{FONTS}/Poppins_wght_700.ttf', size)
TOP = cfg.get('text_top', 230); MAXW = 960; MARGIN = 60; LGAP = cfg.get('line_gap', 14); LEAD = cfg.get('word_lead', 0.08)


# ---------------- subject matte (text goes BEHIND the subject on talking-head shots) ----------------
MATTE = np.load('build/matte.npy', mmap_mode='r') if os.path.exists('build/matte.npy') and cfg.get('depth', True) else None
TOPMIN = cfg.get('safe_top', 150); SAFE_BOTTOM = cfg.get('safe_bottom', 1560)


def face_shot(T):
    return MATTE is not None and T < BODY and not any(i.active(T) for i in INS) and not any(d.active(T) for d in DFS)


def matte_full(i, z, cy):
    m = cv2.resize(np.asarray(MATTE[min(i, len(MATTE) - 1)]), (W, H), interpolation=cv2.INTER_LINEAR)
    M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, cy - z * cy]])
    return cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def matte_small(i, z, cy):   # quarter-res float mask for layout decisions
    m = cv2.resize(np.asarray(MATTE[min(i, len(MATTE) - 1)]), (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    M = np.float32([[z, 0, W / 8 - z * W / 8], [0, z, cy / 4 - z * cy / 4]])
    return cv2.warpAffine(m, M, (W // 4, H // 4), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


_occ_cache = {}
def subject_map(T0, T1):
    """quarter-res bool map: pixels where the subject is present in >= 25% of the face-shot frames of [T0, T1)"""
    key = (round(T0, 3), round(T1, 3))
    if key not in _occ_cache:
        fr = [i for i in range(int(math.ceil(T0 * FPS - 1e-6)), int(T1 * FPS), 2) if face_shot(i / FPS)]
        if not fr: _occ_cache[key] = None
        else:
            acc = np.zeros((H // 4, W // 4), np.float32)
            for i in fr:
                z, cy = base_zoom(i / FPS); acc += matte_small(i, z, cy) > .5
            _occ_cache[key] = acc / len(fr)       # presence frequency per pixel
    return _occ_cache[key]


def occ(S, x0, y0, x1, y1):
    xa, ya, xb, yb = max(0, int(x0 // 4)), max(0, int(y0 // 4)), min(W // 4, int(x1 // 4) + 1), min(H // 4, int(y1 // 4) + 1)
    if xa >= xb or ya >= yb: return 0.0
    return float(S[ya:yb, xa:xb].mean())


class Card:
    def __init__(self, d):
        self.d = d; self.T0 = o(d['t0']); self.T1 = o(d['t1']); self.align = d.get('align', 'left'); self.cache = None
        self.top = d.get('y', TOP); self.build(1.0); self.layout()

    def build(self, gscale):
        lines = []
        for ln in self.d['lines']:
            scale = gscale
            while True:
                runs = []; xx = 0; top = 0; bot = 0; big = False
                for k, run in enumerate(ln):
                    style, text, t = run[0], run[1], run[2]
                    size = int((BSZ if style == 'b' else FSZ) * scale * (run[3] if len(run) > 3 else 1))
                    f = font(style, size); big = big or style == 'b'
                    words = text.split(' '); step = 0.13 if style == 's' else 0.2
                    wts = run[4] if len(run) > 4 else [t + i * step for i in range(len(words))]
                    wts = list(wts) + [wts[-1] + (j + 1) * step for j in range(len(words) - len(wts))]   # extrapolate missing
                    wts = [v - LEAD for v in wts]       # whisper word times run a little late: reveal slightly early
                    if k > 0: xx += f.getlength(' ') * (0.9 if style == 'b' else 1)
                    for i, w in enumerate(words):
                        runs.append(dict(text=w, font=f, style=style, x=xx, t=o(wts[i])))
                        xx += f.getlength(w) + (f.getlength(' ') if i < len(words) - 1 else 0)
                    bb = f.getbbox(text, anchor='ls'); top = min(top, bb[1]); bot = max(bot, bb[3], int(size * .04))
                if xx <= MAXW or scale < .55: break
                scale *= .93
            lines.append(dict(runs=runs, width=xx, top=top, bot=bot, big=big))
        self.lines = lines; self.h = int(sum(l['bot'] - l['top'] + LGAP for l in lines)) + 40

    def rects(self, top, align):
        out = []; y = top
        for l in self.lines:
            x0 = MARGIN if align == 'left' else (W - MARGIN - l['width'] if align == 'right' else (W - l['width']) / 2)
            hh = l['bot'] - l['top']; out.append((x0, y, x0 + l['width'], y + hh, l['big'])); y += hh + LGAP
        return out

    def layout(self):
        """Pick top/alignment so small text never sits on the subject and big keywords tuck behind the head
        by at most ~22% (depth effect) - searched over the subject's actual positions during this card."""
        if MATTE is None or 'y' in self.d: return
        S = subject_map(self.T0, self.T1)
        if S is None: return
        aligns = [self.align] + [a for a in ('center', 'left', 'right') if a != self.align]
        obst = [ov.rect() for ov in OVS if ov.T0 < self.T1 - .05 and ov.T1 > self.T0 + .05 and ov.rect()]
        U = S > .04; P = S >= .25          # U: anywhere she goes during the card, P: where she usually is
        for gscale in (1.0, .9, .8, .7):
            if gscale != 1.0: self.build(gscale)
            best = None
            for ai, al in enumerate(aligns):
                for top in range(TOPMIN, SAFE_BOTTOM - self.h, 8):
                    rs = self.rects(top, al); ok = True; depth = 0.0; hasbig = False
                    for x0, y0, x1, y1, big in rs:
                        if any(x0 < ob[2] and x1 > ob[0] and y0 < ob[3] and y1 > ob[1] for ob in obst): ok = False; break
                        if not big:
                            if occ(U, x0, y0, x1, y1) > .01: ok = False; break
                        else:
                            cut = y0 + .6 * (y1 - y0)
                            if occ(U, x0, y0, x1, cut) > .01: ok = False; break
                            hasbig = True; depth = max(depth, occ(P, x0, cut, x1, y1))
                    if not ok: continue
                    score = (-abs(depth - .35) * 2 if hasbig else 0) + (top / H) * .6 - ai * .08
                    if best is None or score > best[0]: best = (score, top, al)
            if best:
                _, self.top, self.align = best; self.top += 20; return
        print('WARN: no clear layout for card', self.d['lines'][0][0][1])

    def draw(self, fr, T):
        if not (self.T0 - 1e-6 <= T < self.T1): return
        exit_a = 1 - ease_io((T - (self.T1 - .12)) / .12) if T > self.T1 - .12 else 1
        if self.cache is not None and exit_a >= 1:
            lay = self.cache
        else:
            layer = Image.new('RGBA', (W, self.h + 60), (0, 0, 0, 0)); dr = ImageDraw.Draw(layer)
            y = 20; done = True
            for l in self.lines:
                x0 = MARGIN if self.align == 'left' else (W - MARGIN - l['width'] if self.align == 'right' else (W - l['width']) / 2)
                base = y - l['top']
                for r in l['runs']:
                    col = YEL if r['style'] == 'b' else WHITE
                    for ci, ch in enumerate(r['text']):
                        a = ease_out((T - (r['t'] + ci * .022)) / .16)
                        if a < 1: done = False
                        if a <= 0: continue
                        cx = x0 + r['x'] + r['font'].getlength(r['text'][:ci])
                        dr.text((cx, base + (1 - a) * 18), ch, font=r['font'], fill=col + (int(255 * a),), anchor='ls')
                y = base + l['bot'] + LGAP
            al = layer.getchannel('A')
            sh1 = Image.new('RGBA', layer.size, (0, 0, 0, 0)); sh1.putalpha(al.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .55)))
            sh2 = Image.new('RGBA', layer.size, (0, 0, 0, 0)); sh2.putalpha(al.filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * .45)))
            comp = Image.new('RGBA', layer.size, (0, 0, 0, 0))
            comp.alpha_composite(sh1, (0, 6)); comp.alpha_composite(sh2, (0, 3)); comp.alpha_composite(layer)
            lay = np.array(comp)
            if done: self.cache = lay
        blend(fr, lay, W / 2, self.top - 20 + lay.shape[0] / 2, exit_a)


CARDS = [Card(d) for d in cfg.get('cards', [])]

# ---------------- fx ----------------
FX = [dict(d, T=o(d['t']) if 't' in d else d['T_out']) for d in cfg.get('fx', [])]
def _leak():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g1 = np.exp(-(((xx - 820) / 520) ** 2 + ((yy - 700) / 760) ** 2))
    g2 = np.exp(-(((xx - 240) / 380) ** 2 + ((yy - 1350) / 560) ** 2))
    col = np.stack([255 * (g1 * 1.0 + g2 * .9), 150 * g1 + 110 * g2, 40 * g1 + 20 * g2], -1)
    return np.clip(col, 0, 255)
LEAK = _leak() if any(f['type'] == 'leak' for f in FX) else None


def apply_fx(fr, T):
    for f in FX:
        tau = T - f['T']
        if f['type'] == 'whip' and abs(tau) < .11:
            s = 1 - abs(tau) / .11; L = int(10 + 90 * s); k = np.ones((1, L), np.float32) / L
            fr = cv2.filter2D(fr, -1, k, borderType=cv2.BORDER_REFLECT)
            fr = zoom_img(fr, 1 + .06 * s, dx=f.get('dir', 1) * -tau / .11 * 90)
        elif f['type'] == 'leak' and -.3 < tau < .45:
            a = math.sin(math.pi * (tau + .3) / .75) ** 1.5 * f.get('strength', .9)
            shift = int(tau * 400)
            lk = np.roll(LEAK, shift, axis=1) * a
            fr = (255 - (255 - fr.astype(np.float32)) * (255 - lk) / 255).astype(np.uint8)
        elif f['type'] == 'shake' and 0 <= tau < f.get('dur', .3):
            q = 1 - tau / f.get('dur', .3); rs = np.random.default_rng(int(T * 1000))
            fr = zoom_img(fr, 1.04, dx=rs.uniform(-1, 1) * 16 * q, dy=rs.uniform(-1, 1) * 12 * q)
        elif f['type'] == 'flash' and 0 <= tau < .14:
            a = (1 - tau / .14) * f.get('strength', .45)
            fr = (fr.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
    return fr


def scrim(fr, strength=.55, height=760):
    g = (np.linspace(1, 0, height) ** 1.4 * strength)[:, None, None]
    fr[:height] = (fr[:height].astype(np.float32) * (1 - g)).astype(np.uint8)


# ---------------- end card ----------------
ENDD = cfg.get('end'); END_ITEMS = [(t, load_png(f, crop=False)[..., :3].copy()) for f, t in ENDD['states']] if ENDD else []
def end_frame(te):
    k = max([i for i, (t, _) in enumerate(END_ITEMS) if t <= te + 1e-6], default=0)
    t, img = END_ITEMS[k]; snap = 1 + .05 * (1 - ease_out((te - t) / .22))
    fr = zoom_img(img, snap * (1 + .03 * te / END))
    if te < .2: fr = apply_fx(fr, BODY + te)
    return fr


# ---------------- frame composer ----------------
def frame_at(i):
    T = i / FPS
    if T >= BODY and ENDD:
        fr = end_frame(T - BODY)
        return apply_fx(fr, T)
    base = BASE.get(i)
    z, cy = base_zoom(T)
    fr = zoom_img(base, z, cy=cy)
    vid = False
    for ins in INS:
        if ins.active(T):
            r = ins.render(T)
            if r is not None: fr = r; vid = vid or ins.kind == 'video'
    for df in DFS:
        if df.active(T): fr = df.render(T)
    if vid: scrim(fr)
    fr = np.ascontiguousarray(fr)
    face = face_shot(T)
    if face: subj = fr.copy()
    for ov in OVS: ov.draw(fr, T)
    for c in CARDS: c.draw(fr, T)
    if face:   # subject cut-out composited back over the graphics -> text sits behind her
        m = (matte_full(i, z, cy).astype(np.float32) / 255)[..., None]
        fr = (fr.astype(np.float32) * (1 - m) + subj.astype(np.float32) * m).astype(np.uint8)
    return apply_fx(fr, T)


# ---------------- audio ----------------
def build_audio(path):
    ev = []   # (name, out_time, gain)
    for n, t, g in cfg.get('sfx', []): ev.append((n, o(t), g))
    for n, t, g in cfg.get('sfx_out', []): ev.append((n, t, g))
    for ins in INS:
        if ins.d.get('sfx'): ev.append((ins.d['sfx'], ins.T0 - (.12 if ins.d['sfx'] == 'whoosh' else 0), ins.d.get('sfx_gain', .5)))
    for f in FX:
        if f['type'] == 'whip': ev.append(('whoosh', f['T'] - .2, .45))
    for ov in OVS:
        if ov.d.get('sfx'):
            ts = [ov.T0] if ov.kind == 'pop' else [t for t, _ in ov.items]
            for t in ts: ev.append((ov.d['sfx'], t, ov.d.get('sfx_gain', .35)))
    mus = cfg['music']
    mpath = 'build/music.wav'
    subprocess.run(['python3', '-I', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_synth.py'), 'music', mpath,
                    f'{TOTAL + .05:.3f}', f"{o(mus['full_from']):.3f}", ','.join(f'{o(t):.3f}' for t in mus.get('drops', [])),
                    str(mus.get('bpm', 104))], check=True)
    inputs = ['-i', SRC, '-i', mpath]; fc = []
    for i, (s, e) in enumerate(KEEPS):
        fc.append(f'[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={SPEED},afade=t=in:d=0.012,afade=t=out:st={(e - s) / SPEED - .012:.3f}:d=0.012[a{i}]')
    fc.append(''.join(f'[a{i}]' for i in range(len(KEEPS))) + f'concat=n={len(KEEPS)}:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11,'
              f'aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={TOTAL:.3f}[voice]')
    fc.append('[voice]asplit=2[vo][vsc]')
    fc.append(f"[1:a]aresample=48000,loudnorm=I={mus.get('lufs', -25)}:TP=-8,aformat=channel_layouts=stereo,"
              f"volume=volume='if(gte(t,{BODY - 0.25:.3f}),{mus.get('end_boost', 1.8)},1)':eval=frame[mus0]")
    fc.append('[mus0][vsc]sidechaincompress=threshold=0.025:ratio=6:attack=20:release=380:makeup=1[mus]')
    labels = ['[vo]', '[mus]']
    for k, (n, t, g) in enumerate(sorted(ev, key=lambda e: e[1])):   # one input per event (simple + robust)
        fp = f'{SFXD}/{n}.wav' if os.path.exists(f'{SFXD}/{n}.wav') else f'{SFXD}/{n}.mp3'
        inputs += ['-i', fp]; ms = max(0, int(round(t * 1000)))
        fc.append(f'[{k + 2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms}[e{k}]')
        labels.append(f'[e{k}]')
    fc.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.89:level=false,'
              f'atrim=0:{TOTAL:.3f}[aout]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '[aout]', '-c:a', 'pcm_s16le', path], check=True)
    print('audio events', len(ev))


# ---------------- main ----------------
if __name__ == '__main__':
    os.makedirs('build', exist_ok=True)
    # client rules (Nov 2026): reels stay under a minute; phone-number card 2-3 s before the final CTA frame
    if TOTAL >= 59.5 and '--allow-long' not in sys.argv:
        sys.exit(f'TOTAL {TOTAL:.1f}s >= 59.5s: tighten keeps/end card (client rule: videos under a minute)')
    has_phone = (ENDD and any('phone_card' in f for f, _ in ENDD['states'])) or any('phone_card' in i.get('file', '') for i in cfg.get('inserts', []))
    if ENDD and not ENDD.get('no_phone') and not has_phone:
        print('WARN: end card has no phone_card state (client rule: phone CTA 2-3 s before the final CTA frame)')
    if '--check' in sys.argv:
        for c in CARDS:
            S = subject_map(c.T0, c.T1)
            rs = c.rects(c.top - 20, c.align)
            oc = ['%.2f' % occ(S > .04, *r[:4]) for r in rs] if S is not None else '-'
            print(f"{c.T0:6.2f}-{c.T1:6.2f} top={c.top:4d} {c.align:6s} occ={oc}", ' / '.join(' '.join(r['text'] for r in l['runs']) for l in c.lines))
        for ov in OVS:
            S = subject_map(ov.T0, ov.T1)
            if S is None: print(f'OV {ov.d.get("file", ov.kind):28s} no face frames'); continue
            if ov.kind == 'pop':
                h, w = ov.img.shape[:2]; sc = ov.d.get('scale', 1)
                print(f'OV {ov.d["file"]:28s} {ov.T0:6.2f}-{ov.T1:6.2f} occ={occ(S > .04, ov.d["x"] - w * sc / 2, ov.d["y"] - h * sc / 2, ov.d["x"] + w * sc / 2, ov.d["y"] + h * sc / 2):.2f}')
            else:
                print(f'OV {ov.kind:28s} {ov.T0:6.2f}-{ov.T1:6.2f} y={ov.d["y"]} occ(row)={occ(S > .04, 100, ov.d["y"] - 60, 980, ov.d["y"] + 60):.2f}')
        sys.exit()
    if '--cards' in sys.argv:
        for c in CARDS:
            print(f"{c.T0:6.2f}-{c.T1:6.2f}", ' / '.join(' '.join(r['text'] for r in l['runs']) for l in c.lines))
        print('BODY', round(BODY, 2), 'TOTAL', round(TOTAL, 2)); sys.exit()
    if STILLS:
        os.makedirs('stills', exist_ok=True)
        ts = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
        for T in ts:
            Image.fromarray(frame_at(int(round(T * FPS)))).save(f'stills/s_{T:06.2f}.png')
        print('stills', len(ts)); sys.exit()
    build_audio('build/audio.wav')
    out = cfg['out']
    if '--audio-only' in sys.argv:      # re-mux new audio onto the already rendered video
        tmp = out.replace('.mp4', '_tmp.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-i', 'build/audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', tmp], check=True)
        os.replace(tmp, out); print('remuxed audio ->', out); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', 'build/audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart',
                            '-shortest', out], stdin=subprocess.PIPE)
    import time; t0 = time.time()
    for i in range(NF):
        enc.stdin.write(np.ascontiguousarray(frame_at(i)).tobytes())
        if i % 150 == 0: print(f'frame {i}/{NF}  {time.time() - t0:.0f}s', flush=True)
    enc.stdin.close(); enc.wait(); BASE.close()
    for ins in INS:
        if ins.kind == 'video': ins.s.close()
    print('done ->', out)
