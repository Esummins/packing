"""A111 -- the two FREE logic kills at a YES node (coordinator's addendum item 3).

At a node the YES child's hypothesis is: the class pins + the node's own CONDITIONED box B_node +
one square in each load-path box F_i (in the node's frame).  Two of those pairs can be killed with
no LP at all:

 (K1) CORE-MEET between B_node and some F_i -- A57's own contradictory rule (`pinguard`, A96 tight
      core) applied to two branch boxes instead of a box and a pin.  If the tight cores meet and the
      two boxes share no pose, the conditioned square and the F_i square would have to overlap.

 (K2) Lemma TC between the same two bins -- centre distance c forces |dtheta| <= D(c),
      (1 + cos D + sin D)/2 = c; if the bins force a bigger tilt gap than the centre gap allows,
      the pair is impossible.

Both are one-sided and cost microseconds.  This measures their YIELD over every alive node the two
shadows explain, at each radius, and reports which rule fires.

Writes results/t3_logickills.json.  Read-only.
"""
from __future__ import annotations

import collections, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1
import t2_no as T2
import octagon as OC
from caselp import Box

RADII = ((0.02, 5.0), (0.05, 5.0), (0.0699, 4.87), (0.035, 2.43), (0.0175, 1.22), (0.0087, 0.61), (0.1, 10.0), (0.2, 20.0))


def cond_boxes(node):
    """the node's own conditioned (non-pin) boxes, from its hypothesis."""
    out = []
    for b in node["cores"] if isinstance(node.get("cores"), list) else []:
        pass
    return out


def main():
    ex = {(n["src"], n["nid"]): n for n in
          json.load(open(os.path.join(T2.A107R, "extract.json"), encoding="utf-8"))["nodes"]}
    out = {}
    for tag in ("S02", "S07"):
        sn = json.load(open(os.path.join(T2.A107R, "shadow_nodes.json"), encoding="utf-8"))[tag]
        rows = []
        for rec in sn:
            key = (rec["src"], rec["nid"])
            n = ex.get(key)
            if n is None:
                continue
            op = n.get("struct_op") or "e"
            cls = ("k5_11" if rec["nid"].startswith("k5_11")
                   else "k5_16" if rec["nid"].startswith("k5_16") else "trump5")
            # the node's conditioned boxes: A110's t4 rule -- a hypothesis box that is not a pin
            p = L.copy_node(rec["nid"], rec["src"])
            if p is None:
                continue
            d = json.load(open(p, encoding="utf-8"))
            cond = [b for b in d["hyp"]["boxes"]
                    if (b["th1"] - b["th0"]) > 1e-6 or (b["x1"] - b["x0"]) > 0.02]
            if not cond:
                continue
            s_node = d["s"]
            per = {}
            for (r, rho) in RADII:
                bn, NB = T2.node_boxes(tag, "lpa", cls, r, rho, op, s_node)
                fires = []
                for ci, cb in enumerate(cond):
                    for nm in bn:
                        ok, info = OC.pair_kill(cb, NB[nm])
                        if ok:
                            fires.append(dict(box=nm, cond=ci, rule=info.get("rule"),
                                              **{k: v for k, v in info.items() if k != "rule"}))
                per["%g/%g" % (r, rho)] = dict(killed=bool(fires), fires=fires,
                                               n_cond=len(cond), n_boxes=len(bn))
            rows.append(dict(src=rec["src"], nid=rec["nid"], level=rec["level"], cls=cls, op=op,
                             per_radius=per))
        summ = {}
        for k in RADII:
            kk = "%g/%g" % k
            n_k = sum(1 for q in rows if q["per_radius"][kk]["killed"])
            rules = collections.Counter(f["rule"] for q in rows
                                        for f in q["per_radius"][kk]["fires"])
            summ[kk] = dict(free_logic_kills=n_k, of=len(rows), by_rule=dict(rules))
        out[tag] = dict(rows=rows, summary=summ)
        print(tag, json.dumps(summ), flush=True)
    json.dump(out, open(os.path.join(L.RES, "t3_logickills.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
