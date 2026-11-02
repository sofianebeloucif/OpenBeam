// Open pages in headless Chrome, run optional JS, take screenshots, report JS errors and failed requests.
// Usage: node test/check-pages.mjs <out dir> "name|url|width|height|js|clip" ...   (clip = "main" to crop to <main>)

import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";

const [outDir, ...jobs] = process.argv.slice(2);
const chrome = spawn("google-chrome", ["--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
  "--remote-debugging-port=9342", "--window-size=1280,860", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await sleep(1500);
const target = (await (await fetch("http://127.0.0.1:9342/json")).json()).find((x) => x.type === "page");
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const pending = new Map(), errors = [];
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); }
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description ?? m.params.exceptionDetails.text);
  if (m.method === "Network.responseReceived" && m.params.response.status >= 400) errors.push(`${m.params.response.status} ${m.params.response.url}`);
  if (m.method === "Network.loadingFailed" && !m.params.canceled) errors.push(`failed ${m.params.errorText}`);
});
const send = (method, params = {}) => new Promise((r) => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
await send("Runtime.enable"); await send("Page.enable"); await send("Network.enable");
for (const job of jobs) {
  const [name, url, w, h, js, clip] = job.split("|");
  await send("Emulation.setDeviceMetricsOverride", { width: +w, height: +h, deviceScaleFactor: 1, mobile: +w < 700 });
  await send("Page.navigate", { url }); await sleep(3000);
  if (js) {
    const r = await send("Runtime.evaluate", { expression: js, returnByValue: true });
    if (r.result?.value !== undefined) console.log(name, "->", JSON.stringify(r.result.value));
    await sleep(1500);
  }
  const params = { format: "png" };
  if (clip === "main") {
    const box = JSON.parse((await send("Runtime.evaluate", { expression: `JSON.stringify(document.querySelector("main").getBoundingClientRect())`, returnByValue: true })).result.value);
    params.clip = { x: box.x, y: box.y, width: box.width, height: box.height, scale: 1 };
  }
  const { data } = await send("Page.captureScreenshot", params);
  writeFileSync(`${outDir}/${name}.png`, Buffer.from(data, "base64"));
}
console.log("errors:", errors.length ? errors : "none");
ws.close(); chrome.kill();
