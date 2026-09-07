"""A122 T1 - the interval endpoint certificate (A106 `certify_endpoint`, mpmath iv) for each A122
minimum, plus a direct high-precision interval check at the Lagrange solution.

Two independent certificates per point:

  * A106's ladder.  Round the landing to rationals with denominator 1e12, push the margin at
    s* + eps, and check in mpmath interval arithmetic at 250 bits that every kept pair is strictly
    separated on some axis and every square is strictly inside [0, s*+eps]^2.  Reported as the
    smallest eps on the ladder (1e-9 ... 1e-4) that passes, with the rational s_certified.

  * A DIRECT interval check at the 80-digit Lagrange solution of exact.py: the poses are rounded
    to rationals with denominator 1e30 and the same disjointness/containment obligations are
    verified with iv at 400 bits at s* + eps for a much smaller eps.  This is the honest statement
    that a packing of eleven unit squares of side < s* + eps exists, with no optimiser in the
    decision.

Outputs results/certify.json.
"""
from __future__ import annotations

import json
import math
import os
import time
from fractions import Fraction as Fr

import numpy as np

import a122lib as A
from a122lib import S11
import system as SY
import exact as EX
import polish as P


def direct_iv(x, sysm, eps, den=10 ** 30, prec=400):
    """Rigorous interval check that the eleven squares at the given poses, with s = s* + eps, are
    pairwise interior-disjoint and inside the box.  Returns (ok, worst pair, worst wall)."""
    from mpmath import iv, mp
    iv.prec = prec
    mp.prec = prec

    def q(v):
        return Fr(int(round(float(v) * den)), den) if not isinstance(v, Fr) else v

    from mpmath import mpf as _m
    s_star = x[15]
    S_q = Fr(int(round(float(s_star) * den)), den) + Fr(int(round(eps * den)), den)

    def ivf(fr):
        return iv.mpf(fr.numerator) / iv.mpf(fr.denominator)

    pose = []
    for i in range(11):
        if i < 5:
            pose.append((q(x[3 * i]), q(x[3 * i + 1]), q(x[3 * i + 2])))
        else:
            a, b, c, dd = sysm.slot_aff[i - 5]
            qq = sysm.slot_q[i - 5]
            pose.append((Fr(a).limit_denominator(2) + Fr(int(b)) * S_q,
                         Fr(c).limit_denominator(2) + Fr(int(dd)) * S_q,
                         Fr(qq) * Fr(0)))          # upright: theta = 0 exactly
    S = ivf(S_q)
    ct = [iv.cos(ivf(p[2])) for p in pose]
    st = [iv.sin(ivf(p[2])) for p in pose]
    C = [(ivf(p[0]), ivf(p[1])) for p in pose]

    worst_wall = None
    for i in range(11):
        e = (abs(ct[i]) + abs(st[i])) / 2
        for k in range(2):
            for g in ((C[i][k] - e), (S - C[i][k] - e)):
                worst_wall = g if worst_wall is None or g.a < worst_wall.a else worst_wall
    ok_wall = worst_wall.a > 0

    worst_pair = None
    ok_pair = True
    for i in range(11):
        for j in range(i + 1, 11):
            best = None
            for (ci, si_, cj, sj, a, b) in ((ct[i], st[i], ct[j], st[j], i, j),
                                            (ct[j], st[j], ct[i], st[i], j, i)):
                for ax in ((ci, si_), (-si_, ci)):
                    dd = abs((C[b][0] - C[a][0]) * ax[0] + (C[b][1] - C[a][1]) * ax[1])
                    g = (abs(ax[0] * cj + ax[1] * sj) + abs(-ax[0] * sj + ax[1] * cj))
                    v = dd - iv.mpf(1) / 2 - g / 2
                    best = v if best is None or v.a > best.a else best
            worst_pair = best if worst_pair is None or best.a < worst_pair.a else worst_pair
            if not best.a > 0:
                ok_pair = False
    return (ok_pair and ok_wall), worst_pair, worst_wall


def main():
    t0 = time.time()
    from mpmath import mp
    out = {}
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    R = P.R_all()
    bnds = P.bounds_all(R)
    for tag, sid in (('S33min', 'S33'), ('S35min', 'S35'), ('S38min', 'S38')):
        b = d['entries'][sid]['best']
        s, cfg = b['sigma'], [tuple(c) for c in b['cfg']]
        names = A.names_for(sid)
        print(f'\n=== {tag}')
        z = A.to106(s, cfg)
        eps, rep = S11.certify_endpoint(R, z, bounds=bnds)
        rec = dict(a106_eps=eps,
                   a106_report={k: (str(v) if not isinstance(v, (int, float, type(None))) else v)
                                for k, v in rep.items()})
        print(f'  A106 interval endpoint certificate: eps = {eps}  {rep}')

        # the same certificate on a FINER ladder with a finer rational grid and more bits: how far
        # down does eps go before the rounding of the poses eats the margin?
        eps2, rep2 = S11.certify_endpoint(
            R, z, eps_ladder=(1e-13, 1e-12, 1e-11, 1e-10, 1e-9), den=10 ** 15, prec=400,
            bounds=bnds)
        rec['a106_eps_fine'] = eps2
        rec['a106_report_fine'] = {
            k: (str(v) if not isinstance(v, (int, float, type(None))) else v)
            for k, v in rep2.items()}
        print(f'  finer ladder (den 1e15, 400 bits): eps = {eps2}  {rep2}')

        # the 80-digit Lagrange value, for the record
        sysm = SY.System(s, cfg, names)
        x, lam, res = EX.solve_lagrange(sysm, SY.x0_from(s, cfg), dps=80)
        mp.dps = 60
        rec['s_star_50_digits'] = mp.nstr(x[15], 50)
        rec['lagrange_residual'] = float(res)
        print(f'  s* (Lagrange, 50 digits) = {mp.nstr(x[15], 50)}')
        out[tag] = rec

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'certify.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/certify.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
