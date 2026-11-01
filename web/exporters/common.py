"""Shared export of a beam for the component viewers (``web/src/lib/component-viewer.js``).

For each variant of a beam the viewer receives, on the same arrow anchors
(the centre plus rings at ``RINGS`` times the beam radius):

* ``fixed``: complex phasors of every harmonic at the focus, so the page can
  compute ``Re[E_n e^{-i n w t}]`` at any time;
* ``moving``: for each position of a travelling wavefront of the fundamental,
  the real field of every harmonic at the points of that front, at the time
  the front is there.

Values are in units of the beam amplitude; positions in µm.
"""

from __future__ import annotations

import numpy as np

from openbeam import Grid
from openbeam.modes import beam_radius, gouy_phase, inverse_curvature, rayleigh_range

UM = 1e-6
RINGS = (0.35, 0.7, 1.05, 1.4)   # in units of w(z)
AZIMUTHS = 12
N_FRONTS = 241
TAU0 = np.pi / 4                 # phase of the fundamental on the travelling front


def r(a, digits=5):
    return np.round(np.asarray(a, float), digits).tolist()


def anchors(w: float):
    rho = np.concatenate([[0.0], np.repeat(np.asarray(RINGS) * w, AZIMUTHS)])
    phi = np.concatenate([[0.0], np.tile(np.linspace(0, 2 * np.pi, AZIMUTHS, endpoint=False), len(RINGS))])
    return rho, phi


class Fronts:
    """Equal-phase surfaces of the fundamental: ``k z + k rho^2 / 2R(z) - gouy_order * Gouy(z)``."""

    def __init__(self, wavelength: float, w0: float, gouy_order: int):
        self.wavelength, self.w0, self.gouy_order = wavelength, w0, gouy_order
        self.k = 2 * np.pi / wavelength

    def phase(self, rho, z):
        lam, w0 = self.wavelength, self.w0
        return (self.k * z + self.k * rho**2 / 2 * inverse_curvature(z, w0, lam)
                - self.gouy_order * gouy_phase(z, w0, lam))


def field_at(beam, x, y, z):
    field = beam.field(Grid(*(np.asarray(c, float).reshape(-1, 1, 1) for c in (x, y, z))))
    return {n: E[:, :, 0, 0] for n, E in field.harmonics.items()}, field.omega


def fixed(beam, w0: float) -> dict:
    rho, phi = anchors(w0)
    x, y = rho * np.cos(phi), rho * np.sin(phi)
    harmonics, _ = field_at(beam, x, y, np.zeros_like(x))
    return {
        "points": r(np.column_stack([x, y, np.zeros_like(x)]) / UM, 4),
        "harmonics": {str(n): {"re": r(E.real.T), "im": r(E.imag.T)} for n, E in harmonics.items()},
    }


def moving(beam, fronts: Fronts, z_range) -> list[dict]:
    frames = []
    for z_front in np.linspace(*z_range, N_FRONTS):
        w = beam_radius(z_front, fronts.w0, fronts.wavelength)
        rho, phi = anchors(w)
        target = fronts.phase(0.0, z_front)
        z = z_front + (target - fronts.phase(rho, z_front)) / fronts.k
        x, y = rho * np.cos(phi), rho * np.sin(phi)
        harmonics, omega = field_at(beam, x, y, z)
        t = (target - TAU0) / omega
        frames.append({
            "z": round(z_front / UM, 4),
            "w": round(w / UM, 4),
            "points": r(np.column_stack([x, y, z]) / UM, 4),
            "harmonics": {str(n): r(np.real(E * np.exp(-1j * n * omega * t)).T) for n, E in harmonics.items()},
        })
    return frames


def export_variants(variants: dict, wavelength: float, w0: float, gouy_order: int, omega: float,
                    z_range_zr=(-1.5, 1.5)) -> dict:
    """``variants`` maps a variant id to a beam object exposing ``field(grid)``."""
    zr = rayleigh_range(w0, wavelength)
    fronts = Fronts(wavelength, w0, gouy_order)
    z_range = tuple(c * zr for c in z_range_zr)
    return {
        "wavelength_um": wavelength / UM,
        "w0_um": w0 / UM,
        "zr_um": zr / UM,
        "period_fs": 2 * np.pi / omega / 1e-15,
        "tau0": TAU0,
        "variants": {vid: {"fixed": fixed(beam, w0), "moving": moving(beam, fronts, z_range)}
                     for vid, beam in variants.items()},
    }
