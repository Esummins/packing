"""d2front87.py -- A87 chore: the SECOND-intruder frontier D2*(sigma) INSIDE A85's
sigma-closed 4-corner cover, plus the exact per-pair d2 ceiling of the BL census.

Why d2 and not d1.  deepfront87 established that the DEEPEST intruder d1 is
uninformative for the PI conjecture ("corners cannot all be deep and still be
bridged"): d1 = 1 - eps is bought by a near-slot axis-aligned square at ANY side
where the four gadgets fit, and the analytic trade d2 <~ eps^2/4 means d1 -> 1
costs the second intruder quadratically.  The substantive variable is therefore

    D2 := min_c d2(c),   d2(c) = depth of the SECOND deepest intruder at corner c,
    depth = 1 - f_min_max in the corner frame (A89 t2b_depth / depthdist87).

Known frontier (deepfront87, free-space gadget seeds): D2 = 0.293 at sigma 4.599
(saturating the one-corner ceiling 1 - 1/sqrt2), 0.125 at sigma 4.200, and NO
K0-BLOCKED packing constructible below sigma ~ 3.985.  The gap (s_hat, 4.00) is a
PACKING barrier, not a depth one, so this module replaces the free-space seeds
with A85's enumerated corner pairs at side ~ s0.

Two independent deliverables.

(A) The D2 ascent inside the A85 4-corner nodes.  a85_gate_samples.json stores
    only 200 of its 1000 sampled c4 nodes (30 attemptable), but gate85.r3's RNG
    stream is replayed here EXACTLY (verified against the 200 stored records) and
    the 1000 nodes are re-classified with gate85's own fast gate, recovering all
    179 attemptable nodes.  Per node: seed the 8 corner blockers from the node's
    four box pairs (box centres, or the pair's max-d2 witness = the disjoint grid
    pose pair maximising min(depth_A, depth_B)), add 3 rejection-sampled middles,
    compress the side with k0dir87's K0-confined flow, and run deepfront87's
    soft-min d2 ascent at each cap in {4.00, 3.95, 3.90, s_hat}.  Every reported
    number is deepfront87.certify's exact certificate: rational z, interval SAT
    gaps > 0, certified n_block, outward-rounded depth enclosures.

(B) The pair-census cut (cheap, exact, no search).  For every box of the 644
    sound BL cover boxes, depth_ub(box) = 1 - min_box f_min_max is a SOUND upper
    bound on the depth of any square placed in it, hence on d2 if that square is
    the shallower of the corner's two intruders; for a PAIR it is
    d2_ub(i,j) = min(depth_ub(i), depth_ub(j)) -- "the max d2 this pair box can
    host".  The distribution of d2_ub over the 33656 surviving level-2 pairs says
    what a hypothesis "d2 < delta at some corner" would cut from the census.

Canary: Trump's TL 2-crowd (squares 4 / 6, d1 = 0.168321, d2 = 0.155475).  Trump
is K0-FREE overall, so it enters only as a per-corner check: the same depth code
must reproduce those two numbers, the TL poses must be located in the BL cover,
and the located pair's d2_ub must be >= 0.155475 (soundness of the box bound).

One process, BLAS pinned, OMP_NUM_THREADS=1.  Writes only
results/d2front87.* , notes/d2front87.md , logs/d2front87.*.
Usage: python d2front87.py {selftest|canary|nodes|census|run|report|all}
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import random
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A87, '..'))
A85 = os.path.join(ATT, 'A85-k0-route')
A89 = os.path.join(ATT, 'A89-tilt-floor')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A85, 'code'))
sys.path.insert(0, os.path.join(A89, 'code'))

import cp85                       # noqa: E402
import deepfront87 as DF          # noqa: E402
import depthdist87 as DD          # noqa: E402
import fjpolish87 as F            # noqa: E402
import k0dir87 as K               # noqa: E402
import t2b_reach as TB            # noqa: E402

RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
LOGS = os.path.join(A87, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

OUT_NODES = os.path.join(RESULTS, 'd2front87.nodes.json')
OUT_CENSUS = os.path.join(RESULTS, 'd2front87.census.json')
OUT_JL = os.path.join(RESULTS, 'd2front87.jsonl')
OUT_JS = os.path.join(RESULTS, 'd2front87.json')
OUT_CAN = os.path.join(RESULTS, 'd2front87.canary.json')
OUT_REAL = os.path.join(RESULTS, 'd2front87.realize.json')
OUT_MD = os.path.join(NOTES, 'd2front87.md')
LOG_RUN = os.path.join(LOGS, 'd2front87.run.log')

N = 11
H = 0.5
S_HAT = F.S_HAT
CORNERS = K.CORNERS                     # ('BL','BR','TL','TR') -- k0dir87 order
G_CORNERS = ('BL', 'BR', 'TR', 'TL')    # gate85 order (node dict keys)
CAPS = (4.00, 3.95, 3.90, S_HAT)
REF_CAPS = (4.60, 4.40, 4.20, 4.10, 4.05)   # reference rows above the barrier
DELTAS_CUT = (0.05, 0.10, 0.20)
CEIL = 1.0 - 1.0 / math.sqrt(2.0)       # 0.29289321881345254
SEED = 20260903

# seed-side ladder: the 8 corner squares + 3 middles need room before compression
SS0 = (4.30, 4.50, 4.80, 5.20, 5.50, 6.00, 6.60)   # SMALLEST first: a tight
#      seed compresses; a 6.6 seed can be stuck at 6.6 (the flow cannot move it)
CMP_ROUNDS = 84
POSE_MODES = ('wit', 'centre', 'jit')


def _log_to(path):
    fh = open(path, 'a')

    def log(*a):
        m = ' '.join(str(v) for v in a)
        print(m, flush=True)
        fh.write(m + '\n')
        fh.flush()
    return log, fh


# ================================================== A85 boxes and their d2 ceiling

_BOXES = None


def boxes():
    global _BOXES
    if _BOXES is None:
        _R, _V, _rows, bx = TB.load_boxes()
        _BOXES = bx
    return _BOXES


_UB = None


def depth_ub():
    """SOUND per-box upper bound on the depth of any square in the box.

    f_min_max(cx, cy, th) is nondecreasing in cx and cy (translating a square
    away from the corner cannot lower min max(x,y)), so its minimum over the box
    is at (x0, y0); in theta it is 1/sqrt2-Lipschitz, so a dense theta scan minus
    half a step times the Lipschitz constant is a valid lower bound.  Identical
    to depthdist87.box_depth_ubs (used there for the d1 bound)."""
    global _UB
    if _UB is None:
        ub, _n = DD.box_depth_ubs()
        _UB = np.asarray(ub, float)
    return _UB


def surviving_pairs():
    d = json.load(open(os.path.join(A85, 'results', 'a85_pairs_BL.json')))
    return [(p['i'], p['j']) for p in d['surviving_level2']]


# ============================================ the 1000 c4 nodes, all 179 attemptable

def c4_nodes(log=print):
    """Replay gate85.r3's RNG stream to recover all 1000 sampled 4-corner nodes,
    re-classify them with gate85's own fast gate, and return the attemptable set.

    The replay is VERIFIED against the 200 nodes the file does store: the stream
    is Random(8501), then rnd.sample(pairs, 200) for the gate validation, then
    300 two-corner, 300 three-corner and 1000 four-corner draws (4 randrange per
    four-corner node, in gate85's corner order)."""
    import gate85 as G
    from caselp import Box
    from pinguard import cores_meet
    import tree85 as T
    import alive84

    t0 = time.time()
    pairs = surviving_pairs()
    g = json.load(open(os.path.join(A85, 'results', 'a85_gate_samples.json')))
    stored = g['sample_records']['c4']

    rnd = random.Random(8501)
    rnd.sample(pairs, 200)
    for cs, n in ((['BL', 'TR'], 300), (['BL', 'BR', 'TR'], 300)):
        for _ in range(n):
            {c: pairs[rnd.randrange(len(pairs))] for c in cs}
    nodes = [{c: pairs[rnd.randrange(len(pairs))] for c in G.CORNERS}
             for _ in range(1000)]
    replay_ok = all(all(list(nodes[k][c]) == stored[k]['node'][c]
                        for c in G.CORNERS) for k in range(len(stored)))
    if not replay_ok:
        raise RuntimeError('gate85 RNG replay does not reproduce the stored nodes')

    T.setup('k0_00')
    W = alive84.load_witnesses('k0_00')
    keys = sorted(W)
    R = json.load(open(os.path.join(A85, 'results', 'a85_reach_BL.json')))
    rows = [r for r in R['variants']['sigma_closed_7']['rows'] if r['sound']]
    bx = [Box.from_json(r['box']) for r in rows]
    MASK = {c: [G.drop_masks(G.map_box(b, c), W) for b in bx] for c in G.CORNERS}
    CCORE = {c: [G.map_box(b, c).core() for b in bx] for c in G.CORNERS}

    out = []
    counts = {'attemptable': 0, 'unkillable': 0, 'contradictory': 0}
    for nd in nodes:
        bl = [(c, k) for c in G.CORNERS for k in nd[c]]
        contra = False
        for u in range(len(bl)):
            for v in range(u + 1, len(bl)):
                (cu, iu), (cv, iv) = bl[u], bl[v]
                if cu == cv:
                    continue
                if cores_meet(CCORE[cu][iu], CCORE[cv][iv]):
                    contra = True
                    break
            if contra:
                break
        if contra:
            counts['contradictory'] += 1
            st = 'contradictory'
        else:
            st, _k, _per = G.verdict([MASK[c][i] for (c, i) in bl], 3, keys)
            counts[st] += 1
        out.append({'node': {c: list(nd[c]) for c in G.CORNERS}, 'state': st})

    att = [r for r in out if r['state'] == 'attemptable']
    stored_att = [r for r in stored if r['state'] == 'attemptable']
    res = {'replay_verified_against_stored': bool(replay_ok),
           'n_stored_records': len(stored),
           'n_nodes': len(out), 'counts': counts,
           'file_counts': g['sample_4corner']['counts'],
           'n_attemptable': len(att), 'n_attemptable_stored': len(stored_att),
           'attemptable': [r['node'] for r in att],
           'attemptable_is_stored': [
               bool(any(all(list(r['node'][c]) == s['node'][c]
                            for c in G.CORNERS) for s in stored_att))
               for r in att],
           'secs': time.time() - t0}
    json.dump(res, open(OUT_NODES, 'w'), indent=1)
    log('c4 nodes: %s ; %d attemptable (%d of them among the 200 stored); %.0fs'
        % (counts, len(att), sum(res['attemptable_is_stored']), res['secs']))
    return res


# ============================================================ node seeding

def box_grid(b, nx=7, ny=7, nt=9):
    """float pose grid of a BL box, restricted to poses that fit in the corner
    (cx, cy >= h) and MEET the open unit slot (f_min_max < 1)."""
    xs = np.linspace(b.x0, b.x1, nx)
    ys = np.linspace(b.y0, b.y1, ny)
    ts = np.linspace(math.radians(b.th0), math.radians(b.th1), nt)
    CX, CY, TH = [v.ravel() for v in np.meshgrid(xs, ys, ts, indexing='ij')]
    h = TB.hval(TH)
    fm = TB.f_minmax_np(TB.verts_np(CX, CY, TH))
    keep = (CX >= h) & (CY >= h) & (fm < 1.0)
    return CX[keep], CY[keep], TH[keep], fm[keep]


_WIT = {}
GRID_NX = GRID_NY = 11
GRID_NT = 15
CHUNK = 400


def pair_witness_d2(i, j, transpose=False, nx=GRID_NX, ny=GRID_NY, nt=GRID_NT):
    """The pair's MAX-d2 witness: the disjoint grid pose pair (A in box i, B in
    box j), both INSIDE the corner (cx, cy >= h) and both meeting the OPEN unit
    slot (f_min_max < 1), MINIMISING max(f_min_max(A), f_min_max(B)) -- i.e.
    maximising min(depth_A, depth_B), which is exactly the d2 the pair hosts.

    Returns (A, B, d2_float) or None.  None is a GRID verdict, not a proof: it
    says no pose pair on the 11 x 11 x 15 grid is realizable, so realizability
    counts built on it are LOWER bounds on the realizable fraction.  (A85's pair
    census is a prune of a pair hypothesis in which the CONTAINER WALLS play no
    part -- k0dir87's own note -- so an unrealizable surviving pair is expected,
    not a contradiction.)"""
    key = (i, j, transpose, nx, ny, nt)
    if key in _WIT:
        return _WIT[key]
    bs = boxes()
    ax, ay, at, af = box_grid(bs[i], nx, ny, nt)
    bx_, by_, bt, bf = box_grid(bs[j], nx, ny, nt)
    got = None
    if len(af) and len(bf):
        best = None
        for u0 in range(0, len(af), CHUNK):
            sl = slice(u0, u0 + CHUNK)
            g = TB.sat_gap(ax[sl, None], ay[sl, None], at[sl, None],
                           bx_[None, :], by_[None, :], bt[None, :])
            w = np.maximum(af[sl, None], bf[None, :])
            w = np.where(g >= 1e-9, w, np.inf)
            k = int(np.argmin(w))
            u, v = k // w.shape[1], k % w.shape[1]
            if np.isfinite(w[u, v]) and (best is None or w[u, v] < best[0]):
                best = (float(w[u, v]), u0 + u, v)
        if best is not None:
            _wv, u, v = best
            A = (float(ax[u]), float(ay[u]), float(at[u]))
            B = (float(bx_[v]), float(by_[v]), float(bt[v]))
            got = (A, B, float(1.0 - _wv))
    if got is not None and transpose:
        A, B, d = got
        got = ((A[1], A[0], K.HALFPI - A[2]), (B[1], B[0], K.HALFPI - B[2]), d)
    if len(_WIT) < 200000:
        _WIT[key] = got
    return got


def realizable(i, j):
    return pair_witness_d2(i, j) is not None


def _centre_pose(b):
    return (0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1),
            math.radians(0.5 * (b.th0 + b.th1)))


MARG = 2e-6      # inset from the two near walls: the max-d2 witness usually sits
#                  EXACTLY on a wall (cx = h), and cp85's feasibility asks for a
#                  STRICT container margin, so the seed needs a nudge inward.


def corner_pair_poses(i, j, mode, rng, transpose):
    """(A, B) BL-frame poses for a corner from its cover-box pair, inset by MARG
    from the two near walls."""
    bs = boxes()
    if mode == 'wit':
        w = pair_witness_d2(i, j, transpose)
        if w is None:
            return None
        return tuple((P[0] + MARG, P[1] + MARG, P[2]) for P in (w[0], w[1]))
    if mode == 'centre':
        A, B = _centre_pose(bs[i]), _centre_pose(bs[j])
    else:                                    # 'jit': uniform draw inside the box
        A = (rng.uniform(bs[i].x0, bs[i].x1), rng.uniform(bs[i].y0, bs[i].y1),
             math.radians(rng.uniform(bs[i].th0, bs[i].th1)))
        B = (rng.uniform(bs[j].x0, bs[j].x1), rng.uniform(bs[j].y0, bs[j].y1),
             math.radians(rng.uniform(bs[j].th0, bs[j].th1)))
    if transpose:
        A = (A[1], A[0], K.HALFPI - A[2])
        B = (B[1], B[0], K.HALFPI - B[2])
    A = (A[0] + MARG, A[1] + MARG, A[2])
    B = (B[0] + MARG, B[1] + MARG, B[2])
    for P in (A, B):
        if not (K._meets_unit_slot(*P) and K._inside_corner(*P)):
            return None
    if not K._pair_disjoint((A[0], A[1]), A[2], (B[0], B[1]), B[2]):
        return None
    return A, B


def node_seed(node, sigma, mode, rng, tries=900, transposes=None):
    """11 squares in [0, sigma]^2: the node's 4 corner box pairs (8 blockers,
    every one meeting its corner's open unit slot) + 3 rejection middles."""
    tp = transposes if transposes is not None else tuple(
        rng.random() < 0.5 for _ in range(4))
    cs, ts = [], []
    for ci, cn in enumerate(CORNERS):
        i, j = node[cn]
        pp = corner_pair_poses(i, j, mode, rng, tp[ci])
        if pp is None:
            return None
        for (cx, cy, t) in pp:
            X, Y, T_ = K._corner_map(cn, cx, cy, t, sigma)
            cs.append([X, Y])
            ts.append(T_)
    for u in range(8):
        for v in range(u + 1, 8):
            if u // 2 == v // 2:
                continue
            if not K._pair_disjoint((cs[u][0], cs[u][1]), ts[u],
                                    (cs[v][0], cs[v][1]), ts[v]):
                return None
    for _k in range(3):
        got = False
        for _t in range(tries):
            T_ = rng.uniform(0.0, K.HALFPI)
            e = H * (abs(math.cos(T_)) + abs(math.sin(T_))) + 1e-7
            X = rng.uniform(e, sigma - e)
            Y = rng.uniform(e, sigma - e)
            if all(K._pair_disjoint((X, Y), T_, (cs[q][0], cs[q][1]), ts[q])
                   for q in range(len(cs))):
                cs.append([X, Y])
                ts.append(T_)
                got = True
                break
        if not got:
            return None
    x = cp85.pack(np.array(cs), np.array(ts), float(sigma))
    return x if DF.ok_point(x) else None


def seed_node(node, rng, log=None, ntry_jit=6):
    """First seed that works, over pose mode x seed side (then jittered)."""
    for mode in POSE_MODES:
        reps = ntry_jit if mode == 'jit' else 10
        for _r in range(reps):
            for ss in SS0:
                x = node_seed(node, ss, mode, rng)
                if x is not None:
                    return x, mode, ss
    return None, None, None


# ============================== realizability of a cover pair as a CONCRETE pair

def realize_scan(npairs=6000, seed=SEED, log=print):
    """How many surviving BL cover pairs admit a CONCRETE realizable pair -- two
    disjoint unit squares, both inside the container corner and both meeting the
    open unit slot?  (A85's prune never saw the container walls.)  Grid verdict,
    so the counts are LOWER bounds."""
    t0 = time.time()
    pr = surviving_pairs()
    rng = random.Random(seed)
    idx = (list(range(len(pr))) if npairs is None or npairs >= len(pr)
           else rng.sample(range(len(pr)), npairs))
    good = []
    for k in idx:
        i, j = pr[k]
        w = pair_witness_d2(i, j)
        if w is not None:
            good.append({'i': i, 'j': j, 'd2_witness': w[2]})
    d2 = [g['d2_witness'] for g in good]
    ub = np.minimum(depth_ub(), 1.0)
    res = {'n_pairs_total': len(pr), 'n_scanned': len(idx),
           'n_realizable': len(good),
           'frac_realizable_lower_bound': len(good) / len(idx),
           'grid': [GRID_NX, GRID_NY, GRID_NT],
           'd2_witness': {'min': min(d2), 'median': float(np.median(d2)),
                          'mean': float(np.mean(d2)), 'max': max(d2)} if d2 else None,
           'd2_witness_vs_box_bound': {
               'max_excess_over_d2_ub': max(
                   (g['d2_witness'] - min(ub[g['i']], ub[g['j']])
                    for g in good), default=None)},
           'frac_witness_lt': {('%.2f' % d): float(np.mean([v < d for v in d2]))
                               for d in DELTAS_CUT} if d2 else None,
           'realizable_pairs': [[g['i'], g['j'], g['d2_witness']] for g in good],
           'secs': time.time() - t0}
    json.dump(res, open(OUT_REAL, 'w'), indent=1)
    log('realize: %d / %d scanned pairs realizable (>= %.4f of the census); '
        'witness d2 median %s; %.0fs'
        % (len(good), len(idx), res['frac_realizable_lower_bound'],
           None if not d2 else '%.4f' % float(np.median(d2)), res['secs']))
    return res


# =========================================== gate85's fast 4-corner node verdict

_GATE = None


def gate_fn(log=print):
    """classify(node) -> 'attemptable' | 'unkillable' | 'contradictory', using
    gate85's own precomputed drop masks and core-meet test (budget 3)."""
    global _GATE
    if _GATE is None:
        t0 = time.time()
        import gate85 as G
        from caselp import Box
        from pinguard import cores_meet
        import tree85 as T
        import alive84
        T.setup('k0_00')
        W = alive84.load_witnesses('k0_00')
        keys = sorted(W)
        R = json.load(open(os.path.join(A85, 'results', 'a85_reach_BL.json')))
        rows = [r for r in R['variants']['sigma_closed_7']['rows'] if r['sound']]
        bx = [Box.from_json(r['box']) for r in rows]
        MASK = {c: [G.drop_masks(G.map_box(b, c), W) for b in bx]
                for c in G_CORNERS}
        CCORE = {c: [G.map_box(b, c).core() for b in bx] for c in G_CORNERS}

        def classify(node):
            bl = [(c, k) for c in G_CORNERS for k in node[c]]
            for u in range(len(bl)):
                for v in range(u + 1, len(bl)):
                    (cu, iu), (cv, iv) = bl[u], bl[v]
                    if cu == cv:
                        continue
                    if cores_meet(CCORE[cu][iu], CCORE[cv][iv]):
                        return 'contradictory'
            st, _k, _p = G.verdict([MASK[c][i] for (c, i) in bl], 3, keys)
            return st
        _GATE = classify
        log('gate masks built (%.0fs)' % (time.time() - t0))
    return _GATE


def pool_nodes(nwant=120, seed=SEED, log=print, npairs=6000):
    """ARM 2.  The 179 sampled nodes draw their four corner pairs blind, so a node
    is realizable only if all four of its pairs are -- an event of probability
    ~ (realizable fraction)^4.  This arm therefore SYNTHESISES 4-corner nodes from
    the REALIZABLE pairs only, and classifies each with gate85's own fast gate, so
    the D2 ascent runs on nodes that are simultaneously (a) inside A85's
    sigma-closed cover, (b) attemptable at budget 3, and (c) concretely
    realizable at all four corners."""
    rl = (json.load(open(OUT_REAL)) if os.path.exists(OUT_REAL)
          else realize_scan(npairs=npairs, seed=seed, log=log))
    pool = [(int(a), int(b)) for (a, b, _d) in rl['realizable_pairs']]
    cls = gate_fn(log)
    rng = random.Random(seed + 1)
    counts = {'attemptable': 0, 'unkillable': 0, 'contradictory': 0}
    out = []
    tries = 0
    tmax = 400000
    while len(out) < nwant and tries < tmax:
        tries += 1
        node = {c: pool[rng.randrange(len(pool))] for c in G_CORNERS}
        st = cls(node)
        counts[st] += 1
        if st == 'attemptable':
            out.append(node)
    log('pool nodes: %d attemptable found in %d draws from %d realizable pairs; '
        'draw states %s' % (len(out), tries, len(pool), counts))
    return out, {'n_draws': tries, 'draw_states': counts,
                 'n_realizable_pairs': len(pool)}


# ============================================================ per-node pipeline

def in_box_check(x, node):
    """Diagnostic: are the two deepest intruders of each corner still inside the
    node's cover boxes (mod the D4 corner map)?  The ascent does NOT constrain
    them, so this records how far the answer drifted from the cover."""
    dt, _ca = DF.depth_table(x)
    c, th, s = cp85.unpack(x)
    bs = boxes()
    out = {}
    for ci, cn in enumerate(CORNERS):
        order = np.argsort(-dt[ci])[:2]
        i, j = node[cn]
        inb = []
        for q in order:
            cx, cy, t = float(c[q, 0]), float(c[q, 1]), float(th[q])
            # invert the corner map back to the BL frame
            bxp, byp, btp = K._corner_map(cn, cx, cy, t, float(s))
            hit = False
            for k in (i, j):
                b = bs[k]
                for (u, v, w) in ((bxp, byp, btp), (byp, bxp, K.HALFPI - btp)):
                    wd = math.degrees(w) % 90.0
                    if (b.x0 - 1e-9 <= u <= b.x1 + 1e-9
                            and b.y0 - 1e-9 <= v <= b.y1 + 1e-9
                            and b.th0 - 1e-6 <= wd <= b.th1 + 1e-6):
                        hit = True
            inb.append(bool(hit))
        out[cn] = inb
    return out


def node_run(tag, node, rng, caps, log, cert_side_row=True):
    """Seed -> compress (barrier measurement) -> d2 ascent at each cap."""
    t0 = time.time()
    rec = {'tag': tag, 'node': {c: list(node[c]) for c in G_CORNERS}}
    x0, mode, ss = seed_node(node, rng)
    if x0 is None:
        rec.update(status='seed_fail', secs=time.time() - t0)
        return rec, []
    rec.update(status='ok', pose_mode=mode, seed_side=ss,
               D2_seed=DF.score(x0, 'd2'), D1_seed=DF.score(x0, 'd1'))
    rows = []
    # --- BARRIER arm: push the side as low as the K0-confined flow can take it,
    #     then raise d2 THERE (the honest low-sigma point of this node)
    xc, side = DF.compress(x0, S_HAT, rounds=CMP_ROUNDS)
    xc = DF.to_container(xc)
    if not DF.ok_point(xc):
        xc, side = x0, float(K.enclosing_side_x(x0))
    rec['min_side_reached'] = float(side)
    rec['s_after_compress'] = float(xc[3 * N])
    if cert_side_row:
        own = math.nextafter(float(xc[3 * N]), math.inf)
        xa, sa, ns = DF.ascend(xc, own, 'd2')
        if xa is not None:
            r = DF._row(own, xa, sa, ns)
            r['kind'] = 'own_side'
            rows.append(r)
            xc = xa
        # continue the ladder from the compressed point too
        st = [k for k in range(len(caps)) if caps[k] >= float(xc[3 * N]) - 1e-12]
        if st:
            for r in DF.ladder(xc, 'd2', caps[st[0]:], log=None):
                r['kind'] = 'cap'
                rows.append(r)
    # --- DEPTH-FIRST arm: raise d2 at the SEED side first, then walk the caps
    #     down at a held depth floor (deepfront87's squeeze); the two arms enter
    #     different basins, and the deep one is what the frontier is about.
    xd, sd, nd_ = DF.ascend(x0, math.nextafter(float(x0[3 * N]), math.inf), 'd2')
    if xd is not None:
        rec['D2_at_seed_side'] = float(sd)
        st = [k for k in range(len(caps)) if caps[k] >= float(xd[3 * N]) - 1e-12]
        if st:
            for r in DF.ladder(xd, 'd2', caps[st[0]:], log=None):
                r['kind'] = 'cap'
                rows.append(r)
    # --- ANCHORED arm: a directed anchored search from this node's best rows
    if rows:
        seen = set()
        for src in sorted(rows, key=lambda r: -r['score'])[:2]:
            cp = float(src['cap'])
            if cp in seen:
                continue
            seen.add(cp)
            xa, sa, ns = anchored_ascent(np.array(src['x'], float), cp, rng)
            if xa is not None:
                r = DF._row(cp, xa, sa, ns)
                r['kind'] = 'anchored'
                r['from'] = src['kind']
                rows.append(r)
    rec['n_anchored_rows'] = sum(1 for r in rows if r['kind'] == 'anchored')
    rec['best_D2_anchored'] = max((r['score'] for r in rows
                                   if r['kind'] == 'anchored'), default=None)
    rec['n_cap_rows'] = sum(1 for r in rows if r['kind'] == 'cap')
    rec['caps_reached'] = [r['cap'] for r in rows if r['kind'] == 'cap']
    rec['best_D2_own'] = max((r['score'] for r in rows), default=None)
    rec['secs'] = time.time() - t0
    log('  %s %-6s seed s=%.3f -> min_side %.6f  D2 %s  caps %s  (%.0fs)'
        % (tag, mode, ss, side,
           ('%.6f' % rec['best_D2_own']) if rec['best_D2_own'] is not None else '--',
           ['%.4f' % v for v in rec['caps_reached']], rec['secs']))
    return rec, rows


# ================================== ANCHORING: A90's retreat test on EVERY intruder
# The PI's objection: the raw frontier measures ghosts.  A near-slot gadget (one
# square parked eps off its slot, the partner dipping a single vertex into the
# sliver) is a legal K0-BLOCKED packing but not a Psi-minimal minimiser -- the
# partner can rotate back toward flush and lift out at CONSTANT side, so its
# intrusion is not held by anything.  A candidate is ANCHORED here iff EVERY
# intruder of EVERY corner fails A90's RETREATABLE test (no constant-side cardinal
# translation of the intruder, or of its retreat cluster, reduces its intrusion --
# t3_90.analyse_square, verbatim), and in addition the SHALLOWER intruder of each
# corner has no constant-side rotation TOWARD FLUSH about one of its own contacts
# that reduces its depth while keeping the packing feasible.
#
# A90's res_of() applies RETREATABLE only to NON-DEEPEST intruders (that is what
# RES(z) needs); here it is applied to every intruder, as instructed.

_A90 = None


def a90():
    global _A90
    if _A90 is None:
        sys.path.insert(0, os.path.join(ATT, 'A90-nocrit-blocked', 'code'))
        import t3_90 as A90T
        _A90 = A90T
    return _A90


ROT_STEPS = (3e-3, 3e-4, 3e-5)


def rot_toward_flush_free(x, Q, cn, C, TH, s, cst, rows):
    """Is there a constant-side rotation of square Q TOWARD FLUSH, about one of
    its own active contact points, that strictly reduces Q's depth at corner cn
    while keeping the whole packing feasible?  (The PI's 'rotate back to flush and
    lift out' motion.)  Returns (free, witness)."""
    A = a90()
    dl = A.signed_tilt(TH[Q])
    if abs(dl) < 1e-12:
        return False, None          # already flush: no rotation toward flush
    sgn = -1.0 if dl > 0 else 1.0   # rotate back toward the nearest 90k
    fr = cst[cn]['frame']
    d0 = float(cst[cn]['depth'][Q])
    pts = [np.asarray(r['pt'], float) for r in rows]
    pts.append(np.asarray(C[Q], float))          # spin in place as well
    for P in pts:
        for st in ROT_STEPS:
            ang = sgn * st
            ca, sa = math.cos(ang), math.sin(ang)
            v = np.asarray(C[Q], float) - P
            c2 = P + np.array([ca * v[0] - sa * v[1], sa * v[0] + ca * v[1]])
            C2 = C.copy()
            TH2 = TH.copy()
            C2[Q] = c2
            TH2[Q] = TH[Q] + ang
            x2 = cp85.pack(C2, TH2, s)
            ov, cv = cp85.feasibility(x2)
            if ov > -1e-12 or cv > -1e-12:
                continue            # the motion breaks feasibility: not free
            # the corner FRAME is held fixed at the unmoved packing's tight bbox:
            # a constant-side motion of one square cannot enlarge the bbox here
            # (the motion is feasible, so every square stays in [0, s]^2), and
            # holding the frame is the conservative choice for "did it retreat".
            dnew = float(A.depth_arg(A.verts(C2[Q], TH2[Q]), fr)[0])
            if dnew < d0 - 1e-12:
                return True, {'about': [float(P[0]), float(P[1])],
                              'angle': float(ang), 'depth_before': d0,
                              'depth_after': dnew}
    return False, None


def anchored_report(x, want_clusters=True):
    """Per-intruder A90 retreat analysis of a candidate; ANCHORED iff nothing
    retreats."""
    A = a90()
    C, TH, s = A.unpack_x(x)
    bbox = A.tight_bbox_of(C, TH)
    cst = A.corner_state(C, TH, bbox)
    pcs = A.all_pair_contacts(C, TH)
    wcs = A.wall_contacts(C, TH, s)
    out = {'per_corner': {}, 'n_intruders': 0, 'n_retreatable': 0,
           'n_rot_free': 0}
    for cn in A.CORNERS:
        intr = list(cst[cn]['intruders'])
        rec = {'n_block': int(cst[cn]['n_block']), 'intruders': []}
        if len(intr) >= 2:
            dep = [float(cst[cn]['depth'][q]) for q in intr]
            shallow = intr[int(np.argmin(dep))]
            for Q in intr:
                a = A.analyse_square(Q, cn, C, TH, s, bbox, cst, pcs, wcs,
                                     want_clusters=want_clusters)
                rows = A.contacts_on(Q, pcs, wcs)
                item = {'sq': int(Q), 'depth': a['depth'],
                        'tilt_deg': a['tilt'],
                        'RETREATABLE': bool(a.get('RETREATABLE')),
                        'cardinals': a.get('cardinals'),
                        'n_contacts': a['n_contacts'],
                        'LOCKED': bool(a.get('LOCKED')),
                        'is_shallower': bool(Q == shallow)}
                if want_clusters and a.get('clusters'):
                    item['blocking_contacts'] = {
                        lbl: {'cluster_size': cl['size'],
                              'wall_anchored': cl['wall_anchored'],
                              'wall_hits': cl['wall_hits'],
                              'intruder_anchored': cl['intruder_anchored'],
                              'intruder_hits': cl['intruder_hits'],
                              'blocking': [q['other'] for q in cl['sides']
                                           if q['blocking']],
                              'free': cl['free']}
                        for lbl, cl in a['clusters'].items()}
                if Q == shallow:
                    fr_, wit = rot_toward_flush_free(x, Q, cn, C, TH, s, cst,
                                                     rows)
                    item['rot_toward_flush_free'] = bool(fr_)
                    item['rot_witness'] = wit
                    if fr_:
                        out['n_rot_free'] += 1
                out['n_intruders'] += 1
                if item['RETREATABLE']:
                    out['n_retreatable'] += 1
                rec['intruders'].append(item)
        out['per_corner'][cn] = rec
    out['ANCHORED'] = bool(out['n_intruders'] >= 8 and out['n_retreatable'] == 0
                           and out['n_rot_free'] == 0)
    return out


def is_anchored(x):
    try:
        return bool(anchored_report(x, want_clusters=True)['ANCHORED'])
    except Exception:                                    # noqa: BLE001
        return False


def anchored_ascent(x0, cap, rng, tries=140, rounds=16, wall=22.0):
    """DIRECTED anchored search: find an anchored feasible point near x0 at this
    cap (random probe, since ANCHORED is a discrete predicate and the ladder's
    optima are typically ghosts), then ascend d2 accepting only anchored steps.

    This is the practical stand-in for carrying retreat-blocking as a constraint
    in the ascent: the retreat predicate is combinatorial (which contact blocks
    which cardinal), so it is enforced as an ACCEPTANCE TEST on every step rather
    than as a smooth row.  Every point this returns is anchored by construction."""
    t0 = time.time()
    x = np.asarray(x0, float).copy()
    start = x if (DF.ok_point(x) and is_anchored(x)) else None
    if start is None:
        for t in range(tries):
            if time.time() - t0 > 0.5 * wall:
                break
            st = (1e-2, 3e-3, 1e-3, 3e-4)[t % 4]
            y = x + np.array([rng.gauss(0.0, st) for _ in range(3 * N + 1)])
            y[3 * N] = min(float(y[3 * N]), cap)
            if DF.ok_point(y) and is_anchored(y):
                start = y
                break
    if start is None:
        return None, None, 0
    xb = start
    cur = DF.score(xb, 'd2')
    best = (cur, xb.copy())
    delta = DF.TRUST0
    ns = 0
    for r in range(rounds):
        if delta < DF.TRUST_MIN or time.time() - t0 > wall:
            break
        u = r / max(1, rounds - 1)
        beta = DF.BETA0 * (DF.BETA1 / DF.BETA0) ** u
        dt, ca = DF.depth_table(xb)
        tg = DF.pick_targets(dt, 'd2')
        cd = [ca[ci, jj] for (ci, jj) in tg]
        y = DF.asc_step(xb, tg, cd, beta, beta, delta, cap, True)
        if (y is None or not DF.ok_point(y) or not is_anchored(y)
                or DF.score(y, 'd2') <= cur + 1e-13):
            delta *= 0.4
            continue
        xb = y
        cur = DF.score(y, 'd2')
        ns += 1
        if cur > best[0]:
            best = (cur, xb.copy())
        delta = min(DF.TRUST0, delta * 1.7)
    return best[1], best[0], ns


def certify_d2(x):
    cert = DF.certify(x)
    cert['VERIFIED_D2'] = bool(cert.get('disjoint_certified')
                               and cert.get('K0_BLOCKED_certified')
                               and cert.get('n_unknown') == 0
                               and cert.get('depth_clean')
                               and cert.get('D2_min_d2_lo') is not None)
    return cert


# ==================================================================== campaign

def run(nnodes=None, wall=7000.0, seed=SEED, ncert=2, log=print, caps=CAPS,
        ref_caps=REF_CAPS, npool=140):
    t0 = time.time()
    nd = (json.load(open(OUT_NODES)) if os.path.exists(OUT_NODES)
          else c4_nodes(log=log))
    sampled = [{c: tuple(v) for c, v in n.items()} for n in nd['attemptable']]

    # --- ARM 1: the 179 SAMPLED attemptable nodes, per-corner realizability
    real4 = []
    per_corner_real = []
    for k, n in enumerate(sampled):
        r = [bool(pair_witness_d2(*n[c])) for c in G_CORNERS]
        per_corner_real.append(r)
        if all(r):
            real4.append(k)
    nreal_hist = {str(q): int(sum(1 for r in per_corner_real if sum(r) == q))
                  for q in range(5)}
    log('arm 1: %d / %d sampled attemptable nodes are realizable at ALL FOUR '
        'corners; per-node realizable-corner histogram %s'
        % (len(real4), len(sampled), nreal_hist))

    # --- ARM 2: nodes synthesised from the REALIZABLE pairs, gate-classified
    pool, poolmeta = pool_nodes(nwant=npool, seed=seed, log=log)

    att = [(('s%03d' % k), sampled[k]) for k in real4] + \
          [(('p%03d' % k), n) for k, n in enumerate(pool)]
    rng = random.Random(seed)
    order = list(range(len(att)))
    rng.shuffle(order)
    if nnodes is not None:
        order = order[:nnodes]
    allcaps = tuple(sorted(set(caps) | set(ref_caps), reverse=True))
    bycap = {c: [] for c in allcaps}
    own_rows = []
    recs = []
    nfail = 0
    log('run: %d attemptable nodes, caps %s, wall %.0fs'
        % (len(order), ['%.6f' % c for c in allcaps], wall))
    with open(OUT_JL, 'w') as fh:
        for q, k in enumerate(order):
            if time.time() - t0 > wall:
                log('wall reached after %d nodes' % q)
                break
            tag, nodek = att[k]
            try:
                rec, rows = node_run(tag, nodek, rng, allcaps, log)
            except Exception as ex:                      # noqa: BLE001
                rec, rows = {'tag': tag, 'status': 'error',
                             'error': repr(ex)[:220]}, []
                log('  %s ERROR %s' % (tag, rec['error']))
            recs.append(rec)
            if rec.get('status') != 'ok':
                nfail += 1
            for r in rows:
                if (r['kind'] == 'own_side'
                        or (r['kind'] == 'anchored'
                            and r.get('from') == 'own_side')):
                    own_rows.append((tag, r))
                else:                     # 'cap' and 'anchored' rows share a cap
                    bycap.setdefault(r['cap'], []).append((tag, r))
            fh.write(json.dumps({'rec': rec,
                                 'rows': [{kk: vv for kk, vv in r.items()
                                           if kk != 'x'} for r in rows]}) + '\n')
            fh.flush()
            if (q + 1) % 10 == 0:
                log('[%5.0fs] %d/%d nodes; min_side min %.6f; per-cap n %s'
                    % (time.time() - t0, q + 1, len(order),
                       min((r['min_side_reached'] for r in recs
                            if 'min_side_reached' in r), default=float('nan')),
                       {('%.4f' % c): len(bycap[c]) for c in allcaps}))
    secs_search = time.time() - t0

    res = {'mode': 'd2', 'seed': seed, 'caps': list(allcaps),
           'requested_caps': list(caps), 'reference_caps': list(ref_caps),
           's_hat': S_HAT, 'one_corner_ceiling': CEIL,
           'n_nodes_attempted': len(recs), 'n_attemptable_total': len(att),
           'n_seed_or_error_fail': nfail, 'secs_search': secs_search,
           'arm1': {'n_sampled_attemptable': len(sampled),
                    'n_realizable_all4': len(real4),
                    'realizable_corner_histogram': nreal_hist,
                    'node_index_realizable_all4': real4},
           'arm2': poolmeta,
           'per_cap': {}, 'per_cap_anchored': {}, 'own_side': {},
           'own_side_anchored': {}, 'nodes': recs}

    # --- packing barrier: how many nodes get under each side at all
    sides = sorted(r['min_side_reached'] for r in recs if 'min_side_reached' in r)
    res['barrier'] = {
        'n_with_a_K0_BLOCKED_packing': len(sides),
        'min_side_min': sides[0] if sides else None,
        'min_side_median': float(np.median(sides)) if sides else None,
        'min_side_max': sides[-1] if sides else None,
        'n_under': {('%.6f' % c): int(sum(1 for v in sides if v <= c + 1e-12))
                    for c in allcaps},
        'hist': {}}
    for lo, hi in ((0, 3.90), (3.90, 3.95), (3.95, 4.00), (4.00, 4.05),
                   (4.05, 4.10), (4.10, 4.20), (4.20, 4.40), (4.40, 99.0)):
        res['barrier']['hist']['[%.2f,%.2f)' % (lo, hi)] = int(
            sum(1 for v in sides if lo <= v < hi))

    # --- exact certificates: top candidates per cap, plus the best own-side rows
    def cert_block(rows, label, anchored_only=False, scan=250):
        rows = sorted(rows, key=lambda tr: -tr[1]['score'])
        nscan = 0
        if anchored_only:
            keep = []
            for tag, r in rows[:scan]:
                nscan += 1
                if is_anchored(np.array(r['x'], float)):
                    keep.append((tag, r))
                    if len(keep) >= ncert:
                        break
            rows = keep
        entry = {'n': len(rows), 'anchored_only': bool(anchored_only),
                 'n_scanned_for_anchoring': nscan,
                 'best_float': rows[0][1]['score'] if rows else None,
                 'best_side_float': rows[0][1]['side'] if rows else None,
                 'best_tag': rows[0][0] if rows else None,
                 'candidates': []}
        for tag, r in rows[:ncert]:
            x = np.array(r['x'], float)
            try:
                c = certify_d2(x)
            except Exception as ex:                      # noqa: BLE001
                c = {'VERIFIED_D2': False, 'error': repr(ex)[:220]}
            c['tag'] = tag
            c['float_D2'] = r['score']
            c['float_side'] = r['side']
            c['float_d1'] = r['d1']
            c['float_d2'] = r['d2']
            try:
                c['in_cover_boxes'] = in_box_check(x, dict(att)[tag])
            except Exception:                            # noqa: BLE001
                c['in_cover_boxes'] = None
            try:
                c['anchoring'] = anchored_report(x)
            except Exception as ex:                      # noqa: BLE001
                c['anchoring'] = {'ANCHORED': False, 'error': repr(ex)[:200]}
            entry['candidates'].append(c)
            log('  %s %s D2_float %.6f -> certified D2 in [%s, %s], side <= %s,'
                ' n_block %s, VERIFIED %s, ANCHORED %s'
                % (label, tag, r['score'], c.get('D2_min_d2_lo'),
                   c.get('D2_min_d2_hi'), c.get('sigma_certified_upper'),
                   c.get('n_block_certified'), c.get('VERIFIED_D2'),
                   c['anchoring'].get('ANCHORED')))
        good = [q for q in entry['candidates'] if q.get('VERIFIED_D2')]
        if good:
            entry['best_certified'] = max(good, key=lambda q: q['D2_min_d2_lo'])
        return entry

    for c in allcaps:
        res['per_cap']['%.6f' % c] = cert_block(bycap[c], 'cap %.4f' % c)
        res['per_cap_anchored']['%.6f' % c] = cert_block(
            bycap[c], 'ANCH cap %.4f' % c, anchored_only=True)
    res['own_side'] = cert_block(own_rows, 'own-side')
    res['own_side_anchored'] = cert_block(own_rows, 'ANCH own-side',
                                          anchored_only=True)
    res['secs_total'] = time.time() - t0
    json.dump(res, open(OUT_JS, 'w'), indent=1, default=str)
    log('wrote %s (%.0f s)' % (OUT_JS, res['secs_total']))
    return res


# ================================================= (B) the pair-census d2 cut

def census(log=print):
    t0 = time.time()
    ub = np.minimum(depth_ub(), 1.0)
    pr = surviving_pairs()
    I = np.array([p[0] for p in pr])
    J = np.array([p[1] for p in pr])
    d2p = np.minimum(ub[I], ub[J])
    d1p = np.maximum(ub[I], ub[J])

    g = json.load(open(os.path.join(A85, 'results', 'a85_gate_samples.json')))
    ps = g['pair_states']
    pa = [(r['i'], r['j']) for r in ps if r['state'] == 'attemptable']
    Ia = np.array([p[0] for p in pa])
    Ja = np.array([p[1] for p in pa])
    d2a = np.minimum(ub[Ia], ub[Ja])

    def dist(v, name):
        v = np.asarray(v, float)
        return {'name': name, 'n': int(len(v)), 'min': float(v.min()),
                'max': float(v.max()), 'mean': float(v.mean()),
                'median': float(np.median(v)),
                'q': {p: float(np.quantile(v, p / 100.0))
                      for p in (1, 5, 10, 25, 50, 75, 90, 95, 99)},
                'frac_lt': {('%.2f' % d): float((v < d).mean())
                            for d in DELTAS_CUT},
                'n_lt': {('%.2f' % d): int((v < d).sum()) for d in DELTAS_CUT},
                'frac_le_0': float((v <= 0.0).mean()),
                'frac_ge_ceiling': float((v >= CEIL - 1e-12).mean())}

    hist_edges = [-1.0, 0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25, CEIL, 0.4,
                  0.6, 0.8, 1.01]

    def hist(v):
        v = np.asarray(v, float)
        return {'%.4g..%.4g' % (hist_edges[k], hist_edges[k + 1]):
                int(((v >= hist_edges[k]) & (v < hist_edges[k + 1])).sum())
                for k in range(len(hist_edges) - 1)}

    # --- node-level cut over the 1000 c4 nodes
    nd = json.load(open(OUT_NODES)) if os.path.exists(OUT_NODES) else None
    node_cut = None
    if nd is not None:
        att = nd['attemptable']
        mins = []
        for n in att:
            mins.append(min(min(ub[i], ub[j]) for (i, j) in
                            (tuple(n[c]) for c in G_CORNERS)))
        node_cut = {'n_attemptable_nodes': len(att),
                    'min_c_d2_ub': {'min': float(min(mins)),
                                    'median': float(np.median(mins)),
                                    'max': float(max(mins))},
                    'n_all4_can_host_d2_ge': {
                        ('%.2f' % d): int(sum(1 for v in mins if v >= d))
                        for d in DELTAS_CUT + (0.3,)},
                    'note': ('a node is CUT by "d2 < delta at some corner" iff '
                             'min_c d2_ub < delta, i.e. iff it is NOT counted '
                             'in n_all4_can_host_d2_ge[delta]')}

    # the REALIZABLE subset (both members admit a concrete in-container placement)
    rz = None
    if os.path.exists(OUT_REAL):
        rl = json.load(open(OUT_REAL))
        Ir = np.array([int(a) for (a, _b, _d) in rl['realizable_pairs']])
        Jr = np.array([int(b) for (_a, b, _d) in rl['realizable_pairs']])
        wd = np.array([float(d) for (_a, _b, d) in rl['realizable_pairs']])
        d2r = np.minimum(ub[Ir], ub[Jr])
        rz = {'d2_ub': dist(d2r, 'realizable surviving pairs: d2_ub'),
              'd2_ub_hist': None,
              'witness_d2': dist(wd, 'realizable surviving pairs: the d2 the '
                                     'grid witness ACHIEVES (a lower bound)'),
              'max_witness_excess_over_ub': float((wd - d2r).max())}

    res = {'n_sound_boxes': int(len(ub)),
           'one_corner_ceiling': CEIL,
           'realizable_subset': rz,
           'box_depth_ub': dist(ub, '644 sound BL boxes: depth_ub (= max d2 the '
                                    'box can host as the shallower member)'),
           'box_hist': hist(ub),
           'pair_d2_ub': dist(d2p, '33656 surviving level-2 BL pairs: '
                                   'd2_ub = min over the pair of depth_ub'),
           'pair_hist': hist(d2p),
           'pair_d1_ub': dist(d1p, 'same pairs: d1_ub = max over the pair'),
           'pair_attemptable_d2_ub': dist(
               d2a, 'attemptable BL pairs of the 2000-row pair_states census'),
           'pair_attemptable_hist': hist(d2a),
           'node_cut': node_cut,
           'secs': time.time() - t0}
    json.dump(res, open(OUT_CENSUS, 'w'), indent=1)
    log('census: boxes n=%d frac depth_ub < %s = %s' %
        (len(ub), list(res['box_depth_ub']['frac_lt'].keys()),
         list(res['box_depth_ub']['frac_lt'].values())))
    log('census: pairs n=%d frac d2_ub < %s = %s' %
        (len(d2p), list(res['pair_d2_ub']['frac_lt'].keys()),
         list(res['pair_d2_ub']['frac_lt'].values())))
    return res


# ==================================================================== canary

def canary(log=print):
    """Trump's TL 2-crowd through the same code: depth, and its location in the
    BL cover.  Trump is K0-FREE (BL/BR/TR each hold one flush slot square), so
    this is a PER-CORNER check only."""
    out = {}
    x = K.trump_x()
    dt, _ca = DF.depth_table(x)
    srt = np.sort(dt, axis=1)[:, ::-1]
    ti = CORNERS.index('TL')
    out['float_TL_d1'] = float(srt[ti, 0])
    out['float_TL_d2'] = float(srt[ti, 1])
    out['float_all_d1'] = [float(v) for v in srt[:, 0]]
    out['d1_ref'] = 0.16832098955
    out['d2_ref'] = 0.155475
    out['d1_err'] = abs(out['float_TL_d1'] - out['d1_ref'])
    out['d2_err'] = abs(out['float_TL_d2'] - out['d2_ref'])

    # locate the TL pair in the BL cover (map TL poses back to the BL frame)
    c, th, s = cp85.unpack(x)
    bs = boxes()
    ub = np.minimum(depth_ub(), 1.0)
    order = np.argsort(-dt[ti])[:2]
    loc = []
    for q in order:
        cx, cy, t = float(c[q, 0]), float(c[q, 1]), float(th[q])
        bxp, byp, btp = K._corner_map('TL', cx, cy, t, float(s))
        hits = []
        for k, b in enumerate(bs):
            for (u, v, w) in ((bxp, byp, btp), (byp, bxp, K.HALFPI - btp)):
                wd = math.degrees(w) % 90.0
                if (b.x0 - 1e-12 <= u <= b.x1 + 1e-12
                        and b.y0 - 1e-12 <= v <= b.y1 + 1e-12
                        and b.th0 - 1e-9 <= wd <= b.th1 + 1e-9):
                    hits.append(k)
        loc.append({'square': int(q), 'depth': float(dt[ti, q]),
                    'BL_pose': [bxp, byp, math.degrees(btp) % 90.0],
                    'boxes': sorted(set(hits)),
                    'depth_ub_of_boxes': [float(ub[k]) for k in sorted(set(hits))]})
    try:
        ar = anchored_report(x)
        tl = ar['per_corner']['TL']
        out['TL_anchoring'] = tl
        out['TL_both_intruders_non_retreatable'] = bool(
            tl['intruders'] and all(not it['RETREATABLE'] for it in tl['intruders']))
        out['TL_shallower_rotation_to_flush_free'] = bool(
            any(it.get('rot_toward_flush_free') for it in tl['intruders']))
    except Exception as ex:                              # noqa: BLE001
        out['TL_anchoring'] = {'error': repr(ex)[:200]}
    out['TL_located'] = loc
    both = all(l['boxes'] for l in loc)
    out['both_located_in_cover'] = bool(both)
    if both:
        d2ub = min(max(ub[k] for k in l['boxes']) for l in loc)
        out['d2_ub_of_located_pair'] = float(d2ub)
        out['box_bound_sound_on_trump'] = bool(d2ub >= out['float_TL_d2'] - 1e-12)
        out['slack'] = float(d2ub - out['float_TL_d2'])
    json.dump(out, open(OUT_CAN, 'w'), indent=1)
    log('canary Trump TL: d1 %.9f (err %.2e), d2 %.9f (err %.2e); located %s; '
        'd2_ub %s sound %s'
        % (out['float_TL_d1'], out['d1_err'], out['float_TL_d2'], out['d2_err'],
           out['both_located_in_cover'], out.get('d2_ub_of_located_pair'),
           out.get('box_bound_sound_on_trump')))
    return out


# ==================================================================== selftest

def selftest(log=print):
    ok = []

    def chk(name, cond, extra=''):
        ok.append((name, bool(cond), extra))
        log('%-52s %s %s' % (name, 'ok' if cond else 'FAIL', extra))

    bs = boxes()
    chk('644 sound BL boxes', len(bs) == 644, str(len(bs)))
    good, i, j = TB.verify_box_index(
        bs, os.path.join(A85, 'results', 'a85_pairs_BL.json'))
    chk('pair (i,j) address the SOUND box list', good, '%d,%d' % (i, j))

    ub = np.minimum(depth_ub(), 1.0)
    chk('depth_ub finite, <= 1', np.all(np.isfinite(ub)) and ub.max() <= 1.0,
        'max %.6f' % ub.max())

    # depth_ub is SOUND: a dense random sample inside a box never beats it
    rng = random.Random(11)
    worst = -9.0
    for k in rng.sample(range(len(bs)), 60):
        b = bs[k]
        cx = np.array([rng.uniform(b.x0, b.x1) for _ in range(400)])
        cy = np.array([rng.uniform(b.y0, b.y1) for _ in range(400)])
        tt = np.array([math.radians(rng.uniform(b.th0, b.th1)) for _ in range(400)])
        d = 1.0 - TB.f_minmax_np(TB.verts_np(cx, cy, tt))
        worst = max(worst, float(d.max() - ub[k]))
    chk('depth_ub sound vs 24000 in-box samples', worst <= 1e-9,
        'worst excess %.3e' % worst)

    # the max-d2 witness really is disjoint, in-slot, and hits its own d2
    pr = surviving_pairs()
    nw = 0
    bad = 0
    for (i2, j2) in [pr[k] for k in rng.sample(range(len(pr)), 40)]:
        w = pair_witness_d2(i2, j2)
        if w is None:
            continue
        nw += 1
        A, B, d = w
        f = TB.f_minmax_np(TB.verts_np(np.array([A[0], B[0]]),
                                       np.array([A[1], B[1]]),
                                       np.array([A[2], B[2]])))
        dj = K._pair_disjoint((A[0], A[1]), A[2], (B[0], B[1]), B[2])
        if not (dj and f.max() < 1.0 and abs((1.0 - f.max()) - d) < 1e-12
                and d <= min(ub[i2], ub[j2]) + 1e-9):
            bad += 1
    chk('max-d2 witnesses valid and <= the box bound', bad == 0 and nw > 0,
        '%d witnesses, %d bad' % (nw, bad))

    # the smooth score really is a LOWER bound (deepfront87's own invariant),
    # re-checked here on a node seed
    if os.path.exists(OUT_REAL):
        pn, _m = pool_nodes(nwant=4, log=lambda *a: None)
        got = None
        for node in pn:
            x, mode, ss = seed_node(node, random.Random(3))
            if x is not None:
                got = (x, mode, ss)
                break
        chk('a cover-node seed is feasible + K0-BLOCKED', got is not None,
            '' if got is None else 'mode %s, s=%.2f, D2=%.3e'
            % (got[1], got[2], DF.score(got[0], 'd2')))
        if got is not None:
            nb, _m1, _m2, blk = DF.k0_container(got[0])
            chk('node seed n_block >= 2 at all four corners',
                blk and nb.min() >= 2, str(nb.tolist()))
            # the smooth objective is an UPPER bound on f_min_max, so 1 - G is a
            # LOWER bound on the true score -- deepfront87's own invariant
            dt, ca = DF.depth_table(got[0])
            tg = DF.pick_targets(dt, 'd2')
            cd = [ca[ci, jj] for (ci, jj) in tg]
            Gv, _g = DF.obj_soft(got[0], tg, cd, 3000.0, 3000.0)
            chk('1 - G is a lower bound on the true D2',
                (1.0 - Gv) <= DF.score(got[0], 'd2') + 1e-12,
                '1-G = %.9f <= D2 = %.9f' % (1.0 - Gv, DF.score(got[0], 'd2')))
    chk('one-corner ceiling constant', abs(CEIL - 0.29289321881345254) < 1e-15)
    nb2 = sum(1 for _n, c, _e in ok if not c)
    log('selftest: %d checks, %d FAIL' % (len(ok), nb2))
    return ok


# ==================================================================== report

def _fmt(v, nd=9):
    if v is None:
        return '--'
    try:
        return '%.*f' % (nd, float(Fraction(v) if isinstance(v, str) else v))
    except Exception:                                    # noqa: BLE001
        return str(v)


def _sci(v):
    if v is None:
        return '--'
    try:
        return '%.2e' % float(Fraction(v) if isinstance(v, str) else v)
    except Exception:                                    # noqa: BLE001
        return str(v)


def report(log=print):
    res = json.load(open(OUT_JS))
    cen = json.load(open(OUT_CENSUS))
    can = json.load(open(OUT_CAN)) if os.path.exists(OUT_CAN) else {}
    nd = json.load(open(OUT_NODES))
    L = []

    def A(s=''):
        L.append(s)

    A('# A87 chore: the SECOND-intruder frontier D2*(sigma) inside A85\'s '
      '4-corner cover')
    A()
    A('`D2 = min_c d2(c)`, `d2(c)` = depth of the SECOND deepest intruder at '
      'corner c (depth = `1 - f_min_max` in the corner frame).  The deepest '
      'intruder `d1` is uninformative (deepfront87: a near-slot square buys '
      '`d1 = 1 - eps` at any side where the four gadgets fit, and the analytic '
      'trade is `d2 <~ eps^2/4`), so `d2` is the substantive variable for the '
      'PI conjecture.  Seeds here are A85\'s ENUMERATED corner pairs, not '
      'free-space gadgets.  Code `code/d2front87.py`.')
    A()
    A('## Frontier D2*(sigma) inside the A85 4-corner nodes')
    A()
    A('| cap sigma | nodes reaching the cap | best D2 (float) | certified D2 '
      'enclosure | certified sigma <= | min pair gap >= | n_block | '
      'EXTRAPOLATED |')
    A('| ---: | ---: | ---: | :--- | ---: | ---: | :--- | :--- |')
    caps = sorted((float(k) for k in res['per_cap']), reverse=True)
    for c in caps:
        e = res['per_cap']['%.6f' % c]
        b = e.get('best_certified')
        if b:
            A('| %.6f | %d | %.6f | [%s, %s] | %s | %s | %s | no (certified) |'
              % (c, e['n'], e['best_float'], _fmt(b['D2_min_d2_lo']),
                 _fmt(b['D2_min_d2_hi']), b['sigma_certified_upper'],
                 _sci(b['min_pair_gap_lower']), b['n_block_certified']))
        elif e['n']:
            A('| %.6f | %d | %.6f | NOT CERTIFIED | -- | -- | -- | no |'
              % (c, e['n'], e['best_float']))
        else:
            A('| %.6f | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- '
              '| **yes, unprobed** |' % c)
    e = res['own_side']
    b = e.get('best_certified')
    if b:
        A('| (own side) | %d | %.6f | [%s, %s] | %s | %s | %s | no (certified) |'
          % (e['n'], e['best_float'], _fmt(b['D2_min_d2_lo']),
             _fmt(b['D2_min_d2_hi']), b['sigma_certified_upper'],
             _sci(b['min_pair_gap_lower']), b['n_block_certified']))
    A()
    A('The `own side` row is the best D2 at whatever side the node\'s own '
      'K0-confined compression actually reached -- the honest low-sigma point of '
      'this run.  One-corner ceiling for reference: `1 - 1/sqrt2 = %.14f`.'
      % CEIL)
    A()
    A('### (b) ANCHORED-ONLY frontier')
    A()
    A('The raw table above measures ghosts.  A near-slot gadget -- one square '
      'parked eps off its slot, the partner dipping a single vertex into the '
      'sliver -- is a legal K0-BLOCKED packing but not a Psi-minimal minimiser: '
      'the partner can rotate back toward flush and lift out at CONSTANT side, so '
      'nothing holds its intrusion.  A candidate is ANCHORED here iff (i) EVERY '
      'intruder of EVERY corner fails A90\'s RETREATABLE test (no constant-side '
      'cardinal translation of the intruder, or of its retreat cluster, reduces '
      'its intrusion -- `t3_90.analyse_square`, verbatim; A90\'s own `res_of` '
      'applies it only to non-deepest intruders, here it is applied to all), and '
      '(ii) the SHALLOWER intruder of each corner has no constant-side rotation '
      'TOWARD FLUSH about one of its own active contacts (or in place) that '
      'reduces its depth while the whole packing stays feasible.  Same exact '
      'verification as (a).')
    A()
    A('| cap sigma | rows scanned | anchored found | best anchored D2 (float) | '
      'certified D2 enclosure | certified sigma <= | n_block | EXTRAPOLATED |')
    A('| ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |')
    pca = res.get('per_cap_anchored', {})
    for c in caps:
        e = pca.get('%.6f' % c, {})
        b = e.get('best_certified')
        if b:
            A('| %.6f | %d | %d | %.6f | [%s, %s] | %s | %s | no (certified) |'
              % (c, e.get('n_scanned_for_anchoring', 0), e['n'],
                 e['best_float'], _fmt(b['D2_min_d2_lo']),
                 _fmt(b['D2_min_d2_hi']), b['sigma_certified_upper'],
                 b['n_block_certified']))
        elif e.get('n'):
            A('| %.6f | %d | %d | %.6f | NOT CERTIFIED | -- | -- | no |'
              % (c, e.get('n_scanned_for_anchoring', 0), e['n'],
                 e['best_float']))
        elif e.get('n_scanned_for_anchoring'):
            A('| %.6f | %d | 0 | -- | NO ANCHORED CANDIDATE among the scanned '
              'rows | -- | -- | no |' % (c, e['n_scanned_for_anchoring']))
        else:
            A('| %.6f | 0 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- '
              '| **yes, unprobed** |' % c)
    ea = res.get('own_side_anchored', {})
    ba = ea.get('best_certified')
    if ba:
        A('| (own side) | %d | %d | %.6f | [%s, %s] | %s | %s | no (certified) |'
          % (ea.get('n_scanned_for_anchoring', 0), ea['n'], ea['best_float'],
             _fmt(ba['D2_min_d2_lo']), _fmt(ba['D2_min_d2_hi']),
             ba['sigma_certified_upper'], ba['n_block_certified']))
    elif ea.get('n_scanned_for_anchoring'):
        A('| (own side) | %d | 0 | -- | NO ANCHORED CANDIDATE among the scanned '
          'rows | -- | -- | no |' % ea['n_scanned_for_anchoring'])
    A()
    A('**Procedure caveat, stated plainly.**  The anchoring test is applied as a '
      'FILTER over the ladder rows in descending raw D2 (up to %d rows per cap), '
      'not as a constraint inside the ascent.  So row (b) is a certified LOWER '
      'bound on the anchored frontier and the raw row (a) an upper bound on it; '
      'an ascent that carried the retreat-blocking as a penalty could land '
      'between them.  A cap whose (b) cell says "NO ANCHORED CANDIDATE" is '
      'evidence that the raw optimum at that side is a ghost, not evidence that '
      'no anchored packing exists there.'
      % (pca.get('%.6f' % caps[0], {}).get('n_scanned_for_anchoring', 0) or 90))
    A()
    A('### Which contacts block each intruder of the best ANCHORED candidate')
    A()
    shown = 0
    for lab, e in ([('%.6f' % c, pca.get('%.6f' % c, {})) for c in caps]
                   + [('own side', ea)]):
        b = e.get('best_certified')
        if not b or not b.get('anchoring'):
            continue
        A('**%s** (tag %s, certified sigma <= %s):' % (lab, b.get('tag'),
                                                       b.get('sigma_certified_upper')))
        A()
        A('| corner | sq | depth | tilt (deg) | retreatable | e_x cluster: '
          'blocked by | e_y cluster: blocked by | shallower: rotation to flush '
          'free? |')
        A('| --- | ---: | ---: | ---: | :--- | :--- | :--- | :--- |')
        for cn in CORNERS:
            rc = b['anchoring']['per_corner'].get(cn, {})
            for it in rc.get('intruders', []):
                bc = it.get('blocking_contacts') or {}

                def blk(lbl, bc=bc):
                    q = bc.get(lbl)
                    if q is None:
                        return 'not a retreat direction'
                    bits = []
                    if q['wall_anchored']:
                        bits.append('wall %s' % q['wall_hits'])
                    if q['intruder_anchored']:
                        bits.append('intruder %s' % q['intruder_hits'])
                    if q['blocking']:
                        bits.append('sq %s' % q['blocking'])
                    return ('FREE' if q['free'] and not bits
                            else '; '.join(bits) or 'FREE')
                A('| %s | %d | %.9f | %.6f | %s | %s | %s | %s |'
                  % (cn, it['sq'], it['depth'], it['tilt_deg'],
                     'YES' if it['RETREATABLE'] else 'no',
                     blk('e_x'), blk('e_y'),
                     ('--' if not it.get('is_shallower')
                      else ('YES' if it.get('rot_toward_flush_free') else 'no'))))
        A()
        shown += 1
        if shown >= 2:
            break
    if not shown:
        A('No anchored candidate was certified, so there is nothing to report '
          'here.')
    A()
    A('## The barrier is upstream of packing: REALIZABILITY of a cover pair')
    A()
    rl = json.load(open(OUT_REAL)) if os.path.exists(OUT_REAL) else None
    if rl:
        A('A85\'s pair prune never saw the CONTAINER WALLS (k0dir87\'s own note), '
          'so a surviving cover pair need not admit an actual pair of disjoint '
          'unit squares that both fit inside the corner (`cx, cy >= h(theta)`) '
          'and both meet the open unit slot.  On a %d x %d x %d pose grid per '
          'box, **%d of %d** scanned surviving pairs do (>= %.4f of the census; '
          'a grid verdict, so this is a LOWER bound on the realizable fraction).  '
          'Witness d2 over the realizable pairs: min %.4f, median %.4f, max %.4f.'
          % (rl['grid'][0], rl['grid'][1], rl['grid'][2], rl['n_realizable'],
             rl['n_scanned'], rl['frac_realizable_lower_bound'],
             rl['d2_witness']['min'], rl['d2_witness']['median'],
             rl['d2_witness']['max']))
        A()
    a1 = res['arm1']
    A('The consequence for the SAMPLED 4-corner nodes is decisive: a node needs '
      'all FOUR of its independently drawn pairs realizable, and **%d of the %d '
      'attemptable nodes** clear that.  Realizable-corner histogram over the %d '
      'nodes: %s.'
      % (a1['n_realizable_all4'], a1['n_sampled_attemptable'],
         a1['n_sampled_attemptable'],
         ', '.join('%s corners: %d' % (k, v) for k, v in
                   sorted(a1['realizable_corner_histogram'].items()))))
    A()
    a2 = res['arm2']
    A('So the ascent is run on a second arm as well (ARM 2): 4-corner nodes '
      'SYNTHESISED from the realizable pairs only and then classified by '
      'gate85\'s own fast gate at budget 3.  Of %d such draws, %s -- i.e. the '
      'binding constraint on a realizable 4-corner node is core CONTRADICTION '
      '(two corners\' cover cores meeting), not the alive gate.'
      % (a2['n_draws'], json.dumps(a2['draw_states'])))
    A()
    A('## The packing barrier')
    A()
    bar = res['barrier']
    A('%d of %d attemptable 4-corner nodes were attempted; %d yielded a feasible '
      'K0-BLOCKED packing at all (seed + compression).  Minimum enclosing side '
      'reached, over those: min %s, median %s, max %s.'
      % (res['n_nodes_attempted'], res['n_attemptable_total'],
         bar['n_with_a_K0_BLOCKED_packing'], _fmt(bar['min_side_min'], 6),
         _fmt(bar['min_side_median'], 6), _fmt(bar['min_side_max'], 6)))
    A()
    A('| side threshold | nodes with a K0-BLOCKED packing at <= that side |')
    A('| ---: | ---: |')
    for k in sorted(bar['n_under'], key=lambda v: -float(v)):
        A('| %.6f | %d |' % (float(k), bar['n_under'][k]))
    A()
    A('| min-side bin | nodes |')
    A('| --- | ---: |')
    for k, v in bar['hist'].items():
        A('| %s | %d |' % (k, v))
    A()
    A('## Per-corner detail of the best certified configuration')
    A()
    A('| row | corner | n_block | d1 | tilt of d1 (deg) | d2 | tilt of d2 (deg) '
      '| still in its cover box? |')
    A('| --- | --- | ---: | ---: | ---: | ---: | ---: | :--- |')
    blocks = [('%.6f' % c, res['per_cap']['%.6f' % c]) for c in caps]
    blocks.append(('own side', res['own_side']))
    for lab, e in blocks:
        b = e.get('best_certified')
        if not b:
            continue
        for cn in CORNERS:
            p = b['per_corner'][cn]
            inb = (b.get('in_cover_boxes') or {}).get(cn)
            A('| %s | %s | %s | %s | %s | %s | %s | %s |'
              % (lab, cn, p.get('n_block_certified'),
                 _fmt(p.get('d1'), 9), _fmt(p.get('d1_tilt_deg'), 6),
                 _fmt(p.get('d2'), 9), _fmt(p.get('d2_tilt_deg'), 6),
                 ('--' if inb is None else ('%s / %s' % tuple(inb)))))
    A()
    A('## The pair-census cut: what "d2 < delta at some corner" would buy')
    A()
    bx = cen['box_depth_ub']
    A('Per BOX (the %d sound BL cover boxes).  `depth_ub(b) = 1 - min_b '
      'f_min_max` is a SOUND upper bound on the depth of any square placed in '
      'b, hence on `d2` when that square is the shallower of the corner\'s two '
      'intruders -- "the max d2 this box can host".'
      % cen['n_sound_boxes'])
    A()
    A('| statistic | boxes (n = %d) | surviving pairs (n = %d) | attemptable '
      'pairs (n = %d) |' % (bx['n'], cen['pair_d2_ub']['n'],
                            cen['pair_attemptable_d2_ub']['n']))
    A('| --- | ---: | ---: | ---: |')
    pp = cen['pair_d2_ub']
    pa = cen['pair_attemptable_d2_ub']
    for nm, key in (('min', 'min'), ('median', 'median'), ('mean', 'mean'),
                    ('max', 'max')):
        A('| %s | %.6f | %.6f | %.6f |' % (nm, bx[key], pp[key], pa[key]))
    for d in DELTAS_CUT:
        k = '%.2f' % d
        A('| fraction < %.2f | %.4f | %.4f | %.4f |'
          % (d, bx['frac_lt'][k], pp['frac_lt'][k], pa['frac_lt'][k]))
    for d in DELTAS_CUT:
        k = '%.2f' % d
        A('| count < %.2f | %d | %d | %d |'
          % (d, bx['n_lt'][k], pp['n_lt'][k], pa['n_lt'][k]))
    A('| fraction <= 0 (cannot meet the slot at all) | %.4f | %.4f | %.4f |'
      % (bx['frac_le_0'], pp['frac_le_0'], pa['frac_le_0']))
    A('| fraction >= the one-corner ceiling %.6f | %.4f | %.4f | %.4f |'
      % (CEIL, bx['frac_ge_ceiling'], pp['frac_ge_ceiling'],
         pa['frac_ge_ceiling']))
    A()
    A('`d2_ub(i,j) = min(depth_ub(i), depth_ub(j))` for a pair, because BOTH '
      'members must be deep for the SECOND intruder to be.  A pair with '
      '`d2_ub < delta` CANNOT host `d2 >= delta`, so a 4-corner node using it at '
      'any corner is settled for free by a "d2 < delta at some corner" '
      'hypothesis; the residual is the complement.')
    rz = cen.get('realizable_subset')
    if rz:
        A()
        A('Restricted to the REALIZABLE pairs (n = %d): `d2_ub` min %.6f, median '
          '%.6f, max %.6f, fraction < 0.05 / 0.10 / 0.20 = %.4f / %.4f / %.4f; '
          'and the grid witness ACHIEVES d2 with median %.6f, max %.6f (never '
          'above its box bound -- max excess %.2e), so for these pairs the '
          'ceiling and an attained value bracket the truth.'
          % (rz['d2_ub']['n'], rz['d2_ub']['min'], rz['d2_ub']['median'],
             rz['d2_ub']['max'], rz['d2_ub']['frac_lt']['0.05'],
             rz['d2_ub']['frac_lt']['0.10'], rz['d2_ub']['frac_lt']['0.20'],
             rz['witness_d2']['median'], rz['witness_d2']['max'],
             rz['max_witness_excess_over_ub']))
    A()
    A('| d2_ub bin | boxes | surviving pairs | attemptable pairs |')
    A('| --- | ---: | ---: | ---: |')
    for k in cen['pair_hist']:
        A('| %s | %d | %d | %d |' % (k, cen['box_hist'][k], cen['pair_hist'][k],
                                     cen['pair_attemptable_hist'][k]))
    A()
    nc = cen.get('node_cut')
    if nc:
        A('At NODE level (the %d attemptable 4-corner nodes): `min_c d2_ub` has '
          'min %.6f, median %.6f, max %.6f, and the number of nodes that could '
          'host `d2 >= delta` at ALL FOUR corners is'
          % (nc['n_attemptable_nodes'], nc['min_c_d2_ub']['min'],
             nc['min_c_d2_ub']['median'], nc['min_c_d2_ub']['max']))
        A()
        A('| delta | nodes that can host d2 >= delta at all 4 corners | cut by '
          '"d2 < delta somewhere" |')
        A('| ---: | ---: | ---: |')
        for k, v in nc['n_all4_can_host_d2_ge'].items():
            A('| %s | %d / %d | %d |' % (k, v, nc['n_attemptable_nodes'],
                                         nc['n_attemptable_nodes'] - v))
    A()
    A('## Node recovery')
    A()
    A('gate85 stores only %d of its %d sampled 4-corner nodes.  Its RNG stream '
      'is replayed here and VERIFIED against those %d stored records (exact '
      'match on every node), so all %d nodes were re-classified with gate85\'s '
      'own fast gate: %s -- recovering the full attemptable set (the file\'s own '
      'counts: %s).'
      % (nd['n_stored_records'], nd['n_nodes'], nd['n_stored_records'],
         nd['n_nodes'], json.dumps(nd['counts']),
         json.dumps(nd['file_counts'])))
    A()
    A('## Canary')
    A()
    if can:
        A('Trump\'s TL 2-crowd, same code path: `d1 = %.11f` (reference '
          '0.16832098955, |diff| %.2e), `d2 = %.9f` (reference 0.155475, '
          '|diff| %.2e).  Trump is K0-FREE overall (BL / BR / TR each hold one '
          'flush slot square, `d1 = 1`), so it enters only as a per-corner '
          'check.'
          % (can['float_TL_d1'], can['d1_err'], can['float_TL_d2'],
             can['d2_err']))
        A()
        if can.get('both_located_in_cover'):
            A('Both TL squares were located in the BL cover: '
              '`d2_ub` of the located pair = %.6f >= the actual `d2` = %.6f '
              '(slack %.6f), so the box bound is SOUND on Trump.  Boxes: %s.'
              % (can['d2_ub_of_located_pair'], can['float_TL_d2'],
                 can['slack'],
                 ', '.join(str(l['boxes']) for l in can['TL_located'])))
        else:
            A('NOT both TL squares fall in a sound cover box (the cover is a '
              'cover of the K0-PAIR hypothesis at s0, not of every 2-crowd), so '
              'only the depth half of the canary applies.  Located: %s.'
              % json.dumps([l['boxes'] for l in can['TL_located']]))
    A()
    A('## What this does and does not settle')
    A()
    reached = [c for c in caps if res['per_cap']['%.6f' % c]['n']]
    unreached = [c for c in caps if not res['per_cap']['%.6f' % c]['n']]
    A('* **Reached (certified).**  %s' % (
        ('caps %s' % ', '.join('%.6f' % c for c in reached)) if reached
        else 'NO requested cap was reached.'))
    A('* **Unreached (EXTRAPOLATED / unprobed).**  %s  Rows marked '
      '"**yes, unprobed**" above carry NO evidence: the obstruction is the '
      'PACKING barrier measured in the table above, not a depth ceiling, and '
      'nothing in this run licenses continuing the D2 curve into them.'
      % (('caps %s' % ', '.join('%.6f' % c for c in unreached)) if unreached
         else 'none.'))
    A('* **Sound in the opposite direction, at exactly s_hat.**  The pair-census '
      'cut above is an UPPER bound valid over the whole cover box, so every '
      '"cannot host" line in it EXCLUDES the corresponding d2, at the s_hat '
      'scale, with no search involved.')
    A()
    A('## Provenance')
    A()
    A('* %d nodes attempted of %d attemptable, seed %s, %.0f s search + '
      'certification (%.0f s total).  %d seed/error failures.'
      % (res['n_nodes_attempted'], res['n_attemptable_total'], res['seed'],
         res['secs_search'], res['secs_total'], res['n_seed_or_error_fail']))
    A('* Every certified row: rational z (`k0dir87.x_to_z` / `zfrac_of`), '
      'interval SAT gaps certified > 0 and side an outward interval UPPER bound '
      '(`fjpolish87.verify_exact`), blocker counts against the INNER rational '
      'slot rectangle (`k0dir87.exact_blocked_test`), depths as outward-rounded '
      'interval enclosures (`depthdist87.corner_depths`).')
    A('* Files: `results/d2front87.{json,jsonl,nodes.json,census.json,'
      'canary.json}`; log `logs/d2front87.run.log`.')
    A('* One process, OMP_NUM_THREADS=1.  No A57 / A60 / A61 file or process '
      'touched; nothing committed.')
    txt = '\n'.join(L) + '\n'
    open(OUT_MD, 'w').write(txt)
    log('wrote %s (%d lines)' % (OUT_MD, len(L)))
    return txt


# ======================================================================== main

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    log, fh = _log_to(LOG_RUN)
    log('=== d2front87 %s  %s' % (cmd, time.strftime('%Y-%m-%d %H:%M:%S')))
    kw = {}
    for a in sys.argv[2:]:
        k, _, v = a.partition('=')
        kw[k.lstrip('-')] = float(v) if v else True
    if cmd == 'selftest':
        selftest(log)
    elif cmd == 'nodes':
        c4_nodes(log)
    elif cmd == 'census':
        census(log)
    elif cmd == 'canary':
        canary(log)
    elif cmd == 'realize':
        realize_scan(npairs=(int(kw['npairs']) if 'npairs' in kw else 6000),
                     log=log)
    elif cmd == 'run':
        run(nnodes=(int(kw['nnodes']) if 'nnodes' in kw else None),
            wall=kw.get('wall', 7000.0), log=log,
            npool=int(kw.get('npool', 140)))
    elif cmd == 'report':
        report(log)
    elif cmd == 'all':
        c4_nodes(log)
        realize_scan(npairs=(int(kw['npairs']) if 'npairs' in kw else 6000),
                     log=log)
        selftest(log)
        canary(log)
        census(log)
        run(nnodes=(int(kw['nnodes']) if 'nnodes' in kw else None),
            wall=kw.get('wall', 7000.0), log=log,
            npool=int(kw.get('npool', 140)))
        report(log)
    else:
        raise SystemExit(__doc__)
    fh.close()


if __name__ == '__main__':
    main()
