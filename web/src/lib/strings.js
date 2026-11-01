// Interface texts shared by the pages, in French and English.

export const VIEWER_STRINGS = {
  back: { fr: "← OpenBeam", en: "← OpenBeam" },
  backTitle: { fr: "Tous les faisceaux", en: "All beams" },
  settings: { fr: "Réglages", en: "Settings" },
  modeFixed: { fr: "Front fixe au foyer", en: "Wavefront at the focus" },
  modeMoving: { fr: "Front qui avance", en: "Travelling wavefront" },
  views: { fr: "Vues", en: "Views" },
  play: { fr: "Lecture", en: "Play" },
  pause: { fr: "Pause", en: "Pause" },
  position: { fr: "Temps ou position", en: "Time or position" },
  speed: { fr: "Vitesse", en: "Speed" },
  periodsPerSecond: { fr: (v) => `${v.toFixed(2)} période/s`, en: (v) => `${v.toFixed(2)} period/s` },
  crossing: { fr: (v) => `traversée en ${v} s`, en: (v) => `crossing in ${v} s` },
  reset: { fr: "Recentrer la vue", en: "Reset view" },
  about: { fr: "À propos de cette vue", en: "About this view" },
  references: { fr: "Références", en: "References" },
  helpFixed: {
    fr: (T) => `Le front d'onde au foyer : le champ oscille au cours du temps (une période ≈ ${T} fs, ralentie).`,
    en: (T) => `The wavefront at the focus: the field oscillates in time (one period ≈ ${T} fs, slowed down).`,
  },
  helpMoving: {
    fr: "Un front d'onde traverse le foyer en transportant son champ. Sur son propre front d'onde, la phase de l'onde "
      + "est constante : les flèches n'oscillent pas, mais la taille du faisceau, l'amplitude et la phase relative "
      + "des composantes changent (courbure, phase de Gouy).",
    en: "A wavefront crosses the focus, carrying its field. On its own wavefront the phase of the wave is constant: "
      + "the arrows do not oscillate, but the beam size, the amplitude and the relative phase of the components "
      + "change (curvature, Gouy phase).",
  },
  controlsHelp: {
    fr: "Glisser pour tourner, molette ou pincement pour zoomer. Les composantes faibles sont agrandies à l'écran "
      + "(curseurs) ; la résultante est la somme exacte des composantes affichées.",
    en: "Drag to rotate, scroll or pinch to zoom. Weak components are magnified on screen (sliders); the resultant "
      + "is the exact sum of the components shown.",
  },
  computedBy: { fr: "Champs calculés avec OpenBeam.", en: "Fields computed with OpenBeam." },
};

export const HUB_STRINGS = {
  eyebrow: { fr: "OpenBeam", en: "OpenBeam" },
  heading: { fr: "Visualiser la lumière structurée", en: "Visualizing structured light" },
  lede: {
    fr: "Des faisceaux laser calculés numériquement et animés en 3D : champ électrique, polarisation, fronts d'onde. "
      + "Choisissez un faisceau à explorer.",
    en: "Laser beams computed numerically and animated in 3D: electric field, polarization, wavefronts. "
      + "Pick a beam to explore.",
  },
  beamsLabel: { fr: "Faisceaux", en: "Beams" },
  explore: { fr: "Explorer", en: "Explore" },
  soon: { fr: "Bientôt", en: "Coming soon" },
  open: { fr: "Ouvrir :", en: "Open:" },
  footer: {
    fr: "Bibliothèque open source OpenBeam : les champs sont calculés en Python puis affichés avec Three.js.",
    en: "Open-source library OpenBeam: the fields are computed in Python and rendered with Three.js.",
  },
  noscript: {
    fr: "Cette page a besoin de JavaScript pour afficher la liste des faisceaux.",
    en: "This page needs JavaScript to list the beams.",
  },
};
