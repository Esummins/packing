"""A260 task 1, corpus tests [M] on A258's corpus (A253's 44 ring + poker rows + A255's 2 controls), exact region search
(room259.centre_set, 1-degree tilt grid).  Per row:
  lock      : the locked wall, the shift e = (W - T) along the wall, tilt difference            (norm258.normalise, kept)
  F_O       : contains_O margin of the poker F (> 0: O in int F)
  ringO     : pierce_O of the bare HYBRID ring of eight (< 0: every sampled-tilt free square contains O), components
  tenth     : the largest centre-set area of ring + F over the tilt grid (0: the poker is the ONLY free square that fits
              beside itself -- no tenth square)
  unlock    : after W -> T (F removed): least |q - q_F| over the centre set of F's own tilt (the LIFT of reading (U)),
              the lifted pose's exact free margin against ring', and whether the lifted Q contains O
Output results/corpus260.jsonl + a printed tally.  ~2 min."""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Point

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = H.Z


def main():
    rows, N = H.corpus()
    out = os.path.join(HERE, '..', 'results', 'corpus260.jsonl')
    tally = dict(n=0, locked=0, F_has_O=0, ring_all_O=0, no_tenth=0, lift_exists=0, lift_has_O=0)
    with open(out, 'w') as fh:
        for name, s, sq in rows:
            rec = dict(name=name, s=s)
            ring = [np.array(V, float) for V in sq[:8]]
            tally['n'] += 1
            wO, pose, nc = R.pierce_O(None, s, 1.0, ring)
            rec.update(ringO=wO, ring_ncomp=nc, ring_worst_pose=pose)
            tally['ring_all_O'] += wO < 0
            if len(sq) > 8:
                F = np.array(sq[8], float)
                pF = Z.pose_of(F)
                rec['F_pose'] = pF
                rec['F_O'] = float(R.contains_O(pF, s))
                tally['F_has_O'] += rec['F_O'] > 0
                area = 0.0
                for td in np.arange(0.0, 90.0, 1.0):
                    C = R.centre_set(ring + [F], s, td * Z.DEG)
                    area = max(area, sum(p.area for p in R.polys_of(C)))
                rec['tenth_area'] = area
                tally['no_tenth'] += area == 0.0
                cur, info = N.normalise(sq, s, True)
                lk = [i for i in info if i['status'].startswith('LOCKED')]
                rec['lock'] = [dict(wall=i['wall'], e=i['W_minus_T_along_wall'], dtilt_deg=i['dtilt_deg'],
                                    phi_deg=i['phi_deg'], a=i['a']) for i in lk]
                tally['locked'] += len(lk) > 0
                if lk:
                    i = lk[0]
                    w = i['wall']
                    T = ring[0] * 0
                    i1, iW = N.wall_pair(ring, s, w)
                    T = ring[i1] + (1.0 / math.cos(i['phi_deg'] * Z.DEG)) * np.array(N.EW[w], float)
                    ring2 = [V for j, V in enumerate(ring) if j != iW] + [T]
                    th = pF[2] % (math.pi / 2)
                    C = R.centre_set(ring2, s, th)
                    ps = R.polys_of(C)
                    if ps:
                        q0 = Point(pF[0], pF[1])
                        best = min(ps, key=lambda p: p.distance(q0))
                        d = best.distance(q0)
                        from shapely.ops import nearest_points
                        qn = nearest_points(best, q0)[0]
                        # step 1e-9 inside the centre set (towards its representative point) before the exact check
                        rp = best.representative_point()
                        q = (qn.x + 1e-7 * (rp.x - qn.x), qn.y + 1e-7 * (rp.y - qn.y), th)
                        rec['lift'] = dict(dist=d, pose=q, free_margin=R.free_margin(q, ring2, s),
                                           has_O=float(R.contains_O(q, s)), T_dip=float(H.Z.poly_gap(F, T)))
                        tally['lift_exists'] += rec['lift']['free_margin'] >= -1e-7
                        tally['lift_has_O'] += rec['lift']['has_O'] > 0
            fh.write(json.dumps(rec) + '\n')
            print(name, {k: (round(v, 5) if isinstance(v, float) else v) for k, v in rec.items()
                         if k in ('ringO', 'F_O', 'tenth_area')},
                  rec.get('lock'), {k: round(v, 5) for k, v in rec.get('lift', {}).items() if k != 'pose'}, flush=True)
    print(json.dumps(tally))


if __name__ == '__main__':
    main()
