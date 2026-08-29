"""VERIFICATION (b): Trump canary, extended to the A43 EXACT filters.

A31's check_trump.py hard-filter suite, plus:
  N1 per-wall <= 3            (the NEW hard row R11)
  N2 all-wall consistency     (Trump has interior squares, so the all-wall kill must NOT fire)
  N5 W1 tight-variety         (every Trump placement must be NON-exempt: exact mu(Q_i) <= 1+eta,
                               its wall-mask window m_low must not exceed 1+eta, and its
                               eroded grid cell must not be exempt -- A38 canary cross-check)
  N6 W2 pair tight-sum        (every pair: mu(Q_i) + mu(Q_j) <= 2 + eta)
Any FAIL here means the corresponding filter is UNSOUND.
"""
from fractions import Fraction as F
import json, math, os, sys
import numpy as np
import lib0 as L
import field_h1 as FH
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', '..', 'results', 'h1')
CERT = os.path.join(FH.REPO, 'certs', 'trump11_certificate.json')

d = json.load(open(CERT))
s_ex = F(str(d['side']))
s = float(s_ex)
k = len(d['squares'])
sq = []
for q in d['squares']:
    cxe, cye, te = F(str(q['cx'])), F(str(q['cy'])), F(str(q['t']))
    cx, cy, t = float(cxe), float(cye), float(te)
    th = 2 * math.atan(t)
    c, sn = math.cos(th), math.sin(th)
    pts = [(cx + 0.5 * (a * c - b * sn), cy + 0.5 * (a * sn + b * c))
           for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    sq.append(dict(c=(cx, cy), ce=(cxe, cye), te=te, th=th, pts=pts))


def sat_gap(P, Q):
    best = -1e9
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            ax, ay = -(y2 - y1), (x2 - x1)
            nn = math.hypot(ax, ay)
            ax, ay = ax / nn, ay / nn
            p = [x * ax + y * ay for x, y in P]
            q = [x * ax + y * ay for x, y in Q]
            best = max(best, max(min(q) - max(p), min(p) - max(q)))
    return best


TOL = 1e-6
edges = [(i, j) for i in range(k) for j in range(i + 1, k)
         if sat_gap(sq[i]['pts'], sq[j]['pts']) < TOL]
wm = [0] * k
for i, q in enumerate(sq):
    xs = [p[0] for p in q['pts']]
    ys = [p[1] for p in q['pts']]
    if min(xs) < TOL:
        wm[i] |= 1
    if min(ys) < TOL:
        wm[i] |= 2
    if max(xs) > s - TOL:
        wm[i] |= 4
    if max(ys) > s - TOL:
        wm[i] |= 8
adj = [0] * k
for i, j in edges:
    adj[i] |= 1 << j
    adj[j] |= 1 << i
deg = [bin(a).count('1') for a in adj]
tot = [deg[i] + L.POP[wm[i]] for i in range(k)]

out = dict(side=str(s_ex), side_float=s, k=k, ss_edges=len(edges), edges=edges,
           wall_masks=wm, sw_edges=sum(L.POP[m] for m in wm), degrees=deg, total_degrees=tot,
           checks=[])
ok = True


def rep(name, val, extra=None):
    global ok
    ok = ok and bool(val)
    out['checks'].append(dict(name=name, pass_=bool(val), detail=extra))
    print(('  PASS ' if val else '  FAIL ') + name + ('' if extra is None else '  [%s]' % extra))


# ---------------------------------------------------------------- A31 hard filters (unchanged)
rep('L1 every square degree >= 2', all(t >= 2 for t in tot))
rep('L5(b) wall-degree <= 2 and adjacent', all(m in L.ALLOWED_SET for m in wm))
rep('L5(d) square-square degree <= 12', max(deg) <= 12)
E = len(edges) + sum(L.POP[m] for m in wm)
rep('L4(a) Euler |E| <= 3k+2', E <= 3 * k + 2, 'E=%d, bound=%d' % (E, 3 * k + 2))
D = L.hop_matrix(adj, k)
m5a = all(L.OKTAB[D[i][j]][wm[i] * 16 + wm[j]] for i in range(k) for j in range(i + 1, k))
rep('L5(a) metric broad phase', m5a)
G = nx.Graph()
G.add_nodes_from(range(k + 4))
G.add_edges_from(edges)
for i in range(k):
    for b in range(4):
        if (wm[i] >> b) & 1:
            G.add_edge(i, k + b)
G2 = G.copy()
for b in range(4):
    G2.add_edge(k + b, k + (b + 1) % 4)
rep('L4(b) planar (H alone)', nx.check_planarity(G, counterexample=False)[0])
rep('L4(b) planar (H + wall 4-cycle)', nx.check_planarity(G2, counterexample=False)[0])
comps = L.components(adj, k)
cw = []
for vs in comps:
    m = 0
    for v in vs:
        m |= wm[v]
    cw.append(m)
ch = True
while ch:
    ch = False
    for a in range(len(cw)):
        for b in range(a + 1, len(cw)):
            if cw[a] & cw[b] and cw[a] != cw[b]:
                cw[a] = cw[b] = cw[a] | cw[b]
                ch = True
rep('L3 no floating component', all(c != 0 for c in cw))
rep('L6 spanning component', any((c & 5) == 5 or (c & 10) == 10 for c in cw))
allw = 0
for m in wm:
    allw |= m
rep('L7 some axis both walls touched', (allw & 5) == 5 or (allw & 10) == 10)

# ---------------------------------------------------------------- NEW A43 EXACT filters
wall_deg = [sum(1 for m in wm if (m >> b) & 1) for b in range(4)]
out['wall_degrees_LBRT'] = wall_deg
rep('N1 per-wall <= 3 (NEW HARD row R11)', max(wall_deg) <= 3, 'LBRT=%s' % wall_deg)

n_interior = sum(1 for m in wm if m == 0)
out['n_interior_squares'] = n_interior
rep('N2 all-wall does NOT fire (Trump has interior squares)', n_interior > 0,
    '%d squares with zero wall mask' % n_interior)

f = FH.field()
thr1, thr2 = f.thr1, f.thr2
cov = [FH.coverage_exact(q['te'], q['ce'][0], q['ce'][1], f) for q in sq]
out['field'] = dict(cert=os.path.relpath(f.path, FH.REPO), eta=str(f.eta),
                    thr1=str(thr1), thr1_float=float(thr1), thr2=str(thr2))
out['trump_coverage_exact'] = [str(c) for c in cov]
out['trump_coverage_float'] = [float(c) for c in cov]
worst = max(cov)
rep('N5 W1: every Trump placement satisfies mu(Q) <= 1 + eta (EXACT rationals)',
    all(c <= thr1 for c in cov),
    'max mu = %.9f, threshold = %.9f, slack = %.9f' % (float(worst), float(thr1),
                                                       float(thr1 - worst)))
rep('N5 field feasibility sanity: every Trump placement has mu(Q) >= 1',
    all(c >= 1 for c in cov), 'min mu = %.9f' % float(min(cov)))

# wall-mask window m_low: the census filter itself must not fire on Trump's masks
gp = os.path.join(RES, 'mlow_grid_a39.npz')
Mg, meta = FH.load_grid(gp) if os.path.exists(gp) else (None, None)
mm = FH.mask_mlow(sorted(set(wm)), Mg, meta, f)
out['trump_mask_windows'] = {str(m): mm[m] for m in mm}
rep('N5 window form: no Trump wall-mask window is certified exempt',
    all(mm[m]['mlow_certified'] <= float(thr1) for m in mm),
    'max window m_low = %.6f' % max(mm[m]['mlow_certified'] for m in mm))

# A38 canary cross-check: the eroded grid cell of each Trump placement must NOT be exempt
if Mg is not None:
    NEG = -1e18
    P = np.full((meta['NT'] + 2, meta['NC'] + 2, meta['NC'] + 2), NEG)
    P[1:-1, 1:-1, 1:-1] = Mg
    Eg = P
    for ax in (0, 1, 2):
        Eg = np.minimum(np.minimum(np.roll(Eg, 1, ax), Eg), np.roll(Eg, -1, ax))
    ero = Eg[1:-1, 1:-1, 1:-1]
    ex = []
    for q in sq:
        t = float(q['te']) % 1.0 if float(q['te']) > 1 else float(q['te'])
        i = min(meta['NT'] - 1, max(0, int(t / meta['ht'])))
        j = int((q['c'][0] - meta['clo']) / meta['hc'])
        kk = int((q['c'][1] - meta['clo']) / meta['hc'])
        inb = 0 <= j < meta['NC'] and 0 <= kk < meta['NC']
        ex.append(bool(inb and ero[i, j, kk] > float(thr1)))
    out['trump_cell_exempt'] = ex
    rep('N5 grid form (A38 canary): no Trump placement lies in an exempt eroded cell',
        not any(ex), '%d/%d exempt' % (sum(ex), len(ex)))

pairsum = [(i, j, cov[i] + cov[j]) for i in range(k) for j in range(i + 1, k)]
wp = max(pairsum, key=lambda z: z[2])
rep('N6 W2: every Trump PAIR satisfies mu+mu <= 2 + eta (EXACT)',
    all(z[2] <= thr2 for z in pairsum),
    'worst pair (%d,%d) = %.9f, threshold %.9f' % (wp[0], wp[1], float(wp[2]), float(thr2)))
rep('N6 window form: no Trump contact edge is killed',
    all(mm[wm[i]]['mlow_certified'] + mm[wm[j]]['mlow_certified'] <= float(thr2)
        for i, j in edges))
totcov = sum(cov, F(0))
rep('A33.1 global: sum of all 11 Trump coverages <= 11 + eta',
    totcov <= f.total, 'sum = %.9f, total mass = %.9f' % (float(totcov), float(f.total)))

# N7 APPROX proxy (report only -- must NOT be used as an exact kill)
def has4(adj, k):
    for a in range(k):
        for b in range(k):
            if b == a or not ((adj[a] >> b) & 1):
                continue
            for c in range(k):
                if c in (a, b) or not ((adj[b] >> c) & 1):
                    continue
                for dd in range(k):
                    if dd in (a, b, c):
                        continue
                    if ((adj[c] >> dd) & 1) and ((adj[dd] >> a) & 1):
                        return True
    return False


out['trump_has_4cycle'] = has4(adj, k)
print('  INFO N7a 4-cycle proxy on Trump: %s  (APPROX -- report only; if True this confirms the '
      'proxy would over-kill the known optimum)' % out['trump_has_4cycle'])

out['verdict'] = 'PASS' if ok else 'FAIL - a hard filter is UNSOUND'
print('\nOVERALL:', out['verdict'])
os.makedirs(RES, exist_ok=True)
json.dump(out, open(os.path.join(RES, 'trump_canary.json'), 'w'), indent=1, default=str)
sys.exit(0 if ok else 1)
