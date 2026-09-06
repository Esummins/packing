"""A59 leg (b) driver: the Level-0 grain census of the trump5 residual polygon.

Run:  python census.py            (full run, ~10 min)
      python census.py --quick    (smaller Monte-Carlo sample)
"""
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
import networkx as nx

import geomlib as G
import count_exact as CE
import canary as CAN

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
LOGS = os.path.join(HERE, '..', 'logs')
os.makedirs(RES, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)
LOGF = open(os.path.join(LOGS, 'census.log'), 'w')


def log(*a):
    m = ' '.join(str(x) for x in a)
    print(m, flush=True)
    LOGF.write(m + '\n')
    LOGF.flush()


# ------------------------------------------------------------------ masks
def build_masks(g):
    """All anchor-element masks that are not PROVABLY infeasible (filter 1)."""
    ok0, bx0 = g.mask_box(0)
    boxes = {0: bx0}
    cur = [0]
    while cur:
        nxt = set()
        for b in cur:
            for i in range(G.NE):
                if (b >> i) & 1:
                    continue
                nb = b | (1 << i)
                if nb in boxes or nb in nxt:
                    continue
                ok, bx = g.mask_box(nb)
                if ok:
                    nxt.add(nb)
                    boxes[nb] = bx
        cur = sorted(nxt)
    adm = sorted(boxes)
    return adm, [boxes[m] for m in adm]


def build_tables(adm, BX):
    n = len(adm)
    COEX = np.zeros((n, n), bool)
    INTER = np.zeros((n, n), bool)
    TOUCH = np.zeros((n, n), bool)
    MIND = np.zeros((n, n))
    for a in range(n):
        for b in range(n):
            COEX[a, b] = G.rect_max_dist(BX[a], BX[b]) >= 1.0 - G.EPS
            INTER[a, b] = G.interleaves(adm[a], adm[b])
            d = G.rect_min_dist(BX[a], BX[b])
            MIND[a, b] = d
            TOUCH[a, b] = d <= G.SQRT2 + G.EPS
    assert (COEX == COEX.T).all() and (INTER == INTER.T).all() and (TOUCH == TOUCH.T).all()
    return COEX, INTER, TOUCH, MIND


# ------------------------------------------------------------------ planarity
def planar_ok(masks, edges):
    """Contact structure drawn in the closed residual polygon: 6 square nodes,
    16 anchor nodes in boundary-cycle order, the 16 cycle edges, and an apex
    node joined to all 16 anchors (the cycle bounds the outer face, since every
    square lies inside the simply-connected region R(s))."""
    Gr = nx.Graph()
    Gr.add_nodes_from(range(23))
    Gr.add_edges_from((i, j) for i, j in edges)
    for i, m in enumerate(masks):
        for e in range(G.NE):
            if (m >> e) & 1:
                Gr.add_edge(i, 6 + e)
    for t in range(16):
        Gr.add_edge(6 + G.CYCLE[t], 6 + G.CYCLE[(t + 1) % 16])
        Gr.add_edge(22, 6 + G.CYCLE[t])
    return nx.check_planarity(Gr, counterexample=False)[0]


def caps_ok(masks, caps):
    cnt = [0] * G.NE
    for m in masks:
        for e in range(G.NE):
            if (m >> e) & 1:
                cnt[e] += 1
                if cnt[e] > caps[e]:
                    return False
    return True


# ------------------------------------------------------------------ canary
def run_canary(g, adm, BX, COEX, INTER, TOUCH, caps):
    r = CAN.derive()
    free = r['free']
    masks = [r['masks'][i] for i in free]
    lab = {v: t for t, v in enumerate(free)}
    edges = sorted((lab[a], lab[b]) for a, b in r['edges'])
    log('CANARY derived grain (A03 contacts, tol 1e-9):')
    for t, v in enumerate(free):
        log('   sq%-2d -> %-14s centre (%.6f, %.6f)'
            % (v, ','.join(CAN.bits_names(masks[t])) or '(none)',
               r['centres'][v][0], r['centres'][v][1]))
    log('   E (A03 labels) =', r['edges'])
    verdict = []
    idx = {}
    for t, m in enumerate(masks):
        if m not in adm:
            verdict.append('mask of square %d (%s) NOT admissible' % (free[t], bin(m)))
        else:
            idx[t] = adm.index(m)
    if len(idx) == len(masks):
        # boxes contain the true centres
        for t, m in enumerate(masks):
            bx = BX[idx[t]]
            cx, cy = r['centres'][free[t]]
            if not (bx[0][0] - 1e-9 <= cx <= bx[0][1] + 1e-9
                    and bx[1][0] - 1e-9 <= cy <= bx[1][1] + 1e-9):
                verdict.append('centre of square %d outside its mask box' % free[t])
        ed = set(edges)
        for a in range(6):
            for b in range(a + 1, 6):
                ia, ib = idx[a], idx[b]
                if not COEX[ia, ib]:
                    verdict.append('pair (%d,%d) fails coexistence' % (free[a], free[b]))
                if INTER[ia, ib]:
                    verdict.append('pair (%d,%d) fails interleave' % (free[a], free[b]))
                if (a, b) in ed and not TOUCH[ia, ib]:
                    verdict.append('edge (%d,%d) fails touch window' % (free[a], free[b]))
    if not caps_ok(masks, caps):
        verdict.append('capacity caps violated')
    if not planar_ok(masks, edges):
        verdict.append('planarity fails')
    ok = not verdict
    log('CANARY verdict:', 'PASS' if ok else 'FAIL ' + '; '.join(verdict))
    return ok, dict(free=free, masks=[int(m) for m in masks],
                    mask_names=[CAN.bits_names(m) for m in masks],
                    edges_a03=[list(e) for e in r['edges']],
                    edges_local=[list(e) for e in edges],
                    centres={str(k): v for k, v in r['centres'].items()},
                    problems=verdict)


# ------------------------------------------------------------------ canonical form
_PERMS6 = None


def perms6():
    global _PERMS6
    if _PERMS6 is None:
        import itertools
        _PERMS6 = list(itertools.permutations(range(6)))
    return _PERMS6


def canon_grain(masks, edges):
    best = None
    es = set(edges)
    for p in perms6():
        nm = tuple(masks[p[t]] for t in range(6))
        ne = []
        for a in range(6):
            for b in range(a + 1, 6):
                if (min(p[a], p[b]), max(p[a], p[b])) in es:
                    ne.append((a, b))
        key = (nm, tuple(sorted(ne)))
        if best is None or key < best:
            best = key
    return best


# ------------------------------------------------------------------ Monte Carlo
def monte_carlo(adm, W, INTER, caps, nwant, seed=20260901):
    """Uniform samples of LABELLED pairwise-admissible structures (filters 1-4),
    by rejection from the uniform measure on M^6 x {0,1}^15; then measure the
    conditional pass rate of the capacity caps and of full planarity."""
    n = len(adm)
    rng = np.random.default_rng(seed)
    pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    INC = np.zeros((n, G.NE), np.int16)
    for a, m in enumerate(adm):
        for e in range(G.NE):
            if (m >> e) & 1:
                INC[a, e] = 1
    capv = np.array(caps, np.int16)
    got = 0
    raw = 0
    n_caps = 0
    n_inter = 0
    n_pl = 0
    stats = dict(by_anch={}, by_edges={}, joint={}, elem_use=np.zeros(G.NE),
                 elem_mult=np.zeros(G.NE), conn=0, loaded=0, sum_mu=0.0,
                 sum_e=0.0, log10fan=[])
    buckets = {}
    B = 200000
    while got < nwant:
        M = rng.integers(0, n, size=(B, 6))
        raw += B
        wt = np.ones(B)
        for (i, j) in pairs:
            wt *= W[M[:, i], M[:, j]]
        acc = rng.random(B) * (2.0 ** 15) < wt
        idx = np.nonzero(acc)[0]
        if idx.size == 0:
            continue
        Ms = M[idx]
        # sample an edge set uniformly among the admissible ones
        Wp = np.stack([W[Ms[:, i], Ms[:, j]] for (i, j) in pairs], 1)   # (k,15)
        E = (Wp == 2) & (rng.random(Wp.shape) < 0.5)
        # caps
        cnt = INC[Ms].sum(1)
        okc = (cnt <= capv[None, :]).all(1)
        oki = np.ones(Ms.shape[0], bool)
        for (i, j) in pairs:
            oki &= ~INTER[Ms[:, i], Ms[:, j]]
        for t in range(Ms.shape[0]):
            if got >= nwant:
                break
            got += 1
            if oki[t]:
                n_inter += 1
            if not okc[t]:
                continue
            n_caps += 1
            if not oki[t]:
                continue
            masks = [int(adm[v]) for v in Ms[t]]
            edges = [pairs[q] for q in range(15) if E[t, q]]
            if not planar_ok(masks, edges):
                continue
            n_pl += 1
            na = sum(1 for m in masks if m)
            ne = len(edges)
            smu = sum(bin(m).count('1') for m in masks)
            stats['by_anch'][na] = stats['by_anch'].get(na, 0) + 1
            stats['by_edges'][ne] = stats['by_edges'].get(ne, 0) + 1
            stats['joint'][(na, ne)] = stats['joint'].get((na, ne), 0) + 1
            stats['sum_mu'] += smu
            stats['sum_e'] += ne
            stats['log10fan'].append(ne * math.log10(20.0) + smu * math.log10(2.0))
            deg = [0] * 6
            for a, b in edges:
                deg[a] += 1
                deg[b] += 1
            if all(deg[i] + bin(masks[i]).count('1') >= 2 for i in range(6)):
                stats['loaded'] += 1
            gg = nx.Graph()
            gg.add_nodes_from(range(6))
            gg.add_edges_from(edges)
            comp = list(nx.connected_components(gg))
            anch = [set() for _ in range(6)]
            for i in range(6):
                anch[i] = set(e for e in range(G.NE) if (masks[i] >> e) & 1)
            if len(comp) == 1 and all(anch[i] for i in range(6)):
                stats['conn'] += 1
            for e in range(G.NE):
                k = sum(1 for m in masks if (m >> e) & 1)
                if k:
                    stats['elem_use'][e] += 1
                    stats['elem_mult'][e] += k
            key = (na, ne)
            buckets.setdefault(key, [])
            if len(buckets[key]) < 80:
                buckets[key].append((masks, edges))
    return dict(n_sampled=got, n_raw=raw, n_caps=n_caps, n_inter=n_inter,
                n_pass=n_pl, stats=stats, buckets=buckets)


# ------------------------------------------------------------------ main
def main():
    quick = '--quick' in sys.argv
    t0 = time.time()
    log('A59 leg (b): Level-0 grain census of the trump5 residual polygon')
    log('s-window [%.6f, %.6f], %d sub-intervals' % (G.SLO, G.S0, G.NSUB))
    g = G.Geometry()
    log('capacity caps:', dict(zip(G.NAMES, g.caps)))
    adm, BX = build_masks(g)
    n = len(adm)
    log('admissible anchor masks: %d' % n)
    bysize = {}
    for m in adm:
        bysize[bin(m).count('1')] = bysize.get(bin(m).count('1'), 0) + 1
    log('   by |mu|:', bysize)

    COEX, INTER, TOUCH, MIND = build_tables(adm, BX)
    log('max mask-box min-distance = %.6f  (2*sqrt2 = %.6f) -> hop bound vacuous '
        'for hops >= 2' % (MIND.max(), 2 * G.SQRT2))
    log('pair-table densities: COEX %.4f  TOUCH %.4f  INTERLEAVE %.4f'
        % (COEX.mean(), TOUCH.mean(), INTER.mean()))

    ok, cinfo = run_canary(g, adm, BX, COEX, INTER, TOUCH, g.caps)
    if not ok:
        log('*** CANARY FAILED -- census run is discarded per the T4 contract ***')

    # ---------------- exact ablation (Burnside over S6)
    Ws = [('1 mask admissibility', 2.0 * np.ones((n, n))),
          ('2 + pairwise coexistence', 2.0 * COEX),
          ('3 + touching window', COEX * (1.0 + TOUCH)),
          ('4 + hop bound', COEX * (1.0 + TOUCH)),
          ('6a + planarity(interleave)', (COEX & ~INTER) * (1.0 + TOUCH))]
    ab = []
    Wfinal = None
    for name, W in Ws:
        if name.startswith('4 '):
            ab.append((name, ab[-1][1], 'identical to level 3 (vacuous, proved)'))
            continue
        t = time.time()
        tot, _ = CE.burnside(W)
        ab.append((name, tot, '%.1fs' % (time.time() - t)))
        log('ablation %-28s -> %d grains   (%s)' % (name, tot, ab[-1][2]))
        Wfinal = W
    W4 = COEX * (1.0 + TOUCH)
    pc = CE.prefix_counts(W4)
    log('exact per-prefix growth curve (labelled, filters 1-4):', pc)
    pc6 = CE.prefix_counts(Wfinal)
    log('exact per-prefix growth curve (labelled, filters 1-4+interleave):', pc6)

    # ---------------- exact breakdown by number of anchored squares
    log('exact breakdown by #anchored squares (interpolating the empty-mask weight)')
    vals = []
    for z in range(7):
        vw = np.ones(n)
        vw[adm.index(0)] = float(z)
        tt, _ = CE.burnside(Wfinal, vw=vw)
        vals.append((Fraction(z), Fraction(tt)))
        log('   z=%d -> %d' % (z, tt))
    # P(z) = sum_j c_j z^(6-j);  Lagrange interpolation over Fractions
    coef = [Fraction(0)] * 7
    for i, (zi, yi) in enumerate(vals):
        basis = [Fraction(1)]
        den = Fraction(1)
        for j, (zj, _) in enumerate(vals):
            if i == j:
                continue
            nb = [Fraction(0)] * (len(basis) + 1)
            for t, cc in enumerate(basis):
                nb[t] -= cc * zj
                nb[t + 1] += cc
            basis = nb
            den *= (zi - zj)
        for t, cc in enumerate(basis):
            coef[t] += yi * cc / den
    by_anch_exact = {}
    for t, cc in enumerate(coef):          # coefficient of z^t  = 6 - #anchored
        assert cc.denominator == 1, cc
        by_anch_exact[6 - t] = int(cc)
    log('   exact by #anchored:', {k: by_anch_exact[k] for k in sorted(by_anch_exact)})

    # ---------------- rigorous lower bound (see lower_bound.py for the proof)
    DISJ = np.zeros((n, n), bool)
    for a in range(n):
        for b in range(n):
            DISJ[a, b] = (adm[a] & adm[b]) == 0
    lb, _ = CE.burnside((COEX & ~INTER & DISJ).astype(float))
    log('rigorous LOWER bound (E empty, masks pairwise element-disjoint and '
        'non-crossing; caps and planarity then automatic): %d' % lb)

    # ---------------- Monte Carlo for caps + full planarity
    nwant = 5000 if quick else 400000
    log('Monte Carlo: %d uniform samples of pairwise-admissible labelled structures'
        % nwant)
    mc = monte_carlo(adm, W4, INTER, g.caps, nwant)
    N = mc['n_sampled']
    f_caps = mc['n_caps'] / N
    f_all = mc['n_pass'] / N
    f_int = mc['n_inter'] / N
    se = math.sqrt(max(f_all * (1 - f_all), 1e-12) / N)
    L4 = ab[3][1]
    est_caps = int(L4 * f_caps)
    est_all = int(L4 * f_all)
    log('   caps pass rate     %.5f' % f_caps)
    log('   caps+planar rate   %.5f  (+- %.5f, 1 sigma)' % (f_all, se))
    log('   estimated grains after caps           %.4e' % est_caps)
    log('   estimated grains after caps+planarity %.4e  (+- %.2e)'
        % (est_all, L4 * se))
    # consistency check: the MC measures LABELLED structures, so compare against the
    # exact LABELLED ratio Z_id(interleave)/Z_id(level 4), not the orbit ratio
    f_int_exact = pc6[5] / pc[5]
    log('   MC validation: interleave rate MC %.6f vs exact labelled %.6f (%.2f sigma); '
        'orbit ratio %.6f' % (f_int, f_int_exact,
           abs(f_int - f_int_exact) / max(math.sqrt(f_int_exact *
               (1 - f_int_exact) / N), 1e-12), ab[4][1] / ab[3][1]))

    st = mc['stats']
    npass = max(mc['n_pass'], 1)
    log('   soft stats over passing samples: connected&all-anchored %.4f, '
        'all squares loaded (deg>=2) %.4f'
        % (st['conn'] / npass, st['loaded'] / npass))
    log('   mean sum|mu| = %.3f, mean |E| = %.3f'
        % (st['sum_mu'] / npass, st['sum_e'] / npass))

    # ---------------- stratified samples
    samples = []
    keys = sorted(mc['buckets'])
    pos = 0
    while len(samples) < 1000:
        added = 0
        for k in keys:
            b = mc['buckets'][k]
            if pos < len(b) and len(samples) < 1000:
                masks, edges = b[pos]
                cm, ce = canon_grain(masks, edges)
                samples.append(dict(masks=[int(x) for x in cm],
                                    edges=[list(e) for e in ce],
                                    n_anchored=k[0], n_edges=k[1]))
                added += 1
        pos += 1
        if added == 0:
            break
    p = os.path.join(RES, 'grains_sample.jsonl')
    with open(p, 'w') as fh:
        for s in samples:
            fh.write(json.dumps(s) + '\n')
    log('wrote %d stratified sample grains to %s' % (len(samples), p))

    # ---------------- summary json
    elem_use = {G.NAMES[e]: dict(grain_frac=float(st['elem_use'][e] / npass),
                                 mean_mult=float(st['elem_mult'][e] / npass))
                for e in range(G.NE)}
    fan = st['log10fan']
    summ = dict(
        n_grains=est_all,
        n_grains_exact_upper_bound=ab[4][1],
        n_grains_rigorous_lower_bound=lb,
        n_grains_estimate_note='caps and full planarity are Monte-Carlo estimated; '
                               'levels 1-4 and the interleave sub-filter are exact',
        n_masks=n,
        masks_by_size=bysize,
        caps=dict(zip(G.NAMES, g.caps)),
        ablation={a[0]: a[1] for a in ab},
        ablation_est={'5 + capacity caps': est_caps,
                      '6 + full planarity': est_all},
        prefix_curve_labelled_L4=pc,
        prefix_curve_labelled_L6a=pc6,
        by_anchored_exact={str(k): by_anch_exact[k] for k in sorted(by_anch_exact)},
        by_anchored_mc={str(k): v for k, v in sorted(st['by_anch'].items())},
        by_edges_mc={str(k): v for k, v in sorted(st['by_edges'].items())},
        joint_mc={'%d_%d' % k: v for k, v in sorted(st['joint'].items())},
        elem_usage_mc=elem_use,
        mc=dict(n_sampled=mc['n_sampled'], n_raw=mc['n_raw'],
                caps_rate=f_caps, caps_planar_rate=f_all, sigma=se,
                interleave_rate_mc=f_int,
                interleave_rate_exact_labelled=f_int_exact,
                interleave_rate_exact_orbits=ab[4][1] / ab[3][1]),
        soft=dict(connected_all_anchored=st['conn'] / npass,
                  all_loaded=st['loaded'] / npass,
                  mean_sum_mu=st['sum_mu'] / npass, mean_edges=st['sum_e'] / npass),
        level1_fanout_log10=dict(mean=float(np.mean(fan)) if fan else None,
                                 p50=float(np.median(fan)) if fan else None,
                                 p95=float(np.percentile(fan, 95)) if fan else None),
        canary='PASS' if ok else 'FAIL',
        canary_grain=cinfo,
        runtime_s=round(time.time() - t0, 1),
    )
    with open(os.path.join(RES, 'census_summary.json'), 'w') as fh:
        json.dump(summ, fh, indent=1)
    log('runtime %.1fs' % (time.time() - t0))
    return summ


if __name__ == '__main__':
    main()
