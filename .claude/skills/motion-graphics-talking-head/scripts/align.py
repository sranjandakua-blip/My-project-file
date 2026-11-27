# Re-transcribes each kept take (from edl.json) and maps word times onto the OUTPUT timeline
# (after cuts and the global speed-up SP). Writes words.json: {speed,total,segs:{take:{start,end,words:[[t0,t1,word],...]}}}
# Print shows word indices -> use them in timeline.py.
import json,numpy as np
from faster_whisper import WhisperModel
SP=1.08
m=WhisperModel("small.en",device="cpu",compute_type="int8")
e=json.load(open('edl.json'))
a=np.fromfile('../work/a16.wav',dtype=np.int16)[22:].astype(np.float32)/32768
# group consecutive pieces of same take for transcription context
groups=[]
for i,(n,s,t) in enumerate(e):
    if groups and groups[-1]['name']==n: groups[-1]['idx'].append(i)
    else: groups.append({'name':n,'idx':[i]})
offs=[];o=0
for n,s,t in e: offs.append(o); o+=t-s
words=[];segs={}
for g in groups:
    clip=[np.zeros(8000,np.float32)];mapping=[]  # (clip_time_start, clip_time_end, out_offset)
    ct=0.5
    for i in g['idx']:
        n,s,t=e[i]; c=a[int(s*16000):int(t*16000)]; clip.append(c); mapping.append((ct,ct+len(c)/16000,offs[i])); ct+=len(c)/16000
    clip.append(np.zeros(8000,np.float32)); clip=np.concatenate(clip)
    def mp(x):
        for c0,c1,of in mapping:
            if x<=c1+1e-3: return (of+max(0,x-c0))/SP
        c0,c1,of=mapping[-1]; return (of+(c1-c0))/SP
    sg,_=m.transcribe(clip,word_timestamps=True,language='en',condition_on_previous_text=False)
    ws=[[round(mp(w.start),3),round(mp(w.end),3),w.word.strip()] for s_ in sg for w in s_.words]
    segs[g['name']]={'start':round(offs[g['idx'][0]]/SP,3),'end':round((offs[g['idx'][-1]]+e[g['idx'][-1]][2]-e[g['idx'][-1]][1])/SP,3),'words':ws}
    print(g['name'],segs[g['name']]['start'],segs[g['name']]['end'],' '.join(f"{i}:{w[2]}@{w[0]}" for i,w in enumerate(ws)))
json.dump({'speed':SP,'total':o/SP,'segs':segs},open('words.json','w'))
