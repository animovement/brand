"""MetBrewer Cross, with Orange retired and Teal replaced by Veronese jade.

Why the substitutions:
  Teal   #62929A  (h 214) sat only 20 degrees from Deepteal (h 234) - the two
                  ramps collapsed. Replaced by Veronese #175449 (h 178), which
                  lands almost centrally in the 87-degree gap between Sage and
                  Deepteal and needs no chroma clipping.
  Salmon #EE8577  (h 33) is the same hue as Red (h 31); one ramp for both.
  Orange #EB7926  (h 57) sat 21 degrees from Amber - the tightest remaining
                  pair at dE 11.1. Dropping it leaves seven hues spaced almost
                  evenly round the wheel (gap sd 3.6 degrees).
"""
import numpy as np
from lab import parse, rgb2lab, lab2lch, lab2rgb, lch2lab, hx, ingamut_strict, max_chroma

CROSS_FULL = [("Magenta","#C969A1"),("Red","#CE4441"),("Salmon","#EE8577"),
              ("Orange","#EB7926"),("Amber","#FFBB44"),("Sage","#859B6C"),
              ("Teal","#62929A"),("Deepteal","#004F63"),("Navy","#122451")]

# the eight used for the vivid marks (rainbow order, warm -> cool)
CROSS = [("Magenta","#C969A1"),("Red","#CE4441"),("Orange","#EB7926"),
         ("Amber","#FFBB44"),("Sage","#859B6C"),("Jade","#175449"),
         ("Deepteal","#004F63"),("Navy","#122451")]

# the seven that carry a package identity (Orange retired)
PACKAGES = [("anicore","Jade"),("aniread","Sage"),
            ("aniprocess","Amber"),("animetric","Deepteal"),("anicheck","Red"),
            ("anivis","Magenta"),("anispace","Navy")]

HUES  = [float(lab2lch(rgb2lab(parse(b)))[2]) for _,b in CROSS]
HUE   = {n.lower(): float(lab2lch(rgb2lab(parse(b)))[2]) for n,b in CROSS}
BASE  = {n.lower(): b for n,b in CROSS}

# ---- the original logo's own structure, used to recolour it ------------------
SRC_BORDER_HUE = 208.6
SRC_RAMP = ['#FEF8ED','#E7E6D1','#CDD1B7','#B7BB8D','#A9B083','#91A68C',
            '#708D84','#5E8274','#3E6A62','#023A3F']

def _w(L):
    return float(np.clip((100.0-L)/40.0,0,1) * np.clip((L+12.0)/48.0,0.62,1.0))

def ramp_fn(base_hex, cmin=20.0, cmax=48.0):
    """Monochrome ramp in one hue: lightness drives everything, chroma fades to
    a faint tint near white and eases back at the dark end."""
    L,C,h = lab2lch(rgb2lab(parse(base_hex)))
    Cref = float(np.clip(C/max(_w(L),1e-6), cmin, cmax))
    def f(L_target):
        for k in np.linspace(1,0,26):
            lab=lch2lab(np.array([L_target, Cref*_w(L_target)*k, h]))
            if ingamut_strict(lab): return hx(lab2rgb(lab))
        return hx(lab2rgb(lch2lab(np.array([L_target,0,h]))))
    return f

if __name__=='__main__':
    print(f"{'name':9s} {'base':9s} {'L':>6s} {'C':>6s} {'h':>7s}")
    for n,b in CROSS:
        L,C,h=lab2lch(rgb2lab(parse(b)))
        print(f"{n:9s} {b:9s} {L:6.1f} {C:6.1f} {h:7.1f}")
    hs=sorted(HUES); gaps=[(hs[(i+1)%len(hs)]-hs[i])%360 for i in range(len(hs))]
    print(f"\nhue gaps: {[round(g) for g in gaps]}  sd={np.std(gaps):.1f}")
