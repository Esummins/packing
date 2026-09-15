"""A221 -- the POCKET COVER itself: the exact clip of A171/A172 rooted at ONE pocket, and the pass over a pocket
LIST.  The lemma it certifies (LEMMA POCKET-DEAD) and the leaf that uses it are in `noroom221.py`; this module is
just the engine, so that both live under the attempt's 250-line file rule.  A171 / A189 are READ-ONLY.
"""
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _d in (os.path.join(ROOT, "attempts", "A189-noroom", "code"),
           os.path.join(ROOT, "attempts", "A171-multibox-invariant", "code"),
           os.path.join(ROOT, "attempts", "A141-polycore-lane", "code"),
           os.path.join(ROOT, "attempts", "A161-chord-lane", "code"),
           os.path.join(ROOT, "attempts", "A213-int-polycore", "code")):
    if os.path.isdir(_d) and _d not in sys.path:
        sys.path.insert(0, _d)

import noroom189 as NR                                             # READ-ONLY (A189)
import multibox as MB                                             # READ-ONLY (A171/A172)

DEFAULTS = dict(NR.DEFAULT_BUDGET)
DEFAULTS.update(
    pk_tsub=8,             # tilt sub-bins of the pocket root
    pk_depth=34,           # halvings of the pocket cover (the pocket is ~1/16 of the container's area)
    pk_max_pieces=200000,   # stack cap (depth-first: this is the frontier, not the whole level)
    pk_max_open=20000,      # undischarged pieces at pk_depth before the pocket is given up
    pk_deadline=5.0,       # per pocket.  MEASURED (results/bench221.md s."the cap"): on 42 pocket covers every DEAD
                           # pocket died in <= 0.1 s and every surviving one burned the whole 45 s cap -- the cover
                           # either collapses at once or not at all, so a 5 s cap is a 50x margin and turns an
                           # UNDECIDED node from ~45 s into ~5 s.
    pk_deadline_inherit=3.0,   # per pocket in the INHERITED pass: it is a cheap filter, and a parent pocket that
                                # survives it is paid for again by the full leaf -- so keep the filter short
    pk_container=True,     # the sound w_min container clip on every piece (A171 container_clip, strict=False)
    grow=0.0,              # extra margin added to an inherited pocket before the cover (0: the cover is exact)
)


def install_kernels():
    """A213's integer K' build + A214's C vertex kernel, exactly as coarse211.install_a213 does (idempotent)."""
    try:
        import mbpatch213 as M213
        return bool(M213.install())
    except Exception:                                              # noqa: BLE001 -- never let the patch stop a node
        return False


def budget_of(b=None):
    d = dict(DEFAULTS)
    d.update(b or {})
    return d


# ------------------------------------------------------------------ LEMMA POCKET-DEAD
def cover_rect(nd, rect, bud, deadline=None):
    """Bisect { (c, th) : c in `rect` } against the node's cores.  -> (open pieces, certificate).

    `rect` is a float 4-tuple (x0, x1, y0, y1); it is intersected with [1/2, s-1/2]^2 (every unit square's centre
    is there) and rationalised OUTWARD, so the cover is of a superset of the pocket."""
    S = nd.s
    half = Fr(1, 2)
    x0 = max(half, Fr(math.floor(rect[0] * 4096 - 1), 4096))
    x1 = min(S - half, Fr(math.ceil(rect[1] * 4096 + 1), 4096))
    y0 = max(half, Fr(math.floor(rect[2] * 4096 - 1), 4096))
    y1 = min(S - half, Fr(math.ceil(rect[3] * 4096 + 1), 4096))
    t0 = time.time()
    if x1 <= x0 or y1 <= y0:
        return [], dict(depth=0, stop="empty", n_open=0, n_dropped=0, seconds=0.0,
                        root=[float(x0), float(x1), float(y0), float(y1)], dropped_container=0)
    obst = [nd.boxes[k].obstacle("poly") for k in nd.names]
    root = [(0, MB.Bin(a, b), (x0, x1, y0, y1)) for (a, b) in MB.sub_bins(Fr(0), Fr(1), bud["pk_tsub"])]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for _d, bn, r in root)
    stats = nd.stats
    # DEPTH-FIRST, unlike A189's level-by-level `bisect_free`: the memory is the stack (depth x 2), not the whole
    # frontier, so a pocket whose residue is thin reaches depth 30+ where a breadth-first pass dies on its piece cap.
    stack = list(reversed(root))
    open_ = []
    depth = 0
    nseen = n_dropped = n_cont = 0
    why = "exhausted"
    while stack:
        d, bn, r = stack.pop()
        nseen += 1
        depth = max(depth, d)
        if (nseen & 255) == 0 and deadline is not None and time.time() > deadline:
            why = "deadline"
            open_.append((bn, r))
            open_.extend([(b2, r2) for _d2, b2, r2 in stack])
            break
        cur = r
        if bud["pk_container"]:
            cur, _sl = MB.container_clip(cur, bn, S, strict=False)
            if cur is None:
                n_cont += 1
                continue
        for ob in obst:
            cur = MB._clip_rect_obstacle(cur, ob, bn, stats)
            if cur is None:
                break
        if cur is None:
            n_dropped += 1
            continue
        if d >= bud["pk_depth"]:
            open_.append((bn, cur))
            if len(open_) > bud["pk_max_open"]:
                why = "open cap"
                open_.extend([(b2, r2) for _d2, b2, r2 in stack])
                break
            continue
        for (b2, r2) in MB.split_piece(bn, cur):
            stack.append((d + 1, b2, r2))
        if len(stack) > bud["pk_max_pieces"]:
            why = "piece cap"
            open_.extend([(b2, r2) for _d2, b2, r2 in stack])
            break
    vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in open_)
    cert = dict(depth=depth, stop=why, n_open=len(open_), n_dropped=n_dropped, dropped_container=n_cont,
                n_seen=nseen, root=[float(x0), float(x1), float(y0), float(y1)],
                open_volume=float(vol), root_volume=float(vol0),
                dropped_fraction=float(1 - vol / vol0) if vol0 else None,
                seconds=round(time.time() - t0, 1))
    return open_, cert


def pocket_dead(nd, pocket, bud, deadline=None):
    """LEMMA POCKET-DEAD on one pocket -> dict(dead, cert, residue_pockets)."""
    g = bud["grow"]
    rect = (pocket[0] - g, pocket[1] + g, pocket[2] - g, pocket[3] + g)
    dl = time.time() + bud["pk_deadline"]
    if deadline is not None:
        dl = min(dl, deadline)
    pieces, cert = cover_rect(nd, rect, bud, deadline=dl)
    out = dict(pocket=[round(float(v), 6) for v in pocket], dead=not pieces, cert=cert,
               seconds=cert["seconds"], residue=[],
               open_volume=cert.get("open_volume"), root_volume=cert.get("root_volume"),
               dropped_fraction=cert.get("dropped_fraction"))
    if pieces:
        # re-pocket the SURVIVORS with NO extra margin: `pockets_of`'s grid-cell hulls already contain every open
        # piece, so the margin is pure slack -- and re-applying it at every level would GROW the pocket each time.
        rb = dict(bud)
        rb["margin"] = 0.0
        rb["grid"] = min(bud["grid"], 0.015625)
        out["residue"] = [[round(c, 6) for c in p] for p in NR.pockets_of(pieces, float(nd.s), rb)]
    return out


def pocket_pass(nd, pockets, bud, deadline, m):
    """the cover on a pocket LIST -> (verdict, per-pocket records, surviving pockets)."""
    recs, alive = [], []
    for p in pockets:
        if deadline is not None and time.time() > deadline:
            recs.append(dict(pocket=[round(float(v), 6) for v in p], dead=False, cert=dict(stop="deadline"),
                             seconds=0.0, residue=[[round(float(v), 6) for v in p]]))
            alive.append(list(p))
            continue
        r = pocket_dead(nd, p, bud, deadline=deadline)
        recs.append(r)
        if not r["dead"]:
            alive.extend(r["residue"] or [list(p)])
    return ("DEAD" if not alive else "UNDECIDED"), recs, alive
