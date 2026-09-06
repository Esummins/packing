"""atlas85.py -- A85 JOB 2: A37 atlas containment tool.

Loads attempts/A37-cp-atlas/results/atlas_final.json (37 entries) plus the referenced
certificate files, and answers: does a given 11-square packing lie inside some entry's
certified box?

Coordinate convention of z_center (determined from the cert files and
A37-cp-atlas/code/a37_check.py -- see results/atlas85_convention.md):

    z = [cx_0, cy_0, th_0, cx_1, cy_1, th_1, ..., cx_10, cy_10, th_10, s]   (34 entries)

    * squares in triples (A22 order), NOT pack11's blocked layout;
    * th is the TILT ANGLE IN RADIANS (a37_check.py feeds it straight into iv.cos/iv.sin);
      it is NOT t = tan(theta/2) and it is NOT reduced mod pi/2 (values 0 and pi/2 both occur);
    * centres are absolute coordinates in the CP's OWN container frame [0, s]^2, with s
      itself the 34th coordinate of the box -- nothing is normalised or rescaled;
    * there is NO D4 normalisation and no canonical square ordering: each entry sits at
      whichever D4 image / labelling the A04 catalogue (or the A37 drain probe) produced.
      E.g. entry 0's z_center is the TRANSPOSE (reflection in y = x) of
      A03-upper-reconstruct/trump11_float.json, with theta -> pi/2 - theta.

    Claim per entry: every interior-disjoint 11-square packing z with
    ||z - z_center||_inf <= h_certified has s(z) >= V (>= s0 = 969271/250000).

Soundness of the two normalisations we apply before measuring the distance:
    (i) D4 image: the image of a feasible packing under a symmetry of the container is a
        feasible packing with the same side;
    (ii) square relabelling and theta -> theta + k*pi/2: these change the coordinate vector
        but not the set of squares, hence not feasibility and not s.
We do NOT translate the configuration (the container frame is fixed by the walls).

Public API:
    load_atlas()                     -> list of Entry
    in_atlas(placements, s, atlas)   -> list of dicts (family_id, margin, ...), best first
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
from fractions import Fraction

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ATTEMPTS = os.path.join(REPO, "attempts")
ATLAS_JSON = os.path.join(ATTEMPTS, "A37-cp-atlas", "results", "atlas_final.json")

S0 = 969271.0 / 250000.0          # 3.877084, the incumbent rational bound
S_HAT = 3.877083590022814         # Trump's side
NSQ = 11
HALFPI = np.pi / 2.0


# ----------------------------------------------------------------- atlas loading
class Entry(object):
    __slots__ = ("family_id", "s_min_float", "cls", "h", "h_str", "cert_path",
                 "z_center", "P", "T", "s_center", "V")

    def __repr__(self):
        return "<Entry %s s=%.6f h=%.3e>" % (self.family_id, self.s_min_float, self.h)


def _z_to_pt(z):
    """34-vector -> (P (11,2) centres, T (11,) thetas rad, s)."""
    z = np.asarray(z, dtype=float)
    P = np.empty((NSQ, 2))
    T = np.empty(NSQ)
    for i in range(NSQ):
        P[i, 0] = z[3 * i]
        P[i, 1] = z[3 * i + 1]
        T[i] = z[3 * i + 2]
    return P, T, float(z[33])


def load_atlas(path=ATLAS_JSON):
    doc = json.load(open(path))
    out = []
    for rec in doc["entries"]:
        e = Entry()
        e.family_id = rec["family_id"]
        e.s_min_float = float(rec["s_min_float"])
        e.cls = rec["class"]
        e.h_str = rec["h_certified"]
        e.h = float(Fraction(e.h_str))
        e.cert_path = rec["cert_path"]
        cert = json.load(open(os.path.join(ATTEMPTS, rec["cert_path"])))
        z = [float(Fraction(t)) for t in cert["z_center"]]
        assert len(z) == 34, (e.family_id, len(z))
        e.z_center = np.array(z)
        e.P, e.T, e.s_center = _z_to_pt(z)
        v = rec.get("value", {})
        e.V = v.get("V", v.get("v_lo"))
        out.append(e)
    return out


# ----------------------------------------------------------------- D4 images
D4_NAMES = ["e", "r90", "r180", "r270", "mx", "my", "diag", "anti"]


def d4_image(P, T, s, g):
    """Act on a packing in [0,s]^2 by the g-th element of D4.  Returns (P', T')."""
    x, y = P[:, 0].copy(), P[:, 1].copy()
    if g == 0:      # identity
        X, Y, Th = x, y, T.copy()
    elif g == 1:    # rotate +90:  (x,y) -> (s-y, x)
        X, Y, Th = s - y, x, T + HALFPI
    elif g == 2:    # rotate 180
        X, Y, Th = s - x, s - y, T.copy()
    elif g == 3:    # rotate -90
        X, Y, Th = y, s - x, T + HALFPI
    elif g == 4:    # mirror x
        X, Y, Th = s - x, y, -T
    elif g == 5:    # mirror y
        X, Y, Th = x, s - y, -T
    elif g == 6:    # transpose (reflect in y=x)
        X, Y, Th = y, x, HALFPI - T
    elif g == 7:    # anti-transpose
        X, Y, Th = s - y, s - x, HALFPI - T
    else:
        raise ValueError(g)
    return np.stack([X, Y], axis=1), Th


def theta_delta(a, b):
    """Signed difference a-b reduced into (-pi/4, pi/4] -- the square is invariant
    under theta -> theta + pi/2, so this is the smallest achievable |dtheta|."""
    d = np.mod(a - b + np.pi / 4.0, HALFPI) - np.pi / 4.0
    return d


# ----------------------------------------------------------------- bottleneck assignment
def _perfect_matching_exists(mask):
    n = mask.shape[0]
    rows, cols = np.nonzero(mask)
    if len(rows) == 0:
        return False
    g = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=mask.shape)
    m = maximum_bipartite_matching(g, perm_type="column")
    return not np.any(m == -1) and len(m) == n


def bottleneck_assign(C):
    """Exact bottleneck (minimax) assignment.  Returns (value, perm) with
    perm[i] = column matched to row i, minimising max_i C[i, perm[i]]."""
    vals = np.unique(C)
    lo, hi = 0, len(vals) - 1
    if not _perfect_matching_exists(C <= vals[hi]):
        return np.inf, None
    while lo < hi:
        mid = (lo + hi) // 2
        if _perfect_matching_exists(C <= vals[mid]):
            hi = mid
        else:
            lo = mid + 1
    t = vals[lo]
    mask = C <= t
    rows, cols = np.nonzero(mask)
    g = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=mask.shape)
    m = maximum_bipartite_matching(g, perm_type="column")
    return float(t), m


def align_linf(P, T, s, Pc, Tc, sc, include_s=True):
    """Smallest L_inf distance from (P,T,s) to (Pc,Tc,sc) over the 8 D4 images and all
    square relabellings.  Returns (dist, g_index, perm)."""
    best = (np.inf, None, None)
    ds = abs(s - sc) if include_s else 0.0
    for g in range(8):
        Pg, Tg = d4_image(P, T, s, g)
        dx = np.abs(Pg[:, None, 0] - Pc[None, :, 0])
        dy = np.abs(Pg[:, None, 1] - Pc[None, :, 1])
        dt = np.abs(theta_delta(Tg[:, None], Tc[None, :]))
        C = np.maximum(np.maximum(dx, dy), dt)
        val, perm = bottleneck_assign(C)
        val = max(val, ds)
        if val < best[0]:
            best = (val, g, perm)
    return best


# ----------------------------------------------------------------- public entry point
def in_atlas(placements, s, atlas=None, only_positive=False):
    """placements: (11,3) array of (cx, cy, theta_rad) in the container [0,s]^2.
    Returns a list of dicts, one per atlas entry, sorted by margin descending:
        family_id, class, h_certified, dist_linf, margin = h - dist, d4, perm, V.
    margin >= 0  <=>  the packing is certified by that entry."""
    if atlas is None:
        atlas = load_atlas()
    A = np.asarray(placements, dtype=float)
    P, T = A[:, :2], A[:, 2]
    out = []
    for e in atlas:
        d, g, perm = align_linf(P, T, s, e.P, e.T, e.s_center)
        rec = dict(family_id=e.family_id, cls=e.cls, h_certified=e.h_str,
                   h=e.h, dist_linf=d, margin=e.h - d,
                   d4=D4_NAMES[g] if g is not None else None,
                   perm=(None if perm is None else [int(v) for v in perm]),
                   V=e.V, s_center=e.s_center)
        if only_positive and rec["margin"] < 0:
            continue
        out.append(rec)
    out.sort(key=lambda r: -r["margin"])
    return out


def trump_placements():
    d = json.load(open(os.path.join(ATTEMPTS, "A03-upper-reconstruct", "trump11_float.json")))
    return np.array(d["X"], dtype=float), float(d["s"])


# ----------------------------------------------------------------- self-test
def selftest():
    atlas = load_atlas()
    res = dict(atlas_json=os.path.relpath(ATLAS_JSON, REPO), n_entries=len(atlas), tests=[])

    X, s = trump_placements()
    r = in_atlas(X, s, atlas)
    top = r[0]
    hit0 = [q for q in r if q["family_id"] == 0][0]
    res["tests"].append(dict(
        name="trump_placements_land_in_family_0",
        best_family=top["family_id"], best_margin=top["margin"],
        family0_dist_linf=hit0["dist_linf"], family0_margin=hit0["margin"],
        family0_h=hit0["h"], family0_d4=hit0["d4"],
        n_entries_containing=sum(1 for q in r if q["margin"] >= 0),
        verdict="PASS" if (top["family_id"] == 0 and hit0["margin"] > 0
                           and hit0["dist_linf"] < 1e-9) else "FAIL"))

    for e in atlas:
        if not (str(e.family_id).startswith("A37-NEW") or str(e.family_id).startswith("A51-NEW")):
            continue
        pl = np.concatenate([e.P, e.T[:, None]], axis=1)
        r = in_atlas(pl, e.s_center, atlas)
        own = [q for q in r if q["family_id"] == e.family_id][0]
        res["tests"].append(dict(
            name="center_of_%s_lands_in_itself" % e.family_id,
            best_family=r[0]["family_id"], best_margin=r[0]["margin"],
            own_dist_linf=own["dist_linf"], own_margin=own["margin"], own_h=own["h"],
            n_entries_containing=sum(1 for q in r if q["margin"] >= 0),
            verdict="PASS" if (own["dist_linf"] < 1e-12
                               and abs(own["margin"] - own["h"]) < 1e-12) else "FAIL"))

    # every entry centre must land in its own box with margin = h
    bad = []
    for e in atlas:
        pl = np.concatenate([e.P, e.T[:, None]], axis=1)
        d, g, _ = align_linf(e.P, e.T, e.s_center, e.P, e.T, e.s_center)
        if d > 1e-12:
            bad.append(dict(family_id=e.family_id, dist=d))
    res["tests"].append(dict(name="all_37_centres_selfmatch_at_distance_0",
                             n_bad=len(bad), bad=bad,
                             verdict="PASS" if not bad else "FAIL"))
    res["all_pass"] = all(t["verdict"] == "PASS" for t in res["tests"])
    return res


if __name__ == "__main__":
    out = selftest()
    dest = os.path.join(os.path.dirname(__file__), "..", "results", "atlas85_selftest.json")
    dest = os.path.abspath(dest)
    json.dump(out, open(dest, "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("written", dest)
    sys.exit(0 if out["all_pass"] else 1)
