// Compare web/src/lib/fields.js with the reference fields of the Python library (web/test/reference.py).
// Usage: node test/compare.mjs build/reference.json

import { readFileSync } from "node:fs";
import { harmonicFields } from "../src/lib/fields.js";

const TOLERANCE = 1e-7; // relative to the largest field component of each case
const { cases } = JSON.parse(readFileSync(process.argv[2] ?? "build/reference.json", "utf8"));
let failures = 0;
for (const { spec, points, harmonics } of cases) {
  let worst = 0, peak = 0;
  points.forEach(([x, y, z], i) => {
    const js = harmonicFields(spec, x, y, z);
    for (const n of Object.keys(harmonics)) {
      if (!js[n]) throw new Error(`harmonic ${n} missing in the JS field of ${JSON.stringify(spec.mode)}`);
      harmonics[n][i].forEach(([re, im], c) => {
        peak = Math.max(peak, Math.hypot(re, im));
        worst = Math.max(worst, Math.hypot(js[n][c][0] - re, js[n][c][1] - im));
      });
    }
  });
  const ok = worst <= TOLERANCE * peak;
  if (!ok) failures++;
  console.log(`${ok ? "ok  " : "FAIL"} ${spec.mode.type.padEnd(6)} ${JSON.stringify({ ...spec.mode, jones: undefined })}`
    + `${spec.chiral ? " + 2w partner" : ""}  max error ${(worst / peak).toExponential(1)}`);
}
if (failures) { console.error(`${failures} case(s) differ from the Python library`); process.exit(1); }
