# Original instrumental bed for the Kwill short. Synthesised from scratch with numpy.
import numpy as np, wave, sys
SR=48000; BPM=104; BEAT=60/BPM; BAR=4*BEAT
DUR=float(sys.argv[1]) if len(sys.argv)>1 else 44.4
N=int((DUR+3)*SR); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def hz(m): return 440*2**((m-69)/12)
RING=float(sys.argv[3]) if len(sys.argv)>3 else 1e9
def add(sig,t,pan=0.0,g=1.0,final=False):
    if not final and t>=RING-0.02: return
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*g; L[i:j]+=s*np.sqrt(0.5*(1-pan)); R[i:j]+=s*np.sqrt(0.5*(1+pan))
def env(n,a,d_tau):
    t=np.arange(n)/SR; e=np.exp(-t/d_tau); ai=int(a*SR)
    if ai>0: e[:ai]*=np.linspace(0,1,ai)
    return e
def keys(m,dur,vel=1.0):          # soft electric-piano tone
    n=int((dur+1.2)*SR); t=np.arange(n)/SR; f=hz(m)
    s=np.sin(2*np.pi*f*t+0.6*np.sin(2*np.pi*f*t)*np.exp(-t/0.25))
    s+=0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.4)+0.08*np.sin(2*np.pi*3*f*t)*np.exp(-t/0.15)
    e=env(n,0.006,0.9); rel=np.ones(n); k=int(dur*SR); rel[k:]=np.exp(-np.arange(n-k)/SR/0.25)
    return s*e*rel*(1+0.08*np.sin(2*np.pi*4.5*t))*vel
def bass(m,dur):
    n=int((dur+0.2)*SR); t=np.arange(n)/SR; f=hz(m)
    s=np.tanh(1.6*(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)))
    e=env(n,0.004,0.45); k=int(dur*SR); e[k:]*=np.exp(-np.arange(n-k)/SR/0.04)
    return s*e
def pluck(m):
    n=int(0.6*SR); t=np.arange(n)/SR; f=hz(m)
    s=sum(np.sin(2*np.pi*f*h*t)/h*np.exp(-t*h*3.5) for h in range(1,6))
    return s*env(n,0.002,0.22)
def kick():
    n=int(0.35*SR); t=np.arange(n)/SR
    f=48+90*np.exp(-t/0.035); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env(n,0.001,0.12)
def hat(open_=False):
    n=int((0.18 if open_ else 0.05)*SR); x=rng.standard_normal(n)
    x=np.diff(np.concatenate([[0],x]))  # crude high-pass
    return x*env(n,0.0005,0.05 if open_ else 0.012)
def clap():
    n=int(0.25*SR); x=rng.standard_normal(n); x=np.convolve(x,np.ones(6)/6,'same')
    e=env(n,0.001,0.07); 
    for d in (0.0,0.011,0.022): e[int(d*SR):int(d*SR)+40]+=0.6
    return x*e*0.6
# IV - V - iii - vi in C  (Fmaj7, G6, Em7, Am7)
chords=[[53,57,60,64],[55,59,62,64],[52,55,59,62],[57,60,64,67]]
roots=[41,43,40,45]
arp=[[72,69,65,67],[71,67,62,64],[71,67,64,62],[72,69,64,67]]
nbars=int(np.ceil(min(DUR,RING)/BAR))
for b in range(nbars):
    t0=b*BAR; c=chords[b%4]
    for (bt,ln,v) in [(0,1.4,0.55),(1.5,0.4,0.35),(2.5,1.4,0.45)]:
        for m in c: add(keys(m,ln*BEAT,v),t0+bt*BEAT,pan=(m-60)/30)
    for (bt,ln) in [(0,1.2),(1.5,0.4),(2,0.9),(3.5,0.4)]:
        add(bass(roots[b%4]+(12 if bt==3.5 else 0),ln*BEAT),t0+bt*BEAT,g=0.42)
    if b>=1:   # drums enter on bar 2
        for k in (0,1.5,2,): add(kick(),t0+k*BEAT,g=0.55 if k!=1.5 else 0.3)
        for k in (1,3): add(clap(),t0+k*BEAT,g=0.12)
        for e in range(8): add(hat(e%4==3),t0+e*BEAT/2,pan=0.3,g=0.045 if e%2 else 0.028)
    if b>=2:   # pluck arpeggio enters on bar 3
        for e in range(8):
            m=arp[b%4][e%4]+(0 if e<4 else 0)
            add(pluck(m),t0+e*BEAT/2,pan=-0.35 if e%2 else 0.35,g=0.16)
if RING<DUR:   # final ringing chord on the sign-off
    c=[48,52,55,59,64]
    for m in c: add(keys(m,2.4,0.55),RING,pan=(m-60)/30,final=True)
    add(bass(36,2.4),RING,g=0.5,final=True)
# simple stereo reverb
ir_n=int(1.6*SR); t=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-t/0.38); irR=rng.standard_normal(ir_n)*np.exp(-t/0.38)
def conv(x,ir):
    m=len(x)+len(ir)-1; F=1<<int(np.ceil(np.log2(m)))
    return np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
wL=conv(L,irL); wR=conv(R,irR); wL*=0.12/np.abs(wL).max(); wR*=0.12/np.abs(wR).max()
L=L/np.abs(L).max()*0.8+wL; R=R/np.abs(R).max()*0.8+wR
st=np.stack([L,R],1); st=np.tanh(st*1.1)*0.9
n_out=int(DUR*SR); st=st[:n_out]
fi=int(0.4*SR); st[:fi]*=np.linspace(0,1,fi)[:,None]
with wave.open(sys.argv[2] if len(sys.argv)>2 else 'music/kwill_bgm.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print('bars',nbars,'dur',DUR)
