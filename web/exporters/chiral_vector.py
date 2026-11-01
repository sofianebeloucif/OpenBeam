"""Fields of ``openbeam.ChiralVectorBeam`` for the ``chiral-vector`` web viewer (see ``common.py``)."""

from __future__ import annotations

from openbeam import ChiralVectorBeam

from .common import export_variants


def export() -> dict:
    beam = ChiralVectorBeam()
    data = export_variants({"default": beam}, beam.wavelength, beam.w_omega, gouy_order=2, omega=beam.omega)
    data.update(source="openbeam.ChiralVectorBeam", psi_2w=beam.psi_2w,
                intensity_ratio=beam.intensity_ratio)
    return data
