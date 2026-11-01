"""Fields of ``openbeam.BesselBeam`` (Bessel-Gauss) for the ``bessel`` web viewer (see ``common.py``)."""

from __future__ import annotations

from openbeam import BesselBeam

from .common import Variant, export_variants


def export() -> dict:
    beams = {"n0": BesselBeam(n=0), "n1": BesselBeam(n=1)}
    ref = beams["n0"]
    # wavefronts are planes travelling with the reduced axial wavenumber k_z = k - k_r^2 / 2k
    # (helicoids of charge n for n != 0); the core does not spread, so the arrow rings keep a fixed size
    k_axial = ref.k - ref.kr**2 / (2 * ref.k)
    scale = 6 / ref.kr
    variants = {
        vid: Variant(beam, phase=lambda rho, z, phi, n=beam.n: k_axial * z + n * phi, k_axial=k_axial,
                     scale=lambda z: scale)
        for vid, beam in beams.items()
    }
    data = export_variants(variants, ref.wavelength, ref.w0, ref.omega,
                           z_range=(-1.5 * ref.max_range, 1.5 * ref.max_range))
    data.update(source="openbeam.BesselBeam", kr_per_um=ref.kr * 1e-6, max_range_um=ref.max_range * 1e6,
                cone_angle_deg=float(ref.cone_angle * 180 / 3.141592653589793))
    return data
