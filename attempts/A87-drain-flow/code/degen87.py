r"""degen87.py -- A87 chore: GLOBAL degeneration of the exact K0-BLOCKED packings.

PI finding (docs/residue_map.md s.5, 2026-09-05).  The 3.985 record K0-BLOCKED
packing degenerates at the SAME side into a dead Young class by a move the
corner-local flood (flood87.py) never tries: a "nick" that is a 1e-8 TANGENCY is
not a block, and once the near-cell squares are ALIGNED onto their cells, other
squares can be SLID / TELEPORTED into the cells those alignments free.  That is
K0-FREE applied at the CELL level rather than at the corner-slot level.

This file implements the global degeneration with the wider move set and runs it
on all 8 exact K0-BLOCKED packings (5 from k0dir87 + 3 anchored from d2front87)
plus Trump as the canary (which must NOT degenerate).

INTRUDER (with a tangency tolerance).  A square meets a cell only if its
CERTIFIED penetration depth exceeds TOL_INTRUDER.  Depth is -(SAT gap); the
certificate is an mpmath.iv interval, so "certified depth > tol" means the
interval UPPER end of the gap is < -tol.  Primary tol 1e-6; the whole run is
repeated at 1e-4 for the sensitivity report.

MOVES, applied greedily at fixed side while exact validity holds (interval SAT,
gap >= 0 allowed -- a packing wants INTERIOR-disjointness, so touching is legal):

 (a) ALIGN     any square with tilt < 1 deg whose centre is within 0.01 (max
               norm) of a corner-anchored lattice cell snaps exactly onto that
               cell (theta := 0, centre := the cell's exact rational centre).
 (b) WALL-SLIDE any axis-aligned square touching a wall slides along that wall
               toward the nearest corner-anchored lattice cell ON that wall,
               until it touches something or reaches the cell.  The full snap is
               tried first; if it fails, the maximal feasible fraction of the
               translation is found by bisection and taken only if it advances
               at least MIN_SLIDE.
 (c) FLOOD     the corner-local exchange / Young flood of exchange87 + flood87,
               objective = largest inscribed square, run on the CURRENT
               configuration at each corner.
 (d) TELEPORT  K0-FREE at the cell level: a lattice cell met by exactly one
               square, whose removal therefore frees it, receives that square.
               (d0) is the degenerate sibling: a cell met by NO square receives
               the nearest square that is not itself already on a cell.

Iterated to a fixpoint: (a)(b)(d) are cheap and are run to a fixpoint first;
(c) is expensive and is tried only when the cheap moves have stalled, and any
success restarts the cheap loop.

TERMINATION.  (a), (b)-full-snap, (d) and (d0) each strictly increase the number
of squares sitting exactly on a lattice cell, which is bounded by 11.  Partial
wall slides do not, so they are capped (MAX_PARTIAL_SLIDES); (c) is capped by
MAX_FLOOD_CALLS.

SIMPLE SQUARES AND THE YOUNG CLASS.  A square is on cell (i, j) of corner c if
it is axis-aligned to 1e-9 and its centre is within 1e-9 of that cell's centre.
The simple squares of a corner are the maximal YOUNG sub-diagram of its occupied
cells: (i, j) counts iff every (i', j') with i' <= i, j' <= j is occupied too.
Squares that match cells of two corners (possible when the side is within
~1e-7 of 4, where the L and R slot families nearly coincide) are resolved by
taking the assignment that maximises the total.  The class is named by mapping
each (corner, cell) to its A53 slot coordinate at s0 and canonicalising the slot
set under D4 (skeletons.py's action), then looking the canonical form up in
A53 name_to_slots (56 classes, k = 5, 6) and A55 name_to_slots (k4_00..k4_13,
corners4, trump5, k3_00).

DEAD ON THE WINDOW.  Taken from the A56 scoreboard's window_coverage, overlaid
with the A61 campaign61_progress verdicts; k5_11 / k5_16 (A57 running), trump5,
corners4 and every protected k <= 4 class are NOT dead; k >= 7 is certifiably
empty by A53's tier-1 cap.

One process, OMP_NUM_THREADS=1.  Writes only results/degen87.* and
notes/degen87.md.
Usage: python degen87.py [all|canary|record]
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
import flood87 as F                                             # noqa: E402

A87 = X.A87
ATT = X.ATT
RESULTS = X.RESULTS
NOTES = X.NOTES

OUT_JS = os.path.join(RESULTS, 'degen87.json')
OUT_JL = os.path.join(RESULTS, 'degen87.jsonl')
OUT_MD = os.path.join(NOTES, 'degen87.md')
LOG = os.path.join(RESULTS, 'degen87.log')

T0 = time.time()
_fh = open(LOG, 'a')

# do not let the imported modules write into their own logs
try:
    X._fh.close()
except Exception:
    pass
try:
    F._fh.close()
except Exception:
    pass


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh.flush()


BUDGET = float(os.environ.get('DG87_BUDGET', 2.0 * 3600.0))


def budget_left():
    return BUDGET - (time.time() - T0)


X.log = log
F.log = log

_SUB_DEADLINE = [None]          # per-packing cap on the imported modules


def sub_budget_left():
    b = budget_left()
    if _SUB_DEADLINE[0] is not None:
        b = min(b, _SUB_DEADLINE[0] - time.time())
    return b


X.budget_left = sub_budget_left
F.budget_left = sub_budget_left

# ------------------------------------------------------------------ knobs

TOL_INTRUDER = 1e-6         # certified depth above which a square MEETS a cell
TOL_SENS = 1e-4             # sensitivity re-run
ALIGN_TILT = math.radians(1.0)
ALIGN_DIST = 1e-2
TOL_ONCELL = 1e-9           # "sitting exactly on a cell"
TOL_WALL = 1e-6             # "touching a wall"
MIN_SLIDE = 1e-4            # a partial slide must advance at least this far
MAX_PARTIAL_SLIDES = 12
MAX_FLOOD_CALLS = 4
MAX_ROUNDS = 60
BISECT = 34

CORNERS = ('BL', 'BR', 'TR', 'TL')
HALFPI = math.pi / 2.0
S0 = Fraction(969271, 250000)


# ============================================================== geometry

def cell_pose(cn, i, j, m):
    return F.cell_poseQ(cn, i, j, m)


def cells_inside(m):
    """every corner-anchored lattice cell that fits in the container."""
    n = int(math.floor(float(m))) + 1
    out = []
    for cn in CORNERS:
        for i in range(n):
            for j in range(n):
                if F.cell_inside(i, j, m):
                    out.append((cn, i, j))
    return out


def tilt_of(th):
    t = float(th)
    return abs((t + math.pi / 4.0) % HALFPI - math.pi / 4.0)


def exactly_on(sq, cn, i, j, m, tol=TOL_ONCELL):
    if tilt_of(sq[2]) > tol:
        return False
    p = cell_pose(cn, i, j, m)
    return (abs(float(sq[0] - p[0])) <= tol and abs(float(sq[1] - p[1])) <= tol)


def on_any_cell(sq, m, cellist, tol=TOL_ONCELL):
    for (cn, i, j) in cellist:
        if exactly_on(sq, cn, i, j, m, tol):
            return (cn, i, j)
    return None


def n_on_cells(sqs, m, cellist):
    return sum(1 for s in sqs if on_any_cell(s, m, cellist) is not None)


# ============================================================ certification

def _exact_axis(sq):
    return (isinstance(sq[2], Fraction) and sq[2] == 0
            and isinstance(sq[0], Fraction) and isinstance(sq[1], Fraction))


def pair_gap_iv(a, b):
    """certified [lo, hi] enclosure of the SAT gap of two unit squares."""
    if _exact_axis(a) and _exact_axis(b):
        g = max(abs(a[0] - b[0]) - 1, abs(a[1] - b[1]) - 1)
        return (float(g), float(g), g >= 0)
    g = X.iv_pair_gap(a, b)
    return (float(g.a), float(g.b), bool(g.a >= 0))


def move_ok(sqs, k, newpose, m):
    """is the configuration with sqs[k] := newpose still an exact packing?

    Only the rows that changed are re-certified: the 10 pairs touching k and
    k's own containment.  (The rest of the configuration is unchanged and was
    certified when it was committed.)"""
    cl, cok = X.clearance_info(newpose, m)
    if not cok:
        return False, {'reason': 'containment', 'clearance_lb': cl}
    gmin = None
    for t in range(len(sqs)):
        if t == k:
            continue
        lo, _hi, ok = pair_gap_iv(newpose, sqs[t])
        gmin = lo if gmin is None else min(gmin, lo)
        if not ok:
            return False, {'reason': 'overlap', 'with': t, 'gap_lb': lo}
    return True, {'min_pair_gap_lb': gmin, 'clearance_lb': cl}


def certify(sqs, m):
    return F.certify_flood(sqs, m)


def valid(cert):
    return bool(cert['interior_disjoint_certified'] and cert['contained_certified'])


# ============================================================== intruders

def intruders(cellpose, sqs, m, tol, skip=()):
    """indices whose CERTIFIED penetration depth into the cell exceeds tol."""
    cf = (float(cellpose[0]), float(cellpose[1]), 0.0)
    hits, depths = [], {}
    for t, s in enumerate(sqs):
        if t in skip:
            continue
        sf = (float(s[0]), float(s[1]), float(s[2]))
        gf = X.pair_gap_f(cf, sf)
        if gf > -0.5 * tol:
            continue                       # cannot be a certified intruder
        lo, hi, _ok = pair_gap_iv(cellpose, s)
        if hi < -tol:                      # certified depth > tol
            hits.append((hi, t))
            depths[t] = -hi
    hits.sort()
    return [t for _h, t in hits], depths


# ======================================================= simple squares

def occupied_cells(sqs, m, cellist):
    """square index -> the (corner, i, j) cells it sits exactly on."""
    opt = {}
    for k, s in enumerate(sqs):
        hits = [(cn, i, j) for (cn, i, j) in cellist
                if exactly_on(s, cn, i, j, m)]
        if hits:
            opt[k] = hits
    return opt


def young_of(occ):
    """maximal Young sub-diagram of a set of cells (i, j)."""
    O = set(occ)
    D = set()
    for (i, j) in O:
        if all((a, b) in O for a in range(i + 1) for b in range(j + 1)):
            D.add((i, j))
    return D


def shape_of(D):
    if not D:
        return []
    jm = max(j for _i, j in D)
    return [sum(1 for (ii, jj) in D if jj == j) for j in range(jm + 1)]


def simple_squares(sqs, m, cellist, cap=20000):
    """(k, per-corner Young diagrams, per-corner shapes, square->cell map).

    Enumerates the (few) ambiguous corner assignments and keeps the best."""
    opt = occupied_cells(sqs, m, cellist)
    keys = sorted(opt)
    multi = [k for k in keys if len(opt[k]) > 1]
    fixed = [k for k in keys if len(opt[k]) == 1]
    combos = [[]]
    if multi:
        n = 1
        for k in multi:
            n *= len(opt[k])
        if n > cap:
            multi = multi[:6]
        combos = [[]]
        for k in multi:
            combos = [c + [(k, ch)] for c in combos for ch in opt[k]]
    best = None
    for c in combos:
        asg = {k: opt[k][0] for k in fixed}
        for k, ch in c:
            asg[k] = ch
        per = {cn: set() for cn in CORNERS}
        clash = False
        for k, (cn, i, j) in asg.items():
            if (i, j) in per[cn]:
                clash = True
            per[cn].add((i, j))
        if clash:
            continue
        Ds = {cn: young_of(per[cn]) for cn in CORNERS}
        kk = sum(len(Ds[cn]) for cn in CORNERS)
        cand = (kk, Ds, asg)
        if best is None or cand[0] > best[0]:
            best = cand
    if best is None:
        return 0, {cn: set() for cn in CORNERS}, {}, {}
    kk, Ds, asg = best
    keep = {k: v for k, v in asg.items() if v[1:] in Ds[v[0]]}
    shapes = {cn: shape_of(Ds[cn]) for cn in CORNERS if Ds[cn]}
    return kk, Ds, shapes, keep


# ============================================================ class naming

def slot_at_s0(cn, i, j):
    h = Fraction(1, 2)
    x = (h + i) if cn in ('BL', 'TL') else (S0 - h - i)
    y = (h + j) if cn in ('BL', 'BR') else (S0 - h - j)
    return (x, y)


def d4_images(pts):
    out = []
    for rot in range(4):
        for refl in (False, True):
            B = []
            for (x, y) in pts:
                a, b = x, y
                for _ in range(rot):
                    a, b = b, S0 - a
                if refl:
                    a = S0 - a
                B.append((a, b))
            out.append(frozenset(B))
    return out


def canon(pts):
    return min(tuple(sorted(im)) for im in d4_images(pts))


def _load_name_table():
    tab = {}
    src = {}
    for p, tag in ((os.path.join(ATT, 'A53-simple-strata', 'results',
                                 'name_to_slots.json'), 'A53'),
                   (os.path.join(ATT, 'A55-k4-sweep', 'results',
                                 'name_to_slots.json'), 'A55')):
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for name, slots in d.items():
            pts = frozenset((Fraction(repr(a)), Fraction(repr(b)))
                            for a, b in slots)
            c = canon(pts)
            tab.setdefault(c, name)
            src.setdefault(name, tag)
    return tab, src


NAME_TABLE, NAME_SRC = _load_name_table()


def name_class(Ds):
    """canonical D4 name of the Young class given by the per-corner diagrams."""
    pts = []
    for cn in CORNERS:
        for (i, j) in Ds[cn]:
            pts.append(slot_at_s0(cn, i, j))
    k = len(pts)
    if k == 0:
        return 'k0_00', {'k': 0, 'exact': True}
    if len(set(pts)) != k:
        return None, {'k': k, 'exact': False,
                      'why': 'slot collision under the s0 naming lattice'}
    for (x, y) in pts:
        if not (Fraction(1, 2) <= x <= S0 - Fraction(1, 2)
                and Fraction(1, 2) <= y <= S0 - Fraction(1, 2)):
            return None, {'k': k, 'exact': False,
                          'why': 'cell does not exist at s0'}
    for a in range(k):
        for b in range(a + 1, k):
            if (abs(pts[a][0] - pts[b][0]) < 1
                    and abs(pts[a][1] - pts[b][1]) < 1):
                return None, {'k': k, 'exact': False,
                              'why': 'NOT REALISABLE at s0: these two cells '
                                     'overlap when the side is s0 (the tuple '
                                     'only exists at a side >= 4), so it is '
                                     'not one of the A53 strata at all'}
    c = canon(frozenset(pts))
    nm = NAME_TABLE.get(c)
    return nm, {'k': k, 'exact': nm is not None,
                'canonical_slots': [[str(a), str(b)] for a, b in c]}


# ====================================================== deadness verdicts

PROTECTED = {'trump5', 'corners4', 'k0_00'}


def _load_status():
    """per-class window status: A56 scoreboard overlaid with A61 verdicts."""
    st = {}
    p = os.path.join(ATT, 'A56-sparametric', 'results', 'scoreboard.json')
    if os.path.exists(p):
        for n, r in json.load(open(p))['rows'].items():
            st[n] = {'window_coverage': r.get('window_coverage'),
                     'status': r.get('status'), 'src': 'A56 scoreboard'}
    p = os.path.join(ATT, 'A61-window-stragglers', 'results',
                     'campaign61_progress.json')
    if os.path.exists(p):
        for n, r in json.load(open(p))['rows'].items():
            if 'CONVERTS (full window)' in str(r.get('verdict', '')):
                st[n] = {'window_coverage': 1.0,
                         'status': r.get('verdict') + ' certify=%s margin=%s'
                                   % (r.get('certify'), r.get('cert_margin')),
                         'src': 'A61 campaign61_progress'}
    return st


STATUS = _load_status()


def _key(Ds):
    return tuple(tuple(sorted(Ds[cn])) for cn in CORNERS)


def subdiagrams(Ds, kmin=5):
    """every Young sub-tuple reachable by deleting removable cells, by size.

    Kills climb: a dead class kills its extensions, so a class is dead as soon
    as ONE of its Young sub-tuples is dead."""
    cur = {_key(Ds): {cn: set(Ds[cn]) for cn in CORNERS}}
    out = []
    while cur:
        nxt = {}
        for _kk, D in cur.items():
            k = sum(len(D[cn]) for cn in CORNERS)
            if k <= kmin:
                continue
            for cn in CORNERS:
                for (i, j) in list(D[cn]):
                    if (i + 1, j) in D[cn] or (i, j + 1) in D[cn]:
                        continue
                    E = {c: set(D[c]) for c in CORNERS}
                    E[cn].discard((i, j))
                    nxt.setdefault(_key(E), E)
        out.extend(nxt.values())
        cur = nxt
    return out


def dead_verdict(name, k):
    """is the class DEAD on the whole window [3.82, s0)?"""
    if name is None:
        if k >= 7:
            return True, ('k >= 7: certifiably empty (A53 tier-1 cap -- every '
                          'k >= 7 Young tuple contains a certified k6 '
                          'sub-tuple)')
        return False, 'unnamed class (no window certificate on record)'
    if name in ('k5_11', 'k5_16'):
        return False, 'ALIVE on the window: A57/A96 tree running (not dead)'
    if name in PROTECTED:
        return False, 'PROTECTED (contains a Trump image); no single-square kill'
    if name.startswith(('k4_', 'k3_', 'k2_', 'k1_')):
        return False, 'PROTECTED tier (k <= 4): P-TREE unrun'
    r = STATUS.get(name)
    if r is None:
        if k >= 7:
            return True, 'k >= 7: certifiably empty (A53 tier-1 cap)'
        return False, 'no window row on record'
    cov = r.get('window_coverage')
    if cov == 1.0:
        return True, 'DEAD on [3.82, s0): %s [%s]' % (r['status'], r['src'])
    if cov and cov > 0:
        return False, 'PARTIAL window coverage %.6f: %s' % (cov, r['status'])
    return False, ('s0-only (A61 straggler, window conversion in flight): %s'
                   % r['status'])


def dead_climbing(Ds, k):
    """dead directly, or dead because a Young SUB-tuple of it is dead."""
    name, info = name_class(Ds)
    dead, why = dead_verdict(name, k)
    best = None
    for E in subdiagrams(Ds, kmin=4):
        kk = sum(len(E[cn]) for cn in CORNERS)
        nm, _i = name_class(E)
        d, w = dead_verdict(nm, kk)
        if d and (best is None or kk > best[0]):
            best = (kk, nm, w, {cn: shape_of(E[cn]) for cn in CORNERS
                                if E[cn]})
    wit = None if best is None else {
        'witness_class': best[1], 'witness_k': best[0],
        'witness_shapes': best[3], 'witness_why': best[2]}
    if dead:
        if wit is not None:
            why = why + ('  [explicit sub-tuple witness: %s (k=%d, %s) -- %s]'
                         % (wit['witness_class'], wit['witness_k'],
                            wit['witness_shapes'], wit['witness_why']))
        return True, name, why, wit
    if wit is None:
        return False, name, why, None
    return True, name, ('kills climb: the Young sub-tuple %s (k=%d, %s) is '
                        'dead -- %s' % (best[1], best[0], best[3], best[2])), wit


# ================================================================== moves

def align_moves(sqs, m, cellist):
    """(a) ALIGN candidates, nearest cell first."""
    out = []
    for k, s in enumerate(sqs):
        if tilt_of(s[2]) > ALIGN_TILT:
            continue
        if on_any_cell(s, m, cellist) is not None:
            continue        # already on a cell: never re-label it as another
        for (cn, i, j) in cellist:
            p = cell_pose(cn, i, j, m)
            d = max(abs(float(s[0] - p[0])), abs(float(s[1] - p[1])))
            if d > ALIGN_DIST:
                continue
            if exactly_on(s, cn, i, j, m):
                continue                     # already there: not a move
            out.append((d, k, (cn, i, j), p))
    out.sort(key=lambda t: (t[0], t[1]))
    return out


def bad_rows(sqs, m):
    """the pairs that overlap and the squares that stick out, if any."""
    bad = []
    for i in range(len(sqs)):
        cl, cok = X.clearance_info(sqs[i], m)
        if not cok:
            bad.append(('wall', i, i, cl))
        for j in range(i + 1, len(sqs)):
            lo, _hi, ok = pair_gap_iv(sqs[i], sqs[j])
            if not ok:
                bad.append(('pair', i, j, lo))
    bad.sort(key=lambda t: t[3])
    return bad


def joint_targets(sqs, m, cellist, tol, passes=3):
    """one destination cell per square, over the whole move set (a)/(b)/(d).

    The corner-local rules stall on CIRCULAR blocks: on the 3.985 record,
    square 6's align onto TR(0,1) is blocked by square 7, and square 7's
    teleport into TR(0,0) is blocked by square 6 -- "unblocked once 6 is
    aligned", as the PI puts it.  So targets are collected for all squares at
    once and refined: a square that already has a target is treated as gone
    when the next pass looks for the sole intruder of a cell.  Nothing here is
    load-bearing -- the resulting configuration is certified exactly."""
    tgt = {}
    used = set()

    def claim(k, kind, cell, pose, disp):
        if k in tgt or cell in used:
            return
        tgt[k] = {'kind': kind, 'cell': cell, 'pose': pose, 'disp': disp}
        used.add(cell)

    # (a) ALIGN first: the smallest displacements
    for d, k, cell, p in align_moves(sqs, m, cellist):
        claim(k, 'ALIGN', cell, p, d)

    occ = set()
    for k, s in enumerate(sqs):
        c = on_any_cell(s, m, cellist)
        if c is not None:
            occ.add(c)

    per = {cn: set() for cn in CORNERS}
    for (cn, i, j) in occ:
        per[cn].add((i, j))
    Ds = {cn: young_of(per[cn]) for cn in CORNERS}

    def rank(cn, i, j):
        comp = 0 if ((i == 0 or (i - 1, j) in Ds[cn])
                     and (j == 0 or (i, j - 1) in Ds[cn])) else 1
        return (comp, i + j, max(i, j), i, j, CORNERS.index(cn))

    for _ in range(passes):
        gone = set(tgt)
        cands = []
        for (cn, i, j) in cellist:
            if (cn, i, j) in occ or (cn, i, j) in used:
                continue
            p = cell_pose(cn, i, j, m)
            ins, dep = intruders(p, sqs, m, tol, skip=gone)
            if len(ins) != 1:
                continue
            u = ins[0]
            if u in tgt or on_any_cell(sqs[u], m, cellist) is not None:
                continue
            d = max(abs(float(sqs[u][0] - p[0])), abs(float(sqs[u][1] - p[1])))
            cands.append((rank(cn, i, j), u, (cn, i, j), p, d, dep.get(u)))
        cands.sort(key=lambda t: t[0])
        n0 = len(tgt)
        for _r, u, cell, p, d, dep in cands:
            claim(u, 'TELEPORT', cell, p, d)
            if u in tgt:
                tgt[u]['sole_intruder_depth'] = dep
        if len(tgt) == n0:
            break

    # (b) WALL-SLIDE for whatever is left
    for d, k, w, cell, dest in wall_slide_moves(sqs, m, cellist):
        if on_any_cell(sqs[k], m, cellist) is not None:
            continue
        claim(k, 'WALL_SLIDE', cell, dest, d)
        if k in tgt and tgt[k]['kind'] == 'WALL_SLIDE':
            tgt[k]['wall'] = w
    return tgt


_FLOOD_CACHE = {}

VARIANTS = [
    {'tag': 'v0_drop_far_then_single', 'drop': 'far', 'single': True},
    {'tag': 'v1_drop_far_only', 'drop': 'far', 'single': False},
    {'tag': 'v2_drop_near_then_single', 'drop': 'near', 'single': True},
]


def joint_move(sqs, m, cellist, tol, opt):
    """take every target at once, dropping members until the result certifies.

    The greedy is path dependent, so the driver runs the few tie-breaking
    VARIANTS and keeps the best outcome."""
    tgt = joint_targets(sqs, m, cellist, tol)
    S = set(tgt)
    while S:
        trial = list(sqs)
        for k in S:
            trial[k] = tgt[k]['pose']
        bad = bad_rows(trial, m)
        if not bad:
            return S, trial, tgt
        _kind, i, j, _v = bad[0]
        cands = [k for k in (i, j) if k in S]
        if not cands:
            break
        pick = (max if opt['drop'] == 'far' else min)
        S.discard(pick(cands, key=lambda k: tgt[k]['disp']))
    if opt['single']:
        # the joint move collapsed: fall back on the single best move that works
        for k in sorted(tgt, key=lambda t: tgt[t]['disp']):
            ok, _info = move_ok(sqs, k, tgt[k]['pose'], m)
            if ok:
                trial = list(sqs)
                trial[k] = tgt[k]['pose']
                return {k}, trial, tgt
    return None, None, tgt


def align_group(sqs, m, cellist):
    """(a) as a SIMULTANEOUS move.

    Two near-cell neighbours (the 3.985 record's squares 4 and 5, 1e-4 off
    their TL cells) each block the OTHER's individual snap, so the greedy
    one-at-a-time rule stalls at once.  The move is therefore taken on the
    whole align-eligible set, and repaired by dropping the member with the
    larger displacement from the worst offending row until the configuration
    certifies (or the set is empty)."""
    cand = {}
    used = {}
    for d, k, cell, p in align_moves(sqs, m, cellist):
        if k in cand or cell in used:
            continue
        cand[k] = (d, cell, p)
        used[cell] = k
    S = set(cand)
    while S:
        trial = list(sqs)
        for k in S:
            trial[k] = cand[k][2]
        bad = bad_rows(trial, m)
        if not bad:
            return S, trial, cand
        _kind, i, j, _v = bad[0]
        opts = [k for k in (i, j) if k in S]
        if not opts:
            return None, None, cand
        S.discard(max(opts, key=lambda k: cand[k][0]))
    return None, None, cand


WALLS = {'left': 0, 'bottom': 1, 'right': 2, 'top': 3}


def wall_slide_moves(sqs, m, cellist):
    """(b) WALL-SLIDE candidates: (square, wall, target cell, dest pose)."""
    h = Fraction(1, 2)
    out = []
    for k, s in enumerate(sqs):
        if tilt_of(s[2]) > TOL_ONCELL:
            continue
        cx, cy = float(s[0]), float(s[1])
        mf = float(m)
        touch = []
        if abs(cx - 0.5) <= TOL_WALL:
            touch.append('left')
        if abs(cy - 0.5) <= TOL_WALL:
            touch.append('bottom')
        if abs(mf - 0.5 - cx) <= TOL_WALL:
            touch.append('right')
        if abs(mf - 0.5 - cy) <= TOL_WALL:
            touch.append('top')
        for w in touch:
            # cells lying on that wall
            tg = []
            for (cn, i, j) in cellist:
                if w == 'left' and not (cn in ('BL', 'TL') and i == 0):
                    continue
                if w == 'right' and not (cn in ('BR', 'TR') and i == 0):
                    continue
                if w == 'bottom' and not (cn in ('BL', 'BR') and j == 0):
                    continue
                if w == 'top' and not (cn in ('TL', 'TR') and j == 0):
                    continue
                p = cell_pose(cn, i, j, m)
                dv = (float(p[1] - s[1]) if w in ('left', 'right')
                      else float(p[0] - s[0]))
                if abs(dv) <= TOL_ONCELL:
                    continue                 # already at that cell
                tg.append((abs(dv), (cn, i, j), p))
            if not tg:
                continue
            tg.sort(key=lambda t: t[0])
            d, cell, p = tg[0]
            # the destination is flush on the wall and centred on the cell
            if w == 'left':
                dest = (h, p[1], Fraction(0))
            elif w == 'right':
                dest = (m - h, p[1], Fraction(0))
            elif w == 'bottom':
                dest = (p[0], h, Fraction(0))
            else:
                dest = (p[0], m - h, Fraction(0))
            out.append((d, k, w, cell, dest))
    out.sort(key=lambda t: (t[0], t[1]))
    return out


def bisect_slide(sqs, k, dest, m):
    """maximal feasible fraction of the translation sqs[k] -> dest."""
    s = sqs[k]
    lo, hi = Fraction(0), Fraction(1)
    best = None
    for _ in range(BISECT):
        mid = (lo + hi) / 2
        cand = (s[0] + mid * (dest[0] - s[0]),
                s[1] + mid * (dest[1] - s[1]), Fraction(0))
        ok, _info = move_ok(sqs, k, cand, m)
        if ok:
            best = (mid, cand)
            lo = mid
        else:
            hi = mid
    return best


def teleport_moves(sqs, m, cellist, tol):
    """(d) cells met by exactly one square; (d0) cells met by none."""
    one, free = [], []
    occ = set()
    for k, s in enumerate(sqs):
        c = on_any_cell(s, m, cellist)
        if c is not None:
            occ.add(c)
    # cells that are Young-completable at their corner come first
    per = {cn: set() for cn in CORNERS}
    for (cn, i, j) in occ:
        per[cn].add((i, j))
    Ds = {cn: young_of(per[cn]) for cn in CORNERS}

    def rank(cn, i, j):
        comp = 0 if ((i == 0 or (i - 1, j) in Ds[cn])
                     and (j == 0 or (i, j - 1) in Ds[cn])) else 1
        return (comp, i + j, max(i, j), i, j, CORNERS.index(cn))

    for (cn, i, j) in cellist:
        if (cn, i, j) in occ:
            continue
        p = cell_pose(cn, i, j, m)
        ins, dep = intruders(p, sqs, m, tol)
        if len(ins) == 1:
            u = ins[0]
            if on_any_cell(sqs[u], m, cellist) is not None:
                continue                 # would vacate a cell: not progress
            one.append((rank(cn, i, j), u, (cn, i, j), p, dep.get(u)))
        elif not ins:
            free.append((rank(cn, i, j), (cn, i, j), p))
    one.sort(key=lambda t: t[0])
    free.sort(key=lambda t: t[0])
    return one, free


# ============================================================ the driver

def degenerate(pk, tol, deadline, do_flood=True, opt=None):
    opt = opt or VARIANTS[0]
    t0 = time.time()
    _SUB_DEADLINE[0] = deadline
    sqs, m = X.z_to_sqs(list(pk['z']))
    mf = float(m)
    cellist = cells_inside(m)
    cert0 = certify(sqs, m)
    rec = {'packing': pk['name'], 'src': pk['src'], 'sigma': pk['sigma'],
           'variant': opt['tag'],
           'side': mf, 'tol_intruder': tol, 'n_cells': len(cellist),
           'input_cert': cert0, 'input_valid': valid(cert0), 'moves': []}
    k0, D0, sh0, _ = simple_squares(sqs, m, cellist)
    n0, i0 = name_class(D0)
    rec['initial'] = {'k_simple': k0, 'shapes': sh0, 'class': n0}
    n_partial = 0
    n_flood = 0
    rounds = 0

    def commit(kind, k, pose, extra):
        sqs[k] = pose
        e = {'move': kind, 'square': int(k), 'round': rounds}
        e.update(extra)
        rec['moves'].append(e)
        log('    %-14s sq%-2d -> %s' % (kind, k, extra.get('cell', extra)))

    while rounds < MAX_ROUNDS and time.time() < deadline:
        rounds += 1
        fired = False
        kk, DD, ss, _a = simple_squares(sqs, m, cellist)
        if kk > k0 and rec.get('first_dead') is None:
            d, nm, w, _wit = dead_climbing(DD, kk)
            if d:
                rec['first_dead'] = {
                    'k_simple': kk, 'shapes': ss,
                    'class': nm if nm else 'k%d unnamed %s' % (kk, ss),
                    'why': w, 'after_n_moves':
                        len([e for e in rec['moves'] if 'square' in e])}
                log('      first DEAD class reached: %s (k=%d) after %d moves'
                    % (rec['first_dead']['class'], kk,
                       rec['first_dead']['after_n_moves']))

        # ---- (a) + (b) + (d), taken simultaneously on the eligible set
        S, trial, tgt = joint_move(sqs, m, cellist, tol, opt)
        if S:
            for k in sorted(S):
                t = tgt[k]
                e = {'move': t['kind'], 'square': int(k), 'round': rounds,
                     'cell': '%s%d,%d' % t['cell'], 'travel': t['disp'],
                     'tilt_deg': math.degrees(tilt_of(sqs[k][2])),
                     'reached_cell': True,
                     'simultaneous_with': sorted(int(u) for u in S if u != k)}
                if 'sole_intruder_depth' in t:
                    e['sole_intruder_depth'] = t['sole_intruder_depth']
                if 'wall' in t:
                    e['wall'] = t['wall']
                rec['moves'].append(e)
                log('    %-14s sq%-2d -> %-8s  travel %.3e  tilt %.4f deg'
                    % (t['kind'], k, '%s%d,%d' % t['cell'], t['disp'],
                       math.degrees(tilt_of(sqs[k][2]))))
            sqs = list(trial)
            fired = True
        if fired:
            continue

        one, free = teleport_moves(sqs, m, cellist, tol)
        if n_partial < MAX_PARTIAL_SLIDES:
            for d, k, w, cell, dest in wall_slide_moves(sqs, m, cellist):
                if on_any_cell(sqs[k], m, cellist) is not None:
                    continue          # never slide a square OFF a cell
                b = bisect_slide(sqs, k, dest, m)
                if b is None:
                    continue
                t, cand = b
                travel = max(abs(float(cand[0] - sqs[k][0])),
                             abs(float(cand[1] - sqs[k][1])))
                if travel < MIN_SLIDE:
                    continue
                commit('WALL_SLIDE_PARTIAL', k, cand,
                       {'cell': '%s%d,%d' % cell, 'wall': w, 'travel': travel,
                        'fraction': float(t), 'reached_cell': False})
                n_partial += 1
                fired = True
                break
            if fired:
                continue

        # ---- (d0) a cell met by NOTHING receives the nearest off-cell square
        for _r, cell, p in free:
            cands = []
            for k, s in enumerate(sqs):
                if on_any_cell(s, m, cellist) is not None:
                    continue
                cands.append((max(abs(float(s[0] - p[0])),
                                  abs(float(s[1] - p[1]))), k))
            cands.sort()
            for _d, k in cands:
                ok, info = move_ok(sqs, k, p, m)
                if ok:
                    commit('TELEPORT_FREE', k, p,
                           {'cell': '%s%d,%d' % cell, 'travel': _d,
                            'min_pair_gap_lb': info['min_pair_gap_lb']})
                    fired = True
                    break
            if fired:
                break
        if fired:
            continue

        # ---- (c) the corner-local exchange / Young flood
        if do_flood and rec.get('first_dead') is None \
                and n_flood < MAX_FLOOD_CALLS and budget_left() > 300 \
                and time.time() < deadline - 240:
            got = None
            for cn in CORNERS:
                if time.time() > deadline - 120 or budget_left() < 200:
                    break
                sub = {'name': pk['name'], 'src': pk['src'],
                       'sigma': pk['sigma']}
                ck = (pk['name'], cn, tuple(map(str, [v for s in sqs
                                                      for v in s])))
                try:
                    if ck in _FLOOD_CACHE:
                        fr = _FLOOD_CACHE[ck]
                    else:
                        fr = F.flood(sub, cn, list(sqs), m, mf)
                        _FLOOD_CACHE[ck] = fr
                except Exception as exc:           # noqa: BLE001
                    rec['moves'].append({'move': 'FLOOD', 'corner': cn,
                                         'error': repr(exc)})
                    continue
                n_flood += 1
                ent = {'move': 'FLOOD', 'corner': cn, 'status': fr['status'],
                       'depth': fr['depth_reached'],
                       'terminal_deficit': fr['terminal_deficit'],
                       'diagram_shape': fr['diagram_shape'],
                       'VERIFIED': fr['VERIFIED']}
                rec['moves'].append(ent)
                if fr.get('VERIFIED'):
                    new = []
                    for row in fr['final_config']:
                        new.append(tuple(Fraction(v) for v in row))
                    c = certify(new, m)
                    ent['adopted'] = bool(valid(c) and len(new) == 11)
                    if ent['adopted']:
                        got = new
                        break
                if n_flood >= MAX_FLOOD_CALLS:
                    break
            if got is not None:
                sqs = list(got)
                fired = True
        if not fired:
            break

    cert = certify(sqs, m)
    k1, D1, sh1, asg = simple_squares(sqs, m, cellist)
    n1, i1 = name_class(D1)
    dead, n1, why, witness = dead_climbing(D1, k1)
    rec['rounds'] = rounds
    rec['n_moves'] = len([e for e in rec['moves'] if 'square' in e])
    rec['n_flood_calls'] = n_flood
    rec['final_cert'] = cert
    rec['final_valid'] = valid(cert)
    label = n1 if n1 else ('k%d unnamed %s' % (k1, sh1))
    rec['final'] = {'k_simple': k1, 'shapes': sh1, 'class': n1,
                    'class_label': label, 'class_info': i1,
                    'cells': {'sq%d' % k: '%s%d,%d' % v
                              for k, v in sorted(asg.items())}}
    rec['degenerated'] = bool(k1 > k0)
    rec['dead_class'] = bool(dead)
    rec['dead_why'] = why
    rec['dead_witness'] = witness
    rec['final_config'] = [['%d/%d' % (v.numerator, v.denominator)
                            for v in sq] for sq in sqs]
    rec['secs'] = time.time() - t0
    log('  %-18s tol %.0e: k %d -> %d  class %s  valid=%s  dead=%s  (%d moves,'
        ' %.0fs)' % (pk['name'], tol, k0, k1, label, rec['final_valid'], dead,
                     rec['n_moves'], rec['secs']))
    log('      %s' % why)
    return rec


def _score(r):
    return (bool(r['dead_class']), r['final']['k_simple'], -r['n_moves'])


def degenerate_best(pk, tol, deadline, do_flood=True):
    """the greedy is path dependent: run the tie-breaking variants, keep the
    best (dead beats alive, then the larger simple-square count)."""
    best, tried = None, []
    for opt in VARIANTS:
        if time.time() > deadline - 20:
            break
        r = degenerate(pk, tol, min(deadline, time.time() + 420.0),
                       do_flood=do_flood, opt=opt)
        tried.append({'variant': opt['tag'], 'k_out': r['final']['k_simple'],
                      'class_out': r['final']['class_label'],
                      'dead': r['dead_class'], 'n_moves': r['n_moves'],
                      'n_flood_calls': r['n_flood_calls']})
        if best is None or _score(r) > _score(best):
            best = r
    best['variants_tried'] = tried
    log('  %-18s tol %.0e: BEST variant %s -> k %d, class %s, dead=%s'
        % (pk['name'], tol, best['variant'], best['final']['k_simple'],
           best['final']['class_label'], best['dead_class']))
    return best


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'canary':
        packings = [X.load_trump()]
    elif mode == 'record':
        packings = [X.load_packings()[0]]
    else:
        packings = X.load_packings() + X.load_anchored() + [X.load_trump()]
    log('degen87: %d packings, budget %.0fs, tol %.0e (sensitivity %.0e)'
        % (len(packings), BUDGET, TOL_INTRUDER, TOL_SENS))

    rows = []
    n = len(packings)
    for idx, pk in enumerate(packings):
        share = budget_left() / max(1, (n - idx))
        dl = time.time() + max(120.0, min(share, 900.0))
        log('%s  src=%s  sigma=%.12f' % (pk['name'], pk['src'], pk['sigma']))
        r = degenerate_best(pk, TOL_INTRUDER, dl, do_flood=True)
        rows.append(r)
        # sensitivity: same machinery, tangency bar raised to 1e-4, no flood
        dl2 = time.time() + max(60.0, min(budget_left() * 0.15, 240.0))
        r2 = degenerate_best(pk, TOL_SENS, dl2, do_flood=False)
        r2['sensitivity_run'] = True
        rows.append(r2)
        with open(OUT_JL, 'w') as f:
            for x in rows:
                f.write(json.dumps(x) + '\n')

    main_rows = [r for r in rows if not r.get('sensitivity_run')]
    sens = {r['packing']: r for r in rows if r.get('sensitivity_run')}
    canary = [r for r in main_rows if r['packing'].startswith('TRUMP')]
    eight = [r for r in main_rows if not r['packing'].startswith('TRUMP')]
    reached = [r for r in eight if r['dead_class']]
    summary = {
        'n_packings': len(main_rows),
        'tol_intruder': TOL_INTRUDER, 'tol_sensitivity': TOL_SENS,
        'headline': {
            'n_K0_BLOCKED': len(eight),
            'n_reaching_a_dead_class_at_the_same_side': len(reached),
            'which': [r['packing'] for r in reached],
            'n_degenerated_at_all': sum(1 for r in eight if r['degenerated']),
            'all_final_configs_certified_valid':
                all(r['final_valid'] for r in eight),
            'sides': {r['packing']: r['side'] for r in eight},
            'note_on_sides': ('only record_s0115 (3.98548) is BELOW 4; the four '
                              'polish rows sit at 4.0000001 and the three '
                              'anchored rows at 4.08-4.11, where the unit '
                              'lattice is roomy -- their degeneration is '
                              'geometrically easy and says little about the '
                              'window [3.82, s0)'),
        },
        'trump_input_certificate_note': (
            "Trump's own squares TOUCH, so an interval SAT gap on its exact "
            "decimal poses straddles 0 (min pair gap lb -6.4e-40) and the "
            "gap >= 0 certifier reports interior_disjoint_certified = False on "
            "the INPUT.  flood87 documents the same artefact.  It is not a "
            "degeneration: the canary made zero moves, so its output IS its "
            "input."),
        'canary': None if not canary else {
            'packing': canary[0]['packing'],
            'k_simple_in': canary[0]['initial']['k_simple'],
            'k_simple_out': canary[0]['final']['k_simple'],
            'class_in': canary[0]['initial']['class'],
            'class_out': canary[0]['final']['class'],
            'n_moves': canary[0]['n_moves'],
            'moves': canary[0]['moves'],
            'degenerated': canary[0]['degenerated'],
            'PASS': bool(canary[0]['final']['class'] == 'trump5'
                         and canary[0]['final']['k_simple'] == 5
                         and canary[0]['n_moves'] == 0),
        },
        'per_packing': [{
            'packing': r['packing'], 'src': r['src'], 'side': r['side'],
            'k_in': r['initial']['k_simple'], 'k_out': r['final']['k_simple'],
            'class_in': r['initial']['class'],
            'class_out': r['final']['class_label'],
            'shapes_out': r['final']['shapes'],
            'dead': r['dead_class'], 'why': r['dead_why'],
            'dead_witness': r['dead_witness'],
            'first_dead_class_reached': r.get('first_dead'),
            'valid': r['final_valid'],
            'min_pair_gap_lb': r['final_cert']['min_pair_gap_lb'],
            'n_moves': r['n_moves'],
            'move_sequence': ['%s:sq%s->%s' % (e['move'], e.get('square'),
                                               e.get('cell'))
                              for e in r['moves'] if 'square' in e],
            'flood': [e for e in r['moves'] if e['move'] == 'FLOOD'],
            'sensitivity_1e-4': None if r['packing'] not in sens else {
                'k_out': sens[r['packing']]['final']['k_simple'],
                'class_out': sens[r['packing']]['final']['class'],
                'dead': sens[r['packing']]['dead_class'],
                'n_moves': sens[r['packing']]['n_moves'],
                'same_as_primary': bool(
                    sens[r['packing']]['final']['class'] == r['final']['class']
                    and sens[r['packing']]['final']['k_simple']
                    == r['final']['k_simple']),
            },
        } for r in main_rows],
        'class_status_sources': {
            'window': 'A56 scoreboard.json window_coverage, overlaid with A61 '
                      'campaign61_progress verdicts',
            'alive': ['k5_11', 'k5_16', 'trump5', 'corners4',
                      'protected k <= 4', 'k0_00'],
            'k_ge_7': 'certifiably empty (A53 tier-1 cap)',
        },
        'secs': time.time() - T0,
    }
    with open(OUT_JS, 'w') as f:
        json.dump(summary, f, indent=1)
    log('DONE: %d/%d K0-BLOCKED packings reach a DEAD class at the same side; '
        'canary PASS=%s; %.0fs'
        % (len(reached), len(eight),
           summary['canary'] and summary['canary']['PASS'], summary['secs']))
    return summary


if __name__ == '__main__':
    main()
