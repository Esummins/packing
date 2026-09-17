"""A243 addendum (PI, 18:00) -- Lemma WALL-SLOT and the 12-cell hypothesis (notes/wall_slot243.md).

(1) the 12 cells of a container below side 4 (four corner boxes, eight wall slots) and which squares of a ring meet
    each; (2) SLOT-MET's random search: two interior-disjoint meeters of a corner box that BOTH avoid the wall slot
    above it -- none found; (3) the wall-grain supply as a summary inequality and the leaf's verdict on a cell.
Writes results/wallslot243.md.  Corner frame as in leaves243; container [0, S]^2.
"""
import math
import os
import random
import sys

from shapely.geometry import box

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import leaves243 as L                                                   # noqa: E402
import price243 as P                                                    # noqa: E402

CORNERS = ('BL', 'BR', 'TR', 'TL')


def cells12(S):
    """the four corner boxes and the eight wall slots, as (name, box); below 4 the twelve cover the border strip."""
    out = []
    for c in CORNERS:
        u0 = 0.0 if c in ('BL', 'TL') else S - 1.0
        v0 = 0.0 if c in ('BL', 'BR') else S - 1.0
        du = 1.0 if c in ('BL', 'TL') else -1.0
        dv = 1.0 if c in ('BL', 'BR') else -1.0
        lu = u0 + du if du > 0 else u0 - 1.0                            # the slot beside the corner, along its floor
        lv = v0 + dv if dv > 0 else v0 - 1.0                            # the slot above the corner, up its wall
        out.append((c + '00', box(u0, v0, u0 + 1, v0 + 1)))
        out.append((c + '10', box(lu, v0, lu + 1, v0 + 1)))
        out.append((c + '01', box(u0, lv, u0 + 1, lv + 1)))
    return out


def ring_polys(A, B, S, alternate=True):
    """the eight bodies of the four-crowd built from the BL-frame crowd (A, B) at every corner (A237's alternating
    ring when `alternate`); labels c:A / c:B."""
    out = []
    for c in CORNERS:
        for nm, Pz in (('A', A), ('B', B)):
            out.append((c + ':' + nm, P.to_corner(L.poly(Pz), c, S, alternate=alternate)))
    return out


def meeters_of_cells(bodies, S, tol=1e-9):
    """for each of the 12 cells the labels of the bodies whose interior meets the open cell (area of overlap > tol)."""
    table = []
    for name, cell in cells12(S):
        met = [lab for lab, b in bodies if b.intersection(cell).area > tol]
        table.append((name, met))
    return table


# ---------------------------------------------------------------- SLOT-MET: the random search
def _cap_square(th, lam, vL):
    """the unit square of tilt th whose leftmost vertex is L = (1 - lam, vL): its cap left of u = 1 is the right-angled
    triangle at L, which avoids the slot (0,1)x(1,2) iff vL + lam tan th <= 1 (and lam < cos th keeps T right of u = 1)."""
    uL = 1 - lam
    V = (uL + math.sin(th), vL - math.cos(th))
    return (V[0] + (math.cos(th) - math.sin(th)) / 2, V[1] + (math.sin(th) + math.cos(th)) / 2, th)


def slot_met_search(n=200000, seed=11):
    """two meeters of the open corner box, both avoiding the open wall slot Z = (0,1)x(1,2) (every such tilted meeter is
    a cap square: notes s.2), sampled over the whole parameter range; returns (tested, disjoint pairs found, least
    overlap area, its pair)."""
    rng = random.Random(seed)
    Z = box(0, 1, 1, 2)
    tested = found = 0
    best = None
    for _ in range(n):
        thA, thB = rng.uniform(1e-3, math.pi / 2 - 1e-3), rng.uniform(1e-3, math.pi / 2 - 1e-3)
        lamA = rng.uniform(0, min(math.sin(thA), math.cos(thA)))
        lamB = rng.uniform(0, min(math.sin(thB), math.cos(thB)))
        loA, hiA = math.cos(thA), 1 - lamA * math.tan(thA)
        loB, hiB = math.cos(thB), 1 - lamB * math.tan(thB)
        if hiA <= loA or hiB <= loB:
            continue
        A = _cap_square(thA, lamA, rng.uniform(loA, hiA))
        B = _cap_square(thB, lamB, rng.uniform(loB, hiB))
        if not (L.in_quadrant(A) and L.in_quadrant(B) and L.meets_box(A) and L.meets_box(B)):
            continue
        pa, pb = L.poly(A), L.poly(B)
        assert pa.intersection(Z).area < 1e-9 and pb.intersection(Z).area < 1e-9
        tested += 1
        ov = pa.intersection(pb).area
        if best is None or ov < best[0]:
            best = (ov, A, B)
        if ov <= 1e-12:
            found += 1
    return tested, found, best


# ---------------------------------------------------------------- the wall-grain supply in summary coordinates
def wall_grain_possible(rv_lo_hi_c, rv_lo_hi_c2, S):
    """slot c01 (up c's wall) can have the ADJACENT corner c2's meeter as its second meeter only if c2's crowd reaches
    below S - 2 along that wall: r_wall(c2) > S - 2; and symmetrically for c2's slot.  Both are needed for the mutual
    (wall-grain) supply; returns (c's slot can be served by c2, c2's slot can be served by c)."""
    return (rv_lo_hi_c2[1] > S - 2, rv_lo_hi_c[1] > S - 2)


def wall_slot_leaf(rv_c, rv_c2, S):
    """what the summary decides for the pair of slots on one wall: 'MUTUAL-POSSIBLE' or 'MUTUAL-IMPOSSIBLE'.  Neither
    is a kill: the slot's second meeter may be the corner's other meeter (its tip in the notch) or a free square, and
    the summary does not exclude either (notes/wall_slot243.md s.3)."""
    a, b = wall_grain_possible(rv_c, rv_c2, S)
    return 'MUTUAL-POSSIBLE' if (a and b) else 'MUTUAL-IMPOSSIBLE (UNDECIDED)'


def main():
    P.be_polite()
    S = L.SHAT
    lines = ["# A243 addendum -- Lemma WALL-SLOT, the 12 cells, SLOT-MET's search (generated by `code/wallslot243.py`)", "",
             "## 1. Which squares meet the 12 cells of the window ring at s-hat (theta = 20, delta = sin 20 + 0.02)", "",
             "| cell | meeters | count |", "|---|---|---|"]
    A, B = L.pair_F(20.0, math.sin(20 * L.DEG) + 0.02)
    bodies = ring_polys(A, B, S)
    for name, met in meeters_of_cells(bodies, S):
        lines.append("| %s | %s | %d |" % (name, ", ".join(met) or "-", len(met)))
    lines += ["", "Four of the eight wall slots -- the slot the tilted partner reaches into, at every corner -- are met by exactly",
              "ONE square, that partner: by Lemma WALL-SLOT the ring is not 12-stuck (the slot square swaps in, the corner is",
              "then singly met, K0-FREE settles it into a corner domino at the same side, and (k1-a) kills it in the window).",
              "The other four slots are met by the flat meeter and the adjacent corner's partner (the wall grain).", ""]
    for th in (5.0, 30.0):
        A2, B2 = L.pair_F(th, math.sin(th * L.DEG) + 0.02)
        tab = meeters_of_cells(ring_polys(A2, B2, S), S)
        singly = [nm for nm, m in tab if len(m) <= 1]
        lines.append("- window ring theta = %.0f: cells met by <= 1 square: %s" % (th, ", ".join(singly) or "none"))
    tested, found, best = slot_met_search()
    lines += ["", "## 2. SLOT-MET: two meeters of the corner box both avoiding the slot above it", "",
              "Random search over cap squares (every tilted meeter avoiding the open slot is one, notes s.2): %d pairs tested, "
              "%d interior-disjoint pairs found; least overlap area %.4f at A = (%.3f, %.3f, %.1f deg), B = (%.3f, %.3f, %.1f deg)."
              % (tested, found, best[0], best[1][0], best[1][1], best[1][2] / L.DEG, best[2][0], best[2][1], best[2][2] / L.DEG), "",
              "## 3. The wall-grain supply in the summary", "",
              "| s | r_wall needed of the adjacent crowd (> s - 2) | window crowd's r_v at theta = 20 | verdict for the left wall |", "|---|---|---|---|"]
    rv = L.summary(A, B)[1]
    for s in (3.82, S, 3.95, 3.99):
        lines.append("| %.4f | %.4f | %.4f | %s |" % (s, s - 2, rv, wall_slot_leaf((rv, rv), (rv, rv), s)))
    lines.append("")
    with open(os.path.join(BASE, "results", "wallslot243.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
