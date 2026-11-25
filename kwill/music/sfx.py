# Subtle synthesized sound design: whooshes on transitions, soft pops on text, clicks on taps.
import numpy as np, wave, json, sys
SR=48000; ev=json.load(open(sys.argv[1])); DUR=float(sys.argv[2])
out=np.zeros((int(DUR*SR)+SR,2)); rng=np.random.default_rng(3)
def put(x,t,g,pan=0):
    i=int(max(0,t)*SR); j=min(len(out),i+len(x)); x=x[:j-i]*g
    out[i:j,0]+=x*np.sqrt(.5*(1-pan)); out[i:j,1]+=x*np.sqrt(.5*(1+pan))
def lp(x,a):  # one-pole low-pass with time-varying coefficient
    y=np.zeros_like(x); s=0.0
    for k in range(len(x)): s+=a[k]*(x[k]-s); y[k]=s
    return y
def whoosh(d=0.45):
    n=int(d*SR); t=np.linspace(0,1,n); x=rng.standard_normal(n)
    a=0.02+0.25*np.sin(np.pi*t)**2; y=lp(x,a)-lp(x,a*0.15)
    return y*np.sin(np.pi*t)**1.5/np.abs(y).max()
def pop():
    n=int(0.09*SR); t=np.arange(n)/SR; f=900*np.exp(-t/0.02)+500
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.022)
def click():
    n=int(0.04*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*2400*t)*0.5+rng.standard_normal(n)*0.5)*np.exp(-t/0.006)
def ding():
    n=int(0.9*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*1568*t)+0.5*np.sin(2*np.pi*2349*t)+0.25*np.sin(2*np.pi*3136*t))*np.exp(-t/0.25)*np.minimum(1,t/0.003)
def tick():
    n=int(0.025*SR); t=np.arange(n)/SR
    return (rng.standard_normal(n)*0.6+np.sin(2*np.pi*3200*t)*0.4)*np.exp(-t/0.004)
for t in ev.get('soft',[]): put(whoosh(0.6),t-0.25,0.3)
for t in ev.get('ding',[]): put(ding(),t,0.18)
ty=ev.get('type',[])
if len(ty)==2:
    t=ty[0]
    while t<ty[1]: put(tick(),t,0.12,pan=rng.uniform(-.3,.3)); t+=rng.uniform(0.045,0.09)
for t in ev['whoosh']: put(whoosh(),t-0.22,0.55,pan=rng.uniform(-.3,.3))
for t in ev['pop']: put(pop(),t,0.22,pan=rng.uniform(-.2,.2))
for t in ev['click']: put(click(),t-0.02,0.35)
out=out[:int(DUR*SR)]
with wave.open(sys.argv[3],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
