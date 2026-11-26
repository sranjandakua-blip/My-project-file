"""Stage 1: python3 -I build_base.py <edit.json>
Stitch + reframed source + B-roll / agent overlays + SFX  ->  <dir>/build/base.mp4 (+ build/meta.json)."""
import subprocess, json, os, sys
cfg_path = os.path.abspath(sys.argv[1]); cfg = json.load(open(cfg_path))
os.chdir(os.path.dirname(cfg_path)); os.makedirs('build', exist_ok=True)
W, H, FPS = 1080, 1920, 30
ST = cfg['stitch']; STITCH = ST['end']
SRC_DUR = cfg['source_duration']; TAIL = cfg.get('tail', 0.8)
FONT_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
def run(cmd): print(' '.join(cmd)[:200]); subprocess.run(cmd, check=True)

# ---------- image cards (client-supplied stills: agent art, logos, diagrams) ----------
def image_card(ins, dur, out):
    """kind "image": one or more stills (stacked) on an optional white card, rounded, hard shadow,
    pop-in (0.18 s ease-out-back) and fade-out (0.12 s), centred at y; rendered with alpha (ProRes 4444)."""
    from PIL import Image, ImageOps, ImageDraw
    files = ins.get('files') or [ins['file']]
    width = ins.get('width', 820); card = ins.get('card', False); pad = 36 if card else 0
    ims = []
    for f in files:
        im = ImageOps.exif_transpose(Image.open(f)).convert('RGBA')
        iw = width - 2 * pad if card else width
        ims.append(im.resize((iw, round(im.height * iw / im.width)), Image.LANCZOS))
    gap = 28 if card else 0
    ch_ = sum(i.height for i in ims) + gap * (len(ims) - 1) + 2 * pad
    body = Image.new('RGBA', (width, ch_), (255, 255, 255, 255) if card else (0, 0, 0, 0))
    y = pad
    for im in ims: body.alpha_composite(im, ((width - im.width) // 2, y)); y += im.height + gap
    r = ins.get('radius', 28)
    m = Image.new('L', body.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, width - 1, ch_ - 1], r, fill=255)
    body.putalpha(Image.composite(body.getchannel('A'), Image.new('L', body.size, 0), m))
    sh = Image.new('RGBA', body.size, (10, 10, 14, 200)); sh.putalpha(body.getchannel('A').point(lambda v: v * 200 // 255))
    yc = ins.get('y', 1000); n = round(dur * FPS)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', out], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS; u = min(1, t / 0.18); c1 = 1.7
        sc = 0.82 + 0.18 * (1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2)      # ease-out-back
        a = min(1, t / 0.1) * min(1, max(0, (dur - t) / 0.12))
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        bw, bh = max(1, round(width * sc)), max(1, round(ch_ * sc))
        b2 = body.resize((bw, bh), Image.BILINEAR); s2 = sh.resize((bw, bh), Image.BILINEAR)
        x0, y0 = (W - bw) // 2, yc - bh // 2
        fr.alpha_composite(s2, (x0 + 10, y0 + 12)); fr.alpha_composite(b2, (x0, y0))
        if a < 1: fr.putalpha(fr.getchannel('A').point(lambda v: int(v * a)))
        enc.stdin.write(fr.tobytes())
    enc.stdin.close(); enc.wait()

# ---------- inserts, each rendered as a full-frame 1080x1920 clip ----------
cw, ch, cx0, cy0 = cfg.get('agent_crop', [974, 1675, 50, 320])
paths = []
for ins in cfg['inserts']:
    dur = ins['end'] - ins['start']; kind = ins['kind']
    sp = ins.get('speed', 1.0)   # >1 plays faster (use to fit a full agent-card demo loop into the spoken span)
    if kind == 'full':      # 9:16 crop from a 16:9 clip, scaled to fill
        cx = ins.get('crop_x', 437)
        vf = f'crop=ih*9/16:ih:{cx}*iw/1280:0,scale={W}:{H}:flags=lanczos,setsar=1'
    elif kind == 'box':     # 16:9 card on black; captions stay visible above it
        vf = f'scale=880:-2:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2+40:black,setsar=1'
    elif kind == 'image':
        out = f"build/{ins['name']}.mov"; image_card(ins, dur, out); paths.append(out); continue
    elif kind == 'agent':   # nxtjob.ai agent card (its page background acts as the panel)
        vf = (f'crop={cw}:{ch}:{cx0}:{cy0},scale=864:-2:flags=lanczos,'
              f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black@0,setsar=1,format=yuva444p10le')
    else: raise SystemExit('unknown kind ' + kind)
    if kind == 'agent':
        out = f"build/{ins['name']}.mov"
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ins['ss']), '-i', ins['file'], '-t', f'{dur * sp:.3f}',
             '-vf', f'setpts=PTS/{sp},' + vf, '-r', str(FPS), '-an', '-c:v', 'prores_ks', '-profile:v', '4444', out])
    else:
        out = f"build/{ins['name']}.mp4"
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ins['ss']), '-i', ins['file'], '-t', f'{dur:.3f}', '-vf', vf, '-an', *ENC, out])
    paths.append(out)

# ---------- base video ----------
label = ST.get('label', '*Stitch incoming*').replace(':', r'\:').replace("'", r"\'")
stitch_txt = (f"drawtext=fontfile={FONT_B}:text='{label}':fontcolor=0xFFD21F:fontsize=48:"
              f"x=(w-text_w)/2:y={ST.get('label_y', 1478)}")
FILL = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}'   # never stretch non-9:16 sources
# stitch.delogo: [x, y, w, h] in the stitch clip's own pixels — blurs out a channel logo/watermark
DL = ''.join(f'delogo=x={x}:y={y}:w={w}:h={h},' for x, y, w, h in ST.get('delogo', []))
fc = [f'[0:v]trim=0:{STITCH},setpts=PTS-STARTPTS,{DL}fps={FPS},{FILL},setsar=1,{stitch_txt}[st]']
labels = []
for k, p in enumerate(cfg['parts']):
    chain = f"[1:v]trim={p['start']}:{p['end']},setpts=PTS-STARTPTS,fps={FPS},{FILL}"
    if p.get('crop_y'):   # letterboxed take -> crop bars and fill the frame
        y0, y1 = p['crop_y']; hh = y1 - y0; ww = int(round(W * hh / H / 2) * 2)
        chain += f',crop={ww}:{hh}:{(W - ww) // 2}:{y0},scale={W}:{H}:flags=lanczos'
    fc.append(chain + f',setsar=1[s{k}]'); labels.append(f'[s{k}]')
fc.append(''.join(labels) + f'concat=n={len(labels)}:v=1:a=0,tpad=stop_mode=clone:stop_duration={TAIL}[src]')
fc.append('[st][src]concat=n=2:v=1:a=0[base0]')
inputs = ['-i', ST['file'], '-i', cfg['source']]
cur = 'base0'
for k, (ins, path) in enumerate(zip(cfg['inserts'], paths)):
    oa, ob = ins['start'] + STITCH, ins['end'] + STITCH
    inputs += ['-itsoffset', f'{oa:.3f}', '-i', path]
    fc.append(f"[{cur}][{2 + k}:v]overlay=0:0:enable='between(t,{oa:.3f},{ob - 0.001:.3f})':eof_action=pass[v{k}]")
    cur = f'v{k}'

# ---------- audio: voice (both normalised to -14 LUFS) + click per insert + ping at "link" ----------
na = 2 + len(paths); sfx = cfg['sfx']
inputs += ['-i', sfx['click'], '-i', sfx['ping']]
fc.append(f'[0:a]atrim=0:{STITCH},asetpts=PTS-STARTPTS,afade=t=out:st={STITCH - 0.04}:d=0.04,'
          'loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ast]')
fc.append(f'[1:a]atrim=0:{SRC_DUR},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=pad_dur={TAIL}[asrc]')
fc.append('[ast][asrc]concat=n=2:v=0:a=1[voice]')
clicks = [i['start'] + STITCH for i in cfg['inserts']]
fc.append(f'[{na}:a]atrim=0:0.25,aresample=48000,volume=0.55,asplit={len(clicks)}' + ''.join(f'[c{i}]' for i in range(len(clicks))))
for i, t in enumerate(clicks):
    ms = int(round(t * 1000)); fc.append(f'[c{i}]adelay={ms}|{ms}[cd{i}]')
ms = int(round((sfx['ping_at'] + STITCH) * 1000))
fc.append(f'[{na + 1}:a]atrim=0:1.3,aresample=48000,volume=0.6,adelay={ms}|{ms}[ping]')
fc.append('[voice]' + ''.join(f'[cd{i}]' for i in range(len(clicks))) + f'[ping]amix=inputs={len(clicks) + 2}:normalize=0:duration=first[aout]')

total = STITCH + SRC_DUR + TAIL
run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-map', '[aout]',
     '-t', f'{total:.3f}', *ENC, '-c:a', 'aac', '-b:a', '192k', 'build/base.mp4'])
json.dump({'STITCH': STITCH, 'hide': [[i['start'] + STITCH, i['end'] + STITCH] for i in cfg['inserts'] if i['kind'] == 'agent']},
          open('build/meta.json', 'w'))
print('done -> build/base.mp4')
