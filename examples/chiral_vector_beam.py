"""Animate the chiral vector beam (radial w + azimuthal 2w vector vortex beams) over a few optical cycles.

Run: python examples/chiral_vector_beam.py   (outputs written to ./output)
"""

from pathlib import Path

from openbeam import ChiralVectorBeam
from openbeam.viz import animate_propagation, animate_transverse
from openbeam.viz.volume import animate_3d

out = Path("output")
beam = ChiralVectorBeam()  # lambda = 639 nm, w = 2.5 / 5 um, I_2w / I_w = 0.01, psi_2w = 1.94 pi

print(animate_transverse(beam, out / "chiral_vector_transverse.mp4"))
print(animate_transverse(beam, out / "chiral_vector_transverse.gif", n_frames=40))
print(animate_propagation(beam, out / "chiral_vector_propagation.mp4"))
print(animate_3d(beam, out / "chiral_vector_3d.mp4"))
print(animate_3d(beam, out / "chiral_vector_3d.gif", n_frames=40))
