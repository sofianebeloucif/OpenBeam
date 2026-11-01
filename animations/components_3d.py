"""The same wavefront shown four times: one field component per panel, then the resultant (PyVista).

Run:
    python animations/components_3d.py   # -> output/components_3d.mp4 and output/components_3d.gif

Each panel shows the wavefront at the focus of ``openbeam.ChiralVectorBeam``
(disc coloured by intensity) with arrows for one part of the real field:
the radial w field, the longitudinal E_z, the azimuthal 2w field, and finally
their sum. E_z and the 2w field are magnified by ``BOOST_Z`` and ``BOOST_2W``
in every panel, so the last panel is exactly the sum of the first three. The field is periodic,
so the GIF loops seamlessly.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pyvista as pv

from openbeam import ChiralVectorBeam, Grid
from wavefront_3d import FONT, HOT, intensity

UM = 1e-6
FS = 1e-15
BEAM = ChiralVectorBeam()
W0 = BEAM.w_omega
BOOST_Z = 5.0              # on-screen magnification of E_z
BOOST_2W = 8.0             # on-screen magnification of the 2w field
SECONDS_PER_PERIOD = 2.0
PERIODS = 4
FPS = 25
ARROW_LENGTH = 0.8          # µm on screen for |F| = 1
RINGS = (0.35, 0.7, 1.05, 1.4)   # arrow rings, in units of w0
AZIMUTHS = 12

PANELS = [
    ("1. Faisceau ω : polarisation radiale", "#4fd1ff"),
    (f"2. Composante longitudinale E_z (×{BOOST_Z:g})", "#6cf28a"),
    (f"3. Faisceau 2ω : polarisation azimutale (×{BOOST_2W:g})", "#ffd84f"),
    ("4. Résultante : somme des trois", "#ffffff"),
]


def sample_points() -> np.ndarray:
    rho = np.concatenate([[0.0], np.repeat(np.asarray(RINGS) * W0, AZIMUTHS)])
    phi = np.concatenate([[0.0], np.tile(np.linspace(0, 2 * np.pi, AZIMUTHS, endpoint=False), len(RINGS))])
    return np.column_stack([rho * np.cos(phi), rho * np.sin(phi), np.zeros_like(rho)])


def disc() -> pv.StructuredGrid:
    rho = np.linspace(0, 1.7 * W0, 50)[:, None]
    phi = np.linspace(0, 2 * np.pi, 90)
    surface = pv.StructuredGrid(rho * np.cos(phi) / UM, rho * np.sin(phi) / UM, np.zeros((rho.size, phi.size)))
    level = np.clip(np.broadcast_to(intensity(rho, 0.0), (rho.size, phi.size)).ravel(order="F"), 0, 1)
    rgba = HOT(level / 1.1)
    rgba[:, 3] = 0.15 + 0.55 * level
    surface["rgba"] = (255 * rgba).astype(np.uint8)
    return surface


class Components:
    def __init__(self):
        pts = sample_points()
        field = BEAM.field(Grid(*(c.reshape(-1, 1, 1) for c in pts.T)))
        E1 = field.harmonics[1][:, :, 0, 0]
        self.parts = [
            (1, E1 * np.array([1, 1, 0])[:, None]),                # radial w
            (1, E1 * np.array([0, 0, BOOST_Z])[:, None]),          # longitudinal E_z
            (2, field.harmonics[2][:, :, 0, 0] * BOOST_2W),        # azimuthal 2w
        ]
        self.omega = field.omega
        self.points = pts / UM

    def real(self, t: float) -> list[np.ndarray]:
        parts = [np.real(E * np.exp(-1j * n * self.omega * t)) for n, E in self.parts]
        return parts + [sum(parts)]

    def arrows(self, F: np.ndarray) -> pv.PolyData:
        cloud = pv.PolyData(self.points)
        cloud["F"] = F.T
        return cloud.glyph(orient="F", scale="F", factor=ARROW_LENGTH,
                           geom=pv.Arrow(tip_length=0.3, tip_radius=0.09, shaft_radius=0.03))


def main(out: Path = Path("output/components_3d.mp4")):
    out.parent.mkdir(parents=True, exist_ok=True)
    plotter = pv.Plotter(off_screen=True, window_size=(1920, 1080), shape=(2, 2), border=False)
    components = Components()
    period = 2 * np.pi / components.omega
    front = disc()
    axis_end = 4.0

    for k, (title, _) in enumerate(PANELS):
        plotter.subplot(k // 2, k % 2)
        plotter.set_background("black")
        plotter.add_mesh(front, scalars="rgba", rgba=True)
        plotter.add_mesh(pv.Line((0, 0, -axis_end), (0, 0, axis_end)), color="#777777", line_width=2)
        plotter.add_mesh(pv.Cone(center=(0, 0, axis_end), direction=(0, 0, 1), height=0.5, radius=0.18),
                         color="#777777")
        plotter.add_point_labels([(0, 0, axis_end + 0.6)], ["z"], text_color="#bbbbbb", font_size=20,
                                 shape_opacity=0, show_points=False, always_visible=True, font_file=FONT)
        plotter.add_text(title, position="upper_left", font_size=13, color="white", font_file=FONT)
        plotter.camera.focal_point = (0, 0, 0)
        plotter.camera.position = (6.5, 13.0, -7.0)
        plotter.camera.up = (1, 0, 0)
        plotter.camera.view_angle = 30
    plotter.enable_anti_aliasing("ssaa", all_renderers=True)
    plotter.open_movie(str(out), framerate=FPS, quality=9)

    n_frames = int(PERIODS * SECONDS_PER_PERIOD * FPS)
    for i in range(n_frames):
        t = i / FPS / SECONDS_PER_PERIOD * period
        for k, F in enumerate(components.real(t)):
            plotter.subplot(k // 2, k % 2)
            plotter.add_mesh(components.arrows(F), name="arrows", color=PANELS[k][1], smooth_shading=True)
        plotter.subplot(0, 1)
        plotter.add_text(f"t = {t / FS:.2f} fs", name="time", position="upper_right", font_size=12,
                         color="#bbbbbb", font_file=FONT)
        plotter.write_frame()
    plotter.close()

    # one period loops seamlessly
    gif = out.with_suffix(".gif")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-t", str(SECONDS_PER_PERIOD * 2), "-i", str(out), "-vf",
        "fps=20,scale=1280:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse", "-loop", "0", str(gif),
    ], check=True)
    return out, gif


if __name__ == "__main__":
    print(main())
