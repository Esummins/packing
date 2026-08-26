"""SOUNDNESS CHECK: extract the contact graph of Trump's 11-square packing (the known
optimum, s = 3.877084) and verify that it passes every HARD filter used at Level 0.
A hard filter that rejected it would be unsound."""
from fractions import Fraction as F
import json, math, os, sys
import lib0 as L
import networkx as nx

d = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                'certs', 'trump11_certificate.json')))
s = float(F(d['side']))
k = len(d['squares'])
sq = []
for q in d['squares']:
    cx, cy, t = float(F(q['cx'])), float(F(q['cy'])), float(F(q['t']))
    th = 2 * math.atan(t)
    c, sn = math.cos(th), math.sin(th)
    pts = [(cx + 0.5 * (a * c - b * sn), cy + 0.5 * (a * sn + b * c))
           for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    sq.append(dict(c=(cx, cy), th=th, pts=pts))


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
            gap = max(min(q) - max(p), min(p) - max(q))
            best = max(best, gap)
    return best


TOL = 1e-6
edges = []
for i in range(k):
    for j in range(i + 1, k):
        g = sat_gap(sq[i]['pts'], sq[j]['pts'])
        if g < TOL:
            edges.append((i, j))
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
print('contact edges (square-square):', len(edges), edges)
print('wall masks:', wm, ' wall edges:', sum(L.POP[m] for m in wm))
print('square-square degrees:', deg)
tot = [deg[i] + L.POP[wm[i]] for i in range(k)]
print('total degrees:', tot)

ok = True


def rep(name, val):
    global ok
    print(('  PASS ' if val else '  FAIL ') + name)
    ok = ok and val


print('HARD FILTERS on Trump\'s ACTIVE-CONTACT graph (k=11):')
rep('Fact 0 simple graph', True)
rep('L1  every square degree >= 2', all(t >= 2 for t in tot))
rep('L5(b) wall-degree <= 2 and adjacent', all(m in L.ALLOWED_SET for m in wm))
rep('L5(d) square-square degree <= 12', max(deg) <= 12)
E = len(edges) + sum(L.POP[m] for m in wm)
rep('L4(a) Euler |E| <= 3k+2 (=%d), got %d' % (3 * k + 2, E), E <= 3 * k + 2)
D = L.hop_matrix(adj, k)
m5a = True
for i in range(k):
    for j in range(i + 1, k):
        t = L.OKTAB[D[i][j]]
        if not t[wm[i] * 16 + wm[j]]:
            m5a = False
            print('    L5a violated for pair', i, j, wm[i], wm[j], D[i][j])
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
changed = True
while changed:
    changed = False
    for a in range(len(cw)):
        for b in range(a + 1, len(cw)):
            if cw[a] & cw[b] and cw[a] != cw[b]:
                cw[a] = cw[b] = cw[a] | cw[b]
                changed = True
rep('L3 no floating component', all(c != 0 for c in cw))
rep('L6 spanning component (opposite walls)',
    any((c & 5) == 5 or (c & 10) == 10 for c in cw))
allw = 0
for m in wm:
    allw |= m
rep('L7 some axis has both walls touched', (allw & 5) == 5 or (allw & 10) == 10)
print('SOFT columns:')
print('  |E| = %d, Maxwell threshold 3k+1 = %d  ->  %s' % (
    E, 3 * k + 1, 'meets' if E >= 3 * k + 1 else 'DOES NOT meet (needs flush rows)'))
for b, nm in enumerate('LBRT'):
    print('  wall %s degree %d' % (nm, sum(1 for m in wm if (m >> b) & 1)))
print('  min total degree %d (thin/L2 present: %s)' % (min(tot), 2 in tot))
print('\nOVERALL:', 'PASS - no hard filter rejects the known optimum' if ok
      else 'FAIL - a hard filter is UNSOUND')
