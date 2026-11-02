// Fundamental Gaussian beam (TEM00), linear or circular polarization.

import { createFieldViewer } from "../lib/field-viewer.js";

const POLARIZATION = { linear: [[1, 0], [0, 0]], circular: [[Math.SQRT1_2, 0], [0, Math.SQRT1_2]] };

createFieldViewer({
  title: { fr: "Faisceau gaussien", en: "Gaussian beam" },
  spec: (variant, w0um) => ({ lambda: 632.8e-9, w0: w0um * 1e-6, mode: { type: "lg", l: 0, jones: POLARIZATION[variant] } }),
  variants: {
    label: { fr: "Polarisation", en: "Polarization" },
    options: [
      { id: "linear", label: { fr: "linéaire (x)", en: "linear (x)" } },
      { id: "circular", label: { fr: "circulaire", en: "circular" } },
    ],
  },
  size: { label: { fr: "Waist w₀", en: "Waist w₀" }, min: 0.8, max: 6, step: 0.1, value: 2.5, format: (v) => `${v.toFixed(1)} µm` },
  cameras: { fixed: [-4.6, 4.3, 8.6], moving: [-12, 8.6, 20] },
  about: {
    fr: "Le mode fondamental d'un laser (TEM₀₀, λ = 632,8 nm) : profil d'intensité gaussien de rayon w(z), focalisé "
      + "au waist w₀ puis divergent, fronts d'onde courbés et phase de Gouy. La divergence du champ transverse crée "
      + "une composante longitudinale E_z ∝ x E_x : nulle sur l'axe et partout où E_x est maximal, elle forme deux "
      + "lobes de part et d'autre de l'axe, le long de la polarisation (un anneau en polarisation circulaire).",
    en: "The fundamental mode of a laser (TEM₀₀, λ = 632.8 nm): Gaussian intensity profile of radius w(z), focused "
      + "to the waist w₀ then diverging, curved wavefronts and Gouy phase. The divergence of the transverse field "
      + "creates a longitudinal component E_z ∝ x E_x: zero on the axis and wherever E_x is largest, it forms two "
      + "lobes on either side of the axis, along the polarization (a ring for circular polarization).",
  },
  references: [
    { label: "Kogelnik & Li, Appl. Opt. 5, 1550 (1966)", href: "https://doi.org/10.1364/AO.5.001550" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
