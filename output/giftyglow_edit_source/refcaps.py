# Reference-style keyword captions (serif + glow hero word, gold script + block band,
# yellow highlight box, frosted glass pill, 3D bubble price, colour emoji stickers)
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

def setup(D, W_, H_, eout_, spring_):
    global FD, W, H, eout, spring
    FD, W, H, eout, spring = D + '/fonts/', W_, H_, eout_, spring_

_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        p = name if name.startswith('/') else FD + name
        _fc[k] = ImageFont.truetype(p, size)
    return _fc[k]

SERIF, SERIFB = 'PlayfairDisplay-400.ttf', 'PlayfairDisplay-900.ttf'
SCRIPT, BLOCK = 'Courgette-400.ttf', 'RussoOne-400.ttf'
POP, POPX, BUB = 'Poppins-700.ttf', 'Poppins-800.ttf', 'LilitaOne-400.ttf'
MBLACK = 'Montserrat-Black.ttf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
YELLOW = (255, 226, 60)

def fa(t, t0, d=0.3): return eout((t - t0) / d)

def text_img(text, f, fill, track=0.0, pad=40, stroke=0, stroke_fill=None):
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    asc, desc = f.getmetrics()
    if track == 0:
        tw = d0.textlength(text, font=f)
    else:
        ws = [d0.textlength(ch, font=f) for ch in text]
        tw = sum(ws) + track * f.size * (len(text) - 1)
    im = Image.new('RGBA', (int(tw + 2 * pad), int(asc + desc + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track == 0:
        d.text((pad, pad), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    else:
        x = pad
        for ch, w in zip(text, ws):
            d.text((x, pad), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += w + track * f.size
    return im

def shadowed(im, blur=10, alpha=170, off=(0, 6), color=(0, 0, 0)):
    a = im.getchannel('A')
    sh = Image.new('RGBA', im.size, color + (0,))
    sh.putalpha(a.point(lambda v: v * alpha // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)) if blur else sh
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, off) if off != (0, 0) else out.alpha_composite(sh)
    out.alpha_composite(im)
    return out

def mul_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * max(a, 0)))); return im

def place(base, im, cx, cy, alpha=1.0, scale=1.0, rot=0, anchor='c'):
    if alpha <= 0.01 or scale <= 0.02: return
    if scale != 1: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    im = mul_alpha(im, alpha)
    x = cx - im.width / 2 if anchor == 'c' else cx - 40 * scale
    base.alpha_composite(im, (int(x), int(cy - im.height / 2)))

# ---------- styles ----------
def serif_in(base, text, t, t0, cx, cy, size=78, anchor='c'):
    """classic serif, letter-spacing tightens as it fades in (ref: 'Special One')"""
    if t < t0: return
    k = fa(t, t0, 0.45)
    im = text_img(text, F(SERIF, size), (255, 255, 255, 255), track=0.02 + 0.45 * (1 - k))
    place(base, shadowed(im, 12, 190, (0, 5)), cx, cy, alpha=k, anchor=anchor)

_glow = {}
def glow_word(base, text, t, t0, cx, cy, size=200, top=(255, 255, 255), bot=(255, 205, 120), glow=(255, 160, 50)):
    """huge heavy serif with gradient fill, outer glow and a shine sweep (ref: 'GIFT')"""
    if t < t0: return
    key = (text, size, top, bot, glow)
    if key not in _glow:
        m = text_img(text, F(SERIFB, size), (255, 255, 255, 255), track=0.01, pad=90).getchannel('A')
        bb = m.getbbox()
        grad = Image.new('RGBA', m.size)
        gd = ImageDraw.Draw(grad)
        for y in range(m.size[1]):
            u = min(max((y - bb[1]) / max(1, bb[3] - bb[1]), 0), 1)
            c = tuple(int(top[i] + (bot[i] - top[i]) * u) for i in range(3))
            gd.line((0, y, m.size[0], y), fill=c + (255,))
        fill = Image.new('RGBA', m.size, (0, 0, 0, 0)); fill.paste(grad, (0, 0), m)
        g1 = Image.new('RGBA', m.size, glow + (0,)); g1.putalpha(m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, v * 2)))
        g2 = Image.new('RGBA', m.size, (0, 0, 0, 0)); g2.putalpha(m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 150 // 255))
        _glow[key] = (m, fill, g1, g2)
    m, fill, g1, g2 = _glow[key]
    lt = t - t0
    k = fa(t, t0, 0.4)
    out = Image.new('RGBA', m.size, (0, 0, 0, 0))
    out.alpha_composite(g2, (0, 8)); out.alpha_composite(mul_alpha(g1, 0.9))
    out.alpha_composite(fill)
    # shine sweep
    sx = (-0.3 + 1.6 * min(lt / 0.9, 1)) * m.size[0]
    if lt < 0.95:
        band = Image.new('L', m.size, 0); bd = ImageDraw.Draw(band)
        bd.polygon([(sx - 60, 0), (sx + 20, 0), (sx - 80 + 20, m.size[1]), (sx - 140, m.size[1])], fill=210)
        band = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(12)), m)
        wl = Image.new('RGBA', m.size, (255, 255, 255, 0)); wl.putalpha(band)
        out.alpha_composite(wl)
    place(base, out, cx, cy, alpha=k, scale=1.18 - 0.18 * k)

def script_line(base, text, t, t0, cx, cy, size=92, color=YELLOW):
    """gold casual script with crisp dark drop shadow, written on left->right (ref: 'kaise bhi ise')"""
    if t < t0: return
    im = text_img(text, F(SCRIPT, size), color + (255,))
    im = shadowed(im, 2, 230, (4, 5), (40, 20, 0))
    k = fa(t, t0, 0.4)
    w = int(im.width * (0.15 + 0.85 * k))
    mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).rectangle((0, 0, w, im.height), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(14))
    im = im.copy(); im.putalpha(ImageChops.multiply(im.getchannel('A'), mask))
    place(base, im, cx, cy)

def block_band(base, text, t, t0, cy, size=170, band=(186, 150, 236)):
    """lavender gradient band + heavy block word (ref: 'DESIGN')"""
    if t < t0: return
    k = fa(t, t0, 0.35)
    bh = int(size * 1.6)
    b = Image.new('RGBA', (W, bh), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
    for y in range(bh):
        u = y / bh
        a = int(225 * (1 - u) ** 1.3)
        c = tuple(int(band[i] * (1 - 0.55 * u)) for i in range(3))
        bd.line((0, y, W, y), fill=c + (a,))
    # wipe from centre
    half = int(W / 2 * k) + 1
    m = Image.new('L', (W, bh), 0); ImageDraw.Draw(m).rectangle((W // 2 - half, 0, W // 2 + half, bh), fill=255)
    b.putalpha(ImageChops.multiply(b.getchannel('A'), m))
    base.alpha_composite(b, (0, int(cy - bh * 0.42)))
    im = shadowed(text_img(text, F(BLOCK, size), (255, 255, 255, 255), track=0.02), 8, 120, (0, 6))
    place(base, im, W / 2, cy + 40 * (1 - fa(t, t0 + 0.08, 0.3)), alpha=fa(t, t0 + 0.08, 0.3))

def highlight(base, text, t, t0, cx, cy, size=62, t_end=None):
    """black bold text on a yellow box (ref: 'guess what??')"""
    if t < t0: return
    f = F(POP, size)
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    bb = d0.textbbox((0, 0), text, font=f)
    px, py = 22, 12
    im = Image.new('RGBA', (bb[2] - bb[0] + 2 * px, bb[3] - bb[1] + 2 * py), (255, 229, 0, 255))
    ImageDraw.Draw(im).text((px - bb[0], py - bb[1]), text, font=f, fill=(0, 0, 0))
    s = spring((t - t0) / 0.4)
    a = 1.0 if t_end is None else 1 - fa(t, t_end - 0.12, 0.12)
    place(base, shadowed(im, 14, 110, (0, 8)), cx, cy, alpha=a, scale=s)

def glass_pill(base, lines, t, t0, cx, cy, size=62, width=820):
    """frosted glass card with stacked bold white lines (ref: 'Cute unique customised gifts')"""
    if t < t0: return
    f = F(POPX, size)
    lh = int(size * 1.22)
    h = lh * len(lines) + 100
    x0, y0 = int(cx - width / 2), int(cy - h / 2)
    s = spring((t - t0) / 0.45)
    if s < 0.98:
        w2, h2 = int(width * s), int(h * s)
        x0, y0 = int(cx - w2 / 2), int(cy - h2 / 2)
    else:
        w2, h2 = width, h
    if w2 < 20: return
    region = base.crop((x0, y0, x0 + w2, y0 + h2)).filter(ImageFilter.GaussianBlur(22))
    card = Image.new('RGBA', (w2, h2), (0, 0, 0, 0))
    card.alpha_composite(region.convert('RGBA'))
    ov = Image.new('RGBA', (w2, h2), (255, 255, 255, 70)); card.alpha_composite(ov)
    mask = Image.new('L', (w2, h2), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, w2 - 1, h2 - 1), int(44 * s), fill=255)
    card.putalpha(mask)
    ImageDraw.Draw(card).rounded_rectangle((1, 1, w2 - 2, h2 - 2), int(44 * s), outline=(255, 255, 255, 170), width=3)
    # soft drop shadow
    sh = Image.new('RGBA', (w2 + 80, h2 + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, w2 + 40, h2 + 40), 44, fill=(0, 0, 0, 90))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (x0 - 40, y0 - 40))
    base.alpha_composite(card, (x0, y0))
    if s < 0.98: return
    for i, (txt, tl) in enumerate(lines):
        if t < tl: continue
        k = fa(t, tl, 0.3)
        im = shadowed(text_img(txt, f, (255, 255, 255, 255), track=0.01 + 0.3 * (1 - k)), 8, 150, (0, 4))
        place(base, im, cx, y0 + 50 + lh * i + lh / 2 + 18 * (1 - k), alpha=k)

_bub = {}
def bubble_price(base, t, t0, cx, cy, size=230):
    """chunky 3D orange price (ref: '10 OFF')"""
    if t < t0: return
    if 'img' not in _bub:
        f1, f2 = F(MBLACK, int(size * 0.8)), F(BUB, size)
        a = text_img('₹', f1, (255, 255, 255, 255), pad=0)
        b = text_img('299', f2, (255, 255, 255, 255), pad=0)
        pad = 60
        m = Image.new('L', (a.width + b.width + 2 * pad, max(a.height, b.height) + 2 * pad), 0)
        m.paste(a.getchannel('A'), (pad, pad + (b.height - a.height) // 2 + 14))
        m.paste(b.getchannel('A'), (pad + a.width - 6, pad))
        out = Image.new('RGBA', (m.width + 30, m.height + 30), (0, 0, 0, 0))
        outline = m.filter(ImageFilter.MaxFilter(15))
        ex = Image.new('RGBA', m.size, (150, 55, 0, 255))
        for i in range(18, 0, -1):
            out.paste(ex, (int(i * 0.5), i), outline)
        out.paste(Image.new('RGBA', m.size, (255, 255, 255, 255)), (0, 0), outline)
        grad = Image.new('RGBA', m.size); gd = ImageDraw.Draw(grad)
        bb = m.getbbox()
        for y in range(m.size[1]):
            u = min(max((y - bb[1]) / (bb[3] - bb[1]), 0), 1)
            gd.line((0, y, m.size[0], y), fill=(255, int(215 - 110 * u), int(70 - 60 * u), 255))
        out.paste(grad, (0, 0), m)
        # glossy highlight on upper half
        hl = Image.new('L', m.size, 0); ImageDraw.Draw(hl).rectangle((0, 0, m.size[0], bb[1] + (bb[3] - bb[1]) * 0.38), fill=90)
        hl = ImageChops.multiply(hl, m.filter(ImageFilter.MinFilter(9)))
        out.paste(Image.new('RGBA', m.size, (255, 255, 255, 255)), (0, 0), hl)
        _bub['img'] = shadowed(out, 16, 140, (0, 14))
    s = spring((t - t0) / 0.5)
    place(base, _bub['img'], cx, cy, scale=s, rot=6 - 2 * s)

_em = {}
def emoji(base, ch, t, t0, cx, cy, size=170, rot=-10):
    if t < t0: return
    if ch not in _em:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor='mm')
        _em[ch] = shadowed(im.crop(im.getbbox()), 6, 120, (0, 6))
    im = _em[ch]
    s = spring((t - t0) / 0.5)
    sc = size / im.width * s
    wob = 4 * math.sin((t - t0) * 5)
    place(base, im, cx, cy, scale=sc, rot=rot + wob)

# ---------- the beats for this edit ----------
def draw(base, t, k, shot_start, shot_end):
    def within(a, b): return a <= t < b
    if within(0.0, 1.95):            # Imagine GIFTING 🎁
        serif_in(base, 'Imagine', t, 0.05, 400, 1325, size=84)
        glow_word(base, 'GIFTING', t, 0.72, 540, 1475, size=205)
        emoji(base, '\U0001F381', t, 0.95, 900, 1300, size=170)
    elif within(1.95, 3.0):          # someone something that has…
        serif_in(base, 'someone', t, 1.95, 540, 1395, size=96)
        serif_in(base, 'something that has…', t, 2.25, 540, 1500, size=70)
    elif within(3.15, 7.2):          # glass pill over the product shot
        glass_pill(base, [('Their name', 3.26), ('Their special date', 3.95), ('A design just for them', 5.30)],
                   t, 3.12, 540, 1500, size=60, width=860)
    elif within(7.25, 8.6):          # sounds amazing, right??
        highlight(base, 'sounds amazing, right??', t, 7.40, 540, 1470, size=64)
    elif within(8.65, 11.2):         # that's exactly what you can CREATE
        script_line(base, "that's exactly", t, 8.70, 540, 1300, size=96)
        script_line(base, 'what you can', t, 9.42, 540, 1405, size=96)
        block_band(base, 'CREATE', t, 9.92, 1560, size=175)
    elif within(15.2, 16.55):        # truly PERSONAL
        serif_in(base, 'truly', t, 15.30, 300, 1330, size=96)
        glow_word(base, 'PERSONAL', t, 15.70, 540, 1470, size=180)
    elif k in ('scroll', 'zoomin') and within(16.55, 20.1):   # occasions: small yellow tags
        tag = {16.55: 'birthdays', 17.55: 'anniversaries', 18.25: 'couples', 18.85: 'every special occasion'}[shot_start]
        highlight(base, tag, t, shot_start + 0.05, 540, 1640, size=64, t_end=shot_end)
    elif within(20.15, 22.62):       # starting at just ₹299 / visit giftyglow.com
        serif_in(base, 'starting at just', t, 20.30, 540, 1290, size=82)
        bubble_price(base, t, 20.90, 560, 1480, size=230)
        highlight(base, 'visit giftyglow.com', t, 21.70, 540, 1700, size=60)
    elif k == 'end':
        highlight(base, 'giftyglow.com', t, 22.97, 540, 1330, size=60)
        serif_in(base, 'create your own', t, 22.94, 540, 1470, size=78)
        glow_word(base, 'PERSONALISED', t, 23.55, 540, 1600, size=108)
        script_line(base, 'gift', t, 23.95, 470, 1745, size=110)
        emoji(base, '\U0001F381', t, 24.05, 640, 1740, size=120, rot=8)
