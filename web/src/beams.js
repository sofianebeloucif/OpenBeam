// Registry of the beams shown on the hub. To add a beam:
//   1. web/exporters/<name>.py exporting its data, registered in web/exporters/__init__.py;
//   2. web/src/viewers/<id>.js (a createComponentViewer config) and web/<id>/index.html
//      (copy an existing viewer page and change its title and script names);
//   3. an entry below with status "ready" and a thumbnail in web/assets/thumbs/.
// Texts are { fr, en }.

export const BEAMS = [
  {
    id: "gaussian",
    title: { fr: "Faisceau gaussien", en: "Gaussian beam" },
    summary: {
      fr: "Le mode fondamental d'un laser (TEM₀₀) : profil d'intensité gaussien, focalisation et divergence, "
        + "courbure des fronts d'onde et phase de Gouy, en polarisation linéaire ou circulaire.",
      en: "The fundamental mode of a laser (TEM₀₀): Gaussian intensity profile, focusing and divergence, "
        + "wavefront curvature and Gouy phase, with linear or circular polarization.",
    },
    tags: [{ fr: "scalaire", en: "scalar" }, { fr: "mode fondamental", en: "fundamental mode" },
      { fr: "polarisation linéaire / circulaire", en: "linear / circular polarization" }],
    references: [{ label: "Kogelnik & Li, Appl. Opt. (1966)", href: "https://doi.org/10.1364/AO.5.001550" }],
    href: "gaussian/index.html",
    thumbnail: "assets/thumbs/gaussian.jpg",
    status: "ready",
  },
  {
    id: "vortex",
    title: { fr: "Faisceaux vortex", en: "Vortex beams" },
    summary: {
      fr: "Vortex scalaires, dont la phase tourne autour de l'axe (front d'onde hélicoïdal, moment angulaire "
        + "orbital), et vortex vectoriels, dont c'est la polarisation qui tourne (radiale, azimutale).",
      en: "Scalar vortices, whose phase winds around the axis (helical wavefront, orbital angular momentum), "
        + "and vector vortices, whose polarization winds instead (radial, azimuthal).",
    },
    tags: [{ fr: "moment angulaire orbital", en: "orbital angular momentum" },
      { fr: "vortex vectoriel", en: "vector vortex" }, { fr: "singularités", en: "singularities" }],
    references: [
      { label: "Allen et al., Phys. Rev. A (1992)", href: "https://doi.org/10.1103/PhysRevA.45.8185" },
      { label: "Rosales-Guzmán et al., J. Opt. (2018)", href: "https://doi.org/10.1088/2040-8986/aaeb7d" },
    ],
    href: "vortex/index.html",
    thumbnail: "assets/thumbs/vortex.jpg",
    status: "ready",
  },
  {
    id: "bessel",
    title: { fr: "Faisceau de Bessel", en: "Bessel beam" },
    summary: {
      fr: "Un cône d'ondes planes qui interfèrent : un cœur fin qui ne s'étale pas sur une longue distance "
        + "(faisceau quasi non diffractant), en version physique de Bessel-Gauss, d'ordre 0 ou 1.",
      en: "A cone of interfering plane waves: a narrow core that does not spread over a long distance "
        + "(quasi non-diffracting beam), in its physical Bessel-Gauss form, of order 0 or 1.",
    },
    tags: [{ fr: "non diffractant", en: "non-diffracting" }, { fr: "Bessel-Gauss", en: "Bessel-Gauss" },
      { fr: "cône d'ondes planes", en: "cone of plane waves" }],
    references: [
      { label: "Durnin et al., PRL (1987)", href: "https://doi.org/10.1103/PhysRevLett.58.1499" },
      { label: "Gori et al., Opt. Commun. (1987)", href: "https://doi.org/10.1016/0030-4018(87)90276-8" },
    ],
    href: "bessel/index.html",
    thumbnail: "assets/thumbs/bessel.jpg",
    status: "ready",
  },
  {
    id: "chiral-vector",
    title: { fr: "Faisceau vectoriel chiral", en: "Chiral vector beam" },
    summary: {
      fr: "Deux faisceaux vortex vectoriels, radial à ω (fortement focalisé) et azimutal à 2ω : le champ "
        + "électrique se tord en 3D et devient localement chiral.",
      en: "Two vector vortex beams, radial at ω (tightly focused) and azimuthal at 2ω: the electric field "
        + "twists in 3D and becomes locally chiral.",
    },
    tags: [{ fr: "vortex vectoriel", en: "vector vortex" }, { fr: "deux couleurs", en: "two colours" },
      { fr: "localement chiral", en: "locally chiral" }],
    references: [
      { label: "Rodriguez et al., arXiv (2026)", href: "https://arxiv.org/abs/2610.17111" },
      { label: "Ayuso et al., Nat. Photon. (2019)", href: "https://doi.org/10.1038/s41566-019-0531-2" },
    ],
    href: "chiral-vector/index.html",
    thumbnail: "assets/thumbs/chiral-vector.jpg",
    status: "ready",
  },
];
