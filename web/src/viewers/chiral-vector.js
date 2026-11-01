// Chiral vector beam (radial w + E_z + azimuthal 2w). Data: web/exporters/chiral_vector.py.

import { createComponentViewer } from "../lib/component-viewer.js";

createComponentViewer({
  title: { fr: "Faisceau vectoriel chiral", en: "Chiral vector beam" },
  panels: [
    {
      key: "radial", color: 0x4fd1ff, chip: { fr: "ω radial", en: "radial ω" },
      title: { fr: "1. Faisceau ω : polarisation radiale", en: "1. ω beam: radial polarization" },
      parts: [{ harmonic: "1", mask: [1, 1, 0] }],
    },
    {
      key: "ez", color: 0x6cf28a, chip: { fr: "E_z", en: "E_z" },
      title: (b, lang) => (lang === "en" ? `2. Longitudinal component E_z (×${b.z})` : `2. Composante longitudinale E_z (×${b.z})`),
      parts: [{ harmonic: "1", mask: [0, 0, 1], boost: "z" }],
    },
    {
      key: "azimuthal", color: 0xffd84f, chip: { fr: "2ω azimutal", en: "azimuthal 2ω" },
      title: (b, lang) => (lang === "en" ? `3. 2ω beam: azimuthal polarization (×${b.w2})` : `3. Faisceau 2ω : polarisation azimutale (×${b.w2})`),
      parts: [{ harmonic: "2", mask: [1, 1, 1], boost: "w2" }],
    },
    {
      key: "total", color: 0xffffff, chip: { fr: "Résultante", en: "Resultant" }, sum: true,
      title: { fr: "4. Résultante : somme des trois", en: "4. Resultant: sum of the three" },
    },
  ],
  boosts: [
    { key: "z", label: { fr: "E_z", en: "E_z" }, min: 1, max: 10, value: 5 },
    { key: "w2", label: { fr: "2ω", en: "2ω" }, min: 1, max: 15, value: 8 },
  ],
  // LG_{0,±1} ring: 1 on the bright ring at the focus
  intensity: (r, w, w0) => (w0 / w) ** 2 * 2 * Math.E * r ** 2 * Math.exp(-2 * r ** 2),
  envelopeRadius: (w) => w / Math.SQRT2,
  about: {
    fr: "Deux faisceaux vortex vectoriels (polarisation non uniforme, singularité de polarisation sur l'axe) : un "
      + "faisceau ω à polarisation radiale fortement focalisé, qui acquiert une composante longitudinale E_z, et un "
      + "faisceau 2ω à polarisation azimutale. Leur somme est localement chirale : en chaque point, la pointe du "
      + "champ électrique décrit une figure de Lissajous 3D chirale, mesurée par la fonction de corrélation h⁽⁵⁾.",
    en: "Two vector vortex beams (inhomogeneous polarization, polarization singularity on the axis): a tightly "
      + "focused radially polarized ω beam, which acquires a longitudinal component E_z, and an azimuthally "
      + "polarized 2ω beam. Their sum is locally chiral: at each point, the tip of the electric field draws a chiral "
      + "3D Lissajous figure, measured by the correlation function h⁽⁵⁾.",
  },
  references: [
    { label: "Rosales-Guzmán, Ndagano, Forbes, J. Opt. 20, 123001 (2018)", href: "https://doi.org/10.1088/2040-8986/aaeb7d" },
    { label: "Zhan, Adv. Opt. Photon. 1, 1 (2009)", href: "https://doi.org/10.1364/AOP.1.000001" },
    { label: "Ayuso et al., Nat. Photon. 13, 866 (2019)", href: "https://doi.org/10.1038/s41566-019-0531-2" },
    { label: "Mayer et al., Nat. Photon. (2024)", href: "https://doi.org/10.1038/s41566-024-01499-8" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
    { label: "Dorn, Quabis, Leuchs, PRL 91, 233901 (2003)", href: "https://doi.org/10.1103/PhysRevLett.91.233901" },
  ],
});
