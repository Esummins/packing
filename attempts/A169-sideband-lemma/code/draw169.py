"""A169 draw169: docs/residue_map/sideband_lemma.svg in the lab's drawing style (Segoe UI, white ground, black
container, blue corner box, cyan Q1, green partner, dashed sidebands).  Four panels: (1) the 2x2 cell picture at c
with the meeter-centre set M and a disjoint pair in cells NW/SE; (2) the two [F] counterexamples (widened diamonds
with both centres > 1; the tilt-0 / 2.87 deg pair with both centres in the band x < 1); (3) the slide construction
at tilt theta: Q1 slid delta, the mode-(a) partner resting on Q1's upper-left edge, lowest point at height
sec(theta) - delta tan(theta); (4) delta_min(theta) = tan(theta/2) up to theta* and the crossing mode beyond, with
the atlas v2 thresholds marked as pitch artefacts.  Light: < 1 s."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import W0
R2 = math.sqrt(2)
HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, '..', 'results')
slide = json.load(open(os.path.join(RES, 'slide169.json')))
cexa = json.load(open(os.path.join(RES, 'check_a.json')))
FONT = 'font-family="Segoe UI, sans-serif"'
out = []
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def T(x, y, s, size=10, extra=''):
    s = esc(s)
    out.append('<text x="%.1f" y="%.1f" font-size="%d" %s>%s</text>' % (x, y, size, extra, s))
def verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + a*c - b*s, cy + a*s + b*c) for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
class Panel:
    def __init__(self, x0, y0, size, span):
        self.x0, self.y0, self.size, self.span = x0, y0, size, span
        self.k = size / span
    def P(self, x, y): return (self.x0 + x*self.k, self.y0 + self.size - y*self.k)
    def poly(self, pts, fill, stroke, sw=1.0, dash=''):
        d = ' '.join('%.1f,%.1f' % self.P(x, y) for x, y in pts)
        out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" %s/>' % (d, fill, stroke, sw, dash))
    def line(self, a, b, stroke, sw=1.0, dash=''):
        (x1, y1), (x2, y2) = self.P(*a), self.P(*b)
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" %s/>' % (x1, y1, x2, y2, stroke, sw, dash))
    def dot(self, x, y, fill, r=3):
        px, py = self.P(x, y); out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (px, py, r, fill))
    def frame(self):
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="1.2"/>' % (self.x0, self.y0, self.size, self.size))
    def box(self, c, fill='#e3f2fd', stroke='#1565c0'):
        self.poly([(0, 0), (c, 0), (c, c), (0, c)], fill, stroke, 1.2)
    def text(self, x, y, s, size=9, extra=''):
        px, py = self.P(x, y); T(px, py, s, size, extra)
DASH = 'stroke-dasharray="4,3"'
W, H = 1180, 720
out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" %s style="background:#fff">' % (W, H, FONT))
T(20, 22, 'The sideband lemma (A169, docs/proofs/sideband.md): the sharp constant is c itself, and what is true is the CELL form', 14, 'font-weight="bold"')
T(20, 40, 'blue = corner box (0,c)^2; dashed = the lines x = c, y = c; cyan = first meeter Q1; green = second meeter Q2; dots = centres; grey = the meeter-centre set M = [1/2, c+1/sqrt2)^2 cut by the quarter-disc at (c,c).', 10, 'fill="#444"')
# ---- panel 1: cells at c (widened), pair in NW / SE
c = 1 + W0
p1 = Panel(20, 60, 300, 2.3)
p1.frame(); p1.box(c)
# meeter-centre set M (grey): [1/2, c)^2 union bands union quarter disc
pts = [(0.5, 0.5), (c + 1/R2, 0.5), (c + 1/R2, c)]
for k in range(0, 31):
    a = (k/30)*(math.pi/2); pts.append((c + math.cos(a)/R2, c + math.sin(a)/R2))
pts += [(c, c + 1/R2), (0.5, c + 1/R2)]
p1.poly(pts, '#eeeeee', '#9e9e9e', 0.8)
p1.line((c, 0), (c, 2.3), '#555', 0.8, DASH); p1.line((0, c), (2.3, c), '#555', 0.8, DASH)
p1.box(c, 'none')
# pair: Q1 in NW cell hugging the wall, Q2 in SE cell along the floor (tilt 0 both, touching the box)
q1 = (0.5, c + 0.45, 0.0); q2 = (c + 0.45, 0.5, 0.0)
p1.poly(verts(*q1), '#b2ebf2', '#00838f', 1.2); p1.poly(verts(*q2), '#c8e6c9', '#2e7d32', 1.2)
p1.dot(q1[0], q1[1], '#00838f'); p1.dot(q2[0], q2[1], '#2e7d32')
p1.text(0.55, 0.55, 'SW', 10); p1.text(0.55, c + 1/R2 - 0.08, 'NW', 10); p1.text(c + 0.45, c + 1/R2 - 0.08, 'NE', 10); p1.text(c + 0.5, 0.55, 'SE', 10)
T(20, 380, '1. Lemma A2 (cells): two disjoint meeters of (0,c)^2 sit in', 10, 'font-weight="bold"')
T(20, 394, 'DIFFERENT cells of {x<c, x>=c} x {y<c, y>=c}: centres are', 9)
T(20, 407, '>= 1/sqrt2 apart in l-inf (Lemma A1) and each cell of M has', 9)
T(20, 420, 'l-inf diameter < 1/sqrt2 when c < 1/2 + 1/sqrt2 = 1.207.', 9)
T(20, 433, 'Never {NE, NE}: that is SIDEBAND (a) with its sharp constant c', 9)
T(20, 446, '(Lean not_both_ne; no quadrant hypothesis, any c).  Shown:', 9)
T(20, 459, 'c = 1 + w = 1.0255, the pair {NW, SE} (up the wall / along the floor).', 9)
# ---- panel 2: the two [F] counterexamples
p2 = Panel(340, 60, 300, 2.6)
p2.frame(); p2.box(c)
p2.line((1, 0), (1, 2.6), '#555', 0.8, DASH); p2.line((0, 1), (2.6, 1), '#555', 0.8, DASH)
d1 = (1.01, 1.7226, math.pi/4); d2 = (1.7226, 1.01, math.pi/4)
p2.poly(verts(*d1), '#b2ebf2', '#00838f', 1.2); p2.poly(verts(*d2), '#c8e6c9', '#2e7d32', 1.2)
p2.dot(d1[0], d1[1], '#00838f'); p2.dot(d2[0], d2[1], '#2e7d32')
p2.text(1.05, 2.35, '(1.01, 1.72)', 9); p2.text(1.75, 0.55, '(1.72, 1.01)', 9)
T(340, 380, '2a. [F] "within 1 of a wall" at the WIDENED box: two 45-deg', 10, 'font-weight="bold"')
T(340, 394, 'diamonds, SAT gap %.4f, both meet (0, 1+w)^2 (neither meets' % cexa['widened_cex']['gap'], 9)
T(340, 407, 'the unit box), both centres > 1 in x and y.  The sharp band is c.', 9)
p2b = Panel(340, 445, 130, 2.6)
p2b.frame(); p2b.box(1.0)
p2b.line((1, 0), (1, 2.6), '#555', 0.6, DASH)
t0 = cexa['theta0_delta01']
e1 = (0.6, 0.5, 0.0); e2 = (t0['centre'][0], t0['centre'][1], math.radians(t0['tilt_deg']))
p2b.poly(verts(*e1), '#b2ebf2', '#00838f', 1.0); p2b.poly(verts(*e2), '#c8e6c9', '#2e7d32', 1.0)
p2b.dot(e1[0], e1[1], '#00838f', 2); p2b.dot(e2[0], e2[1], '#2e7d32', 2)
T(480, 460, '2b. [F] "the other lies outside the band":', 10, 'font-weight="bold"')
T(480, 474, 'Q1 = [0.1,1.1]x[0,1], Q2 at tilt %.2f deg,' % t0['tilt_deg'], 9)
T(480, 487, 'centre (%.3f, %.3f), gap %.0e:' % (t0['centre'][0], t0['centre'][1], t0['gap']), 9)
T(480, 500, 'both meet (0,1)^2, both centres x < 1.', 9)
T(480, 513, 'Cells SW and NW: the cell form holds.', 9)
T(340, 592, 'Sharpness of c: the diamonds at (c-e, c+1/sqrt2-e\') and (c+1/sqrt2-e\', c-e),', 9)
T(340, 605, 'e < e\', are disjoint meeters with both centres > c - e: no band narrower than c.', 9)
# ---- panel 3: the slide construction at theta = 30 deg, delta = 0.45
p3 = Panel(660, 60, 300, 2.3)
th = math.radians(30); dl = 0.45; g = 0.5*(math.cos(th) + math.sin(th))
p3.frame(); p3.box(1.0)
p3.line((1, 0), (1, 2.3), '#555', 0.8, DASH); p3.line((0, 1), (2.3, 1), '#555', 0.8, DASH)
Q1 = (g + dl, g, th)
p3.poly(verts(*Q1), '#b2ebf2', '#00838f', 1.2); p3.dot(Q1[0], Q1[1], '#00838f')
# mode-(a) partner: tilt theta, leftmost vertex on the wall, lowest vertex at height sec(th) - dl tan(th)
yl = 1/math.cos(th) - dl*math.tan(th); gg = 0.5*(math.sin(th) + math.cos(th))
Q2 = (gg, yl + gg, th)
p3.poly(verts(*Q2), '#c8e6c9', '#2e7d32', 1.2); p3.dot(Q2[0], Q2[1], '#2e7d32')
p3.line((0, yl), (2.3, yl), '#e65100', 0.8, DASH)
p3.text(1.05, yl + 0.04, 'sec(th) - delta tan(th) = %.3f' % yl, 9, 'fill="#e65100"')
p3.line((g + dl - 0.5*math.cos(th) + 0.5*math.sin(th), 0), (g + dl - 0.5*math.cos(th) + 0.5*math.sin(th), -0.0), '#000', 0.5)
p3.text(0.05, 0.08, 'delta = %.2f' % dl, 9); p3.text(g + dl + 0.3, g - 0.05, 'Q1, theta = 30 deg', 9)
T(660, 380, '3. The slide construction (Cor. B2): Q1 on the floor at tilt theta, slid delta; the deepest', 10, 'font-weight="bold"')
T(660, 394, 'mode-(a) partner rests on Q1\'s upper-left edge with its left vertex on the wall; its lowest', 10)
T(660, 408, 'point is at height sec(theta) - delta tan(theta) < 1 iff delta > tan(theta/2) = t,', 10)
T(660, 422, 'intrusion (delta - t) tan(theta) = 2t(delta - t)/(1 - t^2).  Pressed (delta = 0): lonely at', 10)
T(660, 436, 'every tilt for the unit box (Cor. B1).', 10)
# ---- panel 4: delta_min(theta) curve
x0, y0, w4, h4 = 660, 460, 480, 230
out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#000" stroke-width="1.2"/>' % (x0, y0, w4, h4))
def PX(deg, d): return (x0 + deg/90*w4, y0 + h4 - d/1.0*h4)
for dv in (0.2, 0.4, 0.6, 0.8):
    (ax, ay) = PX(0, dv); out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#eee"/>' % (ax, ay, x0 + w4, ay)); T(x0 - 26, ay + 3, '%.1f' % dv, 9)
for deg in (15, 30, 45, 60, 75):
    (ax, ay) = PX(deg, 0); T(ax - 6, y0 + h4 + 12, '%d' % deg, 9)
# tan(theta/2) curve
pts = ' '.join('%.1f,%.1f' % PX(d, math.tan(math.radians(d)/2)) for d in range(0, 90))
out.append('<polyline points="%s" fill="none" stroke="#9e9e9e" stroke-width="1" stroke-dasharray="3,3"/>' % pts)
# exact delta_min (unit, widened)
for name, col in (('unit', '#1565c0'), ('widened', '#7b1fa2')):
    pts = ' '.join('%.1f,%.1f' % PX(int(k), v[name]['delta_min']) for k, v in sorted(slide['slide'].items(), key=lambda kv: int(kv[0])))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pts, col))
# atlas v2 thresholds (pitch artefacts)
for deg, d in ((0, 0.18), (15, 0.34), (30, 0.38), (45, 0.56), (60, 0.64), (75, 0.72)):
    ax, ay = PX(deg, d); out.append('<rect x="%.1f" y="%.1f" width="6" height="6" fill="#ef9a9a" stroke="#c62828"/>' % (ax - 3, ay - 3))
ts = slide['theta_star_deg']; ax, ay = PX(ts, 0)
out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e65100" stroke-dasharray="2,2"/>' % (ax, y0, ax, y0 + h4))
T(ax + 3, y0 + 12, 'theta* = %.1f deg' % ts, 9, 'fill="#e65100"')
T(x0 + 8, y0 + 14, 'delta_min(theta): blue = unit box, purple = widened box (exact, Thm B);', 9)
T(x0 + 8, y0 + 26, 'grey dashed = tan(theta/2) (mode (a)); red squares = atlas v2 "d*" = pitch artefacts.', 9)
T(660, 703, '4. Cor. B4: delta_min = tan(theta/2) exactly for theta <= theta*; beyond, the crossing (W)-mode with zeta* < theta', 9)
T(660, 715, 'is smaller.  Widened box: 0 below 17.35 deg and above 72.65 deg (clause NE at alpha = theta), 0.39 at 45 deg.', 9)
out.append('</svg>')
path = os.path.join(HERE, '..', '..', '..', 'docs', 'residue_map', 'sideband_lemma.svg')
open(path, 'w', encoding='utf-8').write('\n'.join(out))
print('wrote', os.path.abspath(path), len(out), 'elements')
