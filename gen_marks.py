"""Non-hex marks: squares, circles and icons with vivid wave bands."""
import os, sys
from palette import HUES
from waves import gradients, bands_h, bands_v, namespace
from typeset import POPPINS_REG, POPPINS_MEDIUM, centred

VIVID = dict(L0=74.0, L1=54.0)          # light at the top, deep at the foot

def mark(size, clip, txt, target_w, font, vertical=True, amp=None, freq=None, key='g'):
    fn   = bands_v if vertical else bands_h
    kw   = {k:v for k,v in (('amp',amp),('freq',freq)) if v is not None}
    body = fn(size,size,key,**kw)
    d    = centred(font,txt,target_w,size/2,size/2)['d']
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}"><defs>'
            + gradients(key,HUES,horiz=vertical,**VIVID)
            + f'<clipPath id="c">{clip}</clipPath></defs><g clip-path="url(#c)">'
            + body
            + f'<path d="{d}" fill="#FFFFFF" fill-rule="evenodd"/>'   # solid, not knocked out
            + '</g></svg>')

RSQ = lambda s,r: f'<rect width="{s}" height="{s}" rx="{r}"/>'
RCI = lambda s:   f'<circle cx="{s/2}" cy="{s/2}" r="{s/2}"/>'

SPEC = {
 'square-wave-v-ani'  : (512, RSQ(512,96), "ani", 300, POPPINS_REG,    True,  None, None),
 'square-wave-v-a'    : (512, RSQ(512,96), "a",   190, POPPINS_MEDIUM, True,  None, None),
 'circle-wave-v-ani'  : (512, RCI(512),    "ani", 280, POPPINS_REG,    True,  None, None),
 'circle-wave-v-a'    : (512, RCI(512),    "a",   190, POPPINS_MEDIUM, True,  None, None),
 'icon-wave-v-a'      : (256, RSQ(256,52), "a",   104, POPPINS_MEDIUM, True,  0.060, 0.95),
 'icon-wave-v-circle' : (256, RCI(256),    "a",   104, POPPINS_MEDIUM, True,  0.060, 0.95),
 'icon-wave-v-ani'    : (256, RSQ(256,52), "ani", 180, POPPINS_REG,    True,  0.060, 0.95),
}

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else "out/marks"
    os.makedirs(out,exist_ok=True)
    for name,(s,clip,txt,tw,font,vert,amp,freq) in SPEC.items():
        svg=namespace(mark(s,clip,txt,tw,font,vert,amp,freq), name)
        open(f"{out}/{name}.svg","w").write(svg); print("  ",name)
