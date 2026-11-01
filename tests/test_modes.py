import numpy as np
import pytest

from openbeam.grid import Grid
from openbeam.modes import beam_radius, gouy_phase, laguerre_gauss, rayleigh_range

WAVELENGTH = 639e-9
W0 = 2.5e-6


@pytest.mark.parametrize("p,l", [(0, 0), (0, 1), (0, -1), (1, 2), (2, -3)])
@pytest.mark.parametrize("z", [0.0, 20e-6])
def test_lg_is_normalized(p, l, z):
    grid = Grid.transverse(extent=12 * W0, n=401, z=z)
    u = laguerre_gauss(p, l, W0, WAVELENGTH, grid.rho, grid.phi, grid.z)
    power = np.sum(np.abs(u) ** 2) * grid.dx * grid.dy
    assert power == pytest.approx(1.0, rel=1e-3)


def test_beam_radius_and_gouy():
    zr = rayleigh_range(W0, WAVELENGTH)
    assert zr == pytest.approx(np.pi * W0**2 / WAVELENGTH)
    assert beam_radius(zr, W0, WAVELENGTH) == pytest.approx(np.sqrt(2) * W0)
    assert gouy_phase(zr, W0, WAVELENGTH) == pytest.approx(np.pi / 4)


def test_lg_carries_orbital_phase():
    grid = Grid.transverse(extent=4 * W0, n=64)
    u = laguerre_gauss(0, 1, W0, WAVELENGTH, grid.rho, grid.phi, grid.z)
    mask = grid.rho > 0.3 * W0
    np.testing.assert_allclose(np.angle(u[mask] * np.exp(-1j * grid.phi[mask])), 0, atol=1e-12)
