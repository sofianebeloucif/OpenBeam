# OpenBeam

Open source Python library to compute and visualize structured light beams.

Beams implemented: the fundamental **Gaussian beam** (TEM00, linear or circular
polarization, with its post-paraxial longitudinal field) and a two-colour
**chiral vector beam**: a tightly focused radially polarized vector vortex beam
at `ω` (with its longitudinal component `E_z`) superposed with an azimuthally
polarized vector vortex beam at `2ω`, whose sum is locally chiral, as proposed
by A. Rodriguez *et al.*, *Chiral Vector Beams for Topological Enantio-Sensitive
Imaging*, [arXiv:2610.17111](https://arxiv.org/abs/2610.17111) (2026).

### Definitions and references

- **Chiral vector beam**: the beam implemented here and its default parameters
  (λ = 639 nm, waists 2.5 and 5 µm, I₂ω/Iω = 0.01, ψ₂ω = 1.94π).
  A. Rodriguez *et al.*, [arXiv:2610.17111](https://arxiv.org/abs/2610.17111) (2026).
- **Vector vortex beam**: spatially inhomogeneous polarization with a
  polarization singularity on the axis, built from Laguerre-Gauss vortices of
  charges ±ℓ in opposite circular polarizations; ℓ = 1 gives the radially and
  azimuthally polarized (cylindrical vector) beams. C. Rosales-Guzmán,
  B. Ndagano, A. Forbes, *A review of complex vector light fields and their
  applications*, J. Opt. **20**, 123001 (2018),
  [doi:10.1088/2040-8986/aaeb7d](https://doi.org/10.1088/2040-8986/aaeb7d);
  Q. Zhan, *Cylindrical vector beams: from mathematical concepts to
  applications*, Adv. Opt. Photon. **1**, 1 (2009),
  [doi:10.1364/AOP.1.000001](https://doi.org/10.1364/AOP.1.000001).
- **Locally chiral light**: at each point the tip of the electric field draws a
  chiral 3D Lissajous figure during one cycle. D. Ayuso *et al.*, *Synthetic
  chiral light for efficient control of chiral light–matter interaction*,
  Nat. Photon. **13**, 866 (2019),
  [doi:10.1038/s41566-019-0531-2](https://doi.org/10.1038/s41566-019-0531-2)
  ([arXiv:1809.01632](https://arxiv.org/abs/1809.01632)).
- **Chiral correlation function** h⁽⁵⁾(−2ω, −ω, ω, ω, ω) =
  E*(2ω)·[E*(ω)×E(ω)](E(ω)·E(ω)), its lowest-order measure. N. Mayer *et al.*,
  *Chiral topological light for detection of robust enantiosensitive
  observables*, Nat. Photon. (2024),
  [doi:10.1038/s41566-024-01499-8](https://doi.org/10.1038/s41566-024-01499-8)
  ([arXiv:2303.10932](https://arxiv.org/abs/2303.10932)), after Ayuso *et al.*
- **Longitudinal field of a focused beam**, first post-paraxial order of
  `div E = 0`: `E_z = (i/k) ∇⊥·E⊥`. K. Y. Bliokh, F. Nori, Phys. Rep. **592**, 1
  (2015), [doi:10.1016/j.physrep.2015.06.003](https://doi.org/10.1016/j.physrep.2015.06.003);
  strong for radial polarization: R. Dorn, S. Quabis, G. Leuchs, PRL **91**,
  233901 (2003), [doi:10.1103/PhysRevLett.91.233901](https://doi.org/10.1103/PhysRevLett.91.233901).
- **Gaussian beam**: H. Kogelnik, T. Li, *Laser beams and resonators*,
  Appl. Opt. **5**, 1550 (1966), [doi:10.1364/AO.5.001550](https://doi.org/10.1364/AO.5.001550).

`openbeam.chiral_correlation(field)` computes h⁽⁵⁾. For the chiral vector beam
its modulus does not depend on the two-colour phase `ψ_2ω`, and
`ψ_2ω → ψ_2ω + π` flips its sign, which is equivalent to exchanging the
enantiomers (both tested).

## Installation

```bash
python -m venv .venv
.venv/bin/pip install -e ".[3d,dev]"   # [3d] adds PyVista for the 3D animation
```

`ffmpeg` is needed to write `.mp4` files (GIFs work without it).

## Usage

```python
from openbeam import ChiralVectorBeam, Grid
from openbeam.viz import animate_propagation, animate_transverse
from openbeam.viz.volume import animate_3d

beam = ChiralVectorBeam()                        # default parameters
field = beam.field(Grid.transverse(10e-6, 201))  # complex phasors per harmonic
F = field.real(t=0.5e-15)                        # real field (3, nx, ny, nz)

animate_transverse(beam, "transverse.mp4")       # plane z = 0: <|F|^2>, F_perp(t), F_z(t)
animate_propagation(beam, "propagation.mp4")    # side view (x, z): wavefronts travelling through the focus
animate_3d(beam, "volume.mp4")                   # 3D arrows along z + field-tip Lissajous curves
```

Or run `python examples/chiral_vector_beam.py`.

## Propagation video

A 12 s minimal side view of the beam crossing its focus: red glow = intensity,
white lines = wavefronts (one every 8 wavelengths) moving at the speed of light.

```bash
manim -qh --fps 30 animations/beam_propagation.py BeamPropagation
```

## 3D field of the chiral vector beam

12 s PyVista video, a few wavelengths around the focus, slowed down to 2 s per
optical period. Along four lines of the bright ring, arrows show the total
time-dependent field (radial `ω` + `E_z` + azimuthal `2ω`, from
`ChiralVectorBeam`) and white curves join their tips; faint discs are the
travelling crests of the `ω` wave. `E_z` and `2ω` are magnified ×5, z is
stretched ×2 (both stated on screen).

```bash
python animations/wavefront_3d.py   # -> output/wavefronts_3d.mp4
```

## Field components, one wavefront each

2×2 panels showing the same wavefront at the focus with, over time, the radial
`ω` field, the longitudinal `E_z` (×5), the azimuthal `2ω` field (×8) and their
resultant (exact sum of the three panels). The 4 s GIF loops seamlessly.

```bash
python animations/components_3d.py   # -> output/components_3d.mp4 and .gif
```

## Field components on a travelling wavefront

Same 2×2 layout, but one wavefront travels from −1.5 z_R to +1.5 z_R and the
arrows ride on it. The phase of the `ω` wave is constant on its own wavefront,
so the arrows do not oscillate; what evolves is the beam size, the amplitude and
the phase of `E_z` and `2ω` relative to the radial field (curvature, Gouy
phases), hence the shape of the resultant. z is compressed on screen.

```bash
python animations/components_moving_3d.py   # -> output/components_moving_3d.mp4 and .gif
```

## Web version

`web/` is a static site in French and English (language button, or `?lang=en`):
a hub (`web/index.html`) listing the beams, and one interactive Three.js viewer
per beam (`web/<beam id>/index.html`): the Gaussian beam (linear or circular
polarization) and the chiral vector beam.

Each viewer shows the components of the field in separate 3D panels (e.g.
radial `ω`, `E_z`, azimuthal `2ω` and their resultant), each view can be shown
or hidden, in two modes (wavefront fixed at the focus, oscillating in time;
wavefront travelling through the focus), with play/pause, a time or position
slider, speed and on-screen magnification of the weak components. Pages adapt
to the screen (views side by side or stacked, settings in a drawer on phones).
Add `#moving` to a viewer URL to start in the second mode.

```
web/
  index.html                   hub
  <beam id>/index.html         viewer pages (generic markup, filled by the viewer script)
  assets/                      shared CSS, favicon, card thumbnails
  src/beams.js                 registry of the beams shown on the hub
  src/hub.js                   hub cards
  src/lib/component-viewer.js  generic viewer, driven by a per-beam config
  src/lib/scene.js             Three.js helpers (arrows, wavefront disc, layout)
  src/lib/i18n.js, strings.js  language selection and interface texts (fr / en)
  src/viewers/<id>.js          per-beam config: panels, boosts, variants, texts, references
  exporters/common.py          field export on the arrow anchors (focus + travelling front)
  exporters/<name>.py          per-beam export, registered in exporters/__init__.py
  export.py                    writes web/build/data/<id>.js
  build/                       generated (data + bundles), not versioned
```

Build and open locally:

```bash
python web/export.py                    # -> web/build/data/*.js
cd web && npm install && npm run build  # -> web/build/hub.js, web/build/viewers/*.js
# then open web/index.html
```

### Adding a beam

1. A beam class in `openbeam.beams` exposing `field(grid)`.
2. `web/exporters/<name>.py` with an `export() -> dict` function built on
   `common.export_variants`, registered in `EXPORTERS` (`web/exporters/__init__.py`)
   under the beam id (see `gaussian.py`).
3. `web/src/viewers/<id>.js`: a `createComponentViewer` config (see
   `gaussian.js`), and `web/<id>/index.html`: copy an existing viewer page and
   change its title and the two script names.
4. An entry in `web/src/beams.js` (texts in `{ fr, en }`) with `status: "ready"`
   and a thumbnail in `web/assets/thumbs/`.

### GitHub Pages

`.github/workflows/pages.yml` exports the data, builds the bundles and publishes
the hub and every viewer folder on each push to `main`. In the repository
settings, choose *Pages > Build and deployment > Source: GitHub Actions*; the
site is then served at `https://<user>.github.io/<repo>/`.

## Explainer video

A ~75 s popular-science video (French captions, Manim, 3Blue1Brown style)
built from the same fields: wave along z, radial polarization, longitudinal
`E_z`, azimuthal `2ω` beam and the chiral 3D Lissajous loop with its mirror image.

```bash
.venv/bin/pip install -e ".[video]"   # needs a LaTeX install (latex, dvisvgm)
manim -qh --fps 30 animations/chiral_vector_beam_explainer.py ChiralVectorBeamExplainer
```

For readability the video uses `ψ_2ω = π/2` (strongest local chirality) and
magnifies `E_z` (×8) and the `2ω` field (×6); the captions say so.

## Structure

| Module | Content |
| --- | --- |
| `openbeam.grid` | `Grid`: transverse planes and volumes with cylindrical coordinates |
| `openbeam.modes` | Paraxial Laguerre-Gauss modes (Gouy phase, curvature, `w(z)`) |
| `openbeam.field` | `MultiHarmonicField`: `F(t) = Re Σ E_n e^{-i n ω t}` |
| `openbeam.beams` | Ready-made beams (`GaussianBeam`, `ChiralVectorBeam`) |
| `openbeam.chirality` | `chiral_correlation`: local chirality h⁽⁵⁾ of ω + 2ω fields |
| `openbeam.viz` | Matplotlib (transverse plane, propagation along z) and PyVista (3D) animations |

## Conventions

Phasors use `exp(-iωt)` and propagate as `exp(ikz)`. The chiral vector beam uses
the standard polar basis `e_ρ = (cos φ, sin φ)`, `e_φ = (−sin φ, cos φ)`, and
`ψ_2ω` is the phase of the azimuthal `2ω` field relative to the radial `ω` field
at the focus.

## Tests

```bash
.venv/bin/pytest
```

## License

MIT
