#!/usr/bin/env python3
"""
A39 P2b -- RESEAL THE s-hat GUARD FIELD (A33 gaps G5/G6).

The field A38's W1/W2 cuts are built on is
    attempts/A33-tight-variety/t1/certs/A33_measure_feasible_3.877084.json
exact total 44630467/3906250 = 11.4254, i.e. eta_cert = 0.4254, while the underlying float LP
field has tau = 11.2448 (eta_float = 0.2448).  The whole 0.18 gap is the UNIFORM SEALING SCALE
127/125 = 1.016 that the exact verifier demanded: the t1 row oracle's grid missed closed unit
squares carrying ~0.985 of mass, and a uniform 1.6% inflation was the sledgehammer that fixed them.

This driver runs A33's t2/refine_384.py pattern at s0: verifier-in-the-loop row generation

   verify at the TARGET scale  ->  harvest the deficit witnesses  ->  add them (+ D4 images)
   as LP rows  ->  re-solve min sum(m_i w_i) s.t. mu(Q_row) >= 1  ->  new field  ->  repeat

so that the sealing scale, not the mass, carries the shrinking margin.  Every field is turned into
an exact rational certificate (make_cert33) and every claim is decided by the exact verifier
certs/verify_measure.py -- the sole arbiter.  Checkpointed per iteration.

W1's threshold is thr_cert = 1 + eta_cert, so eta is a direct multiplier on the excluded volume.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A33 = os.path.join(REPO, "attempts", "A33-tight-variety")
sys.path.insert(0, os.path.join(A33, "t1"))
sys.path.insert(0, os.path.join(A33, "t2"))

VERIFY = os.path.join(REPO, "certs", "verify_measure.py")
MAKECERT = os.path.join(A33, "t1", "make_cert33.py")
S0_STR = "969271/250000"
OUTDIR = os.path.abspath(os.path.join(HERE, "..", "results", "p2b"))
LOGDIR = os.path.abspath(os.path.join(HERE, "..", "logs"))


def _lazy():
    import highspy                                                    # noqa: F401
    from lp_measure2 import d4_placement_images                       # noqa: F401
    from perturb_field import build                                   # noqa: F401
    return highspy, d4_placement_images, build


def verify(cert, scale="1", depth=50, jobs=2, maxw=800, wfile=None, report=None, timeout=7200):
    cmd = [sys.executable, VERIFY, cert, "--n", "12", "--depth", str(depth), "--split", "3",
           "--jobs", str(jobs), "--scale-weights", scale, "--max-witnesses", str(maxw),
           "--max-witnesses-per-box", "6", "--quiet"]
    if wfile:
        cmd += ["--witness-file", wfile]
    if report:
        cmd += ["--report", report]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        rc, out = 124, "timeout"
    return rc, out, time.time() - t0


def harvest(wfile):
    if not os.path.exists(wfile):
        return []
    try:
        W = json.load(open(wfile))["witnesses"]
    except Exception:
        return []
    out = []
    for w in W:
        p = w.get("placement")
        if not p:
            continue
        out.append((float(p["cx_float"]), float(p["cy_float"]), 2 * math.atan(float(p["t_float"]))))
    return out


def solve_field(st, rows, tag, t0, threads=2, solver="simplex", w0=None):
    """min sum_i m_i w_i  s.t.  mu(Q_r) >= 1 for all rows r,  w >= 0  (fixed atom orbits).

    solver='ipm' (default): interior point, crossover OFF.  The LP has few columns (3349 orbits)
    and tens of thousands of rows, which is the regime where dual simplex is slow and IPX is fast;
    and the interior solution has SLACK on every row, which is exactly what a guard field wants
    (an optimal vertex sits tight on thousands of rows, so any hole the row oracle missed near one
    of them is a sealing failure).  The price is a total slightly above tau*; the exact verifier,
    not the LP, decides whether the field seals."""
    highspy, _, build = _lazy()
    st2 = dict(st)
    st2["rows"] = rows
    s, reps, P, P_orb, m_orb, rws, idxs, vals, starts = build(st2)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", threads)
    if solver == "ipm":
        h.setOptionValue("solver", "ipm")
        h.setOptionValue("run_crossover", "off")
    h.addVars(len(reps), np.zeros(len(reps)), np.full(len(reps), highspy.kHighsInf))
    h.changeColsCost(len(reps), np.arange(len(reps), dtype=np.int32), m_orb)
    AS = np.array(starts[:-1], dtype=np.int32)
    AI = np.concatenate(idxs).astype(np.int32)
    AV = np.concatenate(vals)
    h.addRows(len(rws), np.ones(len(rws)), np.full(len(rws), highspy.kHighsInf),
              len(AI), AS, AI, AV)
    if w0 is not None and len(w0) == len(reps):        # crash from A33's own weights
        try:
            sol = highspy.HighsSolution()
            sol.col_value = list(map(float, w0))
            h.setSolution(sol)
        except Exception as e:
            print("   [setSolution failed: %r]" % (e,), flush=True)
    h.run()
    w = np.maximum(np.array(h.getSolution().col_value), 0.0)
    tau = float((w * m_orb).sum())
    atoms = [[float(P[i, 0]), float(P[i, 1]), float(w[P_orb[i]])]
             for i in range(len(P)) if w[P_orb[i]] > 1e-12]
    orbits = [[reps[i][0], reps[i][1], float(w[i]), int(m_orb[i])]
              for i in range(len(reps)) if w[i] > 1e-12]
    out_w = list(map(float, w))
    fld = dict(_w=out_w, s=s, n_atoms=len(atoms), atoms=atoms, orbits=orbits, tau=tau, tau_solver=tau,
               eps_geo=st.get("eps_geo"), tag=tag, phase="A39-P2b verifier-in-the-loop",
               converged=True, n_rows=len(rws), n_orbits=len(reps), wall_time=time.time() - t0)
    return fld, tau


def make_cert(field_path, out, scale=1.0, jitter=3):
    subprocess.run([sys.executable, MAKECERT, "--field", field_path, "--s", S0_STR,
                    "--scale", str(scale), "--jitter", str(jitter), "--out", out],
                   check=True, capture_output=True, text=True)
    c = json.load(open(out))
    return float(F(c["total"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=os.path.join(A33, "t1", "checkpoints",
                                                    "r7_s3.877084_state.json"))
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--target_scale", default="251/250", help="scale the loop harvests against")
    ap.add_argument("--depth", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--maxw", type=int, default=800)
    ap.add_argument("--jitter", type=int, default=3)
    ap.add_argument("--tag", default="a39")
    ap.add_argument("--deadline_h", type=float, default=6.0)
    ap.add_argument("--solver", default="simplex", choices=["ipm", "simplex"])
    a = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(os.path.join(OUTDIR, "certs"), exist_ok=True)
    os.makedirs(os.path.join(OUTDIR, "witn"), exist_ok=True)
    t0 = time.time()
    _, d4_placement_images, _ = _lazy()
    st = json.load(open(a.state))
    rows = [tuple(r) for r in st["rows"]]
    print("[init] s=%s rows=%d orbits=%d" % (st["s"], len(rows), len(st["orbits"])), flush=True)

    ledger = dict(when=time.strftime("%FT%T"), state=a.state, target_scale=a.target_scale,
                  depth=a.depth, iters=[])
    ledger_path = os.path.join(OUTDIR, "reseal_ledger.json")

    # iteration 0 field = the state's own LP re-solve (audit that we reproduce A33's tau)
    fld, tau = solve_field(st, rows, a.tag + "_it0", t0, solver=a.solver, w0=st.get("w"))
    w_prev = fld.pop("_w", None)
    fpath = os.path.join(OUTDIR, "field_%s_it0.json" % a.tag)
    json.dump(fld, open(fpath, "w"))
    print("[it0] tau=%.9f (A33 r7: 11.244816546)  %.0fs" % (tau, time.time() - t0), flush=True)

    best = None
    for it in range(a.iters):
        cert = os.path.join(OUTDIR, "certs", "cert_%s_it%d.json" % (a.tag, it))
        tot1 = make_cert(fpath, cert, scale=1.0, jitter=a.jitter)
        wfile = os.path.join(OUTDIR, "witn", "w_%s_it%d.json" % (a.tag, it))
        rep = os.path.join(OUTDIR, "certs", "cert_%s_it%d.report.json" % (a.tag, it))
        rc, txt, dt = verify(cert, scale=a.target_scale, depth=a.depth, jobs=a.jobs,
                             maxw=a.maxw, wfile=wfile, report=rep)
        pls = harvest(wfile)
        eta_at_target = tot1 * float(F(a.target_scale)) - 11
        rec = dict(it=it, tau=tau, cert_total_scale1=tot1, target_scale=a.target_scale,
                   eta_at_target=eta_at_target, verify_rc=rc, verify_s=dt, n_witness=len(pls),
                   n_rows=len(rows), elapsed=time.time() - t0)
        print("[it%d] tau=%.6f total@1=%.6f  verify@%s -> %s (%.0fs)  witnesses=%d"
              % (it, tau, tot1, a.target_scale, "PASS" if rc == 0 else "FAIL", dt, len(pls)),
              flush=True)
        ledger["iters"].append(rec)
        json.dump(ledger, open(ledger_path, "w"), indent=1)
        if rc == 0:
            best = dict(field=fpath, cert=cert, scale=a.target_scale, total=tot1,
                        eta=eta_at_target, it=it)
            ledger["sealed_at_target"] = best
            json.dump(ledger, open(ledger_path, "w"), indent=1)
            print("[it%d] TARGET SCALE PASSES -> eta = %.6f" % (it, eta_at_target), flush=True)
            break
        if not pls:
            print("[it%d] verifier FAILED with no usable witnesses; stop" % it, flush=True)
            break
        seen = set((round(c[0], 6), round(c[1], 6), round(c[2], 9)) for c in rows)
        nadd = 0
        for (cx, cy, th) in pls:
            for (qx, qy, qt) in d4_placement_images(cx, cy, th, st["s"]):
                k = (round(qx, 6), round(qy, 6), round(qt, 9))
                if k in seen:
                    continue
                seen.add(k)
                rows.append((qx, qy, qt))
                nadd += 1
        rec["rows_added"] = nadd
        print("[it%d] +%d rows -> %d  (%.0fs)" % (it, nadd, len(rows), time.time() - t0), flush=True)
        if nadd == 0:
            print("[it%d] no new rows; the blocker is inside the existing row set; stop" % it,
                  flush=True)
            break
        fld, tau = solve_field(st, rows, "%s_it%d" % (a.tag, it + 1), t0, solver=a.solver, w0=w_prev)
        w_prev = fld.pop("_w", None)
        fpath = os.path.join(OUTDIR, "field_%s_it%d.json" % (a.tag, it + 1))
        json.dump(fld, open(fpath, "w"))
        json.dump(dict(s=st["s"], n=st["n"], eps_geo=st.get("eps_geo"), rows=rows,
                       orbits=st["orbits"], tau=tau, it=it + 1),
                  open(os.path.join(OUTDIR, "state_%s.json" % a.tag), "w"))
        ledger["iters"][-1]["tau_next"] = tau
        json.dump(ledger, open(ledger_path, "w"), indent=1)
        if time.time() - t0 > a.deadline_h * 3600:
            print("deadline", flush=True)
            break
    json.dump(ledger, open(ledger_path, "w"), indent=1)
    print("done in %.0fs; last field %s (tau %.6f)" % (time.time() - t0, fpath, tau), flush=True)


if __name__ == "__main__":
    main()
