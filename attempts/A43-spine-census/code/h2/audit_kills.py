#!/usr/bin/env python3
"""A43-H2 INDEPENDENT KILL AUDIT.

For every type the census KILLED, search for a witness with a second, simpler
implementation: a direct grid over the tilt of every class (step DPHI degrees,
default 0.05) and over every discrete branch label, with the continuous slide
parameters (t in [-1,1] for FL, u in [-1/2,1/2] for CE) handled exactly (dx is
affine in them, so the reachable dx is the closed interval between the endpoint
values).  Plain float arithmetic, no bins, no cells, no outward rounding.

If this finds a chain of centres reaching x_k = s - h(phi_k) from x_1 = h(phi_1)
inside the container for a KILLED type, the census kill is UNSOUND.  Finding
nothing is not a proof, but it is an independent stress test of the binning
(3 deg) and of the cell relaxation.
"""
from __future__ import annotations

import json
import math
import os
import sys

import spine as S

S0 = 969271 / 250000.0
R2H = math.sqrt(0.5)


def h(p):
    return 0.5 * (math.cos(math.radians(p)) + math.sin(math.radians(p)))


def dx_branches_exact(link, pa, pb):
    """[(lo, hi)] reachable dx = x_{i+1} - x_i at exact tilts pa, pb."""
    out = []
    if link == S.FL:
        if abs(pa - pb) > 1e-12:
            return []
        for m in range(4):
            psi = math.radians(pa + 90 * m)
            c, s = math.cos(psi), math.sin(psi)
            out.append((c - abs(s), c + abs(s)))
        return out
    if link == S.CC:
        for ja in range(4):
            ta = math.radians(pa + 45 + 90 * ja)
            for jb in range(4):
                tb = math.radians(pb + 45 + 90 * jb)
                if math.cos(ta - tb) > 1e-12:
                    continue
                v = R2H * (math.cos(tb) - math.cos(ta))
                out.append((v, v))
        return out
    # CE
    if link == S.CEAB:
        A, B, sign = pa, pb, -1.0          # dx_link = -(c_a - c_b)_x
    else:
        A, B, sign = pb, pa, +1.0
    if abs(A - B) < 1e-12:
        return []
    n = 3 if A > B else 0
    for m in range(4):
        j = (m + n) % 4
        psi = math.radians(B + 90 * m)
        thd = math.radians(A + 45 + 90 * j)
        d = (math.degrees(thd - psi) + 180.0) % 360.0 - 180.0
        if abs(d) >= 45.0:
            continue
        c, s = math.cos(psi), math.sin(psi)
        base = 0.5 * c + R2H * math.cos(thd)
        lo, hi = base - 0.5 * abs(s), base + 0.5 * abs(s)
        out.append((sign * lo, sign * hi) if sign > 0 else (-hi, -lo))
    return out


def witness(s, eL, eR, links, dphi=0.05):
    """Search for a realization; returns the tilt assignment if found."""
    k = len(links) + 1
    run, nrun = __import__('census').runs_of(links)
    grid = [x * dphi for x in range(int(90.0 / dphi))]
    zr = set()
    if eL == S.END_F:
        zr.add(run[0])
    if eR == S.END_F:
        zr.add(run[-1])
    if (eL == S.END_C and run[0] in zr) or (eR == S.END_C and run[-1] in zr):
        return None
    choices = []
    for r in range(nrun):
        choices.append([0.0] if r in zr else grid)

    def rec(r, assign):
        if r == nrun:
            return check(s, eL, eR, links, run, assign)
        for v in choices[r]:
            a = assign + [v]
            if not prefix_ok(s, eL, links, run, a):
                continue
            w = rec(r + 1, a)
            if w:
                return w
        return None

    return rec(0, [])


def prefix_ok(s, eL, links, run, assign):
    """Forward interval propagation over the squares whose class is assigned."""
    nass = len(assign)
    phi = []
    for i in range(len(run)):
        if run[i] < nass:
            phi.append(assign[run[i]])
        else:
            break
    if not phi:
        return True
    # CE strict-inequality consistency inside the assigned prefix
    for i in range(len(phi) - 1):
        if links[i] in (S.CEAB, S.CEBA) and abs(phi[i] - phi[i + 1]) < 1e-12:
            return False
    lo = hi = h(phi[0])
    for i in range(len(phi) - 1):
        br = dx_branches_exact(links[i], phi[i], phi[i + 1])
        if not br:
            return False
        lo2 = lo + min(a for a, b in br)
        hi2 = hi + max(b for a, b in br)
        lo = max(lo2, h(phi[i + 1]))
        hi = min(hi2, s - h(phi[i + 1]))
        if lo > hi:
            return False
    return True


def check(s, eL, eR, links, run, assign):
    phi = [assign[run[i]] for i in range(len(run))]
    for i in range(len(phi) - 1):
        if links[i] in (S.CEAB, S.CEBA) and abs(phi[i] - phi[i + 1]) < 1e-12:
            return None
    lo = hi = h(phi[0])
    for i in range(len(phi) - 1):
        br = dx_branches_exact(links[i], phi[i], phi[i + 1])
        if not br:
            return None
        lo = max(lo + min(a for a, b in br), h(phi[i + 1]))
        hi = min(hi + max(b for a, b in br), s - h(phi[i + 1]))
        if lo > hi:
            return None
    tgt = s - h(phi[-1])
    return phi if lo - 1e-12 <= tgt <= hi + 1e-12 else None


def main():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', '..', 'results', 'h2')
    ks = [int(a) for a in sys.argv[1:]] or [3, 4, 5, 6, 7]
    DPHI = {3: 0.5, 4: 0.5, 5: 1.0, 6: 1.5, 7: 2.0}
    out = []
    dphis = {}
    for k in ks:
        dphi = DPHI.get(k, 2.0)
        dphis[k] = dphi
        f = os.path.join(base, 'checkpoints', 'census_k%d.json' % k)
        if not os.path.exists(f):
            continue
        killed = json.load(open(f))['killed']
        bad = []
        for r in killed:
            a, mid, b = r['type'].split('-')
            eL = S.END_NAME.index(a)
            eR = S.END_NAME.index(b)
            links = tuple(S.LINK_NAME.index(x) for x in mid.split('.'))
            w = witness(S0, eL, eR, links, dphi)
            if w:
                bad.append(dict(type=r['type'], stage=r['stage'],
                                witness_phi=[round(v, 4) for v in w]))
        out.append(dict(k=k, dphi_deg=dphi, n_killed=len(killed),
                        n_witness_found=len(bad), witnesses=bad))
        print('k=%d killed=%d  independent witnesses found=%d'
              % (k, len(killed), len(bad)), flush=True)
    json.dump(dict(dphi_deg=dphis, note='independent float re-search over the '
                   'killed types; a witness would mean the census kill is '
                   'UNSOUND', rows=out),
              open(os.path.join(base, 'kill_audit.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
