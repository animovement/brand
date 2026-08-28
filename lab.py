"""sRGB <-> CIELAB <-> LCh conversions, with strict gamut testing.

The strict test matters: a naive round-trip through lab2rgb clips silently, so
every colour appears to be in gamut and chroma ceilings come back meaningless.
"""
import numpy as np

M  = np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
Mi = np.linalg.inv(M)
WP = np.array([0.95047,1.0,1.08883])

def s2l(c):
    c = np.asarray(c,float)/255.0
    return np.where(c<=0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def l2s(c):
    c = np.asarray(c,float)
    out = np.where(c<=0.0031308, c*12.92, 1.055*np.abs(c)**(1/2.4)-0.055)
    return np.clip(out,0,1)*255
def _f(t):  d=6/29; return np.where(t>d**3, np.cbrt(t), t/(3*d*d)+4/29)
def _fi(t): d=6/29; return np.where(t>d, t**3, 3*d*d*(t-4/29))

def rgb2lab(rgb):
    x = s2l(rgb)@M.T/WP; F=_f(x)
    return np.stack([116*F[...,1]-16, 500*(F[...,0]-F[...,1]), 200*(F[...,1]-F[...,2])],-1)
def lab2rgb(lab):
    L,A,B = lab[...,0],lab[...,1],lab[...,2]
    fy=(L+16)/116; fx=fy+A/500; fz=fy-B/200
    return l2s((np.stack([_fi(fx),_fi(fy),_fi(fz)],-1)*WP)@Mi.T)
def lab2lch(lab):
    L,A,B = lab[...,0],lab[...,1],lab[...,2]
    return np.stack([L, np.hypot(A,B), np.degrees(np.arctan2(B,A))%360],-1)
def lch2lab(lch):
    L,C,H = lch[...,0],lch[...,1],lch[...,2]; h=np.radians(H)
    return np.stack([L, C*np.cos(h), C*np.sin(h)],-1)

def parse(h):
    h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],float)
def hx(rgb):
    r,g,b = [int(round(v)) for v in np.clip(rgb,0,255)]
    return f"#{r:02X}{g:02X}{b:02X}"

def ingamut_strict(lab, tol=1.0):
    """True only if lab converts to sRGB without clipping."""
    L,A,B = lab[...,0],lab[...,1],lab[...,2]
    fy=(L+16)/116; fx=fy+A/500; fz=fy-B/200
    lin=(np.stack([_fi(fx),_fi(fy),_fi(fz)],-1)*WP)@Mi.T
    srgb=np.where(lin<=0.0031308, lin*12.92, 1.055*np.abs(lin)**(1/2.4)-0.055)*255
    return bool(np.all(np.isfinite(srgb)) and srgb.min()>=-tol and srgb.max()<=255+tol)

def max_chroma(L,h,lo=0.0,hi=160.0):
    """Highest in-gamut chroma for a hue at a given lightness (bisection)."""
    for _ in range(40):
        m=(lo+hi)/2
        if ingamut_strict(lch2lab(np.array([L,m,h]))): lo=m
        else: hi=m
    return lo

def vivid(L,h,k=0.92):
    """Colour at lightness L and hue h, chroma at k x the gamut ceiling."""
    C=max_chroma(L,h)*k
    for f in np.linspace(1,0,26):
        lab=lch2lab(np.array([L,C*f,h]))
        if ingamut_strict(lab): return hx(lab2rgb(lab))
    return hx(lab2rgb(lch2lab(np.array([L,0,h]))))

def contrast(a,b):
    """WCAG contrast ratio between two hex colours."""
    def rl(c):
        c=s2l(parse(c) if isinstance(c,str) else c)
        return float(np.asarray(c)@[0.2126,0.7152,0.0722])
    x,y = rl(a),rl(b)
    return (max(x,y)+0.05)/(min(x,y)+0.05)
