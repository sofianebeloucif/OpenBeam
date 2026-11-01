import numpy as np
import pytest

from openbeam import GaussianBeam, Grid
from openbeam.modes import rayleigh_range

BEAM = GaussianBeam(include_carrier=False)


def test_peak_amplitude_and_waist():
    grid = Grid.transverse(extent=6 * BEAM.w0, n=301)
    E = BEAM.field(grid).harmonics[1]
    intensity = np.sum(np.abs(E[:2]) ** 2, axis=0)
    assert np.sqrt(intensity.max()) == pytest.approx(BEAM.amplitude)
    # 1/e^2 radius of the intensity is w0
    edge = Grid.from_axes(BEAM.w0, 0.0, 0.0)
    assert np.sum(np.abs(BEAM.field(edge).harmonics[1][:2]) ** 2) == pytest.approx(np.exp(-2))


def test_gouy_phase_on_axis():
    zr = rayleigh_range(BEAM.w0, BEAM.wavelength)
    E = BEAM.field(Grid.from_axes(0.0, 0.0, zr)).harmonics[1][0].item()
    assert np.angle(E) == pytest.approx(-np.pi / 4)
    assert abs(E) == pytest.approx(1 / np.sqrt(2))


@pytest.mark.parametrize("polarization", ["linear", "circular", (1, 0.5j)])
@pytest.mark.parametrize("z", [0.0, 12e-6])
def test_longitudinal_field_matches_divergence(polarization, z):
    beam = GaussianBeam(polarization=polarization, include_carrier=False)
    h = 1e-9
    x = np.linspace(-2, 2, 9) * beam.w0
    grid = Grid.from_axes(x, 0.37 * beam.w0, z)
    E = beam.field(grid).harmonics[1]
    dEx = (beam.field(Grid.from_axes(x + h, 0.37 * beam.w0, z)).harmonics[1][0]
           - beam.field(Grid.from_axes(x - h, 0.37 * beam.w0, z)).harmonics[1][0]) / (2 * h)
    dEy = (beam.field(Grid.from_axes(x, 0.37 * beam.w0 + h, z)).harmonics[1][1]
           - beam.field(Grid.from_axes(x, 0.37 * beam.w0 - h, z)).harmonics[1][1]) / (2 * h)
    np.testing.assert_allclose(E[2], 1j / beam.k * (dEx + dEy), atol=1e-6 * np.max(np.abs(E[0])))


def test_circular_polarization_rotates():
    beam = GaussianBeam(polarization="circular")
    field = beam.field(Grid.from_axes(0.0, 0.0, 0.0))
    quarter = field.real(field.period / 4)[:2].ravel()
    start = field.real(0.0)[:2].ravel()
    assert np.dot(start, quarter) == pytest.approx(0, abs=1e-12)
    assert np.linalg.norm(start) == pytest.approx(np.linalg.norm(quarter))
