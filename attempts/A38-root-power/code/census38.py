#!/usr/bin/env python3
"""
A38 / W3 census -- survivor boxes vs the A37 critical-point atlas (design.md W3, T0 seam S6).

A survivor of the interior-first tree is a WITNESS box
    B = [x0,x1] x [y0,y1] x [th0,th1] deg      ("some square of P has (centre, theta) in B")
Nothing in the tree pins the other ten squares, so W3/K2 CANNOT fire at pilot depths.  What this
module measures instead is the CHARACTER of a survivor: how close its witness box is to the
placement set of a certified attractor, minimised over the D4 action on the container.

--------------------------------------------------------------------------------- the atlas
attempts/A37-cp-atlas/results/atlas_final.json, 36 entries.  Per entry:
    canonical_sig  = 11 placements [cx, cy, theta] with theta in RADIANS
                     (verified by the lead: pair separations vanish to machine precision
                      when the third coordinate is read as radians)
    s_min_float    = the entry's own container side  s_e  (the configuration lives in [0,s_e]^2)
    h_certified    = the box radius on which sigma >= V is certified (NOT used for the census
                     distance -- it is a full-configuration radius, not a per-placement one)

--------------------------------------------------------------------------------- the D4 action
D4 acts on the container [0,S]^2 (S = s0 throughout; see "scale caveat").  As maps of the plane:

    rotations   e   : (x, y) -> (x,     y    )
                r90 : (x, y) -> (S - y, x    )
                r180: (x, y) -> (S - x, S - y)
                r270: (x, y) -> (y,     S - x)
    reflections mx  : (x, y) -> (S - x, y    )
                my  : (x, y) -> (x,     S - y)
                dg  : (x, y) -> (y,     x    )        (about y = x)
                ad  : (x, y) -> (S - y, S - x)        (about y = S - x)

INDUCED THETA MAP.  A placement is the unit square Q(c, theta) = c + R(theta) [-1/2,1/2]^2, and
theta is only defined modulo 90 deg (a quarter turn maps the square to itself).  An element of
D4 with determinant +1 (the four rotations) conjugates R(theta) to R(theta + k*90), so

        theta  ->  theta            (mod 90)          for the 4 rotations,

and an element with determinant -1 (the four reflections) conjugates R(theta) to R(-theta + k*90):

        theta  ->  (-theta) mod 90  =  (90 - theta) mod 90     for the 4 reflections.

(The same rule caselp.d4_rect_images uses for NO-families.)  This is DERIVED, not assumed:
`selftest` checks it geometrically -- the image of the four corners of Q(c,theta) under g is
exactly the corner set of Q(g(c), theta_g(theta)), to 1e-12, for all 8 g and random (c,theta).

--------------------------------------------------------------------------------- the distances
For a witness box B and a placement (cx, cy, th_deg) the two distances are reported SEPARATELY
and never mixed:

    d_center = max(0, x0 - cx, cx - x1, y0 - cy, cy - y1)      Chebyshev, container units
    d_theta  = circular distance (period 90) from th_deg to the interval [th0, th1], degrees

A single scalar `score = max(d_center / TOL_C, d_theta / TOL_TH)` is used ONLY to order candidates
(score <= 1 <=> inside the inflated box); it is never reported as "the" distance.

Classification with TOL_C = 0.02, TOL_TH = 3 deg:
    trump_consistent  some D4 image of some family-0 (Trump) placement has score <= 1
    atlas_consistent  otherwise, some D4 image of some placement of an entry != family 0 does
    unexplained       neither

--------------------------------------------------------------------------------- scale caveat
Entries have s_e = s_min_float ranging over [3.8771, 3.9370] while the tree lives in [0, s0]^2,
s0 = 3.877084.  D4 is ALWAYS taken about the container centre s0/2 -- one group acting on one
container -- because otherwise the orbit-minimised distance is not invariant under moving the
witness box by a symmetry (selftest (c) catches exactly that: mixing S = s_e for the atlas with
S = s0 for the box gives orbit-closure defects up to 9.6).  Two readings of "the same
configuration placed in [0,s0]^2" are reported, both internally D4-consistent:
    mode "s0"     : placements as stored (corner-anchored, the drain-lemma normalisation)
    mode "scaled" : centres multiplied by s0/s_e (squares stay unit), i.e. the configuration
                    shrunk to fill [0,s0]^2
Classification uses "s0" by default (`--mode`); the other set is always reported alongside.
The distinction is immaterial for the Trump column (|s_e - s0| = 4.1e-7 << TOL_C, so the two
modes agree there to 4e-7) and matters only for the high-s families, whose labels are [NUM].

--------------------------------------------------------------------------------- CLI
    python census38.py --survivors survivors.json --out ../results/census_<tag>.json
    python census38.py --selftest

`survivors.json` is any of
    [[x0,x1,y0,y1,th0,th1], ...]
    [{"x0":..,"x1":..,"y0":..,"y1":..,"th0":..,"th1":..,"id":"optional"}, ...]
    {"boxes": [ ... as above ... ]}          (also accepts "survivors" / "nodes" keys, and
                                              records carrying the box under a "box" field)
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATLAS_PATH = os.path.join(REPO, "attempts", "A37-cp-atlas", "results", "atlas_final.json")

S0F = 3.877084                     # float(969271/250000)
TOL_C = 0.02                       # centre inflation for "consistent" (container units)
TOL_TH = 3.0                       # theta inflation for "consistent" (degrees)
PERIOD = 90.0                      # theta period of a square

TRUMP_IN_ZONE = [(1.272254, 2.424525), (1.959613, 1.688559), (2.623834, 2.436509)]
TRUMP_THETA_DEG = 49.8181          # = degrees(0.869489)


# ------------------------------------------------------------------------------- the D4 action
# (name, a, b, c, d, e, f, det) with  g(x,y) = (a*x + b*y + c*S,  d*x + e*y + f*S)
D4 = [
    ("e",    1,  0, 0,   0,  1, 0,  +1),
    ("r90",  0, -1, 1,   1,  0, 0,  +1),
    ("r180", -1, 0, 1,   0, -1, 1,  +1),
    ("r270", 0,  1, 0,  -1,  0, 1,  +1),
    ("mx",  -1,  0, 1,   0,  1, 0,  -1),
    ("my",   1,  0, 0,   0, -1, 1,  -1),
    ("dg",   0,  1, 0,   1,  0, 0,  -1),
    ("ad",   0, -1, 1,  -1,  0, 1,  -1),
]
D4_NAMES = [g[0] for g in D4]


def d4_point(g, x, y, S):
    _, a, b, c, d, e, f, _ = g
    return (a * x + b * y + c * S, d * x + e * y + f * S)


def d4_theta_deg(g, th_deg):
    """Induced action on the orientation, in degrees mod 90 (see module docstring)."""
    det = g[7]
    return (th_deg % PERIOD) if det > 0 else ((-th_deg) % PERIOD)


def d4_points(g, P, S):
    """vectorised: P (m,2) -> (m,2)"""
    _, a, b, c, d, e, f, _ = g
    out = np.empty_like(P)
    out[:, 0] = a * P[:, 0] + b * P[:, 1] + c * S
    out[:, 1] = d * P[:, 0] + e * P[:, 1] + f * S
    return out


def d4_box(g, box, S):
    """image of a witness box under g (used only by the orbit-closure selftest).

    box = (x0, x1, y0, y1, th0, th1).  Rectangles map to rectangles; the theta interval maps to
    [th0, th1] for a rotation and to [90 - th1, 90 - th0] for a reflection (both stay in [0,90]
    when the input does, since reflections reverse the interval)."""
    x0, x1, y0, y1, th0, th1 = box
    cx = [d4_point(g, x0, y0, S), d4_point(g, x1, y0, S),
          d4_point(g, x0, y1, S), d4_point(g, x1, y1, S)]
    nx0 = min(p[0] for p in cx); nx1 = max(p[0] for p in cx)
    ny0 = min(p[1] for p in cx); ny1 = max(p[1] for p in cx)
    if g[7] > 0:
        nth0, nth1 = th0, th1
    else:
        nth0, nth1 = 90.0 - th1, 90.0 - th0
    return (nx0, nx1, ny0, ny1, nth0, nth1)


def d4_corner_check(seed=0, S=3.877084, n=200, tol=1e-12):
    """DERIVATION CHECK for the theta map: g(corners of Q(c,theta)) == corners of
    Q(g(c), theta_g(theta)) as SETS, for all 8 elements."""
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n):
        cx, cy = rng.uniform(0.5, S - 0.5, 2)
        th = float(rng.uniform(0.0, 90.0))
        r = math.radians(th)
        e1 = np.array([math.cos(r), math.sin(r)])
        e2 = np.array([-math.sin(r), math.cos(r)])
        C = np.array([np.array([cx, cy]) + 0.5 * (i * e1 + j * e2)
                      for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
        for g in D4:
            GC = d4_points(g, C, S)
            gc = d4_point(g, cx, cy, S)
            th2 = d4_theta_deg(g, th)
            r2 = math.radians(th2)
            f1 = np.array([math.cos(r2), math.sin(r2)])
            f2 = np.array([-math.sin(r2), math.cos(r2)])
            D = np.array([np.array(gc) + 0.5 * (i * f1 + j * f2)
                          for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
            # set distance (Hausdorff, both ways) between the two 4-point corner sets
            M = np.linalg.norm(GC[:, None, :] - D[None, :, :], axis=2)
            h = max(M.min(axis=1).max(), M.min(axis=0).max())
            worst = max(worst, float(h))
    return dict(ok=bool(worst <= tol), worst_hausdorff=worst, tol=tol, n=n)


# ---------------------------------------------------------------------------------- distances
def theta_dist_deg(th, a, b, period=PERIOD):
    """circular distance (period 90 deg) from th to the closed interval [a, b]."""
    w = float(b) - float(a)
    if w >= period - 1e-12:
        return 0.0
    u = (float(th) - float(a)) % period
    if u <= w:
        return 0.0
    return min(u - w, period - u)


def theta_dist_deg_many(TH, a, b, period=PERIOD):
    TH = np.asarray(TH, dtype=float)
    w = float(b) - float(a)
    if w >= period - 1e-12:
        return np.zeros_like(TH)
    u = np.mod(TH - float(a), period)
    return np.where(u <= w, 0.0, np.minimum(u - w, period - u))


def center_dist_many(C, x0, x1, y0, y1):
    """Chebyshev distance from each centre to the rectangle (0 inside)."""
    dx = np.maximum(np.maximum(x0 - C[:, 0], C[:, 0] - x1), 0.0)
    dy = np.maximum(np.maximum(y0 - C[:, 1], C[:, 1] - y1), 0.0)
    return np.maximum(dx, dy)


# ------------------------------------------------------------------------------------- atlas
class Atlas:
    """The A37 atlas, pre-expanded under D4 in both scale readings."""

    def __init__(self, path=ATLAS_PATH, s0=S0F):
        d = json.load(open(path))
        self.path = path
        self.s0 = float(s0)
        self.raw = d
        self.entries = []
        for idx, e in enumerate(d["entries"]):
            sig = e["canonical_sig"]
            P = np.array([[p[0], p[1]] for p in sig], dtype=float)
            TH = np.array([math.degrees(p[2]) % PERIOD for p in sig], dtype=float)
            s_e = float(e["s_min_float"])
            rec = dict(idx=idx, family_id=e["family_id"], klass=e.get("class"),
                       s_min=s_e, h_certified=e.get("h_certified"),
                       n_place=len(sig), P=P, TH=TH,
                       is_trump=(e["family_id"] == 0))
            THG = [np.array([d4_theta_deg(g, t) for t in TH]) for g in D4]
            # D4 images, mode "s0": placements as stored, D4 about the container centre s0/2
            rec["img_s0"] = [(D4[i][0], d4_points(D4[i], P, self.s0), THG[i])
                             for i in range(len(D4))]
            # D4 images, mode "scaled": centres scaled by s0/s_e first, same D4
            Ps = P * (self.s0 / s_e)
            rec["img_scaled"] = [(D4[i][0], d4_points(D4[i], Ps, self.s0), THG[i])
                                 for i in range(len(D4))]
            self.entries.append(rec)
        self.trump = [r for r in self.entries if r["is_trump"]]
        assert len(self.trump) == 1, "expected exactly one family-0 entry"

    # ---- core query
    def nearest(self, box, mode="s0", topk=5, tol_c=TOL_C, tol_th=TOL_TH):
        """All (entry, placement, D4 element) candidates, ordered by score; returns the topk
        overall plus the best Trump candidate and the best non-Trump candidate."""
        x0, x1, y0, y1, th0, th1 = box
        key = "img_" + mode
        cands = []
        for rec in self.entries:
            best = None
            mdc = mdt = float("inf")
            for gname, P, TH in rec[key]:
                dc = center_dist_many(P, x0, x1, y0, y1)
                dt = theta_dist_deg_many(TH, th0, th1)
                sc = np.maximum(dc / tol_c, dt / tol_th)
                mdc = min(mdc, float(dc.min()))
                mdt = min(mdt, float(dt.min()))
                i = int(np.argmin(sc))
                cand = dict(entry=rec["idx"], family_id=rec["family_id"], klass=rec["klass"],
                            s_min=rec["s_min"], is_trump=rec["is_trump"],
                            d4=gname, placement=i,
                            placement_xytheta=[float(P[i, 0]), float(P[i, 1]), float(TH[i])],
                            d_center=float(dc[i]), d_theta_deg=float(dt[i]), score=float(sc[i]))
                if best is None or cand["score"] < best["score"]:
                    best = cand
            # marginal minima: each coordinate minimised INDEPENDENTLY over the whole orbit.
            # These -- unlike the (d_center, d_theta) of the score-argmin, which can flip between
            # tied placements -- are exactly D4-invariant, so they are what selftest (c) checks.
            best["min_d_center_any"] = mdc
            best["min_d_theta_deg_any"] = mdt
            cands.append(best)
        cands.sort(key=lambda c: (c["score"], c["d_center"], c["d_theta_deg"]))
        trump = min((c for c in cands if c["is_trump"]), key=lambda c: c["score"])
        other = min((c for c in cands if not c["is_trump"]), key=lambda c: c["score"])
        return cands[:topk], trump, other

    def classify(self, box, mode="s0", topk=5, tol_c=TOL_C, tol_th=TOL_TH):
        top, trump, other = self.nearest(box, mode=mode, topk=topk, tol_c=tol_c, tol_th=tol_th)
        tr_ok = (trump["d_center"] <= tol_c and trump["d_theta_deg"] <= tol_th)
        at_ok = (other["d_center"] <= tol_c and other["d_theta_deg"] <= tol_th)
        cls = "trump_consistent" if tr_ok else ("atlas_consistent" if at_ok else "unexplained")
        return dict(classification=cls, mode=mode, tol_center=tol_c, tol_theta_deg=tol_th,
                    trump=trump, nearest_other=other, nearest=top)


# ------------------------------------------------------------------------------- box parsing
BOX_KEYS = ("x0", "x1", "y0", "y1", "th0", "th1")


def parse_box(o):
    if isinstance(o, dict):
        d = o.get("box", o)
        if isinstance(d, (list, tuple)):
            return tuple(float(v) for v in d[:6]), o.get("id", o.get("idx"))
        return tuple(float(d[k]) for k in BOX_KEYS), o.get("id", o.get("idx"))
    return tuple(float(v) for v in o[:6]), None


def load_survivors(path):
    d = json.load(open(path))
    if isinstance(d, dict):
        for k in ("boxes", "survivors", "nodes", "records"):
            if k in d:
                d = d[k]
                break
        else:
            raise SystemExit("survivors json: no boxes/survivors/nodes/records key")
    out = []
    for i, o in enumerate(d):
        b, bid = parse_box(o)
        out.append(dict(id=(bid if bid is not None else i), box=list(b), src=o if isinstance(o, dict) else None))
    return out


# ----------------------------------------------------------------------------------- selftest
def selftest(atlas=None, verbose=True):
    A = atlas or Atlas()
    R = {}

    def say(*a):
        if verbose:
            print(*a, flush=True)

    # ---------------------------------------------------------------- (0) the D4 theta map
    R["d4_theta_map"] = d4_corner_check()
    say("(0) D4 corner/theta derivation check:", json.dumps(R["d4_theta_map"]))

    # ------------------------------------------------- (a) boxes on the in-zone Trump squares
    #   half-widths at A38 depth-3 scale: 0.0131 in the centre, 1.875 deg in theta
    hw, hth = 0.0131, 1.875
    a_recs = []
    for (cx, cy) in TRUMP_IN_ZONE:
        box = (cx - hw, cx + hw, cy - hw, cy + hw,
               TRUMP_THETA_DEG - hth, TRUMP_THETA_DEG + hth)
        c = A.classify(box)
        a_recs.append(dict(box=list(box), classification=c["classification"],
                           d_center=c["trump"]["d_center"], d_theta_deg=c["trump"]["d_theta_deg"],
                           d4=c["trump"]["d4"], placement=c["trump"]["placement"]))
    R["a_trump_boxes"] = dict(
        ok=all(r["classification"] == "trump_consistent" and r["d_center"] == 0.0
               and r["d_theta_deg"] == 0.0 for r in a_recs),
        records=a_recs)
    say("(a) in-zone Trump boxes:", json.dumps(R["a_trump_boxes"]))

    # ------------------------------------------------------ (b) container centre, theta [0,15]
    m = A.s0 / 2.0
    box_b = (m - hw, m + hw, m - hw, m + hw, 0.0, 15.0)
    cb = A.classify(box_b)
    # independent corroboration: the raw min over EVERY atlas placement and every D4 image
    best_c = min(c["d_center"] for c in [cb["trump"], cb["nearest_other"]])
    R["b_centre_box"] = dict(ok=(cb["classification"] == "unexplained"), box=list(box_b),
                             classification=cb["classification"],
                             nearest=cb["nearest"][:3], min_d_center_over_all=best_c)
    say("(b) container-centre box:", cb["classification"],
        "| nearest:", json.dumps(cb["nearest"][:2]))

    # --------------------------------------------------------------- (c) D4 orbit closure
    hw2 = 0.0131
    probe = [(1.272254 - hw2, 1.272254 + hw2, 2.424525 - hw2, 2.424525 + hw2, 47.9, 51.7),
             (m - hw2, m + hw2, m - hw2, m + hw2, 0.0, 15.0),
             (1.10, 1.35, 2.20, 2.60, 10.0, 40.0)]
    worst = 0.0
    rows = []
    for mode in ("s0", "scaled"):
        for box in probe:
            base = A.classify(box, mode=mode)
            for g in D4:
                gb = d4_box(g, box, A.s0)
                c = A.classify(gb, mode=mode)
                dd = 0.0
                for k in ("trump", "nearest_other"):
                    for f in ("score", "min_d_center_any", "min_d_theta_deg_any"):
                        dd = max(dd, abs(c[k][f] - base[k][f]))
                worst = max(worst, dd)
                rows.append(dict(box=list(box), mode=mode, g=g[0], delta=dd,
                                 cls=c["classification"], cls0=base["classification"],
                                 same_cls=(c["classification"] == base["classification"])))
    R["c_orbit_closure"] = dict(ok=(worst <= 1e-9 and all(r["same_cls"] for r in rows)),
                                worst_delta=worst, n=len(rows),
                                note="D4 image of the BOX must leave all min-over-orbit "
                                     "distances and the classification unchanged")
    say("(c) D4 orbit closure: worst delta = %.3e over %d (box,g) pairs; classes stable = %s"
        % (worst, len(rows), all(r["same_cls"] for r in rows)))

    # ------------------------------------------- (d) atlas sanity: theta really is in radians
    sig = A.entries[0]["TH"]
    R["d_trump_theta"] = dict(distinct_theta_deg=sorted(set(round(float(t), 4) for t in sig)),
                              s_min=A.entries[0]["s_min"], s0=A.s0,
                              s0_minus_s_min=A.s0 - A.entries[0]["s_min"])
    say("(d) Trump orientations (deg mod 90):", R["d_trump_theta"]["distinct_theta_deg"])

    R["ok"] = all(R[k]["ok"] for k in ("d4_theta_map", "a_trump_boxes", "b_centre_box",
                                       "c_orbit_closure"))
    return R


# --------------------------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--survivors", default=None, help="json with a list of witness boxes")
    ap.add_argument("--atlas", default=ATLAS_PATH)
    ap.add_argument("--out", default=None)
    ap.add_argument("--mode", default="s0", choices=("s0", "scaled"))
    ap.add_argument("--tol_c", type=float, default=TOL_C)
    ap.add_argument("--tol_th", type=float, default=TOL_TH)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    A = Atlas(a.atlas)
    out = dict(atlas=os.path.relpath(a.atlas, REPO).replace("\\", "/"),
               n_entries=len(A.entries), s0=A.s0, mode=a.mode,
               tol_center=a.tol_c, tol_theta_deg=a.tol_th,
               d4_theta_rule="rotations: theta -> theta mod 90; reflections: theta -> (-theta) mod 90")

    if a.selftest or not a.survivors:
        out["selftest"] = selftest(A)
        print("SELFTEST ok =", out["selftest"]["ok"], flush=True)

    if a.survivors:
        surv = load_survivors(a.survivors)
        recs, tally = [], {}
        for s in surv:
            c = A.classify(tuple(s["box"]), mode=a.mode, topk=a.topk,
                           tol_c=a.tol_c, tol_th=a.tol_th)
            alt = A.classify(tuple(s["box"]),
                             mode=("scaled" if a.mode == "s0" else "s0"),
                             topk=1, tol_c=a.tol_c, tol_th=a.tol_th)
            r = dict(id=s["id"], box=s["box"], **c)
            r["alt_mode"] = dict(mode=alt["mode"], classification=alt["classification"],
                                 trump=alt["trump"], nearest_other=alt["nearest_other"])
            recs.append(r)
            tally[c["classification"]] = tally.get(c["classification"], 0) + 1
            print("%-12s %-18s trump(d_c=%.4f, d_th=%.3f deg, %s#%d) other(e%d f%s d_c=%.4f, "
                  "d_th=%.3f)" % (str(s["id"]), c["classification"],
                                  c["trump"]["d_center"], c["trump"]["d_theta_deg"],
                                  c["trump"]["d4"], c["trump"]["placement"],
                                  c["nearest_other"]["entry"], c["nearest_other"]["family_id"],
                                  c["nearest_other"]["d_center"], c["nearest_other"]["d_theta_deg"]),
                  flush=True)
        out["survivors_path"] = a.survivors
        out["n_survivors"] = len(recs)
        out["tally"] = tally
        out["records"] = recs
        print("CENSUS", json.dumps(tally), flush=True)

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, "w"), indent=1)
        print("->", a.out, flush=True)


if __name__ == "__main__":
    main()
