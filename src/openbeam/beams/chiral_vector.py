"""Chiral vector beam: synthetic chiral light made of two cylindrical vector beams.

A tightly focused radially polarized beam at ``omega`` (with its longitudinal
field) plus an azimuthally polarized beam at ``2 omega``: at each point the
field draws a chiral 3D Lissajous figure (locally chiral light, D. Ayuso et al.,
Nat. Photon. 13, 866 (2019)), measured by ``openbeam.chiral_correlation``.
Beam proposed by A. Rodriguez et al., "Chiral Vector Beams for Topological
Enantio-Sensitive Imaging", arXiv:2610.17111 (2026), whose parameters are the
defaults here.

``psi_2w`` is the phase of the azimuthal field relative to the radial one at
the focus; the modulus of h5 does not depend on it and ``psi_2w -> psi_2w + pi``
flips its sign.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..field import MultiHarmonicField
from ..grid import Grid
from .two_colour import TwoColourBeam
from .vector import VectorBeam


@dataclass
class ChiralVectorBeam:
    """Radial vector beam at ``omega`` + azimuthal vector beam at ``2 omega``.

    ``amplitude`` is the peak transverse field of the ``omega`` beam at the
    focus; the ``2 omega`` peak is ``amplitude * sqrt(intensity_ratio)``.
    """

    wavelength: float = 639e-9
    w_omega: float = 2.5e-6
    w_2omega: float = 5e-6
    intensity_ratio: float = 0.01
    psi_2w: float = 1.94 * np.pi
    amplitude: float = 1.0
    include_carrier: bool = True

    @property
    def k(self) -> float:
        return 2 * np.pi / self.wavelength

    @property
    def omega(self) -> float:
        return 2 * np.pi * 299_792_458.0 / self.wavelength

    def two_colour(self) -> TwoColourBeam:
        common = dict(m=1, amplitude=self.amplitude, include_carrier=self.include_carrier)
        return TwoColourBeam(
            VectorBeam(wavelength=self.wavelength, w0=self.w_omega, theta0=0.0, **common),
            VectorBeam(wavelength=self.wavelength / 2, w0=self.w_2omega, theta0=np.pi / 2, **common),
            intensity_ratio=self.intensity_ratio, psi_2w=self.psi_2w,
        )

    def field(self, grid: Grid) -> MultiHarmonicField:
        return self.two_colour().field(grid)
