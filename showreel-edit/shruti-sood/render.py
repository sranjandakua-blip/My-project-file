import json, subprocess, sys, os
S='/tmp/claude-0/-home-user-My-project-file/b8f68f35-e422-5be6-8710-30ffbc413c24/scratchpad'
FPS=30000/1001
p=json.load(open(f'{S}/edit/plan.json'))
os.makedirs(f'{S}/edit/shots',exist_ok=True)
only=set(sys.argv[1:])
def fr(t): return round(t*FPS)
for i,s in enumerate(p['shots']):
    if only and str(i) not in only: continue
    n=fr(s['t1'])-fr(s['t0']); D=n/FPS
    fx=s['fx'].split(',') if s['fx'] else []
    vf=['scale=1296:2304:flags=bicubic']
    if 'zoomin' in fx:   z=f"(1.0+0.10*t/{D:.3f})"
    elif 'zoomout' in fx:z=f"(1.10-0.10*t/{D:.3f})"
    elif 'punch' in fx:  z="1.15"
    else:                z="1.0"
    vf.append(f"scale=w='2*trunc(1080*{z}/2)':h='2*trunc(1920*{z}/2)':eval=frame:flags=lanczos")
    vf.append("crop=1080:1920:(iw-1080)/2:(ih-1920)*0.35")
    vf.append("eq=contrast=1.07:saturation=1.12:gamma=0.98")
    if 'bw' in fx: vf.append("hue=s=0,eq=contrast=1.15")
    vf.append("vignette=angle=PI/5")
    vf.append("noise=alls=5:allf=t")
    pre=list(vf); vf=[]
    png=None
    if 'title' in fx: png=(S+'/edit/title.png',f"fade=t=in:st=0.15:d=0.4:alpha=1,fade=t=out:st={D-0.35:.3f}:d=0.35:alpha=1")
    if 'endcard' in fx: png=(S+'/edit/endcard.png',"fade=t=in:st=0.25:d=0.4:alpha=1")
    if 'flash' in fx: vf.append("fade=t=in:st=0:d=0.15:color=white")
    if 'outro' in fx: vf.append(f"fade=t=out:st={D-1.3:.3f}:d=1.3")
    vf.append("format=yuv420p")
    inp=['-ss',f"{s['src']:.3f}",'-i',f"{S}/raw/{s['clip']}.MP4"]
    if png:
        inp+=['-loop','1','-t',f'{D+0.2:.3f}','-i',png[0]]
        filt=['-filter_complex',f"[0:v]{','.join(pre)}[v];[1:v]format=rgba,{png[1]}[t];[v][t]overlay=0:0:shortest=0,{','.join(vf)}[o]",'-map','[o]']
    else:
        filt=['-vf',','.join(pre+vf)]
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']+inp+['-an']+filt+['-r','30000/1001','-frames:v',str(n),
         '-c:v','libx264','-preset','medium','-crf','15','-g','30','-bf','0',f"{S}/edit/shots/{i:02d}.mp4"]
    r=subprocess.run(cmd,capture_output=True,text=True)
    print(i,s['clip'],n,'frames', 'ERR '+r.stderr[-300:] if r.returncode else 'ok',flush=True)
