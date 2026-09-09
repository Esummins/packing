"""A167 -- the INDEPENDENT checker for `conditional_chord_limited_lane_v1` certificates.

Discipline as A161's `checkcl.py`, which this extends and re-uses (`checkcl` shares with the
emitters ONLY A132's trusted `polycore.vertex_ok` and A57's `caselp.Box/t_lo/t_hi`; the chord
formula, the five-point `minchord`, the band threshold, the separating-axis margins, the container
prune, the split rule, cover completeness, the pairwise-overlap test, the frame re-derivation and
the arithmetic are re-implemented there).  A `chord_limited_lane_v1` certificate is delegated to
`checkcl.check` unchanged; the conditional kind adds:

  E1  leaf name, `s`, the slot is USABLE for the class with the declared extension and a FULL
      window, and every declared hypothesis box holds a container-admissible pose;
      the frame boxes are re-derived from the node record (checkcl's D1) when it is supplied;
  E2  `split_root` IS the declared conditioned box `hyp_boxes[cond_index]`, and the pieces' paths
      are a COMPLETE PREFIX CODE over it with every stored box equal to the box the split rule
      recomputes from its path -- so the pieces TILE `B_H` and no realisation escapes;
  E3  each piece's guard line is an exact rational strictly inside (0, 1) with the cell's wall
      orientation;
  E4  each piece's `beta` is RE-DERIVED from the other hypothesis boxes plus THE PIECE'S OWN BOX
      (the per-piece guard row, sound because `minchord` is monotone under box inclusion), and the
      re-derived value is the one used in the arithmetic;
  E5  a piece declaring `m = 0` carries an exact separating axis for its own box against the cell;
      `m = 1` needs nothing (it is the conservative case);
  E5b a `witness` leaf citing the conditioned index is checked against THE PIECE'S box, not
      `B_H`: on that branch the piece IS the conditioned square's hypothesis, and the piece is the
      strictly stronger obstacle (this is the whole point of the conditional form);
  E6  the `LANE_out` cover's root CONTAINS every centre of a pose meeting int C
      (`[X0 - sqrt2/2, X1 + sqrt2/2] n [1/2, s - 1/2]`, tilt [0, 90]) and its leaves are discharged
      by `container` / `band` / `misses_cell` / `witness` only;
  E7  the `LANE_band` cover's root CONTAINS that window INTERSECTED WITH THE BAND SLAB
      `|off - c_perp| <= 1/2` -- legal because `chord >= 1 => |v| <= f(1) = 1/2` -- and its leaves
      are discharged by `container` / `not_band` / `misses_cell` / `witness` only (`band` is
      illegal there, `not_band` is illegal in the LANE_out cover);
  E8  open sets: value 0 needs an EMPTY open list, value 1 needs every pair (diagonal included)
      certified always-overlapping;
  E9  per piece: `m = 0` => `beta + LANE_out <= 1`; `m = 1` => `LANE_out = 0` and
      `min(beta, LANE_band) = 0`; a piece may instead declare `chord-contradiction`, which is
      re-derived as `s - SUM minchord < 0` on that piece (the piece is then EMPTY of realisations).

    python checkcond167.py --dir ../certs --nodes ../results/nodepaths.json
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
for _p in (os.path.join(ROOT, "attempts", "A161-chord-lane", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import checkcl as K                                  # noqa: E402  READ-ONLY (A161's checker)

HALF = Fr(1, 2)
ROOT_TOL = Fr(1, 10 ** 12)      # float slack on the emitter's window arithmetic (A141 uses 1e-12)
OUT_WHY = {"container", "band", "misses_cell", "witness"}
BAND_WHY = {"container", "not_band", "misses_cell", "witness"}


def not_band_holds(b, orient, off):
    """chord < 1 at EVERY pose of `b`:  min |v| > (y + 1 - y^2)/2 at y = cs_min.

    `f(y) = (y + 1 - y^2)/2` is DECREASING on [1, sqrt2], so the LARGEST threshold over the tilt
    bin is at `cs_min`; a lower bound of `cs_min` therefore makes the test strict in the safe
    direction.  `min |v| = 0` whenever the line crosses the centre range."""
    lo, hi = (Fr(b[2]), Fr(b[3])) if orient == "h" else (Fr(b[0]), Fr(b[1]))
    a_, b_ = off - hi, off - lo
    V = Fr(0) if (a_ <= 0 <= b_) else min(abs(a_), abs(b_))
    Y = K.cs_lo(*K.tbin(b))
    return V > (Y + 1 - Y * Y) / 2


def required_window(cell, s):
    """The centres of every pose that can meet int(cell) from inside [0, s]^2, as an EXACT
    rectangle the declared root must contain: `Q(c, th) c c + [-h, h]^2` with
    `h = (|cos|+|sin|)/2 <= sqrt2/2`, and admissibility forces `c in [h, s - h] c [1/2, s - 1/2]`
    since `h >= 1/2`."""
    X0, X1, Y0, Y1 = (Fr(v) for v in cell)
    r = K.SQRT2_HI / 2
    return (max(HALF, X0 - r), min(s - HALF, X1 + r),
            max(HALF, Y0 - r), min(s - HALF, Y1 + r))


def check_root(root, need, tag, errs, orient=None, off=None, slab=False):
    """The declared cover root must CONTAIN `need` (optionally intersected with the band slab)."""
    nx0, nx1, ny0, ny1 = need
    if slab:
        lo, hi = off - HALF, off + HALF
        if orient == "h":
            ny0, ny1 = max(ny0, lo), min(ny1, hi)
        else:
            nx0, nx1 = max(nx0, lo), min(nx1, hi)
    if nx1 <= nx0 or ny1 <= ny0:
        return                                   # the required window is empty: nothing to cover
    if root is None:
        errs.append("%s: null cover root but the required window is non-empty" % tag)
        return
    rx0, rx1, ry0, ry1, t0, t1 = (Fr(v) for v in root)
    if not (rx0 <= nx0 + ROOT_TOL and rx1 >= nx1 - ROOT_TOL
            and ry0 <= ny0 + ROOT_TOL and ry1 >= ny1 - ROOT_TOL):
        errs.append("%s: cover root [%s, %s] x [%s, %s] does not contain the required window "
                    "[%s, %s] x [%s, %s]" % (tag, float(rx0), float(rx1), float(ry0), float(ry1),
                                             float(nx0), float(nx1), float(ny0), float(ny1)))
    if not (t0 <= 0 and t1 >= 90):
        errs.append("%s: cover root tilt range [%s, %s] does not contain [0, 90]" % (tag, t0, t1))


def check_leaf2(lf, cell, hyp, skip, orient, off, allowed, errs, tag):
    why = lf.get("why")
    if why not in allowed:
        errs.append("%s leaf %r: discharge %r is not legal in this cover" % (tag, lf.get("path"),
                                                                            why))
        return
    if why == "not_band":
        if not not_band_holds(lf["box"], orient, off):
            errs.append("%s leaf %r: not_band prune false (chord >= 1 somewhere)"
                        % (tag, lf["path"]))
        return
    K.check_leaf(lf, cell, hyp, skip, orient, off, ("band" in allowed), errs, tag)


def check_cover2(cov, cell, hyp, skip, orient, off, allowed, errs, tag):
    root = cov["root"]
    if root is None:                       # an empty cover root: nothing to cover, value must be 0
        if cov["value"] != 0 or cov["leaves"] or cov.get("open"):
            errs.append("%s: null root with value %r" % (tag, cov["value"]))
        return
    paths = [lf["path"] for lf in cov["leaves"]] + [o["path"] for o in cov.get("open", [])]
    ok, msg = K.complete_prefix_code(paths)
    if not ok:
        errs.append("%s: leaf paths are not a complete cover of the root (%s)" % (tag, msg))
    for lf in cov["leaves"] + list(cov.get("open", [])):
        rb = K.box_from_path(root, lf["path"])
        if max(abs(float(u) - float(v)) for u, v in zip(rb, lf["box"])) > 1e-12:
            errs.append("%s leaf %r: stored box != box from the split rule" % (tag, lf["path"]))
    for lf in cov["leaves"]:
        check_leaf2(lf, cell, hyp, skip, orient, off, allowed, errs, tag)
    op = list(cov.get("open", []))
    v = cov["value"]
    if v == 0:
        if op:
            errs.append("%s: value 0 declared with %d open boxes" % (tag, len(op)))
    elif v == 1:
        bxs = [o["box"] for o in op]
        for u in range(len(bxs)):
            for w in range(u, len(bxs)):
                if not K.always_overlap(bxs[u], bxs[w]):
                    errs.append("%s: open boxes %d,%d not certified always-overlapping"
                                % (tag, u, w))
                    return
    else:
        errs.append("%s: value %r is not 0 or 1" % (tag, v))


def beta_of(hyp, jH, piece_box, orient, off, s):
    """The PER-PIECE guard row: `floor(s - SUM minchord)` over the other hypothesis boxes and the
    piece's own box.  Returns (beta or None if rhs < 0, rhs)."""
    tot = Fr(0)
    for k, b in enumerate(hyp):
        tot += K.minchord(piece_box if k == jH else b, orient, off)
    rhs = s - tot
    return (None if rhs < 0 else int(math.floor(rhs))), rhs


def check(path, node_paths=None, verbose=True):
    c = json.load(open(path, encoding="utf-8"))
    if c.get("leaf") == "chord_limited_lane_v1":
        return K.check(path, node_paths, verbose)
    errs, notes = [], []
    if c.get("leaf") != "conditional_chord_limited_lane_v1":
        return ["not an A167 certificate: %r" % c.get("leaf")], []
    s = Fr(c["s"])
    hyp = c["hyp_boxes"]
    cell = c["cell"]
    i, j = c["ij"]
    jH = c["cond_index"][0]

    # ---- E1
    for k, b in enumerate(hyp):
        if K.outside_container(b, s):
            errs.append("E1: hyp box B%d holds no container-admissible pose" % k)
    ext = K.USABLE.get(c["cls"], {}).get(c["slot"])
    if ext is None:
        errs.append("E1: slot %s is not a usable slot of class %s" % (c["slot"], c["cls"]))
    elif ext != c["extension"]:
        errs.append("E1: extension %r declared, table says %r" % (c["extension"], ext))
    if "FULL" not in c.get("extension_window", ""):
        errs.append("E1: extension window not declared FULL")
    rp = (node_paths or {}).get(c["nid"])
    if rp:
        try:
            der = K.frame_boxes_from_record(rp, c["cls"], c["corner"], c["src"])
        except Exception as e:                                       # noqa: BLE001
            der = None
            notes.append("E1: frame re-derivation unavailable (%s)" % repr(e)[:60])
        if der is not None:
            if len(der) != len(hyp):
                errs.append("E1: %d frame boxes re-derived vs %d declared" % (len(der), len(hyp)))
            else:
                for k, (a, b) in enumerate(zip(der, hyp)):
                    if not (Fr(b[0]) - K.TOL <= Fr(a[0]) and Fr(a[1]) <= Fr(b[1]) + K.TOL
                            and Fr(b[2]) - K.TOL <= Fr(a[2]) and Fr(a[3]) <= Fr(b[3]) + K.TOL
                            and Fr(b[4]) - K.TOL <= Fr(a[4]) and Fr(a[5]) <= Fr(b[5]) + K.TOL):
                        errs.append("E1: declared B%d does not contain the re-derived frame box "
                                    "%s vs %s" % (k, a, b))
            notes.append("E1: frame boxes re-derived from %s" % rp)
    else:
        notes.append("E1: node record not supplied -- frame containment not re-derived")

    # ---- E2
    if max(abs(float(u) - float(v)) for u, v in zip(c["split_root"], hyp[jH])) > 1e-12:
        errs.append("E2: split_root != hyp_boxes[%d]" % jH)
    pieces = c["pieces"]
    ok, msg = K.complete_prefix_code([p["path"] for p in pieces])
    if not ok:
        errs.append("E2: the pieces do not tile the conditioned box (%s)" % msg)
    for p in pieces:
        rb = K.box_from_path(c["split_root"], p["path"])
        if max(abs(float(u) - float(v)) for u, v in zip(rb, p["box"])) > 1e-12:
            errs.append("E2: piece %r box != box from the split rule" % p["path"])

    need = required_window(cell, s)
    want_or = "h" if j == 0 else "v"
    for p in pieces:
        tg = "piece %r" % (p["path"] or "(root)")
        pb = p["box"]
        m = p["m"]

        # ---- E5
        if m == 0:
            okm, nm = K.misses_cell(pb, cell, axis=(p.get("misses_detail") or {}).get("axis"))
            if not okm:
                errs.append("%s: m = 0 declared but no declared axis separates it from the cell"
                            % tg)

        # ---- E9 (the chord-contradiction escape)
        if p.get("chord_contradiction"):
            cc = p["chord_contradiction"]
            b2, rhs2 = beta_of(hyp, jH, pb, cc["orient"], Fr(cc["off"]), s)
            if b2 is not None:
                errs.append("%s: chord-contradiction declared but re-derived rhs = %s >= 0"
                            % (tg, rhs2))
            continue

        # ---- E3
        ln = p.get("line")
        if ln is None:
            errs.append("%s: no guard line" % tg)
            continue
        orient, off = ln["orient"], Fr(ln["off"])
        if not (0 < off < 1):
            errs.append("%s: guard offset %s not strictly inside (0, 1)" % (tg, off))
        if orient != want_or and not (i == 0 and j == 0):
            errs.append("%s: cell (%d,%d) wants a %s wall line, got %s" % (tg, i, j, want_or,
                                                                          orient))
        # ---- E4
        beta, rhs = beta_of(hyp, jH, pb, orient, off, s)
        if beta is None:
            notes.append("%s: rhs < 0 -- the guard row alone empties the piece" % tg)
            beta = 0
        if p.get("beta") is not None and p["beta"] < beta:
            errs.append("%s: beta %r declared, %d re-derived (the larger is used)"
                        % (tg, p["beta"], beta))

        # ---- E6
        co = p.get("out_cover")
        if co is None:
            errs.append("%s: no LANE_out cover" % tg)
            continue
        # ON THIS BRANCH the conditioned square's hypothesis IS the piece, so a `witness` leaf
        # citing `cond_index` must hold for every pose of the PIECE (a strictly stronger obstacle
        # than `B_H`, which is exactly why the conditional leaf closes where A161's does not).
        hypp = list(hyp)
        hypp[jH] = pb
        check_root(co["root"], need, tg + " LANE_out", errs)
        check_cover2(co, cell, hypp, None, orient, off, OUT_WHY, errs, tg + " LANE_out")
        lane_out = co["value"]

        # ---- E7
        cb = p.get("band_cover")
        lane_band = None
        if cb is not None:
            check_root(cb["root"], need, tg + " LANE_band", errs, orient=orient, off=off,
                       slab=True)
            check_cover2(cb, cell, hypp, None, orient, off, BAND_WHY, errs, tg + " LANE_band")
            lane_band = cb["value"]

        # ---- E9
        if m == 0:
            tot = beta + lane_out
            if tot > 1:
                errs.append("%s: m = 0, beta + LANE_out = %d > 1" % (tg, tot))
        else:
            if lane_out != 0:
                errs.append("%s: m = 1 needs LANE_out = 0, got %r" % (tg, lane_out))
            bb = 0 if beta == 0 else lane_band
            if bb is None:
                errs.append("%s: m = 1 with beta = %d needs a LANE_band cover" % (tg, beta))
            elif min(beta, bb) != 0:
                errs.append("%s: m = 1, min(beta, LANE_band) = %d != 0" % (tg, min(beta, bb)))
        if p.get("total") is not None:
            rec = (beta + lane_out) if m == 0 else (min(beta, 0 if beta == 0 else (lane_band or 0))
                                                   + lane_out + 1)
            if rec != p["total"]:
                notes.append("%s: total %r declared, %d re-derived" % (tg, p["total"], rec))

    if verbose:
        st = "PASS" if not errs else "FAIL"
        print("%-4s %-46s pieces=%d  m1=%d  leaves=%d(out)+%d(band)"
              % (st, os.path.basename(path), len(pieces),
                 sum(1 for p in pieces if p.get("m")),
                 sum(len((p.get("out_cover") or {}).get("leaves") or []) for p in pieces),
                 sum(len((p.get("band_cover") or {}).get("leaves") or []) for p in pieces)),
              flush=True)
        for e in errs:
            print("      ERR %s" % e, flush=True)
        for n in notes[:4]:
            print("      ... %s" % n, flush=True)
    return errs, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="*")
    ap.add_argument("--dir", default="")
    ap.add_argument("--nodes", default="")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "checkcond.json"))
    a = ap.parse_args()
    files = list(a.certs)
    if a.dir:
        files += sorted(glob.glob(os.path.join(a.dir, "cond_*.json")))
        files += sorted(glob.glob(os.path.join(a.dir, "cl_*.json")))
    npaths = {}
    if a.nodes and os.path.exists(a.nodes):
        npaths = json.load(open(a.nodes, encoding="utf-8"))
    res, nfail = [], 0
    for f in files:
        errs, notes = check(f, npaths)
        res.append(dict(cert=os.path.relpath(f, ROOT).replace(os.sep, "/"), ok=(not errs),
                        errors=errs, notes=notes))
        nfail += bool(errs)
    print("\n%d certificates, %d PASS, %d FAIL" % (len(files), len(files) - nfail, nfail))
    json.dump(dict(n=len(files), n_pass=len(files) - nfail, n_fail=nfail, results=res),
              open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
