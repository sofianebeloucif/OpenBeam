"""Fields of ``openbeam.VortexBeam`` and ``openbeam.VectorVortexBeam`` for the ``vortex`` web viewer."""

from __future__ import annotations

import numpy as np

from openbeam import VectorVortexBeam, VortexBeam

from .common import Variant, export_variants


def export() -> dict:
    variants = {
        # scalar vortices, polarized along x: helical wavefront, Gouy phase (|l| + 1) zeta
        "scalar-l1": Variant(VortexBeam(l=1), gouy_order=2, helicity=1),
        "scalar-l2": Variant(VortexBeam(l=2), gouy_order=3, helicity=2),
        # vector vortices of order 1: the polarization winds, the phase does not
        "radial": Variant(VectorVortexBeam(m=1, theta0=0.0), gouy_order=2),
        "azimuthal": Variant(VectorVortexBeam(m=1, theta0=np.pi / 2), gouy_order=2),
    }
    beam = variants["scalar-l1"].beam
    data = export_variants(variants, beam.wavelength, beam.w0, beam.omega)
    data.update(source="openbeam.VortexBeam, openbeam.VectorVortexBeam")
    return data
