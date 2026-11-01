import numpy as np
import pytest
from scipy.special import jn_zeros, jv

from openbeam import BesselBeam, Grid

BEAM = BesselBeam(include_carrier=False)


@pytest.mark.parametrize("n", [0, 1, 2])
def test_focal_plane_is_a_bessel_function_under_a_gaussian(n):
    beam = BesselBeam(n=n, include_carrier=False)
    grid = Grid.transverse(extent=4 * beam.w0, n=41)
    E = beam.field(grid).harmonics[1][0]
    expected = jv(n, beam.kr * grid.rho) * np.exp(1j * n * grid.phi) * np.exp(-(grid.rho / beam.w0) ** 2)
    mask = np.abs(expected) > 1e-6
    ratio = E[mask] / expected[mask]
    np.testing.assert_allclose(ratio, ratio[0], rtol=1e-9)


@pytest.mark.parametrize("n", [0, 1])
def test_peak_amplitude(n):
    grid = Grid.transverse(extent=3 * BEAM.w0, n=601)
    E = BesselBeam(n=n, include_carrier=False).field(grid).harmonics[1]
    assert np.sqrt(np.max(np.sum(np.abs(E[:2]) ** 2, axis=0))) == pytest.approx(1, rel=2e-3)


def test_on_axis_amplitude_decays_over_the_nondiffracting_range():
    """|E(0, z)| / |E(0, 0)| = exp(-(z / z_max)^2 / (1 + (z / z_R)^2)) / |1 + i z / z_R| for n = 0."""
    zmax = BEAM.max_range
    z = np.array([0.0, 0.3, 0.7, 1.2]) * zmax
    E = np.abs(BEAM.field(Grid.from_axes(0.0, 0.0, z)).harmonics[1][0].ravel())
    zr = np.pi * BEAM.w0**2 / BEAM.wavelength
    expected = np.exp(-((z / zmax) ** 2) / (1 + (z / zr) ** 2)) / np.abs(1 + 1j * z / zr)
    np.testing.assert_allclose(E / E[0], expected, rtol=1e-9)


def test_core_does_not_spread():
    """The first zero of the n = 0 core stays at 2.405 / k_r inside the non-diffracting range."""
    x = np.linspace(0, 2 * jn_zeros(0, 1)[0] / BEAM.kr, 4001)
    for z in (0.0, 0.5 * BEAM.max_range):
        I = np.abs(BEAM.field(Grid.from_axes(x, 0.0, z)).harmonics[1][0].ravel()) ** 2
        first_min = x[np.argmax(np.diff(I) > 0)]
        assert first_min == pytest.approx(jn_zeros(0, 1)[0] / BEAM.kr, rel=0.02)


@pytest.mark.parametrize("beam", [BesselBeam(n=0, include_carrier=False),
                                  BesselBeam(n=1, polarization="circular", include_carrier=False)])
@pytest.mark.parametrize("z", [0.0, 25e-6])
def test_longitudinal_field_matches_divergence(beam, z):
    h = 1e-10
    x, y = np.linspace(-2, 2, 9) * 2.4 / beam.kr, 0.37 / beam.kr
    E = beam.field(Grid.from_axes(x, y, z)).harmonics[1]
    dEx = (beam.field(Grid.from_axes(x + h, y, z)).harmonics[1][0] - beam.field(Grid.from_axes(x - h, y, z)).harmonics[1][0]) / (2 * h)
    dEy = (beam.field(Grid.from_axes(x, y + h, z)).harmonics[1][1] - beam.field(Grid.from_axes(x, y - h, z)).harmonics[1][1]) / (2 * h)
    np.testing.assert_allclose(E[2], 1j / beam.k * (dEx + dEy), atol=1e-6 * np.max(np.abs(E[:2])))


def test_order_one_phase_winds_once():
    phi = np.linspace(0, 2 * np.pi, 721)
    r = 1.84 / BEAM.kr
    grid = Grid(r * np.cos(phi)[:, None, None], r * np.sin(phi)[:, None, None], np.zeros((phi.size, 1, 1)))
    E = BesselBeam(n=1, include_carrier=False).field(grid).harmonics[1][0].ravel()
    assert (np.unwrap(np.angle(E))[-1] - np.angle(E[0])) / (2 * np.pi) == pytest.approx(1, abs=1e-6)
