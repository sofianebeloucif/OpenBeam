"""Animation of the real field in a transverse plane."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

from ..grid import Grid

UM = 1e-6
FS = 1e-15


def animate_transverse(
    beam,
    out: str | Path,
    z: float = 0.0,
    extent: float | None = None,
    n: int = 151,
    arrows: int = 21,
    n_frames: int = 60,
    n_periods: float = 1.0,
    fps: int = 20,
    threshold: float = 0.02,
) -> Path:
    """Animate ``F(x, y, z, t)`` over ``n_periods`` optical cycles of ``beam``.

    Left: time-averaged intensity with the instantaneous transverse field as
    arrows. Right: instantaneous longitudinal field ``F_z``. The writer is
    chosen from the extension of ``out`` (``.gif`` or a video format).
    """
    out = Path(out)
    if extent is None:
        extent = 4 * beam.w_omega

    image = beam.field(Grid.transverse(extent, n, z))
    arrow_grid = Grid.transverse(extent, arrows, z)
    arrow_field = beam.field(arrow_grid)

    intensity = image.time_averaged_intensity()[:, :, 0]
    hidden = (arrow_field.time_averaged_intensity()[:, :, 0] < threshold * intensity.max()).ravel()
    fz_max = np.max(np.abs(image.harmonics[1][2]))
    f_max = np.sqrt(2 * intensity.max())
    spacing = extent / UM / (arrows - 1)
    bounds = np.array([-extent, extent, -extent, extent]) / 2 / UM
    ax_x, ax_y = arrow_grid.x.ravel() / UM, arrow_grid.y.ravel() / UM

    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
    left.imshow(intensity.T, origin="lower", extent=bounds, cmap="inferno")
    quiver = left.quiver(
        ax_x, ax_y, np.zeros_like(ax_x), np.zeros_like(ax_y),
        color="cyan", angles="xy", scale_units="xy", scale=f_max / spacing, width=0.004,
    )
    left.set(title=r"$\langle|F|^2\rangle$ and $F_\perp(t)$", xlabel="x (µm)", ylabel="y (µm)")
    fz_image = right.imshow(
        np.zeros((n, n)), origin="lower", extent=bounds, cmap="RdBu_r", vmin=-fz_max, vmax=fz_max
    )
    right.set(title=r"$F_z(t)$", xlabel="x (µm)")
    fig.colorbar(fz_image, ax=right, shrink=0.8)
    suptitle = fig.suptitle("")

    times = np.linspace(0, n_periods * image.period, n_frames, endpoint=False)

    def update(i):
        t = times[i]
        F = arrow_field.real(t)
        u, v = F[0].ravel(), F[1].ravel()
        u[hidden] = v[hidden] = np.nan
        quiver.set_UVC(u, v)
        fz_image.set_data(image.real(t)[2][:, :, 0].T)
        suptitle.set_text(f"z = {z / UM:.2f} µm    t = {t / FS:.3f} fs")
        return quiver, fz_image, suptitle

    animation = FuncAnimation(fig, update, frames=n_frames, blit=False)
    writer = PillowWriter(fps=fps) if out.suffix == ".gif" else FFMpegWriter(fps=fps, bitrate=4000)
    out.parent.mkdir(parents=True, exist_ok=True)
    animation.save(out, writer=writer, dpi=110)
    plt.close(fig)
    return out
