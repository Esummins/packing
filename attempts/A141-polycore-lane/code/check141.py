"""A141 -- the INDEPENDENT checker for `polycore_lane_v1` / `polycore_pair_v1` certificates.

It shares NOTHING with the emitter except A132's exact rational vertex test `polycore.vertex_ok`
(the trusted primitive, whose Lean counterpart `PolyCoreT5.checkVertexInPBox` is proved sound) and
`caselp.Box`.  Every interval prune, the split rule, the cover-completeness test and the pairwise
overlap test are re-implemented here from the certificate's own numbers.

    python check141.py <cert.json> [<cert.json> ...]
    python check141.py --dir ../certs

Checks, in order:
  C1  the tightened conditioned boxes are inside the raw ones and inside the container hull;
  C2  the leaf paths form a COMPLETE prefix code (a full binary subdivision of the root), and the
      box recomputed from each path by the certificate's own split rule equals the stored box;
  C3  every leaf's discharge holds:
        container   -- every pose of the box leaves [0, s]^2,
        misses_cell -- one axis separates the box's squares from the cell for every pose,
        witness     -- the rational point lies in Q(pose) for every pose of the leaf box AND for
                       every pose of conditioned box j  (exact, `vertex_ok` twice);
  C4  if lane_ub = 1: every pair of OPEN boxes (diagonal included) always overlaps;
  C5  the M covers are complete covers of the conditioned boxes they exclude, with the same leaf
      checks and `skip = j` (a witness against j itself would be vacuous);
  C6  lane_ub + M <= 1 for a KILL.
"""
import argparse
import glob
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
           os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from polycore import vertex_ok                      # noqa: E402  the exact rational primitive
from caselp import Box                              # noqa: E402

SQ2 = math.sqrt(2.0)


def _cs(deg):
    r = math.radians(deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def cs_max(d0, d1):
    best = max(_cs(d0), _cs(d1))
    k = math.floor(d0 / 90.0)
    while k * 90.0 + 45.0 <= d1 + 1e-12:
        c = k * 90.0 + 45.0
        if c >= d0 - 1e-12:
            best = max(best, _cs(c))
        k += 1
    return best


def cs_min(d0, d1):
    best = min(_cs(d0), _cs(d1))
    k = math.ceil(d0 / 90.0)
    while k * 90.0 <= d1 + 1e-12:
        best = min(best, _cs(k * 90.0))
        k += 1
    return best


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
    """The paths are the leaves of ONE full binary tree rooted at '' (so their boxes tile the
    root exactly): no path is a prefix of another, and every internal node has both children."""
    S = set(paths)
    if len(S) != len(paths):
        return False, "duplicate path"
    if S == {""}:
        return True, ""
    seen = set()
    for p in S:
        for k in range(len(p)):
            if p[:k] in S:
                return False, "path %r is under leaf %r" % (p, p[:k])
            seen.add(p[:k])
    for node in seen:
        for ch in "01":
            c = node + ch
            if c not in S and c not in seen:
                return False, "node %r has no subtree" % c
    return True, ""


def leaf_container(b, s, eps=1e-12):
    hmin = 0.5 * cs_min(b[4], b[5])
    return (b[1] < hmin - eps or b[3] < hmin - eps
            or b[0] > s - hmin + eps or b[2] > s - hmin + eps)


def leaf_misses(b, cell, eps=1e-12):
    X0, X1, Y0, Y1 = cell
    hmax = 0.5 * cs_max(b[4], b[5])
    return (b[0] - hmax >= X1 - eps or b[1] + hmax <= X0 + eps
            or b[2] - hmax >= Y1 - eps or b[3] + hmax <= Y0 + eps)


def _gmax(alpha, beta):
    """max over psi in [alpha, beta] (RADIANS) of max(|cos psi|, |sin psi|): 1 when the interval
    straddles a multiple of pi/2, otherwise attained at an endpoint (the function is V-shaped in
    between)."""
    if math.ceil(alpha / (math.pi / 2)) <= beta / (math.pi / 2) + 1e-15:
        return 1.0
    return max(max(abs(math.cos(alpha)), abs(math.sin(alpha))),
               max(abs(math.cos(beta)), abs(math.sin(beta))))


def _max_abs_proj(D, th0, th1):
    """max over d in the interval box D = (dx0, dx1, dy0, dy1) and over the two edge normals of a
    square with tilt in [th0, th1] (degrees) of |n . d|.  The max over the box is at a corner
    (|n.d| is convex in d), and for a fixed corner it is |d| * g(theta - arg d)."""
    a0, a1 = math.radians(th0), math.radians(th1)
    best = 0.0
    for dx in (D[0], D[1]):
        for dy in (D[2], D[3]):
            R = math.hypot(dx, dy)
            if R == 0.0:
                continue
            phi = math.atan2(dy, dx)
            best = max(best, R * _gmax(a0 - phi, a1 - phi))
    return best


def always_overlap(b1, b2, eps=1e-12):
    """No separating axis for ANY pose in b1 and ANY pose in b2 (A118 sec 1.2(ii)).

    Along an edge normal n of square 1 the SAT gap is |n.(c2-c1)| - 1/2 - (|cos D| + |sin D|)/2
    with D the relative tilt; bounding the projection above and (|cos D| + |sin D|) below over the
    two boxes gives a sound upper bound on the gap.  Negative for BOTH normal families means no
    separating axis exists.  The coarse screen |n.d| <= |d| is tried first."""
    ax = max(abs(b2[0] - b1[1]), abs(b2[1] - b1[0]))
    ay = max(abs(b2[2] - b1[3]), abs(b2[3] - b1[2]))
    dmax = math.hypot(ax, ay)
    lo, hi = b2[4] - b1[5], b2[5] - b1[4]
    m = 1.0 if math.ceil(lo / 90.0) <= hi / 90.0 + 1e-12 else min(_cs(lo), _cs(hi))
    lim = 0.5 + 0.5 * m
    if dmax - lim < -eps:
        return True
    D = (b2[0] - b1[1], b2[1] - b1[0], b2[2] - b1[3], b2[3] - b1[2])
    if _max_abs_proj(D, b1[4], b1[5]) - lim >= -eps:
        return False
    return _max_abs_proj(D, b2[4], b2[5]) - lim < -eps


def check_leaves(leaves, root, cell, cond_boxes, s, skip=None, extra_open=()):
    errs = []
    paths = [lf["path"] for lf in leaves] + [o["path"] for o in extra_open]
    ok, why = complete_prefix_code(paths)
    if not ok:
        errs.append("cover not a complete subdivision: " + why)
    for lf in list(leaves) + list(extra_open):
        b = box_from_path(root, lf["path"])
        if max(abs(u - v) for u, v in zip(b, lf["box"])) > 1e-12:
            errs.append("leaf %r: stored box != box from path" % lf["path"])
        why = lf.get("why")
        if why is None:
            continue                                   # an OPEN leaf: nothing to discharge
        if why == "container":
            if not leaf_container(b, s):
                errs.append("leaf %r: container prune fails" % lf["path"])
        elif why == "misses_cell":
            if not leaf_misses(b, cell):
                errs.append("leaf %r: misses_cell prune fails" % lf["path"])
        elif why == "witness":
            j = lf["j"]
            if skip is not None and j == skip:
                errs.append("leaf %r: witness against the skipped square itself" % lf["path"])
                continue
            wx, wy = Fr(lf["w"][0]), Fr(lf["w"][1])
            bb = Box(*b)
            cj = Box(*cond_boxes[j])
            if not vertex_ok(wx, wy, bb):
                errs.append("leaf %r: witness not in every pose of the leaf box" % lf["path"])
            if not vertex_ok(wx, wy, cj):
                errs.append("leaf %r: witness not in every pose of box %d" % (lf["path"], j))
        else:
            errs.append("leaf %r: unknown reason %r" % (lf["path"], why))
    return errs


def check_lane_cert(d):
    errs = []
    s = d["s"]
    # C1 -- the tightened boxes
    for k, (raw, tig) in enumerate(zip(d["cond_boxes_raw"], d["cond_boxes"])):
        hmin = 0.5 * cs_min(raw[4], raw[5])
        want = [max(raw[0], hmin), min(raw[1], s - hmin),
                max(raw[2], hmin), min(raw[3], s - hmin), raw[4], raw[5]]
        same = all(abs(t - r) <= 1e-12 for t, r in zip(tig, raw))
        hull = (all(abs(t - w) <= 1e-12 for t, w in zip(tig[:4], want[:4]))
                and tig[4] == raw[4] and tig[5] == raw[5])
        if not (same or hull):
            errs.append("box %d: the stored box is neither the raw box nor its container hull"
                        % k)
    # the cell: either the WIDENED unit corner box (k0, Lemma K0-WIDEN) or a plain unit slot cell
    cell = d["cell_rect"]
    w = d["widen_w"]
    kind = d.get("cell_kind", "k0_corner_widened")
    span = [round(cell[1] - cell[0], 9), round(cell[3] - cell[2], 9)]
    want_span = (1.0 + w) if kind == "k0_corner_widened" else 1.0
    if any(abs(v - want_span) > 1e-9 for v in span):
        errs.append("cell rect is not the %s (span %s, want %.9f)" % (kind, span, want_span))
    # C2/C3 -- the LANE cover
    if d.get("lane_ub") is None:
        errs.append("no certified LANE upper bound")
    else:
        errs += check_leaves(d["lane_leaves"] or [], d["root"], cell, d["cond_boxes"], s,
                             extra_open=d.get("lane_open") or [])
        opens = [o["box"] for o in (d.get("lane_open") or [])]
        if d["lane_ub"] == 0 and opens:
            errs.append("lane_ub = 0 but the cover has open leaves")
        if d["lane_ub"] == 1:
            if not opens:
                errs.append("lane_ub = 1 with an empty open set (should be 0)")
            for a in range(len(opens)):
                for b_ in range(a, len(opens)):
                    if not always_overlap(opens[a], opens[b_]):
                        errs.append("open pair (%d, %d) is not certified always-overlapping"
                                    % (a, b_))
                        break
                else:
                    continue
                break
    # C5 -- the M covers.  `M_index[k]` says which conditioned box the k-th M record is about
    # (for a pinned class only the NON-PIN squares count towards M).
    idx = d.get("M_index") or list(range(len(d.get("M_cert") or [])))
    for k, cert in enumerate(d.get("M_cert") or []):
        if cert is None:
            continue
        j = idx[k]
        errs += check_leaves(cert, d["cond_boxes"][j], cell, d["cond_boxes"], s, skip=j)
    nx = sum(1 for c in (d.get("M_cert") or []) if c is None)
    if d.get("M_exact") and d.get("M") is not None and d["M"] != nx:
        errs.append("stored M = %s but %d boxes have no exclusion certificate" % (d["M"], nx))
    # C6
    if d["verdict"] == "KILL":
        if d.get("lane_ub") is None or not d.get("M_exact") or d["lane_ub"] + d["M"] > 1:
            errs.append("KILL claimed without LANE + M <= 1")
    return errs


def check_split_cert(d):
    """The JOINT leaf: a complete binary subdivision of the conditioned box, the ordinary leaf on
    every piece.  Checks: the piece paths tile `cond_boxes[split_index]`; each piece's box is the
    box its path names; each piece's `m_j = 0` claim is the certified `misses_cell` prune on that
    piece; each piece's lane cover is a complete cover of the pose window whose leaves discharge;
    and `lane_ub + M_other + m_j <= 1` on every piece."""
    errs = []
    s = d["s"]
    cell = d["cell_rect"]
    j = d["split_index"]
    root_j = d["cond_boxes"][j]
    ok, why = complete_prefix_code([p["path"] for p in d["pieces"]])
    if not ok:
        errs.append("the split of box %d is not a complete subdivision: %s" % (j, why))
    span = [round(cell[1] - cell[0], 9), round(cell[3] - cell[2], 9)]
    want = (1.0 + d["widen_w"]) if d.get("cell_kind", "k0_corner_widened") == \
        "k0_corner_widened" else 1.0
    if any(abs(v - want) > 1e-9 for v in span):
        errs.append("cell rect is not the expected cell")
    for p in d["pieces"]:
        b = box_from_path(root_j, p["path"])
        if max(abs(u - v) for u, v in zip(b, p["box"])) > 1e-12:
            errs.append("piece %r: stored box != box from path" % p["path"])
        if p["m_j"] == 0 and not leaf_misses(b, cell):
            errs.append("piece %r: claims the conditioned square misses the cell, and it is not "
                        "certified" % p["path"])
        cmap = dict(zip(p["cond_index"], p["cond_boxes"]))
        if cmap.get(j) is not None and max(abs(u - v) for u, v in zip(cmap[j], b)) > 1e-12:
            errs.append("piece %r: the obstacle for square %d is not the piece box"
                        % (p["path"], j))
        if p["lane_ub"] is None:
            errs.append("piece %r: no certified LANE bound" % p["path"])
            continue
        errs += check_leaves(p.get("lane_leaves") or [], p["root"], cell, cmap, s,
                             extra_open=p.get("lane_open") or [])
        opens = [o["box"] for o in (p.get("lane_open") or [])]
        if p["lane_ub"] == 0 and opens:
            errs.append("piece %r: lane_ub = 0 with open leaves" % p["path"])
        if p["lane_ub"] == 1:
            for a in range(len(opens)):
                for b2 in range(a, len(opens)):
                    if not always_overlap(opens[a], opens[b2]):
                        errs.append("piece %r: open pair (%d, %d) not always-overlapping"
                                    % (p["path"], a, b2))
                        break
                else:
                    continue
                break
        idx = p.get("M_index") or []
        for k, cert in enumerate(p.get("M_cert") or []):
            if cert is None:
                continue
            jj = idx[k]
            errs += check_leaves(cert, cmap[jj], cell, cmap, s, skip=jj)
        nx = sum(1 for c in (p.get("M_cert") or []) if c is None)
        if p["M_other"] != nx:
            errs.append("piece %r: M_other = %s but %d boxes lack an exclusion certificate"
                        % (p["path"], p["M_other"], nx))
        if p["lane_ub"] + p["M_other"] + p["m_j"] > 1:
            errs.append("piece %r: LANE + M + m_j = %d > 1"
                        % (p["path"], p["lane_ub"] + p["M_other"] + p["m_j"]))
    if d["verdict"] != "KILL":
        errs.append("split certificate does not claim the kill")
    return errs


def check_pair_cert(d):
    errs = check_leaves(d["leaves"], d["box_i"], (-1e9, 1e9, -1e9, 1e9),
                        {0: d["box_j"]}, d["s"])
    if d["verdict"] != "DEAD-BY-PAIR":
        errs.append("pair certificate does not claim the kill")
    return errs


def check_file(p):
    d = json.load(open(p, encoding="utf-8"))
    if d.get("format") == "polycore_pair_v1":
        return check_pair_cert(d)
    if d.get("format") == "polycore_split_lane_v1":
        return check_split_cert(d)
    return check_lane_cert(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="*")
    ap.add_argument("--dir", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    files = list(a.certs)
    if a.dir:
        files += sorted(glob.glob(os.path.join(a.dir, "*.json")))
    rows = []
    bad = 0
    for p in files:
        try:
            errs = check_file(p)
        except Exception as e:                       # noqa: BLE001
            errs = ["EXCEPTION " + repr(e)[:200]]
        rows.append(dict(cert=os.path.basename(p), ok=not errs, errors=errs[:8]))
        bad += bool(errs)
        print(("PASS  " if not errs else "FAIL  ") + os.path.basename(p)
              + ("" if not errs else "   " + errs[0]), flush=True)
    print("checked %d, failed %d" % (len(files), bad))
    if a.out:
        json.dump(dict(checked=len(files), failed=bad, rows=rows),
                  open(a.out, "w", encoding="utf-8"), indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
