"""A191 -- the guard-line grid of a CASCADE node (roles = windowed, cored squares; no pins) and the selection of
the lines that carry the LP (A144's rule: the K largest OFFLINE violations on a dual support).

The family: the container sixteenths; per role (H, D, S, B ...) the lines through its bbox centre, its bbox edges
+-1/2 (where the role's own square must end) and K'(role)'s extreme / mid x and y.  Every role is WINDOWED and its
core ATTACHED, so no core enters rhs* (Theorem G: an attached core's square is counted by its window and enters
rhs* not at all) and rhs*(l) = s exactly for every line; the row's power at a cascade node is the chord the
window walk charges the windowed squares (G3) plus what the free squares' chords sum to on one line.
Read-only on A144 / A57 / A168.
"""
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(ATT, "A168-cascade-fable", "code"), os.path.join(ATT, "A144-guard-lines", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import cas168 as K                                               # noqa: E402  (A168, read-only; pulls A144's path)
import guardline as G                                            # noqa: E402  (A144, read-only)
import guardlp                                                   # noqa: E402  (A144, read-only)

S_RAT = K.S_RAT
LDEN = G.LDEN


def _q(x):
    return Fr(round(float(x) * LDEN), LDEN)


def family(roles, s=S_RAT, max_lines=64):
    """the node's grid as A144 Lines (tags record provenance); deduplicated on the 1e-9 grid, inside (0, s)."""
    cand = []
    for k in range(1, 16):
        cand.append(("h", Fr(k, 16) * s, "grid h %d/16" % k))
        cand.append(("v", Fr(k, 16) * s, "grid v %d/16" % k))
    for r in roles:
        b = r.bbox()
        cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
        cand += [("h", _q(cy), "%s centre y" % r.name), ("v", _q(cx), "%s centre x" % r.name),
                 ("h", _q(b.y0 - 0.5), "%s bottom edge" % r.name), ("h", _q(b.y1 + 0.5), "%s top edge" % r.name),
                 ("v", _q(b.x0 - 0.5), "%s left edge" % r.name), ("v", _q(b.x1 + 0.5), "%s right edge" % r.name)]
        if r.core:
            xs = [Fr(v[0]) for v in r.core]
            ys = [Fr(v[1]) for v in r.core]
            cand += [("v", _q(min(xs)), "K'(%s) min x" % r.name), ("v", _q(max(xs)), "K'(%s) max x" % r.name),
                     ("v", _q((min(xs) + max(xs)) / 2), "K'(%s) mid x" % r.name),
                     ("h", _q(min(ys)), "K'(%s) min y" % r.name), ("h", _q(max(ys)), "K'(%s) max y" % r.name),
                     ("h", _q((min(ys) + max(ys)) / 2), "K'(%s) mid y" % r.name)]
    seen, out = set(), []
    for (o, off, tg) in cand:
        off = Fr(off)
        if not (Fr(0) < off < s):
            continue
        key = (o, off)
        if key in seen:
            continue
        seen.add(key)
        out.append(G.Line(o, off, tg))
        if len(out) >= max_lines:
            break
    return out


def select(support, fam, k=8, s=S_RAT, boxes=None):
    """(lines with costs attached, report rows): the k largest offline violations SUM_p y_p |l n Q_p| - rhs on the
    dual support (a list of dicts cx, cy, theta, y).  rhs = s exactly when every core is attached (`boxes` None);
    with `boxes` (the v1-style LP: the roles' union boxes carry UNATTACHED exact cores) rhs = s - SUM_j
    minchord(box_j, l) (A144's guard_row; the verifier re-derives rhs* from the cores' pbox = these boxes)."""
    rec = dict(packing=support or [])
    scored = []
    for L in fam:
        rhs = Fr(s)
        terms = []
        if boxes:
            for b in boxes:
                lo = G.minchord_box(b, L, a=G.HALF)["lo"]
                terms.append(lo)
                rhs -= lo
        _c, lhs = G.support_chords(rec, L, a=0.5)
        scored.append((lhs - float(rhs), L, rhs, terms))
    scored.sort(key=lambda x: -x[0])
    chosen = scored[:k]
    rows = [dict(rhs=rhs, rhs_float=float(rhs)) for (_v, _L, rhs, _t) in chosen]
    lines = guardlp.attach_costs([x[1] for x in chosen], rows)
    rep = [dict(line=L.to_json(), rhs=str(rhs), rhs_float=float(rhs), offline_viol=v, box_terms=[float(t) for t in terms])
           for (v, L, rhs, terms) in chosen]
    return lines, rep
