"""A201 -- rule (c) as a SEEDED two-box mutual clip (A171 multibox primitives, READ-ONLY): the two option rows' own
surviving pieces (centre rect x tilt sub-bin; already container-clipped and clipped against the pins' and every
role's K' by A198's reach bisection) are clipped against EACH OTHER's certified K' until nothing moves.
  K'(X) for a row X = the exact intersection of the per-piece K' (A172, `MBox.rebuild(kmode="pieces")`) over
  COARSENED pieces: one hull piece per initial tilt quarter (a hull piece contains its fine pieces, so its K' is a
  subset of theirs and the intersection is a sound, slightly smaller K').
  A pose of X1 meeting int K'(X2) meets X2's square at EVERY pose of X2 (`_clip_rect_obstacle` / `dead_poly`, exact),
  so it cannot coexist with X2: dropped.  Both sides empty-or-not after <= max_iter passes; a side with no surviving
  piece => the pair is EXCLUDED (no interior-disjoint admissible pair exists).  Optional `refine` levels split the
  fine pieces once (tautologous) so a diagonal dead band bites.  Anything undecided is COMPATIBLE.
"""
import time
from fractions import Fraction as Fr

import fastprop as FP                                          # READ-ONLY (A198)

MB = FP.MB
SQ2 = Fr(14142135624, 10 ** 10)                                # > sqrt2: centres this far apart never meet


def coarsen(pcs, n=4):
    groups = {}
    for bn, r in pcs:
        g = min(n - 1, int(bn.t0 * n))
        groups.setdefault(g, []).append((bn, r))
    out = []
    for g in sorted(groups):
        h = FP.pieces_hull(groups[g])
        out.append((MB.Bin(h[4], h[5]), (h[0], h[1], h[2], h[3])))
    return out


def mbox_of(name, pcs, n_coarse=4):
    h = FP.pieces_hull(pcs)
    mb = MB.MBox(name, MB.Box(float(h[0]), float(h[1]), float(h[2]), float(h[3]), MB.deg_of_t(h[4]), MB.deg_of_t(h[5])))
    mb.kmode = "pieces"
    mb.pieces = coarsen(pcs, n_coarse)
    return mb


def far_apart(h1, h2):
    """min Euclidean distance between the two centre rects >= sqrt2: every pair of poses is disjoint."""
    dx = max(Fr(0), h2[0] - h1[1], h1[0] - h2[1])
    dy = max(Fr(0), h2[2] - h1[3], h1[2] - h2[3])
    return dx * dx + dy * dy >= SQ2 * SQ2


def _clip_side(pcs, obs, stats, refine):
    keep, changed = [], False
    for bn, r in pcs:
        if not FP.obstacle_near(obs, r):                         # the K' polygon is > 1/sqrt2 from the rect: untouched
            keep.append((bn, r))
            continue
        cur = MB._clip_rect_obstacle(r, obs, bn, stats)
        if cur is None:
            changed = True
            continue
        if cur != r:
            changed = True
        if refine > 0:
            for bn2, r2 in MB.split_piece(bn, cur):
                c2 = MB._clip_rect_obstacle(r2, obs, bn2, stats)
                if c2 is not None:
                    keep.append((bn2, c2))
                else:
                    changed = True
        else:
            keep.append((bn, cur))
    return keep, changed


def pair_clip(p1, p2, s, max_iter=4, refine=0, n_coarse=4, max_pieces=600, stats=None):
    """-> dict(excluded, why, passes, seconds, kept_a, kept_b)."""
    t0 = time.time()
    stats = stats if stats is not None else {"exact_calls": 0, "backoffs": 0}
    A, B = list(p1), list(p2)
    if not A or not B:
        return dict(excluded=True, why="no surviving piece on one side", passes=0, seconds=0.0)
    va0, vb0 = FP.pieces_volume(A), FP.pieces_volume(B)
    if far_apart(FP.pieces_hull(A), FP.pieces_hull(B)):
        return dict(excluded=False, why="hulls >= sqrt2 apart: trivially compatible", passes=0, seconds=round(time.time() - t0, 3))
    passes = []
    for it in range(max_iter):
        ma, mb_ = mbox_of("X1", A, n_coarse), mbox_of("X2", B, n_coarse)
        ma.rebuild()
        mb_.rebuild()
        oa, ob = ma.obstacle("poly"), mb_.obstacle("poly")
        rf = refine if (it == 0 and len(A) + len(B) <= max_pieces) else 0
        A, ca = _clip_side(A, ob, stats, rf)
        if not A:
            passes.append(dict(pass_=it + 1, dead="X1"))
            return dict(excluded=True, why="X1 has no pose clear of K'(X2) after pass %d" % (it + 1), passes=passes,
                        seconds=round(time.time() - t0, 3), kept_a=0.0, kept_b=round(float(FP.pieces_volume(B) / vb0), 5))
        B, cb = _clip_side(B, oa, stats, rf)
        if not B:
            passes.append(dict(pass_=it + 1, dead="X2"))
            return dict(excluded=True, why="X2 has no pose clear of K'(X1) after pass %d" % (it + 1), passes=passes,
                        seconds=round(time.time() - t0, 3), kept_a=round(float(FP.pieces_volume(A) / va0), 5), kept_b=0.0)
        ka, kb = float(FP.pieces_volume(A) / va0), float(FP.pieces_volume(B) / vb0)
        passes.append(dict(pass_=it + 1, kept_a=round(ka, 5), kept_b=round(kb, 5), n_a=len(A), n_b=len(B)))
        if not (ca or cb):
            break
    return dict(excluded=False, why="both sides keep poses (X1 %.3f, X2 %.3f of their volume): COMPATIBLE" % (ka, kb),
                passes=passes, seconds=round(time.time() - t0, 3), kept_a=round(ka, 5), kept_b=round(kb, 5))


def cover_clip(piece_sets, s, max_iter=3, n_coarse=4, stats=None, names=None):
    """the same clip on a WHOLE cover: every row's pieces against every other row's K' (rows whose hulls are >= sqrt2
    apart skip each other), to a fixed point.  A row with no surviving piece => the cover is refuted: no packing
    realises all its rows by distinct squares (the pairwise argument, applied to every pair at once, is exactly
    what a pairwise-verified cover has NOT been asked).  -> dict(excluded, dead, why, passes, seconds, kept)."""
    t0 = time.time()
    stats = stats if stats is not None else {"exact_calls": 0, "backoffs": 0}
    P = [list(p) for p in piece_sets]
    names = names or ["X%d" % i for i in range(len(P))]
    if any(not p for p in P):
        i = [k for k, p in enumerate(P) if not p][0]
        return dict(excluded=True, dead=names[i], why="row %s has no surviving piece" % names[i], passes=[], seconds=0.0)
    v0 = [FP.pieces_volume(p) for p in P]
    hulls = [FP.pieces_hull(p) for p in P]
    near = {(i, j) for i in range(len(P)) for j in range(len(P)) if i != j and not far_apart(hulls[i], hulls[j])}
    passes = []
    for it in range(max_iter):
        obs = {}
        for i, p in enumerate(P):
            if any((i, j) in near for j in range(len(P))):
                mb = mbox_of(names[i], p, n_coarse)
                mb.rebuild()
                obs[i] = mb.obstacle("poly")
        changed = False
        for i in range(len(P)):
            for j in range(len(P)):
                if (i, j) not in near:
                    continue
                P[i], c = _clip_side(P[i], obs[j], stats, 0)
                changed = changed or c
                if not P[i]:
                    passes.append(dict(pass_=it + 1, dead=names[i], against=names[j]))
                    return dict(excluded=True, dead=names[i], why="row %s has no pose clear of K'(%s) after pass %d" % (names[i], names[j], it + 1),
                                passes=passes, seconds=round(time.time() - t0, 3),
                                kept={names[k]: round(float(FP.pieces_volume(P[k]) / v0[k]), 5) for k in range(len(P))})
        kept = {names[k]: round(float(FP.pieces_volume(P[k]) / v0[k]), 5) for k in range(len(P))}
        passes.append(dict(pass_=it + 1, kept=kept))
        if not changed:
            break
    return dict(excluded=False, dead=None, why="every row keeps poses: the cover stands (joint clip, %d passes)" % len(passes),
                passes=passes, seconds=round(time.time() - t0, 3), kept=kept)
