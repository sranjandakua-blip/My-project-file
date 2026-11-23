"""Usage: python3 -I frames_to_video.py <frames dir with ts.json> <out.mp4>
Retimes the record_agent.js screenshots to real speed at 30 fps (1074x2000)."""
import json, os, subprocess, sys
d, out = sys.argv[1], sys.argv[2]
ts = json.load(open(os.path.join(d, 'ts.json')))
lst = os.path.join(d, 'list.txt')
with open(lst, 'w') as f:
    for i in range(len(ts)):
        dur = (ts[i + 1] - ts[i]) if i + 1 < len(ts) else 0.05
        f.write(f"file 'f{i:05d}.jpg'\nduration {dur:.4f}\n")
    f.write(f"file 'f{len(ts) - 1:05d}.jpg'\n")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                '-vf', 'fps=30,crop=1074:2000:0:0,format=yuv420p', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', out],
               check=True)
print('wrote', out)
