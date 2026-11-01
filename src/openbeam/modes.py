"""Paraxial scalar beam modes.

Conventions: monochromatic fields are complex phasors with time dependence
``exp(-i w t)``, propagating towards +z as ``u(rho, phi, z) exp(i k z)``.
The functions below return the slowly varying envelope ``u``; the carrier
``exp(i k z)`` is applied by the beam that uses them.
"""

from __future__ import annotations

from math import factorial

import numpy as np
from scipy.special import genlaguerre


def rayleigh_range(w0: float, wavelength: float) -> float:
    return np.pi * w0**2 / wavelength


def beam_radius(z, w0: float, wavelength: float):
    """Gaussian beam radius ``w(z)``."""
    return w0 * np.sqrt(1 + (z / rayleigh_range(w0, wavelength)) ** 2)


def inverse_curvature(z, w0: float, wavelength: float):
    """``1 / R(z)``, which is finite (zero) at the focus."""
    zr = rayleigh_range(w0, wavelength)
    return z / (z**2 + zr**2)


def gouy_phase(z, w0: float, wavelength: float):
    """Gouy phase ``arctan(z / z_R)`` of the fundamental Gaussian mode."""
    return np.arctan(z / rayleigh_range(w0, wavelength))


def laguerre_gauss(p: int, l: int, w0: float, wavelength: float, rho, phi, z):
    """Power-normalized Laguerre-Gauss envelope ``LG_{p,l}(rho, phi, z)``.

    ``integral |LG|^2 dx dy = 1`` in every transverse plane.
    """
    k = 2 * np.pi / wavelength
    w = beam_radius(z, w0, wavelength)
    s = np.sqrt(2) * rho / w
    norm = np.sqrt(2 * factorial(p) / (np.pi * factorial(p + abs(l))))
    amplitude = norm / w * s ** abs(l) * genlaguerre(p, abs(l))(s**2) * np.exp(-((rho / w) ** 2))
    phase = (
        l * phi
        + k * rho**2 / 2 * inverse_curvature(z, w0, wavelength)
        - (2 * p + abs(l) + 1) * gouy_phase(z, w0, wavelength)
    )
    return amplitude * np.exp(1j * phase)
