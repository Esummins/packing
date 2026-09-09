"""A168 -- the two FREE screens at every node: A164's uncoverable area |U| (Leaf WASTE, charged
against B0 = s0^2 - 11) and A153's cover number (Leaf CN: the number of side-0.7 pieces needed to
cover the outer admissible-centre region, against the budget).  Both are read-only imports of
A164 `geo164` and A153 `cover153`; both are certified LOWER bounds in the sound direction (a kill
needs |U| > B0, resp. cover < budget).

    python screens168.py --list results/lpnodes_l1_104.json
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
for _p in (os.path.join(K.ATT, "A164-wastage-area", "code"),
           os.path.join(K.ATT, "A153-cover-number", "code"),
           os.path.join(K.ATT, "A148-gallery-v4", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import geo164 as G                                               # noqa: E402  A164 (read-only)
import cover153 as CN                                            # noqa: E402  A153 (read-only)
from caselp import Box                                           # noqa: E402

B0 = K.S0 * K.S0 - 11.0


def screens(boxes, budget, pitch=0.02, ntilt=30):
    bj = [b.to_json() for b in boxes]
    t0 = time.time()
    O, names, kinds, _ = G.obstacles_of(bj)
    Um, xs, ys, res = G.uncoverable(K.S0, O, boxes, lam=1.0, pitch=pitch, ntilt=ntilt,
                                    want_extra=False)
    out = dict(area_U=res["area_U"], B0=B0, area_kill=bool(res["area_U"] > B0),
               U_wall_s=round(time.time() - t0, 1))
    t0 = time.time()
    try:
        pr, reg, obst, onames, kinds = CN.price_node(boxes, budget, is_pin=None, exact_limit=6,
                                                     floor=True)
        out.update(cover=pr["cover"], cover_lb=pr["lb"], cover_kills=pr["kills"],
                   floor_1sep=pr.get("floor_1sep"), area_open=pr["area_open"],
                   CN_wall_s=round(time.time() - t0, 1))
    except Exception as e:                                       # noqa: BLE001
        out["cover_error"] = repr(e)[:200]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--pitch", type=float, default=0.02)
    ap.add_argument("--ntilt", type=int, default=30)
    a = ap.parse_args()
    nodes = json.load(open(a.list, encoding="utf-8"))
    out = a.out or os.path.join(K.RES, "screens_%s.jsonl" % os.path.basename(a.list)[8:-5])
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            done.add(json.loads(ln)["node"])
    for n in nodes:
        if n["node"] in done or K.sentinel():
            continue
        boxes = [Box(**b) for b in n["boxes"]]
        r = screens(boxes, n["budget"], a.pitch, a.ntilt)
        r.update(node=n["node"], cell=n["cell"], step=n.get("step"), budget=n["budget"],
                 n_boxes=len(boxes))
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(r) + "\n")
        print("%-40s b=%d |U|=%.4f/%.4f cover=%s (lb %s) floor=%s" % (
            n["node"], n["budget"], r["area_U"], B0, r.get("cover"), r.get("cover_lb"),
            r.get("floor_1sep")), flush=True)


if __name__ == "__main__":
    main()
