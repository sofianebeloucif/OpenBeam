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
    reference: { label: "Kogelnik & Li, Appl. Opt. (1966)", href: "https://doi.org/10.1364/AO.5.001550" },
    href: "gaussian/index.html",
    thumbnail: "assets/thumbs/gaussian.jpg",
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
    reference: { label: "Ayuso et al., Nat. Photon. (2019)", href: "https://doi.org/10.1038/s41566-019-0531-2" },
    href: "chiral-vector/index.html",
    thumbnail: "assets/thumbs/chiral-vector.jpg",
    status: "ready",
  },
];
