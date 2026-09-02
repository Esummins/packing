r"""
A66 D4: the structure of the k4_08 pair-LP tie at gamma=0, beta=1.0 (value 28.000000 = the
threshold 21 + 7*beta), and an EXACT verification of it if it is integral.

The basin-run cell reported sum_z = 21 over 21 support pairs with mbar2 = 1/3, i.e.
sum z*m2 = 7 = m -- one MORE box-incidence than crowdfam's family (sum m2 = 6, TL(0,0)
deficient).  If that support is an integral 7-family it is a full death witness in the sense of
pair_kill.md sect. 4, and it kills the pair route for k4_08 at EVERY beta, not just beta = 0.

All verification is exact: with t rational, cos(theta) = (1-t^2)/(1+t^2) and
sin(theta) = 2t/(1+t^2) are rational and c^2 + s^2 = 1 exactly, so every separating-axis
projection and half-width is a Fraction.

    python code\tie08.py
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
import basinlp as bl
from pairlp import (log, require_headroom, membership, dedupe_by_pattern, build_points,
                    build_catalog, control_family, disjoint_pairs, RowStore)

DEN = 10 ** 8


# ---------------------------------------------------------------- exact geometry
def cs(t):
    """exact (cos theta, sin theta) for theta = 2*atan(t); c^2 + s^2 = 1 exactly."""
    d = 1 + t * t
    return (1 - t * t) / d, 2 * t / d


def hw(u, c, s):
    """exact half-width of the unit square with tilt (c,s) on the unit direction u."""
    return (abs(u[0] * c + u[1] * s) + abs(-u[0] * s + u[1] * c)) / 2


def sat_gap(P, Q):
    """exact max-over-normals separation gap of two unit squares ((cx,cy,c,s) each).
    > 0 <=> interiors disjoint with room to spare."""
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    best = None
    for (c, s) in ((P[2], P[3]), (Q[2], Q[3])):
        for u in ((c, s), (-s, c)):
            g = abs(dx * u[0] + dy * u[1]) - hw(u, P[2], P[3]) - hw(u, Q[2], Q[3])
            best = g if best is None else max(best, g)
    return best


def core_gap(P, pin):
    """exact max-over-normals gap against an AXIS unit square at `pin`.
    >= 0 <=> the placement meets no part of that (full, delta=0) core."""
    dx, dy = P[0] - pin[0], P[1] - pin[1]
    w = abs(P[2]) + abs(P[3])
    thr = (1 + w) / 2
    best = abs(dx) - thr
    for g in (abs(dy) - thr,
              abs(dx * P[2] + dy * P[3]) - thr,
              abs(-dx * P[3] + dy * P[2]) - thr):
        best = max(best, g)
    return best


def box_margin(P, box):
    """exact min-over-normals slack of the OPEN-interior incidence with an axis unit box.
    > 0 <=> interiors meet (and by how much on the tightest axis)."""
    dx, dy = P[0] - box[0], P[1] - box[1]
    w = abs(P[2]) + abs(P[3])
    thr = (1 + w) / 2
    return min(thr - abs(dx), thr - abs(dy),
               thr - abs(dx * P[2] + dy * P[3]),
               thr - abs(-dx * P[3] + dy * P[2]))


def _subsets(lst, k):
    from itertools import combinations
    return [list(c) for c in combinations(lst, k)]


def fr(x, den=DEN):
    return Fr(round(Fr(x).limit_denominator(10 ** 14) * den), den)


def main():
    ap = argparse.ArgumentParser()
    for a, k in (("--cls", dict(default="k4_08")), ("--tag", dict(default="")), ("--beta", dict(type=float, default=1.0)),
                 ("--r_z", dict(type=float, default=1e-3)),
                 ("--d_in", dict(type=float, default=3e-4)),
                 ("--d_out", dict(type=float, default=3e-3)),
                 ("--cap_total", dict(type=int, default=300)),
                 ("--cap_m2", dict(type=int, default=200)),
                 ("--cap_m1", dict(type=int, default=60)),
                 ("--cap_coarse", dict(type=int, default=40)),
                 ("--min_sep", dict(type=float, default=0.35)),
                 ("--max_rounds", dict(type=int, default=40)),
                 ("--max_cuts", dict(type=int, default=1500)),
                 ("--max_rows", dict(type=int, default=25000)),
                 ("--max_nnz", dict(type=int, default=25000000)),
                 ("--outer_passes", dict(type=int, default=3)),
                 ("--cut_tol", dict(type=float, default=1e-6)),
                 ("--fine_tol", dict(type=float, default=1.05)),
                 ("--probe_squares", dict(type=int, default=200)),
                 ("--probe_cap", dict(type=int, default=4000)),
                 ("--seg_cap", dict(type=int, default=900000)),
                 ("--probe_eps", dict(type=float, default=1e-5)),
                 ("--n_seed_random", dict(type=int, default=2000)),
                 ("--lp_time", dict(type=float, default=600.0)),
                 ("--cls_budget", dict(type=float, default=600.0)),
                 ("--zub", dict(type=float, default=30.0)),
                 ("--chunk", dict(type=int, default=384)),
                 ("--fine_global", dict(type=float, default=0.05)),
                 ("--fine_local", dict(type=float, default=0.02)),
                 ("--fine_radius", dict(type=float, default=1.2)),
                 ("--fine_cap", dict(type=int, default=9000)),
                 ("--seed", dict(type=int, default=20260901)),
                 ("--headroom", dict(type=float, default=6.0)),
                 ("--headroom_wait", dict(type=float, default=300.0))):
        ap.add_argument(a, **k)
    args = ap.parse_args()
    args.catalog = None
    args.no_control_cols = False

    fh = open(os.path.join(pl.BASE, "logs", "tie_%s%s.log" % (args.cls, args.tag)), "w")
    T0 = time.time()
    log("A66 D4 tie structure: class=%s beta=%g (gamma=0)" % (args.cls, args.beta), fh)
    require_headroom(args.headroom, fh, args.headroom_wait)

    spec = json.load(open(pl.BOXSPEC))
    e = spec["classes"][args.cls]
    pinsQ = [(Fr(a), Fr(b)) for a, b in e["pins"]]
    boxesQ = [(Fr(b["slot"][0]), Fr(b["slot"][1])) for b in e["boxes"]]
    tags = ["%s%s" % (b["corner"], tuple(b["cell"])) for b in e["boxes"]]
    pins = np.array([[float(a), float(b)] for a, b in pinsQ])
    boxes = np.array([[float(a), float(b)] for a, b in boxesQ])
    N, m = int(e["N"]), len(boxes)
    thresh = N * (N - 1) // 2 + args.beta * m

    # ---- reproduce the basin-run catalog exactly (same zones + perturbations + seed)
    ctrl = control_family(args.cls, pins, boxes, fh)
    zones = ctrl["placements"]
    extra = list(zones) + bl.perturbed(zones, pins, args.d_in, args.d_out)
    cat = build_catalog(pins, boxes, args, fh, extra=extra)
    I, J = disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1") for a, b in zip(I, J)])
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

    r = pl.solve_beta(cat, I, J, m2, P, A, args.beta, args, fh, RowStore(), boxes)
    z = r["z"]
    sup = np.nonzero(z > 1e-9)[0]
    lmax = max(r["Lmax_fine"] or 1.0, 1.0)
    log("LP: value=%.9f Lmax_fine=%.9f threshold=%.4f support pairs=%d converged=%s"
        % (r["value"], lmax, thresh, len(sup), r["converged"]), fh)

    zs = z[sup]
    integral = bool(np.all((np.abs(zs - 1.0) < 1e-6) | (np.abs(zs) < 1e-6)))
    sq = np.unique(np.concatenate([I[sup], J[sup]])) if len(sup) else np.zeros(0, dtype=int)
    integral = integral and len(sup) == N * (N - 1) // 2 and len(sq) == N
    log("support: %d pairs, %d distinct placements, z in {0,1}? %s -> INTEGRAL=%s"
        % (len(sup), len(sq), bool(np.all((np.abs(zs - 1.0) < 1e-6) | (np.abs(zs) < 1e-6))),
           integral), fh)

    out = dict(cls=args.cls, beta=args.beta, gamma=0.0, N=N, m=m, box_tags=tags,
               lp_value=r["value"], Lmax_fine=lmax, threshold=thresh,
               converged=bool(r["converged"]), n_support_pairs=int(len(sup)),
               n_support_placements=int(len(sq)), integral=integral,
               crowdfam_sum_m2=ctrl["sum_m2"], crowdfam_box_meets=ctrl["box_meet_counts"])

    weights_integral = bool(np.all((np.abs(zs - 1.0) < 1e-6) | (np.abs(zs) < 1e-6)))
    out["weights_integral"] = weights_integral
    out["support_sum_m2"] = int(sum(int(m2[k]) for k in sup))
    deg = {}
    for k in sup:
        deg[int(I[k])] = deg.get(int(I[k]), 0) + 1
        deg[int(J[k])] = deg.get(int(J[k]), 0) + 1
    out["support_degree_sequence"] = sorted(deg.values(), reverse=True)
    out["support_placements"] = [[float(cat["t"][a]), float(cat["C"][a, 0]),
                                  float(cat["C"][a, 1]), int(cat["m"][a])] for a in sq]

    if not integral:
        # The tie object is NOT a single N-family.  Find the N-cliques of the DISJOINTNESS graph
        # restricted to the support placements -- those are the genuine death-witness candidates
        # (sect. 4) hiding inside it -- and score each by its sum m2.
        idx = {int(a): p for p, a in enumerate(sq)}
        n = len(sq)
        adj = [set() for _ in range(n)]
        pm2 = {}
        for k in range(len(I)):
            a, b = int(I[k]), int(J[k])
            if a in idx and b in idx:
                pa, pb = idx[a], idx[b]
                adj[pa].add(pb)
                adj[pb].add(pa)
                pm2[(min(pa, pb), max(pa, pb))] = int(m2[k])
        cliques = []

        def bk(R, Pv, X):
            if not Pv and not X:
                if len(R) >= N:
                    cliques.append(sorted(R))
                return
            if len(R) + len(Pv) < N:
                return
            piv = max(Pv | X, key=lambda v: len(adj[v]))
            for v in list(Pv - adj[piv]):
                bk(R | {v}, Pv & adj[v], X & adj[v])
                Pv = Pv - {v}
                X = X | {v}

        bk(set(), set(range(n)), set())
        fams = []
        for cl in cliques:
            for comb in ([cl] if len(cl) == N else _subsets(cl, N)):
                sm2 = sum(pm2[(min(a, b), max(a, b))]
                          for i, a in enumerate(comb) for b in comb[i + 1:])
                fams.append(dict(n_placements=len(comb), sum_m2=int(sm2),
                                 placements=[[float(cat["t"][sq[p]]), float(cat["C"][sq[p], 0]),
                                              float(cat["C"][sq[p], 1])] for p in comb],
                                 support_index=[int(p) for p in comb]))
        fams.sort(key=lambda d: -d["sum_m2"])
        out["n_full_families_in_support"] = len(fams)
        out["families"] = fams[:10]
        out["largest_integral_sum_m2"] = fams[0]["sum_m2"] if fams else None
        log("NOT an N-family: weights integral=%s on %d pairs over %d placements "
            "(degree seq %s); support sum m2=%d; %d N-cliques inside, largest sum m2=%s"
            % (weights_integral, len(sup), len(sq), out["support_degree_sequence"],
               out["support_sum_m2"], len(fams), out["largest_integral_sum_m2"]), fh)
        if fams:                      # exact-verify the best N-clique found
            best = fams[0]["support_index"]
            sq = np.array([sq[p] for p in best])
            integral = True
            out["exact_target"] = "best N-clique inside the tie support (sum m2 = %d)" % fams[0]["sum_m2"]
    if integral:
        # ---------------- exact verification of the 7-family at denominator 1e8
        fam = []
        for a in sq:
            t = fr(float(cat["t"][a]))
            c, s = cs(t)
            fam.append((fr(float(cat["C"][a, 0])), fr(float(cat["C"][a, 1])), c, s, t))
        gaps = []
        for i in range(N):
            for j in range(i + 1, N):
                gaps.append((i, j, sat_gap(fam[i], fam[j])))
        min_gap = min(g for _, _, g in gaps)
        cores = [(i, k, core_gap(fam[i], pinsQ[k])) for i in range(N) for k in range(len(pinsQ))]
        min_core = min(g for _, _, g in cores)
        cont = [pl.contain_margin_exact(f[4], f[0], f[1]) for f in fam]
        min_cont = min(cont)
        inc = [[b for b in range(m) if box_margin(fam[i], boxesQ[b]) > 0] for i in range(N)]
        Isingle = sum(len(x) for x in inc)
        meets = [[i for i in range(N) if b in inc[i]] for b in range(m)]
        summ2 = sum(len(set(inc[i]) & set(inc[j])) for i in range(N) for j in range(i + 1, N))
        out["exact"] = dict(
            denominator=DEN,
            family=[dict(t=str(f[4]), cx=str(f[0]), cy=str(f[1])) for f in fam],
            pairwise_disjoint=bool(min_gap > 0), min_sat_gap=str(min_gap),
            min_sat_gap_float=float(min_gap),
            all_core_free=bool(min_core > 0), min_core_gap=str(min_core),
            min_core_gap_float=float(min_core),
            all_contained=bool(min_cont >= 0), min_containment_margin=str(min_cont),
            min_containment_margin_float=float(min_cont),
            per_placement_containment=[float(c) for c in cont],
            I_single_incidences=Isingle,
            box_meet_counts=[len(x) for x in meets],
            box_meeters=meets, sum_m2=summ2,
            per_placement_boxes=inc)
        log("EXACT: min SAT gap=%.3e, min core gap=%.3e, min CONTAINMENT margin=%.3e, "
            "I=%d, box meets=%s, sum m2=%d"
            % (float(min_gap), float(min_core), float(min_cont), Isingle,
               [len(x) for x in meets], summ2), fh)
        # the deficient-in-crowdfam box: who supplies the second meeter, and by what margin
        defb = [b for b in range(m) if ctrl["box_meet_counts"][b] < 2]
        det = []
        for b in defb:
            mm = [dict(placement=int(i), t=str(fam[i][4]), cx=str(fam[i][0]), cy=str(fam[i][1]),
                       margin=str(box_margin(fam[i], boxesQ[b])),
                       margin_float=float(box_margin(fam[i], boxesQ[b]))) for i in meets[b]]
            mm.sort(key=lambda d: d["margin_float"])
            det.append(dict(box=tags[b], box_index=b, crowdfam_meeters=ctrl["box_meet_counts"][b],
                            tie_meeters=len(meets[b]), meeters=mm))
            log("box %s (crowdfam had %d meeter(s)): tie family has %d; weakest margin %s (%.3e)"
                % (tags[b], ctrl["box_meet_counts"][b], len(meets[b]),
                   mm[0]["margin"] if mm else "-", mm[0]["margin_float"] if mm else 0.0), fh)
        out["exact"]["previously_deficient_boxes"] = det
        out["exact"]["is_full_death_witness"] = bool(min_gap > 0 and min_core > 0
                                                    and min_cont >= 0 and summ2 >= m)

    out["seconds"] = time.time() - T0
    fp = os.path.join(pl.BASE, "results", "k4_08_tie_witness%s.json" % args.tag)
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs)" % (fp, out["seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
