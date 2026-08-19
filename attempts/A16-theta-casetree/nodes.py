"""A16 — case-tree node hypotheses (A14 semantics, via A14's caselp.Hyp) and LP-support seeds for the placement grid.

A node H = (core boxes, NO-families, budget = 11 - #cores).  On a finite placement set P the node's ADMISSIBLE set is
{p in P : hyp.ok(p)}  (A14's row filter: drop placements provably inside a NO-family (margins EPS_ZONE/EPS_TH) or
penetrating a core by SAT depth > EPS_CORE).  The node relaxations (LP nu*, theta', alpha) live on the induced subgraph.
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
A14 = os.path.join(ROOT, "attempts", "A14-close-tree-384")
A12 = os.path.join(ROOT, "attempts", "A12-region-rank-pilot")
A07 = os.path.join(ROOT, "attempts", "A07-lp-dual")
sys.path.insert(0, A14)
import caselp
from caselp import Box, NoFam, Hyp


def corner_exact_boxes(s, which=(0, 1, 2, 3)):
    """degenerate boxes = corner squares fixed exactly at (0.5,0.5,0), (s-.5,.5,0), (s-.5,s-.5,0), (.5,s-.5,0)."""
    c = [(0.5, 0.5), (s - 0.5, 0.5), (s - 0.5, s - 0.5), (0.5, s - 0.5)]
    return [Box(c[k][0], c[k][0], c[k][1], c[k][1], 0.0, 0.0) for k in which]


def corner_zones(s):
    """the four corner zones [0.5,1.1]^2 and images (A14 node 1: NO all corners)"""
    z = [(0.5, 1.1, 0.5, 1.1), (s - 1.1, s - 0.5, 0.5, 1.1), (s - 1.1, s - 0.5, s - 1.1, s - 0.5), (0.5, 1.1, s - 1.1, s - 0.5)]
    return [NoFam(*r, [(0.0, 90.0)]) for r in z]


def side_zones(s, which=(0, 1, 2, 3)):
    """side zones: 0 = left [0.5,1.1]x[1.1,s-1.1], 1 = bottom, 2 = right, 3 = top (A14's hyp_c4_noside0 / hyp_nosides)"""
    z = [(0.5, 1.1, 1.1, s - 1.1), (1.1, s - 1.1, 0.5, 1.1), (s - 1.1, s - 0.5, 1.1, s - 1.1), (1.1, s - 1.1, s - 1.1, s - 0.5)]
    return [NoFam(*z[k], [(0.0, 90.0)]) for k in which]


def make_node(name, s):
    """returns (hyp, budget, description, seed_files) for the node catalogue"""
    NoFam.s_hi = s - 0.5
    tag384 = lambda *fs: [os.path.join(A14, "results", f) for f in fs]
    l1 = lambda k: os.path.join(A14, "results", "l1_385", f"node_{k}.json")
    if name == "N0":
        return Hyp(), 11, "root", ([] if abs(s - 3.85) > 1e-9 else [l1(0)])
    if name == "N1":
        return Hyp(corner_exact_boxes(s, (0,))), 10, "one corner square fixed exactly (core = [0,1]^2)", tag384("x_corner0_exact_state.json")
    if name == "N2":
        return Hyp(corner_exact_boxes(s)), 7, "four corner squares fixed exactly", tag384("buggy_oracle/x_corners4_exact.json", "x_corners4_exact_state.json")
    if name in ("N3a", "N3b", "N3c"):
        th = {"N3a": (0.0, 30.0), "N3b": (30.0, 60.0), "N3c": (60.0, 90.0)}[name]
        k = {"N3a": 2, "N3b": 3, "N3c": 4}[name]
        seeds = tag384(f"n{k}.json") + ([f"{A14}/results/n2_v3.json"] if k == 2 else []) if abs(s - 3.84) < 1e-9 else [l1(k)]
        return Hyp([Box(0.5, 0.8, 0.5, 0.8, th[0], th[1])]), 10, f"YES corner0 box [0.5,0.8]^2 x [{th[0]:.0f},{th[1]:.0f}] deg", seeds
    if name in ("N3d", "N3e"):
        # A14 off-corner boxes: node 6 = [0.5,0.8]x[0.8,1.1]x[30,60] (LP 10.04 at 3e-3), node 5 = ...x[0,30] (LP 9.87/10.00)
        th = {"N3d": (30.0, 60.0), "N3e": (0.0, 30.0)}[name]
        k = {"N3d": 6, "N3e": 5}[name]
        seeds = tag384(f"n{k}_e3.json") + (tag384("n5.json") if k == 5 else []) if abs(s - 3.84) < 1e-9 else [l1(k)]
        return Hyp([Box(0.5, 0.8, 0.8, 1.1, th[0], th[1])]), 10, f"YES corner0 off-corner box [0.5,0.8]x[0.8,1.1] x [{th[0]:.0f},{th[1]:.0f}] deg (A14 node {k})", seeds
    if name == "N4":
        return Hyp(corner_exact_boxes(s), side_zones(s, (0,))), 7, "four corners fixed + NO side0 zone", tag384("x_c4_noside0.json")
    if name == "N4b":
        return Hyp(corner_exact_boxes(s), side_zones(s)), 7, "four corners fixed + NO all four side zones", tag384("x_c4_nosides.json")
    if name == "N5":
        seeds = tag384("n1_e3.json") if abs(s - 3.84) < 1e-9 else [l1(1)]
        return Hyp([], corner_zones(s)), 11, "NO all four corner zones", seeds
    if name == "N5s":
        return Hyp([], side_zones(s)), 11, "NO all four side zones (root)", tag384("x_nosides.json")
    raise ValueError(name)


def load_seed_packing(path, ymin=0.01):
    """fractional packing (cx, cy, theta_rad, y) from an A14 result json (key 'packing') or a state json (rows + y)."""
    d = json.load(open(path))
    out = []
    if "packing" in d:
        for p in d["packing"]:
            if p["y"] >= ymin:
                out.append((p["cx"], p["cy"], p["theta"], p["y"]))
    elif "rows" in d and "y" in d:
        R = np.array(d["rows"], float); y = np.array(d["y"], float)
        n = min(len(R), len(y))
        for i in range(n):
            if y[i] >= ymin:
                out.append((R[i, 0], R[i, 1], R[i, 2], y[i]))
    return out


def stretch_to(pk, s_from, s_to):
    """map a packing from container s_from to s_to: centres affinely stretched about the container centre
    (keeps wall contacts approximately; only used as grid seeds)."""
    out = []
    for cx, cy, th, y in pk:
        f = (s_to - 1.0) / (s_from - 1.0)          # admissible centre square scales from s_from-1 to s_to-1 (theta = 0)
        x = 0.5 * s_to + (cx - 0.5 * s_from) * f
        z = 0.5 * s_to + (cy - 0.5 * s_from) * f
        out.append((x, z, th, y))
    return out


def a15_extras(s, a07_ymin=0.05, mode="all"):
    """A15's injected structures: A12 1/4-structure supports (3.85/3.86/3.87) + A07 3.84 dual support.
    mode = "s": only the A12 structure nearest to s (3.85 for s <= 3.855, else 3.86/3.87)."""
    out = []
    if mode == "s":
        ss = "3.85" if s <= 3.855 else ("3.86" if s <= 3.865 else "3.87")
        d = json.load(open(os.path.join(A12, "results", f"analysis_s{ss}.json")))
        return [(cx, cy, th, w) for cx, cy, th, w in d["images"]]
    for ss in ("3.85", "3.86", "3.87"):
        d = json.load(open(os.path.join(A12, "results", f"analysis_s{ss}.json")))
        for cx, cy, th, w in d["images"]:
            out.append((cx, cy, th, w))
    d = json.load(open(os.path.join(A07, "results", "v2_s3.84.json")))
    for r in d["packing"]:
        if r["y"] >= a07_ymin:
            out.append((r["cx"], r["cy"], r["theta"], r["y"]))
    return out


def clamp_admissible(pk, s):
    res = []
    for cx, cy, th, y in pk:
        th = th % (math.pi / 2)
        w = math.cos(th) + math.sin(th)
        cx = min(max(cx, w / 2), s - w / 2); cy = min(max(cy, w / 2), s - w / 2)
        res.append((cx, cy, th, y))
    return res


def node_seeds(name, s, seed_files, ymin=0.01, with_a15=True, a15_mode="all"):
    """seed placements (cx, cy, theta) for the grid: the node's own LP fractional packing support (A14 result at 3.84,
    stretched if s != 3.84 and no 3.85 result exists) + A15's injected root structures."""
    pk = []
    for f in seed_files:
        if not os.path.exists(f):
            print(f"  [seeds] missing {f}")
            continue
        d = json.load(open(f))
        s_from = float(d.get("s", 3.84))
        p = load_seed_packing(f, ymin)
        if abs(s_from - s) > 1e-9:
            p = stretch_to(p, s_from, s)
        pk += p
    if with_a15:
        pk += a15_extras(s, mode=a15_mode)
    pk = clamp_admissible(pk, s)
    return [(cx, cy, th) for cx, cy, th, y in pk]


def node_init_points(seed_files, s):
    """atoms of the node's A14 LP measure (atoms_all = [x, y, w]) as initial points for the point LP (stretched to s)."""
    pts = []
    for f in seed_files:
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        s_from = float(d.get("s", 3.84))
        if "atoms_all" in d:
            A = np.array([[a[0], a[1]] for a in d["atoms_all"]], float).reshape(-1, 2)
        elif "orbits" in d and "w" in d:
            w = np.array(d["w"]); O = np.array(d["orbits"], float)
            n = min(len(w), len(O))
            A = O[:n][w[:n] > 1e-10].reshape(-1, 2) if O.ndim == 2 else np.zeros((0, 2))
        else:
            continue
        if abs(s_from - s) > 1e-9:
            f_ = (s - 1.0) / (s_from - 1.0)
            A = 0.5 * s + (A - 0.5 * s_from) * f_
        pts.append(A)
    return np.vstack(pts) if pts else np.zeros((0, 2))


def admissible_mask(hyp, P):
    """A14 row filter on a placement array P (N,3) (theta radians): True = kept (not provably exempt)."""
    P = np.asarray(P, float)
    keep = np.ones(len(P), dtype=bool)
    if not hyp.boxes and not hyp.nofams:
        return keep
    ths = np.unique(np.round(P[:, 2], 12))
    for th in ths:
        m = np.abs(P[:, 2] - th) < 1e-11
        keep[m] = hyp.ok_many(P[m, :2], float(th))
    return keep


if __name__ == "__main__":
    for s in (3.84, 3.85):
        for nm in ("N0", "N1", "N2", "N3a", "N3b", "N3c", "N4", "N5"):
            hyp, budget, desc, seeds = make_node(nm, s)
            sd = node_seeds(nm, s, seeds, with_a15=False)
            print(s, nm, budget, desc, "| seeds", len(sd), "| hyp:", hyp.describe()[:100])
