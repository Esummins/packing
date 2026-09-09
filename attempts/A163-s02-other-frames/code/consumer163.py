"""A163 T2 -- A151's / A116's consumer test, adapted to k5_16's and trump5's frames.

The test (A116's, kept verbatim): canonicalise the node's A107 representative support into the
shadow frame with A107's `struct_op`, then look for an injection of the certificate's TILTED free
boxes (`f1 f2 f3`) into DISTINCT support squares with every coordinate inside its box (tilt compared
mod 90 deg around the box's anchor).  `BR(0,1)` is a slot square and is not matched -- A116's
convention, kept, so the numbers are comparable with A116's 72 / A151's 96 / A160's 114.

What the FRAME changes is not the geometric test -- the boxes are the same absolute boxes -- but
*whose* nodes may be tested: a k5_16 node has k5_16's five pins fixed by construction, so only a
certificate whose hypothesis pins those five squares can kill it.  That is why the 68 k5_16 and 12
trump5 S02 nodes had no consumer count before this attempt.

Populations
  * k5_16: the 68 S02 nodes of `A107/shadow_nodes.json`; ALIVE = A151's `alive_s02.json` (37).
  * trump5: the 12 S02 nodes of the A60 protected-tier run (`residue_ledger` sec 1b); the three
    `*.stageA` A61 rows in A107's S02 list are k5_02 / k5_03 / k6_29 and are NOT trump5, so they are
    excluded.  A60 is PAUSED and has had no re-solve ledger since A107, so all 12 count as alive
    (`residue_ledger` sec 0: "325 alive nodes in A107's input (S01 196, S07 18, S02 12)").

    python consumer163.py --cls k5_16 [--tree ../results/tree_k5_16.jsonl]
    python consumer163.py --cls k5_11 --control      # reproduce A160's 114 / 50

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, itertools, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                            # noqa: E402
import a116lib as A                           # noqa: E402

TRUMP5_SRC = ("A60",)


def node_class(rec):
    if rec["src"] == "A57":
        return rec["nid"].split("_interior")[0]
    if rec["src"] in TRUMP5_SRC:
        return "trump5"
    return "other:" + rec["src"]              # A61's k5_02 / k5_03 / k6_29 stage-A rows


def supports(cls):
    sn = json.load(open(os.path.join(L.A107R, "shadow_nodes.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(L.A107R, "extract.json"), encoding="utf-8"))["nodes"]
    idx = {(n["src"], n["nid"]): n for n in ex}
    f = dict(A.L11.d4_ops(A.S0))
    rows = []
    for rec in sn["S02"]:
        if node_class(rec) != cls:
            continue
        n = idx[(rec["src"], rec["nid"])]
        op = n.get("struct_op") or "e"
        rows.append(dict(nid=rec["nid"], src=rec["src"], level=rec["level"],
                         tau=rec.get("tau"), budget=rec.get("budget"), struct_op=op,
                         sup=[tuple(f[op](x, y, t)) for (x, y, t) in n["cfg"]]))
    return rows


def alive_set(cls, rows):
    if cls == "trump5":
        return {r["nid"] for r in rows}, "A107 input (A60 paused; no re-solve ledger since)"
    a = {e["nid"] for e in json.load(open(os.path.join(L.A151R, "alive_s02.json"),
                                          encoding="utf-8"))["s02_alive"]}
    return a, "A151 results/alive_s02.json (the population still alive after the night)"


def boxes_of(rec, names=("f1", "f2", "f3")):
    """[(name, x0, x1, y0, y1, t0, t1, anchor_t)] of one certified record's tilted boxes."""
    out = []
    for b in rec["boxes"]:
        if b["kind"] != "free" or b["name"] not in names:
            continue
        at = math.radians(b["anchor"][2])
        out.append((b["name"], b["x"][0], b["x"][1], b["y"][0], b["y"][1],
                    math.radians(b["theta_deg"][0]), math.radians(b["theta_deg"][1]), at))
    return out


def inside(boxes, sup):
    """Is there an injection of `boxes` into distinct support squares, every coordinate inside?"""
    if len(boxes) > len(sup):
        return False, -1e9, None
    best = None
    for perm in itertools.permutations(range(len(sup)), len(boxes)):
        worst = None
        for b, j in zip(boxes, perm):
            x, y, t = sup[j]
            _, x0, x1, y0, y1, t0, t1, at = b
            sx = min(x - x0, x1 - x)
            sy = min(y - y0, y1 - y)
            dev = math.degrees(t) % 90.0 - math.degrees(at) % 90.0
            dev = (dev + 45.0) % 90.0 - 45.0
            st = min(dev - math.degrees(t0 - at), math.degrees(t1 - at) - dev)
            w = min(sx, sy, st)
            worst = w if worst is None else min(worst, w)
        if best is None or worst > best[0]:
            best = (worst, perm)
    return (best[0] >= 0.0), best[0], best[1]


def score(label, sets, rows, alive):
    if not sets:
        print("%-46s no certified box sets" % label)
        return dict(label=label, n_sets=0, inside=0, inside_alive=0, rows=[])
    out, hits = [], []
    for r in rows:
        ok, sl, which, allhit = False, -1e9, None, []
        for k, (eid, bx) in enumerate(sets):
            o, s, _ = inside(bx, r["sup"])
            if s > sl:
                sl, which = s, eid
            if o:
                ok = True
                allhit.append(eid)
        out.append(dict(nid=r["nid"], level=r["level"], inside=bool(ok), slack=round(sl, 5),
                        best=which, in_sets=allhit, n_sets_hit=len(allhit),
                        alive=bool(r["nid"] in alive)))
        if ok:
            hits.append(r["nid"])
    n_alive = sum(1 for r in out if r["inside"] and r["alive"])
    print("%-46s %3d set(s): %3d of %3d inside, %3d ALIVE" % (label, len(sets), len(hits),
                                                              len(out), n_alive))
    return dict(label=label, n_sets=len(sets), n_class=len(out), inside=len(hits),
                inside_alive=n_alive, inside_ids=sorted(hits), rows=out)


def certified(path, family=None):
    """[(id, boxes)] for the certified records of this attempt's tree run."""
    sets = []
    if not os.path.exists(path):
        return sets
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if not r.get("dead"):
            continue
        if family and r.get("family") != family:
            continue
        sets.append((r.get("key", r["id"]), boxes_of(r)))
    return sets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--tree", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--control", action="store_true",
                    help="use A160's own certified verdicts (from N_boxes160.json) instead")
    a = ap.parse_args()
    tree = a.tree or os.path.join(L.RES, "tree_%s.jsonl" % a.cls)
    out = a.out or os.path.join(L.RES, "consumer163_%s%s.json" % (a.cls,
                                                                  "_control" if a.control else ""))
    rows = supports(a.cls)
    alive, prov = alive_set(a.cls, rows)
    print("frame %-7s %d S02 nodes, %d of them ALIVE (%s)"
          % (a.cls, len(rows), sum(1 for r in rows if r["nid"] in alive), prov))

    if a.control:
        sets = [(e["id"], boxes_of(dict(boxes=[dict(name=b["name"], kind="free", x=b["cx"],
                                                    y=b["cy"], theta_deg=b["theta_deg"],
                                                    anchor=b["anchor"]) for b in e["boxes"]])))
                for e in L.entries()]
        fams = {"chain": [s for s, e in zip(sets, L.entries()) if L.family(e["id"]) == "chain"],
                "slice": [s for s, e in zip(sets, L.entries()) if L.family(e["id"]) == "slice"]}
    else:
        sets = certified(tree)
        fams = {f: certified(tree, f) for f in ("chain", "slice")}

    res = [score("SLICES only (union)", fams.get("slice", []), rows, alive),
           score("CHAIN only (union)", fams.get("chain", []), rows, alive),
           score("UNION of every certified box set", sets, rows, alive)]

    # the PI's node, first
    y = dict(nid=None)
    for r in res[-1]["rows"]:
        if r["nid"].endswith("Y1110"):
            y = r
    print("Y1110: %s" % json.dumps({k: v for k, v in y.items() if k != "in_sets"})[:300])
    if y.get("in_sets"):
        print("Y1110 is inside %d certified box set(s); first: %s"
              % (len(y["in_sets"]), y["in_sets"][:4]))

    # which box sets are worth an exact t-certificate: a greedy cover of the in-N ALIVE nodes
    need = {r["nid"]: set(r["in_sets"]) for r in res[-1]["rows"] if r["inside"] and r["alive"]}
    cover, left = [], dict(need)
    while left:
        cnt = {}
        for nid, ss in left.items():
            for s in ss:
                cnt[s] = cnt.get(s, 0) + 1
        if not cnt:
            break
        # prefer the set that serves Y1110 first, then the largest gain
        best = max(cnt, key=lambda s: (1 if (y.get("in_sets") and s in y["in_sets"]
                                             and not cover) else 0, cnt[s], s))
        served = [nid for nid, ss in left.items() if best in ss]
        cover.append(dict(set=best, new_alive=len(served), nodes=sorted(served)))
        for nid in served:
            left.pop(nid)
    print("greedy cover of the %d in-N ALIVE nodes: %d box set(s)" % (len(need), len(cover)))
    for c in cover:
        print("   %-40s +%d alive" % (c["set"], c["new_alive"]))
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), cls=a.cls, control=bool(a.control),
                   tree=os.path.basename(tree), n_nodes=len(rows), alive_provenance=prov,
                   n_alive=sum(1 for r in rows if r["nid"] in alive), y1110=y,
                   greedy_cover=cover, entries=res),
              open(out, "w", encoding="utf-8"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
