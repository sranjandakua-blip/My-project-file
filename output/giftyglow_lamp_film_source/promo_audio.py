import numpy as np, wave
SR=44100; B=60/70.6; M=1.45; OFF=M+B*17; DUR=OFF+2.6; N=int(SR*DUR)
rng=np.random.default_rng(11)
def hz(m): return 440*2**((m-69)/12)
def add(buf,sig,at):
    i=int(at*SR)
    if i>=N or i+len(sig)<=0: return
    if i<0: sig=sig[-i:]; i=0
    j=min(N,i+len(sig)); buf[i:j]+=sig[:j-i]
def piano(m,dur=3.0,v=0.3):
    n=int(SR*dur); x=np.arange(n)/SR; f=hz(m); s=np.zeros(n)
    for k,a in enumerate([1,.55,.28,.14,.07,.04],1):
        s+=a*np.sin(2*np.pi*f*k*x*(1+0.0004*k))*np.exp(-x*(0.9+0.8*k*f/400))
    att=np.minimum(x/0.006,1)
    return v*s*att
def pad(ms,dur,v=0.05,att=0.6,rel=0.8):
    n=int(SR*dur); x=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        for d in (-0.08,0.08):
            f=hz(m)*2**(d/12); s+=np.sin(2*np.pi*f*x)+0.3*np.sin(2*np.pi*2*f*x)
    e=np.minimum(x/att,1)*np.minimum((dur-x)/rel,1).clip(0,1)
    return v*s*e/len(ms)
mus=np.zeros(N); sfx=np.zeros(N)
# --- pre-drop: dark drone + room tone + riser
n=int(SR*(M+0.3)); x=np.arange(n)/SR
drone=0.05*(np.sin(2*np.pi*hz(33)*x)+0.6*np.sin(2*np.pi*hz(40)*x))*np.minimum(x/0.5,1)*np.clip((M+0.3-x)/0.3,0,1)
add(mus,drone,0)
room=np.cumsum(rng.standard_normal(int(SR*DUR)))*0.0; 
riser=rng.standard_normal(int(SR*1.1)); y=np.zeros_like(riser); a=0
cut=np.linspace(0.01,0.25,len(riser))
for i in range(len(riser)): a+=cut[i]*(riser[i]-a); y[i]=a
y*=np.linspace(0,1,len(y))**2.5*0.18
add(sfx,y,M-1.1)
# --- music from the drop
prog=[([57,60,64,71],45),([53,57,60,64],41),([48,55,60,62],36),([55,59,62,64],43)]  # Am9 Fmaj7 Cadd9 G6
t=M; k=0
while t<OFF-0.01:
    ch,root=prog[k%4]
    # rolled chord on the downbeat
    for i,m in enumerate(ch): add(mus,piano(m,3.0,0.16),t+i*0.025)
    add(mus,piano(root-12+12,3.0,0.20),t)
    # 8th-note arpeggio
    arp=[ch[1]+12,ch[2]+12,ch[3]+12,ch[2]+12]
    for j in range(4): 
        if t+B/2*(j+0) >= M+0.01 or j>0: add(mus,piano(arp[j],1.6,0.075),t+B/2*j+ (B/2 if j==0 else 0)*0)
    add(mus,pad(ch,2*B+0.9,0.07),t)
    # sub
    nn=int(SR*2*B); xx=np.arange(nn)/SR
    add(mus,0.22*np.sin(2*np.pi*hz(root-12)*xx)*np.exp(-xx/1.2)*np.minimum(xx/0.01,1),t)
    t+=2*B; k+=1
# final note on the end card + held pad
add(mus,piano(76,3.5,0.14),OFF+0.45); add(mus,piano(69,3.5,0.12),OFF+0.45)
add(mus,pad([57,64,71],2.4,0.06,0.5,1.4),OFF)
# --- soft pulse from the 2nd cut
def kick():
    n=int(SR*.3); x=np.arange(n)/SR; f=48+70*np.exp(-x/0.025)
    return 0.32*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/0.11)
def shaker(v):
    n=int(SR*.06); s=np.diff(rng.standard_normal(n+1)); return v*0.035*s*np.exp(-np.arange(n)/SR/0.018)
t=M+2*B
while t<OFF-0.1:
    add(mus,kick(),t)
    for j in range(4): add(mus,shaker(1 if j%2 else 0.55),t+j*B/2+B/4)
    t+=2*B if False else B
# --- sfx
def click(v=0.5,f=2400):
    n=int(SR*.05); x=np.arange(n)/SR; s=rng.standard_normal(n)
    s=np.diff(s,prepend=0)*np.exp(-x/0.0025)+0.6*np.sin(2*np.pi*f*x)*np.exp(-x/0.004)
    th=0.5*np.sin(2*np.pi*90*x)*np.exp(-x/0.02)
    return v*(s+th)
add(sfx,click(0.55),M-0.005); add(sfx,click(0.3,2000),M+0.09)
n=int(SR*0.32); x=np.arange(n)/SR
buzz=0.03*np.sign(np.sin(2*np.pi*100*x))*np.exp(-x/0.12)*(0.5+0.5*np.sin(2*np.pi*31*x)); add(sfx,buzz,M)
add(sfx,0.6*buzz[:int(SR*0.18)]*np.hanning(int(SR*0.18)),0.5)
boom_n=int(SR*1.4); xb=np.arange(boom_n)/SR
add(sfx,0.35*np.sin(2*np.pi*np.cumsum(38+30*np.exp(-xb/0.08))/SR)*np.exp(-xb/0.45),M)
for i,m in enumerate([88,93,95,100]): add(sfx,piano(m,1.5,0.05),M+0.08+i*0.05)
def whoosh(d=0.6,v=0.16):
    n=int(SR*d); s=rng.standard_normal(n); y=np.zeros(n); a=0
    c=0.02+0.2*np.sin(np.pi*np.arange(n)/n)
    for i in range(n): a+=c[i]*(s[i]-a); y[i]=a
    return v*y*np.sin(np.pi*np.arange(n)/n)**2/np.abs(y).max()
add(sfx,whoosh(),M+2*B-0.3); add(sfx,whoosh(),M+10*B-0.3)  # shadow passes at T0, T4
add(sfx,whoosh(),M+B*2*5-0.3) if False else None
add(sfx,click(0.5),OFF-0.005); add(sfx,click(0.25,1900),OFF+0.07)
# --- reverb on music
ir_n=int(SR*1.8); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR/0.45); ir/=np.abs(ir).sum()/6
wet=np.fft.irfft(np.fft.rfft(mus,len(mus)+ir_n)*np.fft.rfft(ir,len(mus)+ir_n))[:N]
mus=mus+0.35*wet
# fades
tt=np.arange(N)/SR
mus*=np.clip((DUR-tt)/1.6,0,1)
out=mus*0.9+sfx
out/=np.abs(out).max()/0.9
st=np.stack([out,out],1)
w=wave.open('promo_audio.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
print('dur',DUR)

