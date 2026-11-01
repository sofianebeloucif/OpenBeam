"""Optical vortex beams: scalar (helical phase) and vector (rotating polarization).

* Scalar vortex: ``LG_{0,l}`` mode with a uniform polarization; its phase
  ``e^{i l phi}`` winds ``l`` times around the axis and the beam carries an
  orbital angular momentum ``l hbar`` per photon. L. Allen, M. W. Beijersbergen,
  R. J. C. Spreeuw, J. P. Woerdman, Phys. Rev. A 45, 8185 (1992).
* Vector vortex: ``LG_{0,+m}`` and ``LG_{0,-m}`` in opposite circular
  polarizations; the field is linearly polarized at the angle ``m phi + theta0``
  (Poincare index ``m``), with a polarization singularity on the axis. ``m = 1``
  gives the radially (``theta0 = 0``) and azimuthally (``theta0 = pi/2``)
  polarized beams. C. Rosales-Guzman, B. Ndagano, A. Forbes, J. Opt. 20, 123001
  (2018); Q. Zhan, Adv. Opt. Photon. 1, 1 (2009).

Both include the first post-paraxial longitudinal field ``E_z = (i/k) div_perp E_perp``
(K. Y. Bliokh, F. Nori, Phys. Rep. 592, 1 (2015)), evaluated analytically.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..field import MultiHarmonicField
from ..grid import Grid
from ..modes import beam_radius, gouy_phase, inverse_curvature

SIGMA_PLUS = np.array([1, 1j, 0]) / np.sqrt(2)
SIGMA_MINUS = np.array([1, -1j, 0]) / np.sqrt(2)
POLARIZATIONS = {
    "linear": np.array([1, 0, 0], dtype=complex),
    "circular": SIGMA_PLUS,
}


def lg0_with_gradient(l: int, w0: float, wavelength: float, grid: Grid):
    """``LG_{0,l}`` envelope with its transverse derivatives ``(u, d_x u, d_y u)``.

    Written in Cartesian form, ``rho^|l| e^{i l phi} = (x + i s y)^|l|`` with
    ``s = sign(l)``, so nothing is singular on the axis. Normalized to a peak
    modulus of 1 at the focus.
    """
    n, s = abs(l), np.sign(l)
    k = 2 * np.pi / wavelength
    w = beam_radius(grid.z, w0, wavelength)
    q = 1 / w**2 - 0.5j * k * inverse_curvature(grid.z, w0, wavelength)
    peak = (n ** (n / 2) * np.exp(-n / 2)) if n else 1.0   # max of s^n e^{-s^2/2}, s = sqrt(2) rho / w0
    common = (w0 / w) * (np.sqrt(2) / w) ** n / peak * np.exp(-q * grid.rho**2 - 1j * (n + 1) * gouy_phase(grid.z, w0, wavelength))
    zeta = grid.x + 1j * s * grid.y
    power = zeta**n
    lower = n * zeta ** (n - 1) if n else 0
    u = common * power
    du_dx = common * (lower - 2 * q * grid.x * power)
    du_dy = common * (1j * s * lower - 2 * q * grid.y * power)
    return u, du_dx, du_dy


def _field(parts, k: float, omega: float, grid: Grid, include_carrier: bool, amplitude: float) -> MultiHarmonicField:
    """Sum of ``jones * u`` terms and their longitudinal field."""
    E = np.zeros((3, *grid.shape), dtype=complex)
    for jones, (u, du_dx, du_dy) in parts:
        E[:2] += jones[:2].reshape(2, 1, 1, 1) * u
        E[2] += 1j / k * (jones[0] * du_dx + jones[1] * du_dy)
    E *= amplitude
    if include_carrier:
        E = E * np.exp(1j * k * grid.z)
    return MultiHarmonicField(grid=grid, omega=omega, harmonics={1: E})


@dataclass
class _Beam:
    wavelength: float = 632.8e-9
    w0: float = 2.5e-6
    amplitude: float = 1.0
    include_carrier: bool = True

    @property
    def k(self) -> float:
        return 2 * np.pi / self.wavelength

    @property
    def omega(self) -> float:
        return 2 * np.pi * 299_792_458.0 / self.wavelength


@dataclass
class VortexBeam(_Beam):
    """Scalar vortex ``LG_{0,l}`` with uniform polarization (``"linear"`` along x, ``"circular"`` or Jones).

    ``amplitude`` is the peak transverse field at the focus. ``l = 0`` is the
    Gaussian beam.
    """

    l: int = 1
    polarization: str | tuple = "linear"

    @property
    def jones(self) -> np.ndarray:
        if isinstance(self.polarization, str):
            return POLARIZATIONS[self.polarization]
        p = np.array([*self.polarization, 0], dtype=complex)
        return p / np.linalg.norm(p)

    def field(self, grid: Grid) -> MultiHarmonicField:
        parts = [(self.jones, lg0_with_gradient(self.l, self.w0, self.wavelength, grid))]
        return _field(parts, self.k, self.omega, grid, self.include_carrier, self.amplitude)


@dataclass
class VectorVortexBeam(_Beam):
    """Vector vortex of order ``m``: linear polarization at the angle ``m phi + theta0``.

    ``m = 1, theta0 = 0`` is radial and ``m = 1, theta0 = pi/2`` azimuthal.
    ``amplitude`` is the peak transverse field at the focus.
    """

    m: int = 1
    theta0: float = 0.0

    def field(self, grid: Grid) -> MultiHarmonicField:
        # e^{i(m phi + theta0)} (x - iy)/sqrt2 + e^{-i(m phi + theta0)} (x + iy)/sqrt2
        #   = sqrt2 (cos(m phi + theta0), sin(m phi + theta0))
        lam, w0 = self.wavelength, self.w0
        parts = [
            (SIGMA_MINUS * np.exp(1j * self.theta0) / np.sqrt(2), lg0_with_gradient(self.m, w0, lam, grid)),
            (SIGMA_PLUS * np.exp(-1j * self.theta0) / np.sqrt(2), lg0_with_gradient(-self.m, w0, lam, grid)),
        ]
        return _field(parts, self.k, self.omega, grid, self.include_carrier, self.amplitude)
