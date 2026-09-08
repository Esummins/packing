"""A140 -- the twelve converged-alive k0_00 cells (A115 T6 `0d4c79fd`), and the wider open k0 pool.

READ-ONLY on every campaign.  The authoritative record of a converged-alive cell is A115's own LP
record `attempts/A115-k0-corner-rows/results/nodes/<nid>.t{4,5}.lp.json` (tau = budget exactly,
minmass 1.000, converged True) -- NOT the A38/A99 record the cell was first seen in, whose LP had
not converged.  A107's gallery was built from the latter, which is why some cells have a K-shadow
under an alias whose support differs from the converged one.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A115 = os.path.join(ROOT, "attempts", "A115-k0-corner-rows")
A118 = os.path.join(ROOT, "attempts", "A118-lane-count")
A107 = os.path.join(ROOT, "attempts", "A107-shadow-gallery")
A128 = os.path.join(ROOT, "attempts", "A128-coupled-moves")

S0 = 969271.0 / 250000.0
SHAT = 3.877083590022814

# cell -> (level, source of the cell id, A115 record file, A118 lane key, A107 alias)
CELLS = [
    ("l1_071", 1, "A38 l1 idx 71", "l1_071_plain_warm.t4.lp.json",
     "A99/k0_00/l1_071_plain_warm", "l1_071_plain_warm"),
    ("l1_104", 1, "A38 l1 idx 104", "l1_104_plain_warm.t4.lp.json",
     "A99/k0_00/l1_104_plain_warm", "l1_104_plain_warm"),
    ("l1_124", 1, "A38 l1 idx 124", "node_124.t5.lp.json", None, None),
    ("l1_148", 1, "A38 l1 idx 148", "node_148.t5.lp.json",
     "A99/k0_00/l1_148_plain_warm", "l1_148_plain_warm"),
    ("l1_153", 1, "A38 l1 idx 153 (Trump image)", "node_153.t5.lp.json", None, None),
    ("l1_158", 1, "A38 l1 idx 158", "node_158.t5.lp.json", None, None),
    ("l1_159", 1, "A38 l1 idx 159", "node_159.t5.lp.json",
     "A99/k0_00/l1_159_plain_warm", "l1_159_plain_warm"),
    ("l2_p114_001", 2, "A38 l2", "l2_p114_001.t5.lp.json",
     "A38/l2_nodes/l2_p114_001", "l2_p114_001"),
    ("l2_p65_101", 2, "A38 l2", "l2_p65_101.t5.lp.json",
     "A38/l2_nodes/l2_p65_101", "l2_p65_101"),
    ("l2_p65_111", 2, "A38 l2", "l2_p65_111.t5.lp.json",
     "A38/l2_nodes/l2_p65_111", "l2_p65_111"),
    ("l2_p74_001", 2, "A38 l2", "l2_p74_001.t5.lp.json",
     "A38/l2_nodes/l2_p74_001", "l2_p74_001"),
    ("s3_far_BL389484_TR018470", 4, "A85 k0 route", "s3_far_BL389484_TR018470.t4.lp.json",
     "A85/k0_00/s3_far_BL389484_TR018470", "s3_far_BL389484_TR018470"),
]

NODES = os.path.join(A115, "results", "nodes")


def load_cell(cell):
    """(meta, record) for one of the twelve."""
    for (name, lvl, src, fn, lanekey, a107alias) in CELLS:
        if name != cell:
            continue
        p = os.path.join(NODES, fn)
        d = json.load(open(p, encoding="utf-8"))
        return dict(cell=name, level=lvl, src=src, record=os.path.relpath(p, ROOT),
                    lane_key=lanekey, a107_alias=a107alias), d
    raise KeyError(cell)


def all_cells():
    return [load_cell(c[0]) for c in CELLS]


# --------------------------------------------------------------------- the wider open pool
def open_pool():
    """Every k0 cell A115 left OPEN: its last run did not certify it dead.  Returns
    [(nid, verdict, path-to-LP-record)] with the best LP record A115 stored for it."""
    last = {}
    for f in ("t4_runs.jsonl", "t5_runs.jsonl"):
        p = os.path.join(A115, "results", f)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            last[r["nid"]] = r
    out = []
    for nid, r in sorted(last.items()):
        if str(r.get("verdict", "")).upper().startswith("CERTIFIED"):
            continue
        lp = None
        for pat in (f"{nid}.t5.lp.json", f"{nid}.t4.lp.json"):
            q = os.path.join(NODES, pat)
            if os.path.exists(q):
                lp = q
                break
        if lp is None:
            g = sorted(glob.glob(os.path.join(NODES, nid + "*.lp.json")))
            lp = g[-1] if g else None
        if lp is None:
            continue
        out.append((nid, r.get("verdict"), lp, r))
    return out


def a118_lane(key):
    """A118's per-cell lane verdicts for one node key, or None."""
    if not key:
        return None
    for f in sorted(glob.glob(os.path.join(A118, "results", "lane_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            if r.get("key") == key:
                return r
    return None


def a107_shadow(alias):
    """(shadow id, entry) for a node alias in A107's k0 gallery, or (None, None)."""
    p = os.path.join(A107, "results", "shadow_nodes_k0.json")
    d = json.load(open(p, encoding="utf-8"))
    for sid, rows in d.items():
        for r in rows:
            if r["nid"] == alias:
                return sid, r
    return None, None


def a107_shadow_geom(sid):
    """The minimised shadow (slots, free, s) for a shadow id, or None."""
    p = os.path.join(A107, "results", "shadows_k0.json")
    for sh in json.load(open(p, encoding="utf-8")):
        if sh["id"] == sid:
            return sh
    return None


def a128_nearpack(cell):
    p = os.path.join(A128, "results", "nearpack128.json")
    d = json.load(open(p, encoding="utf-8"))
    return d.get(cell)
