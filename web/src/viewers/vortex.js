// Optical vortices: scalar (helical phase, l = 1, 2) and vector (radial, azimuthal). Data: web/exporters/vortex.py.

import { createComponentViewer } from "../lib/component-viewer.js";

// |l| of the LG_{0,l} modes of each variant (vector vortices of order 1 use l = +-1)
const CHARGE = { "scalar-l1": 1, "scalar-l2": 2, radial: 1, azimuthal: 1 };

createComponentViewer({
  title: { fr: "Faisceaux vortex", en: "Vortex beams" },
  panels: [
    {
      key: "transverse", color: 0x4fd1ff, chip: { fr: "Transverse", en: "Transverse" },
      title: { fr: "1. Champ transverse E_⊥", en: "1. Transverse field E_⊥" },
      parts: [{ harmonic: "1", mask: [1, 1, 0] }],
    },
    {
      key: "ez", color: 0x6cf28a, chip: { fr: "E_z", en: "E_z" },
      title: (b, lang) => (lang === "en" ? `2. Longitudinal component E_z (×${b.z})` : `2. Composante longitudinale E_z (×${b.z})`),
      parts: [{ harmonic: "1", mask: [0, 0, 1], boost: "z" }],
    },
    {
      key: "total", color: 0xffffff, chip: { fr: "Résultante", en: "Resultant" }, sum: true,
      title: { fr: "3. Résultante", en: "3. Resultant" },
    },
  ],
  boosts: [{ key: "z", label: { fr: "E_z", en: "E_z" }, min: 1, max: 30, value: 10 }],
  variants: {
    label: { fr: "Type", en: "Type" },
    options: [
      { id: "scalar-l1", label: { fr: "scalaire ℓ = 1", en: "scalar ℓ = 1" } },
      { id: "scalar-l2", label: { fr: "scalaire ℓ = 2", en: "scalar ℓ = 2" } },
      { id: "radial", label: { fr: "vectoriel radial", en: "radial vector" } },
      { id: "azimuthal", label: { fr: "vectoriel azimutal", en: "azimuthal vector" } },
    ],
  },
  // |LG_{0,l}|^2 normalized to 1 on the bright ring at the focus (rho = w sqrt(|l| / 2))
  intensity: (r, w, w0, variant) => {
    const n = CHARGE[variant];
    return (w0 / w) ** 2 * (2 * r * r) ** n * Math.exp(-2 * r * r) / (n ** n * Math.exp(-n));
  },
  envelopeRadius: (w, variant) => w * Math.sqrt(CHARGE[variant] / 2),
  about: {
    fr: "Vortex scalaire : faisceau de Laguerre-Gauss LG₀ℓ polarisé selon x, dont la phase e^{iℓφ} tourne ℓ fois "
      + "autour de l'axe (front d'onde hélicoïdal, moment angulaire orbital ℓħ par photon) ; au foyer, le motif du "
      + "champ tourne autour de l'axe au cours du temps. Vortex vectoriel : la polarisation, linéaire en chaque point, "
      + "tourne autour de l'axe (singularité de polarisation), radiale ou azimutale pour l'ordre 1. Dans les deux cas "
      + "l'intensité est nulle sur l'axe.",
    en: "Scalar vortex: Laguerre-Gauss beam LG₀ℓ polarized along x, whose phase e^{iℓφ} winds ℓ times around the axis "
      + "(helical wavefront, orbital angular momentum ℓħ per photon); at the focus the field pattern rotates around the "
      + "axis in time. Vector vortex: the polarization, linear at each point, winds around the axis (polarization "
      + "singularity), radial or azimuthal at order 1. In both cases the intensity vanishes on the axis.",
  },
  references: [
    { label: "Allen et al., Phys. Rev. A 45, 8185 (1992)", href: "https://doi.org/10.1103/PhysRevA.45.8185" },
    { label: "Rosales-Guzmán, Ndagano, Forbes, J. Opt. 20, 123001 (2018)", href: "https://doi.org/10.1088/2040-8986/aaeb7d" },
    { label: "Zhan, Adv. Opt. Photon. 1, 1 (2009)", href: "https://doi.org/10.1364/AOP.1.000001" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
