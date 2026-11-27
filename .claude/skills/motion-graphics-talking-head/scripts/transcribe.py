# Usage: python3 transcribe.py ../work/a16.wav ../work/tx.json   (a16.wav = 16 kHz mono s16 WAV of the raw)
# Prints every segment with times so you can pick the best take of each line.
import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
import numpy as np
audio=np.fromfile(sys.argv[1],dtype=np.int16)[22:].astype(np.float32)/32768
segs,info=m.transcribe(audio,word_timestamps=True,vad_filter=False,language=None)
out=[]
for s in segs:
    out.append({"s":s.start,"e":s.end,"t":s.text,"w":[[w.start,w.end,w.word,w.probability] for w in s.words]})
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}",flush=True)
json.dump({"lang":info.language,"segs":out},open(sys.argv[2],"w"))
