#!/usr/bin/env python3
"""
A38 / G1 seam probe -- the SECOND-SQUARE occupancy branch at a near-Trump witness leaf.

T0 seam S1 ("the ridge/cliff handoff") is the localization cascade: the interior-first tree pins
ONE square; K2/K3 need all eleven.  The pilot cannot run the cascade, but it can measure its first
step at a depth-3 near-Trump leaf.  That is this module.

Setup.  B1 is a depth-3 witness box (half-widths ~0.0131 in the centre, ~1.875 deg in theta) that
the census matched to Trump placement `match` under D4 element `d4`.  Let g = that element and
let p_0..p_10 = g(canonical_sig of atlas family 0) -- the eleven Trump placements in the frame in
which B1 sits.  Define, for each i != match,

    Z2_i = [cx_i - r, cx_i + r] x [cy_i - r, cy_i + r] x [th_i - dth, th_i + dth]   (mod 90)

(r = 0.06, dth = 6 deg by default), and Z2 = union_i Z2_i.  Rectangles are clipped to the
admissible centre range [0.5, s0 - 0.5] (a no-op: no unit square has a centre outside it); theta
windows that straddle 0/90 are split into two intervals, which is exact, not an approximation.

PROBE A -- occupancy.   node = Hyp(cores = [B1], nofams = [Z2_0 ... Z2_9]),  budget 11 - 1 = 10.
    NoFam semantics (caselp): a NoFam is a zone x theta-interval-list carrying the hypothesis
    "NO square of P has (centre, theta) in it".  Passing the ten Z2_i as nofams therefore
    hypothesises that NONE of the ten neighbourhoods is occupied.
    A certified tau < 10 kills that hypothesis, i.e. proves

        every 11-packing at s0 whose witness square lies in B1 has a SECOND square in Z2.

PROBE B -- branching.   For each i, node = Hyp(cores = [B1, Z2_i-as-a-core]), budget 11 - 2 = 9.
    Two kill routes per child:
      * the W2 PAIR node-kill (no LP, ~ms): c_1 = mlow_box(B1 inflated), c_2 = mlow_box(Z2_i
        inflated), both CONSERVATIVE LOWER bounds from fieldcut.  Corollary A33.2 with the
        two-element subfamily gives c_1 + c_2 <= 2 + eta for any 11-packing at sigma <= s-hat,
        so  c_1 + c_2 > 2 + eta_cert  (eta_cert = 0.4254 exactly)  kills the child outright.
      * the 2-core case-LP (node38.solve_a38_node, which also applies W1/W2 per-core and the
        field row filter).
    b2 = the number of children that survive both.  Together with PROBE A's verdict this is the
    branching factor the S1 cascade pays per additional square.

SOUND DIRECTION.  The Z2 boxes are HYPOTHESES (a branch disjunction over "which neighbourhood the
second square occupies"), never theorems, so they need no erosion and no outward rounding: making
them smaller only makes the resulting statement stronger and the LPs harder.  The only place a
one-sided bound is required is the W2 pair test, and it uses fieldcut.mlow_box / core_mlow, which
are conservative lower bounds by construction (SLOP = 1e-6 inward, box inflated by one grid cell).
The disjunction {PROBE A} u {PROBE B child i} is a COVER of the near-Trump leaf only if the
children are read as "some square lies in Z2_i"; with --exclusive the children are additionally
made pairwise disjoint by adding NoFams for the lower-indexed Z2_j (sound, and it tightens each
child's LP), which is off by default so the reported b2 matches the brief's definition.

    python seam38.py --witness w.json --r 0.06 --dth 6 --time_limit 300 --workers 4 \
                     --out ../results/seam_<tag>.json
    python seam38.py --smoke            # structure-only probe A + ONE 2-core LP at 120 s

witness json:  {"box": [x0,x1,y0,y1,th0,th1] or {"x0":..}, "match": 6, "d4": "e", "id": "..."}
(`match` / `d4` come straight from a census38 record's `trump` block.)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import multiprocessing as mp

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import census38 as cen                                       # noqa: E402
import fieldcut as fc                                        # noqa: E402
import node38                                                # noqa: E402
from caselp import Box, NoFam                                # noqa: E402

S0F = cen.S0F
R_DEFAULT = 0.06
DTH_DEFAULT = 6.0
CLO, CHI = 0.5, S0F - 0.5          # admissible centre range (necessary condition)

# depth-3 witness half-widths (design.md: level-1 cell 0.05241 / 7.5 deg, halved twice)
HW3, HTH3 = 0.0131, 1.875


# ------------------------------------------------------------------------ Trump in a D4 frame
def trump_placements(d4="e", atlas_path=cen.ATLAS_PATH, s0=S0F):
    """the 11 Trump placements (cx, cy, theta_deg mod 90) after applying D4 element `d4`."""
    A = cen.Atlas(atlas_path, s0=s0)
    rec = A.trump[0]
    g = dict((h[0], h) for h in cen.D4)[d4]
    P = cen.d4_points(g, rec["P"], s0)
    TH = np.array([cen.d4_theta_deg(g, t) for t in rec["TH"]])
    return [(float(P[i, 0]), float(P[i, 1]), float(TH[i])) for i in range(len(TH))], rec


# ------------------------------------------------------------------------------- Z2 geometry
def theta_window(th, dth, period=90.0):
    """[th-dth, th+dth] mod 90 as a list of 1 or 2 closed intervals inside [0,90]."""
    a, b = th - dth, th + dth
    if b - a >= period:
        return [(0.0, period)]
    a %= period
    b = a + 2.0 * dth
    if b <= period:
        return [(a, b)]
    return [(a, period), (0.0, b - period)]


def clip_rect(cx, cy, r):
    return (max(CLO, cx - r), min(CHI, cx + r), max(CLO, cy - r), min(CHI, cy + r))


def z2_families(places, match, r=R_DEFAULT, dth=DTH_DEFAULT):
    """the ten Z2_i, each as (index, NoFam, [Box, ...]).

    The NoFam carries the (possibly two-interval) theta window exactly.  A caselp Box cannot
    express a wrapped theta window, so a wrapped Z2_i yields TWO core boxes -- that is a split of
    the same hypothesis, not a loss: their union is Z2_i."""
    out = []
    for i, (cx, cy, th) in enumerate(places):
        if i == match:
            continue
        x0, x1, y0, y1 = clip_rect(cx, cy, r)
        ivs = theta_window(th, dth)
        nf = NoFam(x0, x1, y0, y1, ivs)
        boxes = [Box(x0, x1, y0, y1, a, b) for (a, b) in ivs]
        boxes = [b for b in boxes if b.core() is not None and not b.vacuous(S0F)]
        out.append(dict(i=i, centre=[cx, cy, th], nofam=nf, boxes=boxes,
                        rect=[x0, x1, y0, y1], thetas=ivs))
    return out


# -------------------------------------------------------------------------- W2 pair node-kill
def pair_test(B1, B2, meta, eta=None):
    """W2 PAIR kill (fieldcut.mlow_box on both cores, inflated by one grid cell).

    c_j is a conservative LOWER bound on min coverage over core j, so c_1 + c_2 > 2 + eta is a
    sound exclusion (Corollary A33.2, |I| = 2)."""
    eta = float(fc.ETA_CERT if eta is None else eta)
    c1 = fc.core_mlow(B1, meta)
    c2 = fc.core_mlow(B2, meta)
    return dict(c_1=c1, c_2=c2, sum=c1 + c2, thr=2.0 + eta, eta=eta, dead=bool(c1 + c2 > 2.0 + eta))


# ------------------------------------------------------------------------------- probe drivers
def probe_a_structure(B1, fams, budget=10):
    """the PROBE A node, as data (no solve)."""
    return dict(probe="A", budget=budget,
                core=B1.to_json(),
                n_nofams=len(fams),
                nofams=[f["nofam"].to_json() for f in fams],
                z2=[dict(i=f["i"], trump_placement=f["centre"], rect=f["rect"],
                         thetas=f["thetas"]) for f in fams],
                semantics=("Hyp(cores=[B1], nofams=Z2) = 'the witness square is in B1 AND NO "
                           "square of P lies in any Z2_i'; certified tau < %d kills it, i.e. every "
                           "packing with witness in B1 has a second square in Z2." % budget))


def _child_job(args):
    (i, k, s, b1j, b2j, budget, tl, eps_geo, w1, w2, outdir, nofj) = args
    t0 = time.time()
    rec = dict(i=i, k=k, box=b2j)
    try:
        B1 = Box.from_json(b1j)
        B2 = Box.from_json(b2j)
        mk = node38.mask()
        rec["pair_test"] = pair_test(B1, B2, mk.meta)
        if rec["pair_test"]["dead"]:
            rec["status"] = "dead(W2-pair)"
            rec["seconds"] = time.time() - t0
            return rec
        nofams = [NoFam.from_json(d) for d in nofj]
        out = os.path.join(outdir, "child_%d_%d.json" % (i, k)) if outdir else None
        r = node38.solve_a38_node(s, [B1, B2], budget, w1=w1, w2=w2, time_limit=tl,
                                  out=out, eps_geo=eps_geo, nofams=nofams,
                                  log=(lambda *a: None))
        rec.update({kk: r.get(kk) for kk in
                    ("status", "tau", "slack", "converged", "minmass", "maxcov",
                     "n_rows", "field", "filter")})
        rec["seconds"] = time.time() - t0
        return rec
    except Exception:
        rec["status"] = "error"
        rec["error"] = traceback.format_exc()[-1200:]
        rec["seconds"] = time.time() - t0
        return rec


def probe_b(B1, fams, s=S0F, budget=9, time_limit=300, workers=1, eps_geo=1e-4,
            w1=True, w2=True, outdir=None, exclusive=False, log=print):
    """the ten (or more, after theta splits) second-core children."""
    jobs = []
    for n, f in enumerate(fams):
        nofj = []
        if exclusive:
            nofj = [g["nofam"].to_json() for g in fams[:n]]
        for k, B2 in enumerate(f["boxes"]):
            jobs.append((f["i"], k, s, B1.to_json(), B2.to_json(), budget, time_limit,
                         eps_geo, w1, w2, outdir, nofj))
    recs = []
    if workers <= 1:
        for j in jobs:
            recs.append(_child_job(j))
            log("  child %s -> %s" % ((recs[-1]["i"], recs[-1]["k"]), recs[-1].get("status")))
    else:
        with mp.Pool(min(workers, len(jobs))) as pool:
            for r in pool.imap_unordered(_child_job, jobs):
                recs.append(r)
                log("  child %s -> %s" % ((r["i"], r["k"]), r.get("status")))
    recs.sort(key=lambda r: (r["i"], r["k"]))
    dead = [r for r in recs if str(r.get("status", "")).startswith("dead")]
    alive = [r for r in recs if not str(r.get("status", "")).startswith("dead")]
    return dict(probe="B", budget=budget, n_children=len(recs),
                n_dead=len(dead), b2=len(alive),
                dead_by=_tally(r.get("status") for r in dead),
                children=recs)


def _tally(it):
    t = {}
    for v in it:
        t[v] = t.get(v, 0) + 1
    return t


# ----------------------------------------------------------------------------- witness parsing
def parse_witness(path):
    d = json.load(open(path))
    if isinstance(d, list):
        d = d[0]
    b = d.get("box", d)
    if isinstance(b, dict):
        box = [float(b[k]) for k in ("x0", "x1", "y0", "y1", "th0", "th1")]
    else:
        box = [float(v) for v in b[:6]]
    match = d.get("match", d.get("placement"))
    d4 = d.get("d4", "e")
    if match is None:
        raise SystemExit("witness json needs 'match' (Trump placement index) -- take it from a "
                         "census38 record's trump.placement / trump.d4")
    return dict(id=d.get("id", "w"), box=box, match=int(match), d4=str(d4))


# ------------------------------------------------------------------------------------- smoke
def smoke(time_limit=120.0, r=R_DEFAULT, dth=DTH_DEFAULT, out=None):
    """Structure-only PROBE A + exactly ONE 2-core LP (the campaign is running: 1 worker)."""
    places, rec = trump_placements("e")
    # B1 = the depth-3 box around Trump placement (1.959613, 1.688559), theta 49.82 +- 1.875
    c1 = (1.959613, 1.688559)
    c2 = (1.272254, 2.424525)
    idx1 = min(range(11), key=lambda i: max(abs(places[i][0] - c1[0]), abs(places[i][1] - c1[1])))
    idx2 = min(range(11), key=lambda i: max(abs(places[i][0] - c2[0]), abs(places[i][1] - c2[1])))
    th1 = places[idx1][2]
    th2 = places[idx2][2]
    B1 = Box(c1[0] - HW3, c1[0] + HW3, c1[1] - HW3, c1[1] + HW3, 49.82 - HTH3, 49.82 + HTH3)
    B2 = Box(c2[0] - HW3, c2[0] + HW3, c2[1] - HW3, c2[1] + HW3, 49.82 - HTH3, 49.82 + HTH3)
    fams = z2_families(places, idx1, r=r, dth=dth)
    A = probe_a_structure(B1, fams, budget=10)

    print("=" * 78)
    print("A38 SEAM SMOKE  (s0 = %.6f, D4 element 'e', Trump family 0)" % S0F)
    print("theta convention: caselp Box th0/th1 are the square's rotation in DEGREES in [0,90]")
    print("  atlas theta[%d] = %.6f rad = %.4f deg (mod 90); B1 uses [%.4f, %.4f] deg,"
          % (idx1, math.radians(th1), th1, 49.82 - HTH3, 49.82 + HTH3))
    print("  which contains it with margin %.4f deg -- no remapping of 49.82 is needed."
          % min(th1 - (49.82 - HTH3), (49.82 + HTH3) - th1))
    print("-" * 78)
    print("PROBE A structure (NOT solved): core B1 = %r, budget %d, %d NoFams"
          % (B1, A["budget"], A["n_nofams"]))
    for z in A["z2"]:
        print("   Z2_%-2d trump p=(%.6f, %.6f, %.4f deg)  rect=[%.4f,%.4f]x[%.4f,%.4f] "
              "thetas=%s" % (z["i"], z["trump_placement"][0], z["trump_placement"][1],
                             z["trump_placement"][2], z["rect"][0], z["rect"][1],
                             z["rect"][2], z["rect"][3],
                             ["[%.3f,%.3f]" % t for t in z["thetas"]]))
    print("   " + A["semantics"])
    print("-" * 78)

    mk = node38.mask()
    pt = pair_test(B1, B2, mk.meta)
    print("W2 pair test on the smoke pair: c_1 = %.9f  c_2 = %.9f  sum = %.9f  thr = 2 + eta = "
          "%.9f  -> %s" % (pt["c_1"], pt["c_2"], pt["sum"], pt["thr"],
                           "DEAD" if pt["dead"] else "no kill"))
    print("2-core LP smoke: cores [%r, %r] budget 9 time_limit %.0f s, 1 worker"
          % (B1, B2, time_limit))
    t0 = time.time()
    res = node38.solve_a38_node(S0F, [B1, B2], 9, w1=True, w2=True, time_limit=time_limit,
                                out=None, log=(lambda *a: None))
    wall = time.time() - t0
    print("  status=%s tau=%.6f (budget 9, slack %.6f) converged=%s minmass=%s maxcov=%s "
          "n_rows=%s  %.1f s"
          % (res.get("status"), res.get("tau", float("nan")), res.get("slack", float("nan")),
             res.get("converged"), res.get("minmass"), res.get("maxcov"), res.get("n_rows"), wall))
    print("  field: %s" % json.dumps(res.get("field")))
    print("  filter: %s" % json.dumps(res.get("filter")))
    print("=" * 78)

    rep = dict(kind="seam38-smoke", s0=S0F, d4="e", r=r, dth=dth,
               B1=B1.to_json(), B2=B2.to_json(),
               trump_match_B1=dict(index=idx1, placement=list(places[idx1])),
               trump_match_B2=dict(index=idx2, placement=list(places[idx2])),
               probe_a_structure=A, pair_test=pt,
               lp=dict(time_limit=time_limit, wall_s=wall,
                       **{k: res.get(k) for k in ("status", "tau", "slack", "converged",
                                                  "minmass", "maxcov", "n_rows", "n_orbits",
                                                  "iters", "field", "filter", "seconds")}))
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        json.dump(rep, open(out, "w"), indent=1)
        print("->", out)
    return rep


# --------------------------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--witness", default=None, help="json: {box, match, d4}")
    ap.add_argument("--r", type=float, default=R_DEFAULT)
    ap.add_argument("--dth", type=float, default=DTH_DEFAULT)
    ap.add_argument("--time_limit", type=float, default=300.0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--eps_geo", type=float, default=1e-4)
    ap.add_argument("--probe", default="all", choices=("structure", "A", "B", "all"))
    ap.add_argument("--exclusive", action="store_true",
                    help="probe B children carry NoFams for the lower-indexed Z2_j "
                         "(pairwise-disjoint disjunction; sound, tightens each LP)")
    ap.add_argument("--w1", type=int, default=1)
    ap.add_argument("--w2", type=int, default=1)
    ap.add_argument("--out", default=None)
    ap.add_argument("--outdir", default=None, help="per-child node json dir")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    if a.smoke or not a.witness:
        smoke(time_limit=min(a.time_limit, 120.0), r=a.r, dth=a.dth, out=a.out)
        return

    w = parse_witness(a.witness)
    B1 = Box(*w["box"])
    places, _ = trump_placements(w["d4"])
    fams = z2_families(places, w["match"], r=a.r, dth=a.dth)
    rep = dict(kind="seam38", s0=S0F, witness=w, r=a.r, dth=a.dth,
               time_limit=a.time_limit, exclusive=bool(a.exclusive),
               trump_match=dict(index=w["match"], placement=list(places[w["match"]])))
    A = probe_a_structure(B1, fams, budget=10)
    rep["probe_a_structure"] = A
    print(json.dumps({k: A[k] for k in ("probe", "budget", "n_nofams")}), flush=True)
    for z in A["z2"]:
        print("  Z2_%-2d %s thetas=%s" % (z["i"], [round(v, 5) for v in z["rect"]], z["thetas"]),
              flush=True)

    if a.outdir:
        os.makedirs(a.outdir, exist_ok=True)

    if a.probe in ("A", "all"):
        t0 = time.time()
        r = node38.solve_a38_node(S0F, [B1], 10, w1=bool(a.w1), w2=bool(a.w2),
                                  time_limit=a.time_limit, eps_geo=a.eps_geo,
                                  nofams=[f["nofam"] for f in fams],
                                  out=(os.path.join(a.outdir, "probeA.json") if a.outdir else None))
        r["wall_s"] = time.time() - t0
        r["occupancy_certified"] = bool(str(r.get("status", "")).startswith("dead"))
        rep["probe_a"] = {k: v for k, v in r.items() if k != "nofams"}
        print("PROBE A: status=%s tau=%s budget=10 -> second square in Z2 %s"
              % (r.get("status"), r.get("tau"), "PROVED" if r["occupancy_certified"] else "not proved"),
              flush=True)

    if a.probe in ("B", "all"):
        rep["probe_b"] = probe_b(B1, fams, budget=9, time_limit=a.time_limit,
                                 workers=a.workers, eps_geo=a.eps_geo,
                                 w1=bool(a.w1), w2=bool(a.w2), outdir=a.outdir,
                                 exclusive=a.exclusive)
        print("PROBE B: %d children, %d dead %s -> b2 = %d"
              % (rep["probe_b"]["n_children"], rep["probe_b"]["n_dead"],
                 json.dumps(rep["probe_b"]["dead_by"]), rep["probe_b"]["b2"]), flush=True)

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(rep, open(a.out, "w"), indent=1)
        print("->", a.out, flush=True)


if __name__ == "__main__":
    main()
