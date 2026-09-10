"""A184 E3 -- the CERTIFIED uncoverable region U at a recorded node (after S2 / S3 / the (H,D,B)
intermediate), three parts, every one an INNER approximation of the true U (A164's raster contract:
a cell is claimed only when NO admissible pose meets the closed cell, Lipschitz margins included):

  (b) A164's construction (geo164.uncoverable, read-only): free squares admissible iff inside the
      container and interior-disjoint from every role's K' polygon; a role's cover = the union of
      its poses over its surviving pieces (merged per tilt sub-bin into a bounding rect: a
      SUPERSET of the poses, so the complement stays sound [T]).  |U| <= s0^2 - 11 (Leaf WASTE).
  (a) per forced corner c with its meeter roles present (TR: D, S; BR: B): the widened box W_c
      minus every role's cover and minus the cover of the free squares that can still MEET W_c --
      by Lemma A2 (A169) a third meeter's centre lies in a cell of the 2x2 grid at c = 1 + w
      DIFFERENT from each present meeter's cell (when that role's pieces sit in one cell), so the
      free cover on W_c is computed with those centre cells excluded (shrunk by the raster slack,
      outward-sound).  The NAIVE number (W_c minus the meeter roles' covers only) is reported
      too, as what the reading would give if a third meeter were impossible -- it is not [F].
  (c) the kill |U_b u U_a(TR) u U_a(BR)| > s0^2 - 11.
  plus the NO-family ZONE for (d): {centres within 1/2 of U} (a square with centre there contains
      a point of U, so NO square of the packing has its centre there [T]), as rects (inner).

    python waste184.py [--keys k1,k2] [--pitch 0.01] [--ntilt 36]   -> results/waste184.jsonl, results/masks/
"""
import argparse
import math
import os
import time

import numpy as np

import common184 as C
from common184 import K, R, RS, Box
import geo164 as G                                               # noqa: E402  (A164, read-only)
import polycore                                                  # noqa: E402

OUT = os.path.join(C.RES, "waste184.jsonl")
MASKS = os.path.join(C.RES, "masks")
S0 = K.S0
CW = float(RS.C_RAT)                                             # 1 + w
MEETERS = {"TR": ("D", "S"), "BR": ("B", "Bp"), "TL": ("T1", "T2"), "BL": ("L1", "L2")}


def role_geometry(rj, max_groups=48):
    """K' polygon (floats) and the per-sub-bin bounding boxes of the pieces (a superset cover)."""
    P = [(float(C.Fr(v[0])), float(C.Fr(v[1]))) for v in rj["core"]]
    groups = {}
    for p in rj["pieces"]:
        b = Box(*p)
        groups.setdefault((round(b.th0, 9), round(b.th1, 9)), []).append(b)
    boxes = [Box(min(b.x0 for b in g), max(b.x1 for b in g), min(b.y0 for b in g), max(b.y1 for b in g), k[0], k[1])
             for k, g in groups.items()]
    if len(boxes) > max_groups:                                   # merge neighbouring sub-bins (still a superset)
        boxes.sort(key=lambda b: b.th0)
        step = int(math.ceil(len(boxes) / max_groups))
        boxes = [Box(min(b.x0 for b in g), max(b.x1 for b in g), min(b.y0 for b in g), max(b.y1 for b in g),
                     min(b.th0 for b in g), max(b.th1 for b in g))
                 for g in (boxes[i:i + step] for i in range(0, len(boxes), step))]
    return P, boxes


def local_xy(X, Y, corner):
    """corner-local coordinates (distance from the corner's two walls)."""
    if corner == "TR":
        return S0 - X, S0 - Y
    if corner == "TL":
        return X, S0 - Y
    if corner == "BR":
        return S0 - X, Y
    return X, Y


def cell_of_role(rj, corner):
    """the 2x2 cell (lx < c, ly < c) of the role's centres at c = 1 + w, or None if not unique."""
    cells = set()
    for p in rj["pieces"]:
        b = Box(*p)
        for (x, y) in ((b.x0, b.y0), (b.x1, b.y0), (b.x0, b.y1), (b.x1, b.y1)):
            lx, ly = local_xy(x, y, corner)
            cells.add((lx < CW, ly < CW))
    return cells.pop() if len(cells) == 1 else None


def free_cover_masked(obstacles, xs, ys, p, excluded, corner, q=0.01, ntilt=36):
    """geo164.free_cover with the centres in `excluded` cells removed (OUTER: a grid node is dropped
    only when every centre within q*sqrt2/2 + m1 of it lies in an excluded cell)."""
    slack = q * G.ROOT2H + q * G.ROOT2H + (math.pi / 2 / ntilt) * G.ROOT2H / 2 + 1e-9
    ny, nx = len(ys), len(xs)
    PXo, PYo = np.meshgrid(xs, ys)
    cover = np.zeros((ny, nx), bool)
    dth = (math.pi / 2.0) / ntilt
    m1 = q * G.ROOT2H + G.ROOT2H * (dth / 2.0)
    Hw = 0.5 + G.ROOT2H * (dth / 2.0) + 0.5 * q + p * G.ROOT2H
    Rn = int(math.ceil(Hw / q + 0.5))
    pad = m1 + 0.02
    lo, hi = 0.5 - pad, S0 - 0.5 + pad
    corners = np.array([[lo, lo], [hi, lo], [hi, hi], [lo, hi]])
    for th in (np.arange(ntilt) + 0.5) * dth:
        c, sn = math.cos(th), math.sin(th)
        U_ = corners[:, 0] * c + corners[:, 1] * sn
        V_ = -corners[:, 0] * sn + corners[:, 1] * c
        u0, v0 = U_.min(), V_.min()
        nu, nv = int(math.ceil((U_.max() - u0) / q)) + 1, int(math.ceil((V_.max() - v0) / q)) + 1
        UU, VV = np.meshgrid(u0 + np.arange(nu) * q, v0 + np.arange(nv) * q)
        CX, CY = UU * c - VV * sn, UU * sn + VV * c
        w = 0.5 * (abs(c) + abs(sn))
        cl = np.minimum.reduce([CX - w, S0 - w - CX, CY - w, S0 - w - CY])
        live = cl >= -m1
        lx, ly = local_xy(CX, CY, corner)
        for (ex, ey) in excluded:                                 # cell (lx < c ?, ly < c ?), shrunk by slack
            inx = (lx < CW - slack) if ex else (lx >= CW + slack)
            iny = (ly < CW - slack) if ey else (ly >= CW + slack)
            live &= ~(inx & iny)
        if live.any() and obstacles:
            Cl = np.stack([CX[live], CY[live]], 1)
            cs = cl[live]
            for P in obstacles:
                cs = np.minimum(cs, -polycore.poly_square_depth(P, Cl, np.full(len(Cl), th)))
            tmp = np.full(cl.shape, -9e9)
            tmp[live] = cs
            cl = tmp
        elif not live.any():
            continue
        A = cl >= -m1
        if not A.any():
            continue
        Sd = G._dilate_box(np.pad(A, Rn, constant_values=False), Rn)
        Up, Vp = PXo * c + PYo * sn, -PXo * sn + PYo * c
        iu = np.rint((Up - u0) / q).astype(np.int64) + Rn
        iv = np.rint((Vp - v0) / q).astype(np.int64) + Rn
        ok = (iu >= 0) & (iu < Sd.shape[1]) & (iv >= 0) & (iv < Sd.shape[0])
        hit = np.zeros((ny, nx), bool)
        hit[ok] = Sd[iv[ok], iu[ok]]
        cover |= hit
    return cover


def corner_part(roles, corner, obstacles, rolecov, xs, ys, p, ntilt):
    """U_a(corner) and the naive number; None when no meeter role of the corner is present."""
    present = [nm for nm in MEETERS[corner] if nm in roles]
    if not present:
        return None
    X, Y = np.meshgrid(xs, ys)
    X0, X1, Y0, Y1 = K.corner_cell(corner)
    W = (X >= X0) & (X <= X1) & (Y >= Y0) & (Y <= Y1)
    cells = {nm: cell_of_role(roles[nm], corner) for nm in present}
    excluded = [c for c in cells.values() if c is not None]
    meet = np.zeros(W.shape, bool)
    for nm in present:
        meet |= rolecov[nm]
    naive = W & ~meet
    allrole = np.zeros(W.shape, bool)
    for m in rolecov.values():
        allrole |= m
    fc = free_cover_masked(obstacles, xs, ys, p, excluded, corner, q=p, ntilt=ntilt)
    Ua = W & ~allrole & ~fc
    return dict(mask=Ua, area=float(Ua.sum()) * p * p, naive_area=float(naive.sum()) * p * p,
                area_W=float(W.sum()) * p * p, present=present,
                cells={nm: (None if c is None else [bool(c[0]), bool(c[1])]) for nm, c in cells.items()},
                n_excluded_cells=len(excluded))


def zone_rects(U, xs, ys, p):
    """{c : dist(c, U) <= 1/2} inner-approximated by dilating the U cells by k = floor(h/p) - 1 cells,
    h = 1/(2 sqrt2) (a point within h in Chebyshev of a U cell is within 1/2 of it), then rows merged."""
    k = int(math.floor((0.5 / math.sqrt(2.0)) / p)) - 1
    Z = G._dilate_box(np.pad(U, k, constant_values=False), k)[k:-k, k:-k] if k > 0 else U
    runs = G.runs_of(Z, xs, ys, p)
    merged = []
    for (x0, x1, y0, y1) in runs:                                 # merge vertically adjacent equal runs
        if merged and abs(merged[-1][0] - x0) < 1e-12 and abs(merged[-1][1] - x1) < 1e-12 and abs(merged[-1][3] - y0) < 1e-9:
            merged[-1] = (x0, x1, merged[-1][2], y1)
        else:
            merged.append((x0, x1, y0, y1))
    return Z, [[round(v, 6) for v in r] for r in merged]


def sample_check(obstacles, boxes, Umask, xs, ys, n=30000, seed=184):
    return G.sample_confirm(S0, obstacles, boxes, Umask, xs, ys, lam=1.0, n=n, n_contain=8000)


def uncoverable_node(key, roles, pitch=0.01, ntilt=36, corners=("TR", "BR"), save_mask=True):
    t0 = time.time()
    obstacles, boxes, per_role = [], [], {}
    for nm, rj in roles.items():
        P, bx = role_geometry(rj)
        obstacles.append(P)
        boxes += bx
        per_role[nm] = bx
    Ub, xs, ys, res = G.uncoverable(S0, obstacles, boxes, lam=1.0, pitch=pitch, ntilt=ntilt, want_extra=False)
    p = float(res["pitch"])
    t_b = time.time() - t0
    rolecov = {nm: np.zeros(Ub.shape, bool) for nm in roles}
    for nm, bx in per_role.items():
        for b in bx:
            rolecov[nm] |= G.box_cover(b, xs, ys, p, lam=1.0)[0]
    U = Ub.copy()
    parts = {}
    for c in corners:
        cp = corner_part(roles, c, obstacles, rolecov, xs, ys, p, ntilt)
        if cp is None:
            continue
        U |= cp["mask"]
        parts[c] = {k: v for k, v in cp.items() if k != "mask"}
    area = float(U.sum()) * p * p
    Z, zr = zone_rects(U, xs, ys, p)
    chk = sample_check(obstacles, boxes, Ub, xs, ys)
    rec = dict(key=key, roles=list(roles), pitch=p, ntilt=ntilt, area_U_b=res["area_U"], by_region=res["by_region"],
               corner=parts, area_U=area, ratio_B0=area / C.B0, kill=bool(area > C.B0), B0=C.B0,
               zone_n_rects=len(zr), zone_area=float(Z.sum()) * p * p, zone_rects=zr,
               sample=chk, n_boxes=len(boxes), t_b=round(t_b, 1), seconds=round(time.time() - t0, 1))
    if save_mask:
        os.makedirs(MASKS, exist_ok=True)
        np.savez_compressed(os.path.join(MASKS, key.replace("|", "_").replace("/", "_") + ".npz"),
                            U=U, Ub=Ub, Z=Z, xs=xs, ys=ys)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", default="")
    ap.add_argument("--pitch", type=float, default=0.01)
    ap.add_argument("--ntilt", type=int, default=36)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--steps", default="S2,S3,HDB,S1")
    a = ap.parse_args()
    C.set_process()
    import run184 as RU
    recs = RU.load_all(2)
    recs.update(C.load_jsonl(os.path.join(C.RES, "nodes184_s0of1.jsonl")))
    done = C.load_jsonl(OUT)
    sk, sn = RS.shard_of(a.shard)
    keys = a.keys.split(",") if a.keys else sorted(k for k, r in recs.items()
                                                    if r.get("roles") and r.get("step") in a.steps.split(","))
    keys = [k for i, k in enumerate(keys) if i % sn == sk and k not in done]
    print("waste184: %d nodes to do" % len(keys), flush=True)
    for key in keys:
        with C.NodeWall("waste|" + key):
            rec = uncoverable_node(key, recs[key]["roles"], pitch=a.pitch, ntilt=a.ntilt)
        rec["step"] = recs[key].get("step")
        rec["exp"] = recs[key].get("exp")
        C.append_jsonl(OUT, rec)
        print("  %-34s |U_b| %.4f  U %.4f (%.1f%% of B0)  corners %s  hits %s  %.0fs" % (
            key, rec["area_U_b"], rec["area_U"], 100 * rec["ratio_B0"],
            {c: (round(v["area"], 4), round(v["naive_area"], 3)) for c, v in rec["corner"].items()},
            rec["sample"]["free"]["hits"], rec["seconds"]), flush=True)


if __name__ == "__main__":
    main()
