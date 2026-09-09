"""A161 T8 -- the CONDITIONAL chord-limited lane: split the conditioned square's own box.

WHY.  A161 T3 retires a cell `NO-LINE` when `beta + M >= 2` on every swept offset -- typically
`beta = 1` (two pins on the wall) and `M = 1` (`H` reaches `int C` from PART of its box).  Counting
`beta` and `M` separately cannot see that the band square and `H` are mutually exclusive.  The fix is
A141's `lane_corner_split` idea applied to the chord leaf: partition `H`'s parameter box, and on
each piece use the sharper of the two accountings.

THE LEAF (conditional form).  Let `B_H` be the conditioned square's box and `B_1, ..., B_N` a COMPLETE
binary subdivision of it (so the true pose of `H` lies in exactly one piece).  For a piece `b`, with
`K'(b) ⊇ K'(B_H)` its own -- strictly fatter -- polygon core used as the obstacle:

    m(b)        = 0 if EVERY pose of b misses int C (box_misses_cell_exact), else 1
    LANE_band(b)= max # of pairwise interior-disjoint FREE squares whose pose meets int C, is in
                  BAND (chord >= 1 on l), and avoids every core        [cover with the `not_band`
                                                                        prune: OUTSIDE poses are
                                                                        discharged, they belong to
                                                                        LANE_out]
    LANE_out(b) = the same with the `band` prune                        [A161 T3's counter]
    n(b)        = LANE(b) + 1                     if m(b) = 1   [LANE over EVERY free meeter]
                = beta + LANE_out(b)               if m(b) = 0

`n(b) <= 1` on EVERY piece  ==>  `int C` is met by at most one non-pin square in every realisation
==>  SLOT-CROWD's `>= 2` is contradicted  ==>  the node is DEAD.

Two facts make this strictly stronger than T3's unconditional form and keep it sound:

* the split is TAUTOLOGOUS -- the pieces tile `B_H`, so no realisation escapes;
* on a `m(b) = 0` piece the bound is `min(beta, LANE_band) + LANE_out`, which is T3's bound with
  `M = 0`; on a `m(b) = 1` piece `H` is a meeter and BOTH lanes must be empty, but there `K'(b)` is
  much fatter than `K'(B_H)` -- `H`'s corner intrudes into the cell and blocks the band -- which is
  exactly the case the unconditional form cannot express.
* `LANE_band(b) <= beta` always (the chord row), so `min` is a free tightening and `beta` alone
  suffices on a piece where the band cover does not close.

The PI's case, `c0_Y0169 / TL(0,0)` (trump5, `H` at x 1.2398-1.3795, y 2.3578-2.4976, tilt
14.25-28.07 deg): the wall is the LEFT wall of the TL frame, carrying the two pins below the cell, so
`beta = 1`; `M = 1` because part of `H`'s box reaches the cell. On the `B_miss` pieces nothing from
the right can reach `TL` (the gap above `H` is under 1) so `LANE_out = 0`; on the `B_meet` pieces
`H`'s corner occupies the right part of the cell, leaving under 1 of width for a band square, so
`LANE_band = 0` and `H` is the sole meeter.

    python condlane.py --nid c0_Y0169 --slot "TL(0,0)"
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import chordlane as CL  # noqa: E402
import numpy as np  # noqa: E402
import polylane as P  # noqa: E402
import polycore as PC  # noqa: E402
import guardline as GL  # noqa: E402
from caselp import Box  # noqa: E402
from fractions import Fraction as Fr  # noqa: E402


def piece_bound(cell, others, piece_cs, line, beta, s, max_depth, max_open, deadline,
                keep_cert=True, band_open=None):
    """`n(b)` for one piece of `H`'s box.

    Two regimes, and each needs only ONE cover:

    * `m(b) = 0`: `H` is not a meeter, so `n(b) = beta + LANE_out(b)` -- one cover.
    * `m(b) = 1`: `H` is a meeter, so `n(b) = min(beta, LANE_band(b)) + LANE_out(b) + 1` and BOTH
      lanes must be empty.  They are run as TWO covers rather than one plain cover over all free
      meeters, because each carries an extra sound prune (`band` / `not_band`) that discharges half
      the window outright -- a single plain cover has neither and does not close.
    """
    b = piece_cs.box
    misses, mdet = CL.box_misses_cell_exact(b, cell)
    m = 0 if misses else 1
    conds = others + [piece_cs]
    out = dict(box=P.box_json(b), misses_cell=bool(misses), misses_detail=mdet, m=m)
    # LANE_out is always needed and is the cheap one (the `band` prune discharges the whole wall
    # lane at once); LANE_band is needed only when H is a meeter.
    co = CL.lane_out(cell, conds, line, s=s, max_depth=max_depth, max_open=max_open,
                     deadline=deadline, band_mode="out")
    out.update(lane_out=co["lane"], out_leaves=len(co["leaves"]), out_open=len(co["open"]),
               out_reason=co.get("reason"), root=co["root"])
    if co["lane"] is None:
        out.update(lane_band=None, total=None, ok=False)
        if keep_cert:
            out["out_leaves_cert"] = out["out_open_cert"] = None
        return out
    if m == 0:
        out.update(lane_band=None, total=beta + co["lane"], ok=(beta + co["lane"] <= 1))
    else:
        cb = CL.lane_out(cell, conds, line, s=s, max_depth=max_depth, max_open=band_open,
                         deadline=deadline, band_mode="band")
        out.update(lane_band=cb["lane"], band_leaves=len(cb["leaves"]),
                   band_open=len(cb["open"]), band_reason=cb.get("reason"))
        if cb["lane"] is None:
            out.update(total=None, ok=False)
        else:
            lb = min(beta, cb["lane"])
            tot = lb + co["lane"] + 1
            out.update(band_used=lb, total=tot, ok=(tot <= 1))
        if keep_cert:
            out["band_leaves_cert"] = cb["leaves"] if cb["lane"] is not None else None
            out["band_open_cert"] = cb["open"] if cb["lane"] is not None else None
    if keep_cert:
        out["out_leaves_cert"] = co["leaves"]
        out["out_open_cert"] = co["open"]
    return out


def sample_child(cell, conds, line, piece_box, s, n, rng):
    """Per-child sample line: poses of H drawn from the PIECE (how many meet int C), and poses in
    the pose window (how many are FREE meeters, split band / outside)."""
    b = piece_box
    C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
    T = np.radians(rng.uniform(b.th0, b.th1, n)) if b.th1 > b.th0 else \
        np.full(n, np.radians(b.th0))
    h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
    inside = ((C[:, 0] >= h) & (C[:, 0] <= s - h) & (C[:, 1] >= h) & (C[:, 1] <= s - h))
    meets = inside & P.rect_square_meets(cell, C, T)
    pool = CL.sample_pool(cell, conds, s, n, rng)
    sm = CL.sample_split(pool, line)
    return dict(H_drawn=n, H_admissible=int(inside.sum()), H_meeting_cell=int(meets.sum()),
                pose_drawn=sm.get("drawn"), pose_meeting=sm.get("meeting"),
                free=sm.get("free"), band_free=sm.get("band_free"),
                outside_free=sm.get("outside_free"), band=sm.get("band"),
                outside=sm.get("outside"), min_chord_band=sm.get("min_chord_band"))


def run(rec, slot, rng=None, max_pieces=64, max_depth=8, cover_depth=36, max_open=3000,
        sample=12000, budget_s=240.0, keep_cert=True, n_lines=48, force_off=None,
        band_open=None):
    rng = rng if rng is not None else np.random.default_rng(1618)
    dl = time.time() + budget_s
    s = CL.S0
    conds, meet, cell, corner, i, j = CL.frame_boxes(rec, slot)
    row = dict(nid=rec["nid"], src=rec["src"], cls=rec["cls"], level=rec["level"], slot=slot,
               cell=list(cell), corner=corner, ij=[i, j], n_pins=len(conds) - len(meet),
               cond_index=list(meet), verdict="UNDECIDED")
    if len(meet) != 1:
        row["verdict"] = "NOT-SINGLE-CONDITIONED (%d)" % len(meet)
        return row, None
    jH = meet[0]
    others = [c for c in conds if c.idx != jH]
    B_H = conds[jH].box
    orients = CL.WALL_ORIENT.get((i, j)) or ()
    if not orients:
        row["verdict"] = "NOT-WALL-ADJACENT"
        return row, None

    # ---- pick the guard line: smallest beta, then the deepest band margin on the free poses
    best = None
    for orient in orients:
        pool = CL.sample_pool(cell, conds, s, sample, rng)
        cands = ([GL.Line(orient, Fr(force_off), tag="forced")] if force_off is not None
                 else CL.line_candidates(orient, n=n_lines))
        for ln in cands:
            rhs, beta, terms = CL.guard_rhs([c.box for c in conds], ln, s=CL.S_RAT)
            if beta is None:
                row.update(verdict="CHORD-CONTRADICTION", line=ln.to_json(), rhs=str(rhs))
                return row, None
            sm = CL.sample_split(pool, ln)
            key = (beta, sm.get("outside_free", 10 ** 9),
                   -(sm.get("band_margin_min_free") or -9.0))
            if best is None or key < best[0]:
                best = (key, orient, ln, rhs, beta, terms, sm)
    key, orient, ln, rhs, beta, terms, sm = best
    row.update(line=ln.to_json(), rhs=str(rhs), rhs_float=float(rhs), beta=beta,
               minchords=terms, sample={k: v for k, v in sm.items() if k != "per_core"})
    if beta >= 2:
        row["verdict"] = "RETIRED-beta>=2"
        return row, None

    # ---- the tautologous split of H's box
    stack = [("", B_H)]
    done, opens = [], []
    while stack:
        path, b = stack.pop()
        if time.time() > dl:
            opens.append(dict(path=path, box=P.box_json(b), why="time budget"))
            break
        try:
            pc = P.build_cond([b], tighten=False)[0]
        except Exception as e:                                    # noqa: BLE001
            opens.append(dict(path=path, box=P.box_json(b), why="polycore build: %r" % e))
            continue
        pc.idx = jH
        r = piece_bound(cell, others, pc, ln, beta, s, cover_depth, max_open, dl,
                        keep_cert=keep_cert, band_open=band_open or max_open)
        r["path"] = path
        if r["ok"]:
            done.append(r)
            continue
        if len(path) >= max_depth or len(done) + len(stack) + len(opens) >= max_pieces:
            opens.append(r)
            continue
        b0, b1 = P.split_box(b)
        stack.append((path + "0", b0))
        stack.append((path + "1", b1))
    row.update(n_pieces=len(done) + len(opens), n_done=len(done), n_open=len(opens),
               verdict=("KILL" if not opens else "UNDECIDED"))
    if opens:
        row["open_pieces"] = [{k: v for k, v in o.items()
                               if k in ("path", "box", "m", "lane_out", "lane_band",
                                        "total", "out_reason", "band_reason", "why")}
                              for o in opens[:6]]
        return row, None

    # ---- per-child sample line
    samples = []
    for r in done:
        pc = P.build_cond([Box(*r["box"])], tighten=False)[0]
        pc.idx = jH
        samples.append(dict(path=r["path"],
                            **sample_child(cell, others + [pc], ln, Box(*r["box"]), s,
                                           max(10000, sample), rng)))
    row["child_samples"] = samples
    row["pieces_summary"] = [dict(path=r["path"], m=r["m"], lane_out=r["lane_out"],
                                  lane_band=r.get("lane_band"), total=r["total"],
                                  out_leaves=r.get("out_leaves"),
                                  band_leaves=r.get("band_leaves")) for r in done]
    cert = None
    if keep_cert:
        cert = dict(
            leaf="conditional_chord_limited_lane_v1",
            claim="a COMPLETE binary subdivision of the conditioned square's box on which "
                  "min(beta, LANE_band) + LANE_out + m <= 1 everywhere; hence int C is met by at "
                  "most one non-pin square in every realisation, contradicting SLOT-CROWD",
            s=str(CL.S_RAT), s_float=s, nid=rec["nid"], src=rec["src"], cls=rec["cls"],
            level=rec["level"], slot=slot, corner=corner, ij=[i, j], cell=list(cell),
            cell_kind="usable_slot",
            extension=CL.CP.CLASSES[rec["cls"]]["usable"][slot],
            extension_window="[191/50, 969271/250000] FULL (A56/A61/A114 scoreboard)",
            frame="A118 lane.cframe_boxes, hulled over m in [m_lo, s0]",
            m_lo=CL.LANE.M_LO.get(rec["src"], 3.82),
            n_pins=row["n_pins"], cond_index=[jH],
            hyp_boxes=[P.box_json(c.box) for c in conds],
            split_root=P.box_json(B_H),
            split_rule="widest of (x, y, theta/60), deterministic (A141 polylane.split_box)",
            guardline=dict(orient=ln.orient, off=str(ln.off), off_float=ln.foff, tag=ln.tag,
                           rhs=str(rhs), rhs_float=float(rhs), beta=beta, minchords=terms,
                           band_rule="chord >= 1  <=>  |v| <= (y + 1 - y^2)/2 at y = cs_max; "
                                     "chord < 1 for every pose  <=  min|v| > the same at cs_min"),
            pieces=done, child_samples=samples, verdict="KILL",
        )
    return row, cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="c0_Y0169")
    ap.add_argument("--slot", default="TL(0,0)")
    ap.add_argument("--budget", type=float, default=300.0)
    ap.add_argument("--maxpieces", type=int, default=64)
    ap.add_argument("--maxopen", type=int, default=3000)
    ap.add_argument("--bandopen", type=int, default=0)
    ap.add_argument("--sample", type=int, default=12000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t8_cond.json"))
    a = ap.parse_args()
    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    rec = recs[a.nid]
    t0 = time.time()
    row, cert = run(rec, a.slot, max_pieces=a.maxpieces, max_open=a.maxopen, sample=a.sample,
                    budget_s=a.budget, band_open=(a.bandopen or None))
    print("%s %s -> %s  beta=%s pieces=%s (done %s, open %s)  %.0f s"
          % (a.nid, a.slot, row["verdict"], row.get("beta"), row.get("n_pieces"),
             row.get("n_done"), row.get("n_open"), time.time() - t0), flush=True)
    if "line" in row:
        print("  guard line %s = %s  rhs = %s" % (row["line"]["orient"], row["line"]["off"],
                                                  row.get("rhs")), flush=True)
    for p in (row.get("pieces_summary") or [])[:12]:
        print("   piece %-9s m=%d LANE_out=%s LANE_band=%s total=%s (leaves %s/%s)"
              % (p["path"] or "(root)", p["m"], p["lane_out"], p["lane_band"], p["total"],
                 p.get("out_leaves"), p.get("band_leaves")), flush=True)
    for o in (row.get("open_pieces") or [])[:6]:
        print("   OPEN  %-9s m=%s LANE_out=%s LANE_band=%s (%s | %s)"
              % (o.get("path"), o.get("m"), o.get("lane_out"), o.get("lane_band"),
                 o.get("out_reason"), o.get("band_reason")), flush=True)
    for sc in (row.get("child_samples") or [])[:12]:
        print("   sample %-8s H drawn %d, meeting cell %d | poses %d, free %d (band %d, outside %d)"
              % (sc["path"] or "(root)", sc["H_drawn"], sc["H_meeting_cell"], sc["pose_meeting"],
                 sc["free"], sc["band_free"], sc["outside_free"]), flush=True)
    if cert is not None:
        q = os.path.join(BASE, "certs_cond", "cond_%s__%s.json"
                         % (a.nid, a.slot.replace("(", "").replace(")", "").replace(",", "_")))
        os.makedirs(os.path.dirname(q), exist_ok=True)
        blob = json.dumps(cert, sort_keys=True, indent=1).encode("utf-8")
        open(q, "wb").write(blob)
        row["cert"] = os.path.relpath(q, ROOT)
        row["sha256"] = hashlib.sha256(blob).hexdigest()
        print("  cert %s sha256 %s" % (row["cert"], row["sha256"][:16]), flush=True)
    json.dump(row, open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
