// Generic viewer: a beam's electric field on a wavefront, split into components, one 3D panel each.
//
// Data (window.BEAM_DATA) come from web/exporters/common.py: for each variant, complex phasors at
// the focus ("fixed") and real fields on a travelling wavefront ("moving"), per harmonic.
// A beam viewer only provides a config (see createComponentViewer and src/viewers/*.js).

import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  TWO_PI, toScene, makeDisc, updateDisc, makeAxis, makeArrows, updateArrows, layout, fitCamera,
} from "./scene.js";
import { initialLang, mountLangToggle, tr, translateStatic } from "./i18n.js";
import { VIEWER_STRINGS as S } from "./strings.js";

const MODES = {
  fixed: { zScale: 1, arrowLength: 1.0, camera: [-7, 6.5, 13], fov: 30 },
  moving: { zScale: 0.15, arrowLength: 1.5, camera: [-16, 11.5, 27], fov: 26 },
};

const $ = (id) => document.getElementById(id);

function element(tag, { dataset, ...props } = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  Object.assign(node.dataset, dataset); // dataset itself is read-only
  node.append(...children);
  return node;
}

/**
 * config = {
 *   title: {fr, en},
 *   panels: [{ key, color, title: {fr, en} | (boost, lang) => string, chip: {fr, en},
 *              parts: [{ harmonic: "1", mask: [1, 1, 0], boost: "z" }] }   // or sum: true for the resultant
 *   boosts: [{ key, label, min, max, value }],          // on-screen magnification of weak components
 *   variants: { label: {fr, en}, options: [{ id, label: {fr, en} }] },  // optional
 *   intensity: (rhoOverW, w, w0, variant) => number,     // 1 at the brightest point of the focus
 *   envelopeRadius: (w, variant) => number,              // radius of the faint beam envelope
 *   about: {fr, en}, references: [{ label, href }],
 *   modes: { fixed: {...}, moving: {...} },              // optional overrides of MODES (camera, arrow length)
 * }
 */
export function createComponentViewer(config) {
  const DATA = window.BEAM_DATA;
  const modes = Object.fromEntries(Object.entries(MODES).map(([m, cfg]) => [m, { ...cfg, ...config.modes?.[m] }]));
  const variantIds = Object.keys(DATA.variants);
  const state = {
    lang: initialLang(),
    mode: "fixed",
    variant: variantIds[0],
    playing: true,
    tau: 0,                 // w t, fixed mode
    s: 0,                   // position along the path in [0, 1], moving mode
    periodsPerSecond: 0.5,
    crossingSeconds: 10,
    boost: Object.fromEntries((config.boosts ?? []).map((b) => [b.key, b.value])),
    visible: Object.fromEntries(config.panels.map((p) => [p.key, true])),
  };
  const variant = () => DATA.variants[state.variant];

  // ---------- field ----------

  const scaled = (v, part) => v.map((x, k) => x * part.mask[k] * (part.boost ? state.boost[part.boost] : 1));

  function fixedVectors(tau) {
    const { harmonics } = variant().fixed;
    const real = (n, i) => {
      const { re, im } = harmonics[n], c = Math.cos(n * tau), s = Math.sin(n * tau);
      // Re[(a + ib) e^{-i n tau}] = a cos(n tau) + b sin(n tau)
      return [0, 1, 2].map((k) => re[i][k] * c + im[i][k] * s);
    };
    return variant().fixed.points.map((_, i) => vectorsAt((part) => scaled(real(+part.harmonic, i), part)));
  }

  function movingFrame(s) {
    const frames = variant().moving;
    const f = s * (frames.length - 1);
    const i = Math.min(Math.floor(f), frames.length - 2);
    const a = f - i, A = frames[i], B = frames[i + 1];
    const lerp = (u, v) => u + a * (v - u);
    const lerp3 = (u, v) => [lerp(u[0], v[0]), lerp(u[1], v[1]), lerp(u[2], v[2])];
    return {
      z: lerp(A.z, B.z),
      w: lerp(A.w, B.w),
      points: A.points.map((p, k) => lerp3(p, B.points[k])),
      vectors: A.points.map((_, k) => vectorsAt((part) => scaled(
        lerp3(A.harmonics[part.harmonic][k], B.harmonics[part.harmonic][k]), part))),
    };
  }

  // { panelKey: vector } at one point; the "sum" panel adds up all the others
  function vectorsAt(partValue) {
    const out = {}, total = [0, 0, 0];
    config.panels.filter((p) => !p.sum).forEach((p) => {
      const v = p.parts.reduce((acc, part) => {
        const u = partValue(part);
        return [acc[0] + u[0], acc[1] + u[1], acc[2] + u[2]];
      }, [0, 0, 0]);
      out[p.key] = v;
      total[0] += v[0]; total[1] += v[1]; total[2] += v[2];
    });
    config.panels.filter((p) => p.sum).forEach((p) => { out[p.key] = total; });
    return out;
  }

  const intensity = (r, w) => config.intensity(r, w, DATA.w0_um, state.variant);

  function makeEnvelope(zScale) {
    const profile = variant().moving.map((f) => new THREE.Vector2(config.envelopeRadius(f.w, state.variant), f.z * zScale));
    const lathe = new THREE.LatheGeometry(profile, 72);
    lathe.rotateZ(-Math.PI / 2); // lathe axis y -> scene x (physical z)
    return new THREE.Mesh(lathe, new THREE.MeshBasicMaterial({
      color: 0xff5a36, transparent: true, opacity: 0.07, depthWrite: false, side: THREE.DoubleSide,
    }));
  }

  // ---------- page ----------

  function buildControls() {
    const chips = $("view-chips");
    config.panels.forEach((p) => {
      const id = `view-${p.key}`;
      const dot = element("span", { className: "dot" });
      dot.style.background = `#${p.color.toString(16).padStart(6, "0")}`;
      chips.append(
        element("input", { type: "checkbox", id, checked: true }),
        element("label", { htmlFor: id }, dot, element("span", { className: "chip-text", dataset: { panel: p.key } })),
      );
      $(id).addEventListener("change", (e) => {
        const others = config.panels.some((q) => q.key !== p.key && state.visible[q.key]);
        if (!e.target.checked && !others) { e.target.checked = true; return; } // keep at least one view
        state.visible[p.key] = e.target.checked;
      });
    });

    (config.boosts ?? []).forEach((b) => {
      const id = `boost-${b.key}`;
      const value = element("span", { className: "value", textContent: `×${b.value}` });
      const input = element("input", { type: "range", id, min: b.min, max: b.max, step: 1, value: b.value });
      input.addEventListener("input", () => { state.boost[b.key] = +input.value; value.textContent = `×${input.value}`; });
      $("boosts").append(element("div", { className: "group" },
        element("label", { htmlFor: id, dataset: { boost: b.key } }), input, value));
    });

    if (config.variants && variantIds.length > 1) {
      const group = $("variants");
      group.hidden = false;
      config.variants.options.forEach((o, k) => {
        const id = `variant-${o.id}`;
        group.querySelector(".segmented").append(
          element("input", { type: "radio", name: "variant", id, checked: k === 0 }),
          element("label", { htmlFor: id, dataset: { variant: o.id } }),
        );
        $(id).addEventListener("change", () => { state.variant = o.id; setMode(state.mode); });
      });
    }

    const frames = $("frames");
    config.panels.forEach((p) => frames.append(
      element("div", { className: "frame", id: `frame-${p.key}` }, element("div", { className: "label", id: `label-${p.key}` }))));
  }

  function panelTitle(p) {
    return typeof p.title === "function" ? p.title(state.boost, state.lang) : tr(p.title, state.lang);
  }

  function applyLanguage() {
    const L = state.lang;
    translateStatic(S, L);
    document.title = `${tr(config.title, L)} · OpenBeam`;
    $("beam-title").textContent = tr(config.title, L);
    $("back").title = tr(S.backTitle, L);
    document.querySelectorAll("[data-panel]").forEach((el) => {
      el.textContent = tr(config.panels.find((p) => p.key === el.dataset.panel).chip, L);
    });
    document.querySelectorAll("[data-boost]").forEach((el) => {
      el.textContent = tr(config.boosts.find((b) => b.key === el.dataset.boost).label, L);
    });
    if (config.variants) {
      $("variants-title").textContent = tr(config.variants.label, L);
      document.querySelectorAll("[data-variant]").forEach((el) => {
        el.textContent = tr(config.variants.options.find((o) => o.id === el.dataset.variant).label, L);
      });
    }
    $("play").textContent = tr(state.playing ? S.pause : S.play, L);
    $("speed-fixed-value").textContent = S.periodsPerSecond[L](state.periodsPerSecond);
    $("speed-moving-value").textContent = S.crossing[L](state.crossingSeconds);
    $("mode-help").textContent = state.mode === "fixed"
      ? S.helpFixed[L](DATA.period_fs.toFixed(2)) : tr(S.helpMoving, L);
    $("about-text").textContent = `${tr(config.about, L)} ${tr(S.controlsHelp, L)} ${tr(S.computedBy, L)}`;
    const refs = $("references");
    refs.replaceChildren(element("strong", { textContent: `${tr(S.references, L)} : ` }));
    (config.references ?? []).forEach((ref, k) => {
      if (k) refs.append(" · ");
      refs.append(element("a", { href: ref.href, textContent: ref.label }));
    });
    refs.hidden = !(config.references ?? []).length;
  }

  // ---------- three.js ----------

  const canvas = $("view");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setScissorTest(true);
  renderer.setClearColor(0x000000);
  renderer.autoClear = false;

  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 500);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;

  buildControls();
  const panels = config.panels.map((panel) => {
    const scene = new THREE.Scene();
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const light = new THREE.DirectionalLight(0xffffff, 1.6);
    light.position.set(-5, 10, 12);
    scene.add(light);
    const disc = makeDisc();
    const arrows = makeArrows(variant().fixed.points.length, panel.color);
    const extras = new THREE.Group();
    scene.add(disc, arrows, extras);
    return { ...panel, scene, disc, arrows, extras, frame: $(`frame-${panel.key}`), label: $(`label-${panel.key}`) };
  });

  function setMode(mode) {
    state.mode = mode;
    if (window.location.hash !== `#${mode}`) history.replaceState(null, "", `#${mode}`);
    const cfg = modes[mode];
    panels.forEach((p) => {
      p.extras.clear();
      if (mode === "moving") {
        const half = Math.max(...variant().moving.map((f) => Math.abs(f.z))) * cfg.zScale;
        p.extras.add(makeEnvelope(cfg.zScale), makeAxis(half * 1.1));
      } else {
        p.extras.add(makeAxis(4));
      }
    });
    camera.position.set(...cfg.camera);
    controls.target.set(0, 0, 0);
    controls.update();
    document.querySelectorAll(".fixed-only").forEach((e) => (e.hidden = mode !== "fixed"));
    document.querySelectorAll(".moving-only").forEach((e) => (e.hidden = mode !== "moving"));
    applyLanguage();
    syncSlider();
  }

  function render() {
    const cfg = modes[state.mode];
    let anchors, vectors, w, zScene;
    if (state.mode === "fixed") {
      anchors = variant().fixed.points.map((p) => toScene(p, cfg.zScale));
      vectors = fixedVectors(state.tau);
      w = DATA.w0_um; zScene = 0;
      $("readout").textContent = `t = ${((state.tau / TWO_PI) * DATA.period_fs).toFixed(2)} fs`;
    } else {
      const frame = movingFrame(state.s);
      anchors = frame.points.map((p) => toScene(p, cfg.zScale));
      vectors = frame.vectors;
      w = frame.w; zScene = frame.z * cfg.zScale;
      $("readout").textContent = `z = ${(frame.z / DATA.zr_um).toFixed(2)} z_R`;
    }

    const width = canvas.clientWidth, height = canvas.clientHeight;
    renderer.setViewport(0, 0, width, height);
    renderer.setScissor(0, 0, width, height);
    renderer.clear();
    const shown = panels.filter((p) => state.visible[p.key]);
    const cells = layout(width, height, shown.length);
    panels.forEach((p) => (p.frame.hidden = !state.visible[p.key]));
    shown.forEach((p, k) => {
      const c = cells[k];
      Object.assign(p.frame.style, { left: `${c.x}px`, top: `${c.y}px`, width: `${c.w}px`, height: `${c.h}px` });
      p.label.textContent = panelTitle(p);
      updateDisc(p.disc, w, zScene, intensity);
      updateArrows(p.arrows, anchors, vectors.map((v) => v[p.key]), cfg.arrowLength);
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

  function modeFromHash() {
    const mode = window.location.hash === "#moving" ? "moving" : "fixed";
    $(`mode-${mode}`).checked = true;
    if (mode !== state.mode || !panels[0].extras.children.length) setMode(mode);
  }
  window.addEventListener("hashchange", modeFromHash);
  modeFromHash();
  requestAnimationFrame(loop);
}
