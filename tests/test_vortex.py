import numpy as np
import pytest

from openbeam import Grid, VortexBeam
from openbeam.modes import laguerre_gauss

W0 = 2.5e-6


def circle(radius, z=0.0, n=721):
    phi = np.linspace(0, 2 * np.pi, n)
    return phi, Grid(radius * np.cos(phi)[:, None, None], radius * np.sin(phi)[:, None, None], np.full((n, 1, 1), z))


@pytest.mark.parametrize("l", [0, 1, -2, 3])
def test_peak_amplitude(l):
    grid = Grid.transverse(extent=8 * W0, n=401)
    E = VortexBeam(l=l, include_carrier=False).field(grid).harmonics[1]
    assert np.sqrt(np.max(np.sum(np.abs(E[:2]) ** 2, axis=0))) == pytest.approx(1, rel=1e-3)


@pytest.mark.parametrize("l", [1, -2, 3])
@pytest.mark.parametrize("z", [0.0, 20e-6])
def test_scalar_vortex_is_an_lg_mode(l, z):
    """Same shape and phase as the power-normalized LG_{0,l} of openbeam.modes."""
    beam = VortexBeam(l=l, include_carrier=False)
    grid = Grid.transverse(extent=4 * W0, n=41, z=z)
    E = beam.field(grid).harmonics[1][0]
    lg = laguerre_gauss(0, l, W0, beam.wavelength, grid.rho, grid.phi, grid.z)
    ratio = E[np.abs(lg) > 1e-3 * np.abs(lg).max()] / lg[np.abs(lg) > 1e-3 * np.abs(lg).max()]
    np.testing.assert_allclose(ratio, ratio[0], rtol=1e-9)


@pytest.mark.parametrize("l", [1, -1, 2])
def test_phase_winds_l_times(l):
    phi, grid = circle(W0)
    E = VortexBeam(l=l, include_carrier=False).field(grid).harmonics[1][0].ravel()
    winding = (np.unwrap(np.angle(E))[-1] - np.angle(E[0])) / (2 * np.pi)
    assert winding == pytest.approx(l, abs=1e-6)


@pytest.mark.parametrize("beam", [VortexBeam(l=2, polarization="circular", include_carrier=False),
                                  VortexBeam(l=-1, include_carrier=False)])
@pytest.mark.parametrize("z", [0.0, 15e-6])
def test_longitudinal_field_matches_divergence(beam, z):
    h = 1e-9
    x, y = np.linspace(-2, 2, 9) * W0, 0.37 * W0
    E = beam.field(Grid.from_axes(x, y, z)).harmonics[1]
    dEx = (beam.field(Grid.from_axes(x + h, y, z)).harmonics[1][0] - beam.field(Grid.from_axes(x - h, y, z)).harmonics[1][0]) / (2 * h)
    dEy = (beam.field(Grid.from_axes(x, y + h, z)).harmonics[1][1] - beam.field(Grid.from_axes(x, y - h, z)).harmonics[1][1]) / (2 * h)
    np.testing.assert_allclose(E[2], 1j / beam.k * (dEx + dEy), atol=1e-6 * np.max(np.abs(E[:2])))
