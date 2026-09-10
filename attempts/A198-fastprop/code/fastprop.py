"""A198 -- FASTPROP: cheap exact propagation over a page node (pins + H + instantiated meeters), n-general.

The PI's design (2026-09-10 11:30): propagate with CHEAP exact tests before any bisection/LP, and only call the
expensive tests where the cheap ones leave a genuine ambiguity.  Every pruning here is one of

  DEAD-CELL   multibox's exact dead test (A171 `dead_poly` via `_clip_rect_obstacle`) of a (centre rect x tilt bin)
              piece against a role's K' -- a free square there would meet the role's square; plus the container
              clip at w_min (A171 `container_clip`, strict=False);
  MISS        A161's exact separating-axis test `box_misses_cell_exact`: every pose of the piece misses the widened
              open slot box, so the piece holds no meeter of that slot;
  LONELY      A169 Theorem B's lonely clip (A173 `_clip_rect_lonely`) at CORNER slots only;
  A1          Lemma A1 (sideband.md): interior-disjoint unit squares have centres at l-inf distance >= 1/sqrt2, so a
              closed cell of side < 1/sqrt2 holds the centre of at most ONE square of the packing;
  FC          Theorem FC (forced_corners.md): every usable forced cell has TWO DISTINCT NON-pin meeters of its widened
              open box, i.e. from {H} u {the free squares};
  CHORD       the open-chord row (A144/A190 `guardlines_v5.minchord`, OPEN chords): the chords of the distinct squares
              of one packing on a line sum to <= s.

The engine (fastprop.run_page):
  (a) a global grid of cells of side < 1/sqrt2 over the centre range; per (cell, slot) the cell n window is bisected
      (4 tilt sub-bins, depth D) with DEAD-CELL + MISS (+ LONELY at corners): the surviving pieces = where a free
      meeter of the slot with its centre in the cell can be; cached;
  (b) forced clips: a slot with <= 1 alive cell and H able to reach it forces H (FC + A1); a slot H provably misses
      with <= 1 alive cell is DEAD (A1); H forced at a set of slots is clipped to the pieces not provably missing
      all of them (MISS) -- empty => DEAD; a forced free meeter at a cell is INSTANTIATED as a role (box = cell n
      window, tilt 0..90) so that multibox's mutual clip carries it into H and the other cells;
  (c) the JOINT count: a free square at cell g meets a set S of slots only if the exact reach test on the
      intersection of the windows (DEAD-CELL + MISS for every slot of S) leaves a piece; the placements (g, S) with
      their chords are the option table; an exact search asks whether H + the (n - #pins - 1) free squares can cover
      every slot twice with pairwise-distinct cells (A1) and chord rows <= s (CHORD).  Infeasible => DEAD;
      infeasible with H barred from a slot => H forced there (b);
  (d) if the count leaves options: A178's geo178b.slot_pair_test (fine setting) on the most constrained slot.
Every step is timed and every pruning recorded with its test; the certificate is the list of exact tests.
"""
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A178-gallery-geometry", "code"), os.path.join(ATT, "A190-guardline-clause", "code"),
           os.path.join(ATT, "A161-chord-lane", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import geo178 as G                                             # noqa: E402  READ-ONLY (A178; imports A171 multibox + mbpatch178)
import classes178 as CL                                        # noqa: E402  READ-ONLY (A178)
import multibox as MB                                          # noqa: E402  READ-ONLY (A171/A172/A173)
import guardlines_v5 as GV                                     # noqa: E402  READ-ONLY (A190)
import chordlane as CLN                                        # noqa: E402  READ-ONLY (A161)

S_RAT = MB.S_RAT
HALF = Fr(1, 2)
CELL_MAX = Fr(70, 100)                     # < 1/sqrt2 = 0.7071: one centre per closed cell (Lemma A1)
SQ2H_UP = Fr(7071067812, 10 ** 10)         # > 1/sqrt2
EPS = Fr(1, 10 ** 9)


# ----------------------------------------------------------------------------- bookkeeping
class Trace:
    """every step timed; every pruning recorded with its test and result."""

    def __init__(self, t0=None, wall=None):
        self.t0 = time.time() if t0 is None else t0
        self.wall = wall
        self.steps = []
        self.tests = []

    def now(self):
        return time.time() - self.t0

    def left(self):
        return None if self.wall is None else self.wall - self.now()

    def out_of_time(self):
        return self.wall is not None and self.now() > self.wall

    def step(self, name, seconds, **kw):
        d = dict(step=name, t=round(self.now(), 2), seconds=round(seconds, 3))
        d.update(kw)
        self.steps.append(d)
        return d

    def test(self, kind, **kw):
        d = dict(test=kind)
        d.update(kw)
        self.tests.append(d)
        return d


def fl(v):
    return float(v)


def rect_f(r):
    return [round(float(v), 6) for v in r]


# ----------------------------------------------------------------------------- the grid
def make_grid(s=S_RAT):
    """closed cells of side < 1/sqrt2 covering the centre range [1/2, s-1/2]^2."""
    n = int(math.ceil(float((s - 1) / CELL_MAX) - 1e-12))
    side = (s - 1) / n
    cells = []
    for i in range(n):
        for j in range(n):
            cells.append(dict(i=i, j=j, rect=(HALF + i * side, HALF + (i + 1) * side, HALF + j * side, HALF + (j + 1) * side)))
    return cells, side


def rect_inter(a, b):
    x0, x1, y0, y1 = max(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return (x0, x1, y0, y1)


def slot_geometry(item, s=S_RAT):
    """exact (outward-rounded) widened box and meeter window of a forced item.  A LARGER box only makes the MISS
    test harder to pass (sound); a LARGER window is a superset of the meeter centres (sound)."""
    W = item["wbox"]
    wb = (Fr(W[0]) - EPS, Fr(W[1]) + EPS, Fr(W[2]) - EPS, Fr(W[3]) + EPS)
    win = (max(HALF, wb[0] - SQ2H_UP), min(s - HALF, wb[1] + SQ2H_UP), max(HALF, wb[2] - SQ2H_UP), min(s - HALF, wb[3] + SQ2H_UP))
    return wb, win


# ----------------------------------------------------------------------------- the exact reach bisection
SQ2H_LO = Fr(7071067811, 10 ** 10)         # < 1/sqrt2


def obstacle_near(ob, rect):
    """False only when NO unit square with centre in rect can meet the obstacle's polygon (every point of the
    square is within 1/sqrt2 of the centre; the polygon's bounding box is at Euclidean distance > 1/sqrt2)."""
    if ob is None:
        return False
    vs = getattr(ob, "verts", None)
    if not vs:
        return True
    bx0, bx1 = min(v[0] for v in vs), max(v[0] for v in vs)
    by0, by1 = min(v[1] for v in vs), max(v[1] for v in vs)
    dx = max(Fr(0), Fr(bx0) - rect[1], rect[0] - Fr(bx1))
    dy = max(Fr(0), Fr(by0) - rect[3], rect[2] - Fr(by1))
    return dx * dx + dy * dy <= SQ2H_UP * SQ2H_UP


def bisect_region(rect, obst, wbs, s, stats, depth=6, nsub=4, corner=None, t_range=(Fr(0), Fr(1)), seed_pieces=None,
                  max_pieces=512):
    """pieces of (rect x tilt) NOT provably dead: container clip, DEAD-CELL against every obstacle, MISS for every
    widened box in `wbs`, LONELY at a corner.  -> (surviving volume fraction, pieces, n_tests)."""
    if seed_pieces is None:
        R = tuple(Fr(v) for v in rect)
        pieces = [(MB.Bin(a, b), R) for (a, b) in MB.sub_bins(t_range[0], t_range[1], nsub)]
    else:
        pieces = list(seed_pieces)
        if not pieces:
            return 0.0, [], 0
        R = pieces_hull(pieces)[:4]
    obst = [ob for ob in obst if obstacle_near(ob, R)]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    if vol0 <= 0:
        return 0.0, [], 0
    n_tests = 0
    for d in range(depth + 1):
        nxt = []
        for bn, r in pieces:
            cur, _ = MB.container_clip(r, bn, s, strict=False)
            if cur is None:
                n_tests += 1
                continue
            for ob in obst:
                if ob is None:
                    continue
                cur = MB._clip_rect_obstacle(cur, ob, bn, stats)
                n_tests += 1
                if cur is None:
                    break
            if cur is None:
                continue
            if corner is not None:
                cur = MB._clip_rect_lonely(cur, bn, corner, MB.C_WIDEN, s, 4, stats)
                n_tests += 1
                if cur is None:
                    continue
            if wbs:
                bx = MB.piece_box(bn, cur)[0]
                dead = False
                for wb in wbs:
                    n_tests += 1
                    if CLN.box_misses_cell_exact(bx, wb)[0]:
                        dead = True
                        break
                if dead:
                    continue
            if d < depth and len(pieces) <= max_pieces:
                nxt.extend(MB.split_piece(bn, cur))
            else:
                nxt.append((bn, cur))
        pieces = nxt
        if not pieces:
            return 0.0, [], n_tests
    vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    return float(vol / vol0), pieces, n_tests


def pieces_hull(pcs):
    return (min(r[0] for _, r in pcs), max(r[1] for _, r in pcs), min(r[2] for _, r in pcs), max(r[3] for _, r in pcs),
            min(b.t0 for b, _ in pcs), max(b.t1 for b, _ in pcs))


def pieces_volume(pcs):
    return sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pcs)


# ----------------------------------------------------------------------------- chord rows
def guard_lines(s=S_RAT):
    offs = [HALF, Fr(1), Fr(3, 2), s / 2, s - Fr(3, 2), s - 1, s - HALF]
    return [(o, off) for o in ("h", "v") for off in offs]


def minchord_pieces(pcs, lines):
    """min over the pieces of the exact OPEN min-chord on every line (a square whose pose is in one of the pieces has
    chord >= this)."""
    out = {}
    for (o, off) in lines:
        m = None
        for bn, r in pcs:
            c = GV.minchord(HALF, bn.t0, bn.t1, r[0], r[1], r[2], r[3], o, off)
            m = c if m is None else min(m, c)
            if m <= 0:
                break
        out[(o, off)] = Fr(0) if m is None else m
    return out


def minchord_box(box, lines):
    """a role's (x0,x1,y0,y1,th0,th1) box (degrees) -> exact min open chords."""
    t0, t1 = MB.t_lo(box[4]), MB.t_hi(box[5])
    x0, x1, y0, y1 = MB.PIN.outer_rect(MB.Box(*box))
    return {(o, off): GV.minchord(HALF, t0, t1, x0, x1, y0, y1, o, off) for (o, off) in lines}


# ----------------------------------------------------------------------------- the count search
class CountResult:
    def __init__(self, feasible, witness=None, nodes=0, capped=False):
        self.feasible, self.witness, self.nodes, self.capped = feasible, witness, nodes, capped


def a1_compatible(h1, h2):
    """Lemma A1: two distinct squares with centres in the hulls h1, h2 need SOME pair of centres at l-inf distance
    >= 1/sqrt2; impossible when both coordinate ranges are too close (compared with a LOWER bound of 1/sqrt2)."""
    mx = max(h1[1] - h2[0], h2[1] - h1[0])
    my = max(h1[3] - h2[2], h2[3] - h1[2])
    return mx >= SQ2H_LO or my >= SQ2H_LO


def count_search(slots, free_opts, fixed_opts, n_free, lines, base_chords, s, node_cap=200000, use_chords=True):
    """Exact cover search.  slots: list of slot names (demand 2 each, Theorem FC).  free_opts: [(cell, S, chords)]
    placements for anonymous free squares.  fixed_opts: {role: [(cell, S, chords)]} -- H and the instantiated
    roles, each a DISTINCT square that must take exactly one option.  n_free anonymous squares, each at most one
    option, pairwise-distinct cells with the fixed squares (A1).  Chord rows: base (pins) + chosen <= s on every
    line.  Feasible => a witness; infeasible => exhaustive (unless capped)."""
    names = list(fixed_opts)
    nodes = [0]
    capped = [False]
    by_slot = {p: [o for o in free_opts if p in o[1]] for p in slots}

    def chords_ok(ch):
        if not use_chords:
            return True
        return all(ch[L] <= s for L in lines)

    def add(ch, c):
        return {L: ch[L] + c[L] for L in lines}

    def compat(o, chosen):
        return all(a1_compatible(o[3], c[1][3]) for c in chosen)

    def rec_free(demand, used, ch, left, chosen):
        nodes[0] += 1
        if nodes[0] > node_cap:
            capped[0] = True
            return None
        need = [p for p in slots if demand[p] > 0]
        if not need:
            return list(chosen)
        if left == 0:
            return None
        tot = sum(demand[p] for p in need)
        # the slot with the fewest admissible placements first
        best, cands = None, None
        for p in need:
            cs = [o for o in by_slot[p] if o[0] not in used]
            if best is None or len(cs) < len(cands):
                best, cands = p, cs
            if not cs:
                return None
        maxS = max(len(o[1]) for o in free_opts) if free_opts else 0
        if left * maxS < tot:
            return None
        for o in cands:
            if not compat(o, chosen):
                continue
            ch2 = add(ch, o[2])
            if not chords_ok(ch2):
                continue
            d2 = dict(demand)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
            r = rec_free(d2, used | {o[0]}, ch2, left - 1, chosen + [("free", o)])
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    def rec_fixed(k, demand, used, ch, chosen):
        if k == len(names):
            return rec_free(demand, used, ch, n_free, chosen)
        for o in fixed_opts[names[k]]:
            if o[0] in used or not compat(o, chosen):
                continue
            ch2 = add(ch, o[2])
            if not chords_ok(ch2):
                continue
            d2 = dict(demand)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
            r = rec_fixed(k + 1, d2, used | {o[0]}, ch2, chosen + [(names[k], o)])
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    w = rec_fixed(0, {p: 2 for p in slots}, frozenset(), dict(base_chords), [])
    return CountResult(w is not None or capped[0], w, nodes[0], capped[0])


# ----------------------------------------------------------------------------- the page
class Page:
    def __init__(self, rec, cls, name, trace, depth=5, joint_depth=2, nsub_mb=4, refine_mb=2, n=11):
        self.rec, self.cls, self.name, self.T = rec, cls, name, trace
        self.depth, self.joint_depth = depth, joint_depth
        self.nsub_mb, self.refine_mb = nsub_mb, refine_mb
        self.s = S_RAT
        self.base = G.base_roles(rec)
        self.pins = {k: v for k, v in self.base.items() if k.startswith("P")}
        self.hnames = [k for k in self.base if k.startswith("H")]
        assert len(self.hnames) == 1, "one conditioned square per page"
        self.H = "H"
        self.roles = dict(self.base)                       # current boxes (pins, H hull, instantiated F roles)
        self.n_free = n - len(self.pins) - 1
        self.items = G.forced_items(cls, rec)
        for it in self.items:
            it["wb"], it["win"] = slot_geometry(it, self.s)
        self.slots = [it["cell"] for it in self.items]
        self.item = {it["cell"]: it for it in self.items}
        self.cells, self.side = make_grid(self.s)
        self.lines = guard_lines(self.s)
        self.pin_chords = {L: Fr(0) for L in self.lines}
        for k, b in self.pins.items():
            mc = minchord_box(b, self.lines)
            for L in self.lines:
                self.pin_chords[L] += mc[L]
        self.cell_role = {}                                # global cell index -> instantiated role name
        self.role_cell = {}
        self.forced_H = set()
        self.nd = None
        self.dead = None
        self.reach_cache = {}
        self.rounds = []

    # ------------------------------------------------------------------ node
    def normalise(self, label):
        t0 = time.time()
        nd = MB.Node(dict(self.roles), name=self.name + "/" + label)
        corners = {k: self.role_corner[k] for k in getattr(self, "role_corner", {}) if k in self.roles}
        try:
            nd.normalise(nsub=self.nsub_mb, refine=self.refine_mb, mode="poly", kmode="pieces", strict_container=False,
                         corners=corners or None, verbose=False)
        except MB.EmptyBox as e:
            self.T.step("normalise", time.time() - t0, label=label, dead=e.name)
            self.T.test("EMPTYBOX", role=e.name, label=label, roles={k: rect_f(v) for k, v in self.roles.items()})
            self.dead = "EmptyBox(%s) at %s" % (e.name, label)
            return None
        self.nd = nd
        self.obst = {k: nd.boxes[k].obstacle("poly") for k in nd.names}
        self.reach_cache = {}
        kept = {k: round(b.kept_fraction(), 4) for k, b in nd.boxes.items()}
        self.T.step("normalise", time.time() - t0, label=label, kept=kept, passes=nd.stats.get("passes"))
        return nd

    def obstacles_for_free(self):
        return [self.obst[k] for k in self.nd.names]

    def obstacles_except(self, role):
        return [self.obst[k] for k in self.nd.names if k != role]

    # ------------------------------------------------------------------ (a) cell reach
    def reach(self, ci, S):
        """surviving pieces of a free square with centre in cell ci meeting every slot of S (frozenset).  A joint set
        (|S| >= 2) is SEEDED from the single-slot survivors of its most constrained member, restricted to the other
        windows, and bisected `joint_depth` levels further with every MISS test (sound: every pose meeting all of S
        lies in every single-slot survivor set)."""
        key = (ci, S)
        if key in self.reach_cache:
            return self.reach_cache[key]
        rect = self.cells[ci]["rect"]
        for p in S:
            rect = rect_inter(rect, self.item[p]["win"]) if rect is not None else None
        if rect is None:
            res = (0.0, [], 0)
        else:
            t0 = time.time()
            corner = None
            for p in S:
                if self.item[p]["is_corner"]:
                    corner = self.item[p]["corner"]
            wbs = [self.item[p]["wb"] for p in S]
            if len(S) == 1:
                res = bisect_region(rect, self.obstacles_for_free(), wbs, self.s, self.nd.stats, depth=self.depth, corner=corner)
                depth = self.depth
            else:
                p0 = min(S, key=lambda q: self.reach(ci, frozenset([q]))[0])
                seed = []
                for bn, r in self.reach(ci, frozenset([p0]))[1]:
                    ri = rect_inter(r, rect)
                    if ri is not None:
                        seed.append((bn, ri))
                res = bisect_region(None, self.obstacles_for_free(), wbs, self.s, self.nd.stats, depth=self.joint_depth,
                                    corner=corner, seed_pieces=seed)
                depth = self.depth + self.joint_depth
            self.T.test("REACH", cell=ci, slots=sorted(S), rect=rect_f(rect), depth=depth, frac=round(res[0], 6),
                        n_pieces=len(res[1]), n_exact=res[2], lonely=corner, seconds=round(time.time() - t0, 3))
        self.reach_cache[key] = res
        return res

    def role_reach(self, role, S):
        """pieces of an instantiated role (or H) not provably missing every slot of S, re-clipped against the others."""
        key = (role, S)
        if key in self.reach_cache:
            return self.reach_cache[key]
        pcs = self.nd.boxes[role].pieces
        t0 = time.time()
        res = bisect_region(None, self.obstacles_except(role), [self.item[p]["wb"] for p in S], self.s, self.nd.stats,
                            depth=2, seed_pieces=pcs)
        self.T.test("ROLE-REACH", role=role, slots=sorted(S), frac=round(res[0], 6), n_pieces=len(res[1]), n_exact=res[2],
                    seconds=round(time.time() - t0, 3))
        self.reach_cache[key] = res
        return res

    def role_cells(self, role):
        """global cells the role's surviving pieces touch."""
        pcs = self.nd.boxes[role].pieces
        out = []
        for ci, c in enumerate(self.cells):
            if any(rect_inter(c["rect"], r) is not None for _, r in pcs):
                out.append(ci)
        return out

    def role_pieces_in_cell(self, role, S, ci):
        _, pcs, _ = self.role_reach(role, S)
        out = []
        for bn, r in pcs:
            ri = rect_inter(r, self.cells[ci]["rect"])
            if ri is not None:
                out.append((bn, ri))
        return out

    # ------------------------------------------------------------------ option tables
    def build_options(self):
        t0 = time.time()
        free_opts = []
        single = {}                                  # slot -> {cell: frac}
        for p in self.slots:
            single[p] = {}
        n_cells_used = set(self.cell_role.values())
        for ci in range(len(self.cells)):
            if ci in self.cell_role:
                continue                             # an instantiated role sits there: no anonymous square (A1)
            reach1 = {}
            for p in self.slots:
                if rect_inter(self.cells[ci]["rect"], self.item[p]["win"]) is None:
                    continue
                fr, pcs, _ = self.reach(ci, frozenset([p]))
                if pcs:
                    reach1[p] = pcs
                    single[p][ci] = fr
            if not reach1:
                continue
            alive_sets = {frozenset([p]): pcs for p, pcs in reach1.items()}
            # upward closure: test S only when every (|S|-1)-subset is alive (monotone)
            for k in range(2, len(reach1) + 1):
                any_new = False
                for S in itertools.combinations(sorted(reach1), k):
                    S = frozenset(S)
                    if all((S - {q}) in alive_sets for q in S):
                        fr, pcs, _ = self.reach(ci, S)
                        if pcs:
                            alive_sets[S] = pcs
                            any_new = True
                if not any_new:
                    break
            for S, pcs in alive_sets.items():
                free_opts.append((ci, S, minchord_pieces(pcs, self.lines), pieces_hull(pcs)[:4]))
        fixed_opts = {}
        for role in [self.H] + sorted(self.role_cell):
            opts = []
            cells = self.role_cells(role)
            reach1 = [p for p in self.slots if self.role_reach(role, frozenset([p]))[1]]
            alive_sets = {frozenset(): None}
            for p in reach1:
                alive_sets[frozenset([p])] = True
            for k in range(2, len(reach1) + 1):
                any_new = False
                for S in itertools.combinations(reach1, k):
                    S = frozenset(S)
                    if all((S - {q}) in alive_sets for q in S) and self.role_reach(role, S)[1]:
                        alive_sets[S] = True
                        any_new = True
                if not any_new:
                    break
            for ci in cells:
                for S in alive_sets:
                    pcs = self.role_pieces_in_cell(role, S, ci)
                    if not pcs:
                        continue
                    opts.append((ci, S, minchord_pieces(pcs, self.lines), pieces_hull(pcs)[:4]))
            fixed_opts[role] = opts
        self.T.step("options", time.time() - t0, n_free_opts=len(free_opts),
                    n_fixed={r: len(v) for r, v in fixed_opts.items()},
                    alive_cells={p: len(v) for p, v in single.items()})
        return free_opts, fixed_opts, single

    # ------------------------------------------------------------------ (b)+(c) one propagation round
    def propagate_round(self, rnd):
        free_opts, fixed_opts, single = self.build_options()
        info = dict(round=rnd, single={p: {ci: round(f, 4) for ci, f in v.items()} for p, v in single.items()},
                    n_free_opts=len(free_opts), fixed={r: [(ci, sorted(S)) for ci, S, _, _ in v] for r, v in fixed_opts.items()},
                    free_opts=[(ci, sorted(S), rect_f(h)) for ci, S, _, h in free_opts])
        H_reach = set()
        for ci, S, _, _ in fixed_opts[self.H]:
            H_reach |= S
        info["H_reach"] = sorted(H_reach)
        # --- A1 unit rules per slot
        forced_H, instantiate = set(), {}
        for p in self.slots:
            n_free_cells = len(single[p])
            n_role_cells = sum(1 for r in self.role_cell if any(p in S for _, S, _, _ in fixed_opts[r]))
            if p not in H_reach:
                if n_free_cells + n_role_cells < 2:
                    self.dead = "A1/FC at %s: H provably misses it and only %d free cell(s) can hold a meeter" % (p, n_free_cells + n_role_cells)
                    self.T.test("A1-FC", slot=p, free_cells=sorted(single[p]), role_cells=n_role_cells, H_reach=False, verdict="DEAD")
                    info["dead"] = self.dead
                    return info
                if n_free_cells + n_role_cells == 2:
                    for ci in single[p]:
                        instantiate.setdefault(ci, set()).add(p)
                    self.T.test("A1-FC", slot=p, free_cells=sorted(single[p]), H_reach=False, verdict="both meeters forced")
            else:
                if n_free_cells + n_role_cells == 0:
                    self.dead = "A1/FC at %s: no free cell can hold a meeter" % p
                    self.T.test("A1-FC", slot=p, free_cells=[], H_reach=True, verdict="DEAD")
                    info["dead"] = self.dead
                    return info
                if n_free_cells + n_role_cells == 1:
                    forced_H.add(p)
                    for ci in single[p]:
                        instantiate.setdefault(ci, set()).add(p)
                    self.T.test("A1-FC", slot=p, free_cells=sorted(single[p]), H_reach=True, verdict="H forced + the free meeter forced")
        # --- the joint count, H free
        t0 = time.time()
        r = count_search(self.slots, free_opts, fixed_opts, self.n_free - len(self.role_cell), self.lines, self.pin_chords, self.s,
                         use_chords=False)
        info["count_nochord"] = dict(feasible=r.feasible, nodes=r.nodes, capped=r.capped)
        self.T.step("count", time.time() - t0, chords=False, feasible=r.feasible, nodes=r.nodes, capped=r.capped)
        if not r.feasible:
            self.dead = "JOINT COUNT: no cover of the %d forced slots by H + %d free squares (A1 cells, exact reach)" % (len(self.slots), self.n_free - len(self.role_cell))
            self.T.test("COUNT", chords=False, verdict="DEAD", nodes=r.nodes, n_free_opts=len(free_opts))
            info["dead"] = self.dead
            return info
        t0 = time.time()
        r2 = count_search(self.slots, free_opts, fixed_opts, self.n_free - len(self.role_cell), self.lines, self.pin_chords, self.s,
                          use_chords=True)
        info["count_chord"] = dict(feasible=r2.feasible, nodes=r2.nodes, capped=r2.capped)
        self.T.step("count", time.time() - t0, chords=True, feasible=r2.feasible, nodes=r2.nodes, capped=r2.capped)
        if not r2.feasible:
            self.dead = "JOINT COUNT + CHORD ROWS: no cover of the %d forced slots by H + %d free squares" % (len(self.slots), self.n_free - len(self.role_cell))
            self.T.test("COUNT", chords=True, verdict="DEAD", nodes=r2.nodes, n_free_opts=len(free_opts))
            info["dead"] = self.dead
            return info
        self.witness = r2.witness if r2.witness is not None else r.witness
        info["witness"] = [(who, ci, sorted(S)) for who, (ci, S, _, _) in (self.witness or [])]
        # --- H forced at p?  (bar H from p; infeasible => forced)
        for p in self.slots:
            if p in forced_H or p not in H_reach or self.T.out_of_time():
                continue
            fo = dict(fixed_opts)
            fo[self.H] = [o for o in fixed_opts[self.H] if p not in o[1]]
            t0 = time.time()
            rr = count_search(self.slots, free_opts, fo, self.n_free - len(self.role_cell), self.lines, self.pin_chords, self.s, use_chords=False)
            if rr.feasible:
                rr = count_search(self.slots, free_opts, fo, self.n_free - len(self.role_cell), self.lines, self.pin_chords, self.s, use_chords=True)
            self.T.step("count-barH", time.time() - t0, slot=p, feasible=rr.feasible, nodes=rr.nodes, capped=rr.capped)
            if not rr.feasible:
                forced_H.add(p)
                self.T.test("COUNT", barH=p, verdict="H forced at %s" % p, nodes=rr.nodes)
        info["forced_H"] = sorted(forced_H)
        info["instantiate"] = {ci: sorted(v) for ci, v in instantiate.items()}
        changed = False
        # --- apply: clip H
        if forced_H - self.forced_H:
            self.forced_H |= forced_H
            S = frozenset(self.forced_H)
            fr, pcs, _ = self.role_reach(self.H, S)
            if not pcs:
                self.dead = "H forced at %s but cannot meet them simultaneously (exact MISS test on every piece)" % sorted(S)
                self.T.test("H-JOINT", slots=sorted(S), verdict="DEAD")
                info["dead"] = self.dead
                return info
            hull = pieces_hull(pcs)
            old = self.roles[self.H]
            newH = (fl(hull[0]), fl(hull[1]), fl(hull[2]), fl(hull[3]), MB.deg_of_t(hull[4]), MB.deg_of_t(hull[5]))
            # never grow: intersect with the current H box (the hull is outward-rounded)
            newH = (max(newH[0], old[0]), min(newH[1], old[1]), max(newH[2], old[2]), min(newH[3], old[3]),
                    max(newH[4], old[4]), min(newH[5], old[5]))
            self.T.test("H-CLIP", slots=sorted(S), frac=round(fr, 6), n_pieces=len(pcs), box_before=rect_f(old), box_after=rect_f(newH))
            self.roles[self.H] = newH
            info["H_box"] = rect_f(newH)
            changed = True
        # --- apply: instantiate forced free meeters
        for ci, ps in instantiate.items():
            if ci in self.cell_role:
                role = self.cell_role[ci]
                # the unique instantiated role at that cell IS the meeter: clip it to the poses meeting ps too
                S = frozenset(ps) | frozenset(self.role_slots.get(role, ()))
                fr, pcs, _ = self.role_reach(role, S)
                if not pcs:
                    self.dead = "%s at cell %d forced to meet %s: no pose (exact MISS)" % (role, ci, sorted(S))
                    self.T.test("ROLE-JOINT", role=role, slots=sorted(S), verdict="DEAD")
                    info["dead"] = self.dead
                    return info
                if S != frozenset(self.role_slots.get(role, ())):
                    hull = pieces_hull(pcs)
                    old = self.roles[role]
                    nb = (max(fl(hull[0]), old[0]), min(fl(hull[1]), old[1]), max(fl(hull[2]), old[2]), min(fl(hull[3]), old[3]),
                          max(MB.deg_of_t(hull[4]), old[4]), min(MB.deg_of_t(hull[5]), old[5]))
                    self.roles[role] = nb
                    self.role_slots[role] = tuple(sorted(S))
                    self.T.test("ROLE-CLIP", role=role, slots=sorted(S), box_after=rect_f(nb))
                    changed = True
                continue
            S = frozenset(ps)
            rect = self.cells[ci]["rect"]
            for p in S:
                rect = rect_inter(rect, self.item[p]["win"])
            fr, pcs, _ = self.reach(ci, S)
            if not pcs:
                self.dead = "forced free meeter at cell %d for %s: no pose" % (ci, sorted(S))
                self.T.test("CELL-JOINT", cell=ci, slots=sorted(S), verdict="DEAD")
                info["dead"] = self.dead
                return info
            hull = pieces_hull(pcs)
            role = "F%d" % (len(self.role_cell) + 1)
            box = (fl(hull[0]), fl(hull[1]), fl(hull[2]), fl(hull[3]), MB.deg_of_t(hull[4]), MB.deg_of_t(hull[5]))
            self.roles[role] = box
            self.cell_role[ci] = role
            self.role_cell[role] = ci
            if not hasattr(self, "role_slots"):
                self.role_slots = {}
            self.role_slots[role] = tuple(sorted(S))
            if not hasattr(self, "role_corner"):
                self.role_corner = {}
            for p in S:
                if self.item[p]["is_corner"]:
                    self.role_corner[role] = self.item[p]["corner"]
            self.T.test("INSTANTIATE", role=role, cell=ci, slots=sorted(S), box=rect_f(box), frac=round(fr, 6))
            changed = True
        info["changed"] = changed
        return info

    # ------------------------------------------------------------------ the loop
    def run(self, max_rounds=4):
        self.role_slots, self.role_corner = {}, {}
        self.witness = None
        if self.normalise("base") is None:
            return self.result()
        for rnd in range(1, max_rounds + 1):
            info = self.propagate_round(rnd)
            self.rounds.append(info)
            if self.dead or not info.get("changed") or self.T.out_of_time():
                break
            if self.normalise("round%d" % rnd) is None:
                break
        return self.result()

    def result(self):
        return dict(nid=self.name, cls=self.cls, verdict="DEAD" if self.dead else "ALIVE", leaf=self.dead,
                    rounds=self.rounds, forced_H=sorted(self.forced_H), roles={k: rect_f(v) for k, v in self.roles.items()},
                    role_cells=dict(self.role_cell), witness=[(who, ci, sorted(S), rect_f(h)) for who, (ci, S, _, h) in (self.witness or [])],
                    seconds=round(self.T.now(), 1), n_tests=len(self.T.tests), steps=self.T.steps)


# ----------------------------------------------------------------------------- (d) the pair test on the most constrained slot
def pair_test_fallback(page, wall_left, nsub=8, refine=4):
    import geo178b as GB
    if page.nd is None or wall_left is None or wall_left < 60:
        return None
    rd = page.rounds[-1] if page.rounds else {}
    single = rd.get("single") or {}
    if not single:
        return None
    p = min(single, key=lambda q: (len(single[q]), sum(single[q].values())))
    it = page.item[p]
    hull = {page.H: list(page.roles[page.H])}
    pinroles = dict(page.pins)
    for r, b in page.roles.items():
        if r.startswith("F"):
            pinroles[r] = b
    t0 = time.time()
    res = GB.slot_pair_test(pinroles, [page.H], hull, it, nsub=nsub, refine=refine, log=lambda *a: None, label=page.name)
    page.T.step("pair-test", time.time() - t0, slot=p, alive=res["alive"], subcases=res.get("subcases"))
    return dict(slot=p, alive=res["alive"], leaf=res.get("leaf"), seconds=res["seconds"], subcases=res.get("subcases"))


# ----------------------------------------------------------------------------- driver
def load_page(nid, csv_path=None):
    import csv
    csv_path = csv_path or os.path.join(ROOT, "docs", "shadows", "a57v4", "review_a57v4.csv")
    for r in csv.DictReader(open(csv_path, encoding="utf-8")):
        if r["node"] == nid:
            rec = G.load_record(r["record"].replace("\\", "/"))
            cls = G.class_of_record(rec)
            return rec, cls, r
    raise KeyError(nid)


def run_page(nid, wall=600, depth=5, joint_depth=2, pair=True, log=print):
    T = Trace(wall=wall)
    rec, cls, row = load_page(nid)
    log("== %s (%s): %d pins, H %s" % (nid, cls, len(rec["pins"]), [round(v, 3) for v in rec["H"][0]]))
    pg = Page(rec, cls, nid, T, depth=depth, joint_depth=joint_depth)
    log("   forced cells: %s; grid %dx%d of side %.4f; free squares %d" % (
        [it["cell"] for it in pg.items], int(round(float((pg.s - 1) / pg.side))), int(round(float((pg.s - 1) / pg.side))), float(pg.side), pg.n_free))
    out = pg.run()
    for rd in out["rounds"]:
        log("   round %d: alive cells %s; H reaches %s; forced_H %s; instantiate %s; count %s / chords %s%s" % (
            rd["round"], {p: len(v) for p, v in rd["single"].items()}, rd.get("H_reach"), rd.get("forced_H"), rd.get("instantiate"),
            (rd.get("count_nochord") or {}).get("feasible"), (rd.get("count_chord") or {}).get("feasible"),
            ("; DEAD: " + rd["dead"]) if rd.get("dead") else ""))
    if out["verdict"] == "ALIVE" and pair:
        pr = pair_test_fallback(pg, T.left())
        out["pair_test"] = pr
        if pr is not None:
            log("   pair test on %s: %s (%.0f s)" % (pr["slot"], "ALIVE" if pr["alive"] else "DEAD", pr["seconds"]))
            if not pr["alive"]:
                out["verdict"], out["leaf"] = "DEAD", "pair test (geo178b, nsub 8 / refine 4) at %s: %s" % (pr["slot"], pr["leaf"])
    out["tests"] = T.tests
    out["seconds"] = round(T.now(), 1)
    out["row"] = dict(family=row.get("family"), camp=row.get("camp"), tau=row.get("tau"))
    log("   => %s in %.1f s (%d exact tests)%s" % (out["verdict"], out["seconds"], len(T.tests), ("; " + out["leaf"]) if out["leaf"] else ""))
    return out, pg


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--wall", type=float, default=600)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument("--jdepth", type=int, default=2)
    ap.add_argument("--nopair", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cert", default=None)
    ap.add_argument("--svg", default=None)
    a = ap.parse_args()
    out, pg = run_page(a.nid, wall=a.wall, depth=a.depth, joint_depth=a.jdepth, pair=not a.nopair)
    if a.cert:
        json.dump(out, open(a.cert, "w", encoding="utf-8"), indent=1, default=str)
    if a.out:
        slim = {k: v for k, v in out.items() if k not in ("tests", "steps")}
        slim["cert"] = a.cert
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(slim, default=str) + "\n")
    if a.svg:
        import fig198
        fig198.draw(pg, out, a.svg)
