"""A243 -- the PRICE by construction (notes/reach243.md s.4): grid counts of the summary domain, the type-F closed
forms' curves, the off-wall holder witness, and the fibre / core measurement that shows R3 cannot fire on a summary
cell until the cell is a pose box.  Writes results/reach243.jsonl (one record per item) and results/reach243.md.
One process, BelowNormal, affinity 0xFFFF; ~1-3 min.
"""
import json
import math
import os
import sys
import time

from shapely import affinity
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import leaves243 as L                                                   # noqa: E402

RES = os.path.join(BASE, "results")
JSONL = os.path.join(RES, "reach243.jsonl")
MD = os.path.join(RES, "reach243.md")


def be_polite():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x4000)
        k.SetProcessAffinityMask(h, ctypes.c_size_t(0xFFFF))
    except Exception:
        pass


def to_corner(P, corner, S, alternate=True):
    """map a BL-frame polygon to corner 'BL' | 'BR' | 'TL' | 'TR' of the container [0, S]^2; with `alternate` the
    BR and TL copies are the (u, v)-swapped crowd, i.e. A237's ALTERNATING window ring (floor / wall variants)."""
    if alternate and corner in ('BR', 'TL'):
        P = affinity.affine_transform(P, [0, 1, 1, 0, 0, 0])
    if corner == 'BL':
        return P
    if corner == 'BR':
        return affinity.affine_transform(P, [-1, 0, 0, 1, S, 0])
    if corner == 'TL':
        return affinity.affine_transform(P, [1, 0, 0, -1, 0, S])
    return affinity.affine_transform(P, [-1, 0, 0, -1, S, S])


def grids():
    rows = []
    for g in (4, 6, 8, 10):
        rows.append({"item": "grid", "g": g, "cells_8": L.grid_count(g, 8), "cells_16": L.grid_count(g, 16)})
    for h in (0.2, 0.1, 0.05, 0.02, 0.01):
        nr = math.ceil(L.SQ2 / (2 * h))                                  # reach in [1, 1 + sqrt 2)
        nd = math.ceil(1.0 / (2 * h))                                    # depth in (0, 1]
        Nc = nr * nr * nd * nd
        rows.append({"item": "grid_h", "h": h, "per_corner": Nc, "cells_16": Nc ** 4 / 8})
    return rows


def closed_forms():
    rows = []
    for s in (3.82, L.SHAT, 3.90, 3.95, 3.99, 4.0, 4.11):
        rows.append({"item": "theta_star", "s": s, "theta_star_deg": L.theta_star(s)})
    th_min = next(k / 100.0 for k in range(1, 9000) if L.lever_delta(k / 100.0) <= 1.0)
    rows.append({"item": "lever_branch", "theta_min_deg": th_min})
    for th in (57.2, 60.0, 70.0, 80.0, 89.0):
        d = L.lever_delta(th)
        rows.append({"item": "lever_reach", "theta_deg": th, "delta": d, "R": L.reach_F(th, d),
                     "needs_side": 2 + L.reach_F(th, d)})
    # timing of the closed-form leaf (microseconds per evaluation)
    t0 = time.perf_counter()
    acc = 0.0
    for k in range(200000):
        acc += L.reach_F(1 + (k % 880) / 10.0, 0.5 + (k % 49) / 100.0)
    rows.append({"item": "closed_form_us", "us_per_eval": (time.perf_counter() - t0) / 200000 * 1e6})
    return rows


def holder():
    A, C, f, ov, ylow = L.holder_witness()
    return [{"item": "holder_witness", "A": A, "C": C, "force_on_A": f, "overlap_area": ov, "C_lowest_vertex_v": ylow,
             "C_meets_box": L.meets_box(C), "C_touches_floor": ylow <= 1e-9}]


def fibre_rows(S=L.SHAT, theta=20.0, margin=0.02):
    """the window ring's crowd at (theta, delta = sin theta + margin) as the cell centre; for each half-width h the
    sampled fibre, the two role cores' OUTER bounds, and the three-free witness on the container minus the eight
    cores placed at the four corners."""
    A, B = L.pair_F(theta, math.sin(theta * L.DEG) + margin)
    base = L.summary(A, B)
    rows = [{"item": "fibre_base", "S": S, "theta": theta, "delta": math.sin(theta * L.DEG) + margin, "A": A, "B": B,
             "summary": base}]
    # h = 0: the exact ring; the pocket is the container minus the eight bodies (A237: capacity 1)
    bodies = [to_corner(L.poly(P), c, S) for c in ('BL', 'BR', 'TL', 'TR') for P in (A, B)]
    t0 = time.perf_counter()
    w0 = L.three_free_witness(bodies, S)
    rows.append({"item": "fibre", "h": 0.0, "n": 1, "acceptance": 1.0, "core_deep_area": L.poly(A).area
                 if L.depth(A) >= L.depth(B) else L.poly(B).area, "core_shallow_area": 1.0, "three_free": len(w0),
                 "sec": time.perf_counter() - t0})
    for h in (0.2, 0.1, 0.05, 0.02, 0.01):
        t0 = time.perf_counter()
        cell = L.cell_around(A, B, h)
        pairs, acc = L.sample_fibre(cell, 200, seed=int(h * 1000), tries=1500000)
        cd = L.core_outer(pairs, 'deep') if pairs else None
        cs = L.core_outer(pairs, 'shallow') if pairs else None
        obs = []
        for c in ('BL', 'BR', 'TL', 'TR'):
            for P in (cd, cs):
                if P is not None and not P.is_empty and P.area > 0:
                    obs.append(to_corner(P, c, S))
        w = L.three_free_witness(obs, S)
        rows.append({"item": "fibre", "h": h, "cell": cell, "n": len(pairs), "acceptance": acc,
                     "core_deep_area": (cd.area if cd is not None else None),
                     "core_shallow_area": (cs.area if cs is not None else None),
                     "core_deep_wkt": (cd.wkt if cd is not None and not cd.is_empty else ""),
                     "core_shallow_wkt": (cs.wkt if cs is not None and not cs.is_empty else ""),
                     "three_free": len(w), "witness": [list(q.bounds) for q in w],
                     "sample": [[list(P), list(Q)] for P, Q in pairs[:6]], "sec": time.perf_counter() - t0})
        print("h=%.3f n=%d acc=%.2e core_deep=%.4f core_shallow=%.4f three_free=%d (%.1fs)" % (
            h, len(pairs), acc, cd.area if cd is not None else -1, cs.area if cs is not None else -1, len(w),
            rows[-1]["sec"]), flush=True)
    return rows


def generic_rows(n=8000, seed=7):
    """random crowds binned by their summary at cell width 2h: per occupied bin (>= 20 members) the OUTER bound on
    the deeper role's core from the bin's members.  How thin is a generic fibre?"""
    t0 = time.perf_counter()
    crowds = L.random_crowds(n, seed=seed, tries=15000000)
    rows = []
    for h in (0.2, 0.1):
        bins = {}
        for A, B in crowds:
            key = tuple(int(x // (2 * h)) for x in L.summary(A, B))
            bins.setdefault(key, []).append((A, B))
        full = {k: v for k, v in bins.items() if len(v) >= 20}
        areas = []
        for k, v in full.items():
            cd = L.core_outer(v[:60], 'deep')
            areas.append(cd.area if cd is not None and not cd.is_empty else 0.0)
        areas.sort()
        rows.append({"item": "generic", "h": h, "crowds": len(crowds), "occupied_bins": len(bins),
                     "bins_ge20": len(full), "core_deep_median": areas[len(areas) // 2] if areas else None,
                     "core_deep_max": areas[-1] if areas else None,
                     "frac_core_lt_0.05": sum(a < 0.05 for a in areas) / max(1, len(areas)),
                     "frac_core_gt_0.3": sum(a > 0.3 for a in areas) / max(1, len(areas)),
                     "sec": time.perf_counter() - t0})
        print(rows[-1], flush=True)
    return rows


def write_md(rows):
    g = [r for r in rows if r["item"] == "grid"]
    gh = [r for r in rows if r["item"] == "grid_h"]
    ts = [r for r in rows if r["item"] == "theta_star"]
    lv = [r for r in rows if r["item"] == "lever_reach"]
    fb = [r for r in rows if r["item"] == "fibre"]
    hw = next(r for r in rows if r["item"] == "holder_witness")
    cf = next(r for r in rows if r["item"] == "closed_form_us")
    out = ["# A243 -- the reach-summary root, priced by construction (generated by `code/price243.py`)", "",
           "Design and soundness: `notes/reach243.md`.  Every number below is [M] or [T computed]; none is a kill.", "",
           "## 1. The summary domain's cell counts (D4 quotient /8 taken; a product grid is D4-equivariant)", "",
           "| grid g | 8 coordinates (reaches only) g^8/8 | 16 coordinates (reaches + depths) g^16/8 |", "|---|---|---|"]
    out += ["| %d | %.2e | %.2e |" % (r["g"], r["cells_8"], r["cells_16"]) for r in g]
    out += ["", "| cell half-width h | per-corner cells | four-corner cells /8 |", "|---|---|---|"]
    out += ["| %.2f | %d | %.2e |" % (r["h"], r["per_corner"], r["cells_16"]) for r in gh]
    out += ["", "## 2. The type-F closed forms (A239 REACH / LEVER), as curves in the (theta, delta) plane", "",
            "| s | theta* (least offset delta = sin theta + 0.02) |", "|---|---|"]
    out += ["| %.4f | %s |" % (r["s"], ("%.2f" % r["theta_star_deg"]) if r["theta_star_deg"] else "never") for r in ts]
    out += ["", "LEVER's admissible branch (delta = sin theta + cos^3 theta <= 1): theta >= %.2f deg." %
            next(r["theta_min_deg"] for r in rows if r["item"] == "lever_branch"), "",
            "| theta | delta (LEVER) | R | side needed for a contact ring 2 + R |", "|---|---|---|---|"]
    out += ["| %.1f | %.4f | %.4f | %.4f |" % (r["theta_deg"], r["delta"], r["R"], r["needs_side"]) for r in lv]
    out += ["", "Closed-form leaf cost: %.2f microseconds per evaluation." % cf["us_per_eval"], "",
            "## 3. R1's missing lemma: an along-wall holder that is not a wall member (`leaves243.holder_witness`)", "",
            "A = flat floor meeter at offset 0.36; C's edge through A's corner (1.36, 1): force of C on A = (%.4f, %.4f) "
            "(F_u < 0: a Lemma-HOLD holder along the floor), overlap %.1e, C's lowest vertex at v = %.4f > 0, C meets "
            "the corner box: %s." % (hw["force_on_A"][0], hw["force_on_A"][1], hw["overlap_area"],
                                     hw["C_lowest_vertex_v"], hw["C_meets_box"]), "",
            "## 4. R3 on a summary cell: the fibre's cores and the three-free witness", "",
            "Cell centre: the window ring's crowd at s-hat, theta = 20 deg, delta = sin 20 + 0.02.  Cores are OUTER "
            "bounds (intersection over the sampled fibre); a three-free witness (three flat unit squares in the container "
            "avoiding every core) proves the no-room leaf with m = 3 cannot fire on the cell.", "",
            "| h | fibre samples | acceptance | core area, deeper role | core area, shallower role | three free squares found | s |",
            "|---|---|---|---|---|---|---|"]
    for r in fb:
        out.append("| %.2f | %d | %.1e | %s | %s | %d | %.1f |" % (
            r["h"], r["n"], r["acceptance"], "%.4f" % r["core_deep_area"] if r["core_deep_area"] is not None else "-",
            "%.4f" % r["core_shallow_area"] if r["core_shallow_area"] is not None else "-", r["three_free"], r["sec"]))
    out += ["", "## 5. Generic fibres: random crowds binned by summary, the deeper role's core (outer bound) per bin", "",
            "| h | random crowds | occupied bins | bins with >= 20 members | median core area | max | fraction < 0.05 | fraction > 0.3 |",
            "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["item"] == "generic":
            out.append("| %.2f | %d | %d | %d | %.4f | %.4f | %.2f | %.2f |" % (
                r["h"], r["crowds"], r["occupied_bins"], r["bins_ge20"], r["core_deep_median"] or 0, r["core_deep_max"] or 0,
                r["frac_core_lt_0.05"], r["frac_core_gt_0.3"]))
    out.append("")
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main():
    be_polite()
    os.makedirs(RES, exist_ok=True)
    rows = grids() + closed_forms() + holder() + fibre_rows() + generic_rows()
    with open(JSONL, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    write_md(rows)
    print("wrote", JSONL, MD)


if __name__ == "__main__":
    main()
