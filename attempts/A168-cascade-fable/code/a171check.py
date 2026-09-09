"""A168 -- re-verify every ALIVE node of a cascade tree with A171's multibox invariant library
(`attempts/A171-multibox-invariant/code/multibox.py`, read-only): rebuild the node from the SAME
source boxes the cascade normalised (H's box and every role's `src` cover box), run
`Node.normalise(s, nsub=4, strict_container=False)` -- the SOUND w_min container clip, as A171's
soundness note prescribes for anything certified -- then `assert_invariant()`.

Three outcomes per node, all recorded in results/a171_<cell>.json and back into the tree:
  * A171 PASS: the invariant holds on A171's normalised boxes; kept fractions compared with ours;
  * A171 EmptyBox: A171's clip empties a box we kept -> the node is DEAD by A171's pair leaf and
    is re-marked DEAD(C, A171 EmptyBox) (a strictly stronger clip found the contradiction);
  * A171 InvariantError on its OWN normalised boxes: reported loudly (would be a library
    disagreement; none expected).
Nothing here relaxes a verdict: a node we call DEAD stays DEAD.

    python a171check.py --cell l1_104 [--steps S1,S2] [--max 200]
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import cascade168 as CS                                          # noqa: E402
sys.path.insert(0, os.path.join(K.ATT, "A171-multibox-invariant", "code"))
import multibox as MB                                            # noqa: E402  A171 (read-only)
from caselp import Box                                           # noqa: E402


def src_boxes(T, node):
    out = {}
    for nm, rj in node["roles"].items():
        src = rj.get("src")
        if src is None:
            src = T["H"]["box"] if nm == "H" else rj["box"]
        out[nm] = tuple(src)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--steps", default="")
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=1)
    ap.add_argument("--write", type=int, default=1)
    a = ap.parse_args()
    T = CS.load_tree(a.cell)
    steps = set(a.steps.split(",")) if a.steps else None
    rows = []
    n_pass = n_empty = n_err = n_kept_disagree = 0
    t00 = time.time()
    for p, n in list(T["nodes"].items()):
        if not n.get("roles") or not n["verdict"].startswith("ALIVE"):
            continue
        if (n.get("step") or "root") == "root" or (n.get("step") or "").endswith("complement"):
            continue
        if steps and n.get("step") not in steps:
            continue
        if a.max and len(rows) >= a.max:
            break
        if K.sentinel():
            break
        t0 = time.time()
        boxes = src_boxes(T, n)
        row = dict(node=p, step=n.get("step"), roles=list(boxes))
        try:
            nd = MB.Node(boxes, s=K.S_RAT, name=p)
            nd.normalise(K.S_RAT, nsub=a.nsub, strict_container=False, refine=a.refine)
            rep = nd.assert_invariant(raise_on_fail=True, strict=False)   # sound clip => POSE-CONTAINER-STRICT is a diagnostic, not a gate (A171 limitation (i))
            row.update(result="PASS", kept_a171=nd.kept(), kept_ours=n.get("kept"),
                       checks={k: v.get("ok") for k, v in rep.get("checks", {}).items()},
                       diagnostics=rep.get("diagnostics"))
            n_pass += 1
            ko, ka = n.get("kept") or {}, nd.kept()
            if any(abs(ko.get(k, 1.0) - ka.get(k, 1.0)) > 0.25 for k in ka):
                n_kept_disagree += 1
                row["kept_disagree"] = True
        except MB.EmptyBox as e:
            row.update(result="EmptyBox", detail=str(e)[:200])
            n_empty += 1
            if a.write:
                n["verdict"] = "DEAD(C, A171 multibox.normalise EmptyBox: %s)" % str(e)[:80]
                n["a171"] = "EmptyBox"
        except MB.InvariantError as e:
            row.update(result="InvariantError", detail=str(e)[:400])
            n_err += 1
        except Exception as e:                                       # noqa: BLE001
            row.update(result="error", detail=repr(e)[:200])
            n_err += 1
        row["wall_s"] = round(time.time() - t0, 1)
        if row["result"] == "PASS" and a.write:
            n["a171"] = dict(result="PASS", kept=row["kept_a171"])
        rows.append(row)
        print("  %-36s %-14s kept_a171=%s ours=%s %.1fs" % (
            p, row["result"], {k: round(v, 2) for k, v in (row.get("kept_a171") or {}).items()},
            {k: round(v, 2) for k, v in (n.get("kept") or {}).items()}, row["wall_s"]), flush=True)
    out = dict(cell=a.cell, n=len(rows), n_pass=n_pass, n_emptybox=n_empty, n_error=n_err,
               n_kept_disagree=n_kept_disagree, rows=rows, wall_s=round(time.time() - t00, 1),
               settings=dict(nsub=a.nsub, strict_container=False, assert_strict=False, refine=a.refine))
    K.jdump(out, os.path.join(K.RES, "a171_%s.json" % a.cell))
    if a.write:
        T["a171"] = {k: v for k, v in out.items() if k != "rows"}
        CS.save_tree(T)
    print("A171 re-verification of %s: %d nodes, %d PASS, %d EmptyBox (re-marked DEAD), %d errors, "
          "%d kept disagreements > 0.25; %.1fs" % (a.cell, len(rows), n_pass, n_empty, n_err,
                                                    n_kept_disagree, out["wall_s"]), flush=True)


if __name__ == "__main__":
    main()
