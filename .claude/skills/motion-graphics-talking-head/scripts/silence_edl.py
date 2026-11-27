# Build a tight EDL from chosen takes: keeps speech, removes every pause > ~0.13 s.
# Usage: python3 silence_edl.py takes.json   -> edl.json  [[take, src_start, src_end], ...]
# takes.json: [["hook",71.6,77.4],["n1",81.3,83.6],...]  (rough windows around the best take of each line,
# found with transcribe.py). Optional 4th element = exact start override (e.g. to drop a filler word like "or").
import numpy as np, json, sys
a=np.fromfile('../work/a16.wav',dtype=np.int16)[22:].astype(np.float32)/32768
hop=160;n=len(a)//hop
db=20*np.log10(np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(1))+1e-12)
TH=-47          # speech threshold (dBFS, 10 ms RMS). Check noise floor first: room tone was ~-70..-60
GAP=13          # merge gaps <= 0.13 s
PRE,POST=0.03,0.06
takes=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'takes.json'))
edl=[]
for tk in takes:
    name,s,e=tk[:3]
    i0,i1=int(s*100),int(e*100)
    idx=np.where(db[i0:i1]>TH)[0]
    regs=[[idx[0],idx[0]]]
    for k in idx[1:]:
        if k-regs[-1][1]<=GAP: regs[-1][1]=k
        else: regs.append([k,k])
    regs=[r for r in regs if r[1]-r[0]>=3]
    first=True
    for r in regs:
        rs=(i0+r[0])/100-PRE; re=(i0+r[1])/100+POST
        if first and len(tk)>3: rs=tk[3]
        first=False
        if edl and edl[-1][0]==name and rs-edl[-1][2]<0.05: edl[-1][2]=round(re,3)
        else: edl.append([name,round(rs,3),round(re,3)])
tot=sum(x[2]-x[1] for x in edl)
for x in edl: print(x,round(x[2]-x[1],2))
print('total',round(tot,2),'-> at 1.08x',round(tot/1.08,2))
json.dump(edl,open('edl.json','w'))
