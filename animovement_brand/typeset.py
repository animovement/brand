"""Font -> SVG outline paths via fontTools. No <text>, so no font dependency
in the delivered artwork."""
import os
import pathlib
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

# Poppins is vendored in base/fonts/ at the repository root (this file lives one
# level down, in the package), so a checkout is self-contained. Override with
# ANIMOVEMENT_FONT_DIR; the original build used
# /usr/share/fonts/truetype/google-fonts inside a Linux container.
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_FONT_DIR = pathlib.Path(
    os.environ.get("ANIMOVEMENT_FONT_DIR", _REPO_ROOT / "base" / "fonts")
)

POPPINS_LIGHT  = str(_FONT_DIR / "Poppins-Light.ttf")
POPPINS_REG    = str(_FONT_DIR / "Poppins-Regular.ttf")
POPPINS_MEDIUM = str(_FONT_DIR / "Poppins-Medium.ttf")

def _layout(font,txt):
    if not os.path.exists(font):
        raise FileNotFoundError(
            f"{font} not found. Poppins is OFL-licensed: drop "
            f"Poppins-Light/Regular/Medium.ttf into base/fonts/, or point "
            f"ANIMOVEMENT_FONT_DIR at a directory holding them."
        )
    f=TTFont(font); gs=f.getGlyphSet(); cm=f.getBestCmap(); upem=f['head'].unitsPerEm
    items=[]; x=0
    for ch in txt:
        gn=cm.get(ord(ch))
        if gn is None: continue
        items.append((gn,x)); x+=gs[gn].width
    return gs,upem,items

def _ink(gs,items):
    bp=BoundsPen(gs)
    for gn,xo in items: gs[gn].draw(TransformPen(bp,Transform(1,0,0,1,xo,0)))
    return bp.bounds

def em_for(font,txt,target_w):
    """em size that makes txt exactly target_w wide (ink bounds, not advance)."""
    gs,upem,items=_layout(font,txt); x0,_,x1,_=_ink(gs,items)
    return upem*target_w/(x1-x0)

def word(font,txt,em,cx=600.0,baseline=560.0):
    """Outline path with the ink box horizontally centred on cx."""
    gs,upem,items=_layout(font,txt); x0,y0,x1,y1=_ink(gs,items)
    s=em/upem; ox=cx-s*(x0+x1)/2
    pen=SVGPathPen(gs)
    for gn,xo in items: gs[gn].draw(TransformPen(pen,Transform(s,0,0,-s,ox+s*xo,baseline)))
    return dict(d=pen.getCommands(), width=s*(x1-x0), top=baseline-s*y1, bottom=baseline-s*y0)

def centred(font,txt,target_w,cx,cy):
    """Ink box centred on (cx,cy) both ways. Self-corrects for the dot on 'i',
    which is what threw the early icon centring out by up to 33px."""
    em=em_for(font,txt,target_w)
    r=word(font,txt,em,cx,0.0)
    return word(font,txt,em,cx,cy-(r['top']+r['bottom'])/2)
