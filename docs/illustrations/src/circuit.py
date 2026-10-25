from xh import *
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "caveat-latin-600-normal.woff2"

def dials(c, x, y, angles, lit=None):
    c.rect(x, y, 250, 56, fill="#fff")
    for i, a in enumerate(angles):
        cx = x + 24 + i * 34
        c.circle(cx, y + 28, 11, sw=2.6)
        c.line([(cx, y + 28), (cx + 9 * math.sin(a), y + 28 - 9 * math.cos(a))], RED if lit and i in lit else BLACK, 2.6)

# 1. same tool, different settings
c = Canvas(11, F)
dials(c, 150, 250, [-1.6, .4, 1.2, -.5, .9, -1.1, .3])
dials(c, 150, 520, [-1.6, 1.3, 1.2, .8, -.7, -1.1, 1.8], lit={1, 3, 4, 6})
c.xiaohei(345, 250, .8, look=-.6, hands=[(310, 270), None])
c.xiaohei(345, 520, .8, look=-.6, hands=[(378, 540), None])
c.text(150, 205, "analyst A", BLUE, 38)
c.text(150, 475, "analyst B", BLUE, 38)
c.text(150, 640, "7 settings each,\nboth defensible", BLUE, 34)
c.arrow([(420, 278), (640, 360), (760, 390)])
c.arrow([(420, 548), (640, 440), (760, 410)])
# the shared instrument: a box with a press and a slot
c.rect(780, 300, 250, 220, fill="#fff")
c.rect(840, 262, 130, 40, fill="#fff")
c.line([(905, 302), (905, 330)], BLACK, 5)
c.rect(850, 330, 110, 24, fill="#fff")
c.line([(810, 470), (1000, 470)], BLACK, 3)
c.text(905, 440, "one instrument", BLACK, 40, "middle")
c.arrow([(1040, 410), (1180, 410)])
c.rect(1190, 340, 130, 150, rot=-3, fill="#fff"); c.rect(1215, 365, 130, 150, rot=4, fill="#fff")
c.text(1250, 440, "claim", BLACK, 36, "middle")
c.text(780, 600, "same system, same tool,\nsame task", RED, 40)
c.save("01-same-tool.svg")

# 2. the claims flip
c = Canvas(12, F)
def claim(c, x, y, nodes, edges, rot):
    c.rect(x, y, 230, 290, rot=rot, fill="#fff")
    for (a, b) in edges:
        c.line([(x + nodes[a][0], y + nodes[a][1]), (x + nodes[b][0], y + nodes[b][1])], BLACK, 2.6)
    for (px, py) in nodes:
        c.circle(x + px, y + py, 11, sw=2.6)
claim(c, 270, 230, [(60, 60), (60, 140), (60, 220), (170, 100), (170, 190)], [(0, 1), (1, 2), (0, 3), (1, 4), (3, 4)], -3)
claim(c, 880, 230, [(60, 80), (60, 200), (115, 140), (170, 70), (170, 210)], [(0, 2), (1, 2), (2, 3), (2, 4), (0, 3)], 3)
c.xiaohei(688, 640, 1.0, look=0, hands=[(520, 470), (860, 470)])
c.text(385, 190, "analyst A's claim", BLUE, 38, "middle")
c.text(995, 190, "analyst B's claim", BLUE, 38, "middle")
c.text(690, 420, "≠", RED, 150, "middle")
c.text(690, 290, "same decision", BLACK, 36, "middle")
c.text(1130, 625, "flips in 73.2%\nof pairs", RED, 44, "end")
c.save("02-claims-flip.svg")

# 3. plan first, then look
c = Canvas(13, F)
c.rect(190, 300, 200, 250, fill="#fff", rot=-2)
for i in range(4):
    c.line([(215, 340 + i * 36), (360, 342 + i * 36)], BLACK, 2.6)
c.circle(340, 505, 26, RED, "#fff", 3.4); c.text(340, 516, "✓", RED, 38, "middle")
c.text(290, 270, "the plan", BLACK, 44, "middle")
c.xiaohei(520, 600, 0.95, look=-.6, hands=[(410, 500), (470, 540)])
c.text(520, 230, "tagged and\ntimestamped first", RED, 40, "middle")
c.arrow([(640, 480), (820, 480)], ORANGE)
# a heap of slips
import random as _r
rr = _r.Random(5)
levels = 7
for lv in range(levels):
    n = levels - lv + 2
    for j in range(n):
        x = 1090 - n * 30 + j * 60 + rr.uniform(-6, 6)
        y = 650 - lv * 34 + rr.uniform(-4, 4)
        c.rect(x, y, 56, 38, fill="#fff", sw=2.2, rot=rr.uniform(-18, 18))
c.text(1090, 305, "15,840\nspecifications", BLACK, 46, "middle")
c.text(1090, 215, "then the sweep", BLUE, 38, "middle")
c.save("03-plan-first.svg")
