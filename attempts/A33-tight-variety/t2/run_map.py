#!/usr/bin/env python3
"""Driver for the A33/T2 exclusion maps.

  python run_map.py --source cert --path ../t1/certs/A33_measure_feasible_3.877084.json \
      --eta 0.425399552 --mode exact --out results/map_sealed_certified.json
  python run_map.py --source field --path ../t1/results/field_3.877084_r5.json \
      --eta 0.2429 --mode float --out results/map_r5_float.json
"""
import os
import sys
import json
import time
import argparse
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper import Mapper, load_cert_exact, field_to_exact                # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["cert", "field"], required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--eta", required=True, help="rational or decimal string")
    ap.add_argument("--mode", choices=["exact", "float"], default="exact")
    ap.add_argument("--res-t", type=float, default=0.005)
    ap.add_argument("--res-c", type=float, default=0.01)
    ap.add_argument("--nt", type=int, default=8)
    ap.add_argument("--nc", type=int, default=12)
    ap.add_argument("--cbits", type=int, default=8)
    ap.add_argument("--tbits", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    if a.source == "cert":
        d, s, atoms, weights = load_cert_exact(a.path)
    else:
        d, s, atoms, weights = field_to_exact(a.path)
    tot = sum(weights, F(0))
    if a.eta == "auto":                      # eta = (exact total of THIS field) - 11
        a.eta = str(tot - 11)
        print(f"[map] eta auto = {float(F(a.eta)):.12f}")
    thr = 1 + F(a.eta)
    m = Mapper(s, atoms, weights, thr, res_t=a.res_t, res_c=a.res_c, mode=a.mode,
               cbits=a.cbits, tbits=a.tbits)
    print(f"[map] {a.label or a.path}  s={s} atoms={len(atoms)} total={float(sum(weights,F(0))):.9f} "
          f"thr={float(thr):.9f} mode={a.mode} res=({a.res_t},{a.res_c})", flush=True)
    t0 = time.time()
    summ = m.run(m.root_boxes(nt=a.nt, nc=a.nc))
    summ["label"] = a.label
    summ["source_path"] = a.path
    summ["eta"] = str(F(a.eta))
    summ["field_total"] = str(tot)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    m.save(a.out, extra={"label": a.label, "source_path": a.path, "eta": str(F(a.eta)),
                         "field_total": str(tot)})
    print(json.dumps(summ, indent=1))
    print(f"[map] wrote {a.out} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
