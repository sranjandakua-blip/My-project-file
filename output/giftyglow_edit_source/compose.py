import json, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
D = sys.argv[1] if len(sys.argv) > 1 else '.'
CAP = D + '/cap/'
DUR = 25.233
N = int(DUR * FPS)
PREVIEW = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None

GOLD = (255, 190, 70)
INK = (28, 22, 16)
FB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
FBL = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
FSB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
font = lambda p, s: ImageFont.truetype(p, s)

def ease(x):  # easeInOutCubic
    x = min(max(x, 0), 1)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

def eout(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3

def spring(x):  # overshoot pop 0->1
    x = max(x, 0)
    if x >= 1: return 1.0
    return 1 - math.exp(-6 * x) * math.cos(9 * x)

# ---------- assets ----------
def load(p):
    return Image.open(CAP + p).convert('RGB')

pages = {k: load(k + '.png') for k in ['home_full', 'prod_full', 'birthday-lamps', 'couple-lamps',
                                         'festival-religious', 'couple-lamps_happy-wedding-day-couple']}
cust = [load(f'cust_{i:02d}.png') for i in range(13)]

def photo(p, w):
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)

P1 = photo(D + '/dl/19sM-5oJrKtPFToB_UBak_DPBYs1b_AWs.jpg', 1400)   # portrait
P2 = photo(D + '/dl/1vsSAudq2S7Qxm3XzH4S3BGuhcFOGzcqN.jpg', 1600)   # landscape
logo = Image.open(CAP + 'logo_src.png').convert('RGBA')

def view(img, cx, cy, z, x0=None):
    """crop a W/z x H/z window centred at (cx,cy) of img, return WxH"""
    cw, ch = min(W / z, img.width), min(H / z, img.height)
    l = min(max(cx - cw / 2, 0), img.width - cw)
    t = min(max(cy - ch / 2, 0), img.height - ch)
    return img.resize((W, H), Image.BICUBIC, box=(l, t, l + cw, t + ch))

def page_scroll(img, y, z=1.0):
    return view(img, img.width / 2, y + H / 2 / 1, z) if z == 1 else view(img, img.width / 2, y + H / 2, z)

# ---------- face video ----------
face_proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', D + '/cut.mov', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             stdout=subprocess.PIPE)
def face_frames():
    while True:
        b = face_proc.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield Image.frombuffer('RGB', (W, H), b)
FF = face_frames()
last_face = [None]

def face(z, cy=820):
    return view(last_face[0], W / 2, cy, z)

# ---------- graphics ----------
def rounded(im, r):
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.convert('RGBA'); out.putalpha(m); return out

def shadow_paste(base, card, x, y, blur=28, off=14, alpha=150):
    sh = Image.new('RGBA', (card.width + blur * 4, card.height + blur * 4), (0, 0, 0, 0))
    a = card.split()[-1].point(lambda v: alpha if v > 0 else 0)
    sh.paste((0, 0, 0, 255), (blur * 2, blur * 2), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh, (int(x - blur * 2), int(y - blur * 2 + off)))
    base.alpha_composite(card, (int(x), int(y)))

def scaled_center(base, card, cx, cy, s, shadow=True):
    if s <= 0.02: return
    c = card.resize((max(1, int(card.width * s)), max(1, int(card.height * s))), Image.BICUBIC)
    x, y = cx - c.width / 2, cy - c.height / 2
    if shadow: shadow_paste(base, c, x, y)
    else: base.alpha_composite(c, (int(x), int(y)))

def pill(text, fnt, fg, bg, padx=44, pady=26, icon=None):
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bb = d0.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new('RGBA', (tw + padx * 2, th + pady * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=bg)
    d.text((padx - bb[0], pady - bb[1]), text, font=fnt, fill=fg)
    return im

# logo badge
lg = logo.resize((560, int(logo.height * 560 / logo.width)), Image.LANCZOS)
LOGO_CARD = Image.new('RGBA', (lg.width + 80, lg.height + 50), (0, 0, 0, 0))
ImageDraw.Draw(LOGO_CARD).rounded_rectangle((0, 0, LOGO_CARD.width - 1, LOGO_CARD.height - 1), 36, fill=(255, 255, 255, 245))
LOGO_CARD.alpha_composite(lg, (40, 25))

# price sticker
def price_card():
    f1, f2 = font(FSB, 40), font(FB, 120)
    im = Image.new('RGBA', (470, 270), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 469, 269), 40, fill=GOLD + (255,))
    d.text((235, 62), 'STARTING AT JUST', font=f1, fill=INK, anchor='mm')
    d.text((235, 170), '₹299', font=f2, fill=INK, anchor='mm')
    return im.rotate(-4, resample=Image.BICUBIC, expand=True)
PRICE = price_card()
URL = pill('giftyglow.com', font(FB, 64), (255, 255, 255), (20, 20, 20, 235), padx=54, pady=30)

# end card static parts
def end_bg():
    bg = P2.resize((int(P2.width * H / P2.height), H), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new('RGB', (W, H), (12, 8, 4)), 0.45)
    return bg
END_BG = end_bg()
from PIL import ImageEnhance
_c = P2.crop((int(P2.width*0.24), int(P2.height*0.18), int(P2.width*0.76), int(P2.height*0.90)))
_c = ImageEnhance.Brightness(_c).enhance(1.25)
END_PHOTO = rounded(_c.resize((900, int(_c.height * 900 / _c.width)), Image.LANCZOS), 48)

# ---------- captions ----------
words = json.load(open(D + '/cutwords.json'))
fix = {'favorite': 'favourite', 'personalize': 'personalise', 'personalized': 'personalised', '299': '₹299',
       'giftyglow': 'giftyglow', '.com': '.com'}
toks = []
for w in words:
    t = w['w']
    core = t.strip('.,?!')
    t = t.replace(core, fix.get(core, core))
    if t == '.com' and toks:  # merge with previous
        toks[-1]['w'] += '.com'; toks[-1]['e'] = w['e']; continue
    toks.append(dict(w=t, s=w['s'], e=w['e']))
# hand-phrased caption groups (token index ranges)
G = [(0,1),(2,3),(4,5),(6,7),(8,10),(11,13),(14,16),(17,19),(20,22),(23,24),(25,28),(29,31),(32,33),(34,35),(36,37),
     (38,39),(40,41),(42,44),(45,46),(47,48),(49,51),(52,52),(53,54),(55,56),(57,58),(59,61),(62,62),(63,64),(65,66),(67,68),(69,70)]
assert len(toks) == 71, len(toks)
chunks = [toks[a_:b_ + 1] for a_, b_ in G]
for i, c in enumerate(chunks):
    c_start = c[0]['s']
    c_end = chunks[i + 1][0]['s'] if i + 1 < len(chunks) else DUR
    if c_end - c[-1]['e'] > 0.6: c_end = c[-1]['e'] + 0.35
    c.append({'span': (c_start, c_end)})
CF = font(FB, 84)

def draw_caption(base, t, y=1430):
    for c in chunks:
        s, e = c[-1]['span']
        if s <= t < e:
            ws = c[:-1]
            d = ImageDraw.Draw(base)
            sp = 22
            sizes = [d.textbbox((0, 0), w['w'], font=CF) for w in ws]
            tw = sum(b[2] - b[0] for b in sizes) + sp * (len(ws) - 1)
            scale_in = (0.85 + 0.15 * eout((t - s) / 0.12)) * min(1, 960 / tw)
            x = W / 2 - tw / 2 if tw < W - 20 else 10
            LW = int(max(W, tw + 40)); x += (LW - W) / 2 if tw >= W - 20 else 0
            layer = Image.new('RGBA', (LW, 220), (0, 0, 0, 0))
            dl = ImageDraw.Draw(layer)
            for w, b in zip(ws, sizes):
                active = w['s'] - 0.03 <= t < max(w['e'], w['s'] + 0.15)
                col = GOLD if active else (255, 255, 255)
                dl.text((x - b[0], 110), w['w'], font=CF, fill=col, anchor='ls', stroke_width=9, stroke_fill=(0, 0, 0))
                x += b[2] - b[0] + sp
            if scale_in < 1:
                layer = layer.resize((int(LW * scale_in), int(220 * scale_in)), Image.BICUBIC)
            base.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(y - layer.height / 2)))
            return

# ---------- timeline ----------
# (start, end, kind, params)
SH = [
    (0.00, 3.00, 'face', dict(z0=1.0, z1=1.08)),
    (3.00, 7.20, 'prod', {}),
    (7.20, 8.60, 'face', dict(z0=1.22, z1=1.26)),
    (8.60, 11.20, 'face', dict(z0=1.06, z1=1.12, logo=10.45)),
    (11.20, 12.90, 'scroll', dict(img='home_full', y0=1550, y1=3500)),
    (12.90, 14.80, 'cust', {}),
    (14.80, 16.55, 'photo1', {}),
    (16.55, 17.55, 'scroll', dict(img='birthday-lamps', y0=420, y1=900)),
    (17.55, 18.25, 'zoomin', dict(img='couple-lamps_happy-wedding-day-couple', cx=560, cy=650, z0=1.0, z1=1.35)),
    (18.25, 18.85, 'scroll', dict(img='couple-lamps', y0=500, y1=900)),
    (18.85, 20.10, 'scroll', dict(img='festival-religious', y0=250, y1=800)),
    (20.10, 22.62, 'face', dict(z0=1.12, z1=1.18, price=20.90, url=21.72)),
    (22.62, DUR + 1, 'end', {}),
]
CUST_T = [(12.90, 0), (13.18, 1)] + [(13.42 + i * 0.105, 2 + i) for i in range(10)] + [(14.52, 12)]
SFX = []  # (time, kind)

def frame(t):
    for (s, e, k, p) in SH:
        if s <= t < e: break
    lt, L = t - s, e - s
    u = lt / L
    if k == 'face':
        img = face(p['z0'] + (p['z1'] - p['z0']) * u)
    elif k == 'prod':
        im = pages['prod_full']
        # hold page top, then push into the product image (names + date)
        z = 1.0 + 0.95 * ease((lt - 0.7) / 2.2)
        cy = 960 + (640 - 960) * ease((lt - 0.7) / 2.2)
        cx = 540 + (560 - 540) * ease((lt - 0.7) / 2.2)
        img = view(im, cx, cy, z + 0.03 * lt / L)
    elif k == 'scroll':
        im = pages[p['img']]
        y = p['y0'] + (p['y1'] - p['y0']) * ease(u)
        img = view(im, W / 2, y + H / 2, 1.0)
    elif k == 'zoomin':
        im = pages[p['img']]
        z = p['z0'] + (p['z1'] - p['z0']) * eout(u)
        img = view(im, p['cx'], p['cy'] + (960 - p['cy']) * (1 - eout(u)), z)
    elif k == 'cust':
        idx = 0
        for (ct, ci) in CUST_T:
            if t >= ct: idx = ci
        img = view(cust[idx], 540, 960, 1.0 + 0.06 * u)
    elif k == 'photo1':
        z = 1.0 + 0.12 * u
        im = P1
        # fit width 1400 => scale to cover 1080x1920
        sc = H / im.height if im.width * H / im.height >= W else W / im.width
        img = view(im, im.width / 2, im.height * 0.52, sc * z)
    elif k == 'end':
        img = END_BG.copy()
    base = img.convert('RGBA')
    # entry pop for b-roll cuts
    if k in ('prod', 'scroll', 'zoomin', 'cust', 'photo1') and lt < 0.2:
        s_ = 1.06 - 0.06 * eout(lt / 0.2)
        b2 = base.resize((int(W * s_), int(H * s_)), Image.BICUBIC)
        base = b2.crop(((b2.width - W) // 2, (b2.height - H) // 2, (b2.width - W) // 2 + W, (b2.height - H) // 2 + H))
    if k == 'photo1':
        # warm vignette
        pass
    if k == 'face' and 'logo' in p and t >= p['logo']:
        sc = spring((t - p['logo']) / 0.5)
        scaled_center(base, LOGO_CARD, W / 2, 330, sc)
    if k == 'face' and 'price' in p and t >= p['price']:
        sc = spring((t - p['price']) / 0.5)
        scaled_center(base, PRICE, W - 290, 300, sc)
    if k == 'face' and 'url' in p and t >= p['url']:
        sc = spring((t - p['url']) / 0.5)
        scaled_center(base, URL, W / 2, 1610, sc)
    if k == 'end':
        a = eout(lt / 0.45)
        sc = 0.85 + 0.15 * spring(lt / 0.6)
        ph = END_PHOTO
        scaled_center(base, ph, W / 2, 790 + 60 * (1 - a), sc)
        scaled_center(base, LOGO_CARD, W / 2, 210, spring((lt - 0.15) / 0.5))
        scaled_center(base, URL, W / 2, 1330, spring((lt - 0.35) / 0.5))
        d = ImageDraw.Draw(base)
        if lt > 0.5:
            d.text((W / 2, 1720), 'Name  •  Date  •  Design', font=font(FSB, 44),
                   fill=(255, 230, 190, int(255 * eout((lt - 0.5) / 0.4))), anchor='mm')
    draw_caption(base, t, y=1430 if k != 'end' else 1560)
    # fade out last 0.35s
    if t > DUR - 0.35:
        f = (DUR - t) / 0.35
        base = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), base, max(f, 0))
    return base.convert('RGB')

if PREVIEW:
    i = 0
    for n in range(N):
        t = n / FPS
        last_face[0] = next(FF)
        for pt in PREVIEW:
            if abs(t - pt) < 0.5 / FPS:
                frame(t).resize((360, 640)).save(f'{D}/prev_{pt:05.2f}.png')
    sys.exit()

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                        D + '/video_only.mp4'], stdin=subprocess.PIPE)
for n in range(N):
    t = n / FPS
    try: last_face[0] = next(FF)
    except StopIteration: pass
    enc.stdin.write(frame(t).tobytes())
    if n % 150 == 0: print(n, file=sys.stderr)
enc.stdin.close(); enc.wait()
json.dump([(s, k) for (s, e, k, p) in SH], open(D + '/shots.json', 'w'))
