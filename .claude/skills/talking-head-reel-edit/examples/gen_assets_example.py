"""Write HTML for every graphic asset (screens, tiles, chips, bubbles, end cards) + jobs.json for shoot.js.
Usage: python3 -I gen_assets.py <W>"""
import json, os, re, sys, html
W = sys.argv[1]
F = f'{W}/fonts'; IC = f'{W}/icons'; ML = json.load(open(f'{W}/assets/ml/ml.json'))
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


# ======================= VIDEO 1 (churn) =======================
C = ML['churn']
# tutorial feed
thumbs = [('ML IN 10 HOURS', '#ff5f6d,#ffc371', 'Machine Learning Full Course 2026', '2.1M views · 3 months ago', '10:04:12'),
          ('DEEP LEARNING', '#4776e6,#8e54e9', 'Deep Learning Explained in 1 Hour', '880K views · 1 month ago', '1:02:45'),
          ('PYTHON FOR AI', '#11998e,#38ef7d', 'Python for AI — Complete Beginner', '1.4M views · 8 months ago', '6:31:20'),
          ('GEN AI 2026', '#f7971e,#ffd200', 'Generative AI Crash Course', '640K views · 2 weeks ago', '48:10'),
          ('NEURAL NETS', '#ee0979,#ff6a00', 'Neural Networks From Scratch', '1.1M views · 1 year ago', '2:14:03'),
          ('LLMs EXPLAINED', '#00c6ff,#0072ff', 'How LLMs Actually Work', '930K views · 5 months ago', '37:22')]
tabs = ''.join(f'<div class=tab><span class=fav></span>{t}</div>' for t in
               ['ML Full Course', 'Deep Learning…', 'Python for AI', 'Gen AI Crash…', 'Neural Nets…', 'LLMs Explained', 'Pandas Tutor…', 'NumPy in 1hr', 'ML Project…', 'TensorFlow…', 'Kaggle Tips', 'Stats for ML'])
grid = ''.join(f'''<div class=v><div class=th style="background:linear-gradient(135deg,{g})"><span>{a}</span><i>{d}</i></div>
  <div class=vt>{t}</div><div class=vm>{m}</div></div>''' for a, g, t, m, d in thumbs)
css_feed = """.tabs{display:flex;gap:4px;padding:8px 12px 0;background:#181825;overflow:hidden}
.tab{flex:none;width:138px;background:#232336;border-radius:10px 10px 0 0;padding:9px 10px;font:600 15px Inter;color:#bac2de;white-space:nowrap;overflow:hidden;display:flex;gap:7px;align-items:center}
.fav{width:18px;height:13px;border-radius:4px;background:#ff2d2d;flex:none}
.addr{background:#0f0f0f;padding:16px 26px;display:flex;align-items:center;gap:16px}
.addr .q{flex:1;background:#222;border:1px solid #333;border-radius:999px;padding:12px 24px;font:400 22px Inter;color:#eee}
.g{background:#0f0f0f;display:grid;grid-template-columns:1fr 1fr;gap:26px 22px;padding:10px 26px 30px}
.th{height:262px;border-radius:16px;position:relative;display:flex;align-items:center;justify-content:center}
.th span{font:800 44px Poppins;color:#fff;text-shadow:0 4px 14px rgba(0,0,0,.35);text-align:center;line-height:1.05;padding:0 16px}
.th i{position:absolute;right:10px;bottom:10px;background:rgba(0,0,0,.8);color:#fff;font:600 17px Inter;font-style:normal;padding:3px 8px;border-radius:6px}
.vt{font:600 22px Inter;color:#f1f1f1;margin-top:12px}.vm{font:400 18px Inter;color:#aaa;margin-top:4px}"""
page('v1_tutorials', f'''<div class=canvas><div class=win style="top:600px;height:1120px;background:#0f0f0f">{bar("Videos — machine learning full course")}
  <div class=tabs>{tabs}</div><div class=addr><span class=fav style="width:40px;height:28px;border-radius:8px"></span>
  <div class=q>machine learning full course</div></div><div class=g>{grid}</div></div></div>''', extra_css=css_feed)

copy_code = '''import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("customers.csv")   # copied from tutorial
X = df.drop(columns=["churn"])
y = df["churn"]'''
fit_code = '''model = RandomForestClassifier()
model.fit(X, y)'''
trace = ('<b>ValueError</b>                    Traceback (most recent call last)\n'
         'Cell In[2], line 2\n      1 model = RandomForestClassifier()\n----&gt; 2 model.fit(X, y)\n...\n'
         '<b>ValueError: could not convert string to float: \'monthly\'</b>')
page('v1_err_a', f'<div class=canvas><div class=win style="top:640px;height:800px">{bar("tutorial_copy.ipynb")}'
     f'{cell(1, copy_code)}{cell(2, fit_code)}<div class=out style="color:#7f849c">running…</div></div></div>')
page('v1_err_b', f'<div class=canvas><div class=win style="top:640px;height:800px">{bar("tutorial_copy.ipynb")}'
     f'{cell(1, copy_code)}{cell(2, fit_code)}<div class=err>{trace}</div></div></div>')

css_doc = """.doc{padding:34px 46px;font:400 27px/1.5 Inter;color:#cdd6f4}
.doc h1{font:800 44px Poppins;color:#fff;margin-bottom:6px}.doc h2{font:700 26px Poppins;color:#f9e2af;margin:26px 0 12px;letter-spacing:1px}
.doc .meta{color:#a6adc8;font-size:23px}.req{display:flex;gap:16px;align-items:center;margin:12px 0}
.bx{width:30px;height:30px;border:3px solid #89b4fa;border-radius:8px;flex:none}"""
reqs = ['Predict which customers will churn', 'Handle missing + categorical data', f'Target ≥ 75% accuracy on unseen data',
        'Ship a web app for the support team']
page('v1_brief', f'''<div class=canvas><div class=win style="top:640px;height:760px">{bar("project_brief.md")}<div class=doc>
  <div class=meta>PROJECT BRIEF · Telecom client</div><h1>Customer Churn Predictor</h1>
  <div class=meta>{C['rows']:,} customer records · 5 features</div><h2>REQUIREMENTS</h2>
  {''.join(f'<div class=req><span class=bx></span>{r}</div>' for r in reqs)}</div></div>
  <div class=chip style="top:1460px">REAL REQUIREMENTS</div></div>''', extra_css=css_doc)

nulls = '\n'.join(f'{k:<16}{v}' for k, v in C['nulls'].items())
head_rows = C['head'][:4]
screen('v1_data', cell(3, 'df.isnull().sum()', out=f'{nulls}\ndtype: int64') +
       cell(4, 'df = df.dropna()\ndf = pd.get_dummies(df, columns=["contract"])\ndf.head()') +
       df_table(head_rows, ['tenure', 'monthly_bill', 'support_tickets', 'usage_hrs', 'contract']),
       top=640, height=760, chip='REAL DATA', title='churn_model.ipynb')

screen('v1_train', cell(5, 'model = RandomForestClassifier(n_estimators=300,\n                               max_depth=9)\nmodel.fit(X_train, y_train)\naccuracy_score(y_test, model.predict(X_test))',
                        out=f'<span style="color:#a6e3a1;font-weight:700;font-size:30px">{C["acc"]:.4f}</span>') +
       f'<div style="padding:4px 0 0 110px"><img src="file://{W}/assets/ml/cm_churn.png" style="width:470px;border-radius:12px"></div>',
       top=600, height=860, chip='REAL IMPLEMENTATION', chip_y=1500, title='churn_model.ipynb')

css_app = """.app{background:#0e1117;height:100%;padding:34px 50px;font:400 24px Inter;color:#fafafa}
.app h1{font:800 46px Poppins;margin-bottom:6px}.app .sub{color:#a3a8b8;font-size:22px;margin-bottom:26px}
.f{margin:14px 0}.f label{display:block;color:#c9cdd8;font-size:21px;margin-bottom:8px}
.in{background:#262730;border-radius:10px;padding:13px 18px;font:600 24px Inter}
.sl{height:8px;background:#3a3b47;border-radius:4px;position:relative;margin:18px 0 8px}.sl b{position:absolute;left:0;top:0;height:8px;border-radius:4px;background:#ff4b4b}
.sl i{position:absolute;top:-9px;width:26px;height:26px;border-radius:50%;background:#ff4b4b}
.btn{display:inline-block;background:#ff4b4b;color:#fff;font:700 24px Inter;padding:14px 30px;border-radius:10px;margin:14px 0 20px}
.res{border-radius:14px;padding:22px 26px;font:700 30px Poppins}"""
churn_risk = int(C['demo_risk'][0])
page('v1_app', f'''<div class=canvas><div class=win style="top:600px;height:900px">{bar("churn-predictor.app")}<div class=app>
  <h1>Churn Predictor</h1><div class=sub>Random Forest · trained on {C['clean_rows']:,} customers</div>
  <div class=f><label>Tenure (months): 4</label><div class=sl><b style="width:6%"></b><i style="left:5%"></i></div></div>
  <div class=f><label>Monthly bill (₹)</label><div class=in>1,290</div></div>
  <div class=f><label>Support tickets (last 90 days)</label><div class=in>4</div></div>
  <div class=f><label>Contract</label><div class=in>Monthly</div></div>
  <div class=btn>Predict</div>
  <div class=res style="background:#3e1a1d;color:#ff8a8a">⚠ High churn risk: {churn_risk}%</div></div></div>
  <div class=chip style="top:1540px">REAL PROJECTS</div></div>''', extra_css=css_app)

# ======================= VIDEO 2 (loan) =======================
L = ML['loan']
lo_risk, hi_risk = int(L['demo_risk'][0]), int(L['demo_risk'][1])
css_phone = """.ph{position:absolute;left:50%;transform:translateX(-50%);width:600px;height:1180px;border-radius:70px;background:#0b0b0f;
  box-shadow:0 40px 100px rgba(0,0,0,.7),0 0 0 3px #2b2b33;padding:22px}
.sc{width:100%;height:100%;border-radius:52px;background:#f5f6fa;overflow:hidden;font-family:Inter;color:#14161f;position:relative}
.nt{position:absolute;left:50%;top:14px;transform:translateX(-50%);width:170px;height:38px;border-radius:20px;background:#0b0b0f}
.hd{padding:80px 36px 20px;font:800 34px Poppins}.card{margin:0 26px 20px;background:#fff;border-radius:26px;padding:28px;box-shadow:0 8px 24px rgba(20,22,40,.08)}
.x{width:150px;height:150px;border-radius:50%;background:#ffe3e3;margin:6px auto 18px;display:flex;align-items:center;justify-content:center;font:800 90px Inter;color:#e5383b}
.big{font:800 40px Poppins;text-align:center;color:#e5383b}.mid{text-align:center;color:#666b80;font-size:22px;margin-top:6px}
.row{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #eef0f5;font-size:23px}
.tag{background:#e3f9e5;color:#1a7f37;font:700 20px Inter;padding:5px 14px;border-radius:999px}"""
page('v2_rejected', f'''<div class=canvas><div class=ph style="top:610px"><div class=sc><div class=nt></div>
  <div class=hd>Loan Status</div><div class=card><div class=x>✕</div><div class=big>Application Rejected</div>
  <div class=mid>Personal Loan · ₹3,00,000</div></div>
  <div class=card><div class=row><span>CIBIL Score</span><b style="font-size:30px">700 <span class=tag>GOOD</span></b></div>
  <div class=row><span>Credit history</span><b>2 yrs</b></div><div class=row style="border:0"><span>Decision</span><b style="color:#e5383b">High risk profile</b></div></div>
  </div></div></div>''', extra_css=css_phone)

# CIBIL sticker (transparent) – semicircle gauge with needle at 700
import math
ang = math.pi * (1 - (700 - 300) / 600)
nx, ny = 210 + 105 * math.cos(ang), 190 - 105 * math.sin(ang)
page('v2_cibil', f'''<div style="width:440px;height:370px;padding:10px"><div style="background:#fff;border-radius:34px;width:420px;height:350px;
  box-shadow:0 18px 40px rgba(0,0,0,.45);position:relative;font-family:Inter;text-align:center">
  <svg width="420" height="220" style="position:absolute;left:0;top:10px"><defs><linearGradient id=g x1=0 x2=1>
  <stop offset=0 stop-color="#e5383b"/><stop offset=.5 stop-color="#ffb703"/><stop offset=1 stop-color="#2a9d8f"/></linearGradient></defs>
  <path d="M65 190 A145 145 0 0 1 355 190" fill=none stroke="url(#g)" stroke-width=32 stroke-linecap=round />
  <line x1=210 y1=190 x2="{nx:.0f}" y2="{ny:.0f}" stroke="#14161f" stroke-width=10 stroke-linecap=round /><circle cx=210 cy=190 r=15 fill="#14161f"/></svg>
  <div style="position:absolute;left:0;right:0;top:212px;font:800 66px/1 Poppins;color:#14161f">700</div>
  <div style="position:absolute;left:0;right:0;top:292px;font:800 26px Poppins;color:#1a7f37;letter-spacing:2px">CIBIL SCORE · GOOD</div>
  </div></div>''', w=440, h=370, transparent=True)

# tiles (icon squircle + label), transparent
def tile(name, icon, color, bg, label, size=170):
    page(f'tile_{name}', f'''<div style="width:300px;height:{size + 90}px;display:flex;flex-direction:column;align-items:center;padding-top:10px">
      <div style="width:{size}px;height:{size}px;border-radius:{int(size * .27)}px;background:{bg};display:flex;align-items:center;justify-content:center;
      box-shadow:0 14px 34px rgba(0,0,0,.45),inset 0 0 0 1px rgba(255,255,255,.25)">{svg(f"{IC}/{icon}.svg", color, int(size * .58))}</div>
      <div style="margin-top:12px;font:700 30px Poppins;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.8),0 0 2px rgba(0,0,0,.9)">{label}</div></div>''',
         w=300, h=size + 90, transparent=True)


tile('python', 'si_python', '#3776AB', 'linear-gradient(160deg,#ffffff,#e9eef7)', 'Python')
tile('sklearn', 'si_scikitlearn', '#F7931E', 'linear-gradient(160deg,#ffffff,#eef1f7)', 'Machine Learning')
tile('pytorch', 'si_pytorch', '#EE4C2C', 'linear-gradient(160deg,#ffffff,#f3ecea)', 'Deep Learning')
tile('genai', 'lu_sparkles', '#ffffff', 'linear-gradient(160deg,#8e54e9,#4776e6)', 'Generative AI')
tile('youtube', 'si_youtube', '#FF0000', 'linear-gradient(160deg,#ffffff,#f4eeee)', 'YouTube')
tile('banking', 'lu_landmark', '#ffffff', 'linear-gradient(160deg,#2a9d8f,#1d6b68)', 'Banking')
tile('fintech', 'lu_smartphone', '#ffffff', 'linear-gradient(160deg,#4776e6,#2b4bb8)', 'Fintech')
tile('risk', 'lu_shield-check', '#ffffff', 'linear-gradient(160deg,#f7971e,#e0670b)', 'Risk')
tile('consulting', 'lu_briefcase-business', '#ffffff', 'linear-gradient(160deg,#8e54e9,#6236b5)', 'Consulting')
tile('dm', 'lu_message-circle', '#ffffff', 'linear-gradient(160deg,#ff5f6d,#c2185b)', 'DM', size=150)
# data-flow tiles
for n, ic, col, lab in [('income', 'lu_indian-rupee', '#2a9d8f', 'Income'), ('spend', 'lu_shopping-cart', '#f7971e', 'Spending'),
                        ('bills', 'lu_file-text', '#4776e6', 'Bill Payments'), ('upi', 'lu_smartphone', '#8e54e9', 'UPI Data'),
                        ('job', 'lu_briefcase-business', '#e5383b', 'Job Stability')]:
    tile(f'df_{n}', ic, '#ffffff', f'linear-gradient(160deg,{col},{col}cc)', lab, size=150)
page('ai_box', f'''<div style="width:520px;height:520px;display:flex;align-items:center;justify-content:center">
  <div style="width:340px;height:340px;border-radius:70px;background:linear-gradient(160deg,#243b80,#101a3d);
  box-shadow:0 0 70px 18px rgba(80,140,255,.55),inset 0 0 0 3px rgba(140,180,255,.7);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">
  {svg(f"{IC}/lu_brain-circuit.svg", "#9ec5ff", 150)}<div style="font:800 40px Poppins;color:#fff;letter-spacing:2px">AI MODEL</div></div></div>''',
     w=520, h=520, transparent=True)
page('dataflow_bg', '<div class=canvas></div>')

# chips (transparent)
def chip(name, text, bg='#FFE135', fg='#121212', size=44):
    sh = 'none' if bg == 'transparent' else '0 12px 30px rgba(0,0,0,.45)'
    tsh = '0 3px 10px rgba(0,0,0,.7)' if bg == 'transparent' else 'none'
    page(f'chip_{name}', f'''<div style="display:inline-block;padding:16px 20px"><div id=c style="background:{bg};color:{fg};font:800 {size}px Poppins;
      padding:14px {12 if bg == 'transparent' else 38}px;border-radius:999px;letter-spacing:.5px;box-shadow:{sh};text-shadow:{tsh};white-space:nowrap">{text}</div></div>''',
         w=1080, h=size + 80, transparent=True)


chip('watching', 'WATCHING ≠ BUILDING', bg='#e5383b', fg='#fff')
chip('learn', 'LEARN'); chip('apply', 'APPLY'); chip('build', 'BUILD')
chip('arrow', '→', bg='transparent', fg='#FFE135', size=54)
chip('oldway', 'OLD WAY: 1 SCORE', bg='#14161f', fg='#FFE135')
chip('finance', 'FINANCE + AI = FUTURE-READY')
chip('riskscore', 'RISK SCORE', bg='#FFE135')
chip('income', 'INCOME', bg='#14161f', fg='#fff', size=44); chip('spend', 'SPENDING', bg='#14161f', fg='#fff', size=44)
chip('bills', 'BILLS', bg='#14161f', fg='#fff', size=44); chip('upi', 'UPI DATA', bg='#14161f', fg='#fff', size=44)
chip('job', 'JOB', bg='#14161f', fg='#fff', size=44)
page('chip_buildwithai', '''<div style="display:inline-block;padding:16px 20px"><div style="background:#14161f;border-radius:30px;padding:22px 40px;text-align:center;
  box-shadow:0 12px 30px rgba(0,0,0,.45)"><div style="font:800 40px Poppins;color:#fff">DON'T JUST LEARN AI.</div>
  <div style="font:800 52px Poppins;color:#FFE135">BUILD WITH AI.</div></div></div>''', w=1080, h=200, transparent=True)
page('btn_enroll', '''<div style="width:1080px;display:flex;flex-direction:column;align-items:center;padding:16px">
  <div style="background:#F05A28;color:#fff;font:800 56px Poppins;padding:14px 64px;border-radius:16px;box-shadow:0 14px 34px rgba(0,0,0,.5);letter-spacing:1px">ENROLL NOW</div>
  <div style="margin-top:14px;font:800 36px Poppins;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.85);border-bottom:4px solid #F05A28;padding-bottom:4px">LINK IN BIO</div></div>''',
     w=1080, h=230, transparent=True)

# risk profiles (model output) – two states
def prof(n, cibil, bills, inc, risk, good):
    col, bg, lab = ('#2a9d8f', '#e3f9f2', 'LOW RISK') if good else ('#e5383b', '#ffe3e3', 'HIGH RISK')
    return f'''<div style="background:#fff;border-radius:30px;padding:30px 36px;margin:0 70px 34px;box-shadow:0 20px 50px rgba(0,0,0,.5);font-family:Inter;color:#14161f">
    <div style="display:flex;justify-content:space-between;align-items:center"><div style="font:800 42px Poppins">{n}</div>
    <div style="background:{bg};color:{col};font:800 30px Poppins;padding:8px 22px;border-radius:999px">{lab}</div></div>
    <div style="color:#666b80;font-size:24px;margin:10px 0 18px">CIBIL {cibil} · Bills on time {bills} · ₹{inc}/mo</div>
    <div style="display:flex;align-items:center;gap:18px"><div style="flex:1;height:22px;border-radius:11px;background:#eef0f5;overflow:hidden">
    <div style="width:{risk}%;height:100%;background:{col}"></div></div><div style="font:800 40px Poppins;color:{col}">{risk}%</div></div>
    <div style="color:#9aa0b4;font-size:20px;margin-top:6px">predicted default risk</div></div>'''


p1 = prof('Rahul', 742, '97%', '68,000', lo_risk, True); p2 = prof('Amit', 700, '61%', '31,000', hi_risk, False)
hdr = '<div style="text-align:center;font:800 34px Poppins;color:#9ec5ff;letter-spacing:3px;margin:0 0 30px">MODEL OUTPUT</div>'
page('v2_risk_a', f'<div class=canvas><div style="position:absolute;top:640px;left:0;right:0">{hdr}{p1}</div></div>')
page('v2_risk_b', f'<div class=canvas><div style="position:absolute;top:640px;left:0;right:0">{hdr}{p1}{p2}</div></div>')

lnulls = '\n'.join(f'{k:<16}{v}' for k, v in L['nulls'].items())
screen('v2_data', cell(1, 'df = pd.read_csv("loan_applications.csv")\ndf.isnull().sum()', out=f'{lnulls}\ndtype: int64') +
       cell(2, 'df = df.dropna()\ndf.head()') + df_table(L['head'][:4], ['income', 'spend_ratio', 'bills_on_time', 'upi_txns', 'job_years', 'cibil']),
       top=640, height=760, chip='CLEAN DATA', title='loan_model.ipynb')
screen('v2_train', cell(3, 'X = df.drop(columns=["default"])\ny = df["default"]\nmodel = RandomForestClassifier(n_estimators=300)\nmodel.fit(X_train, y_train)',
                        out='RandomForestClassifier(n_estimators=300)') +
       cell(4, 'pd.Series(model.feature_importances_, X.columns)', out='\n'.join(f'{k:<16}{v:.3f}' for k, v in L['importances'])),
       top=640, height=760, chip='TRAIN MODEL', title='loan_model.ipynb')
screen('v2_eval', cell(5, 'accuracy_score(y_test, model.predict(X_test))',
                       out=f'<span style="color:#a6e3a1;font-weight:700;font-size:30px">{L["acc"]:.4f}</span>') +
       f'<div style="padding:4px 0 0 110px"><img src="file://{W}/assets/ml/cm_loan.png" style="width:470px;border-radius:12px"></div>',
       top=620, height=700, chip='EVALUATE', title='loan_model.ipynb')
page('v2_app', f'''<div class=canvas><div class=win style="top:600px;height:900px">{bar("loan-approval.app")}<div class=app>
  <h1>Loan Approval AI</h1><div class=sub>Random Forest · trained on {L['clean_rows']:,} applications</div>
  <div class=f><label>Monthly income (₹)</label><div class=in>68,000</div></div>
  <div class=f><label>Bills paid on time</label><div class=sl><b style="width:97%;background:#2a9d8f"></b><i style="left:95%;background:#2a9d8f"></i></div></div>
  <div class=f><label>UPI transactions / month</label><div class=in>52</div></div>
  <div class=f><label>Years in current job</label><div class=in>6</div></div>
  <div class=btn style="background:#2a9d8f">Check eligibility</div>
  <div class=res style="background:#123b33;color:#7ff0c9">✓ APPROVED · default risk {lo_risk}%</div></div></div>
  <div class=chip style="top:1540px">BUILD APP</div></div>''', extra_css=css_app)

# comment bubble typing states
css_cm = """.cb{width:1000px;margin:20px 40px;background:#fff;border-radius:999px;display:flex;align-items:center;gap:22px;padding:16px 22px;
  box-shadow:0 16px 40px rgba(0,0,0,.5);font-family:Inter}
.av{width:74px;height:74px;border-radius:50%;background:linear-gradient(135deg,#f9ce34,#ee2a7b,#6228d7);flex:none}
.tx{flex:1;font:800 46px Poppins;color:#14161f;letter-spacing:1px}.ph2{font:400 34px Inter;color:#9aa0b4}
.post{font:700 32px Inter;color:#0095f6}.car{display:inline-block;width:4px;height:46px;background:#0095f6;vertical-align:middle;margin-left:4px}"""
word = 'COURSE'
for i in range(len(word) + 1):
    t = f'<span class=ph2>Add a comment…</span>' if i == 0 else f'{word[:i]}<span class=car></span>'
    page(f'comment_{i}', f'<div class=cb><div class=av></div><div class=tx>{t}</div><div class=post style="opacity:{1 if i else .35}">Post</div></div>',
         w=1080, h=150, transparent=True, extra_css=css_cm)

# end cards (teal, like the reference's brand card)
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
p_v1 = ['<div class="l w">STOP JUST</div>', '<div class="l w">WATCHING.</div>', '<div class="l">START</div>', '<div class="l">BUILDING.</div>',
        '<div class="bt">ENROLL NOW</div><div class="lk">LINK IN BIO</div>']
WA = f'<div class="wa"><div class="ic">{svg(f"{IC}/si_whatsapp.svg", "#ffffff", 74)}</div><div class="n">+91-8177988081</div></div>'
p_v1.append(WA)
for k in (2, 4, 5, 6): end(f'end_v1_{k}', p_v1, k)
p_v2 = ['<div class="sm">COMMENT</div>', '<div class="l">&quot;COURSE&quot;</div>', '<div class="sm" style="margin-top:40px">WE\'LL SEND THE DETAILS</div>',
        '<div class="l w" style="font-size:120px">IN YOUR DM</div>']

# phone-number CTA card: shown 2-3 s on its own, BEFORE the final CTA frame (client rule, Nov 2026)
PHONE = '+91-8177988081'
page('phone_card', f"""<div class=end><div class="sm">FOR COURSE DETAILS</div><div class="l" style="font-size:130px">WHATSAPP US</div>
  <div class="wa" style="transform:scale(1.35);margin-top:110px"><div class="ic">{svg(f"{IC}/si_whatsapp.svg", "#ffffff", 74)}</div>
  <div class="n">{PHONE}</div></div><div class="sm" style="margin-top:110px;font-size:52px">TAP · SAVE · MESSAGE</div></div>""", extra_css=css_end)
p_v2.append(WA)
for k in (2, 4, 5): end(f'end_v2_{k}', p_v2, k)

json.dump(jobs, open(f'{W}/assets/jobs.json', 'w'), indent=0)
print(len(jobs), 'jobs')
