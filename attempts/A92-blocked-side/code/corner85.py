"""
A85 `corner85.py` -- the CORNER FRAME pilot for k0_00 (R1 reach cover, R2 pair census,
R3 alive gate + D4 samples).  Exact; no LP anywhere in this module.

The BL corner box is [0,1]^2; the WIDENED box is [0, a]^2 with a = 1 + w, w = 0.026.
Half-extent of a unit square at tilt theta: h(theta) = (cos theta + sin theta)/2.

A pose (c, theta) MEETS the open widened box iff  f(Q) := min over Q of max(x, y)  <  a.
The min of the convex-piecewise-linear max(x, y) over the convex polygon Q is attained at a
vertex of Q or where an edge of Q crosses the diagonal x = y -- both computed exactly in
Fractions from a rational t = tan(theta/2) (cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2)).

Reach-set membership of a COVER BOX is a SOUND over-inclusion:
    box in reach  iff  x0 - h_max < a  and  y0 - h_max < a,
h_max = max of h over the box's theta range (padded outward), because meeting [0,a)^2 forces
min_Q x < a and min_Q y < a, i.e. cx - h < a and cy - h < a.

Prunes for a PAIR of boxes (both SOUND):
  (P1) pinguard.cores_meet(core_i, core_j) -- every square realising box i overlaps every
       square realising box j, so the two-square hypothesis is contradictory;
  (P2) the maximum possible centre distance over the two boxes is < 1 -- two interior-disjoint
       unit squares have centre distance >= 1.
REFINED prune at level L: subdivide each box into 2^(3L) sub-boxes (Box.split repeated) and
prune the pair iff EVERY sub-pair is pruned by (P1) or (P2).  Sound: the sub-boxes cover.
"""
import argparse, itertools, json, math, os, random, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from caselp import Box, t_lo, t_hi, cos_sin_t
from pinguard import cores_meet
import class85 as K85

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
for d in (RES, LOGS):
    os.makedirs(d, exist_ok=True)

S0 = K85.S0
S0F = K85.S0F
W_WIDEN = 0.026
RECT = (0.5, 1.75, 0.5, 1.75)          # centre rect of the BL reach cover
W_BOX = 0.15
A_MIN = 0.34
T_EDGES = [Fr(0), Fr(1, 8), Fr(1, 4), Fr(3, 8), Fr(5, 11), Fr(3, 5), Fr(7, 9), Fr(1)]
SQRT_HALF = math.sqrt(0.5)


# ------------------------------------------------------------------ exact "meets" test
def _verts(cx, cy, t):
    co, si = cos_sin_t(t)
    h = Fr(1, 2)
    e1 = (h * co, h * si)
    e2 = (-h * si, h * co)
    return [(cx + su * e1[0] + sv * e2[0], cy + su * e1[1] + sv * e2[1])
            for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def f_min_max(cx, cy, t):
    """exact  min over Q of max(x, y)."""
    V = _verts(cx, cy, t)
    best = None
    for (x, y) in V:
        v = max(x, y)
        best = v if best is None else min(best, v)
    for i in range(4):
        (px, py) = V[i]
        (qx, qy) = V[(i + 1) % 4]
        dx, dy = qx - px, qy - py
        if dx == dy:
            continue
        s = (py - px) / (dx - dy)
        if 0 <= s <= 1:
            x = px + s * dx
            best = min(best, x)
    return best


def meets_open_box(cx, cy, t, a):
    """the open interiors of Q(c, theta) and [0, a]^2 intersect."""
    return f_min_max(cx, cy, t) < a


# ------------------------------------------------------------------ cover with explicit t-edges
def _deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


def cover_t(rect, s, w, tedges, a_min, max_split=3):
    """tree57.cover semantics, with an EXPLICIT t-partition."""
    x0, x1, y0, y1 = rect
    nx = max(1, int(math.ceil((x1 - x0) / w)))
    ny = max(1, int(math.ceil((y1 - y0) / w)))
    te = [_deg_of_t(t) for t in tedges]
    nth = len(tedges) - 1
    todo = [Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                te[k], te[k + 1])
            for i in range(nx) for j in range(ny) for k in range(nth)]
    out, bad = [], []
    for _ in range(max_split + 1):
        nxt = []
        for b in todo:
            if b.vacuous(s):
                continue
            c = b.core()
            if c is not None and float(c.a) >= a_min:
                out.append(b)
            else:
                nxt.append(b)
        if not nxt:
            break
        todo = [h for b in nxt for h in b.split()]
    else:
        for b in todo:
            if b.vacuous(s):
                continue
            if b.core() is not None:
                out.append(b)
            else:
                bad.append(b)
    return out, bad, (nx, ny, nth)


def sigma_box(b):
    """the exact diagonal reflection (x, y, theta) -> (y, x, 90 - theta) of a cover box."""
    return Box(b.y0, b.y1, b.x0, b.x1, 90.0 - b.th1, 90.0 - b.th0)


def cover_sigma(rect, s, w, tedges, a_min, max_split=3):
    """SIGMA-EQUIVARIANT cover.  tree57.cover's split rule is NOT equivariant under
    theta -> 90 - theta: it bisects along the widest dimension measured in t, and mirrored
    t-bins of a sigma-closed partition have DIFFERENT t-widths (1/8 vs 2/9 here), so the bin
    [0, 1/8] survives at a_min while its mirror [7/9, 1] is split -- the resulting BOX SET is
    not sigma-closed and the D4 corner maps of R3(b) do not land on cover boxes.

    Repair (same soundness, same a_min gate): refine by bisecting THETA at the DEGREE midpoint
    (which commutes with theta -> 90 - theta), and refine a box iff min(a(b), a(sigma b)) <
    a_min.  Both the criterion and the refinement are sigma-equivariant, so the box set is
    sigma-closed at every level.  Vacuous boxes are dropped exactly as tree57 does (and
    vacuity is itself sigma-invariant on a square rect)."""
    x0, x1, y0, y1 = rect
    nx = max(1, int(math.ceil((x1 - x0) / w)))
    ny = max(1, int(math.ceil((y1 - y0) / w)))
    te = [_deg_of_t(t) for t in tedges]
    nth = len(tedges) - 1
    todo = [Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                te[k], te[k + 1])
            for i in range(nx) for j in range(ny) for k in range(nth)]

    def amin_sym(b):
        c1, c2 = b.core(), sigma_box(b).core()
        if c1 is None or c2 is None:
            return -1.0
        return min(float(c1.a), float(c2.a))

    out, bad = [], []
    for _ in range(max_split + 1):
        nxt = []
        for b in todo:
            if b.vacuous(s):
                continue
            if amin_sym(b) >= a_min:
                out.append(b)
            else:
                nxt.append(b)
        if not nxt:
            break
        todo = [Box(b.x0, b.x1, b.y0, b.y1, b.th0, 0.5 * (b.th0 + b.th1)) for b in nxt] + \
               [Box(b.x0, b.x1, b.y0, b.y1, 0.5 * (b.th0 + b.th1), b.th1) for b in nxt]
    else:
        for b in todo:
            if b.vacuous(s):
                continue
            if b.core() is not None:
                out.append(b)
            else:
                bad.append(b)
    return out, bad, (nx, ny, nth)


def bkey(b, nd=6):
    return (round(b.x0, nd), round(b.x1, nd), round(b.y0, nd), round(b.y1, nd),
            round(b.th0, nd), round(b.th1, nd))


def sigma_closed_boxes(boxes):
    """-> (closed?, perm) where perm[i] = index of sigma(box_i) in the same list."""
    K = {bkey(b): i for i, b in enumerate(boxes)}
    perm = []
    for b in boxes:
        perm.append(K.get(bkey(sigma_box(b)), -1))
    return (all(p >= 0 for p in perm) and sorted(perm) == list(range(len(boxes)))), perm


# ------------------------------------------------------------------ reach / sense
def h_max_of(b):
    """max of h(theta) = (cos + sin)/2 over [th0, th1], padded outward (sound)."""
    vals = [0.5 * (math.cos(math.radians(t)) + math.sin(math.radians(t))) for t in (b.th0, b.th1)]
    if b.th0 <= 45.0 <= b.th1:
        vals.append(SQRT_HALF)
    return max(vals) + 1e-12


def in_reach(b, a):
    return (b.x0 - h_max_of(b) < a) and (b.y0 - h_max_of(b) < a)


def sense_class(b):
    """P = theta range inside [0,45), M = inside (45,90], S = straddles 45, A = touches 0 or 90.
    A takes precedence (a box touching a domain end is the mod-90 glue case)."""
    if b.th0 <= 1e-9 or b.th1 >= 90.0 - 1e-9:
        return "A"
    if b.th0 < 45.0 < b.th1:
        return "S"
    return "P" if b.th1 <= 45.0 else "M"


def sense_pm(b):
    """the P/M/S class ignoring the A (domain-end) override."""
    if b.th0 < 45.0 < b.th1:
        return "S"
    return "P" if b.th1 <= 45.0 else "M"


def witnessed(b, a, n=5):
    """a sampled pose of the box (n x n x n grid) that EXACTLY meets the open widened box."""
    tl, th = t_lo(b.th0), t_hi(b.th1)
    if th > 1:
        th = Fr(1)
    for i in range(n):
        cx = Fr(round((b.x0 + (b.x1 - b.x0) * i / (n - 1.0)) * 10 ** 9), 10 ** 9)
        for j in range(n):
            cy = Fr(round((b.y0 + (b.y1 - b.y0) * j / (n - 1.0)) * 10 ** 9), 10 ** 9)
            for k in range(n):
                t = tl + (th - tl) * Fr(k, n - 1)
                if meets_open_box(cx, cy, t, a):
                    return True, [str(cx), str(cy), str(t)]
    return False, None


# ------------------------------------------------------------------ R1
def r1(w_widen=W_WIDEN, out="a85_reach_BL.json"):
    t0 = time.time()
    a = 1.0 + w_widen
    a_fr = Fr(1) + Fr(round(w_widen * 10 ** 9), 10 ** 9)
    variants = {}
    for label, te, fn in (("sigma_closed_7", T_EDGES, cover_sigma),
                          ("tree57_sigma7", T_EDGES, cover_t),
                          ("tree57_uniform8", [Fr(k, 8) for k in range(9)], cover_t)):
        boxes, bad, grid = fn(RECT, S0F, W_BOX, te, A_MIN)
        closed, perm = sigma_closed_boxes(boxes)
        rows = []
        for i, b in enumerate(boxes):
            snd = in_reach(b, a)
            snd0 = in_reach(b, 1.0)
            wit, wpose = (witnessed(b, a_fr) if snd else (False, None))
            rows.append(dict(i=i, box=b.to_json(), sound=bool(snd), sound_w0=bool(snd0),
                             witnessed=bool(wit), witness_pose=wpose,
                             core_a=float(b.core().a), sense=sense_class(b), sense_pm=sense_pm(b),
                             h_max=h_max_of(b)))
        cnt = dict(cover=len(boxes), uncoverable=len(bad),
                   sound=sum(1 for r in rows if r["sound"]),
                   sound_w0=sum(1 for r in rows if r["sound_w0"]),
                   witnessed=sum(1 for r in rows if r["witnessed"]))
        by_sense = {}
        for r in rows:
            if r["sound"]:
                by_sense[r["sense"]] = by_sense.get(r["sense"], 0) + 1
        variants[label] = dict(t_edges=[str(x) for x in te], grid=list(grid), counts=cnt,
                               box_set_sigma_closed=bool(closed), sigma_perm=perm,
                               sound_by_sense=by_sense, rows=rows)
    res = dict(cls="k0_00", phase="R1_reach_BL", corner="BL", w_widen=w_widen, a=a,
               rect=list(RECT), w_box=W_BOX, a_min=A_MIN, s0=S0F,
               sigma_closed_check=sigma_check(T_EDGES),
               seconds=round(time.time() - t0, 1), variants=variants)
    json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res


def sigma_check(te):
    """t -> (1-t)/(1+t) must permute the edge set (theta -> 90 - theta)."""
    S = set(te)
    img = {(1 - t) / (1 + t) for t in te}
    return dict(closed=bool(S == img), edges=[str(x) for x in te],
                image=[str(x) for x in sorted(img)])


# ------------------------------------------------------------------ R2
def subdivide(b, n):
    out = [b]
    for _ in range(n):
        out = [h for x in out for h in x.split()]
    return out


def max_centre_dist(b, c):
    dx = max(abs(b.x0 - c.x1), abs(b.x1 - c.x0))
    dy = max(abs(b.y0 - c.y1), abs(b.y1 - c.y0))
    return math.hypot(dx, dy)


def pruned(bi, bj, ci, cj):
    """(P1) or (P2): the two-square hypothesis is contradictory."""
    if max_centre_dist(bi, bj) + 1e-12 < 1.0:
        return "maxdist<1"
    if ci is not None and cj is not None and cores_meet(ci, cj):
        return "cores_meet"
    return None


def pair_survives(bi, bj, subs_i, subs_j):
    """True iff SOME sub-pair is not pruned."""
    for (sb, sc) in subs_i:
        for (tb, tc) in subs_j:
            if pruned(sb, tb, sc, tc) is None:
                return True
    return False


def r2(reach_file="a85_reach_BL.json", out="a85_pairs_BL.json", variant="sigma_closed_7"):
    t0 = time.time()
    R = json.load(open(os.path.join(RES, reach_file)))
    rows = [r for r in R["variants"][variant]["rows"] if r["sound"]]
    boxes = [Box.from_json(r["box"]) for r in rows]
    idx = [r["i"] for r in rows]
    sense = [r["sense"] for r in rows]
    cores = [b.core() for b in boxes]
    n = len(boxes)
    lvl = {0: [], 1: [], 2: []}

    # level 0
    for i in range(n):
        for j in range(i + 1, n):
            if pruned(boxes[i], boxes[j], cores[i], cores[j]) is None:
                lvl[0].append((i, j))
    # level 1 (8 sub-boxes each), then level 2 (64) -- only on survivors
    sub = {}

    def subs(k, lv):
        key = (k, lv)
        if key not in sub:
            sub[key] = [(b, b.core()) for b in subdivide(boxes[k], 3 * lv)]
        return sub[key]

    part = os.path.join(RES, out + ".partial")
    json.dump(dict(phase="R2_pairs_BL", level_done=0, n_sound_boxes=n,
                   n_pair={"level0": len(lvl[0])}), open(part, "w"), indent=1)
    for lv in (1, 2):
        keep = []
        for m, (i, j) in enumerate(lvl[lv - 1]):
            if pair_survives(boxes[i], boxes[j], subs(i, lv), subs(j, lv)):
                keep.append((i, j))
            if m % 2000 == 0:
                print("  L%d %d/%d kept %d  %.0fs" % (lv, m, len(lvl[lv - 1]), len(keep),
                                                      time.time() - t0), flush=True)
        lvl[lv] = keep
        sub.clear()
        json.dump(dict(phase="R2_pairs_BL", level_done=lv, n_sound_boxes=n,
                       n_pair={"level%d" % k: len(lvl[k]) for k in range(lv + 1)},
                       seconds=round(time.time() - t0, 1)), open(part, "w"), indent=1)

    def table(pairs):
        T = {}
        for (i, j) in pairs:
            k = "".join(sorted(sense[i] + sense[j]))
            T[k] = T.get(k, 0) + 1
        return T

    res = dict(cls="k0_00", phase="R2_pairs_BL", corner="BL", variant=variant,
               n_sound_boxes=n, box_index=idx,
               n_pair=dict(level0=len(lvl[0]), level1=len(lvl[1]), level2=len(lvl[2]),
                           all_unordered=n * (n - 1) // 2),
               sense_table=dict(level0=table(lvl[0]), level1=table(lvl[1]),
                                level2=table(lvl[2])),
               seconds=round(time.time() - t0, 1),
               surviving_level2=[dict(i=i, j=j, sense_i=sense[i], sense_j=sense[j],
                                      pair_sense="".join(sorted(sense[i] + sense[j])),
                                      box_i=boxes[i].to_json(), box_j=boxes[j].to_json(),
                                      core_i=cores[i].to_json(), core_j=cores[j].to_json())
                                 for (i, j) in lvl[2]])
    json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["r1", "r2"])
    ap.add_argument("--w", type=float, default=W_WIDEN)
    a = ap.parse_args()
    if a.cmd == "r1":
        res = r1(a.w)
        for lab, v in res["variants"].items():
            print(lab, json.dumps(v["counts"]), json.dumps(v["sound_by_sense"]),
                  "grid", v["grid"], "sigma_closed_boxset", v["box_set_sigma_closed"])
        print("sigma", json.dumps(res["sigma_closed_check"]["closed"]),
              "seconds", res["seconds"])
    else:
        res = r2()
        print(json.dumps(dict(n_sound=res["n_sound_boxes"], n_pair=res["n_pair"],
                              sense=res["sense_table"], seconds=res["seconds"])))


if __name__ == "__main__":
    main()
