"""A145 -- controls on the measurement.

(A) REGRESSION against A142.  A142's gallery counted the same thing with a DIFFERENT implementation
    (pure-python `sat_poly` over an explicit 7^3 pose loop, and `meets_poly` / exact-pin-core SAT
    for the certified flag); A145 uses `polycore.poly_square_depth` vectorised over the grid.  The
    40 drawn A57 pages carry `n_support`, `n_impossible` and `n_impossible_certified`, so all three
    are compared node by node.  A disagreement is a bug in one of the two, not a finding.

(B) SAMPLED SOUNDNESS of the EXACT test.  For every column A145 calls impossible-by-K', draw random
    poses of the owning box and check by an INDEPENDENT float SAT (written here, not imported) that
    the column really does overlap the hypothesis square at each of them.  A hit is the failure that
    would make the whole measurement wrong; drawn -> tested -> hits is reported.

(C) THE GRID'S OWN ERROR.  Columns flagged by the 7^3 grid but NOT by K': search random poses of
    the box for a witness pose at which the two are DISJOINT.  Each witness found is a column the
    PI's grid reading over-claims, exhibited.

    set PYTHONDONTWRITEBYTECODE=1 && python code/check145.py
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A142 = os.path.join(ATT, "A142-a57-review-gallery")
sys.path.insert(0, HERE)
import measure145 as M                                        # noqa: E402


def sat_gap(P, Q):
    """independent SAT gap between two convex polygons: > 0 disjoint, < 0 overlapping."""
    best = -9e9
    for A, B in ((P, Q), (Q, P)):
        n = len(A)
        for i in range(n):
            a, b = A[i], A[(i + 1) % n]
            ex, ey = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ex, ey)
            if ln < 1e-15:
                continue
            ax, ay = -ey / ln, ex / ln
            pp = [x * ax + y * ay for x, y in A]
            qq = [x * ax + y * ay for x, y in B]
            best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def unit_sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def main():
    rows = {json.loads(l)["id"]: json.loads(l)
            for l in open(os.path.join(BASE, "results", "impossible_weight.jsonl"),
                          encoding="utf-8") if l.strip()}
    out = {}

    # ---------------------------------------------------------------- (A)
    g = json.load(open(os.path.join(A142, "results", "gallery142_A57_0_40.json"),
                       encoding="utf-8"))["summary"]
    n_cmp = n_sup = n_imp = n_cert = 0
    diffs = []
    for s in g:
        nid = s["id"]
        r = rows.get(nid)
        if r is None or r.get("status") != "ok":
            continue
        n_cmp += 1
        ok_s = (int(s["n_support"]) == r["n_support_meas"])
        ok_i = (int(s["n_impossible"]) == r["n_imposs_grid"])
        ok_c = (int(s["n_impossible_certified"]) == r["n_imposs_exact"])
        n_sup += ok_s
        n_imp += ok_i
        n_cert += ok_c
        if not (ok_s and ok_i and ok_c):
            diffs.append(dict(id=nid, a142=[s["n_support"], s["n_impossible"],
                                            s["n_impossible_certified"]],
                              a145=[r["n_support_meas"], r["n_imposs_grid"],
                                    r["n_imposs_exact"]]))
    out["A_regression_vs_A142"] = dict(compared=n_cmp, n_support_agree=n_sup,
                                       n_impossible_grid_agree=n_imp,
                                       n_impossible_exact_agree=n_cert, diffs=diffs)
    print(f"(A) {n_cmp} of A142's 40 drawn A57 pages compared: n_support {n_sup}/{n_cmp}, "
          f"grid-impossible {n_imp}/{n_cmp}, exact-impossible {n_cert}/{n_cmp}, "
          f"{len(diffs)} disagreements", flush=True)

    # ---------------------------------------------------------------- (B) and (C)
    rnd = random.Random(20260907)
    NP = 200
    drawn = tested = hits = 0
    gridonly = gridonly_witnessed = 0
    witnesses = []
    sample = [r for r in rows.values() if r.get("status") == "ok" and r.get("columns")]
    rnd.shuffle(sample)
    for r in sample[:120]:
        got = M.load_node(r["id"])
        if got is None:
            continue
        d, _ = got
        boxes = d["hyp"]["boxes"]
        pk = d.get("packing") or []
        for c in r["columns"]:
            p = pk[c["col"]]
            P = unit_sq(float(p["cx"]), float(p["cy"]), float(p["theta"]))
            if c["exact"]:
                b = boxes[c["exact_owner"]]
                drawn += 1
                for _ in range(NP):
                    hx = rnd.uniform(b["x0"], b["x1"])
                    hy = rnd.uniform(b["y0"], b["y1"])
                    ht = math.radians(rnd.uniform(b["th0"], b["th1"]))
                    tested += 1
                    if sat_gap(P, unit_sq(hx, hy, ht)) > 0.0:
                        hits += 1
                        witnesses.append(dict(kind="UNSOUND", id=r["id"], col=c["col"]))
            elif c["grid"]:
                gridonly += 1
                b = boxes[c["grid_owner"]]
                found = None
                for _ in range(4000):
                    hx = rnd.uniform(b["x0"], b["x1"])
                    hy = rnd.uniform(b["y0"], b["y1"])
                    ht = math.radians(rnd.uniform(b["th0"], b["th1"]))
                    if sat_gap(P, unit_sq(hx, hy, ht)) > 0.0:
                        found = [round(hx, 8), round(hy, 8), round(math.degrees(ht), 6)]
                        break
                if found:
                    gridonly_witnessed += 1
                    if len(witnesses) < 40:
                        witnesses.append(dict(kind="grid-overclaim", id=r["id"], col=c["col"],
                                              disjoint_pose=found))
    out["B_exact_soundness"] = dict(nodes=min(120, len(sample)), columns_drawn=drawn,
                                    poses_tested=tested, unsound_hits=hits)
    out["C_grid_overclaim"] = dict(grid_only_columns=gridonly,
                                   disjoint_pose_found=gridonly_witnessed,
                                   rate=(round(gridonly_witnessed / gridonly, 4)
                                         if gridonly else None))
    out["witnesses"] = witnesses[:40]
    print(f"(B) {drawn} exact-impossible columns x {NP} drawn poses = {tested} independent SAT "
          f"tests -> {hits} unsound", flush=True)
    print(f"(C) {gridonly} grid-only columns: a DISJOINT pose was found for "
          f"{gridonly_witnessed} of them "
          f"({(100.0 * gridonly_witnessed / gridonly) if gridonly else 0:.1f} %) -- "
          f"those are columns the 7^3 grid over-claims", flush=True)
    json.dump(out, open(os.path.join(BASE, "results", "check145.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
