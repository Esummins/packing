"""A149 -- the nodes NO queue has ever offered: G1-tree rows masked by a dead L1-tree row.

`targets137.py` (and anything else that walks `tree_*.jsonl` into a dict keyed by id) builds a
LAST-WINS map.  An id can name a node in BOTH window trees -- the G1 tree (slack pins,
delta = 1e-2, pin core 0.492928902) and the L1 tree (eps-fat pins, core 1/2 - 2.98e-8) -- and the
two are different nodes with different hypotheses; PAUSED v3 Sec.C.3 makes exactly this point for
the fold-in.  When the L1 row is PASS and the G1 row is ALIVE or FAIL, the last-wins map records
the id as dead and the OPEN G1 node is silently dropped from every queue.

19 such nodes exist.  The coordinator's second priority bump, `k5_11_interior_Y0275`, is one of
them, and it is a CERTIFIED KILL on the first re-solve (tau 4.999999999999965 -> 3.999999999999985,
frozen verify_case PASS) -- so the population is worth running, not just recording.

This builds the remaining ones, G1 box and G1 budget, in `frac_exact` order where A145 measured it.
Read-only; writes only `results/targets_masked149.json`.
"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees", "results")
A145 = os.path.join(ROOT, "A145-impossible-weight", "results", "impossible_weight.jsonl")
OUT = os.path.join(BASE, "results", "targets_masked149.json")


def cat(c):
    c = c or ""
    for pre, n in (("PASS", "PASS"), ("KILL-BY-LOGIC", "logic"), ("ALIVE", "ALIVE"),
                   ("FAIL", "FAIL")):
        if c.startswith(pre):
            return n
    return "other"


def main():
    G1, last = {}, {}
    for p in sorted(glob.glob(os.path.join(A57, "tree_*.jsonl"))):
        b = os.path.basename(p)
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            v = cat(r.get("cert"))
            last[r["id"]] = v
            if "_G1" not in b:
                continue
            if r["id"] in G1 and G1[r["id"]]["verdict"] in ("PASS", "logic"):
                continue        # a kill on any G1 row is absorbing
            G1[r["id"]] = dict(verdict=v, box=r.get("box"), budget=r.get("budget", 5),
                               tau=r.get("tau"), eta=r.get("eta"), cert=r.get("cert"))

    FR = {}
    if os.path.exists(A145):
        for ln in open(A145, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("frac_exact") is not None:
                FR[r["id"]] = float(r["frac_exact"])

    done = set()
    for fn in os.listdir(os.path.join(BASE, "results")):
        if fn.startswith("exact_reemit_") and fn.endswith(".jsonl"):
            for ln in open(os.path.join(BASE, "results", fn), encoding="utf-8"):
                try:
                    done.add(json.loads(ln)["id"])
                except Exception:
                    pass

    T = []
    for nid, g in G1.items():
        if g["verdict"] not in ("ALIVE", "FAIL") or last.get(nid) not in ("PASS", "logic"):
            continue
        if nid in done or not g["box"]:
            continue
        T.append(dict(id=nid, box=g["box"], budget=g["budget"], scope="exall",
                      level=1 + nid.count("_D"), eta=g["eta"], tau=g["tau"],
                      frac_exact=FR.get(nid), prior=(g["cert"] or "")[:40],
                      cls=nid.split("_interior")[0],
                      why="G1-tree row masked by a dead L1-tree row of the same id"))
    T.sort(key=lambda t: (-(0.45 if t["frac_exact"] is None else t["frac_exact"]),
                          t["level"], t["id"]))
    json.dump(T, open(OUT, "w"), indent=0)
    print("%d masked G1 nodes -> %s" % (len(T), OUT))
    print(json.dumps(collections.Counter(t["prior"][:5] for t in T)))
    for t in T[:20]:
        print("   %-32s %-6s frac_exact %s  tau %s" % (t["id"], t["prior"][:5], t["frac_exact"],
                                                       t["tau"]))


if __name__ == "__main__":
    main()
