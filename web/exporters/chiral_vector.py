"""Fields of ``openbeam.ChiralVectorBeam`` for the ``chiral-vector`` web viewer (see ``common.py``)."""

from __future__ import annotations

from openbeam import ChiralVectorBeam

from .common import Variant, export_variants


def export() -> dict:
    beam = ChiralVectorBeam()
    # wavefronts of the radial w beam: LG_{0,+-1}, Gouy phase 2 zeta, polarization (not phase) winds
    data = export_variants({"default": Variant(beam, gouy_order=2)}, beam.wavelength, beam.w_omega, beam.omega)
    data.update(source="openbeam.ChiralVectorBeam", psi_2w=beam.psi_2w, intensity_ratio=beam.intensity_ratio)
    return data
