# animovement brand

Source of truth for the *animovement* artwork: the scripts that generate the
package hexes, icon marks, OpenGraph card and README banner, plus the traced
base logo they all derive from.

Nothing here is rendered or published automatically. Output is copied by hand
into the repos that consume it:

| output | consumed by |
| --- | --- |
| `out/packages/<pkg>.svg` | each package's `man/figures/logo.svg`, and `assets/logos/` on the website |
| `out/marks/` | favicons and app icons on the website |
| `out/og/` | `assets/images/opengraph-card.*` on the website |
| `out/banner/` | the README banner |

## Provenance

**The scripts are a reconstruction, not the original files** — the working
container was reset and the originals were lost. They have been re-run and
checked against the delivered artwork (see *Verification* below), but treat
them as freshly written code rather than the exact scripts that produced the
shipped assets. That loss is why they are versioned here.

`base/animovement-fixed.svg` is the one file that **cannot be regenerated**.
It came from vector-tracing the original raster logo, and the tracing pipeline
that produced it is not included (see *Not included*). Everything else in this
repo can be rebuilt from it.

## Setup

Python 3 with `numpy`, `fonttools` and `Pillow`:

```
python3 -m venv .venv && . .venv/bin/activate
pip install numpy fonttools Pillow
```

Poppins is **not vendored yet**. It is OFL-licensed and redistributable, so it
can be committed here: drop `Poppins-Light.ttf`, `Poppins-Regular.ttf` and
`Poppins-Medium.ttf` into `base/fonts/`. Alternatively point
`ANIMOVEMENT_FONT_DIR` at a directory that has them. Until then the generators
raise a `FileNotFoundError` naming the missing file. The original build read
them from `/usr/share/fonts/truetype/google-fonts` inside a Linux container.

`verify.py` additionally shells out to a renderer to rasterise SVGs for
comparison.

## Modules

| file | what it does |
|---|---|
| `lab.py` | sRGB ↔ CIELAB ↔ LCh, **strict** gamut testing, `max_chroma`, `vivid`, WCAG `contrast` |
| `fitcurve.py` | Schneider least-squares cubic Bézier fitting |
| `typeset.py` | font → SVG outline paths (no `<text>`, so no font dependency) |
| `palette.py` | MetBrewer Cross + substitutions, monochrome ramp builder |
| `waves.py` | wave band generation, gaussian haze, id namespacing |
| `geometry.py` | regular pointy-top hexagon, keyline border |

## Generators

```
python3 gen_packages.py base/animovement-fixed.svg out/packages
python3 gen_marks.py    out/marks
python3 gen_og.py       out/og
python3 gen_banner.py   out/banner
```

`gen_packages.py` needs `base/animovement-fixed.svg` — the traced,
geometry-corrected landscape. See *Provenance* above: it is data, not output.

## Things that bit during the build

**Gamut testing must be strict.** `lab2rgb` clips internally, so a naive
round-trip reports every colour as in-gamut and chroma ceilings come back
meaningless. `ingamut_strict` checks the unclipped values. This bug made an
early palette come out muted because chroma was being clamped invisibly.

**Chroma ceilings vary hugely by hue.** At L\* 60, green reaches C\* 77 but
teal only 35.7. Setting chroma as a fraction of each hue's own ceiling keeps a
set looking evenly vivid; setting one absolute value leaves teals dull and
clips oranges. In a *landscape* the reverse applies — a fraction-of-ceiling rule
makes green shout, so `gen_rainbow` caps it.

**Lightness caps chroma.** Above roughly L\* 85 no hue holds much saturation.
Asking for vivid colour there does nothing; the fix is to compress the
lightness range into 45–80 first.

**Namespace every id.** Inlining several SVGs into one HTML document makes every
`url(#gradient119)` resolve to the first definition found. This silently turned
all eight package gradients magenta in one contact sheet. `waves.namespace()`
prefixes ids and references.

**Centre type on ink bounds, not the baseline.** The dot on the `i` extends the
ink box upward; centring by eye left the 512px marks 33px high. `typeset.centred`
measures and corrects.

**A linear haze ramp clamps.** Once pad + feather reaches the edge, increasing
feather stops doing anything. `waves.gaussian_haze` feathers all the way out.

**Booleans need closed, stroked-to-path shapes.** Inkscape's Intersection works
on fill areas; open paths get implicitly closed with a straight segment.

## Verification

`verify.py` re-renders regenerated files against the shipped ones and reports
the pixel difference. Current state:

```
anicore.svg             max diff 0    (packages, exact)
aniread.svg             max diff 0
anivis.svg              max diff 0
anispace.svg            max diff 0
icon-wave-v-a.svg       max diff 0    (marks, exact)
square-wave-v-ani.svg   max diff 0
og-v-haze50.svg         max diff 3    (antialiasing only)
banner-s34.svg          max diff 4    (antialiasing only)
```

## Not included

The original raster-tracing pipeline (image segmentation, ridge tracking,
gradient fitting) that produced `animovement-fixed.svg` from the source PNG.
It is reconstructible from the session transcript if ever needed, but the
traced SVG already exists so it should not be.
