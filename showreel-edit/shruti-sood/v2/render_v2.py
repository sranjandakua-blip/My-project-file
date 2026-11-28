"""Showreel v2: cut to music track v4 (71.29 s).
Intro fast cuts (band) -> B0085 dancers in sync -> B0086 singing in sync -> drum fill (drummer)
-> song-B intro (band) -> B0093 singing in sync -> strobe section (crowd/band) -> synced finale + freeze on the thud."""
import json, subprocess, sys, os
S = '/tmp/claude-0/-home-user-My-project-file/b8f68f35-e422-5be6-8710-30ffbc413c24/scratchpad'
OUT = f'{S}/edit2/shots'; os.makedirs(OUT, exist_ok=True)
FPS = 30000 / 1001
TOTAL = 71.2873
A0, AB = 0.0, 0.6734                 # song A / intro beat grid (intro bar lines at 0, 2.694, 5.388, 8.082)
J1 = 8.0844                          # B0086 enters (on grid)
J2 = 32.3724                         # song B downbeat
BB = 0.418                           # song B beat
THUD = 68.4881
SYNC86 = 42.8607 - J1                # B0086 src = t + SYNC86
SYNC93 = 58.3573 - J2                # B0093 src = t + SYNC93
STRETCH = 0.6385 / 0.6734            # B0085 audio was slowed by this factor
SYNC = 'SYNC'
def a(m): return J1 + AB * m         # song-A beat m after J1
def b(k): return J2 + BB * k         # song-B beat k after J2
def i(m): return A0 + AB * m         # intro beat

SH = []
def add(t0, t1, clip, src, **kw): SH.append(dict(t0=t0, t1=t1, clip=clip, src=src, **kw))
# ---- 0-6.06: fast band cuts on the beat (half-beat stutter in bar 2) ----
add(i(0), i(1), 'B0054', 3.6, flash=1, z0=1.12, z1=1.12)
add(i(1), i(2), 'B0051', 3.1, z0=1.0, z1=1.06)
add(i(2), i(3), 'B0013', 64.6, bw=1, z0=1.15, z1=1.15)
add(i(3), i(4), 'B0056', 0.2, z0=1.0, z1=1.08)
add(i(4), i(4.5), 'B0054', 6.2, z0=1.2, z1=1.2)
add(i(4.5), i(5), 'B0051', 9.2, bw=1, z0=1.15, z1=1.15)
add(i(5), i(5.5), 'B0013', 67.8, z0=1.2, z1=1.2)
add(i(5.5), i(6), 'B0056', 1.5, z0=1.15, z1=1.15)
add(i(6), i(7), 'B0054', 0.7, z0=1.0, z1=1.08)
add(i(7), i(8), 'B0013', 52.5, bw=1, z0=1.12, z1=1.12)
add(i(8), i(9), 'B0051', 6.0, flash=1, z0=1.15, z1=1.0)
# ---- 6.06-8.08: B0085 dancers, in sync with their own (stretched) audio ----
add(i(9), J1, 'B0085', (i(9) + 3.063) * STRETCH, speed=STRETCH, z0=1.0, z1=1.08, yb=0.5)
# ---- song A: B0086 in lip sync, reframed on bar lines, short cutaways ----
add(a(0), a(4), 'B0086', SYNC, flash=1, z0=1.0, z1=1.06, title=1)
add(a(4), a(8), 'B0086', SYNC, z0=1.25, z1=1.25)
add(a(8), a(12), 'B0086', SYNC, z0=1.0, z1=1.08)
add(a(12), a(14), 'B0086', SYNC, z0=1.28, z1=1.28)
add(a(14), a(16), 'B0083', 10.2, z0=1.05, z1=1.15, yb=0.5)          # crowd dancing (purple)
add(a(16), a(20), 'B0086', SYNC, z0=1.0, z1=1.07)
add(a(20), a(24), 'B0086', SYNC, z0=1.22, z1=1.22)
add(a(24), a(26), 'B0013', 65.4, z0=1.1, z1=1.18)                    # guitarist
add(a(26), a(28), 'B0086', SYNC, z0=1.15, z1=1.15)
add(a(28), a(30), 'B0085', 11.0, z0=1.05, z1=1.12, yb=0.5)           # dancer (red)
add(a(30), a(32), 'B0086', SYNC, z0=1.0, z1=1.06)
add(a(32), a(33), 'B0083', 42.0, z0=1.1, z1=1.1, yb=0.5)            # B0086 strobes to black here
add(a(33), a(34), 'B0013', 66.8, z0=1.18, z1=1.18)
# ---- drum fill -> drummer ----
add(a(34), a(35), 'B0054', 3.6, z0=1.15, z1=1.15)
add(a(35), J2, 'B0054', 6.3, bw=1, z0=1.3, z1=1.3)
# ---- song B instrumental intro: band ----
add(b(0), b(2), 'B0056', 0.2, flash=1, z0=1.15, z1=1.15)
add(b(2), b(4), 'B0054', 0.8, z0=1.2, z1=1.2)
add(b(4), b(6), 'B0051', 9.0, z0=1.25, z1=1.25)
# ---- song B: B0093 in lip sync ----
add(b(6), b(14), 'B0093', SYNC, z0=1.0, z1=1.08)
add(b(14), b(22), 'B0093', SYNC, z0=1.22, z1=1.22)
add(b(22), b(24), 'B0083', 38.5, z0=1.05, z1=1.12, yb=0.5)          # crowd
add(b(24), b(32), 'B0093', SYNC, z0=1.0, z1=1.08)
add(b(32), b(36), 'B0093', SYNC, z0=1.26, z1=1.26)
add(b(36), b(38), 'B0013', 55.0, z0=1.1, z1=1.1)                     # bassist
add(b(38), b(46), 'B0093', SYNC, z0=1.0, z1=1.08)
add(b(46), b(48), 'B0083', 12.0, z0=1.05, z1=1.12, yb=0.5)
add(b(48), b(55), 'B0093', SYNC, z0=1.15, z1=1.15)
# ---- strobe section: crowd / band, one synced strobe flash ----
add(b(55), b(57), 'B0083', 14.0, z0=1.05, z1=1.1, yb=0.5)
add(b(57), b(59), 'B0054', 5.0, bw=1, z0=1.2, z1=1.2)
add(b(59), b(61), 'B0051', 1.0, z0=1.15, z1=1.15)
add(b(61), b(63), 'B0083', 30.2, z0=1.05, z1=1.1, yb=0.5)
add(b(63), b(65), 'B0013', 66.2, z0=1.15, z1=1.15)
add(b(65), b(67), 'B0085', 1.8, z0=1.05, z1=1.12, yb=0.5)
add(b(67), b(69), 'B0054', 7.4, z0=1.15, z1=1.15)
add(b(69), b(71), 'B0083', 16.0, z0=1.05, z1=1.1, yb=0.5)
add(b(71), b(73), 'B0085', 7.0, z0=1.05, z1=1.12, yb=0.5)           # dancer, arms up (purple)
add(b(73), b(75), 'B0056', 1.2, z0=1.15, z1=1.15)
add(b(75), b(77), 'B0083', 40.5, z0=1.05, z1=1.1, yb=0.5)
add(b(77), b(78), 'B0054', 2.0, bw=1, z0=1.25, z1=1.25)
add(b(78), b(79), 'B0051', 11.0, z0=1.2, z1=1.2)
add(b(79), b(80), 'B0083', 44.0, z0=1.1, z1=1.1, yb=0.5)
add(b(80), b(82), 'B0013', 68.0, z0=1.2, z1=1.2)
# ---- finale: synced, light hits as she raises her arm; freeze on the thud ----
FREEZE_T = 68.15
add(b(82), FREEZE_T, 'B0093', SYNC, z0=1.0, z1=1.06)
add(FREEZE_T, TOTAL, 'B0093', FREEZE_T + 0 + 0, freeze=FREEZE_T, z0=1.06, z1=1.16, flash_at=THUD - FREEZE_T,
    endcard=THUD - FREEZE_T + 0.3, fadeout=1.0)

def frm(t): return round(t * FPS)
def resolve(s):
    if s.get('freeze'): return s['freeze'] + SYNC93
    if s['src'] == SYNC: return s['t0'] + (SYNC86 if s['clip'] == 'B0086' else SYNC93)
    return s['src']
for s in SH: s['src_abs'] = round(resolve(s), 4)
# sanity: contiguous, frame counts
for x, y in zip(SH, SH[1:]): assert abs(x['t1'] - y['t0']) < 1e-6, (x, y)
assert abs(SH[0]['t0']) < 1e-9 and abs(SH[-1]['t1'] - TOTAL) < 1e-6
json.dump(SH, open(f'{S}/edit2/plan_v2.json', 'w'), indent=0)

F = f'{S}/edit'
def render(idx, s):
    n = frm(s['t1']) - frm(s['t0']); D = n / FPS
    sp = s.get('speed', 1.0); z0, z1 = s.get('z0', 1.0), s.get('z1', 1.0); yb = s.get('yb', 0.35)
    z = f"({z0}+({z1}-{z0})*t/{D:.4f})"
    pre = []
    if sp != 1.0: pre.append(f"setpts=(PTS-STARTPTS)/{sp}")
    pre += ['scale=1404:2496:flags=bicubic',
            f"scale=w='2*trunc(1080*{z}/2)':h='2*trunc(1920*{z}/2)':eval=frame:flags=lanczos",
            f"crop=1080:1920:(iw-1080)/2:(ih-1920)*{yb}",
            'eq=contrast=1.07:saturation=1.12:gamma=0.98']
    if s.get('bw'): pre.append('hue=s=0,eq=contrast=1.15')
    pre += ['vignette=angle=PI/5', 'noise=alls=5:allf=t']
    post = []
    if s.get('flash'): post.append('fade=t=in:st=0:d=0.15:color=white')
    if s.get('flash_at') is not None:
        fa = s['flash_at']
        post.append(f"geq=lum='min(255,lum(X,Y)+255*max(0,1-abs(T-{fa:.3f})/0.12)*gte(T,{fa-0.02:.3f}))':cb='cb(X,Y)':cr='cr(X,Y)'")
    if s.get('fadeout'): post.append(f"fade=t=out:st={D - s['fadeout']:.3f}:d={s['fadeout']}")
    post.append('format=yuv420p')
    if s.get('freeze'):
        still = f'{OUT}/freeze.png'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',f"{s['src_abs']:.3f}",'-i',f"{S}/raw/{s['clip']}.MP4",'-frames:v','1',still],check=True)
        inp = ['-loop','1','-framerate','30000/1001','-t',f'{D+0.1:.3f}','-i',still]
    else:
        inp = ['-ss', f"{s['src_abs']:.3f}", '-t', f'{D*sp+0.3:.3f}', '-i', f"{S}/raw/{s['clip']}.MP4"]
    png = None
    if s.get('title'): png = (f'{F}/title.png', f"fade=t=in:st=0.25:d=0.4:alpha=1,fade=t=out:st={D-0.4:.3f}:d=0.4:alpha=1")
    if s.get('endcard') is not None: png = (f'{F}/endcard.png', f"fade=t=in:st={s['endcard']:.3f}:d=0.5:alpha=1")
    if png:
        inp += ['-loop','1','-t',f'{D+0.2:.3f}','-i',png[0]]
        filt = ['-filter_complex', f"[0:v]{','.join(pre)}[v];[1:v]format=rgba,{png[1]}[t];[v][t]overlay=0:0,{','.join(post)}[o]", '-map', '[o]']
    else:
        filt = ['-vf', ','.join(pre + post)]
    cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y'] + inp + ['-an'] + filt + ['-r','30000/1001','-frames:v',str(n),
           '-c:v','libx264','-preset','medium','-crf','15','-g','30','-bf','0', f'{OUT}/{idx:03d}.mp4']
    r = subprocess.run(cmd, capture_output=True, text=True)
    return f"{idx:3d} {s['clip']} t={s['t0']:.3f}-{s['t1']:.3f} src={s['src_abs']:.3f} n={n} " + ('ERR ' + r.stderr[-400:] if r.returncode else 'ok')

if __name__ == '__main__':
    only = set(int(x) for x in sys.argv[1:])
    from concurrent.futures import ThreadPoolExecutor
    jobs = [(k, s) for k, s in enumerate(SH) if not only or k in only]
    with ThreadPoolExecutor(2) as ex:
        for line in ex.map(lambda p: render(*p), jobs): print(line, flush=True)
