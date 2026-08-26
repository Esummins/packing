"""A32 mode-D driver: decorated frontier per depth, kill shares, validation."""
import os
import sys
import json
import math
import time
import random
import argparse

import core as C
import decor as D

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'results'))
STATE = os.path.normpath(os.path.join(HERE, '..', 'state'))
A31RES = os.path.normpath(os.path.join(HERE, '..', '..', 'A31-structure-count',
                                       'results'))


def load_main(K):
    p = os.path.join(STATE, 'K%d_level%d.json' % (K, K))
    masks = json.load(open(p))['masks']
    out = []
    for m in masks:
        adj, wm = C.decode(K, m)
        r = C.close_checks(K, adj, wm)
        if r['main']:
            out.append((m, adj, wm, r))
    return out


def validate_tilt(K, n=12, seed=3):
    """Exact mode-D leaf count with ONLY tilt propagation must equal A31's exact
    Level-1 gauge_surv for the same graph."""
    import level1 as L1
    rows = load_main(K)
    rnd = random.Random(seed)
    pick = rnd.sample(rows, min(n, len(rows)))
    out = []
    for m, adj, wm, r in pick:
        t = D.DTree(K, adj, wm, use_rot=False, use_l2=False)
        if t.nedge > 9:
            continue
        front = t.enumerate_exact(cap=4_000_000)
        if front is None:
            continue
        gm = 0
        for (i, j), e in C.ctx(K).pidx.items():
            if (adj[i] >> j) & 1:
                gm |= 1 << e
        ex = L1.fanout(K, gm, tuple(wm))
        out.append(dict(K=K, gmask=gm, wm=list(wm), E=t.nedge,
                        a32_leaves=front[-1], a31_gauge_surv=ex['gauge_surv'],
                        agree=front[-1] == ex['gauge_surv']))
        print('  k=%d E=%d  A32 exact leaves=%d  A31 gauge_surv=%d  %s'
              % (K, t.nedge, front[-1], ex['gauge_surv'],
                 'OK' if front[-1] == ex['gauge_surv'] else 'MISMATCH'), flush=True)
    return out


def run_mode_d(K, ngraph, trials, seed=5, exact_edge_cap=7):
    rows = load_main(K)
    rnd = random.Random(seed)
    pick = rnd.sample(rows, min(ngraph, len(rows)))
    recs = []
    for m, adj, wm, r in pick:
        rec = dict(K=K, mask=m, wm=list(wm), E=r['E'], thin=r['thin'])
        for tag, use_rot, use_l2 in (('tilt', False, False),
                                     ('tilt_rot', True, False),
                                     ('all', True, True)):
            t = D.DTree(K, adj, wm, use_rot=use_rot, use_l2=use_l2)
            t0 = time.perf_counter()
            est, bf = t.knuth(trials, seed=seed)
            el = time.perf_counter() - t0
            rec[tag] = dict(
                frontier=[e[0] for e in est], stderr=[e[1] for e in est],
                branch=bf, kills=dict(t.kills), visited=t.visited,
                deferred_L2=t.defer[0],
                sec_per_child=el / max(1, t.visited),
                menu=float(20 ** len(t.ss) * 2 ** len(t.sw)))
        recs.append(rec)
        print('  K=%d E=%d menu=%.3e  tilt-leaves=%.3e  +rot=%.3e  +L2=%.3e'
              % (K, rec['E'], rec['tilt']['menu'], rec['tilt']['frontier'][-1],
                 rec['tilt_rot']['frontier'][-1], rec['all']['frontier'][-1]),
              flush=True)
    return recs


def dead_scan(K, ngraph, cap=120_000, seed=9):
    """Capped EXACT DFS per MAIN graph: how many graphs are proven to have NO
    surviving decoration at all (a graph-level kill produced by decoration-level
    tests)?  'dead' is rigorous; 'alive_capped' only means the tree exceeded the
    node cap."""
    rows = load_main(K)
    rnd = random.Random(seed)
    pick = rnd.sample(rows, min(ngraph, len(rows)))
    out = []
    for m, adj, wm, r in pick:
        rec = dict(K=K, E=r['E'], thin=r['thin'], mask=m)
        for tag, ur, ul in (('tilt', False, False), ('tilt_rot', True, False),
                            ('all', True, True)):
            t = D.DTree(K, adj, wm, use_rot=ur, use_l2=ul)
            t0 = time.perf_counter()
            fr = t.enumerate_exact(cap=cap)
            rec[tag] = dict(exhausted=fr is not None,
                            leaves=(fr[-1] if fr else None),
                            frontier=fr, seconds=time.perf_counter() - t0,
                            visited=t.visited, kills=dict(t.kills))
        out.append(rec)
        print('  K=%d E=%2d thin=%-5s  dead(all)=%s  leaves=%s'
              % (K, r['E'], r['thin'],
                 rec['all']['exhausted'] and rec['all']['leaves'] == 0,
                 rec['all']['leaves']), flush=True)
    ndead = sum(1 for x in out if x['all']['exhausted'] and x['all']['leaves'] == 0)
    ndead_t = sum(1 for x in out if x['tilt']['exhausted']
                  and x['tilt']['leaves'] == 0)
    print('  K=%d: %d/%d graphs PROVEN dead with tilt+rot+L2 (%d with tilt only)'
          % (K, ndead, len(out), ndead_t), flush=True)
    return dict(K=K, n=len(out), dead=ndead, dead_tilt_only=ndead_t, rows=out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--validate', type=int, nargs='*', default=None)
    ap.add_argument('--K', type=int, nargs='*', default=[4, 5, 6])
    ap.add_argument('--ngraph', type=int, default=12)
    ap.add_argument('--trials', type=int, default=200)
    ap.add_argument('--dead', action='store_true')
    ap.add_argument('--cap', type=int, default=120000)
    a = ap.parse_args()
    out = {}
    if a.dead:
        res = []
        for K in a.K:
            res.append(dead_scan(K, a.ngraph, cap=a.cap))
            json.dump(res, open(os.path.join(RES, 'deadscan.json'), 'w'), indent=1)
        sys.exit(0)
    if a.validate is not None:
        ks = a.validate or [3, 4]
        out['validation'] = []
        for K in ks:
            print('validation K=%d' % K, flush=True)
            out['validation'] += validate_tilt(K)
        json.dump(out, open(os.path.join(RES, 'moded_validation.json'), 'w'),
                  indent=1)
    else:
        out['runs'] = {}
        for K in a.K:
            print('mode D K=%d' % K, flush=True)
            out['runs'][K] = run_mode_d(K, a.ngraph, a.trials)
            json.dump(out, open(os.path.join(RES, 'moded.json'), 'w'), indent=1)
