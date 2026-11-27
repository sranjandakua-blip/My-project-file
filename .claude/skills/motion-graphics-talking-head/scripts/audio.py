# Voice + SFX mix. Voice chain is deliberately minimal (client feedback: heavy processing hurt quality):
# mono -> atempo (WSOLA) -> 60 Hz HPF -> gentle 1.8:1 comp -> static gain to -15 LUFS. NO afftdn, NO EQ, NO loudnorm.
# SFX list comes from sfx.json written by timeline.py: [[time_s, file_stem_in_../sfx, gain_db], ...]
import json,subprocess,numpy as np
SR=48000
edl=json.load(open('edl.json')); SX=json.load(open('sfx.json'))
parts=[];lab=[]
for i,(n,s,t) in enumerate(edl):
    parts.append(f"[0:a]atrim={s}:{t},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={t-s-0.012:.3f}:d=0.012[a{i}]");lab.append(f"[a{i}]")
fc=";".join(parts)+";"+"".join(lab)+f"concat=n={len(edl)}:v=0:a=1,pan=mono|c0=0.5*c0+0.5*c1,atempo=1.08,highpass=f=60:poles=2,acompressor=threshold=-21dB:ratio=1.8:attack=15:release=220:knee=6:makeup=1[out]"
subprocess.run(['ffmpeg','-v','error','-y','-i','../dl/raw.mp4','-filter_complex',fc,'-map','[out]','-ar',str(SR),'-c:a','pcm_f32le','voice_pre.wav'],check=True)
import re
m=subprocess.run(['ffmpeg','-hide_banner','-i','voice_pre.wav','-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
I=float(re.findall(r"I:\s+(-?[\d.]+) LUFS",m)[-1]); g=-15.0-I
print('voice LUFS',I,'gain',round(g,2))
subprocess.run(['ffmpeg','-v','error','-y','-i','voice_pre.wav','-af',f'volume={g:.2f}dB','-ac','2','-ar',str(SR),'-c:a','pcm_f32le','voice.wav'],check=True)
def load(f):
    b=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(b,np.float32).reshape(-1,2)
v=load('voice.wav'); print('voice dur',len(v)/SR)
TLT=json.load(open('timeline.json'))['total']; total=int((TLT+0.1)*SR)
mix=np.zeros((total,2),np.float32); mix[:len(v)]+=v
cache={}
for t,f,db in SX:
    if f not in cache:
        x=load(f'../sfx/{f}.wav'); cache[f]=x/np.abs(x).max()*0.89
    x=cache[f]*10**(db/20); i=max(0,int(t*SR)); n=min(len(x),total-i)
    if n>0: mix[i:i+n]+=x[:n]
mix.tofile('mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','mix.f32','-af','alimiter=limit=0.94:attack=2:release=40:level=false','-c:a','pcm_s16le','mix.wav'],check=True)
