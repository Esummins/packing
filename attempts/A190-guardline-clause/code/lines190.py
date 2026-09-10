"""A190 -- the guard-line GRID of a node and the selection of the lines that carry the LP.

The family (docs/proofs/guardline_clause.md sec. 5): A144's `line_family` (pin core edges and midlines, K'(H)'s
extreme and mid x/y, the container eighths) + the container SIXTEENTHS + A188's pin-row / pin-column lines at the
quartiles of the pins' full-chord interval + the page's own best band line (consumer188: the c maximising
minchord(H, l)); deduplicated on a 1e-9 grid, clipped to the open container, capped at 64.  The <= K lines with
the largest OFFLINE violation on the stored dual support carry the LP (A144's rule), the consumer's line always
among them; every rhs is A144's exact `guard_row`.  Read-only on A144 / A57.
"""
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
A144C = os.path.join(ATT, "A144-guard-lines", "code")
for _p in (A144C, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import guardline as G                                            # noqa: E402  (A144, read-only)
import guardlp                                                   # noqa: E402  (A144, read-only)
import polycore                                                  # noqa: E402  (A132, read-only)

S_RAT = G.S_RAT
PIN_H = Fr(1, 100) / G.SQRT2_LO                                  # rational UPPER bound of delta/sqrt2


def _pin_rows(pins):
    """A188's pin lines: for each pin row / column the interval of offsets on which EVERY pin of the row has a
    full unit chord (|v| <= 1/2 - h for the whole slack core), at its quartiles."""
    out = []
    for orient in ("h", "v"):
        groups = {}
        for b in pins:
            c = Fr(round(0.5 * ((b.y0 + b.y1) if orient == "h" else (b.x0 + b.x1)), 6))
            groups.setdefault(c, []).append(b)
        for c, bs in groups.items():
            lo, hi = c - (Fr(1, 2) - PIN_H), c + (Fr(1, 2) - PIN_H)
            for q in (Fr(1, 4), Fr(1, 2), Fr(3, 4)):
                out.append(G.Line(orient, lo + q * (hi - lo), "pin row k=%d q%s" % (len(bs), q)))
    return out


def family(pins, hbox, best=None, s=S_RAT, max_lines=64):
    """the node's grid; `best` = (orient, c) from consumer188, added first with tag 'consumer188 best'."""
    try:
        pcv = polycore.build(hbox, max_v=16).verts
    except Exception:                                            # noqa: BLE001
        pcv = None
    extra = list(_pin_rows(pins))
    extra += [G.Line("h", Fr(k, 16) * s, "grid h %d/16" % k) for k in range(1, 16) if k % 2]
    extra += [G.Line("v", Fr(k, 16) * s, "grid v %d/16" % k) for k in range(1, 16) if k % 2]
    if best is not None:
        o, c = best
        extra.insert(0, G.Line(o, Fr(round(float(c) * G.LDEN), G.LDEN), "consumer188 best"))
    fam = G.line_family(pins, hbox, s=s, pc_verts=pcv, max_lines=max_lines, extra=extra)
    return fam, pcv


def select(rec, pins, hbox, fam, pcv, k=8):
    """(lines with costs attached, report rows): the k largest offline violations on the stored support, the
    consumer's line always kept."""
    scored = []
    for L in fam:
        gr = G.guard_row(pins, hbox, L, pc_verts=pcv)
        _c, lhs = G.support_chords(rec, L, a=0.5)
        scored.append((lhs - gr["rhs_float"], L, gr))
    scored.sort(key=lambda x: -x[0])
    chosen = scored[:k]
    for x in scored[k:]:
        if x[1].tag == "consumer188 best" and not any(y[1].tag == "consumer188 best" for y in chosen):
            chosen[-1] = x
    lines = guardlp.attach_costs([x[1] for x in chosen], [x[2] for x in chosen])
    rows = [dict(line=L.to_json(), rhs=str(gr["rhs"]), rhs_float=gr["rhs_float"], offline_viol=v,
                 pins_full=gr["n_pins_full"], h_minchord=gr["h_float"], uses=gr["uses"])
            for (v, L, gr) in chosen]
    return lines, rows, len(fam)
