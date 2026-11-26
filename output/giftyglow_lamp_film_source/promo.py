"""GiftyGlow product film — built only from the two Krishna-lamp photos.
Hook: lamp starts dark while 'A gift that' types on; on 'glows' it clicks on.
Body: beat-cut macro details (70.6 bpm, cut every 2 beats). End: 'Their name in light', lamp clicks off, logo."""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

D = sys.argv[1]
PREVIEW = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None
W, H, FPS = 1080, 1920, 30
B = 60 / 70.6                      # beat (s)
M = 1.45                           # music drop / lamp switches on
T = [M + B * 2 * k for k in range(1, 9)]   # 3.15 4.85 ... cut points
OFF = M + B * 17                    # lamp switches off (~15.9)
DUR = OFF + 2.6
N = int(DUR * FPS)
FD = D + '/fonts/'

Image.MAX_IMAGE_PIXELS = None
P1 = Image.open(D + '/promo/p1.png').convert('RGB')   # 4672x7008 portrait
P2 = Image.open(D + '/promo/p2.png').convert('RGB')   # 7008x4672 landscape
# extend the dark backdrop above the lamp so the type sits on clean black
_top = np.asarray(P1.crop((0, 0, P1.width, 200)), np.float32).mean(axis=(0, 1))
PAD = 2400
P1PAD = Image.new('RGB', (P1.width, P1.height + PAD), tuple(int(v) for v in _top))
P1PAD.paste(P1, (0, PAD))
_m = Image.linear_gradient('L').resize((P1.width, 300))          # soften the seam
P1PAD.paste(Image.new('RGB', (P1.width, 300), tuple(int(v) for v in _top)), (0, PAD), _m.transpose(Image.FLIP_TOP_BOTTOM))
LOGO = Image.open(D + '/cap/logo_src.png').convert('RGBA')

def ease(x):
    x = min(max(x, 0), 1); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eout(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(a, b, u): return a + (b - a) * u

def win(img, cx, cy, h):
    """9:16 window of height h centred at (cx,cy), clamped, resized to WxH"""
    w = h * W / H
    w, h = min(w, img.width), min(h, img.height)
    l = min(max(cx - w / 2, 0), img.width - w); t = min(max(cy - h / 2, 0), img.height - h)
    return img.resize((W, H), Image.BICUBIC, box=(l, t, l + w, t + h))

# ---------- look ----------
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.55 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)).clip(0.35, 1)[..., None].astype(np.float32)
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]

def bloom(im, amt=0.35):
    a = np.asarray(im, np.float32)
    hi = np.clip(a - 150, 0, None) * 1.6
    hb = np.asarray(Image.fromarray(hi.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28)), np.float32)
    return a + amt * hb

def finish(arr, n):
    a = arr * VIG
    a[..., 0] *= 1.03; a[..., 2] *= 0.95                      # warm grade
    g = GRAIN[n % 8]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    a = a + g * 3.2
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def off_state(arr):
    """lamp switched off: emission gone, faint grey engraving + dim room"""
    lum = arr.mean(axis=2, keepdims=True)
    return arr * 0.045 + lum * 0.06

def level(t, t_on, rev=False):
    """LED switch-on flicker curve 0..~1.15..1 (or reversed for switch-off)"""
    x = t - t_on
    if x < 0: return 1.0 if rev else 0.0
    keys = [(0, .0), (.02, .65), (.06, .12), (.11, .85), (.15, .35), (.21, 1.18), (.55, 1.0)] if not rev else \
           [(0, 1.0), (.03, .25), (.07, .7), (.11, .08), (.16, .3), (.24, 0.0)]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if x < b: return va + (vb - va) * (x - a) / (b - a)
    return keys[-1][1]

# ---------- type ----------
_f = {}
def F(n, s):
    if (n, s) not in _f: _f[(n, s)] = ImageFont.truetype(FD + n, s)
    return _f[(n, s)]
REG, IT, BOLD = 'PlayfairDisplay-400.ttf', 'PlayfairDisplay-900i.ttf', 'PlayfairDisplay-700.ttf'

def word(base, txt, font, x, y_base, t, t0, glow=0.0):
    """pop-on word (ref style: quick scale-settle), x = left, y = baseline"""
    if t < t0: return
    k = eout((t - t0) / 0.18)
    s = 1.12 - 0.12 * k
    f = font
    bb = f.getbbox(txt, anchor='ls')
    pad = 60
    L = Image.new('RGBA', (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(L).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=(255, 255, 255, 255), anchor='ls')
    a = L.getchannel('A')
    sh = Image.new('RGBA', L.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 120 // 255))
    out = Image.new('RGBA', L.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 6))
    if glow > 0:
        g = Image.new('RGBA', L.size, (255, 190, 110, 0)); g.putalpha(a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * glow)))
        out.alpha_composite(g)
    out.alpha_composite(L)
    if s != 1: out = out.resize((int(out.width * s), int(out.height * s)), Image.BICUBIC)
    if k < 1: out.putalpha(out.getchannel('A').point(lambda v: int(v * k)))
    ox, oy = x + bb[0] - pad, y_base + bb[1] - pad
    cxo, cyo = ox + L.width / 2, oy + L.height / 2
    base.alpha_composite(out, (int(cxo - out.width / 2), int(cyo - out.height / 2)))

def hook_text(base, t, alpha_t_out):
    if t >= alpha_t_out + 0.25: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = 0.55 if t >= M else 0.0
    word(lay, 'A', F(REG, 160), 110, 300, t, 0.10)
    word(lay, 'gift', F(IT, 300), 90, 580, t, 0.45, g)
    word(lay, 'that', F(BOLD, 100), after('gift', (IT, 300), 90), 570, t, 0.88, g)
    word(lay, 'glows', F(IT, 300), 290, 850, t, M, g)
    word(lay, 'every night', F(BOLD, 96), 120, 980, t, M + B * 0.6, g)
    if t > alpha_t_out:
        k = 1 - eout((t - alpha_t_out) / 0.25)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * k)))
    base.alpha_composite(lay)

def end_text(base, t, t_out):
    if t >= t_out + 0.3: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    t0 = T[6]
    word(lay, 'Their', F(REG, 160), 110, 300, t, t0 + 0.12, 0.5)
    word(lay, 'name', F(IT, 300), 90, 580, t, t0 + 0.12 + B * 0.5, 0.5)
    word(lay, 'in', F(BOLD, 110), after('name', (IT, 300), 90), 570, t, t0 + 0.12 + B * 1.0, 0.5)
    word(lay, 'light', F(IT, 300), 400, 860, t, t0 + 0.12 + B * 1.5, 0.5)
    if t > t_out:
        k = 1 - eout((t - t_out) / 0.3)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * k)))
    base.alpha_composite(lay)

def tracked(d, cx, cy, text, f, fill, tr):
    ws = [d.textlength(c, font=f) for c in text]; tw = sum(ws) + tr * f.size * (len(text) - 1)
    x = cx - tw / 2
    for c, w in zip(text, ws): d.text((x, cy), c, font=f, fill=fill, anchor='lm'); x += w + tr * f.size

LG = LOGO.resize((640, int(LOGO.height * 640 / LOGO.width)), Image.LANCZOS)
def end_card(base, t, t0):
    if t < t0: return
    a1 = eout((t - t0) / 0.6)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L.alpha_composite(LG, ((W - LG.width) // 2, 760))
    d = ImageDraw.Draw(L)
    d.text((W / 2, 1060), 'Personalise yours', font=F(IT, 96), fill=(255, 236, 205, 255), anchor='mm')
    tracked(d, W / 2, 1190, 'GIFTYGLOW.COM', F('Montserrat-SemiBold.ttf', 38), (255, 200, 120, 255), 0.32)
    k = a1
    L.putalpha(L.getchannel('A').point(lambda v: int(v * k)))
    base.alpha_composite(L, (0, int(30 * (1 - a1))))

def shadow_pass(arr, t, t_mid, dur=0.45, dir=1):
    """a dark soft band sweeps across (like someone walking past camera in the reference)"""
    u = (t - (t_mid - dur / 2)) / dur
    if not (0 <= u <= 1): return arr
    x = (-0.6 + 2.2 * u) * W if dir > 0 else (1.6 - 2.2 * u) * W
    prof = np.exp(-((np.arange(W) - x) / (W * 0.33)) ** 2)[None, :, None]
    return arr * (1 - 0.93 * prof)

def blur(im, r):
    return im.filter(ImageFilter.GaussianBlur(r)) if r > 0.4 else im

def hero_cy(h, disc_screen_y=1060):
    # keep the top of the acrylic disc (P1 y=1752) at a fixed screen height
    top = PAD + 1752 - disc_screen_y * h / H
    return top + h / 2

def after(txt, f, x0, gap=34):
    return x0 + F(*f).getlength(txt) + gap

# ---------- shots ----------
def shot(t):
    if t < T[0]:                       # S0 hero, off -> on
        u = ease(t / T[0])
        h = lerp(7000, 6500, u)
        im = win(P1PAD, 2300, hero_cy(h), h)
        a = bloom(im, 0.30)
        L = level(t, M)
        if 0.5 <= t < 0.68:                      # teaser flicker: the lamp 'tries' to come on
            L = max(L, 0.22 * math.sin(math.pi * (t - 0.5) / 0.18) * (1 if int(t * 60) % 3 else 0.4))
        return off_state(a) * (1 - min(L, 1)) + a * L
    if t < T[1]:                       # S1 wide landscape pan
        u = ease((t - T[0]) / (T[1] - T[0]))
        return bloom(win(P2, lerp(2950, 3950, u), 2420, lerp(4500, 4250, u)), 0.3)
    if t < T[2]:                       # S2 macro peacock feather, tilt up
        u = ease((t - T[1]) / (T[2] - T[1]))
        return bloom(win(P1, 2150, lerp(2350, 1950, u), 2350), 0.4)
    if t < T[3]:                       # S3 macro face + flute, rack focus
        lt = t - T[2]; u = ease(lt / (T[3] - T[2]))
        im = win(P1, 2260, 2720, lerp(2750, 2350, u))
        return bloom(blur(im, 16 * (1 - eout(lt / 0.65))), 0.4)
    if t < T[4]:                       # S4 drift across stars / notes
        u = ease((t - T[3]) / (T[4] - T[3]))
        return bloom(win(P1, lerp(3300, 1500, u), 3150, 2500), 0.4)
    if t < T[5]:                       # S5 base glow -> reflection, tilt down
        u = ease((t - T[4]) / (T[5] - T[4]))
        return bloom(win(P1, 2280, lerp(4150, 4900, u), 2600), 0.35)
    if t < T[6]:                       # S6 hero pull-back on the landscape
        u = eout((t - T[5]) / (T[6] - T[5]))
        h = lerp(2500, 4550, u)
        return bloom(win(P2, 3504, lerp(2250, 2420, u), h), 0.3)
    # S7 end hero: on -> off
    u = ease((t - T[6]) / (DUR - T[6]))
    h = lerp(6900, 6500, u)
    a = bloom(win(P1PAD, 2300, hero_cy(h), h), 0.30)
    L = level(t, OFF, rev=True)
    return off_state(a) * (1 - L) + a * L

def frame(t, n):
    arr = shot(t)
    arr = shadow_pass(arr, t, T[0], 0.5, 1)
    arr = shadow_pass(arr, t, T[4], 0.5, -1)
    # fade from black at the very start
    if t < 0.25: arr = arr * (t / 0.25)
    img = finish(arr, n).convert('RGBA')
    hook_text(img, t, T[0] - 0.22)
    end_text(img, t, OFF + 0.02)
    end_card(img, t, OFF + 0.45)
    if t > DUR - 0.5:
        img = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), img, max((DUR - t) / 0.5, 0))
    return img.convert('RGB')

if PREVIEW:
    for pt in PREVIEW:
        frame(pt, int(pt * FPS)).resize((360, 640)).save(f'{D}/promo/pv_{pt:05.2f}.png')
    sys.exit()

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                        D + '/promo/promo_video.mp4'], stdin=subprocess.PIPE)
for n in range(N):
    enc.stdin.write(frame(n / FPS, n).tobytes())
    if n % 60 == 0: print(n, N, file=sys.stderr)
enc.stdin.close(); enc.wait()
print('DUR', DUR, 'T', [round(x, 2) for x in T], 'OFF', round(OFF, 2))
