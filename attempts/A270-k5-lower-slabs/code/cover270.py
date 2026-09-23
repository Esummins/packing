"""A270 -- is A57's G1 level-1 COVER complete?  Every box of the cover against the rows of the G1 tree (READ-ONLY).

A57's G1 tree (lemmas.md T23) is a statement about k5_11 / k5_16 ONLY if EVERY child of its root is closed: the NO
child and the YES box B_i for every box of the cover of the interior zone (tree57.build_children, the same call the
shards made: w 0.15, nth 8, cw 0.6, a_min 0.34, pin_delta 1e-2, side s0; the T5'' trim deployed).  load211.census()
lists only the tree ROWS that are ALIVE / FAIL -- a box whose shard never reached it has no row and is invisible to
it.  This file rebuilds the cover (pure geometry, ~2 s a class), and classifies every child:

  row      the G1 tree (k5_*_interior_G1 jsonl, any shard) holds a row for the id -- closed / alive as the census says
  logic    no row, but tree57's own pinguard / T5'' classification is 'contradictory' (a free logic kill: T5, the
           box's core meets a pin core; valid wherever the pin cores sit inside the dilated pins -- G1 by B')
  MISSING  no row and pinguard 'ok': the box needs an LP or a page kill, and has NEITHER -- open on EVERY slab

    python cover270.py      -> results/cover270.json (+ the per-class counts on stdout)"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees")
sys.path.insert(0, os.path.join(A57, "code"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"))


def main():
    import tree57 as T                                          # READ-ONLY (A57): build_children only
    import load211 as L                                         # READ-ONLY (A211): the tree rows, dead_ids
    trees = L.trees()
    dead = L.dead_ids()
    out = dict(params=dict(w=0.15, nth=8, cw=0.6, a_min=0.34, pin_delta=0.01, side="969271/250000"), classes={})
    for cls in ("k5_11", "k5_16"):
        kids, bad, slots, rect, grid = T.build_children(cls, "interior", 0.15, 8, 0.6, 0.34, pin_delta=1e-2)
        rows = trees.get("%s_interior_G1" % cls, {})
        recs, cnt = [], collections.Counter()
        for k in kids:
            i = k["id"]
            if i in rows:
                v = rows[i][0]
                st = "row:" + v
                if v in ("ALIVE", "FAIL"):
                    st += ":closed-by-ledger" if L.is_dead(i, "%s_interior_G1" % cls, dead) else ":OPEN"
            elif k.get("pin") == "contradictory":
                st = "logic"
            else:
                st = "MISSING"
            cnt[st] += 1
            b = k["box"]
            recs.append(dict(id=i, kind=k["kind"], pin=k.get("pin"), status=st,
                             box=None if b is None else [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]))
        out["classes"][cls] = dict(children=len(kids), uncoverable=len(bad), counts=dict(cnt), rows_not_in_cover=sorted(
            set(rows) - {k["id"] for k in kids}), children_list=recs)
        print("%s: %d children (%d uncoverable); %s; tree rows outside the rebuilt cover: %d" % (
            cls, len(kids), len(bad), dict(sorted(cnt.items())), len(out["classes"][cls]["rows_not_in_cover"])))
    json.dump(out, open(os.path.join(ATT, "results", "cover270.json"), "w", encoding="utf-8"), indent=0)


if __name__ == "__main__":
    main()
