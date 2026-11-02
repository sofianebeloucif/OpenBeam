"""Building blocks shared by the beams: base parameters, polarizations, LG envelopes, field assembly.

All beams are paraxial modes with their first post-paraxial longitudinal field,
``E_z = (i/k) div_perp E_perp`` (K. Y. Bliokh, F. Nori, Phys. Rep. 592, 1 (2015)),
evaluated analytically from the transverse derivatives of their envelopes.
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


@dataclass
class Beam:
    """Monochromatic beam: wavelength, waist, peak transverse field at the focus, carrier ``e^{ikz}`` or not."""

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


def jones_vector(polarization: str | tuple) -> np.ndarray:
    """``"linear"`` (along x), ``"circular"`` or a Jones vector ``(p_x, p_y)``, as a normalized 3-vector."""
    if isinstance(polarization, str):
        return POLARIZATIONS[polarization]
    p = np.array([*polarization, 0], dtype=complex)
    return p / np.linalg.norm(p)


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


def field_from_terms(beam: Beam, terms, grid: Grid) -> MultiHarmonicField:
    """Field of ``sum jones * u`` over ``terms = [(jones, (u, d_x u, d_y u)), ...]``, with its longitudinal part."""
    E = np.zeros((3, *grid.shape), dtype=complex)
    for jones, (u, du_dx, du_dy) in terms:
        E[:2] += jones[:2].reshape(2, 1, 1, 1) * u
        E[2] += 1j / beam.k * (jones[0] * du_dx + jones[1] * du_dy)
    E *= beam.amplitude
    if beam.include_carrier:
        E = E * np.exp(1j * beam.k * grid.z)
    return MultiHarmonicField(grid=grid, omega=beam.omega, harmonics={1: E})
