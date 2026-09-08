"""A89-O3 DIAGNOSTIC D -- anatomy of the k0_00 depth-2 certification coverage HOLES.

Reads (read-only) A85's cert witness files for the FAILed depth-2 nodes and, for every
witness box (kind 'hole' = an exact uncovered placement box, kind 'undecided' = the exact
arithmetic could not decide at max depth), reports

  * the centre box [cx0,cx1] x [cy0,cy1] and the tilt (= dist(theta, 90 Z)) range in degrees;
  * for each of the four corners c, the EXACT reach quantity
        g_c(B) := min over poses (c_Q, theta) in B of  f_c(c_Q, theta),
    f_c := min over Q of max(x_c, y_c) in c's corner frame (corner85.f_min_max, exact in
    Fractions).  f_c < 1  <=>  Q meets the open unit corner box B_c.  g_c < 1 means SOME pose
    of the box is a corner blocker; g_c - 1 is the (signed) reach gap.  Monotonicity: f_c is
    nondecreasing in both corner-frame centre coordinates, so the min over the centre rect is
    at the rect's corner nearest c; the theta min is taken over a fine grid with the exact
    Lipschitz pad L = sqrt(2)/2 per radian (f is (sqrt2/2)-Lipschitz in theta), so the
    reported g is a rigorous LOWER bound (=> 'meets' claims are certified by an exact witness
    pose, and 'does not meet' by g - pad >= 1).
  * the Euclidean distance of the centre box to the nearest corner POINT of [0,s]^2;
  * whether the theta range meets (0,2) u (88,90) degrees (the near-flush ghost zone).

Classification: corner-pose (some pose meets a corner box), near-flush corner pose (corner
pose AND theta range meets the ghost zone), interior/mid-tilt (no pose meets any corner box).
"""
import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from corner85 import f_min_max

A85 = os.path.abspath(os.path.join(BASE, "..", "A85-k0-route"))
CERTD = os.path.join(A85, "certs", "k0_00")
RES = os.path.join(BASE, "results")

S = Fr("969271/250000")
SF = float(S)
LIP = math.sqrt(0.5)          # |d f / d theta| <= sqrt(2)/2 (radians)
NTH = 97                      # theta grid per box


def theta_deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


def tilt_deg(th):
    return min(th % 90.0, 90.0 - (th % 90.0))


# corner frames: (x_c, y_c) = A_c (x, y).  BL identity; BR x->s-x; TL y->s-y; TR both.
def to_frame(corner, x0, x1, y0, y1):
    if corner == "BL":
        return x0, x1, y0, y1
    if corner == "BR":
        return S - x1, S - x0, y0, y1
    if corner == "TL":
        return x0, x1, S - y1, S - y0
    return S - x1, S - x0, S - y1, S - y0


def refl_t(t):
    """theta -> 90 - theta on t = tan(theta/2):  t -> (1-t)/(1+t)."""
    return (1 - t) / (1 + t)


def frame_t_range(corner, t0, t1):
    """a reflection of the frame maps theta -> 90 - theta (t -> (1-t)/(1+t)); two
    reflections (TR) map theta -> theta."""
    if corner in ("BL", "TR"):
        return t0, t1
    a, b = refl_t(t1), refl_t(t0)
    return a, b


def reach_min(corner, box):
    """rigorous lower bound on min over the box of f_c, plus the best exact pose value."""
    x0, x1, y0, y1 = to_frame(corner, box["cx0"], box["cx1"], box["cy0"], box["cy1"])
    t0, t1 = frame_t_range(corner, box["t0"], box["t1"])
    # f nondecreasing in both frame coordinates -> min of the centre rect at (x0, y0)
    best, best_t = None, None
    for i in range(NTH):
        t = t0 + (t1 - t0) * Fr(i, NTH - 1)
        v = f_min_max(x0, y0, t)
        if best is None or v < best:
            best, best_t = v, t
    dth = 2.0 * (math.atan(float(t1)) - math.atan(float(t0))) / (NTH - 1)   # radians per step
    pad = LIP * dth / 2.0
    return float(best) - pad, float(best), best_t


def dist_to_corner(box):
    out = {}
    for c, (px, py) in (("BL", (0.0, 0.0)), ("BR", (SF, 0.0)),
                        ("TL", (0.0, SF)), ("TR", (SF, SF))):
        dx = max(0.0, float(box["cx0"]) - px, px - float(box["cx1"]))
        dy = max(0.0, float(box["cy0"]) - py, py - float(box["cy1"]))
        out[c] = math.hypot(dx, dy)
    return out


def parse_box(w):
    b = w["box"]
    return dict(t0=Fr(b["t"][0]), t1=Fr(b["t"][1]),
                cx0=Fr(b["cx"][0]), cx1=Fr(b["cx"][1]),
                cy0=Fr(b["cy"][0]), cy1=Fr(b["cy"][1]))


def do_file(name):
    wp = os.path.join(CERTD, name + ".witnesses.json")
    rp = os.path.join(CERTD, name + ".report.json")
    if not os.path.exists(wp):
        return None
    W = json.load(open(wp))["witnesses"]
    rep = json.load(open(rp)) if os.path.exists(rp) else {}
    rows = []
    for k, w in enumerate(W):
        box = parse_box(w)
        th0 = theta_deg_of_t(box["t0"])
        th1 = theta_deg_of_t(box["t1"])
        tl = sorted((tilt_deg(th0), tilt_deg(th1)))
        if th0 < 45.0 < th1:
            tl = [min(tl[0], tl[1]), 45.0]
        ghost = (th1 > 0.0 and th0 < 2.0) or (th1 > 88.0 and th0 < 90.0)
        reach = {}
        for c in ("BL", "BR", "TL", "TR"):
            lo, exact, bt = reach_min(c, box)
            reach[c] = dict(g_lower=lo, g_exact_best=exact,
                            meets_corner_box=bool(exact < 1.0),
                            certainly_no_meet=bool(lo >= 1.0))
        d = dist_to_corner(box)
        meets = [c for c in reach if reach[c]["meets_corner_box"]]
        rows.append(dict(node=name, k=k, kind=w.get("kind"),
                         cx=[float(box["cx0"]), float(box["cx1"])],
                         cy=[float(box["cy0"]), float(box["cy1"])],
                         theta_deg=[th0, th1], tilt_deg=tl,
                         t=[str(box["t0"]), str(box["t1"])],
                         width_cx=float(box["cx1"] - box["cx0"]),
                         width_cy=float(box["cy1"] - box["cy0"]),
                         width_theta_deg=th1 - th0,
                         depth=w.get("depth"), exact_mass=w.get("exact_mass"),
                         float_mass=w.get("float_mass"),
                         ghost_zone_theta=bool(ghost),
                         dist_to_corner_point=d,
                         nearest_corner=min(d, key=d.get),
                         nearest_corner_dist=min(d.values()),
                         meets_corner_boxes=meets,
                         corner_pose=bool(meets),
                         reach=reach))
    summ = dict(node=name, result=rep.get("result"), total_float=rep.get("total_float"),
                n_witness=len(rows),
                n_hole=sum(1 for r in rows if r["kind"] == "hole"),
                n_undecided=sum(1 for r in rows if r["kind"] == "undecided"),
                n_corner_pose=sum(1 for r in rows if r["corner_pose"]),
                n_corner_pose_ghost=sum(1 for r in rows if r["corner_pose"] and r["ghost_zone_theta"]),
                n_ghost=sum(1 for r in rows if r["ghost_zone_theta"]),
                n_interior=sum(1 for r in rows if not r["corner_pose"]),
                min_nearest_corner_dist=min([r["nearest_corner_dist"] for r in rows], default=None),
                max_nearest_corner_dist=max([r["nearest_corner_dist"] for r in rows], default=None),
                tilt_span=[min([r["tilt_deg"][0] for r in rows], default=None),
                           max([r["tilt_deg"][1] for r in rows], default=None)],
                min_reach_gap=min([min(r["reach"][c]["g_exact_best"] for c in r["reach"]) - 1.0
                                   for r in rows], default=None))
    return rows, summ


def main():
    names = ["s1int_l2_l2_p215_011", "s1int_l2_l2_p215_011_epsgeo0.002",
             "s1int_l2_l2_p215_011_epsgeo0.004",
             "s1int_l2_l2_p210_001", "s1int_l2_l2_p210_001_epsgeo0.002",
             "s1int_l2_l2_p210_001_epsgeo0.004"]
    allrows, summs = [], []
    for n in names:
        r = do_file(n)
        if r is None:
            print("absent", n)
            continue
        rows, s = r
        allrows += rows
        summs.append(s)
        print(json.dumps(s))
    # global counts over the DISTINCT witness boxes of the two base certs
    base = [r for r in allrows if not r["node"].endswith(("0.002", "0.004"))]
    tot = dict(n_witness=len(base),
               n_hole=sum(1 for r in base if r["kind"] == "hole"),
               n_undecided=sum(1 for r in base if r["kind"] == "undecided"),
               n_corner_pose=sum(1 for r in base if r["corner_pose"]),
               n_corner_pose_ghost=sum(1 for r in base if r["corner_pose"] and r["ghost_zone_theta"]),
               n_ghost=sum(1 for r in base if r["ghost_zone_theta"]),
               n_interior_midtilt=sum(1 for r in base if not r["corner_pose"]))
    print("BASE TOTAL", json.dumps(tot))
    json.dump(dict(diagnostic="D", s=str(S), s_float=SF, n_theta_grid=NTH, lipschitz=LIP,
                   per_node=summs, base_total=tot, rows=allrows),
              open(os.path.join(RES, "o3_holes.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
