"""
A53: residual tight-variety map on Trump's skeleton (A33 t2 mapper pattern, FLOAT, labelled).

Loads the trump5 node result (guard field = LP atoms), sweeps the placement space
(theta, cx, cy), drops placements that SAT-collide with the pinned skeleton squares
(exact pins, float SAT with outward slop -> conservative toward keeping), and maps
T_eta = { residual placements : mu(Q) <= 1 + eta }. Reports volume fractions, cluster
structure, and localization vs Trump's own six free squares. FLOAT diagnostic map --
not a certificate (the exact analogue is A33 t2 mapper mode=exact; out of pilot scope).
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
S0 = 969271 / 250000

def cover_counts(A, W, C, theta):
    """mass covered by unit square at centres C (m,2), orientation theta, from atoms A (n,2), W."""
    c, s = math.cos(theta), math.sin(theta)
    d0 = A[None, :, 0] - C[:, None, 0]
    d1 = A[None, :, 1] - C[:, None, 1]
    u = np.abs(d0 * c + d1 * s)
    v = np.abs(-d0 * s + d1 * c)
    inside = (u <= 0.5 + 1e-12) & (v <= 0.5 + 1e-12)
    return inside @ W

def collide_any(pins, C, theta):
    """SAT overlap (depth > slop) of Q(C, theta) with any pinned axis-aligned unit square."""
    c, s = math.cos(theta), math.sin(theta)
    g = abs(c) + abs(s)
    bad = np.zeros(len(C), bool)
    for (px, py) in pins:
        d0 = C[:, 0] - px; d1 = C[:, 1] - py
        de = np.minimum(0.5 + 0.5 * g - np.abs(d0), 0.5 + 0.5 * g - np.abs(d1))
        pf1 = np.abs(d0 * c + d1 * s); pf2 = np.abs(-d0 * s + d1 * c)
        df = np.minimum(0.5 + 0.5 * g - pf1, 0.5 + 0.5 * g - pf2)
        bad |= np.minimum(de, df) > 1e-9   # positive-depth overlap on every axis
    return bad

def main():
    node = json.load(open(os.path.join(BASE, "results", "nodes", "trump5.json")))
    pins = [tuple(p) for p in node["skeleton_slots"]]
    A = np.array([[a[0], a[1]] for a in node["atoms_all"]], float)
    W = np.array([a[2] for a in node["atoms_all"]], float)
    tau = node["tau"]
    print(f"trump5: tau={tau:.6f} budget={node['budget']} atoms>0={len(A)}")
    # Trump's own six free squares (float, A03), embedded at bottom-left of the s0 box
    trump = json.load(open(os.path.join(BASE, "..", "A03-upper-reconstruct", "trump11_float.json")))
    free = [trump["X"][i] for i in (4, 6, 7, 8, 9, 10)]
    etas = [0.02, 0.05, 0.10]
    step = 0.02
    th_step_deg = 1.0
    rows = []
    n_res_tot = 0
    tight_pts = {e: [] for e in etas}
    for thd in np.arange(0, 90 + 1e-9, th_step_deg):
        th = math.radians(thd)
        w = (math.cos(th) + math.sin(th)) / 2
        lo, hi = w, S0 - w
        xs = np.arange(lo, hi + 1e-12, step)
        Cx, Cy = np.meshgrid(xs, xs)
        C = np.stack([Cx.ravel(), Cy.ravel()], 1)
        keep = ~collide_any(pins, C, th)
        C = C[keep]
        n_res_tot += len(C)
        if not len(C):
            continue
        cov = cover_counts(A, W, C, th)
        for e in etas:
            m = cov <= 1 + e
            if m.any():
                P = C[m]
                tight_pts[e].append(np.column_stack([P, np.full(len(P), thd)]))
    out = {"tau": tau, "budget": node["budget"], "eta_residual": tau - node["budget"],
           "grid": {"cstep": step, "theta_step_deg": th_step_deg},
           "n_residual_placements": int(n_res_tot), "etas": {}}
    for e in etas:
        pts = np.vstack(tight_pts[e]) if tight_pts[e] else np.zeros((0, 3))
        rec = {"n_tight": int(len(pts)), "frac": float(len(pts)) / max(n_res_tot, 1)}
        if len(pts):
            rec["cx_range"] = [float(pts[:, 0].min()), float(pts[:, 0].max())]
            rec["cy_range"] = [float(pts[:, 1].min()), float(pts[:, 1].max())]
            thetas = sorted(set(pts[:, 2]))
            rec["theta_deg_values"] = [float(t) for t in thetas[:40]]
            # distance of each Trump free square to the tight set (position + 5deg-scaled angle)
            dloc = []
            for (fx, fy, fth) in free:
                fthd = math.degrees(fth) % 90
                d = np.sqrt((pts[:, 0] - fx) ** 2 + (pts[:, 1] - fy) ** 2 +
                            ((pts[:, 2] - fthd) / 57.29578) ** 2)
                dloc.append(float(d.min()))
            rec["dist_trump_free_squares"] = dloc
            # crude clustering: round to 0.15 / 5 deg boxes
            cl = set()
            for p in pts:
                cl.add((round(p[0] / 0.15), round(p[1] / 0.15), round(p[2] / 5)))
            rec["n_clusters_015_5deg"] = len(cl)
        out["etas"][str(e)] = rec
        print(f"eta={e}: tight {rec['n_tight']}/{n_res_tot} = {rec['frac']:.4f}",
              rec.get("cx_range"), rec.get("cy_range"), "clusters:", rec.get("n_clusters_015_5deg"),
              "dist to Trump free squares:", [f"{x:.3f}" for x in rec.get("dist_trump_free_squares", [])])
    json.dump(out, open(os.path.join(BASE, "results", "trump5_tightmap.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
