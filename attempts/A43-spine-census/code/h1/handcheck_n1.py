"""VERIFICATION (c): one documented hand-check of a k=4 MAIN survivor killed by N1.

N1 (EXACT, elementary).  Two squares touching the SAME wall have centres within sqrt2/2 of it,
so their distances to that wall lie in [1/2, sqrt2/2] and differ by at most sqrt2/2 - 1/2 =
0.2071067811865476.  Interior-disjoint unit squares have centre distance >= 1, so their
ALONG-wall coordinates differ by at least
    sqrt(1 - (sqrt2/2 - 1/2)^2) = sqrt(1 - 0.042893...) = 0.9783183874...
Every centre's along-wall coordinate lies in [1/2, s - 1/2], a range of length s - 1 <= s0 - 1 =
2.877084.  With q squares on one wall the extreme along-wall coordinates differ by at least
(q-1)*0.9783183874, so (q-1)*0.9783183874 <= 2.877084, i.e. q - 1 <= 2.9408..., q <= 3.
"""
import json, math, os
import numpy as np
import lib0 as L
import run_level0_h1 as R

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', '..', 'results', 'h1')

SEP = math.sqrt(1 - (math.sqrt(2) / 2 - 0.5) ** 2)
S0 = 969271 / 250000

k = 4
found = None
for gmask, aut in L.graph_reps(k):
    adj, edges = L.mask_to_adj(gmask, k)
    degA = [bin(adj[i]).count('1') for i in range(k)]
    D = L.hop_matrix(adj, k)
    comps = L.components(adj, k)
    ctx = (degA, edges, D, comps, len(edges))
    per = [[m for m in L.ALLOWED if L.POP[m] >= 2 - degA[i]] for i in range(k)]
    N = 1
    for p in per:
        N *= len(p)
    if N == 0:
        continue
    W = R.build_W(per, 0, N)
    cand = R.canonical_rows(W, aut, k)
    if not cand.size:
        continue
    Wc = W[cand]
    f, s, thin, E, wallcap3, allwall, n5, n6e, n6p = R.eval_filters(Wc, k, ctx)
    pl = np.zeros(Wc.shape[0], dtype=bool)
    for t in range(Wc.shape[0]):
        pl[t] = L.is_planar(k, tuple(edges), tuple(int(x) for x in Wc[t]), True)
    main = ((f & 1) != 0) & ((f & 2) != 0) & ((f & 4) != 0) & pl & \
           ((f & 8) != 0) & ((f & 16) != 0)
    hit = np.nonzero(main & ~wallcap3)[0]
    if hit.size:
        t = int(hit[0])
        found = dict(k=k, gmask=int(gmask), edges=[list(e) for e in edges],
                     wall_masks=[int(x) for x in Wc[t]])
        break

assert found is not None, 'no k=4 MAIN survivor killed by N1 found'
wm = found['wall_masks']
wd = [sum(1 for m in wm if (m >> b) & 1) for b in range(4)]
b = int(np.argmax(wd))
q = wd[b]
found.update(
    wall_degrees_LBRT=wd, violating_wall='LBRT'[b], squares_on_that_wall=q,
    separation_lower_bound=SEP,
    required_along_wall_extent=(q - 1) * SEP,
    available_along_wall_extent=S0 - 1,
    violation='%d squares on wall %s force along-wall extent >= %d*%.10f = %.10f, but the '
              'available range is s-1 <= %.6f - 1 = %.10f. %.10f > %.10f, contradiction; the '
              'structure is impossible.' % (q, 'LBRT'[b], q - 1, SEP, (q - 1) * SEP, S0,
                                            S0 - 1, (q - 1) * SEP, S0 - 1),
    max_squares_per_wall=1 + math.floor((S0 - 1) / SEP))
print(json.dumps(found, indent=1))
json.dump(found, open(os.path.join(RES, 'handcheck_n1.json'), 'w'), indent=1)
