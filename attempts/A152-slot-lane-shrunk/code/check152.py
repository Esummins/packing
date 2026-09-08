"""A152 -- the checker for `polycore_slot_lane_shrunk_v1`.

A152's certificate is A141's `polycore_lane_v1` object with the cell rectangle TRANSLATED by an
admissible `t`, so the whole of A141's `check141.py` (C1-C6: tightened boxes, the cover being a
complete prefix code, every leaf discharge re-decided -- the witness points exactly in Q, via
A132's `vertex_ok` -- the pairwise always-overlap test, the M exclusion covers and
`LANE + M <= 1`) is imported READ-ONLY and run first.

On top of it A152 checks the four facts that make the TRANSLATED snap legitimate:

  C7  the cell rectangle is the unit cell `[i, i+1] x [j, j+1]` translated by the stored `t`,
      and `|t|_inf <= snap_h = snap_delta / sqrt(2)`                              -- (T0)
  C8  the translated cell lies in the container `[0, s]^2` of the corner frame     -- (T1)
  C9  the translated cell is interior-disjoint from every position any PIN of the class may
      occupy: pin centre box (as stored, already fattened by the node's pin slack) grown by 1/2
      on every side                                                               -- (T2)
  C10 the pin obstacle boxes are at least as wide as the node's own pin slack (a NARROWER pin box
      would mean a bigger K' core than the slack family licenses), and the certificate declares
      itself CONDITIONAL with a `prerequisite` naming the missing slack-form extension kill.

C10's second half is the point of the checker: a `polycore_slot_lane_shrunk_v1` certificate that
claims an unconditional kill is REJECTED, because the extension classes are certified dead only
with exact pins (notes/prereq.md).

    python check152.py --dir ../certs --out ../results/check152.json
"""
import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "code")
if A141 not in sys.path:
    sys.path.insert(0, A141)

import check141 as C141                     # noqa: E402  READ-ONLY

SQ2 = math.sqrt(2.0)
EPS = 1e-9


def check_shrunk_cert(d):
    errs = list(C141.check_lane_cert(d))
    s = d["s"]
    cell = d["cell_rect"]
    t = d.get("translate")
    ij = d.get("slot_ij")
    hs = d.get("snap_h")
    dl = d.get("snap_delta")

    # C7 -- the cell is the unit slot cell translated by t, and |t|_inf <= snap_h = delta/sqrt(2)
    if t is None or ij is None or hs is None or dl is None:
        return errs + ["missing translate / slot_ij / snap_h / snap_delta"]
    if abs(hs - dl / SQ2) > 1e-12:
        errs.append("snap_h != snap_delta / sqrt(2)")
    if max(abs(t[0]), abs(t[1])) > hs + 1e-12:
        errs.append("|t|_inf = %.9g exceeds the pin tolerance %.9g" % (max(map(abs, t)), hs))
    want = [ij[0] + t[0], ij[0] + 1.0 + t[0], ij[1] + t[1], ij[1] + 1.0 + t[1]]
    if any(abs(a - b) > 1e-9 for a, b in zip(cell, want)):
        errs.append("cell_rect %s is not the unit cell (%d,%d) translated by %s"
                    % (cell, ij[0], ij[1], t))

    # C8 -- the translated cell is inside the container of the corner frame
    if cell[0] < -EPS or cell[2] < -EPS or cell[1] > s + EPS or cell[3] > s + EPS:
        errs.append("translated cell leaves the container [0, %g]^2" % s)

    # C9 -- interior-disjoint from every admissible pin position
    meet = set(d.get("M_index") or [])
    pins = [b for k, b in enumerate(d["cond_boxes"]) if k not in meet]
    if not pins and d.get("n_pins"):
        errs.append("n_pins = %s but no pin box could be identified" % d.get("n_pins"))
    for k, b in enumerate(pins):
        X0, X1 = b[0] - 0.5, b[1] + 0.5
        Y0, Y1 = b[2] - 0.5, b[3] + 0.5
        if not (cell[1] <= X0 + EPS or cell[0] >= X1 - EPS
                or cell[3] <= Y0 + EPS or cell[2] >= Y1 - EPS):
            errs.append("translated cell overlaps pin %d's admissible square "
                        "[%.6f,%.6f]x[%.6f,%.6f]" % (k, X0, X1, Y0, Y1))
        if abs(b[4]) > 1e-12 or abs(b[5]) > 1e-12:
            errs.append("pin box %d is not zero-tilt" % k)

    # C10a -- the pin obstacle boxes carry at least the node's own pin slack
    ph = d.get("pin_h")
    if ph is None:
        errs.append("no pin_h recorded")
    elif ph > 0:
        for k, b in enumerate(pins):
            if (b[1] - b[0]) < 2.0 * ph - 1e-9 or (b[3] - b[2]) < 2.0 * ph - 1e-9:
                errs.append("pin box %d is narrower than the node's pin slack 2*%g" % (k, ph))

    # C10b -- the certificate must declare itself conditional
    if not d.get("conditional"):
        errs.append("a translated-snap kill is CONDITIONAL on the slack-form kill of the "
                    "extension class; the certificate does not say so")
    if not d.get("prerequisite"):
        errs.append("no `prerequisite` field naming the missing slack-form extension kill")
    if not d.get("extension"):
        errs.append("no extension class recorded")
    return errs


def check_file(p):
    d = json.load(open(p, encoding="utf-8"))
    if d.get("format") != "polycore_slot_lane_shrunk_v1":
        return ["not a polycore_slot_lane_shrunk_v1 certificate (%r)" % d.get("format")]
    return check_shrunk_cert(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="*")
    ap.add_argument("--dir", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    files = list(a.certs)
    if a.dir:
        files += sorted(glob.glob(os.path.join(a.dir, "*.json")))
    rows, bad = [], 0
    for p in files:
        try:
            errs = check_file(p)
        except Exception as e:                              # noqa: BLE001
            errs = ["EXCEPTION " + repr(e)[:200]]
        rows.append(dict(cert=os.path.basename(p), ok=not errs, errors=errs[:8]))
        bad += bool(errs)
        print(("PASS  " if not errs else "FAIL  ") + os.path.basename(p)
              + ("" if not errs else "   " + errs[0]), flush=True)
    print("checked %d, failed %d" % (len(files), bad))
    if a.out:
        json.dump(dict(checked=len(files), failed=bad, rows=rows),
                  open(a.out, "w", encoding="utf-8"), indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
