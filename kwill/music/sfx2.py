# Varied synthesized sound design for the Kwill reel. Usage: sfx2.py events.json duration out.wav
import numpy as np, wave, json, sys
SR=48000; ev=json.load(open(sys.argv[1])); DUR=float(sys.argv[2])
out=np.zeros((int(DUR*SR)+2*SR,2)); rng=np.random.default_rng(11)
def put(x,t,g,pan=0.0):
    i=int(max(0,t)*SR); j=min(len(out),i+len(x)); x=x[:j-i]*g
    out[i:j,0]+=x*np.sqrt(.5*(1-pan)); out[i:j,1]+=x*np.sqrt(.5*(1+pan))
def tt(d): return np.arange(int(d*SR))/SR
def sweep(f0,f1,d,curve=3):
    t=tt(d); k=(t/d)**curve if f1>f0 else 1-(1-t/d)**curve
    f=f0+(f1-f0)*k; return np.sin(2*np.pi*np.cumsum(f)/SR)
def bp(x,lo,hi):
    F=np.fft.rfft(x); fr=np.fft.rfftfreq(len(x),1/SR); F[(fr<lo)|(fr>hi)]=0; return np.fft.irfft(F,len(x))
def bell(f,d=0.8,dec=0.3):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*2.76*f*t)*np.exp(-t/0.08)+0.2*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/0.04))*np.exp(-t/dec)*np.minimum(1,t/0.002)
def mix(*xs):
    n=max(len(x) for x in xs); y=np.zeros(n)
    for x in xs: y[:len(x)]+=x
    return y
G={}
G['impact']=lambda p: mix(sweep(110,38,0.6)*np.exp(-tt(0.6)/0.18)*1.2,bp(rng.standard_normal(int(0.25*SR)),80,900)*np.exp(-tt(0.25)/0.05)*0.6)
G['pop']=lambda p: sweep(700*p,1500*p,0.07,1)*np.exp(-tt(0.07)/0.02)
G['flick']=lambda p: mix(bp(rng.standard_normal(int(0.06*SR)),1800*p,6000)*np.exp(-tt(0.06)/0.012)*2,sweep(900*p,1300*p,0.05,1)*np.exp(-tt(0.05)/0.015)*0.5)
def logo(p):
    x=np.zeros(int(1.4*SR))
    for i,f in enumerate([1047,1319,1568,2093,2637]): s=bell(f,1.0,0.35)*0.5; k=int(i*0.06*SR); x[k:k+len(s)]+=s[:len(x)-k]
    sub=sweep(90,45,0.5)*np.exp(-tt(0.5)/0.2); x[:len(sub)]+=sub*0.9; return x
G['logo']=logo
G['slideup']=lambda p: sweep(220,700,0.35,2)*np.sin(np.pi*tt(0.35)/0.35)*0.6
G['chime']=lambda p: sum(bell(f*p,1.0,0.4) for f in (523,659,784))/2
G['swipe']=lambda p: bp(rng.standard_normal(int(0.22*SR)),2500,9000)*np.sin(np.pi*tt(0.22)/0.22)**2*2.2
G['click']=lambda p: (bp(rng.standard_normal(int(0.03*SR)),2000,8000)*2+np.sin(2*np.pi*3000*tt(0.03)))*np.exp(-tt(0.03)/0.005)
def scribble(p):
    t=tt(0.65); n=bp(rng.standard_normal(len(t)),1500,7000)
    am=0.5+0.5*np.abs(np.sin(2*np.pi*7*t+np.sin(2*np.pi*2.3*t)*2)); return n*am*np.sin(np.pi*t/0.65)**0.5*1.6
G['scribble']=scribble
def cash(p):
    x=np.zeros(int(1.2*SR)); r=bp(rng.standard_normal(int(0.12*SR)),3000,10000)*np.exp(-tt(0.12)/0.04)*1.5; x[:len(r)]+=r
    for d,f in ((0.05,2637),(0.13,3136)): s=bell(f,1.0,0.3)*0.6; k=int(d*SR); x[k:k+len(s)]+=s[:len(x)-k]
    return x
G['cash']=cash
def boop(p):
    a=np.sin(2*np.pi*660*tt(0.09))*np.exp(-tt(0.09)/0.05); b=np.sin(2*np.pi*990*tt(0.14))*np.exp(-tt(0.14)/0.07)
    x=np.zeros(int(0.25*SR)); x[:len(a)]+=a; k=int(0.09*SR); x[k:k+len(b)]+=b; return x*0.8
G['boop']=boop
G['zip']=lambda p: (sweep(250,1800,0.28,2) if p>0 else sweep(1800,250,0.28,2))*np.sin(np.pi*tt(0.28)/0.28)*0.45+bp(rng.standard_normal(int(0.28*SR)),3000,8000)*np.sin(np.pi*tt(0.28)/0.28)*0.4
def shimmer(p):
    x=np.zeros(int(1.3*SR))
    for i,f in enumerate([784,988,1175,1568,1976,2349,3136]): s=bell(f,0.9,0.25)*0.35; k=int(i*0.045*SR); x[k:k+len(s)]+=s[:len(x)-k]
    return x
G['shimmer']=shimmer
G['bloop']=lambda p: sweep(180,620,0.18,1)*np.exp(-tt(0.18)/0.09)*0.9
def sparkle(p):
    x=np.zeros(int(0.8*SR))
    for i in range(5): f=rng.uniform(2500,4200); s=bell(f,0.5,0.12)*0.3; k=int(i*0.05*SR); x[k:k+len(s)]+=s[:len(x)-k]
    return x
G['sparkle']=sparkle
G['tick']=lambda p: bell(1047*p,0.4,0.12)*0.7
def shutter(p):
    x=np.zeros(int(0.25*SR))
    for d in (0.0,0.09): s=bp(rng.standard_normal(int(0.04*SR)),800,7000)*np.exp(-tt(0.04)/0.008)*2; k=int(d*SR); x[k:k+len(s)]+=s
    return x
G['shutter']=shutter
G['msg']=lambda p: sweep(800,1600,0.12,1)*np.exp(-tt(0.12)/0.05)*0.7
def comb(x,delay_s,fb):
    d=max(1,int(delay_s*SR)); y=x.copy()
    for i in range(d,len(y)): y[i]+=fb*y[i-d]
    return y
def riser(d):
    # metallic riser: reversed 808-style cymbal + inharmonic metal partials gliding up with ring-mod, through a resonant comb
    n=int(d*SR); t=tt(d); k=t/d
    sq=lambda f: np.sign(np.sin(2*np.pi*f*np.arange(int(1.6*SR))/SR))
    cym=sum(sq(f) for f in (205.3,304.4,369.6,522.7,540.0,800.0))
    cym=bp(cym+0.6*rng.standard_normal(len(cym)),5000,15000)*np.exp(-np.arange(len(cym))/SR/0.45)
    rev=cym[::-1][-n:]
    glide=2**(k*1.6)
    metal=np.zeros(n)
    for r,amp in ((1,1),(1.41,.8),(2.13,.7),(2.76,.6),(3.52,.45),(4.07,.4),(5.4,.3)):
        metal+=amp*np.sin(2*np.pi*np.cumsum(420*r*glide)/SR)
    metal*=np.sin(2*np.pi*np.cumsum(55*glide)/SR)*0.5+0.5      # ring-mod shimmer
    metal=comb(metal*0.15,1/(700*1.0),0.55)
    x=rev/np.abs(rev).max()*0.9+metal/np.abs(metal).max()*0.55
    return x*np.clip(k,0.03,1)**1.6
G['riser']=riser
def typing(d):
    x=np.zeros(int((d+0.1)*SR)); t=0.0
    while t<d:
        n=int(0.03*SR); s=bp(rng.standard_normal(n),1500,6000)*np.exp(-tt(0.03)/0.005)*1.5+np.sin(2*np.pi*rng.uniform(180,260)*tt(0.03))*np.exp(-tt(0.03)/0.01)*0.4
        k=int(t*SR); x[k:k+n]+=s[:len(x)-k]; t+=rng.uniform(0.05,0.12)
    return x
GAIN={'impact':0.5,'pop':0.25,'flick':0.3,'logo':0.35,'slideup':0.25,'chime':0.25,'swipe':0.3,'click':0.35,'scribble':0.22,'cash':0.3,'boop':0.25,'zip':0.3,'shimmer':0.3,'bloop':0.35,'sparkle':0.3,'tick':0.22,'shutter':0.35,'msg':0.25,'riser':1.0,'typing':0.18}
for e in ev:
    t,k=e[0],e[1]; p=e[2] if len(e)>2 else 1
    x=typing(p) if k=='typing' else G[k](p)
    off=-0.12 if k in ('swipe','zip') else 0
    put(x/max(1e-6,np.abs(x).max()),t+off,GAIN[k],pan=rng.uniform(-.25,.25))
out=out[:int(DUR*SR)]
with wave.open(sys.argv[3],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
print('events',len(ev))
