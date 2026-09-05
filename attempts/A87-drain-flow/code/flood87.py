r"""flood87.py -- A87 chore: recursive YOUNG FLOOD (extends exchange87.py).

exchange87 asked a depth-1 question: remove a corner's two intruders, drop the
axis-aligned unit square into the corner slot, and see whether an 11th unit
square still fits somewhere.  21 of 33 (packing, corner) cases said yes; 12 said
no.  The FLOOD recurses on the same idea: instead of one corner cell, grow a
YOUNG DIAGRAM of exact axis-aligned unit cells anchored at the corner, paying
for each new cell with the squares it displaces, and stop as soon as the books
balance.

State, per packing and per starting corner c, at fixed side m:

    R  -- the set of REMOVED squares (original indices), cumulative
    D  -- the Young diagram of PLACED cells, anchored at c; each cell of D holds
          an EXACT axis-aligned unit square
    U  -- the UNTOUCHED squares, still at their original exact poses
    X  -- squares re-fitted ANYWHERE by the depth-1 exchange's fit search

A cell (i, j) is the unit square occupying [i, i+1] x [j, j+1] in c's frame
(c at the origin, both axes pointing into the container); it is inside the
container iff i + 1 <= m and j + 1 <= m (exact rational test).  D is a Young
diagram: (i, j) in D implies (i', j') in D for every i' <= i, j' <= j.  A
COMPLETABLE SLOT is a cell (i, j) not in D, inside the container, with
(i-1, j) in D or i = 0, and (i, j-1) in D or j = 0.

Step (one unit of depth):

  (iii) BONUS (run to a fixpoint before each step, which is the same thing as
        running it after every step): if a completable slot's ONLY intruder is
        a single untouched square u, then u can be moved rigidly at fixed side
        so as to occupy that cell exactly -- the destination cell is
        interior-disjoint from every other square present -- so do it.  U loses
        u, D gains a cell, nothing is removed and nothing is spent: a FREE
        placement.
  (i)   if some completable slot has n = 0 intruders, place one REMOVED square
        there as an exact cell square.  |D| +1, one removed square is now
        placed: the deficit drops by one.
  (ii)  else take the slot with the FEWEST intruders (ties -> nearest the
        corner, by (i+j, max(i,j), i, j)), remove all of its intruders into R,
        and place a slot square there from R.  The deficit moves by n - 1.

  Then the SUCCESS CHECK, which also carries exchange87's fallback: while the
  deficit is positive (and <= 3), run the depth-1 exchange's HIGH-RESOLUTION fit
  search (exchange87_refine.per_tilt_scan over 90 tilts on the 1/200 centre grid,
  then a pattern search in (cx, cy, theta) from the best cell of each of the top
  6 tilts) on the CURRENT configuration and, if lambda >= 1, put a removed
  square there.  At depth 1 with the usual two corner intruders this IS
  exchange87, so the flood subsumes it exactly.

SUCCESS when every removed square is placed -- equivalently when the current
configuration again holds 11 squares.  It is then verified exactly with
exchange87's own certifier (interval SAT pair gaps and container clearance on
exact rational poses); cells are exact rationals and untouched squares carry the
input packing's own coordinates unchanged.

FAILURE when no completable slot is inside the container, or when the next
removal would push |R| past 9 (a Young diagram of unit cells at side < 4 holds
at most 9 cells that a removal can pay for), or at a depth cap of 8 steps.  The
terminal deficit and the diagram shape are recorded either way.

ACCOUNTING NOTE.  The brief writes the deficit as |R| - |D| and calls the
slide-in a free placement.  A slid square is not a removed square, so a cell it
occupies is not available to a removed one; the quantity that decides whether
the result is an 11-square packing is

    deficit = |R| - (number of removed squares actually placed)
            = 11 - (|U| + |D| + |X|),

and that is what this file calls the deficit and what SUCCESS tests.  |R|, |D|
and the slide-in count are all reported separately so the |R| - |D| reading is
recoverable.  The bonus still earns its place: it grows D for free, and the
cells it opens are what later come up with n = 0.

The rigid slide-in is checked at its DESTINATION (the moved square's final pose
is interior-disjoint from everything else present and inside the container), not
along a continuous path -- a packing is a configuration, not a motion.

Run: 8 exact K0-BLOCKED packings (5 from k0dir87 + 3 anchored from d2front87),
all four corners each, plus Trump's TL corner as the canary, which MUST fail.

One process, OMP_NUM_THREADS=1.  Writes only results/flood87.* and
notes/flood87.md.
Usage: python flood87.py [all|canary]
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import exchange87 as X                                          # noqa: E402
import exchange87_refine as RF                                  # noqa: E402

RESULTS = X.RESULTS
NOTES = X.NOTES
OUT_JS = os.path.join(RESULTS, 'flood87.json')
OUT_JL = os.path.join(RESULTS, 'flood87.jsonl')
OUT_MD = os.path.join(NOTES, 'flood87.md')
LOG = os.path.join(RESULTS, 'flood87.log')

DEPTH_CAP = 8
RMAX = 9                     # |R| may not exceed this
TOL_BLOCK = X.TOL_BLOCK      # 1e-9: a tangency is NOT an intrusion
MAX_FIT_TRIES = 3            # anywhere-fits attempted per success check
BONUS_ROUNDS = 24
BUDGET = float(os.environ.get('FL87_BUDGET', 2.6 * 3600.0))

T0 = time.time()
_fh = open(LOG, 'a')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh.flush()


def budget_left():
    return BUDGET - (time.time() - T0)


# ================================================================== cells

CORNER_ORIGIN = {'BL': (0, 0), 'BR': (1, 0), 'TR': (1, 1), 'TL': (0, 1)}
CORNER_SIGN = {'BL': (1, 1), 'BR': (-1, 1), 'TR': (-1, -1), 'TL': (1, -1)}


def cell_poseQ(cn, i, j, m):
    """EXACT axis-aligned unit square occupying cell (i, j) of corner cn."""
    ox, oy = CORNER_ORIGIN[cn]
    sx, sy = CORNER_SIGN[cn]
    h = Fraction(1, 2)
    cx = (m if ox else Fraction(0)) + sx * (Fraction(i) + h)
    cy = (m if oy else Fraction(0)) + sy * (Fraction(j) + h)
    return (cx, cy, Fraction(0))


def cell_inside(i, j, m):
    return (Fraction(i) + 1 <= m) and (Fraction(j) + 1 <= m)


def young_ok(D, cell):
    i, j = cell
    return (i == 0 or (i - 1, j) in D) and (j == 0 or (i, j - 1) in D)


def completable(D, m, cn=None, obstacles=()):
    """the cells that may be added to D next, nearest the corner first.

    `obstacles` are float poses of squares that are neither untouched nor cells
    (i.e. squares already re-fitted ANYWHERE by the fallback); a cell they meet
    can never be filled, so it is not a completable slot at all."""
    cands = set()
    if not D:
        cands.add((0, 0))
    else:
        for (i, j) in D:
            for c in ((i + 1, j), (i, j + 1)):
                if c not in D:
                    cands.add(c)
    out = [c for c in cands if young_ok(D, c) and cell_inside(c[0], c[1], m)]
    if obstacles:
        keep = []
        for c in out:
            p = cell_poseQ(cn, c[0], c[1], m)
            pf = (float(p[0]), float(p[1]), 0.0)
            if all(X.pair_gap_f(pf, o) >= -TOL_BLOCK for o in obstacles):
                keep.append(c)
        out = keep
    out.sort(key=lambda c: (c[0] + c[1], max(c[0], c[1]), c[0], c[1]))
    return out


def diagram_shape(D):
    """row lengths of the Young diagram, bottom row first (in c's frame)."""
    if not D:
        return []
    jmax = max(j for _i, j in D)
    return [sum(1 for (i, jj) in D if jj == j) for j in range(jmax + 1)]


# =============================================================== certifier

def exact_axis(sq):
    """an EXACTLY axis-aligned square with rational centre (a cell, or an
    input square whose stored theta is exactly 0)."""
    return (isinstance(sq[2], Fraction) and sq[2] == 0
            and isinstance(sq[0], Fraction) and isinstance(sq[1], Fraction))


def certify_flood(sqs, m):
    """exchange87's interval certifier, with two corrections it needs here.

    (1) EXACT PAIRS.  Two exactly axis-aligned rational unit squares have a
        rational SAT gap, max(|dx| - 1, |dy| - 1); routing it through
        iv.mpf(num)/iv.mpf(den) rounds each side independently and reports
        -4.6e-41 for two cells that share an edge by construction.  This is
        exactly the correction exchange87.clearance_info already applies to the
        container rows of such a square, extended to the pair rows.

    (2) TANGENCY.  A packing asks for INTERIOR-disjointness, so a certified
        gap >= 0 is a pass; exchange87.certify_config's `disjoint_certified`
        demands > 0, a bar that the Trump input packing itself fails (its
        squares touch: min pair gap -6.4e-40).  Both verdicts are reported.

    A gap lower bound of >= 0 -- whether exact or an interval lower bound -- is
    a rigorous certificate that the two OPEN squares are disjoint."""
    gmin, worst = None, None
    ok_open, ok_strict = True, True
    n_tangent, n_exact_pairs = 0, 0
    for i in range(len(sqs)):
        for j in range(i + 1, len(sqs)):
            if exact_axis(sqs[i]) and exact_axis(sqs[j]):
                g = max(abs(sqs[i][0] - sqs[j][0]) - 1,
                        abs(sqs[i][1] - sqs[j][1]) - 1)
                lb, gt0 = float(g), bool(g > 0)
                ok = bool(g >= 0)
                n_exact_pairs += 1
            else:
                iv = X.iv_pair_gap(sqs[i], sqs[j])
                lb, gt0 = float(iv.a), bool(iv.a > 0)
                ok = bool(iv.a >= 0)
            if not ok:
                ok_open = False
            if not gt0:
                ok_strict = False
                if ok:
                    n_tangent += 1
            if gmin is None or lb < gmin:
                gmin, worst = lb, [i, j]
    cmin, cok = None, True
    for sq in sqs:
        v, o = X.clearance_info(sq, m)
        cok = cok and o
        if cmin is None or v < cmin:
            cmin = v
    return {'min_pair_gap_lb': gmin, 'worst_pair': worst,
            'min_clearance_lb': cmin,
            'interior_disjoint_certified': bool(ok_open),
            'strictly_disjoint_certified': bool(ok_strict),
            'n_certified_tangencies': n_tangent,
            'n_exact_rational_pairs': n_exact_pairs,
            'contained_certified': bool(cok)}


# ============================================================== intruders

def intruders_of(cell_f, U, sqs_f):
    """untouched squares whose interior meets the OPEN cell, deepest first."""
    hits = []
    for u in U:
        g = X.pair_gap_f(cell_f, sqs_f[u])
        if g < -TOL_BLOCK:
            hits.append((g, u))
    hits.sort()
    return [u for _g, u in hits], {u: g for g, u in hits}


# ================================================================ fit search

def best_fit(sqs_f, mf, ntop=6):
    """exchange87_refine's HIGH-RESOLUTION fit search: the largest inscribable
    square over the 1/200 centre grid x 1 deg tilt grid, then a pattern search
    in (cx, cy, theta) from the best cell of each of the top ntop tilts."""
    scan = RF.per_tilt_scan(sqs_f, mf, list(range(0, 90)))
    scan.sort(key=lambda t: -t[0])
    best = (-1e30, 0.0, 0.0, 0.0)
    for lam, td, px, py in scan[:ntop]:
        v = RF.pattern_search(sqs_f, mf, lam, td, px, py)
        if v[0] > best[0]:
            best = v
    return best                                    # (lam, th_rad, px, py)


# =================================================================== flood

def flood(pk, cn, sqsQ, m, mf):
    t_case = time.time()
    sqs_f = [(float(a), float(b), float(c)) for a, b, c in sqsQ]

    U = set(range(11))          # untouched original indices
    R = []                      # removed original indices, cumulative
    D = {}                      # cell -> ('R', idx) | ('slide', idx)
    Xtra = []                   # (poseQ, pose_f, info) anywhere-fits
    placed = 0                  # removed squares actually placed
    n_slid = 0

    rec = {'packing': pk['name'], 'src': pk['src'], 'sigma': pk['sigma'],
           'side': mf, 'corner': cn, 'steps': [],
           'n_slot_n0': 0, 'n_slot_n1': 0, 'n_slot_n2': 0, 'n_slot_ge3': 0,
           'n_slots_seen': 0, 'n_bonus_fires': 0, 'n_fit_calls': 0,
           'n_fit_success': 0, 'deficit_traj': []}

    def present():
        """(exact poses, float poses) of everything currently in the box."""
        q = [sqsQ[u] for u in sorted(U)]
        f = [sqs_f[u] for u in sorted(U)]
        for g in sorted(D):
            p = cell_poseQ(cn, g[0], g[1], m)
            q.append(p)
            f.append((float(p[0]), float(p[1]), 0.0))
        for pq, pf, _i in Xtra:
            q.append(pq)
            f.append(pf)
        return q, f

    def deficit():
        return len(R) - placed

    def obstacles():
        return [pf for _pq, pf, _i in Xtra]

    def slots_now():
        return completable(D, m, cn, obstacles())

    def run_bonus():
        """slide untouched squares into completable cells they alone block."""
        nonlocal n_slid
        fired = []
        for _ in range(BONUS_ROUNDS):
            hit = None
            for g in slots_now():
                pq = cell_poseQ(cn, g[0], g[1], m)
                pf = (float(pq[0]), float(pq[1]), 0.0)
                ins, _d = intruders_of(pf, U, sqs_f)
                if len(ins) == 1:
                    hit = (g, ins[0])
                    break
            if hit is None:
                break
            g, u = hit
            D[g] = ('slide', u)
            U.discard(u)
            n_slid += 1
            fired.append({'cell': list(g), 'square': int(u)})
        return fired

    def success_check(depth):
        """exchange87's fallback: re-fit the still-unplaced removed squares
        ANYWHERE, with the depth-1 exchange's high-resolution fit search.

        SPECULATIVE -- the fitted squares are committed only if they close the
        WHOLE remaining deficit, i.e. only if they make the configuration an
        11-square packing.  A partial fit is discarded: committing it would
        park a square in the container that can then block the very cells the
        flood still needs (which is exactly what happens on the canary)."""
        nonlocal placed
        tries = []
        d = deficit()
        if d <= 0 or d > MAX_FIT_TRIES:
            return tries
        q, f = present()
        got = []
        while len(got) < d:
            if budget_left() < 90:
                tries.append({'depth': depth, 'skipped': 'budget'})
                break
            rec['n_fit_calls'] += 1
            t0 = time.time()
            lam, th, px, py = best_fit(f, mf)
            ent = {'depth': depth, 'n_host': len(f), 'lambda_max': lam,
                   'theta_deg': math.degrees(th), 'cx': px, 'cy': py,
                   'secs': time.time() - t0}
            if lam < 1.0:
                tries.append(ent)
                break
            ver = X.verify_placement(q, m, px, py, th)
            ent['placement'] = ver
            tries.append(ent)
            if not ver['VERIFIED']:
                break
            pq = (Fraction(px), Fraction(py), Fraction(th))
            got.append((pq, (px, py, th)))
            q.append(pq)
            f.append((px, py, th))
        if len(got) == d:
            for pq, pf in got:
                Xtra.append((pq, pf, len(Xtra)))
            placed += d
            rec['n_fit_success'] += d
        else:
            for t in tries:
                t['discarded_partial_fit'] = bool(got)
        return tries

    # ------------------------------------------------------------- main loop
    status = None
    depth = 0
    while depth < DEPTH_CAP:
        if budget_left() < 90:
            status = 'budget_exhausted'
            break
        # (iii) bonus to a fixpoint (== running it after every step)
        fired = run_bonus()
        rec['n_bonus_fires'] += len(fired)

        slots = slots_now()
        if not slots:
            status = 'no_completable_slot'
            rec['steps'].append({'depth': depth + 1, 'bonus': fired,
                                 'rule': 'none', 'slots': []})
            break
        info = []
        for g in slots:
            pq = cell_poseQ(cn, g[0], g[1], m)
            pf = (float(pq[0]), float(pq[1]), 0.0)
            ins, dep = intruders_of(pf, U, sqs_f)
            info.append((g, ins, dep))
            n = len(ins)
            rec['n_slots_seen'] += 1
            rec['n_slot_n0'] += (n == 0)
            rec['n_slot_n1'] += (n == 1)
            rec['n_slot_n2'] += (n == 2)
            rec['n_slot_ge3'] += (n >= 3)

        depth += 1
        st = {'depth': depth, 'bonus': fired,
              'slots': [{'cell': list(g), 'n': len(ins),
                         'intruders': [int(u) for u in ins]}
                        for g, ins, _d in info]}

        zero = [t for t in info if not t[1]]
        if zero and deficit() > 0:
            g = zero[0][0]                     # already nearest-corner sorted
            D[g] = ('R', R[placed])
            placed += 1
            st['rule'] = 'i_free_cell'
            st['cell'] = list(g)
        elif zero:
            # a free corner cell with nothing owed: the packing already had a
            # k >= 1 corner, so there is nothing for the flood to do.
            st['rule'] = 'i_free_cell_but_no_debt'
            rec['steps'].append(st)
            status = 'corner_already_free_no_debt'
            break
        else:
            g, ins, _d = min(info, key=lambda t: (len(t[1]),
                                                  t[0][0] + t[0][1],
                                                  max(t[0][0], t[0][1]),
                                                  t[0][0], t[0][1]))
            if len(R) + len(ins) > RMAX:
                st['rule'] = 'ii_blocked_R_cap'
                st['cell'] = list(g)
                st['would_remove'] = [int(u) for u in ins]
                rec['steps'].append(st)
                status = 'R_would_exceed_%d' % RMAX
                break
            for u in ins:
                R.append(u)
                U.discard(u)
            D[g] = ('R', R[placed])
            placed += 1
            st['rule'] = 'ii_pay_%d' % len(ins)
            st['cell'] = list(g)
            st['removed'] = [int(u) for u in ins]

        st['R'] = len(R)
        st['D'] = len(D)
        st['slid'] = n_slid
        st['deficit'] = deficit()
        st['fits'] = success_check(depth)
        st['deficit_after_fit'] = deficit()
        rec['deficit_traj'].append(deficit())
        rec['steps'].append(st)
        log('    d%d %-14s cell %s  |R|=%d |D|=%d slid=%d  deficit %d'
            % (depth, st['rule'], st.get('cell'), len(R), len(D), n_slid,
               deficit()))
        if deficit() == 0:
            status = 'FLOOD_SUCCESS'
            break
    else:
        status = 'depth_cap_%d' % DEPTH_CAP

    q, f = present()
    rec['n_squares_final'] = len(q)
    rec['terminal_deficit'] = deficit()
    rec['R'] = [int(u) for u in R]
    rec['n_removed'] = len(R)
    rec['n_cells'] = len(D)
    rec['n_slid'] = n_slid
    rec['n_anywhere_fits'] = len(Xtra)
    rec['diagram'] = sorted([list(g) for g in D])
    rec['diagram_shape'] = diagram_shape(D)
    rec['cell_sources'] = {'%d,%d' % g: [D[g][0], int(D[g][1])]
                           for g in sorted(D)}
    rec['depth_reached'] = depth
    rec['status'] = status
    if status == 'FLOOD_SUCCESS':
        cert = certify_flood(q, m)
        rec['final_cert'] = cert
        rec['final_cert_exchange87_strict'] = X.certify_config(q, m)
        rec['final_config'] = [['%d/%d' % (v.numerator, v.denominator)
                                if isinstance(v, Fraction) else repr(v)
                                for v in sq] for sq in q]
        rec['VERIFIED'] = bool(len(q) == 11
                               and cert['interior_disjoint_certified']
                               and cert['contained_certified'])
        if not rec['VERIFIED']:
            rec['status'] = 'success_but_exact_verify_failed'
    else:
        rec['VERIFIED'] = False
    rec['secs'] = time.time() - t_case
    log('  %-4s %-22s depth %d  terminal deficit %d  shape %s  (%.0fs)'
        % (cn, rec['status'], depth, rec['terminal_deficit'],
           rec['diagram_shape'], rec['secs']))
    return rec


# =================================================================== driver

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'canary':
        packings = [X.load_trump()]
    else:
        packings = X.load_packings() + X.load_anchored() + [X.load_trump()]

    rows = []
    for pk in packings:
        sqsQ, m = X.z_to_sqs(pk['z'])
        mf = float(m)
        cert = certify_flood(sqsQ, m)
        pk['input_cert'] = cert
        log('%s  m=%.12f  input cert interior-disjoint=%s (strict=%s, %d '
            'tangencies) contained=%s (min gap %.3e)'
            % (pk['name'], mf, cert['interior_disjoint_certified'],
               cert['strictly_disjoint_certified'],
               cert['n_certified_tangencies'], cert['contained_certified'],
               cert['min_pair_gap_lb']))
        corners = ('TL',) if pk['name'].startswith('TRUMP') else X.CORNERS
        for cn in corners:
            if budget_left() < 120:
                log('BUDGET EXHAUSTED before %s/%s' % (pk['name'], cn))
                break
            r = flood(pk, cn, sqsQ, m, mf)
            r['input_cert'] = cert
            rows.append(r)
            with open(OUT_JL, 'w') as f:
                for x in rows:
                    f.write(json.dumps(x) + '\n')

    # -------------------------------------------------------------- summary
    ex = {}
    for f in ('exchange87.jsonl', 'exchange87.anchored.jsonl'):
        p = os.path.join(RESULTS, f)
        if os.path.exists(p):
            for l in open(p):
                r = json.loads(l)
                ex[(r['packing'], r['corner'])] = bool(r.get('fit_success'))
    ref = os.path.join(RESULTS, 'exchange87.refine.json')
    if os.path.exists(ref):
        for r in json.load(open(ref))['rows']:
            if r.get('EXCHANGE_SUCCESS'):
                ex[(r['packing'], r['corner'])] = True

    succ = [r for r in rows if r['status'] == 'FLOOD_SUCCESS' and r['VERIFIED']]
    rescued = [r for r in succ
               if not ex.get((r['packing'], r['corner']), False)]
    canary = [r for r in rows if r['packing'].startswith('TRUMP')]
    summary = {
        'n_cases': len(rows),
        'n_success': len(succ),
        'n_rescued_beyond_exchange87': len(rescued),
        'rescued': [[r['packing'], r['corner'], r['depth_reached']]
                    for r in rescued],
        'max_depth_needed': max([r['depth_reached'] for r in succ], default=0),
        'depth_histogram': {str(d): sum(1 for r in succ
                                        if r['depth_reached'] == d)
                            for d in range(1, DEPTH_CAP + 1)},
        'exchange87_success': {'%s/%s' % k: v for k, v in sorted(ex.items())},
        'stats': {
            'slots_seen': sum(r['n_slots_seen'] for r in rows),
            'slots_n0': sum(r['n_slot_n0'] for r in rows),
            'slots_n1': sum(r['n_slot_n1'] for r in rows),
            'slots_n2': sum(r['n_slot_n2'] for r in rows),
            'slots_ge3': sum(r['n_slot_ge3'] for r in rows),
            'bonus_fires': sum(r['n_bonus_fires'] for r in rows),
            'fit_calls': sum(r['n_fit_calls'] for r in rows),
            'fit_successes': sum(r['n_fit_success'] for r in rows),
            'cases_with_a_zero_slot': sum(1 for r in rows if r['n_slot_n0']),
            'cases_with_a_bonus_fire': sum(1 for r in rows
                                           if r['n_bonus_fires']),
            'cases_with_a_ge3_slot': sum(1 for r in rows if r['n_slot_ge3']),
        },
        'canary': None if not canary else {
            'packing': canary[0]['packing'], 'corner': canary[0]['corner'],
            'status': canary[0]['status'],
            'terminal_deficit': canary[0]['terminal_deficit'],
            'depth_reached': canary[0]['depth_reached'],
            'diagram_shape': canary[0]['diagram_shape'],
            'VERIFIED': canary[0]['VERIFIED']},
        'canary_OK': bool(canary and not canary[0]['VERIFIED']),
        'per_case': [{k: r[k] for k in
                      ('packing', 'corner', 'side', 'status', 'depth_reached',
                       'terminal_deficit', 'n_removed', 'n_cells', 'n_slid',
                       'n_anywhere_fits', 'diagram_shape', 'n_squares_final',
                       'VERIFIED')} for r in rows],
        'secs': time.time() - T0,
    }
    with open(OUT_JS, 'w') as f:
        json.dump(summary, f, indent=1)
    log('DONE: %d/%d floods succeed; %d rescued beyond exchange87; '
        'max depth %d; canary_OK=%s; %.0fs'
        % (summary['n_success'], summary['n_cases'],
           summary['n_rescued_beyond_exchange87'],
           summary['max_depth_needed'], summary['canary_OK'],
           summary['secs']))


if __name__ == '__main__':
    main()
