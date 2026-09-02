r"""
A71 -- does the corners4 (k4_13) answer survive enlarging the catalog?

The converged value 20.528... was computed on A66's 204-placement adversary-adequate SUPPORT
catalog.  The natural worry is that the full 3287-placement enriched catalog (1.74M disjoint
pairs -- far too many columns to put in the LP directly) would price higher and cross 21.  This
script settles it from the DUAL side, where no extra columns have to be solved for:

    let y >= 0 be the row weights of the converged solve, indexed by the point pairs (c,d) that
    generated the rows.  Each row is the (P2') constraint
        sum_{i<j} z_ij ([c in Qi][d in Qj] + [c in Qj][d in Qi]) <= 1,
    which is a VALID constraint for every catalog.  If

        (A^T y)_{ij} = sum_{(c,d)} y_{cd} ([c in Qi][d in Qj] + [c in Qj][d in Qi])  >=  c_ij

    holds for EVERY disjoint pair (i,j) of the ENRICHED catalog, then weak duality gives

        tau_2^{enriched}(beta) <= sum_{(c,d)} y_{cd}

    with no adequacy assumption and no completeness assumption about the point family -- the
    rows used are valid constraints whatever the geometry does elsewhere.  (Completeness is
    only needed for the LOWER bound, where it is stated as a caveat.)

Two passes: a float screen over all 1.74M enriched pairs, then, if it clears, an EXACT pass
with y rounded UP onto the 1/DEN_Y lattice (rounding up can only help A^T y >= c) and exact
rational membership, giving an exactly certified upper bound sum(y_up).
"""
import os, sys
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, json, math, time
from fractions import Fraction as Fr
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import pairlp413 as PL
from exactcert413 import Sq, membership_exact, DEN_P

DEN_Y = 10 ** 7          # dual lattice (rounded UP)


def log(msg, fh=None):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n"); fh.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dual", required=True)
    ap.add_argument("--cls", default="k4_13")
    ap.add_argument("--catalog", required=True, help="the ENRICHED catalog to price against")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "k4_13_dual_upper.json"))
    ap.add_argument("--logfile", default=os.path.join(BASE, "logs", "dualcheck_k4_13.log"))
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--exact", action="store_true", default=True)
    args = ap.parse_args()

    fh = open(args.logfile, "w")
    T0 = time.time()
    d = json.load(open(args.dual))
    log("A71 dual check: %s (lp_value=%.9f, %d nonzero duals over %d points)"
        % (args.dual, d["lp_value"], d["n_nonzero"], d["n_points"]), fh)

    P = np.array(d["points"])
    rows = d["rows"]
    wmin = min(r[2] for r in rows)
    wmax = max(r[2] for r in rows)
    neg = sum(1 for r in rows if r[2] < 0)
    assert wmin > -1e-6, ("duals are not sign-consistent (min %.3e) -- check the HiGHS max/min "
                          "convention before trusting this bound" % wmin)
    # y must be >= 0 for the weak-duality argument; the few negatives are simplex noise at the
    # 1e-11 level and are CLAMPED to 0.  Clamping raises sum(y) (safe for an upper bound) and
    # lowers A^T y by at most 1e-8 in total, which the exact pass re-checks anyway.
    y = np.zeros((len(P), len(P)))
    ysum = 0.0
    clamped = 0.0
    for (c, dd, w) in rows:
        if w < 0:
            clamped += -w
            w = 0.0
        y[c, dd] += w
        y[dd, c] += w                      # symmetric: the row is unordered in (c,d)
        ysum += w
    log("duals: sum=%.9f (after clamping %d negatives totalling %.3e), min=%.3e max=%.3e"
        % (ysum, neg, clamped, wmin, wmax), fh)
    neg = 0

    spec = json.load(open(PL.BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    N, m = int(e["N"]), len(boxes)
    thresh = N * (N - 1) // 2

    pls = json.load(open(args.catalog))["placements"]
    cat = PL.catalog_from_list(pls, pins, boxes)
    ncat = len(cat["t"])
    log("enriched catalog: %d placements imported (%s)" % (ncat, json.dumps(cat["stats"])), fh)
    I, J = PL.disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1") for a, b in zip(I, J)])
    log("enriched disjoint pairs: %d (m2>0: %d)" % (len(I), int((m2 > 0).sum())), fh)

    # ---------- float screen: (A y A^T)_{ij}, A = membership of the enriched squares
    t1 = time.time()
    A = PL.membership(P, cat).T.astype(np.float64)          # (ncat, npts)
    log("membership (enriched x point family): %d x %d, depth mean %.1f (%.1fs)"
        % (A.shape[0], A.shape[1], A.sum(1).mean(), time.time() - t1), fh)
    t1 = time.time()
    B = A @ y                                               # (ncat, npts)
    worst, wpair = None, None
    obj = 1.0                                               # beta = 0
    for r0 in range(0, ncat, args.chunk):
        r1 = min(ncat, r0 + args.chunk)
        M = B[r0:r1] @ A.T                                  # (chunk, ncat)
        sel = (I >= r0) & (I < r1)
        vals = obj - M[I[sel] - r0, J[sel]]                 # deficit = c - (A^T y)
        if len(vals):
            k = int(np.argmax(vals))
            if worst is None or vals[k] > worst:
                worst = float(vals[k])
                wpair = (int(I[sel][k]), int(J[sel][k]))
    log("float screen: max deficit c - (A^T y) over the %d enriched disjoint pairs = %.6e "
        "at pair %s (%.1fs)" % (len(I), worst, wpair, time.time() - t1), fh)
    feasible_float = worst <= 1e-7

    out = dict(format="A71-dual-upper-v1", cls=args.cls, beta=0.0, N=N, m=m,
               decision_line=thresh, source_dual=os.path.basename(args.dual),
               enriched_catalog=os.path.basename(args.catalog),
               n_enriched_placements=int(ncat), n_enriched_disjoint_pairs=int(len(I)),
               lp_value_support_catalog=d["lp_value"],
               dual_sum_float=float(ysum),
               float_max_deficit=worst, float_worst_pair=list(wpair) if wpair else None,
               dual_feasible_float=bool(feasible_float))

    # ---------- exact pass
    if args.exact and feasible_float:
        squares = [Sq(float(cat["t"][a]), float(cat["C"][a, 0]), float(cat["C"][a, 1]))
                   for a in range(ncat)]
        pts_num = [(int(round(P[a, 0] * DEN_P)), int(round(P[a, 1] * DEN_P))) for a in range(len(P))]
        t1 = time.time()
        Ae = membership_exact(pts_num, squares)             # (npts, ncat)
        log("EXACT membership: %d x %d (%.1fs); float/exact disagreements %d"
            % (Ae.shape[0], Ae.shape[1], time.time() - t1, int((Ae.T != (A > 0.5)).sum())), fh)
        # y rounded UP onto the 1/DEN_Y lattice: this can only increase A^T y, so feasibility is
        # preserved, and sum(y_up) is the (slightly larger) exactly certified upper bound.
        Yint = np.zeros((len(P), len(P)), dtype=np.int64)
        tot = 0
        for (c, dd, w) in rows:
            wv = -w if neg else w
            n = math.ceil(Fr(wv).limit_denominator(10 ** 13) * DEN_Y)
            if n <= 0:
                continue
            Yint[c, dd] += n
            Yint[dd, c] += n
            tot += n
        Ysum = Fr(tot, DEN_Y)
        bound = float(tot) * 2.0 + 1.0
        assert bound < 2.0 ** 53, "int-in-double exactness bound violated"
        Aef = Ae.T.astype(np.float64)
        Bi = Aef @ Yint.astype(np.float64)
        need = float(DEN_Y)                                 # c_ij = 1 at beta = 0
        worst_e, wpair_e = None, None
        for r0 in range(0, ncat, args.chunk):
            r1 = min(ncat, r0 + args.chunk)
            M = Bi[r0:r1] @ Aef.T
            assert np.all(np.abs(M) < 2.0 ** 53)
            sel = (I >= r0) & (I < r1)
            vals = need - M[I[sel] - r0, J[sel]]
            if len(vals):
                k = int(np.argmax(vals))
                if worst_e is None or vals[k] > worst_e:
                    worst_e = float(vals[k]); wpair_e = (int(I[sel][k]), int(J[sel][k]))
        ok = worst_e <= 0.0
        log("EXACT check: max deficit (x %d) = %s at pair %s -> dual %sFEASIBLE"
            % (DEN_Y, worst_e, wpair_e, "" if ok else "IN"), fh)
        log("EXACT upper bound: tau_2^enriched(0) <= sum(y_up) = %s = %.9f  (vs decision line %d)"
            % (Ysum, float(Ysum), thresh), fh)
        out.update(dual_lattice=DEN_Y, dual_sum_exact=str(Ysum),
                   dual_sum_exact_float=float(Ysum),
                   exact_max_deficit_scaled=worst_e,
                   exact_worst_pair=list(wpair_e) if wpair_e else None,
                   dual_feasible_exact=bool(ok),
                   certified_upper=str(Ysum) if ok else None,
                   certified_upper_float=float(Ysum) if ok else None,
                   below_decision_line=bool(ok and Ysum < thresh),
                   claim=("y >= 0 rounded UP to 1/%d satisfies A^T y >= c for every one of the "
                          "%d disjoint pairs of the %d-placement ENRICHED catalog, and every row "
                          "used is a valid (P2') constraint, so tau_2(0) over that catalog is at "
                          "most sum(y) = %s < %d.  This direction needs NO catalog-adequacy and "
                          "NO point-family-completeness assumption."
                          % (DEN_Y, len(I), ncat, Ysum, thresh)) if ok else None)
    out["seconds"] = time.time() - T0
    json.dump(out, open(args.out, "w"), indent=1)
    log("wrote %s (%.1fs)" % (args.out, time.time() - T0), fh)
    fh.close()


if __name__ == "__main__":
    main()
