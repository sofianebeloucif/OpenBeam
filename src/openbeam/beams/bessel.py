"""Bessel(-Gauss) beam: a quasi non-diffracting beam.

An ideal Bessel beam ``J_n(k_r rho) e^{i n phi} e^{i k_z z}`` keeps the same
transverse profile while propagating, but carries infinite energy
(J. Durnin, J. J. Miceli, J. H. Eberly, Phys. Rev. Lett. 58, 1499 (1987)).
A physical beam is limited by an aperture; the Bessel-Gauss beam, a Bessel
beam under a Gaussian envelope of waist ``w0``, is an exact paraxial solution
(F. Gori, G. Guattari, C. Padovani, Opt. Commun. 64, 491 (1987)):

    u = 1/d J_n(k_r rho / d) e^{i n phi} exp(-rho^2 / (w0^2 d)) exp(-i k_r^2 z / (2 k d)),  d = 1 + i z / z_R,

with ``z_R`` the Rayleigh range of the envelope. Its core keeps a radius of
about ``2.405 / k_r`` (for n = 0) over ``z_max = w0 k / k_r``, the length over
which the cone of plane waves (half-angle ``asin(k_r / k)``) overlaps.

The longitudinal field ``E_z = (i/k) div_perp E_perp`` is computed analytically
with ``(d_x +- i d_y) [J_n(b rho) e^{i n phi}] = -+ b J_{n+-1}(b rho) e^{i (n+-1) phi}``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import jv

from ..field import MultiHarmonicField
from ..grid import Grid
from ..modes import rayleigh_range
from .vortex import POLARIZATIONS


@dataclass
class BesselBeam:
    """Bessel-Gauss beam of order ``n`` with a uniform polarization.

    ``kr`` is the radial wavenumber, ``w0`` the waist of the Gaussian envelope;
    ``polarization`` is ``"linear"`` (along x), ``"circular"`` or a Jones vector.
    ``amplitude`` is the peak transverse field at the focus.
    """

    wavelength: float = 632.8e-9
    kr: float = 2.0e6
    w0: float = 8e-6
    n: int = 0
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
    def cone_angle(self) -> float:
        return float(np.arcsin(self.kr / self.k))

    @property
    def max_range(self) -> float:
        """``z_max = w0 k / k_r``: half-length of the quasi non-diffracting region."""
        return self.w0 * self.k / self.kr

    @property
    def jones(self) -> np.ndarray:
        if isinstance(self.polarization, str):
            return POLARIZATIONS[self.polarization]
        p = np.array([*self.polarization, 0], dtype=complex)
        return p / np.linalg.norm(p)

    def _peak(self) -> float:
        rho = np.linspace(0, 3 * self.w0, 20001)
        return float(np.max(np.abs(jv(self.n, self.kr * rho)) * np.exp(-((rho / self.w0) ** 2))))

    def field(self, grid: Grid) -> MultiHarmonicField:
        k, n = self.k, self.n
        d = 1 + 1j * grid.z / rayleigh_range(self.w0, self.wavelength)
        a = 1 / (self.w0**2 * d)
        b = self.kr / d
        envelope = np.exp(-a * grid.rho**2 - 1j * self.kr**2 * grid.z / (2 * k * d)) / d / self._peak()

        def bessel(m):  # J_m(b rho) e^{i m phi}
            return jv(m, b * grid.rho) * np.exp(1j * m * grid.phi)

        f = bessel(n)
        df_dx = b / 2 * (bessel(n - 1) - bessel(n + 1))
        df_dy = -b / 2j * (bessel(n + 1) + bessel(n - 1))
        u = envelope * f
        du_dx = envelope * (df_dx - 2 * a * grid.x * f)
        du_dy = envelope * (df_dy - 2 * a * grid.y * f)

        p = self.jones
        E = np.zeros((3, *grid.shape), dtype=complex)
        E[0], E[1] = p[0] * u, p[1] * u
        E[2] = 1j / k * (p[0] * du_dx + p[1] * du_dy)
        E *= self.amplitude
        if self.include_carrier:
            E = E * np.exp(1j * k * grid.z)
        return MultiHarmonicField(grid=grid, omega=self.omega, harmonics={1: E})
