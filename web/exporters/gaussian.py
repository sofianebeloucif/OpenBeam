"""Fields of ``openbeam.GaussianBeam`` for the ``gaussian`` web viewer (see ``common.py``)."""

from __future__ import annotations

from openbeam import GaussianBeam

from .common import Variant, export_variants


def export() -> dict:
    variants = {p: Variant(GaussianBeam(polarization=p), gouy_order=1) for p in ("linear", "circular")}
    beam = variants["linear"].beam
    data = export_variants(variants, beam.wavelength, beam.w0, beam.omega)
    data.update(source="openbeam.GaussianBeam")
    return data
