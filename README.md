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

Everything runs through [pixi](https://pixi.sh) — no manual environment steps:

```
pixi run all
```

`pixi.toml` pins `python`, `numpy`, `fonttools` and `Pillow` from conda-forge,
and pixi resolves them on first run. Individual targets are available too:

| task | output |
| --- | --- |
| `pixi run packages` | `out/packages/` — the seven package hexes |
| `pixi run marks` | `out/marks/` — icon and square marks |
| `pixi run og` | `out/og/` — OpenGraph cards at four haze levels |
| `pixi run banner` | `out/banner/` — README banners at three sizes |
| `pixi run all` | all of the above |

Poppins Light, Regular and Medium are vendored in `base/fonts/` along with
their OFL licence, so a fresh checkout renders type without installing
anything. Paths resolve from the repository root, so run tasks from there; set
`ANIMOVEMENT_FONT_DIR` to point elsewhere. The original build read them from
`/usr/share/fonts/truetype/google-fonts` inside a Linux container.

## Layout

```
base/                    inputs that are not generated
  animovement-fixed.svg  the traced landscape everything derives from
  fonts/                 Poppins + OFL licence
animovement_brand/       library modules and gen_* entry points
out/                     generated artwork (gitignored)
```

## Modules

| file | what it does |
|---|---|
| `animovement_brand/lab.py` | sRGB ↔ CIELAB ↔ LCh, **strict** gamut testing, `max_chroma`, `vivid`, WCAG `contrast` |
| `animovement_brand/fitcurve.py` | Schneider least-squares cubic Bézier fitting |
| `animovement_brand/typeset.py` | font → SVG outline paths (no `<text>`, so no font dependency) |
| `animovement_brand/palette.py` | MetBrewer Cross + substitutions, monochrome ramp builder |
| `animovement_brand/waves.py` | wave band generation, gaussian haze, id namespacing |
| `animovement_brand/geometry.py` | regular pointy-top hexagon, keyline border |

## Generators

The pixi tasks above wrap these; call them directly only to change arguments.
They run as modules, so invoke them from the repository root.

```
pixi run python -m animovement_brand.gen_packages base/animovement-fixed.svg out/packages
pixi run python -m animovement_brand.gen_marks  out/marks
pixi run python -m animovement_brand.gen_og     out/og
pixi run python -m animovement_brand.gen_banner out/banner
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

`pixi run verify <reference-dir>` rasterises every SVG under `out/` and the
same-named file under the reference directory, and reports the pixel
difference. Both sides go through the same renderer (cairosvg), so the numbers
measure whether the *artwork* matches rather than whether two renderers agree.
Files with no counterpart are listed, not skipped silently.

Against the logos shipped on the website:

```
$ pixi run verify ../animovement-website/assets/logos
  anicheck.svg               max   0   mean  0.0000
  anicore.svg                max   0   mean  0.0000
  animetric.svg              max   0   mean  0.0000
  aniprocess.svg             max   0   mean  0.0000
  aniread.svg                max   0   mean  0.0000
  anispace.svg               max   0   mean  0.0000
  anivis.svg                 max   0   mean  0.0000

7 compared, 14 unmatched, worst max diff 0, rendered at 512px
```

All seven hexes are pixel-identical to what is shipped. The generated files are
28 bytes larger as text — one gradient id is named `keyline` rather than
`rbline`, and the wordmark carries an `inkscape:label` — but the path geometry
is byte-identical and neither difference renders.

The 14 unmatched are the marks, OG cards and banners, which ship under
different filenames elsewhere in the website repo; point `verify` at those
directories to check them.

The original build rasterised via `wkhtmltoimage` against
`/mnt/user-data/outputs` in a container that no longer exists, and recorded
`max diff 3`/`4` on the OG card and banner as antialiasing noise. Those numbers
came from a different renderer and are not directly comparable to these.

## Not included

**The metapackage hex.** `gen_packages.py` produces the seven package logos;
`animovement.svg` is not among them and cannot currently be regenerated from
anything in this repo. The shipped file lives on the website in
`assets/logos/animovement.svg`. How it was produced was not recovered.

The original raster-tracing pipeline (image segmentation, ridge tracking,
gradient fitting) that produced `animovement-fixed.svg` from the source PNG.
It is reconstructible from the session transcript if ever needed, but the
traced SVG already exists so it should not be.
