import numpy as np
import pytest

from openbeam import Grid, VectorBeam

W0 = 2.5e-6


def circle(radius, z=0.0, n=721):
    phi = np.linspace(0, 2 * np.pi, n)
    return phi, Grid(radius * np.cos(phi)[:, None, None], radius * np.sin(phi)[:, None, None], np.full((n, 1, 1), z))


def test_peak_amplitude():
    grid = Grid.transverse(extent=8 * W0, n=401)
    E = VectorBeam(include_carrier=False).field(grid).harmonics[1]
    assert np.sqrt(np.max(np.sum(np.abs(E[:2]) ** 2, axis=0))) == pytest.approx(1, rel=1e-3)


@pytest.mark.parametrize("m", [1, 2, -1])
def test_polarization_angle_and_poincare_index(m):
    theta0 = 0.3
    phi, grid = circle(W0 / np.sqrt(2))
    F = VectorBeam(m=m, theta0=theta0).field(grid).real(0.0)
    angle = np.arctan2(F[1].ravel(), F[0].ravel())
    expected = m * phi + theta0
    np.testing.assert_allclose(np.cos(2 * (angle - expected)), 1, atol=1e-9)  # same axis (sign oscillates in time)
    index = (np.unwrap(2 * angle)[-1] - np.unwrap(2 * angle)[0]) / (4 * np.pi)
    assert index == pytest.approx(m, abs=1e-6)




@pytest.mark.parametrize("z", [0.0, 15e-6])
def test_longitudinal_field_matches_divergence(z):
    beam = VectorBeam(m=2, theta0=0.4, include_carrier=False)
    h = 1e-9
    x, y = np.linspace(-2, 2, 9) * W0, 0.37 * W0
    E = beam.field(Grid.from_axes(x, y, z)).harmonics[1]
    dEx = (beam.field(Grid.from_axes(x + h, y, z)).harmonics[1][0] - beam.field(Grid.from_axes(x - h, y, z)).harmonics[1][0]) / (2 * h)
    dEy = (beam.field(Grid.from_axes(x, y + h, z)).harmonics[1][1] - beam.field(Grid.from_axes(x, y - h, z)).harmonics[1][1]) / (2 * h)
    np.testing.assert_allclose(E[2], 1j / beam.k * (dEx + dEy), atol=1e-6 * np.max(np.abs(E[:2])))


def test_azimuthal_beam_has_no_longitudinal_field():
    E = VectorBeam(theta0=np.pi / 2, include_carrier=False).field(Grid.transverse(4 * W0, 41, z=10e-6)).harmonics[1]
    assert np.max(np.abs(E[2])) < 1e-12 * np.max(np.abs(E[:2]))
