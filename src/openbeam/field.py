"""Polychromatic vector fields made of harmonics of a fundamental frequency."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .grid import Grid


@dataclass
class MultiHarmonicField:
    """Real field ``F(t) = Re sum_n E_n exp(-i n omega t)``.

    ``harmonics`` maps the harmonic order ``n`` to its complex phasor of shape
    ``(3, *grid.shape)`` holding the (x, y, z) components.
    """

    grid: Grid
    omega: float
    harmonics: dict[int, np.ndarray]

    @property
    def period(self) -> float:
        return 2 * np.pi / self.omega

    def real(self, t: float) -> np.ndarray:
        """Instantaneous real field, shape ``(3, *grid.shape)``."""
        return sum(np.real(E * np.exp(-1j * n * self.omega * t)) for n, E in self.harmonics.items())

    def intensity(self, t: float) -> np.ndarray:
        """Instantaneous ``|F(t)|^2``."""
        return np.sum(self.real(t) ** 2, axis=0)

    def time_averaged_intensity(self) -> np.ndarray:
        """Cycle average of ``|F(t)|^2`` (harmonics do not interfere on average)."""
        return sum(0.5 * np.sum(np.abs(E) ** 2, axis=0) for E in self.harmonics.values())
