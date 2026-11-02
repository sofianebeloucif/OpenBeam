// Registry of the beams shown on the hub. To add a beam:
//   1. the beam in the Python library (src/openbeam/beams) and in its JavaScript port (src/lib/fields.js),
//      with a case in test/reference.py so that `npm test` checks that both agree;
//   2. web/src/viewers/<id>.js (a createFieldViewer config) and web/<id>/index.html
//      (copy an existing viewer page and change its title and script name);
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
    tags: [{ fr: "mode fondamental", en: "fundamental mode" },
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
      fr: "Modes de Laguerre-Gauss dont la phase tourne autour de l'axe : front d'onde hélicoïdal, moment "
        + "angulaire orbital ℓħ par photon, intensité nulle sur l'axe (charges ℓ = 1, 2, 3).",
      en: "Laguerre-Gauss modes whose phase winds around the axis: helical wavefront, orbital angular momentum "
        + "ℓħ per photon, zero intensity on the axis (charges ℓ = 1, 2, 3).",
    },
    tags: [{ fr: "moment angulaire orbital", en: "orbital angular momentum" },
      { fr: "singularité de phase", en: "phase singularity" }],
    references: [{ label: "Allen et al., Phys. Rev. A (1992)", href: "https://doi.org/10.1103/PhysRevA.45.8185" }],
    href: "vortex/index.html",
    thumbnail: "assets/thumbs/vortex.jpg",
    status: "ready",
  },
  {
    id: "vector",
    title: { fr: "Faisceaux vectoriels", en: "Vector beams" },
    summary: {
      fr: "Polarisation radiale ou azimutale : la direction du champ change d'un point à l'autre du faisceau. "
        + "Fortement focalisé, le faisceau radial acquiert une composante longitudinale intense sur l'axe.",
      en: "Radial or azimuthal polarization: the field direction changes across the beam. Tightly focused, "
        + "the radial beam acquires a strong longitudinal component on the axis.",
    },
    tags: [{ fr: "polarisation radiale / azimutale", en: "radial / azimuthal polarization" },
      { fr: "singularité de polarisation", en: "polarization singularity" }],
    references: [
      { label: "Zhan, Adv. Opt. Photon. (2009)", href: "https://doi.org/10.1364/AOP.1.000001" },
      { label: "Dorn et al., PRL (2003)", href: "https://doi.org/10.1103/PhysRevLett.91.233901" },
    ],
    href: "vector/index.html",
    thumbnail: "assets/thumbs/vector.jpg",
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
    tags: [{ fr: "non diffractant", en: "non-diffracting" }, { fr: "cône d'ondes planes", en: "cone of plane waves" }],
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
      fr: "Lumière chirale synthétique à partir de faisceaux vectoriels : un faisceau radial à ω fortement focalisé "
        + "et un faisceau azimutal à 2ω. Le champ électrique se tord en 3D et devient localement chiral.",
      en: "Synthetic chiral light from vector beams: a tightly focused radial beam at ω and an azimuthal beam at 2ω. "
        + "The electric field twists in 3D and becomes locally chiral.",
    },
    tags: [{ fr: "lumière chirale synthétique", en: "synthetic chiral light" }, { fr: "deux couleurs", en: "two colours" }],
    references: [
      { label: "Rodriguez et al., arXiv (2026)", href: "https://arxiv.org/abs/2610.17111" },
      { label: "Ayuso et al., Nat. Photon. (2019)", href: "https://doi.org/10.1038/s41566-019-0531-2" },
    ],
    href: "vector/index.html?variant=radial&chiral=1",
    thumbnail: "assets/thumbs/chiral-vector.jpg",
    status: "ready",
  },
];
