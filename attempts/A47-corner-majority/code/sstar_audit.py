#!/usr/bin/env python3
"""A47 leg (a): final audit -- re-verify EVERY s* certificate from scratch (fresh process, obstacle
rebuilt and its containment proof re-run) and spot-check each with the independent random-placement
test.  Writes work/sstar/audit.json."""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import verify_measure_obs as V   # noqa: E402
import sstar_selfcheck as SC     # noqa: E402


def main():
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    nspot = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
    out = []
    ok = True
    for p in sorted(glob.glob(os.path.join(ROOT, "work", "sstar", "*.cert.json"))):
        t0 = time.time()
        passed, stats, wits, total, n = V.run_verify(p, depth=36, split=2, jobs=jobs,
                                                     max_witnesses=4, per_box_cap=2)
        rc = SC.main([p, "--n", str(nspot)])
        row = {"cert": os.path.basename(p), "verify": "PASS" if passed else "FAIL",
               "total": str(total), "total_float": float(total), "n": n,
               "boxes": stats.get("boxes"), "exempt": stats.get("exempt"),
               "spotcheck": "OK" if rc == 0 else "REFUTED", "time_s": round(time.time() - t0, 1)}
        ok &= passed and rc == 0
        out.append(row)
        print(f"{row['cert']:38s} {row['verify']:4s} total {row['total_float']:.4f} "
              f"boxes {row['boxes']} spot {row['spotcheck']} {row['time_s']}s", flush=True)
    res = {"n_certs": len(out), "all_pass": bool(ok),
           "max_total": max((r["total_float"] for r in out), default=None), "rows": out}
    with open(os.path.join(ROOT, "work", "sstar", "audit.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"AUDIT: {len(out)} certificates, all_pass = {ok}, max total = {res['max_total']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
