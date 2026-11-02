// Cylindrical vector beams: radial and azimuthal polarization. With the synthetic-chiral option, the radial
// beam plus its azimuthal 2w partner is the chiral vector beam.

import { createFieldViewer } from "../lib/field-viewer.js";

createFieldViewer({
  title: { fr: "Faisceaux vectoriels", en: "Vector beams" },
  spec: (variant, w0um) => ({ lambda: 639e-9, w0: w0um * 1e-6,
    mode: { type: "vector", m: 1, theta0: variant === "radial" ? 0 : Math.PI / 2 } }),
  variants: {
    label: { fr: "Polarisation", en: "Polarization" },
    options: [
      { id: "radial", label: { fr: "radiale", en: "radial" } },
      { id: "azimuthal", label: { fr: "azimutale", en: "azimuthal" } },
    ],
  },
  size: { label: { fr: "Waist w₀", en: "Waist w₀" }, min: 0.8, max: 6, step: 0.1, value: 2.5, format: (v) => `${v.toFixed(1)} µm` },
  about: {
    fr: "Faisceaux vectoriels cylindriques (λ = 639 nm) : la polarisation, linéaire en chaque point, est radiale ou "
      + "azimutale, avec une singularité de polarisation sur l'axe où l'intensité s'annule. Ce sont des superpositions "
      + "de vortex LG₀,±₁ de polarisations circulaires opposées. Focalisé, le faisceau radial acquiert une forte "
      + "composante longitudinale E_z, maximale sur l'axe, nulle en ρ = w puis formant un anneau ; le faisceau "
      + "azimutal n'en a pas. Faisceau radial + option chirale (2ω azimutal) : faisceau vectoriel chiral.",
    en: "Cylindrical vector beams (λ = 639 nm): the polarization, linear at each point, is radial or azimuthal, with "
      + "a polarization singularity on the axis where the intensity vanishes. They are superpositions of LG₀,±₁ "
      + "vortices with opposite circular polarizations. When focused, the radial beam acquires a strong longitudinal "
      + "component E_z, largest on the axis, zero at ρ = w and then forming a ring; the azimuthal beam has none. "
      + "Radial beam + chiral option (azimuthal 2ω): chiral vector beam.",
  },
  references: [
    { label: "Zhan, Adv. Opt. Photon. 1, 1 (2009)", href: "https://doi.org/10.1364/AOP.1.000001" },
    { label: "Rosales-Guzmán, Ndagano, Forbes, J. Opt. 20, 123001 (2018)", href: "https://doi.org/10.1088/2040-8986/aaeb7d" },
    { label: "Dorn, Quabis, Leuchs, PRL 91, 233901 (2003)", href: "https://doi.org/10.1103/PhysRevLett.91.233901" },
    { label: "Rodriguez et al., arXiv:2610.17111 (2026)", href: "https://arxiv.org/abs/2610.17111" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
