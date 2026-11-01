"""3D view of the chiral vector beam near its focus: time-dependent electric field (PyVista).

Run:
    python animations/wavefront_3d.py            # -> output/wavefronts_3d.mp4

The window spans a few wavelengths around the focus, slowed down so that one
optical period of the w beam lasts ``SECONDS_PER_PERIOD`` seconds.

* Along four lines of the bright ring (top, bottom, left, right), arrows show
  the total real field ``F(t) = Re[(E_rho + E_z) e^{-i w t} + E_phi e^{-2 i w t}]``
  computed by ``openbeam.ChiralVectorBeam``, and a white curve joins the arrow
  tips. E_z and the 2w field are magnified by ``BOOST``.
* Faint discs are the crests of the w wave (one per wavelength), coloured by
  intensity; they travel along z at the speed of light.
* Positions along z are stretched by ``STRETCH_Z`` on screen.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv
from matplotlib import colormaps

from openbeam import ChiralVectorBeam, Grid
from openbeam.modes import beam_radius, gouy_phase, inverse_curvature

UM = 1e-6
FS = 1e-15
BEAM = ChiralVectorBeam()
W0, LAM, K = BEAM.w_omega, BEAM.wavelength, BEAM.k
Z_MAX = 2 * LAM
STRETCH_Z = 2.0
BOOST = 5.0                 # on-screen magnification of E_z and of the 2w field
SECONDS_PER_PERIOD = 2.0
DURATION = 12.0
FPS = 30
ARROWS_PER_WAVELENGTH = 8
CURVE_SUBSAMPLING = 4       # curve points per arrow
ARROW_LENGTH = 0.9          # µm on screen for |F| = 1
HOT = colormaps["hot"]
LINE_COLORS = ["#4fd1ff", "#ffb84f"]  # top and bottom lines (cyan) / lines facing the camera (orange)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # VTK's default font has no Greek letters


def to_screen(x, y, z):
    return np.stack([x, y, z * STRETCH_Z], axis=-1) / UM


def phase(rho, z):
    """Phase of the radial w field (carrier, curvature and l = 1 Gouy phase)."""
    return K * z + K * rho**2 / 2 * inverse_curvature(z, W0, LAM) - 2 * gouy_phase(z, W0, LAM)


def intensity(rho, z):
    """Cycle-averaged intensity of the w beam, 1 on the bright ring at the focus."""
    w = beam_radius(z, W0, LAM)
    return (W0 / w) ** 2 * 2 * np.e * (rho / w) ** 2 * np.exp(-2 * rho**2 / w**2)


class FieldLines:
    """Total field along lines parallel to z on the bright ring."""

    def __init__(self, azimuths=(0, np.pi / 2, np.pi, 3 * np.pi / 2)):
        ring = W0 / np.sqrt(2)
        n = int(2 * Z_MAX / LAM * ARROWS_PER_WAVELENGTH * CURVE_SUBSAMPLING) + 1
        z = np.linspace(-Z_MAX, Z_MAX, n)
        A, Z = np.meshgrid(np.asarray(azimuths), z, indexing="ij")  # (lines, n)
        x, y = ring * np.cos(A), ring * np.sin(A)
        field = BEAM.field(Grid(*(c.reshape(-1, 1, 1) for c in (x, y, Z))))
        shape = (3, *A.shape)
        self.E1 = (field.harmonics[1][:, :, 0, 0] * np.array([1, 1, BOOST])[:, None]).reshape(shape)
        self.E2 = (field.harmonics[2][:, :, 0, 0] * BOOST).reshape(shape)
        self.omega = field.omega
        self.base = to_screen(x, y, Z)  # (lines, n, 3)

    def meshes(self, t: float):
        F = np.real(self.E1 * np.exp(-1j * self.omega * t) + self.E2 * np.exp(-2j * self.omega * t))
        tips = self.base + np.moveaxis(F, 0, -1) * ARROW_LENGTH
        curves = [pv.Spline(line, len(line)) for line in tips]
        cloud = pv.PolyData(self.base[:, ::CURVE_SUBSAMPLING].reshape(-1, 3))
        cloud["F"] = np.moveaxis(F[:, :, ::CURVE_SUBSAMPLING], 0, -1).reshape(-1, 3)
        cloud["line"] = np.repeat(np.arange(len(tips)) % 2, cloud.n_points // len(tips))
        arrows = cloud.glyph(orient="F", scale="F", factor=ARROW_LENGTH,
                             geom=pv.Arrow(tip_length=0.25, tip_radius=0.07, shaft_radius=0.025))
        return arrows, pv.merge(curves)


class Crests:
    """Equal-phase discs of the w wave at its crests, one per wavelength."""

    def __init__(self, n_rho: int = 40, n_phi: int = 72):
        self.rho = np.linspace(0, 1.7 * W0, n_rho)[:, None]
        self.phi = np.linspace(0, 2 * np.pi, n_phi)
        self.z = np.linspace(-2 * Z_MAX, 2 * Z_MAX, 4000)
        self.on_axis = phase(0.0, self.z)

    def meshes(self, tau: float):
        lo = int(np.ceil((phase(0.0, -Z_MAX) - tau) / (2 * np.pi)))
        hi = int(np.floor((phase(0.0, Z_MAX) - tau) / (2 * np.pi)))
        for m in range(lo, hi + 1):
            target = 2 * np.pi * m + tau
            z0 = np.interp(target, self.on_axis, self.z)
            z = np.broadcast_to(z0 + (target - phase(self.rho, z0)) / K, (self.rho.size, self.phi.size))
            pts = to_screen(self.rho * np.cos(self.phi), self.rho * np.sin(self.phi), z)
            surface = pv.StructuredGrid(pts[..., 0], pts[..., 1], pts[..., 2])
            level = np.clip(np.broadcast_to(intensity(self.rho, z0), z.shape).ravel(order="F"), 0, 1)
            rgba = HOT(level / 1.1)
            rgba[:, 3] = 0.3 * level**0.8  # dim parts transparent
            surface["rgba"] = (255 * rgba).astype(np.uint8)
            yield surface


def main(out: Path = Path("output/wavefronts_3d.mp4"), duration: float = DURATION):
    out.parent.mkdir(parents=True, exist_ok=True)
    plotter = pv.Plotter(off_screen=True, window_size=(1920, 1080))
    plotter.set_background("black")
    plotter.enable_anti_aliasing("ssaa")

    z_end = Z_MAX * STRETCH_Z / UM * 1.12
    plotter.add_mesh(pv.Line((0, 0, -z_end), (0, 0, z_end)), color="#777777", line_width=2)
    plotter.add_mesh(pv.Cone(center=(0, 0, z_end), direction=(0, 0, 1), height=0.3, radius=0.1), color="#777777")
    plotter.add_point_labels([(0, 0, z_end + 0.35)], ["z"], text_color="#bbbbbb", font_size=26,
                             shape_opacity=0, show_points=False, always_visible=True, font_file=FONT)
    plotter.add_text("Faisceau vectoriel chiral : le champ électrique au cours du temps",
                     position="upper_left", font_size=18, color="white", font_file=FONT)
    plotter.add_text(
        "Flèches : champ électrique total (ω radial + E_z + 2ω azimutal) sur quatre lignes de l'anneau lumineux\n"
        "(bleu : haut et bas, orange : avant et arrière).\n"
        "Courbes blanches : pointe des flèches.   Disques : crêtes de l'onde ω, qui avancent le long de z.\n"
        f"E_z et le faisceau 2ω agrandis ×{BOOST:g}, axe z étiré ×{STRETCH_Z:g}.",
        position="lower_left", font_size=11, color="#aaaaaa", font_file=FONT,
    )

    lines, crests = FieldLines(), Crests()
    period = 2 * np.pi / lines.omega
    plotter.camera.view_angle = 30
    plotter.open_movie(str(out), framerate=FPS, quality=9)

    for i in range(int(duration * FPS)):
        s = i / FPS
        t = s / SECONDS_PER_PERIOD * period
        angle = np.deg2rad(-30 + 20 * s / duration)  # slow orbit; +y side so that z runs left to right
        plotter.camera.position = (5.0, 14 * np.cos(angle), 14 * np.sin(angle))
        plotter.camera.up = (1, 0, 0)
        plotter.camera.focal_point = (0, 0, 0)

        names = set()
        for j, surface in enumerate(crests.meshes(lines.omega * t)):
            plotter.add_mesh(surface, name=f"crest{j}", scalars="rgba", rgba=True, smooth_shading=True)
            names.add(f"crest{j}")
        for name in [a for a in plotter.actors if a.startswith("crest") and a not in names]:
            plotter.remove_actor(name)
        arrows, curves = lines.meshes(t)
        plotter.add_mesh(arrows, name="arrows", scalars="line", cmap=LINE_COLORS, clim=(0, 1),
                         show_scalar_bar=False, smooth_shading=True)
        plotter.add_mesh(curves, name="curves", color="white", line_width=4, render_lines_as_tubes=True)
        plotter.add_text(f"t = {t / FS:.2f} fs", name="time", position="upper_right", font_size=14,
                         color="#bbbbbb", font_file=FONT)
        plotter.write_frame()
    plotter.close()
    return out


if __name__ == "__main__":
    print(main())
