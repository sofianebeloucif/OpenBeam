// Three.js building blocks shared by the beam viewers.
//
// Physical (x, y, z) in µm maps to three.js (z * zScale, x, y): a cyclic permutation,
// hence a rotation, so the handedness of the field is preserved. z runs left to right.

import * as THREE from "three";

export const TWO_PI = 2 * Math.PI;

export const toScene = (p, zScale) => new THREE.Vector3(p[2] * zScale, p[0], p[1]);
export const vecToScene = (v) => new THREE.Vector3(v[2], v[0], v[1]);

export const HOT = (x) => {
  // matplotlib "hot"
  const t = Math.min(Math.max(x, 0), 1);
  return [Math.min(1, t / 0.365), Math.min(1, Math.max(0, (t - 0.365) / 0.381)), Math.max(0, (t - 0.746) / 0.254)];
};

export function makeDisc() {
  // polar grid in units of w; scaled to w(z) and placed at the front each frame
  const nR = 40, nP = 90, rMax = 1.7;
  const positions = [], colors = [], index = [];
  for (let i = 0; i <= nR; i++) {
    for (let j = 0; j <= nP; j++) {
      const r = (rMax * i) / nR, p = (TWO_PI * j) / nP;
      positions.push(0, r * Math.cos(p), r * Math.sin(p));
      colors.push(0, 0, 0, 0);
    }
  }
  for (let i = 0; i < nR; i++) {
    for (let j = 0; j < nP; j++) {
      const a = i * (nP + 1) + j, b = a + nP + 1;
      index.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 4));
  geometry.setIndex(index);
  const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
    vertexColors: true, transparent: true, depthWrite: false, side: THREE.DoubleSide,
  }));
  mesh.userData.radii = Array.from({ length: (nR + 1) * (nP + 1) }, (_, k) => (rMax * Math.floor(k / (nP + 1))) / nR);
  return mesh;
}

export function updateDisc(disc, w, zScene, intensity) {
  // intensity(rho / w, w): cycle-averaged intensity, 1 at the brightest point of the focus
  disc.position.set(zScene, 0, 0);
  disc.scale.set(1, w, w);
  const colors = disc.geometry.attributes.color;
  disc.userData.radii.forEach((r, k) => {
    const level = Math.min(intensity(r, w), 1);
    const [R, G, B] = HOT(level / 1.1);
    colors.setXYZW(k, 0.85 * R, 0.85 * G, 0.85 * B, 0.06 + 0.42 * level);
  });
  colors.needsUpdate = true;
}

export function makeAxis(length) {
  const group = new THREE.Group();
  const material = new THREE.MeshBasicMaterial({ color: 0x777777 });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2 * length, 8), material);
  shaft.rotation.z = -Math.PI / 2;
  const head = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.5, 16), material);
  head.rotation.z = -Math.PI / 2;
  head.position.x = length;
  group.add(shaft, head, textSprite("z", length + 0.7, 0, 0, 0.6));
  return group;
}

export function textSprite(text, x, y, z, height) {
  const canvas = document.createElement("canvas");
  canvas.width = 256; canvas.height = 128;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#bbbbbb";
  ctx.font = "80px sans-serif";
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.fillText(text, 128, 64);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas), depthWrite: false }));
  sprite.position.set(x, y, z);
  sprite.scale.set(height * 2, height, 1);
  return sprite;
}

export function makeArrows(count, color) {
  // unit arrow along +y from the origin; instances are scaled uniformly by the field magnitude
  const material = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.1 });
  const shaftGeometry = new THREE.CylinderGeometry(0.045, 0.045, 0.7, 10).translate(0, 0.35, 0);
  const headGeometry = new THREE.ConeGeometry(0.12, 0.3, 16).translate(0, 0.85, 0);
  const shafts = new THREE.InstancedMesh(shaftGeometry, material, count);
  const heads = new THREE.InstancedMesh(headGeometry, material, count);
  const group = new THREE.Group();
  group.add(shafts, heads);
  group.userData = { shafts, heads };
  return group;
}

const UP = new THREE.Vector3(0, 1, 0);
const tmpMatrix = new THREE.Matrix4(), tmpQuat = new THREE.Quaternion(), tmpScale = new THREE.Vector3();

export function updateArrows(group, anchors, vectors, length) {
  const { shafts, heads } = group.userData;
  anchors.forEach((p, k) => {
    const v = vecToScene(vectors[k]);
    const m = v.length();
    if (m < 1e-6) {
      tmpMatrix.makeScale(0, 0, 0);
    } else {
      tmpQuat.setFromUnitVectors(UP, v.clone().divideScalar(m));
      tmpScale.setScalar(m * length);
      tmpMatrix.compose(p, tmpQuat, tmpScale);
    }
    shafts.setMatrixAt(k, tmpMatrix);
    heads.setMatrixAt(k, tmpMatrix);
  });
  shafts.instanceMatrix.needsUpdate = true;
  heads.instanceMatrix.needsUpdate = true;
}

// Cells for the visible panels: rows of equal height, each row split evenly
// (so 3 views on 2 columns give a full-width last row).
export function layout(width, height, n) {
  const ratio = width / height;
  let cols;
  if (n === 1) cols = 1;
  else if (n === 2) cols = ratio >= 1 ? 2 : 1;
  else if (n === 3) cols = ratio > 1.8 ? 3 : ratio >= 0.9 ? 2 : 1;
  else cols = ratio > 0.7 ? 2 : 1;
  const rows = Math.ceil(n / cols);
  return Array.from({ length: n }, (_, i) => {
    const row = Math.floor(i / cols), inRow = Math.min(cols, n - row * cols);
    const w = width / inRow, h = height / rows;
    return { x: (i % cols) * w, y: row * h, w, h };
  });
}

// Keep the horizontal field of view of a 16:9 panel when a panel is narrower.
const REFERENCE_ASPECT = 16 / 9;
export function fitCamera(camera, fov, aspect) {
  camera.aspect = aspect;
  const t = Math.tan(THREE.MathUtils.degToRad(fov) / 2);
  camera.fov = aspect >= REFERENCE_ASPECT ? fov : THREE.MathUtils.radToDeg(2 * Math.atan((t * REFERENCE_ASPECT) / aspect));
  camera.updateProjectionMatrix();
}

