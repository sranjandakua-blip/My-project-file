# Base talking-head layer: cuts from edl.json, global speed SP, face-centred zoom with speed-curved
# punch-ins ('ramp'), post-cutaway 'settle', hook "framed card on peach" open, grade LUT + subtle vignette,
# and a speed-ramped slow-mo outro (motion-interpolated) for the wave/goodbye.
# Inputs (build dir): edl.json, faces.json, timeline.json (Z keys, C.hookExpand, C.tail), grade.cube, vig.npy
# Output: base.mp4 (1080x1920, 30 fps)
import json,subprocess,numpy as np,cv2,sys,math,os
W,H,FPS=1080,1920,30
SRC='../dl/raw.mp4'
edl=json.load(open('edl.json')); TL=json.load(open('timeline.json'))
F=json.load(open('faces.json')); SW,SH=F['size']; FACE=F['faces']
SP=TL.get('speed',1.08); Z=TL['Z']; C=TL['C']
def eo(x): x=min(1,max(0,x)); return 1-(1-x)**4
def zoom_at(t):
    i=max(k for k in range(len(Z)) if Z[k][0]<=t+1e-6)
    t0,z,mode=Z[i]; drift=1+0.010*(t-t0)                       # slow push inside every shot
    if mode=='ramp' and i>0:                                     # speed-curve punch-in (fast start, soft land)
        zp=Z[i-1][1]*(1+0.010*(t0-Z[i-1][0])); p=eo((t-t0)/0.24); return (zp+(z-zp)*p)*drift
    if mode=='settle':                                           # after a cutaway: snap in +12%, ease out
        p=eo((t-t0)/0.40); return (z*1.12+(z-z*1.12)*p)*drift
    return z*drift                                               # 'cut' = clean hard cut
def frame_at(img,fx,fy,z):
    cw=SW/z; ch=cw*H/W
    x0=min(max(fx-cw/2,0),SW-cw); y0=min(max(fy-0.44*ch,0),SH-ch); sc=W/cw   # face at ~44% height
    M=np.array([[sc,0,-x0*sc],[0,sc,-y0*sc]],np.float32)
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
offs=[];o=0
for n,s,e in edl: offs.append(o); o+=(e-s)/SP
NF=int(round(TL['total']*FPS)); VIG=np.load('vig.npy')[...,None]
pt,pb=np.array([255,214,186],np.float32),np.array([255,163,120],np.float32)
yy=np.linspace(0,1,H)[:,None,None]; PEACH=(pt*(1-yy)+pb*yy).repeat(W,1).astype(np.float32)
def rounded_mask(w,h,r):
    m=np.zeros((h,w),np.uint8); r=max(1,int(r))
    cv2.rectangle(m,(r,0),(w-r,h),255,-1); cv2.rectangle(m,(0,r),(w,h-r),255,-1)
    for cx,cy in [(r,r),(w-r,r),(r,h-r),(w-r,h-r)]: cv2.circle(m,(cx,cy),r,255,-1,cv2.LINE_AA)
    return m
EX=C.get('hookExpand',-1)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-vf','lut3d=grade.cube','-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p','base.mp4'],stdin=subprocess.PIPE)
def put(out): enc.stdin.write((out*VIG).astype(np.uint8).tobytes())
fi=0; sz=SW*SH*3
for si,(n,s,e) in enumerate(edl):
    fx,fy,_=FACE[n]; fx*=SW; fy*=SH
    nfr=int(round((offs[si]+(e-s)/SP)*FPS))-fi
    dec=subprocess.Popen(['ffmpeg','-v','error','-ss',f'{s:.3f}','-i',SRC,'-t',f'{e-s+0.3:.3f}','-vf',f'setpts=PTS/{SP},fps=30,format=rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    last=None
    for k in range(nfr):
        b=dec.stdout.read(sz)
        if len(b)<sz: b=last
        last=b
        t=fi/FPS; out=frame_at(np.frombuffer(b,np.uint8).reshape(SH,SW,3),fx,fy,zoom_at(t))
        if EX>=0 and t<EX+0.30:   # hook: video in a rounded card on peach; holds, then whips open (speed ramp)
            p=eo((t-EX)/0.30); cs=min(1.0,0.70+0.30*p+0.012*min(t,EX)*(1-p)); hh=0.86+0.14*p
            src=out[int((H-H*hh)/2):int((H+H*hh)/2)]; cw2,ch2=int(W*cs),int(H*cs*hh)
            card=cv2.resize(src,(cw2,ch2),interpolation=cv2.INTER_AREA).astype(np.float32)
            m=(rounded_mask(cw2,ch2,48*(1-p)+1)/255.0)[...,None]; bg=PEACH.copy()
            x1,y1=(W-cw2)//2,(H-ch2)//2+int(40*(1-p))
            sh=np.zeros((H,W),np.float32); sh[max(0,y1+24):y1+ch2+24,x1:x1+cw2]=0.35*(1-p)
            bg=bg*(1-cv2.GaussianBlur(sh,(0,0),30)[...,None])
            bg[y1:y1+ch2,x1:x1+cw2]=bg[y1:y1+ch2,x1:x1+cw2]*(1-m)+card*m; out=bg.clip(0,255).astype(np.uint8)
        put(out); fi+=1
    dec.kill()
# ---- outro (C.tail = {take, src_start, src_hold, slow}): speed-ramp from SP down to `slow`x on interpolated
# 120 fps frames, freeze at src_hold with a slow push until the end.
T=C.get('tail')
if T and fi<NF:
    c0=T['src_start']-0.12
    if not os.path.exists('tail120.rgb'):
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(c0),'-i',SRC,'-t',str(T['src_hold']-c0+0.3),'-vf',
          'minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=rgb24','-f','rawvideo','tail120.rgb'],check=True)
    raw=np.fromfile('tail120.rgb',np.uint8); TF=len(raw)//sz; raw=raw[:TF*sz].reshape(TF,SH,SW,3)
    fx,fy,_=FACE[T['take']]; fx*=SW; fy*=SH; src=T['src_start']; tau=0
    while fi<NF:
        t=fi/FPS; k=min(TF-1,max(0,int(round((min(src,T['src_hold'])-c0)*120))))
        z=zoom_at(t)*((1+0.05*(src-T['src_hold'])/0.6) if src>T['src_hold'] else 1)
        put(frame_at(raw[k],fx,fy,z)); fi+=1
        src+=(T['slow']+(SP-T['slow'])*math.exp(-tau/0.20))/FPS; tau+=1/FPS
while fi<NF: put(out); fi+=1
enc.stdin.close(); enc.wait(); print('done',fi,'frames',file=sys.stderr)
