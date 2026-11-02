// Bessel-Gauss beams of order 0 and 1 (quasi non-diffracting), polarized along x.

import { createFieldViewer } from "../lib/field-viewer.js";

const X = [[1, 0], [0, 0]];
const LAMBDA = 632.8e-9;

createFieldViewer({
  title: { fr: "Faisceau de Bessel", en: "Bessel beam" },
  spec: (variant, angleDeg) => ({ lambda: LAMBDA, w0: 8e-6,
    mode: { type: "bessel", n: +variant.slice(1), kr: (2 * Math.PI / LAMBDA) * Math.sin(angleDeg * Math.PI / 180), jones: X } }),
  variants: {
    label: { fr: "Ordre", en: "Order" },
    options: [
      { id: "n0", label: { fr: "J₀ (cœur brillant)", en: "J₀ (bright core)" } },
      { id: "n1", label: { fr: "J₁ (vortex)", en: "J₁ (vortex)" } },
    ],
  },
  size: { label: { fr: "Angle du cône", en: "Cone angle" }, min: 4, max: 25, step: 0.5, value: 12, format: (v) => `${v.toFixed(1)}°` },
  cameras: { fixed: [-4.2, 3.9, 7.8], moving: [-8.5, 6.2, 14.5] },
  about: {
    fr: "Faisceau de Bessel-Gauss (λ = 632,8 nm), polarisé selon x : une fonction de Bessel J_n(k_r ρ) sous une "
      + "enveloppe gaussienne de waist 8 µm. C'est un cône d'ondes planes qui interfèrent : le cœur garde le même "
      + "rayon (≈ 2,4 / k_r) sans s'étaler sur la zone de recouvrement ± w₀ k / k_r (le cylindre pâle), puis se "
      + "défait. Un cône plus ouvert donne un cœur plus fin, une zone plus courte et une composante E_z plus forte "
      + "(deux lobes le long de la polarisation). L'ordre 1 a une phase hélicoïdale et un axe sombre.",
    en: "Bessel-Gauss beam (λ = 632.8 nm) polarized along x: a Bessel function J_n(k_r ρ) under a Gaussian envelope "
      + "of waist 8 µm. It is a cone of interfering plane waves: the core keeps the same radius (≈ 2.4 / k_r) without "
      + "spreading over the overlap region ± w₀ k / k_r (the faint cylinder), then falls apart. A wider cone gives a "
      + "thinner core, a shorter region and a stronger E_z (two lobes along the polarization). Order 1 has a helical "
      + "phase and a dark axis.",
  },
  references: [
    { label: "Durnin, Miceli, Eberly, PRL 58, 1499 (1987)", href: "https://doi.org/10.1103/PhysRevLett.58.1499" },
    { label: "Gori, Guattari, Padovani, Opt. Commun. 64, 491 (1987)", href: "https://doi.org/10.1016/0030-4018(87)90276-8" },
    { label: "Bliokh & Nori, Phys. Rep. 592, 1 (2015)", href: "https://doi.org/10.1016/j.physrep.2015.06.003" },
  ],
});
