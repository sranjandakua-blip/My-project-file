# Writes grade.cube (33^3 LUT) + vig.npy. Client-approved look: neutral-clean, slightly brighter than raw,
# a hint of warmth only (an earlier warm/teal-orange matte grade was rejected as "yellowish and darker").
import numpy as np
N=33; g=np.linspace(0,1,N)
b,gg,r=np.meshgrid(g,g,g,indexing='ij'); x=np.stack([r,gg,b],-1)
x=1-(1-x)**1.18                                   # exposure lift with soft shoulder
x[...,0]*=1.012; x[...,2]*=0.992; x=np.clip(x,0,1) # tiny warmth
s=x*x*(3-2*x); x=x*0.78+s*0.22                     # gentle S-curve
L=(0.2126*x[...,0]+0.7152*x[...,1]+0.0722*x[...,2])[...,None]
x=x+((1-L)**2.5)*np.array([-0.010,0,0.012])+(L**2.2)*np.array([0.012,-0.004,0.002])
L=(0.2126*x[...,0]+0.7152*x[...,1]+0.0722*x[...,2])[...,None]
x=L+(x-L)*1.08; x=np.clip(0.008+x*(0.995-0.008),0,1)
with open('grade.cube','w') as f:
    f.write('LUT_3D_SIZE 33\n')
    for v in x.reshape(-1,3): f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
W,H=1080,1920; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
rr=np.sqrt(((xx-W/2)/(W*0.62))**2+((yy-H*0.46)/(H*0.60))**2)
t=np.clip((rr-0.65)/0.65,0,1); t=t*t*(3-2*t)
np.save('vig.npy',(1-0.13*t).astype(np.float32))   # subtle: max 13% darkening at far corners
print('grade.cube + vig.npy written')
