"""1200 x 630 social cards: vertical waves under an even white haze."""
import os, sys
from .palette import HUES
from .waves import gradients, bands_v, namespace
W,H = 1200.0, 630.0

def radial_haze(gid, base):
    return (f'<radialGradient id="{gid}" cx="0.5" cy="0.5" r="0.80">'
            f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="{min(base+0.10,1):.2f}"/>'
            f'<stop offset="0.55" stop-color="#FFFFFF" stop-opacity="{base:.2f}"/>'
            f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="{max(base-0.08,0):.2f}"/>'
            f'</radialGradient>')

def card(haze=0.50, L0=70.0, L1=50.0, amp=0.040, freq=0.85, bleed=0.16, key='g'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
            f'width="{W:.0f}" height="{H:.0f}"><defs>'
            + gradients(key,HUES,L0,L1,horiz=True) + radial_haze('hz',haze)
            + f'<clipPath id="c"><rect width="{W:.0f}" height="{H:.0f}"/></clipPath></defs>'
            + f'<g clip-path="url(#c)">' + bands_v(W,H,key,amp=amp,freq=freq,bleed=bleed,span=0.95,start=0.05,samples=240)
            + f'<rect width="{W:.0f}" height="{H:.0f}" fill="url(#hz)"/></g></svg>')

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else "out/og"
    os.makedirs(out,exist_ok=True)
    for hz in (0.40,0.50,0.60,0.70):
        n=f"og-v-haze{int(hz*100)}"
        open(f"{out}/{n}.svg","w").write(namespace(card(haze=hz),n)); print("  ",n)
