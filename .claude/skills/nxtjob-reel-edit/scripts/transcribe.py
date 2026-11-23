"""Usage: python3 -I transcribe.py <media> <model: small|medium> [lang] [words]
Prints segments (and word timestamps as `   W word@start-end ...` lines when 4th arg given)."""
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
# decode with ffmpeg ourselves: the PyAV in some sandboxes breaks faster-whisper's decoder
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
m = WhisperModel(sys.argv[2], device="cpu", compute_type="int8")
kw = dict(word_timestamps=True)
if len(sys.argv) > 3: kw["language"] = sys.argv[3]
segs, info = m.transcribe(a, **kw)
print("LANG", info.language, info.language_probability, flush=True)
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
    if len(sys.argv) > 4:
        print("   W " + " ".join(f"{w.word.strip()}@{w.start:.2f}-{w.end:.2f}" for w in s.words), flush=True)
