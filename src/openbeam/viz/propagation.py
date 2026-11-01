"""Animation of the real field in the (x, z) plane, along the propagation axis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

from ..grid import Grid
from ..modes import rayleigh_range

UM = 1e-6
FS = 1e-15


def animate_propagation(
    beam,
    out: str | Path,
    zoom: float | None = None,
    extent: float | None = None,
    n: int = 201,
    samples_per_wavelength: int = 40,
    frames_per_period: int = 24,
    n_periods: int = 4,
    fps: int = 20,
) -> Path:
    """Animate ``F(x, y=0, z, t)`` as the beam travels through its focus.

    Top: cycle-averaged intensity over ``[-2 z_R, 2 z_R]`` (focusing of the
    ``omega`` beam) with the zoomed window outlined. Below, over
    ``|z| < zoom / 2``: the radial ``F_x`` and longitudinal ``F_z`` components
    of the ``omega`` beam, then the out-of-plane ``F_y`` carried by the
    azimuthal ``2 omega`` beam. The writer is chosen from the extension of ``out``.
    """
    out = Path(out)
    if zoom is None:
        zoom = 8 * beam.wavelength
    if extent is None:
        extent = 4 * beam.w_omega
    z_r = rayleigh_range(beam.w_omega, beam.wavelength)
    x = np.linspace(-extent / 2, extent / 2, n)

    overview = beam.field(Grid.from_axes(x, 0.0, np.linspace(-2 * z_r, 2 * z_r, 4 * n)))
    nz = int(samples_per_wavelength * zoom / beam.wavelength)
    image = beam.field(Grid.from_axes(x, 0.0, np.linspace(-zoom / 2, zoom / 2, nz)))
    zoom_bounds = np.array([-zoom, zoom, -extent, extent]) / 2 / UM

    fig, axes = plt.subplots(
        4, 1, figsize=(11, 12), constrained_layout=True, sharex=False,
        gridspec_kw={"height_ratios": [1, 1.3, 1.3, 1.3]},
    )
    top = axes[0]
    top.imshow(
        overview.time_averaged_intensity()[:, 0, :], origin="lower", aspect="auto", cmap="inferno",
        extent=np.array([-2 * z_r, 2 * z_r, -extent / 2, extent / 2]) / UM,
    )
    top.add_patch(Rectangle(zoom_bounds[[0, 2]], zoom / UM, extent / UM, fill=False, color="cyan", lw=1.5))
    top.set(
        title=rf"$\langle|F|^2\rangle$ through the focus ($z_R$ = {z_r / UM:.0f} µm), zoomed window in cyan",
        xlabel="z (µm)", ylabel="x (µm)",
    )

    panels = [
        (0, 1, r"$\omega$ radial: $F_x(t)$", "RdBu_r"),
        (2, 1, r"$\omega$ longitudinal (tight focusing): $F_z(t)$", "PiYG"),
        (1, 2, r"$2\omega$ azimuthal, out of plane: $F_y(t)$", "PuOr_r"),
    ]
    images = []
    for ax, (component, harmonic, title, cmap) in zip(axes[1:], panels):
        vmax = np.max(np.abs(image.harmonics[harmonic][component]))
        images.append(ax.imshow(
            np.zeros((n, nz)), origin="lower", extent=zoom_bounds, aspect="auto", cmap=cmap,
            vmin=-vmax, vmax=vmax, interpolation="bilinear",
        ))
        ax.set(title=title, ylabel="x (µm)")
        ax.annotate(
            "propagation", xy=(0.99, 0.06), xytext=(0.80, 0.06), xycoords="axes fraction",
            va="center", ha="right", fontsize=9,
            arrowprops={"arrowstyle": "->", "lw": 1.5}, bbox={"fc": "white", "alpha": 0.7, "lw": 0},
        )
        fig.colorbar(images[-1], ax=ax, shrink=0.9)
    axes[-1].set_xlabel("z (µm)")
    suptitle = fig.suptitle("")

    n_frames = frames_per_period * n_periods
    times = np.linspace(0, n_periods * image.period, n_frames, endpoint=False)

    def update(i):
        t = times[i]
        F = image.real(t)
        for im, (component, *_) in zip(images, panels):
            im.set_data(F[component][:, 0, :])
        suptitle.set_text(f"Propagation along z  (plane y = 0)    t = {t / FS:.2f} fs")
        return (*images, suptitle)

    animation = FuncAnimation(fig, update, frames=n_frames, blit=False)
    writer = PillowWriter(fps=fps) if out.suffix == ".gif" else FFMpegWriter(fps=fps, bitrate=6000)
    out.parent.mkdir(parents=True, exist_ok=True)
    animation.save(out, writer=writer, dpi=100)
    plt.close(fig)
    return out
