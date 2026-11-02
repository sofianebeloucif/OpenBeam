"""Fundamental Gaussian beam (TEM00): the ``l = 0`` vortex.

H. Kogelnik, T. Li, Appl. Opt. 5, 1550 (1966).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .vortex import VortexBeam


@dataclass
class GaussianBeam(VortexBeam):
    """Gaussian beam ``E = A u_00 p``, polarization ``"linear"`` (x), ``"circular"`` or a Jones vector.

    ``amplitude`` is the field at the centre of the focus. Its longitudinal field
    is ``E_z = (i/k) div_perp E_perp``: zero on the axis, two lobes along a linear
    polarization.
    """

    l: int = field(default=0, init=False)
