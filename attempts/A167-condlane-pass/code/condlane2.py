"""A167 -- the CONDITIONAL chord-limited lane with A161's three queued levers.

THE LEAF (unchanged from A161 T8 / `condlane.py`'s docstring, restated with the per-piece line).

Let `B_H` be the conditioned square's box at a WALL-ADJACENT usable slot cell `C` of a pinned class,
and let `B_1, ..., B_N` be a COMPLETE binary subdivision of `B_H` (so the true pose of `H` lies in
exactly one piece).  Fix a piece `b`, use its OWN polygon core `K'(b) ⊇ K'(B_H)` as the obstacle
(strictly fatter -- that is the point), and choose ONE wall guard line `l(b)` for that piece.  With

    beta(b)      = floor( s0 - minchord(b, l) - SUM_{pins} minchord(B_j, l) )     [A144 LINE-1/2]
    m(b)         = 0 if EVERY pose of b misses int C (exact SAT), else 1
    LANE_out(b)  = lane cover of the meeting window with the `band` prune      (BAND poses are
                                                                               charged to beta)
    LANE_band(b) = lane cover of the BAND SLAB with the `not_band` prune       (OUTSIDE poses are
                                                                               charged to LANE_out)
    n(b)         = beta(b) + LANE_out(b)                              if m(b) = 0
                 = min(beta(b), LANE_band(b)) + LANE_out(b) + 1       if m(b) = 1

`n(b) <= 1` on EVERY piece  ==>  `int C` is met by at most one non-pin square in every realisation
==>  SLOT-CROWD's `>= 2` is contradicted  ==>  the node is DEAD.

WHY THE THREE CHANGES ARE SOUND.

(i) PER-PIECE LINE.  The band/outside partition is taken with respect to ONE line per piece, and
    all three counters of that piece use that same line; the pieces are a partition of `H`'s pose
    space, so a realisation is scored by its own piece's line only.  Ranking those lines by the
    sampled `band_free` count computed with `K'(piece)` (A161's lever (i)) changes nothing about
    soundness -- it is a search heuristic over exact tests.

(ii) PER-PIECE beta.  `minchord` is monotone under box inclusion (`b ⊆ B_H` ==> the minimum of the
     chord over `b` is `>=` the minimum over `B_H`), so using the PIECE's box in the guard row is a
     sound tightening on that piece: `H`'s true pose is in `b`, so its chord on `l` really is at
     least `minchord(b, l)`.  This is what turns `beta = 1` into `beta = 0` on the pieces where
     `H` sits deep in the wall lane, and then `min(beta, LANE_band) = 0` with NO band cover at all.

(iii) BAND-SLAB ROOT.  `chord >= 1  <=>  |v| <= f(y) = (y + 1 - y^2)/2` with `y = |cos|+|sin| in
      [1, sqrt2]`, and `f` is DECREASING there, so `f(y) <= f(1) = 1/2` for every tilt: EVERY band
      pose has `|off - c_perp| <= 1/2`.  Hence the `LANE_band` cover may be run over
      `centre_window(C) INTERSECT { |off - c_perp| <= 1/2 }` instead of the whole window -- the
      poses discarded are all OUTSIDE poses, which `LANE_out` already accounts for.  The emitted
      root is widened by `SLAB_EPS` so the checker's exact containment test passes.

Everything else -- `band_ok`, `not_band_ok`, `box_misses_cell_exact`, `minchord_box`, `cover`,
`split_box`, `find_witness`, `pairs_always_overlap` -- is A161/A144/A141/A118 code imported
READ-ONLY.

    python runcond167.py --nid c0_Y0169 --slot "TL(0,0)"
"""
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A161C = os.path.join(ROOT, "attempts", "A161-chord-lane", "code")
for _p in (A161C, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import chordlane as CL                       # noqa: E402  READ-ONLY (A161)
import numpy as np                           # noqa: E402
import polylane as P                         # noqa: E402  READ-ONLY (A141)
import guardline as GL                       # noqa: E402  READ-ONLY (A144)
from caselp import Box                       # noqa: E402  READ-ONLY (A57)

SLAB_EPS = 1e-9                              # the band slab is emitted 1e-9 wide of |v| <= 1/2
SQ2 = float(CL.SQRT2_HI)


# ===================================================================== the two cover roots
def free_pose_witness(pool, dead_entry=None):
    """One sampled FREE pose meeting int C, band first: the realisation that makes a screened-out
    offset (and, at the deepest split reached, the whole piece) a NO-GO for this leaf."""
    Cs, Ts, hit = pool["C"], pool["T"], pool["hit"]
    if not len(Cs):
        return None
    free = ~hit
    ix = np.nonzero(free)[0]
    if not len(ix):
        return None
    k = int(ix[0])
    return dict(c=[float(Cs[k, 0]), float(Cs[k, 1])], theta_deg=float(np.degrees(Ts[k])),
                n_free_meeting=int(free.sum()),
                screened=(dead_entry if isinstance(dead_entry, dict) else None))


def out_root(cell, s):
    """The full meeting window (A141 `centre_window`): every pose meeting int C has its centre
    here, because `Q(c, th) ⊆ c + [-h, h]^2` with `h <= sqrt2/2`, and `h >= 1/2` for an admissible
    pose."""
    x0, x1, y0, y1 = P.centre_window(cell, s)
    return None if (x1 <= x0 or y1 <= y0) else Box(x0, x1, y0, y1, 0.0, 90.0)


def band_root(cell, line, s):
    """The meeting window INTERSECTED with the band slab `|off - c_perp| <= 1/2` (lever (iii))."""
    x0, x1, y0, y1 = P.centre_window(cell, s)
    lo, hi = line.foff - 0.5 - SLAB_EPS, line.foff + 0.5 + SLAB_EPS
    if line.orient == "h":
        y0, y1 = max(y0, lo), min(y1, hi)
    else:
        x0, x1 = max(x0, lo), min(x1, hi)
    return None if (x1 <= x0 or y1 <= y0) else Box(x0, x1, y0, y1, 0.0, 90.0)


def _cover(root, cell, conds, line, s, band_mode, max_depth, max_open, deadline):
    if root is None:
        return dict(ok=True, lane=0, leaves=[], open=[], depth=0, root=None,
                    reason="empty root")
    out = CL.cover(root, cell, conds, line, s=s, max_depth=max_depth, max_open=max_open,
                   deadline=deadline, band_mode=band_mode)
    out["root"] = [root.x0, root.x1, root.y0, root.y1, root.th0, root.th1]
    return out


# ===================================================================== the per-piece line ranking
def rank_lines(cell, others, piece_cs, orients, s, rng, sample, n_lines, m, force_off=None):
    """Rank the swept wall offsets FOR THIS PIECE.

    One pose pool is drawn with `K'(piece)` among the obstacles (lever (i)): the `band_free` count
    it reports is the number of sampled free BAND meeters that the piece's own core does NOT block,
    i.e. exactly what the `LANE_band` cover has to kill.  `beta` is recomputed per offset with the
    PIECE's box in the guard row (lever (ii)).

    Returns (ranked, pool, contradiction) with ranked entries
    (key, orient, line, rhs, beta, terms, sample).
    """
    conds = others + [piece_cs]
    pool = CL.sample_pool(cell, conds, s, sample, rng)
    boxes = [c.box for c in conds]
    ranked, dead, contra = [], [], None
    for orient in orients:
        cands = ([GL.Line(orient, Fr(force_off), tag="forced")] if force_off is not None
                 else CL.line_candidates(orient, n=n_lines))
        for ln in cands:
            rhs, beta, terms = CL.guard_rhs(boxes, ln, s=CL.S_RAT)
            if beta is None:                        # rhs < 0: A144's guard row alone kills
                contra = dict(orient=orient, off=str(ln.off), rhs=str(rhs), minchords=terms)
                continue
            sm = CL.sample_split(pool, ln)
            of = sm.get("outside_free") or 0
            bf = sm.get("band_free") or 0
            mg = -(sm.get("band_margin_min_free") or -9.0)
            # VIABILITY.  A sampled FREE pose meeting int C is a realisation of the lane quantity
            # it belongs to (it avoids every K', the fattened piece core included), so it is a
            # hard lower bound -- A159's witness rule.  An offset whose sample already forces
            # `n(b) >= 2` can never produce a kill, so no cover is run on it at all: that screen
            # is what makes the deep split affordable (measured: a hopeless offset costs 2-4 s of
            # cover time and a screened one costs nothing).
            if m:
                viable = (of == 0) and (beta == 0 or bf == 0)
                why = None if viable else ("free outside pose => LANE_out >= 1" if of else
                                           "free band pose and beta >= 1 => min >= 1")
                key = (of, (bf if beta else 0), beta, mg)
            else:
                two = 1 if sm.get("two_crowd_outside") else 0
                viable = (beta <= 1) and ((of == 0) if beta else (two == 0))
                why = None if viable else ("beta = %d >= 2" % beta if beta >= 2 else
                                           ("two interior-disjoint free outside poses"
                                            if two else "free outside pose with beta = 1"))
                key = (beta, of, mg)
            ent = (key, orient, ln, rhs, beta, terms, sm)
            (ranked if viable else dead).append(ent if viable else
                                               dict(orient=orient, off=str(ln.off), beta=beta,
                                                    outside_free=of, band_free=bf, why=why))
    ranked.sort(key=lambda z: z[0])
    return ranked, pool, contra, dead


# ===================================================================== one piece
def piece_bound(cell, others, piece_cs, orients, s, rng, *, sample=8000, n_lines=48,
                n_off=6, max_depth=34, max_open=2500, band_open=None, deadline=None,
                keep_cert=True, force_off=None, off_s=2.0, long_s=12.0):
    """`n(b)` for one piece of `H`'s box, trying the top `n_off` ranked offsets.

    MEASURED (logs/diag_y0169_d3.log): a cover that closes closes in 0.6-1.2 s, and one that does
    not grinds for as long as it is given.  So each offset gets a SHORT hard slice `off_s` and the
    breadth over offsets is what buys kills -- A161's "which line, not how long", made operational.
    """
    b = piece_cs.box
    misses, mdet = CL.box_misses_cell_exact(b, cell)
    m = 0 if misses else 1
    conds = others + [piece_cs]
    out = dict(box=P.box_json(b), m=m, misses_cell=bool(misses), misses_detail=mdet,
               ok=False, tries=[])
    ranked, pool, contra, dead = rank_lines(cell, others, piece_cs, orients, s, rng, sample,
                                            n_lines, m, force_off=force_off)
    if contra is not None:                       # the chord row alone is contradictory on b
        out.update(ok=True, chord_contradiction=contra, total=0, why="chord-contradiction")
        return out
    if not ranked:
        mf = min([(d["outside_free"] + d["band_free"]) for d in dead] or [0])
        out.update(why="no viable offset", n_dead_offsets=len(dead), dead_min_free=mf,
                   dead_sample=sorted(dead, key=lambda d: d["outside_free"] + d["band_free"])[:3],
                   witness=(free_pose_witness(pool, dead[0]) if dead else None))
        return out

    def attempt(cand, slice_s):
        key, orient, ln, rhs, beta, terms, sm = cand
        dl = time.time() + slice_s if deadline is None else min(deadline,
                                                               time.time() + slice_s)
        tt = time.time()
        co = _cover(out_root(cell, s), cell, conds, ln, s, "out", max_depth, max_open, dl)
        t = dict(orient=orient, off=str(ln.off), beta=beta, lane_out=co["lane"],
                 out_leaves=len(co["leaves"]), out_open=len(co["open"]),
                 out_reason=co.get("reason"), t_out=round(time.time() - tt, 2),
                 slice_s=slice_s, sample_outside_free=sm.get("outside_free"),
                 sample_band_free=sm.get("band_free"))
        lo, cb = co["lane"], None
        if lo == 0 and m and beta >= 1:
            tt = time.time()
            dl2 = tt + slice_s if deadline is None else min(deadline, tt + slice_s)
            cb = _cover(band_root(cell, ln, s), cell, conds, ln, s, "band", max_depth,
                        band_open or max_open, dl2)
            t.update(lane_band=cb["lane"], band_leaves=len(cb["leaves"]),
                     band_open=len(cb["open"]), band_reason=cb.get("reason"),
                     t_band=round(time.time() - tt, 2))
        ok, total = False, None
        if lo is not None:
            if m == 0:
                total = beta + lo
                ok = total <= 1
            elif lo == 0:
                bb = 0 if beta == 0 else (cb["lane"] if (cb and cb["lane"] is not None) else None)
                if bb is not None:
                    total = min(beta, bb) + lo + 1
                    ok = total <= 1
        t.update(total=total, ok=ok, open_left=((t["out_open"] if lo is None else 0)
                                               + (t.get("band_open", 0) if
                                                  (cb and cb["lane"] is None) else 0)))
        out["tries"].append(t)
        if ok:
            out.update(ok=True, total=total, beta=beta, rhs=str(rhs), minchords=terms,
                       lane_out=lo, lane_band=(None if cb is None else cb["lane"]),
                       line=dict(orient=orient, off=str(ln.off), off_float=ln.foff, tag=ln.tag),
                       sample={k: v for k, v in sm.items() if k != "per_core"})
            if keep_cert:
                out["out_cover"] = dict(value=lo, root=co["root"], leaves=co["leaves"],
                                        open=co["open"])
                out["band_cover"] = (None if cb is None else
                                     dict(value=cb["lane"], root=cb["root"],
                                          leaves=cb["leaves"], open=cb["open"]))
        return ok

    # PHASE 1: a short hard slice on each of the top `n_off` VIABLE offsets.
    seen, tried = set(), []
    for cand in ranked:
        if len(tried) >= n_off:
            break
        if deadline is not None and time.time() > deadline:
            out["why"] = "time budget (phase 1)"
            return out
        tag = (cand[1], str(cand[2].off))
        if tag in seen:
            continue
        seen.add(tag)
        n0 = len(out["tries"])
        if attempt(cand, off_s):
            return out
        tried.append((out["tries"][n0]["open_left"], len(tried), cand))
    # PHASE 2: the offset that got CLOSEST (fewest boxes left open) gets a long slice.
    tried.sort(key=lambda z: (z[0], z[1]))
    if tried and (deadline is None or time.time() < deadline - 1.0):
        if attempt(tried[0][2], max(off_s, long_s)):
            return out
    out["why"] = "no viable offset closed (%d tried, %d screened out)" % (len(tried), len(dead))
    return out


# ===================================================================== the (node, slot) driver
def run(rec, slot, rng=None, *, max_pieces=48, split_depth=4, pre_depth=0, cover_depth=34,
        max_open=2500, band_open=None, sample=8000, n_lines=48, n_off=6, budget_s=60.0,
        keep_cert=True, force_off=None, off_s=2.0, long_s=12.0, nogo_cut=5):
    rng = rng if rng is not None else np.random.default_rng(1670)
    t0 = time.time()
    dl = t0 + budget_s
    s = CL.S0
    conds, meet, cell, corner, i, j = CL.frame_boxes(rec, slot)
    row = dict(nid=rec["nid"], src=rec["src"], cls=rec["cls"], level=rec["level"], slot=slot,
               cell=list(cell), corner=corner, ij=[i, j], n_pins=len(conds) - len(meet),
               cond_index=list(meet), verdict="UNDECIDED")
    if len(meet) != 1:
        row["verdict"] = "NOT-SINGLE-CONDITIONED (%d)" % len(meet)
        return row, None
    orients = CL.WALL_ORIENT.get((i, j)) or ()
    if not orients:
        row["verdict"] = "NOT-WALL-ADJACENT"
        return row, None
    jH = meet[0]
    others = [c for c in conds if c.idx != jH]
    B_H = conds[jH].box

    # lever (ii): the split starts at depth `pre_depth` -- the shallow pieces of `B_H` are the
    # expensive hopeless ones (a fat `K'(b)` is what blocks the band), and the split is
    # tautologous at every depth, so pre-splitting loses nothing.
    stack = [("", B_H)]
    for _ in range(max(0, pre_depth)):
        nxt = []
        for (p2, b2) in stack:
            c0, c1 = P.split_box(b2)
            nxt.append((p2 + "0", c0))
            nxt.append((p2 + "1", c1))
        stack = nxt
    done, opens = [], []
    while stack:
        path, b = stack.pop()
        if time.time() > dl:
            opens.append(dict(path=path, box=P.box_json(b), why="time budget"))
            opens.extend([dict(path=p2, box=P.box_json(b2), why="time budget")
                          for (p2, b2) in stack])
            break
        try:
            pc = P.build_cond([b], tighten=False)[0]
        except Exception as e:                                       # noqa: BLE001
            opens.append(dict(path=path, box=P.box_json(b), why="polycore build: %r" % e))
            continue
        pc.idx = jH
        # each piece gets an equal slice of what is left, with a floor
        nleft = max(1, len(stack) + 1)
        pdl = min(dl, time.time() + max(4.0, (dl - time.time()) / nleft))
        r = piece_bound(cell, others, pc, orients, s, rng, sample=sample, n_lines=n_lines,
                        n_off=n_off, max_depth=cover_depth, max_open=max_open,
                        band_open=band_open, deadline=pdl, keep_cert=keep_cert,
                        force_off=force_off, off_s=off_s, long_s=long_s)
        r["path"] = path
        if r["ok"]:
            done.append(r)
            continue
        # a piece with NO viable offset and plenty of sampled free meeters is terminal: a deeper
        # split fattens `K'` but cannot remove that many realisations, so the cell is abandoned
        # here instead of eating the rest of the budget (measured on c0_Y0169/TL(0,0)).
        if (r.get("why") == "no viable offset" and (r.get("dead_min_free") or 0) >= nogo_cut):
            r["terminal"] = True
            opens.append(r)
            break
        if len(path) >= split_depth or len(done) + len(stack) + len(opens) + 1 >= max_pieces:
            opens.append(r)
            continue
        b0, b1 = P.split_box(b)
        stack.append((path + "0", b0))
        stack.append((path + "1", b1))
    whys = [(o.get("why") or "") for o in opens]
    if not opens:
        verdict = "KILL"
    elif any(o.get("terminal") for o in opens) or all(w == "no viable offset" for w in whys):
        # every unfinished piece carries a SAMPLED free meeter alongside `H`: two non-pin squares
        # can meet int C in that piece, so this leaf cannot fire there at the depth searched.
        verdict = "NO-GO-witness"
    elif any(w.startswith("time budget") for w in whys):
        verdict = "UNDECIDED-time"
    else:
        verdict = "UNDECIDED"
    row.update(n_pieces=len(done) + len(opens), n_done=len(done), n_open=len(opens),
               elapsed=round(time.time() - t0, 1), verdict=verdict,
               n_nogo=sum(1 for w in whys if w.startswith("no viable offset")))
    row["pieces_summary"] = [dict(path=r.get("path"), m=r.get("m"), beta=r.get("beta"),
                                  lane_out=r.get("lane_out"), lane_band=r.get("lane_band"),
                                  total=r.get("total"), off=(r.get("line") or {}).get("off"),
                                  why=r.get("why")) for r in (done + opens)]
    if opens:
        ng = [o for o in opens if o.get("why") == "no viable offset"]
        if ng:
            g = ng[0]
            row["nogo"] = dict(path=g.get("path"), box=g.get("box"), m=g.get("m"),
                               n_dead_offsets=g.get("n_dead_offsets"),
                               dead_min_free=g.get("dead_min_free"),
                               dead_sample=g.get("dead_sample"), witness=g.get("witness"),
                               terminal=bool(g.get("terminal")))
        row["open_pieces"] = [{k: v for k, v in o.items()
                               if k in ("path", "box", "m", "why", "tries", "total",
                                        "witness", "dead_sample", "n_dead_offsets")}
                              for o in opens[:4]]
        return row, None
    row["sample_lines"] = [dict(path=r["path"], m=r.get("m"),
                                **{k: (r.get("sample") or {}).get(k)
                                   for k in ("drawn", "meeting", "free", "band", "outside",
                                             "band_free", "outside_free", "min_chord_band")})
                           for r in done]
    cert = None
    if keep_cert:
        cert = dict(
            leaf="conditional_chord_limited_lane_v1",
            claim="a COMPLETE binary subdivision of the conditioned square's box on which, with a "
                  "PER-PIECE wall guard line and the piece's own box in the guard row, "
                  "beta + LANE_out <= 1 (piece misses the cell) resp. "
                  "min(beta, LANE_band) + LANE_out + 1 <= 1 (piece meets it); hence int C is met "
                  "by at most one non-pin square in every realisation, contradicting SLOT-CROWD",
            s=str(CL.S_RAT), s_float=CL.S0, nid=rec["nid"], src=rec["src"], cls=rec["cls"],
            level=rec["level"], slot=slot, corner=corner, ij=[i, j], cell=list(cell),
            cell_kind="usable_slot",
            extension=CL.CP.CLASSES[rec["cls"]]["usable"][slot],
            extension_window="[191/50, 969271/250000] FULL (A56/A61/A114 scoreboard)",
            frame="A118 lane.cframe_boxes: original packing at side m, cell's corner frame, "
                  "every box hulled over m in [m_lo, s0]",
            m_lo=CL.LANE.M_LO.get(rec["src"], 3.82),
            n_pins=row["n_pins"], cond_index=[jH],
            hyp_boxes=[P.box_json(c.box) for c in conds],
            split_root=P.box_json(B_H),
            split_rule="widest of (x, y, theta/60), deterministic (A141 polylane.split_box)",
            band_rule="chord >= 1  <=>  |v| <= (y + 1 - y^2)/2 at y = |cos|+|sin|; band_ok uses "
                      "cs_max, not_band_ok uses cs_min; every band pose has |v| <= 1/2, which is "
                      "why the LANE_band root may be the band slab",
            slab_eps=SLAB_EPS,
            pieces=[{k: v for k, v in r.items() if k != "tries"} for r in done],
            sample_lines=row["sample_lines"], verdict="KILL",
        )
    return row, cert
