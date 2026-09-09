"""A168 -- the INDEPENDENT checker of the cascade's geometric steps (v2, piece roles).

Shares with the emitter ONLY A132's `polycore.vertex_ok` (Lean `checkVertexInPBox`) and A57's
`caselp.Box` / `t_lo` / `t_hi`.  Everything else is re-derived here from the statements and every
claim of the tree record is re-decided in the HARD direction.

  C1  pad, (R6), M(c) by an own full SAT + 5e4 sampled poses of H per corner
  C2  every cover of every step is a complete prefix code over its declared root and every
      discharged leaf's reason holds by an own exact test (witness leaves: vertex_ok on the box
      AND on every piece of the named role)
  C3  every piece of every role of every node is a subset of the role's source box; every
      ADMISSIBLE sampled pose in (source box \\ pieces) overlaps some other role's certified axis
      core (the clip removed nothing admissible and free)
  C4  every role's core polygon and axis core re-certified with vertex_ok against every piece
  C5  the node INVARIANT re-decided with an own SAT on every ALIVE node: every K' inside the
      container, all pairs interior-disjoint (a violation = an unsound alive node); every DEAD
      verdict re-decided (OVL by sampling pose pairs, PAIR witness by vertex_ok, rows by an own
      minchord, labelling prunes)
  C6  the canary: the real family lands in an ALIVE node at every built level (distinct squares)
  C7  the LP records: budget = 11 - #boxes; cores = A135 exact_a re-run; cores pairwise disjoint

    python check168.py --cell l1_104
"""
import argparse
import json
import math
import os
import random
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A132-polygon-core", "code"), os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import polycore as PC                                            # noqa: E402  trusted primitive
from caselp import Box, t_lo, t_hi                               # noqa: E402

S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
WLO = Fr(382, 100)
SQ2_LO = Fr(math.isqrt(2 * 10 ** 48), 10 ** 24)
SQ2_HI = SQ2_LO + Fr(1, 10 ** 24)
HALF = Fr(1, 2)
RES = os.path.join(BASE, "results")
FAILS = []
STATS = {}


def fail(tag, msg, **kw):
    FAILS.append(dict(check=tag, msg=msg, **kw))
    print("  FAIL [%s] %s %s" % (tag, msg, json.dumps(kw, default=str)[:240]), flush=True)


def note(tag, msg):
    print("  %s %s" % (tag, msg), flush=True)


# ===================================================================== exact helpers (own)
def tbin(b):
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    return (t1, t0) if t0 > t1 else (t0, t1)


def cs_of_t(t):
    t = Fr(t)
    return (1 - t * t + 2 * t) / (1 + t * t)


def cs_bounds(t0, t1):
    lo = min(cs_of_t(t0), cs_of_t(t1))
    hi = SQ2_HI if (t0 <= SQ2_HI - 1 and t1 >= SQ2_LO - 1) else max(cs_of_t(t0), cs_of_t(t1))
    return lo, hi


def cos_sin(t):
    t = Fr(t)
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def proj_min(dx, dy, t0, t1):
    dx, dy = Fr(dx), Fr(dy)
    if dx <= 0 and dy <= 0:
        return -(abs(dx) + abs(dy))
    out = None
    for t in (Fr(t0), Fr(t1)):
        c, s = cos_sin(t)
        v = dx * c + dy * s
        out = v if out is None else min(out, v)
    return out


def box_outside_container(b):
    lo, _ = cs_bounds(*tbin(b))
    h = lo / 2
    return Fr(b.x1) < h or Fr(b.y1) < h or Fr(b.x0) > S_RAT - h or Fr(b.y0) > S_RAT - h


def box_misses_cell_full(b, cell):
    X0, X1, Y0, Y1 = (Fr(v) for v in cell)
    x0, x1, y0, y1 = Fr(b.x0), Fr(b.x1), Fr(b.y0), Fr(b.y1)
    t0, t1 = tbin(b)
    _lo, hi = cs_bounds(t0, t1)
    hmax = hi / 2
    for m in (x0 - X1, X0 - x1, y0 - Y1, Y0 - y1):
        if m >= hmax:
            return True
    DX, DY = (x0 - X1, x1 - X0), (y0 - Y1, y1 - Y0)
    for k in (0, 1):
        for sg in (1, -1):
            worst = None
            for dx in DX:
                for dy in DY:
                    ex, ey = sg * dx, sg * dy
                    if k == 1:
                        ex, ey = ey, -ex
                    g = proj_min(ex, ey, t0, t1)
                    worst = g if worst is None else min(worst, g)
            if worst >= HALF:
                return True
    return False


def chord_min_over_box(b, orient, off):
    lo, hi = ((Fr(b.y0), Fr(b.y1)) if orient == "h" else (Fr(b.x0), Fr(b.x1)))
    off = Fr(off)
    V = max(abs(off - lo), abs(off - hi))
    t0, t1 = tbin(b)
    ts = [t0, t1]
    if t0 <= SQ2_HI - 1 and t1 >= SQ2_LO - 1:
        ts.append(SQ2_LO - 1)
    cands = []
    for t in ts:
        c, s = cos_sin(Fr(t))
        c = abs(c)
        if c == 0 or s == 0:
            cands.append(Fr(1) if V < HALF else Fr(0))
            continue
        A = 1 / max(c, s)
        B = ((c + s) / 2 - V) / (c * s)
        cands.append(max(Fr(0), min(A, B)))
    return min(cands)


def band_all(b, orient, off):
    lo, hi = ((Fr(b.y0), Fr(b.y1)) if orient == "h" else (Fr(b.x0), Fr(b.x1)))
    off = Fr(off)
    V = max(abs(off - lo), abs(off - hi))
    _l, Y = cs_bounds(*tbin(b))
    return V <= (Y + 1 - Y * Y) / 2


def out_all(b, orient, off):
    lo, hi = ((Fr(b.y0), Fr(b.y1)) if orient == "h" else (Fr(b.x0), Fr(b.x1)))
    off = Fr(off)
    a_, b_ = off - hi, off - lo
    V = Fr(0) if (a_ <= 0 <= b_) else min(abs(a_), abs(b_))
    Y, _h = cs_bounds(*tbin(b))
    return V > (Y + 1 - Y * Y) / 2


def sq_verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (c * ux - s * uy), cy + 0.5 * (s * ux + c * uy))
            for ux, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sat_gap_polys(P, Q):
    best = -1e9
    for A in (P, Q):
        for i in range(len(A)):
            ax, ay = A[(i + 1) % len(A)][0] - A[i][0], A[(i + 1) % len(A)][1] - A[i][1]
            nx, ny = ay, -ax
            L = math.hypot(nx, ny)
            if L < 1e-15:
                continue
            nx, ny = nx / L, ny / L
            p = [v[0] * nx + v[1] * ny for v in P]
            q = [v[0] * nx + v[1] * ny for v in Q]
            best = max(best, max(min(p) - max(q), min(q) - max(p)))
    return best


def polys_disjoint_exact(P, Q):
    """own exact SAT: separated on some edge normal of either polygon (touching allowed)."""
    for A in (P, Q):
        m = len(A)
        for i in range(m):
            a, b = A[i], A[(i + 1) % m]
            nx, ny = b[1] - a[1], a[0] - b[0]
            if nx == 0 and ny == 0:
                continue
            pa = [nx * p[0] + ny * p[1] for p in P]
            pb = [nx * p[0] + ny * p[1] for p in Q]
            if min(pb) >= max(pa) or min(pa) >= max(pb):
                return True
    return False


def sq_meets_rect(cx, cy, th, rect):
    X0, X1, Y0, Y1 = rect
    return sat_gap_polys(sq_verts(cx, cy, th), [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]) < 0


def in_box(cx, cy, thd, b, tol=1e-9):
    return (b.x0 - tol <= cx <= b.x1 + tol and b.y0 - tol <= cy <= b.y1 + tol
            and b.th0 - tol <= thd <= b.th1 + tol)


def split_box(b):
    wx, wy, wt = b.x1 - b.x0, b.y1 - b.y0, (b.th1 - b.th0) / 60.0
    if wx >= wy and wx >= wt:
        m = 0.5 * (b.x0 + b.x1)
        return (Box(b.x0, m, b.y0, b.y1, b.th0, b.th1), Box(m, b.x1, b.y0, b.y1, b.th0, b.th1))
    if wy >= wt:
        m = 0.5 * (b.y0 + b.y1)
        return (Box(b.x0, b.x1, b.y0, m, b.th0, b.th1), Box(b.x0, b.x1, m, b.y1, b.th0, b.th1))
    m = 0.5 * (b.th0 + b.th1)
    return (Box(b.x0, b.x1, b.y0, b.y1, b.th0, m), Box(b.x0, b.x1, b.y0, b.y1, m, b.th1))


def replay(root, path):
    b = root
    for ch in path:
        b = split_box(b)[int(ch)]
    return b


def prefix_complete(paths):
    S = set(paths)
    if len(S) != len(paths):
        return False, "duplicate paths"
    for p in paths:
        for k in range(1, len(p)):
            if p[:k] in S:
                return False, "prefix"
    kr = sum(Fr(1, 2 ** len(p)) for p in paths)
    return kr == 1, "Kraft %s" % kr


def corner_rect(c, w):
    lo, hi = Fr(0), 1 + w
    return {"BL": (lo, hi, lo, hi), "BR": (S_RAT - hi, S_RAT, lo, hi),
            "TR": (S_RAT - hi, S_RAT, S_RAT - hi, S_RAT), "TL": (lo, hi, S_RAT - hi, S_RAT)}[c]


def pieces_of(rj):
    return [Box(*p) for p in rj["pieces"]]


def core_of(rj):
    return [(Fr(v[0]), Fr(v[1])) for v in rj["core"]]


def pose_in_role(p, rj):
    return any(in_box(p[0], p[1], p[2], b) for b in pieces_of(rj))


# ===================================================================== checks
def c1(T):
    lam = S_RAT / WLO
    w = (lam - 1) * (1 + 1 / SQ2_LO)
    if abs(float(w) - T["w"]) > 3e-9:
        fail("C1", "pad disagrees", mine=float(w), theirs=T["w"])
    gap = S_RAT - 2 * (1 + w) - SQ2_HI
    if gap <= 0:
        fail("C1", "(R6) fails")
    note("C1", "w = %.9f, (R6) gap %+.6f" % (float(w), float(gap)))
    H = Box(*T["H"]["box"])
    rng = random.Random(168)
    for c in ("BL", "BR", "TR", "TL"):
        cell = [float(v) for v in corner_rect(c, w)]
        mine = box_misses_cell_full(H, cell)
        if T["M"][c]["misses"] and not mine:
            fail("C1", "M(%s) = 0 claimed but not re-proved" % c)
        hits = 0
        for _ in range(50000):
            cx = H.x0 + (H.x1 - H.x0) * rng.random()
            cy = H.y0 + (H.y1 - H.y0) * rng.random()
            th = math.radians(H.th0 + (H.th1 - H.th0) * rng.random())
            if sq_meets_rect(cx, cy, th, cell):
                hits += 1
        if mine and hits:
            fail("C1", "M(%s) = 0 but sampled poses of H meet the cell" % c, hits=hits)
        note("C1", "M(%s): own SAT misses=%s (emitter %s), sampled meeting poses %d/50000"
             % (c, mine, T["M"][c]["misses"], hits))
    return w


def check_cover(tag, cov, roles_json, cell, line):
    root = Box(*cov["root"])
    paths = [lf["path"] for lf in cov["leaves"]] + [o["path"] for o in cov["open"]]
    ok, why = prefix_complete(paths)
    if not ok:
        fail("C2", "%s: cover not a complete prefix code (%s)" % (tag, why))
    bad = 0
    cnt = {}
    for lf in cov["leaves"]:
        b = replay(root, lf["path"])
        r = lf["why"]
        cnt[r] = cnt.get(r, 0) + 1
        if r == "container":
            good = box_outside_container(b)
        elif r == "misses_cell":
            good = cell is not None and box_misses_cell_full(b, cell)
        elif r == "witness":
            wq = (Fr(lf["w"][0]), Fr(lf["w"][1]))
            rj = roles_json.get(lf["j"])
            good = rj is not None and PC.vertex_ok(wq[0], wq[1], b) and all(
                PC.vertex_ok(wq[0], wq[1], pb) for pb in pieces_of(rj))
        elif r == "not_band":
            good = line is not None and out_all(b, *line)
        elif r == "band":
            good = line is not None and band_all(b, *line)
        else:
            good = False
        if not good:
            bad += 1
    if bad:
        fail("C2", "%s: %d discharged leaves fail the own test" % (tag, bad))
    for o in cov["open"]:
        rb = replay(root, o["path"])
        if max(abs(a - b) for a, b in zip([rb.x0, rb.x1, rb.y0, rb.y1, rb.th0, rb.th1], o["box"])) > 1e-9:
            fail("C2", "%s: an open box disagrees with the replayed split" % tag)
            break
    STATS["covers"] = STATS.get("covers", 0) + 1
    return cnt, bad


def check_roles(T, w):
    """C3 (pieces subset of the source, clip falsification) and C4 (cores certified)."""
    rng = random.Random(1680)
    n_roles = n_bad_sub = n_bad_core = tested = clear = 0
    for p, node in T["nodes"].items():
        roles = node.get("roles") or {}
        if not roles or not (node["verdict"].startswith("ALIVE") or node["verdict"].startswith("DEAD")):
            continue
        for nm, rj in roles.items():
            n_roles += 1
            src = Box(*rj["src"]) if rj.get("src") else None
            P = pieces_of(rj)
            for b in P:
                if src is not None and not (src.x0 - 1e-9 <= b.x0 and b.x1 <= src.x1 + 1e-9
                                            and src.y0 - 1e-9 <= b.y0 and b.y1 <= src.y1 + 1e-9
                                            and src.th0 - 1e-9 <= b.th0 and b.th1 <= src.th1 + 1e-9):
                    n_bad_sub += 1
            core = core_of(rj)
            for (vx, vy) in core:
                if not all(PC.vertex_ok(vx, vy, b) for b in P):
                    n_bad_core += 1
                    break
            kx, ky, a = Fr(rj["axis_core"]["kx"]), Fr(rj["axis_core"]["ky"]), Fr(rj["axis_core"]["a"])
            if a > 0 and not all(PC.vertex_ok(kx + sx * a, ky + sy * a, b) for b in P
                                 for sx in (-1, 1) for sy in (-1, 1)):
                n_bad_core += 1
        # clip falsification on ALIVE nodes: an admissible pose in src \ pieces of a role must
        # overlap some OTHER role's axis core (else the clip removed a free admissible pose)
        if not node["verdict"].startswith("ALIVE"):
            continue
        for nm, rj in roles.items():
            if not rj.get("src"):
                continue
            src = Box(*rj["src"])
            P = pieces_of(rj)
            others = [(float(Fr(v["axis_core"]["kx"])), float(Fr(v["axis_core"]["ky"])),
                       float(Fr(v["axis_core"]["a"]))) for k, v in roles.items() if k != nm]
            for _ in range(120):
                cx = src.x0 + (src.x1 - src.x0) * rng.random()
                cy = src.y0 + (src.y1 - src.y0) * rng.random()
                thd = src.th0 + (src.th1 - src.th0) * rng.random()
                if any(in_box(cx, cy, thd, b) for b in P):
                    continue
                th = math.radians(thd)
                h = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
                if not (h <= cx <= S0 - h and h <= cy <= S0 - h):
                    continue
                tested += 1
                V = sq_verts(cx, cy, th)
                if not any(a_ > 0 and sat_gap_polys(V, [(kx - a_, ky - a_), (kx + a_, ky - a_),
                                                         (kx + a_, ky + a_), (kx - a_, ky + a_)]) < 0
                           for (kx, ky, a_) in others):
                    clear += 1
    if n_bad_sub:
        fail("C3", "%d pieces are not subsets of their source box" % n_bad_sub)
    if clear:
        fail("C3", "%d sampled admissible poses in clipped-away regions are clear of every other core"
             % clear, tested=tested)
    if n_bad_core:
        fail("C4", "%d cores fail vertex_ok against a piece" % n_bad_core)
    note("C3", "%d roles: pieces subsets (%d bad); clip falsification %d poses, %d clear" % (
        n_roles, n_bad_sub, tested, clear))
    note("C4", "%d roles: core polygons and axis cores re-certified (%d bad)" % (n_roles, n_bad_core))


def check_invariant_and_verdicts(T):
    rng = random.Random(16800)
    n = dict(alive=0, inv_bad=0, ovl=0, ovl_bad=0, pair=0, pair_bad=0, row=0, row_bad=0, prune=0,
             prune_bad=0)
    for p, node in T["nodes"].items():
        roles = node.get("roles") or {}
        v = node["verdict"]
        if v.startswith("ALIVE") and roles and not (node.get("step") or "").endswith("complement"):
            n["alive"] += 1
            cores = {nm: core_of(rj) for nm, rj in roles.items()}
            for nm, C in cores.items():
                if not C or not all(0 <= q[0] <= S_RAT and 0 <= q[1] <= S_RAT for q in C):
                    n["inv_bad"] += 1
            names = list(cores)
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    if not polys_disjoint_exact(cores[names[i]], cores[names[j]]):
                        n["inv_bad"] += 1
                        fail("C5", "ALIVE node with meeting cores", node=p, pair=[names[i], names[j]])
        elif "OVL" in v:
            n["ovl"] += 1
            nm = v.split("every pose of ")[1].split(" overlaps")[0], v.split("every pose of ")[2].split(" (")[0] \
                if "every pose of" in v else (None, None)
            if nm[0] and node.get("parent") in T["nodes"]:
                par = T["nodes"][node["parent"]]
                # the dead pair: the parent's role (or the src box) vs the new src box
                A = [Box(*q) for q in par["roles"][nm[0]]["pieces"]] if nm[0] in par["roles"] else \
                    [Box(*node["src_box"])]
                Bx = [Box(*q) for q in par["roles"][nm[1]]["pieces"]] if nm[1] in par["roles"] else \
                    [Box(*node["src_box"])]
                ok = True
                for _ in range(300):
                    ba, bb = rng.choice(A), rng.choice(Bx)
                    a1 = (ba.x0 + (ba.x1 - ba.x0) * rng.random(), ba.y0 + (ba.y1 - ba.y0) * rng.random(),
                          math.radians(ba.th0 + (ba.th1 - ba.th0) * rng.random()))
                    a2 = (bb.x0 + (bb.x1 - bb.x0) * rng.random(), bb.y0 + (bb.y1 - bb.y0) * rng.random(),
                          math.radians(bb.th0 + (bb.th1 - bb.th0) * rng.random()))
                    if sat_gap_polys(sq_verts(*a1), sq_verts(*a2)) > 1e-12:
                        ok = False
                        break
                if not ok:
                    n["ovl_bad"] += 1
        elif "PAIR" in v or "shared point" in v:
            n["pair"] += 1
            wit = node.get("witness")
            if wit and wit.get("certified"):
                wq = (Fr(wit["w"][0]), Fr(wit["w"][1]))
                par = T["nodes"][node["parent"]]
                names = wit["pair"]
                pcs = []
                for nm in names:
                    if nm in par["roles"]:
                        pcs += pieces_of(par["roles"][nm])
                    else:
                        pcs += [Box(*node["src_box"])]
                if not all(PC.vertex_ok(wq[0], wq[1], b) for b in pcs):
                    n["pair_bad"] += 1
        elif "chord row" in v and node.get("rows"):
            n["row"] += 1
            killed = False
            for wl, r in node["rows"].items():
                mine = []
                for nm, rj in roles.items():
                    mine.append(min(chord_min_over_box(b, r["orient"], r["off"]) for b in pieces_of(rj)))
                for a_, b_ in zip([Fr(x) for x in r["minchords"]], mine):
                    if a_ > b_ + Fr(1, 10 ** 12):
                        n["row_bad"] += 1
                if S_RAT - sum(mine) < 0:
                    killed = True
            if not killed:
                n["row_bad"] += 1
        elif v.startswith("PRUNED"):
            n["prune"] += 1
    for k in ("inv_bad", "ovl_bad", "pair_bad", "row_bad", "prune_bad"):
        if n[k]:
            fail("C5", "%s: %d" % (k, n[k]))
    note("C5", "invariant re-decided on %d alive nodes (%d bad); OVL %d (%d bad), PAIR %d (%d bad), "
         "rows %d (%d bad), labelling prunes %d" % (n["alive"], n["inv_bad"], n["ovl"], n["ovl_bad"],
                                                    n["pair"], n["pair_bad"], n["row"], n["row_bad"], n["prune"]))


def check_canary(T):
    for im in T["canary"]["images"]:
        Z = im["poses"]
        for i in range(11):
            for j in range(i + 1, 11):
                if sat_gap_polys(sq_verts(Z[i][0], Z[i][1], math.radians(Z[i][2])),
                                 sq_verts(Z[j][0], Z[j][1], math.radians(Z[j][2]))) < -1e-9:
                    fail("C6", "image squares %d,%d overlap" % (i, j))
        for k in range(1, 9):
            nodes = im.get("S%d_nodes" % k)
            if nodes is None:
                continue
            good = []
            for p in nodes:
                node = T["nodes"].get(p)
                if node is None or not node.get("roles") or not node["verdict"].startswith("ALIVE"):
                    continue
                used = set()
                ok = True
                for nm, rj in node["roles"].items():
                    js = [j for j in range(11) if pose_in_role(Z[j], rj) and j not in used]
                    if not js:
                        ok = False
                        break
                    used.add(js[0])
                if ok:
                    good.append(p)
            built = any(n.get("step") == "S%d" % k for n in T["nodes"].values())
            if built and not good:
                fail("C6", "canary %s: no alive node at S%d holds the real family" % (im["image"], k))
            note("C6", "canary %s S%d: %d alive nodes hold the real family (distinct squares per role)"
                 % (im["image"], k, len(good)))


def check_lp(T, cell):
    import exactcore                                              # noqa: E402  trusted base (A135)
    p = os.path.join(RES, "lp_%s.jsonl" % cell)
    if not os.path.exists(p):
        note("C7", "no LP records")
        return
    n = bad = 0
    for ln in open(p, encoding="utf-8"):
        r = json.loads(ln)
        n += 1
        if r["budget"] != 11 - len(r["boxes"]):
            bad += 1
        boxes = [Box(**b) for b in r["boxes"]]
        for b, ae in zip(boxes, r.get("a_exact", [])):
            a, _a0, ok = exactcore.exact_a(b)
            if not ok or abs(float(a) - ae) > 1e-12:
                bad += 1
        node = T["nodes"].get(r["node"])
        if node and node.get("roles"):
            for b, (nm, rj) in zip(boxes, node["roles"].items()):
                bb = Box(*rj["box"])
                if max(abs(x - y) for x, y in zip([b.x0, b.x1, b.y0, b.y1, b.th0, b.th1],
                                                  [bb.x0, bb.x1, bb.y0, bb.y1, bb.th0, bb.th1])) > 1e-9:
                    bad += 1
    if bad:
        fail("C7", "%d LP records inconsistent" % bad)
    note("C7", "%d LP records checked, %d bad" % (n, bad))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    a = ap.parse_args()
    T = json.load(open(os.path.join(RES, "tree_%s.json" % a.cell), encoding="utf-8"))
    print("A168 independent check of %s (%s)" % (a.cell, T.get("version")), flush=True)
    w = c1(T)
    nc = 0
    for p, node in T["nodes"].items():
        for step in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"):
            if step not in node or not isinstance(node[step], dict) or "cover" not in node[step]:
                continue
            cov = dict(node[step]["cover"])
            corner = CSTEP[step]
            cell = [float(v) for v in corner_rect(corner, w)]
            line = None
            if cov.get("line"):
                line = ("h" if cov.get("band_mode") and corner in ("TL", "TR") else "v", cov["line"])
            cnt, bad = check_cover("%s %s" % (step, p), cov, node["roles"], cell, line)
            nc += 1
            if nc <= 12:
                note("C2", "%s %s: %d leaves %s, %d open" % (step, p, len(cov["leaves"]), cnt, len(cov["open"])))
    note("C2", "%d covers checked" % nc)
    check_roles(T, w)
    check_invariant_and_verdicts(T)
    check_canary(T)
    check_lp(T, a.cell)
    out = dict(cell=a.cell, n_fail=len(FAILS), fails=FAILS, stats=STATS,
               verdict=("ALL_OK" if not FAILS else "FAIL"))
    json.dump(out, open(os.path.join(RES, "check168_%s.json" % a.cell), "w", encoding="utf-8"),
              indent=1, default=str)
    print("\nVERDICT %s (%d failures)" % (out["verdict"], len(FAILS)), flush=True)


CSTEP = {"S1": "TR", "S2": "TR", "S3": "BR", "S4": "BR", "S5": "TL", "S6": "TL", "S7": "BL", "S8": "BL"}

if __name__ == "__main__":
    main()
