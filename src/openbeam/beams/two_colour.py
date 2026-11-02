"""Two-colour (w + 2w) beams, the building block of synthetic chiral light.

Superposing a beam at ``w`` with a beam at ``2w`` makes the electric field draw,
at each point, a 3D Lissajous figure during one cycle; when the field has a
component out of the transverse plane (longitudinal field of a focused beam)
this figure can be chiral: locally chiral light (D. Ayuso et al., Nat. Photon.
13, 866 (2019)), measured by ``openbeam.chiral_correlation``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..field import MultiHarmonicField
from ..grid import Grid


@dataclass
class TwoColourBeam:
    """``fundamental`` at ``w`` plus ``second`` at ``2w`` (its wavelength must be half).

    The 2w field is scaled by ``sqrt(intensity_ratio)`` (ratio of peak
    intensities when both beams have unit amplitude) and delayed by ``psi_2w``.
    """

    fundamental: object
    second: object
    intensity_ratio: float = 0.01
    psi_2w: float = 0.0

    def __post_init__(self):
        if not np.isclose(self.second.wavelength, self.fundamental.wavelength / 2):
            raise ValueError("the second beam must have half the wavelength of the fundamental")

    @property
    def wavelength(self) -> float:
        return self.fundamental.wavelength

    @property
    def omega(self) -> float:
        return self.fundamental.omega

    def field(self, grid: Grid) -> MultiHarmonicField:
        E1 = self.fundamental.field(grid).harmonics[1]
        E2 = self.second.field(grid).harmonics[1] * np.sqrt(self.intensity_ratio) * np.exp(1j * self.psi_2w)
        return MultiHarmonicField(grid=grid, omega=self.omega, harmonics={1: E1, 2: E2})
