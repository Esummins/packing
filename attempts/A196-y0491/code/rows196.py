"""A196 step 2 -- the CHORD ROWS of the node (Lemma LINE-1, OPEN chords; A144 guardline.minchord_box).

For an axis-parallel line l inside the container, the open chords |l n int Q_i| of the eleven squares sum to
<= s0.  A boxed role contributes at least  min over its PIECES of minchord(piece, l)  (every pose lies in some
piece; the per-piece minimum is >= the hull's minimum, so it is the tighter sound bound); a pin whose band the
line crosses contributes 1; the free squares contribute >= 0.  rhs(l) = s0 - SUM_roles;  rhs < 0 kills the
node [T]; beta = floor(rhs) is the number of free squares that can still have a UNIT chord on l.

OPEN chords, never a line ON a square edge: the chord primitive is verify_case_v5's own (guardlines_v5.minchord,
external review P0/P1 fix: an axis-aligned pose whose edge lies on the line counts 0), on each piece's outward box.
The pin lines: the four pin midlines y = 1/2, y = s0 - 1/2, x = 1/2, x = s0 - 1/2 (each pin of the row has open
chord 1 at every pose of its delta-box) plus a sweep of the band (0.02, 0.98) and its mirror, on the 1e-9 grid.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A144-guard-lines", "code"), os.path.join(ATT, "A57-shadow-trees", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import guardline as GL                                           # noqa: E402  READ-ONLY (A144)
from caselp import Box, t_lo, t_hi                               # noqa: E402  READ-ONLY (A57)
sys.path.insert(0, os.path.join(ATT, "A190-guardline-clause", "code"))
import guardlines_v5 as V5                                       # noqa: E402  READ-ONLY (A190): the verifier's exact primitive

S_RAT = GL.S_RAT
S0 = float(S_RAT)
LDEN = GL.LDEN


def _q(x):
    return Fr(round(float(x) * LDEN), LDEN)


def pin_lines(sweep=24):
    """the four pin midlines + a sweep of each pin band (offsets where every pin of the band has a unit chord)."""
    out = [("h", Fr(1, 2), "bottom pin midline y=1/2"), ("h", S_RAT - Fr(1, 2), "top pin midline y=s0-1/2"),
           ("v", Fr(1, 2), "left pin midline x=1/2"), ("v", S_RAT - Fr(1, 2), "right pin midline x=s0-1/2")]
    for k in range(1, sweep):
        v = Fr(2, 100) + Fr(96, 100) * Fr(k, sweep)
        out += [("h", v, "bottom band"), ("h", S_RAT - v, "top band"), ("v", v, "left band"), ("v", S_RAT - v, "right band")]
    lines, seen = [], set()
    for (o, off, tg) in out:
        off = _q(off)
        if (o, off) in seen or not (Fr(0) < off < S_RAT):
            continue
        seen.add((o, off))
        lines.append(GL.Line(o, off, tg))
    return lines


def minchord_pieces(pieces, line):
    """min over the role's pieces of verify_case_v5's own exact OPEN-chord primitive (guardlines_v5.minchord: t in
    [0, 1] via A57's outward t_lo / t_hi clamped, centre rect as exact rationals of the piece's outward box; an
    axis-aligned pose with the line at distance >= 1/2 -- the line ON an edge -- counts 0).  A lower bound of the
    open chord over every pose of the role [T]."""
    best = None
    for p in pieces:
        t0, t1 = max(Fr(0), t_lo(p[4])), min(Fr(1), t_hi(p[5]))
        if t0 > t1:
            t0, t1 = t1, t0
        lo = V5.minchord(GL.HALF, t0, t1, Fr(p[0]), Fr(p[1]), Fr(p[2]), Fr(p[3]), line.orient, line.off)
        best = lo if best is None else min(best, lo)
    return best if best is not None else Fr(0)


def rows(node_pieces, lines, free):
    """node_pieces = {role: [[x0,x1,y0,y1,th0,th1], ...]}.  -> [row dicts] sorted by rhs."""
    out = []
    for L in lines:
        terms = {r: minchord_pieces(P, L) for r, P in node_pieces.items()}
        tot = sum(terms.values(), Fr(0))
        rhs = S_RAT - tot
        out.append(dict(orient=L.orient, off=str(L.off), off_float=float(L.off), tag=L.tag, rhs=str(rhs), rhs_float=float(rhs),
                        beta=int(math.floor(rhs)) if rhs >= 0 else -1, negative=bool(rhs < 0),
                        minchord={r: float(v) for r, v in terms.items()},
                        pins_full=sum(1 for r, v in terms.items() if r.startswith("P") and v >= 1 - Fr(1, 10 ** 9)),
                        free=free, free_unit_max=min(free, int(math.floor(rhs))) if rhs >= 0 else 0))
    out.sort(key=lambda r: r["rhs_float"])
    return out


def summary(rws):
    named = [r for r in rws if "midline" in r["tag"]]
    neg = [r for r in rws if r["negative"]]
    b1 = [r for r in rws if 0 <= r["beta"] <= 1]
    tight = {}
    for band in ("bottom", "top", "left", "right"):
        cand = [r for r in rws if r["tag"].startswith(band)]
        if cand:
            tight[band] = min(cand, key=lambda r: r["rhs_float"])
    return dict(named=named, n_negative=len(neg), negative=neg[:8], n_beta_le1=len(b1), tightest_per_band=tight,
                tightest=rws[0] if rws else None)


def lines_from_rows(rws, k=8):
    """the k tightest rows as A144 Lines with costs attached (for guardlp) -- the LP carries these rows."""
    import guardlp                                               # READ-ONLY (A144)
    chosen = rws[:k]
    Ls = [GL.Line(r["orient"], Fr(r["off"]), r["tag"]) for r in chosen]
    return guardlp.attach_costs(Ls, [dict(rhs=Fr(r["rhs"]), rhs_float=r["rhs_float"]) for r in chosen])
