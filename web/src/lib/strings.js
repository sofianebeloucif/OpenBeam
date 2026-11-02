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
    fr: "Glisser pour tourner, molette ou pincement pour zoomer. Chaque panneau a sa propre échelle : le disque "
      + "montre l'intensité moyenne de sa composante et les flèches son champ instantané, normalisés à leur maximum "
      + "au foyer ; le titre donne l'amplitude relative. La résultante est à l'échelle réelle : réduire le waist "
      + "w₀ (focalisation plus serrée) fait grandir E_z. E_z est calculé au premier ordre au-delà de l'approximation "
      + "paraxiale, valable tant que w₀ reste plus grand que la longueur d'onde.",
    en: "Drag to rotate, scroll or pinch to zoom. Each panel has its own scale: the disc shows the mean intensity of "
      + "its component and the arrows its instantaneous field, normalized to their maximum at the focus; the title "
      + "gives the relative amplitude. The resultant is at true scale: reducing the waist w₀ (tighter focusing) makes "
      + "E_z grow. E_z is computed at first order beyond the paraxial approximation, valid as long as w₀ stays larger "
      + "than the wavelength.",
  },
  computedBy: {
    fr: "Champs calculés par OpenBeam (port JavaScript vérifié contre la bibliothèque Python).",
    en: "Fields computed by OpenBeam (JavaScript port checked against the Python library).",
  },
  license: {
    fr: "OpenBeam, licence MIT. Si vous l'utilisez, merci de le citer (voir CITATION.cff).",
    en: "OpenBeam, MIT license. If you use it, please cite it (see CITATION.cff).",
  },
  chips: {
    transverse: { fr: "E_⊥", en: "E_⊥" },
    ez: { fr: "E_z", en: "E_z" },
    second: { fr: "2ω", en: "2ω" },
    total: { fr: "Résultante", en: "Resultant" },
  },
  titleTransverse: { fr: "Champ transverse E_⊥ (ω)", en: "Transverse field E_⊥ (ω)" },
  titleEz: {
    fr: (p) => `Composante longitudinale E_z : ${p} % de E_⊥`,
    en: (p) => `Longitudinal component E_z: ${p}% of E_⊥`,
  },
  titleSecond: {
    fr: (p) => `Faisceau 2ω, polarisation orthogonale : ${p} % de E_⊥`,
    en: (p) => `2ω beam, orthogonal polarization: ${p}% of E_⊥`,
  },
  titleTotal: { fr: "Résultante (échelle réelle)", en: "Resultant (true scale)" },
  chiral: { fr: "Lumière chirale synthétique (+ 2ω)", en: "Synthetic chiral light (+ 2ω)" },
  ratio: { fr: "I₂ω / Iω", en: "I₂ω / Iω" },
  psi: { fr: "Déphasage ψ₂ω", en: "Phase delay ψ₂ω" },
  chiralAbout: {
    fr: "Lumière chirale synthétique : on ajoute le même faisceau au second harmonique 2ω (waist double, "
      + "polarisation orthogonale, déphasage ψ₂ω). Avec la composante longitudinale du faisceau focalisé, la pointe "
      + "du champ décrit en chaque point une figure de Lissajous 3D qui peut être chirale (lumière localement "
      + "chirale) ; un déphasage de π revient à échanger les énantiomères.",
    en: "Synthetic chiral light: the same beam is added at the second harmonic 2ω (twice the waist, orthogonal "
      + "polarization, phase delay ψ₂ω). With the longitudinal component of the focused beam, the tip of the field "
      + "draws at each point a 3D Lissajous figure that can be chiral (locally chiral light); a π delay amounts to "
      + "exchanging the enantiomers.",
  },
  chiralReferences: [
    { label: "Ayuso et al., Nat. Photon. 13, 866 (2019)", href: "https://doi.org/10.1038/s41566-019-0531-2" },
    { label: "Mayer et al., Nat. Photon. (2024)", href: "https://doi.org/10.1038/s41566-024-01499-8" },
  ],
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
    fr: "Bibliothèque open source OpenBeam (licence MIT) : les champs sont calculés par OpenBeam et affichés avec "
      + "Three.js. Si vous l'utilisez, merci de le citer (voir CITATION.cff sur GitHub).",
    en: "Open-source library OpenBeam (MIT license): the fields are computed by OpenBeam and rendered with Three.js. "
      + "If you use it, please cite it (see CITATION.cff on GitHub).",
  },
  chiralNote: {
    fr: "Chaque faisceau peut aussi être combiné à son second harmonique pour former de la lumière chirale synthétique.",
    en: "Each beam can also be combined with its second harmonic to form synthetic chiral light.",
  },
  noscript: {
    fr: "Cette page a besoin de JavaScript pour afficher la liste des faisceaux.",
    en: "This page needs JavaScript to list the beams.",
  },
};
