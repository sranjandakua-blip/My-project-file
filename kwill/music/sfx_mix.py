# Places library sound effects on the timeline. Usage: sfx_mix.py events.json duration libdir user_riser.wav out.wav
import numpy as np, json, sys, subprocess, wave, os
ev=json.load(open(sys.argv[1])); DUR=float(sys.argv[2]); LIB=sys.argv[3]; URISER=sys.argv[4]; OUT=sys.argv[5]
SR=48000; out=np.zeros((int(DUR*SR),2)); M=json.load(open(f'{LIB}/map.json'))
def load(path,rate=1.0):
    af=f'aresample={SR}'+(f',asetrate={int(SR*rate)},aresample={SR}' if rate!=1 else '')
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-af',af,'-ac','2','-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
def env(x,w=0.05):
    m=x.mean(1)**2; k=max(1,int(w*SR)); return np.sqrt(np.convolve(m,np.ones(k)/k,'same'))
def db(v): return 20*np.log10(v+1e-12)
def put(x,t,gain_db):
    x=x*10**(gain_db/20); i=int(round(t*SR)); a=max(0,-i); i=max(0,i); j=min(len(out),i+len(x)-a)
    if j>i: out[i:j]+=x[a:a+j-i]
def place(key,t,target,align='onset',rate=1.0,maxlen=None,fade=0.06):
    x=load(f"{LIB}/{M[key]}",rate)
    if maxlen: n=int(maxlen*SR); x=x[:n].copy(); f=int(fade*SR); x[-f:]*=np.linspace(1,0,f)[:,None]
    e=env(x); pk=np.argmax(e); g=target-db(e[pk])
    if align=='onset': on=np.argmax(np.abs(x).max(1)>0.1*np.abs(x).max()); put(x,t-on/SR,g)
    else: put(x,t-pk/SR,g)
# kind -> (sample, target dB (50ms RMS peak), align, time offset of the peak/onset relative to event)
MAP={'impact':('hit',-13,'onset',0),'pop':('pop',-21,'onset',0),'logo':('magic',-18,'peak',0.2),'slideup':('swing',-23,'peak',0.3),
     'flick':('click',-24,'onset',0),'chime':('ding',-22,'onset',0),'swipe':('trans',-19,'peak',0.22),'click':('mouse',-21,'onset',0),
     'cash':('cash',-20,'onset',0),'boop':('notif',-22,'onset',0),'shimmer':('energy',-22,'onset',0),'bloop':('bloop',-21,'onset',0),
     'sparkle':('granted',-23,'onset',0),'tick':('click',-25,'onset',0),'shutter':('shutter',-20,'onset',0),'msg':('msg',-22,'onset',0)}
for e in ev:
    t,k=e[0],e[1]; p=e[2] if len(e)>2 else 1
    if k in MAP:
        s,g,al,off=MAP[k]; rate=p if k in ('pop','flick','tick') else 1.0
        place(s,t+off,g,al,rate=rate,maxlen=1.6 if k=='shimmer' else None)
    elif k=='zip': place('whip4' if p>0 else 'whip6',t+0.22,-19,'peak')
    elif k=='typing': place('keys',t,-31,'onset',maxlen=p,fade=0.1)
# form-split riser: peak lands as the split opens
place('riser_s',34.2,-19,'peak')
# user's riser on the hook: peak exactly on the slam at 0.85s
r=load(URISER); e=env(r); pk=np.argmax(e); seg=r[int(pk-0.85*SR):]; seg=seg.copy(); f=int(0.04*SR); seg[:f]*=np.linspace(0,1,f)[:,None]
tail=seg[int(0.6*SR):int(0.85*SR)]; g=-19-db(np.sqrt((tail.mean(1)**2).mean())); put(seg,0.0,g)
pk_all=np.abs(out).max(); out*=0.5   # -6 dB headroom; restored with a limiter at mix time
with wave.open(OUT,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
print('placed',len(ev),'events; peak',round(db(pk_all),1),'dBFS')
