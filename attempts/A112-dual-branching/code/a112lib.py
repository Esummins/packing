"""A112 -- dual-guided branching: shared helpers.

Layered on A111's `a111lib` (copied byte-for-byte here so `octagon.py` imports unchanged).  Adds

  * the A38 k0 level-1 node index (A113's un-killable cells) on top of A111's A57/A60/A61 index;
  * the SUPPORT object every ORDER function scores: the node LP's fractional placements with
    y > 0, de-duplicated into clusters;
  * the three ORDER functions of the brief -- load path, stranded space, hybrid -- and the
    LP-free scores they use (row mass struck out by the YES core; support mass removed by the NO
    family; the unusable-area variant);
  * the dense pose-pair sampler that every LP-free geometric count must pass before it is
    reported (A111's standing rule: >= 1e4 sampled pose pairs, zero counterexamples).

READ-ONLY on every campaign: node jsons are COPIED into results/nodes/<nid>.src.json first.
"""
from __future__ import annotations

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  MUST precede numpy

import glob, json, math, random, time
import numpy as np

import a111lib as L
from a111lib import (IV, S0, SHAT, S_RAT, gate, memstat, corners, half_width, axis_vec,  # noqa: F401
                     gap_axis, sat_gap, sat_argmax, wall_gaps, box_iv, w_range, d4_ops,
                     D4_INV, slot_xy, shadow, tmod_deg)
from caselp import Box, NoFam, Hyp
import octagon as OCT
import trim57
from pinguard import classify as pin_classify

BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
# A run tag isolates one measurement pass from another: earlier partial passes are LEFT IN PLACE
# (nothing is ever deleted) and simply not read by the aggregator.  Set A112_RUN in the process.
RUN = os.environ.get("A112_RUN", "")
SUF = ("_" + RUN) if RUN else ""
RT = os.path.join(RES, "rt" + SUF)
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for d in (RES, NODES, RT, LOGS, CERTS):
    os.makedirs(d, exist_ok=True)

A107R = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A113R = os.path.join(ROOT, "attempts", "A113-k0-manifold-distance", "results")
A111R = os.path.join(ROOT, "attempts", "A111-loadpath-branch", "results")

# A57's slack pin cores (tree57.build_children, pin_delta = 1e-2)
PIN_DELTA = 1e-2
PIN_SLACK = PIN_DELTA / math.sqrt(2.0)
CLASS_PINS = {
    "k5_11": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BL(1,0)", "BR(0,0)"),
    "k5_16": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BR(0,0)", "TR(0,0)"),
    "trump5": ("BL(0,0)", "BL(1,0)", "BL(0,1)", "BR(0,0)", "TR(0,0)"),
}


# ------------------------------------------------------------------ node index (READ-ONLY)
SRC_GLOB = dict(L.SRC_GLOB)
SRC_GLOB["A38"] = "attempts/A38-root-power/results/l1_nodes/*.json"
SRC_GLOB["A85"] = "attempts/A85-*/results/**/*.json"
_INDEX = None


def node_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for src, pat in SRC_GLOB.items():
            for p in glob.glob(os.path.join(ROOT, pat), recursive=True):
                nid = os.path.splitext(os.path.basename(p))[0]
                _INDEX.setdefault((src, nid), p)
                _INDEX.setdefault(nid, p)
    return _INDEX


def copy_node(nid, src=None, path=None):
    """Copy a campaign's node json into our own results/nodes/ before anything reads it."""
    dst = os.path.join(NODES, nid + ".src.json")
    if not os.path.exists(dst):
        p = path
        if p is None or not os.path.exists(p):
            p = node_index().get((src, nid)) or node_index().get(nid)
        if p is None:
            return None
        with open(p, "rb") as f:
            b = f.read()
        with open(dst, "wb") as f:
            f.write(b)
    return dst


# ------------------------------------------------------------------ boxes / hypotheses
def box_json(b):
    return dict(x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, th0=b.th0, th1=b.th1)


def is_pin_box(b, tol=1e-12):
    return (b.x1 - b.x0 <= 2 * PIN_SLACK + tol and b.y1 - b.y0 <= 2 * PIN_SLACK + tol
            and b.th1 - b.th0 <= tol)


def split_hyp(hyp):
    """(pin boxes, conditioned bins) of a node hypothesis, by A57's emission shape: a pin is a
    degenerate (or slack-square) box at tilt 0."""
    pins = [b for b in hyp.boxes if is_pin_box(b)]
    bins = [b for b in hyp.boxes if not is_pin_box(b)]
    return pins, bins


def pin_slots(pins):
    return [(0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)) for b in pins]


def normalise_tilt(b):
    """the box as one or two boxes with tilt inside [0, 90] (A111 bug (ii): every |cos|+|sin|
    envelope in pinguard/trim57 is stated on that domain and must never be fed anything else)."""
    return OCT.normalised(b)


def assert_core_half_side(b):
    """every core used by a kill must have half-side <= 1/2 on every tilt branch."""
    out = []
    for nb in normalise_tilt(b):
        c = OCT.safe_kill_core(nb)
        if c is None:
            return None
        a = float(c.a)
        assert a <= 0.5 + 1e-12, "core half-side %.6f > 1/2 on [%g, %g]" % (a, nb.th0, nb.th1)
        out.append(a)
    return max(out)


# ------------------------------------------------------------------ the support
def support(res, ytol=1e-6, cluster=0.02, cluster_deg=2.0, cap=400):
    """The node LP's dual support as branch candidates: the fractional placements with y > 0,
    clustered so near-duplicates (the same physical placement re-generated by column generation)
    count once.  Returns [dict(cx, cy, theta_deg, y, n)] sorted by descending mass."""
    P = [(float(p["cx"]), float(p["cy"]), float(p["theta"]), float(p.get("y", 0.0)))
         for p in (res.get("packing") or []) if float(p.get("y", 0.0)) > ytol]
    P.sort(key=lambda q: -q[3])
    out = []
    for (cx, cy, th, y) in P[:cap * 4]:
        td = math.degrees(th) % 90.0
        hit = None
        for o in out:
            dth = abs(o["theta_deg"] - td)
            dth = min(dth, 90.0 - dth)
            if abs(o["cx"] - cx) <= cluster and abs(o["cy"] - cy) <= cluster and dth <= cluster_deg:
                hit = o
                break
        if hit is None:
            out.append(dict(cx=cx, cy=cy, theta_deg=td, y=y, n=1))
        else:
            hit["y"] += y
            hit["n"] += 1
    out.sort(key=lambda o: -o["y"])
    return out[:cap]


def cand_box(p, r, rho, s=None):
    """F = [c +- r] x [theta +- rho], with the tilt interval CLAMPED into [0, 90].

    The clamp matters and is not cosmetic.  `caselp.Box` is documented on 0 <= th0 <= th1 <= 90 and
    every downstream tool is stated there: `pinguard.tight_a` and `trim57.dead_by_pin` RAISE on a
    negative interval (A111 bug B5's fix), `octagon.safe_kill_core` refuses it, and the frozen
    parametric verifier rejects a core with tm outside [0, 1].  A support placement at tilt 0 with
    rho = 10 deg would otherwise produce [-10, 10] and silently switch every free kill off.

    Clamping SHRINKS the YES box (the wrapped part [90 - x, 90] is dropped), which is sound: the
    branch is "some square's pose in F" vs "no square's pose in F" for whichever F is chosen, and
    that is a tautology for every F.  The NO sibling uses the same clamped F, so the two children
    still cover the parent exactly.
    """
    t0 = max(0.0, min(90.0, p["theta_deg"] - rho))
    t1 = max(0.0, min(90.0, p["theta_deg"] + rho))
    if t1 <= t0:
        t0, t1 = max(0.0, min(t0, 90.0 - 1e-6)), min(90.0, max(t1, 1e-6))
    return Box(p["cx"] - r, p["cx"] + r, p["cy"] - r, p["cy"] + r, t0, t1)


# ------------------------------------------------------------------ LP-free scores
def _core_depth(core, cx, cy, th):
    """SAT depth of the unit square Q(c, th) against a core square (>0 means they overlap).
    Exactly caselp.Core.depth's geometry, evaluated in floats."""
    a = float(core.a)
    kx, ky = float(core.kx), float(core.ky)
    cm, sm = float(core.cm), float(core.sm)
    c, s = math.cos(th), math.sin(th)
    dx, dy = cx - kx, cy - ky
    best = 1e18
    for (ax, ay, ha, hb) in ((cm, sm, a, None), (-sm, cm, a, None), (c, s, 0.5, None), (-s, c, 0.5, None)):
        d = abs(dx * ax + dy * ay)
        if ha == a:                                   # core axis: support of Q is (|cos|+|sin|)/2
            w = 0.5 * (abs(ax * c + ay * s) + abs(-ax * s + ay * c))
            lim = a + w
        else:                                         # square axis: support of the core
            w = a * (abs(ax * cm + ay * sm) + abs(-ax * sm + ay * cm))
            lim = 0.5 + w
        best = min(best, lim - d)
    return best


def rows_struck(F, sup, eps=1e-9):
    """The LP row mass the YES core of F strikes out: the support mass whose square is FORCED to
    overlap K(F) (so its covering row is exempt once a square is conditioned into F).  No LP."""
    tot, hits = 0.0, 0
    for nb in normalise_tilt(F):
        core = OCT.safe_kill_core(nb)
        if core is None:
            return 0.0, 0
        for q in sup:
            if _core_depth(core, q["cx"], q["cy"], math.radians(q["theta_deg"])) > eps:
                tot += q["y"]
                hits += 1
    return tot, hits


def nofam_mass(F, sup, s):
    """The support mass the NO-family of F removes: the placements inside the zone."""
    nf = NoFam(max(0.5, min(F.x0, s - 0.5)), max(0.5, min(F.x1, s - 0.5)),
               max(0.5, min(F.y0, s - 0.5)), max(0.5, min(F.y1, s - 0.5)),
               OCT.theta_intervals(F.th0, F.th1))
    NoFam.s_hi = s - 0.5
    tot, hits = 0.0, 0
    for q in sup:
        if nf.contains(q["cx"], q["cy"], q["theta_deg"]):
            tot += q["y"]
            hits += 1
    return tot, hits


def _poly_clip(poly, ax, ay, lim):
    """half-plane clip {p : p.(ax,ay) <= lim} of a convex polygon."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp = p[0] * ax + p[1] * ay - lim
        dq = q[0] * ax + q[1] * ay - lim
        if dp <= 0:
            out.append(p)
        if (dp < 0 < dq) or (dq < 0 < dp):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def _area(poly):
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def unusable_area(F, ntheta=9):
    """The 'unusable area' variant of the stranded score: the mean over the tilt interval of the
    area of the octagon {c : Q(c, theta) meets K(F)} = K(F) (+) (-Q(0, theta)), the exact centre
    region that F's core forbids to every OTHER square.  Convex-polygon intersection, exact per
    tilt, averaged on a grid (a shape descriptor, not a certified quantity)."""
    tot, k = 0.0, 0
    for nb in normalise_tilt(F):
        core = OCT.safe_kill_core(nb)
        if core is None:
            continue
        a = float(core.a)
        cm, sm = float(core.cm), float(core.sm)
        for i in range(ntheta):
            th = math.radians(nb.th0 + (nb.th1 - nb.th0) * (i / max(1, ntheta - 1.0)))
            c, s = math.cos(th), math.sin(th)
            w = abs(c) + abs(s)
            A = w / 2.0 + a                     # half-width along the core's own axes
            B = 0.5 + a * w                     # half-width along the square's axes
            poly = [(-9, -9), (9, -9), (9, 9), (-9, 9)]
            for (ax, ay, lim) in ((cm, sm, A), (-cm, -sm, A), (-sm, cm, A), (sm, -cm, A),
                                  (c, s, B), (-c, -s, B), (-s, c, B), (s, -c, B)):
                poly = _poly_clip(poly, ax, ay, lim)
                if not poly:
                    break
            tot += _area(poly) if poly else 0.0
            k += 1
    return tot / max(1, k)


# ------------------------------------------------------------------ PIN WASTAGE (PI, 2026-09-06)
def _core_of(b):
    """the tight common inscribed core of a box, on every normalised tilt branch (a list)."""
    out = []
    for nb in normalise_tilt(b):
        c = OCT.safe_kill_core(nb)
        if c is not None:
            out.append(c)
    return out


def _blocked_mask(core, GX, GY, c, s_):
    """boolean mask over the centre grid: Q(centre, theta) OVERLAPS `core` (depth > 0).
    Vectorised copy of caselp.Core.depth_many's four-axis SAT test."""
    a = float(core.a); kx, ky = float(core.kx), float(core.ky)
    cm, sm = float(core.cm), float(core.sm)
    g = abs(c * cm + s_ * sm) + abs(-s_ * cm + c * sm)
    dx = GX - kx; dy = GY - ky
    pe1 = np.abs(dx * cm + dy * sm)
    pe2 = np.abs(-dx * sm + dy * cm)
    pf1 = np.abs(dx * c + dy * s_)
    pf2 = np.abs(-dx * s_ + dy * c)
    return (a + 0.5 * g - pe1 > 0) & (a + 0.5 * g - pe2 > 0) & \
           (0.5 + a * g - pf1 > 0) & (0.5 + a * g - pf2 > 0)


class Wastage:
    """The stranded-AREA instrument.  A container point c is USABLE if some tilt theta admits a
    unit square centred at c that (i) fits between the walls and (ii) overlaps NONE of the
    blockers -- the class pins' cores, the node's other conditioned bins' cores, and (when a
    candidate is scored) the candidate box's own core.  Everything a square with pose in F
    contains, K(F) contains, so a blocker core is a sound obstruction for every OTHER square.

    wastage(F) = area(unusable | pins, walls, bins, F) - area(unusable | pins, walls, bins),
    i.e. the POCKET the candidate creates.  Pure geometry on a centre grid x tilt grid; no LP.
    It is a branching SCORE, not a certified quantity: the grid makes it an estimate of an area,
    and no kill is ever claimed from it."""

    def __init__(self, s, blockers, step=0.02, ntheta=19):
        self.s, self.step = s, step
        xs = np.arange(0.5, s - 0.5 + 1e-12, step)
        self.GX, self.GY = np.meshgrid(xs, xs, indexing="ij")
        self.cell = step * step
        self.thetas = [math.radians(t) for t in np.linspace(0.0, 90.0, ntheta)]
        self.base = []                                  # per tilt: admissible mask
        for th in self.thetas:
            c, s_ = math.cos(th), math.sin(th)
            w = 0.5 * (abs(c) + abs(s_))
            ok = (self.GX >= w) & (self.GX <= s - w) & (self.GY >= w) & (self.GY <= s - w)
            for core in blockers:
                ok &= ~_blocked_mask(core, self.GX, self.GY, c, s_)
            self.base.append(ok)
        self.base_usable = np.zeros_like(self.base[0])
        for ok in self.base:
            self.base_usable |= ok
        self.base_unusable_area = float((~self.base_usable).sum()) * self.cell

    def score(self, F):
        cores = _core_of(F)
        if not cores:
            return 0.0
        usable = np.zeros_like(self.base[0])
        for th, ok in zip(self.thetas, self.base):
            c, s_ = math.cos(th), math.sin(th)
            m = ok.copy()
            for core in cores:
                m &= ~_blocked_mask(core, self.GX, self.GY, c, s_)
            usable |= m
        return float((~usable).sum()) * self.cell - self.base_unusable_area


def spearman(a, b):
    """rank correlation, ties averaged (no scipy: this runs inside the BLAS-pinned worker)."""
    n = len(a)
    if n < 3:
        return None

    def ranks(v):
        idx = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[idx[j + 1]] == v[idx[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[idx[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(list(a)), ranks(list(b))
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    if da == 0 or db == 0:
        return None
    return num / (da * db)


# ------------------------------------------------------------------ the load path in a node frame
_SHADOW_NODES = None
_EXTRACT = None


def shadow_nodes(tag):
    global _SHADOW_NODES
    if _SHADOW_NODES is None:
        _SHADOW_NODES = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))
    return _SHADOW_NODES.get(tag, [])


def extract_index():
    global _EXTRACT
    if _EXTRACT is None:
        _EXTRACT = {(n["src"], n["nid"]): n for n in
                    json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]}
    return _EXTRACT


def loadpath_rank(tag, cls):
    """The Fritz-John weight of each member of the shadow's load path: the number of LOADED
    contacts it carries among the (load path + class pin) squares, read off the closed-form SAT
    gap at the shadow's own configuration (A111 `t1_yes.loaded_pairs`, never a finite difference).
    Members of the load path proper outrank the anchors."""
    import t1_yes as T1
    pn = CLASS_PINS.get(cls, tuple(L.shadow(tag)[3]))
    lp = list(L.shadow(tag)[5])
    pairs = T1.loaded_pairs(tag, pn)
    cnt = {}
    for (a, b) in pairs:
        cnt[a] = cnt.get(a, 0) + 1
        cnt[b] = cnt.get(b, 0) + 1
    return {n: (0 if n in lp else 1, -cnt.get(n, 0)) for n in set(list(cnt) + lp)}, set(lp)


def loadpath_boxes(tag, cls, r, rho, op, s, with_anchors=True):
    """The shadow's load-bearing free squares (+ anchors) as boxes in the NODE's own frame.
    A111's construction: boxes at the shadow's own poses, mapped by the inverse of A107's
    struct_op (a D4 isometry of the container)."""
    import t1_yes as T1
    pn = CLASS_PINS.get(cls, tuple(L.shadow(tag)[3]))
    ext = T1.anchors(tag, pn) if with_anchors else ()
    _, _, _, _, _, names, B = T1.make_boxes(tag, r, rho, extra=ext)
    inv = D4_INV[op]
    f = d4_ops(s)[inv]
    out = {}
    for n in names:
        b = B[n]
        xs, ys = [], []
        for (x, y) in ((b["x0"], b["y0"]), (b["x1"], b["y0"]), (b["x0"], b["y1"]), (b["x1"], b["y1"])):
            X, Y, _ = f(x, y, 0.0)
            xs.append(X); ys.append(Y)
        flip = inv in ("mx", "my", "diag", "anti")
        t0, t1 = (-b["th1"], -b["th0"]) if flip else (b["th0"], b["th1"])
        out[n] = Box(min(xs), max(xs), min(ys), max(ys), t0, t1)
    return out


# ------------------------------------------------------------------ dense pose sampling (the rule)
def sample_pair(a, b, n=400, seed=0):
    """Dense random pose pairs inside two boxes.  Returns (worst SAT gap, counterexamples), where
    a counterexample is a sampled pair that does NOT overlap -- i.e. a refutation of a claimed
    geometric kill.  A111's standing rule: no LP-free geometric count is reported before every
    fire has passed this."""
    rng = random.Random(seed)
    worst, bad = -1e18, 0
    for _ in range(n):
        ca = (rng.uniform(a.x0, a.x1), rng.uniform(a.y0, a.y1))
        ta = math.radians(rng.uniform(a.th0, a.th1))
        cb = (rng.uniform(b.x0, b.x1), rng.uniform(b.y0, b.y1))
        tb = math.radians(rng.uniform(b.th0, b.th1))
        g = sat_gap(ca, ta, cb, tb)
        worst = max(worst, g)
        if g >= 0.0:
            bad += 1
    return worst, bad


# ------------------------------------------------------------------ misc
def jdump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mklog(name):
    p = os.path.join(LOGS, name)

    def log(*x):
        m = " ".join(str(v) for v in x)
        print(m, flush=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + m + "\n")
    return log
