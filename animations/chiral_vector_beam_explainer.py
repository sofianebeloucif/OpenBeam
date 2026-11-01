"""Popular-science explainer of the chiral vector beam (Manim, French captions).

Render (1080p, 30 fps):
    manim -qh --fps 30 animations/chiral_vector_beam_explainer.py ChiralVectorBeamExplainer
Quick preview:
    manim -ql animations/chiral_vector_beam_explainer.py ChiralVectorBeamExplainer

All fields come from ``openbeam.ChiralVectorBeam``. The longitudinal and
second-harmonic components are a few percent of the radial one, so they are
magnified on screen (stated in the captions).
"""

from __future__ import annotations

import numpy as np
from manim import (
    BLUE_C, BLUE_E, DEGREES, DOWN, GREY_B, GREY_D, LEFT, ORANGE, PI, RIGHT, TEAL_C, UL, UP, UR, WHITE,
    YELLOW_C, Annulus, Arrow, Create, FadeIn, FadeOut, MathTex, ParametricFunction, Rectangle, Text,
    ThreeDScene, ValueTracker, VGroup, VMobject, Write, always_redraw,
)

from openbeam import ChiralVectorBeam, Grid

UM = 1e-6
UNIT = 1.0           # scene units per micrometre
KZ = 8.0             # on-screen magnification of E_z
K2 = 6.0             # on-screen magnification of the 2w field
CYCLES_PER_SECOND = 0.5

BEAM = ChiralVectorBeam(psi_2w=PI / 2)
R0 = BEAM.w_omega / np.sqrt(2) / UM  # radius of the bright ring (µm)


def to_scene(v: np.ndarray) -> np.ndarray:
    """Physical (x, y, z) -> scene (z, x, y): a rotation, so handedness is preserved."""
    return np.asarray(v)[[2, 0, 1]]


class Probe:
    """Phasors of both harmonics at a set of points given in micrometres, shape (3, N)."""

    def __init__(self, points_um: np.ndarray):
        self.points = np.asarray(points_um, dtype=float)
        grid = Grid(*(c.reshape(-1, 1, 1) * UM for c in self.points))
        field = BEAM.field(grid)
        self.E1 = field.harmonics[1][:, :, 0, 0]
        self.E2 = field.harmonics[2][:, :, 0, 0]

    def real(self, tau: float, w1: float = 1.0, w2: float = 0.0, kz: float = 1.0) -> np.ndarray:
        """Real field at phase ``tau = omega t`` with per-term on-screen weights."""
        E1 = self.E1 * np.array([1, 1, kz])[:, None]
        return w1 * np.real(E1 * np.exp(-1j * tau)) + w2 * np.real(self.E2 * np.exp(-2j * tau))


class FieldArrows(VGroup):
    """Arrows anchored on a probe, refreshed from a phase tracker."""

    def __init__(self, probe: Probe, tau: ValueTracker, scale: float, color, z_stretch: float = 1.0, **weights):
        self.probe, self.tau, self.scale_factor, self.weights = probe, tau, scale, weights
        self.starts = to_scene(probe.points).T * UNIT * np.array([z_stretch, 1, 1])
        arrows = [
            Arrow(s, s + RIGHT * scale, buff=0, color=color, stroke_width=3,
                  max_tip_length_to_length_ratio=0.3, tip_length=0.12)
            for s in self.starts
        ]
        super().__init__(*arrows)
        self.add_updater(lambda m: m.refresh())
        self.refresh()

    def refresh(self):
        vectors = to_scene(self.probe.real(self.tau.get_value(), **self.weights)).T * self.scale_factor
        for arrow, start, v in zip(self.submobjects, self.starts, vectors):
            if np.linalg.norm(v) < 1e-3:
                v = 1e-3 * RIGHT
            arrow.put_start_and_end_on(start, start + v)


def ring_points(radii, n_phi, z=0.0, offset=0.0):
    rho, phi = np.meshgrid(radii, np.linspace(0, 2 * np.pi, n_phi, endpoint=False) + offset)
    return np.stack([rho * np.cos(phi), rho * np.sin(phi), np.full(rho.shape, z)]).reshape(3, -1)


class ChiralVectorBeamExplainer(ThreeDScene):
    def construct(self):
        self.tau = ValueTracker(0)
        self.tau.add_updater(lambda m, dt: m.increment_value(2 * PI * CYCLES_PER_SECOND * dt))
        self.add(self.tau)

        self.title_card()
        self.wave_along_z()
        self.radial_polarization()
        self.longitudinal_field()
        self.second_harmonic()
        self.chiral_lissajous()
        self.outro()

    # -- helpers -------------------------------------------------------------
    def chapter(self, title: str, caption: str | None = None):
        heading = Text(title, font_size=36, weight="BOLD").to_corner(UL)
        group = [heading]
        if caption:
            group.append(Text(caption, font_size=24, color=GREY_B, line_spacing=1.2).to_edge(DOWN))
        self.add_fixed_in_frame_mobjects(*group)
        self.play(*(FadeIn(m) for m in group))
        return VGroup(*group)

    def caption(self, text: str, old: VGroup | None = None):
        new = Text(text, font_size=24, color=GREY_B, line_spacing=1.2).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(new)
        self.play(*([FadeOut(old)] if old else []), FadeIn(new))
        return new

    def clear_scene(self):
        self.play(*(FadeOut(m) for m in self.mobjects if m is not self.tau))
        self.remove(*(m for m in self.mobjects if m is not self.tau))

    def transverse_glow(self):
        """Cycle-averaged intensity of the w beam drawn as concentric rings in the plane z = 0."""
        radii = np.linspace(0.05, 4.0, 40)
        probe = Probe(np.stack([radii, 0 * radii, 0 * radii]))
        intensity = np.sum(np.abs(probe.E1) ** 2, axis=0)
        intensity /= intensity.max()
        dr = radii[1] - radii[0]
        rings = VGroup(*(
            Annulus(inner_radius=max(r - dr / 2, 0) * UNIT, outer_radius=(r + dr / 2) * UNIT,
                    fill_color=ORANGE, fill_opacity=0.55 * i, stroke_width=0)
            for r, i in zip(radii, intensity)
        ))
        return rings.rotate(PI / 2, axis=UP)  # into the scene (y, z) plane, i.e. physical z = 0

    # -- chapters ------------------------------------------------------------
    def title_card(self):
        title = Text("Les faisceaux vectoriels chiraux", font_size=52, weight="BOLD")
        subtitle = Text("Une lumière qui a une « main »", font_size=32, color=TEAL_C).next_to(title, DOWN)
        source = Text("D'après Rodriguez et al., arXiv:2610.17111 (2026) ; lumière localement chirale : "
                      "Ayuso et al., Nat. Photon. 13, 866 (2019)", font_size=18, color=GREY_B).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(title, subtitle, source)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3), FadeIn(source))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(source))

    def wave_along_z(self):
        """Side view; z is stretched x2 on screen so that individual wavelengths are readable."""
        self.set_camera_orientation(phi=75 * DEGREES, theta=-90 * DEGREES, zoom=0.8)
        stretch = 2.0
        z_max = 3.0
        lines = []
        for y in (R0, -R0):
            z = np.arange(-z_max, z_max, BEAM.wavelength / UM / 6)
            arrows = FieldArrows(Probe(np.stack([0 * z, 0 * z + y, z])), self.tau, 1.2, BLUE_C, z_stretch=stretch)
            z_fine = np.linspace(-z_max, z_max, 400)
            fine = Probe(np.stack([0 * z_fine, 0 * z_fine + y, z_fine]))
            base = to_scene(fine.points).T * UNIT * np.array([stretch, 1, 1])
            curve = always_redraw(lambda fine=fine, base=base: VMobject(color=WHITE, stroke_width=2).set_points_smoothly(
                base + to_scene(fine.real(self.tau.get_value())).T * 1.2
            ))
            lines += [arrows, curve]
        axis = Arrow(LEFT * 6.6, RIGHT * 6.8, buff=0, color=GREY_D, stroke_width=2)
        label = MathTex("z", color=GREY_B).move_to(RIGHT * 6.9 + DOWN * 0.4)
        self.add_fixed_orientation_mobjects(label)

        text = self.chapter(
            "1. La lumière est une onde",
            "Le champ électrique oscille… et cette oscillation avance le long de z\n"
            "à 300 000 km/s (ici ralentie un million de milliards de fois).",
        )
        self.play(Create(axis), FadeIn(label))
        self.play(*(FadeIn(m) for m in lines))
        self.wait(6)
        self.play(FadeOut(text))
        self.clear_scene()

    def radial_polarization(self):
        self.move_camera(phi=90 * DEGREES, theta=0, zoom=1.0, run_time=0.1)
        glow = self.transverse_glow()
        probe = Probe(ring_points([0.6, 1.2, 1.8, 2.4, 3.0], 16))
        arrows = FieldArrows(probe, self.tau, 0.9, BLUE_C)
        text = self.chapter(
            "2. Polarisation radiale",
            "Face au faisceau : l'intensité forme un anneau (orange),\n"
            "et le champ pointe partout vers l'extérieur… puis vers l'intérieur.",
        )
        self.play(FadeIn(glow), FadeIn(arrows))
        self.wait(7)
        self.play(FadeOut(text))
        self.glow, self.ring_probe, self.radial_arrows = glow, probe, arrows

    def longitudinal_field(self):
        text = self.chapter(
            "3. Focalisation serrée",
            f"En focalisant fortement, une composante E_z apparaît le long de la propagation,\n"
            f"maximale au centre et décalée d'un quart de période (agrandie ×{KZ:g}).",
        )
        formula = MathTex(r"E_z = \frac{i}{k}\,\frac{1}{\rho}\,\partial_\rho\!\left(\rho\,E_\rho\right)",
                          font_size=40).to_corner(UR)
        self.add_fixed_in_frame_mobjects(formula)
        center = Probe(ring_points([0.0, 0.6], 8))
        center_arrows = FieldArrows(center, self.tau, 0.9, TEAL_C, kz=KZ)
        self.remove(self.radial_arrows)
        arrows = FieldArrows(self.ring_probe, self.tau, 0.9, BLUE_C, kz=KZ)
        self.add(arrows)
        self.play(FadeIn(formula), FadeIn(center_arrows))
        self.move_camera(phi=65 * DEGREES, theta=-35 * DEGREES, zoom=0.95, run_time=3)
        self.wait(5)
        self.play(FadeOut(text), FadeOut(formula), FadeOut(center_arrows))
        self.omega_arrows = arrows

    def second_harmonic(self):
        text = self.chapter(
            "4. Ajout d'un second faisceau à 2ω",
            f"Un faisceau de couleur double (UV), polarisé en tourbillon (azimutal),\n"
            f"oscille deux fois plus vite (jaune, agrandi ×{K2:g}).",
        )
        self.move_camera(phi=90 * DEGREES, theta=0, zoom=1.0, run_time=2)
        swirl = FieldArrows(self.ring_probe, self.tau, 0.9, YELLOW_C, w1=0, w2=K2)
        self.play(FadeOut(self.omega_arrows), FadeIn(swirl))
        self.wait(4)
        total = FieldArrows(self.ring_probe, self.tau, 0.9, WHITE, w1=1, w2=K2, kz=KZ)
        caption = self.caption("Les deux faisceaux se superposent : le champ total (blanc) tourne en 3D.",
                               old=text[1])
        self.play(FadeOut(swirl), FadeIn(total))
        self.move_camera(phi=65 * DEGREES, theta=-35 * DEGREES, run_time=3)
        self.wait(2)
        self.play(FadeOut(text[0]), FadeOut(caption))
        self.clear_scene()

    def chiral_lissajous(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES, zoom=0.85)
        probe = Probe(np.array([[R0], [0.0], [0.0]]))
        scale = 2.2
        weights = {"w1": 1, "w2": K2, "kz": KZ}

        def tip(tau, mirror=False):
            v = probe.real(tau, **weights)[:, 0]
            if mirror:
                v = v * np.array([1, 1, -1])  # reflection z -> -z, through the plane between the loops
            return to_scene(v) * scale

        left, right = LEFT * 3.2, RIGHT * 3.2
        start = self.tau.get_value()
        tracer = always_redraw(lambda: ParametricFunction(
            lambda s: left + tip(s), t_range=[start, max(self.tau.get_value(), start + 1e-3)],
            color=TEAL_C, stroke_width=4,
        ))
        arrow = always_redraw(lambda: Arrow(left, left + tip(self.tau.get_value()), buff=0, color=WHITE,
                                            stroke_width=4, tip_length=0.18))
        text = self.chapter(
            "5. Une figure chirale",
            "En un point de l'anneau, la pointe du champ dessine une boucle tordue en 3D.",
        )
        self.add(tracer, arrow)
        self.wait(1 / CYCLES_PER_SECOND + 0.2)
        loop = ParametricFunction(lambda s: left + tip(s), t_range=[0, 2 * PI], color=TEAL_C, stroke_width=4)
        self.remove(tracer)
        self.add(loop)

        mirror_plane = Rectangle(width=4.5, height=4.5, stroke_color=GREY_B, fill_color=BLUE_E,
                                 fill_opacity=0.15).rotate(PI / 2, axis=UP)
        mirrored = ParametricFunction(lambda s: right + tip(s, mirror=True), t_range=[0, 2 * PI],
                                      color=ORANGE, stroke_width=4)
        caption = self.caption(
            "Son image dans un miroir (orange) ne lui est pas superposable, comme une main gauche\n"
            "et une main droite : le champ est chiral.", old=text[1],
        )
        self.play(FadeOut(arrow), FadeIn(mirror_plane))
        self.play(Create(mirrored), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.35)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(text[0]), FadeOut(caption))
        self.clear_scene()

    def outro(self):
        lines = VGroup(
            Text("Les molécules chirales « gauches » et « droites »", font_size=34),
            Text("réagissent différemment à cette lumière :", font_size=34),
            Text("on peut les distinguer en imagerie.", font_size=34, color=TEAL_C),
        ).arrange(DOWN, buff=0.3)
        credits = Text("Animation : OpenBeam · ψ₂ω = π/2, E_z et 2ω agrandis pour la lisibilité",
                       font_size=18, color=GREY_B).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(lines, credits)
        self.play(FadeIn(lines, shift=UP * 0.3), FadeIn(credits))
        self.wait(4)
        self.play(FadeOut(lines), FadeOut(credits))
