"""Short, minimal animation of the beam propagating through its focus (side view).

Render (1080p, 30 fps):
    manim -qh --fps 30 animations/beam_propagation.py BeamPropagation

The red glow is the cycle-averaged intensity of ``openbeam.ChiralVectorBeam``
in the plane y = 0; white lines are wavefronts of the radial field (surfaces of
equal phase, one every ``FRONT_EVERY`` wavelengths), moving at the speed of light.
The transverse axis is stretched with respect to z.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN, GREY_B, GREY_C, LEFT, RIGHT, UL, UP, WHITE, Arrow, FadeIn, ImageMobject, Line, MathTex, Scene,
    Text, ValueTracker, VGroup, VMobject, always_redraw,
)

from openbeam import ChiralVectorBeam, Grid
from openbeam.modes import beam_radius, gouy_phase, inverse_curvature, rayleigh_range

UM = 1e-6
BEAM = ChiralVectorBeam()
ZR = rayleigh_range(BEAM.w_omega, BEAM.wavelength)
Z_MAX = 2 * ZR                      # physical half-length shown
X_MAX = 7 * UM                      # physical half-height shown
HALF_WIDTH, HALF_HEIGHT = 6.4, 2.4  # scene units
FRONT_EVERY = 8                     # draw one wavefront every N wavelengths
SECONDS_TO_CROSS = 5.0              # time for a wavefront to cross the screen
DURATION = 10.0


def to_scene(z, x):
    return np.stack([z / Z_MAX * HALF_WIDTH, x / X_MAX * HALF_HEIGHT, np.zeros_like(z)], axis=-1)


def intensity_image(nz: int = 1400, nx: int = 500) -> np.ndarray:
    """RGBA picture of the cycle-averaged intensity in the (z, x) plane."""
    grid = Grid.from_axes(np.linspace(X_MAX, -X_MAX, nx), 0.0, np.linspace(-Z_MAX, Z_MAX, nz))
    intensity = BEAM.field(grid).time_averaged_intensity()[:, 0, :]
    level = (intensity / intensity.max()) ** 0.6
    rgba = np.zeros((nx, nz, 4), dtype=np.uint8)
    rgba[..., 0] = 255 * level
    rgba[..., 1] = 60 * level**2
    rgba[..., 2] = 40 * level**3
    rgba[..., 3] = 255
    return rgba


class Wavefronts:
    """Lines of equal phase of the radial field, ``k z + k x^2 / 2R(z) - 2 Gouy(z) = const``."""

    def __init__(self, nx: int = 161, nz: int = 4000):
        self.x = np.linspace(-X_MAX, X_MAX, nx)
        z = np.linspace(-Z_MAX, Z_MAX, nz)
        w0, lam, k = BEAM.w_omega, BEAM.wavelength, BEAM.k
        self.z = z
        self.phase = (
            k * z[None, :]
            + k * self.x[:, None] ** 2 / 2 * inverse_curvature(z, w0, lam)[None, :]
            - 2 * gouy_phase(z, w0, lam)[None, :]
        )
        self.step = 2 * np.pi * FRONT_EVERY

    def lines(self, tau: float) -> VGroup:
        lo, hi = self.phase.min(), self.phase.max()
        targets = np.arange(np.ceil((lo - tau) / self.step), np.floor((hi - tau) / self.step) + 1) * self.step + tau
        fronts = np.array([np.interp(targets, row, self.z) for row in self.phase]).T  # (n_fronts, nx)
        group = VGroup()
        for z_front in fronts:
            inside = np.abs(self.x) < 1.6 * beam_radius(z_front, BEAM.w_omega, BEAM.wavelength)
            if inside.sum() < 3:
                continue
            points = to_scene(z_front[inside], self.x[inside])
            group.add(VMobject(stroke_color=WHITE, stroke_width=2.5, stroke_opacity=0.8).set_points_smoothly(points))
        return group


class BeamPropagation(Scene):
    def construct(self):
        glow = ImageMobject(intensity_image())
        glow.stretch_to_fit_width(2 * HALF_WIDTH).stretch_to_fit_height(2 * HALF_HEIGHT)
        glow.set_resampling_algorithm(2)  # bilinear

        fronts = Wavefronts()
        tau = ValueTracker(0)
        # phase speed: the whole window (2 Z_MAX) is crossed in SECONDS_TO_CROSS
        omega_scene = BEAM.k * 2 * Z_MAX / SECONDS_TO_CROSS
        tau.add_updater(lambda m, dt: m.increment_value(omega_scene * dt))
        lines = always_redraw(lambda: fronts.lines(tau.get_value()))

        title = Text("Propagation du faisceau laser", font_size=36, weight="BOLD").to_corner(UL)
        subtitle = Text("λ = 639 nm, vu de côté", font_size=22, color=GREY_B).next_to(title, DOWN, aligned_edge=LEFT)
        axis = Arrow(LEFT * HALF_WIDTH, RIGHT * (HALF_WIDTH + 0.3), buff=0, color=GREY_C, stroke_width=2)
        axis.shift(DOWN * (HALF_HEIGHT + 0.35))
        z_label = MathTex("z", color=GREY_B, font_size=36).next_to(axis, RIGHT, buff=0.15)
        focus_tick = Line(UP * 0.12, DOWN * 0.12, color=GREY_B).move_to([0, axis.get_y(), 0])
        focus_label = Text("foyer", font_size=22, color=GREY_B).next_to(focus_tick, DOWN, buff=0.12)
        legend = Text(
            f"lignes blanches : fronts d'onde (1 sur {FRONT_EVERY}), ralentis ~10¹³ fois",
            font_size=20, color=GREY_C,
        ).to_edge(DOWN, buff=0.15)

        self.add(tau)
        self.play(FadeIn(glow), FadeIn(title), FadeIn(subtitle), FadeIn(axis), FadeIn(z_label),
                  FadeIn(focus_tick), FadeIn(focus_label), run_time=1)
        self.play(FadeIn(lines), FadeIn(legend), run_time=1)
        self.wait(DURATION)
