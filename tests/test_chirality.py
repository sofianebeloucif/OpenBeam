import numpy as np
import pytest

from openbeam import ChiralVectorBeam, GaussianBeam, Grid, chiral_correlation

RING = ChiralVectorBeam().w_omega / np.sqrt(2)


def ring_point(phi=0.0, z=0.0):
    return Grid.from_axes(RING * np.cos(phi), RING * np.sin(phi), z)


def test_closed_form_on_the_x_axis():
    """At phi = 0, E(w) = (E_x, 0, E_z) and E(2w) = (0, E_y, 0): the definition reduces to
    h5 = E_y* (E_z* E_x - E_x* E_z) (E_x^2 + E_z^2)."""
    beam = ChiralVectorBeam(include_carrier=False)
    field = beam.field(ring_point())
    (Ex, _, Ez), (_, Ey, _) = field.harmonics[1][:, 0, 0, 0], field.harmonics[2][:, 0, 0, 0]
    expected = np.conj(Ey) * (np.conj(Ez) * Ex - np.conj(Ex) * Ez) * (Ex**2 + Ez**2)
    assert chiral_correlation(field).item() == pytest.approx(expected)
    assert abs(expected) > 0


def test_modulus_independent_of_two_colour_phase_and_pi_shift_flips_sign():
    h = [chiral_correlation(ChiralVectorBeam(psi_2w=psi).field(ring_point())).item() for psi in (0.0, 0.7, np.pi)]
    assert abs(h[0]) > 0
    assert abs(h[1]) == pytest.approx(abs(h[0]))
    assert h[2] == pytest.approx(-h[0])  # equivalent to exchanging the enantiomers


def test_azimuthally_symmetric_on_the_ring():
    h = [chiral_correlation(ChiralVectorBeam().field(ring_point(phi))).item() for phi in np.linspace(0, 2 * np.pi, 7)]
    np.testing.assert_allclose(h, h[0], rtol=1e-9)


def test_requires_two_colours():
    with pytest.raises(ValueError):
        chiral_correlation(GaussianBeam().field(ring_point()))


def test_two_colour_beam_reproduces_the_chiral_vector_beam():
    from openbeam import TwoColourBeam, VectorVortexBeam

    chiral = ChiralVectorBeam()
    two = TwoColourBeam(
        VectorVortexBeam(wavelength=chiral.wavelength, w0=chiral.w_omega, m=1, theta0=0.0),
        VectorVortexBeam(wavelength=chiral.wavelength / 2, w0=chiral.w_2omega, m=1, theta0=np.pi / 2),
        intensity_ratio=chiral.intensity_ratio, psi_2w=chiral.psi_2w,
    )
    grid = Grid.volume(extent=4 * chiral.w_omega, n=9, z_min=-10e-6, z_max=10e-6, nz=3)
    a, b = chiral.field(grid), two.field(grid)
    for n in (1, 2):
        np.testing.assert_allclose(a.harmonics[n], b.harmonics[n], atol=1e-12)


def test_two_colour_beam_requires_half_wavelength():
    from openbeam import TwoColourBeam

    with pytest.raises(ValueError):
        TwoColourBeam(GaussianBeam(), GaussianBeam())
