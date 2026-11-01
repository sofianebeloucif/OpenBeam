import numpy as np
import pytest

from openbeam import ChiralVectorBeam, GaussianBeam, Grid, VectorVortexBeam, VortexBeam
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


def test_l0_is_the_gaussian_beam():
    grid = Grid.volume(extent=6 * W0, n=9, z_min=-10e-6, z_max=10e-6, nz=3)
    for pol in ("linear", "circular"):
        a = VortexBeam(l=0, polarization=pol).field(grid).harmonics[1]
        b = GaussianBeam(polarization=pol).field(grid).harmonics[1]
        np.testing.assert_allclose(a, b, atol=1e-12)


@pytest.mark.parametrize("beam", [VortexBeam(l=2, polarization="circular", include_carrier=False),
                                  VectorVortexBeam(m=2, theta0=0.4, include_carrier=False)])
@pytest.mark.parametrize("z", [0.0, 15e-6])
def test_longitudinal_field_matches_divergence(beam, z):
    h = 1e-9
    x, y = np.linspace(-2, 2, 9) * W0, 0.37 * W0
    E = beam.field(Grid.from_axes(x, y, z)).harmonics[1]
    dEx = (beam.field(Grid.from_axes(x + h, y, z)).harmonics[1][0] - beam.field(Grid.from_axes(x - h, y, z)).harmonics[1][0]) / (2 * h)
    dEy = (beam.field(Grid.from_axes(x, y + h, z)).harmonics[1][1] - beam.field(Grid.from_axes(x, y - h, z)).harmonics[1][1]) / (2 * h)
    np.testing.assert_allclose(E[2], 1j / beam.k * (dEx + dEy), atol=1e-6 * np.max(np.abs(E[:2])))


@pytest.mark.parametrize("m", [1, 2, -1])
def test_vector_vortex_polarization_angle_and_poincare_index(m):
    theta0 = 0.3
    phi, grid = circle(W0 / np.sqrt(2))
    F = VectorVortexBeam(m=m, theta0=theta0).field(grid).real(0.0)
    angle = np.arctan2(F[1].ravel(), F[0].ravel())
    expected = m * phi + theta0
    np.testing.assert_allclose(np.cos(2 * (angle - expected)), 1, atol=1e-9)  # same axis (sign oscillates in time)
    index = (np.unwrap(2 * angle)[-1] - np.unwrap(2 * angle)[0]) / (4 * np.pi)
    assert index == pytest.approx(m, abs=1e-6)


def test_radial_vector_vortex_matches_the_chiral_beam_fundamental():
    chiral = ChiralVectorBeam(include_carrier=False)
    radial = VectorVortexBeam(wavelength=chiral.wavelength, w0=chiral.w_omega, m=1, include_carrier=False)
    grid = Grid.volume(extent=6 * chiral.w_omega, n=11, z_min=-20e-6, z_max=20e-6, nz=3)
    expected = chiral.radial_component(grid) + chiral.longitudinal_component(grid)
    np.testing.assert_allclose(radial.field(grid).harmonics[1], expected, atol=1e-12)
