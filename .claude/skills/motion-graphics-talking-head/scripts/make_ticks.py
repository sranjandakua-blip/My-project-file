# Soft phone-keyboard "tock" (4 variants) -> ../sfx/tick0..3.wav. Rounded, ~1.5 kHz centroid.
# (A brighter 2.5-9 kHz click was rejected as "irritating to the ear".)
import numpy as np,subprocess
SR=48000
def bp(x,lo,hi):
    X=np.fft.rfft(x);f=np.fft.rfftfreq(len(x),1/SR)
    m=np.clip((f-lo*0.6)/(lo*0.4),0,1)*np.clip((hi*1.5-f)/(hi*0.5),0,1)
    return np.fft.irfft(X*m,len(x))
for v in range(4):
    rng=np.random.default_rng(40+v); p=1+(v-1.5)*0.035
    n=int(0.04*SR); t=np.arange(n)/SR; att=np.minimum(1,t/0.0012)
    noise=bp(rng.standard_normal(n),900*p,3200*p)*np.exp(-t/0.0016)*att
    body=np.sin(2*np.pi*(620*p)*t)*np.exp(-t/0.0035)*att
    x=noise/np.abs(noise).max()*0.55+body*0.75; x=np.convolve(x,np.ones(5)/5,'same'); x=x/np.abs(x).max()*0.9
    np.stack([x,x],1).astype(np.float32).tofile('tk.f32')
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar','48000','-ac','2','-i','tk.f32','-c:a','pcm_s16le',f'../sfx/tick{v}.wav'],check=True)
print('ticks written')
