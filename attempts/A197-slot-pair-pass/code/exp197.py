"""A197 experiment: does the MEET constraint iterated to a FIXED POINT kill the H-meets branch?

  python exp197.py <nid> <cell> [nsub] [refine] [iters]

The H-meets branch of a forced cell is {pins, H, one free B}, with BOTH H and B required to MEET the
widened open slot box.  A178 carried neither requirement; A197's first pass carried them once (the
exact meet cover of each role's box).  Here they are carried to a FIXED POINT: normalise, take each
role's surviving hull, re-apply the exact meet cover, normalise again.  Each step is sound (the meet
cover drops only poses whose square provably misses the box, and the hull only shrinks).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))
sys.path.insert(0, HERE)
import geo178 as G                                              # noqa: E402
import pair197 as P                                             # noqa: E402
import csv                                                      # noqa: E402


def record_of(nid):
    d = os.path.join(ROOT, "docs", "shadows", "a57v4")
    for r in csv.DictReader(open(os.path.join(d, "review_a57v4.csv"), encoding="utf-8")):
        if r["node"] == nid:
            return r["record"].replace("\\", "/")
    raise SystemExit("no such page " + nid)


def main():
    nid = sys.argv[1]
    cell = sys.argv[2]
    nsub = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    refine = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    iters = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    rec = G.load_record(record_of(nid))
    cls = G.class_of_record(rec)
    base = G.base_roles(rec)
    hn = [k for k in base if k.startswith("H")][0]
    pinroles = {k: v for k, v in base.items() if k.startswith("P")}
    it = [x for x in G.forced_items(cls, rec) if x["cell"] == cell][0]
    wbox, W = it["wbox"], it["window"]
    tag = "B_" + cell.replace("(", "").replace(",", "").replace(")", "")
    hcur = P.meet_cover(base[hn], wbox, max_boxes=1)
    bcur = P.meet_cover((W[0], W[1], W[2], W[3], 0.0, 90.0), wbox, max_boxes=1)
    print("%s %s  H0 %s" % (nid, cell, base[hn]))
    if not hcur:
        print("H-meets VACUOUS: H can never meet the widened box (A161 exact)")
        return
    hcur, bcur = hcur[0], bcur[0]
    cs = {tag: it["corner"]} if it.get("is_corner") else None
    for k in range(iters):
        t = time.time()
        nd, info = G.run_node(dict(pinroles, **{hn: hcur, tag: bcur}), corners=cs,
                              nsub=nsub, refine=refine, label="exp/%s/%d" % (cell, k))
        if info["dead"]:
            print("iter %d: DEAD EmptyBox(%s) in %.0f s  <-- the H-meets branch is empty"
                  % (k, info["dead"], time.time() - t))
            return
        h2, b2 = G.hull_of(nd, hn), G.hull_of(nd, tag)
        print("iter %d: %.0f s kept H %.4g B %.4g | H %s | B %s"
              % (k, time.time() - t, info["kept"][hn], info["kept"][tag],
                 ["%.4f" % v for v in h2], ["%.4f" % v for v in b2]))
        hc, bc = P.meet_cover(h2, wbox, max_boxes=1), P.meet_cover(b2, wbox, max_boxes=1)
        if not hc or not bc:
            print("iter %d: VACUOUS after the meet cover (%s can no longer meet the box)"
                  % (k, "H" if not hc else "B"))
            return
        h3, b3 = hc[0], bc[0]
        shrink = (P._vol(h3) < P._vol(hcur) * (1 - 1e-9)) if hasattr(P, "_vol") else True
        same = (tuple(round(v, 12) for v in h3) == tuple(round(v, 12) for v in hcur)
                and tuple(round(v, 12) for v in b3) == tuple(round(v, 12) for v in bcur))
        hcur, bcur = h3, b3
        print("        meet cover -> H %s | B %s%s"
              % (["%.4f" % v for v in h3], ["%.4f" % v for v in b3], "  (fixed point)" if same else ""))
        if same:
            break
    print("H-meets branch ALIVE at the fixed point")


if __name__ == "__main__":
    main()
