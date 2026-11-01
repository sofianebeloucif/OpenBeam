"""Two-colour chiral vector beam: two vector vortex beams whose sum is locally chiral.

Beam proposed by A. Rodriguez et al., "Chiral Vector Beams for Topological
Enantio-Sensitive Imaging", arXiv:2610.17111 (2026). Definitions it builds on:

* Vector vortex beams: beams with a spatially inhomogeneous polarization and a
  polarization singularity on the axis, built from Laguerre-Gauss vortices of
  charges +l and -l in opposite circular polarizations; for l = 1 they are the
  radially and azimuthally polarized (cylindrical vector) beams.
  C. Rosales-Guzman, B. Ndagano, A. Forbes, J. Opt. 20, 123001 (2018);
  Q. Zhan, Adv. Opt. Photon. 1, 1 (2009).
* Locally chiral light: at each point the tip of the electric field draws a
  chiral 3D Lissajous figure during one cycle; measured by the chiral
  correlation function h5 (``openbeam.chiral_correlation``).
  D. Ayuso et al., Nat. Photon. 13, 866 (2019), arXiv:1809.01632;
  N. Mayer et al., Nat. Photon. (2024), doi:10.1038/s41566-024-01499-8.
* Longitudinal field of a tightly focused beam, first post-paraxial order of
  ``div E = 0``: ``E_z = (i/k) div_perp E_perp``. K. Y. Bliokh, F. Nori, Phys.
  Rep. 592, 1 (2015); strong for radial polarization: R. Dorn, S. Quabis,
  G. Leuchs, PRL 91, 233901 (2003).

The beam:

* fundamental ``omega``: tightly focused **radially** polarized vector vortex
  beam, ``LG_{0,+1}`` and ``LG_{0,-1}`` in opposite circular polarizations,
  with its longitudinal component ``E_z = (i/k) (1/rho) d_rho(rho E_rho)``;
* second harmonic ``2 omega``: **azimuthally** polarized vector vortex beam,
  delayed by ``psi_2w``, without longitudinal component.

Conventions: phasors ``e^{-i w t}``, standard basis ``e_rho = (cos phi, sin phi)``,
``e_phi = (-sin phi, cos phi)``; the 2w field is ``E_phi = A_2w R_2w(rho, z)
e^{i psi_2w} e_phi``, so ``psi_2w`` is the phase of the azimuthal field relative
to the radial one at the focus. The modulus of h5 does not depend on
``psi_2w``; ``psi_2w -> psi_2w + pi`` flips its sign.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..field import MultiHarmonicField
from ..grid import Grid
from ..modes import beam_radius, gouy_phase, inverse_curvature, laguerre_gauss

SIGMA_PLUS = np.array([1, 1j, 0]) / np.sqrt(2)
SIGMA_MINUS = np.array([1, -1j, 0]) / np.sqrt(2)


def _lg1_peak(w0: float) -> float:
    """Peak of ``|LG_{0,+-1}|`` at the focus, reached at ``rho = w0 / sqrt(2)``."""
    return np.sqrt(2 / np.pi) / w0 * np.exp(-0.5)


def _vector(components_x_y_z: np.ndarray, scalar: np.ndarray) -> np.ndarray:
    return components_x_y_z.reshape(3, 1, 1, 1) * scalar


@dataclass
class ChiralVectorBeam:
    """Radial ``omega`` + azimuthal ``2 omega`` vector vortex beams.

    ``amplitude`` is the peak transverse field of the ``omega`` beam at the
    focus; the ``2 omega`` peak is ``amplitude * sqrt(intensity_ratio)``.
    Default parameter values from Rodriguez et al. (2026).
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

    def radial_component(self, grid: Grid) -> np.ndarray:
        """Transverse ``omega`` phasor ``(x, y, 0)`` from two circular vortices."""
        lam, w0 = self.wavelength, self.w_omega
        a = self.amplitude / _lg1_peak(w0) / np.sqrt(2)
        u_plus = laguerre_gauss(0, +1, w0, lam, grid.rho, grid.phi, grid.z)
        u_minus = laguerre_gauss(0, -1, w0, lam, grid.rho, grid.phi, grid.z)
        # e^{+i phi} (x - iy) + e^{-i phi} (x + iy) = 2 e_rho
        return a * (_vector(SIGMA_MINUS, u_plus) + _vector(SIGMA_PLUS, u_minus))

    def longitudinal_component(self, grid: Grid) -> np.ndarray:
        """``E_z = (i/k) (1/rho) d_rho(rho E_rho)`` (first post-paraxial order), evaluated analytically."""
        lam, w0, k = self.wavelength, self.w_omega, self.k
        w = beam_radius(grid.z, w0, lam)
        q = 1 / w**2 - 0.5j * k * inverse_curvature(grid.z, w0, lam)
        # E_rho = g * rho with g holding the Gaussian envelope and the l=1 Gouy phase
        g = (
            self.amplitude / _lg1_peak(w0)
            * np.sqrt(2 / np.pi) / w * np.sqrt(2) / w
            * np.exp(-q * grid.rho**2 - 2j * gouy_phase(grid.z, w0, lam))
        )
        Ez = 1j / k * g * (2 - 2 * q * grid.rho**2)
        return _vector(np.array([0, 0, 1]), Ez)

    def azimuthal_component(self, grid: Grid) -> np.ndarray:
        """Transverse ``2 omega`` phasor, azimuthally polarized."""
        lam, w0 = self.wavelength / 2, self.w_2omega
        a = self.amplitude * np.sqrt(self.intensity_ratio) / _lg1_peak(w0) / np.sqrt(2)
        u_plus = laguerre_gauss(0, +1, w0, lam, grid.rho, grid.phi, grid.z)
        u_minus = laguerre_gauss(0, -1, w0, lam, grid.rho, grid.phi, grid.z)
        # i [e^{+i phi} (x - iy) - e^{-i phi} (x + iy)] = 2 e_phi
        return 1j * a * np.exp(1j * self.psi_2w) * (_vector(SIGMA_MINUS, u_plus) - _vector(SIGMA_PLUS, u_minus))

    def field(self, grid: Grid) -> MultiHarmonicField:
        E1 = self.radial_component(grid) + self.longitudinal_component(grid)
        E2 = self.azimuthal_component(grid)
        if self.include_carrier:
            E1 = E1 * np.exp(1j * self.k * grid.z)
            E2 = E2 * np.exp(2j * self.k * grid.z)
        return MultiHarmonicField(grid=grid, omega=self.omega, harmonics={1: E1, 2: E2})
