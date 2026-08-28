"""Regenerate the package hex logos from the traced base artwork.

Input : animovement-fixed.svg  (the corrected, regular-hexagon landscape)
Output: one hex per package, recoloured, with its own wordmark and keyline.
"""
import sys, re, os
import numpy as np
from .lab import parse, rgb2lab, lab2lch, vivid
from .palette import PACKAGES, HUE, BASE, ramp_fn
from .typeset import POPPINS_LIGHT, em_for, word
from .geometry import W, H, keyline_border
from .waves import namespace

BASE_SVG = sys.argv[1] if len(sys.argv)>1 else "animovement-fixed.svg"
OUTDIR   = sys.argv[2] if len(sys.argv)>2 else "out/packages"
BASELINE = 560.0
EM       = em_for(POPPINS_LIGHT,"animovement",950.0)   # constant across the family

def border_gradient(gid, h0, n=6, L=(46.0,70.0), hue_drift=16.0):
    st=""
    for i in range(n):
        t=i/(n-1)
        st+=(f'<stop offset="{t:.3f}" stop-color="'
             f'{vivid(L[0]+(L[1]-L[0])*t, (h0-hue_drift/2+hue_drift*t)%360)}"/>')
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="0" y1="0" x2="{W:.0f}" y2="{H:.0f}">{st}</linearGradient>')

def main():
    src=open(BASE_SVG).read()
    cols=sorted({m.group(0).lower() for m in re.finditer(r'#[0-9a-fA-F]{6}',src)})
    Ls={c: float(lab2lch(rgb2lab(parse(c)))[0]) for c in cols}
    os.makedirs(OUTDIR,exist_ok=True)
    for pkg,colour in PACKAGES:
        h0=HUE[colour.lower()]
        f=ramp_fn(BASE[colour.lower()])
        mp={c:f(Ls[c]) for c in cols}
        svg=re.sub(r'#[0-9a-fA-F]{6}', lambda m: mp[m.group(0).lower()], src)
        svg=namespace(svg,pkg)
        gid=f'{pkg}-keyline'
        wm=(f'<path id="{pkg}-wordmark" inkscape:label="wordmark" '
            f'fill="{vivid(34,h0,0.80)}" fill-rule="evenodd" '
            f'd="{word(POPPINS_LIGHT,pkg,EM,W/2,BASELINE)["d"]}"/>')
        svg=re.sub(r'<path[^>]*id="'+pkg+r'-hexagon"[^>]*/>', wm+keyline_border(pkg,gid), svg)
        svg=svg.replace('</defs>', border_gradient(gid,h0)+'</defs>')
        open(f"{OUTDIR}/{pkg}.svg","w").write(svg)
        print(f"  {pkg:11s} {colour:9s} h={h0:6.1f}  wordmark {vivid(34,h0,0.80)}")

if __name__=='__main__': main()
