// Geometry for the explanation-multiplicity bench. Every function takes the projection P and returns SVG text.
// The same file is used by build.mjs (first frame) and inlined into the page (live frames).
import * as k from "./kit/iso-kit.mjs";

export const W = {
  PLATE: { x: -172, y: -78, w: 352, d: 156, r: 9 },
  PLATE_H: 12,
  FOOT_H: 5,
  YA: -40, // belt line of analyst A (behind)
  YB: 40, // belt line of analyst B (in front)
  BELT: { x0: -96, x1: 78, w: 20 },
  PANEL_A: { x: -164, y: -54, w: 62, d: 28, r: 2.5 },
  PANEL_B: { x: -164, y: 26, w: 62, d: 28, r: 2.5 },
  PANEL_H: 12,
  KNOB_X: (i) => -157 + 8.7 * i,
  BEAM: { x: -27, y: -68, w: 14, d: 138, r: 2 },
  BEAM_Z: 36,
  HEAD_X: -20,
  GAUGE: [142, 0],
  GAUGE_R: 19,
  GAUGE_Z: 24,
  GAUGE_H: 9,
  SLOT_X: 40,
  CARD: { w: 24, d: 15 },
  // gauge scale: 0 to 1 over 270 degrees, starting at 7:30
  A0: -0.75 * Math.PI,
  SPAN: 1.5 * Math.PI,
};

const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const at = (P, p) => k.iso(p, P);
const opaque = (svg, op) => (op >= 0.999 ? svg : `<g opacity="${Math.max(0, op).toFixed(3)}">${svg}</g>`);

export function plate(P) {
  const { PLATE, PLATE_H, FOOT_H } = W;
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  const feet = [...k.corners(PLATE, 22), [0, PLATE.y + 22], [0, PLATE.y + PLATE.d - 22]];
  for (const [x, y] of [...feet].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P))) {
    out.push(S(k.cylinder(x, y, 7, -PLATE_H - FOOT_H, 1.6, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5.4, -PLATE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }));
  const corner = k.corners(PLATE, 10);
  out.push(L(corner.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(corner.map(([x, y]) => at(P, [x, y, 0])), { size: 0.5 }));
  // ruler strip along the near edge
  const strip = { x: -158, y: PLATE.y + PLATE.d - 15, w: 322, d: 7, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  const t = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 5, 5, strip.y + 0.8, 0.6, [2, 3.6], P);
  out.push(L(t.minor, { tone: "lo" }), L(t.major, { tone: "mid" }));
  out.push(D([at(P, [strip.x + 2, strip.y + 3.5, 0.6]), at(P, [strip.x + strip.w - 2, strip.y + 3.5, 0.6])], { size: 0.45 }));
  return out.join("");
}

// two belts and the two receiving slots
export function belts(P) {
  const { BELT, YA, YB, SLOT_X } = W;
  const out = [];
  for (const y of [YA, YB]) {
    const plan = { x: BELT.x0, y: y - BELT.w / 2, w: BELT.x1 - BELT.x0, d: BELT.w, r: 2 };
    out.push(S(k.slabOf(plan, 0, 1.6, P, 4, 0.4), { tone: "mid" }));
    out.push(L(k.lineOnTop([BELT.x0, y - 6.5], [BELT.x1, y - 6.5], 1.6, P), { tone: "faint" }));
    out.push(L(k.lineOnTop([BELT.x0, y + 6.5], [BELT.x1, y + 6.5], 1.6, P), { tone: "faint" }));
    out.push(L(k.topTicks(BELT.x0 + 4, BELT.x1 - 4, 6, 4, y - 9.2, 1.6, [1.2, 2.2], P).minor, { tone: "lo" }));
    out.push(D([at(P, [BELT.x0 + 2.6, y, 1.6]), at(P, [BELT.x1 - 2.6, y, 1.6])], { size: 0.45 }));
    // receiving slot: a recessed plate at the end
    const slot = { x: SLOT_X, y: y - 11, w: 38, d: 22, r: 2 };
    out.push(S(k.slabOf(slot, 0, 0.8, P, 4, 0.3), { tone: "lo", crease: "none" }));
    out.push(L(k.planOutline(k.insetPlan(slot, 2), 0.8, P, 4), { tone: "faint" }));
  }
  return out.join("");
}

function panel(P, plan, angles) {
  const { PANEL_H, KNOB_X } = W;
  const y = plan.y + plan.d / 2;
  const out = [`<path class="iso-halo" d="${k.haloOf(plan, 0, PANEL_H, P)}" style="filter:blur(4px)"/>`];
  out.push(S(k.slabOf(plan, 0, PANEL_H, P, 5, 0.7), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(plan, 2.2), PANEL_H, P, 4), { tone: "faint" }));
  out.push(D(k.corners(plan, 2.4).map(([x, yy]) => at(P, [x, yy, PANEL_H])), { size: 0.4 }));
  return { shell: out.join(""), y, knobs: (a) => knobs(P, y, a) };
}

function knobs(P, y, angles) {
  const { PANEL_H, KNOB_X } = W;
  const out = [];
  angles.forEach((a, i) => {
    const x = KNOB_X(i);
    out.push(S(k.cylinder(x, y, 3.3, PANEL_H, 3.2, P, 24, 0.3), { tone: "mid" }));
    out.push(L(k.knurl(x, y, 3.3, PANEL_H, PANEL_H + 3.2, 14, P), { tone: "lo" }));
    out.push(L(k.lineOnTop([x, y], [x + Math.sin(a) * 3.3, y - Math.cos(a) * 3.3], PANEL_H + 3.2, P), { tone: "lit" }));
  });
  return out.join("");
}

export const panelA = (P) => panel(P, W.PANEL_A);
export const panelB = (P) => panel(P, W.PANEL_B);
export const knobsA = (P, angles) => knobs(P, W.YA, angles);
export const knobsB = (P, angles) => knobs(P, W.YB, angles);

// the shared instrument: a gantry that straddles both belts, with one press head over each
export function post(P, y) {
  const out = [];
  const plan = { x: W.BEAM.x, y: y - 4, w: W.BEAM.w, d: 8, r: 1.6 };
  out.push(S(k.slabOf(plan, 0, W.BEAM_Z, P, 4, 0.6), { tone: "mid" }));
  out.push(L([8, 22].map((z) => k.sideSeam(plan, z, P, 4)).join(""), { tone: "faint" }));
  out.push(D([at(P, [plan.x + 3.5, plan.y + 4, W.BEAM_Z]), at(P, [plan.x + plan.w - 3.5, plan.y + 4, W.BEAM_Z])], { size: 0.4 }));
  return out.join("");
}
export const postBack = (P) => post(P, W.BEAM.y + 4);
export const postFront = (P) => post(P, W.BEAM.y + W.BEAM.d - 4);

export function beam(P) {
  const { BEAM, BEAM_Z } = W;
  const out = [S(k.slabOf(BEAM, BEAM_Z, 8, P, 4, 0.6), { tone: "mid" })];
  out.push(L(k.planOutline(k.insetPlan(BEAM, 2.4), BEAM_Z + 8, P, 4), { tone: "faint" }));
  out.push(k.faceTextSvg(k.topMatrix([BEAM.x + 2.4, BEAM.y + 100], BEAM_Z + 8, P, "y"), "auto-circuit", { size: 3.4, tone: "mid" }));
  out.push(D([at(P, [BEAM.x + 5, BEAM.y + 4, BEAM_Z + 8]), at(P, [BEAM.x + 5, BEAM.y + BEAM.d - 4, BEAM_Z + 8])], { size: 0.45 }));
  return out.join("");
}

export function head(P) {
  const { HEAD_X } = W;
  const y = 0;
  const out = [];
  out.push(S(k.cylinder(HEAD_X, y, 2.4, 14, W.BEAM_Z - 14, P, 20), { tone: "mid", crease: "none" }));
  out.push(S(k.cylinder(HEAD_X, y, 7, 8, 7, P, 28, 0.5), { tone: "hi", lit: true }));
  out.push(L(k.knurl(HEAD_X, y, 7, 8, 15, 22, P), { tone: "lo" }));
  return out.join("");
}

// a belt card: a slip carrying one analyst's claim. `bars` are the printed lengths, `printed` 0..1 how much is stamped.
export function card(P, x, y, bars, printed, op = 1) {
  if (op <= 0.003) return "";
  const { w, d } = W.CARD;
  const z = 1.6;
  const plan = { x: x - w / 2, y: y - d / 2, w, d, r: 1.2 };
  const out = [S(k.slabOf(plan, z, 1.2, P, 4, 0.3), { tone: "hi", lit: true, crease: "lo" })];
  const top = z + 1.2;
  bars.forEach((len, i) => {
    const yy = y - d / 2 + 3.4 + i * 4.2;
    const l = len * printed;
    if (l > 0.4) out.push(L(k.lineOnTop([x - w / 2 + 2.6, yy], [x - w / 2 + 2.6 + l, yy], top, P), { tone: "lo", free: true }));
  });
  out.push(D([at(P, [x + w / 2 - 2.2, y - d / 2 + 2.2, top])], { size: 0.45, tone: "hi" }));
  return opaque(out.join(""), op);
}

// the comparator: a dial gauge on a post, reading the flip rate
export function gauge(P) {
  const [x, y] = W.GAUGE;
  const { GAUGE_R: R, GAUGE_Z: Z, GAUGE_H: H, A0, SPAN } = W;
  const top = Z + H;
  const out = [];
  const foot = { x: x - 15, y: y - 15, w: 30, d: 30, r: 3 };
  out.push(`<path class="iso-halo" d="${k.haloOf(foot, 0, 4, P)}" style="filter:blur(4px)"/>`);
  out.push(S(k.slabOf(foot, 0, 4, P, 5, 0.6), { tone: "mid" }));
  out.push(D(k.corners(foot, 3).map(([a, b]) => at(P, [a, b, 4])), { size: 0.4 }));
  out.push(S(k.cylinder(x, y, 4.2, 4, Z - 4, P, 24), { tone: "mid", crease: "none" }));
  out.push(L(k.sideArc(x, y, 4.2, 14, P, 14), { tone: "faint" }));
  out.push(S(k.cylinder(x, y, R, Z, H, P, 56, 0.8), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(x, y, R, top - 3.2, top, 76, P, 0.3), { tone: "lo" }));
  out.push(L(k.ring(x, y, R - 2.2, top, P, 56), { tone: "lo" }));
  const ticks = k.radialTicks(x, y, R - 3, 50, 5, top, [1.3, 2.8], P, A0, SPAN);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(L(k.ring(x, y, 1.6, top, P, 16), { tone: "mid" }));
  const lab = (a, text) => k.faceTextSvg(k.topMatrix([x + Math.sin(a) * (R - 8.2), y - Math.cos(a) * (R - 8.2) + 1.1], top, P, "x"), text, { size: 2.8, tone: "mid", anchor: "middle" });
  out.push(lab(A0, "0"), lab(A0 + SPAN, "1"));
  out.push(k.faceTextSvg(k.topMatrix([x, y + 9.4], top, P, "x"), "F", { size: 3.2, tone: "hi", anchor: "middle" }));
  return out.join("");
}

export function needleD(P, v) {
  const [x, y] = W.GAUGE;
  const { GAUGE_R: R, GAUGE_Z: Z, GAUGE_H: H, A0, SPAN } = W;
  const a = A0 + SPAN * v;
  return k.lineOnTop([x - Math.sin(a) * 3.4, y + Math.cos(a) * 3.4], [x + Math.sin(a) * (R - 4.4), y - Math.cos(a) * (R - 4.4)], Z + H + 0.2, P);
}

// wires from the two slots to the gauge post, animated while the two claims are compared
export function wires(P, flow) {
  const [gx, gy] = W.GAUGE;
  const out = [];
  for (const y of [W.YA, W.YB]) {
    const pt = (q) => at(P, q);
    out.push(k.wireSvg(pt([W.SLOT_X + 38, y, 0.8]), pt([gx - 5, gy + Math.sign(y) * 5, 10]), { via: [pt([gx - 20, y, 0.8]), pt([gx - 5, y, 0.8])], tone: "lo", dotted: true, flow: flow > 0.5 }));
  }
  return opaque(out.join(""), 0.25 + 0.75 * flow);
}
