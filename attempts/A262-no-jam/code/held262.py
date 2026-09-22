"""A262 task 2 [M]: HELD-JAM -- P4 (RETREAT) on the floater of a JAM ring.

For every JAM ring of results/ring262.jsonl (+ search262 / adv262 single-JAM rows when present):
  * RETREAT directions psi (1-degree grid in (0, 90)): C' = C + mu1 (cos psi, sin psi), mu1 = (1 - ymin(C))/sin psi + 1e-6,
    is a retreat iff the sweep hull(C, C') is interior-disjoint from the other 7 ring squares, inside the container,
    C' meets NO floor-band cell it... exactly: the set of border cells met by C' is a PROPER subset of C's (fam262 cells).
  * HOLDER test per retreat direction: is there a unit square G, free of all 8 ring squares, whose interior meets the
    sweep?  exact per tilt: area( centre_set(ring) minus centre_set(ring + sweep hull) ) > 0 on a 3-degree tilt grid.
  * ONE-HOLDER test: a single G that blocks EVERY retreat direction: the intersection over psi of the blocking centre
    sets, per tilt.
Verdicts per ring: 'bare ring retreats' (n_retreat > 0), 'holdable' (every retreat direction has a holder),
'one_holder' (some single free square blocks them all -- necessary for a 9-square JAM packing in normal form, since
the room is <= 1).     python held262.py   -> results/held262.json
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import MultiPoint

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
import fam262 as F                                                    # noqa: E402
import room259 as R                                                   # noqa: E402
Z = G.Z


def cells_met(V, s):
    return {c for c in F.FM.CELLS if -Z.poly_gap(V, F.cell_poly(c, s)) > 1e-9}


def analyse(p, s, tilt_step=3.0):
    Vs = G.verts(p, s)
    C, others = Vs[7], Vs[:7]
    met = cells_met(C, s)
    ymin = float(C[:, 1].min())
    retreats = []
    for pd in range(1, 90):
        psi = math.radians(pd)
        mu = (1.0 - ymin) / math.sin(psi) + 1e-6
        C2 = C + mu * np.array([math.cos(psi), math.sin(psi)])
        H = np.array(MultiPoint([tuple(v) for v in np.vstack([C, C2])]).convex_hull.exterior.coords)[:-1]
        if Z.contain_margin(C2, s) < 0 or min(Z.poly_gap(H, W) for W in others) < -1e-12:
            continue
        m2 = cells_met(C2, s)
        if m2 < met:
            retreats.append((pd, H))
    out = dict(n_retreat=len(retreats), retreat_deg=[r[0] for r in retreats][:1] + [r[0] for r in retreats][-1:],
               cells_C=sorted(met))
    if not retreats:
        return out
    holdable, one = True, 0.0
    sub = retreats[:: max(1, len(retreats) // 6)]
    for td in np.arange(0.0, 90.0, tilt_step):
        th = td * Z.DEG
        base = R.centre_set(Vs, s, th)
        if base.is_empty:
            continue
        inter = None
        for pd, H in sub:
            blk = base.difference(R.centre_set(Vs + [H], s, th))
            inter = blk if inter is None else inter.intersection(blk)
        one = max(one, 0.0 if inter is None else inter.area)
    for pd, H in sub:
        a = 0.0
        for td in np.arange(0.0, 90.0, tilt_step):
            th = td * Z.DEG
            base = R.centre_set(Vs, s, th)
            if not base.is_empty:
                a = max(a, base.area - R.centre_set(Vs + [H], s, th).area)
        holdable = holdable and a > 1e-12
    out.update(holdable=bool(holdable), one_holder_area=float(one), one_holder=bool(one > 1e-12))
    return out


def main():
    rows = []
    for f in ('ring262.jsonl', 'search262.jsonl'):
        path = os.path.join(ATT, 'results', f)
        if os.path.exists(path):
            rows += [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r['t'] > 1e-6]
    out = []
    for r in rows:
        a = analyse(np.array(r['p']), r['s'])
        a.update(id=r['id'], s=r['s'], t=r['t'], pierce=r.get('pierce'))
        out.append(a)
        print(r['id'], a['n_retreat'], a.get('holdable'), a.get('one_holder'), a.get('one_holder_area'), flush=True)
    summ = dict(rings=len(out), bare_ring_retreats=sum(o['n_retreat'] > 0 for o in out),
                holdable=sum(bool(o.get('holdable')) for o in out), one_holder=sum(bool(o.get('one_holder')) for o in out))
    json.dump(dict(summary=summ, rows=out), open(os.path.join(ATT, 'results', 'held262.json'), 'w'), indent=1)
    print(summ)


if __name__ == '__main__':
    main()
