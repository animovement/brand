import subprocess, os
import numpy as np
from PIL import Image
PAIRS=[("out/marks/icon-wave-v-a.svg","/mnt/user-data/outputs/vshapes/icon-wave-v-a.svg",256),
       ("out/marks/square-wave-v-ani.svg","/mnt/user-data/outputs/vshapes/square-wave-v-ani.svg",512),
       ("out/og/og-v-haze50.svg","/mnt/user-data/outputs/og/og-v-haze50.svg",1200),
       ("out/banner/banner-s34.svg","/mnt/user-data/outputs/org-banner-soft/banner-s34.svg",1200)]
def render(path,w,out):
    s=open(path).read().split('?>',1)[-1]
    open('/tmp/c.html','w').write('<html><body style="margin:0;background:#808080">'+s+'</body></html>')
    subprocess.run(['timeout','120','wkhtmltoimage','--width',str(w),'--quality','100','/tmp/c.html',out],
                   capture_output=True)
    return np.asarray(Image.open(out).convert('RGB')).astype(int)
for a,b,w in PAIRS:
    if not os.path.exists(b): print(f"{os.path.basename(a):26s} shipped file missing"); continue
    x=render(a,w,'/tmp/r1.png'); y=render(b,w,'/tmp/r2.png')
    n=min(x.shape[0],y.shape[0]); m=min(x.shape[1],y.shape[1])
    d=np.abs(x[:n,:m]-y[:n,:m])
    print(f"{os.path.basename(a):26s} max diff {d.max():3d}   mean {d.mean():.4f}")
