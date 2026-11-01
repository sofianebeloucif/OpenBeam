"""Animations of beam fields (``volume`` requires the ``[3d]`` extra)."""

from .propagation import animate_propagation
from .transverse import animate_transverse

__all__ = ["animate_propagation", "animate_transverse"]
