# OpenBeam

Open source Python library to compute and visualize structured light beams.

Beams implemented: the fundamental **Gaussian beam** (TEM00, linear or circular
polarization), **scalar vortex beams** (LG₀ℓ, helical phase, orbital angular
momentum), **vector beams** (polarization rotating around the axis: radial,
azimuthal, any order), **Bessel(-Gauss) beams** (quasi non-diffracting, any
order), all with their post-paraxial longitudinal field, and a two-colour
**chiral vector beam**: a tightly focused radially polarized vector beam at `ω`
(with its longitudinal component `E_z`) superposed with an azimuthally
polarized vector beam at `2ω`, whose sum is locally chiral, as proposed
by A. Rodriguez *et al.*, *Chiral Vector Beams for Topological Enantio-Sensitive
Imaging*, [arXiv:2610.17111](https://arxiv.org/abs/2610.17111) (2026).

### Definitions and references

- **Chiral vector beam**: the beam implemented here and its default parameters
  (λ = 639 nm, waists 2.5 and 5 µm, I₂ω/Iω = 0.01, ψ₂ω = 1.94π).
  A. Rodriguez *et al.*, [arXiv:2610.17111](https://arxiv.org/abs/2610.17111) (2026).
- **Vector beam** (cylindrical vector beam): the polarization, linear at each
  point, rotates around the axis (angle mφ + θ₀), with a polarization
  singularity on the axis and no orbital angular momentum; built from
  Laguerre-Gauss vortices of charges ±m in opposite circular polarizations.
  m = 1 gives the radially and azimuthally polarized beams. Unlike a (scalar)
  vortex beam, its phase does not wind around the axis. C. Rosales-Guzmán,
  B. Ndagano, A. Forbes, *A review of complex vector light fields and their
  applications*, J. Opt. **20**, 123001 (2018),
  [doi:10.1088/2040-8986/aaeb7d](https://doi.org/10.1088/2040-8986/aaeb7d);
  Q. Zhan, *Cylindrical vector beams: from mathematical concepts to
  applications*, Adv. Opt. Photon. **1**, 1 (2009),
  [doi:10.1364/AOP.1.000001](https://doi.org/10.1364/AOP.1.000001).
- **Scalar vortex beam**: Laguerre-Gauss mode LG₀ℓ whose phase e^{iℓφ} winds ℓ
  times around the axis, carrying an orbital angular momentum ℓħ per photon.
  L. Allen, M. W. Beijersbergen, R. J. C. Spreeuw, J. P. Woerdman, Phys. Rev. A
  **45**, 8185 (1992), [doi:10.1103/PhysRevA.45.8185](https://doi.org/10.1103/PhysRevA.45.8185).
- **Bessel beam**: a cone of plane waves whose transverse profile
  J_n(k_r ρ) does not spread while propagating. J. Durnin, J. J. Miceli,
  J. H. Eberly, *Diffraction-free beams*, PRL **58**, 1499 (1987),
  [doi:10.1103/PhysRevLett.58.1499](https://doi.org/10.1103/PhysRevLett.58.1499);
  finite-energy Bessel-Gauss beam (implemented): F. Gori, G. Guattari,
  C. Padovani, *Bessel-Gauss beams*, Opt. Commun. **64**, 491 (1987),
  [doi:10.1016/0030-4018(87)90276-8](https://doi.org/10.1016/0030-4018(87)90276-8).
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

Live site: <https://sofianebeloucif.github.io/OpenBeam/> (French and English:
language button, or `?lang=en`).

`web/` is a static site: a hub (`web/index.html`) and one interactive Three.js
viewer per beam family (`web/<id>/index.html`): Gaussian beam (linear or
circular polarization), vortex beams (ℓ = 1, 2, 3), vector beams (radial,
azimuthal) and Bessel beams (orders 0 and 1).

Each viewer shows the field on a wavefront, split into components in separate
3D panels: transverse field, longitudinal field `E_z`, and their resultant.
Each panel has its own scale: the disc shows the cycle-averaged intensity of
its component and the arrows its instantaneous field, normalized to their
maximum at the focus, with the relative amplitude in the title (e.g. two `E_z`
lobes along the polarization of a Gaussian beam); the resultant is at true
scale. A slider sets the waist `w₀` (the cone angle for Bessel beams): tighter
focusing makes `E_z` grow. Two modes: wavefront fixed at the focus, oscillating
in time, or travelling through the focus (`#moving` in the URL).

**Synthetic chiral light** is an option on every beam (`?chiral=1`): the same
beam at `2ω` (half the wavelength, twice the waist, orthogonal polarization:
x → y, σ⁺ → σ⁻, radial → azimuthal), with adjustable intensity ratio and phase
delay `ψ_2ω`. The radial vector beam with this option is the chiral vector
beam (`vector/index.html?variant=radial&chiral=1`).

The fields are computed in the browser by `web/src/lib/fields.js`, a
JavaScript port of the OpenBeam beams (`VortexBeam`, `GaussianBeam`,
`VectorBeam`, `BesselBeam`, `TwoColourBeam`). `web/test/reference.py`
computes reference fields with the Python library and `npm test` checks that
the port agrees with them (relative error below 1e-7); the deployment fails
otherwise.

```
web/
  index.html                hub
  <id>/index.html           viewer pages (generic markup, filled by the viewer script)
  assets/                   shared CSS, favicon, card thumbnails
  src/beams.js              registry of the beams shown on the hub
  src/hub.js                hub cards
  src/lib/fields.js         JavaScript port of the OpenBeam fields
  src/lib/field-viewer.js   generic viewer, driven by a per-beam config
  src/lib/scene.js          Three.js helpers (arrows, wavefront disc, layout)
  src/lib/i18n.js, strings.js  language selection and interface texts (fr / en)
  src/viewers/<id>.js       per-beam config: beam spec, variants, size slider, texts, references
  test/reference.py         reference fields from the Python library -> web/build/reference.json
  test/compare.mjs          `npm test`: JavaScript port vs reference
  test/check-pages.mjs      headless-Chrome screenshots and error report of pages
  build/                    generated, not versioned
```

Build, check and open locally:

```bash
python web/test/reference.py            # reference fields from the Python library
cd web && npm install && npm test       # JavaScript port vs Python
npm run build                           # -> web/build/hub.js, web/build/viewers/*.js
# then open web/index.html
```

### Adding a beam

1. The beam in the Python library (`src/openbeam/beams`, with tests).
2. Its formula in `web/src/lib/fields.js` (a new `mode.type`, and its
   wavefront phase and size in `modeGeometry`), and a case in
   `web/test/reference.py`; `npm test` must pass.
3. `web/src/viewers/<id>.js`: a `createFieldViewer` config (see
   `gaussian.js`), and `web/<id>/index.html`: copy an existing viewer page and
   change its title and script name.
4. An entry in `web/src/beams.js` (texts in `{ fr, en }`) with
   `status: "ready"` and a thumbnail in `web/assets/thumbs/`.

### GitHub Pages

`.github/workflows/pages.yml` computes the reference fields, runs `npm test`,
builds the bundles and publishes the hub and every viewer folder on each push
to `main` (*Pages > Build and deployment > Source: GitHub Actions*).

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
| `openbeam.beams` | Ready-made beams (`GaussianBeam`, `VortexBeam`, `VectorBeam`, `BesselBeam`, `TwoColourBeam`, `ChiralVectorBeam`) |
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

## How to cite

If you use OpenBeam (library, animations or web viewers) in a publication, a
course or another project, please cite it:

> S. Beloucif, *OpenBeam: compute and visualize structured light beams*,
> version 0.1.0 (2026), https://github.com/sofianebeloucif/OpenBeam

The citation metadata are in [`CITATION.cff`](CITATION.cff) (GitHub's
*Cite this repository* button).

## License

MIT (see [`LICENSE`](LICENSE)): free use, modification and redistribution,
keeping the copyright notice.
