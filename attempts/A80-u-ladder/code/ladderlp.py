r"""
A80 T2: the U_k COUNTING ROW in the pair LP (docs/proofs/u_ladder.md).

Row (level k, image g, exact stratum S with 4 pins): at most 10-k of the 11 squares lie in the
Trump-slot zones of g; the 4 pins are always in-zone (slot drift <= 5/2 (lambda-1) << r_z), so
at most 6-k of the 7 FREE squares are in-zone, hence at most C(6-k, 2) in-zone free PAIRS:

    sum_{ij : bz_g(ij) = 1} z_ij  <=  cap_k := C(6-k, 2)       (k = 0: 15 = Lemma P-B's count)

added as a HARD row to the A66 packing LP (max sum z (1 + beta m2) s.t. point loads <= 1).
By LP duality its multiplier gamma* is the discount of the (P2'') certificate form
mu2 >= 1 + beta m2 - gamma bz, with threshold C(N,2) + beta m - gamma cap_k; the constrained
value V_k < 28 (beta = 1) iff a restricted certificate exists at the optimal gamma.  So
margin_k = V_k/Lmax - 28 is the ladder's restricted margin at rung k, and V_0 reproduces the
P-B optimum over gamma (A66 measured gamma = 0.1: margin -1.40).

Zones: (cx, cy, t) boxes of radius r_z about the crowdfam k4_08 family (= the trump-sym4 image
at s0, exact to 1e-8; the second compatible image 'diag' = its diagonal reflection).  The
catalog gets +-d_in (in-zone) and +-d_out (out-of-zone) perturbation columns per zone centre so
the fractional dual can actually trade in-zone against out-of-zone mass (the A12 dodge).

    python code\ladderlp.py --ks -1,0,1,2,3,4,5 --r_z 1e-3 --n_images 1
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, json, sys, time
from fractions import Fraction as Fr
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pairlp as pl
from pairlp import (S0, log, require_headroom, membership, dedupe_by_pattern, build_points,
                    build_catalog, control_family, core_free_mask, disjoint_pairs, RowStore,
                    theta_of)
from basinlp import zone_id, perturbed


def reflect_diag(zones):
    """the diagonal D4 image: (x,y) -> (y,x); tilt theta -> pi/2 - theta, i.e. t -> (1-t)/(1+t)
    for the tilted squares; uprights stay upright (t = 0 mod the pi/2 branch)."""
    out = []
    for (t, cx, cy) in zones:
        tt = (1.0 - t) / (1.0 + t) if t > 0.2 else -t
        out.append((tt, cy, cx))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_08")
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--ks", default="-1,0,1,2,3,4,5")
    ap.add_argument("--r_z", type=float, default=1e-3)
    ap.add_argument("--d_in", type=float, default=None, help="default 0.3 r_z")
    ap.add_argument("--d_out", type=float, default=None, help="default 3 r_z")
    ap.add_argument("--n_images", type=int, default=1)
    ap.add_argument("--cap_total", type=int, default=300)
    ap.add_argument("--cap_m2", type=int, default=200)
    ap.add_argument("--cap_m1", type=int, default=60)
    ap.add_argument("--cap_coarse", type=int, default=40)
    ap.add_argument("--min_sep", type=float, default=0.35)
    ap.add_argument("--max_rounds", type=int, default=40)
    ap.add_argument("--max_cuts", type=int, default=1500)
    ap.add_argument("--max_rows", type=int, default=25000)
    ap.add_argument("--max_nnz", type=int, default=25000000)
    ap.add_argument("--outer_passes", type=int, default=3)
    ap.add_argument("--cut_tol", type=float, default=1e-6)
    ap.add_argument("--fine_tol", type=float, default=1.05)
    ap.add_argument("--probe_squares", type=int, default=200)
    ap.add_argument("--probe_cap", type=int, default=4000)
    ap.add_argument("--seg_cap", type=int, default=900000)
    ap.add_argument("--probe_eps", type=float, default=1e-5)
    ap.add_argument("--n_seed_random", type=int, default=2000)
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cls_budget", type=float, default=600.0)
    ap.add_argument("--zub", type=float, default=30.0)
    ap.add_argument("--chunk", type=int, default=384)
    ap.add_argument("--fine_global", type=float, default=0.05)
    ap.add_argument("--fine_local", type=float, default=0.02)
    ap.add_argument("--fine_radius", type=float, default=1.2)
    ap.add_argument("--fine_cap", type=int, default=9000)
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--headroom_wait", type=float, default=3600.0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--fresh_store", action="store_true", help="new (P2') row store per rung")
    args = ap.parse_args()
    args.catalog = None
    args.no_control_cols = False
    if args.d_in is None:
        args.d_in = 0.3 * args.r_z
    if args.d_out is None:
        args.d_out = 3.0 * args.r_z

    os.makedirs(os.path.join(pl.BASE, "results"), exist_ok=True)
    os.makedirs(os.path.join(pl.BASE, "logs"), exist_ok=True)
    fh = open(os.path.join(pl.BASE, "logs", "ladderlp_%s%s.log" % (args.cls, args.tag)), "w")
    T0 = time.time()
    log("A80 ladder LP: class=%s beta=%g ks=%s r_z=%g d_in=%g d_out=%g images=%d"
        % (args.cls, args.beta, args.ks, args.r_z, args.d_in, args.d_out, args.n_images), fh)
    require_headroom(args.headroom, fh, args.headroom_wait)

    spec = json.load(open(pl.BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    N, k_pins, m = int(e["N"]), int(e["k"]), len(boxes)
    thresh_base = N * (N - 1) // 2
    thr = thresh_base + args.beta * m
    log("class %s: k=%d N=%d m=%d threshold = %d + beta*%d = %.3f" % (args.cls, k_pins, N, m,
                                                                     thresh_base, m, thr), fh)

    ctrl = control_family(args.cls, pins, boxes, fh)
    if ctrl is None:
        log("no crowdfam family -> no zones; abort", fh)
        sys.exit(2)
    images = [("id", list(ctrl["placements"]))]
    if args.n_images >= 2:
        images.append(("diag", reflect_diag(ctrl["placements"])))
    extra = []
    for name, zones in images:
        extra += list(zones) + perturbed(zones, pins, args.d_in, args.d_out)
    log("images=%d, extra columns (zone centres + perturbed) = %d" % (len(images), len(extra)), fh)

    cat = build_catalog(pins, boxes, args, fh, extra=extra)
    I, J = disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1") for a, b in zip(I, J)])
    bzs = {}
    for name, zones in images:
        zid = zone_id(cat, zones, args.r_z)
        bz = ((zid[I] >= 0) & (zid[J] >= 0) & (zid[I] != zid[J])).astype(float)
        bzs[name] = bz
        log("image %s: in-zone placements=%d (per zone %s), ghost pairs=%d"
            % (name, int((zid >= 0).sum()), [int((zid == j).sum()) for j in range(len(zones))],
               int(bz.sum())), fh)
    log("catalog |S|=%d, disjoint pairs=%d" % (len(cat["t"]), len(I)), fh)

    P = build_points(cat, boxes, 0.3, 0.12, 1.5)
    boxpts = np.vstack([boxes] + [boxes + np.array([sx, sy])
                                  for sx in (-0.5, 0.5) for sy in (-0.5, 0.5)])
    keyP = {(round(x, 12), round(y, 12)): i for i, (x, y) in enumerate(P)}
    head = [keyP[(round(x, 12), round(y, 12))] for x, y in boxpts
            if (round(x, 12), round(y, 12)) in keyP]
    rest = [i for i in range(len(P)) if i not in set(head)]
    P = P[np.array(head + rest)]
    args.n_boxpts = len(head)
    A = membership(P, cat)
    P, A = dedupe_by_pattern(P, A, keep_empty=False, protect=args.n_boxpts)
    log("cut-loop points: %d (depth mean %.1f)" % (len(P), A.sum(1).mean()), fh)

    out = dict(cls=args.cls, N=N, m=m, beta=args.beta, threshold=thr, r_z=args.r_z,
               d_in=args.d_in, d_out=args.d_out, images=[n for n, _ in images],
               n_placements=int(len(cat["t"])), n_pairs_disjoint=int(len(I)),
               n_ghost_pairs={n: int(b.sum()) for n, b in bzs.items()},
               control_sum_m2=ctrl["sum_m2"], rungs=[],
               settings={kk: vv for kk, vv in vars(args).items()})
    fp = os.path.join(pl.BASE, "results", "ladderlp_%s%s.json" % (args.cls, args.tag))

    store = RowStore()              # (P2') rows are cap-independent: warm across rungs
    for k in [int(x) for x in args.ks.split(",")]:
        require_headroom(args.headroom, fh, args.headroom_wait)
        if args.fresh_store:
            store = RowStore()
        extra_rows = []
        cap = None
        if k >= 0:
            q = N - 1 - k                      # free squares allowed in-zone: 6 - k
            cap = q * (q - 1) // 2 if q >= 2 else 0
            for name, bz in bzs.items():
                cols = np.nonzero(bz > 0)[0]
                extra_rows.append((cols, np.ones(len(cols)), cap))
        r = pl.solve_beta(cat, I, J, m2, P, A, args.beta, args, fh, store, boxes,
                          extra_rows=extra_rows or None)
        lmax = max(r["Lmax_fine"] if r["Lmax_fine"] is not None else 1.0, 1.0)
        scaled = r["value"] / lmax
        z = r["z"]
        mass = float(z.sum())
        ghost = {n: float((z * b).sum()) for n, b in bzs.items()}
        rung = dict(k=k, cap=cap, value=r["value"], Lmax_fine=lmax, scaled_value=scaled,
                    threshold=thr, margin=scaled - thr, converged=bool(r["converged"]),
                    cap_duals=r.get("cap_duals", []), sum_z=mass, ghost_mass=ghost,
                    ghost_mass_fraction={n: (g / mass if mass > 0 else 0.0) for n, g in ghost.items()},
                    mbar2=float((z * m2).sum() / mass) if mass > 0 else 0.0,
                    n_support_pairs=int(len(r["support"])), rounds=r["rounds"],
                    n_rows=r["n_rows"], note=r["note"], seconds=r["seconds"], top10=r["top10"])
        # dodge witness: the full support with zone tags (image id) and displacement class
        zid0 = zone_id(cat, images[0][1], args.r_z)
        zones0 = images[0][1]
        def dclass(a):
            if zid0[a] >= 0:
                return "in"
            d = min(max(abs(cat["C"][a, 0] - cx), abs(cat["C"][a, 1] - cy), abs(cat["t"][a] - t))
                    for (t, cx, cy) in zones0)
            return "near" if d <= 4.0 * args.r_z else "far"
        sup = np.nonzero(z > 1e-7)[0]
        cls_mass = {}
        support = []
        for p_ in sup:
            a, b = int(I[p_]), int(J[p_])
            ca, cb = dclass(a), dclass(b)
            key = "-".join(sorted([ca, cb]))
            cls_mass[key] = cls_mass.get(key, 0.0) + float(z[p_])
            support.append(dict(z=float(z[p_]), m2=int(m2[p_]), bz=int(bzs["id"][p_]),
                                a=[float(cat["t"][a]), float(cat["C"][a, 0]), float(cat["C"][a, 1]), ca, int(zid0[a])],
                                b=[float(cat["t"][b]), float(cat["C"][b, 0]), float(cat["C"][b, 1]), cb, int(zid0[b])]))
        rung["support_class_mass"] = cls_mass
        rung["support"] = support
        out["rungs"].append(rung)
        log("RUNG k=%d cap=%s: value=%.6f Lmax=%.6f scaled=%.6f thr=%.3f margin=%+.4f "
            "gamma*=%s ghost=%s converged=%s (%.0fs)"
            % (k, cap, r["value"], lmax, scaled, thr, scaled - thr,
               ["%.4f" % g for g in rung["cap_duals"]],
               {n: round(g, 3) for n, g in ghost.items()}, r["converged"], r["seconds"]), fh)
        json.dump(out, open(fp, "w"), indent=1)

    out["total_seconds"] = time.time() - T0
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs)" % (fp, out["total_seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
