#!/usr/bin/env python3
"""A45 agent A -- TRUMP CANARY (spec sect.5 item 5, notes sect.7 canary 1).

Extract EVERY square-square and square-wall contact of certs/trump11_certificate.json,
classify it (WF / WC / FL / CE / CC), look up its charge in results/charge_table.json
(min over the table bins containing the realised parameters; uncovered => 0), and
report the sum.  Theorem A45.1 forces  sum <= B0 = s0^2 - 11 = 4.031780343056,
since Trump's packing EXISTS.  An excess is a soundness bug -> STOP.

TOLERANCE CONVENTION.  Trump's certificate stores centres/tilts rounded to ~1e-11,
so exact SAT gaps at his contacts are tiny but NOT 0.  Following A43
(check_trump_h1.py, TOL = 1e-6) a pair counts as a contact iff its EXACT rational
SAT gap is < 1e-6; the same tolerance is used for vertex/edge incidence.  Every
arithmetic step is exact Fractions (the square normals (c,s), (-s,c) are exact
rational unit vectors because c,s come from t = tan(theta/2)).
"""
import json
import math
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RES = os.path.join(HERE, '..', 'results')
CERT = os.path.join(REPO, 'certs', 'trump11_certificate.json')

TOL = F(1, 10 ** 6)                 # A43 contact tolerance
HALF = F(1, 2)


def cos_sin(t):
    tt = t * t
    return (1 - tt) / (1 + tt), 2 * t / (1 + tt)


class Sq:
    def __init__(self, cx, cy, t, idx):
        self.i = idx
        self.cx, self.cy, self.t = F(cx), F(cy), F(t)
        self.c, self.s = cos_sin(self.t)
        c, s = self.c, self.s
        self.e1 = (c, s)                     # unit, exact rational
        self.e2 = (-s, c)
        self.V = [(self.cx + c * u - s * v, self.cy + s * u + c * v)
                  for (u, v) in ((-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF))]
        self.theta = math.degrees(2 * math.atan(float(self.t)))


def proj(V, n):
    return [n[0] * x + n[1] * y for (x, y) in V]


def sat(A, B):
    """(max gap, axis n oriented so that A is on the n-negative side of B)."""
    best = None
    for n in (A.e1, A.e2, B.e1, B.e2):
        pa, pb = proj(A.V, n), proj(B.V, n)
        g1 = min(pb) - max(pa)                     # A below B along n
        g2 = min(pa) - max(pb)                     # A above B along n
        for (g, nn) in ((g1, n), (g2, (-n[0], -n[1]))):
            if best is None or g > best[0]:
                best = (g, nn)
    return best


def classify_pair(A, B):
    """Returns dict(type, ...) for a touching pair, or None."""
    gap, n = sat(A, B)
    if gap >= TOL:
        return None
    t = (n[1], -n[0])                              # right-handed with n
    pa, pb = proj(A.V, n), proj(B.V, n)
    mA = max(pa)
    mB = min(pb)
    VA = [A.V[k] for k in range(4) if mA - pa[k] < TOL]
    VB = [B.V[k] for k in range(4) if pb[k] - mB < TOL]
    ta = sorted(proj(VA, t))
    tb = sorted(proj(VB, t))
    lo, hi = max(ta[0], tb[0]), min(ta[-1], tb[-1])
    seg = hi - lo
    out = dict(gap=str(gap), gap_float=float(gap), normal=[str(v) for v in n],
               nA=len(VA), nB=len(VB), overlap=float(seg))
    if len(VA) == 2 and len(VB) == 2 and seg > TOL:
        out['type'] = 'FL'
        return out
    # point contact
    pmid_t = (lo + hi) / 2
    pmid_n = (mA + mB) / 2
    P = (t[0] * pmid_t + n[0] * pmid_n, t[1] * pmid_t + n[1] * pmid_n)
    isvA = any(abs(q[0] - P[0]) < TOL and abs(q[1] - P[1]) < TOL for q in A.V)
    isvB = any(abs(q[0] - P[0]) < TOL and abs(q[1] - P[1]) < TOL for q in B.V)
    out['point'] = [float(P[0]), float(P[1])]
    if isvA and isvB:
        out['type'] = 'CC'
        return out
    if not isvA and not isvB:
        out['type'] = 'UNKNOWN'
        return out
    # CE: the square whose VERTEX it is = a (corner); the other = b (edge)
    if isvA:
        a, b, n_out = A, B, (-n[0], -n[1])         # outward normal of b's face
    else:
        a, b, n_out = B, A, n
    tt = (n_out[1], -n_out[0])
    # b's contacted edge: the two vertices of b maximising n_out
    pb2 = proj(b.V, n_out)
    m = max(pb2)
    E = [b.V[k] for k in range(4) if m - pb2[k] < TOL]
    if len(E) != 2:
        out['type'] = 'UNKNOWN'
        return out
    mid = ((E[0][0] + E[1][0]) / 2, (E[0][1] + E[1][1]) / 2)
    u = tt[0] * (P[0] - mid[0]) + tt[1] * (P[1] - mid[1])
    d = _corner_angle(a, n_out, tt)
    out.update(type='CE', a=a.i, b=b.i, u=str(u), u_float=float(u), d_deg=d,
               b_theta=b.theta, a_theta=a.theta)
    return out


def _corner_angle(a, n_out, tt):
    """angle in (0,90) of a's edge direction from the tangent tt, in the frame
    (tt, n_out); a sits on the n_out side."""
    best = None
    for e in (a.e1, a.e2, (-a.e1[0], -a.e1[1]), (-a.e2[0], -a.e2[1])):
        cn = n_out[0] * e[0] + n_out[1] * e[1]
        ct = tt[0] * e[0] + tt[1] * e[1]
        if cn > 0 and ct > 0:
            best = math.degrees(math.atan2(float(cn), float(ct)))
    return best


WALLS = [((1, 0), 'left'), ((0, 1), 'bottom'), ((-1, 0), 'right'), ((0, -1), 'top')]


def wall_contacts(A, s):
    """inward normal n, offset: wall {n.x = off}; contact iff min over corners of
    (n.x - off) < TOL."""
    out = []
    for (n, name) in WALLS:
        n = (F(n[0]), F(n[1]))
        off = F(0) if (n[0] + n[1]) > 0 else -s
        p = [n[0] * x + n[1] * y - off for (x, y) in A.V]
        m = min(p)
        if m >= TOL:
            continue
        touch = [A.V[k] for k in range(4) if p[k] - m < TOL]
        rec = dict(square=A.i, wall=name, gap=float(m), n_touch=len(touch))
        if len(touch) >= 2:
            rec['type'] = 'WF'
        else:
            tt = (n[1], -n[0])
            rec['type'] = 'WC'
            rec['phi_deg'] = _corner_angle(A, n, tt)
            rec['point'] = [float(touch[0][0]), float(touch[0][1])]
        out.append(rec)
    return out


def reduce_wc(phi):
    return 90.0 - phi if phi > 45.0 else phi


def reduce_ce(d, u):
    return (90.0 - d, -u) if d > 45.0 else (d, u)


def lookup(table, typ, params):
    """min charge over the table entries whose bin contains the parameters.
    Uncovered / dropped => 0.  Returns (charge Fraction, [entry ids])."""
    hits = []
    for e in table['entries']:
        if e['type'] != typ:
            continue
        b = e['bins']
        if typ == 'WC':
            lo, hi = F(b['phi'][0]), F(b['phi'][1])
            if not (float(lo) - 1e-9 <= params['phi'] <= float(hi) + 1e-9):
                continue
        elif typ == 'CE':
            lo, hi = F(b['d'][0]), F(b['d'][1])
            if not (float(lo) - 1e-9 <= params['d'] <= float(hi) + 1e-9):
                continue
            ulo, uhi = F(b['u'][0]), F(b['u'][1])
            if not (float(ulo) - 1e-9 <= params['u'] <= float(uhi) + 1e-9):
                continue
        else:
            continue
        hits.append(e)
    if not hits:
        return F(0), []
    return min(F(e['charge']) for e in hits), [e['id'] for e in hits]


if __name__ == '__main__':
    d = json.load(open(CERT))
    s = F(d['side'])
    sq = [Sq(q['cx'], q['cy'], q['t'], i) for i, q in enumerate(d['squares'])]
    k = len(sq)
    table = json.load(open(os.path.join(RES, 'charge_table.json')))
    B0 = F(table['budget_B0'])

    contacts = []
    for i in range(k):
        for w in wall_contacts(sq[i], s):
            contacts.append(w)
    for i in range(k):
        for j in range(i + 1, k):
            r = classify_pair(sq[i], sq[j])
            if r:
                r['pair'] = [i, j]
                contacts.append(r)

    total = F(0)
    for cdet in contacts:
        typ = cdet['type']
        if typ == 'WC':
            phi = reduce_wc(cdet['phi_deg'])
            cdet['phi_reduced'] = phi
            ch, ids = lookup(table, 'WC', dict(phi=phi))
        elif typ == 'CE':
            dd, uu = reduce_ce(cdet['d_deg'], cdet['u_float'])
            cdet['d_reduced'], cdet['u_reduced'] = dd, uu
            ch, ids = lookup(table, 'CE', dict(d=dd, u=uu))
        else:
            ch, ids = F(0), []
            cdet['reason'] = dict(WF='exact 0 (A26)', FL='exact 0 (sect.6.1)',
                                  CC='0: no moat exists (structural)',
                                  UNKNOWN='unclassified -> 0').get(typ, '0')
        cdet['charge'] = str(ch)
        cdet['charge_float'] = float(ch)
        cdet['table_bins'] = ids
        total += ch

    # ---- the same canary at every rung of the moat ladder (the drop-more frontier):
    # keep only bins with moat >= rho*, charge them on B(p, rho*/2).
    frontier = {}
    for rho, fr in table.get('frontier', {}).items():
        per = fr['per_bin_float']
        tot = 0.0
        for cdet in contacts:
            ids = cdet.get('table_bins') or []
            if not ids:
                continue
            tot += min(per.get(i, 0.0) for i in ids)
        frontier[rho] = dict(R=fr['R'], n_bins=fr['n_bins'], trump_total=tot,
                             capture_fraction=tot / float(B0))

    by = {}
    for cdet in contacts:
        by.setdefault(cdet['type'], []).append(float(F(cdet['charge'])))
    summary = {t: dict(n=len(v), sum=sum(v)) for t, v in by.items()}
    frac = float(total / B0)
    verdict = 'PASS' if total <= B0 else 'FAIL -- SOUNDNESS BUG, STOP'
    out = dict(cert=os.path.relpath(CERT, REPO), side=str(s), k=k,
               tolerance=dict(convention='A43 check_trump_h1.py', TOL=str(TOL),
                              note=('Trump certificate coordinates are rounded to ~1e-11, '
                                    'so exact SAT gaps at contacts are nonzero; a pair '
                                    'counts as a contact iff the exact rational SAT gap '
                                    'is < TOL')),
               rho_min=table['rho_min'], R=table['R'],
               n_contacts=len(contacts), by_type=summary,
               total_charge=str(total), total_charge_float=float(total),
               budget_B0=str(B0), budget_B0_float=float(B0),
               capture_fraction=frac,
               a26_wall_calibration=0.8672,
               capture_vs_a26=frac / 0.8672,
               frontier_canary=frontier,
               verdict=verdict, contacts=contacts)
    json.dump(out, open(os.path.join(RES, 'canary_trump.json'), 'w'), indent=1)
    print(f'contacts: {len(contacts)}')
    for t, v in sorted(summary.items()):
        print(f'  {t:8s} n={v["n"]:3d}  sum={v["sum"]:.6f}')
    print(f'TOTAL charge = {float(total):.9f}   B0 = {float(B0):.9f}')
    print(f'capture fraction = {frac:.6f}   (A26 per-square wall calibration 0.8672)')
    print('frontier (drop bins below rho*, charge on B(p,rho*/2)):')
    for rho, v in frontier.items():
        print(f'  rho*={rho:>5}  R={v["R"]:>5}  bins={v["n_bins"]:3d}  '
              f'Trump total={v["trump_total"]:.6f}  capture={v["capture_fraction"]:.6f}')
    print('VERDICT:', verdict)
