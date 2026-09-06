"""A108 T1 - polish S07 to a genuine local minimum of the side with ALL ELEVEN squares free, then
certify the endpoint in interval arithmetic.

The A107 gallery entry holds the six slot squares on their slot lines c(s) = alpha + beta*s, so its
s* = 3.8856180554 is the minimum of a RESTRICTED problem (16 variables).  Here nothing is held: the
variables are (cx, cy, theta) for all eleven squares plus s, 34 of them, and the only question asked
of the configuration is whether it is a packing.  A106's engine `shadow11.Reduction` does exactly
this at k = 0 pins (its 34 x 34 reduction map is then the identity on (x, y, theta) x 11 + s).

Outputs results/polish.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

import a108lib as A
from a108lib import S11, MZ, L


def R_all():
    """shadow11 reduction with zero pins: all eleven squares free, 34 variables."""
    return S11.Reduction([], pin_hw=0.0)


def bounds_all(R):
    b = list(R.base_bounds)
    b[R.nz - 1] = (3.4, 4.6)
    return b


def run106(z0_106, R=None, penalty=True):
    """A106 pipeline: penalty continuation (optional) then frozen-axis SLSQP polish."""
    R = R or R_all()
    bnds = bounds_all(R)
    z = z0_106.copy()
    if penalty:
        z = S11.penalty_solve(R, z, bounds=bnds)
    z = S11.polish(R, z, rounds=10, maxiter=800, bounds=bnds)
    ov, cv = S11.feasibility(R, z)
    return z, float(z[-1]), float(ov), float(cv)


def run107(s, cfg):
    """A107 pipeline on the same problem: slots = (), nfree = 11, plain SLSQP on the SAT gaps."""
    cons = MZ.make_cons((), 11)
    z0 = A.to107(s, cfg)
    z, sv, feas = MZ.solve(cons, z0, 11)
    return z, float(sv), float(feas)


def main():
    t0 = time.time()
    out = {}
    s07_s, s07_cfg = A.load_s07()
    out['a107_landing'] = dict(s=s07_s, cfg=[list(c) for c in s07_cfg],
                               worst_pair_gap=A.worst_gaps(s07_s, s07_cfg)[0],
                               worst_wall_gap=A.worst_gaps(s07_s, s07_cfg)[1],
                               sigma=A.sigma(*A.normalise(s07_s, s07_cfg)))

    R = R_all()
    print('nz =', R.nz, 'pairs kept', int(R.pair_keep.sum()), 'containment kept', int(R.cont_keep.sum()))

    # ---- 1. polish only (no penalty): does the A107 landing survive releasing the six uprights?
    z0 = A.to106(s07_s, s07_cfg)
    zp, sp, ovp, cvp = run106(z0, R, penalty=False)
    sP, cfgP = A.from106(zp)
    out['polish_only'] = dict(s=sp, ov=ovp, cv=cvp, cfg=[list(c) for c in cfgP],
                              sigma=A.sigma(*A.normalise(sP, cfgP)))
    print(f'polish-only   s* = {sp:.10f}  ov {ovp:+.2e} cv {cvp:+.2e}  sigma {out["polish_only"]["sigma"]:.10f}')

    # ---- 2. full A106 pipeline (penalty continuation then polish) from the same seed
    zf, sf, ovf, cvf = run106(z0, R, penalty=True)
    sF, cfgF = A.from106(zf)
    out['penalty_polish'] = dict(s=sf, ov=ovf, cv=cvf, cfg=[list(c) for c in cfgF],
                                 sigma=A.sigma(*A.normalise(sF, cfgF)))
    print(f'penalty+polish s* = {sf:.10f}  ov {ovf:+.2e} cv {cvf:+.2e}  sigma {out["penalty_polish"]["sigma"]:.10f}')

    # ---- 3. independent engine: A107's plain SLSQP with all 11 free
    z7, s7, feas7 = run107(s07_s, s07_cfg)
    s7s, cfg7 = A.from107(z7)
    out['a107_engine_allfree'] = dict(s=s7, feas=feas7, cfg=[list(c) for c in cfg7],
                                      sigma=A.sigma(*A.normalise(s7s, cfg7)))
    print(f'A107 SLSQP     s* = {s7:.10f}  worst constraint {feas7:+.2e}  '
          f'sigma {out["a107_engine_allfree"]["sigma"]:.10f}')

    # ---- 4. basin probe: perturb and re-minimise, all eleven free.  Where does it land?
    rng = np.random.RandomState(20260906)
    land = []
    best = min((out['polish_only']['sigma'], zp.tolist()),
               (out['penalty_polish']['sigma'], zf.tolist()))
    for k in range(40):
        amp = [0.002, 0.01, 0.03, 0.08][k % 4]
        z = A.to106(s07_s, s07_cfg)
        z[:33] += rng.uniform(-amp, amp, 33) * np.tile([1.0, 1.0, 0.6], 11)
        z[-1] = s07_s + 0.02
        try:
            zz, sv, ov, cv = run106(z, R, penalty=True)
        except Exception as e:                                   # pragma: no cover
            land.append(dict(amp=amp, error=str(e)))
            continue
        ss, cc = A.from106(zz)
        sg = A.sigma(*A.normalise(ss, cc)) if max(ov, cv) < 1e-6 else None
        land.append(dict(amp=amp, s=sv, ov=ov, cv=cv, sigma=sg))
        if sg is not None and sg < best[0] - 1e-9:
            best = (sg, zz.tolist())
    out['basin_probe'] = land
    vals = sorted(round(d['sigma'], 7) for d in land if d.get('sigma') is not None)
    out['basin_probe_spectrum'] = sorted(set(vals))
    print('basin probe landings (sigma, rounded 1e-7):', out['basin_probe_spectrum'])
    print('reached s-hat?', any(abs(v - A.SHAT) < 1e-5 for v in vals))

    out['best'] = dict(sigma=best[0], z106=best[1])
    out['seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(A.RES, 'polish.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print('wrote results/polish.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
