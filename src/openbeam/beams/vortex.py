"""Scalar optical vortex: ``LG_{0,l}`` mode with a uniform polarization.

Its phase ``e^{i l phi}`` winds ``l`` times around the axis (helical wavefront)
and the beam carries an orbital angular momentum ``l hbar`` per photon.
L. Allen, M. W. Beijersbergen, R. J. C. Spreeuw, J. P. Woerdman, Phys. Rev. A
45, 8185 (1992).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..field import MultiHarmonicField
from ..grid import Grid
from ._common import Beam, field_from_terms, jones_vector, lg0_with_gradient


@dataclass
class VortexBeam(Beam):
    """Scalar vortex ``LG_{0,l}`` with a uniform polarization (``"linear"`` along x, ``"circular"`` or Jones).

    ``amplitude`` is the peak transverse field at the focus.
    """

    l: int = 1
    polarization: str | tuple = "linear"

    @property
    def jones(self):
        return jones_vector(self.polarization)

    def field(self, grid: Grid) -> MultiHarmonicField:
        return field_from_terms(self, [(self.jones, lg0_with_gradient(self.l, self.w0, self.wavelength, grid))], grid)
