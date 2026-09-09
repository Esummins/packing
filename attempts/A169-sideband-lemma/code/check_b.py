"""A169 check B: slide-family threshold delta_min(theta) (bisection on existence of a second meeter, unit box and
widened box), the max depth of the second meeter vs the closed form (delta - tan(theta/2)) tan(theta) [mode (a)],
and the pull-family threshold."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import *
PITCH, NT = 0.04, 45

def q1_slide(theta, d):
    h = 0.5 * (math.cos(theta) + math.sin(theta)); return (h + d, h, theta)
def q1_pull(theta, d):
    h = 0.5 * (math.cos(theta) + math.sin(theta)); return (h + d / math.sqrt(2), h + d / math.sqrt(2), theta)

def exists(q1, c):
    ok, pose, g = second_meeter_exists(verts(*q1), c, pitch=PITCH, ntilt=NT)
    return ok, pose, g

def bisect(fam, theta, c, lo=0.0, hi=1.3, it=9):
    if not exists(fam(theta, hi), c)[0]:
        return None
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if exists(fam(theta, mid), c)[0]: hi = mid
        else: lo = mid
    return hi

def max_depth(q1, c, pitch=0.02, nt=90):
    """deepest second meeter: max over admissible Q2 of (c - min_y of Q2 inside x<c) -- we report c - min over
    Q2 vertices y restricted to poses meeting the box; rough (grid) lower bound on depth_max."""
    Q1 = verts(*q1); best = -1; bp = None
    n = int(2.3 / pitch)
    for i in range(n):
        for j in range(n):
            cx, cy = 0.5 + i * pitch, 0.5 + j * pitch
            for k in range(nt):
                th = k * (math.pi / 2) / nt
                P = verts(cx, cy, th)
                if not in_quadrant(P) or not meets_open_box(P, c) or sat_gap(P, Q1) < 0: continue
                d = c - min(v[1] for v in P)
                if d > best: best, bp = d, (cx, cy, th)
    return best, bp

out = {'pitch': PITCH, 'ntilt': NT, 'slide': {}, 'pull': {}, 'depth': {}}
for deg in (0, 5, 10, 15, 20, 30, 45, 60, 75, 80, 85):
    th = math.radians(deg); t = math.tan(th / 2)
    r = {'t': t}
    for c, name in ((1.0, 'unit'), (1 + W0, 'widened')):
        r[name] = bisect(q1_slide, deg and th, c)
    out['slide'][deg] = r; print('slide', deg, r, flush=True)
for deg in (0, 15, 30, 45, 60, 75):
    th = math.radians(deg); r = {}
    for c, name in ((1.0, 'unit'), (1 + W0, 'widened')):
        r[name] = bisect(q1_pull, th, c)
    out['pull'][deg] = r; print('pull', deg, r, flush=True)
for deg, d in ((15, 0.3), (30, 0.4), (45, 0.6), (60, 0.8), (30, 0.6), (45, 0.9)):
    th = math.radians(deg); t = math.tan(th / 2)
    dm, bp = max_depth(q1_slide(th, d), 1.0)
    out['depth'][f'{deg}_{d}'] = dict(grid=dm, pose=bp, closed_form_a=(d - t) * math.tan(th))
    print('depth', deg, d, dm, (d - t) * math.tan(th), bp, flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'results', 'check_b.json'), 'w'), indent=1)
