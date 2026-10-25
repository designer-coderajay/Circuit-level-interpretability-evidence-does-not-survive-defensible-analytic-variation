# Illustration sources

The three images one level up are drawn by `circuit.py` with the small kit in `xh.py` (wobbly black lines, a black creature with white dot eyes, orange for the path, red for the key point, blue for side notes). They are hand-authored vector drawings, not AI-generated art.

```bash
python3 circuit.py                       # writes 01-same-tool.svg, 02-claims-flip.svg, 03-plan-first.svg
node render.js 01-same-tool 02-claims-flip 03-plan-first   # needs playwright with Chromium; writes the PNGs
```

The lettering font is Caveat (SIL Open Font License 1.1), embedded in each SVG from `caveat-latin-600-normal.woff2`.

Only the number 73.2% (the claim flip rate, 0.7316) and 15,840 (pre-registered specifications) come from the paper. The knob positions and the claim sketches are illustrative.
