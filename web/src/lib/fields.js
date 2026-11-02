// JavaScript port of the OpenBeam fields used by the web viewers.
//
// Mirrors src/openbeam/beams (VortexBeam / GaussianBeam, VectorBeam, BesselBeam, TwoColourBeam):
// same formulas, normalizations and conventions (phasors e^{-i w t}, propagation e^{ikz}, SI units).
// web/test/compare.mjs checks it against values computed by the Python library.
//
// A beam spec is { lambda, w0, mode, amplitude?, chiral? } with mode one of
//   { type: "lg", l, jones: [jx, jy] }        scalar LG_{0,l} (l = 0: Gaussian), jones complex pairs [re, im]
//   { type: "vector", m, theta0 }             polarization at the angle m phi + theta0 (m = 1: radial / azimuthal)
//   { type: "bessel", n, kr, jones }          Bessel-Gauss beam of order n
// and chiral = { ratio, psi } adding the synthetic-chiral 2w partner (see partnerSpec).

// ---------- complex numbers as [re, im] ----------

export const C = (re, im = 0) => [re, im];
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const scale = (a, s) => [a[0] * s, a[1] * s];
const conj = (a) => [a[0], -a[1]];
const abs2 = (a) => a[0] * a[0] + a[1] * a[1];
const div = (a, b) => { const d = abs2(b); return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
const cexp = (a) => { const r = Math.exp(a[0]); return [r * Math.cos(a[1]), r * Math.sin(a[1])]; };
const I = [0, 1];
export const cabs2 = abs2;

// ---------- beam geometry ----------

export const rayleighRange = (w0, lambda) => Math.PI * w0 * w0 / lambda;
export const beamRadius = (z, w0, lambda) => w0 * Math.sqrt(1 + (z / rayleighRange(w0, lambda)) ** 2);
const inverseCurvature = (z, w0, lambda) => { const zr = rayleighRange(w0, lambda); return z / (z * z + zr * zr); };
const gouyPhase = (z, w0, lambda) => Math.atan(z / rayleighRange(w0, lambda));

// ---------- scalar envelopes with their transverse derivatives: { u, ux, uy } ----------

function lgTerms(l, w0, lambda, x, y, z) {
  const n = Math.abs(l), s = Math.sign(l);
  const k = 2 * Math.PI / lambda;
  const w = beamRadius(z, w0, lambda);
  const q = [1 / (w * w), -0.5 * k * inverseCurvature(z, w0, lambda)];
  const peak = n ? n ** (n / 2) * Math.exp(-n / 2) : 1;
  const rho2 = x * x + y * y;
  const common = scale(cexp(sub(scale(q, -rho2), [0, (n + 1) * gouyPhase(z, w0, lambda)])),
    (w0 / w) * (Math.SQRT2 / w) ** n / peak);
  const zeta = [x, s * y];
  let power = C(1), lower = C(0);
  for (let j = 0; j < n; j++) { lower = power; power = mul(power, zeta); }
  lower = scale(lower, n); // n zeta^(n-1)
  const twoQ = scale(q, 2);
  return {
    u: mul(common, power),
    ux: mul(common, sub(lower, mul(twoQ, scale(power, x)))),
    uy: mul(common, sub(mul([0, s], lower), mul(twoQ, scale(power, y)))),
  };
}

// J_m(z) for integer m and complex z, power series (|z| stays below ~15 here)
function besselJ(m, z) {
  const order = Math.abs(m);
  const half = scale(z, 0.5), half2 = mul(half, half);
  let term = C(1);
  for (let j = 1; j <= order; j++) term = scale(mul(term, half), 1 / j); // (z/2)^order / order!
  let sum = term;
  for (let k = 1; k < 80; k++) {
    term = scale(mul(term, half2), -1 / (k * (k + order)));
    sum = add(sum, term);
    if (abs2(term) < 1e-34 * abs2(sum)) break;
  }
  return m < 0 && order % 2 ? scale(sum, -1) : sum;
}

const besselPeakCache = new Map();
function besselPeak(n, kr, w0) {
  // same grid as BesselBeam._peak in Python
  const key = `${n}|${kr}|${w0}`;
  if (!besselPeakCache.has(key)) {
    const rmax = Math.min(3 * w0, 12 / kr), N = 20001;
    let peak = 0;
    for (let i = 0; i < N; i++) {
      const rho = (rmax * i) / (N - 1);
      peak = Math.max(peak, Math.sqrt(abs2(besselJ(n, C(kr * rho)))) * Math.exp(-((rho / w0) ** 2)));
    }
    besselPeakCache.set(key, peak);
  }
  return besselPeakCache.get(key);
}

function besselTerms(n, kr, w0, lambda, x, y, z) {
  const k = 2 * Math.PI / lambda;
  const d = [1, z / rayleighRange(w0, lambda)];
  const a = div(C(1 / (w0 * w0)), d);
  const b = div(C(kr), d);
  const rho = Math.hypot(x, y), phi = Math.atan2(y, x);
  // exp(-a rho^2 - i kr^2 z / (2 k d)) / d / peak
  const env = scale(div(cexp(sub(scale(a, -rho * rho), mul(I, div(C(kr * kr * z / (2 * k)), d)))), d),
    1 / besselPeak(n, kr, w0));
  const f = (m) => mul(besselJ(m, scale(b, rho)), cexp([0, m * phi]));
  const fn = f(n), fm = f(n - 1), fp = f(n + 1);
  const dfx = mul(scale(b, 0.5), sub(fm, fp));
  const dfy = mul(mul([0, 0.5], b), add(fp, fm)); // -b / 2i (f(n+1) + f(n-1))
  const twoA = scale(a, 2);
  return {
    u: mul(env, fn),
    ux: mul(env, sub(dfx, mul(twoA, scale(fn, x)))),
    uy: mul(env, sub(dfy, mul(twoA, scale(fn, y)))),
  };
}

// ---------- vector fields ----------

const SIGMA_PLUS = [C(Math.SQRT1_2), C(0, Math.SQRT1_2)];
const SIGMA_MINUS = [C(Math.SQRT1_2), C(0, -Math.SQRT1_2)];

function normalizeJones([a, b]) {
  const norm = Math.sqrt(abs2(a) + abs2(b));
  return [scale(a, 1 / norm), scale(b, 1 / norm)];
}

// [(jones, {u, ux, uy})] for a beam spec at one point
function terms(spec, x, y, z) {
  const { mode, lambda, w0 } = spec;
  if (mode.type === "lg") return [[normalizeJones(mode.jones), lgTerms(mode.l, w0, lambda, x, y, z)]];
  if (mode.type === "bessel") return [[normalizeJones(mode.jones), besselTerms(mode.n, mode.kr, w0, lambda, x, y, z)]];
  if (mode.type === "vector") {
    const plus = cexp([0, mode.theta0]), minus = cexp([0, -mode.theta0]);
    const r = Math.SQRT1_2;
    return [
      [[scale(mul(SIGMA_MINUS[0], plus), r), scale(mul(SIGMA_MINUS[1], plus), r)], lgTerms(mode.m, w0, lambda, x, y, z)],
      [[scale(mul(SIGMA_PLUS[0], minus), r), scale(mul(SIGMA_PLUS[1], minus), r)], lgTerms(-mode.m, w0, lambda, x, y, z)],
    ];
  }
  throw new Error(`unknown mode ${mode.type}`);
}

// complex field [Ex, Ey, Ez] of one monochromatic beam spec at (x, y, z), carrier included
export function monochromaticField(spec, x, y, z) {
  const k = 2 * Math.PI / spec.lambda;
  let Ex = C(0), Ey = C(0), Ez = C(0);
  for (const [[jx, jy], { u, ux, uy }] of terms(spec, x, y, z)) {
    Ex = add(Ex, mul(jx, u));
    Ey = add(Ey, mul(jy, u));
    Ez = add(Ez, mul(scale(I, 1 / k), add(mul(jx, ux), mul(jy, uy))));
  }
  const factor = scale(cexp([0, k * z]), spec.amplitude ?? 1);
  const phase = spec.phase ? mul(factor, cexp([0, spec.phase])) : factor;
  return [mul(Ex, phase), mul(Ey, phase), mul(Ez, phase)];
}

// ---------- synthetic chiral light: the 2w partner ----------

// Same beam at half the wavelength, twice the waist, orthogonal polarization
// (x -> y, sigma+ -> sigma-, radial -> azimuthal), amplitude sqrt(ratio), delayed by psi.
export function partnerSpec(spec) {
  const { ratio, psi } = spec.chiral;
  let mode;
  if (spec.mode.type === "vector") mode = { ...spec.mode, theta0: spec.mode.theta0 + Math.PI / 2 };
  else {
    const [a, b] = normalizeJones(spec.mode.jones);
    mode = { ...spec.mode, jones: [scale(conj(b), -1), conj(a)] };
  }
  return { lambda: spec.lambda / 2, w0: 2 * spec.w0, mode, amplitude: Math.sqrt(ratio), phase: psi };
}

// { 1: [Ex, Ey, Ez], 2: [...] } at (x, y, z): the beam and, if spec.chiral, its 2w partner
export function harmonicFields(spec, x, y, z) {
  const out = { 1: monochromaticField(spec, x, y, z) };
  if (spec.chiral) out[2] = monochromaticField(partnerSpec(spec), x, y, z);
  return out;
}

export const omegaOf = (spec) => 2 * Math.PI * 299792458 / spec.lambda;

// ---------- wavefronts and sizes of the fundamental ----------

export function modeGeometry(spec) {
  const { mode, lambda, w0 } = spec;
  const k = 2 * Math.PI / lambda;
  if (mode.type === "bessel") {
    const kAxial = k - mode.kr * mode.kr / (2 * k);
    const size = 6 / mode.kr; // arrow rings and disc: the core does not spread
    const ring = (mode.n === 0 ? 2.405 : 1.841) / mode.kr;
    return {
      k: kAxial,
      phase: (rho, z, phi) => kAxial * z + mode.n * phi,
      scale: () => size,
      ringRadius: () => ring,
      zUnit: { value: w0 * k / mode.kr, label: "z_max" },
    };
  }
  const charge = mode.type === "vector" ? mode.m : Math.abs(mode.l);
  const helicity = mode.type === "lg" ? mode.l : 0; // the polarization of a vector beam winds, not its phase
  return {
    k,
    phase: (rho, z, phi) => k * z + k * rho * rho / 2 * inverseCurvature(z, w0, lambda)
      - (charge + 1) * gouyPhase(z, w0, lambda) + helicity * phi,
    scale: (z) => beamRadius(z, w0, lambda),
    // 1/e^2 radius of the Gaussian, bright ring w sqrt(|l| / 2) of the LG_{0,l} modes
    ringRadius: (z) => beamRadius(z, w0, lambda) * (charge ? Math.sqrt(charge / 2) : 1),
    zUnit: { value: rayleighRange(w0, lambda), label: "z_R" },
  };
}
