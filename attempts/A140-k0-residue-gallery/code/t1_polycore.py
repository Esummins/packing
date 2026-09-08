"""A140 T1 -- the polygon core K'(B) measured on the k0_00 residue.

A132 measured K' on A57/A60, where a node's hypothesis is 5 PINS + 1 conditioned square and the
T5-polygon kill is "K'(conditioned) meets K'(pin)".  k0_00 has NO pins: every hypothesis core of a
k0 node IS a conditioned square, so the only geometric kills available are

  (i)   COLUMN EXCLUSION -- a dual-support / pool column whose square meets K'(B) but not the
        deployed axis core K(a).  Such a placement cannot coexist with the conditioned square (a
        square meeting K' meets Q0 at every pose of B, and the LP's columns are squares OTHER than
        Q0), so the LP is charging weight to a column its own hypothesis forbids.  The weight
        carried is measured against the slack tau - budget.
  (ii)  K' vs the CONTAINER -- if K'(B) leaves [0,s]^2 then no pose of B admits a square inside the
        container and the node is empty (a T5-type kill, with the walls in the role of the pin).
  (iii) K' vs K' BETWEEN the conditioned boxes of one cell -- if two conditioned boxes' polygon
        cores meet, their two squares share an interior point, so they are the SAME square and the
        cell's own "two distinct squares" hypothesis is contradicted (`core_meet_same_square`'s set
        form).  One exact rational witness point per hit.

Every K' is A132's certified polygon (exact rational vertex test).  Alongside K' the A135 EXACT
AXIS CORE is measured: the largest half-side a at the box's own (kx, ky, tm) that passes the same
exact vertex test.  That one is a SQUARE and therefore fits the FROZEN certificate schema, so any
kill it alone produces is certifiable with no verifier change; a kill that needs the full polygon
is not.

READ-ONLY on every campaign.   python code/t1_polycore.py [--pool] [--out ...]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for p in (os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"),
          os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
          os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code"),
          HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                              # noqa: E402
import exactcore                                             # noqa: E402
from caselp import Box, Core, EPS_CORE                       # noqa: E402
import cells140 as C140                                      # noqa: E402

EPS = EPS_CORE          # 2e-3, the LP's own drop margin
S0 = C140.S0


def core_at(box, a):
    k = box.core()
    return Core(k.kx, k.ky, k.tm, a, box)


def measure(meta, d, want_witness=True):
    boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
    rec = dict(meta)
    rec["n_boxes"] = len(boxes)
    rec["tau"] = d.get("tau")
    rec["budget"] = d.get("budget")
    rec["converged"] = d.get("converged")
    rec["minmass"] = d.get("minmass")
    rec["s"] = d.get("s")
    slack = float(d["tau"]) - float(d["budget"])
    rec["slack"] = slack

    pcs, stock, exact, binfo = [], [], [], []
    for b in boxes:
        pc = polycore.build(b)
        k = b.core()
        a_ex, a_st, ok = exactcore.exact_a(b)
        pcs.append(pc)
        stock.append(k)
        exact.append(core_at(b, a_ex) if ok else k)
        binfo.append(dict(
            box=[b.x0, b.x1, b.y0, b.y1, b.th0, b.th1],
            th_width=b.th1 - b.th0, xy_width=max(b.x1 - b.x0, b.y1 - b.y0),
            poly_verts=len(pc.verts), poly_certified=pc.certified,
            area_poly=pc.area(), a_stock=float(k.a), a_exact=float(a_ex) if ok else None,
            exact_ok=bool(ok),
            area_stock=(2.0 * float(k.a)) ** 2,
            area_exact=(2.0 * float(a_ex)) ** 2 if ok else None,
            ratio_poly_stock=pc.area() / (2.0 * float(k.a)) ** 2,
            ratio_exact_stock=(float(a_ex) / float(k.a)) ** 2 if ok else None))
    rec["boxes"] = binfo

    # ---------------------------------------------------------------- (i) column exclusion
    def scan(P):
        if len(P) == 0:
            return dict(n=0, n_stock=0, n_exact_only=0, n_poly_only=0, n_poly_only_strict=0,
                        w=0.0, w_exact_only=0.0, w_poly_only=0.0, w_poly_only_strict=0.0,
                        idx_poly_only=[], idx_exact_only=[])
        C, TH, W = P[:, :2], P[:, 2], P[:, 3]
        hit_st = np.zeros(len(P), bool)
        hit_ex = np.zeros(len(P), bool)
        hit_pl = np.zeros(len(P), bool)
        hit_pls = np.zeros(len(P), bool)
        for k, ke, pc in zip(stock, exact, pcs):
            hit_st |= polycore.core_depth_fast(k, C, TH) > EPS
            hit_ex |= polycore.core_depth_fast(ke, C, TH) > EPS
            dp = polycore.poly_square_depth(pc.P, C, TH)
            hit_pl |= dp > EPS
            hit_pls |= dp > 0.0
        eonly = hit_ex & ~hit_st
        ponly = hit_pl & ~hit_st
        ponly_s = hit_pls & ~hit_st
        return dict(n=int(len(P)), n_stock=int(hit_st.sum()), n_exact=int(hit_ex.sum()),
                    n_poly=int(hit_pl.sum()),
                    n_exact_only=int(eonly.sum()), n_poly_only=int(ponly.sum()),
                    n_poly_only_strict=int(ponly_s.sum()),
                    w=float(W.sum()), w_exact_only=float(W[eonly].sum()),
                    w_poly_only=float(W[ponly].sum()),
                    w_poly_only_strict=float(W[ponly_s].sum()),
                    idx_poly_only=np.flatnonzero(ponly).tolist()[:64],
                    idx_exact_only=np.flatnonzero(eonly).tolist()[:64])

    pk = np.array([[p["cx"], p["cy"], p["theta"], p.get("y", 0.0)]
                   for p in d.get("packing", [])], dtype=float).reshape(-1, 4)
    rec["support"] = scan(pk)
    rows = np.array(d.get("rows_all") or [], dtype=float).reshape(-1, 3)
    rec["pool"] = scan(np.hstack([rows, np.zeros((len(rows), 1))]) if len(rows) else rows)
    rec["kills_i"] = bool(rec["support"]["w_poly_only"] > slack + 1e-12)
    rec["kills_i_exact"] = bool(rec["support"]["w_exact_only"] > slack + 1e-12)

    # ---------------------------------------------------------------- (ii) K' vs container
    s = float(d.get("s") or S0)
    cont = []
    for j, (pc, k, ke) in enumerate(zip(pcs, stock, exact)):
        V = pc.P
        exc_p = float(max(0.0, np.max(np.maximum(-V, V - s))))
        vs = np.array([[float(a), float(b)] for a, b in
                       exactcore.core_corners(k.kx, k.ky, k.cm, k.sm, k.a)], float)
        exc_s = float(max(0.0, np.max(np.maximum(-vs, vs - s))))
        ve = np.array([[float(a), float(b)] for a, b in
                       exactcore.core_corners(ke.kx, ke.ky, ke.cm, ke.sm, ke.a)], float)
        exc_e = float(max(0.0, np.max(np.maximum(-ve, ve - s))))
        cont.append(dict(box=j, excursion_poly=exc_p, excursion_exact=exc_e,
                         excursion_stock=exc_s,
                         margin_poly=float(np.min(np.minimum(V, s - V)))))
    rec["container"] = cont
    rec["kills_ii"] = any(c["excursion_poly"] > 0.0 for c in cont)

    # ---------------------------------------------------------------- (iii) K' vs K'
    pairs = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            dpp = polycore.poly_poly_depth(pcs[i].P, pcs[j].P)
            dss = polycore.poly_poly_depth(polycore.core_verts(stock[i]),
                                           polycore.core_verts(stock[j]))
            dee = polycore.poly_poly_depth(polycore.core_verts(exact[i]),
                                           polycore.core_verts(exact[j]))
            w = None
            if dpp > 0.0 and want_witness:
                w = polycore.overlap_witness(pcs[i], pcs[j])
            pairs.append(dict(i=i, j=j, depth_poly=float(dpp), depth_stock=float(dss),
                              depth_exact=float(dee), witness=w))
    rec["pairs"] = pairs
    rec["kills_iii"] = any(p["depth_poly"] > 0.0 for p in pairs)
    rec["kills_iii_exact"] = any(p["depth_exact"] > 0.0 for p in pairs)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", action="store_true", help="also measure every open k0 cell A115 lists")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t1_polycore.json"))
    a = ap.parse_args()

    t0 = time.time()
    out = {"twelve": [], "pool": [], "eps": EPS, "s0": S0}
    for meta in [dict(m) for m in
                 [C140.load_cell(c[0])[0] for c in C140.CELLS]]:
        _m, d = C140.load_cell(meta["cell"])
        r = measure(meta, d)
        out["twelve"].append(r)
        sup, pool = r["support"], r["pool"]
        print(f"{r['cell']:26s} boxes {r['n_boxes']}  tau {r['tau']:.9f} bud {r['budget']} "
              f"slack {r['slack']:+.2e}", flush=True)
        for b in r["boxes"]:
            print(f"     box th [{b['box'][4]:.3f},{b['box'][5]:.3f}] w{b['th_width']:.3f} deg | "
                  f"K' {b['poly_verts']} verts area {b['area_poly']:.6f} "
                  f"({b['ratio_poly_stock']:.3f}x K(a)) | a_stock {b['a_stock']:.6f} -> "
                  f"a_exact {b['a_exact']:.6f} ({b['ratio_exact_stock']:.3f}x area)", flush=True)
        print(f"     support: drawn {sup['n']} -> tested {sup['n']} -> "
              f"K(a) hits {sup['n_stock']}, exact-core hits {sup['n_exact']} "
              f"(+{sup['n_exact_only']} new, w {sup['w_exact_only']:.4f}), "
              f"K' hits {sup['n_poly']} (+{sup['n_poly_only']} new, w {sup['w_poly_only']:.4f}); "
              f"total w {sup['w']:.4f}", flush=True)
        print(f"     pool:    drawn {pool['n']} -> tested {pool['n']} -> K(a) {pool['n_stock']}, "
              f"exact {pool['n_exact']} (+{pool['n_exact_only']}), "
              f"K' {pool['n_poly']} (+{pool['n_poly_only']})", flush=True)
        print(f"     container: worst K' excursion "
              f"{max(c['excursion_poly'] for c in r['container']):+.3e}; "
              f"pairs: {'; '.join('%d-%d %.4f' % (p['i'], p['j'], p['depth_poly']) for p in r['pairs']) or 'n/a'}",
              flush=True)
        print(f"     VERDICT (i) {r['kills_i']} (exact-core only {r['kills_i_exact']}) "
              f"(ii) {r['kills_ii']} (iii) {r['kills_iii']}", flush=True)

    if a.pool:
        pool = C140.open_pool()
        print(f"\nopen k0 pool: {len(pool)} cells with a stored LP record", flush=True)
        for i, (nid, verdict, lp, run) in enumerate(pool):
            try:
                d = json.load(open(lp, encoding="utf-8"))
                if not (d.get("hyp") or {}).get("boxes"):
                    continue
                r = measure(dict(cell=nid, verdict=verdict, level=None,
                                 record=os.path.relpath(lp, ROOT), src="A115 open pool"),
                            d, want_witness=False)
            except Exception as e:                    # noqa: BLE001
                r = dict(cell=nid, verdict=verdict, error=repr(e)[:200])
            out["pool"].append(r)
            if (i + 1) % 25 == 0:
                print(f"  {i + 1}/{len(pool)}  {time.time() - t0:.0f} s", flush=True)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)
    print(f"\nwrote {a.out}  ({time.time() - t0:.1f} s)", flush=True)


if __name__ == "__main__":
    main()
