import numpy as np, wave, sys
SR=48000; DUR=24.89; N=int(SR*DUR); rng=np.random.default_rng(7)
t=np.arange(N)/SR
def env(n,a=0.005,d=1.0):
    x=np.arange(n)/SR; return np.minimum(x/a,1)*np.exp(-x/d)
def add(buf,sig,at,warp=False):
    if warp and at>=15.11: at-=0.36
    i=int(at*SR)
    if i>=N: return
    j=min(N,i+len(sig)); buf[i:j]+=sig[:j-i]
def hz(m): return 440*2**((m-69)/12)
# ---- music ----
mus=np.zeros(N)
bpm=100; beat=60/bpm; bar=4*beat
chords=[[53,57,60,64],[55,59,62,67],[52,55,59,62],[57,60,64,67]]  # Fmaj7 G Em7 Am7
roots=[41,43,40,45]
def ep(m,dur,vel):
    n=int(SR*dur); x=np.arange(n)/SR; f=hz(m)
    s=(np.sin(2*np.pi*f*x)+.35*np.sin(2*np.pi*2*f*x)*np.exp(-x/0.4)+.12*np.sin(2*np.pi*3*f*x)*np.exp(-x/0.2))
    s*= (1+0.15*np.sin(2*np.pi*4.5*x))
    return vel*s*env(n,0.004,1.1)
k=0; tt=0.0
while tt<DUR:
    c=chords[k%4]
    for hit,v in [(0,1.0),(1.5*beat,0.55),(2.5*beat,0.7)]:
        for i,m in enumerate(c):
            add(mus,ep(m,2.6,0.16*v),tt+hit+i*0.012)
    # bass
    n=int(SR*bar); x=np.arange(n)/SR
    add(mus,0.32*np.sin(2*np.pi*hz(roots[k%4]-12+12)*x)*env(n,0.01,0.9),tt)
    add(mus,0.22*np.sin(2*np.pi*hz(roots[k%4])*x)*env(n,0.01,0.5),tt+2*beat)
    tt+=bar; k+=1
# drums from 2.4s
def kick():
    n=int(SR*0.35); x=np.arange(n)/SR; f=50+90*np.exp(-x/0.03)
    return 0.55*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/0.12)
def hat(v):
    n=int(SR*0.05); s=rng.standard_normal(n); s=np.diff(s,prepend=0); return v*0.06*s*np.exp(-np.arange(n)/SR/0.012)
tt=bar
while tt<DUR-0.8:
    for b in range(4):
        if b in (0,2): add(mus,kick(),tt+b*beat)
        add(mus,hat(1.0),tt+b*beat+beat/2); add(mus,hat(0.5),tt+b*beat)
    tt+=bar
# gentle intro/outro fades
mus*=np.minimum(t/0.6,1)*np.minimum((DUR-t)/0.6,1)
# ---- sfx ----
sfx=np.zeros(N)
def adds(sig,at): add(sfx,sig,at,True)
def whoosh(d=0.35,v=0.35):
    n=int(SR*d); x=np.arange(n)/SR; s=rng.standard_normal(n)
    # sweeping one-pole lowpass
    out=np.zeros(n); y=0; cut=np.linspace(0.02,0.35,n)**1.2
    for i in range(n): y+=cut[i]*(s[i]-y); out[i]=y
    e=np.sin(np.pi*np.minimum(x/d,1))**2
    return v*out*e/ (np.abs(out).max()+1e-9)
def pop(v=0.35,f0=900):
    n=int(SR*0.12); x=np.arange(n)/SR; f=f0*np.exp(-x/0.05)+300
    return v*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/0.035)
def click(v=0.25):
    n=int(SR*0.03); s=rng.standard_normal(n); s=np.diff(s,prepend=0)
    return v*s*np.exp(-np.arange(n)/SR/0.004)
def shimmer(v=0.12):
    out=np.zeros(int(SR*1.4))
    for i,m in enumerate([84,88,91,96,100]):
        n=int(SR*1.0); x=np.arange(n)/SR
        s=np.sin(2*np.pi*hz(m)*x)*env(n,0.003,0.35)
        out[int(i*0.06*SR):int(i*0.06*SR)+n]+=s
    return v*out
for w in [3.00,11.20,12.90,16.55,17.55,18.25,18.85,22.62]: adds(whoosh(),w-0.18)
adds(whoosh(0.5,0.3),14.80-0.25); adds(shimmer(),14.82)
for p_ in [10.45,20.90,21.72]: adds(pop(),p_)
adds(pop(0.25,1200),22.77); adds(pop(0.25,1100),22.97); adds(shimmer(0.1),22.65)
adds(click(0.4),13.18)
for i in range(10): adds(click(0.22),13.42+i*0.105)
def wr(fn,x):
    x=np.clip(x,-1,1); w=wave.open(fn,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
wr('music.wav',mus/np.abs(mus).max()*0.8); wr('sfx.wav',sfx)
