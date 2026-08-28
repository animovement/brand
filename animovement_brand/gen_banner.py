"""1200 x 200 organisation banner: vertical waves, gaussian haze through the
middle, wordmark as a window onto the unhazed bands."""
import os, sys
from .palette import HUES
from .waves import gradients, bands_v, gaussian_haze, namespace
from .typeset import POPPINS_LIGHT, centred
W,H = 1200.0, 200.0

def banner(txt="animovement", tw=560.0, sigma=0.34, peak=0.90,
           amp_px=22.0, freq=0.7, phase=0.8, bleed=0.20, L0=70.0, L1=50.0, key='g'):
    bands = bands_v(W,H,key,amp_px=amp_px,freq=freq,phase=phase,bleed=bleed,span=0.95,start=0.05,samples=200,tol=0.30)
    d = centred(POPPINS_LIGHT,txt,tw,W/2,H/2)['d']
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
            f'width="{W:.0f}" height="{H:.0f}"><defs>'
            + gradients(key,HUES,L0,L1,horiz=True)
            + gaussian_haze('hz',peak=peak,sigma=sigma)
            + f'<clipPath id="c"><rect width="{W:.0f}" height="{H:.0f}"/></clipPath>'
            + f'<clipPath id="t"><path d="{d}"/></clipPath></defs>'
            + f'<g clip-path="url(#c)">' + bands
            + f'<rect width="{W:.0f}" height="{H:.0f}" fill="url(#hz)"/>'
            + f'<g clip-path="url(#t)">' + bands + '</g></g></svg>')

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else "out/banner"
    os.makedirs(out,exist_ok=True)
    for s in (0.28,0.34,0.42):
        n=f"banner-s{int(s*100)}"
        open(f"{out}/{n}.svg","w").write(namespace(banner(sigma=s),n)); print("  ",n)
