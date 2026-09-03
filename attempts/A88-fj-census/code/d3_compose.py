"""A88 D3: compose the Level-0 and Level-1 numbers into the DECORATED bracket at
k_H = 11, and pin the explicit lower-bound structure."""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import json
import math
from fractions import Fraction

import networkx as nx
import numpy as np

import a88lib as A

K = 11
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')


def aut_size(wm, edges):
    """|Aut| of the Level-0 structure = the stabiliser in S_11 x D4: the
    automorphism group of (11 square nodes + 4 wall nodes + the wall 4-cycle),
    squares and walls in different colour classes."""
    G = nx.Graph()
    for i in range(K):
        G.add_node(i, col=0)
    for b in range(4):
        G.add_node(K + b, col=1)
    G.add_edges_from(edges)
    for i in range(K):
        for b in range(4):
            if (wm[i] >> b) & 1:
                G.add_edge(i, K + b)
    for b in range(4):
        G.add_edge(K + b, K + (b + 1) % 4)
    gm = nx.algorithms.isomorphism.GraphMatcher(
        G, G, node_match=lambda a, b: a['col'] == b['col'])
    return sum(1 for _ in gm.isomorphisms_iter())


def main():
    bs = json.load(open(os.path.join(RES, 'burnside88.json')))
    r3 = json.load(open(os.path.join(RES, 'mc_run3.json')))
    l1 = json.load(open(os.path.join(RES, 'level1_88.json')))
    lb0 = json.load(open(os.path.join(RES, 'lower88.json')))
    surv = [json.loads(x) for x in
            open(os.path.join(RES, 'level0_survivors.jsonl'))]

    UB0 = bs['k11_factorable_orbits_UB']
    p = r3['F0_rate']
    sp = r3['F0_rate_sigma']
    N0 = UB0 * p
    N0s = UB0 * sp

    # ---- decoration fan-out per graph (MC, 300 uniformly sampled survivors)
    lg = [r['tot_hat_log10'] for r in l1['rows'] if r['tot_hat_log10'] is not None]
    vals = np.array([10.0 ** x for x in lg])
    mean_dec = float(vals.mean())
    med_dec = float(np.median(vals))
    # K0-1 & K0-3 conditional pass rates (decoration level)
    k01 = np.array([r['K0_1_rate'] for r in l1['rows']
                    if r['K0_1_rate'] is not None])
    k013 = np.array([r['K0_1_and_3_rate'] for r in l1['rows']
                     if r['K0_1_and_3_rate'] is not None])
    k03 = np.array([r['K0_3_rate'] for r in l1['rows']
                    if r['K0_3_rate'] is not None])
    # decoration-count-weighted rate (what multiplies the total)
    w = np.array([10.0 ** r['tot_hat_log10'] for r in l1['rows']
                  if r['tot_hat_log10'] is not None])
    r01 = np.array([r['K0_1_rate'] for r in l1['rows']
                    if r['tot_hat_log10'] is not None])
    r013 = np.array([r['K0_1_and_3_rate'] for r in l1['rows']
                     if r['tot_hat_log10'] is not None])
    wr01 = float((w * r01).sum() / w.sum())
    wr013 = float((w * r013).sum() / w.sum())

    # ---- explicit DECORATED lower bound: the all-corner sub-menu of ONE graph
    best = None
    for s in surv:
        edges = [tuple(e) for e in s['edges']]
        Ess = len(edges)
        Esw = sum(A.POP[m] for m in s['wm'])
        if best is None or Ess > best[0]:
            best = (Ess, Esw, s['wm'], edges)
    Ess, Esw, wm, edges = best
    f = A.f0_flags(K, edges, wm)
    assert all(f.values()), 'lower-bound graph must pass full F0'
    ao = A.acyclic_orientations(K, edges)
    count = (8 ** Ess) * ao
    aut = aut_size(wm, edges)
    lb_dec = count // aut
    # sanity: the all-corner decoration is tilt-feasible, K0-1 and K0-3 clean
    sw = {(i, b): 'CW' for i in range(K) for b in range(4) if (wm[i] >> b) & 1}
    ss = [('C', j, 0, True) for (i, j) in edges]
    dec = A.Decoration(K, edges, wm, ss, sw)
    ts = dec.tilt_system()
    ok3, _ = dec.k0_3(ts)
    ok2, _ = A.k0_2(K, edges, wm)

    # ---- crude decorated UPPER bound
    # planarity of H alone caps Ess <= 3*11-6 = 27; the Euler bound caps
    # Ess+Esw <= 3k+2 = 35; N1 caps Esw <= 12.  max menu = 20^27 * 2^8.
    max_menu_log10 = 27 * math.log10(20.0) + 8 * math.log10(2.0)
    ub_dec_log10 = math.log10(UB0) + max_menu_log10

    out = dict(
        level0=dict(UB_exact=UB0, MC_point_estimate=N0, sigma=N0s,
                    LB_exact=lb0['LOWER_BOUND_orbits']),
        decoration_fanout_per_graph=dict(
            n_graphs=len(lg), mean=mean_dec, mean_log10=math.log10(mean_dec),
            median=med_dec, median_log10=math.log10(med_dec),
            max_log10=float(max(lg)), p05_log10=float(np.percentile(lg, 5)),
            p95_log10=float(np.percentile(lg, 95)),
            note='heavy-tailed; the arithmetic mean is dominated by the top few '
                 'graphs and is the noisiest of these statistics'),
        A31_extrapolated_fanout_k11=6.478810725671843e+18,
        k0_decoration_rates=dict(
            K0_1_mean=float(k01.mean()), K0_1_median=float(np.median(k01)),
            K0_3_mean=float(k03.mean()), K0_3_median=float(np.median(k03)),
            K0_1_and_3_mean=float(k013.mean()),
            K0_1_decoration_weighted=wr01,
            K0_1_and_3_decoration_weighted=wr013),
        decorated_census_k11=dict(
            point_estimate_F0=N0 * mean_dec,
            point_estimate_F0_log10=math.log10(N0 * mean_dec),
            point_estimate_F0_median_fanout_log10=math.log10(N0 * med_dec),
            point_estimate_F0_K01_K03=N0 * mean_dec * wr013,
            point_estimate_F0_K01_K03_log10=math.log10(N0 * mean_dec * wr013),
            upper_bound_log10=ub_dec_log10,
            upper_bound_note='crude: exact Level-0 Burnside UB x the largest '
                             'possible gauge-fixed menu 20^27 * 2^8 (Ess <= 27 '
                             'by planarity of H alone, Esw <= 8 by the Euler '
                             'bound at Ess = 27)',
            lower_bound=lb_dec, lower_bound_log10=math.log10(lb_dec)),
        lower_bound_structure=dict(
            wall_mask=wm, ss_edges=[list(e) for e in edges], Ess=Ess, Esw=Esw,
            acyclic_orientations=ao, all_corner_decorations=str(count),
            aut_size=aut, orbits=lb_dec,
            F0=dict((a, bool(b)) for a, b in f.items()),
            all_corner_tilt_feasible=bool(ts['feasible']),
            K0_1=bool(dec.k0_1()), K0_3=bool(ok3), K0_2=bool(ok2),
            definition='every square-square contact corner-on-edge (8 gauge '
                       'types each) with the strict class order given by an '
                       'ACYCLIC ORIENTATION of the square graph, every '
                       'square-wall contact corner-on-wall: 8^Ess * AO(G) '
                       'decorations, all tilt-feasible by construction, no '
                       'wall-flush so K0-1 holds and no flush link so K0-3 '
                       'holds'),
    )
    with open(os.path.join(RES, 'd3_compose.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
