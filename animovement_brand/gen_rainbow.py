"""Regenerate animovement.svg - the metapackage hex.

The landscape keeps the original logo's structure but sweeps the full palette
by depth: magenta at the far ridges through to navy in the foreground. Sky and
river stay a shared near-white, which is what keeps the wordmark legible (6:1)
where the abstract wave versions only managed 1.9:1.

Two chroma rules differ from the abstract marks and both matter:
  * lightness is remapped 41.5-89.6 -> 45-80 first. Above L* 85 no hue holds
    saturation, so the original's pale back layers could not go vivid at all.
  * chroma is capped at C* 62. Green's gamut ceiling is more than twice teal's,
    so a plain fraction-of-ceiling rule made one band shout (C* 77 against
    neighbours at 29-48). In an abstract bar that is invisible; in a landscape
    it reads as a lime stripe.
"""
import sys, os, re
import xml.etree.ElementTree as ET
import numpy as np
from .lab import (parse, rgb2lab, lab2lch, lab2rgb, lch2lab, hx,
                 ingamut_strict, max_chroma)
from .palette import HUES, BASE, ramp_fn
from .typeset import POPPINS_LIGHT, em_for, word
from .geometry import W, H, keyline_border
from .waves import namespace

SVG='http://www.w3.org/2000/svg'; XL='http://www.w3.org/1999/xlink'
for p,u in [('svg',SVG),('inkscape','http://www.inkscape.org/namespaces/inkscape'),
            ('sodipodi','http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'),('xlink',XL)]:
    ET.register_namespace(p,u)
ET.register_namespace('',SVG)

PKG      = "animovement"
BASELINE = 560.0
CAP      = 62.0                       # soft chroma ceiling
L_SRC    = (41.5, 89.6)               # original landscape lightness range
L_DST    = (45.0, 80.0)               # remapped into the vivid-reachable zone
K_RANGE  = (0.78, 0.92)               # chroma, misty at the back -> rich in front
SKY      = dict(L=97.5, k=0.045)
WORD     = dict(L=44.0, k=0.92, x1=160, x2=1040)
LINE     = dict(L=58.0, k=0.92)   # uncapped: the border reads brighter than the landscape

# landscape paths, back to front; sky and river share one flat colour
LAND = ['path80','path95','path130','path96','path98','path101','path104',
        'path106','path109','path110','path111','path112','path113','path114']
FLAT = {'path80','path104'}

def remap(L):
    return L_DST[0] + (L-L_SRC[0])/(L_SRC[1]-L_SRC[0])*(L_DST[1]-L_DST[0])

def tint(L, h, k, keepL=False, cap=CAP):
    if not keepL: L = remap(L)
    C = min(max_chroma(L,h)*k, cap)
    for f in np.linspace(1,0,26):
        lab = lch2lab(np.array([L, C*f, h]))
        if ingamut_strict(lab): return hx(lab2rgb(lab))
    return hx(lab2rgb(lch2lab(np.array([L,0,h]))))

def recolour(hexcol, h, k):
    return tint(float(lab2lch(rgb2lab(parse(hexcol)))[0]), h, k)

def rainbow_gradient(gid, L, k, x1, y1, x2, y2, cap=CAP):
    # the wordmark gradient is capped like the landscape; the border line is not,
    # so it stays brighter than the artwork it frames
    st = "".join(f'<stop offset="{i/(len(HUES)-1):.3f}" '
                 f'stop-color="{tint(L,h,k,keepL=True,cap=cap)}"/>' for i,h in enumerate(HUES))
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')

def main(base_svg, outdir):
    # Historical quirk, kept because it is what the shipped file was built from:
    # the rainbow was applied on top of the deepteal-ramped package hex, not on
    # the raw base artwork. The extra 8-bit round trip shifts a few lightness
    # values by a fraction, which shows as +/-1 in a channel. Going straight
    # from base_svg is defensible but will not match byte for byte.
    raw = open(base_svg).read()
    cols = sorted({m.group(0).lower() for m in re.finditer(r'#[0-9a-fA-F]{6}', raw)})
    dt = ramp_fn(BASE['deepteal'])
    Ls = {c: float(lab2lch(rgb2lab(parse(c)))[0]) for c in cols}
    mp = {c: dt(Ls[c]) for c in cols}
    raw = re.sub(r'#[0-9a-fA-F]{6}', lambda m: mp[m.group(0).lower()], raw)
    src = namespace(raw, PKG)
    em  = em_for(POPPINS_LIGHT, "animovement", 950.0)
    wm  = (f'<path id="{PKG}-wordmark" inkscape:label="wordmark" '
           f'fill="url(#rb-word)" fill-rule="evenodd" '
           f'd="{word(POPPINS_LIGHT,"animovement",em,W/2,BASELINE)["d"]}"/>')
    src = re.sub(r'<path[^>]*id="'+PKG+r'-hexagon"[^>]*/>',
                 wm + keyline_border(PKG, f'{PKG}-rbline'), src)
    src = src.replace('</defs>',
            rainbow_gradient('rb-word', WORD['L'], WORD['k'], WORD['x1'], 0, WORD['x2'], 0)
          + rainbow_gradient(f'{PKG}-rbline', LINE['L'], LINE['k'], 0, 0,
                             f"{W:.0f}", f"{H:.0f}", cap=float('inf'))
          + '</defs>')

    root = ET.fromstring(src)
    grads = {e.get('id'): e for e in root.iter() if e.tag == f'{{{SVG}}}linearGradient'}
    def stops_of(gid):
        e = grads[gid]
        if len(e): return e
        href = e.get(f'{{{XL}}}href') or e.get('href')
        return stops_of(href.lstrip('#')) if href else e
    paths = {e.get('id'): e for e in root.iter() if e.tag == f'{{{SVG}}}path'}

    mtn = [p for p in LAND if p not in FLAT]
    for i, name in enumerate(mtn):
        frac = i/(len(mtn)-1)
        hue  = HUES[min(int(frac*(len(HUES)-1)+0.5), len(HUES)-1)]
        k    = K_RANGE[0] + (K_RANGE[1]-K_RANGE[0])*frac
        e  = paths[f'{PKG}-{name}']; st = e.get('style') or ''
        m  = re.search(r'fill:\s*url\(#([^)]+)\)', st)
        if m:
            for s in stops_of(m.group(1)):
                sc = re.search(r'stop-color:\s*(#[0-9a-fA-F]{6})', s.get('style') or '')
                s.set('style', re.sub(r'stop-color:\s*#[0-9a-fA-F]{6}',
                                      f'stop-color:{recolour(sc.group(1),hue,k)}', s.get('style')))
        else:
            f = re.search(r'fill:\s*(#[0-9a-fA-F]{6})', st)
            if f:
                e.set('style', re.sub(r'fill:\s*#[0-9a-fA-F]{6}',
                                      f'fill:{recolour(f.group(1),hue,k)}', st))
            elif (e.get('fill') or '').startswith('#'):
                e.set('fill', recolour(e.get('fill'), hue, k))
    sky = tint(SKY['L'], HUES[0], SKY['k'], keepL=True)
    for name in FLAT:
        e = paths[f'{PKG}-{name}']; st = e.get('style') or ''
        if re.search(r'fill:\s*#[0-9a-fA-F]{6}', st):
            e.set('style', re.sub(r'fill:\s*#[0-9a-fA-F]{6}', f'fill:{sky}', st))
        else:
            e.set('fill', sky)

    os.makedirs(outdir, exist_ok=True)
    ET.ElementTree(root).write(f"{outdir}/{PKG}.svg", encoding='UTF-8', xml_declaration=True)
    print(f"  sky/river {sky}")
    for i,name in enumerate(mtn):
        frac=i/(len(mtn)-1)
        print(f"  {name:9s} hue {HUES[min(int(frac*7+0.5),7)]:6.1f}  "
              f"k={K_RANGE[0]+(K_RANGE[1]-K_RANGE[0])*frac:.2f}")

if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else "animovement-fixed.svg",
         sys.argv[2] if len(sys.argv)>2 else "out/packages")
