"""One wavefront travelling through the focus, its field split into components (PyVista).

Run:
    python animations/components_moving_3d.py   # -> output/components_moving_3d.mp4 and .gif

Same 2x2 layout as ``components_3d.py``, but the wavefront now advances from
-1.5 z_R to +1.5 z_R. The arrows ride on it: they show the field of
``openbeam.ChiralVectorBeam`` at the points of the moving front, at the time the
front is there. Since the phase of the w wave is constant on its own wavefront,
the arrows do not oscillate; what changes along the way is the beam size, the
amplitude (largest at the focus) and the phase of E_z and of the 2w field
relative to the radial field (curvature and different Gouy phases), hence the
shape of the resultant.

The front is the surface where the radial w field equals ``cos(TAU0)`` times its
amplitude. The z axis is compressed by ``Z_SCALE`` on screen.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pyvista as pv

from components_3d import BOOST_2W, BOOST_Z, PANELS, RINGS
from openbeam import Grid
from openbeam.modes import beam_radius, rayleigh_range
from wavefront_3d import BEAM, FONT, HOT, K, LAM, W0, intensity, phase

UM = 1e-6
ZR = rayleigh_range(W0, LAM)
Z_RANGE = (-1.5 * ZR, 1.5 * ZR)
Z_SCALE = 0.15              # on-screen compression of z
TAU0 = np.pi / 4            # phase of the w wave on the displayed front
DURATION = 10.0
FPS = 25
ARROW_LENGTH = 1.5          # µm on screen for |F| = 1
AZIMUTHS = 12


def to_screen(x, y, z):
    return np.stack([x, y, z * Z_SCALE], axis=-1) / UM


def front_points(z_front: float):
    """Arrow anchors and disc on the equal-phase surface crossing the axis at ``z_front``."""
    w = beam_radius(z_front, W0, LAM)
    rho = np.concatenate([[0.0], np.repeat(np.asarray(RINGS) * w, AZIMUTHS)])
    phi = np.concatenate([[0.0], np.tile(np.linspace(0, 2 * np.pi, AZIMUTHS, endpoint=False), len(RINGS))])
    target = phase(0.0, z_front)
    z = z_front + (target - phase(rho, z_front)) / K
    return np.column_stack([rho * np.cos(phi), rho * np.sin(phi), z]), target


def disc(z_front: float) -> pv.StructuredGrid:
    w = beam_radius(z_front, W0, LAM)
    rho = np.linspace(0, 1.7 * w, 50)[:, None]
    phi = np.linspace(0, 2 * np.pi, 90)
    z = np.broadcast_to(z_front + (phase(0.0, z_front) - phase(rho, z_front)) / K, (rho.size, phi.size))
    pts = to_screen(rho * np.cos(phi), rho * np.sin(phi), z)
    surface = pv.StructuredGrid(pts[..., 0], pts[..., 1], pts[..., 2])
    level = np.clip(np.broadcast_to(intensity(rho, z_front), z.shape).ravel(order="F"), 0, 1)
    rgba = HOT(level / 1.1)
    rgba[:, 3] = 0.2 + 0.6 * level
    surface["rgba"] = (255 * rgba).astype(np.uint8)
    return surface


def envelope() -> pv.StructuredGrid:
    """Faint surface traced by the bright ring, rho = w(z) / sqrt(2)."""
    z = np.linspace(*Z_RANGE, 120)[:, None]
    phi = np.linspace(0, 2 * np.pi, 90)
    rho = beam_radius(z, W0, LAM) / np.sqrt(2)
    pts = to_screen(rho * np.cos(phi), rho * np.sin(phi), np.broadcast_to(z, (z.size, phi.size)))
    return pv.StructuredGrid(pts[..., 0], pts[..., 1], pts[..., 2])


def components(z_front: float):
    """Field parts on the front: radial w, E_z, azimuthal 2w, resultant; and anchors on screen."""
    pts, target = front_points(z_front)
    field = BEAM.field(Grid(*(c.reshape(-1, 1, 1) for c in pts.T)))
    t = (target - TAU0) / field.omega
    E1 = field.harmonics[1][:, :, 0, 0] * np.exp(-1j * field.omega * t)
    E2 = field.harmonics[2][:, :, 0, 0] * np.exp(-2j * field.omega * t)
    parts = [
        np.real(E1 * np.array([1, 1, 0])[:, None]),
        np.real(E1 * np.array([0, 0, BOOST_Z])[:, None]),
        np.real(E2 * BOOST_2W),
    ]
    return parts + [sum(parts)], to_screen(*pts.T)


def arrows(anchors: np.ndarray, F: np.ndarray) -> pv.PolyData:
    cloud = pv.PolyData(anchors)
    cloud["F"] = F.T
    return cloud.glyph(orient="F", scale="F", factor=ARROW_LENGTH,
                       geom=pv.Arrow(tip_length=0.3, tip_radius=0.09, shaft_radius=0.03))


def main(out: Path = Path("output/components_moving_3d.mp4")):
    out.parent.mkdir(parents=True, exist_ok=True)
    plotter = pv.Plotter(off_screen=True, window_size=(1920, 1080), shape=(2, 2), border=False)
    z_end = Z_RANGE[1] * Z_SCALE / UM * 1.1
    tube = envelope()

    for k, (title, _) in enumerate(PANELS):
        plotter.subplot(k // 2, k % 2)
        plotter.set_background("black")
        plotter.add_mesh(tube, color="#ff5a36", opacity=0.07)
        plotter.add_mesh(pv.Line((0, 0, -z_end), (0, 0, z_end)), color="#777777", line_width=2)
        plotter.add_mesh(pv.Cone(center=(0, 0, z_end), direction=(0, 0, 1), height=0.6, radius=0.22),
                         color="#777777")
        plotter.add_point_labels([(0, 0, z_end + 0.8)], ["z"], text_color="#bbbbbb", font_size=20,
                                 shape_opacity=0, show_points=False, always_visible=True, font_file=FONT)
        plotter.add_point_labels([(-1.9 * W0 / UM, 0, 0)], ["foyer"], text_color="#999999", font_size=16,
                                 shape_opacity=0, show_points=False, always_visible=True, font_file=FONT)
        plotter.add_text(title, position="upper_left", font_size=13, color="white", font_file=FONT)
        plotter.camera.focal_point = (0, 0, 0)
        plotter.enable_parallel_projection()  # same viewing angle on the front all along its path
        plotter.camera.position = (8.0, 19.0, -11.0)
        plotter.camera.up = (1, 0, 0)
        plotter.camera.parallel_scale = 8.5
    plotter.enable_anti_aliasing("ssaa", all_renderers=True)
    plotter.open_movie(str(out), framerate=FPS, quality=9)

    n_frames = int(DURATION * FPS)
    for z_front in np.linspace(*Z_RANGE, n_frames):
        parts, anchors = components(z_front)
        front = disc(z_front)
        for k, F in enumerate(parts):
            plotter.subplot(k // 2, k % 2)
            plotter.add_mesh(front, name="front", scalars="rgba", rgba=True)
            plotter.add_mesh(arrows(anchors, F), name="arrows", color=PANELS[k][1], smooth_shading=True)
        plotter.subplot(0, 1)
        plotter.add_text(f"z = {z_front / ZR:+.2f} z_R", name="z", position="upper_right", font_size=12,
                         color="#bbbbbb", font_file=FONT)
        plotter.write_frame()
    plotter.close()

    gif = out.with_suffix(".gif")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", str(out), "-vf",
        "fps=15,scale=1280:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse", "-loop", "0", str(gif),
    ], check=True)
    return out, gif


if __name__ == "__main__":
    print(main())
