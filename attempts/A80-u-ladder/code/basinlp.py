r"""
A66 D3: the pair LP with the BASIN-EXCLUSION DISCOUNT of docs/proofs/pair_kill.md sect. 6
(Lemma P-B).

Row claim (P2''):  mu2{Q,Q'} >= 1 + beta*m2 - gamma * sum_{g in G_S} bz_g(Q,Q'),
kill threshold (P1''):  W2 < C(N,2) + beta*m - gamma*C(N-1,2)*|G_S|.

|G_S| = 1 here (the single compatible trump-sym4 image for k4_08), so the packing-side LP is

    max sum_ij z_ij * (1 + beta*m2_ij - gamma*bz_ij)   s.t. the same (P2') point loads <= 1,

against threshold 21 + 7*beta - 15*gamma.  bz_ij = 1 iff the two members sit in two DISTINCT
zone boxes of the image; zones are (cx, cy, t) boxes of radius r_z about the 7 crowdfam k4_08
family placements (pilot operationalization -- the zhat-derived zones are emission-time
bookkeeping).

The question this measures: the discount costs a PURE ghost family 21*gamma while the
threshold only drops 15*gamma (net +6*gamma per image), but the LP is fractional -- can it
dodge by MIXING ghost and non-ghost mass?  The reported ghost-mass fraction answers that.

    python code\basinlp.py --cls k4_08 --gammas 0,0.1,0.3 --betas 0.25,1.0
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


def zone_id(cat, zones, r_z):
    """(ns,) int: index of the zone box containing each placement, or -1."""
    zid = -np.ones(len(cat["t"]), dtype=int)
    for j, (t, cx, cy) in enumerate(zones):
        m = ((np.abs(cat["C"][:, 0] - cx) <= r_z) & (np.abs(cat["C"][:, 1] - cy) <= r_z)
             & (np.abs(cat["t"] - t) <= r_z))
        zid[m] = j
    return zid


def perturbed(zones, pins, d_in, d_out):
    """~6 variants per zone centre: +-displacement in cx, cy, t, at an in-zone and an
    out-of-zone scale, so the LP can actually trade ghost mass against non-ghost mass."""
    out = []
    for (t, cx, cy) in zones:
        for d in (d_in, d_out):
            for ax in range(3):
                for sg in (-1.0, 1.0):
                    tt, xx, yy = t, cx, cy
                    if ax == 0:
                        xx = cx + sg * d
                    elif ax == 1:
                        yy = cy + sg * d
                    else:
                        tt = min(1.0, max(0.0, t + sg * d))
                    if not core_free_mask(np.array([[xx, yy]]), theta_of(tt), pins)[0]:
                        continue
                    if pl.ENFORCE_CONTAINMENT and pl.contain_margin_exact(tt, xx, yy) < 0:
                        continue          # BUG FIX: a displaced variant can leave [0,s0]^2
                    out.append((tt, xx, yy))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_08")
    ap.add_argument("--betas", default="0.25,1.0")
    ap.add_argument("--gammas", default="0,0.1,0.3")
    ap.add_argument("--r_z", type=float, default=1e-3)
    ap.add_argument("--d_in", type=float, default=3e-4)
    ap.add_argument("--d_out", type=float, default=3e-3)
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
    ap.add_argument("--cls_budget", type=float, default=300.0)
    ap.add_argument("--zub", type=float, default=30.0)
    ap.add_argument("--chunk", type=int, default=384)
    ap.add_argument("--fine_global", type=float, default=0.05)
    ap.add_argument("--fine_local", type=float, default=0.02)
    ap.add_argument("--fine_radius", type=float, default=1.2)
    ap.add_argument("--fine_cap", type=int, default=9000)
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--headroom_wait", type=float, default=300.0)
    ap.add_argument("--no_control_cols", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--betas_pos", default=None,
                    help="beta list to use when gamma > 0 (defaults to --betas)")
    args = ap.parse_args()
    args.catalog = None

    fh = open(os.path.join(pl.BASE, "logs", "pairlp_%s_basin%s.log" % (args.cls, args.tag)), "w")
    T0 = time.time()
    log("A66 D3 basin-discount pair LP: class=%s betas=%s gammas=%s r_z=%g"
        % (args.cls, args.betas, args.gammas, args.r_z), fh)
    require_headroom(args.headroom, fh, args.headroom_wait)

    spec = json.load(open(pl.BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    N, k, m = int(e["N"]), int(e["k"]), len(boxes)
    thresh_base = N * (N - 1) // 2
    rebate = (N - 1) * (N - 2) // 2 * args.n_images          # C(N-1,2)*|G_S|
    log("class %s: N=%d m=%d  threshold = %d + beta*%d - gamma*%d"
        % (args.cls, N, m, thresh_base, m, rebate), fh)

    ctrl = control_family(args.cls, pins, boxes, fh)
    if ctrl is None:
        log("no crowdfam family -> no zones; abort", fh)
        sys.exit(2)
    zones = ctrl["placements"]                                # (t, cx, cy) per zone centre
    extra = list(zones) + perturbed(zones, pins, args.d_in, args.d_out)
    log("zones=%d, perturbed variants added=%d" % (len(zones), len(extra) - len(zones)), fh)

    cat = build_catalog(pins, boxes, args, fh, extra=extra)
    zid = zone_id(cat, zones, args.r_z)
    log("catalog |S|=%d, in-zone placements=%d (per zone %s)"
        % (len(cat["t"]), int((zid >= 0).sum()),
           [int((zid == j).sum()) for j in range(len(zones))]), fh)

    I, J = disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1") for a, b in zip(I, J)])
    bz = ((zid[I] >= 0) & (zid[J] >= 0) & (zid[I] != zid[J])).astype(float)
    log("disjoint pairs=%d, ghost pairs (bz=1)=%d" % (len(I), int(bz.sum())), fh)

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

    out = dict(cls=args.cls, N=N, m=m, n_images=args.n_images, r_z=args.r_z,
               d_in=args.d_in, d_out=args.d_out,
               threshold_formula="%d + beta*%d - gamma*%d" % (thresh_base, m, rebate),
               n_placements=int(len(cat["t"])), n_in_zone=int((zid >= 0).sum()),
               n_pairs_disjoint=int(len(I)), n_ghost_pairs=int(bz.sum()),
               control_sum_m2=ctrl["sum_m2"], cells=[])

    for gamma in [float(x) for x in args.gammas.split(",")]:
        store = RowStore()                       # rows are gamma-independent within a gamma sweep
        blist = ([float(x) for x in args.betas.split(",")] if gamma == 0
                 else [float(x) for x in (args.betas_pos or args.betas).split(",")])
        for beta in blist:
            require_headroom(args.headroom, fh, args.headroom_wait)
            if beta <= 0 and gamma > 0:
                log("SKIP gamma=%g beta=0: the discount is encoded through beta; use beta>0"
                    % gamma, fh)
                continue
            eff = (m2.astype(float) - (gamma / beta) * bz) if beta > 0 else m2.astype(float)
            # solve_beta computes obj = 1 + beta*eff, so eff encodes the discount exactly
            r = pl.solve_beta(cat, I, J, eff, P, A, beta, args, fh, store, boxes)
            lmax = max(r["Lmax_fine"] if r["Lmax_fine"] is not None else 1.0, 1.0)
            scaled = r["value"] / lmax
            thr = thresh_base + beta * m - gamma * rebate
            z = r["z"]
            mass = float(z.sum())
            ghost = float((z * bz).sum())
            cell = dict(beta=beta, gamma=gamma, value=r["value"], Lmax_fine=lmax,
                        scaled_value=scaled, threshold=thr, margin=scaled - thr,
                        converged=bool(r["converged"]),
                        sum_z=mass, ghost_mass=ghost,
                        ghost_mass_fraction=(ghost / mass if mass > 0 else 0.0),
                        mbar2=float((z * m2).sum() / mass) if mass > 0 else 0.0,
                        n_support_pairs=int(len(r["support"])),
                        rounds=r["rounds"], n_rows=r["n_rows"], note=r["note"],
                        seconds=r["seconds"])
            out["cells"].append(cell)
            log("CELL gamma=%.3g beta=%.3g: value=%.6f Lmax=%.6f scaled=%.6f thr=%.4f "
                "margin=%+.6f ghostfrac=%.4f converged=%s (%.0fs)"
                % (gamma, beta, r["value"], lmax, scaled, thr, scaled - thr,
                   cell["ghost_mass_fraction"], r["converged"], r["seconds"]), fh)
            json.dump(out, open(os.path.join(pl.BASE, "results",
                                             "pairlp_%s_basin%s.json" % (args.cls, args.tag)), "w"), indent=1)

    out["total_seconds"] = time.time() - T0
    fp = os.path.join(pl.BASE, "results", "pairlp_%s_basin%s.json" % (args.cls, args.tag))
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs)" % (fp, out["total_seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
