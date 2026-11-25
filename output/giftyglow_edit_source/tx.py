import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
import numpy as np,wave
wf=wave.open(sys.argv[1]);a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
segs,info=m.transcribe(a,word_timestamps=True)
print(info.language)
out=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append(dict(w=w.word.strip(),s=round(w.start,2),e=round(w.end,2)))
json.dump(out,open(sys.argv[2],"w"),indent=0)
