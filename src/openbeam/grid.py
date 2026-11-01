"""Cartesian sampling grids with their cylindrical coordinates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Grid:
    """Rectilinear grid; coordinate arrays have shape ``(nx, ny, nz)`` (SI units)."""

    x: np.ndarray
    y: np.ndarray
    z: np.ndarray

    @classmethod
    def from_axes(cls, x, y, z) -> "Grid":
        X, Y, Z = np.meshgrid(np.atleast_1d(x), np.atleast_1d(y), np.atleast_1d(z), indexing="ij")
        return cls(X, Y, Z)

    @classmethod
    def transverse(cls, extent: float, n: int, z: float = 0.0) -> "Grid":
        """Square ``n x n`` plane of full width ``extent`` at a given ``z``."""
        axis = np.linspace(-extent / 2, extent / 2, n)
        return cls.from_axes(axis, axis, z)

    @classmethod
    def volume(cls, extent: float, n: int, z_min: float, z_max: float, nz: int) -> "Grid":
        """Stack of ``nz`` square transverse planes between ``z_min`` and ``z_max``."""
        axis = np.linspace(-extent / 2, extent / 2, n)
        return cls.from_axes(axis, axis, np.linspace(z_min, z_max, nz))

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.x.shape

    @property
    def rho(self) -> np.ndarray:
        return np.hypot(self.x, self.y)

    @property
    def phi(self) -> np.ndarray:
        return np.arctan2(self.y, self.x)

    @property
    def dx(self) -> float:
        return float(self.x[1, 0, 0] - self.x[0, 0, 0])

    @property
    def dy(self) -> float:
        return float(self.y[0, 1, 0] - self.y[0, 0, 0])
