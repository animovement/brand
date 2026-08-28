"""Schneider's algorithm: least-squares cubic Bezier fitting to a polyline.
Used to trace the original raster logo and to render smooth wave bands."""
import numpy as np

def q(c,t):
    mt=1-t
    return ((mt**3)[:,None]*c[0] + (3*mt**2*t)[:,None]*c[1]
          + (3*mt*t**2)[:,None]*c[2] + (t**3)[:,None]*c[3])
def qprime(c,t):
    mt=1-t
    return ((3*mt**2)[:,None]*(c[1]-c[0]) + (6*mt*t)[:,None]*(c[2]-c[1])
          + (3*t**2)[:,None]*(c[3]-c[2]))
def qpp(c,t):
    mt=1-t
    return (6*mt)[:,None]*(c[2]-2*c[1]+c[0]) + (6*t)[:,None]*(c[3]-2*c[2]+c[1])
def _n(v):
    m=np.linalg.norm(v); return v/m if m>1e-12 else v
def _chord(p):
    d=np.r_[0.0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    return d/d[-1] if d[-1]>0 else np.linspace(0,1,len(p))

def _gen(p,u,t1,t2):
    A=np.zeros((len(p),2,2)); mt=1-u
    A[:,0]=t1*(3*mt**2*u)[:,None]; A[:,1]=t2*(3*mt*u**2)[:,None]
    p0,p3=p[0],p[-1]
    tmp=p-q(np.array([p0,p0,p3,p3]),u)
    C=np.zeros((2,2)); X=np.zeros(2)
    C[0,0]=(A[:,0]*A[:,0]).sum(); C[0,1]=C[1,0]=(A[:,0]*A[:,1]).sum()
    C[1,1]=(A[:,1]*A[:,1]).sum()
    X[0]=(A[:,0]*tmp).sum(); X[1]=(A[:,1]*tmp).sum()
    det=C[0,0]*C[1,1]-C[0,1]*C[1,0]; seg=np.linalg.norm(p3-p0)
    if abs(det)<1e-12: a1=a2=seg/3
    else:
        a1=(X[0]*C[1,1]-X[1]*C[0,1])/det; a2=(C[0,0]*X[1]-C[1,0]*X[0])/det
        if a1<1e-6 or a2<1e-6: a1=a2=seg/3
    return np.array([p0,p0+t1*a1,p3+t2*a2,p3])

def _reparam(c,p,u):
    d=q(c,u)-p
    num=(d*qprime(c,u)).sum(1)
    den=(qprime(c,u)**2).sum(1)+(d*qpp(c,u)).sum(1)
    return np.clip(u-np.where(np.abs(den)<1e-12,0,num/np.where(den==0,1,den)),0,1)

def _err(c,p,u):
    d=np.linalg.norm(q(c,u)-p,axis=1); i=int(np.argmax(d)); return d[i]**2,i

def _fit(p,t1,t2,tol,out):
    if len(p)==2:
        d=np.linalg.norm(p[1]-p[0])/3
        out.append(np.array([p[0],p[0]+t1*d,p[1]+t2*d,p[1]])); return
    u=_chord(p); c=_gen(p,u,t1,t2); e,s=_err(c,p,u)
    if e<tol*tol: out.append(c); return
    if e<(tol*tol)*16:
        for _ in range(24):
            u=_reparam(c,p,u); c=_gen(p,u,t1,t2); e,s=_err(c,p,u)
            if e<tol*tol: out.append(c); return
    s=max(1,min(s,len(p)-2))
    v=_n(_n(p[s-1]-p[s])-_n(p[s+1]-p[s]))
    if np.linalg.norm(v)<1e-9: v=_n(p[s-1]-p[s+1])
    _fit(p[:s+1],t1,v,tol,out); _fit(p[s:],-v,t2,tol,out)

def fit_curve(pts,tol=1.2,closed=False):
    p=np.asarray(pts,float)
    p=p[np.r_[True,(np.linalg.norm(np.diff(p,axis=0),axis=1)>1e-9)]]
    if len(p)<2: return []
    if closed and np.linalg.norm(p[0]-p[-1])>1e-9: p=np.vstack([p,p[0]])
    if closed: t1=_n(p[1]-p[-2]); t2=-t1
    else:      t1=_n(p[1]-p[0]);  t2=_n(p[-2]-p[-1])
    out=[]; _fit(p,t1,t2,tol,out); return out

def to_d(segs,closed=False,prec=2):
    if not segs: return ""
    f=lambda v: f"{v:.{prec}f}".rstrip('0').rstrip('.') or '0'
    d=[f"M{f(segs[0][0][0])} {f(segs[0][0][1])}"]
    for s in segs:
        d.append(f"C{f(s[1][0])} {f(s[1][1])} {f(s[2][0])} {f(s[2][1])} {f(s[3][0])} {f(s[3][1])}")
    if closed: d.append("Z")
    return "".join(d)
