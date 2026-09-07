"""A118 T4 (PI generalisation): the REVERSED leaf -- branch on the TWO meeters of a usable cell.

The split is tautologous and needs no LP on one side:

    (>= 2 non-pin squares meet C)   OR   (<= 1 non-pin square meets C)

and the second branch is DEAD BY TELEPORT (SLOT-CROWD for a pinned class, K0-FREE for a corner
cell) -- the leaf of T1, with no LP and no certificate.  The first branch is covered by a
PAIR-BOX cover: a box cover {B_1, ..., B_N} of R(C) gives, for the two meeters, an unordered
pair (B_a, B_b) containing them, so the parent is the union of the N(N+1)/2 children

    child(a, b) = parent hypothesis + core(B_a) + core(B_b), budget - 2.

Each child is an ordinary A57 node: the same Box/Core objects, the same pinguard, the same
frozen verifier.  A child dies FREE (no LP) when the two bins provably cannot hold two disjoint
squares -- core(B_a) meets core(B_b) (Lemma TC / CORE-MEET between bins) or the octagon interval
test certifies that every pose in B_a overlaps every pose in B_b.

Boxes are built in the CELL's CORNER FRAME (where the cell is [i,i+1]x[j,j+1] at every side) and
mapped to A57's world frame at s0 through the dilation, so the emitted boxes are exactly A57's
format and the existing cores / tight core / octagon tests apply verbatim.

Usage:  python pairbox.py --out results/pairbox.json
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blas1  # noqa: F401
import numpy as np

import lanelib as L
import corpus as CP
import lane as LN

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
S0 = CP.S0


def cframe_to_world_s0(b, corner, m_lo):
    """Map a corner-frame box (valid for every side m in [m_lo, s0]) to the box its DILATED image
    occupies in A57's world frame at s0.  world_x(m) = u or m - u; dilated x' = (s0/m) world_x,
    so x' = (s0/m) u  (near wall)  or  s0 - (s0/m) u  (far wall); both monotone in m, so the hull
    over m in {m_lo, s0} is exact."""
    lam_hi = S0 / m_lo
    flipx = corner in ("BR", "TR")
    flipy = corner in ("TR", "TL")

    def mp(u0, u1, flip):
        vals = []
        for u in (u0, u1):
            for lam in (1.0, lam_hi):
                vals.append(S0 - lam * u if flip else lam * u)
        return min(vals), max(vals)

    X0, X1 = mp(b.x0, b.x1, flipx)
    Y0, Y1 = mp(b.y0, b.y1, flipy)
    t0, t1 = b.th0, b.th1
    if flipx != flipy:
        t0, t1 = 90.0 - t1, 90.0 - t0
    t0 = min(max(t0, 0.0), 90.0); t1 = min(max(t1, 0.0), 90.0)
    assert 0.0 <= t0 <= t1 <= 90.0, "tilt interval not normalised to [0, 90]"
    return L.Bx(X0, X1, Y0, Y1, t0, t1)


def d4_ops_fixing(cls, cell):
    """Symmetries of the class's pin set that also fix the cell (used to de-duplicate pairs).
    Only the main diagonal is ever available for these classes; identity always is."""
    ops = [("id", lambda x, y, t: (x, y, t))]
    if cls == "k0_00":
        return ops
    pins = sorted((round(p, 6), round(q, 6)) for p, q in CP.CLASSES[cls]["pins"])
    dpins = sorted((round(q, 6), round(p, 6)) for p, q in CP.CLASSES[cls]["pins"])
    c, i, j = L.parse_cell(cell)
    diag_cell = {"BL": "BL", "TR": "TR", "BR": "TL", "TL": "BR"}[c] + "(%d,%d)" % (j, i)
    if pins == dpins and diag_cell == cell:
        ops.append(("diag", lambda x, y, t: (y, x, 90.0 - t)))
    return ops


def _key(b, ndig=5):
    return (round(b.x0, ndig), round(b.x1, ndig), round(b.y0, ndig), round(b.y1, ndig),
            round(b.th0, 3), round(b.th1, 3))


def _apply(op, b):
    f = op[1]
    x0, y0, t1 = f(b.x0, b.y0, b.th1)
    x1, y1, t0 = f(b.x1, b.y1, b.th0)
    return L.Bx(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(t0, t1), max(t0, t1))


def build(rec, cell, nx=8, nth=6, refine=0):
    """Return the pair-box census for (node, cell)."""
    t0 = time.time()
    c, i, j = L.parse_cell(cell)
    fr = (1.0, float(i), 1.0, float(j))
    m_lo = LN.M_LO.get(rec["src"], 3.82)
    pins, cond = LN.cores_of(rec, c, i, j)
    cores = pins + [k for (_, k) in cond]
    cov = L.cover_R(fr, 1.0, cores, S0, nx=nx, nth=nth, rho=0.0)
    for _ in range(refine):
        nxt = []
        for b in cov:
            nxt.extend(b.split())
        cov = LN._prune(nxt, fr, 1.0, cores, S0, rho=0.0)
    W = [cframe_to_world_s0(b, c, m_lo) for b in cov]
    n = len(W)

    # per-box logic screens (T5 core-meet vs pins, T5'' octagon vs pins, pinguard 'parent')
    pin_world = [LN.cframe_boxes(rec, "BL", 0, 0)[0]]     # pins in the world frame (BL frame)
    pin_world = pin_world[0]
    pinK = [L.tight_core_of_box(b) for b in pin_world]
    slots = [(0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)) for b in pin_world]
    dead_box = []
    for b in W:
        why = None
        if L.box_hits_core(b, [k for k in pinK if k is not None]):
            why = "T5/T5'' vs a pin"
        else:
            th_ok = (b.th0 - 1e-9 <= 0.0 <= b.th1 + 1e-9) or (b.th0 - 1e-9 <= 90.0 <= b.th1 + 1e-9)
            if th_ok and any(b.x0 - 1e-2 <= px <= b.x1 + 1e-2 and b.y0 - 1e-2 <= py <= b.y1 + 1e-2
                             for px, py in slots):
                why = "pinguard parent (unsound at reduced budget)"
        dead_box.append(why)

    ops = d4_ops_fixing(rec["cls"], cell)
    seen = set()
    pairs, tc, oct_, both_dead, parent = [], 0, 0, 0, 0
    for a in range(n):
        for b in range(a, n):
            key = None
            for op in ops:
                A, B = _apply(op, W[a]), _apply(op, W[b])
                ka, kb = _key(A), _key(B)
                k = (ka, kb) if ka <= kb else (kb, ka)
                key = k if key is None or k < key else key
            if key in seen:
                continue
            seen.add(key)
            if dead_box[a] == "pinguard parent (unsound at reduced budget)" or \
               dead_box[b] == "pinguard parent (unsound at reduced budget)":
                parent += 1
                continue
            if dead_box[a] or dead_box[b]:
                both_dead += 1
                continue
            Ka, Kb = L.tight_core_of_box(W[a]), L.tight_core_of_box(W[b])
            if Ka is not None and Kb is not None and L.sq_gap(Ka, Kb) < 0.0:
                tc += 1
                continue
            if L.pair_always_overlap(W[a], W[b]):
                oct_ += 1
                continue
            pairs.append((a, b))
    return dict(node=rec["nid"], src=rec["src"], cls=rec["cls"], cell=cell,
                level=rec.get("level"), budget=rec.get("budget"),
                boxes=n, grid=[nx, nth, refine],
                unordered_pairs_after_symmetry=len(seen),
                sym_ops=[o[0] for o in ops],
                killed_box_level=both_dead, killed_pinguard_parent=parent,
                killed_lemma_TC=tc, killed_octagon_pair=oct_,
                surviving=len(pairs), secs=round(time.time() - t0, 2),
                boxes_json=[b.to_json() for b in W], pairs=pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "pairbox.json"))
    ap.add_argument("--nx", type=int, default=8)
    ap.add_argument("--nth", type=int, default=6)
    ap.add_argument("--nodes", type=int, default=12)
    a = ap.parse_args()

    recs = CP.load_nodes()
    by = {r["nid"]: r for r in recs}
    jobs = []
    # the two class ROOTS (pins only, no conditioned square)
    for cls, src, bud in (("k5_11", "A57", 6), ("trump5", "A60", 6)):
        jobs.append(dict(src=src, nid=cls + "_ROOT", cls=cls, level=0, side=S0,
                         budget=bud, cond=[], alive=True))
    # alive nodes: A57 k5_11/k5_16 level 1-2 and A60 trump5, stratified
    alive = [r for r in recs if r.get("alive") and r["cls"] != "k0_00"]
    alive.sort(key=lambda r: (r["cls"], r["level"], r["nid"]))
    step = max(1, len(alive) // a.nodes)
    jobs += alive[::step][:a.nodes]

    out = []
    for r in jobs:
        cells = list(CP.CLASSES[r["cls"]]["usable"].keys())
        for cn in cells:
            rr = build(r, cn, nx=a.nx, nth=a.nth)
            out.append(rr)
            print("%-28s %-9s boxes %4d pairs %6d  TC %6d oct %6d box %6d parent %5d  SURV %5d  %.1fs"
                  % (r["nid"][:28], cn, rr["boxes"], rr["unordered_pairs_after_symmetry"],
                     rr["killed_lemma_TC"], rr["killed_octagon_pair"], rr["killed_box_level"],
                     rr["killed_pinguard_parent"], rr["surviving"], rr["secs"]), flush=True)
    json.dump(dict(rows=out), open(a.out, "w"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
