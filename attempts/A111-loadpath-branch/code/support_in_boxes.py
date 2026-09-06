"""A111 -- does the node's own LP support satisfy the YES hypothesis?

For every alive node a shadow explains, map the shadow's boxes into the node's frame (inverse of
A107's struct_op) and count how many boxes contain a square of the node's representative support
configuration (A107's extract.json cfg = hypothesis cores + integral placements).  A node whose
support meets EVERY box is a node at which the branch bites: its YES child is the one the chain
leaf kills, and its NO children have to remove exactly that support.

Writes results/support_in_boxes.json.  Read-only.
"""
from __future__ import annotations

import collections, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1
import t2_no as T2

RADII = ((0.02, 2.0), (0.035, 2.43), (0.05, 5.0), (0.0699, 4.87), (0.1, 10.0), (0.2, 20.0))


def cls_of(nid, src):
    for c in ("k5_11", "k5_16"):
        if nid.startswith(c):
            return c
    return "trump5"


def main():
    ex = {(n["src"], n["nid"]): n for n in
          json.load(open(os.path.join(T2.A107R, "extract.json"), encoding="utf-8"))["nodes"]}
    out = {}
    for tag in ("S02", "S07"):
        sn = json.load(open(os.path.join(T2.A107R, "shadow_nodes.json"), encoding="utf-8"))[tag]
        t4 = {}
        p4 = os.path.join(T2.A110R, "t4_%s.jsonl" % tag)
        if os.path.exists(p4):
            for line in open(p4, encoding="utf-8"):
                d = json.loads(line)
                t4[(d["src"], d["nid"])] = bool(d["inside_family"])
        rows = []
        for rec in sn:
            key = (rec["src"], rec["nid"])
            n = ex.get(key)
            if n is None:
                continue
            op = n.get("struct_op") or "e"
            cls = cls_of(rec["nid"], rec["src"])
            cfg = n["cfg"]
            per = {}
            for (r, rho) in RADII:
                bn, NB = T2.node_boxes(tag, "lpa", cls, r, rho, op, L.S0)
                hit = 0
                for b in bn:
                    B = NB[b]
                    if any(B["x0"] <= x <= B["x1"] and B["y0"] <= y <= B["y1"]
                           and any(B["th0"] <= (math.degrees(t) % 90.0) + o <= B["th1"]
                                   for o in (-90.0, 0.0, 90.0))
                           for (x, y, t) in cfg):
                        hit += 1
                per["%g/%g" % (r, rho)] = [hit, len(bn)]
            rows.append(dict(src=rec["src"], nid=rec["nid"], level=rec["level"], cls=cls, op=op,
                             inside_family=t4.get(key), boxes_hit=per))
        summ = {}
        for k in rows[0]["boxes_hit"]:
            full = sum(1 for q in rows if q["boxes_hit"][k][0] == q["boxes_hit"][k][1])
            full_in = sum(1 for q in rows
                          if q["inside_family"] and q["boxes_hit"][k][0] == q["boxes_hit"][k][1])
            mean = sum(q["boxes_hit"][k][0] for q in rows) / max(1, len(rows))
            summ[k] = dict(all_boxes_hit=full, of=len(rows),
                           all_boxes_hit_inside_family=full_in,
                           inside_family=sum(1 for q in rows if q["inside_family"]),
                           mean_boxes_hit=round(mean, 2))
        out[tag] = dict(rows=rows, summary=summ)
        print(tag, json.dumps(summ, indent=1), flush=True)
    json.dump(out, open(os.path.join(L.RES, "support_in_boxes.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
