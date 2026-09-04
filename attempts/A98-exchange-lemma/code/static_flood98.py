r"""static_flood98.py -- A98 (theory lead): exact STATIC flood census + Lemma ARM test.

For each exact K0-BLOCKED packing of the A87 corpus (5 k0dir87 + 3 anchored) and
Trump (canary), each corner c, and EVERY Young diagram D of unit cells at c that
fits the container, compute

    N(D) = #{squares Q : int Q meets int D},   X(D) = N(D) - |D|   (the excess).

Lemma FLOOD-D (docs/proofs/exchange_lemma.md): X(D) <= 0 for some D  =>  the
packing converts to a k >= 1 packing at the SAME side (replace the N(D) squares
by D's |D| cells).  min_D X(D) per corner is the static flood's verdict; the
diagrams with X <= 0 are listed with the squares they displace.

Lemma ARM test: for each intruder Q of c with depth d, the translate
Q + (d, d) (diagonal, mu_c = 1 exactly) and the cardinal translates Q + t e_x,
Q + t e_y with t = the first t at which mu_c >= 1, are tested for interval-
certified interior-disjointness from the other nine squares and the slot square
-- each success is an exactly verified depth-1 exchange placement.

Intrusion test: SAT gap of the two closed squares < -TOL (TOL = 1e-9, the
k0dir87 tolerance law: a tangency is not an intrusion); borderline gaps
(|gap| <= TOL) are counted and reported separately.

One process, OMP_NUM_THREADS=1, seconds.  Reads A87 data; writes only
attempts/A98-exchange-lemma/results/static_flood98.{json,md}.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import time
from fractions import Fraction
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
A98 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A98, '..'))
sys.path.insert(0, os.path.join(ATT, 'A87-drain-flow', 'code'))
import exchange87 as X                                          # noqa: E402

RES = os.path.join(A98, 'results')
os.makedirs(RES, exist_ok=True)
OUT_JS = os.path.join(RES, 'static_flood98.json')
OUT_MD = os.path.join(RES, 'static_flood98.md')

TOL = 1e-9
CORNERS = ('BL', 'BR', 'TR', 'TL')


# ------------------------------------------------------------------ frames

def to_frame(sq, cn, m):
    """pose of sq in corner cn's frame (corner at origin, container in the
    positive quadrant); tilt sign is irrelevant for SAT tests, keep exact."""
    cx, cy, th = sq
    if cn == 'BL':
        return (cx, cy, th)
    if cn == 'BR':
        return (m - cx, cy, -th)
    if cn == 'TR':
        return (m - cx, m - cy, th)
    return (cx, m - cy, -th)


def cell_sq(i, j):
    return (Fraction(2 * i + 1, 2), Fraction(2 * j + 1, 2), Fraction(0))


def young_diagrams(w, h):
    """all Young diagrams inside a w x h box (partitions with <= h rows, parts <= w)."""
    out = []

    def rec(rows, maxpart):
        if rows:
            out.append(list(rows))
        if len(rows) == h:
            return
        for p in range(1, maxpart + 1):
            rec(rows + [p], p)
    rec([], w)
    return out


def cells_of(shape):
    return [(i, j) for j, r in enumerate(shape) for i in range(r)]


# ------------------------------------------------------------------ tests

def meets_cell(sqf, cell):
    """(intrudes, borderline) by float SAT gap with the tolerance law."""
    g = X.pair_gap_f(sqf, (float(cell[0]), float(cell[1]), 0.0))
    return g < -TOL, abs(g) <= TOL


def mu_c(sqf):
    """mu in the frame: min over the square of max(x, y)."""
    return 1.0 - X.depth_at_corner(sqf, 'BL', 10.0) if X.depth_at_corner(sqf, 'BL', 10.0) > 0 \
        else _mu_full(sqf)


def _mu_full(sqf):
    W = X.verts_f(*sqf)
    cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t))
                cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return min(max(p[0], p[1]) for p in cand)


def first_t(sqf, e):
    """smallest t >= 0 with mu(sq + t e) >= 1 (bisection; mu is convex, nondecreasing along e in K)."""
    def mu_at(t):
        return _mu_full((sqf[0] + t * e[0], sqf[1] + t * e[1], sqf[2]))
    if mu_at(0.0) >= 1.0:
        return 0.0
    lo, hi = 0.0, 2.0
    if mu_at(hi) < 1.0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mu_at(mid) >= 1.0:
            hi = mid
        else:
            lo = mid
    return hi


def arm_tests(sqsQ_frame, m, intr, others):
    """for each intruder: diagonal and cardinal translates; interval-verified."""
    slot = cell_sq(0, 0)
    out = []
    for q in intr:
        sq = sqsQ_frame[q]
        sqf = (float(sq[0]), float(sq[1]), float(sq[2]))
        d = X.depth_at_corner(sqf, 'BL', float(m))
        rows = []
        for name, e in (('diag', (1.0, 1.0)), ('ex', (1.0, 0.0)), ('ey', (0.0, 1.0))):
            t = first_t(sqf, e) if name != 'diag' else d
            if t is None:
                rows.append({'dir': name, 't': None, 'ok': False, 'why': 'mu never reaches 1'})
                continue
            tpad = t + 1e-12
            cand = (Fraction(sqf[0] + tpad * e[0]), Fraction(sqf[1] + tpad * e[1]), sq[2])
            gmin, worst = None, None
            for o in others:
                g = X.iv_pair_gap(cand, sqsQ_frame[o])
                if gmin is None or float(g.a) < gmin:
                    gmin, worst = float(g.a), o
            gs = X.iv_pair_gap(cand, slot)
            cl, clok = X.clearance_info(cand, m)
            ok = gmin is not None and gmin > 0 and float(gs.a) >= 0 and clok
            # the slot square is allowed to TOUCH (mu = 1 exactly): certify gap >= -1e-13
            ok_touch = gmin is not None and gmin > 0 and float(gs.b) >= -1e-13 and float(gs.a) > -1e-9 and clok
            rows.append({'dir': name, 't': t, 'min_gap_others_lb': gmin, 'worst_other': worst,
                         'slot_gap_iv': [float(gs.a), float(gs.b)], 'clearance_lb': cl,
                         'ok': bool(ok), 'ok_touching_slot': bool(ok_touch)})
        out.append({'square': q, 'depth': d, 'translates': rows})
    return out


# ------------------------------------------------------------------ driver

def run_packing(pk):
    sqsQ, m = X.z_to_sqs(pk['z'])
    mf = float(m)
    wmax = int(math.floor(mf))          # cells i with i+1 <= m
    res = {'packing': pk['name'], 'side': mf, 'corners': {}}
    shapes = young_diagrams(wmax, wmax)
    for cn in CORNERS:
        fr = [to_frame(s, cn, m) for s in sqsQ]
        frf = [(float(a), float(b), float(c)) for a, b, c in fr]
        dep = [X.depth_at_corner(s, 'BL', mf) for s in frf]
        intr = sorted([i for i in range(11) if dep[i] > TOL], key=lambda i: -dep[i])
        # cell incidence matrix
        inc = {}
        border = 0
        for i in range(wmax):
            for j in range(wmax):
                c = cell_sq(i, j)
                s = set()
                for q in range(11):
                    hit, bl = meets_cell(frf[q], c)
                    border += bl
                    if hit:
                        s.add(q)
                inc[(i, j)] = s
        table = []
        best = None
        for sh in shapes:
            cells = cells_of(sh)
            squares = set()
            for ce in cells:
                squares |= inc[ce]
            Xv = len(squares) - len(cells)
            row = {'shape': sh, 'cells': len(cells), 'N': len(squares), 'X': Xv,
                   'squares': sorted(squares)}
            table.append(row)
            if best is None or Xv < best['X'] or (Xv == best['X'] and len(cells) < best['cells']):
                best = row
        two = [r for r in table if r['cells'] == 2]
        wins = [r for r in table if r['X'] <= 0]
        others = [q for q in range(11) if q not in intr[:2]] if len(intr) >= 2 else []
        arm = arm_tests(fr, m, intr[:2], others) if len(intr) >= 2 else []
        res['corners'][cn] = {
            'n_intruders': len(intr), 'intruders': intr, 'depths': [dep[i] for i in intr],
            'cells_incidence': {'%d,%d' % k: sorted(v) for k, v in inc.items()},
            'borderline_cell_tests': border,
            'min_X': best['X'], 'argmin': best,
            'X_two_cell': [{'shape': r['shape'], 'X': r['X'], 'squares': r['squares']} for r in two],
            'n_diagrams': len(table), 'n_wins': len(wins),
            'wins': [{'shape': r['shape'], 'N': r['N'], 'squares': r['squares']} for r in wins][:12],
            'arm': arm,
        }
    return res


def main():
    t0 = time.time()
    packs = X.load_packings() + X.load_anchored() + [X.load_trump()]
    out = []
    lines = ['# static flood census + Lemma ARM (A98)', '',
             '| packing | side | corner | intruders (depths) | min X | argmin shape | X(2-cell) | #wins | ARM certified |',
             '|---|---|---|---|---|---|---|---|---|']
    for pk in packs:
        r = run_packing(pk)
        out.append(r)
        for cn, c in r['corners'].items():
            armc = []
            for a in c['arm']:
                for t in a['translates']:
                    if t.get('ok') or t.get('ok_touching_slot'):
                        armc.append('sq%d:%s' % (a['square'], t['dir']))
            lines.append('| %s | %.6f | %s | %s | %d | %s | %s | %d | %s |' % (
                r['packing'], r['side'], cn,
                ', '.join('%d(%.3g)' % (i, d) for i, d in zip(c['intruders'], c['depths'])),
                c['min_X'], c['argmin']['shape'],
                ', '.join('%s:%d' % (t['shape'], t['X']) for t in c['X_two_cell']),
                c['n_wins'], ' '.join(armc) or '-'))
            print(lines[-1], flush=True)
    with open(OUT_JS, 'w') as f:
        json.dump({'secs': time.time() - t0, 'packings': out}, f, indent=1)
    with open(OUT_MD, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('DONE %.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
