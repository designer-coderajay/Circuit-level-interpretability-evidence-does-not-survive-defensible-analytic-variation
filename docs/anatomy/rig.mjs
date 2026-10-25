// The model behind the figure. Pure functions: the geometry, the motion and the readout all read from here.
// What is real: the README's headline flip rate F = 0.7316 (15,840 pre-registered specifications, 7,561 of which
// produced a claim) and that a specification has seven axes. Everything else here is illustrative: the knob
// positions and the two claim cards are drawn to show the idea, not taken from the sweep.

export const F_REAL = 0.7316;
export const AXES = 7;
export const SPECS = 15840;
export const CLAIMS = 7561;

// Knob angles in radians for analyst A and analyst B. Illustrative: B differs from A on four of the seven axes.
export const KNOB_A = [-1.6, 0.4, 1.2, -0.5, 0.9, -1.1, 0.3];
export const KNOB_B = [-1.6, 1.3, 1.2, 0.8, -0.7, -1.1, 1.8];
// Illustrative claim cards: three bar lengths each.
export const CLAIM_A = [14, 7, 10];
export const CLAIM_B = [6, 14, 9];

export const clamp = (v, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
export const seg = (u, a, b) => clamp((u - a) / (b - a));
export const ease = (t) => t * t * (3 - 2 * t);
export const wave = (u, a, b) => Math.sin(Math.PI * seg(u, a, b));

export const CYCLE = 24;
export const T = {
  knobA: [0.02, 0.2],
  knobB: [0.2, 0.38],
  cardA: [0.4, 0.62],
  cardB: [0.46, 0.68],
  flow: [0.7, 0.78],
  needle: [0.78, 0.95],
  fade: [0.985, 1.0],
};

const X0 = -92; // card start
const XP = -20; // under the press
const X1 = 58; // comparison slot

function carriage(u, [a, b]) {
  const s = seg(u, a, b);
  const x = s < 0.4 ? X0 + (XP - X0) * ease(s / 0.4) : s < 0.6 ? XP : XP + (X1 - XP) * ease((s - 0.6) / 0.4);
  return { x, shown: u >= a, press: wave(s, 0.4, 0.6), printed: seg(s, 0.46, 0.6) };
}

export function pose(u) {
  const fadeOut = 1 - seg(u, T.fade[0], T.fade[1]);
  const ca = carriage(u, T.cardA);
  const cb = carriage(u, T.cardB);
  const ka = seg(u, ...T.knobA);
  const kb = seg(u, ...T.knobB);
  return {
    u,
    fade: fadeOut,
    knobA: KNOB_A.map((t, i) => t * ease(clamp(ka * (AXES + 2) - i * 0.9, 0, 1))),
    knobB: KNOB_B.map((t, i) => t * ease(clamp(kb * (AXES + 2) - i * 0.9, 0, 1))),
    cardA: ca,
    cardB: cb,
    pressA: ca.press,
    pressB: cb.press,
    flow: seg(u, ...T.flow) * (u < 0.95 ? 1 : 0.4),
    needle: F_REAL * ease(seg(u, ...T.needle)),
  };
}

export function describe(u) {
  const p = pose(u);
  if (u < T.knobA[1]) return `analyst A sets ${AXES} axes`;
  if (u < T.knobB[1]) return `analyst B sets ${AXES} axes, a little differently`;
  if (u < T.cardB[1]) return "same instrument, same prompts: each stamps a claim";
  if (u < T.needle[0]) return "two claims side by side";
  if (u < T.fade[0]) return `claim flip rate F = ${p.needle.toFixed(4)}`;
  return "ready for the next pair";
}
