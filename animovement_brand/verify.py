"""Compare regenerated artwork against shipped files, pixel for pixel.

Both sides are rasterised with the same renderer (cairosvg), so the numbers
measure whether the *artwork* matches, not whether two renderers agree.

    python -m animovement_brand.verify <reference-dir> [--width N]

Every SVG under out/ is matched by filename against the reference directory,
searched recursively. Files with no counterpart are reported, not skipped
silently. The reference directory may also be given as ANIMOVEMENT_REF_DIR.

The original build compared against /mnt/user-data/outputs inside a container
that no longer exists, rasterising via wkhtmltoimage. The recorded "max diff 0"
results came from that renderer; numbers here are not directly comparable to
them, though identical artwork should still land at 0.
"""
import argparse
import io
import os
import pathlib
import sys

import numpy as np
import cairosvg
from PIL import Image

# Flatten against mid-grey so differences in transparent regions still show up.
BACKGROUND = "#808080"


def render(path, width):
    png = cairosvg.svg2png(
        url=str(path), output_width=width, background_color=BACKGROUND
    )
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(int)


def compare(a, b, width):
    x, y = render(a, width), render(b, width)
    n, m = min(x.shape[0], y.shape[0]), min(x.shape[1], y.shape[1])
    d = np.abs(x[:n, :m] - y[:n, :m])
    return int(d.max()), float(d.mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "refdir",
        nargs="?",
        default=os.environ.get("ANIMOVEMENT_REF_DIR"),
        help="directory holding the shipped artwork (or $ANIMOVEMENT_REF_DIR)",
    )
    ap.add_argument("--width", type=int, default=512, help="raster width (default 512)")
    ap.add_argument("--outdir", default="out", help="generated artwork (default out)")
    args = ap.parse_args()

    if not args.refdir:
        ap.error("no reference directory given (argument or ANIMOVEMENT_REF_DIR)")
    ref = pathlib.Path(args.refdir)
    if not ref.is_dir():
        ap.error(f"reference directory not found: {ref}")

    generated = sorted(pathlib.Path(args.outdir).rglob("*.svg"))
    if not generated:
        ap.error(f"no SVGs under {args.outdir}/ — run `pixi run all` first")

    index = {}
    for p in ref.rglob("*.svg"):
        index.setdefault(p.name, p)

    matched = worst = 0
    unmatched = []
    for g in generated:
        r = index.get(g.name)
        if r is None:
            unmatched.append(g)
            continue
        mx, mean = compare(g, r, args.width)
        flag = "" if mx == 0 else "  <-- differs"
        print(f"  {g.name:26s} max {mx:3d}   mean {mean:7.4f}{flag}")
        matched += 1
        worst = max(worst, mx)

    for g in unmatched:
        print(f"  {g.name:26s} no counterpart in {ref}")

    print(
        f"\n{matched} compared, {len(unmatched)} unmatched, "
        f"worst max diff {worst}, rendered at {args.width}px"
    )
    return 1 if worst else 0


if __name__ == "__main__":
    sys.exit(main())
