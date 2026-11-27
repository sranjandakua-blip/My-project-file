"""Stage 2: python3 -I captions.py <edit.json>
Instagram-Edits style captions (slate bold text, white highlighter sweeping word by word) burned onto
build/base.mp4 -> build/final.mp4. Prints the caption chunks so you can proofread them."""
import re, json, subprocess, os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
cfg_path = os.path.abspath(sys.argv[1]); cfg = json.load(open(cfg_path))
os.chdir(os.path.dirname(cfg_path))
W, H, FPS = 1080, 1920, 30
meta = json.load(open('build/meta.json'))
OFF = meta['STITCH']; HIDE = meta['hide']

# ---- words (transcribe.py output with word timestamps) ----
words = []
for line in open(cfg['transcript']):
    if line.startswith('   W '):
        for tok in line[5:].split():
            m = re.match(r'(.+)@([\d.]+)-([\d.]+)$', tok)
            if m: words.append([m.group(1), float(m.group(2)) + OFF, float(m.group(3)) + OFF])
# whisper splits "NxtJob.ai" -> "Nextjob" ".ai" and "Rs.199" -> "Rs" ".199": glue "."-tokens back on
fixed = []
for w in words:
    if fixed and w[0].startswith('.') and len(w[0]) > 1:
        prev = fixed[-1]
        if w[0][1].isdigit():                       # ".199." -> separate number word
            fixed.append([w[0][1:], w[1], w[2]])
        else:                                       # ".ai" -> merge
            prev[0] += w[0]; prev[2] = w[2]
        continue
    fixed.append(w)
# phrase_fix: [["heard words ...", "correct words ..."]] — replaces a run of words, spreading the new words
# evenly over the run's time span (fixes mis-heard phrases and split tokens like "5 -9." / "follow -up")
for bad, good in cfg.get('phrase_fix', []):
    bw, gw = bad.split(), good.split()
    i = 0
    while i <= len(fixed) - len(bw):
        if [w[0] for w in fixed[i:i + len(bw)]] == bw:
            t0, t1 = fixed[i][1], fixed[i + len(bw) - 1][2]
            step = (t1 - t0) / len(gw)
            fixed[i:i + len(bw)] = [[g, t0 + k * step, t0 + (k + 1) * step] for k, g in enumerate(gw)]
            i += len(gw)
        else:
            i += 1
REPL = cfg.get('replace', [])
for w in fixed:
    for a, b in REPL:
        if w[0] == a or w[0].startswith(a): w[0] = b + w[0][len(a):]
words = fixed

# ---- chunk into 1–2 line groups ----
# caption_style: "highlighter" (slate Inter Bold + white box sweeping, Negotiator reel)
#                "yellow_word" (white DM Sans ExtraBold, spoken word yellow, dark outline + hard shadow;
#                 creator's "Pick a style" choice from Nov 2026)
STYLE = cfg.get('caption_style', 'yellow_word')   # client's default since Nov 2026
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if STYLE == 'yellow_word':
    SIZE = cfg.get('caption_size', 56)          # client: "font thode chote" -> 56 (was 64)
    FONT = ImageFont.truetype(os.path.join(SKILL_DIR, 'fonts', 'DMSans-ExtraBold.ttf'), SIZE)
    MAXLINE = int(560 * SIZE / 64)
else:
    FONT = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 46)
    MAXLINE = 380   # px per line (narrow block like the reference)
def tw(s): return FONT.getlength(s)
chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    txt = ' '.join(x[0] for x in cur)
    end_sent = w[0][-1] in '.?!'
    pause = nxt and nxt[1] - w[2] > 0.25
    full = nxt and tw(txt + ' ' + nxt[0]) > 2 * MAXLINE - 60
    if not nxt or end_sent or full or (pause and len(cur) >= 2) or (w[0][-1] == ',' and len(cur) >= 4):
        chunks.append(cur); cur = []
# don't leave a single word stranded in its own caption: glue it onto the previous chunk when it fits
k = 1
while k < len(chunks):
    if len(chunks[k]) == 1 and chunks[k - 1][-1][0][-1] not in '.?!' and \
            tw(' '.join(x[0] for x in chunks[k - 1] + chunks[k])) <= 2 * MAXLINE + 40:
        chunks[k - 1] += chunks.pop(k)
    else:
        k += 1
def split_lines(ch):
    if tw(' '.join(x[0] for x in ch)) <= MAXLINE: return [ch]
    best = None
    for k in range(1, len(ch)):
        a, b = ' '.join(x[0] for x in ch[:k]), ' '.join(x[0] for x in ch[k:])
        if tw(a) <= MAXLINE + 40 and tw(b) <= MAXLINE + 40:
            sc = abs(tw(a) - tw(b)) - (25 if ch[k - 1][0][-1] in ',.' else 0)
            if best is None or sc < best[0]: best = (sc, k)
    k = best[1] if best else len(ch) // 2
    return [ch[:k], ch[k:]]
groups = []
for j, ch in enumerate(chunks):
    start = ch[0][1]
    end = chunks[j + 1][0][1] if j + 1 < len(chunks) else ch[-1][2] + 0.6
    end = min(end, ch[-1][2] + 1.2)
    groups.append((start, end, split_lines(ch)))
for g in groups: print(f'{g[0]:6.2f}-{g[1]:6.2f}', ' / '.join(' '.join(x[0] for x in l) for l in g[2]))
if '--list' in sys.argv: sys.exit(0)   # proofread the captions without rendering

# ---- render ----
TEXT = (62, 72, 92, 255)     # slate
DIM = (62, 72, 92, 235)
LIGHT = (214, 219, 228, 255)
BOX = (255, 255, 255, 255)
TOP, LH, GAP, PADX, PADY = cfg.get("caption_top", 388), 56, 8, 9, 5   # caption_top: keep the block just above the head
asc, desc = FONT.getmetrics()
# spoken-word colour: client wants butter yellow (soft, creamy) -> #FFE27A
_hex = cfg.get('caption_color', '#FFE27A').lstrip('#')
YELLOW = tuple(int(_hex[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
WHITE = (255, 255, 255, 255); INK = (17, 17, 20, 255)
SHADOW = cfg.get('caption_shadow', [5, 7])   # hard shadow offset (px), no blur
# client rule: hard shadow OR outline — never both
EFFECT = cfg.get('caption_effect', 'shadow')
assert EFFECT in ('shadow', 'outline', 'none'), 'caption_effect must be "shadow", "outline" or "none"'
OUTLINE = 3 if EFFECT == 'outline' else 0
def render_yellow(t):
    g = next((g for g in groups if g[0] <= t < g[1]), None)
    if g is None or any(a <= t < b for a, b in HIDE): return None
    flat = [w for l in g[2] for w in l]
    active = max((w for w in flat if w[1] <= t), key=lambda w: w[1], default=None)
    LH2 = int(FONT.size * 1.22)
    im = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, l in enumerate(g[2]):
        y = 10 + li * LH2
        x = (W - tw(' '.join(w[0] for w in l))) / 2
        for w in l:
            if EFFECT == 'shadow':
                sx, sy = SHADOW
                d.text((x + sx, y + sy), w[0], font=FONT, fill=INK)
            d.text((x, y), w[0], font=FONT, fill=YELLOW if w is active else WHITE, stroke_width=OUTLINE, stroke_fill=INK)
            x += tw(w[0] + ' ')
    return im

def render(t, dark=False):
    if STYLE == 'yellow_word': return render_yellow(t)
    g = next((g for g in groups if g[0] <= t < g[1]), None)
    if g is None or any(a <= t < b for a, b in HIDE): return None
    lines = g[2]
    widths = [tw(' '.join(x[0] for x in l)) for l in lines]
    bw = max(widths); x0 = (W - bw) / 2
    im = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, l in enumerate(lines):
        y = li * (LH + GAP)
        # highlighter extent
        x = 0.0; hx = 0.0
        for wi, w in enumerate(l):
            s = w[0] + (' ' if wi < len(l) - 1 else '')
            wl = tw(w[0]); sl = tw(s)
            if t >= w[2]: hx = x + (sl if wi < len(l) - 1 and t >= l[wi + 1][1] else wl)
            elif t >= w[1]: hx = x + wl * min(1, (t - w[1]) / max(0.12, w[2] - w[1]))
            x += sl
        if hx > 0:
            d.rectangle([x0 - PADX, y - PADY, x0 + hx + PADX, y + LH - PADY], fill=BOX)
        d.text((x0, y + (LH - asc - desc) / 2 - 2), ' '.join(x[0] for x in l), font=FONT, fill=TEXT if hx > 0 else (LIGHT if dark else DIM))
        if 0 < hx < tw(' '.join(x[0] for x in l)) and dark:
            # spoken part stays slate on white; repaint the unspoken tail light
            im2 = Image.new('RGBA', im.size, (0,0,0,0)); d2 = ImageDraw.Draw(im2)
            d2.text((x0, y + (LH - asc - desc) / 2 - 2), ' '.join(x[0] for x in l), font=FONT, fill=LIGHT)
            mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).rectangle([x0 + hx + PADX, y - PADY, W, y + LH], fill=255)
            im.paste(im2, (0, 0), Image.composite(im2.getchannel('A'), mask, mask))
    return im

tot = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'build/base.mp4'],
                           capture_output=True, text=True).stdout)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', 'build/base.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', 'build/base.mp4', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                        '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', '-c:a', 'copy', '-shortest', 'build/final.mp4'],
                       stdin=subprocess.PIPE)
n = 0; fs = W * H * 3
while True:
    buf = dec.stdout.read(fs)
    if len(buf) < fs: break
    t = n / FPS
    arr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    dark = arr[TOP:TOP + 130:4, 150:930:4].mean() < 95
    ov = render(t, dark)
    if ov is not None:
        fr = Image.frombuffer('RGB', (W, H), buf, 'raw', 'RGB', 0, 1).copy()
        fr.paste(ov, (0, TOP), ov)
        buf = fr.tobytes()
    enc.stdin.write(buf); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames', n)
