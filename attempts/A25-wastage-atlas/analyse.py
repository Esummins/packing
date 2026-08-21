#!/usr/bin/env python3
"""
analyse.py -- A25 deliverable 3: the headline map (dead area vs tilt and
distance-to-wall / separation), atlas coverage statistics, and the minimum-k
question:  how many mid-tilt squares must a case-tree node fix, in cells whose
atlas values are pairwise region-disjoint, before  sum dead_lb > s^2 - 11  fires?

Usage:  python analyse.py --single results/atlas_single_3.84.json \
                          [--pair results/atlas_pair_3.84.json] --out results/headline_3.84.json
"""
import argparse
import json
import math
from fractions import Fraction as F

from query import D4, rect_disjoint


def load(path):
    with open(path) as f:
        return json.load(f)


def orbit_images(cell, s):
    """the 8 D4 images of an atlas cell: (centre box, theta box, value, regions)."""
    out = []
    x0, x1 = F(cell['cx'][0]), F(cell['cx'][1])
    y0, y1 = F(cell['cy'][0]), F(cell['cy'][1])
    a0, a1 = cell['theta_deg']
    v = F(cell['dead_lb'])
    seen = set()
    for g in D4:
        gx0, gx1, gy0, gy1 = g.box(x0, x1, y0, y1, s)
        ga = (90.0 - a1, 90.0 - a0) if g.flip else (a0, a1)
        key = (gx0, gx1, gy0, gy1, ga)
        if key in seen:
            continue
        seen.add(key)
        regs = [g.box(F(r[0]), F(r[2]), F(r[1]), F(r[3]), s) for r in cell['regions']]
        out.append(dict(box=(gx0, gx1, gy0, gy1), theta=ga, v=v, regions=regs,
                        id=cell['id'], nsq=1))
    return out


def pair_images(cell, s):
    out = []
    A, B = cell['A'], cell['B']
    ax0, ax1 = F(A['cx'][0]), F(A['cx'][1])
    ay0, ay1 = F(A['cy'][0]), F(A['cy'][1])
    bx0, bx1 = F(B['cx'][0]), F(B['cx'][1])
    by0, by1 = F(B['cy'][0]), F(B['cy'][1])
    v = F(cell['dead_lb'])
    seen = set()
    for g in D4:
        A2 = g.box(ax0, ax1, ay0, ay1, s)
        B2 = g.box(bx0, bx1, by0, by1, s)
        key = A2 + B2
        if key in seen:
            continue
        seen.add(key)
        regs = [g.box(F(r[0]), F(r[2]), F(r[1]), F(r[3]), s) for r in cell['regions']]
        out.append(dict(box=A2, box2=B2, theta=A['theta'], v=v, regions=regs,
                        id=cell['id'], nsq=2))
    return out


def boxes_of(item):
    return [item['box']] + ([item['box2']] if item.get('box2') else [])


def can_coexist(u, w):
    """necessary condition for two DISTINCT squares in these centre boxes to have
    disjoint interiors: max centre distance over the boxes >= 1."""
    for a in boxes_of(u):
        for b in boxes_of(w):
            dx = max(abs(float(a[1] - b[0])), abs(float(b[1] - a[0])))
            dy = max(abs(float(a[3] - b[2])), abs(float(b[3] - a[2])))
            if math.hypot(dx, dy) < 1.0:
                return False
    return True


def regions_disjoint(u, w):
    for a in u['regions']:
        for b in w['regions']:
            if not rect_disjoint(a, b):
                return False
    return True


def best_for_k(items, kmax=6, beam=120):
    """beam search: for every k <= kmax, the largest sum of atlas values obtainable
    from region-disjoint, pairwise-placeable entries covering exactly <= k squares.
    Returns {k: (total, chosen)}.  (Greedy alone answers the wrong question: it
    maximises value, not the NUMBER of squares needed.)"""
    srt = sorted(items, key=lambda it: -float(it['v']))
    # keep the strongest entries BUT make sure single-square entries are present:
    # the pair entries all have nsq=2 and would otherwise crowd out every k=1 (and
    # every odd-k) candidate.
    items = srt[:300]
    seen = {id(x) for x in items}
    items += [x for x in srt if x['nsq'] == 1 and id(x) not in seen][:200]
    best = {0: (F(0), [])}
    frontier = [(F(0), [])]
    for k in range(1, kmax + 1):
        nxt = {}
        for (tot, sel) in frontier:
            for it in items:
                if sum(c['nsq'] for c in sel) + it['nsq'] > k:
                    continue
                if any(c is it for c in sel):
                    continue
                if any(not regions_disjoint(it, c) or not can_coexist(it, c)
                       for c in sel):
                    continue
                key = tuple(sorted(id(c) for c in sel + [it]))
                if key not in nxt or nxt[key][0] < tot + it['v']:
                    nxt[key] = (tot + it['v'], sel + [it])
        cand = sorted(nxt.values(), key=lambda p: -float(p[0]))[:beam]
        if not cand:
            best[k] = best.get(k - 1, (F(0), []))
            continue
        frontier = cand + [f for f in frontier
                           if sum(c['nsq'] for c in f[1]) <= k][:beam]
        frontier = sorted(frontier, key=lambda p: -float(p[0]))[:beam]
        frontier.append((F(0), []))      # the empty seed must survive pruning,
        # otherwise an entry of size nsq=2 (a pair) can never start a new set
        best[k] = max([p for p in frontier
                       if sum(c['nsq'] for c in p[1]) <= k] or [(F(0), [])],
                      key=lambda p: float(p[0]))
    return best


def greedy_k(items, budget, kmax=12):
    """greedily pick region-disjoint, mutually placeable atlas entries of maximal
    value until the budget is exceeded.  Returns (k, total, chosen)."""
    items = sorted(items, key=lambda it: -float(it['v']))
    chosen, tot, nsq = [], F(0), 0
    for it in items:
        if nsq >= kmax:
            break
        if any(not regions_disjoint(it, c) or not can_coexist(it, c) for c in chosen):
            continue
        chosen.append(it)
        tot += it['v']
        nsq += it['nsq']
        if tot > budget:
            break
    return nsq, tot, chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--single', required=True)
    ap.add_argument('--pair', default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--plot', default=None)
    a = ap.parse_args()

    at = load(a.single)
    s = F(at['s'])
    budget = F(at['budget'])
    h = F(at['grid']['h'])
    dth = at['grid']['dtheta_deg']

    # ---------------- headline table: dead vs (tilt, min centre-wall distance)
    tab = {}
    for c in at['cells']:
        k = int(round(c['theta_deg'][0] / dth))
        d = min(F(c['cx'][0]), F(c['cy'][0]))
        db = round(float(d) / 0.15) * 0.15
        key = (k, round(db, 3))
        tab[key] = max(tab.get(key, 0.0), c['dead_lb_float'])
    ks = sorted({k for (k, _) in tab})
    ds = sorted({d for (_, d) in tab})
    lines = ['theta\\d  ' + ' '.join(f'{d:5.2f}' for d in ds)]
    for k in ks:
        lines.append(f'{k*dth:3.0f}-{(k+1)*dth:3.0f}  ' +
                     ' '.join(f'{tab.get((k,d),0.0):5.3f}' for d in ds))
    headline = '\n'.join(lines)
    print('== single-square atlas: max certified dead area')
    print('   rows = tilt bin (deg), cols = min(cx0,cy0) = closest the centre may')
    print('   come to a wall;  s =', float(s), ' budget s^2-11 =', float(budget))
    print(headline)

    # ---------------- coverage
    nmid = ntot = 0
    cov = {t: 0 for t in (0.1, 0.2, 0.3, 0.4, 0.5)}
    covmid = {t: 0 for t in cov}
    nmid_all = at['counts']['enumerated']
    for c in at['cells']:
        ntot += 1
        mid = c['theta_deg'][0] >= 15
        if mid:
            nmid += 1
        for t in cov:
            if c['dead_lb_float'] >= t:
                cov[t] += 1
                if mid:
                    covmid[t] += 1
    n_enum = at['counts']['enumerated']
    n_enum_mid = None

    # ---------------- min-k
    items, items_mid = [], []
    for c in at['cells']:
        if c['dead_lb_float'] > 0.02:
            im = orbit_images(c, s)
            items += im
            # "mid-tilt" is a property of the CANONICAL cell (tilt mod 90 folded
            # into [0,45]); the flipped images carry theta in [45,90] and are the
            # same physical square, so filter before taking the orbit.
            if c['theta_deg'][0] >= 15:
                items_mid += im
    if a.pair:
        pr = load(a.pair)
        for c in pr['cells']:
            if c['dead_lb_float'] > 0.02:
                im = pair_images(c, s)
                items += im
                if c['A']['theta'][0] >= 15 and c['B']['theta'][0] >= 15:
                    items_mid += im
    kbest, tot, chosen = greedy_k(items, budget)
    kmid, totmid, chosenmid = greedy_k(items_mid, budget)
    res_mid_chosen = chosenmid
    bk = best_for_k(items, 5)
    bkm = best_for_k(items_mid, 5)
    print()
    print("== best achievable sum of atlas values with exactly <= k squares")
    mink = minkm = None
    for k in sorted(bk):
        if k == 0:
            continue
        t1, t2 = bk[k][0], bkm.get(k, (F(0), []))[0]
        if mink is None and t1 > budget:
            mink = k
        if minkm is None and t2 > budget:
            minkm = k
        print(f"   k={k}: any tilt {float(t1):.4f}{' > budget' if t1>budget else ''}"
              f"   mid-tilt {float(t2):.4f}{' > budget' if t2>budget else ''}")
    print(f"   MINIMUM k that kills:  any tilt {mink}   mid-tilt {minkm}   "
          f"(budget {float(budget):.4f})")
    if minkm:
        print("   witness (mid-tilt):")
        for it in bkm[minkm][1]:
            print(f"     +{float(it['v']):.4f} {it['id']} nsq={it['nsq']} "
                  f"centre [{float(it['box'][0]):.2f},{float(it['box'][1]):.2f}]x"
                  f"[{float(it['box'][2]):.2f},{float(it['box'][3]):.2f}] "
                  f"th {it['theta'][0]:.0f}-{it['theta'][1]:.0f}"
                  + (f" + [{float(it['box2'][0]):.2f},{float(it['box2'][1]):.2f}]x"
                     f"[{float(it['box2'][2]):.2f},{float(it['box2'][3]):.2f}]"
                     if it.get('box2') else ''))
    # typical case: median positive value
    import statistics as st
    povs = sorted(c['dead_lb_float'] for c in at['cells'] if c['theta_deg'][0] >= 15)
    med = st.median(povs) if povs else 0
    ktyp = int(math.ceil(float(budget) / med)) if med > 0 else None
    print(f"   typical (median mid-tilt positive cell = {med:.4f}) -> "
          f"k ~ {ktyp} squares if the regions can be kept disjoint")
    print(f"\n== minimum k (greedy, region-disjoint, pairwise placeable)")
    print(f"   any tilt : k = {kbest} squares, sum dead = {float(tot):.4f} "
          f"vs budget {float(budget):.4f}  -> {'KILLS' if tot > budget else 'does NOT kill'}")
    print(f"   mid-tilt : k = {kmid} squares, sum dead = {float(totmid):.4f} "
          f"-> {'KILLS' if totmid > budget else 'does NOT kill'}")
    for it in chosen + ['--- mid-tilt ---'] + chosenmid:
        if isinstance(it, str):
            print('    ', it)
            continue
        print(f"     +{float(it['v']):.4f}  {it['id']}  centre "
              f"[{float(it['box'][0]):.2f},{float(it['box'][1]):.2f}]x"
              f"[{float(it['box'][2]):.2f},{float(it['box'][3]):.2f}] "
              f"theta {it['theta'][0]:.0f}-{it['theta'][1]:.0f}"
              + (f" + [{float(it['box2'][0]):.2f},{float(it['box2'][1]):.2f}]x"
                 f"[{float(it['box2'][2]):.2f},{float(it['box2'][3]):.2f}]"
                 if it.get('box2') else ''))

    res = dict(s=at['s'], budget=str(budget), headline_table=headline,
               coverage={str(t): dict(cells=cov[t], mid_tilt_cells=covmid[t])
                         for t in sorted(cov)},
               n_positive=ntot, n_positive_midtilt=nmid, n_enumerated=n_enum,
               max_single=at['cells'][0]['dead_lb_float'] if at['cells'] else 0,
               min_k=dict(any_tilt=mink, mid_tilt=minkm,
                          best_sum_by_k={str(k): [str(bk[k][0]),
                                                  str(bkm.get(k, (F(0), []))[0])]
                                         for k in sorted(bk) if k},
                          typical_median_midtilt=med, typical_k=ktyp,
                          greedy=dict(any_tilt=dict(k=kbest, total=str(tot)),
                                      mid_tilt=dict(k=kmid, total=str(totmid)))),
               chosen=[dict(id=it['id'], v=str(it['v']), nsq=it['nsq'],
                            box=[str(v) for v in it['box']],
                            theta=list(it['theta'])) for it in chosen])
    if a.pair:
        res['max_pair'] = pr['cells'][0]['dead_lb_float'] if pr['cells'] else 0
    with open(a.out, 'w') as f:
        json.dump(res, f, indent=1)
    print('\nwrote', a.out)

    if a.plot:
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
            M = np.zeros((len(ks), len(ds)))
            for (ii, k) in enumerate(ks):
                for (jj, d) in enumerate(ds):
                    M[ii, jj] = tab.get((k, d), 0.0)
            fig, ax = plt.subplots(figsize=(9, 5))
            im = ax.imshow(M, origin='lower', aspect='auto', cmap='viridis',
                           extent=[ds[0] - .075, ds[-1] + .075,
                                   ks[0] * dth, (ks[-1] + 1) * dth])
            ax.set_xlabel('min possible centre distance to a wall')
            ax.set_ylabel('tilt bin (deg)')
            ax.set_title(f'A25 certified dead area, one square in a '
                         f'{float(h):.2f} x {dth:.0f}deg box, s={float(s):.4f}')
            fig.colorbar(im, label='certified dead area (lower bound)')
            fig.tight_layout()
            fig.savefig(a.plot, dpi=110)
            print('wrote', a.plot)
        except Exception as e:
            print('plot skipped:', e)


if __name__ == '__main__':
    main()
