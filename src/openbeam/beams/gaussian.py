"""Fundamental Gaussian beam (TEM00) with its first post-paraxial longitudinal field."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..field import MultiHarmonicField
from ..grid import Grid
from ..modes import beam_radius, gouy_phase, inverse_curvature

POLARIZATIONS = {
    "linear": np.array([1, 0, 0], dtype=complex),
    "circular": np.array([1, 1j, 0]) / np.sqrt(2),
}


@dataclass
class GaussianBeam:
    """Paraxial Gaussian beam ``E = A u_00(rho, z) e^{ikz} p + E_z e_z``.

    ``polarization`` is ``"linear"`` (along x), ``"circular"`` or a Jones
    vector ``(p_x, p_y)``. ``amplitude`` is the transverse field at the
    centre of the focus. The longitudinal component follows from
    ``div E = 0`` at first post-paraxial order, ``E_z = (i/k) div_perp E_perp``,
    the same relation as for ``ChiralVectorBeam``.
    """

    wavelength: float = 632.8e-9
    w0: float = 2.5e-6
    polarization: str | tuple = "linear"
    amplitude: float = 1.0
    include_carrier: bool = True

    @property
    def k(self) -> float:
        return 2 * np.pi / self.wavelength

    @property
    def omega(self) -> float:
        return 2 * np.pi * 299_792_458.0 / self.wavelength

    @property
    def jones(self) -> np.ndarray:
        if isinstance(self.polarization, str):
            return POLARIZATIONS[self.polarization]
        p = np.array([*self.polarization, 0], dtype=complex)
        return p / np.linalg.norm(p)

    def envelope(self, grid: Grid) -> tuple[np.ndarray, np.ndarray]:
        """Scalar envelope ``u`` (1 at the focus centre) and ``q`` with ``u ~ exp(-q rho^2)``."""
        lam, w0 = self.wavelength, self.w0
        w = beam_radius(grid.z, w0, lam)
        q = 1 / w**2 - 0.5j * self.k * inverse_curvature(grid.z, w0, lam)
        u = w0 / w * np.exp(-q * grid.rho**2 - 1j * gouy_phase(grid.z, w0, lam))
        return u, q

    def field(self, grid: Grid) -> MultiHarmonicField:
        u, q = self.envelope(grid)
        p = self.jones.reshape(3, 1, 1, 1)
        E = self.amplitude * p * u
        # d_x u = -2 q x u and d_y u = -2 q y u
        E[2] = 1j / self.k * (-2 * q) * (grid.x * E[0] + grid.y * E[1])
        if self.include_carrier:
            E = E * np.exp(1j * self.k * grid.z)
        return MultiHarmonicField(grid=grid, omega=self.omega, harmonics={1: E})
