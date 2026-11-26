import cv2, sys, json, numpy as np
cap = cv2.VideoCapture(sys.argv[1]); fps = cap.get(cv2.CAP_PROP_FPS)
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
out = []; i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if i % 5 == 0:
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        fs = casc.detectMultiScale(g, 1.1, 5, minSize=(60, 60))
        if len(fs):
            x, y, w, h = max(fs, key=lambda r: r[2]*r[3])
            out.append([round(i/fps, 3), int(x+w/2), int(y+h/2), int(w)])
        else:
            out.append([round(i/fps, 3), None, None, None])
    i += 1
json.dump(out, open(sys.argv[2], 'w'))
v = [o for o in out if o[1] is not None]
print(len(out), len(v), 'cx range', min(o[1] for o in v), max(o[1] for o in v), 'cy', min(o[2] for o in v), max(o[2] for o in v), 'w', np.median([o[3] for o in v]))
