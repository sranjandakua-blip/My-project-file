# EXAMPLE timeline from the "3 things before posting" reel (Nov 2026). Copy to the build dir as timeline.py and
# rewrite the cues/captions for the new script. Everything is anchored to WORD INDICES from words.json
# (W(take,i) = start of word i of that take on the output timeline), so re-cuts never break sync.
# Outputs: timeline.json / timeline.js (read by base.py, overlay.html, audio.py) and sfx.json.
import json, random
random.seed(7)
D = json.load(open('words.json'))
S = D['segs']; VOICE = D['total']; TAIL = 2.35; TOTAL = VOICE + TAIL

def W(seg, i): return S[seg]['words'][i][0]
def WE(seg, i): return S[seg]['words'][i][1]
def ST(seg): return S[seg]['start']
def EN(seg): return S[seg]['end']

# ---------------- cues
C = {}
C['hookExpand'] = 0.92
C['prof'] = (W('hook', 6) - 0.05, W('hook', 8) + 0.25)
C['chips'] = (W('hook', 10) - 0.03, W('hook', 16) - 0.02)
C['ch1'] = (ST('n1'), EN('n1'))
C['feed'] = (W('audience', 11), EN('audience'))
C['feedStop'] = W('audience', 19)
C['ch2'] = (ST('n2'), EN('n2'))
C['scr'] = (W('offer', 10) - 0.02, W('offer', 15) - 0.04)
C['scrVal'] = W('offer', 14)
C['ch3'] = (ST('n3'), EN('n3'))
C['wk'] = (ST('existing'), W('existing', 7) - 0.03)
C['wkCheck'] = W('existing', 2); C['wkB'] = W('existing', 3); C['wkX'] = W('existing', 6)
C['eng'] = (W('existing', 7) - 0.03, EN('existing'))
C['engT'] = [W('existing', 8), W('existing', 9), W('existing', 12)]
C['rch'] = (W('reach', 4), EN('reach'))
C['ana'] = (W('because', 8) - 0.03, EN('because'))
C['anaNow'] = W('because', 15)
C['sav'] = (W('save', 6), W('save', 8) + 0.6)
C['fol'] = W('follow', 8)
C['folClick'] = WE('follow', 9) + 0.12
C['voice'] = VOICE
C['tail'] = {'take': 'follow', 'src_start': 303.57, 'src_hold': 304.02, 'slow': 0.22}  # source secs of the wave
C['total'] = TOTAL

# ---------------- zoom keys for base: (t, z, mode)  mode: cut | ramp | settle
Z = [(0, 1.14, 'cut'), (W('hook', 16), 1.36, 'ramp'),
     (EN('n1'), 1.14, 'settle'), (W('audience', 7), 1.32, 'ramp'),
     (EN('n2'), 1.30, 'settle'), (W('offer', 4), 1.14, 'ramp'), (C['scr'][1], 1.38, 'settle'),
     (EN('n3'), 1.14, 'cut'), (C['wk'][1], 1.16, 'settle'),
     (ST('reach'), 1.28, 'cut'), (W('reach', 5), 1.42, 'ramp'),
     (ST('because'), 1.14, 'cut'), (ST('save'), 1.16, 'settle'), (W('save', 8), 1.34, 'ramp'),
     (ST('follow'), 1.16, 'cut'), (W('follow', 8), 1.30, 'ramp')]

# ---------------- captions: (seg, small range, big range, accent, emoji, side)
G = [
 ('hook', (0, 3), (4, 4), 0, None),
 ('hook', (5, 6), (7, 7), 0, '1f4f8'),
 ('hook', (8, 9), (10, 11), 1, '2728'),
 ('hook', (12, 14), (15, 15), 0, '2705'),
 ('hook', (16, 18), (19, 21), 1, '1f644'),
 ('audience', (0, 3), (4, 6), 0, '1f3af'),
 ('audience', (7, 9), (10, 10), 1, '1f629'),
 ('offer', (0, 2), (3, 3), 1, '1f911'),
 ('offer', (4, 7), (8, 9), 0, '1f62c'),
 ('offer', (15, 18), (19, 19), 1, '1f971'),
 ('reach', (0, 3), (4, 4), 0, '1f62d'),
 ('reach', (5, 5), (6, 7), 1, '1f440'),
 ('because', (0, 1), (2, 2), 0, '1f914'),
 ('because', (3, 5), (6, 7), 1, '1f92f'),
 ('save', (0, 3), (4, 5), 0, '1f60e'),
 ('save', None, (6, 7), 1, '1f525'),
 ('save', (8, 9), (10, 10), 0, '1f4af'),
 ('save', (11, 12), (13, 14), 1, '1f9e0'),
 ('save', (15, 15), (16, 16), 0, '1f680'),
 ('follow', (0, 2), (3, 5), 1, '1f4a1'),
 ('follow', (6, 6), (7, 7), 0, '2728'),
 ('follow', None, (8, 9), 1, '1f44b'),
]
FIX = {'wanna': 'want to', 'and': 'and', '3.': '3'}
def wtext(seg, i):
    t = S[seg]['words'][i][2]
    if seg == 'hook' and i == 10: return '3'
    if seg == 'follow' and i == 4: return '&'
    t = FIX.get(t, t)
    t = t.rstrip(',.') if t not in ('3',) else t
    return t

def chartimes(t0, n, per=0.034, maxd=0.2):
    step = min(per, maxd / max(1, n))
    return [round(t0 + k * step, 3) for k in range(n)]

caps = []; ticks = []
# hard stops for captions: cutaways / chapter cards
STOPS = sorted([C['eng'][0], C['ch1'][0], C['feed'][0], C['ch2'][0], C['scr'][0], C['ch3'][0], C['ana'][0], TOTAL])
for gi, (seg, sm, bg, acc, emo) in enumerate(G):
    words = []
    def addw(i, big):
        txt = wtext(seg, i)
        if txt not in ('I', 'Instagram'): txt = txt.lower()
        t0 = max(W(seg, i) - 0.02, 0)
        ct = chartimes(t0, len(txt))
        words.append({'t': txt, 'c': ct, 'b': big})
        # typing ticks: up to 5 per word
        idx = [0] if (not big or len(ct) < 4) else [0, len(ct) // 2]
        for k in idx:
            ticks.append((ct[k], -19.0 if big else -22.0))
    if sm:
        for i in range(sm[0], sm[1] + 1): addw(i, 0)
    for i in range(bg[0], bg[1] + 1): addw(i, 1)
    start = words[0]['c'][0]
    caps.append({'start': start, 'acc': acc, 'emo': emo, 'words': words,
                 'bigT': words[[w['b'] for w in words].index(1)]['c'][0]})
for k, c in enumerate(caps):
    nxt = caps[k + 1]['start'] if k + 1 < len(caps) else TOTAL + 1
    stop = min([s for s in STOPS if s > c['start'] + 0.05] + [nxt])
    c['end'] = round(min(nxt, stop, c['start'] + 2.6), 3) if k + 1 < len(caps) else round(TOTAL + 1, 3)

# typed titles inside graphics: id -> (start, text, per-char)
TY = {}
def typed(key, t0, text, per=0.045):
    ct = [round(t0 + k * per, 3) for k in range(len(text))]
    TY[key] = {'t': text, 'c': ct}
    for k, x in enumerate(ct):
        if text[k] != ' ' and (k == 0 or text[k - 1] == ' ' or k % 3 == 0): ticks.append((x, -20))
typed('ch1t', C['ch1'][0] + 0.30, 'YOUR AUDIENCE', 0.05)
typed('fdB', C['feedStop'] - 0.05, 'STOP SCROLLING?', 0.035)
typed('ch2q', C['ch2'][0] + 0.95, 'what are you actually selling?', 0.026)
typed('scrL2', C['scrVal'], 'VALUABLE?', 0.04)
typed('ch3t', C['ch3'][0] + 1.25, 'CONTENT', 0.06)
typed('engS', W('existing', 7) - 0.02, 'are people', 0.035)
typed('engB', W('existing', 9) - 0.02, 'ENGAGING', 0.04)
typed('engC', W('existing', 10) - 0.02, 'with your posts?', 0.028)
typed('anB', C['anaNow'] - 0.05, 'RIGHT NOW', 0.045)

# ---------------- emojis on graphics (code, t0, t1, x, y, size, rot)
E = []
ex = C['hookExpand']
E += [('1f914', 0.03, ex + 0.3, 70, 230, 210, -10), ('1f9d0', 0.12, ex + 0.3, 800, 330, 200, 10),
      ('1f62c', 0.21, ex + 0.3, 60, 1450, 200, 8), ('1fae3', 0.30, ex + 0.3, 810, 1540, 210, -8)]
E += [('1f440', C['ch1'][0] + 0.45, C['ch1'][1], 760, 120, 200, 8)]
E += [('1f6d1', C['feedStop'], C['feed'][1], 790, 330, 210, 10), ('270b', C['feedStop'] + 0.12, C['feed'][1], 60, 1300, 220, -12)]
E += [('1f48e', C['scr'][0] + 0.05, C['scr'][1], 430, 500, 220, 0)]
E += [('1f4ca', C['ch3'][0] + 0.35, C['ch3'][1], 800, 120, 190, 10)]
E += [('1f4c8', C['wkCheck'], C['wk'][1], 820, 230, 190, 8), ('1f4c9', C['wkX'], C['wk'][1], 820, 870, 190, -8)]
E += [('1f60d', C['engT'][1] + 0.05, C['eng'][1], 790, 1190, 210, 10), ('1f4ac', W('existing', 12), C['eng'][1], 70, 1390, 190, -10)]
E += [('23f0', C['ana'][0] + 0.1, C['ana'][1], 810, 70, 190, 10)]
E += [('1f389', C['folClick'] + 0.05, TOTAL + 1, 90, 1340, 210, -10), ('1f64c', C['folClick'] + 0.2, TOTAL + 1, 790, 1300, 200, 10)]
BURST = [('1f4af', [c for c in caps if c['emo'] == '1f4af'][0]['bigT']), ('1f525', [c for c in caps if c['emo'] == '1f525'][0]['bigT']),
         ('2764_fe0f_200d_1f525', C['engT'][1] + 0.1), ('1f389', C['folClick'])]

meta = json.load(open('../apple/meta.json'))
C['bye'] = VOICE + 0.12
TL = {'speed': D['speed'], 'C': C, 'Z': Z, 'caps': caps, 'typed': TY, 'E': E, 'burst': BURST, 'meta': meta, 'total': TOTAL}
json.dump(TL, open('timeline.json', 'w'))
open('timeline.js', 'w').write('window.TL=' + json.dumps(TL) + ';')

# ---------------- SFX list
SX = []
def a(t, f, db): SX.append((round(t, 3), f, db))
for t, db in ticks:
    a(t, 'tick%d' % random.randint(0, 3), db + random.uniform(-1.5, 1.5))
PK = {'whoosh01': .60, 'whoosh02': 1.45, 'whoosh03': .65, 'whoosh04': .60, 'whoosh05': .65, 'whoosh06': 1.05}
def wh(t, f, db): a(t - PK[f], f, db)
for k in range(4): a(0.03 + k * 0.09, 'click02', -17)
wh(ex + 0.12, 'whoosh04', -9)
a(C['prof'][0] + 0.03, 'select02', -14)
for k in range(3): a(C['chips'][0] + k * 0.11, 'click04', -14)
wh(W('hook', 16) + 0.05, 'whoosh03', -16)
# chapter 1 (clean cut in => impact on the cut)
a(C['ch1'][0] - 0.02, 'subdrop01', -6); wh(C['ch1'][0], 'whoosh01', -8); a(C['ch1'][0] + 0.25, 'hud01', -15)
wh(C['ch1'][1], 'whoosh04', -14)
wh(C['feed'][0], 'whoosh05', -9); a(C['feedStop'], 'select01', -8)
a(C['ch2'][0] - 0.02, 'subdrop03', -6); wh(C['ch2'][0], 'whoosh05', -8); a(C['ch2'][0] + 0.8, 'click04', -17)
wh(C['ch2'][1], 'whoosh04', -14)
wh(C['scr'][0], 'whoosh03', -10); a(C['scrVal'], 'select01', -15); wh(C['scr'][1], 'whoosh05', -15)
a(C['ch3'][0] - 0.02, 'subdrop01', -7); wh(C['ch3'][0], 'whoosh01', -8)
for k in range(9): a(C['ch3'][0] + 0.25 + k * 0.06, 'click02', -22)
wh(C['ch3'][1], 'whoosh06', -13)
a(C['wkCheck'], 'bells', -10); wh(C['wkB'] + 0.1, 'whoosh03', -15); a(C['wkX'], 'wrong', -10)
for t in C['engT']: a(t, 'click04', -13)
a(C['rch'][0], 'select01', -13)
wh(C['ana'][0], 'whoosh05', -8); a(C['ana'][0] + 0.15, 'hud01', -12)
a(C['sav'][0] + 0.03, 'notification', -8)
a(C['fol'], 'select01', -14); a(C['folClick'], 'click02', -7); a(C['folClick'] + 0.06, 'bells', -13); a(C['folClick'] + 0.05, 'select02', -16)
a(C['bye'] + 0.45 - PK['whoosh03'], 'whoosh03', -8); a(C['bye'] + 0.62, 'select02', -15)
json.dump(SX, open('sfx.json', 'w'))
print('caps', len(caps), 'ticks', len(ticks), 'sfx', len(SX), 'total', TOTAL)
for c in caps: print(round(c['start'], 2), round(c['end'], 2), ' '.join(w['t'] for w in c['words']))
