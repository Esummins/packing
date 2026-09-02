r"""
A66 D1: catalog ADEQUACY diagnostic + product witness.

(a) tau_f_cat -- the SINGLE-square fractional packing LP on a pair-LP catalog:
        max sum_i nu_i,  nu >= 0,  sum{ nu_i : c in Q_i } <= 1 for every point c,
    solved with the same adaptive cell-representative cut loop as pairlp.py (converged to
    fine Lmax <= 1).  Compared against the A65 single-LP references: a catalog that cannot
    express the known fractional cheat cannot be trusted to price the pair LP either.

(b) column generation: placements whose dual price sum_{c in Q} y_c < 1 are exactly the
    cheat-riders the catalog is missing; the fine placement grid (centre 0.05, tilt 0.02) is
    scanned for them and the worst are added.

(c) PRODUCT WITNESS: from a converged nu, y_ij = nu_i nu_j on the DISJOINT catalog pairs is
    feasible for the pair LP by construction -- for any c,d the pair load is at most
    f(c) f(d) <= 1 where f is the single load -- so its value is a certified lower bound on
    tau_2(0).  If that lands at/above C(N,2) the emptiness route is dead regardless of what
    the restricted pair LP reported.

    python code\singlelp.py --cls k4_13 --enrich
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, json, math, sys, time
from fractions import Fraction as Fr
import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pairlp as pl
from pairlp import (S0, log, require_headroom, membership, dedupe_by_pattern, build_points,
                    build_catalog, control_family, square_vertices, seg_intersections,
                    core_free_mask, box_mask_bits, theta_of, width, disjoint_pairs)

REF_TAU_F = {"k4_08": 7.000000, "k4_13": 7.2545}


def single_probes(cat, sup_sq, args, rng, cap):
    if len(sup_sq) == 0:
        return np.zeros((0, 2))
    idx = sup_sq[:args.probe_squares]
    V = square_vertices(cat, idx)
    X, _ = seg_intersections(cat, idx, cap=args.seg_cap)
    base = np.vstack([V, X]) if len(X) else V
    nb = max(1, cap // 4)
    if len(base) > nb:
        base = base[rng.choice(len(base), nb, replace=False)]
    out = []
    for ex in (-args.probe_eps, args.probe_eps):
        for ey in (-args.probe_eps, args.probe_eps):
            out.append(base + np.array([ex, ey]))
    P = np.vstack(out)
    return P[(P[:, 0] >= -1e-9) & (P[:, 0] <= S0 + 1e-9)
             & (P[:, 1] >= -1e-9) & (P[:, 1] <= S0 + 1e-9)]


def fine_points(cat, sup_sq, boxes, args):
    V = square_vertices(cat, sup_sq)
    X, _ = seg_intersections(cat, sup_sq, cap=args.seg_cap)
    probe = np.vstack([V, X]) if len(X) else V
    pts = []
    for ex in (-args.probe_eps, args.probe_eps):
        for ey in (-args.probe_eps, args.probe_eps):
            pts.append(probe + np.array([ex, ey]))
    v = np.arange(0.0, S0 + 1e-12, args.fine_global)
    XX, YY = np.meshgrid(v, v, indexing="ij")
    pts.append(np.column_stack([XX.ravel(), YY.ravel()]))
    if len(boxes):
        v2 = np.arange(0.0, S0 + 1e-12, args.fine_local)
        XX, YY = np.meshgrid(v2, v2, indexing="ij")
        G = np.column_stack([XX.ravel(), YY.ravel()])
        d = np.min(np.hypot(G[:, None, 0] - boxes[None, :, 0], G[:, None, 1] - boxes[None, :, 1]), axis=1)
        pts.append(G[d <= args.fine_radius])
    P = np.vstack(pts)
    return P[(P[:, 0] >= -1e-9) & (P[:, 0] <= S0 + 1e-9)
             & (P[:, 1] >= -1e-9) & (P[:, 1] <= S0 + 1e-9)]


class Single:
    """max sum nu s.t. point loads <= 1; rows are points, columns are placements."""

    def __init__(self, cat, args):
        self.cat = cat
        self.args = args
        self.h = highspy.Highs()
        self.h.setOptionValue("output_flag", False)
        self.h.setOptionValue("threads", 1)
        self.h.setOptionValue("time_limit", float(args.lp_time))
        self.h.changeObjectiveSense(highspy.ObjSense.kMaximize)
        n = len(cat["t"])
        self.h.addCols(n, np.ones(n), np.zeros(n), np.ones(n), 0,
                       np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))
        self.rowpts = np.zeros((0, 2))
        self.rowkeys = set()

    def add_points(self, P):
        A = membership(P, self.cat)
        fresh, sups = [], []
        for r in range(len(P)):
            sup = np.nonzero(A[r])[0]
            if len(sup) == 0:
                continue
            key = sup.tobytes()
            if key in self.rowkeys:
                continue
            self.rowkeys.add(key)
            fresh.append(P[r])
            sups.append(sup)
        if not sups:
            return 0
        starts, run = [], 0
        for s in sups:
            starts.append(run)
            run += len(s)
        ind = np.concatenate(sups).astype(np.int32)
        self.h.addRows(len(sups), np.full(len(sups), -highspy.kHighsInf), np.ones(len(sups)),
                       len(ind), np.array(starts, dtype=np.int32), ind, np.ones(len(ind)))
        self.rowpts = np.vstack([self.rowpts, np.array(fresh)])
        return len(sups)

    def add_placements(self, tnew, Cnew, boxes):
        """column generation: extend the catalog and give the new columns their coefficients."""
        cat = self.cat
        thn = np.array([theta_of(t) for t in tnew])
        cols = []
        for a in range(len(tnew)):
            m = pl.inside_mask_points(self.rowpts, Cnew[a, 0], Cnew[a, 1], thn[a])
            cols.append(np.nonzero(m)[0])
        starts, run = [], 0
        for c in cols:
            starts.append(run)
            run += len(c)
        ind = np.concatenate(cols).astype(np.int32) if run else np.zeros(0, dtype=np.int32)
        self.h.addCols(len(tnew), np.ones(len(tnew)), np.zeros(len(tnew)), np.ones(len(tnew)),
                       len(ind), np.array(starts, dtype=np.int32), ind, np.ones(len(ind)))
        mask = np.concatenate([cat["mask"], box_mask_bits_multi(Cnew, thn, boxes)])
        self.cat = dict(t=np.concatenate([cat["t"], tnew]),
                        th=np.concatenate([cat["th"], thn]),
                        C=np.vstack([cat["C"], Cnew]), mask=mask,
                        m=np.array([bin(int(x)).count("1") for x in mask]),
                        stats=cat["stats"])
        return len(tnew)

    def run(self):
        self.h.run()
        st = self.h.getModelStatus()
        sol = self.h.getSolution()
        return (st, np.array(sol.col_value), np.array(sol.row_dual),
                float(self.h.getInfo().objective_function_value))


def box_mask_bits_multi(C, ths, boxes):
    out = np.zeros(len(C), dtype=np.int64)
    for a in range(len(C)):
        out[a] = box_mask_bits(C[a:a + 1], ths[a], boxes)[0]
    return out


def converge(mdl, P, boxes, args, fh, rng, tag=""):
    """working-set cut loop + independent fine-grid feedback, until fine Lmax <= 1 + tol."""
    t0 = time.time()
    nu = y = None
    val = 0.0
    lm_fine = None
    for outer in range(args.outer_passes):
        for rd in range(args.max_rounds):
            st, nu, y, val = mdl.run()
            if st != highspy.HighsModelStatus.kOptimal:
                log("single%s: non-optimal %s" % (tag, st), fh)
                break
            sup = np.nonzero(nu > 1e-9)[0]
            probes = single_probes(mdl.cat, sup, args, rng, args.probe_cap)
            W = np.vstack([P, probes]) if len(probes) else P
            A = membership(W, mdl.cat, sup)
            keep = A.any(axis=1)
            W, A = W[keep], A[keep]
            W, A = dedupe_by_pattern(W, A)
            load = A.astype(float) @ nu[sup]
            bad = np.nonzero(load > 1.0 + args.cut_tol)[0]
            if len(bad) == 0:
                break
            if mdl.add_points(W[bad[np.argsort(-load[bad])][:args.max_cuts]]) == 0:
                break
            if time.time() - t0 > args.cls_budget:
                log("single%s: time budget hit" % tag, fh)
                break
        st, nu, y, val = mdl.run()
        sup = np.nonzero(nu > 1e-9)[0]
        F = fine_points(mdl.cat, sup, boxes, args)
        A = membership(F, mdl.cat, sup)
        keep = A.any(axis=1)
        F, A = F[keep], A[keep]
        F, A = dedupe_by_pattern(F, A)
        load = A.astype(float) @ nu[sup]
        lm_fine = float(load.max()) if len(load) else 0.0
        bad = np.nonzero(load > 1.0 + args.cut_tol)[0]
        log("single%s p%d: tau=%.6f fine Lmax=%.6f (fine pts %d, support %d, rows %d, %.0fs)"
            % (tag, outer, val, lm_fine, len(F), len(sup), mdl.h.getNumRow(), time.time() - t0), fh)
        if len(bad) == 0:
            break
        if mdl.add_points(F[bad[np.argsort(-load[bad])][:args.max_cuts]]) == 0:
            break
    st, nu, y, val = mdl.run()
    return nu, y, val, lm_fine


def solve_single(cat, P, boxes, args, fh, tag=""):
    mdl = Single(cat, args)
    mdl.add_points(P)
    rng = np.random.default_rng(args.seed)
    nu, y, val, lm_fine = converge(mdl, P, boxes, args, fh, rng, tag=tag)
    return mdl, nu, y, val, lm_fine


def price_scan(mdl, y, pins, args, fh):
    """fine placement grid (centre 0.05, tilt 0.02); return the worst-priced core-free ones."""
    pos = np.nonzero(y > 1e-10)[0]
    if len(pos) == 0:
        return np.zeros(0), np.zeros((0, 2))
    Y = mdl.rowpts[pos]
    w = y[pos]
    have = set()
    for a in range(len(mdl.cat["t"])):
        have.add((round(float(mdl.cat["C"][a, 0]), 6), round(float(mdl.cat["C"][a, 1]), 6),
                  round(float(mdl.cat["t"][a]), 6)))
    best = []
    for t in np.arange(0.0, 1.0 + 1e-12, args.cg_tstep):
        th = theta_of(float(t))
        ww = width(th)
        v = np.arange(0.0, S0 + 1e-12, args.cg_cstep)
        v = v[(v >= ww / 2 - 1e-12) & (v <= S0 - ww / 2 + 1e-12)]
        if len(v) == 0:
            continue
        XX, YY = np.meshgrid(v, v, indexing="ij")
        C = np.column_stack([XX.ravel(), YY.ravel()])
        C = C[core_free_mask(C, th, pins)]
        if len(C) == 0:
            continue
        c, s = math.cos(th), math.sin(th)
        dx = Y[None, :, 0] - C[:, None, 0]
        dy = Y[None, :, 1] - C[:, None, 1]
        u = dx * c + dy * s
        vv = -dx * s + dy * c
        inside = (np.abs(u) < 0.5 - pl.EPS_IN) & (np.abs(vv) < 0.5 - pl.EPS_IN)
        price = inside.astype(float) @ w
        sel = np.nonzero(price < 1.0 - args.cg_tol)[0]
        for j in sel:
            key = (round(float(C[j, 0]), 6), round(float(C[j, 1]), 6), round(float(t), 6))
            if key in have:
                continue
            best.append((float(price[j]), float(t), float(C[j, 0]), float(C[j, 1])))
    best.sort(key=lambda x: x[0])
    best = best[:args.cg_add]
    if not best:
        return np.zeros(0), np.zeros((0, 2))
    return (np.array([b[1] for b in best]),
            np.array([[b[2], b[3]] for b in best]))


def product_witness(cat, nu, boxes, args, fh):
    """y_ij = nu_i nu_j on disjoint pairs: feasible for the pair LP by construction."""
    sup = np.nonzero(nu > 1e-9)[0]
    sub = dict(t=cat["t"][sup], th=cat["th"][sup], C=cat["C"][sup],
               mask=cat["mask"][sup], m=cat["m"][sup], stats={})
    I, J = disjoint_pairs(sub)
    ns = len(sup)
    nus = nu[sup]
    yij = nus[I] * nus[J]
    m2 = np.array([bin(int(sub["mask"][a] & sub["mask"][b])).count("1") for a, b in zip(I, J)])
    val0 = float(yij.sum())
    tau = float(nus.sum())
    allpairs = 0.5 * (tau * tau - float((nus ** 2).sum()))
    Z = np.zeros((ns, ns))
    Z[I, J] = yij
    Z[J, I] = yij
    F = fine_points(sub, np.arange(ns), boxes, args)
    A = membership(F, sub)
    keep = A.any(axis=1)
    F, A = F[keep], A[keep]
    F, A = dedupe_by_pattern(F, A)
    lm = pl.chunk_lmax(A.astype(float), Z, chunk=args.chunk)
    out = dict(tau_f_cat=tau, n_support=int(ns), n_disjoint_pairs=int(len(I)),
               value_beta0=val0, value_all_pairs_unrestricted=allpairs,
               value_beta_025=float((yij * (1.0 + 0.25 * m2)).sum()),
               value_beta_1=float((yij * (1.0 + 1.0 * m2)).sum()),
               fine_Lmax=float(lm), fine_points=int(len(F)),
               sum_nu_squared=float((nus ** 2).sum()))
    log("product witness: tau=%.6f sup=%d disjoint pairs=%d value(b=0)=%.6f "
        "(all pairs %.6f) fine Lmax=%.6f" % (tau, ns, len(I), val0, allpairs, lm), fh)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--cap_total", type=int, default=300)
    ap.add_argument("--cap_m2", type=int, default=200)
    ap.add_argument("--cap_m1", type=int, default=60)
    ap.add_argument("--cap_coarse", type=int, default=40)
    ap.add_argument("--min_sep", type=float, default=0.35)
    ap.add_argument("--max_rounds", type=int, default=40)
    ap.add_argument("--max_cuts", type=int, default=1500)
    ap.add_argument("--probe_squares", type=int, default=200)
    ap.add_argument("--probe_cap", type=int, default=4000)
    ap.add_argument("--seg_cap", type=int, default=900000)
    ap.add_argument("--probe_eps", type=float, default=1e-5)
    ap.add_argument("--cut_tol", type=float, default=1e-6)
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cls_budget", type=float, default=300.0)
    ap.add_argument("--chunk", type=int, default=384)
    ap.add_argument("--fine_global", type=float, default=0.05)
    ap.add_argument("--fine_local", type=float, default=0.02)
    ap.add_argument("--fine_radius", type=float, default=1.2)
    ap.add_argument("--fine_cap", type=int, default=9000)
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--headroom_wait", type=float, default=300.0)
    ap.add_argument("--enrich", action="store_true")
    ap.add_argument("--enrich_rounds", type=int, default=14)
    ap.add_argument("--outer_passes", type=int, default=4)
    ap.add_argument("--enrich_if_below", type=float, default=7.1)
    ap.add_argument("--enrich_stop", type=float, default=7.24)
    ap.add_argument("--cg_cstep", type=float, default=0.05)
    ap.add_argument("--cg_tstep", type=float, default=0.02)
    ap.add_argument("--cg_add", type=int, default=200)
    ap.add_argument("--cg_tol", type=float, default=1e-6)
    ap.add_argument("--tag", default="")
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--dump_support", default=None)
    ap.add_argument("--support_fill", type=int, default=0)
    args = ap.parse_args()

    fh = open(os.path.join(pl.BASE, "logs", "singlelp_%s%s.log" % (args.cls, args.tag)), "w")
    T0 = time.time()
    log("A66 D1 single-LP adequacy: class=%s" % args.cls, fh)
    require_headroom(args.headroom, fh, args.headroom_wait)

    spec = json.load(open(pl.BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    N = int(e["N"])

    ctrl = control_family(args.cls, pins, boxes, fh)
    extra = ctrl["placements"] if ctrl else None
    if args.catalog:
        pls = json.load(open(args.catalog))["placements"]
        cat = pl.catalog_from_list(pls, pins, boxes)
        log("catalog IMPORTED |S|=%d %s" % (len(cat["t"]), json.dumps(cat["stats"])), fh)
    else:
        cat = build_catalog(pins, boxes, args, fh, extra=extra)
    log("catalog |S|=%d" % len(cat["t"]), fh)
    P = build_points(cat, boxes, 0.3, 0.12, 1.5)

    out = dict(cls=args.cls, N=N, ref_tau_f=REF_TAU_F.get(args.cls),
               catalog_size=int(len(cat["t"])), passes=[])

    mdl, nu, y, val, lmf = solve_single(cat, P, boxes, args, fh, tag=" base")
    out["passes"].append(dict(pass_="base", catalog_size=int(len(mdl.cat["t"])),
                              tau_f_cat=val, fine_Lmax=lmf,
                              n_support=int((nu > 1e-9).sum())))
    out["tau_f_cat_base"] = val
    pw = product_witness(mdl.cat, nu, boxes, args, fh)
    out["product_witness_base"] = pw

    if args.enrich and val < args.enrich_if_below:
        for r in range(args.enrich_rounds):
            require_headroom(args.headroom, fh, args.headroom_wait)
            st, nu, y, val = mdl.run()
            tn, Cn = price_scan(mdl, y, pins, args, fh)
            if len(tn) == 0:
                log("enrich r%d: no under-priced placement found (catalog adequate)" % (r + 1), fh)
                break
            mdl.add_placements(tn, Cn, boxes)
            log("enrich r%d: added %d placements, |S|=%d" % (r + 1, len(tn), len(mdl.cat["t"])), fh)
            rng = np.random.default_rng(args.seed + r)
            nu, y, val, lmf = converge(mdl, P, boxes, args, fh, rng, tag=" e%d" % (r + 1))
            log("enrich r%d: tau=%.6f fine Lmax=%.6f |S|=%d"
                % (r + 1, val, lmf, len(mdl.cat["t"])), fh)
            out["passes"].append(dict(pass_="enrich%d" % (r + 1),
                                      catalog_size=int(len(mdl.cat["t"])), tau_f_cat=val,
                                      fine_Lmax=lmf, added=int(len(tn)),
                                      n_support=int((nu > 1e-9).sum())))
            if val >= args.enrich_stop and lmf <= 1.0 + 1e-6:
                break
        out["tau_f_cat_enriched"] = val
        out["product_witness_enriched"] = product_witness(mdl.cat, nu, boxes, args, fh)
        cp = os.path.join(pl.BASE, "results", "catalog_%s_enriched.json" % args.cls)
        json.dump(dict(cls=args.cls, s0=S0, n=int(len(mdl.cat["t"])),
                       placements=[[float(mdl.cat["t"][a]), float(mdl.cat["C"][a, 0]),
                                    float(mdl.cat["C"][a, 1])] for a in range(len(mdl.cat["t"]))]),
                  open(cp, "w"))
        out["enriched_catalog_path"] = cp
        log("wrote %s" % cp, fh)

    if args.dump_support:
        sup = np.nonzero(nu > 1e-9)[0]
        sel = list(sup)
        if args.support_fill > 0:
            rest = np.setdiff1d(np.arange(len(mdl.cat["t"])), sup)
            if len(rest):
                X = np.column_stack([mdl.cat["C"][rest, 0], mdl.cat["C"][rest, 1],
                                     2.0 * mdl.cat["t"][rest]])
                g = pl.greedy_diverse(X, min(args.support_fill, len(rest)))
                sel += list(rest[g])
        json.dump(dict(cls=args.cls, s0=S0, n=len(sel), tau_f_of_support=out["tau_f_cat_base"],
                       n_support=int(len(sup)),
                       placements=[[float(mdl.cat["t"][a]), float(mdl.cat["C"][a, 0]),
                                    float(mdl.cat["C"][a, 1])] for a in sel]),
                  open(args.dump_support, "w"))
        log("dumped %d placements (%d single-LP support) -> %s"
            % (len(sel), len(sup), args.dump_support), fh)
    out["total_seconds"] = time.time() - T0
    fp = os.path.join(pl.BASE, "results", "singlelp_%s%s.json" % (args.cls, args.tag))
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs)" % (fp, out["total_seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
