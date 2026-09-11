"""A205 audit of a clip-tree kill by pose SAMPLING (the kept rule: a kill the exact tests left alive is a bug until audited).
For a DEAD leaf whose branch instantiated the rows (cell, slot): sample admissible H poses over A203's alive units (container,
pin cores 0.49, meeting every slot H is forced at in the leaf; non-lonely at a forced corner via an independent partner),
admissible F poses on a grid over each branch cell meeting its slot, and -- for an FC kill "at q ... anonymous cap 0" --
admissible G poses over q's whole window meeting B_q+.  A pairwise interior-disjoint (H, F.., G) would REFUTE the kill
(an anonymous meeter of q exists beside the branch's rows); 0 = consistent.
    python audit205.py <nid> <pad> <leaf label> [--nh 300] [--step 0.03] [--tstep 3]"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A204-polyclip-cascade", "scratch"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))
import poly204 as P                                             # noqa: E402
import audit204 as A4                                           # noqa: E402  (A204's samplers, read-only)
import classes178 as CL                                         # noqa: E402

S0 = A4.S0
inside, meets_box, sat_disjoint, pin_free = A4.inside, A4.meets_box, A4.sat_disjoint, A4.pin_free


def grid(W, step, tstep, cell=None):
    x0, x1 = max(0.5, W[0] - 0.71), min(S0 - 0.5, W[1] + 0.71)
    y0, y1 = max(0.5, W[2] - 0.71), min(S0 - 0.5, W[3] + 0.71)
    if cell:
        x0, x1, y0, y1 = max(x0, cell[0]), min(x1, cell[1]), max(y0, cell[2]), min(y1, cell[3])
    xs, ys = np.arange(x0, x1 + 1e-9, step), np.arange(y0, y1 + 1e-9, step)
    ths = np.radians(np.arange(0.0, 90.0 + 1e-9, tstep))
    X, Y, T = np.meshgrid(xs, ys, ths, indexing="ij")
    return X.ravel(), Y.ravel(), T.ravel()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid"); ap.add_argument("pad"); ap.add_argument("leaf")
    ap.add_argument("--nh", type=int, default=300); ap.add_argument("--step", type=float, default=0.03); ap.add_argument("--tstep", type=float, default=3.0)
    a = ap.parse_args()
    cert = json.load(open(os.path.join(HERE, "..", "certs", "cliptree205_%s.json" % a.nid), encoding="utf-8"))
    d = cert["pads"][a.pad]
    node = [n for n in d["nodes"] if n["label"] == a.leaf][0]
    st = P.load_start(a.nid, a.pad)
    wbox = (cert.get("wbox_pad") or {}).get(a.pad) or cert["wbox"]
    cells = cert["cells"]
    pins = [(0.5 * (v["box"][0] + v["box"][1]), 0.5 * (v["box"][2] + v["box"][3])) for k, v in d["nodes"][0]["snapshot"]["roles"].items() if k.startswith("P")]
    # the branch's rows along the path: every ancestor's rows too (labels R.i.j -> R.i)
    rows = []
    for n in d["nodes"]:
        if n.get("rows") and (a.leaf == n["label"] or a.leaf.startswith(n["label"] + ".") or a.leaf.startswith(n["label"] + "u")):
            rows += [(ci, n["slot"]) for ci in n["rows"]]
    forced = sorted(set(node.get("forced_H") or []))
    leaf = str(node.get("leaf") or "")
    q = leaf[6:].split(":")[0] if leaf.startswith("FC at ") else None
    if q is None and leaf.startswith("EmptyBox(") and (node.get("role_slots") or {}).get(leaf[9:].split(")")[0]):
        q = node["role_slots"][leaf[9:].split(")")[0]][0]          # the pair leaf on an FC-instantiated meeter: its slot's window
    if q is None and leaf.startswith("S-CLIP(") and (node.get("role_slots") or {}).get(leaf[7:].split(")")[0]):
        q = node["role_slots"][leaf[7:].split(")")[0]][0]
    print("%s %s leaf %s: %s\n  rows on the path %s; forced H %s; killing slot %s" % (a.nid, a.pad, a.leaf, leaf[:200], rows, forced, q))
    units = P.unit_pieces(st["H_box"], st["units"]) if st.get("units") else [(P.MB.Bin(P.MB.t_lo(st["H_box"][4]), P.MB.t_hi(st["H_box"][5])), tuple(map(float, st["H_box"][:4])))]
    rng = np.random.default_rng(205)
    H = []
    for (bn, r) in units:
        x0, x1, y0, y1 = (float(v) for v in r)
        t0, t1 = float(bn.t0), float(bn.t1)
        for _ in range(max(1, a.nh // len(units))):
            H.append((rng.uniform(x0, x1), rng.uniform(y0, y1), 2 * math.atan(rng.uniform(t0, t1))))
        for cx in (x0, x1):
            for cy in (y0, y1):
                for t in (t0, t1):
                    H.append((cx, cy, 2 * math.atan(t)))
    H = np.array(H)
    ok = inside(H[:, 0], H[:, 1], H[:, 2]) & pin_free(H[:, 0], H[:, 1], H[:, 2], pins)
    for p in forced:
        ok &= meets_box(H[:, 0], H[:, 1], H[:, 2], wbox[p])
    H = H[ok]
    for p in forced:
        if p[3:-1] != "0,0":
            continue
        C = 1 + 0.02551007421394
        xa, ya = CL.frame_to_xy(p[:2], 0, 0, S0); xb, yb = CL.frame_to_xy(p[:2], C, C, S0)
        WB = (min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb))
        GX, GY, GT = grid(WB, 0.02, 2.0)
        okg = inside(GX, GY, GT) & meets_box(GX, GY, GT, WB) & pin_free(GX, GY, GT, pins)
        GX, GY, GT = GX[okg], GY[okg], GT[okg]
        keep = np.array([sat_disjoint(hx, hy, hth, GX, GY, GT).any() for (hx, hy, hth) in H])
        print("  corner %s: H poses with an independent partner (non-lonely): %d of %d" % (p, int(keep.sum()), len(H)))
        H = H[keep]
    if len(H) > a.nh:
        H = H[rng.choice(len(H), a.nh, replace=False)]
    print("  H poses admissible: %d" % len(H))
    F = []
    for ci, p in rows:
        X, Y, T = grid(wbox[p], a.step, a.tstep, cell=cells[ci])
        okf = inside(X, Y, T) & meets_box(X, Y, T, wbox[p]) & pin_free(X, Y, T, pins)
        F.append((ci, p, X[okf], Y[okf], T[okf]))
        print("  row (%d, %s): %d admissible meeter poses in the cell" % (ci, p, int(okf.sum())))
    if q is None:
        print("  (not an FC kill: only the (H, rows) consistency is sampled)")
        G = None
    else:
        X, Y, T = grid(wbox[q], a.step, a.tstep)
        okg = inside(X, Y, T) & meets_box(X, Y, T, wbox[q]) & pin_free(X, Y, T, pins)
        G = (X[okg], Y[okg], T[okg])
        print("  slot %s: %d admissible meeter poses over the whole window" % (q, len(G[0])))
    n_conf, best = 0, None
    for (hx, hy, hth) in H:
        cand = [np.nonzero(sat_disjoint(hx, hy, hth, fx, fy, ft))[0] for (_, _, fx, fy, ft) in F]
        if any(len(c) == 0 for c in cand):
            continue
        gH = None if G is None else sat_disjoint(hx, hy, hth, *G)
        if G is not None and not gH.any():
            continue
        # one F pose per row (the first row's candidates x the second's, capped), then G disjoint from all
        lim = 60
        combos = [(i,) for i in cand[0][:lim]] if len(F) == 1 else [(i, j) for i in cand[0][:lim] for j in cand[1][:lim]]
        for combo in combos:
            fs = [(F[k][2][i], F[k][3][i], F[k][4][i]) for k, i in enumerate(combo)]
            if len(fs) == 2 and not sat_disjoint(fs[0][0], fs[0][1], fs[0][2], np.array([fs[1][0]]), np.array([fs[1][1]]), np.array([fs[1][2]]))[0]:
                continue
            if G is None:
                n_conf += 1
                continue
            m = gH.copy()
            for (fx, fy, ft) in fs:
                m &= sat_disjoint(fx, fy, ft, *G)
                if not m.any():
                    break
            if m.any():
                n_conf += 1
                i = int(np.argmax(m))
                if best is None:
                    best = ((hx, hy, math.degrees(hth)), [(x, y, math.degrees(t)) for x, y, t in fs], (G[0][i], G[1][i], math.degrees(G[2][i])))
    if G is None:
        print("  admissible (H, rows) configurations: %d (the rows' hypothesis is realisable; the kill is by a later clip)" % n_conf)
    else:
        print("  pairwise disjoint (H, rows, G-meeting-%s) configurations: %d  %s" % (q, n_conf, ("-> REFUTED, e.g. %s" % (best,)) if best else "-> 0 refutations (consistent with the kill)"))


if __name__ == "__main__":
    main()
