import numpy as np, json
S='/tmp/claude-0/-home-user-My-project-file/b8f68f35-e422-5be6-8710-30ffbc413c24/scratchpad'
bt=np.load(f'{S}/b13_beats.npy')
i0=int(np.argmin(abs(bt-78.88)))
B=list(bt[i0:]-bt[i0])   # timeline beat times
A0=float(bt[i0])         # audio in-point in B0013
END=123.62-A0            # timeline end
def T(b): return B[b] if b<len(B) else END
SYNC='SYNC'
# (beat_start, beat_end, clip, in_point or SYNC, fx)
shots=[
 (0,1,'B0066',1.0,'bw'),
 (1,2,'B0030',6.6,'punch'),
 (2,3,'B0054',0.7,'bw'),
 (3,4,'B0068',1.9,'punch'),
 (4,12,'B0055',3.6,'flash,zoomin,title'),
 (12,16,'B0013',SYNC,'punch'),
 (16,18,'B0051',3.1,''),
 (18,20,'B0054',3.6,'punch'),
 (20,28,'B0073',4.6,'flash,zoomin'),
 (28,32,'B0085',8.3,''),
 (32,36,'B0059',1.4,'zoomout'),
 (36,44,'B0013',SYNC,'flash,zoomin'),
 (44,52,'B0013',SYNC,'punch,zoomin'),
 (52,54,'B0056',0.2,''),
 (54,56,'B0030',2.3,'bw'),
 (56,60,'B0061',42.0,'zoomin'),
 (60,64,'B0085',10.6,'punch'),
 (64,68,'B0060',9.0,''),
 (68,72,'B0068',3.1,'zoomout'),
 (72,80,'B0052',47.5,'flash,zoomin'),
 (80,84,'B0013',SYNC,'punch'),
 (84,86,'B0054',6.2,'bw'),
 (86,88,'B0051',9.2,'punch'),
 (88,96,'B0091',3.6,'zoomin'),
 (96,97,'B0057',2.5,'flash'),
 (97,98,'B0073',2.6,'punch'),
 (98,99,'B0081',37.0,'bw'),
 (99,100,'B0066',2.6,'punch'),
 (100,999,'B0013',SYNC,'flash,zoomin,outro,endcard'),
]
out=[]
for b0,b1,c,inp,fx in shots:
    t0,t1=T(b0),T(b1)
    src = A0+t0 if inp==SYNC else inp
    out.append(dict(t0=round(t0,3),t1=round(t1,3),clip=c,src=round(src,3),fx=fx))
json.dump(dict(audio_in=A0,end=END,beats=[round(x,3) for x in B],shots=out),open(f'{S}/edit/plan.json','w'),indent=1)
print('audio_in',A0,'end',END,'nbeats',len(B))
for s in out: print(s)
