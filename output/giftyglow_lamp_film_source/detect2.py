import numpy as np, json, sys
from PIL import Image, ImageOps, ImageFilter
Image.MAX_IMAGE_PIXELS=None
ns='05519,05553,05567,05575,05588,05595,05613,05520,05521,05566'.split(',')
out={}
for n in ns:
    im=Image.open(f'med/DSC{n}.jpg').convert('RGB'); w,h=im.size
    a=np.asarray(im.filter(ImageFilter.GaussianBlur(2)),np.float32); lum=a.mean(2)
    if n in ('05521',): lum=a[...,1]*0.3+a[...,0]*0.7   # green cast: use red-weighted
    hot=lum>185; rows=hot.sum(1)
    lo=int(h*0.45); cand=np.arange(lo,h)[rows[lo:]>w*0.04]
    if len(cand)==0:
        hot=lum>140; rows=hot.sum(1); cand=np.arange(lo,h)[rows[lo:]>w*0.02]
        print(n,'fallback',len(cand))
    ybase=int(cand[np.argmax(rows[cand])])
    m=lum[:ybase]>80; r=m.sum(1); top=int(np.where(r>=4)[0][0])
    reg=lum[top:ybase]; wts=np.clip(reg-120,0,None); xs=np.arange(w)
    cx=float((wts.sum(0)*xs).sum()/wts.sum())
    out[n]=dict(top=top*2,base=ybase*2,cx=cx*2)   # in 'hi' (x2) coords
    raw=ImageOps.exif_transpose(Image.open(f'raw/DSC{n}.JPG')).convert('RGB')
    raw.resize((w*2,h*2),Image.LANCZOS).save(f'hi/{n}.png')
json.dump(out,open('align.json','w'),indent=1); print(out)
