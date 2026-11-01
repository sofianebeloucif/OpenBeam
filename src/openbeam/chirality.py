"""Local chirality of two-colour (w + 2w) fields.

A field is locally chiral when, at a fixed point, the tip of the electric
field draws a chiral 3D Lissajous figure during one cycle (synthetic chiral
light, D. Ayuso et al., Nat. Photon. 13, 866 (2019)). Its lowest-order measure
is the chiral correlation function (N. Mayer et al., Nat. Photon. (2024),
doi:10.1038/s41566-024-01499-8, Methods, after Ayuso et al. 2019)

    h5(-2w, -w, w, w, w) = E*(2w) . [E*(w) x E(w)] (E(w) . E(w)),

where ``E*(w) x E(w)`` is proportional to the spin (ellipticity vector) of the
w field. Its modulus sets the strength of the chiral response; its phase,
together with the molecular response, sets the sign, so shifting the 2w field
by pi is equivalent to exchanging the enantiomers.
"""

from __future__ import annotations

import numpy as np

from .field import MultiHarmonicField


def chiral_correlation(field: MultiHarmonicField) -> np.ndarray:
    """``h5(-2w, -w, w, w, w)`` at every point of the field's grid."""
    if not {1, 2} <= field.harmonics.keys():
        raise ValueError("h5 needs the w (n = 1) and 2w (n = 2) harmonics")
    E1, E2 = field.harmonics[1], field.harmonics[2]
    spin = np.cross(np.conj(E1), E1, axis=0)
    return np.sum(np.conj(E2) * spin, axis=0) * np.sum(E1 * E1, axis=0)
