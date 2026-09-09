"""A169: the lonely region from Theorem B's exact criterion (no search).  Per tilt: raster of Q1 centres over
the meeter set (pitch 0.02), unit and widened box, lonely fraction and bounding data; exact slide thresholds
delta_min(theta) by bisection on the criterion (with certified witnesses); the theta=0 cubic law check."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import *
from crit169 import criterion, support

def nonlonely(x1, y1, th, c, steps=720):
    ok, best, cert = criterion(x1, y1, th, c, steps)
    if ok: return True
    # (P) clause for the widened box: the pressed axis square [0,1]^2 as a second meeter
    if c > 1 and sat_gap(verts(x1, y1, th), verts(0.5, 0.5, 0.0)) >= 0: return True
    return False

out = {'raster': {}, 'slide': {}, 'theta0_law': []}
PITCH = 0.02
for deg in range(0, 90, 5):
    th = math.radians(deg); rec = {}
    for c, name in ((1.0, 'unit'), (1 + W0, 'widened')):
        n = int(2.0 / PITCH); tot = 0; lon = 0; lon_pts = []
        for i in range(n):
            for j in range(n):
                cx, cy = 0.5 + i * PITCH, 0.5 + j * PITCH
                Q1 = verts(cx, cy, th)
                if not in_quadrant(Q1) or not meets_open_box(Q1, c): continue
                tot += 1
                if not nonlonely(cx, cy, th, c, steps=360):
                    lon += 1; lon_pts.append((round(cx, 3), round(cy, 3)))
        xs = [p[0] for p in lon_pts]; ys = [p[1] for p in lon_pts]
        rec[name] = dict(meeter_cells=tot, lonely_cells=lon, frac=lon / max(tot, 1), area=lon * PITCH ** 2,
                         bbox=None if not lon_pts else (min(xs), max(xs), min(ys), max(ys)))
    out['raster'][deg] = rec
    print('raster', deg, {k: (v['lonely_cells'], v['meeter_cells'], round(v['area'], 3)) for k, v in rec.items()}, flush=True)
    # slide threshold: Q1 pressed then slid d along the floor
    h = 0.5 * (math.cos(th) + math.sin(th)); r = {'t': math.tan(th / 2)}
    for c, name in ((1.0, 'unit'), (1 + W0, 'widened')):
        lo, hi = 0.0, 1.3
        if not nonlonely(h + hi, h, th, c): r[name] = None; continue
        if nonlonely(h + lo, h, th, c): r[name] = 0.0; continue
        for _ in range(22):
            mid = 0.5 * (lo + hi)
            if nonlonely(h + mid, h, th, c): hi = mid
            else: lo = mid
        r[name] = hi
    out['slide'][deg] = r; print('slide', deg, r, flush=True)
# theta = 0 law: F(a) parametrised by u: a = u(2-u^2), F = u^2 sqrt(1-u^2); check the raster boundary
for u in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
    a = u * (2 - u * u); F = u * u * math.sqrt(1 - u * u)
    out['theta0_law'].append(dict(u=u, a=a, F=F, below=nonlonely(0.5 + a, 0.5 + F * 0.98, 0.0, 1.0, 1440),
                                  above=nonlonely(0.5 + a, 0.5 + F * 1.02, 0.0, 1.0, 1440)))
    print('theta0', out['theta0_law'][-1], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'results', 'lonely_exact.json'), 'w'), indent=1)
