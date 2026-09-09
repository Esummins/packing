"""A161 -- A141's OWN checker, extended by exactly one reason code.

`check141.py` is imported READ-ONLY and does all the work (C1-C6: the tightened boxes, the cover as
a complete prefix code under the split rule, every leaf's discharge, the pairwise-overlap test for
`lane_ub = 1`, the M covers with `skip = j`, and `lane_ub + M <= 1` for a KILL).  The ONE extension:
a `misses_cell` leaf emitted by A161's `run141x.py` may be discharged along one of the SQUARE's own
edge normals, which A141's `leaf_misses` (cell normals + bounding half-width only) cannot verify.
`check141.leaf_misses` is therefore wrapped so that it accepts a leaf if EITHER A141's own test
holds OR the full separating-axis test does -- the latter taken from `checkcl.misses_cell`, A161's
CHECKER-side re-implementation (independent of the emitter's `chordlane.box_misses_cell_exact`).

Both tests are sound sufficient conditions for "no pose of the box meets int(cell)", so the wrapped
checker is sound; it is strictly more permissive than A141's, which is the point.

    python check141x.py --dir ../certs141x
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A141-polycore-lane", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import check141 as C  # noqa: E402  READ-ONLY (A141's frozen checker)
import checkcl as X   # noqa: E402  A161's checker-side exact SAT

_ORIG = C.leaf_misses
STATS = {"a141": 0, "exact": 0, "fail": 0}


def leaf_misses_ext(b, cell, eps=1e-12):
    if _ORIG(b, cell, eps):
        STATS["a141"] += 1
        return True
    ok, _nm = X.misses_cell(b, cell)
    STATS["exact" if ok else "fail"] += 1
    return ok


C.leaf_misses = leaf_misses_ext


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="*")
    ap.add_argument("--dir", default=os.path.join(BASE, "certs141x"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "check141x.json"))
    a = ap.parse_args()
    files = list(a.certs) + sorted(glob.glob(os.path.join(a.dir, "*.json")))
    res, nfail = [], 0
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        errs = C.check_lane_cert(d)
        ok = not errs
        nfail += (not ok)
        res.append(dict(cert=os.path.relpath(f, ROOT), ok=ok, errors=errs,
                        lane_ub=d.get("lane_ub"), M=d.get("M"), verdict=d.get("verdict")))
        print("%-4s %-52s LANE=%s M=%s" % ("PASS" if ok else "FAIL", os.path.basename(f),
                                           d.get("lane_ub"), d.get("M")), flush=True)
        for e in errs[:6]:
            print("      ERR %s" % e, flush=True)
    print("\n%d certificates, %d PASS, %d FAIL" % (len(files), len(files) - nfail, nfail))
    print("misses_cell leaves: %d by A141's own test, %d by the exact SAT extension, %d failed"
          % (STATS["a141"], STATS["exact"], STATS["fail"]))
    json.dump(dict(n=len(files), n_pass=len(files) - nfail, n_fail=nfail, leaf_stats=STATS,
                   results=res), open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
