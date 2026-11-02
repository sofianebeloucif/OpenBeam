"""Cylindrical vector beams: the polarization, linear at each point, rotates around the axis.

``LG_{0,+m}`` and ``LG_{0,-m}`` in opposite circular polarizations give a field
linearly polarized at the angle ``m phi + theta0`` (polarization singularity of
index ``m`` on the axis, no orbital angular momentum). ``m = 1`` gives the radially
(``theta0 = 0``) and azimuthally (``theta0 = pi/2``) polarized beams; tightly
focused, the radial beam has a strong longitudinal field on the axis.
Q. Zhan, Adv. Opt. Photon. 1, 1 (2009); C. Rosales-Guzman, B. Ndagano,
A. Forbes, J. Opt. 20, 123001 (2018); R. Dorn, S. Quabis, G. Leuchs, PRL 91,
233901 (2003).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..field import MultiHarmonicField
from ..grid import Grid
from ._common import SIGMA_MINUS, SIGMA_PLUS, Beam, field_from_terms, lg0_with_gradient


@dataclass
class VectorBeam(Beam):
    """Vector beam of order ``m``: linear polarization at the angle ``m phi + theta0``.

    ``m = 1, theta0 = 0`` is radial and ``m = 1, theta0 = pi/2`` azimuthal.
    ``amplitude`` is the peak transverse field at the focus.
    """

    m: int = 1
    theta0: float = 0.0

    def field(self, grid: Grid) -> MultiHarmonicField:
        # e^{i(m phi + theta0)} (x - iy)/sqrt2 + e^{-i(m phi + theta0)} (x + iy)/sqrt2
        #   = sqrt2 (cos(m phi + theta0), sin(m phi + theta0))
        lam, w0 = self.wavelength, self.w0
        terms = [
            (SIGMA_MINUS * np.exp(1j * self.theta0) / np.sqrt(2), lg0_with_gradient(self.m, w0, lam, grid)),
            (SIGMA_PLUS * np.exp(-1j * self.theta0) / np.sqrt(2), lg0_with_gradient(-self.m, w0, lam, grid)),
        ]
        return field_from_terms(self, terms, grid)
