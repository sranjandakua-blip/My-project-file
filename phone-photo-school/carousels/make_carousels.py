"""Phone Photo School carousels: 1080x1350 (4:5) Instagram slides, one folder per lesson.

    python3 carousels/make_carousels.py            # all lessons -> carousels/out/LNN/slide-N.png
    python3 carousels/make_carousels.py 3 7        # only lessons 3 and 7

Slides: a cover (full-bleed photo + hook), 3-5 tip slides (number, headline, one line, a photo or a camera screenshot),
and a closing slide (avatar, handle, save/follow, "full reel on my profile", next lesson).
Photos come from brand/photos/<key>.jpg, screenshots from brand/screens/<name>.jpg (both kept local, not in git).
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
PH, SC, OUT = ROOT / 'brand/photos', ROOT / 'brand/screens', ROOT / 'carousels/out'
W, H = 1080, 1350
BG, PANEL, INK, WHITE, MUTE = (18, 21, 28), (31, 36, 48), (10, 12, 16), (255, 255, 255), (138, 147, 166)
YELLOW, TEAL, RED, GREEN = (255, 200, 61), (62, 224, 207), (255, 77, 94), (61, 220, 132)
FD = '/usr/share/fonts/opentype/inter/'
F = lambda w, s: ImageFont.truetype(FD + f'Inter-{w}.otf', s)
HANDLE = '@the_linse_art'

# ---------------------------------------------------------------- content
# tip slide: (headline, body, visual) · visual = ('photo', key, opts) | ('photos', [(key, opts), ...]) | ('screen', name, (x0, y0, x1, y1))
# opts: cx, cy (focus 0..1) · grid · dot (fx, fy) · ring (fx, fy) · smudge · tag
LESSONS = {
 1: ('The Grid', 'One setting that instantly fixes your composition', ('lighthouse', {'cy': 0.55}), [
    ('Turn on the grid', 'Camera settings → General → Composition guide → Grid lines and level.', ('screen', 'settings', (0, 3640, 1440, 4400))),
    ('Subject on a crossing', 'Not dead centre. Put it where two grid lines cross.', ('photo', 'tower', {'cx': 0.62, 'grid': 1, 'dot': (2 / 3, 1 / 3)})),
    ('Horizon on a line', 'Keep it on the top or bottom line, never through the middle.', ('photo', 'boats', {'cy': 0.6, 'grid': 1})),
  ], 'Tap to Focus'),
 2: ('Tap to Focus', 'Blurry subject? Your phone guessed wrong.', ('kittens', {'cy': 0.62}), [
    ('Tap your subject', 'Auto focus often picks the background. One tap fixes it.', ('photo', 'kittens', {'cy': 0.62, 'ring': (0.5, 0.64)})),
    ('Slide the little sun', 'Down to save bright skies, up to lift the shadows.', ('photo', 'sunset', {'cy': 0.72, 'ring': (0.39, 0.805)})),
    ('Pro tip: press & hold', 'It locks focus and exposure (AE/AF lock) while you reframe.', ('photo', 'templeNight', {'cx': 0.6, 'cy': 0.7})),
  ], 'Clean Your Lens'),
 3: ('Clean Your Lens', 'The free upgrade most people skip', ('beam', {'cx': 0.45}), [
    ('What a dirty lens does', 'Grease, dust and lint make lights glow and details go soft.', ('photo', 'beam', {'cx': 0.45, 'smudge': 1})),
    ('Wipe it gently', 'Use a soft microfiber cloth, not your shirt. Shirts can rub grit into the glass.', ('photo', 'beam', {'cx': 0.45})),
    ('Make it a habit', 'One quick wipe before every shot.', ('photo', 'lighthouse', {'cy': 0.55})),
  ], 'The Zoom Lenses'),
 4: ('The Zoom Lenses', 'Your phone has 4 cameras. Use them!', ('kanch', {'cy': 0.5}), [
    ('.6× Ultra-wide', 'Huge landscapes and small rooms.', ('photo', 'courtyard', {'cy': 0.55})),
    ('1× Main camera', 'Your best all-rounder, especially at night.', ('photo', 'lighthouse', {'cy': 0.55})),
    ('3× Portraits', 'Natural, flattering faces and pets.', ('photo', 'kittens', {'cy': 0.62})),
    ('5× Far details', 'Pull in what you can’t walk up to.', ('photo', 'templeTop', {'cx': 0.72, 'cy': 0.52})),
    ('Tap, don’t pinch', 'In-between zoom is often just a crop, and you lose quality.', ('screen', 'zoomrow', (270, 2215, 1380, 2390))),
  ], 'Leading Lines'),
 5: ('Leading Lines', 'Photos that pull people in', ('arches', {'cy': 0.6}), [
    ('Lines guide the eye', 'Corridors, roads, rails and rivers all lead somewhere.', ('photo', 'arches', {'cy': 0.6})),
    ('Point them at the subject', 'Not off the edge of the frame.', ('photo', 'courtyard', {'cy': 0.62})),
    ('Look everywhere', 'Walls, stairs, winding roads: lines are all around you.', ('photos', [('mural', {'cy': 0.55}), ('stairs', {'cy': 0.5}), ('winding', {'cy': 0.75})])),
    ('Get low, shoot wide', 'Use .6× close to the ground and the lines stretch out.', ('photo', 'stairs', {'cy': 0.55})),
  ], 'Golden Hour'),
 6: ('Golden Hour', 'Why some photos just glow', ('stupa', {'cy': 0.45}), [
    ('When to shoot', 'The first hour after sunrise and the last hour before sunset.', ('photo', 'stupa', {'cy': 0.4})),
    ('Soft, warm, long shadows', 'Low sun flatters everything. Harsh midday sun doesn’t.', ('photo', 'stairs', {'cy': 0.6})),
    ('Try a silhouette', 'Sun behind the subject, tap the sky, slide the sun down.', ('photo', 'sunset', {'cy': 0.7})),
  ], 'Portrait Mode'),
 7: ('Portrait Mode', 'That dreamy, blurred background', ('shiva', {'cy': 0.45}), [
    ('Swipe to Portrait', 'Wait for the word “Ready” before you shoot.', ('screen', 'portrait', (40, 2200, 1400, 2400))),
    ('Use 3×, step back', 'Natural faces, and let the subject fill the frame.', ('photo', 'kittens', {'cy': 0.62})),
    ('Distance = creamier blur', 'The farther the background, the softer it gets.', ('photo', 'gopuram', {'cy': 0.5})),
    ('Not just people', 'Pets and objects work beautifully too.', ('photos', [('kittens', {'cy': 0.62}), ('shiva', {'cy': 0.45})])),
  ], 'Night Mode'),
 8: ('Night Mode', 'Night photos dark and grainy?', ('gate', {'cy': 0.6}), [
    ('Look for the moon', 'The little number is how many seconds it needs.', ('photo', 'pyramids', {'cy': 0.6})),
    ('Hold perfectly still', 'Brace your elbows or rest the phone on something solid.', ('photo', 'church', {'cy': 0.5})),
    ('Stick to 1×', 'The main camera gathers the most light.', ('photo', 'roof', {'cy': 0.7})),
  ], 'Megapixels'),
 9: ('Megapixels', 'Is 200MP always better?', ('snow', {'cy': 0.55}), [
    ('12M for every day', 'Great in low light, small files. Tap “12M” at the top to switch.', ('photo', 'stadium', {'cy': 0.55})),
    ('50M / 200M for landscapes', 'Huge detail in bright light, but massive files.', ('photo', 'valley', {'cy': 0.6})),
    ('Crop it later', 'High resolution lets you crop in and still print big.', ('photo', 'houses', {'cx': 0.35, 'cy': 0.58, 'zoom': 2.2})),
  ], 'Expert RAW'),
 10: ('Expert RAW', 'Edit like a real camera', ('roof', {'cy': 0.65}), [
    ('Where to find it', 'MORE → EXPERT RAW', ('screen', 'more', (0, 1560, 1440, 2800))),
    ('RAW keeps more detail', 'Rescue bright skies and lift dark shadows when you edit.', ('photo', 'valley', {'cy': 0.55})),
    ('The catch', 'Big files, and every shot needs editing.', ('photo', 'mural', {'cy': 0.55})),
  ], 'Pro Mode'),
}

# ---------------------------------------------------------------- drawing helpers
def cover_fit(im, w, h, cx=0.5, cy=0.5, zoom=1.0):
    s = max(w / im.width, h / im.height) * zoom
    rw, rh = int(im.width * s + 0.5), int(im.height * s + 0.5)
    im = im.resize((rw, rh), Image.LANCZOS)
    x = min(max(int(cx * rw - w / 2), 0), rw - w); y = min(max(int(cy * rh - h / 2), 0), rh - h)
    return im.crop((x, y, x + w, y + h))

def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    out = Image.new('RGBA', im.size); out.paste(im.convert('RGBA'), (0, 0), m); return out

def tw(d, t, f): return d.textlength(t, font=f)

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split('\n'):
        cur = ''
        for wd in para.split():
            t = (cur + ' ' + wd).strip()
            if tw(d, t, f) <= maxw: cur = t
            else: lines.append(cur); cur = wd
        lines.append(cur)
    return lines

def pill(d, x, y, text, f, bg, fg, anchor='l'):
    w = tw(d, text, f) + 44; h = f.size + 26
    x0 = x if anchor == 'l' else x - w / 2 if anchor == 'm' else x - w
    d.rounded_rectangle((x0, y, x0 + w, y + h), h / 2, fill=bg); d.text((x0 + 22, y + h / 2 + 1), text, font=f, fill=fg, anchor='lm')
    return x0 + w

MARK = Image.open(ROOT / 'brand/logo-mark.png').convert('RGBA')

def header(img, n, i, total):
    d = ImageDraw.Draw(img); f = F('Black', 26)
    m = MARK.resize((54, int(54 * MARK.height / MARK.width)), Image.LANCZOS); img.alpha_composite(m, (56, 50))
    d.text((122, 78), 'PHONE PHOTO SCHOOL', font=f, fill=WHITE, anchor='lm')
    pill(d, 122 + tw(d, 'PHONE PHOTO SCHOOL', f) + 16, 58, f'L{n:02d}', F('Black', 24), TEAL, INK)
    d.text((W - 56, 78), f'{i}/{total}', font=F('Bold', 28), fill=MUTE, anchor='rm')

def shot_tag(img, x, y):
    d = ImageDraw.Draw(img); f = F('Black', 22); t = 'SHOT ON S26 ULTRA'; w = tw(d, t, f) + 86
    d.rounded_rectangle((x - w, y - 22, x, y + 22), 22, fill=(10, 12, 16, 200))
    m = MARK.resize((36, int(36 * MARK.height / MARK.width)), Image.LANCZOS); img.alpha_composite(m, (int(x - w + 12), int(y - 18)))
    d.text((x - 18, y + 1), t, font=f, fill=WHITE, anchor='rm')

def photo_panel(key, w, h, o):
    im = cover_fit(Image.open(PH / f'{key}.jpg').convert('RGB'), w, h, o.get('cx', 0.5), o.get('cy', 0.5), o.get('zoom', 1))
    if o.get('smudge'):
        glow = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(28))).enhance(1.6)
        im = Image.blend(im.filter(ImageFilter.GaussianBlur(4)), glow, 0.45)
        im = Image.blend(im, Image.new('RGB', im.size, (255, 246, 224)), 0.12)
    im = im.convert('RGBA'); d = ImageDraw.Draw(im)
    if o.get('grid'):
        for k in (1, 2):
            for c, lw in ((INK, 9), (WHITE, 5)):
                d.line((w * k / 3, 0, w * k / 3, h), fill=c, width=lw); d.line((0, h * k / 3, w, h * k / 3), fill=c, width=lw)
    if o.get('dot'):
        x, y = o['dot'][0] * w, o['dot'][1] * h
        d.ellipse((x - 34, y - 34, x + 34, y + 34), fill=YELLOW); d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=INK)
    if o.get('ring'):
        x, y = o['ring'][0] * w, o['ring'][1] * h; r = 82
        d.ellipse((x - r, y - r, x + r, y + r), outline=YELLOW, width=8)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.line((x + dx * r, y + dy * r, x + dx * r * 0.78, y + dy * r * 0.78), fill=YELLOW, width=8)
    if o.get('smudge'): pill(d, 24, 24, 'SMUDGE (SIMULATED)', F('Black', 22), (10, 12, 16), WHITE)
    return im

# ---------------------------------------------------------------- slides
def cover(n, title, hook, key, o, total):
    img = cover_fit(Image.open(PH / f'{key}.jpg').convert('RGB'), W, H, o.get('cx', 0.5), o.get('cy', 0.5)).convert('RGBA')
    shade = Image.new('L', (1, H)); [shade.putpixel((0, y), int(235 * max(0, (y - H * 0.35) / (H * 0.65)) ** 1.3)) for y in range(H)]
    img.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, H), c) for c in BG] + [shade.resize((W, H))]))
    top = Image.new('L', (1, 200)); [top.putpixel((0, y), int(170 * (1 - y / 200))) for y in range(200)]
    img.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, 200), 0)] * 3 + [top.resize((W, 200))]))
    header(img, n, 1, total); d = ImageDraw.Draw(img)
    y = pill(d, 60, 820, f'LESSON {n:02d} · {title.upper()}', F('Black', 30), YELLOW, INK) and 900
    for ln in wrap(d, hook, F('Black', 78), W - 120):
        d.text((60, y), ln, font=F('Black', 78), fill=WHITE); y += 92
    d.text((W - 60, H - 70), 'SWIPE  →', font=F('Black', 32), fill=YELLOW, anchor='rm')
    shot_tag(img, W - 40, 150)
    return img

def tip(n, i, total, head, body, vis):
    img = Image.new('RGBA', (W, H), BG); header(img, n, i, total); d = ImageDraw.Draw(img)
    d.text((60, 160), f'{i - 1:02d}', font=F('Black', 44), fill=YELLOW)
    y = 215
    for ln in wrap(d, head, F('Black', 66), W - 120): d.text((60, y), ln, font=F('Black', 66), fill=WHITE); y += 76
    for ln in wrap(d, body, F('Medium', 36), W - 120): d.text((60, y + 10), ln, font=F('Medium', 36), fill=(205, 211, 222)); y += 48
    top = y + 40; bh = H - 70 - top; bw = W - 120
    kind = vis[0]
    if kind == 'photo':
        img.alpha_composite(rounded(photo_panel(vis[1], bw, bh, vis[2]), 34), (60, top)); shot_tag(img, 60 + bw - 22, top + bh - 40)
    elif kind == 'photos':
        k = len(vis[1]); gap = 20; cw = (bw - gap * (k - 1)) // k
        for j, (key, o) in enumerate(vis[1]): img.alpha_composite(rounded(photo_panel(key, cw, bh, o), 28), (60 + j * (cw + gap), top))
        shot_tag(img, 60 + bw - 22, top + bh - 40)
    else:                                                            # a crop of the creator's own camera screenshot
        sc = Image.open(SC / f'{vis[1]}.jpg').convert('RGB').crop(vis[2])
        s = min(bw / sc.width, bh / sc.height); sc = sc.resize((int(sc.width * s), int(sc.height * s)), Image.LANCZOS)
        d.rounded_rectangle((60, top, 60 + bw, top + bh), 34, fill=(0, 0, 0))
        img.alpha_composite(rounded(sc, 24), (60 + (bw - sc.width) // 2, top + (bh - sc.height) // 2))
        pill(d, 60 + bw / 2, top + bh - 70, 'ON MY S26 ULTRA', F('Black', 22), TEAL, INK, 'm')
    return img

AV = Image.open(ROOT / 'avatar-the_linse_art.png').convert('RGBA')

def closing(n, total, nxt):
    img = Image.new('RGBA', (W, H), BG); header(img, n, total, total); d = ImageDraw.Draw(img)
    a = AV.resize((300, 300), Image.LANCZOS); m = Image.new('L', (300, 300), 0); ImageDraw.Draw(m).ellipse((0, 0, 300, 300), fill=255)
    d.ellipse((W / 2 - 162, 238, W / 2 + 162, 562), fill=TEAL); img.paste(a, (W // 2 - 150, 250), m)
    d.text((W / 2, 620), HANDLE, font=F('Black', 52), fill=WHITE, anchor='mm')
    for j, (ic, t) in enumerate((('💾', 'SAVE this for your next shoot'), ('↗', 'SHARE with a friend who needs it'), ('＋', 'FOLLOW for the next lesson'))):
        y = 720 + j * 92; d.rounded_rectangle((150, y, W - 150, y + 72), 36, fill=PANEL)
        d.text((W / 2, y + 37), t, font=F('Bold', 32), fill=WHITE, anchor='mm')
    d.rounded_rectangle((150, 1010, W - 150, 1120), 30, fill=YELLOW)
    d.text((W / 2, 1065), f'▶  Watch the full Reel: Lesson {n:02d}', font=F('Black', 34), fill=INK, anchor='mm')
    d.text((W / 2, 1200), f'NEXT · LESSON {n + 1:02d} · {nxt.upper()}', font=F('Black', 30), fill=TEAL, anchor='mm')
    return img

def build(n):
    title, hook, (ck, co), tips, nxt = LESSONS[n]
    total = len(tips) + 2; out = OUT / f'L{n:02d}'; out.mkdir(parents=True, exist_ok=True)
    slides = [cover(n, title, hook, ck, co, total)] + [tip(n, i + 2, total, *t) for i, t in enumerate(tips)] + [closing(n, total, nxt)]
    for i, s in enumerate(slides, 1): s.convert('RGB').save(out / f'slide-{i}.jpg', quality=92)
    return out, len(slides)

if __name__ == '__main__':
    for n in ([int(a) for a in sys.argv[1:]] or sorted(LESSONS)):
        out, k = build(n); print(f'L{n:02d}: {k} slides -> {out.relative_to(ROOT)}')
