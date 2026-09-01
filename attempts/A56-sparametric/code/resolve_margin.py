#!/usr/bin/env python3
"""
resolve_margin.py -- A56 pass 3, item 2: RE-SOLVE-WITH-MARGIN, validated and priced.

Idea.  A parametric FAIL is never a hole: it is a placement whose covering atom sits a few 1e-4
from the boundary of Q, so the box tree cannot certify it once the atom is smeared over an
s-interval.  Refining the tree is exponential (pass 2 measured 0/5 conversions at depth 60).
The cheap fix is to move the problem back to the LP: hand the guard LP the exact placements the
4D verifier choked on as extra rows, re-solve, and re-certify with the largest weight scale the
budget allows.  The resulting certificate has real coverage slack at those placements and then
verifies at depth 48 over the whole window.

RECIPE (mechanical; this script is the executable form of it)
  1. slots      <- A53 results/name_to_slots.json[name];  hyp = hyp_from_slots(slots);
                   budget = 11 - k.
  2. warm start <- union of (a) atoms_all / rows_all of the A53 node json (read-only) and
                   (b) EVERY placement in the A56 4D witness file certs/<name>.param.witnesses.json,
                   expanded on A54's stencil: 9 centre offsets x 3 angle offsets per witness
                   (dx,dy in {0,+-0.003,+-0.006 diag}, dth in {0,+-0.004}).  The 4D witness carries
                   an s; only (cx, cy, theta) is used, because an LP row is just the demand
                   "mu(Q) >= 1 at this placement" and adding it at s0 is always legitimate --
                   it can only tighten the measure.
  3. solve_node at s0, sym_kind C1, prune=0 (rows never dropped, so tau is monotone), column
     generation on.  If tau >= budget the stratum cannot be killed this way; stop.
  4. A54 certify.py --scale 0 --scale_cap 1.06 --loop_cols: it picks the largest scale with
     total < budget and runs its own witness-feedback rounds against the exact fixed-s verifier.
  5. make_param (gap anchoring) + verify_param at depth 48 over [191/50, s0] + canary C2 with the
     UNMODIFIED A53 verify_case.py at both endpoints and the midpoint.

Nothing is written outside attempts/A56-sparametric/ (A53 and A54 are read-only sources; the
A54 modules are imported, and certify.py is invoked with --out inside A56).

Usage:  python resolve_margin.py --name k5_02 [--time_limit 1200] [--cert_time 420] [--depth 48]
"""
import argparse
import glob
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep as SW                                              # noqa: E402

A54C = os.path.join(SW.ATTEMPTS, "A54-stragglers", "code")
A53 = os.path.join(SW.ATTEMPTS, "A53-simple-strata")
sys.path.insert(0, A54C)
from caselp import solve_node                                   # noqa: E402
from run_skel import hyp_from_slots, S0F                        # noqa: E402

OUTC = os.path.join(SW.CERTS, "resolved")
OUTN = os.path.join(SW.RESULTS, "nodes")
STENCIL_XY = ((0, 0), (0.003, 0), (-0.003, 0), (0, 0.003), (0, -0.003),
              (0.006, 0.006), (-0.006, -0.006), (0.006, -0.006), (-0.006, 0.006))
STENCIL_TH = (0.0, 0.004, -0.004)


def build_warm(name):
    atoms, rows, seen_a, seen_r = [], [], set(), set()
    used = []
    src = os.path.join(A53, "results", "nodes", f"{name}.json")
    if os.path.exists(src):
        d = json.load(open(src))
        used.append(os.path.basename(src))
        for a in d.get("atoms_all", []):
            k = (round(a[0], 7), round(a[1], 7))
            if k not in seen_a:
                seen_a.add(k)
                atoms.append((a[0], a[1]))
        for r in d.get("rows_all", []):
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k)
                rows.append((r[0], r[1], r[2]))
    n_lp_rows = len(rows)
    n_wit = 0
    wfs = (glob.glob(os.path.join(SW.CERTS, f"{name}*.witnesses.json"))
           + glob.glob(os.path.join(SW.CERTS, f"{name}*.wit.json")))
    for wf in wfs:
        try:
            W = json.load(open(wf))["witnesses"]
        except Exception:
            continue
        used.append(os.path.basename(wf))
        for w in W:
            p = w.get("placement")
            if not p:
                continue
            n_wit += 1
            th = math.radians(p["theta_deg"])
            for dx, dy in STENCIL_XY:
                for dth in STENCIL_TH:
                    rows.append((p["cx_float"] + dx, p["cy_float"] + dy, th + dth))
    return dict(atoms=atoms, rows=rows), used, n_lp_rows, n_wit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--time_limit", type=float, default=1200)
    ap.add_argument("--max_iter", type=int, default=4000)
    ap.add_argument("--cert_time", type=float, default=420)
    ap.add_argument("--cert_rounds", type=int, default=4)
    ap.add_argument("--cert_depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.06)
    ap.add_argument("--depth", type=int, default=48, help="depth of the A56 4D verification")
    ap.add_argument("--param_timeout", type=int, default=900)
    ap.add_argument("--eps_geo", type=float, default=None,
                    help="row shrink margin: every covering atom must sit at least this far "
                         "INSIDE Q. This, not the weight scale, is the lever the 4D verifier "
                         "needs -- it buys positional slack against the atom's s-interval.")
    a = ap.parse_args(argv)
    if a.eps_geo is not None:
        import lpbox
        lpbox.EPS_GEO = a.eps_geo

    os.makedirs(OUTC, exist_ok=True)
    os.makedirs(OUTN, exist_ok=True)
    name = a.name
    log = os.path.join(SW.LOGS, f"resolve_{name}.log")
    lf = open(log, "a", buffering=1, encoding="utf-8")

    def L(*x):
        print(*x, file=lf, flush=True)
        print(*x, flush=True)

    rec = {"name": name, "eps_geo": a.eps_geo, "recipe": "A56 resolve_margin (steps 1-5 of the module docstring)"}
    slots = [tuple(p) for p in json.load(
        open(os.path.join(A53, "results", "name_to_slots.json")))[name]]
    k = len(slots)
    budget = 11 - k
    hyp = hyp_from_slots(slots)
    warm, used, n_lp_rows, n_wit = build_warm(name)
    L(f"=== {name}: k={k} budget={budget}; warm = {len(warm['atoms'])} atoms, "
      f"{len(warm['rows'])} rows ({n_lp_rows} from A53 + {n_wit} 4D witnesses x 27 stencil) "
      f"from {used}")
    rec.update(k=k, budget=budget, warm_atoms=len(warm["atoms"]), warm_rows=len(warm["rows"]),
               warm_rows_from_a53=n_lp_rows, n_4d_witnesses=n_wit, warm_sources=used)

    t0 = time.time()
    res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.time_limit,
                     max_iter=a.max_iter, out=None, log=L, prune=0, prune_cols=0,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=1200,
                     max_rows_add=2500, fine_slack=99.0, alternate=True,
                     checkpoint=os.path.join(OUTN, f"{name}_state.json"))
    res["skeleton_name"] = name
    res["skeleton_slots"] = [[x, y] for (x, y) in slots]
    res["k"] = k
    node_out = os.path.join(OUTN, f"{name}.json")
    json.dump(res, open(node_out, "w"))
    rec["lp_seconds"] = round(time.time() - t0, 1)
    rec.update(tau=res["tau"], converged=res["converged"], minmass=res["minmass"],
               maxcov=res["maxcov"], n_rows=res["n_rows"], n_orbits=res["n_orbits"])
    L(f"    LP: tau={res['tau']:.6f} budget={budget} conv={res['converged']} "
      f"({rec['lp_seconds']}s)")
    if res["tau"] >= budget:
        rec["verdict"] = "LP infeasible for a kill (tau >= budget)"
        json.dump(rec, open(os.path.join(SW.RESULTS, f"resolve_{name}.json"), "w"), indent=1)
        return 1

    cert_out = os.path.join(OUTC, f"{name}.json")
    cmd = [sys.executable, os.path.join(A54C, "certify.py"), node_out, "--s_rat", str(SW.S0),
           "--rounds", str(a.cert_rounds), "--jobs", "3", "--depth", str(a.cert_depth),
           "--time_limit", str(a.cert_time), "--out", cert_out, "--scale", "0",
           "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "96", "--loop_cols"]
    L("    " + " ".join(cmd))
    t1 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    L(p.stdout[-6000:])
    rec["certify_seconds"] = round(time.time() - t1, 1)
    rec["certify"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
    if p.returncode != 0:
        rec["verdict"] = "fixed-s re-certification failed; recipe did not produce a base cert"
        json.dump(rec, open(os.path.join(SW.RESULTS, f"resolve_{name}.json"), "w"), indent=1)
        return 1
    cj = json.load(open(cert_out))
    rec["new_cert"] = {"atoms": len(cj["atoms"]), "total": cj["total"],
                       "margin": budget - float(F(cj["total"]))}

    par = os.path.join(OUTC, f"{name}.param.json")
    rc, _ = SW.build_param(name, cert_out, par, "gap", log)
    if rc != 0:
        rec["verdict"] = "make_param failed on the re-solved certificate"
        json.dump(rec, open(os.path.join(SW.RESULTS, f"resolve_{name}.json"), "w"), indent=1)
        return 1
    rep = os.path.join(OUTC, f"{name}.param.report.json")
    t2 = time.time()
    rc, dt = SW.sh([sys.executable, SW.VERIFY_PARAM, par, "--slo", str(SW.S_LO),
                    "--shi", str(SW.S0), "--depth", str(a.depth), "--sscale", "8", "--jobs", "3",
                    "--split", "3", "--report", rep, "--max-witnesses", "20",
                    "--witness-file", os.path.join(OUTC, f"{name}.param.wit.json"), "--quiet"],
                   log, timeout=a.param_timeout)
    rec["param_seconds"] = round(dt, 1)
    rec["param_result"] = {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)
    if os.path.exists(rep):
        d = json.load(open(rep))
        rec["param_stats"] = {q: d.get("stats", {}).get(q) for q in
                              ("boxes", "s_splits", "s_cells", "max_depth", "max_s_depth")}
        rec["witness_s_range"] = d.get("witness_s_range")
    if rc == 0:
        rec["c2"] = SW.c2_crosscheck(name, par, SW.S_LO, type("A", (), {
            "depth0": "44", "heavy": 3, "timeout": 1800})(), log, tag=".resolved")
        rec["verdict"] = ("RECIPE CONVERTS" if all(x.get("result") == "PASS" for x in rec["c2"])
                          else "C2-DISCREPANCY")
    else:
        rec["verdict"] = "recipe did NOT convert (4D still open)"
    rec["total_seconds"] = round(time.time() - t0, 1)
    L("    " + json.dumps({q: rec[q] for q in ("verdict", "lp_seconds", "certify_seconds",
                                               "param_seconds", "total_seconds")}))
    json.dump(rec, open(os.path.join(SW.RESULTS, f"resolve_{name}.json"), "w"), indent=1)
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
