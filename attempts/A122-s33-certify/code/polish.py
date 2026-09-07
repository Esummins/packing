"""A122 T1 - polish S33 / S34 / S35 / K19 / S38 to genuine local minima of the side with ALL
ELEVEN squares free, and decide whether they are ONE minimum or several distinct points.

The gallery entries hold the six slot squares on their slot lines c(s) = alpha + beta*s, so their
s* are minima of a RESTRICTED 16-variable problem.  Here nothing is held: 34 variables, and the
only question asked of a configuration is whether it is a packing.  A106's `shadow11.Reduction`
at k = 0 pins does exactly this (its 34x34 reduction map is the identity).

Outputs results/polish.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

import a122lib as A
from a122lib import S11, MZ, L

IDS = ('S33', 'S34', 'S35', 'K19', 'S38')


def R_all():
    return S11.Reduction([], pin_hw=0.0)


def bounds_all(R):
    b = list(R.base_bounds)
    b[R.nz - 1] = (3.4, 4.6)
    return b


def run106(z0_106, R=None, penalty=True):
    R = R or R_all()
    bnds = bounds_all(R)
    z = z0_106.copy()
    if penalty:
        z = S11.penalty_solve(R, z, bounds=bnds)
    z = S11.polish(R, z, rounds=10, maxiter=800, bounds=bnds)
    ov, cv = S11.feasibility(R, z)
    return z, float(z[-1]), float(ov), float(cv)


def run107(s, cfg):
    cons = MZ.make_cons((), 11)
    z0 = A.to107(s, cfg)
    z, sv, feas = MZ.solve(cons, z0, 11)
    return z, float(sv), float(feas)


def canon(s, cfg):
    """A label-free fingerprint: the eleven (cx, cy, tilt mod 90) rows sorted lexicographically."""
    rows = sorted((round(c[0], 7), round(c[1], 7), round(A.tmod(c[2]), 5)) for c in cfg)
    return rows


def main():
    t0 = time.time()
    out = {'ids': list(IDS), 'entries': {}}
    R = R_all()
    print('nz =', R.nz, 'pairs kept', int(R.pair_keep.sum()),
          'containment kept', int(R.cont_keep.sum()))

    best_overall = None
    for sid in IDS:
        s, cfg, rec = A.load_shadow(sid)
        e = {'gallery': dict(s=s, sigma=A.sigma(*A.normalise(s, cfg)),
                             cfg=[list(c) for c in cfg],
                             worst_pair_gap=A.worst_gaps(s, cfg)[0],
                             worst_wall_gap=A.worst_gaps(s, cfg)[1])}
        z0 = A.to106(s, cfg)

        zp, sp, ovp, cvp = run106(z0, R, penalty=False)
        sP, cfgP = A.from106(zp)
        e['polish_only'] = dict(s=sp, ov=ovp, cv=cvp, cfg=[list(c) for c in cfgP],
                                sigma=A.sigma(*A.normalise(sP, cfgP)))

        zf, sf, ovf, cvf = run106(z0, R, penalty=True)
        sF, cfgF = A.from106(zf)
        e['penalty_polish'] = dict(s=sf, ov=ovf, cv=cvf, cfg=[list(c) for c in cfgF],
                                   sigma=A.sigma(*A.normalise(sF, cfgF)))

        z7, s7, feas7 = run107(s, cfg)
        s7s, cfg7 = A.from107(z7)
        e['a107_engine_allfree'] = dict(s=s7, feas=feas7, cfg=[list(c) for c in cfg7],
                                        sigma=A.sigma(*A.normalise(s7s, cfg7)))

        cands = [(e['polish_only']['sigma'], sP, cfgP, 'polish_only'),
                 (e['penalty_polish']['sigma'], sF, cfgF, 'penalty_polish'),
                 (e['a107_engine_allfree']['sigma'], s7s, cfg7, 'a107_engine')]
        cands = [c for c in cands if math.isfinite(c[0])]
        cands.sort()
        e['best'] = dict(sigma=cands[0][0], via=cands[0][3],
                         cfg=[list(c) for c in cands[0][2]], s_raw=cands[0][1])
        out['entries'][sid] = e
        print(f'{sid}: gallery {e["gallery"]["sigma"]:.10f}  polish-only {e["polish_only"]["sigma"]:.10f}  '
              f'penalty+polish {e["penalty_polish"]["sigma"]:.10f}  A107 {e["a107_engine_allfree"]["sigma"]:.10f}'
              f'  -> best {cands[0][0]:.10f} ({cands[0][3]})')
        if best_overall is None or cands[0][0] < best_overall[0]:
            best_overall = (cands[0][0], cands[0][1], [list(c) for c in cands[0][2]], sid)

    # --------------------------------------------------------- are they the same point?
    print('\n=== pairwise comparison of the polished landings (label-free)')
    cmp = {}
    for i, a in enumerate(IDS):
        for b in IDS[i + 1:]:
            sa = out['entries'][a]['best']['sigma']
            sb = out['entries'][b]['best']['sigma']
            ca = [tuple(c) for c in out['entries'][a]['best']['cfg']]
            cb = [tuple(c) for c in out['entries'][b]['best']['cfg']]
            perm, tot, dt = A.match_configs(ca, cb)
            cmp[f'{a}|{b}'] = dict(ds=sb - sa, centre_distance=tot,
                                   max_centre_gap=max(math.hypot(ca[k][0] - cb[perm[k]][0],
                                                                 ca[k][1] - cb[perm[k]][1])
                                                      for k in range(11)),
                                   max_tilt_deg=max(dt), perm=perm)
            print(f'  {a} vs {b}: ds {sb-sa:+.3e}  total centre distance {tot:.3e}  '
                  f'max centre gap {cmp[f"{a}|{b}"]["max_centre_gap"]:.3e}  max tilt {max(dt):.4f} deg')

    out['pairwise'] = cmp
    out['best_overall'] = dict(sigma=best_overall[0], s_raw=best_overall[1],
                               cfg=best_overall[2], from_id=best_overall[3])
    print(f'\nbest overall sigma = {best_overall[0]:.12f} (from {best_overall[3]})')

    out['seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(A.RES, 'polish.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print('wrote results/polish.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
