# Apple emoji PNGs (client wants Apple, NOT Android/Noto) -> ../apple/sheet_<code>.png (180px) + meta.json.
# Usage: python3 apple_emoji.py 1f914 1f9d0 2764_fe0f_200d_1f525 ...   (or no args: codes from timeline.json meta)
# Sources: iamcal/emoji-data img-apple-160 via jsDelivr (sometimes 403s), fallback Emojipedia CDN (needs name slug).
import sys,os,json,subprocess
from PIL import Image
os.makedirs('../apple',exist_ok=True)
codes=sys.argv[1:] or list(json.load(open('timeline.json'))['meta'].keys())
meta=json.load(open('../apple/meta.json')) if os.path.exists('../apple/meta.json') else {}
for c in codes:
    f=c.replace('_','-'); out=f'../apple/raw_{c}.png'
    for attempt in range(3):
        subprocess.run(['curl','-s','-o',out,f'https://cdn.jsdelivr.net/gh/iamcal/emoji-data@master/img-apple-160/{f}.png'])
        try: im=Image.open(out).convert('RGBA'); break
        except Exception: im=None
    if im is None: print('FAILED',c,'- fetch from https://em-content.zobj.net/source/apple/391/<name>_<code>.png'); continue
    im.resize((180,180),Image.LANCZOS).save(f'../apple/sheet_{c}.png'); meta[c]=1
json.dump(meta,open('../apple/meta.json','w')); print(len(meta),'emojis ready')
