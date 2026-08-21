#!/usr/bin/env python3
"""
A24 probe.py -- LP probes (T1) of the nodes an INTERIOR-FIRST composed tree needs.

A14 proved the wall-first tree is barren at 3.84 (corner refinement never kills:
tau* = budget with the 1/4-structure intact, LP slack GROWS with depth).  T2
(wastage) is worthless on corner/side squares (A23: flush corners strand 0) and
bites only on interior mid-tilt squares.  So the composed tree must branch on the
INTERIOR zone first.  This script measures the T1 value of the candidate root
branches.

  python probe.py --tag P --which interior_no,interior_no_midtilt,... --workers 4
"""
from __future__ import annotations

import argparse, json, math, os, sys, time, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import multiprocessing as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpbox
import caselp
from caselp import Box, NoFam, Hyp, solve_node, warm_from_result

A13 = os.path.join(os.path.dirname(HERE), "A13-case-lp-bnb")
A14 = os.path.join(os.path.dirname(HERE), "A14-close-tree-384")


def zones(s, cw=0.6):
    a, b = 0.5, s - 0.5
    c0, c1 = a + cw, b - cw
    return dict(corner0=(a, c0, a, c0), corner1=(c1, b, a, c0), corner2=(c1, b, c1, b),
                corner3=(a, c0, c1, b), side0=(a, c0, c0, c1), side1=(c0, c1, a, c0),
                side2=(c1, b, c0, c1), side3=(c0, c1, c1, b), interior=(c0, c1, c0, c1))


def nf(rect, thetas=((0.0, 90.0),)):
    return NoFam(rect[0], rect[1], rect[2], rect[3], list(thetas))


MID = (15.0, 75.0)


def build(name, s):
    """returns (Hyp, budget, note)"""
    Z = zones(s)
    if name == "root":
        return Hyp(), 11, "root"
    if name == "int_no":
        return Hyp((), [nf(Z["interior"])]), 11, "NO square centred in the interior zone (all theta)"
    if name == "int_no_mid":
        return Hyp((), [nf(Z["interior"], [MID])]), 11, "NO interior square with theta in [15,75]"
    if name == "int_no_mid_wide":
        # interior zone widened to the whole non-corner centre domain
        a, b = 0.5, s - 0.5
        return Hyp((), [NoFam(a + 0.35, b - 0.35, a + 0.35, b - 0.35, [MID])]), 11, \
            "NO square centred in [0.85, s-0.85]^2 with theta in [15,75]"
    if name == "mid_no_all":
        # NO square anywhere with mid tilt (orientation-only family; D4 symmetric)
        a, b = 0.5, s - 0.5
        return Hyp((), [NoFam(a, b, a, b, [MID])]), 11, "NO square at all with theta in [15,75]"
    if name == "corners_no":
        return Hyp((), [nf(Z[f"corner{i}"]) for i in range(4)]), 11, "NO(all corner zones) [D4]"
    if name == "sides_no":
        return Hyp((), [nf(Z[f"side{i}"]) for i in range(4)]), 11, "NO(all side zones) [D4]"
    if name == "int_no_sides_no":
        return Hyp((), [nf(Z["interior"])] + [nf(Z[f"side{i}"]) for i in range(4)]), 11, \
            "NO interior AND NO all side zones [D4]"
    if name.startswith("intz_"):
        # interior-occupancy ladder: NO(interior zone of half-margin cw), all theta.
        # smaller zone = STRONGER theorem = harder LP.
        cw = float(name.split("_")[1]) / 100.0
        a, b = 0.5, s - 0.5
        c0, c1 = a + cw, b - cw
        return Hyp((), [NoFam(c0, c1, c0, c1, [(0.0, 90.0)])]), 11,             f"NO square centred in [{c0:.2f},{c1:.2f}]^2 (interior zone, cw={cw})"
    if name.startswith("thw_"):
        # orientation-window ladder: NO square anywhere with theta in [w, 90-w]
        w = float(name.split("_")[1])
        a, b = 0.5, s - 0.5
        return Hyp((), [NoFam(a, b, a, b, [(w, 90.0 - w)])]), 11,             f"NO square at all with theta in [{w},{90-w}]"
    if name.startswith("intmid_"):
        # "some square centred in the interior zone (cw) with theta in [w,90-w]"
        _, cws, ws = name.split("_")
        cw, w = float(cws) / 100.0, float(ws)
        a, b = 0.5, s - 0.5
        c0, c1 = a + cw, b - cw
        return Hyp((), [NoFam(c0, c1, c0, c1, [(w, 90.0 - w)])]), 11,             f"NO square centred in [{c0:.2f},{c1:.2f}]^2 with theta in [{w},{90-w}]"
    if name.startswith("gbox_"):
        # generic single interior core: gbox_<x1000>_<y1000>_<th0>_<th1>_<d1000>
        _, xs, ys, th0, th1, d1000 = name.split("_")
        cx, cy = float(xs) / 1000.0, float(ys) / 1000.0
        th0, th1, d = float(th0), float(th1), float(d1000) / 1000.0
        b = Box(cx - d, cx + d, cy - d, cy + d, th0, th1)
        c = b.core()
        return Hyp([b], ()), 10, f"YES one interior core {b!r} (core half-side a={float(c.a):.4f})"
    if name.startswith("ibox_"):
        # ONE interior core box at pinwheel centre i, orientation window [th0,th1],
        # centre half-width d/1000:  ibox_<i>_<th0>_<th1>_<d1000>
        _, i, th0, th1, d1000 = name.split("_")
        i, th0, th1, d = int(i), float(th0), float(th1), float(d1000) / 1000.0
        import sys as _s, os as _o
        _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
        from sweep import pinwheel_centres
        from fractions import Fraction as _F
        C = pinwheel_centres(_F(s).limit_denominator(10 ** 6))
        cx, cy = float(C[i][0]), float(C[i][1])
        b = Box(cx - d, cx + d, cy - d, cy + d, th0, th1)
        return Hyp([b], ()), 10, f"YES one interior core at ({cx:.3f},{cy:.3f}) theta[{th0},{th1}] d={d}"
    if name.startswith("pwbox"):
        # HEAD-TO-HEAD: the node whose hypothesis is k core boxes on the (rigidly
        # translated) A12 interior pinwheel 4-cycle, half-width d, theta 33 +- a.
        # T2 kills this node (A24 sweep); does T1?
        _, ks, ds, as_ = name.split("_")
        k, d, adeg = int(ks), float(ds) / 1000.0, float(as_)
        import sys as _s, os as _o
        _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
        from sweep import pinwheel_centres
        from fractions import Fraction as _F
        C = pinwheel_centres(_F(s).limit_denominator(10 ** 6))
        bs = [Box(float(cx) - d, float(cx) + d, float(cy) - d, float(cy) + d,
                  33.0 - adeg, 33.0 + adeg) for (cx, cy) in C[:k]]
        return Hyp(bs, ()), 11 - k, f"YES {k} pinwheel cores d={d} a={adeg}"
    if name.startswith("int_yes"):
        # YES: a core box inside the interior zone with mid tilt.  int_yes_<i>_<j>_<k>
        _, _, i, j, k = name.split("_")
        i, j, k = int(i), int(j), int(k)
        x0, x1, y0, y1 = Z["interior"]
        nx = ny = 4
        b = Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                15.0 + 30.0 * k, 15.0 + 30.0 * (k + 1))
        return Hyp([b], ()), 10, f"YES interior box {b!r}"
    raise ValueError(name)


def _run(args):
    name, s, tl, eps_geo, warm_path, tag = args
    try:
        if eps_geo is not None:
            lpbox.EPS_GEO = eps_geo
        hyp, budget, note = build(name, s)
        sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
        out = os.path.join(HERE, "results", f"{tag}_{name}.json")
        lp = os.path.join(HERE, "logs", f"{tag}_{name}.log")

        def log(*a):
            with open(lp, "a") as f:
                f.write(" ".join(str(x) for x in a) + "\n")
        warm = None
        if warm_path and os.path.exists(warm_path):
            warm = warm_from_result(json.load(open(warm_path)))
        log(f"### {name} s={s} sym={sym} budget={budget} EPS_GEO={lpbox.EPS_GEO} tl={tl} :: {note}")
        t0 = time.time()
        res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=tl, out=out, log=log,
                         max_rows_add=1500, max_cols_add=1500, col_stop_iter=10 ** 6,
                         col_stop_cov=1.01, checkpoint=out.replace(".json", "_state.json"),
                         prune=6, prune_cols=2, alternate=True)
        r = dict(name=name, note=note, s=s, budget=budget, sym=sym, tau=res["tau"],
                 slack=res["tau"] - budget, converged=res["converged"],
                 minmass=res["minmass"], maxcov=res["maxcov"], n_rows=res["n_rows"],
                 seconds=time.time() - t0)
        log("RESULT " + json.dumps(r))
        return r
    except Exception:
        return dict(name=name, error=traceback.format_exc()[-1500:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="p")
    ap.add_argument("--which", required=True)
    ap.add_argument("--s", type=float, default=3.84)
    ap.add_argument("--time_limit", type=float, default=900)
    ap.add_argument("--eps_geo", type=float, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--warm", default=os.path.join(A13, "results", "t384c", "node_0.json"))
    a = ap.parse_args()
    names = a.which.split(",")
    jobs = [(n, a.s, a.time_limit, a.eps_geo, a.warm, a.tag) for n in names]
    out = []
    with mp.Pool(min(a.workers, len(jobs))) as pool:
        for r in pool.imap_unordered(_run, jobs):
            out.append(r)
            print(json.dumps(r), flush=True)
            json.dump(out, open(os.path.join(HERE, "results", f"probes_{a.tag}.json"), "w"), indent=1)
    print("PROBES DONE")


if __name__ == "__main__":
    main()
