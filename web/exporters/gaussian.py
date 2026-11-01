"""Fields of ``openbeam.GaussianBeam`` for the ``gaussian`` web viewer (see ``common.py``)."""

from __future__ import annotations

from openbeam import GaussianBeam

from .common import export_variants


def export() -> dict:
    variants = {p: GaussianBeam(polarization=p) for p in ("linear", "circular")}
    beam = variants["linear"]
    data = export_variants(variants, beam.wavelength, beam.w0, gouy_order=1, omega=beam.omega)
    data.update(source="openbeam.GaussianBeam")
    return data
