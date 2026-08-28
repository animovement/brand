"""Generators for the animovement brand artwork.

Library modules (lab, fitcurve, geometry, palette, typeset, waves) are imported
by the gen_* entry points, which are run as modules from the repository root:

    python -m animovement_brand.gen_packages base/animovement-fixed.svg out/packages

Paths such as base/fonts are resolved relative to the repository root, so run
pixi tasks from there.
"""
