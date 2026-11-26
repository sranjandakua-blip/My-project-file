"""Compositor for the flatmate storytime reel (new-reference style).
Usage:
  python3 -I edit.py WORKDIR preview t1 t2 ...   -> WORKDIR/prev/f_<t>.png
  python3 -I edit.py WORKDIR render              -> WORKDIR/build/video.mp4 (no audio)
All story times are on the raw-video timeline (seconds)."""
import sys, os, json, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD = sys.argv[1]
P = lambda *a: os.path.join(WD, *a)
W, H, FPS = 1080, 1920, 30
SRC_W, SRC_H = 2160, 1214   # x264 4:2:0 rounded the 1215px letterbox crop down to even
MAIN_END = 89.95            # ends on her "okay, bye" like her previous videos (no end card)
FOLLOW_END = MAIN_END
TOTAL = MAIN_END
MAGENTA = (250, 46, 236)    # sampled from the reference
INK = (22, 22, 24)
# Original layout kept: the 16:9 picture sits centred in the 9:16 frame (as in the raw file).
WW, WH = 1080, 608          # picture window
WIN_Y = 656                 # window top (raw letterbox: 1312/3840 -> 656/1920)
CAP_CY = 1418               # captions in the black band under the picture (above the bottom 320px UI zone)
CAP_MAXW = 860
TITLE_CY = 512              # story title in the black band above the picture

FONT_SANS = P('fonts', 'Poppins-ExtraBold.ttf')
FONT_SERIF = P('fonts', 'PlayfairDisplay[wght].ttf')
FONT_MARK = P('fonts', 'PermanentMarker-Regular.ttf')
FONT_ANTON = P('fonts', 'Anton-Regular.ttf')

def ease_out_cubic(p): p = min(max(p, 0), 1); return 1 - (1 - p) ** 3
def ease_out_back(p, c1=1.5):
    p = min(max(p, 0), 1); c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2

def serif(size, weight=700):
    f = ImageFont.truetype(FONT_SERIF, size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f

# ---------------------------------------------------------------- shots (talking head framing)
CUTS = [  # (start, zoom)  -- raw jump cuts + punch-ins on the beats
    (0.00, 1.00), (6.27, 1.00), (12.47, 1.00), (16.57, 1.00), (23.53, 1.00), (28.33, 1.00), (31.37, 1.00),
    (33.63, 1.00), (38.67, 1.00), (39.95, 1.30), (40.60, 1.00), (46.00, 1.00), (51.70, 1.00), (52.62, 1.30),
    (53.22, 1.00), (56.40, 1.00), (60.17, 1.00), (63.53, 1.00), (69.87, 1.00), (74.47, 1.25), (75.59, 1.00),
    (79.10, 1.00), (83.62, 1.00), (89.03, 1.00),
]
faces = json.load(open(P('faces.json')))
PUNCH = 0.6
SHOTS = []
for i, (s, z) in enumerate(CUTS):
    z = 1 + (z - 1) * PUNCH
    e = CUTS[i + 1][0] if i + 1 < len(CUTS) else MAIN_END
    d = [f for f in faces if s <= f[0] < e and f[1] is not None and f[3] > 110]
    if not d: d = [f for f in faces if abs(f[0] - s) < 2 and f[1] is not None]
    cx = float(np.median([f[1] for f in d])) * 2.25
    cy = float(np.median([f[2] for f in d])) * 2.25
    SHOTS.append(dict(s=s, e=e, z=z, cx=cx, cy=cy))

def shot_at(t):
    for sh in SHOTS:
        if sh['s'] <= t < sh['e']: return sh
    return SHOTS[-1]

_v = np.arange(256, dtype=np.float32)
def _curve(gain, lift, top):
    x = _v / 255
    y = lift + (top - lift) * (x ** 1.06) * gain
    return np.clip(y * 255, 0, 255).astype(np.uint8)
WARM = (_curve(0.90, 0.02, 0.90), _curve(0.97, 0.02, 0.93), _curve(1.0, 0.025, 0.97))   # B, G, R (subtle tungsten, highlights held)

def warm(img):
    b, g, r = cv2.split(img)
    return cv2.merge([cv2.LUT(b, WARM[0]), cv2.LUT(g, WARM[1]), cv2.LUT(r, WARM[2])])

BREATHE = [(23.53, 25.07), (31.37, 33.63), (44.72, 46.00), (63.53, 66.57), (79.10, 81.18)]  # picture shrinks on story beats
def breathe_scale(t):
    for a, b in BREATHE:
        if a <= t < b: return 1 - 0.16 * ease_out_cubic((t - a) / 0.55)
    return 1.0

def head_frame(t, src):
    sh = shot_at(t)
    prog = (t - sh['s']) / max(0.001, sh['e'] - sh['s'])
    z = sh['z'] * (1 + 0.012 * prog)              # barely-there drift
    cw, ch = SRC_W / z, SRC_H / z                 # same 16:9 shape, just tighter
    x0 = min(max(sh['cx'] - cw / 2, 0), SRC_W - cw)
    y0 = min(max(sh['cy'] - 0.42 * ch, 0), SRC_H - ch)
    k = WW / cw
    M = np.float32([[k, 0, -x0 * k], [0, k, -y0 * k]])
    return warm(cv2.warpAffine(src, M, (WW, WH), flags=cv2.INTER_AREA if k < 0.75 else cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_REPLICATE))

# ---------------------------------------------------------------- paper background
def make_paper():
    im = np.full((WH, WW, 3), 250, np.uint8)
    pat = Image.new('L', (WW, WH), 0); d = ImageDraw.Draw(pat)
    step = 110
    for k in range(-WH // step - 2, WW // step + WH // step + 3):
        x = k * step
        d.line([(x, 0), (x + WH, WH)], fill=255, width=2)
        d.line([(x, 0), (x - WH, WH)], fill=255, width=2)
    pat = np.array(pat.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    im = im.astype(np.float32) - pat[..., None] * 7
    im[..., 0] += 2  # tiny cool tint like the reference
    return np.clip(im, 0, 255).astype(np.uint8)
PAPER = make_paper()

# ---------------------------------------------------------------- torn-paper masks
def torn_poly(cx, cy, r, rng, rough=1.0):
    n = max(28, int(r / 2.2))
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ph = rng.uniform(0, 2 * np.pi, 4)
    smooth = (0.07 * np.sin(2 * ang + ph[0]) + 0.05 * np.sin(3 * ang + ph[1]) + 0.04 * np.sin(5 * ang + ph[2]))
    jag = rng.normal(0, 0.018 * rough, n) + (rng.random(n) < 0.12) * rng.uniform(-0.05, 0.05, n) * rough
    rr = r * (1 + smooth + jag)
    pts = np.stack([cx + rr * np.cos(ang), cy + rr * np.sin(ang)], 1)
    return pts.astype(np.int32)

def final_region(seed):
    rng = np.random.default_rng(seed)
    m = np.zeros((WH, WW), np.uint8)
    ins = 58
    cv2.rectangle(m, (ins, ins), (WW - ins, WH - ins), 255, -1)
    def edge(points):
        for (x, y) in points:
            r = rng.uniform(34, 62)
            cv2.fillPoly(m, [torn_poly(x + rng.uniform(-8, 8), y + rng.uniform(-8, 8), r, rng, rough=0.5)], 255, cv2.LINE_AA)
    edge([(x, ins) for x in np.arange(ins, WW - ins + 1, 52)])            # cloudy torn border on all sides
    edge([(x, WH - ins) for x in np.arange(ins, WW - ins + 1, 52)])
    edge([(ins, y) for y in np.arange(ins, WH - ins + 1, 52)])
    edge([(WW - ins, y) for y in np.arange(ins, WH - ins + 1, 52)])
    return m

class Torn:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.final = final_region(seed)
        self.blobs = []
        pts = [(rng.uniform(90, WW - 90), rng.uniform(80, WH - 80)) for _ in range(10)]
        for i, (x, y) in enumerate(pts):
            self.blobs.append(dict(x=x, y=y, t0=rng.uniform(0, 0.22) + (0.0 if i < 3 else 0.05),
                                   r=rng.uniform(230, 400), seed=int(rng.integers(1e9))))
        self.cache = {}
    def mask(self, tau):
        """tau = seconds since reveal start. Returns float mask 0..1 (H,W)."""
        if tau >= 0.62:
            key = 'final'
        else:
            key = round(tau * FPS)
        if key in self.cache: return self.cache[key]
        if key == 'final':
            m = self.final.copy()
        else:
            m = np.zeros((WH, WW), np.uint8)
            for b in self.blobs:
                p = (tau - b['t0']) / 0.40
                if p <= 0: continue
                r = b['r'] * (0.07 + 0.93 * ease_out_cubic(p) ** 1.25)
                if r < 6: continue
                rng = np.random.default_rng(b['seed'])
                cv2.fillPoly(m, [torn_poly(b['x'], b['y'], r, rng, rough=1.4)], 255, cv2.LINE_AA)
            m = cv2.bitwise_and(m, self.final)
        mf = m.astype(np.float32) / 255
        er = cv2.erode(m, np.ones((7, 7), np.uint8)).astype(np.float32) / 255
        rim = cv2.GaussianBlur(np.clip(mf - er, 0, 1), (0, 0), 1.6)
        dil = cv2.dilate(m, np.ones((11, 11), np.uint8))
        sh = cv2.GaussianBlur(dil.astype(np.float32) / 255, (0, 0), 7)
        out = (mf, rim, sh)
        self.cache[key] = out
        return out

# ---------------------------------------------------------------- B-roll inserts
INSERTS = [
    dict(s=4.48, e=6.27, clip='12118', ss=14.6, fx=0.48),
    dict(s=7.45, e=9.20, clip='12822', ss=0.3, fx=0.47),
    dict(s=10.87, e=12.47, clip='12131', ss=0.6, fx=0.5, fy=0.42),
    dict(s=19.21, e=21.49, clip='8866', ss=6.0, fx=0.57),
    dict(s=25.07, e=27.35, clip='32024', ss=3.0, fx=0.5),
    dict(s=29.45, e=31.37, clip='21338', ss=2.0, fx=0.5, extra='fridge'),
    dict(s=35.53, e=37.11, clip='42915', ss=0.8, fx=0.5),
    dict(s=41.58, e=42.80, clip='21769', ss=1.8, fx=0.62),
    dict(s=47.60, e=49.76, clip='27691', ss=9.0, fx=0.45),
    dict(s=58.04, e=60.14, clip='42910', ss=1.0, fx=0.45, swap=(58.90, '29385', 10.0, 0.55)),
    dict(s=61.27, e=63.53, kind='bills'),
    dict(s=66.57, e=68.41, clip='39780', ss=2.0, fx=0.42, extra='otp'),
    dict(s=75.59, e=77.77, clip='23466', ss=3.0, fx=0.60),
    dict(s=81.62, e=83.62, clip='4548', ss=4.0, fx=0.62),
]
for i, ins in enumerate(INSERTS):
    ins['torn'] = Torn(1000 + i * 17)
RW, RH = 1120, 630   # clip render size, 16:9 (small margin for the slow zoom)

_clip_cache = {}
def clip_frames(cid, ss, dur, fx, fy):
    key = (cid, ss)
    if key in _clip_cache: return _clip_cache[key]
    path = P('broll', cid + '.mp4')
    vw, vh = [int(v) for v in subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
              'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip().split(',')[:2]]
    sc = max(RW / vw, RH / vh)
    sw, sh = int(math.ceil(vw * sc / 2) * 2), int(math.ceil(vh * sc / 2) * 2)
    x = int(min(max(fx * sw - RW / 2, 0), sw - RW)); y = int(min(max(fy * sh - RH / 2, 0), sh - RH))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', path, '-t', str(dur + 0.2), '-vf',
                          f'fps={FPS},scale={sw}:{sh}:flags=lanczos,crop={RW}:{RH}:{x}:{y},eq=saturation=1.05',
                          '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, RH, RW, 3)
    _clip_cache.clear(); _clip_cache[key] = fr
    return fr

def clip_image(ins, t):
    cid, ss, fx, fy, t0 = ins['clip'], ins['ss'], ins.get('fx', 0.5), ins.get('fy', 0.5), ins['s']
    if 'swap' in ins and t >= ins['swap'][0]:
        t0, cid, ss, fx = ins['swap'][0], ins['swap'][1], ins['swap'][2], ins['swap'][3]
    fr = clip_frames(cid, ss, ins['e'] - t0 + 0.1, fx, fy)
    i = min(int(round((t - t0) * FPS)), len(fr) - 1)
    img = fr[i]
    prog = (t - ins['s']) / (ins['e'] - ins['s'])
    z = 1.0 + 0.07 * prog
    x0 = (RW - WW / z) / 2; y0 = (RH - WH / z) / 2
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(img, M, (WW, WH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

# ---------------------------------------------------------------- sprites (PIL -> BGRA numpy)
def to_bgra(im):
    a = np.array(im.convert('RGBA'))
    return a[..., [2, 1, 0, 3]].copy()

def paste(dst, spr, x, y, alpha=1.0):
    """Alpha-blend BGRA sprite onto BGR uint8 dst with top-left at (x, y)."""
    h, w = spr.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0: return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = s[..., 3:4] / 255 * alpha
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (d * (1 - a) + s[..., :3] * a).astype(np.uint8)

def paste_scaled(dst, spr, cx, cy, scale, alpha=1.0, angle=0.0):
    if scale <= 0.02 or alpha <= 0.01: return
    if abs(scale - 1) > 1e-3 or angle:
        h, w = spr.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
        nw, nh = int(w * scale * 1.2 + 20), int(h * scale * 1.2 + 20)
        M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        spr = cv2.warpAffine(spr, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    h, w = spr.shape[:2]
    paste(dst, spr, int(round(cx - w / 2)), int(round(cy - h / 2)), alpha)

# ---------------------------------------------------------------- captions
def parse_captions():
    pages = []
    for ln in open(P('captions.txt'), encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        lines = []
        for part in ln.split(' / '):
            toks = []
            for tok in part.split():
                word, tm = tok.rsplit('@', 1)
                s, e = [float(v) for v in tm.split('-')]
                emph = word.startswith('*')
                toks.append(dict(text=word.strip('*'), s=s, e=e, emph=emph))
            lines.append(toks)
        pages.append(lines)
    return pages

SANS_SIZE, SERIF_SIZE = 60, 100
_fonts = {}
def font_for(emph, size):
    k = (emph, size)
    if k not in _fonts:
        _fonts[k] = serif(size, 700) if emph else ImageFont.truetype(FONT_SANS, size)
    return _fonts[k]

def word_sprite(text, emph, size, dark):
    f = font_for(emph, size)
    l, t, r, b = f.getbbox(text)
    pad = 26
    w, h = r - l + pad * 2, b - t + pad * 2
    col = MAGENTA if emph else (INK if dark else (255, 255, 255))
    txt = Image.new('L', (w, h), 0)
    ImageDraw.Draw(txt).text((pad - l, pad - t), text, font=f, fill=255)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if not dark:
        sh = txt.filter(ImageFilter.GaussianBlur(8)).point(lambda v: min(255, int(v * 1.6)))
        shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.92)))
        im = Image.alpha_composite(im, shadow.transform((w, h), Image.AFFINE, (1, 0, 0, 0, 1, -3)))
        halo = Image.new('RGBA', (w, h), (0, 0, 0, 0)); halo.putalpha(txt.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * 0.55)))
        im = Image.alpha_composite(im, halo)
    else:
        sh = txt.filter(ImageFilter.GaussianBlur(5))
        shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.18)))
        im = Image.alpha_composite(im, shadow.transform((w, h), Image.AFFINE, (1, 0, 0, 0, 1, -3)))
    fill = Image.new('RGBA', (w, h), col + (255,)); fill.putalpha(txt)
    im = Image.alpha_composite(im, fill)
    return to_bgra(im), (l - pad, t - pad)

def layout_pages(pages):
    """Fixed layout per page: every word gets (cx, cy, size)."""
    out = []
    for lines in pages:
        lay = []
        for toks in lines:
            sc = 1.0
            while True:
                xs, x = [], 0
                for k, tk in enumerate(toks):
                    size = int((SERIF_SIZE if tk['emph'] else SANS_SIZE) * sc)
                    f = font_for(tk['emph'], size)
                    l, t, r, b = f.getbbox(tk['text'])
                    if k: x += int((SANS_SIZE * 0.26) * sc)
                    xs.append((x - l, x + (r - l), size, f))
                    x += r - l
                if x <= CAP_MAXW or sc < 0.55: break
                sc *= 0.92
            above = max(f.getmetrics()[0] - f.getbbox(tk['text'])[1] for (_, _, _, f), tk in zip(xs, toks))
            lay.append(dict(toks=toks, xs=xs, width=x, above=above))
        gap = 24; y = 0; bases = []
        for i, L in enumerate(lay):
            y += L['above'] + (0 if i == 0 else gap)
            bases.append(y)
        total = bases[-1]
        y_off = CAP_CY - total / 2 + 10
        words = []
        for L, base in zip(lay, bases):
            x0 = W / 2 - L['width'] / 2
            for (xa, xb, size, f), tk in zip(L['xs'], L['toks']):
                asc = f.getmetrics()[0]
                words.append(dict(tk, size=size, x=x0 + xa, base=y_off + base, asc=asc))
        out.append(words)
    return out

PAGES = layout_pages(parse_captions())
for i, pg in enumerate(PAGES):
    st = pg[0]['s']; en = pg[-1]['e']
    nxt = PAGES[i + 1][0]['s'] if i + 1 < len(PAGES) else en + 0.6
    pg_end = (nxt - 0.04) if nxt - en < 0.9 else en + 0.5
    for w in pg: w['page_s'], w['page_e'] = st, pg_end
_spr = {}
def get_sprite(w, dark):
    k = (w['text'], w['emph'], w['size'], dark)
    if k not in _spr: _spr[k] = word_sprite(w['text'], w['emph'], w['size'], dark)
    return _spr[k]

def draw_captions(frame, t, dark):
    if t >= MAIN_END: return
    for pg in PAGES:
        if not (pg[0]['page_s'] - 0.04 <= t < pg[0]['page_e']): continue
        for w in pg:
            tau = t - (w['s'] - 0.04)
            if tau < 0: continue
            spr, (ox, oy) = get_sprite(w, dark)
            p = tau / (0.20 if w['emph'] else 0.15)
            sc = 0.45 + 0.55 * ease_out_back(p, 1.9 if w['emph'] else 1.4)
            al = min(1.0, tau / 0.07)
            if w is pg[0] and pg is PAGES[0] and t < 0.2: sc, al = 1.0, 1.0   # hook frame fully legible
            h, ww = spr.shape[:2]
            # sprite top-left at full scale: x + ox, base - asc + ... (PIL draw origin is ascender top)
            tlx = w['x'] + ox; tly = w['base'] - w['asc'] + oy
            cx, cy = tlx + ww / 2, tly + h / 2 + (1 - min(1, p)) * 12
            paste_scaled(frame, spr, cx, cy, sc, al)

# ---------------------------------------------------------------- graphic overlays
def tape_label(text, w=330, h=118, angle=0):
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(text)
    pts = []
    for i in range(12):
        pts.append((20 + i * w / 11, 20 + rng.uniform(-4, 4)))
    pts += [(20 + w + rng.uniform(-6, 6), 20 + h / 2)]
    for i in range(12):
        pts.append((20 + w - i * w / 11, 20 + h + rng.uniform(-4, 4)))
    pts += [(20 + rng.uniform(-6, 6), 20 + h / 2)]
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x + 4, y + 7) for x, y in pts], fill=(0, 0, 0, 90))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im); d.polygon(pts, fill=(242, 228, 196, 245))
    f = ImageFont.truetype(FONT_MARK, 74)
    l, t, r, b = f.getbbox(text)
    d.text((20 + w / 2 - (r - l) / 2 - l, 20 + h / 2 - (b - t) / 2 - t), text, font=f, fill=(200, 20, 40))
    return to_bgra(im)

def tape_strip(length=980, thick=46):
    im = Image.new('RGBA', (thick + 30, length + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([15, 15, 15 + thick, 15 + length], fill=(242, 228, 196, 235))
    return to_bgra(im.filter(ImageFilter.GaussianBlur(0.6)))

def rounded(im_size, box, r, fill, d=None):
    d.rounded_rectangle(box, r, fill=fill)

def bill_card(title, amount, status, col):
    w, h = 640, 300
    im = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([34, 40, 34 + w, 40 + h], 28, fill=(0, 0, 0, 70))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([30, 30, 30 + w, 30 + h], 28, fill=(255, 255, 255, 255), outline=(225, 225, 230, 255), width=3)
    d.rounded_rectangle([30, 30, 30 + w, 30 + 78], 28, fill=col + (255,))
    d.rectangle([30, 80, 30 + w, 108], fill=col + (255,))
    f1 = ImageFont.truetype(FONT_SANS, 40); f2 = ImageFont.truetype(FONT_SANS, 84); f3 = ImageFont.truetype(FONT_SANS, 34)
    d.text((62, 44), title, font=f1, fill=(255, 255, 255))
    d.text((62, 128), amount, font=f2, fill=(25, 25, 30))
    l, t, r, b = f3.getbbox(status)
    sx, sy = 30 + w - (r - l) - 70, 30 + h - 78
    d.rounded_rectangle([sx - 18, sy - 8, sx + (r - l) + 18, sy + (b - t) + 22], 14, outline=(225, 30, 45), width=5)
    d.text((sx - l, sy - t + 6), status, font=f3, fill=(225, 30, 45))
    return to_bgra(im)

def otp_banner():
    w, h = 940, 190
    im = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([30, 38, 30 + w, 38 + h], 44, fill=(0, 0, 0, 90))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([30, 30, 30 + w, 30 + h], 44, fill=(248, 248, 250, 250))
    d.rounded_rectangle([62, 62, 62 + 86, 62 + 86], 22, fill=(52, 199, 89))
    d.ellipse([78, 80, 132, 122], fill=(255, 255, 255)); d.polygon([(88, 112), (82, 134), (104, 118)], fill=(255, 255, 255))
    fa = ImageFont.truetype(FONT_SANS, 30); fb = ImageFont.truetype(P('fonts', 'Poppins-SemiBold.ttf'), 33)
    d.text((176, 60), 'MESSAGES', font=fa, fill=(120, 120, 128)); d.text((w - 70, 60), 'now', font=fa, fill=(120, 120, 128))
    d.text((176, 104), 'Your OTP is 482917.', font=ImageFont.truetype(FONT_SANS, 38), fill=(20, 20, 24))
    d.text((176, 152), 'Do not share it with anyone.', font=fb, fill=(70, 70, 78))
    return to_bgra(im)

GFX = {}
def gfx():
    if not GFX:
        GFX['mine'] = tape_label('MINE'); GFX['hers'] = tape_label('HERS'); GFX['strip'] = tape_strip()
        GFX['b1'] = bill_card('ELECTRICITY', '₹2,340', 'DUE TODAY', (245, 166, 35))
        GFX['b2'] = bill_card('WI-FI', '₹999', 'OVERDUE', (52, 120, 246))
        GFX['b3'] = bill_card('GAS', '₹860', 'DUE TODAY', (230, 70, 60))
        GFX['otp'] = otp_banner()
    return GFX

def pop(t, t0, dur=0.22, c1=1.7):
    p = (t - t0) / dur
    if p <= 0: return 0.0, 0.0
    return 0.4 + 0.6 * ease_out_back(p, c1), min(1.0, p * 3)

def draw_extra(frame, ins, t):
    G = gfx()
    if ins.get('extra') == 'fridge':
        sc, al = pop(t, 29.92); paste_scaled(frame, G['mine'], 300, 190, sc * 0.72, al, angle=7)
        sc, al = pop(t, 30.38); paste_scaled(frame, G['hers'], 790, 330, sc * 0.72, al, angle=-6)
        p = (t - 30.87) / 0.25
        if p > 0:
            strip = G['strip']; L = int(min(strip.shape[0], WH - 70) * ease_out_cubic(p))
            if L > 10: paste(frame, strip[:L], WW // 2 - strip.shape[1] // 2, 35)
    if ins.get('extra') == 'otp':
        p = (t - 66.68) / 0.35
        if p > 0:
            y = -150 + (160 - -150) * ease_out_back(p, 1.2)
            paste_scaled(frame, G['otp'], WW / 2, y, 0.8)

def draw_bills(frame, ins, t):
    G = gfx()
    tau = t - ins['s']
    frame[:] = PAPER
    for k, (key, cx, cy, ang, t0) in enumerate([('b1', 215, 290, -6, 0.05), ('b2', 540, 315, 4, 0.55), ('b3', 865, 290, -4, 1.0)]):
        sc, al = pop(tau, t0, 0.26, 1.6)
        paste_scaled(frame, G[key], cx, cy, sc * 0.5, al, angle=ang)

def title_sprite():
    if 'title' in _spr: return _spr['title']
    f1 = ImageFont.truetype(FONT_SANS, 50); f2 = serif(96, 700)
    l1, l2 = 'never move in with your', 'best friend'
    b1, b2 = f1.getbbox(l1), f2.getbbox(l2)
    w = max(b1[2] - b1[0], b2[2] - b2[0]) + 80; h = 190 + 60
    txt1 = Image.new('L', (w, h), 0); ImageDraw.Draw(txt1).text((w / 2 - (b1[2] - b1[0]) / 2 - b1[0], 30 - b1[1]), l1, font=f1, fill=255)
    txt2 = Image.new('L', (w, h), 0); ImageDraw.Draw(txt2).text((w / 2 - (b2[2] - b2[0]) / 2 - b2[0], 112 - b2[1]), l2, font=f2, fill=255)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    a = Image.new('RGBA', (w, h), (255, 255, 255, 255)); a.putalpha(txt1)
    b = Image.new('RGBA', (w, h), MAGENTA + (255,)); b.putalpha(txt2)
    im = Image.alpha_composite(Image.alpha_composite(im, a), b)
    _spr['title'] = to_bgra(im)
    return _spr['title']

def draw_title(frame, t):
    sc, al = pop(t, 0.0, 0.3, 1.4)
    if t < 0.1: sc, al = 1.0, 1.0
    paste_scaled(frame, title_sprite(), W / 2, TITLE_CY, sc, al)

# ---------------------------------------------------------------- old-reference text system
FONT_QUOTE = P('fonts', 'InstrumentSerif-Regular.ttf')
FONT_CAP = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
TITLE_YELLOW = (250, 236, 170)
TITLE = ['storytime - best friend ke saath', 'flat liya aur dosti khatam']

def text_sprite(lines, font, color, shadow=0.75, blur=6, spacing=0.9):
    asc, desc = font.getmetrics(); lh = int((asc + desc) * spacing)
    widths = [font.getbbox(l)[2] - font.getbbox(l)[0] for l in lines]
    pad = 30; w = max(widths) + pad * 2; h = lh * len(lines) + pad * 2
    txt = Image.new('L', (w, h), 0); d = ImageDraw.Draw(txt)
    for i, (l, lw) in enumerate(zip(lines, widths)):
        d.text((w / 2 - lw / 2 - font.getbbox(l)[0], pad + i * lh), l, font=font, fill=255)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sh.putalpha(txt.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(min(255, v * 2.2) * shadow)))
        im = Image.alpha_composite(im, sh)
        sh2 = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sh2.putalpha(txt.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * 0.6 * shadow)))
        im = Image.alpha_composite(im, sh2)
    f = Image.new('RGBA', (w, h), color + (255,)); f.putalpha(txt)
    return to_bgra(Image.alpha_composite(im, f))

# dialogue / punchline lines on the picture: (start, end, text, x, y in window, size)
QUOTES = [
    (5.46, 6.27, 'shift mat ho jaana', 540, 300, 96),
    (11.33, 12.47, 'naya dost\ndhoondhna padega', 540, 300, 92),
    (15.10, 16.57, 'a whole\ndifferent side', 840, 250, 84),
    (20.72, 21.49, 'kharchili aurat', 540, 470, 100),
    (25.41, 27.35, 'namak alag...\nmasala alag...', 540, 300, 92),
    (37.11, 38.67, 'can I use yours?', 830, 230, 76),
    (41.04, 42.80, '"I don\'t like my shampoo\nbottle getting wet"', 540, 470, 66),
    (42.80, 44.70, 'tune uspe paani\nkaise lagne diya??', 865, 250, 76),
    (46.14, 47.58, 'bhai...\nshampoo bottle\nhi toh hai', 245, 300, 74),
    (48.44, 49.76, 'koi passport\nthodi hai', 540, 300, 96),
    (52.62, 53.40, 'bhasad', 830, 300, 120),
    (72.00, 73.17, 'definitely\nnot my thing', 830, 270, 80),
    (77.77, 79.10, 'unlike my\nflat life', 830, 270, 84),
    (82.44, 83.62, 'just live alone.', 540, 470, 100),
    (85.28, 87.10, 'most bizarre\nflatmate story?', 830, 270, 78),
]
_qs = {}
def draw_quotes(win, t):
    shown = False
    for (a, b, txt, x, y, size) in QUOTES:
        if not (a - 0.03 <= t < b): continue
        k = (txt, size)
        if k not in _qs: _qs[k] = text_sprite(txt.split('\n'), ImageFont.truetype(FONT_QUOTE, size), (255, 255, 255), 1.0, 10, 0.82)
        p = (t - a + 0.03) / 0.18
        paste_scaled(win, _qs[k], x, y, 0.94 + 0.06 * ease_out_cubic(p), min(1, p * 1.6))
        shown = True
    return shown

def draw_title(frame, t):
    if t > 3.6: return
    if 'title' not in _spr: _spr['title'] = text_sprite(TITLE, ImageFont.truetype(FONT_CAP, 46), TITLE_YELLOW, 0, 0, 1.1)
    al = 1.0 if t < 3.2 else max(0, 1 - (t - 3.2) / 0.4)
    paste_scaled(frame, _spr['title'], W / 2, 512, 1.0, al)

CAP_FONT = ImageFont.truetype(FONT_CAP, 46)
def draw_plain_captions(frame, t):
    for pg in PAGES:
        if not (pg[0]['page_s'] <= t < pg[0]['page_e']): continue
        text = ' '.join(w['text'] for w in pg)
        k = ('cap', text)
        if k not in _spr:
            words, lines, cur = text.split(), [], ''
            for wd in words:
                trial = (cur + ' ' + wd).strip()
                if CAP_FONT.getbbox(trial)[2] > 860 and cur: lines.append(cur); cur = wd
                else: cur = trial
            lines.append(cur)
            _spr[k] = text_sprite(lines, CAP_FONT, (255, 255, 255), 0, 0, 1.15)
        paste_scaled(frame, _spr[k], W / 2, 1345, 1.0, 1.0)

def polaroid(path, crop, label, w=300, h=340):
    im = Image.open(path).convert('RGB').crop(crop).resize((w, h), Image.LANCZOS)
    im = Image.fromarray(warm(cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR))[..., ::-1])
    card = Image.new('RGBA', (w + 36, h + 96), (250, 248, 242, 255)); card.paste(im, (18, 18))
    f = ImageFont.truetype(FONT_QUOTE, 54); d = ImageDraw.Draw(card)
    lw = f.getbbox(label)[2]; d.text(((w + 36 - lw) / 2, h + 22), label, font=f, fill=(30, 30, 30))
    out = Image.new('RGBA', (card.width + 40, card.height + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([24, 28, 24 + card.width, 28 + card.height], fill=(0, 0, 0, 110))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(10))); out.alpha_composite(card, (20, 20))
    return to_bgra(out)

def draw_photos(win, t):
    if not (17.12 <= t < 18.75): return
    if 'me' not in GFX:
        GFX['me'] = polaroid(P('stills', 'me_raw.png'), (930, 40, 1650, 856), 'me')
        GFX['her'] = polaroid(P('stills', 'her_raw.png'), (110, 0, 600, 555), 'her')
        f = ImageFont.truetype(FONT_MARK, 110)
        im = Image.new('RGBA', (260, 170), (0, 0, 0, 0)); ImageDraw.Draw(im).text((20, 0), 'ex', font=f, fill=(215, 25, 35))
        GFX['ex'] = to_bgra(im)
    sc, al = pop(t, 17.15, 0.25, 1.6); paste_scaled(win, GFX['me'], 200, 300, sc * 0.82, al, angle=-6)
    sc, al = pop(t, 17.40, 0.25, 1.6); paste_scaled(win, GFX['her'], 880, 300, sc * 0.82, al, angle=5)
    sc, al = pop(t, 18.01, 0.18, 2.0); paste_scaled(win, GFX['ex'], 905, 150, sc, al, angle=-12)

# ---------------------------------------------------------------- end cards
def follow_card(tau):
    im = np.zeros((H, W, 3), np.uint8)
    lines = ['FOLLOW', 'FOR', 'MORE']
    f = ImageFont.truetype(FONT_ANTON, 190)
    for k, s in enumerate(lines):
        sc, al = pop(tau, 0.08 + k * 0.12, 0.25, 1.6)
        key = ('follow', s)
        if key not in _spr:
            l, t, r, b = f.getbbox(s); pad = 60
            w, h = r - l + pad * 2, b - t + pad * 2
            txt = Image.new('L', (w, h), 0); ImageDraw.Draw(txt).text((pad - l, pad - t), s, font=f, fill=255)
            glow = Image.new('RGBA', (w, h), (255, 30, 50, 0)); glow.putalpha(txt.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.8)))
            fill = Image.new('RGBA', (w, h), (255, 40, 60, 255)); fill.putalpha(txt)
            hi = Image.new('RGBA', (w, h), (255, 170, 175, 255)); hi.putalpha(txt.filter(ImageFilter.MinFilter(9)).point(lambda v: int(v * 0.35)))
            _spr[key] = to_bgra(Image.alpha_composite(Image.alpha_composite(glow, fill), hi))
        paste_scaled(im, _spr[key], W / 2, 700 + k * 260, sc, al)
    return im

COVER = None
def cover_frame(src_frame_at):
    global COVER
    if COVER is not None: return COVER
    base = head_frame(40.2, src_frame_at(40.2))
    g = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g = np.clip((g - 0.08) * 1.15, 0, 1) ** 1.1
    im = np.zeros((H, W, 3), np.uint8); im[WIN_Y:WIN_Y + WH] = base
    q = text_sprite(['tune uspe paani', 'kaise lagne diya??'], ImageFont.truetype(FONT_QUOTE, 84), (255, 255, 255), 1.0, 10, 0.82)
    paste_scaled(im, q, 830, WIN_Y + 250, 1.0)
    t1 = text_sprite(['storytime - best friend ke saath', 'flat liya aur dosti khatam'], ImageFont.truetype(FONT_CAP, 54), TITLE_YELLOW, 0, 0, 1.1)
    paste_scaled(im, t1, W / 2, 470, 1.0)
    COVER = im
    return COVER
    pil = None; d = None
    fs = ImageFont.truetype(FONT_SANS, 50); fa = ImageFont.truetype(FONT_ANTON, 96)
    t1 = 'THE SHAMPOO BOTTLE STORY'
    l, t, r, b = fs.getbbox(t1); d.text((W / 2 - (r - l) / 2 - l, 280 - t), t1, font=fs, fill=(255, 255, 255))
    box_y = 360
    lines = ['NEVER MOVE IN WITH', 'YOUR BEST FRIEND!']
    widths = [fa.getbbox(s) for s in lines]
    bw = max(bb[2] - bb[0] for bb in widths) + 60
    bh = 2 * 112 + 44
    d.rectangle([W / 2 - bw / 2, box_y, W / 2 + bw / 2, box_y + bh], fill=(255, 255, 255))
    for k, (s, bb) in enumerate(zip(lines, widths)):
        d.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], box_y + 24 + k * 112 - bb[1] + 4), s, font=fa, fill=(205, 16, 32))
    COVER = cv2.cvtColor(np.array(pil.convert('RGB')), cv2.COLOR_RGB2BGR)
    return COVER

# ---------------------------------------------------------------- frame renderer
def insert_at(t):
    for ins in INSERTS:
        if ins['s'] <= t < ins['e']: return ins
    return None

def render(t, src_frame_at):
    ins = insert_at(t)
    if ins is None:
        win = head_frame(min(t, 89.5), src_frame_at(min(t, 89.5)))
        draw_photos(win, t)
    elif ins.get('kind') == 'bills':
        win = np.empty((WH, WW, 3), np.uint8); draw_bills(win, ins, t)
    else:
        m, rim, sh = ins['torn'].mask(t - ins['s'])
        clip = clip_image(ins, t).astype(np.float32)
        clip *= (1 - 0.55 * rim)[..., None]
        paper = PAPER.astype(np.float32) * (1 - 0.13 * sh * (1 - m))[..., None]
        win = (paper * (1 - m[..., None]) + clip * m[..., None]).astype(np.uint8)
        draw_extra(win, ins, t)
    quoted = draw_quotes(win, t)
    fr = np.zeros((H, W, 3), np.uint8)
    s_ = breathe_scale(t) if ins is None else 1.0
    if s_ < 0.999:
        sw, sh_ = int(WW * s_), int(WH * s_)
        small = cv2.resize(win, (sw, sh_), interpolation=cv2.INTER_AREA)
        x0, y0 = (W - sw) // 2, WIN_Y + (WH - sh_) // 2
        fr[y0:y0 + sh_, x0:x0 + sw] = small
    else:
        fr[WIN_Y:WIN_Y + WH] = win
    draw_title(fr, t)
    if not quoted: draw_plain_captions(fr, t)
    return fr

# ---------------------------------------------------------------- sources
class SeqSource:
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                                  stdout=subprocess.PIPE, bufsize=SRC_W * SRC_H * 3 * 2)
        self.i = -1; self.f = None; self.done = False
    def at(self, t):
        want = int(round(t * FPS))
        while self.i < want and not self.done:
            b = self.p.stdout.read(SRC_W * SRC_H * 3)
            if len(b) < SRC_W * SRC_H * 3: self.done = True; break
            self.f = np.frombuffer(b, np.uint8).reshape(SRC_H, SRC_W, 3); self.i += 1
        return self.f

class SeekSource:
    def __init__(self, path): self.cap = cv2.VideoCapture(path)
    def at(self, t):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * FPS)))
        ok, f = self.cap.read(); return f

if __name__ == '__main__':
    mode = sys.argv[2]
    if mode == 'preview':
        os.makedirs(P('prev'), exist_ok=True)
        src = SeekSource(P('sdr_inner.mp4'))
        for ts in sys.argv[3:]:
            if ts == 'cover':
                cv2.imwrite(P('prev', 'cover.png'), cover_frame(src.at)); continue
            t = float(ts)
            cv2.imwrite(P('prev', f'f_{t:06.2f}.png'), render(t, src.at))
    elif mode == 'render':
        os.makedirs(P('build'), exist_ok=True)
        src = SeqSource(P('sdr_inner.mp4'))
        n = int(round(TOTAL * FPS))
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                                '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                                '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                                P('build', 'video.mp4')], stdin=subprocess.PIPE)
        import time; t0 = time.time()
        for i in range(n):
            t = i / FPS
            fr = render(t, src.at)
            enc.stdin.write(np.ascontiguousarray(fr).tobytes())
            if i % 150 == 0: print(f'frame {i}/{n} t={t:.1f} {time.time() - t0:.0f}s', flush=True)
        enc.stdin.close(); enc.wait()
        print('done', time.time() - t0)
        json.dump(dict(total=TOTAL, main_end=MAIN_END, follow_end=FOLLOW_END,
                       inserts=[dict(s=i['s'], e=i['e'], kind=i.get('kind', 'clip'), extra=i.get('extra')) for i in INSERTS]),
                  open(P('build', 'timeline.json'), 'w'))
