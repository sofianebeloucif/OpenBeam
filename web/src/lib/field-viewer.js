// Generic viewer: the electric field of a beam on a wavefront, split into components, one 3D panel each.
//
// The fields are computed live by fields.js (the JavaScript port of OpenBeam, checked against the Python
// library by web/test/compare.mjs), so the beam size and the synthetic-chiral option can be changed freely.
// Each panel shows the cycle-averaged intensity of its own component on the wavefront disc and the
// instantaneous field as arrows, both normalized to the panel's maximum at the focus; the resultant panel
// uses the true relative sizes. A beam page only provides a config (see createFieldViewer, src/viewers/*.js).

import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  TWO_PI, toScene, makeDisc, updateDisc, makeAxis, makeArrows, updateArrows, layout, fitCamera,
} from "./scene.js";
import { harmonicFields, modeGeometry, omegaOf } from "./fields.js";
import { initialLang, mountLangToggle, tr, translateStatic } from "./i18n.js";
import { VIEWER_STRINGS as S } from "./strings.js";

const UM = 1e-6;
const BASE_SCALE = 2.5e-6;         // camera presets are given for a beam scale of 2.5 µm
const MODES = {
  fixed: { camera: [-7, 6.5, 13], fov: 30, arrow: 0.4 },
  moving: { camera: [-16, 11.5, 27], fov: 26, arrow: 0.6 },
};
const RINGS = [0.35, 0.7, 1.05, 1.4]; // arrow rings, in units of the beam scale
const AZIMUTHS = 12;
const TAU0 = Math.PI / 4;          // phase of the fundamental on the travelling wavefront
const RATIOS = [0.01, 0.03, 0.1, 0.3, 1];

// panels: which harmonics and components they show
const PANELS = [
  { key: "transverse", color: 0x4fd1ff, parts: [[1, [1, 1, 0]]] },
  { key: "ez", color: 0x6cf28a, parts: [[1, [0, 0, 1]]] },
  { key: "second", color: 0xffd84f, parts: [[2, [1, 1, 1]]], chiralOnly: true },
  { key: "total", color: 0xffffff, parts: [[1, [1, 1, 1]], [2, [1, 1, 1]]] },
];

const $ = (id) => document.getElementById(id);

function element(tag, { dataset, ...props } = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  Object.assign(node.dataset, dataset); // dataset itself is read-only
  node.append(...children);
  return node;
}

const percent = (x) => (x >= 0.095 ? (100 * x).toFixed(0) : (100 * x).toPrecision(2));

/**
 * config = {
 *   title, about: {fr, en}, references: [{ label, href }],
 *   spec: (variantId, size) => ({ lambda, w0, mode }),   // beam spec of fields.js (SI units)
 *   variants: { label: {fr, en}, options: [{ id, label: {fr, en} }] },
 *   size: { label: {fr, en}, min, max, step, value, format: (v) => string },  // e.g. the waist in µm
 *   cameras: { fixed: [x, y, z], moving: [x, y, z] },    // optional, for a beam scale of 2.5 µm
 * }
 */
export function createFieldViewer(config) {
  const params = new URLSearchParams(window.location.search);
  const variantIds = config.variants.options.map((o) => o.id);
  const state = {
    lang: initialLang(),
    mode: "fixed",
    variant: variantIds.includes(params.get("variant")) ? params.get("variant") : variantIds[0],
    size: config.size.value,
    chiral: params.get("chiral") === "1",
    ratioIndex: 0,
    psi: 1.94 * Math.PI,
    playing: true,
    tau: 0,          // w t, fixed mode
    s: 0,            // position along the path in [0, 1], moving mode
    periodsPerSecond: 0.5,
    crossingSeconds: 10,
    visible: Object.fromEntries(PANELS.map((p) => [p.key, true])),
  };
  const modes = Object.fromEntries(Object.entries(MODES).map(([m, cfg]) => [m, { ...cfg,
    camera: config.cameras?.[m] ?? cfg.camera }]));

  // ---------- beam (rebuilt when a parameter changes) ----------

  let beam;
  function rebuild() {
    const spec = config.spec(state.variant, state.size);
    if (state.chiral) spec.chiral = { ratio: RATIOS[state.ratioIndex], psi: state.psi };
    const geometry = modeGeometry(spec);
    const scale0 = geometry.scale(0);
    const zHalf = 1.5 * geometry.zUnit.value;
    const previous = beam;
    beam = {
      spec, geometry, scale0, zHalf,
      omega: omegaOf(spec),
      zScale: (9 * (scale0 / BASE_SCALE)) / (zHalf / UM), // scene units per µm along z in "moving" mode
      ...focusData(spec, geometry, scale0),
    };
    if (previous) camera.position.multiplyScalar(scale0 / previous.scale0);
    rebuildExtras();
  }

  function anchors(size) {
    const out = [[0, 0]];
    RINGS.forEach((r) => { for (let j = 0; j < AZIMUTHS; j++) out.push([r * size, (TWO_PI * j) / AZIMUTHS]); });
    return out; // [rho, phi]
  }

  const vertexPoints = () => panels[0].disc.userData.points; // [r in units of the scale, phi]

  // per-panel intensity at the disc vertices: sum over the panel's parts of |E_c|^2
  function panelIntensities(fieldsAt) {
    return PANELS.map((p) => fieldsAt.map((fields) => p.parts.reduce((acc, [n, mask]) => {
      const E = fields[n];
      return E ? acc + mask.reduce((a, m, c) => a + m * (E[c][0] ** 2 + E[c][1] ** 2), 0) : acc;
    }, 0)));
  }

  function discFields(spec, size, z) {
    return vertexPoints().map(([r, phi]) => harmonicFields(spec, r * size * Math.cos(phi), r * size * Math.sin(phi), z));
  }

  function focusData(spec, geometry, scale0) {
    const intensities = panelIntensities(discFields(spec, scale0, 0));
    const peaks = intensities.map((values) => Math.max(...values) || 1);
    const points = anchors(scale0);
    return {
      peaks,                                              // per panel, at the focus
      amplitudes: peaks.map(Math.sqrt),
      focusLevels: intensities.map((values, k) => values.map((v) => v / peaks[k])),
      focusAnchors: points.map(([rho, phi]) => [rho * Math.cos(phi), rho * Math.sin(phi), 0]),
      focusPhasors: points.map(([rho, phi]) => harmonicFields(spec, rho * Math.cos(phi), rho * Math.sin(phi), 0)),
    };
  }

  // real field of each panel at one point, from complex phasors at the phase tau = w t
  function panelVectors(fields, tau) {
    return PANELS.map((p) => p.parts.reduce((acc, [n, mask]) => {
      const E = fields[n];
      if (!E) return acc;
      const c = Math.cos(n * tau), s = Math.sin(n * tau);
      return acc.map((a, k) => a + mask[k] * (E[k][0] * c + E[k][1] * s)); // Re[E e^{-i n tau}]
    }, [0, 0, 0]));
  }

  // ---------- page ----------

  function buildControls() {
    const chips = $("view-chips");
    PANELS.forEach((p) => {
      const id = `view-${p.key}`;
      const dot = element("span", { className: "dot" });
      dot.style.background = `#${p.color.toString(16).padStart(6, "0")}`;
      chips.append(
        element("input", { type: "checkbox", id, checked: true }),
        element("label", { htmlFor: id, id: `chip-${p.key}` }, dot, element("span", { dataset: { chip: p.key } })),
      );
      $(id).addEventListener("change", (e) => {
        const others = PANELS.some((q) => q.key !== p.key && state.visible[q.key] && shown(q));
        if (!e.target.checked && !others) { e.target.checked = true; return; } // keep at least one view
        state.visible[p.key] = e.target.checked;
      });
    });

    const group = $("variants");
    group.hidden = false;
    config.variants.options.forEach((o) => {
      const id = `variant-${o.id}`;
      group.querySelector(".segmented").append(
        element("input", { type: "radio", name: "variant", id, checked: o.id === state.variant }),
        element("label", { htmlFor: id, dataset: { variant: o.id } }),
      );
      $(id).addEventListener("change", () => { state.variant = o.id; rebuild(); applyLanguage(); });
    });

    const size = element("input", { type: "range", id: "size", min: config.size.min, max: config.size.max,
      step: config.size.step, value: state.size });
    const sizeValue = element("span", { className: "value", id: "size-value" });
    size.addEventListener("input", () => { state.size = +size.value; rebuild(); applyLanguage(); });
    $("params").append(element("div", { className: "group" },
      element("label", { htmlFor: "size", id: "size-label" }), size, sizeValue));

    const chiral = element("input", { type: "checkbox", id: "chiral", checked: state.chiral });
    const ratio = element("input", { type: "range", id: "ratio", min: 0, max: RATIOS.length - 1, step: 1, value: 0 });
    const psi = element("input", { type: "range", id: "psi", min: 0, max: 2, step: 0.01, value: state.psi / Math.PI });
    chiral.addEventListener("change", () => { state.chiral = chiral.checked; rebuild(); applyLanguage(); });
    ratio.addEventListener("input", () => { state.ratioIndex = +ratio.value; rebuild(); applyLanguage(); });
    psi.addEventListener("input", () => { state.psi = +psi.value * Math.PI; rebuild(); applyLanguage(); });
    $("params").append(
      element("div", { className: "group chiral-toggle" }, chiral, element("label", { htmlFor: "chiral", dataset: { i18n: "chiral" } })),
      element("div", { className: "group chiral-only" }, element("label", { htmlFor: "ratio", dataset: { i18n: "ratio" } }), ratio,
        element("span", { className: "value", id: "ratio-value" })),
      element("div", { className: "group chiral-only" }, element("label", { htmlFor: "psi", dataset: { i18n: "psi" } }), psi,
        element("span", { className: "value", id: "psi-value" })),
    );

    const frames = $("frames");
    PANELS.forEach((p) => frames.append(
      element("div", { className: "frame", id: `frame-${p.key}` }, element("div", { className: "label", id: `label-${p.key}` }))));
  }

  const shown = (p) => !p.chiralOnly || state.chiral;

  function panelTitles() {
    const L = state.lang, [amp] = [beam.amplitudes];
    const rel = (k) => percent(amp[k] / amp[0]);
    const titles = {
      transverse: S.titleTransverse[L],
      ez: S.titleEz[L](rel(1)),
      second: S.titleSecond[L](rel(2)),
      total: S.titleTotal[L],
    };
    let index = 0;
    return Object.fromEntries(PANELS.map((p) => [p.key, shown(p) && state.visible[p.key] ? `${++index}. ${titles[p.key]}` : ""]));
  }

  function applyLanguage() {
    const L = state.lang;
    translateStatic(S, L);
    document.title = `${tr(config.title, L)} · OpenBeam`;
    $("beam-title").textContent = tr(config.title, L);
    $("back").title = tr(S.backTitle, L);
    document.querySelectorAll("[data-chip]").forEach((el) => { el.textContent = tr(S.chips[el.dataset.chip], L); });
    $("variants-title").textContent = tr(config.variants.label, L);
    document.querySelectorAll("[data-variant]").forEach((el) => {
      el.textContent = tr(config.variants.options.find((o) => o.id === el.dataset.variant).label, L);
    });
    $("size-label").textContent = tr(config.size.label, L);
    $("size-value").textContent = config.size.format(state.size);
    $("ratio-value").textContent = `${RATIOS[state.ratioIndex]}`;
    $("psi-value").textContent = `${(state.psi / Math.PI).toFixed(2)}π`;
    document.querySelectorAll(".chiral-only").forEach((e) => (e.hidden = !state.chiral));
    $("chip-second").hidden = !state.chiral;
    $("play").textContent = tr(state.playing ? S.pause : S.play, L);
    $("speed-fixed-value").textContent = S.periodsPerSecond[L](state.periodsPerSecond);
    $("speed-moving-value").textContent = S.crossing[L](state.crossingSeconds);
    $("mode-help").textContent = state.mode === "fixed"
      ? S.helpFixed[L]((TWO_PI / beam.omega / 1e-15).toFixed(2)) : tr(S.helpMoving, L);
    $("about-text").textContent = [tr(config.about, L), state.chiral ? tr(S.chiralAbout, L) : "",
      tr(S.controlsHelp, L), tr(S.computedBy, L)].filter(Boolean).join(" ");
    const refs = $("references");
    refs.replaceChildren(element("strong", { textContent: `${tr(S.references, L)} : ` }));
    const references = [...config.references, ...(state.chiral ? S.chiralReferences : [])];
    references.forEach((ref, k) => {
      if (k) refs.append(" · ");
      refs.append(element("a", { href: ref.href, textContent: ref.label }));
    });
  }

  // ---------- three.js ----------

  const canvas = $("view");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setScissorTest(true);
  renderer.setClearColor(0x000000);
  renderer.autoClear = false;

  const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 500);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;

  buildControls();
  const panels = PANELS.map((panel) => {
    const scene = new THREE.Scene();
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const light = new THREE.DirectionalLight(0xffffff, 1.6);
    light.position.set(-5, 10, 12);
    scene.add(light);
    const disc = makeDisc();
    const arrows = makeArrows(1 + RINGS.length * AZIMUTHS, panel.color);
    const extras = new THREE.Group();
    scene.add(disc, arrows, extras);
    return { ...panel, scene, disc, arrows, extras, frame: $(`frame-${panel.key}`), label: $(`label-${panel.key}`) };
  });

  function rebuildExtras() {
    const f = beam.scale0 / BASE_SCALE;
    panels.forEach((p) => {
      p.extras.clear();
      if (state.mode === "moving") {
        const zs = Array.from({ length: 120 }, (_, i) => -beam.zHalf + (2 * beam.zHalf * i) / 119);
        const profile = zs.map((z) => new THREE.Vector2(beam.geometry.ringRadius(z) / UM, (z / UM) * beam.zScale));
        const lathe = new THREE.LatheGeometry(profile, 72);
        lathe.rotateZ(-Math.PI / 2); // lathe axis y -> scene x (physical z)
        p.extras.add(new THREE.Mesh(lathe, new THREE.MeshBasicMaterial({
          color: 0xff5a36, transparent: true, opacity: 0.07, depthWrite: false, side: THREE.DoubleSide,
        })));
        const axis = makeAxis((1.1 * (beam.zHalf / UM) * beam.zScale) / f);
        axis.scale.setScalar(f);
        p.extras.add(axis);
      } else {
        const axis = makeAxis(4);
        axis.scale.setScalar(f);
        p.extras.add(axis);
      }
    });
  }

  function setMode(mode) {
    state.mode = mode;
    if (window.location.hash !== `#${mode}`) history.replaceState(null, "", `${window.location.search}#${mode}`);
    camera.position.set(...modes[mode].camera).multiplyScalar(beam.scale0 / BASE_SCALE);
    controls.target.set(0, 0, 0);
    controls.update();
    rebuildExtras();
    document.querySelectorAll(".fixed-only").forEach((e) => (e.hidden = mode !== "fixed"));
    document.querySelectorAll(".moving-only").forEach((e) => (e.hidden = mode !== "moving"));
    applyLanguage();
    syncSlider();
  }

  function frame() {
    const cfg = modes[state.mode];
    if (state.mode === "fixed") {
      $("readout").textContent = `t = ${(state.tau / beam.omega / 1e-15).toFixed(2)} fs`;
      return {
        size: beam.scale0, zScene: 0, levels: beam.focusLevels,
        anchors: beam.focusAnchors,
        vectors: beam.focusPhasors.map((fields) => panelVectors(fields, state.tau)),
        arrow: cfg.arrow,
      };
    }
    const { geometry, spec } = beam;
    const z = -beam.zHalf + 2 * beam.zHalf * state.s;
    const size = geometry.scale(z);
    const target = geometry.phase(0, z, 0);
    const tau = target - TAU0;
    const points = anchors(size).map(([rho, phi]) => {
      const x = rho * Math.cos(phi), y = rho * Math.sin(phi);
      return [x, y, z + (target - geometry.phase(rho, z, phi)) / geometry.k]; // on the wavefront
    });
    const intensities = panelIntensities(discFields(spec, size, z));
    const unit = geometry.zUnit;
    $("readout").textContent = `z = ${(z / unit.value).toFixed(2)} ${unit.label}`;
    return {
      size, zScene: (z / UM) * beam.zScale,
      levels: intensities.map((values, k) => values.map((v) => v / beam.peaks[k])),
      anchors: points,
      vectors: points.map(([x, y, zz]) => panelVectors(harmonicFields(spec, x, y, zz), tau)),
      arrow: cfg.arrow,
    };
  }

  function render() {
    const cfg = modes[state.mode];
    const f = frame();
    const zScale = state.mode === "moving" ? beam.zScale : 1;
    const anchors = f.anchors.map(([x, y, z]) => toScene([x / UM, y / UM, z / UM], zScale));
    const titles = panelTitles();
    const width = canvas.clientWidth, height = canvas.clientHeight;
    renderer.setViewport(0, 0, width, height);
    renderer.setScissor(0, 0, width, height);
    renderer.clear();
    const visible = panels.filter((p) => shown(p) && state.visible[p.key]);
    const cells = layout(width, height, visible.length);
    panels.forEach((p) => (p.frame.hidden = !visible.includes(p)));
    visible.forEach((p, k) => {
      const index = PANELS.findIndex((q) => q.key === p.key);
      const c = cells[k];
      Object.assign(p.frame.style, { left: `${c.x}px`, top: `${c.y}px`, width: `${c.w}px`, height: `${c.h}px` });
      p.label.textContent = titles[p.key];
      updateDisc(p.disc, f.size / UM, f.zScene, f.levels[index]);
      // arrows normalized to the panel's amplitude at the focus; the resultant keeps the true relative sizes
      const length = (f.arrow * beam.scale0) / UM / beam.amplitudes[index];
      updateArrows(p.arrows, anchors, f.vectors.map((v) => v[index]), length);
      const yGL = height - c.y - c.h; // WebGL viewports start at the bottom
      renderer.setViewport(c.x, yGL, c.w, c.h);
      renderer.setScissor(c.x, yGL, c.w, c.h);
      fitCamera(camera, cfg.fov, c.w / c.h);
      renderer.render(p.scene, camera);
    });
  }

  // ---------- controls ----------

  const slider = $("position");
  function syncSlider() {
    slider.value = state.mode === "fixed" ? ((state.tau / TWO_PI) % 1) * 1000 : state.s * 1000;
  }

  $("mode-fixed").addEventListener("change", () => setMode("fixed"));
  $("mode-moving").addEventListener("change", () => setMode("moving"));
  $("play").addEventListener("click", () => {
    state.playing = !state.playing;
    $("play").textContent = tr(state.playing ? S.pause : S.play, state.lang);
  });
  slider.addEventListener("input", () => {
    const u = slider.value / 1000;
    if (state.mode === "fixed") state.tau = u * TWO_PI;
    else state.s = u;
  });
  $("speed-fixed").addEventListener("input", (e) => {
    state.periodsPerSecond = +e.target.value;
    $("speed-fixed-value").textContent = S.periodsPerSecond[state.lang](state.periodsPerSecond);
  });
  $("speed-moving").addEventListener("input", (e) => {
    state.crossingSeconds = +e.target.value;
    $("speed-moving-value").textContent = S.crossing[state.lang](state.crossingSeconds);
  });
  $("reset-view").addEventListener("click", () => setMode(state.mode));
  $("settings-toggle").addEventListener("click", () => {
    const open = document.body.classList.toggle("settings-open");
    $("settings-toggle").setAttribute("aria-expanded", String(open));
  });
  mountLangToggle($("lang"), state.lang, (lang) => { state.lang = lang; applyLanguage(); });

  let last = performance.now();
  function loop(now) {
    const dt = Math.min(Math.max((now - last) / 1000, 0), 0.1);
    last = now;
    if (state.playing) {
      if (state.mode === "fixed") state.tau = (state.tau + TWO_PI * state.periodsPerSecond * dt) % TWO_PI;
      else state.s = (state.s + dt / state.crossingSeconds) % 1;
      syncSlider();
    }
    controls.update();
    render();
    requestAnimationFrame(loop);
  }

  const resize = () => renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  new ResizeObserver(resize).observe(canvas);
  resize();
  if (window.innerWidth < 760) $("about").open = false;

  rebuild();
  function modeFromHash() {
    const mode = window.location.hash === "#moving" ? "moving" : "fixed";
    $(`mode-${mode}`).checked = true;
    setMode(mode);
  }
  window.addEventListener("hashchange", modeFromHash);
  modeFromHash();
  requestAnimationFrame(loop);
}
