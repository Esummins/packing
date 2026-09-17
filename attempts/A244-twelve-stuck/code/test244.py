"""A244 self-tests: the cells, the meeting test (including the CROSS configuration that a
vertex-based crowd row would miss), the crowd rows' jacobian, and the verifier."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells244 as C
import crowd244 as W
import verify244 as V

ok = True


def chk(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print('%-52s %s %s' % (name, 'ok' if cond else 'FAIL', extra))


# 1. at s = 4 the twelve cells are the twelve boundary cells of the 4 x 4 grid, and they tile the
#    border strip exactly.
r = {n: C.cell_rect(n, 4.0) for n in C.CELLS}
grid = {(i, j) for i in range(4) for j in range(4) if i in (0, 3) or j in (0, 3)}
got = {(int(round(v[0])), int(round(v[2]))) for v in r.values()}
chk('s=4: the twelve cells are the 4x4 grid border', got == grid and len(r) == 12)

# 2. a square centred on the frame point (1,1) meets exactly its corner's three cells
m = C.meeter_sets(np.array([1.0, 1.0, 0.0] + [9.0, 9.0, 0.0] * 10 + [12.0]))
hit = [n for n, v in m.items() if 0 in v]
chk('square at (1,1) meets BL00, BL01, BL10 only', sorted(hit) == ['BL00', 'BL01', 'BL10'], hit)

# 3. CROSS: a 45-degree unit square centred on a cell meets it with NO vertex of either inside
#    the other -- the configuration A217's vertex crowd rows cannot express.
cx, cy, th = 0.5, 1.5, math.pi / 4
d = C.overlap_depth(cx, cy, th, C.cell_rect('BL01', 4.0))
q = C.square_corners(cx, cy, th)
x0, x1, y0, y1 = C.cell_rect('BL01', 4.0)
vin = any(x0 < a < x1 and y0 < b < y1 for a, b in q)
box = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
n = C.square_normals(th)
cin = any(all((np.array(p) - np.array([cx, cy])) @ nn < 0.5 for nn in list(n) + list(-n)) for p in box)
chk('cross: 45-deg square on BL01 meets it, no vertex inside', d > 0 and not vin and not cin,
    'depth %.4f vin %s cin %s' % (d, vin, cin))

# 4. crowd-row jacobian against finite differences
rng = np.random.default_rng(0)
z = np.zeros(34)
z[0:33:3] = rng.uniform(1, 3, 11)
z[1:33:3] = rng.uniform(1, 3, 11)
z[2:33:3] = rng.uniform(0, 1.5, 11)
z[33] = 4.2
des = [('BL00', 0), ('BL01', 1), ('TR10', 2), ('BR00', 3)]
w = W.witness_init(z, des)
g0, J = W.crowd_rows(w, des, 0.01)
err = 0.0
for k in range(len(w)):
    h = 1e-7
    wp = w.copy(); wp[k] += h
    wm = w.copy(); wm[k] -= h
    fd = (W.crowd_rows(wp, des, 0.01)[0] - W.crowd_rows(wm, des, 0.01)[0]) / (2 * h)
    err = max(err, float(np.abs(fd - J[:, k]).max()))
chk('crowd rows: jacobian vs finite differences', err < 1e-6, 'max err %.2e' % err)

# 5. the verifier on an exact packing: 11 of the 4x4 grid squares at s = 4.  Contained,
#    disjoint, and NOT 12-stuck (every cell is met by exactly one square).
cent = [(i + 0.5, j + 0.5) for i in range(4) for j in range(4)][:11]
c = V.certify(cent, [0.0] * 11, 4.0, need=('twelve',))
chk('verifier: 4x4 grid minus 5 is a packing', c['contained'] and c['disjoint'], c['s_cert'])
chk('verifier: 4x4 grid minus 5 is NOT 12-stuck', not c['twelve_stuck'])

# 6. the verifier's inflation: a configuration with a -1e-16 pair gap certifies at lam > 1
cent2 = [(0.5, 0.5), (1.5 - 1e-13, 0.5)] + [(2.5 + k, 2.5) for k in range(2)] + \
        [(0.5 + k, 3.5) for k in range(7)]
c2raw = V.certify(cent2, [0.0] * 11, 8.0, need=('four',), lam=1.0)
c2 = V.certify(cent2, [0.0] * 11, 8.0, need=('four',))
chk('verifier: an overlapping configuration is rejected at lam = 1', not c2raw['disjoint'],
    'pair_min %.2e' % c2raw['pair_min'])
chk('verifier: inflation makes an almost-packing a packing', c2['contained'] and c2['disjoint'],
    'lam %s pair_min %.2e' % (c2['lam'], c2['pair_min']))

print('ALL OK' if ok else 'FAILURES')
sys.exit(0 if ok else 1)
