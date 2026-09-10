"""A186 step 3 (measured side) -- the STUCK configurations of a boxed assignment: box-constrained SLSQP
minimisation of the side s over the free bodies' hull boxes (starts sampled inside the PIECES) with the
exact SAT gaps (A116 sat_gap), pins on their slot lines; at the best minimum the active set (contacts,
walls, box faces), the Fritz-John multipliers by NNLS on the active gradients (lambda_0 = 1), the support
graph H, the structure-lemma checks (L1: loaded degree >= 2, L6: far-wall load path), the index count
m_H against 3 k_H + 1, and whether every free pose lies inside a piece (a configuration of the NODE) or
only inside the hull (a configuration of the relaxation).  [M] throughout: a measured upper bound on the
minimal side of the relaxation, and the contact graph the certificate has to beat.

    python stuck186.py [--budget0] [--distinct] [--starts 60] [--only k]   -> results/stuck186.jsonl
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize, nnls

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodes186 as N                                          # noqa: E402
A, S0 = N.A, N.S0
SHAT = A.SHAT
ACT = 1e-6


class Problem:
    def __init__(self, bodies, s_lo=3.5, s_hi=4.6):
        self.free = [b for b in bodies if b.kind == "free"]
        self.pins = [b for b in bodies if b.kind == "pin"]
        self.nf, self.npn = len(self.free), len(self.pins)
        self.bnds = [(s_lo, s_hi)]
        for b in self.free:
            self.bnds += [(b.x0, b.x1), (b.y0, b.y1), (b.t0, b.t1)]
        for p in self.pins:
            self.bnds += [(-p.hh, p.hh), (-p.hh, p.hh)]
        self.names = []                     # row names, in cons() order
        z = self.z0()
        self.cons(z, record=True)

    def unpack(self, z):
        s = z[0]
        Q = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(self.nf)]
        off = z[1 + 3 * self.nf:]
        Pn = [(p.ax[0] + p.ax[1] * s + off[2 * i], p.ay[0] + p.ay[1] * s + off[2 * i + 1], 0.0)
              for i, p in enumerate(self.pins)]
        return s, Q, Pn

    def cons(self, z, record=False):
        s, Q, Pn = self.unpack(z)
        out, nm = [], []
        for i, b in enumerate(self.free):
            cx, cy, th = Q[i]
            w = A.half_width(th)
            out += [cx - w, s - w - cx, cy - w, s - w - cy]
            nm += [("wall", b.name, "L"), ("wall", b.name, "R"), ("wall", b.name, "B"), ("wall", b.name, "T")]
            for j in range(i + 1, self.nf):
                out.append(A.sat_gap((cx, cy), th, Q[j][:2], Q[j][2])); nm.append(("pair", b.name, self.free[j].name))
            for k, q in enumerate(Pn):
                out.append(A.sat_gap((cx, cy), th, q[:2], 0.0)); nm.append(("pair", b.name, self.pins[k].name))
        for i in range(self.npn):
            out += [Pn[i][0] - 0.5, s - 0.5 - Pn[i][0], Pn[i][1] - 0.5, s - 0.5 - Pn[i][1]]
            nm += [("wall", self.pins[i].name, w) for w in "LRBT"]
        if record:
            self.names = nm
        return np.array(out)

    def z0(self):
        z = [S0]
        for b in self.free:
            z += [b.anchor[0], b.anchor[1], b.anchor[2]]
        z += [0.0] * (2 * self.npn)
        return np.array(z)

    def sample(self, rng):
        z = [rng.uniform(S0 - 0.02, S0 + 0.1)]
        for b in self.free:
            p = b.pieces[rng.integers(len(b.pieces))]
            z += [rng.uniform(p[0], p[1]), rng.uniform(p[2], p[3]), rng.uniform(p[4], p[5])]
        for p in self.pins:
            z += [rng.uniform(-p.hh, p.hh), rng.uniform(-p.hh, p.hh)]
        return np.array(z)

    def solve(self, z):
        try:
            r = minimize(lambda v: v[0], z, method="SLSQP", constraints=[{"type": "ineq", "fun": self.cons}],
                         bounds=self.bnds, options=dict(maxiter=400, ftol=1e-13))
        except Exception:
            return None
        if self.cons(r.x).min() < -1e-9:
            return None
        return r.x

    def inside_pieces(self, z):
        s, Q, _ = self.unpack(z)
        out = {}
        for i, b in enumerate(self.free):
            cx, cy, th = Q[i]
            out[b.name] = any(p[0] - 1e-9 <= cx <= p[1] + 1e-9 and p[2] - 1e-9 <= cy <= p[3] + 1e-9
                              and p[4] - 1e-9 <= th <= p[5] + 1e-9 for p in b.pieces)
        return out

    def fj(self, z, h=1e-7):
        """active rows (constraints + box faces), NNLS multipliers of  grad s = sum lambda grad g."""
        g = self.cons(z)
        act = [k for k in range(len(g)) if g[k] < ACT]
        rows, names = [], []
        for k in act:
            grad = np.zeros(len(z))
            for v in range(len(z)):
                zp = z.copy(); zp[v] += h; zm = z.copy(); zm[v] -= h
                grad[v] = (self.cons(zp)[k] - self.cons(zm)[k]) / (2 * h)
            rows.append(grad); names.append(self.names[k])
        for v, (lo, hi) in enumerate(self.bnds):
            if v == 0:
                continue
            if z[v] - lo < 1e-7:
                e = np.zeros(len(z)); e[v] = 1.0; rows.append(e); names.append(("face", self.var_name(v), "lo"))
            if hi - z[v] < 1e-7:
                e = np.zeros(len(z)); e[v] = -1.0; rows.append(e); names.append(("face", self.var_name(v), "hi"))
        if not rows:
            return dict(active=[], support=[], residual=None)
        M = np.array(rows).T
        target = np.zeros(len(z)); target[0] = 1.0
        lam, res = nnls(M, target)
        sup = [(names[k], float(lam[k])) for k in range(len(names)) if lam[k] > 1e-7]
        return dict(active=[list(n) for n in names], support=[[list(n), l] for n, l in sup], residual=float(res),
                    n_active=len(names))

    def var_name(self, v):
        if v <= 3 * self.nf:
            b = self.free[(v - 1) // 3]; return "%s.%s" % (b.name, "xyt"[(v - 1) % 3])
        p = self.pins[(v - 1 - 3 * self.nf) // 2]; return "%s.%s" % (p.name, "uv"[(v - 1 - 3 * self.nf) % 2])


def structure(prob, fjr):
    """support graph: loaded degree per free body, L1, L6 (far-wall load path), m_H vs 3 k_H + 1."""
    sup = fjr["support"]
    deg = {b.name: 0 for b in prob.free}
    edges, ground = [], set()
    for (n, l) in sup:
        kind = n[0]
        if kind == "pair":
            edges.append((n[1], n[2]))
            for a in (n[1], n[2]):
                if a in deg:
                    deg[a] += 1
        elif kind == "wall":
            if n[1] in deg:
                deg[n[1]] += 1
            edges.append((n[1], "W" + n[2]))
        elif kind == "face":
            b = n[1].split(".")[0]
            if b in deg and n[1].split(".")[1] != "t":
                deg[b] += 1
            edges.append((n[1], "FACE"))
    loaded = [b for b, d in deg.items() if d > 0]
    L1 = all(deg[b] >= 2 for b in loaded)
    # far-wall load path: from a body on R/T, walk H to a wall, pin or face
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    m_H = sum(1 for n, l in sup if n[0] != "face" or not n[1].endswith(".t"))
    k_H = len(loaded)
    return dict(deg=deg, loaded=loaded, L1=L1, k_H=k_H, m_H=len(sup), chi=len(sup) - 3 * k_H - 1,
                edges=sorted(set(map(tuple, edges))))


def run_one(rec, starts, seed, log=print):
    bodies, nv = N.build_bodies(rec)
    prob = Problem(bodies)
    rng = np.random.default_rng(seed)
    sols = []
    t0 = time.time()
    for k in range(starts + 1):
        z = prob.z0() if k == 0 else prob.sample(rng)
        x = prob.solve(z)
        if x is not None:
            sols.append(x)
    sols.sort(key=lambda x: x[0])
    row = dict(label=rec["label"], short=N.short_label(rec["label"]), budget=11 - len(rec["roles"]),
               starts=starts, n_converged=len(sols), seconds=round(time.time() - t0, 1), minima=[])
    seen = []
    for x in sols:
        if any(abs(x[0] - y[0]) < 1e-6 and np.max(np.abs(x - y)) < 1e-3 for y in seen):
            continue
        seen.append(x)
        s, Q, Pn = prob.unpack(x)
        fjr = prob.fj(x)
        st = structure(prob, fjr)
        inside = prob.inside_pieces(x)
        row["minima"].append(dict(side=float(s), side_minus_s0=float(s - S0), side_minus_shat=float(s - SHAT),
                                  free={b.name: [float(Q[i][0]), float(Q[i][1]), math.degrees(Q[i][2])] for i, b in enumerate(prob.free)},
                                  pins={p.name: [float(Pn[i][0]), float(Pn[i][1])] for i, p in enumerate(prob.pins)},
                                  inside_pieces=inside, all_inside=all(inside.values()), fj=fjr, structure=st))
        if len(row["minima"]) >= 6:
            break
    for m in row["minima"][:3]:
        log("  s* = %.7f (s0 %+.2e, shat %+.2e) inside %s  L1 %s  k_H %d m_H %d chi %d  res %.1e  support %s" %
            (m["side"], m["side_minus_s0"], m["side_minus_shat"], "ALL" if m["all_inside"] else
             "".join(k for k, v in m["inside_pieces"].items() if not v), m["structure"]["L1"], m["structure"]["k_H"],
             m["structure"]["m_H"], m["structure"]["chi"], m["fj"]["residual"] or 0.0,
             " ".join("%s-%s" % (a, b) for a, b in m["structure"]["edges"])))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget0", action="store_true")
    ap.add_argument("--distinct", action="store_true")
    ap.add_argument("--starts", type=int, default=60)
    ap.add_argument("--only", type=int, default=None)
    ap.add_argument("--seed", type=int, default=186)
    args = ap.parse_args()
    recs = N.load_records()
    items = sorted(recs.items(), key=lambda kv: (-len(kv[1]["roles"]), kv[0]))
    seen = set()
    out = open(os.path.join(N.RES, "stuck186.jsonl"), "a", encoding="utf-8")
    for k, (lab, r) in enumerate(items):
        if args.budget0 and len(r["roles"]) < 11:
            continue
        if args.only is not None and k != args.only:
            continue
        key = json.dumps({n: r["capture"][n]["pieces"] for n in r["roles"]}, sort_keys=True)
        if args.distinct and key in seen:
            continue
        seen.add(key)
        print(N.short_label(lab))
        row = run_one(r, args.starts, args.seed + k)
        row["index"] = k
        out.write(json.dumps(row) + "\n"); out.flush()
        print("  %d converged of %d starts, %.0fs" % (row["n_converged"], args.starts + 1, row["seconds"]))


if __name__ == "__main__":
    main()
