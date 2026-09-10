"""A197 -- the TWO-MEETER requirement at a FORCED CELL, as a genuine PAIR test.

Successor of `attempts/A178-gallery-geometry/code/geo178b.py::slot_pair_test` (imported READ-ONLY
through geo178).  Theorem FC (docs/proofs/forced_corners.md) says two DISTINCT NON-pin squares of
the page's dilate meet the widened open slot box B_p+.  The non-pin squares are the conditioned
square(s) H and the free squares, so exactly one of

  (H-meets)   H is one meeter and one FREE square B is the other;
  (two-free)  two distinct FREE squares B, B' are the meeters.

Lemma A1 (sideband.md section 2) puts the two meeters' centres at l-infinity distance >= 1/sqrt2 =
0.70710678.  Cut the cell's meeter window into a grid of side <= 0.70 < 1/sqrt2: two meeter centres
can NEVER lie in one closed cell, so the case splits over cell pairs and the union of the cases is
the whole case.  A cell pair whose node is EmptyBox is dead; a cell whose intersection with a role's
box is empty is skipped (not a case at all).

WHAT IS NEW AGAINST A178
  * H-meets is a PAIR test: ORDERED cell pairs (cell_H, cell_B), cell_H != cell_B.  A178 ran one
    node with H restricted to the whole window and B in hull(B) -- no Lemma A1 split at all, and
    that single node is what kept every k5_16 page alive.
  * nsub 8 / refine 4 (A178: 4 / 2, where 1e-5 slivers survive).
  * caps 24 cells / 400 pairs (A178: 6 / 40, and both declared ALIVE on exhaustion).
  * forced CORNERS get A169 Theorem B's lonely clip.
  * a witness sampler for ALIVE cells: a real pair of admissible poses when one is found.

SOUNDNESS.  Every node is a sound over-approximation of its case: role boxes are supersets of the
poses the case allows (a meeter's centre lies in the meeter window; the second free meeter survives
the one-free clip, so it lies in hull(B) too).  EmptyBox on every case of a cell refutes the cell's
two-meeter requirement, hence the page's hypothesis.  [C: library geometry -- the frozen verifier is
not involved.]
"""
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A178 = os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code")
if A178 not in sys.path:
    sys.path.insert(0, A178)

import geo178 as G                                              # noqa: E402  READ-ONLY (A178)
import chordlane as CL                                          # noqa: E402  READ-ONLY (A161)

SQ2H = 0.70710678118654757
SIDE = 0.70                     # < 1/sqrt2: two meeter centres never share a closed cell


class Timeout(Exception):
    pass


def _tick(deadline, what):
    if deadline is not None and time.time() > deadline:
        raise Timeout(what)


# ------------------------------------------------------------------ the Lemma A1 grid
def make_grid(win, side=SIDE):
    """a common grid over the meeter window: (x0, y0, nx, ny, px, py) with px, py <= side."""
    x0, x1, y0, y1 = win
    nx = max(1, int(math.ceil((x1 - x0) / side - 1e-12)))
    ny = max(1, int(math.ceil((y1 - y0) / side - 1e-12)))
    return (x0, y0, nx, ny, (x1 - x0) / nx, (y1 - y0) / ny)


def grid_cells(grid):
    x0, y0, nx, ny, px, py = grid
    return [(a * ny + b, (x0 + a * px, x0 + (a + 1) * px, y0 + b * py, y0 + (b + 1) * py))
            for a in range(nx) for b in range(ny)]


def clip_rect(box, rect):
    """box (6-tuple) with its centre rect intersected with `rect` (4-tuple); None if empty."""
    x0, x1 = max(box[0], rect[0]), min(box[1], rect[1])
    y0, y1 = max(box[2], rect[2]), min(box[3], rect[3])
    if x0 > x1 + 1e-15 or y0 > y1 + 1e-15:
        return None
    return (x0, x1, y0, y1, box[4], box[5])


def cells_meeting(grid, box):
    """[(idx, clipped box)] over the grid cells the role's centre rect actually meets."""
    out = []
    for idx, c in grid_cells(grid):
        r = clip_rect(box, c)
        if r is not None and (r[1] - r[0]) * (r[3] - r[2]) >= 0:
            out.append((idx, r))
    return out


# ------------------------------------------------------------------ the MEET cover (A161 exact)
def can_meet(box6, wbox):
    """False when EVERY pose of the box gives a square disjoint from the widened box (A161's exact
    separating-axis test, `chordlane.box_misses_cell_exact`)."""
    ok, _ = CL.box_misses_cell_exact(G.MB.as_box(tuple(box6)), tuple(wbox))
    return not ok


def _bisect(b):
    x0, x1, y0, y1, t0, t1 = b
    dx, dy, dt = x1 - x0, y1 - y0, (t1 - t0) / 90.0
    if dx >= dy and dx >= dt and dx > 1e-12:
        m = 0.5 * (x0 + x1)
        return [(x0, m, y0, y1, t0, t1), (m, x1, y0, y1, t0, t1)]
    if dy >= dt and dy > 1e-12:
        m = 0.5 * (y0 + y1)
        return [(x0, x1, y0, m, t0, t1), (x0, x1, m, y1, t0, t1)]
    if dt > 1e-12:
        m = 0.5 * (t0 + t1)
        return [(x0, x1, y0, y1, t0, m), (x0, x1, y0, y1, m, t1)]
    return [tuple(b)]


def _merge(bs, k):
    bs = sorted(bs)
    g = int(math.ceil(len(bs) / float(k)))
    out = []
    for i in range(0, len(bs), g):
        c = bs[i:i + g]
        out.append((min(b[0] for b in c), max(b[1] for b in c), min(b[2] for b in c),
                    max(b[3] for b in c), min(b[4] for b in c), max(b[5] for b in c)))
    return out


def meet_cover(box6, wbox, depth=9, max_boxes=2, cap=24):
    """A COVER of {poses of box6 whose open square meets the open widened box} by <= max_boxes
    sub-boxes.  `[]` means NO pose of the box meets it -- the branch is VACUOUS, not alive.

    This is the constraint A178's H-meets branch never carried: it restricted H's CENTRE to the
    meeter window (which on a k5_16 page is a no-op, H's record box already lies inside) and never
    asked H to actually MEET the box.  Every sub-box dropped here is dropped by A161's exact
    separating-axis test, so the cover is sound.
    """
    if not can_meet(box6, wbox):
        return []
    cur = [tuple(box6)]
    for _ in range(depth):
        nxt = [h for b in cur for h in _bisect(b) if can_meet(h, wbox)]
        if not nxt:
            return []
        if len(nxt) == len(cur) and nxt == cur:
            break
        cur = nxt
        if len(cur) > max(cap, 4 * max_boxes):
            break
    return _merge(cur, max_boxes) if len(cur) > max_boxes else cur


# ------------------------------------------------------------------ the witness sampler
def _sq_halfext(th, ax):
    c, s = abs(math.cos(th)), abs(math.sin(th))
    return 0.5 * (abs(ax[0] * c + ax[1] * s) + abs(-ax[0] * s + ax[1] * c))


def _disjoint(c1, t1, c2, t2, eps=1e-9):
    """two closed unit squares, SAT on the four edge normals."""
    d = (c2[0] - c1[0], c2[1] - c1[1])
    for th in (t1, t2):
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            proj = abs(d[0] * ax[0] + d[1] * ax[1])
            if proj > _sq_halfext(t1, ax) + _sq_halfext(t2, ax) - eps:
                return True
    return False


def _meets_box(c, th, wbox, eps=1e-9):
    """the OPEN unit square at (c, th) meets the open axis box wbox = (X0, X1, Y0, Y1)."""
    X0, X1, Y0, Y1 = wbox
    bc = (0.5 * (X0 + X1), 0.5 * (Y0 + Y1))
    hb = (0.5 * (X1 - X0), 0.5 * (Y1 - Y0))
    d = (bc[0] - c[0], bc[1] - c[1])
    for ax in ((1.0, 0.0), (0.0, 1.0)):
        proj = abs(d[0] * ax[0] + d[1] * ax[1])
        if proj >= _sq_halfext(th, ax) + abs(ax[0]) * hb[0] + abs(ax[1]) * hb[1] - eps:
            return False
    for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
        proj = abs(d[0] * ax[0] + d[1] * ax[1])
        if proj >= 0.5 + abs(ax[0]) * hb[0] + abs(ax[1]) * hb[1] - eps:
            return False
    return True


def witness(nd, meeters, wbox, s, n=4000, seed=197):
    """a real admissible configuration of the node's roles in which both `meeters` meet wbox.
    -> dict(poses={role: [x, y, deg]}) or None."""
    rng = np.random.default_rng(seed)
    names = list(nd.boxes)
    S = {}
    for k in names:
        C, TH = nd.boxes[k].sample(n, rng)
        if not len(C):
            return None
        S[k] = (C, TH)
    for t in range(n):
        ok = True
        for k in meeters:
            if not _meets_box((S[k][0][t][0], S[k][0][t][1]), S[k][1][t], wbox):
                ok = False
                break
        if not ok:
            continue
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if not _disjoint((S[a][0][t][0], S[a][0][t][1]), S[a][1][t],
                                 (S[b][0][t][0], S[b][0][t][1]), S[b][1][t]):
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        for k in names:
            c, th = S[k][0][t], S[k][1][t]
            h = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
            if not (h <= c[0] <= s - h and h <= c[1] <= s - h):
                ok = False
                break
        if ok:
            return dict(poses={k: [float(S[k][0][t][0]), float(S[k][0][t][1]),
                                   float(math.degrees(S[k][1][t]))] for k in names})
    return None


# ------------------------------------------------------------------ phase 1: one free meeter
def one_free(pinroles, hnames, hull, item, nsub=4, refine=2, deadline=None, label=""):
    """{pins, H, one FREE meeter B in the meeter window}.  Every case of the cell implies this
    node (Corollary FC-count: at least one free square meets B_p+ unconditionally)."""
    _tick(deadline, "one_free")
    tag = item["cell"].replace("(", "").replace(",", "").replace(")", "")
    W = item["window"]
    roles = dict(pinroles)
    for k in hnames:
        roles[k] = tuple(hull[k])
    mc = meet_cover((W[0], W[1], W[2], W[3], 0.0, 90.0), item["wbox"], max_boxes=1)
    roles["B_" + tag] = mc[0] if mc else (W[0], W[1], W[2], W[3], 0.0, 90.0)
    corners = {"B_" + tag: item["corner"]} if item.get("is_corner") else None
    nd, info = G.run_node(roles, corners=corners, nsub=nsub, refine=refine,
                          label=label + "/one-free:" + item["cell"])
    hb = None if info["dead"] else G.hull_of(nd, "B_" + tag)
    return nd, info, hb, tag


# ------------------------------------------------------------------ phase 2: the pair test
def pair_test(pinroles, hnames, hull, item, of_info, hb, tag, s,
              nsub=8, refine=4, max_cells=24, max_pairs=400, meet_boxes=2, deadline=None,
              log=print, label="", want_witness=True):
    """-> dict(alive, subcases, h_hull_union, leaf, seconds, witness).  `of_info`/`hb` from one_free."""
    t0 = time.time()
    W = item["window"]
    wbox = tuple(item["wbox"])
    corner = item["corner"] if item.get("is_corner") else None
    sub = []
    alive_hulls = []
    wit = None
    caps = []

    def node(roles, lab, cs=None):
        _tick(deadline, lab)
        return G.run_node(roles, corners=cs, nsub=nsub, refine=refine, label=lab)

    # ---------- (H-meets): ORDERED cell pairs (cell_H, cell_B), cell_H != cell_B
    hm_alive = 0
    hm_tested = 0
    hm_cases = []
    hrestr = {}
    vacuous = False
    for k in hnames:
        r = clip_rect(hull[k], (W[0], W[1], W[2], W[3]))
        if r is None:
            vacuous = True
        else:
            hrestr[k] = r
    if len(hnames) != 1:
        # more than one conditioned square: the H-meets case is "SOME H meets"; treated as
        # untested-ALIVE rather than silently dropped
        sub.append(dict(case="H-meets", note="multi-H page: not split (treated ALIVE)", n_H=len(hnames)))
        hm_alive = 1
    elif vacuous:
        sub.append(dict(case="H-meets", vacuous=True, reason="H box outside the meeter window"))
    else:
        hn = hnames[0]
        hr = hrestr[hn]
        # the Lemma A1 grid for this branch covers BOTH meeters' centre rects, so "different cells"
        # is a statement about one grid (two centres 1/sqrt2 apart never share a closed cell)
        gridH = make_grid((min(hr[0], hb[0]), max(hr[1], hb[1]),
                           min(hr[2], hb[2]), max(hr[3], hb[3])))
        hcells = cells_meeting(gridH, hr)
        bcells = cells_meeting(gridH, (hb[0], hb[1], hb[2], hb[3], hb[4], hb[5]))
        pairs = [(i, ci, j, cj) for (i, ci) in hcells for (j, cj) in bcells if i != j]
        if len(hcells) > max_cells or len(bcells) > max_cells:
            sub.append(dict(case="H-meets", n_cells_H=len(hcells), n_cells_B=len(bcells),
                            skipped="cell cap: ALIVE untested"))
            caps.append("H-meets cells")
            hm_alive = 1
        elif not pairs:
            sub.append(dict(case="H-meets", n_cells_H=len(hcells), n_cells_B=len(bcells),
                            n_pairs=0, dead="no admissible (cell_H, cell_B) with cell_H != cell_B"))
        else:
            capped = False
            for (i, ci, j, cj) in pairs:
                if hm_tested >= max_pairs:
                    caps.append("H-meets pairs")
                    capped = True
                    hm_alive += 1
                    break
                hsub = meet_cover(ci, wbox, max_boxes=meet_boxes)
                bsub = meet_cover(cj, wbox, max_boxes=meet_boxes)
                hm_tested += 1
                if not hsub or not bsub:
                    hm_cases.append(dict(cH=i, cB=j, vacuous=True,
                                         reason="no pose in %s meets the widened box (A161 exact)"
                                                % ("cell_H" if not hsub else "cell_B")))
                    continue
                alive_here = 0
                secs = 0.0
                for u, hbx in enumerate(hsub):
                    for v, bbx in enumerate(bsub):
                        roles = dict(pinroles)
                        roles[hn] = hbx
                        roles["B_" + tag] = bbx
                        cs = {"B_" + tag: corner} if corner else None
                        nd2, i2 = node(roles, label + "/H-meets:%s:%d+%d:%d.%d"
                                       % (item["cell"], i, j, u, v), cs)
                        secs += i2["seconds"]
                        vac = (not i2["dead"]) and G.h_misses(nd2, list(wbox))
                        if i2["dead"] or vac:
                            continue
                        alive_here += 1
                        alive_hulls.append({k: G.hull_of(nd2, k) for k in hnames})
                        if want_witness and wit is None:
                            wit = witness(nd2, [hn, "B_" + tag], wbox, s)
                            if wit is not None:
                                wit = dict(case="H-meets", cells=[i, j], **wit)
                hm_cases.append(dict(cH=i, cB=j, n_meet_H=len(hsub), n_meet_B=len(bsub),
                                     n_alive=alive_here, seconds=round(secs, 1)))
                hm_alive += alive_here
            sub.append(dict(case="H-meets", n_cells_H=len(hcells), n_cells_B=len(bcells),
                            n_pairs=len(pairs), tested=hm_tested, capped=capped,
                            n_alive=hm_alive, cases=hm_cases))

    # ---------- (two-free): UNORDERED distinct cell pairs of hull(B)
    tf_alive = 0
    tf_cases = []
    gridF = make_grid((hb[0], hb[1], hb[2], hb[3]))
    bcells = cells_meeting(gridF, (hb[0], hb[1], hb[2], hb[3], hb[4], hb[5]))
    tfpairs = [(bcells[a], bcells[b]) for a in range(len(bcells)) for b in range(a + 1, len(bcells))]
    if len(bcells) > max_cells:
        sub.append(dict(case="two-free", n_cells=len(bcells), skipped="cell cap: ALIVE untested",
                        hull_B=list(hb[:4])))
        caps.append("two-free cells")
        tf_alive = 1
    elif not tfpairs:
        sub.append(dict(case="two-free", n_cells=len(bcells), n_pairs=0,
                        dead="hull(B) meets ONE grid cell: two meeters cannot be 1/sqrt2 apart",
                        hull_B=list(hb[:4])))
    else:
        tested = 0
        capped2 = False
        for ((i, ci), (j, cj)) in tfpairs:
            if tested >= max_pairs:
                caps.append("two-free pairs")
                capped2 = True
                tf_alive += 1
                break
            tested += 1
            s1 = meet_cover(ci, wbox, max_boxes=meet_boxes)
            s2 = meet_cover(cj, wbox, max_boxes=meet_boxes)
            if not s1 or not s2:
                tf_cases.append(dict(c1=i, c2=j, vacuous=True,
                                     reason="no pose in that cell meets the widened box "
                                            "(A161 exact)"))
                continue
            alive_here = 0
            secs = 0.0
            for u, b1 in enumerate(s1):
                for v, b2 in enumerate(s2):
                    roles = dict(pinroles)
                    for k in hnames:
                        roles[k] = tuple(hull[k])
                    roles["B_" + tag] = b1
                    roles["B2_" + tag] = b2
                    cs = {"B_" + tag: corner, "B2_" + tag: corner} if corner else None
                    nd2, i2 = node(roles, label + "/two-free:%s:%d+%d:%d.%d"
                                   % (item["cell"], i, j, u, v), cs)
                    secs += i2["seconds"]
                    if i2["dead"]:
                        continue
                    alive_here += 1
                    alive_hulls.append({k: G.hull_of(nd2, k) for k in hnames})
                    if want_witness and wit is None:
                        wit = witness(nd2, ["B_" + tag, "B2_" + tag], wbox, s)
                        if wit is not None:
                            wit = dict(case="two-free", cells=[i, j], **wit)
            tf_cases.append(dict(c1=i, c2=j, n_meet_1=len(s1), n_meet_2=len(s2),
                                 n_alive=alive_here, seconds=round(secs, 1)))
            tf_alive += alive_here
        sub.append(dict(case="two-free", n_cells=len(bcells), n_pairs=len(tfpairs),
                        tested=tested, capped=capped2, n_alive=tf_alive, cases=tf_cases,
                        hull_B=list(hb[:4])))

    alive = bool(hm_alive) or bool(tf_alive)
    log("      %s: B hull %.2fx%.2f | H-meets %d alive / %d tested | two-free %d alive / %d -> %s%s"
        % (item["cell"], hb[1] - hb[0], hb[3] - hb[2], hm_alive, hm_tested, tf_alive, len(tfpairs),
           "ALIVE" if alive else "DEAD", (" [caps: %s]" % ",".join(caps)) if caps else ""))
    hu = None
    if alive_hulls:
        hu = {}
        for k in hnames:
            hs = [h[k] for h in alive_hulls]
            hu[k] = [min(h[0] for h in hs), max(h[1] for h in hs), min(h[2] for h in hs),
                     max(h[3] for h in hs), min(h[4] for h in hs), max(h[5] for h in hs)]
    return dict(alive=alive, subcases=sub, h_hull_union=hu, caps=caps, witness=wit,
                seconds=round(time.time() - t0, 1), hull_B=list(hb),
                leaf=None if alive else
                ("two-meeter requirement at %s: every (H-meets) ordered cell pair and every "
                 "(two-free) cell pair is EmptyBox" % item["cell"]))
