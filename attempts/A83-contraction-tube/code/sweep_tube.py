#!/usr/bin/env python3
"""sweep_tube.py -- the (T, r) trade-off curve of the contraction tube (A83 T1).

For each direction mode (slot = trump5 pins on their slot lines; scale = pure
scaling ray) and each radius profile, bisect the largest T the exact checker
certifies (T_max(r)); for each T bisect the largest isotropic r (r_max(T)).
Every evaluation is the exact checker (certs/verify_tube.py via emit_tube.run_one);
the binding check at the wall is recorded.  Output: results/curve.json +
results/sweep.jsonl (every evaluation).
"""
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emit_tube as ET                     # noqa: E402

RES = os.path.join(HERE, '..', 'results')
os.makedirs(RES, exist_ok=True)
LOG = open(os.path.join(RES, 'sweep.jsonl'), 'a')
K = json.load(open(ET.A22))
K['_sha256'] = ET.hashlib.sha256(open(ET.A22, 'rb').read()).hexdigest()
OM = json.load(open(ET.A36U))
PINS = ET.TRUMP5_PINS


def ev(T, rc, rt, mode, rs=Fraction(0)):
    t0 = time.time()
    tag = ('%s_T%s_rc%s_rt%s' % (mode, T, rc, rt)).replace('/', 'o')
    row = ET.run_one(T, rc, rt, rs, mode, PINS, tag, K, OM, False, quiet=True)
    row['wall'] = round(time.time() - t0, 1)
    LOG.write(json.dumps(row) + '\n')
    LOG.flush()
    print('  %-8s T=%-9.5f rc=%-9.5f rt=%-9.5f %s beta=%.4f psi/X=%.4f x*=%.2e tan=%.5f(%s) %s'
          % (mode, float(T), float(rc), float(rt), 'PASS' if row['PASS'] else 'FAIL',
             row['beta'], row['psi_over_Xmax'], row['x_star'], row['min_tangential'],
             row['min_tangential_row'], [f.split('] ')[-1][:40] for f in row['fails'][:2]]))
    return row


def bisect(f, lo, hi, rel=Fraction(1, 200), maxit=14):
    """largest x in [lo, hi] with f(x) PASS; lo must PASS, hi must FAIL."""
    rlo = f(lo)
    if not rlo['PASS']:
        return None, None, rlo          # nothing passes down to lo
    rhi = f(hi)
    if rhi['PASS']:
        return hi, rhi, None
    for _ in range(maxit):
        if (hi - lo) <= rel * hi:
            break
        mid = (lo + hi) / 2
        mid = Fraction(round(mid * 10 ** 7), 10 ** 7)
        r = f(mid)
        if r['PASS']:
            lo, rlo = mid, r
        else:
            hi, rhi = mid, r
    return lo, rlo, rhi


def main():
    F = Fraction
    part = sys.argv[1] if len(sys.argv) > 1 else 'all'
    profiles = [('landing', F(16, 10000), F(21, 10000)),
                ('landing_theta_eq_c', F(16, 10000), F(16, 10000)),
                ('half', F(8, 10000), F(105, 100000)),
                ('tiny', F(2, 10000), F(2, 10000)),
                ('wide', F(25, 10000), F(30, 10000))]
    if part in ('all', 'Tmax'):
        # ---- 1. T_max at the A60 landing profile and a few others (slot and scale)
        for mode in ('slot', 'scale'):
            for lab, rc, rt in profiles:
                print('== T_max, mode %s, profile %s rc=%s rt=%s' % (mode, lab, rc, rt))
                bisect(lambda T: ev(T, rc, rt, mode), F(0), F(2, 10))
    if part in ('all', 'rmax', 'rmax_scale'):
        # ---- 2. r_max (isotropic r_c = r_theta, r_s = 0) at fixed T
        for mode in (('scale',) if part == 'rmax_scale' else ('slot', 'scale')):
            for T in (F(0), F(1, 1000), F(1, 100), F(2, 100), F(3, 100), F(5708, 100000)):
                print('== r_max, mode %s, T=%s' % (mode, T))
                bisect(lambda r: ev(T, r, r, mode), F(1, 10000), F(8, 1000))
    if part in ('all', 'aniso'):
        # ---- 3. r_theta_max at fixed (T, r_c) -- the anisotropic frontier at T = 1e-2, 2e-2
        for T in (F(1, 100), F(2, 100)):
            for rc in (F(8, 10000), F(16, 10000), F(25, 10000)):
                print('== r_theta_max, slot, T=%s rc=%s' % (T, rc))
                bisect(lambda rt: ev(T, rc, rt, 'slot'), F(1, 10000), F(8, 1000))
    print('done; build results/curve.json with curve_from_sweep.py')


if __name__ == '__main__':
    main()
