# Median face centre per take (Haar cascade; needs opencv-python-headless<5). Writes faces.json {take:[fx,fy,w]} (0..1).
import cv2,json,subprocess,numpy as np
SRC='../dl/raw.mp4'
w,h=[int(v) for v in subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',SRC],capture_output=True,text=True).stdout.replace('\n',',').split(',') if v.strip().isdigit()][:2]
# rotation-aware (phone HEVC often stores 1280x720 + rotation=90; ffmpeg auto-rotates on decode)
rot=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream_side_data=rotation:stream_tags=rotate','-of','csv=p=0',SRC],capture_output=True,text=True).stdout
if any(abs(int(v))%180==90 for v in rot.replace('\n',',').split(',') if v.strip().lstrip('-').isdigit()): w,h=h,w
casc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
out={}
for n,s,t in json.load(open('edl.json')):
    if n in out: continue
    cs=[]
    for k in np.linspace(s+0.2,t-0.2,6):
        raw=subprocess.run(['ffmpeg','-v','error','-ss',str(k),'-i',SRC,'-frames:v','1','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
        img=np.frombuffer(raw,np.uint8).reshape(h,w)
        f=casc.detectMultiScale(img,1.1,6,minSize=(70,70))
        if len(f): x,y,fw,fh=max(f,key=lambda r:r[2]*r[3]); cs.append((x+fw/2,y+fh/2,fw))
    c=np.median(np.array(cs),0) if cs else np.array([w/2,h*0.5,w*0.25])
    out[n]=[float(c[0])/w,float(c[1])/h,float(c[2])/w]; print(n,len(cs),[round(v,3) for v in out[n]])
json.dump({'size':[w,h],'faces':out},open('faces.json','w'))
