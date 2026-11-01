// Fundamental Gaussian beam (TEM00), linear or circular polarization. Data: web/exporters/gaussian.py.

import { createComponentViewer } from "../lib/component-viewer.js";

createComponentViewer({
  title: { fr: "Faisceau gaussien", en: "Gaussian beam" },
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
  boosts: [{ key: "z", label: { fr: "E_z", en: "E_z" }, min: 1, max: 30, value: 12 }],
  variants: {
    label: { fr: "Polarisation", en: "Polarization" },
    options: [
      { id: "linear", label: { fr: "linéaire", en: "linear" } },
      { id: "circular", label: { fr: "circulaire", en: "circular" } },
    ],
  },
  intensity: (r, w, w0) => (w0 / w) ** 2 * Math.exp(-2 * r ** 2),
  envelopeRadius: (w) => w,
  // the Gaussian spot is smaller than the chiral beam's ring: closer camera
  modes: { fixed: { camera: [-4.6, 4.3, 8.6] }, moving: { camera: [-12, 8.6, 20] } },
  about: {
    fr: "Le mode fondamental d'un laser (TEM₀₀) : profil d'intensité gaussien de rayon w(z), focalisé au col w₀ puis "
      + "divergent, fronts d'onde courbés et phase de Gouy. La divergence du champ transverse crée une petite "
      + "composante longitudinale E_z, nulle sur l'axe.",
    en: "The fundamental mode of a laser (TEM₀₀): Gaussian intensity profile of radius w(z), focused to the waist w₀ "
      + "then diverging, curved wavefronts and Gouy phase. The divergence of the transverse field creates a small "
      + "longitudinal component E_z, zero on the axis.",
  },
  references: [
    { label: "Kogelnik & Li, Appl. Opt. 5, 1550 (1966)", href: "https://doi.org/10.1364/AO.5.001550" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
