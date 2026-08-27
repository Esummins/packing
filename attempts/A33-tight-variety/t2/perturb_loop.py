#!/usr/bin/env python3
"""Perturbed-objective field WITH row generation, so the result is (numerically) feasible.

t1's r4/r6/r7 are alternative optimal BASES of the same LP optimum, so their measures -- and
hence their tight sets -- are nearly identical.  Genuine diversity needs a different VERTEX:
randomise the per-orbit cost m_i -> m_i (1 + delta_i).  A single re-solve on the old row set is
NOT feasible (the rows were generated for the unperturbed optimum), so this driver alternates

    solve (perturbed objective)  ->  row oracle scan  ->  add violated rows (D4 images)  ->  solve

until the oracle finds no eps-shrunk unit square of mass < 1 (or the round budget runs out).
"""
import os
import sys
import json
import time
import math
import argparse
import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "t1"))
from lp_measure2 import d4_point_images, d4_placement_images, inside_mask, RowOracle  # noqa: E402


def row_cols(P, P_orb, n_orb, cx, cy, th):
    mk = inside_mask(P, cx, cy, th)
    cnt = np.bincount(P_orb[mk], minlength=n_orb)
    nz = np.nonzero(cnt)[0]
    return nz.astype(np.int32), cnt[nz].astype(float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--amp", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--tag", default="p1")
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--n_theta", type=int, default=181)
    ap.add_argument("--cstep", type=float, default=0.01)
    ap.add_argument("--time_limit", type=float, default=1500)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    st = json.load(open(a.state))
    s = float(st["s"])
    reps = st["orbits"]
    P, P_orb = [], []
    for oi, (x, y) in enumerate(reps):
        pts = []
        for p in d4_point_images(x, y, s):
            if all(abs(p[0] - q[0]) > 1e-12 or abs(p[1] - q[1]) > 1e-12 for q in pts):
                pts.append(p)
        for p in pts:
            P.append(p); P_orb.append(oi)
    P = np.array(P); P_orb = np.array(P_orb)
    n_orb = len(reps)
    m_orb = np.bincount(P_orb, minlength=n_orb).astype(float)
    rng = np.random.default_rng(a.seed)
    cost = m_orb * (1.0 + rng.uniform(-a.amp, a.amp, size=n_orb))

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 2)
    h.addVars(n_orb, np.zeros(n_orb), np.full(n_orb, highspy.kHighsInf))
    h.changeColsCost(n_orb, np.arange(n_orb, dtype=np.int32), cost)
    rows = list(st["rows"])
    seen = set((round(c[0], 6), round(c[1], 6), round(c[2], 9)) for c in rows)
    print(f"state: {n_orb} orbits, {len(P)} atoms, {len(rows)} rows ({time.time()-t0:.0f}s)", flush=True)
    AS, AI, AV = [], [], []
    off = 0
    for (cx, cy, th) in rows:
        i, v = row_cols(P, P_orb, n_orb, cx, cy, th)
        AS.append(off); AI.append(i); AV.append(v); off += len(i)
    h.addRows(len(rows), np.ones(len(rows)), np.full(len(rows), highspy.kHighsInf),
              off, np.array(AS, np.int32), np.concatenate(AI), np.concatenate(AV))
    print(f"matrix built ({time.time()-t0:.0f}s)", flush=True)

    worst = None
    for rd in range(a.rounds):
        h.run()
        w = np.maximum(np.array(h.getSolution().col_value), 0.0)
        tau = float((w * m_orb).sum())
        ro = RowOracle(s, P, w[P_orb], n_theta=a.n_theta, cstep=a.cstep, delta=0.001)
        found = ro.search(thresh=1.0, max_refine=120, max_return=600)
        worst = min([f[3] for f in found], default=1.0)
        print(f"[rd{rd}] tau={tau:.9f} violated={len(found)} worst={worst:.9f} "
              f"rows={len(rows)} ({time.time()-t0:.0f}s)", flush=True)
        if not found or time.time() - t0 > a.time_limit:
            break
        nadd = 0
        AS, AI, AV = [], [], []
        off = 0
        for (cx, cy, th, m) in found:
            for (qx, qy, qt) in d4_placement_images(cx, cy, th, s):
                k = (round(qx, 6), round(qy, 6), round(qt, 9))
                if k in seen:
                    continue
                seen.add(k)
                i, v = row_cols(P, P_orb, n_orb, qx, qy, qt)
                if len(i) == 0:
                    continue
                rows.append((qx, qy, qt))
                AS.append(off); AI.append(i); AV.append(v); off += len(i)
                nadd += 1
        if nadd == 0:
            break
        h.addRows(nadd, np.ones(nadd), np.full(nadd, highspy.kHighsInf),
                  off, np.array(AS, np.int32), np.concatenate(AI), np.concatenate(AV))

    atoms = [[float(P[i, 0]), float(P[i, 1]), float(w[P_orb[i]])]
             for i in range(len(P)) if w[P_orb[i]] > 1e-12]
    orbits = [[reps[i][0], reps[i][1], float(w[i]), int(m_orb[i])]
              for i in range(n_orb) if w[i] > 1e-12]
    out = dict(s=s, n_atoms=len(atoms), atoms=atoms, orbits=orbits, tau=tau, tau_solver=tau,
               eps_geo=st.get("eps_geo"), tag=a.tag, phase="perturbed+rowgen",
               converged=(worst >= 1.0), n_rows=len(rows), n_orbits=n_orb,
               wall_time=time.time() - t0,
               oracle_residuals=dict(row_violation=float(max(0.0, 1.0 - worst)),
                                     worst_shrunk_mass=float(worst)),
               provenance=dict(method="perturbed-objective LP + row generation (A33/T2)",
                               state=a.state, amp=a.amp, seed=a.seed,
                               unperturbed_tau=st["tau"]))
    json.dump(out, open(a.out, "w"))
    print(f"wrote {a.out}: atoms {len(atoms)} orbits {len(orbits)} tau {tau:.9f} "
          f"eta_float {tau-11:.9f} worst_shrunk {worst:.9f}")


if __name__ == "__main__":
    main()
