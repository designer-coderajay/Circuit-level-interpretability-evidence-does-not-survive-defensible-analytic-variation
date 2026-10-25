// Builds the interactive bench: node build.mjs [--light]
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "./kit/iso-kit.mjs";
import { kitScript } from "./scripts/inline-kit.mjs";
import * as rig from "./rig.mjs";
import * as g from "./parts.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";
const WIDTH = 800;
const HEIGHT = 400;
const { W } = g;

const P = k.fitProjection(
  [...k.boxCorners(W.PLATE, -17, 0), [-20, 0, 52], [132, 0, 44], [-160, -40, 18], [-160, 40, 18]],
  WIDTH,
  HEIGHT,
  { pad: 24, azimuth: 62 },
);

const REST = 0.975;

function cards(p) {
  const { CARD } = W;
  const a = p.cardA.shown ? g.card(P, p.cardA.x, W.YA, rig.CLAIM_A, p.cardA.printed, p.fade) : "";
  const b = p.cardB.shown ? g.card(P, p.cardB.x, W.YB, rig.CLAIM_B, p.cardB.printed, p.fade) : "";
  return { a, b };
}

function scene(u) {
  const p = rig.pose(u);
  const c = cards(p);
  const pa = g.panelA(P);
  const pb = g.panelB(P);
  const lift = (press, y) => `transform="${k.translateAlong(P, [0, y, -4 * press])}"`;
  return [
    g.plate(P),
    g.belts(P),
    pa.shell,
    `<g data-part="knobsA">${g.knobsA(P, p.knobA)}</g>`,
    g.postBack(P),
    `<g data-part="cardA">${c.a}</g>`,
    `<g data-part="headA" ${lift(p.pressA, W.YA)}>${g.head(P)}</g>`,
    pb.shell,
    `<g data-part="knobsB">${g.knobsB(P, p.knobB)}</g>`,
    `<g data-part="cardB">${c.b}</g>`,
    `<g data-part="headB" ${lift(p.pressB, W.YB)}>${g.head(P)}</g>`,
    g.beam(P),
    g.postFront(P),
    `<g data-part="wires">${g.wires(P, p.flow)}</g>`,
    g.gauge(P),
    `<path data-part="needle" class="iso-line" data-tone="lit" data-free="start" d="${g.needleD(P, p.needle)}" style="stroke-width:1.1"/>`,
  ];
}

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "A bench that shows explanation multiplicity. Two analysts each set seven knobs, a little differently. Their slips travel on two belts under one shared press, the instrument, which stamps a claim onto each. The two stamped claims arrive side by side and a dial gauge reads the claim flip rate, 0.7316 in the reported sweep.",
  body: scene(REST),
});

// ---- the live part --------------------------------------------------------------------------------
const strip = (file) => readFileSync(join(HERE, file), "utf8").replace(/^export /gm, "").replace(/^import .*$/gm, "");
const kitNames = Object.keys(k).join(", ");

const live = `
const P = ${JSON.stringify(P)};
const REST = ${REST};
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const part = (name) => svg.querySelector('[data-part="' + name + '"]');
const E = { kA: part("knobsA"), kB: part("knobsB"), cA: part("cardA"), cB: part("cardB"), hA: part("headA"), hB: part("headB"), wires: part("wires"), needle: part("needle") };
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const cache = {};
const put = (key, node, html) => { if (cache[key] !== html) { cache[key] = html; node.innerHTML = html; } };
const r2 = (a) => a.map((v) => Math.round(v * 40) / 40);
let u = still.matches ? REST : 0, target = u, touring = !still.matches, frame = 0, last = 0, visible = false, idleTimer = 0;

function render() {
  const p = pose(u);
  put("kA", E.kA, knobsA(P, r2(p.knobA)));
  put("kB", E.kB, knobsB(P, r2(p.knobB)));
  put("cA", E.cA, p.cardA.shown ? card(P, Math.round(p.cardA.x * 4) / 4, W.YA, CLAIM_A, Math.round(p.cardA.printed * 40) / 40, p.fade) : "");
  put("cB", E.cB, p.cardB.shown ? card(P, Math.round(p.cardB.x * 4) / 4, W.YB, CLAIM_B, Math.round(p.cardB.printed * 40) / 40, p.fade) : "");
  E.hA.setAttribute("transform", translateAlong(P, [0, W.YA, -4 * p.pressA]));
  E.hB.setAttribute("transform", translateAlong(P, [0, W.YB, -4 * p.pressB]));
  put("wires", E.wires, wires(P, Math.round(p.flow * 20) / 20));
  E.needle.setAttribute("d", needleD(P, p.needle));
  const text = describe(u);
  if (readout.textContent !== text) readout.textContent = text;
  stage.setAttribute("aria-valuenow", String(Math.round(u * 100)));
  stage.setAttribute("aria-valuetext", text);
}

function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  if (touring) { u += dt / CYCLE; if (u >= 1) u -= 1; target = u; }
  else { u = still.matches ? target : u + (target - u) * (1 - Math.exp(-dt / 0.12)); if (Math.abs(target - u) < 0.0004) u = target; }
  render();
  frame = visible && (touring || u !== target) ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const hold = () => { touring = false; clearTimeout(idleTimer); idleTimer = setTimeout(() => { touring = !still.matches; run(); }, 3600); run(); };

new IntersectionObserver((entries) => { visible = entries[entries.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
stage.addEventListener("pointermove", (event) => {
  const box = svg.getBoundingClientRect();
  target = clamp(((event.clientX - box.left) / box.width - 0.06) / 0.88, 0, 0.995);
  hold();
});
stage.addEventListener("pointerleave", () => { clearTimeout(idleTimer); idleTimer = setTimeout(() => { touring = !still.matches; run(); }, 1200); });
stage.addEventListener("click", () => { u = target = 0; touring = !still.matches; if (still.matches) u = target = REST; clearTimeout(idleTimer); render(); run(); });
stage.addEventListener("keydown", (event) => {
  const key = event.key;
  if (key === "ArrowRight" || key === "ArrowUp") target = clamp(target + 0.03, 0, 0.995);
  else if (key === "ArrowLeft" || key === "ArrowDown") target = clamp(target - 0.03, 0, 0.995);
  else if (key === "Home") target = 0;
  else if (key === "End") target = REST;
  else if (key === " " || key === "Enter") { event.preventDefault(); u = target = 0; touring = !still.matches; render(); run(); return; }
  else return;
  event.preventDefault();
  hold();
});
window.__set = (uu) => { u = target = uu; touring = false; render(); };
render();
`;

const phone = `<style>@media (max-width:560px){.iso-plate-corner[data-corner="hint"]{display:none}.iso-plate-corner[data-corner="readout"]{left:0;right:0;white-space:normal;text-align:right;font-size:9.5px;line-height:1.35}}</style>`;
const body = phone + k.plateHtml({
  fig: "Fig 1",
  title: "Explanation multiplicity",
  hint: "Hover to scrub · click to replay",
  readout: rig.describe(REST),
  keys: [
    { mark: "lit", label: "Knob pointers and the gauge needle" },
    { mark: "raised", label: "Claim slips: what each analyst would file" },
  ],
  caption:
    "Two analysts set the same seven-axis specification a little differently. The same instrument, run on the same task, stamps a claim for each. Across 15,840 pre-registered specifications on GPT-2 small and the indirect object identification task, 7,561 produced a claim, and the claim flip rate F was 0.7316. The knob positions and the two claim slips are illustrative; only F, the counts and the seven axes come from the paper.",
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Explanation multiplicity bench: hover to scrub, click to replay, arrow keys step" aria-valuemin="0" aria-valuemax="100" aria-valuenow="97">${svg}</div>`,
});

const script = kitScript() + `\nconst k = { ${kitNames} };\n` + strip("rig.mjs") + "\n" + strip("parts.mjs") + "\n" + live;
const file = theme === "light" ? "multiplicity-bench-light.html" : "multiplicity-bench.html";
writeFileSync(join(HERE, file), k.pageHtml({ title: "Explanation multiplicity bench", theme, body, script, width: 860 }));
console.log("wrote", file);
