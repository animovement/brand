"""Regular pointy-top hexagon at hexb.in proportions (43.9 x 50.8 mm)."""
import math
W = 1200.0
H = W*2/math.sqrt(3)          # 1385.6406
CX, CY = W/2, H/2

def hex_path(inset=0.0):
    """Path inset perpendicular from the outer edge by `inset`."""
    a = W/2-inset
    b = H/2-1.1547*inset
    v=[(CX,CY-b),(CX+a,CY-b/2),(CX+a,CY+b/2),(CX,CY+b),(CX-a,CY+b/2),(CX-a,CY-b/2)]
    return "M"+" L".join(f"{x:.2f} {y:.2f}" for x,y in v)+" Z"

# keyline border: 46px white band with a 10px coloured line at the outer edge
WHITE_BAND = 46.0
KEYLINE    = 10.0

def keyline_border(pkg, gradient_id):
    return (f'<g id="{pkg}-hexagon">'
            f'<path d="{hex_path(WHITE_BAND/2)}" fill="none" stroke="#FFFFFF" '
            f'stroke-width="{WHITE_BAND}" stroke-linejoin="round"/>'
            f'<path d="{hex_path(KEYLINE/2)}" fill="none" stroke="url(#{gradient_id})" '
            f'stroke-width="{KEYLINE}" stroke-linejoin="round"/></g>')
