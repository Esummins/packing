#!/usr/bin/env python3
"""Generate GENUINELY DIVERSE near-optimal guard fields by re-solving the SAME cutting-plane LP
(rows + atom orbits taken from a t1 checkpoint) with a PERTURBED objective.

Lemma A33.1 needs only FEASIBILITY of the field, so any vertex of {A w >= 1, w >= 0} with total
mass <= 11 + eta_budget is admissible.  The all-ones objective has (numerically) a unique optimal
coverage function -- t1's r4/r6/r7 are alternative optimal BASES of the same measure, which is why
they are near-identical.  Randomising the per-orbit cost to m_i * (1 + delta_i) moves to a
different vertex whose total is only slightly above tau*, giving a field with a genuinely
different tight set.

  python perturb_field.py --state ../t1/checkpoints/r6_s3.877084_state.json --amp 0.06 --seed 3 \
      --tag p1 --out ../t2/results/field_3.877084_p1.json
"""
import os
import sys
import json
import time
import math
import argparse
import numpy as np
import highspy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "t1"))
import lp_measure2 as L                                                   # noqa: E402
from lp_measure2 import d4_point_images, inside_mask, RowOracle           # noqa: E402


def build(state, chunk=400):
    s = float(state["s"])
    reps = state["orbits"]
    P, P_orb = [], []
    for oi, (x, y) in enumerate(reps):
        pts = []
        for p in d4_point_images(x, y, s):
            if all(abs(p[0] - q[0]) > 1e-12 or abs(p[1] - q[1]) > 1e-12 for q in pts):
                pts.append(p)
        for p in pts:
            P.append(p); P_orb.append(oi)
    P = np.array(P); P_orb = np.array(P_orb)
    m_orb = np.bincount(P_orb, minlength=len(reps)).astype(float)
    rows = state["rows"]
    idxs, vals, starts = [], [], [0]
    for r0 in range(0, len(rows), chunk):
        for (cx, cy, th) in rows[r0:r0 + chunk]:
            mk = inside_mask(P, cx, cy, th)
            cnt = np.bincount(P_orb[mk], minlength=len(reps))
            nz = np.nonzero(cnt)[0]
            idxs.append(nz.astype(np.int32))
            vals.append(cnt[nz].astype(float))
            starts.append(starts[-1] + len(nz))
    return s, reps, P, P_orb, m_orb, rows, idxs, vals, starts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--amp", type=float, default=0.06)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--tag", default="p1")
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=float, default=11.30)
    a = ap.parse_args()
    t0 = time.time()
    st = json.load(open(a.state))
    s, reps, P, P_orb, m_orb, rows, idxs, vals, starts = build(st)
    print(f"state: {len(reps)} orbits, {len(P)} atoms, {len(rows)} rows  ({time.time()-t0:.0f}s)",
          flush=True)
    rng = np.random.default_rng(a.seed)
    delta = rng.uniform(-a.amp, a.amp, size=len(reps))
    cost = m_orb * (1.0 + delta)

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.addVars(len(reps), np.zeros(len(reps)), np.full(len(reps), highspy.kHighsInf))
    h.changeColsCost(len(reps), np.arange(len(reps), dtype=np.int32), cost)
    AS = np.array(starts[:-1], dtype=np.int32)
    AI = np.concatenate(idxs).astype(np.int32)
    AV = np.concatenate(vals)
    h.addRows(len(rows), np.ones(len(rows)), np.full(len(rows), highspy.kHighsInf),
              len(AI), AS, AI, AV)
    h.run()
    sol = h.getSolution()
    w = np.array(sol.col_value)
    w = np.maximum(w, 0.0)
    total = float((w * m_orb).sum())
    print(f"perturbed solve: total mass {total:.9f} (unperturbed tau {st['tau']:.9f}) "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- a-posteriori: row activity on the LP rows, then the closed-square oracle residual
    act = []
    for r in range(len(rows)):
        b, e = starts[r], starts[r + 1]
        act.append(float(w[AI[b:e]] @ AV[b:e]))
    act = np.array(act)
    print(f"min LP-row activity {act.min():.12f}", flush=True)

    atoms = [[float(P[i, 0]), float(P[i, 1]), float(w[P_orb[i]])] for i in range(len(P))
             if w[P_orb[i]] > 1e-12]
    orbits = [[reps[i][0], reps[i][1], float(w[i]), int(m_orb[i])] for i in range(len(reps))
              if w[i] > 1e-12]
    ro = RowOracle(s, P, w[P_orb], n_theta=181, cstep=0.01, delta=0.001)
    found = ro.search(thresh=1.0, max_refine=60, max_return=200)
    worst = min([f[3] for f in found], default=1.0)
    print(f"oracle scan: {len(found)} shrunk-square rows below 1, worst mass {worst:.9f}", flush=True)
    out = dict(s=s, n_atoms=len(atoms), atoms=atoms, orbits=orbits, tau=total,
               tau_solver=total, eps_geo=st.get("eps_geo"), tag=a.tag, phase="perturbed",
               converged=True, n_rows=len(rows), n_orbits=len(reps),
               wall_time=time.time() - t0,
               provenance=dict(method="perturbed-objective re-solve of the t1 cutting-plane LP",
                               state=a.state, amp=a.amp, seed=a.seed,
                               min_lp_row_activity=float(act.min()),
                               oracle_n_violating=len(found), oracle_worst_mass=float(worst),
                               unperturbed_tau=st["tau"]),
               oracle_residuals=dict(row_violation=float(max(0.0, 1.0 - worst))))
    json.dump(out, open(a.out, "w"))
    print(f"wrote {a.out}: atoms {len(atoms)} orbits {len(orbits)} total {total:.9f} "
          f"eta_float {total-11:.9f}")
    if total > a.budget:
        print(f"WARNING: total {total:.6f} exceeds budget {a.budget}")


if __name__ == "__main__":
    main()
