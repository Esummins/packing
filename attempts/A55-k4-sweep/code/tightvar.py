"""
A55: TIGHT-VARIETY CHARACTERIZATION of a surviving node (A53 residual_tightmap generalised).

For a node result (pins + guard field mu = the LP atoms with positive weight) sweep the residual
placement space (cx, cy, theta), drop placements that SAT-collide with a pin, and map

    T_eta = { residual placements Q : mu(Q) <= 1 + eta }        (the tight variety)

Reported per eta: volume fraction of the residual, cx/cy/theta extent, cluster count at
0.15 x 0.15 x 5 deg resolution, the coarse-zone split of the tight mass, and

    COVERAGE NUMBER  nu(eta) = the largest set of PAIRWISE INTERIOR-DISJOINT placements found
                     inside T_eta (greedy + randomised restarts, exact-pin-clear, SAT margin).

nu(eta) >= budget is the integral dual witness of A54's alive.py: the node cannot be killed by
any guard measure, because budget disjoint placements each need mass >= 1.  nu(eta) < budget is
inconclusive (a search, not a proof).  FLOAT diagnostic throughout; arbiters unchanged.
"""
import argparse, json, math, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from substrat import zones
S0 = 969271 / 250000
ZORDER = ["interior", "side_L", "side_B", "side_R", "side_T",
          "corner_BL", "corner_BR", "corner_TR", "corner_TL"]


def load_node(name):
    for p in (os.path.join(BASE, "results", "nodes", f"{name}.json"),
              os.path.join(A53, "results", "nodes", f"{name}.json")):
        if os.path.exists(p):
            return json.load(open(p)), p
    raise SystemExit(f"no node json for {name}")


def cover_counts(A, W, C, theta):
    c, s = math.cos(theta), math.sin(theta)
    d0 = A[None, :, 0] - C[:, None, 0]
    d1 = A[None, :, 1] - C[:, None, 1]
    u = np.abs(d0 * c + d1 * s); v = np.abs(-d0 * s + d1 * c)
    return ((u <= 0.5 + 1e-12) & (v <= 0.5 + 1e-12)) @ W


def collide_any(pins, C, theta):
    c, s = math.cos(theta), math.sin(theta)
    g = abs(c) + abs(s)
    bad = np.zeros(len(C), bool)
    for (px, py) in pins:
        d0 = C[:, 0] - px; d1 = C[:, 1] - py
        de = np.minimum(0.5 + 0.5 * g - np.abs(d0), 0.5 + 0.5 * g - np.abs(d1))
        pf1 = np.abs(d0 * c + d1 * s); pf2 = np.abs(-d0 * s + d1 * c)
        df = np.minimum(0.5 + 0.5 * g - pf1, 0.5 + 0.5 * g - pf2)
        bad |= np.minimum(de, df) > 1e-9
    return bad


def sat_gap(c1, t1, c2, t2):
    best = -1e9
    for (cc, tt, oc, ot) in ((c1, t1, c2, t2), (c2, t2, c1, t1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = (abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) +
                 abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot)))
            best = max(best, d - 0.5 - 0.5 * g)
    return best


def coverage_number(P, pins, budget, margin, pool, restarts, seed):
    """largest pairwise-disjoint subset found among tight placements P=(m,3) [cx,cy,thdeg]"""
    rng = random.Random(seed)
    idx = list(range(len(P)))
    if len(idx) > pool:
        idx = rng.sample(idx, pool)
    ok = []
    for i in idx:
        cx, cy, thd = P[i]
        th = math.radians(thd)
        if min(sat_gap((cx, cy), th, p, 0.0) for p in pins) < margin:
            continue
        ok.append((cx, cy, th))
    n = len(ok)
    if n == 0:
        return 0, [], None
    G = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i + 1, n):
            G[i, j] = G[j, i] = sat_gap(ok[i][:2], ok[i][2], ok[j][:2], ok[j][2]) >= margin
    best = []
    order0 = list(range(n))
    for r in range(restarts):
        order = order0 if r == 0 else rng.sample(order0, n)
        sel = []
        for i in order:
            if all(G[i, j] for j in sel):
                sel.append(i)
                if len(sel) >= budget:
                    break
        if len(sel) > len(best):
            best = list(sel)
            if len(best) >= budget:
                break
    gmin = min([sat_gap(ok[i][:2], ok[i][2], ok[j][:2], ok[j][2])
                for a_, i in enumerate(best) for j in best[a_ + 1:]] or [float("inf")])
    return len(best), [dict(cx=ok[i][0], cy=ok[i][1], theta_deg=math.degrees(ok[i][2])) for i in best], gmin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", required=True)
    ap.add_argument("--etas", default="0.02,0.05,0.10")
    ap.add_argument("--step", type=float, default=0.02)
    ap.add_argument("--th_step", type=float, default=1.0)
    ap.add_argument("--margin", type=float, default=1e-6)
    ap.add_argument("--pool", type=int, default=1200)
    ap.add_argument("--restarts", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "tightvar.json"))
    a = ap.parse_args()
    etas = [float(x) for x in a.etas.split(",")]
    Z = zones(S0, 0.6)
    allout = {}
    for name in a.names.split(","):
        node, pth = load_node(name)
        pins = [tuple(p) for p in node["skeleton_slots"]]
        budget = node["budget"]
        A = np.array([[x[0], x[1]] for x in node["atoms_all"]], float)
        W = np.array([x[2] for x in node["atoms_all"]], float)
        n_res = 0
        tight = {e: [] for e in etas}
        for thd in np.arange(0, 90 + 1e-9, a.th_step):
            th = math.radians(thd)
            w = (math.cos(th) + math.sin(th)) / 2
            xs = np.arange(w, S0 - w + 1e-12, a.step)
            Cx, Cy = np.meshgrid(xs, xs)
            C = np.stack([Cx.ravel(), Cy.ravel()], 1)
            C = C[~collide_any(pins, C, th)]
            n_res += len(C)
            if not len(C):
                continue
            cov = cover_counts(A, W, C, th)
            for e in etas:
                m = cov <= 1 + e
                if m.any():
                    P = C[m]
                    tight[e].append(np.column_stack([P, np.full(len(P), thd)]))
        rec = dict(node=os.path.relpath(pth, BASE), tau=node["tau"], budget=budget,
                   eta_residual=node["tau"] - budget, n_residual_placements=int(n_res),
                   grid=dict(cstep=a.step, theta_step_deg=a.th_step), etas={})
        print(f"{name}: tau={node['tau']:.6f} budget={budget} residual grid pts={n_res}")
        for e in etas:
            pts = np.vstack(tight[e]) if tight[e] else np.zeros((0, 3))
            r = dict(n_tight=int(len(pts)), frac=float(len(pts)) / max(n_res, 1))
            if len(pts):
                r["cx_range"] = [float(pts[:, 0].min()), float(pts[:, 0].max())]
                r["cy_range"] = [float(pts[:, 1].min()), float(pts[:, 1].max())]
                r["theta_range_deg"] = [float(pts[:, 2].min()), float(pts[:, 2].max())]
                r["frac_tilted_5_85"] = float(np.mean((pts[:, 2] >= 5) & (pts[:, 2] <= 85)))
                cl = set((round(p[0] / 0.15), round(p[1] / 0.15), round(p[2] / 5)) for p in pts)
                r["n_clusters_015_5deg"] = len(cl)
                zc = {z: 0 for z in ZORDER}
                for p in pts:
                    for z in ZORDER:
                        x0, x1, y0, y1 = Z[z]
                        if x0 - 1e-9 <= p[0] <= x1 + 1e-9 and y0 - 1e-9 <= p[1] <= y1 + 1e-9:
                            zc[z] += 1; break
                r["zone_counts"] = zc
                nu, pl, gmin = coverage_number(pts, pins, budget, a.margin, a.pool, a.restarts, a.seed)
                r["coverage_number"] = nu
                r["coverage_placements"] = pl
                r["min_pairwise_sat_gap"] = (None if gmin is None or gmin == float("inf") else gmin)
                r["verdict"] = ("ALIVE: tau* >= budget (integral dual witness inside T_eta)"
                                if nu >= budget else f"inconclusive ({nu}/{budget} disjoint)")
            rec["etas"][str(e)] = r
            print(f"  eta={e}: tight {r['n_tight']}/{n_res} = {r['frac']:.4f}  "
                  f"clusters={r.get('n_clusters_015_5deg')}  tilted={r.get('frac_tilted_5_85')}  "
                  f"nu={r.get('coverage_number')}/{budget}  {r.get('verdict','')}")
        allout[name] = rec
    json.dump(allout, open(a.out, "w"), indent=1)
    print("->", os.path.relpath(a.out, BASE))


if __name__ == "__main__":
    main()
