"""Reference fields from the Python library, to validate the JavaScript port (web/src/lib/fields.js).

Run:
    python web/test/reference.py        # -> web/build/reference.json, then: cd web && npm test

Each case is a beam spec in the format of fields.js and the Python beam built from it,
including the 2w partner of synthetic chiral light (built explicitly here, so the
partner rule of fields.js is checked too).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from openbeam import BesselBeam, GaussianBeam, Grid, TwoColourBeam, VectorVortexBeam, VortexBeam
from openbeam.modes import rayleigh_range

OUT = Path(__file__).resolve().parents[1] / "build" / "reference.json"
X = [[1, 0], [0, 0]]
Y = [[0, 0], [1, 0]]
SIGMA_PLUS = [[2**-0.5, 0], [0, 2**-0.5]]
SIGMA_PLUS_PARTNER = (1j, 1)  # (-conj(b), conj(a)) of sigma+


def jones_tuple(j):
    return tuple(complex(*c) for c in j)


def python_beam(spec, wavelength=None, w0=None, mode=None):
    lam, w, m = wavelength or spec["lambda"], w0 or spec["w0"], mode or spec["mode"]
    if m["type"] == "lg":
        if m["l"] == 0:
            return GaussianBeam(wavelength=lam, w0=w, polarization=jones_tuple(m["jones"]) if isinstance(m["jones"], list) else m["jones"])
        return VortexBeam(wavelength=lam, w0=w, l=m["l"], polarization=jones_tuple(m["jones"]) if isinstance(m["jones"], list) else m["jones"])
    if m["type"] == "vector":
        return VectorVortexBeam(wavelength=lam, w0=w, m=m["m"], theta0=m["theta0"])
    if m["type"] == "bessel":
        return BesselBeam(wavelength=lam, w0=w, n=m["n"], kr=m["kr"], polarization=jones_tuple(m["jones"]) if isinstance(m["jones"], list) else m["jones"])
    raise ValueError(m["type"])


def case(spec, partner_mode=None):
    beam = python_beam(spec)
    if spec.get("chiral"):
        second = python_beam(spec, wavelength=spec["lambda"] / 2, w0=2 * spec["w0"], mode=partner_mode)
        beam = TwoColourBeam(beam, second, intensity_ratio=spec["chiral"]["ratio"], psi_2w=spec["chiral"]["psi"])
    rng = np.random.default_rng(len(json.dumps(spec)))
    if spec["mode"]["type"] == "bessel":
        size, zs = 6 / spec["mode"]["kr"], spec["w0"] * 2 * np.pi / spec["lambda"] / spec["mode"]["kr"]
    else:
        size, zs = spec["w0"], rayleigh_range(spec["w0"], spec["lambda"])
    pts = np.column_stack([rng.uniform(-2, 2, 24) * size, rng.uniform(-2, 2, 24) * size, rng.uniform(-1.5, 1.5, 24) * zs])
    pts = np.vstack([pts, [[0, 0, 0], [0.3 * size, 0, 0], [0, 0.4 * size, 0.2 * zs]]])
    field = beam.field(Grid(*(c.reshape(-1, 1, 1) for c in pts.T)))
    harmonics = {str(n): [[[float(E[c, i].real), float(E[c, i].imag)] for c in range(3)] for i in range(len(pts))]
                 for n, E in ((n, E[:, :, 0, 0]) for n, E in field.harmonics.items())}
    return {"spec": spec, "points": pts.tolist(), "harmonics": harmonics}


def main():
    lam = 632.8e-9
    kr = 2 * np.pi / lam * np.sin(np.deg2rad(15))
    cases = [
        case({"lambda": lam, "w0": 1.3e-6, "mode": {"type": "lg", "l": 0, "jones": X}}),
        case({"lambda": lam, "w0": 2.5e-6, "mode": {"type": "lg", "l": 0, "jones": SIGMA_PLUS}}),
        case({"lambda": lam, "w0": 2e-6, "mode": {"type": "lg", "l": 2, "jones": X}}),
        case({"lambda": lam, "w0": 2e-6, "mode": {"type": "lg", "l": -1, "jones": X}}),
        case({"lambda": 639e-9, "w0": 2.5e-6, "mode": {"type": "vector", "m": 1, "theta0": np.pi / 2}}),
        case({"lambda": lam, "w0": 8e-6, "mode": {"type": "bessel", "n": 1, "kr": kr, "jones": X}}),
        # synthetic chiral light: partners built explicitly
        case({"lambda": 639e-9, "w0": 2.5e-6, "mode": {"type": "vector", "m": 1, "theta0": 0.0},
              "chiral": {"ratio": 0.01, "psi": 1.94 * np.pi}},
             partner_mode={"type": "vector", "m": 1, "theta0": np.pi / 2}),
        case({"lambda": lam, "w0": 1.5e-6, "mode": {"type": "lg", "l": 0, "jones": X}, "chiral": {"ratio": 0.25, "psi": 0.7}},
             partner_mode={"type": "lg", "l": 0, "jones": Y}),
        case({"lambda": lam, "w0": 2e-6, "mode": {"type": "lg", "l": 0, "jones": SIGMA_PLUS}, "chiral": {"ratio": 0.1, "psi": 2.0}},
             partner_mode={"type": "lg", "l": 0, "jones": SIGMA_PLUS_PARTNER}),
        case({"lambda": lam, "w0": 8e-6, "mode": {"type": "bessel", "n": 0, "kr": kr, "jones": X}, "chiral": {"ratio": 0.5, "psi": 1.0}},
             partner_mode={"type": "bessel", "n": 0, "kr": kr, "jones": Y}),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"cases": cases}))
    print(OUT, len(cases), "cases")


if __name__ == "__main__":
    main()
