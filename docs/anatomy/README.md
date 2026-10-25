# Explanation multiplicity bench: the interactive figure

An isometric, interactive drawing of the paper's setup, built with the [Anatomy](https://github.com/wheresryan22/anatomy) Agent Skill by Ryan (MIT). Two analysts each set seven knobs a little differently; one shared instrument stamps a claim for each; a dial gauge reads the claim flip rate.

| File | What it is |
|---|---|
| `multiplicity-bench-light.html` | The figure, light theme. Standalone: open it in a browser. |
| `multiplicity-bench.html` | The same figure, dark theme. |
| `multiplicity-bench.gif` | A recording of one full cycle, used in the main README. |
| `multiplicity-bench.png` | A still of the finished state. |
| `rig.mjs` | The model: the headline numbers and the timeline. |
| `parts.mjs` | The geometry of every part, shared by the build and the live page. |
| `build.mjs` | Writes the HTML pages. |
| `kit/`, `scripts/` | The Anatomy drawing kit and its capture and line-check scripts, copied unchanged. `LICENSE-anatomy` is its licence. |

## Use it

Hover to scrub through the cycle, click or press Space or Enter to replay, arrow keys to step, Home and End to jump. The figure tours by itself when left alone and shows one still frame under reduced motion.

```bash
node build.mjs --light   # writes multiplicity-bench-light.html  (Node 20.10 or later, nothing to install)
node build.mjs           # writes multiplicity-bench.html
node scripts/lines.mjs multiplicity-bench-light.html --reduced   # every drawn line must end on something (needs Chrome; set CHROME_PATH)
```

## What is real and what is drawn

Real, from the paper and `README.md`: the claim flip rate F = 0.7316, the 15,840 pre-registered specifications, the 7,561 that produced a claim, and that a specification has seven axes.

Drawn for the picture: the knob positions of the two analysts and the two claim slips. They show the idea (small settings differences, different claims), not data from the sweep. The figure makes no statistical claim.
