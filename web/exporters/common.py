"""Shared export of a beam for the component viewers (``web/src/lib/component-viewer.js``).

For each variant of a beam the viewer receives, on the same arrow anchors
(the centre plus rings at ``RINGS`` times the beam radius):

* ``fixed``: complex phasors of every harmonic at the focus, so the page can
  compute ``Re[E_n e^{-i n w t}]`` at any time;
* ``moving``: for each position of a travelling wavefront of the fundamental,
  the real field of every harmonic at the points of that front, at the time
  the front is there.

Both also carry ``profile``: the cycle-averaged intensity along a radius, at
``PROFILE_POINTS`` points from 0 to ``PROFILE_EXTENT`` times the beam scale,
normalized to its maximum at the focus (drawn as the wavefront disc).

Values are in units of the beam amplitude; positions in µm.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from openbeam import Grid
from openbeam.modes import beam_radius, gouy_phase, inverse_curvature, rayleigh_range

UM = 1e-6
RINGS = (0.35, 0.7, 1.05, 1.4)   # in units of w(z)
AZIMUTHS = 12
N_FRONTS = 241
PROFILE_EXTENT = 1.7             # disc radius, in units of the beam scale (as web/src/lib/scene.js)
PROFILE_POINTS = 41
TAU0 = np.pi / 4                 # phase of the fundamental on the travelling front


def r(a, digits=5):
    return np.round(np.asarray(a, float), digits).tolist()


def anchors(w: float):
    rho = np.concatenate([[0.0], np.repeat(np.asarray(RINGS) * w, AZIMUTHS)])
    phi = np.concatenate([[0.0], np.tile(np.linspace(0, 2 * np.pi, AZIMUTHS, endpoint=False), len(RINGS))])
    return rho, phi


@dataclass
class Variant:
    """A beam (exposing ``field(grid)``) and the phase of its fundamental, which defines its wavefronts.

    By default the phase of a Gaussian-like mode, ``k z + k rho^2 / 2R(z) - gouy_order Gouy(z) + helicity phi``
    (``helicity = l`` for a scalar vortex, whose wavefront is a helicoid; 0 when the polarization, not the
    phase, winds around the axis). ``phase(rho, z, phi)`` with its axial wavenumber ``k_axial`` replaces it
    for other beams. ``scale(z)`` is the transverse size used for the arrow rings and the disc (default:
    the Gaussian radius ``w(z)``).
    """

    beam: object
    gouy_order: int = 1
    helicity: int = 0
    phase: Callable | None = None
    k_axial: float | None = None
    scale: Callable | None = None


class Fronts:
    def __init__(self, wavelength: float, w0: float, variant: Variant):
        self.wavelength, self.w0, self.variant = wavelength, w0, variant
        self.k = variant.k_axial or 2 * np.pi / wavelength

    def phase(self, rho, z, phi=0.0):
        if self.variant.phase is not None:
            return self.variant.phase(rho, z, phi)
        lam, w0, v = self.wavelength, self.w0, self.variant
        return (self.k * z + self.k * rho**2 / 2 * inverse_curvature(z, w0, lam)
                - v.gouy_order * gouy_phase(z, w0, lam) + v.helicity * phi)

    def scale(self, z):
        if self.variant.scale is not None:
            return self.variant.scale(z)
        return beam_radius(z, self.w0, self.wavelength)


def field_at(beam, x, y, z):
    field = beam.field(Grid(*(np.asarray(c, float).reshape(-1, 1, 1) for c in (x, y, z))))
    return {n: E[:, :, 0, 0] for n, E in field.harmonics.items()}, field.omega


def intensity_profile(beam, scale: float, z: float) -> np.ndarray:
    """Cycle-averaged intensity along x at ``z``, sampled over the disc radius."""
    x = np.linspace(0, PROFILE_EXTENT * scale, PROFILE_POINTS)
    harmonics, _ = field_at(beam, x, np.zeros_like(x), np.full_like(x, z))
    return sum(0.5 * np.sum(np.abs(E) ** 2, axis=0) for E in harmonics.values())


def fixed(beam, fronts: "Fronts", focus_peak: float) -> dict:
    scale = fronts.scale(0.0)
    rho, phi = anchors(scale)
    x, y = rho * np.cos(phi), rho * np.sin(phi)
    harmonics, _ = field_at(beam, x, y, np.zeros_like(x))
    return {
        "w": round(scale / UM, 4),
        "points": r(np.column_stack([x, y, np.zeros_like(x)]) / UM, 4),
        "harmonics": {str(n): {"re": r(E.real.T), "im": r(E.imag.T)} for n, E in harmonics.items()},
        "profile": r(intensity_profile(beam, scale, 0.0) / focus_peak, 4),
    }


def moving(beam, fronts: Fronts, z_range, focus_peak: float) -> list[dict]:
    frames = []
    for z_front in np.linspace(*z_range, N_FRONTS):
        w = fronts.scale(z_front)
        rho, phi = anchors(w)
        target = fronts.phase(0.0, z_front)
        z = z_front + (target - fronts.phase(rho, z_front, phi)) / fronts.k
        x, y = rho * np.cos(phi), rho * np.sin(phi)
        harmonics, omega = field_at(beam, x, y, z)
        t = (target - TAU0) / omega
        frames.append({
            "z": round(z_front / UM, 4),
            "w": round(w / UM, 4),
            "points": r(np.column_stack([x, y, z]) / UM, 4),
            "harmonics": {str(n): r(np.real(E * np.exp(-1j * n * omega * t)).T) for n, E in harmonics.items()},
            "profile": r(intensity_profile(beam, w, z_front) / focus_peak, 4),
        })
    return frames


def export_variant(v: Variant, wavelength: float, w0: float, z_range) -> dict:
    fronts = Fronts(wavelength, w0, v)
    focus_peak = intensity_profile(v.beam, fronts.scale(0.0), 0.0).max()
    return {"fixed": fixed(v.beam, fronts, focus_peak), "moving": moving(v.beam, fronts, z_range, focus_peak)}


def export_variants(variants: dict[str, Variant], wavelength: float, w0: float, omega: float,
                    z_range_zr=(-1.5, 1.5), z_range=None) -> dict:
    """``variants`` maps a variant id to a ``Variant``; all share the wavelength and waist.

    The travelling front spans ``z_range`` (m) or, by default, ``z_range_zr`` Rayleigh ranges of ``w0``.
    """
    zr = rayleigh_range(w0, wavelength)
    if z_range is None:
        z_range = tuple(c * zr for c in z_range_zr)
    return {
        "wavelength_um": wavelength / UM,
        "w0_um": w0 / UM,
        "zr_um": zr / UM,
        "period_fs": 2 * np.pi / omega / 1e-15,
        "tau0": TAU0,
        "variants": {vid: export_variant(v, wavelength, w0, z_range) for vid, v in variants.items()},
    }
