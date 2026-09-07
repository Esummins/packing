"""A118: build the read-only corpus of nodes/boxes to run LANE-COUNT over.

READ-ONLY on every campaign: this module only reads json/jsonl under attempts/*/results.

A record is  dict(src, nid, path, cls, level, side, budget, alive, cert, pins, cond)
where `pins` is the list of pin cores (as lanelib.Sq) and `cond` is the list of conditioned
parameter boxes (A57 Box format dicts) -- the hypothesis of the node.
"""
import glob
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
S0 = 969271.0 / 250000.0

# ---------------------------------------------------------------- classes
# pin slots and USABLE completable slots.  A slot is usable iff its extension class is certified
# dead on a window containing the node's sides.  Status read 2026-09-06 from
# attempts/A56-sparametric/results/scoreboard.json (A56 + A61 + A114): every extension below is
# FULL [191/50, 969271/250000].
CLASSES = {
    "k5_11": dict(
        pins=[(0.5, 0.5), (0.5, 1.5), (0.5, S0 - 0.5), (1.5, 0.5), (S0 - 0.5, 0.5)],
        usable={"BL(1,1)": "k6_18", "BR(0,1)": "k6_20", "TL(1,0)": "k6_20", "TR(0,0)": "k6_23"},
    ),
    "k5_16": dict(
        pins=[(0.5, 0.5), (0.5, 1.5), (0.5, S0 - 0.5), (S0 - 0.5, 0.5), (S0 - 0.5, S0 - 0.5)],
        usable={"BL(1,0)": "k6_23", "BR(0,1)": "k6_29", "BR(1,0)": "k6_27",
                "TR(0,1)": "k6_30", "TR(1,0)": "k6_28", "TL(1,0)": "k6_27"},
    ),
    "trump5": dict(
        pins=[(0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (S0 - 0.5, 0.5), (S0 - 0.5, S0 - 0.5)],
        usable={"BL(0,2)": "k6_07", "BL(1,1)": "k6_19", "BR(0,1)": "k6_21",
                "TR(0,1)": "k6_22", "TR(1,0)": "k6_24", "TL(0,0)": "k6_23"},
    ),
    # k0_00 has no pins; the four corner cells, extension k1_00 (OPEN dependency, k0_route.md sec 3)
    "k0_00": dict(pins=[], usable={"BL(0,0)": "k1_00", "BR(0,0)": "k1_00",
                                   "TR(0,0)": "k1_00", "TL(0,0)": "k1_00"}),
}

PIN_DELTA = 1e-2


def _alive(d):
    """A107 extract.py's alive-at-LP test, byte-for-byte in spirit."""
    tau, bud = d.get("tau"), d.get("budget")
    at_budget = (tau is not None and bud is not None and float(tau) >= float(bud) - 1e-9)
    return (not d.get("dead", True)) or at_budget


def _split_hyp(d, cls):
    """Split hyp.boxes into (pin boxes, conditioned boxes) by matching the class pin slots."""
    pins = CLASSES[cls]["pins"]
    boxes = (d.get("hyp") or {}).get("boxes", [])
    pin_b, cond_b = [], []
    for b in boxes:
        cx, cy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
        hit = any(abs(cx - px) < 2e-2 and abs(cy - py) < 2e-2 for px, py in pins)
        near_axis = (b.get("th0", 0.0) <= 1e-6 and b.get("th1", 0.0) <= 1e-6)
        (pin_b if (hit and near_axis) else cond_b).append(b)
    return pin_b, cond_b


def _level_from_nid(nid):
    tail = nid.split("_interior_", 1)[-1]
    n = len([t for t in tail.split("_") if t and t[0] in "YD" and t[1:].isdigit()])
    return max(n, 1)


def load_nodes():
    """Every node json of A57 (k5_11/k5_16), A60 (trump5) and the k0 campaigns."""
    out = []
    specs = [
        ("A57", "attempts/A57-shadow-trees/results/tree/*/*.json", None),
        ("A60", "attempts/A60-trump5-campaign/results/nodes/*.json", "trump5"),
        ("A85", "attempts/A85-k0-route/results/nodes/*/*.json", "k0_00"),
        ("A99", "attempts/A99-k0-tree-v2/results/nodes/*/*.json", "k0_00"),
        ("A38", "attempts/A38-root-power/results/l1_nodes/*.json", "k0_00"),
        ("A38", "attempts/A38-root-power/results/l2_nodes/*.json", "k0_00"),
        ("A38", "attempts/A38-root-power/results/l3_nodes/*.json", "k0_00"),
    ]
    for src, pat, fixed in specs:
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            nid = os.path.basename(p)[:-5]
            shard = os.path.basename(os.path.dirname(p))
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if "hyp" not in d:
                continue
            cls = fixed or ("k5_11" if nid.startswith("k5_11") else
                            "k5_16" if nid.startswith("k5_16") else None)
            if cls is None:
                continue
            pin_b, cond_b = _split_hyp(d, cls)
            if src == "A38":
                lvl = 1 if "l1_nodes" in p else (2 if "l2_nodes" in p else 3)
            elif cls == "k0_00":
                lvl = len(cond_b)
            else:
                lvl = _level_from_nid(nid)
            out.append(dict(src=src, nid=nid, shard=shard, path=os.path.relpath(p, ROOT).replace("\\", "/"),
                            cls=cls, level=lvl, side=float(d.get("s", S0)),
                            budget=d.get("budget"), tau=d.get("tau"),
                            alive=bool(_alive(d)), origin="node",
                            n_pin=len(pin_b), cond=cond_b))
    return out


def load_open_boxes(known_ids):
    """A57 tree rows (results/tree_*.jsonl) that have no node json: the hypothesis is the class
    pins plus this box and every ancestor box.  `known_ids` are ids already covered by a node."""
    rows = {}
    for f in glob.glob(os.path.join(ROOT, "attempts/A57-shadow-trees/results/tree_*.jsonl")):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if not r.get("box"):
                continue
            rows[r["id"]] = r
    out, missing = [], 0
    for rid, r in rows.items():
        cls = "k5_11" if rid.startswith("k5_11") else "k5_16" if rid.startswith("k5_16") else None
        if cls is None:
            continue
        chain, cur, ok = [], rid, True
        while cur:
            rr = rows.get(cur)
            if rr is None:
                ok = False
                break
            chain.append(rr["box"])
            cur = rr.get("parent")
        if not ok:
            missing += 1
            continue
        cert = str(r.get("cert") or "")
        out.append(dict(src="A57box", nid=rid, shard="jsonl", path="results/tree_*.jsonl",
                        cls=cls, level=len(chain), side=S0, budget=r.get("budget"),
                        tau=None, cert=cert,
                        logic_kill=cert.startswith("KILL-BY-LOGIC"),
                        certified=cert.startswith("PASS"),
                        alive=(not cert.startswith("KILL-BY-LOGIC")) and (not cert.startswith("PASS")),
                        origin="box", covered_by_node=(rid in known_ids),
                        n_pin=len(CLASSES[cls]["pins"]), cond=chain))
    return out, missing
