"""A85 chore `supply85.py` -- A91 s.9's SUPPLY GATE, run at the sound level.

QUESTION.  In a K0-BLOCKED packing the 8 corner intruders each need far-side
anchoring contacts (Lemma MENU, `docs/proofs/tilt_floor_k0.md` s.4; Theorem
NOCRIT-SEL / Lemma K / CLUSTER / COL, `docs/proofs/nocrit_k0_blocked.md` s.3-4).
Only the other 7 intruders and the 3 free squares can supply them.  How many of
A85's ATTEMPTABLE four-corner box combinations admit ANY geometrically feasible
assignment of suppliers to required zones?

MODEL (everything conservative = never reject an assignment that could exist).

(1) A node is {corner: (i, j)} with i, j indices into the 644 sound BL cover
    boxes; the intruder at corner c with BL index k occupies, IN c's OWN CORNER
    FRAME, exactly the BL box b_k (map_box then the corner frame is the
    identity, including the theta convention), and in CONTAINER coordinates the
    box G85.map_box(b_k, c).

(2) Lemma K type, in the corner frame, for a unit square of centre (u, v) and
    tilt th in [0, 90):
        VL = leftmost vertex = (u - (cos+sin)/2, v + (cos-sin)/2)
        VB = lowest    vertex = (u + (sin-cos)/2, v - (sin+cos)/2)
        (X)  VL_y <= VL_x   <=>  (v - u) + cos th <= 0
        (Y)  VB_x <= VB_y   <=>  (u - v) + sin th <= 0
        (D)  otherwise (the argmin is the single diagonal point)
    At th = 0 the leftmost face is an EDGE, and the X test degenerates to
    v <= u; symmetrically at th = 90 for Y.  Over a pose box we mark a type
    POSSIBLE if the interval evaluation allows it (over-approximating the set of
    possible types is conservative: more types = more options = fewer kills).
    Required retreat directions: X -> {e_x}, Y -> {e_y}, D -> {e_x, e_y}.  If a
    box admits a single-direction type we may use it (a subset of D's
    requirement), so the OPTION LIST of an intruder is the minimal admissible
    requirement sets, and a node is killed only if EVERY option tuple fails.

(3) Required zone.  A presser N of Q against e must touch Q where the outward
    normal has a positive e-component (Lemma CLUSTER's "presses"; Lemma MENU's
    far-side set is the same side of the square for the rotation motion).  For
    e = e_x that is the chain VB -> VR -> VT, for e = e_y the chain VR -> VT ->
    VL.  Per pose the zone's bbox is
        Z_x = [u - |cos-sin|/2, u + (cos+sin)/2] x [v - (cos+sin)/2, v + (cos+sin)/2]
        Z_y = [u - (cos+sin)/2, u + (cos+sin)/2] x [v - |cos-sin|/2, v + (cos+sin)/2]
    and over the POSE BOX the zone is the UNION of these over a 4x4x4
    subdivision of the box (a union of boxes, tighter than one hull box, still
    an over-approximation of the true union of zones).  Mapped to container
    coordinates by the corner frame's involution.

(4) Supplier tests.
    * intruder N supplies zone Z  iff  dist(centre-box of N, Z) <= sqrt2/2
      (a unit square's circumradius is exactly sqrt2/2, so this is a sound
      over-inclusion of "some square of N's box meets Z").  N != Q.
    * a free square supplies a SET S of zones iff some centre p exists with
      p in [1/2, s0-1/2]^2 (a sound over-set of admissible centres),
      dist(p, Z) <= sqrt2/2 for every Z in S, and dist(p, core_i) >= 1/2 for
      every intruder core (a unit square at p covers the disk B(p, 1/2), so
      overlapping is FORCED only inside that radius; we under-approximate each
      core by its inscribed disk B((kx, ky), a), so the excluded set is an
      under-approximation = permissive).  Tested on a grid with the constraints
      relaxed by the grid half-diagonal, so the test never reports "empty" for a
      genuinely feasible set.

(5) Count.  An assignment maps every required zone to one supplier: one of the
    other 7 intruders, or one of the 3 (labelled) free squares; a free square
    may take several zones only if that whole block is jointly feasible by (4).
    #assignments = sum over ordered triples (B1, B2, B3) of pairwise-disjoint
    free-feasible zone sets of prod_{z not in any Bi} a_z, a_z = #intruder
    suppliers of z.  Zero iff no assignment at all.

CANARY.  Trump's TL 2-crowd (sq4 type Y, sq6 type X per A90 t3_trump.json);
suppliers = the other 10 squares at their exact poses.  The gate must NOT fire.

Writes: results/supply85.json, results/supply85.zones.jsonl, notes/supply85.md.
Usage: python supply85.py [--nmax N]
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

import argparse
import itertools
import json
import math
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(BASE, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..'))
sys.path.insert(0, HERE)

import blas1                                    # noqa: F401,E402
import numpy as np                              # noqa: E402
from caselp import Box                          # noqa: E402
import corner85 as C85                          # noqa: E402
import gate85 as G85                            # noqa: E402
import alive84                                  # noqa: E402
from pinguard import cores_meet                 # noqa: E402
import atlas85                                  # noqa: E402

RES = os.path.join(BASE, 'results')
NOTES = os.path.join(BASE, 'notes')
for d in (RES, NOTES):
    os.makedirs(d, exist_ok=True)

S0 = C85.S0F
CORNERS = G85.CORNERS
SEED = 20260903                 # realise85.SEED -- reproduces the SOUND gate sample
NSAMPLE = 1000
BUDGET = 3
R_REACH = math.sqrt(0.5)        # circumradius of a unit square
SUB = 4                         # 4x4x4 subdivision of a pose box for the zone union
NGRID = 241                     # free-square centre grid per axis
SUBSET_CAP = 200000


# ------------------------------------------------------------------ frames
def frame_to_container(c, x, y):
    """inverse (= itself) of the corner frame map for corner c."""
    if c == 'BL':
        return x, y
    if c == 'BR':
        return S0 - x, y
    if c == 'TR':
        return S0 - x, S0 - y
    if c == 'TL':
        return x, S0 - y
    raise ValueError(c)


def box_to_container(c, bx):
    """(x0, x1, y0, y1) in corner frame -> container frame."""
    x0, x1, y0, y1 = bx
    ax, ay = frame_to_container(c, x0, y0)
    bx2, by2 = frame_to_container(c, x1, y1)
    return (min(ax, bx2), max(ax, bx2), min(ay, by2), max(ay, by2))


# ------------------------------------------------------------------ Lemma K types
def possible_types(b, n=41):
    """-> (X_possible, Y_possible, D_possible) over the pose box (corner frame)."""
    ths = np.linspace(b.th0, b.th1, n)
    co = np.cos(np.radians(ths))
    si = np.sin(np.radians(ths))
    dlo = b.x0 - b.y1        # min of (u - v)
    dhi = b.x1 - b.y0        # max of (u - v)
    # X: (v - u) + cos <= 0  i.e.  (u - v) >= cos
    xp = bool(np.any(dhi >= co - 1e-12))
    # Y: (u - v) + sin <= 0  i.e.  (v - u) >= sin
    yp = bool(np.any(-dlo >= si - 1e-12))
    # degenerate faces at th = 0 (X test becomes v <= u) / th = 90 (Y: u <= v)
    if b.th0 <= 1e-9:
        xp = xp or bool(dhi >= -1e-12)
    if b.th1 >= 90.0 - 1e-9:
        yp = yp or bool(-dlo >= -1e-12)
    # D: some pose with (u-v) < cos and (v-u) < sin
    dp = bool(np.any((dlo < co - 1e-12) & (-dhi < si - 1e-12)))
    return xp, yp, dp


def zone_boxes(b, e):
    """union-of-boxes zone for retreat direction e in {'x','y'}, corner frame."""
    xs = np.linspace(b.x0, b.x1, SUB + 1)
    ys = np.linspace(b.y0, b.y1, SUB + 1)
    ts = np.linspace(b.th0, b.th1, SUB + 1)
    out = []
    for a in range(SUB):
        for c in range(SUB):
            for k in range(SUB):
                th = np.linspace(ts[k], ts[k + 1], 9)
                co = np.cos(np.radians(th))
                si = np.sin(np.radians(th))
                W = float(np.max(co + si)) / 2.0
                Dm = float(np.max(np.abs(co - si))) / 2.0
                if e == 'x':
                    out.append((xs[a] - Dm, xs[a + 1] + W, ys[c] - W, ys[c + 1] + W))
                else:
                    out.append((xs[a] - W, xs[a + 1] + W, ys[c] - Dm, ys[c + 1] + W))
    return out


def box_box_dist(p, q):
    dx = max(0.0, p[0] - q[1], q[0] - p[1])
    dy = max(0.0, p[2] - q[3], q[2] - p[3])
    return math.hypot(dx, dy)


def zone_box_dist(zone, q):
    return min(box_box_dist(z, q) for z in zone)


# ------------------------------------------------------------------ the node sample
def load_sample(nmax=None):
    R = json.load(open(os.path.join(RES, 'a85_reach_BL.json')))
    rows = [r for r in R['variants']['sigma_closed_7']['rows'] if r['sound']]
    boxes = [Box.from_json(r['box']) for r in rows]
    W = alive84.load_witnesses('k0_00')
    keys = sorted(W)
    MASK = {c: [G85.drop_masks(G85.map_box(b, c), W) for b in boxes] for c in CORNERS}
    CCORE = {c: [G85.map_box(b, c).core() for b in boxes] for c in CORNERS}
    surv = [tuple(p) for p in
            json.load(open(os.path.join(RES, 'realise85.pairs.json')))['surviving']]
    rnd = random.Random(SEED)
    counts = dict(attemptable=0, unkillable=0, contradictory=0)
    att = []
    for _ in range(NSAMPLE):
        node = {c: surv[rnd.randrange(len(surv))] for c in CORNERS}
        bx = [(c, k) for c in CORNERS for k in node[c]]
        contra = False
        for u in range(len(bx)):
            for v in range(u + 1, len(bx)):
                (cu, iu), (cv, iv) = bx[u], bx[v]
                if cu == cv:
                    continue
                if cores_meet(CCORE[cu][iu], CCORE[cv][iv]):
                    contra = True
                    break
            if contra:
                break
        if contra:
            counts['contradictory'] += 1
            continue
        st, k, _ = G85.verdict([MASK[c][i] for (c, i) in bx], BUDGET, keys)
        counts[st] += 1
        if st == 'attemptable':
            att.append({c: list(node[c]) for c in CORNERS})
    if nmax and len(att) > nmax:
        att = att[:nmax]
    return boxes, CCORE, att, counts


# ------------------------------------------------------------------ free-square grid
GX = np.linspace(0.5, S0 - 0.5, NGRID)
GXX, GYY = np.meshgrid(GX, GX, indexing='ij')
GXX = GXX.ravel()
GYY = GYY.ravel()
GDELTA = float(GX[1] - GX[0]) * math.sqrt(0.5)      # half grid diagonal


def grid_zone_reach(zone_c):
    """boolean over the grid: a unit square centred there can meet the zone."""
    ok = np.zeros(GXX.shape, dtype=bool)
    for (x0, x1, y0, y1) in zone_c:
        dx = np.maximum(0.0, np.maximum(x0 - GXX, GXX - x1))
        dy = np.maximum(0.0, np.maximum(y0 - GYY, GYY - y1))
        ok |= (dx * dx + dy * dy) <= (R_REACH + GDELTA) ** 2
    return ok


def grid_allowed(cores):
    ok = np.ones(GXX.shape, dtype=bool)
    for cr in cores:
        kx, ky, a = float(cr.kx), float(cr.ky), float(cr.a)
        r = a + 0.5 - GDELTA
        if r <= 0:
            continue
        ok &= ((GXX - kx) ** 2 + (GYY - ky) ** 2) >= r * r
    return ok


# ------------------------------------------------------------------ counting
_PC16 = np.array([bin(i).count('1') for i in range(1 << 16)], dtype=np.int64)


def _zeta(F, n):
    for i in range(n):
        a = F.reshape(F.shape[0], 1 << (n - 1 - i), 2, 1 << i)
        a[:, :, 1, :] += a[:, :, 0, :]
    return F


def _mobius(F, n):
    for i in range(n):
        a = F.reshape(F.shape[0], 1 << (n - 1 - i), 2, 1 << i)
        a[:, :, 1, :] -= a[:, :, 0, :]
    return F


def _ranked(f, n):
    F = np.zeros((n + 1, 1 << n), dtype=np.float64)
    pc = _PC16[:1 << n]
    F[pc, np.arange(1 << n)] = f
    return _zeta(F, n)


def _rankmul(A, B, n):
    C = np.zeros_like(A)
    for k in range(n + 1):
        for i in range(k + 1):
            C[k] += A[i] * B[k - i]
    return C


def count_assignments(a_z, feas_mask_bool, nz):
    """#assignments = (h * h * h * A)[full] under disjoint (subset) convolution."""
    N = 1 << nz
    A = np.ones(N, dtype=np.float64)
    for z in range(nz):
        idx = np.arange(N)
        A[(idx >> z) & 1 == 1] *= float(a_z[z])
    h = feas_mask_bool.astype(np.float64)
    Rh = _ranked(h, nz)
    RA = _ranked(A, nz)
    R = _rankmul(_rankmul(_rankmul(Rh, Rh, nz), Rh, nz), RA, nz)
    _mobius(R, nz)
    return float(R[nz][N - 1])


def free_family(bitsets, nz):
    """downward-closed boolean array over subsets of the nz zones (grid-nonempty)."""
    N = 1 << nz
    ok = np.zeros(N, dtype=bool)
    ok[0] = True
    cur = {0: bitsets['ALL']}
    while cur:
        nxt = {}
        for m, v in cur.items():
            top = m.bit_length()
            for z in range(top, nz):
                w = v & bitsets[z]
                if w:
                    mm = m | (1 << z)
                    ok[mm] = True
                    nxt[mm] = w
        cur = nxt
    return ok


def exists_assignment(a_z, feas, nz):
    need = [z for z in range(nz) if a_z[z] == 0]
    if not need:
        return True
    if len(need) > 12:
        return False
    for asg in itertools.product(range(3), repeat=len(need)):
        blocks = [0, 0, 0]
        for z, f in zip(need, asg):
            blocks[f] |= 1 << z
        if all(feas[b] for b in blocks):
            return True
    return False


# ------------------------------------------------------------------ per-node gate
def analyse_node(node, boxes, CCORE):
    intr = [(c, k) for c in CORNERS for k in node[c]]
    cores = [CCORE[c][k] for (c, k) in intr]
    cbox = [G85.map_box(boxes[k], c) for (c, k) in intr]
    cbox_xy = [(b.x0, b.x1, b.y0, b.y1) for b in cbox]
    types = [possible_types(boxes[k]) for (c, k) in intr]

    zones = []
    for (c, k) in intr:
        zones.append({e: [box_to_container(c, q) for q in zone_boxes(boxes[k], e)]
                      for e in ('x', 'y')})

    ZL = [(i, e) for i in range(8) for e in ('x', 'y')]
    sup = [[j for j in range(8) if j != i
            and zone_box_dist(zones[i][e], cbox_xy[j]) <= R_REACH + 1e-12]
           for (i, e) in ZL]

    allowed = grid_allowed(cores)
    aidx = np.flatnonzero(allowed)
    nall = int(aidx.size)
    BS = {}
    for zi, (i, e) in enumerate(ZL):
        r = grid_zone_reach(zones[i][e])[aidx]
        BS[zi] = int.from_bytes(np.packbits(r).tobytes(), 'big') if nall else 0
    BS['ALL'] = (1 << (8 * ((nall + 7) // 8))) - 1 if nall else 0

    opts = []
    for (xp, yp, dp) in types:
        o = []
        if xp:
            o.append(('x',))
        if yp:
            o.append(('y',))
        if not o:
            o.append(('x', 'y'))
        opts.append(o)

    def zidx(i, e):
        return 2 * i + (0 if e == 'x' else 1)

    any_feasible = False
    tuples = list(itertools.product(*opts))
    for tup in tuples:
        sel = [zidx(i, e) for i, t in enumerate(tup) for e in t]
        a_z = [len(sup[z]) for z in sel]
        if all(v > 0 for v in a_z):
            any_feasible = True
            break
        nz = len(sel)
        bs = {k: BS[z] for k, z in enumerate(sel)}
        bs['ALL'] = BS['ALL']
        feas = free_family(bs, nz)
        if exists_assignment(a_z, feas, nz):
            any_feasible = True
            break

    # canonical tuple for the count: per intruder the minimal option with the most
    # intruder suppliers (ties -> e_x); documented in the notes.
    ctup = []
    for i, o in enumerate(opts):
        ctup.append(max(o, key=lambda t: (sum(len(sup[zidx(i, e)]) for e in t), t == ('x',))))
    sel = [zidx(i, e) for i, t in enumerate(ctup) for e in t]
    a_z = [len(sup[z]) for z in sel]
    nz = len(sel)
    bs = {k: BS[z] for k, z in enumerate(sel)}
    bs['ALL'] = BS['ALL']
    feas = free_family(bs, nz)
    n_assign = count_assignments(a_z, feas, nz)

    return dict(node={c: list(node[c]) for c in CORNERS},
                types=[('X' if t[0] else '') + ('Y' if t[1] else '')
                       + ('D' if t[2] else '') for t in types],
                chosen=[''.join(t) for t in ctup],
                n_option_tuples=len(tuples),
                n_zones=nz, a_z=a_z, min_a_z=int(min(a_z)),
                n_zones_without_intruder_supplier=int(sum(1 for v in a_z if v == 0)),
                n_free_feasible_singletons=int(sum(1 for z in range(nz) if feas[1 << z])),
                n_free_feasible_subsets=int(feas.sum()),
                n_allowed_free_cells=nall,
                feasible=bool(any_feasible),
                n_assignments=n_assign)


# ------------------------------------------------------------------ resolution sensitivity
def shrink(b, lam):
    """box shrunk by lam about its centre (NOT a cover for lam < 1: diagnostic only)."""
    mx, my = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
    mt = 0.5 * (b.th0 + b.th1)
    return Box(mx + lam * (b.x0 - mx), mx + lam * (b.x1 - mx),
               my + lam * (b.y0 - my), my + lam * (b.y1 - my),
               mt + lam * (b.th0 - mt), mt + lam * (b.th1 - mt))


def sens_node(node, boxes, CCORE, lam):
    """[NOT SOUND for lam < 1] how many required zones lose every intruder supplier."""
    intr = [(c, k) for c in CORNERS for k in node[c]]
    sb = [shrink(boxes[k], lam) for (c, k) in intr]
    cbox = [G85.map_box(b, c) for b, (c, k) in zip(sb, intr)]
    cbox_xy = [(b.x0, b.x1, b.y0, b.y1) for b in cbox]
    types = [possible_types(b) for b in sb]
    zones = [{e: [box_to_container(c, q) for q in zone_boxes(b, e)] for e in ('x', 'y')}
             for b, (c, k) in zip(sb, intr)]
    opts = []
    for (xp, yp, dp) in types:
        o = []
        if xp:
            o.append(('x',))
        if yp:
            o.append(('y',))
        if not o:
            o.append(('x', 'y'))
        opts.append(o)
    best_bad = None
    for tup in itertools.product(*opts):
        bad = 0
        for i, t in enumerate(tup):
            for e in t:
                if not any(j != i and zone_box_dist(zones[i][e], cbox_xy[j])
                           <= R_REACH + 1e-12 for j in range(8)):
                    bad += 1
        best_bad = bad if best_bad is None else min(best_bad, bad)
        if best_bad == 0:
            break
    return best_bad


# ------------------------------------------------------------------ Trump canary
def trump_canary():
    X, s = atlas85.trump_placements()
    n = len(X)
    # TL corner frame: (x, y) -> (x, s - y); tilt -> (90 - th) mod 90
    def to_TL(cx, cy, th):
        return cx, s - cy, (90.0 - math.degrees(th) % 90.0) % 90.0

    out = dict(s=float(s), squares=[])
    tl = {}
    for q in (4, 6):
        u, v, th = to_TL(float(X[q][0]), float(X[q][1]), float(X[q][2]))
        co, si = math.cos(math.radians(th)), math.sin(math.radians(th))
        VLy_m_VLx = (v - u) + co
        VBx_m_VBy = (u - v) + si
        if VLy_m_VLx <= 1e-12 or (th <= 1e-9 and v - u <= 1e-12):
            typ, dirs = 'X', ('x',)
        elif VBx_m_VBy <= 1e-12 or (th >= 90 - 1e-9 and u - v <= 1e-12):
            typ, dirs = 'Y', ('y',)
        else:
            typ, dirs = 'D', ('x', 'y')
        W = (co + si) / 2.0
        Dm = abs(co - si) / 2.0
        z = {}
        z['x'] = [(u - Dm, u + W, v - W, v + W)]
        z['y'] = [(u - W, u + W, v - Dm, v + W)]
        tl[q] = dict(uv=(u, v), th=th, typ=typ, dirs=dirs, zone=z)
        out['squares'].append(dict(sq=q, TL_frame_centre=[u, v], TL_frame_tilt_deg=th,
                                   lemma_K_type=typ, required_dirs=list(dirs)))
    # suppliers: the other 9 squares at their exact poses (TL frame centres)
    others = [i for i in range(n) if i not in (4, 6)]
    sup_all = {}
    for q in (4, 6):
        for e in tl[q]['dirs']:
            zc = tl[q]['zone'][e]
            s_int = []
            for j in list(others) + [6 if q == 4 else 4]:
                u2, v2, _ = to_TL(float(X[j][0]), float(X[j][1]), float(X[j][2]))
                if zone_box_dist(zc, (u2, u2, v2, v2)) <= R_REACH + 1e-12:
                    s_int.append(j)
            sup_all['%d_%s' % (q, e)] = s_int
    ok = all(len(v) > 0 for v in sup_all.values())
    out['suppliers'] = sup_all
    out['expected_lockers_3_7_8_present'] = {k: sorted(set(v) & {3, 7, 8})
                                             for k, v in sup_all.items()}
    out['n_assignments_at_least_one'] = bool(ok)
    out['PASS'] = bool(ok)
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nmax', type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()

    can = trump_canary()
    print('canary Trump TL:', json.dumps({k: can[k] for k in
                                          ('suppliers', 'PASS')}), flush=True)
    assert can['PASS'], 'CANARY FAIL: Trump TL has a zone with no supplier'

    boxes, CCORE, att, counts = load_sample(a.nmax or None)
    print('sample %s ; attemptable used %d' % (json.dumps(counts), len(att)), flush=True)
    assert counts == dict(attemptable=128, unkillable=5, contradictory=867), \
        'sample does not reproduce realise85 part3_gate: %s' % counts

    recs = []
    fh = open(os.path.join(RES, 'supply85.zones.jsonl'), 'w')
    for m, node in enumerate(att):
        r = analyse_node(node, boxes, CCORE)
        recs.append(r)
        fh.write(json.dumps(r) + '\n')
        if m % 10 == 0:
            print('  %d/%d  %.0fs  killed so far %d'
                  % (m, len(att), time.time() - t0,
                     sum(1 for q in recs if not q['feasible'])), flush=True)
    fh.close()

    sens = {}
    for lam in (1.0, 0.5, 0.25, 0.0):
        bad = [sens_node(node, boxes, CCORE, lam) for node in att]
        sens['lambda=%.2f' % lam] = dict(
            n_nodes_with_an_unsuppliable_zone=sum(1 for v in bad if v > 0),
            fraction=sum(1 for v in bad if v > 0) / float(len(att)),
            total_unsuppliable_zones=sum(bad))
        print('  sens lambda %.2f -> %s' % (lam, json.dumps(sens['lambda=%.2f' % lam])),
              flush=True)

    killed = [r for r in recs if not r['feasible']]
    cnts = [r['n_assignments'] for r in recs if r['feasible'] and r['n_assignments'] is not None]
    logs = [math.log10(c) for c in cnts if c > 0]
    hist = {}
    for c in cnts:
        k = '0' if c == 0 else ('1e%d' % int(math.floor(math.log10(c))))
        hist[k] = hist.get(k, 0) + 1
    minaz = {}
    for r in recs:
        minaz[str(r['min_a_z'])] = minaz.get(str(r['min_a_z']), 0) + 1
    nz_hist = {}
    for r in recs:
        nz_hist[str(r['n_zones'])] = nz_hist.get(str(r['n_zones']), 0) + 1
    ty = {}
    for r in recs:
        for t in r['types']:
            ty[t] = ty.get(t, 0) + 1

    res = dict(
        attempt='A85 chore supply85: A91 s.9 supply gate on the attemptable four-corner samples',
        seconds=round(time.time() - t0, 1),
        sample=counts, n_attemptable_used=len(att),
        headline=dict(
            n_zero_assignment=len(killed),
            fraction_zero=len(killed) / float(max(1, len(recs))),
            a85_attemptable_fraction_sound=0.128),
        count_distribution=dict(histogram_by_decade=hist,
                                min=(min(cnts) if cnts else None),
                                max=(max(cnts) if cnts else None),
                                median_log10=(float(np.median(logs)) if logs else None)),
        n_zones_histogram=nz_hist,
        lemma_K_type_multiset=ty,
        zones_without_intruder_supplier=dict(
            n_nodes_with_any=sum(1 for r in recs
                                 if r['n_zones_without_intruder_supplier'] > 0),
            total=sum(r['n_zones_without_intruder_supplier'] for r in recs)),
        min_intruder_supplier_count_histogram=minaz,
        free_square_stats=dict(
            median_allowed_grid_cells=float(np.median([r['n_allowed_free_cells']
                                                       for r in recs])),
            n_nodes_with_no_allowed_free_cell=sum(1 for r in recs
                                                  if r['n_allowed_free_cells'] == 0),
            median_free_feasible_subsets=float(np.median(
                [r['n_free_feasible_subsets'] for r in recs]))),
        n_option_tuples_histogram={str(k): sum(1 for r in recs
                                               if r['n_option_tuples'] == k)
                                   for k in sorted({r['n_option_tuples']
                                                    for r in recs})},
        box_resolution_sensitivity=dict(
            note=('DIAGNOSTIC ONLY -- lambda < 1 shrinks each pose box about its '
                  'centre and is NOT a sound cover; it measures how much of the '
                  'gate\'s vacuity is A85 box width (0.15 in x,y, 7-14 deg in theta) '
                  'rather than geometry.  Counted: nodes with a required zone that '
                  'NO other intruder can reach, minimised over option tuples.'),
            data=sens),
        canary_trump_TL=can,
        model=dict(reach_radius=R_REACH, sub=SUB, ngrid=NGRID,
                   grid_delta=GDELTA, seed=SEED))
    json.dump(res, open(os.path.join(RES, 'supply85.json'), 'w'), indent=1, default=float)
    print(json.dumps({k: res[k] for k in ('headline', 'count_distribution',
                                          'n_zones_histogram', 'lemma_K_type_multiset',
                                          'zones_without_intruder_supplier',
                                          'min_intruder_supplier_count_histogram',
                                          'free_square_stats',
                                          'n_option_tuples_histogram',
                                          'box_resolution_sensitivity', 'seconds')}, indent=1,
                     default=float))


if __name__ == '__main__':
    main()
