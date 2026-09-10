"""A186 step 3 (the stuck configurations) -- LP DESCENT from the lowest closed leaves of tree186.

A leaf of the selection tree = (tilt cell K, one selection per near pair, q-range splits).  At FIXED
tilts the leaf's rows are affine (Lemma LEAF): the exact LP `min s` gives the leaf's minimal side at
those tilts and, by LP duality, the multipliers = the contact-force system = the SUPPORT GRAPH of the
stuck configuration (Lemma GRAIN-LP).  Centre boxes for the descent: the hull of the pieces meeting K
widened by 1 deg of tilt (a fixed box; the final pose is tested against the PIECES separately).  The
descent minimises the small-cell relaxed value (cell tv +- 0.025 deg, second-order loss) over the tilts
by Nelder-Mead from the leaf LP's own tilt point, re-selects every pair's row to its best separating
axis at the optimum, repeats until stable, then solves the exact LP at the final tilts.  Result per
leaf: the configuration z*, its side s* (exact LP value), check_packing(z*), 'inside the pieces', the LP
support, the structure counts.  [M]: an UPPER bound on the leaf's minimum; the drawn configuration is a
real packing of the boxed squares at side s* whenever check_packing passes; s* <= s0 with every pose
inside the pieces would be a WITNESS.

    python descend186.py [--leaves 8] [--index k]     -> results/descend186.jsonl
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodes186 as N                                          # noqa: E402
import tree186 as T                                           # noqa: E402  (installs build_lp_pieces)
A, S0 = N.A, N.S0
SHAT = A.SHAT
HW = math.radians(0.025)
WIDEN = math.radians(0.25)
M_ELASTIC = 50.0


def solve_elastic(R, M=M_ELASTIC):
    """R's LP with every selection row relaxed by a common slack tau >= 0 (g + tau >= 0), objective
    s + M tau: finite wherever the boxes are non-empty; tau* = 0 iff the leaf polyhedron is non-empty.
    -> (s, tau, x, y) with y the multipliers of R's rows (the support)."""
    from scipy.optimize import linprog
    n = R.nv
    A_ = np.array(R.A) if R.A else np.zeros((0, n)); b_ = np.array(R.b) if R.b else np.zeros(0)
    col = np.array([[-1.0 if m[0] == "sel" else 0.0] for m in R.meta]) if len(R.meta) else np.zeros((0, 1))
    A2 = np.hstack([A_, col])
    c = np.zeros(n + 1); c[0] = 1.0; c[n] = M
    res = linprog(c, A_ub=A2, b_ub=b_, bounds=list(R.bounds) + [(0.0, None)], method="highs")
    if not res.success:
        return math.inf, math.inf, None, None
    y = -res.ineqlin.marginals if len(R.A) else np.zeros(0)
    return float(res.x[0]), float(res.x[n]), res.x[:n], y


class Leaf:
    def __init__(self, rec, leaf):
        self.pbodies, self.nv = N.build_bodies(rec)
        self.idx = {b.name: k for k, b in enumerate(self.pbodies)}
        self.cells = {n: (math.radians(a), math.radians(b)) for n, (a, b) in leaf["cells"].items()}
        self.fixed = {}
        for key, sel in leaf["fixed"].items():
            a, b = key.split("|")
            self.fixed[(self.idx[a], self.idx[b])] = tuple(sel)
        self.qr = {}
        for key, rg in (leaf.get("qranges") or {}).items():
            a, b = key.split("|"); self.qr[(self.idx[a], self.idx[b])] = tuple(rg)
        # fixed centre boxes: hull of the pieces meeting the widened cell
        self.bodies, self.ok = [], True
        for b in self.pbodies:
            if isinstance(b, N.PieceBody):
                c = self.cells[b.name]
                wc = (max(b.t0, c[0] - WIDEN), min(b.t1, c[1] + WIDEN))
                bx = b.box_for(wc)
                if bx is None:
                    self.ok = False; bx = (0, 1, 0, 1)
                self.bodies.append(A.Body(b.name, "free", x0=bx[0], x1=bx[1], y0=bx[2], y1=bx[3], t0=wc[0], t1=wc[1],
                                          vi=b.vi, ti=b.ti, anchor=b.anchor))
            else:
                self.bodies.append(b)
        self.free = [b for b in self.bodies if b.kind == "free"]
        self.pfree = {b.name: b for b in self.pbodies if b.kind == "free"}

    def lp(self, theta, fixed):
        """exact rows at tilts theta, elastic: (s, tau, x, y, R)."""
        R = A.build_lp(self.bodies, self.nv, S0, S0 + 0.3, fixed, cells={n: (t, t) for n, t in theta.items()},
                       exact_theta=theta)
        s, tau, x, y = solve_elastic(R)
        return s, tau, x, y, R

    def relaxed(self, tv, fixed, qranges=None):
        """relaxed rows over the small cell tv +- HW, elastic: (s, tau, x, y, R)."""
        cells = {b.name: (max(b.t0, float(tv[k]) - HW), min(b.t1, float(tv[k]) + HW)) for k, b in enumerate(self.free)}
        if any(c[0] > c[1] for c in cells.values()):
            return math.inf, math.inf, None, None, None
        R = A.build_lp(self.bodies, self.nv, S0, S0 + 0.3, fixed, cells=cells, qranges=qranges)
        s, tau, x, y = solve_elastic(R)
        return s, tau, x, y, R

    def leaf_start(self):
        R = A.build_lp(self.bodies, self.nv, S0, S0 + 0.3, self.fixed, cells=self.cells, qranges=self.qr)
        s, tau, x, y = solve_elastic(R)
        if x is None:
            return None, (s, tau)
        return np.array([x[b.ti] for b in self.free]), (s, tau)

    def reselect(self, theta, x, fixed):
        s, cfg = A.config_from_x(self.bodies, x, theta)
        new = dict(fixed)
        nb = len(self.bodies)
        for i in range(nb):
            for j in range(i + 1, nb):
                if self.bodies[i].kind == "pin" and self.bodies[j].kind == "pin":
                    continue
                pi, pj = cfg[self.bodies[i].name], cfg[self.bodies[j].name]
                gs = [(A.gap_sel(pi[:2], pi[2], pj[:2], pj[2], o, k, e), (o, k, e)) for (o, k, e) in A.SELS]
                best, bsel = max(gs)
                old = new.get((i, j))
                if old is None or A.gap_sel(pi[:2], pi[2], pj[:2], pj[2], *old) < best - 1e-9:
                    new[(i, j)] = bsel
        return new

    def inside_pieces(self, cfg):
        out = {}
        for n, b in self.pfree.items():
            cx, cy, th = cfg[n]
            out[n] = any(p[0] - 1e-9 <= cx <= p[1] + 1e-9 and p[2] - 1e-9 <= cy <= p[3] + 1e-9
                         and p[4] - 1e-9 <= th <= p[5] + 1e-9 for p in b.pieces)
        return out

    def descend(self, rounds=4):
        if not self.ok:
            return dict(ok=False, why="no piece in the cell")
        tv, (s_leaf, tau_leaf) = self.leaf_start()
        if tv is None:
            return dict(ok=False, why="leaf LP infeasible")
        bnds = [(b.t0, b.t1) for b in self.free]
        fixed = dict(self.fixed)
        hist = [[float(s_leaf), float(tau_leaf)]]

        def f(v):
            if any(v[k] < bnds[k][0] - 1e-12 or v[k] > bnds[k][1] + 1e-12 for k in range(len(v))):
                return math.inf
            s, tau = self.relaxed(v, fixed)[:2]
            return s + M_ELASTIC * tau
        step = math.radians(0.3)
        for r in range(rounds):
            sim = [np.array(tv)]
            for k in range(len(tv)):
                e = np.array(tv); a, b = bnds[k]
                e[k] = e[k] + step if e[k] + step <= b else e[k] - step
                sim.append(e)
            res = minimize(f, tv, method="Nelder-Mead",
                           options=dict(initial_simplex=np.array(sim), xatol=1e-7, fatol=1e-12, maxfev=5000))
            if not np.isfinite(res.fun):
                break
            tv = res.x
            s, tau, x, y, R = self.relaxed(tv, fixed)
            hist.append([float(s), float(tau)])
            if x is None:
                break
            theta = {b.name: float(x[b.ti]) for b in self.free}
            new = self.reselect(theta, x, fixed)
            if new == fixed:
                break
            fixed = new
        s0_, tau0, x0, y0, R0 = self.relaxed(tv, fixed)
        cands = []
        if x0 is not None:
            cands.append({b.name: float(x0[b.ti]) for b in self.free})
        cands.append({b.name: float(tv[k]) for k, b in enumerate(self.free)})
        best = None
        for theta in cands:
            s, tau, x, y, R = self.lp(theta, fixed)
            if x is not None and (best is None or s + M_ELASTIC * tau < best[0] + M_ELASTIC * best[1]):
                best = (s, tau, x, y, R, theta)
        if best is None:
            return dict(ok=False, why="exact LP infeasible at the descended tilts", history=hist)
        s, tau, x, y, R, theta = best
        s_, cfg = A.config_from_x(self.bodies, x, theta)
        wp, ww = A.check_packing(s_, cfg)
        inside = self.inside_pieces(cfg)
        sup = R.support(y) if y is not None else []
        return dict(ok=True, side=s, tau=tau, side_minus_s0=s - S0, side_minus_shat=s - SHAT, worst_pair=wp,
                    worst_wall=ww, packing=bool(wp >= -1e-7 and ww >= -1e-7), inside=inside,
                    all_inside=all(inside.values()), widen_deg=math.degrees(WIDEN),
                    cfg={n: [p[0], p[1], math.degrees(p[2])] for n, p in cfg.items()},
                    fixed={"%s|%s" % (self.bodies[i].name, self.bodies[j].name): list(s2) for (i, j), s2 in fixed.items()},
                    support=[[list(m), w] for m, w in sup], history=hist, structure=structure(self, sup))


def structure(leaf, sup):
    deg = {b.name: 0 for b in leaf.free}
    edges = set()
    for m, w in sup:
        if m[0] == "sel":
            edges.add((m[1], m[2]))
            for a in (m[1], m[2]):
                if a in deg:
                    deg[a] += 1
        elif m[0] == "wall":
            edges.add((m[1], "W" + m[2]))
            if m[1] in deg:
                deg[m[1]] += 1
    loaded = [b for b, d in deg.items() if d > 0]
    return dict(deg=deg, loaded=loaded, L1=all(deg[b] >= 2 for b in loaded), k_H=len(loaded), m_H=len(sup),
                edges=sorted(edges))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leaves", type=int, default=8)
    ap.add_argument("--index", type=int, default=None)
    args = ap.parse_args()
    recs = N.load_records()
    items = sorted(recs.items(), key=lambda kv: (-len(kv[1]["roles"]), kv[0]))
    rows = {}
    for l in open(os.path.join(N.RES, "tree186.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r.get("lowest_leaves"):
            rows[r["index"]] = r
    out = open(os.path.join(N.RES, "descend186.jsonl"), "a", encoding="utf-8")
    for k, r in sorted(rows.items()):
        if args.index is not None and k != args.index:
            continue
        rec = items[k][1]
        t0 = time.time()
        res = []
        for leaf in r["lowest_leaves"][:args.leaves]:
            d = Leaf(rec, leaf).descend()
            d["leaf_value"] = leaf["value"]
            res.append(d)
        res.sort(key=lambda d: d.get("side", math.inf))
        row = dict(index=k, short=r["short"], label=r["label"], budget=r["budget"], n_leaves=len(res), results=res,
                   seconds=round(time.time() - t0, 1), when=time.strftime("%Y-%m-%d %H:%M:%S"))
        out.write(json.dumps(row) + "\n"); out.flush()
        print("%s (%.0fs)" % (r["short"], row["seconds"]), flush=True)
        for d in res[:6]:
            if not d.get("ok"):
                print("   leaf %.6f: %s %s" % (d["leaf_value"], d.get("why"), d.get("history")), flush=True); continue
            print("   leaf %.6f -> s* %.7f tau %.1e (s0 %+.2e) packing %s inside %s  k_H %d m_H %d L1 %s  %s" %
                  (d["leaf_value"], d["side"], d["tau"], d["side_minus_s0"], d["packing"],
                   "ALL" if d["all_inside"] else "".join(n for n, v in d["inside"].items() if not v),
                   d["structure"]["k_H"], d["structure"]["m_H"], d["structure"]["L1"],
                   " ".join("%s-%s" % e for e in d["structure"]["edges"])), flush=True)


if __name__ == "__main__":
    main()
