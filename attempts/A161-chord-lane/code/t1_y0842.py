"""A161 T1 -- `k5_16_interior_Y0842` at BL(1,0), the node the PI read, with the unit tests of the
two new primitives it depends on.

    python t1_y0842.py [--nid k5_16_interior_Y0842] [--slot "BL(1,0)"] [--sample 40000]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import chordlane as CL  # noqa: E402
import polylane as P  # noqa: E402
import polycore as PC  # noqa: E402
import guardline as GL  # noqa: E402
from caselp import Box  # noqa: E402
from fractions import Fraction as Fr  # noqa: E402


def selftest(rng):
    """Independent checks of `box_misses_cell_exact` and `band_ok` against brute-force sampling."""
    out = []
    cell = (1.0, 2.0, 0.0, 1.0)
    boxes = [
        Box(2.218056, 2.357813, 1.519271, 1.659028, 53.13010235415598, 64.01076641616699),
        Box(1.30, 1.50, 1.20, 1.40, 0.0, 90.0),          # should NOT be excluded
        Box(3.00, 3.20, 2.00, 2.20, 0.0, 90.0),          # far away: excluded
        Box(0.50, 0.60, 0.50, 0.60, 0.0, 0.0),           # the BL pin: meets? no (x <= 1.1)
    ]
    for b in boxes:
        ok, det = CL.box_misses_cell_exact(b, cell)
        n = 60000
        C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
        T = np.radians(rng.uniform(b.th0, b.th1, n)) if b.th1 > b.th0 else \
            np.full(n, np.radians(b.th0))
        hits = int(P.rect_square_meets(cell, C, T).sum())
        out.append(dict(box=P.box_json(b), exact_excluded=bool(ok), detail=det,
                        sampled_meeting=hits,
                        SOUND=(not ok) or hits == 0))
    # band_ok: every pose of a box declared BAND must have chord >= 1 on the line
    ln = GL.Line("h", Fr(99, 100), tag="test")
    tests = []
    for b in (Box(1.2, 1.4, 0.9, 1.0, 0.0, 5.0), Box(1.2, 1.4, 1.30, 1.45, 0.0, 3.0),
              Box(1.2, 1.4, 1.2, 1.5, 0.0, 90.0)):
        ok, det = CL.band_ok(b, ln)
        n = 40000
        C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
        T = np.radians(rng.uniform(b.th0, b.th1, n)) if b.th1 > b.th0 else \
            np.full(n, np.radians(b.th0))
        ch = CL.chord_band_lo(T, ln.foff - C[:, 1])
        tests.append(dict(box=P.box_json(b), band=bool(ok), detail=det,
                          min_sampled_chord=float(ch.min()),
                          SOUND=(not ok) or float(ch.min()) >= 1.0 - 1e-12))
        # cross-check against A144's independent five-point minimum
        mc = GL.minchord_box(b, ln, a=Fr(1, 2))
        tests[-1]["A144_minchord"] = mc["lo_float"]
        tests[-1]["AGREES_WITH_A144"] = bool(ok) == (mc["lo"] >= 1)
    return dict(misses_cell=out, band=tests)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="k5_16_interior_Y0842")
    ap.add_argument("--slot", default="BL(1,0)")
    ap.add_argument("--sample", type=int, default=40000)
    ap.add_argument("--maxopen", type=int, default=3000)
    ap.add_argument("--maxdepth", type=int, default=34)
    ap.add_argument("--off", default="")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t1_y0842.json"))
    a = ap.parse_args()
    t0 = time.time()
    rng = np.random.default_rng(1611)

    st = selftest(rng)
    bad = [r for r in st["misses_cell"] + st["band"] if not r["SOUND"]]
    print("selftest: %d cases, %d UNSOUND" % (len(st["misses_cell"]) + len(st["band"]), len(bad)),
          flush=True)
    for r in st["misses_cell"]:
        print("  misses_cell %s -> %s (%s) sampled_meeting=%d" %
              (r["box"][:2], r["exact_excluded"], (r["detail"] or {}).get("axis"),
               r["sampled_meeting"]), flush=True)
    for r in st["band"]:
        print("  band %s -> %s min_chord=%.6f a144=%.6f agree=%s" %
              (r["box"][2:4], r["band"], r["min_sampled_chord"], r["A144_minchord"],
               r["AGREES_WITH_A144"]), flush=True)

    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    rec = recs[a.nid]
    print("\n%s  cls=%s level=%s alive=%s  |  slot %s" %
          (a.nid, rec["cls"], rec["level"], rec.get("alive"), a.slot), flush=True)
    conds, meet, cell, corner, i, j = CL.frame_boxes(rec, a.slot)
    for c in conds:
        print("  B%d %s  K' verts=%d area=%.6f" %
              (c.idx, ["%.6f" % v for v in P.box_json(c.box)], len(c.pc.verts), c.pc.area()),
              flush=True)

    row, cert = CL.run_slot(rec, a.slot, rng=rng, sample=a.sample, max_open=a.maxopen,
                            max_depth=a.maxdepth,
                            force_off=(Fr(a.off) if a.off else None))
    print("\nVERDICT %s   beta=%s LANE_out=%s M=%s total=%s" %
          (row["verdict"], row.get("beta"), row.get("lane_out"), row.get("M"),
           row.get("total")), flush=True)
    if "line" in row:
        print("  guard line %s = %s   rhs = %s = %.9f" %
              (row["line"]["orient"], row["line"]["off"], row.get("rhs"),
               row.get("rhs_float", float("nan"))), flush=True)
        for t in row.get("minchords", []):
            print("    minchord(B%d) = %s = %.9f  (V=%.6f, %s)" %
                  (t["j"], t["minchord"], t["minchord_float"], t["V"], t["method"]), flush=True)
    print("  sample:", json.dumps({k: v for k, v in (row.get("sample") or {}).items()
                                   if k != "per_core"}), flush=True)
    print("  M_detail:", json.dumps(row.get("M_detail")), flush=True)

    res = dict(nid=a.nid, slot=a.slot, selftest=st, row=row, elapsed=round(time.time() - t0, 1))
    if cert is not None:
        import hashlib
        p = os.path.join(BASE, "certs", "cl_%s__%s.json"
                         % (a.nid, a.slot.replace("(", "").replace(")", "").replace(",", "_")))
        blob = json.dumps(cert, sort_keys=True, indent=1).encode("utf-8")
        open(p, "wb").write(blob)
        res["cert"] = os.path.relpath(p, os.path.join(BASE, "..", ".."))
        res["sha256"] = hashlib.sha256(blob).hexdigest()
        print("  cert %s  sha256 %s" % (res["cert"], res["sha256"][:16]), flush=True)
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)
    print("\ndone %.1f s -> %s" % (time.time() - t0, a.out), flush=True)


if __name__ == "__main__":
    main()
