"""Shared helpers for reel graphics: page()/screen()/cell() notebook windows, tile(), chip(), end cards, phone CTA.
Usage in a per-video generator:
    import sys; sys.path.insert(0, '<skill>/scripts'); sys.argv = ['x', W]; from assetlib import *
    ... page()/tile()/chip()/end()/phone_card() calls ...
    finish()            # writes W/assets/jobs.json -> render with: node shoot.js W/assets/jobs.json
"""
import json, os, re, sys, html
W = sys.argv[1]
F = f'{W}/fonts'; IC = f'{W}/icons'
HT = f'{W}/assets/html'; PN = f'{W}/assets/png'
os.makedirs(HT, exist_ok=True); os.makedirs(PN, exist_ok=True)
jobs = []

CSS = f"""
@font-face{{font-family:Poppins;font-weight:700;src:url(file://{F}/Poppins_wght_700.ttf)}}
@font-face{{font-family:Poppins;font-weight:800;src:url(file://{F}/Poppins_wght_800.ttf)}}
@font-face{{font-family:Poppins;font-weight:600;src:url(file://{F}/Poppins_wght_600.ttf)}}
@font-face{{font-family:Inter;font-weight:400;src:url(file://{F}/Inter_wght_400.ttf)}}
@font-face{{font-family:Inter;font-weight:600;src:url(file://{F}/Inter_wght_600.ttf)}}
@font-face{{font-family:Inter;font-weight:800;src:url(file://{F}/Inter_wght_800.ttf)}}
@font-face{{font-family:Mono;font-weight:400;src:url(file://{F}/JetBrains_Mono_wght_400.ttf)}}
@font-face{{font-family:Mono;font-weight:700;src:url(file://{F}/JetBrains_Mono_wght_700.ttf)}}
@font-face{{font-family:Anton;src:url(file://{F}/Anton.ttf)}}
@font-face{{font-family:Mali;font-weight:600;src:url(file://{F}/Mali_wght_600.ttf)}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:transparent}}
.canvas{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter;color:#cdd6f4;
  background:radial-gradient(circle at 50% 58%,#1b2756 0%,#0c1124 55%,#070a14 100%)}}
.canvas:before{{content:'';position:absolute;inset:0;opacity:.07;
  background-image:linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);background-size:60px 60px}}
.win{{position:absolute;left:40px;width:1000px;border-radius:24px;background:#1e1e2e;overflow:hidden;
  box-shadow:0 40px 90px rgba(0,0,0,.65),0 0 0 1px rgba(255,255,255,.09)}}
.bar{{height:56px;background:#181825;display:flex;align-items:center;padding:0 22px;gap:10px;font:600 21px Inter;color:#9399b2}}
.dot{{width:15px;height:15px;border-radius:50%}}
.bar .t{{margin-left:18px}}
.cell{{display:flex;gap:14px;padding:16px 24px 6px}}
.pr{{font:400 19px Mono;color:#7f849c;width:72px;padding-top:16px;flex:none}}
.code{{flex:1;background:#11111b;border-radius:12px;padding:14px 18px;font:400 23px/1.5 Mono;color:#cdd6f4;white-space:pre;border-left:4px solid #45475a}}
.out{{font:400 21px/1.45 Mono;color:#cdd6f4;padding:6px 24px 10px 110px;white-space:pre}}
.kw{{color:#cba6f7}} .st{{color:#a6e3a1}} .fn{{color:#89b4fa}} .nu{{color:#fab387}} .cm{{color:#6c7086}}
.err{{background:#3b1d24;border-left:5px solid #f38ba8;color:#f5c2cf;margin:6px 24px 14px 110px;padding:14px 18px;border-radius:10px;font:400 20px/1.45 Mono;white-space:pre-wrap}}
.err b{{color:#f38ba8}}
.chip{{position:absolute;left:50%;transform:translateX(-50%);background:#FFE135;color:#121212;font:800 40px Poppins;
  padding:14px 38px;border-radius:999px;letter-spacing:.5px;box-shadow:0 12px 30px rgba(0,0,0,.45);white-space:nowrap}}
table{{border-collapse:collapse;font:400 19px Inter;margin:4px 24px 12px 110px}}
td,th{{padding:7px 12px;border-bottom:1px solid #313244;text-align:right}} th{{color:#a6adc8;font-weight:600}}
"""


def hl(code):
    """tiny python highlighter"""
    out = []
    for line in code.split('\n'):
        m = re.match(r'^(.*?)(#.*)?$', line); body, com = m.group(1), m.group(2) or ''
        toks = re.split(r'("[^"]*"|\b\d+\.?\d*\b|\b(?:import|from|as|def|return|for|in|if|else|True|False|None)\b|\b[A-Za-z_]\w*(?=\())', body)
        s = ''
        for t in toks:
            if not t: continue
            e = html.escape(t)
            if t.startswith('"'): s += f'<span class=st>{e}</span>'
            elif re.fullmatch(r'\d+\.?\d*', t): s += f'<span class=nu>{e}</span>'
            elif t in ('import', 'from', 'as', 'def', 'return', 'for', 'in', 'if', 'else', 'True', 'False', 'None'): s += f'<span class=kw>{e}</span>'
            elif re.fullmatch(r'[A-Za-z_]\w*', t) and line[line.find(t) + len(t):].startswith('('): s += f'<span class=fn>{e}</span>'
            else: s += e
        if com: s += f'<span class=cm>{html.escape(com)}</span>'
        out.append(s)
    return '\n'.join(out)


def page(name, body, w=1080, h=1920, transparent=False, extra_css=''):
    p = f'{HT}/{name}.html'
    open(p, 'w').write(f'<!doctype html><html><head><meta charset=utf-8><style>{CSS}{extra_css}</style></head><body>{body}</body></html>')
    jobs.append(dict(html=p, out=f'{PN}/{name}.png', w=w, h=h, transparent=transparent))


def bar(title):
    return (f'<div class=bar><span class=dot style="background:#f38ba8"></span><span class=dot style="background:#f9e2af"></span>'
            f'<span class=dot style="background:#a6e3a1"></span><span class=t>{title}</span></div>')


def cell(n, code, out='', err=''):
    s = f'<div class=cell><div class=pr>In [{n}]:</div><div class=code>{hl(code)}</div></div>'
    if out: s += f'<div class=out>{out}</div>'
    if err: s += f'<div class=err>{err}</div>'
    return s


def svg(path, color, size):
    t = open(path).read()
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    head, rest = t.split('>', 1)                      # drop the icon's own width/height
    head = re.sub(r'\s(width|height)="[^"]*"', '', head)
    t = head.replace('<svg', f'<svg width="{size}" height="{size}"', 1) + '>' + rest
    if 'lucide' in t or 'stroke="currentColor"' in t:
        t = t.replace('currentColor', color).replace('stroke-width="2"', 'stroke-width="1.8"')
    else:
        t = t.replace('<path ', f'<path fill="{color}" ')
    return t


def fmt(v):
    if v is None or v != v or v == 'nan': return '<span style="color:#f38ba8">NaN</span>'
    if isinstance(v, float) and v.is_integer() and abs(v) >= 100: return f'{int(v):,}'
    return v


def df_table(rows, cols):
    h = '<tr><th></th>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr>'
    for i, r in enumerate(rows):
        h += f'<tr><th>{i}</th>' + ''.join(f'<td>{fmt(r[c])}</td>' for c in cols) + '</tr>'
    return f'<table>{h}</table>'


def screen(name, inner, top, height, chip=None, chip_y=None, title=''):
    body = f'<div class=canvas><div class=win style="top:{top}px;height:{height}px">{bar(title)}{inner}</div>'
    if chip: body += f'<div class=chip style="top:{chip_y or top + height + 46}px">{chip}</div>'
    page(name, body + '</div>')


css_app = """.app{background:#0e1117;height:100%;padding:34px 50px;font:400 24px Inter;color:#fafafa}
.app h1{font:800 46px Poppins;margin-bottom:6px}.app .sub{color:#a3a8b8;font-size:22px;margin-bottom:26px}
.f{margin:14px 0}.f label{display:block;color:#c9cdd8;font-size:21px;margin-bottom:8px}
.in{background:#262730;border-radius:10px;padding:13px 18px;font:600 24px Inter}
.sl{height:8px;background:#3a3b47;border-radius:4px;position:relative;margin:18px 0 8px}.sl b{position:absolute;left:0;top:0;height:8px;border-radius:4px;background:#ff4b4b}
.sl i{position:absolute;top:-9px;width:26px;height:26px;border-radius:50%;background:#ff4b4b}
.btn{display:inline-block;background:#ff4b4b;color:#fff;font:700 24px Inter;padding:14px 30px;border-radius:10px;margin:14px 0 20px}
.res{border-radius:14px;padding:22px 26px;font:700 30px Poppins}"""

def tile(name, icon, color, bg, label, size=170):
    page(f'tile_{name}', f'''<div style="width:300px;height:{size + 90}px;display:flex;flex-direction:column;align-items:center;padding-top:10px">
      <div style="width:{size}px;height:{size}px;border-radius:{int(size * .27)}px;background:{bg};display:flex;align-items:center;justify-content:center;
      box-shadow:0 14px 34px rgba(0,0,0,.45),inset 0 0 0 1px rgba(255,255,255,.25)">{svg(f"{IC}/{icon}.svg", color, int(size * .58))}</div>
      <div style="margin-top:12px;font:700 30px Poppins;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.8),0 0 2px rgba(0,0,0,.9)">{label}</div></div>''',
         w=300, h=size + 90, transparent=True)


def chip(name, text, bg='#FFE135', fg='#121212', size=44):
    sh = 'none' if bg == 'transparent' else '0 12px 30px rgba(0,0,0,.45)'
    tsh = '0 3px 10px rgba(0,0,0,.7)' if bg == 'transparent' else 'none'
    page(f'chip_{name}', f'''<div style="display:inline-block;padding:16px 20px"><div id=c style="background:{bg};color:{fg};font:800 {size}px Poppins;
      padding:14px {12 if bg == 'transparent' else 38}px;border-radius:999px;letter-spacing:.5px;box-shadow:{sh};text-shadow:{tsh};white-space:nowrap">{text}</div></div>''',
         w=1080, h=size + 80, transparent=True)


css_end = """.end{width:1080px;height:1920px;background:radial-gradient(circle at 50% 40%,#2a8a86 0%,#1d6b68 45%,#11403e 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:6px}
.l{font:400 150px/1.02 Anton;color:#FFE135;letter-spacing:2px;text-shadow:0 8px 24px rgba(0,0,0,.25)}.l.w{color:#fff}
.sm{font:400 64px/1.1 Anton;color:#fff;letter-spacing:2px}.h{visibility:hidden}
.bt{margin-top:60px;background:#F05A28;color:#fff;font:800 64px Poppins;padding:18px 70px;border-radius:18px;box-shadow:0 14px 34px rgba(0,0,0,.35)}
.lk{margin-top:18px;font:800 42px Poppins;color:#fff;border-bottom:5px solid #F05A28}
.wa{margin-top:70px;display:flex;align-items:center;background:#fff;border-radius:999px;padding:0 48px 0 0;height:118px;
  box-shadow:0 16px 40px rgba(0,0,0,.35)}
.wa .ic{width:128px;height:128px;border-radius:50%;background:#111;display:flex;align-items:center;justify-content:center;margin:0 26px 0 -14px;
  box-shadow:0 8px 20px rgba(0,0,0,.35)}
.wa .n{font:700 58px Inter;color:#111;letter-spacing:1px}"""
def end(name, parts, k):
    body = ''.join(p if i < k else p.replace('class="', 'class="h ') for i, p in enumerate(parts))
    page(name, f'<div class=end>{body}</div>', extra_css=css_end)

PHONE = '+91-8177988081'
WA = f'<div class="wa"><div class="ic">{svg(f"{IC}/si_whatsapp.svg", "#ffffff", 74)}</div><div class="n">{PHONE}</div></div>'


def phone_card(name='phone_card', top='FOR COURSE DETAILS'):
    """client rule: shown on its own for 2-3 s BEFORE the final CTA frame"""
    page(name, f"""<div class=end><div class="sm">{top}</div><div class="l" style="font-size:130px">WHATSAPP US</div>
  <div class="wa" style="transform:scale(1.35);margin-top:110px"><div class="ic">{svg(f"{IC}/si_whatsapp.svg", "#ffffff", 74)}</div>
  <div class="n">{PHONE}</div></div><div class="sm" style="margin-top:110px;font-size:52px">TAP · SAVE · MESSAGE</div></div>""", extra_css=css_end)


def finish():
    json.dump(jobs, open(f'{W}/assets/jobs.json', 'w'), indent=0); print(len(jobs), 'jobs')
