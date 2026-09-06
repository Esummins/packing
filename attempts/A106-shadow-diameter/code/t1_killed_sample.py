"""A106 — a CONTROL sample of KILLED level-2/3 nodes.

T3's certificate sensitivity ("how much box width does the verifier tolerate per unit of
slack") is only measurable if the same box-constrained minimisation is run on boxes the
certificate DID kill.  This adds a stratified sample of PASS / KILL-BY-LOGIC nodes at
levels 2-3 to the T1 table (same schema, status "killed_*"), copying their LP jsons.
"""
from __future__ import annotations
import json, os, glob, math, re, random, shutil, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
SNAP = os.path.join(BASE, "results", "snapshot")
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
NODES = os.path.join(BASE, "results", "nodes")


def level(nid):
    return len(re.findall(r"_D\d+", nid)) + 1


def main(n_per_cell=30):
    recs = {}
    for p in sorted(glob.glob(os.path.join(SNAP, "tree_*.jsonl"))):
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            recs[r["id"]] = r
    slots = json.load(open(os.path.join(SNAP, "name_to_slots.json")))
    buckets = collections.defaultdict(list)
    for nid, r in recs.items():
        L = level(nid)
        if L < 2 or L > 3 or not r.get("box"):
            continue
        c = r.get("cert", "") or ""
        if c == "PASS":
            st = "killed_cert"
        elif c.startswith("KILL-BY-LOGIC"):
            st = "killed_logic"
        else:
            continue
        cls = nid.split("_interior")[0]
        buckets[(cls, L, st)].append(nid)
    rng = random.Random(20260906)
    out = []
    for key, ids in sorted(buckets.items()):
        cls, L, st = key
        pick = sorted(ids) if len(ids) <= n_per_cell else rng.sample(sorted(ids), n_per_cell)
        for nid in pick:
            r = recs[nid]
            b = r["box"]
            wx = b["x1"] - b["x0"]; wy = b["y1"] - b["y0"]
            wth = math.radians(b["th1"] - b["th0"])
            src = None
            for p in glob.glob(os.path.join(A57, "results", "tree", "*", nid + ".json")):
                src = p; break
            if src:
                dst = os.path.join(NODES, nid + ".json")
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            out.append(dict(id=nid, cls=cls, level=L, parent=r.get("parent"), status=st,
                            cert=r.get("cert"), box=b, wx=wx, wy=wy, wth_deg=b["th1"] - b["th0"],
                            wth_rad=wth, dmax=max(wx, wy, wth),
                            deuc=math.sqrt(wx * wx + wy * wy + wth * wth),
                            dcentre=math.hypot(wx, wy), a=r.get("a"), tau=r.get("tau"),
                            eta=r.get("eta"), budget=r.get("budget"),
                            node_json=(nid + ".json") if src else None,
                            pins=slots[cls]))
        print(key, len(ids), "->", len(pick))
    json.dump(dict(rows=out), open(os.path.join(BASE, "results", "t1_killed.json"), "w"), indent=1)
    print("control rows:", len(out), " with LP json:", sum(1 for r in out if r["node_json"]))


if __name__ == "__main__":
    main()
