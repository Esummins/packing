#!/usr/bin/env python3
"""Close the gap between T1's s=3.84 LP field and exact feasibility.

T1's field_3.84.json satisfies the LP rows it was generated against, but the exact verifier finds
CLOSED unit squares carrying only ~0.985 of mass -- the row oracle's grid missed them.  That is why
sealing needed a 3% uniform weight scale (eta_cert = 0.3776) instead of ~1%.

This driver runs verifier-in-the-loop row generation: verify -> harvest witness placements ->
add them (and their D4 images) as LP rows -> re-solve with the all-ones objective -> new field.
"""
import os
import sys
import json
import math
import time
import argparse
import subprocess
import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "t1"))
sys.path.insert(0, HERE)
from lp_measure2 import d4_point_images, d4_placement_images, inside_mask, RowOracle  # noqa: E402
from perturb_field import build                                          # noqa: E402
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VERIFY = os.path.join(_REPO, "certs", "verify_measure.py")
MAKECERT = os.path.join(HERE, "..", "t1", "make_cert33.py")


def harvest(cert, wfile, scale="1", depth=50, maxw=800):
    cmd = [sys.executable, VERIFY, cert, "--n", "12", "--depth", str(depth), "--split", "3",
           "--jobs", "2", "--scale-weights", scale, "--max-witnesses", str(maxw),
           "--max-witnesses-per-box", "6", "--quiet", "--witness-file", wfile]
    subprocess.run(cmd, cwd=HERE, check=False, capture_output=True)
    if not os.path.exists(wfile):
        return []
    W = json.load(open(wfile))["witnesses"]
    out = []
    for w in W:
        p = w.get("placement")
        if not p:
            continue
        t = float(p["t_float"])
        out.append((float(p["cx_float"]), float(p["cy_float"]), 2 * math.atan(t)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="../t1/checkpoints/r3_s3.84_state.json")
    ap.add_argument("--cert0", default="certs/cert_3.84_base.json")
    ap.add_argument("--iters", type=int, default=2)
    ap.add_argument("--outfield", default="results/field_3.84_v2.json")
    a = ap.parse_args()
    t0 = time.time()
    st = json.load(open(os.path.join(HERE, a.state)))
    rows = list(st["rows"])
    cert = os.path.join(HERE, a.cert0)
    added_total = 0
    # preload witness placements from earlier runs so their rows are not lost between invocations
    import glob as _glob
    seen0 = set((round(c[0], 6), round(c[1], 6), round(c[2], 9)) for c in rows)
    for wf0 in sorted(_glob.glob(os.path.join(HERE, "logs", "witn_384_it*.json"))):
        try:
            W0 = json.load(open(wf0))["witnesses"]
        except Exception:
            continue
        for w0 in W0:
            p = w0.get("placement")
            if not p:
                continue
            t = float(p["t_float"]); cx = float(p["cx_float"]); cy = float(p["cy_float"])
            for (qx, qy, qt) in d4_placement_images(cx, cy, 2 * math.atan(t), st["s"]):
                k = (round(qx, 6), round(qy, 6), round(qt, 9))
                if k not in seen0:
                    seen0.add(k)
                    rows.append((qx, qy, qt))
    print(f"[preload] rows after witness preload: {len(rows)}", flush=True)
    for it in range(a.iters):
        wf = os.path.join(HERE, f"logs/witn_384_it{it}.json")
        pls = harvest(cert, wf)
        print(f"[it{it}] verifier witnesses: {len(pls)}  ({time.time()-t0:.0f}s)", flush=True)
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
        added_total += nadd
        print(f"[it{it}] added {nadd} rows -> {len(rows)}  ({time.time()-t0:.0f}s)", flush=True)
        if nadd == 0:
            break
        st2 = dict(st); st2["rows"] = rows
        s, reps, P, P_orb, m_orb, rws, idxs, vals, starts = build(st2)
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("threads", 2)
        h.addVars(len(reps), np.zeros(len(reps)), np.full(len(reps), highspy.kHighsInf))
        h.changeColsCost(len(reps), np.arange(len(reps), dtype=np.int32), m_orb)
        AS = np.array(starts[:-1], dtype=np.int32)
        AI = np.concatenate(idxs).astype(np.int32)
        AV = np.concatenate(vals)
        h.addRows(len(rws), np.ones(len(rws)), np.full(len(rws), highspy.kHighsInf),
                  len(AI), AS, AI, AV)
        h.run()
        w = np.maximum(np.array(h.getSolution().col_value), 0.0)
        tau = float((w * m_orb).sum())
        print(f"[it{it}] re-solved tau = {tau:.9f}  ({time.time()-t0:.0f}s)", flush=True)
        atoms = [[float(P[i, 0]), float(P[i, 1]), float(w[P_orb[i]])]
                 for i in range(len(P)) if w[P_orb[i]] > 1e-12]
        orbits = [[reps[i][0], reps[i][1], float(w[i]), int(m_orb[i])]
                  for i in range(len(reps)) if w[i] > 1e-12]
        fld = dict(s=s, n_atoms=len(atoms), atoms=atoms, orbits=orbits, tau=tau, tau_solver=tau,
                   eps_geo=st.get("eps_geo"), tag=f"v2it{it}", phase="verifier-in-the-loop",
                   converged=True, n_rows=len(rws), n_orbits=len(reps),
                   wall_time=time.time() - t0,
                   provenance=dict(method="verifier-witness row generation on top of t1 state",
                                   state=a.state, rows_added=added_total))
        json.dump(fld, open(os.path.join(HERE, a.outfield), "w"))
        cert = os.path.join(HERE, f"certs/cert_3.84_v2it{it}.json")
        subprocess.run([sys.executable, MAKECERT, "--field", os.path.join(HERE, a.outfield),
                        "--s", "96/25", "--scale", "1.0", "--jitter", "3", "--out", cert],
                       cwd=HERE, check=True)
    print(f"done; final cert {cert}  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
