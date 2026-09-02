r"""
A71 T1 design probe: restricted adversary value tau_2^eta(beta=1) for k4_08 as a function of
the membership margin eta (atoms counted only eta-deep).  Motivation: verify_pair.py's COVERED
discharge needs certain membership over a whole factor box, so a certificate verifiable with
leaf boxes of scale ~r effectively covers rows with (~r)-deep membership; the adversary's
value against eta-deep membership is a LOWER bound on any such certificate's W2.  If
tau_2^eta > threshold = 28, NO certificate whose atoms all collect with margin >= eta can
exist, and the verifier must refine below that scale wherever the covering is tight.

Mechanism probed explicitly: grids of squares at spacing just above 1-2*eta (pairwise-disjoint
eta-cores decouple the load rows) -- the '12-packing style' threat.

Monkeypatches its own process copy of pairlp (EPS_IN -> eta, EPS_CORE -> delta for slack
cores); code/pairlp.py on disk is untouched.

    python code/etaprobe.py --etas 0.01,0.03,0.06,0.10,0.15
"""
import os, sys, json, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pairlp as pl
import emitlib as el
from fractions import Fraction as Fr


def run_eta(eta, delta, args, fh):
    pl.EPS_IN = eta                      # membership counted eta-deep
    pl.EPS_CORE = delta                  # slack cores (strict-side approx, see notes)
    cd = el.ClassData("k4_08", delta=Fr(delta).limit_denominator(10**6))

    spec = json.load(open(pl.BOXSPEC))
    e = spec["classes"]["k4_08"]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    N, k, m = int(e["N"]), int(e["k"]), len(boxes)
    thresh_base = N * (N - 1) // 2

    ctrl = pl.control_family("k4_08", pins, boxes, fh)
    extra = list(ctrl["placements"]) if ctrl else []

    # exploit grids for THIS eta
    ex = el.exploit_grids(cd, [eta], np.random.default_rng(7))
    n_ex = 0
    if ex is not None:
        for i in range(ex.n):
            extra.append((float(ex.t[i]), float(ex.cx[i]), float(ex.cy[i])))
            n_ex += 1
    pl.log("eta=%.3f: exploit columns offered = %d" % (eta, n_ex), fh)

    class A: pass
    a = A()
    a.cap_total, a.cap_m2, a.cap_m1, a.cap_coarse = args.cap_total, 160, 50, 40
    a.min_sep = 0.35
    cat = pl.build_catalog(pins, boxes, a, fh, extra=extra)
    pl.log("eta=%.3f: catalog %d  stats=%s" % (eta, len(cat["t"]), json.dumps(cat["stats"])), fh)

    I, J = pl.disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][x] & cat["mask"][y])).count("1") for x, y in zip(I, J)])

    P = pl.build_points(cat, boxes, 0.3, 0.12, 1.5)
    A_ = pl.membership(P, cat)
    P, A_ = pl.dedupe_by_pattern(P, A_)
    a2 = argparse.Namespace(
        max_rounds=args.max_rounds, max_cuts=1200, max_rows=25000, outer_passes=2,
        cut_tol=1e-6, fine_tol=1.05, probe_squares=200, probe_cap=4000, seg_cap=900000,
        probe_eps=1e-5, max_nnz=25000000, n_seed_random=1500, lp_time=180.0,
        cls_budget=args.budget, zub=30.0, chunk=384, fine_global=0.05, fine_local=0.02,
        fine_radius=1.2, fine_cap=9000, seed=20260902, n_boxpts=0, headroom=6.0,
        headroom_wait=300.0)
    store = pl.RowStore()
    r = pl.solve_beta(cat, I, J, m2, P, A_, 1.0, a2, fh, store, boxes)
    lmax = max(r["Lmax_fine"] or 1.0, 1.0)
    rec = dict(eta=eta, delta=delta, value=r["value"], Lmax_fine=lmax,
               scaled=r["value"] / lmax, threshold=thresh_base + m,
               margin=r["value"] / lmax - (thresh_base + m),
               converged=bool(r["converged"]), note=r["note"],
               n_exploit_offered=n_ex, n_catalog=len(cat["t"]),
               n_support=int(len(r["support"])), seconds=r["seconds"],
               top10=r["top10"])
    pl.log("ETA RESULT eta=%.3f: value=%.4f scaled=%.4f thr=%d margin=%+.4f conv=%s"
           % (eta, r["value"], rec["scaled"], rec["threshold"], rec["margin"],
              rec["converged"]), fh)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etas", default="0.01,0.03,0.06,0.10,0.15")
    ap.add_argument("--delta", type=float, default=1e-3)
    ap.add_argument("--cap_total", type=int, default=420)
    ap.add_argument("--max_rounds", type=int, default=30)
    ap.add_argument("--budget", type=float, default=420.0)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    fh = open(os.path.join(el.BASE, "logs", "etaprobe%s.log" % args.tag), "w")
    pl.require_headroom(6.0, fh, 300.0)
    out = dict(cls="k4_08", beta=1.0, delta=args.delta, results=[])
    for eta in [float(x) for x in args.etas.split(",")]:
        out["results"].append(run_eta(eta, args.delta, args, fh))
        json.dump(out, open(os.path.join(el.BASE, "results", "etaprobe%s.json" % args.tag), "w"),
                  indent=1)
    pl.log("etaprobe done", fh)


if __name__ == "__main__":
    main()
