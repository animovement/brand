"""Wave bands: the abstract counterpart to the hex logo's stacked ridges.

Band 0 is full-bleed so the leading edge is always covered; bands 1..n-1 have a
wavy leading edge and fill away from it, so each keeps real area. Two summed
sines at different frequencies avoid the mechanical look of a single sine.
"""
import numpy as np
import fitcurve as fc
from lab import vivid

def gradients(key, hues, L0, L1, horiz=False, n=5):
    out=[]
    x2,y2 = (1,0) if horiz else (0,1)
    for i,h in enumerate(hues):
        st="".join(f'<stop offset="{j/(n-1):.3f}" stop-color="{vivid(L0+(L1-L0)*j/(n-1),h)}"/>'
                   for j in range(n))
        out.append(f'<linearGradient id="{key}{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">{st}</linearGradient>')
    return "".join(out)

def _wave(pts,tol=0.35):
    return fc.to_d(fc.fit_curve(np.asarray(pts,float),tol=tol),closed=False,prec=2)

def bands_h(W,H,key,n=8,amp=0.055,freq=1.30,phase=0.7,bleed=0.18,span=0.955,start=0.045,samples=220,tol=0.35):
    """Stacked ridges: wavy top edges, filling downward."""
    out=[f'<rect x="{-bleed*W:.0f}" y="{-0.35*H:.0f}" width="{W*(1+2*bleed):.0f}" '
         f'height="{H*1.7:.0f}" fill="url(#{key}0)"/>']
    A=amp*H; xs=np.linspace(-bleed*W, W*(1+bleed), samples)
    for i in range(1,n):
        y0=H*span*(i/n)+H*start
        ys=y0+A*np.sin(2*np.pi*freq*xs/W+phase*i)+A*0.45*np.sin(2*np.pi*freq*2.3*xs/W+1.9*i)
        out.append(f'<path d="{_wave(np.c_[xs,ys],tol)} L{xs[-1]:.0f} {H*1.4:.0f} '
                   f'L{xs[0]:.0f} {H*1.4:.0f} Z" fill="url(#{key}{i})"/>')
    return "".join(out)

def bands_v(W,H,key,n=8,amp=0.055,freq=1.05,phase=0.7,bleed=0.18,amp_px=None,span=0.955,start=0.045,samples=220,tol=0.35):
    """Same rotated: wavy left edges, filling rightward. amp_px overrides amp
    with an absolute pixel amplitude (used for the slim banner)."""
    out=[f'<rect x="{-0.35*W:.0f}" y="{-bleed*H:.0f}" width="{W*1.7:.0f}" '
         f'height="{H*(1+2*bleed):.0f}" fill="url(#{key}0)"/>']
    A = amp_px if amp_px is not None else amp*W
    ys=np.linspace(-bleed*H, H*(1+bleed), samples)
    for i in range(1,n):
        x0=W*span*(i/n)+W*start
        xs=x0+A*np.sin(2*np.pi*freq*ys/H+phase*i)+A*0.45*np.sin(2*np.pi*freq*2.3*ys/H+1.9*i)
        out.append(f'<path d="{_wave(np.c_[xs,ys],tol)} L{W*1.4:.0f} {ys[-1]:.0f} '
                   f'L{W*1.4:.0f} {ys[0]:.0f} Z" fill="url(#{key}{i})"/>')
    return "".join(out)

def gaussian_haze(gid, peak=0.90, sigma=0.34, stops=15, vertical=True):
    """Smooth white veil centred on the middle. A linear ramp clamps at the
    edges and stops responding once pad+feather reaches them; a gaussian keeps
    feathering all the way out."""
    ss=""
    for i in range(stops):
        o=i/(stops-1)
        ss+=(f'<stop offset="{o:.4f}" stop-color="#FFFFFF" '
             f'stop-opacity="{peak*float(np.exp(-((o-0.5)/sigma)**2)):.4f}"/>')
    x2,y2 = (0,1) if vertical else (1,0)
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{ss}</linearGradient>'

def namespace(svg, prefix):
    """Prefix every id and reference so several marks can share one document.
    Without this, inlining N svgs makes every url(#g) resolve to the first."""
    import re
    for i in sorted(set(re.findall(r'id="([^"]+)"',svg)), key=len, reverse=True):
        svg=(svg.replace(f'id="{i}"',f'id="{prefix}-{i}"')
                .replace(f'url(#{i})',f'url(#{prefix}-{i})')
                .replace(f'href="#{i}"',f'href="#{prefix}-{i}"'))
    return svg
