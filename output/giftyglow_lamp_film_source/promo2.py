"""GiftyGlow product film v2 — multi-product, built from the Drive product photos.
Hook   : 'Kamna' name lamp is dark while 'A gift that' types on; clicks on at 'glows'.
Swap   : six different lamps swap in the SAME spot on every beat (ref: same table, new vase)
         with 'for every <birthday/name/hero/blessing/prayer/moment>'.
Macro  : name script pan, Shiva face, Krishna face (2 beats each, rack focus).
Colour : warm -> green flip on the beat.
End    : 'Their name in light' on the Yuvraj name lamp, lamp clicks off, logo."""
import sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = sys.argv[1]
PREVIEW = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None
W, H, FPS = 1080, 1920, 30
B = 60 / 70.6
M = 1.45
T_SWAP = M + 2 * B                         # 3.15
SWAPS = [T_SWAP + B * i for i in range(6)] # 3.15 .. 7.40
T_MAC = T_SWAP + 6 * B                     # 8.25
MACS = [T_MAC + 2 * B * i for i in range(3)]
T_COL = T_MAC + 6 * B                      # 13.35
T_END = T_COL + 2 * B                      # 15.05
OFF = T_END + 3 * B                        # 17.60
DUR = OFF + 2.6
N = int(DUR * FPS)
FD = D + '/fonts/'
PH = D + '/photos/'
Image.MAX_IMAGE_PIXELS = None
A = json.load(open(PH + 'align.json'))
HI = {n: Image.open(PH + f'hi/{n}.png').convert('RGB') for n in A}
RAW = {n: ImageOps.exif_transpose(Image.open(PH + f'raw/DSC{n}.JPG')).convert('RGB') for n in ('05567', '05594', '05588')}
LOGO = Image.open(D + '/cap/logo_src.png').convert('RGBA')

def ease(x):
    x = min(max(x, 0), 1); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eout(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(a, b, u): return a + (b - a) * u

# ---------- framing ----------
_bg = {}
def bgcol(n, im):
    if n not in _bg:
        _bg[n] = tuple(int(v) for v in np.asarray(im.crop((0, 0, im.width, 30))).reshape(-1, 3).mean(0))
    return _bg[n]

def crop_pad(img, box, bg, out_size):
    """crop box (may exceed the photo) -> out_size; padding filled with bg and the seam feathered"""
    l, t, r, b = box
    sx, sy = out_size[0] / (r - l), out_size[1] / (b - t)
    il, it, ir, ib = max(l, 0), max(t, 0), min(r, img.width), min(b, img.height)
    out = Image.new('RGB', out_size, bg)
    if ir <= il or ib <= it: return out
    pw, ph = max(1, round((ir - il) * sx)), max(1, round((ib - it) * sy))
    part = img.resize((pw, ph), Image.BICUBIC, box=(il, it, ir, ib))
    px, py = round((il - l) * sx), round((it - t) * sy)
    mask = None
    if it > t + 1:                                   # padding above: feather the photo's top edge
        fe = min(int(ph * 0.18), 260)
        g = np.ones((ph, pw), np.float32); g[:fe] = np.linspace(0, 1, fe)[:, None] ** 1.5
        mask = Image.fromarray((g * 255).astype(np.uint8))
    out.paste(part, (px, py), mask)
    return out

def aligned(n, yb=1560, Ht=820, z=1.0, dx=0):
    im = HI[n]; a = A[n]
    s = Ht * z / (a['base'] - a['top'])
    l = a['cx'] - (540 + dx) / s; t = a['base'] - yb / s
    return crop_pad(im, (l, t, l + W / s, t + H / s), bgcol(n, im), (W, H))

def raw_win(n, cx, cy, h):
    im = RAW[n]; w = h * W / H
    l = min(max(cx - w / 2, 0), im.width - w); t = min(max(cy - h / 2, 0), im.height - h)
    return im.resize((W, H), Image.BICUBIC, box=(l, t, l + w, t + h))

# ---------- look ----------
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.55 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)).clip(0.35, 1)[..., None].astype(np.float32)
rng = np.random.default_rng(3)
GRAIN = [np.repeat(np.repeat(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), 2, 0), 2, 1)[..., None] for _ in range(6)]

def bloom(im, amt=0.33):
    a = np.asarray(im, np.float32)
    hi = np.clip(a - 150, 0, None) * 1.6
    hb = np.asarray(Image.fromarray(hi.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28)), np.float32)
    return a + amt * hb

def finish(arr, n):
    a = arr * VIG
    a[..., 0] *= 1.03; a[..., 2] *= 0.95
    a = a + GRAIN[n % 6] * 3.2
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def off_state(arr):
    lum = arr.mean(axis=2, keepdims=True)
    return arr * 0.045 + lum * 0.06

def level(t, t_on, rev=False):
    x = t - t_on
    if x < 0: return 1.0 if rev else 0.0
    keys = [(0, .0), (.02, .65), (.06, .12), (.11, .85), (.15, .35), (.21, 1.18), (.55, 1.0)] if not rev else \
           [(0, 1.0), (.03, .25), (.07, .7), (.11, .08), (.16, .3), (.24, 0.0)]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if x < b: return va + (vb - va) * (x - a) / (b - a)
    return keys[-1][1]

def shadow_pass(arr, t, t_mid, dur=0.5, dir=1):
    u = (t - (t_mid - dur / 2)) / dur
    if not (0 <= u <= 1): return arr
    x = (-0.6 + 2.2 * u) * W if dir > 0 else (1.6 - 2.2 * u) * W
    prof = np.exp(-((np.arange(W) - x) / (W * 0.33)) ** 2)[None, :, None]
    return arr * (1 - 0.93 * prof)

def blur(im, r): return im.filter(ImageFilter.GaussianBlur(r)) if r > 0.4 else im

# ---------- type ----------
_f = {}
def F(n, s):
    if (n, s) not in _f: _f[(n, s)] = ImageFont.truetype(FD + n, s)
    return _f[(n, s)]
REG, IT, BOLD = 'PlayfairDisplay-400.ttf', 'PlayfairDisplay-900i.ttf', 'PlayfairDisplay-700.ttf'

def word(base, txt, font, x, y_base, t, t0, glow=0.0, center=False, t_out=None):
    if t < t0: return
    if t_out is not None and t >= t_out: return
    k = eout((t - t0) / 0.18)
    s = 1.12 - 0.12 * k
    bb = font.getbbox(txt, anchor='ls'); pad = 60
    L = Image.new('RGBA', (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(L).text((pad - bb[0], pad - bb[1]), txt, font=font, fill=(255, 255, 255, 255), anchor='ls')
    a = L.getchannel('A')
    out = Image.new('RGBA', L.size, (0, 0, 0, 0))
    sh = Image.new('RGBA', L.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 130 // 255))
    out.alpha_composite(sh, (0, 6))
    if glow > 0:
        g = Image.new('RGBA', L.size, (255, 190, 110, 0)); g.putalpha(a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * glow)))
        out.alpha_composite(g)
    out.alpha_composite(L)
    if s != 1: out = out.resize((int(out.width * s), int(out.height * s)), Image.BICUBIC)
    if k < 1: out.putalpha(out.getchannel('A').point(lambda v: int(v * k)))
    if center: x = W / 2 - (bb[2] - bb[0]) / 2 - bb[0]
    ox, oy = x + bb[0] - pad, y_base + bb[1] - pad
    cx, cy = ox + L.width / 2, oy + L.height / 2
    base.alpha_composite(out, (int(cx - out.width / 2), int(cy - out.height / 2)))

def fade_layer(base, lay, t, t_out, d=0.25):
    if t > t_out:
        k = 1 - eout((t - t_out) / d)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * k)))
    base.alpha_composite(lay)

def after(txt, fname, size, x0, gap=34): return x0 + F(fname, size).getlength(txt) + gap

def hook_text(base, t):
    t_out = T_SWAP - 0.2
    if t >= t_out + 0.25: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = 0.55 if t >= M else 0.0
    word(lay, 'A', F(REG, 160), 110, 300, t, 0.10)
    word(lay, 'gift', F(IT, 300), 90, 580, t, 0.45, g)
    word(lay, 'that', F(BOLD, 100), after('gift', IT, 300, 90), 570, t, 0.88, g)
    word(lay, 'glows', F(IT, 300), 290, 850, t, M, g)
    word(lay, 'every night', F(BOLD, 96), 120, 980, t, M + B * 0.6, g)
    fade_layer(base, lay, t, t_out)

SWAP_LAMPS = ['05553', '05567', '05575', '05588', '05595', '05613']
SWAP_WORDS = ['birthday', 'name', 'hero', 'blessing', 'prayer', 'moment']
def swap_text(base, t):
    if not (SWAPS[0] <= t < T_MAC + 0.25): return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    word(lay, 'for every', F(BOLD, 96), 0, 360, t, SWAPS[0] + 0.05, 0.4, center=True)
    for i, w in enumerate(SWAP_WORDS):
        t0 = SWAPS[i]; t1 = SWAPS[i + 1] if i + 1 < len(SWAPS) else T_MAC
        word(lay, w, F(IT, 230), 0, 610, t, t0 + 0.02, 0.45, center=True, t_out=t1)
    fade_layer(base, lay, t, T_MAC - 0.22)

def colour_text(base, t):
    if not (T_COL <= t < T_END + 0.25): return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    word(lay, 'glow in', F(BOLD, 96), 0, 360, t, T_COL + 0.05, 0.4, center=True)
    word(lay, 'warm white', F(IT, 190), 0, 590, t, T_COL + 0.08, 0.45, center=True, t_out=T_COL + B)
    word(lay, 'colour', F(IT, 230), 0, 610, t, T_COL + B + 0.02, 0.45, center=True)
    fade_layer(base, lay, t, T_END - 0.2)

def end_text(base, t):
    t_out = OFF + 0.02
    if not (T_END <= t < t_out + 0.3): return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); t0 = T_END
    word(lay, 'Their', F(REG, 160), 110, 300, t, t0 + 0.12, 0.5)
    word(lay, 'name', F(IT, 300), 90, 580, t, t0 + 0.12 + B * 0.5, 0.5)
    word(lay, 'in', F(BOLD, 110), after('name', IT, 300, 90), 570, t, t0 + 0.12 + B * 1.0, 0.5)
    word(lay, 'light', F(IT, 300), 400, 860, t, t0 + 0.12 + B * 1.5, 0.5)
    fade_layer(base, lay, t, t_out, 0.3)

def tracked(d, cx, cy, text, f, fill, tr):
    ws = [d.textlength(c, font=f) for c in text]; tw = sum(ws) + tr * f.size * (len(text) - 1)
    x = cx - tw / 2
    for c, w in zip(text, ws): d.text((x, cy), c, font=f, fill=fill, anchor='lm'); x += w + tr * f.size

LG = LOGO.resize((640, int(LOGO.height * 640 / LOGO.width)), Image.LANCZOS)
def end_card(base, t):
    t0 = OFF + 0.45
    if t < t0: return
    a1 = eout((t - t0) / 0.6)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L.alpha_composite(LG, ((W - LG.width) // 2, 760))
    d = ImageDraw.Draw(L)
    d.text((W / 2, 1060), 'Personalise yours', font=F(IT, 96), fill=(255, 236, 205, 255), anchor='mm')
    tracked(d, W / 2, 1190, 'GIFTYGLOW.COM', F('Montserrat-SemiBold.ttf', 38), (255, 200, 120, 255), 0.32)
    L.putalpha(L.getchannel('A').point(lambda v: int(v * a1)))
    base.alpha_composite(L, (0, int(30 * (1 - a1))))

# ---------- shots ----------
def shot(t):
    if t < T_SWAP:                                         # hook: Kamna name lamp off -> on
        u = ease(t / T_SWAP)
        a = bloom(aligned('05519', yb=1660, Ht=lerp(520, 560, u)), 0.30)
        L = level(t, M)
        if 0.5 <= t < 0.68:
            L = max(L, 0.22 * math.sin(math.pi * (t - 0.5) / 0.18) * (1 if int(t * 60) % 3 else 0.4))
        return off_state(a) * (1 - min(L, 1)) + a * L
    if t < T_MAC:                                          # same-spot swaps, slow continuous push
        i = min(int((t - T_SWAP) / B), 5)
        u = (t - T_SWAP) / (T_MAC - T_SWAP)
        return bloom(aligned(SWAP_LAMPS[i], yb=1580, Ht=780, z=1.0 + 0.07 * u), 0.33)
    if t < MACS[1]:                                        # name script: track along 'Yuvraj'
        lt = t - MACS[0]; u = ease(lt / (2 * B))
        im = raw_win('05567', lerp(1650, 2850, u), 3000, 2500)
        return bloom(blur(im, 12 * (1 - eout(lt / 0.5))), 0.4)
    if t < MACS[2]:                                        # Shiva face, tilt down
        u = ease((t - MACS[1]) / (2 * B))
        return bloom(raw_win('05594', 2250, lerp(2150, 2650, u), lerp(2600, 2350, u)), 0.38)
    if t < T_COL:                                          # Krishna face, rack focus + push
        lt = t - MACS[2]; u = ease(lt / (2 * B))
        im = raw_win('05588', 2260, 2870, lerp(2700, 2300, u))
        return bloom(blur(im, 14 * (1 - eout(lt / 0.6))), 0.4)
    if t < T_END:                                          # colour flip warm -> green
        u = (t - T_COL) / (2 * B)
        n = '05520' if t < T_COL + B else '05521'
        return bloom(aligned(n, yb=1600, Ht=500, z=1.0 + 0.05 * u), 0.3)
    u = ease((t - T_END) / (DUR - T_END))                  # end: Yuvraj name lamp, on -> off
    a = bloom(aligned('05566', yb=1580, Ht=lerp(800, 840, u)), 0.30)
    L = level(t, OFF, rev=True)
    return off_state(a) * (1 - L) + a * L

def frame(t, n):
    arr = shot(t)
    arr = shadow_pass(arr, t, T_SWAP, 0.5, 1)
    arr = shadow_pass(arr, t, T_MAC, 0.5, -1)
    arr = shadow_pass(arr, t, T_END, 0.5, 1)
    if t < 0.25: arr = arr * (t / 0.25)
    img = finish(arr, n).convert('RGBA')
    hook_text(img, t); swap_text(img, t); colour_text(img, t); end_text(img, t); end_card(img, t)
    if t > DUR - 0.5:
        img = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), img, max((DUR - t) / 0.5, 0))
    return img.convert('RGB')

if PREVIEW:
    for pt in PREVIEW:
        frame(pt, int(pt * FPS)).resize((360, 640)).save(f'{D}/promo/v2_{pt:05.2f}.png')
    sys.exit()

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                        D + '/promo/promo2_video.mp4'], stdin=subprocess.PIPE)
for n in range(N):
    enc.stdin.write(frame(n / FPS, n).tobytes())
    if n % 90 == 0: print(n, N, file=sys.stderr)
enc.stdin.close(); enc.wait()
print('DUR', round(DUR, 3), 'SWAPS', [round(x, 2) for x in SWAPS], 'MACS', [round(x, 2) for x in MACS],
      'COL', round(T_COL, 2), 'END', round(T_END, 2), 'OFF', round(OFF, 2))
