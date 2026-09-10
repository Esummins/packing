"""A186 step 3 (measured side) -- GLOBAL search for the stuck configuration of a boxed assignment.

Objective over the six tilts: the exact ELASTIC LP (descend186.solve_elastic: every selection row
relaxed by one slack tau >= 0, objective s + M tau, M = 50) with the selections chosen by alternation
(solve, re-select every pair to its best separating axis at the LP point, repeat <= 3 times); centre
boxes = the hull of the pieces containing each tilt.  Nelder-Mead from random tilt starts sampled inside
the pieces.  A result with tau = 0 is a real configuration of the hull boxes at side s* (check_packing);
tau > 0 is the least-overlap configuration at that side.  [M] throughout.

    python global186.py --index k [--starts 20] [--seed 7]   -> results/global186.jsonl
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodes186 as N                                          # noqa: E402
import tree186 as T                                           # noqa: E402  (installs build_lp_pieces)
import descend186 as D                                        # noqa: E402
A, S0 = N.A, N.S0
SHAT = A.SHAT
M = D.M_ELASTIC


class Search:
    def __init__(self, rec):
        self.bodies, self.nv = N.build_bodies(rec)
        self.free = [b for b in self.bodies if b.kind == "free"]
        self.idx = {b.name: k for k, b in enumerate(self.bodies)}
        self.cache = {}

    def select_initial(self, theta):
        """best separating axis per pair at the boxes' centres (a heuristic start for the alternation)."""
        cfg = {}
        cells = {n: (t, t) for n, t in theta.items()}
        for b in self.bodies:
            if b.kind == "pin":
                cfg[b.name] = (b.anchor[0], b.anchor[1], 0.0)
            else:
                bx = b.box_for(cells[b.name])
                cfg[b.name] = (0.5 * (bx[0] + bx[1]), 0.5 * (bx[2] + bx[3]), theta[b.name])
        fixed = {}
        nb = len(self.bodies)
        for i in range(nb):
            for j in range(i + 1, nb):
                if self.bodies[i].kind == "pin" and self.bodies[j].kind == "pin":
                    continue
                pi, pj = cfg[self.bodies[i].name], cfg[self.bodies[j].name]
                gs = [(A.gap_sel(pi[:2], pi[2], pj[:2], pj[2], o, k, e), (o, k, e)) for (o, k, e) in A.SELS]
                fixed[(i, j)] = max(gs)[1]
        return fixed

    def reselect(self, theta, x, fixed):
        s, cfg = A.config_from_x(self.bodies, x, theta)
        new = dict(fixed)
        for (i, j), old in fixed.items():
            pi, pj = cfg[self.bodies[i].name], cfg[self.bodies[j].name]
            gs = [(A.gap_sel(pi[:2], pi[2], pj[:2], pj[2], o, k, e), (o, k, e)) for (o, k, e) in A.SELS]
            best, bsel = max(gs)
            if A.gap_sel(pi[:2], pi[2], pj[:2], pj[2], *old) < best - 1e-9:
                new[(i, j)] = bsel
        return new

    def evaluate(self, tv, fixed=None, iters=3):
        theta = {b.name: float(tv[k]) for k, b in enumerate(self.free)}
        cells = {n: (t, t) for n, t in theta.items()}
        for b in self.free:
            if not (b.t0 - 1e-12 <= theta[b.name] <= b.t1 + 1e-12) or b.box_for(cells[b.name]) is None:
                return math.inf, None
        fixed = fixed or self.select_initial(theta)
        best = None
        for it in range(iters):
            R = A.build_lp(self.bodies, self.nv, S0, S0 + 0.4, fixed, cells=cells, exact_theta=theta)
            s, tau, x, y = D.solve_elastic(R, M)
            if x is None:
                return math.inf, None
            val = s + M * tau
            if best is None or val < best[0]:
                best = (val, dict(s=s, tau=tau, x=x, y=y, R=R, theta=theta, fixed=dict(fixed)))
            new = self.reselect(theta, x, fixed)
            if new == fixed:
                break
            fixed = new
        return best[0], best[1]

    def run_start(self, tv0, maxfev=600):
        f = lambda v: self.evaluate(v)[0]
        step = math.radians(4.0)
        sim = [np.array(tv0)]
        for k in range(len(tv0)):
            e = np.array(tv0); b = self.free[k]
            e[k] = e[k] + step if e[k] + step <= b.t1 else e[k] - step
            sim.append(e)
        res = minimize(f, np.array(tv0), method="Nelder-Mead",
                       options=dict(initial_simplex=np.array(sim), xatol=1e-6, fatol=1e-10, maxfev=maxfev))
        val, info = self.evaluate(res.x)
        return val, info

    def record(self, info):
        s, cfg = A.config_from_x(self.bodies, info["x"], info["theta"])
        wp, ww = A.check_packing(s, cfg)
        inside = {}
        for b in self.free:
            cx, cy, th = cfg[b.name]
            inside[b.name] = any(p[0] - 1e-9 <= cx <= p[1] + 1e-9 and p[2] - 1e-9 <= cy <= p[3] + 1e-9
                                 and p[4] - 1e-9 <= th <= p[5] + 1e-9 for p in b.pieces)
        sup = info["R"].support(info["y"]) if info["y"] is not None else []
        st = D.structure(self, sup)
        return dict(side=info["s"], tau=info["tau"], side_minus_s0=info["s"] - S0, side_minus_shat=info["s"] - SHAT,
                    worst_pair=wp, worst_wall=ww, packing=bool(wp >= -1e-7 and ww >= -1e-7),
                    inside=inside, all_inside=all(inside.values()),
                    cfg={n: [p[0], p[1], math.degrees(p[2])] for n, p in cfg.items()},
                    fixed={"%s|%s" % (self.bodies[i].name, self.bodies[j].name): list(v) for (i, j), v in info["fixed"].items()},
                    support=[[list(m), w] for m, w in sup], structure=st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=int, required=True)
    ap.add_argument("--starts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--maxfev", type=int, default=600)
    ap.add_argument("--time", type=float, default=520.0)
    ap.add_argument("--M", type=float, default=None, help="elastic weight (default descend186.M_ELASTIC)")
    args = ap.parse_args()
    global M
    if args.M:
        M = args.M; D.M_ELASTIC = args.M
    recs = N.load_records()
    items = sorted(recs.items(), key=lambda kv: (-len(kv[1]["roles"]), kv[0]))
    lab, rec = items[args.index]
    S = Search(rec)
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    found = []
    for k in range(args.starts):
        if time.time() - t0 > args.time:
            break
        tv0 = []
        for b in S.free:
            p = b.pieces[rng.integers(len(b.pieces))]
            tv0.append(rng.uniform(p[4], p[5]))
        val, info = S.run_start(tv0, maxfev=args.maxfev)
        if info is None:
            continue
        r = S.record(info)
        r["start"] = [math.degrees(t) for t in tv0]
        found.append(r)
        print("  start %2d: s* %.7f tau %.2e (s0 %+.2e) packing %s inside %s  %s" %
              (k, r["side"], r["tau"], r["side_minus_s0"], r["packing"],
               "ALL" if r["all_inside"] else "".join(n for n, v in r["inside"].items() if not v),
               " ".join("%s-%s" % e for e in r["structure"]["edges"])), flush=True)
    found.sort(key=lambda r: r["side"] + M * r["tau"])
    row = dict(index=args.index, short=N.short_label(lab), label=lab, budget=11 - len(rec["roles"]), M=M,
               n_starts=len(found), results=found, seconds=round(time.time() - t0, 1),
               when=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(os.path.join(N.RES, "global186.jsonl"), "a", encoding="utf-8") as out:
        out.write(json.dumps(row) + "\n")
    print("%s: %d starts, best s* %.7f tau %.2e (%.0fs)" % (row["short"], len(found),
          found[0]["side"] if found else math.nan, found[0]["tau"] if found else math.nan, row["seconds"]))


if __name__ == "__main__":
    main()
