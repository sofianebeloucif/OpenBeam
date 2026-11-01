"""3D animation of the real field along the propagation axis (requires PyVista)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ..grid import Grid

try:
    import pyvista as pv
except ImportError as error:  # pragma: no cover
    raise ImportError("openbeam.viz.volume requires the [3d] extra: pip install 'openbeam[3d]'") from error

UM = 1e-6
FS = 1e-15


def _points(grid: Grid) -> np.ndarray:
    return np.column_stack([grid.x.ravel(), grid.y.ravel(), grid.z.ravel()]) / UM


def _vectors(F: np.ndarray) -> np.ndarray:
    return F.reshape(3, -1).T


def animate_3d(
    beam,
    out: str | Path,
    extent: float | None = None,
    z_range: tuple[float, float] | None = None,
    azimuths: int = 12,
    planes: int = 17,
    n_frames: int = 60,
    n_periods: float = 1.0,
    fps: int = 20,
    window_size: tuple[int, int] = (1280, 800),
) -> Path:
    """Animate the 3D field ``F(x, y, z, t)`` over ``n_periods`` optical cycles.

    Arrows show the instantaneous field (coloured by ``F_z``) on the ring of
    maximum ``omega`` intensity, ``rho = w_omega / sqrt(2)``, sampled at
    ``azimuths`` angles on ``planes`` transverse planes, inside a translucent
    surface of the time-averaged intensity. Closed curves trace the tip of ``F`` over one period at four
    points of the focal ring, a moving sphere marks its current position.
    The writer is chosen from the extension of ``out`` (``.gif`` or ``.mp4``).
    """
    out = Path(out)
    if extent is None:
        extent = 3 * beam.w_omega
    if z_range is None:
        z_range = (-2 * beam.wavelength, 2 * beam.wavelength)

    r = beam.w_omega / np.sqrt(2)
    angles = np.linspace(0, 2 * np.pi, azimuths, endpoint=False)[:, None, None]
    z = np.linspace(*z_range, planes)[None, :, None]
    arrow_grid = Grid(*np.broadcast_arrays(r * np.cos(angles), r * np.sin(angles), z))
    field = beam.field(arrow_grid)
    arrow_points = _points(arrow_grid)
    f_max = np.sqrt(2 * field.time_averaged_intensity().max())
    scale = 0.25 * beam.w_omega / UM / f_max
    fz_max = np.max(np.abs(field.harmonics[1][2]))

    # Translucent envelope: half maximum of the cycle-averaged intensity
    envelope_grid = Grid.volume(extent, 61, *z_range, 31)
    envelope = pv.StructuredGrid(*(c / UM for c in (envelope_grid.x, envelope_grid.y, envelope_grid.z)))
    envelope["I"] = beam.field(envelope_grid).time_averaged_intensity().ravel(order="F")
    envelope = envelope.contour([0.5 * envelope["I"].max()], scalars="I")

    # Field-tip trajectories on the focal ring
    phi = np.arange(4) * np.pi / 2
    ring = Grid(r * np.cos(phi)[:, None, None], r * np.sin(phi)[:, None, None], np.zeros((4, 1, 1)))
    ring_field = beam.field(ring)
    ring_points = _points(ring)
    cycle = np.linspace(0, ring_field.period, 200)
    tips = np.stack([ring_points + scale * _vectors(ring_field.real(t)) for t in cycle], axis=1)

    plotter = pv.Plotter(off_screen=True, window_size=window_size)
    plotter.set_background("black")
    plotter.add_mesh(envelope, color="orange", opacity=0.15, smooth_shading=True)
    for tip in tips:
        plotter.add_mesh(pv.lines_from_points(tip, close=True), color="white", line_width=3)
    plotter.add_mesh(
        pv.Line((0, 0, z_range[0] / UM), (0, 0, z_range[1] / UM)), color="gray", line_width=1
    )
    plotter.show_bounds(xtitle="x (um)", ytitle="y (um)", ztitle="z (um)", color="white", font_size=10)
    plotter.view_vector((0.35, -1, -0.45), viewup=(1, 0, 0))
    plotter.reset_camera()

    if out.suffix == ".gif":
        plotter.open_gif(str(out), fps=fps)
    else:
        plotter.open_movie(str(out), framerate=fps, quality=8)
    out.parent.mkdir(parents=True, exist_ok=True)

    for t in np.linspace(0, n_periods * field.period, n_frames, endpoint=False):
        cloud = pv.PolyData(arrow_points)
        vectors = _vectors(field.real(t))
        cloud["F"] = vectors
        cloud["Fz"] = vectors[:, 2]
        glyphs = cloud.glyph(orient="F", scale="F", factor=scale)
        plotter.add_mesh(
            glyphs, name="arrows", scalars="Fz", cmap="coolwarm", clim=(-fz_max, fz_max),
            scalar_bar_args={"title": "F_z", "color": "white"},
        )
        markers = pv.PolyData(ring_points + scale * _vectors(ring_field.real(t)))
        plotter.add_mesh(markers, name="tips", color="cyan", point_size=14, render_points_as_spheres=True)
        plotter.add_text(f"t = {t / FS:.3f} fs", name="time", color="white", font_size=12)
        plotter.write_frame()

    plotter.close()
    return out
