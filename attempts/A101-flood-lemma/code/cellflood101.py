r"""cellflood101.py -- A101 chore 1: the SIMULTANEOUS move set as a static census.

Lemma FLOOD-T (docs/proofs/flood_lemma.md s.2): a packing at side m converts, by ONE
simultaneous multi-teleport, to a packing whose exact cells include a corner cell
c(0,0) iff there is a set T of pairwise interior-disjoint lattice cells (ANY corner
lattice, inside the container) with c(0,0) in T and X(T) := N(T) - |T| <= 0, where
N(T) = #squares whose interior meets int T.  ALIGN / cell-TELEPORT / TELEPORT_FREE /
full WALL-SLIDE / the static Young flood are all instances.  This script computes
X_min(c) := min over such T, exactly, for the 8 exact K0-BLOCKED packings of A87 and
for Trump (canary: over every nonempty T of NON-exact cells X_min >= 1, i.e. Trump
admits no multi-teleport at all).

"meets" = certified SAT penetration depth > tol (mpmath.iv on the exact rational
poses), tol in {1e-9 (the exact convention, a tangency is not a meet), 1e-6 (the
strict convention of A85/A87)}; interval-undecided rows are reported.

Also: the SHELL lemma numerical check (s.1.3 of the note): Q within eta of a cell C at
tilt theta, R interior-disjoint from Q meeting int C  =>  SAT depth(R, C) <= sqrt2 * eps
and, under the containment constraint (Lemma CONT), mu-depth d_C(R) <= (1+sqrt2) * eps,
eps = eta + 1/2 - 1/(2(cos theta + sin theta)).

One process, OMP_NUM_THREADS=1, < 100 MB, seconds.  Reads A87/A03 results only; writes
attempts/A101-flood-lemma/results/cellflood101.json.
"""
from __future__ import annotations

import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import random
import time
from decimal import Decimal
from fractions import Fraction
from itertools import combinations

from mpmath import iv, mp

mp.dps = 30
iv.dps = 30

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..', '..'))
A87R = os.path.join(ATT, 'A87-drain-flow', 'results')
OUT = os.path.join(HERE, '..', 'results', 'cellflood101.json')
CORNERS = ('BL', 'BR', 'TR', 'TL')


# ----------------------------------------------------------------- loaders (A87 verbatim)
def frac(a):
    n, d = a.split('/')
    return Fraction(int(n), int(d))


def load_packings():
    out = []
    d = json.load(open(os.path.join(A87R, 'k0dir87.json')))
    rec = d['record_K0_BLOCKED_packing']
    out.append({'name': 'record_%s' % rec['tag'], 'z': [frac(a) for a in rec['z']]})
    rows = [json.loads(l) for l in open(os.path.join(A87R, 'k0dir87.polish.jsonl'))]
    for i, r in enumerate(rows):
        if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'):
            continue
        out.append({'name': 'polish%02d_%s' % (i, r['tag']),
                    'z': [frac(a) for a in r['z_polished']]})
    d = json.load(open(os.path.join(A87R, 'd2front87.json')))
    src_list = [('own_side_anchored', d['own_side_anchored'])]
    src_list += [('cap' + k, v) for k, v in sorted(d['per_cap_anchored'].items())]
    seen, order = set(), []
    for src, v in src_list:
        if not v.get('anchored_only'):
            continue
        for c in v.get('candidates', []):
            key = tuple(c['z'])
            if key in seen:
                continue
            seen.add(key)
            order.append((src, c))
    for i, (src, c) in enumerate(order):
        out.append({'name': 'anchored%d_%s' % (i, c['tag']), 'z': [frac(a) for a in c['z']]})
    p = os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
    d = json.load(open(p))
    z = []
    for sq in d['squares']:
        for k in ('cx', 'cy', 'theta'):
            z.append(Fraction(Decimal(sq[k])))
    z.append(Fraction(Decimal(d['s'])))
    out.append({'name': 'TRUMP_canary', 'z': z})
    return out


# ----------------------------------------------------------------- interval SAT (A87 verbatim)
def _f2iv(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def _ivmin(a, b):
    return iv.mpf([min(a.a, b.a), min(a.b, b.b)])


def _ivmax(a, b):
    return iv.mpf([max(a.a, b.a), max(a.b, b.b)])


def iv_pose(sq):
    cx, cy = _f2iv(sq[0]), _f2iv(sq[1])
    t = sq[2]
    if t == 0:
        return cx, cy, iv.mpf(1), iv.mpf(0)
    th = _f2iv(t)
    return cx, cy, iv.cos(th), iv.sin(th)


def iv_verts(P):
    cx, cy, c, s = P
    half = iv.mpf(1) / iv.mpf(2)
    out = []
    for hx, hy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        HX, HY = half * hx, half * hy
        out.append((cx + (c * HX - s * HY), cy + (s * HX + c * HY)))
    return out


def iv_pair_gap(sqa, sqb):
    Pa, Pb = iv_pose(sqa), iv_pose(sqb)
    Va, Vb = iv_verts(Pa), iv_verts(Pb)
    best = None
    for P in (Pa, Pb):
        c, s = P[2], P[3]
        for nhx, nhy in ((1, 0), (0, 1)):
            nx = c * nhx - s * nhy
            ny = s * nhx + c * nhy
            pa = [nx * qx + ny * qy for qx, qy in Va]
            pb = [nx * qx + ny * qy for qx, qy in Vb]
            lo_a = hi_a = pa[0]
            lo_b = hi_b = pb[0]
            for p in pa[1:]:
                lo_a, hi_a = _ivmin(lo_a, p), _ivmax(hi_a, p)
            for p in pb[1:]:
                lo_b, hi_b = _ivmin(lo_b, p), _ivmax(hi_b, p)
            g = _ivmax(lo_b - hi_a, lo_a - hi_b)
            best = g if best is None else _ivmax(best, g)
    return best


def pair_gap_f(a, b):
    dx, dy = a[0] - b[0], a[1] - b[1]
    best = -1e30
    for th, other in ((a[2], b[2]), (b[2], a[2])):
        ct, st = math.cos(th), math.sin(th)
        co, so = math.cos(other), math.sin(other)
        for nx, ny in ((ct, st), (-st, ct)):
            p1 = abs(nx * co + ny * so)
            p2 = abs(-nx * so + ny * co)
            g = abs(nx * dx + ny * dy) - 0.5 - 0.5 * (p1 + p2)
            if g > best:
                best = g
    return best


# ----------------------------------------------------------------- cells
def cell_pose(cn, i, j, m):
    h = Fraction(1, 2)
    if cn == 'BL':
        return (i + h, j + h, Fraction(0))
    if cn == 'BR':
        return (m - i - h, j + h, Fraction(0))
    if cn == 'TR':
        return (m - i - h, m - j - h, Fraction(0))
    return (i + h, m - j - h, Fraction(0))


def cells_inside(m):
    n = int(math.floor(float(m))) + 1
    out = []
    for cn in CORNERS:
        for i in range(n):
            for j in range(n):
                if i + 1 <= m and j + 1 <= m:
                    out.append((cn, i, j))
    return out


def cells_conflict(p, q):
    return abs(p[0] - q[0]) < 1 and abs(p[1] - q[1]) < 1


def exactly_on(sq, p, tol=1e-9):
    """on the cell to 1e-9 in centre and tilt (Trump's 60-digit data carries tilts ~1e-72;
    the A87 packings' exact cells are rational with tilt exactly 0)."""
    return abs(float(sq[2])) <= tol and abs(float(sq[0] - p[0])) <= tol and abs(float(sq[1] - p[1])) <= tol


def meet_table(sqs, m, cellist, tol):
    """meeters[cell] = set of squares with certified depth > tol; unknown rows counted."""
    meet, unknown, depth = {}, 0, {}
    for c in cellist:
        p = cell_pose(*c, m)
        cf = (float(p[0]), float(p[1]), 0.0)
        hits = set()
        for t, s in enumerate(sqs):
            sf = (float(s[0]), float(s[1]), float(s[2]))
            gf = pair_gap_f(cf, sf)
            if gf > 0.01:
                continue
            if exactly_on(s, p):
                hits.add(t)
                depth[(c, t)] = 1.0
                continue
            g = iv_pair_gap(p, s)
            lo, hi = float(g.a), float(g.b)
            if hi < -tol:
                hits.add(t)
                depth[(c, t)] = -hi
            elif lo <= -tol:
                unknown += 1
        meet[c] = hits
    return meet, unknown, depth


# ----------------------------------------------------------------- X_min by S-enumeration + MIS
def mis(nodes, adj):
    """max independent set size on a small graph (branch on max-degree vertex)."""
    nodes = set(nodes)
    if not nodes:
        return 0, []
    v = max(nodes, key=lambda u: len(adj[u] & nodes))
    if not (adj[v] & nodes):
        s, l = mis(nodes - {v}, adj)
        return s + 1, l + [v]
    # branch: take v (drop its neighbours) or drop v
    s1, l1 = mis(nodes - {v} - adj[v], adj)
    s2, l2 = mis(nodes - {v}, adj)
    return (s1 + 1, l1 + [v]) if s1 + 1 >= s2 else (s2, l2)


def x_min(meet, cellist, root, exact_cells, forbid_exact=False):
    """min over pairwise-disjoint cell sets T containing `root` (or, if root is None,
    over NONEMPTY T) of N(T) - |T|; if forbid_exact, T may not use an exactly occupied cell."""
    cells = [c for c in cellist if not (forbid_exact and c in exact_cells)]
    poses = {c: cell_pose(*c, m_global[0]) for c in cellist}
    adj = {c: set(d for d in cells if d != c and cells_conflict(poses[c], poses[d])) for c in cells}
    if root is not None and root not in cells:
        return None
    squares = sorted(set().union(*meet.values()))
    best = None
    # S must contain meeters(root)
    base = set(meet[root]) if root is not None else set()
    others = [q for q in squares if q not in base]
    for r in range(len(others) + 1):
        for extra in combinations(others, r):
            S = base | set(extra)
            clean = [c for c in cells if meet[c] <= S]
            if root is not None:
                clean = [c for c in clean if c != root and c not in adj[root]]
                size, lst = mis(clean, adj)
                size += 1
                lst = lst + [root]
            else:
                size, lst = mis(clean, adj)
                if size == 0:
                    continue
            # N(T) exactly, not |S|
            N = len(set().union(*(meet[c] for c in lst)))
            x = N - size
            if best is None or x < best[0]:
                best = (x, sorted(S), sorted(lst), N)
    return best


m_global = [None]


def analyse(pk, tol):
    sqs = [(pk['z'][3 * i], pk['z'][3 * i + 1], pk['z'][3 * i + 2]) for i in range(11)]
    m = pk['z'][33]
    m_global[0] = m
    cellist = cells_inside(m)
    meet, unknown, depth = meet_table(sqs, m, cellist, tol)
    exact_cells = set()
    for c in cellist:
        p = cell_pose(*c, m)
        for s in sqs:
            if exactly_on(s, p):
                exact_cells.add(c)
    free = [c for c in cellist if not meet[c]]
    single = [c for c in cellist if len(meet[c]) == 1 and c not in exact_cells]
    res = {'packing': pk['name'], 'side': float(m), 'tol': tol, 'n_cells': len(cellist),
           'unknown_rows': unknown, 'exact_cells': ['%s%d,%d' % c for c in sorted(exact_cells)],
           'free_cells': ['%s%d,%d' % c for c in free],
           'single_meeter_cells': ['%s%d,%d' % c for c in single],
           'corner_n_meet': {cn: len(meet[(cn, 0, 0)]) for cn in CORNERS},
           'corners': {}}
    full = float(m) < 4 or pk['name'].startswith('TRUMP')   # side >= 4: 16-cell lattices, vacuous (A98 CAP)
    for cn in CORNERS:
        root = (cn, 0, 0)
        if not full:
            res['corners'][cn] = {'X_min': None, 'note': 'side >= 4: not computed (static flood vacuous)'}
            continue
        b = x_min(meet, cellist, root, exact_cells)
        res['corners'][cn] = {'X_min': b[0], 'moved_squares': b[1],
                              'T': ['%s%d,%d' % c for c in b[2]], 'N_T': b[3],
                              'root_exact': root in exact_cells}
    if pk['name'].startswith('TRUMP'):
        b = x_min(meet, cellist, None, exact_cells, forbid_exact=True)
        res['canary_any_nonexact_T'] = {'X_min': b[0], 'moved_squares': b[1],
                                        'T': ['%s%d,%d' % c for c in b[2]], 'N_T': b[3]}
    return res


# ----------------------------------------------------------------- SHELL numerical check
def verts_f(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + c * hx - s * hy, cy + s * hx + c * hy)
            for hx, hy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))]


def clip(poly, inside, cross):
    out = []
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        ia, ib = inside(a), inside(b)
        if ia:
            out.append(a)
        if ia != ib:
            out.append(cross(a, b))
    return out


def area(poly):
    if len(poly) < 3:
        return 0.0
    s = 0.0
    for k in range(len(poly)):
        x1, y1 = poly[k]
        x2, y2 = poly[(k + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def meets_open_region(poly, xmax, ymax):
    """area of poly ∩ {x < xmax, y < ymax} > 0 ?"""
    def cx_(a, b, v):
        t = (v - a[0]) / (b[0] - a[0])
        return (v, a[1] + t * (b[1] - a[1]))

    def cy_(a, b, v):
        t = (v - a[1]) / (b[1] - a[1])
        return (a[0] + t * (b[0] - a[0]), v)
    p = clip(poly, lambda q: q[0] <= xmax, lambda a, b: cx_(a, b, xmax))
    p = clip(p, lambda q: q[1] <= ymax, lambda a, b: cy_(a, b, ymax))
    return area(p) > 1e-12


def mu_depth(poly):
    """mu = min over the polygon of max(x, y) (vertices + edge crossings with x = y)."""
    best = min(max(x, y) for x, y in poly)
    n = len(poly)
    for k in range(n):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % n]
        d1, d2 = x1 - y1, x2 - y2
        if d1 * d2 < 0:
            t = d1 / (d1 - d2)
            x = x1 + t * (x2 - x1)
            best = min(best, x)
    return 1 - best


def shell_check(n=200000, seed=101):
    rng = random.Random(seed)
    worst_sat, worst_mu, cnt, cnt_cont = 0.0, 0.0, 0, 0
    for _ in range(n):
        eta = rng.choice([0.001, 0.01, 0.02, 0.05, 0.1])
        th0 = rng.choice([0.5, 1, 2, 5, 10]) * math.pi / 180
        th = rng.uniform(0, th0)
        qx, qy = 0.5 + rng.uniform(-eta, eta), 0.5 + rng.uniform(-eta, eta)
        eps = eta + 0.5 - 1 / (2 * (math.cos(th) + math.sin(th)))
        Q = (qx, qy, th)
        # R: random pose near the cell
        R = (rng.uniform(-1.2, 2.2), rng.uniform(-1.2, 2.2), rng.uniform(0, math.pi / 2))
        if pair_gap_f(Q, R) < 0:
            continue
        gc = pair_gap_f((0.5, 0.5, 0.0), R)
        if gc >= 0:
            continue
        cnt += 1
        ratio = -gc / (math.sqrt(2) * eps)
        worst_sat = max(worst_sat, ratio)
        poly = verts_f(*R)
        if meets_open_region(poly, 0, 1) or meets_open_region([(y, x) for x, y in poly], 0, 1):
            continue           # violates Lemma CONT: not a legal crowder in the pinned/walled setting
        cnt_cont += 1
        d = mu_depth(poly)
        worst_mu = max(worst_mu, d / ((1 + math.sqrt(2)) * eps))
    return {'trials_meeting': cnt, 'trials_meeting_CONT': cnt_cont,
            'max_SATdepth_over_sqrt2eps': worst_sat,
            'max_mudepth_over_(1+sqrt2)eps': worst_mu}


def main():
    t0 = time.time()
    pks = load_packings()
    out = {'packings': [], 'shell_check': None, 'secs': None}
    for pk in pks:
        for tol in (1e-9, 1e-6):
            r = analyse(pk, tol)
            out['packings'].append(r)
            print('%-18s side %.7f tol %g  corners n_meet %s  X_min %s  free %s  single %s%s' % (
                r['packing'], r['side'], tol, [r['corner_n_meet'][c] for c in CORNERS],
                [r['corners'][c]['X_min'] for c in CORNERS], r['free_cells'],
                r['single_meeter_cells'],
                ('  CANARY any-nonexact-T X_min=%s T=%s' % (r['canary_any_nonexact_T']['X_min'],
                                                            r['canary_any_nonexact_T']['T']))
                if 'canary_any_nonexact_T' in r else ''), flush=True)
            for c in CORNERS:
                b = r['corners'][c]
                if b['X_min'] is not None:
                    print('      %s: X_min %d  T=%s  moved=%s' % (c, b['X_min'], b['T'], b['moved_squares']))
    out['shell_check'] = shell_check()
    print('SHELL check', out['shell_check'])
    out['secs'] = time.time() - t0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), indent=1)
    print('wrote', OUT, '%.1f s' % out['secs'])


if __name__ == '__main__':
    main()
