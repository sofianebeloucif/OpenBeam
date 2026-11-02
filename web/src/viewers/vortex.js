// Scalar optical vortices LG_{0,l} (helical phase, orbital angular momentum), polarized along x.

import { createFieldViewer } from "../lib/field-viewer.js";

const X = [[1, 0], [0, 0]];

createFieldViewer({
  title: { fr: "Faisceaux vortex", en: "Vortex beams" },
  spec: (variant, w0um) => ({ lambda: 632.8e-9, w0: w0um * 1e-6, mode: { type: "lg", l: +variant.slice(1), jones: X } }),
  variants: {
    label: { fr: "Charge", en: "Charge" },
    options: [
      { id: "l1", label: { fr: "ℓ = 1", en: "ℓ = 1" } },
      { id: "l2", label: { fr: "ℓ = 2", en: "ℓ = 2" } },
      { id: "l3", label: { fr: "ℓ = 3", en: "ℓ = 3" } },
    ],
  },
  size: { label: { fr: "Waist w₀", en: "Waist w₀" }, min: 0.8, max: 6, step: 0.1, value: 2.5, format: (v) => `${v.toFixed(1)} µm` },
  about: {
    fr: "Vortex optique : faisceau de Laguerre-Gauss LG₀ℓ (λ = 632,8 nm) polarisé selon x, dont la phase e^{iℓφ} "
      + "tourne ℓ fois autour de l'axe. Le front d'onde est hélicoïdal et chaque photon porte un moment angulaire "
      + "orbital ℓħ ; l'intensité, nulle sur l'axe, forme un anneau. Au foyer, le motif du champ tourne autour de "
      + "l'axe au cours du temps.",
    en: "Optical vortex: Laguerre-Gauss beam LG₀ℓ (λ = 632.8 nm) polarized along x, whose phase e^{iℓφ} winds ℓ "
      + "times around the axis. The wavefront is helical and each photon carries an orbital angular momentum ℓħ; the "
      + "intensity, zero on the axis, forms a ring. At the focus the field pattern rotates around the axis in time.",
  },
  references: [
    { label: "Allen et al., Phys. Rev. A 45, 8185 (1992)", href: "https://doi.org/10.1103/PhysRevA.45.8185" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
