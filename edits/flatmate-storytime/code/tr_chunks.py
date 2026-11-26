import sys, subprocess, numpy as np, time, json
from faster_whisper import WhisperModel
from concurrent.futures import ThreadPoolExecutor
raw = subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32)/32768
cuts = [0, 6.27, 12.47, 16.57, 23.53, 28.33, 31.37, 33.63, 38.67, 40.6, 46.0, 51.7, 56.4, 60.17, 63.53, 69.87, 73.17, 79.1, 83.62, len(a)/16000]
m = WhisperModel(sys.argv[2], device="cpu", compute_type="int8", cpu_threads=2, num_workers=2)
def run(i):
    s, e = cuts[i], cuts[i+1]
    seg = a[int(s*16000):int(e*16000)]
    out = []
    ss, _ = m.transcribe(seg, language=sys.argv[3], word_timestamps=True, beam_size=5, condition_on_previous_text=False,
                         temperature=[0.0, 0.2, 0.4], compression_ratio_threshold=2.2)
    for x in ss:
        out.append({"text": x.text, "words": [[w.word.strip(), round(w.start+s, 2), round(w.end+s, 2)] for w in x.words]})
    return i, out
t0 = time.time(); res = {}
with ThreadPoolExecutor(2) as ex:
    for i, out in ex.map(run, range(len(cuts)-1)):
        res[i] = out
        print(f"## chunk {i} {cuts[i]:.2f}-{cuts[i+1]:.2f}", flush=True)
        for x in out:
            print("  ", x["text"]); print("   W " + " ".join(f"{w}@{s:.2f}-{e:.2f}" for w, s, e in x["words"]), flush=True)
json.dump(res, open(sys.argv[4], "w"), ensure_ascii=False)
print("TIME", time.time()-t0)
