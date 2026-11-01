// Bessel-Gauss beams of order 0 and 1 (quasi non-diffracting). Data: web/exporters/bessel.py.

import { createComponentViewer } from "../lib/component-viewer.js";

// faint cylinder in "travelling wavefront" mode: radius of the core, in units of the arrow scale 6 / k_r
// (first zero of J0 at 2.405 / k_r, bright ring of J1 at 1.841 / k_r)
const CORE = { n0: 2.405 / 6, n1: 1.841 / 6 };

createComponentViewer({
  title: { fr: "Faisceau de Bessel", en: "Bessel beam" },
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
  boosts: [{ key: "z", label: { fr: "E_z", en: "E_z" }, min: 1, max: 15, value: 4 }],
  variants: {
    label: { fr: "Ordre", en: "Order" },
    options: [
      { id: "n0", label: { fr: "J₀ (cœur brillant)", en: "J₀ (bright core)" } },
      { id: "n1", label: { fr: "J₁ (vortex)", en: "J₁ (vortex)" } },
    ],
  },
  intensity: () => 0, // the data carry the exact intensity profile
  envelopeRadius: (w, variant) => CORE[variant] * w,
  // the core is narrower than the other beams: closer camera; z in units of the non-diffracting half-length
  modes: { fixed: { camera: [-4.2, 3.9, 7.8] }, moving: { camera: [-13, 9.4, 22] } },
  zUnit: { um: window.BEAM_DATA.max_range_um, label: "z_max" },
  about: {
    fr: "Faisceau de Bessel-Gauss, polarisé selon x : une fonction de Bessel J_n(k_r ρ) sous une enveloppe gaussienne. "
      + "C'est un cône d'ondes planes (demi-angle ≈ 12° ici) qui interfèrent : le cœur garde le même rayon "
      + "(≈ 2,4 / k_r) sans s'étaler sur toute la zone de recouvrement, ± w₀ k / k_r ≈ ± 40 µm (le cylindre pâle), "
      + "puis se défait. Les anneaux entourant le cœur portent l'énergie qui le reforme. L'ordre 1 a une phase "
      + "hélicoïdale et un axe sombre, comme un vortex.",
    en: "Bessel-Gauss beam polarized along x: a Bessel function J_n(k_r ρ) under a Gaussian envelope. It is a cone "
      + "of plane waves (half-angle ≈ 12° here) that interfere: the core keeps the same radius (≈ 2.4 / k_r) "
      + "without spreading over the whole overlap region, ± w₀ k / k_r ≈ ± 40 µm (the faint cylinder), then "
      + "falls apart. The rings around the core carry the energy that rebuilds it. Order 1 has a helical phase and "
      + "a dark axis, like a vortex.",
  },
  references: [
    { label: "Durnin, Miceli, Eberly, PRL 58, 1499 (1987)", href: "https://doi.org/10.1103/PhysRevLett.58.1499" },
    { label: "Gori, Guattari, Padovani, Opt. Commun. 64, 491 (1987)", href: "https://doi.org/10.1016/0030-4018(87)90276-8" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
