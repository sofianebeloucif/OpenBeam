import numpy as np
import pytest

from openbeam import ChiralVectorBeam, Grid

BEAM = ChiralVectorBeam(include_carrier=False)


def harmonics(grid):
    field = BEAM.field(grid)
    return field.harmonics[1], field.harmonics[2]


def _radial_unit(grid):
    return np.stack([np.cos(grid.phi), np.sin(grid.phi)])


def _azimuthal_unit(grid):
    return np.stack([-np.sin(grid.phi), np.cos(grid.phi)])


@pytest.mark.parametrize("z", [0.0, 15e-6])
def test_radial_at_omega_and_azimuthal_at_2omega(z):
    grid = Grid.transverse(extent=4 * BEAM.w_omega, n=60, z=z)
    E1, E2 = harmonics(grid)
    assert np.max(np.abs(np.sum(E1[:2] * _azimuthal_unit(grid), axis=0))) < 1e-12 * np.max(np.abs(E1))
    assert np.max(np.abs(np.sum(E2[:2] * _radial_unit(grid), axis=0))) < 1e-12 * np.max(np.abs(E2))
    assert np.max(np.abs(E2[2])) < 1e-12 * np.max(np.abs(E2))  # the azimuthal beam has no longitudinal field


def test_peak_amplitudes_and_intensity_ratio():
    grid = Grid.transverse(extent=4 * BEAM.w_2omega, n=801)
    E1, E2 = harmonics(grid)
    peak1 = np.max(np.linalg.norm(E1[:2], axis=0))
    peak2 = np.max(np.linalg.norm(E2[:2], axis=0))
    assert peak1 == pytest.approx(BEAM.amplitude, rel=1e-4)
    assert (peak2 / peak1) ** 2 == pytest.approx(BEAM.intensity_ratio, rel=1e-3)


@pytest.mark.parametrize("z", [0.0, -10e-6, 25e-6])
def test_longitudinal_field_matches_divergence_relation(z):
    """E_z = (i/k) (1/rho) d_rho(rho E_rho), checked by finite differences along phi = 0."""
    rho = np.linspace(0.2, 3, 2001) * BEAM.w_omega
    E1, _ = harmonics(Grid.from_axes(rho, 0.0, z))
    E_rho, Ez = E1[0].ravel(), E1[2].ravel()
    Ez_numeric = 1j / BEAM.k * np.gradient(rho * E_rho, rho) / rho
    np.testing.assert_allclose(Ez[5:-5], Ez_numeric[5:-5], atol=1e-5 * np.max(np.abs(Ez)))


def test_longitudinal_field_at_focus():
    """Central spot, node at rho = w, then a ring; pi/2 phase shift with respect to E_rho."""
    E1, _ = harmonics(Grid.from_axes(np.array([0.3, 1.0, 1.7]) * BEAM.w_omega, 0.0, 0.0))
    E_rho, Ez = E1[0].ravel(), E1[2].ravel()
    assert abs(Ez[1]) < 1e-12 * abs(Ez[0])
    assert np.sign(Ez[0].imag) == -np.sign(Ez[2].imag)
    np.testing.assert_allclose(np.real(Ez / E_rho)[[0, 2]], 0, atol=1e-12)


def test_field_is_periodic():
    beam = ChiralVectorBeam()
    field = beam.field(Grid.volume(extent=6e-6, n=11, z_min=-1e-6, z_max=1e-6, nz=5))
    np.testing.assert_allclose(field.real(0.3e-15), field.real(0.3e-15 + field.period), atol=1e-10)
    averaged = np.mean([field.intensity(t) for t in np.linspace(0, field.period, 64, endpoint=False)], axis=0)
    np.testing.assert_allclose(averaged, field.time_averaged_intensity(), rtol=1e-10)


def test_poincare_index_is_one():
    """Polarization singularity of the radial beam: the field direction winds once around the axis."""
    phi = np.linspace(0, 2 * np.pi, 721)
    r = BEAM.w_omega / np.sqrt(2)
    grid = Grid(r * np.cos(phi)[:, None, None], r * np.sin(phi)[:, None, None], np.zeros((phi.size, 1, 1)))
    F = BEAM.field(grid).real(0.0)
    theta = np.unwrap(np.arctan2(F[1].ravel(), F[0].ravel()))
    assert (theta[-1] - theta[0]) / (2 * np.pi) == pytest.approx(1.0, abs=1e-6)
