"""A161 -- the INDEPENDENT checker for `chord_limited_lane_v1` certificates.

Discipline as A141's `check141.py`: it shares with the emitter ONLY

  * A132's `polycore.vertex_ok`  -- the trusted exact rational "point in Q at every pose of a box"
    primitive, whose Lean counterpart `PolyCoreT5.checkVertexInPBox` is proved sound, and
  * A57's `caselp.Box / t_lo / t_hi` -- the corpus's outward-rounded tilt bounds.

The chord formula (CH), the five-point `minchord`, the band threshold, every separating-axis margin,
the container prune, the split rule, cover completeness, the pairwise-overlap test, the frame
derivation and the final arithmetic are RE-IMPLEMENTED here from `notes/leaf.md`, in Fractions.
A144's `guardline.py` is deliberately NOT imported: the guard row is re-derived, so the two
implementations of `minchord` are cross-checked by every run.

Checks, in order (notes/leaf.md sec 4):
  D1  the declared hypothesis boxes contain the frame boxes re-derived from the node record, and
      every one is inside the container hull;
  D2  the guard line is an exact rational strictly inside (0, 1) with the cell's wall orientation;
  D3  every `minchord(B_j, l)` re-derived by the five-point rule; HARD REJECT if the certificate
      claims more; `rhs* = s - SUM`, REJECT if `rhs > rhs*`; `beta = floor(min(rhs, rhs*))`;
  D4  the lane cover's paths are a COMPLETE prefix code over the declared root and each stored box
      equals the box recomputed from its path by the split rule;
  D5  every lane leaf's discharge holds by its own exact test (container / band / misses_cell /
      witness);
  D6  lane_out = 0 needs an EMPTY open list; lane_out = 1 needs every pair of open boxes (diagonal
      included) to always overlap;
  D7  every excluded conditioned square carries a complete cover of its own box, same leaf checks,
      `skip = j`, and NO `band` rows;
  D8  `beta + lane_out + M <= 1`, the slot is usable for the class with a FULL extension window.

    python checkcl.py <cert.json> [...]        |        python checkcl.py --dir ../certs
"""
import argparse
import glob
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
           os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from polycore import vertex_ok                     # noqa: E402  the ONE shared primitive
from caselp import Box, t_lo, t_hi                 # noqa: E402

S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
HALF = Fr(1, 2)
SQRT2_LO = Fr(math.isqrt(2 * 10 ** 48), 10 ** 24)
SQRT2_HI = SQRT2_LO + Fr(1, 10 ** 24)
PINS = {                                           # A118 corpus.CLASSES, re-typed (not imported)
    "k5_11": [(Fr(1, 2), Fr(1, 2)), (Fr(1, 2), Fr(3, 2)), (Fr(1, 2), S_RAT - Fr(1, 2)),
              (Fr(3, 2), Fr(1, 2)), (S_RAT - Fr(1, 2), Fr(1, 2))],
    "k5_16": [(Fr(1, 2), Fr(1, 2)), (Fr(1, 2), Fr(3, 2)), (Fr(1, 2), S_RAT - Fr(1, 2)),
              (S_RAT - Fr(1, 2), Fr(1, 2)), (S_RAT - Fr(1, 2), S_RAT - Fr(1, 2))],
    "trump5": [(Fr(1, 2), Fr(1, 2)), (Fr(3, 2), Fr(1, 2)), (Fr(1, 2), Fr(3, 2)),
               (S_RAT - Fr(1, 2), Fr(1, 2)), (S_RAT - Fr(1, 2), S_RAT - Fr(1, 2))],
}
USABLE = {
    "k5_11": {"BL(1,1)": "k6_18", "BR(0,1)": "k6_20", "TL(1,0)": "k6_20", "TR(0,0)": "k6_23"},
    "k5_16": {"BL(1,0)": "k6_23", "BR(0,1)": "k6_29", "BR(1,0)": "k6_27", "TR(0,1)": "k6_30",
              "TR(1,0)": "k6_28", "TL(1,0)": "k6_27"},
    "trump5": {"BL(0,2)": "k6_07", "BL(1,1)": "k6_19", "BR(0,1)": "k6_21", "TR(0,1)": "k6_22",
               "TR(1,0)": "k6_24", "TL(0,0)": "k6_23"},
}
TOL = Fr(1, 10 ** 7)                               # slack allowed on the float frame re-derivation


# ===================================================================== exact primitives, re-written
def _u(t):
    """cos th + sin th at t = tan(th/2)."""
    return (1 - t * t + 2 * t) / (1 + t * t)


def cs_hi(t0, t1):
    lo, hi = SQRT2_LO - 1, SQRT2_HI - 1
    return SQRT2_HI if (t0 <= hi and t1 >= lo) else max(_u(t0), _u(t1))


def cs_lo(t0, t1):
    return min(_u(t0), _u(t1))


def tbin(b):
    t0, t1 = t_lo(b[4]), t_hi(b[5])
    return (t1, t0) if t0 > t1 else (t0, t1)


def chord_at_t(t, V, a=HALF):
    """(CH) exactly at t = tan(th/2), V = |v| >= 0."""
    Cn, Sn, D = 1 - t * t, 2 * t, 1 + t * t
    mx = max(Cn, Sn)
    if mx == 0:
        return Fr(0)
    A = 2 * a * D / mx
    if Cn == 0 or Sn == 0:
        return A if V * D <= a * mx else Fr(0)
    B = (a * (Cn + Sn) - V * D) * D / (Cn * Sn)
    return max(Fr(0), min(A, B))


def minchord(b, orient, off, a=HALF):
    """The five-point exact lower bound of the chord over the parameter box (leaf.md sec 1 /
    A144 spec sec 2): A(t) increases, B has its minimum over a y-interval at an endpoint, and the
    chord is antitone in |v| so |v| is taken maximal over the centre rectangle."""
    lo, hi = (Fr(b[2]), Fr(b[3])) if orient == "h" else (Fr(b[0]), Fr(b[1]))
    V = max(abs(off - lo), abs(off - hi))
    t0, t1 = tbin(b)
    if t0 == t1:
        return chord_at_t(t0, V, a)
    cands = []
    for t in (t0, t1):
        Cn, Sn, D = 1 - t * t, 2 * t, 1 + t * t
        mx = max(Cn, Sn)
        if mx:
            cands.append(2 * a * D / mx)                          # A(t)
        y = _u(t)
        if y == 1:
            cands.append(a if V >= a else None)                   # the limit value at y = 1
        else:
            cands.append(2 * (a * y - V) / (y * y - 1))           # B(y(t))
    tstar = SQRT2_LO - 1
    if t0 <= tstar + Fr(1, 10 ** 15) and t1 >= tstar:
        cands.append(2 * (SQRT2_LO * a - V))                      # <= B(sqrt2)
    cands = [c for c in cands if c is not None]
    return max(Fr(0), min(cands))


def band_holds(b, orient, off):
    """chord >= 1 at EVERY pose of `b`:  max|v| <= (y + 1 - y^2)/2 at y = cs_max."""
    lo, hi = (Fr(b[2]), Fr(b[3])) if orient == "h" else (Fr(b[0]), Fr(b[1]))
    V = max(abs(off - lo), abs(off - hi))
    Y = cs_hi(*tbin(b))
    return V <= (Y + 1 - Y * Y) / 2


def proj_min(dx, dy, t0, t1):
    """min over th in the bin of dx cos th + dy sin th, exactly (endpoint rule; the one wrapping
    case dx <= 0 and dy <= 0 falls back to the conservative -(|dx| + |dy|))."""
    if dx <= 0 and dy <= 0:
        return -(abs(dx) + abs(dy))
    out = None
    for t in (t0, t1):
        g = (dx * (1 - t * t) + 2 * dy * t) / (1 + t * t)
        out = g if out is None else min(out, g)
    return out


def misses_cell(b, cell, axis=None):
    """SOUND, exact: does some axis separate every pose's square from int(cell)?  If `axis` is
    given only that axis is tried (the certificate names it, and the checker refuses to
    substitute a different one)."""
    X0, X1, Y0, Y1 = (Fr(v) for v in cell)
    x0, x1, y0, y1 = Fr(b[0]), Fr(b[1]), Fr(b[2]), Fr(b[3])
    t0, t1 = tbin(b)
    hmax = cs_hi(t0, t1) / 2
    fam = {"ex+": x0 - X1, "ex-": X0 - x1, "ey+": y0 - Y1, "ey-": Y0 - y1}
    for nm, m in fam.items():
        if (axis is None or axis == nm) and m >= hmax:
            return True, nm
    DX, DY = (x0 - X1, x1 - X0), (y0 - Y1, y1 - Y0)
    for k in (0, 1):
        for sg in (1, -1):
            nm = "w%d%s" % (k, "+" if sg > 0 else "-")
            if axis is not None and axis != nm:
                continue
            worst = None
            for dx in DX:
                for dy in DY:
                    ex, ey = sg * dx, sg * dy
                    if k == 1:
                        ex, ey = ey, -ex
                    g = proj_min(ex, ey, t0, t1)
                    worst = g if worst is None else min(worst, g)
            if worst >= HALF:
                return True, nm
    return False, None


def outside_container(b, s=S_RAT):
    """Every pose of `b` puts its square outside [0, s]^2 (h(th) >= cs_min/2)."""
    hmin = cs_lo(*tbin(b)) / 2
    return (Fr(b[1]) < hmin or Fr(b[3]) < hmin
            or Fr(b[0]) > Fr(s) - hmin or Fr(b[2]) > Fr(s) - hmin)


def always_overlap(b1, b2):
    """SOUND: every pose of b1 and every pose of b2 give overlapping squares.

    Two independent tests, the first exact.
      (a) DISC.  A unit square contains the open disc of radius 1/2 about its centre, so it is
          enough that the FARTHEST two centres are less than 1 apart (exact Fractions).
      (b) SAT.  Along an edge normal `n` of square 1 the separating gap is
          |n.(c2 - c1)| - 1/2 - (|cos D| + |sin D|)/2 with `D` the relative tilt; bounding the
          projection ABOVE and (|cos D| + |sin D|) BELOW over the two boxes gives a sound upper
          bound on the gap, and a negative bound for BOTH normal families means no separating axis
          exists for any pose pair.  Re-implemented here from A118 sec 1.2(ii) in floats with a
          conservative epsilon, as A141's own checker does.
    """
    d2 = Fr(0)
    for (ax, bx) in ((Fr(b1[0]), Fr(b2[0])), (Fr(b1[0]), Fr(b2[1])),
                     (Fr(b1[1]), Fr(b2[0])), (Fr(b1[1]), Fr(b2[1]))):
        for (ay, by) in ((Fr(b1[2]), Fr(b2[2])), (Fr(b1[2]), Fr(b2[3])),
                         (Fr(b1[3]), Fr(b2[2])), (Fr(b1[3]), Fr(b2[3]))):
            d2 = max(d2, (ax - bx) ** 2 + (ay - by) ** 2)
    if d2 < 1:
        return True
    lo, hi = float(b2[4]) - float(b1[5]), float(b2[5]) - float(b1[4])
    if math.ceil(lo / 90.0) <= hi / 90.0 + 1e-12:
        m = 1.0
    else:
        m = min(_csf(lo), _csf(hi))
    lim = 0.5 + 0.5 * m
    D = (float(b2[0]) - float(b1[1]), float(b2[1]) - float(b1[0]),
         float(b2[2]) - float(b1[3]), float(b2[3]) - float(b1[2]))
    eps = 1e-12
    return (_max_abs_proj(D, float(b1[4]), float(b1[5])) - lim < -eps
            and _max_abs_proj(D, float(b2[4]), float(b2[5])) - lim < -eps)


def _csf(deg):
    r = math.radians(deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def _gmaxf(alpha, beta):
    """max over psi in [alpha, beta] (radians) of max(|cos psi|, |sin psi|)."""
    if math.ceil(alpha / (math.pi / 2)) <= beta / (math.pi / 2) + 1e-15:
        return 1.0
    return max(max(abs(math.cos(alpha)), abs(math.sin(alpha))),
               max(abs(math.cos(beta)), abs(math.sin(beta))))


def _max_abs_proj(D, th0, th1):
    """max over d in the interval box D and the two edge normals of a square with tilt in
    [th0, th1] (degrees) of |n . d|; the max over the box is at a corner."""
    a0, a1 = math.radians(th0), math.radians(th1)
    best = 0.0
    for dx in (D[0], D[1]):
        for dy in (D[2], D[3]):
            R = math.hypot(dx, dy)
            if R == 0.0:
                continue
            phi = math.atan2(dy, dx)
            best = max(best, R * _gmaxf(a0 - phi, a1 - phi))
    return best


# ===================================================================== the cover skeleton
def split(b):
    x0, x1, y0, y1, t0, t1 = b
    wx, wy, wt = x1 - x0, y1 - y0, (t1 - t0) / 60.0
    if wx >= wy and wx >= wt:
        m = 0.5 * (x0 + x1)
        return [x0, m, y0, y1, t0, t1], [m, x1, y0, y1, t0, t1]
    if wy >= wt:
        m = 0.5 * (y0 + y1)
        return [x0, x1, y0, m, t0, t1], [x0, x1, m, y1, t0, t1]
    m = 0.5 * (t0 + t1)
    return [x0, x1, y0, y1, t0, m], [x0, x1, y0, y1, m, t1]


def box_from_path(root, path):
    b = list(root)
    for ch in path:
        b = split(b)[0 if ch == "0" else 1]
    return b


def complete_prefix_code(paths):
    S = set(paths)
    if len(S) != len(paths):
        return False, "duplicate path"
    for p in S:
        for k in range(len(p)):
            if p[:k] in S:
                return False, "path %s has proper prefix %s" % (p, p[:k])
    internal = set()
    for p in S:
        for k in range(len(p)):
            internal.add(p[:k])
    if "" not in internal and S != {""}:
        return False, "root missing"
    for q in internal:
        if not ((q + "0" in S or q + "0" in internal) and (q + "1" in S or q + "1" in internal)):
            return False, "internal node %r lacks both children" % q
    return True, ""


def check_leaf(lf, cell, hyp, skip, orient, off, allow_band, errs, tag):
    b = lf["box"]
    why = lf["why"]
    if why == "container":
        if not outside_container(b):
            errs.append("%s leaf %r: container prune false" % (tag, lf["path"]))
    elif why == "band":
        if not allow_band:
            errs.append("%s leaf %r: `band` is not a legal discharge here" % (tag, lf["path"]))
        elif not band_holds(b, orient, off):
            errs.append("%s leaf %r: band prune false (chord < 1 somewhere)" % (tag, lf["path"]))
    elif why == "misses_cell":
        ok, nm = misses_cell(b, cell, axis=lf.get("axis"))
        if not ok:
            errs.append("%s leaf %r: axis %s does not separate" % (tag, lf["path"],
                                                                   lf.get("axis")))
    elif why == "witness":
        j = lf["j"]
        if skip is not None and j == skip:
            errs.append("%s leaf %r: vacuous witness against itself (j = skip)" % (tag,
                                                                                  lf["path"]))
            return
        wx, wy = Fr(lf["w"][0]), Fr(lf["w"][1])
        bb = Box(*b)
        if not vertex_ok(wx, wy, bb):
            errs.append("%s leaf %r: witness not in every pose of the leaf box" % (tag,
                                                                                  lf["path"]))
        if not vertex_ok(wx, wy, Box(*hyp[j])):
            errs.append("%s leaf %r: witness not in every pose of B%d" % (tag, lf["path"], j))
    else:
        errs.append("%s leaf %r: unknown discharge %r" % (tag, lf["path"], why))


def check_cover(cov, root, cell, hyp, skip, orient, off, allow_band, errs, tag, want_lane):
    paths = [lf["path"] for lf in cov["leaves"]] + [o["path"] for o in cov.get("open", [])]
    ok, msg = complete_prefix_code(paths)
    if not ok:
        errs.append("%s: leaf paths are not a complete cover of the root (%s)" % (tag, msg))
    for lf in cov["leaves"] + list(cov.get("open", [])):
        rb = box_from_path(root, lf["path"])
        if max(abs(float(u) - float(v)) for u, v in zip(rb, lf["box"])) > 1e-12:
            errs.append("%s leaf %r: stored box != box from the split rule" % (tag, lf["path"]))
    for lf in cov["leaves"]:
        check_leaf(lf, cell, hyp, skip, orient, off, allow_band, errs, tag)
    op = list(cov.get("open", []))
    if want_lane == 0:
        if op:
            errs.append("%s: lane_out = 0 declared with %d open boxes" % (tag, len(op)))
    elif want_lane == 1:
        bxs = [o["box"] for o in op]
        for u in range(len(bxs)):
            for v in range(u, len(bxs)):
                if not always_overlap(bxs[u], bxs[v]):
                    errs.append("%s: open boxes %d,%d not certified always-overlapping" %
                                (tag, u, v))
                    return
    else:
        errs.append("%s: lane_out = %r is not 0 or 1" % (tag, want_lane))


# ===================================================================== D1: the frame re-derivation
def _hull(f, ms):
    v = [f(m) for m in ms]
    return min(v), max(v)


def frame_boxes_from_record(rec_path, cls, corner, src):
    """Re-derive A118's cframe boxes from the node JSON, independently (Fractions where the record
    is exact, floats where it is a float; a TOL slack is allowed in the containment test)."""
    d = json.load(open(os.path.join(ROOT, rec_path), encoding="utf-8"))
    m_lo = {"A57": 3.8616374951330865, "A57box": 3.8616374951330865, "A60": S0}.get(src, 3.82)
    ms = (m_lo, S0)
    flipx = corner in ("BR", "TR")
    flipy = corner in ("TR", "TL")

    def fx(g):
        return _hull((lambda m: (m - g(m)) if flipx else g(m)), ms)

    def fy(g):
        return _hull((lambda m: (m - g(m)) if flipy else g(m)), ms)

    pins, cond = [], []
    for (px, py) in PINS[cls]:
        px, py = float(px), float(py)
        bx, ax = (1.0, px - S0) if px > 0.5 * S0 else (0.0, px)
        by, ay = (1.0, py - S0) if py > 0.5 * S0 else (0.0, py)
        X0, X1 = fx(lambda m, a=ax, b=bx: a + b * m)
        Y0, Y1 = fy(lambda m, a=ay, b=by: a + b * m)
        pins.append([X0, X1, Y0, Y1, 0.0, 0.0])
    for bd in (d.get("hyp") or {}).get("boxes", []):
        cx, cy = 0.5 * (bd["x0"] + bd["x1"]), 0.5 * (bd["y0"] + bd["y1"])
        near = any(abs(cx - float(a)) < 2e-2 and abs(cy - float(b)) < 2e-2
                   for a, b in [(float(u), float(v)) for u, v in PINS[cls]])
        if near and float(bd.get("th0", 0.0)) <= 1e-6 and float(bd.get("th1", 0.0)) <= 1e-6:
            continue                                       # a pin: re-derived above
        t0, t1 = float(bd["th0"]), float(bd["th1"])
        if flipx != flipy:
            t0, t1 = 90.0 - t1, 90.0 - t0
        xs = [v for w in (bd["x0"], bd["x1"]) for v in fx(lambda m, q=w: q * m / S0)]
        ys = [v for w in (bd["y0"], bd["y1"]) for v in fy(lambda m, q=w: q * m / S0)]
        cond.append([min(xs), max(xs), min(ys), max(ys), min(max(t0, 0.0), 90.0),
                     min(max(t1, 0.0), 90.0)])
    return pins + cond


# ===================================================================== the certificate
def check(path, node_paths=None, verbose=True):
    c = json.load(open(path, encoding="utf-8"))
    errs, notes = [], []
    if c.get("leaf") != "chord_limited_lane_v1":
        return ["not a chord_limited_lane_v1 certificate: %r" % c.get("leaf")], []
    s = Fr(c["s"])
    hyp = c["hyp_boxes"]
    cell = c["cell"]
    gl = c["guardline"]
    orient, off = gl["orient"], Fr(gl["off"])
    i, j = c["ij"]

    # --- D1
    for k, b in enumerate(hyp):
        if outside_container(b, s):
            errs.append("D1: hyp box B%d holds no container-admissible pose" % k)
    rp = (node_paths or {}).get(c["nid"])
    if rp:
        try:
            der = frame_boxes_from_record(rp, c["cls"], c["corner"], c["src"])
        except Exception as e:                                     # noqa: BLE001
            der = None
            notes.append("D1: frame re-derivation unavailable (%s)" % repr(e)[:60])
        if der is not None:
            if len(der) != len(hyp):
                errs.append("D1: %d frame boxes re-derived vs %d declared" % (len(der), len(hyp)))
            else:
                for k, (a, b) in enumerate(zip(der, hyp)):
                    if not (Fr(b[0]) - TOL <= Fr(a[0]) and Fr(a[1]) <= Fr(b[1]) + TOL
                            and Fr(b[2]) - TOL <= Fr(a[2]) and Fr(a[3]) <= Fr(b[3]) + TOL
                            and Fr(b[4]) - TOL <= Fr(a[4]) and Fr(a[5]) <= Fr(b[5]) + TOL):
                        errs.append("D1: declared B%d does not contain the re-derived frame box "
                                    "%s vs %s" % (k, a, b))
            notes.append("D1: frame boxes re-derived from %s" % rp)
    else:
        notes.append("D1: node record not supplied -- containment not re-derived")

    # --- D2
    if not (0 < off < 1):
        errs.append("D2: guard offset %s not strictly inside (0, 1)" % off)
    want = "h" if j == 0 else "v"
    if orient != want and not (i == 0 and j == 0):
        errs.append("D2: cell (%d,%d) wants a %s wall line, got %s" % (i, j, want, orient))

    # --- D3
    tot = Fr(0)
    for k, b in enumerate(hyp):
        m = minchord(b, orient, off)
        claimed = Fr(gl["minchords"][k]["minchord"])
        if claimed > m:
            errs.append("D3: B%d claims minchord %s > re-derived %s" % (k, claimed, m))
        tot += m
    rhs_star = s - tot
    if Fr(gl["rhs"]) > rhs_star:
        errs.append("D3: rhs %s > re-derived %s" % (gl["rhs"], rhs_star))
    rhs_use = min(Fr(gl["rhs"]), rhs_star)
    if rhs_use < 0:
        notes.append("D3: rhs < 0 -- the guard row alone kills the node")
        beta = 0
    else:
        beta = int(math.floor(rhs_use))
    if beta != gl["beta"]:
        errs.append("D3: beta %d re-derived vs %r declared" % (beta, gl["beta"]))

    # --- D4/D5/D6
    lo = c["lane_out"]
    check_cover(lo, lo["root"], cell, hyp, None, orient, off, True, errs, "lane_out",
                lo["value"])

    # --- D7
    M = c["M"]
    nex = 0
    for e in M["detail"]:
        if not e["excluded"]:
            continue
        nex += 1
        cov = dict(leaves=e["cert"] or [], open=[])
        if not cov["leaves"]:
            errs.append("D7: B%d declared excluded with no cover" % e["j"])
            continue
        for lf in cov["leaves"]:
            if lf["why"] == "band":
                errs.append("D7: B%d cover uses a `band` discharge (illegal for M)" % e["j"])
        check_cover(cov, hyp[e["j"]], cell, hyp, e["j"], orient, off, False, errs,
                    "M[B%d]" % e["j"], 0)
    if M["value"] != len(M["detail"]) - nex:
        errs.append("D7: M %r declared but %d of %d conditioned squares excluded"
                    % (M["value"], nex, len(M["detail"])))

    # --- D8
    tot3 = beta + lo["value"] + M["value"]
    if tot3 != c["total"]:
        errs.append("D8: total %d re-derived vs %r declared" % (tot3, c["total"]))
    if tot3 > 1:
        errs.append("D8: beta + LANE_out + M = %d > 1 -- NOT a kill" % tot3)
    ext = USABLE.get(c["cls"], {}).get(c["slot"])
    if ext is None:
        errs.append("D8: slot %s is not a usable slot of class %s" % (c["slot"], c["cls"]))
    elif ext != c["extension"]:
        errs.append("D8: extension %r declared, table says %r" % (c["extension"], ext))
    if "FULL" not in c.get("extension_window", ""):
        errs.append("D8: extension window not declared FULL")

    if verbose:
        st = "PASS" if not errs else "FAIL"
        print("%-4s %s   beta=%d LANE_out=%s M=%s total=%d   leaves=%d(lane) %s"
              % (st, os.path.basename(path), beta, lo["value"], M["value"], tot3,
                 len(lo["leaves"]),
                 "+".join(str(len(e["cert"] or [])) for e in M["detail"] if e["excluded"])),
              flush=True)
        for e in errs:
            print("      ERR %s" % e, flush=True)
        for n in notes:
            print("      ... %s" % n, flush=True)
    return errs, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="*")
    ap.add_argument("--dir", default="")
    ap.add_argument("--nodes", default="", help="jsonl/json with nid -> record path, for D1")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "checkcl.json"))
    a = ap.parse_args()
    files = list(a.certs)
    if a.dir:
        files += sorted(glob.glob(os.path.join(a.dir, "cl_*.json")))
    npaths = {}
    if a.nodes and os.path.exists(a.nodes):
        npaths = json.load(open(a.nodes, encoding="utf-8"))
    res, nfail = [], 0
    for f in files:
        errs, notes = check(f, npaths)
        res.append(dict(cert=os.path.relpath(f, ROOT), ok=(not errs), errors=errs, notes=notes))
        nfail += bool(errs)
    print("\n%d certificates, %d PASS, %d FAIL" % (len(files), len(files) - nfail, nfail))
    json.dump(dict(n=len(files), n_pass=len(files) - nfail, n_fail=nfail, results=res),
              open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
