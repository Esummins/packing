"""
A58 clear-corner composition -- exact combinatorial layer + Trump canary.

Everything exact (Fractions) except the Trump square/box intersection tests, which are
float SAT with printed margins (Trump coordinates from A03's float file; the certified
60-digit values agree to 1e-15, margins reported are >> 1e-12).

Outputs results/occupancy_matrix.json and prints a PI-readable table:
  (1) CC-1 layer: which exact slot values lie in the A21 corner zone [49/100, 11/10];
      corner-root-box separation vs unit-square diameter; the simple-clip census
      (which slot squares meet which corner-root boxes / completable-slot boxes).
  (2) For every open Young class with k <= 4: occupied corners, clear corners,
      completable slots, and for each completable slot p the class label + cert status
      of S + {p} (the CC-3 matrix), plus whether any slot square of S already meets
      int(B_p) (the R1 simple-clip branch) or overlaps the placement (blocked).
  (3) Trump canary: which Trump squares meet each completable-slot box of trump5,
      with margins; the TL-root box is the decisive row.
"""
import json, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, os.path.join(ATT, "A55-k4-sweep", "code"))
from skeletons import d4_images, canon, TRUMP, S0

HALF = Fr(1, 2)
VALS_L = [HALF, Fr(3, 2), Fr(5, 2)]
VALS_R = [S0 - v for v in VALS_L]
CORNERS = ["BL", "BR", "TR", "TL"]  # (xfam,yfam): BL=(L,L) BR=(R,L) TR=(R,R) TL=(L,R)


def fam(v):
    if v in VALS_L:
        return "L", VALS_L.index(v)
    if v in VALS_R:
        return "R", VALS_R.index(v)
    raise ValueError(v)


def corner_of(slot):
    (fx, i), (fy, j) = fam(slot[0]), fam(slot[1])
    c = {("L", "L"): "BL", ("R", "L"): "BR", ("R", "R"): "TR", ("L", "R"): "TL"}[(fx, fy)]
    return c, (i, j)


def slot_of_cell(c, cell):
    i, j = cell
    x = VALS_L[i] if c in ("BL", "TL") else VALS_R[i]
    y = VALS_L[j] if c in ("BL", "BR") else VALS_R[j]
    return (x, y)


def box_of_slot(slot):
    return (slot[0] - HALF, slot[0] + HALF, slot[1] - HALF, slot[1] + HALF)


def int_overlap(b1, b2):
    """exact: interiors of two axis boxes intersect"""
    return b1[0] < b2[1] and b2[0] < b1[1] and b1[2] < b2[3] and b2[2] < b1[3]


def diagrams(S):
    D = {c: set() for c in CORNERS}
    for slot in S:
        c, cell = corner_of(slot)
        D[c].add(cell)
    return D


def completable(D):
    """Young-ready cells (i,j) per corner, i,j <= 2"""
    out = []
    for c in CORNERS:
        have = D[c]
        for i in range(3):
            for j in range(3):
                if (i, j) in have:
                    continue
                if i > 0 and (i - 1, j) not in have:
                    continue
                if j > 0 and (i, j - 1) not in have:
                    continue
                out.append((c, (i, j)))
    return out


def load_classes():
    d = json.load(open(os.path.join(ATT, "A53-simple-strata", "results",
                                    "skeletons_young.json")))
    by_k = {}
    for cl in d["classes"]:
        S = frozenset((Fr(a), Fr(b)) for a, b in cl["slots"])
        by_k.setdefault(cl["k"], []).append(S)
    trump_c = canon(frozenset(TRUMP))

    def label_of(k, j):
        if k != 5:
            return "k%d_%02d" % (k, j)
        if canon(by_k[5][j]) == trump_c:
            return "trump5"
        return "k5_%02d" % sum(1 for jj in range(j) if canon(by_k[5][jj]) != trump_c)

    canon2label = {}
    for k in sorted(by_k):
        for j, S in enumerate(by_k[k]):
            canon2label[canon(S)] = label_of(k, j)
    return by_k, canon2label, label_of


def main():
    by_k, canon2label, label_of = load_classes()
    cap = json.load(open(os.path.join(ATT, "A55-k4-sweep", "results", "cap.json")))
    status = cap["classes"]

    print("== (1) CC-1 exact layer ==")
    zone_lo, zone_hi = Fr(49, 100), Fr(11, 10)
    inzone = [str(v) for v in VALS_L + VALS_R if zone_lo <= v <= zone_hi]
    print("slot values:", [str(v) for v in VALS_L + VALS_R])
    print("slot values in A21 corner-zone interval [49/100, 11/10]:", inzone)
    sep = S0 - 2  # gap between corner root boxes along an axis
    print("corner-root box axis gap s0-2 = %s = %.6f;  (s0-2)^2 - 2 = %s > 0: %s"
          % (sep, float(sep), (sep * sep - 2), sep * sep > 2))
    print("adjacent-arm clip width 4 - s0 =", 4 - S0, "=", float(4 - S0))

    # simple-clip census: which of the 36 slot squares meet which corner-root boxes
    print("\nslot squares whose interior meets a corner-root box int(B_c):")
    roots = {c: box_of_slot(slot_of_cell(c, (0, 0))) for c in CORNERS}
    for fx in ("L", "R"):
        for fy in ("L", "R"):
            for i in range(3):
                for j in range(3):
                    x = VALS_L[i] if fx == "L" else VALS_R[i]
                    y = VALS_L[j] if fy == "L" else VALS_R[j]
                    b = box_of_slot((x, y))
                    for c in CORNERS:
                        oc, cell = corner_of((x, y))
                        if oc == c and cell == (0, 0):
                            continue  # the root square itself
                        if int_overlap(b, roots[c]):
                            print("  slot (%s,%s) [corner %s cell %s] clips root box of %s"
                                  % (x, y, oc, cell, c))

    # (2) occupancy matrix for open classes k <= 4
    print("\n== (2) occupancy matrix, open classes k <= 4 ==")
    matrix = {}
    for k in range(0, 5):
        for j, S in enumerate(by_k[k]):
            lb = label_of(k, j)
            st = status.get(lb, {}).get("status", "?")
            if st != "OPEN":
                continue
            D = diagrams(S)
            occ = [c for c in CORNERS if D[c]]
            clear = [c for c in CORNERS if not D[c]]
            rows = []
            for (c, cell) in completable(D):
                p = slot_of_cell(c, cell)
                Bp = box_of_slot(p)
                clip = [s_ for s_ in S if int_overlap(box_of_slot(s_), Bp)]
                Sp = frozenset(S) | {p}
                lb2 = canon2label.get(canon(Sp))
                st2 = status.get(lb2, {}).get("status", "?") if lb2 else "NOT-A-CLASS"
                wit = status.get(lb2, {}).get("witness", "") if lb2 else ""
                rows.append(dict(corner=c, cell=list(cell),
                                 slot=[str(p[0]), str(p[1])],
                                 is_corner_root=(cell == (0, 0)),
                                 simple_clips=[[str(a), str(b)] for a, b in clip],
                                 super_class=lb2, super_status=st2,
                                 super_witness=wit))
            matrix[lb] = dict(k=k, occupied_corners=occ, clear_corners=clear,
                              slots=[[str(a), str(b)] for a, b in sorted(S)],
                              completable=rows)
            print("%-6s k=%d occ=%s clear=%s" % (lb, k, occ, clear))
            for r in rows:
                tag = "ROOT" if r["is_corner_root"] else "    "
                clipnote = (" SIMPLE-CLIP:" + str(r["simple_clips"])
                            if r["simple_clips"] else "")
                print("   %s %s%s -> %s [%s%s]%s"
                      % (tag, r["corner"], tuple(r["cell"]), r["super_class"],
                         r["super_status"],
                         (" wit=" + r["super_witness"]) if r["super_witness"] else "",
                         clipnote))

    # (3) Trump canary
    print("\n== (3) Trump canary: meeters of trump5's completable-slot boxes ==")
    tf = json.load(open(os.path.join(ATT, "A03-upper-reconstruct", "trump11_float.json")))
    sT, X = tf["s"], tf["X"]
    import math

    def square_poly(cx, cy, th):
        c, s = math.cos(th), math.sin(th)
        h = 0.5
        return [(cx + c * dx - s * dy, cy + s * dx + c * dy)
                for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h))]

    def sat_margin(poly, box):
        """positive => interiors intersect; = min over separating axes of overlap depth"""
        x0, x1, y0, y1 = box
        bx = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        axes = [(1, 0), (0, 1)]
        for i in range(4):
            (ax, ay), (bx_, by_) = poly[i], poly[(i + 1) % 4]
            ex, ey = bx_ - ax, by_ - ay
            n = math.hypot(ex, ey)
            axes.append((-ey / n, ex / n))
        m = 1e18
        for (ux, uy) in axes:
            p1 = [ux * x + uy * y for (x, y) in poly]
            p2 = [ux * x + uy * y for (x, y) in bx]
            ov = min(max(p1), max(p2)) - max(min(p1), min(p2))
            m = min(m, ov)
        return m

    # trump5 skeleton in the sT frame (same combinatorics)
    trumpS = frozenset(TRUMP)
    D = diagrams(trumpS)
    can = {}
    for (c, cell) in completable(D):
        # slot in the sT frame
        i, j = cell
        x = (VALS_L[i] if c in ("BL", "TL") else None)
        x = float(x) if x is not None else sT - float(VALS_L[i])
        y = (VALS_L[j] if c in ("BL", "BR") else None)
        y = float(y) if y is not None else sT - float(VALS_L[j])
        box = (x - 0.5, x + 0.5, y - 0.5, y + 0.5)
        meet = []
        for idx, (cx, cy, th) in enumerate(X):
            mg = sat_margin(square_poly(cx, cy, th), box)
            if mg > 1e-9:
                meet.append((idx, round(cx, 6), round(cy, 6),
                             round(math.degrees(th), 4), round(mg, 6)))
        # nearly-meeting (margin in (-0.05, 1e-9]) for context
        near = []
        for idx, (cx, cy, th) in enumerate(X):
            mg = sat_margin(square_poly(cx, cy, th), box)
            if -0.05 < mg <= 1e-9:
                near.append((idx, round(mg, 6)))
        can[(c, cell)] = dict(box=[round(v, 6) for v in box], meeters=meet, near=near)
        print(" %s %s box=%s  meeters=%d" % (c, cell, [round(v, 3) for v in box],
                                             len(meet)))
        for m in meet:
            print("    sq%-2d c=(%.4f,%.4f) th=%.3f deg  margin=+%.6f"
                  % (m[0], m[1], m[2], m[3], m[4]))
        for n in near:
            print("    near-miss sq%-2d margin=%.6f" % (n[0], n[1]))

    out = dict(s0=str(S0), zone_slot_values=inzone,
               corner_gap=str(sep), clip_width=str(4 - S0),
               matrix=matrix,
               trump_canary={("%s_%d%d" % (c, cell[0], cell[1])): v
                             for (c, cell), v in can.items()})
    with open(os.path.join(BASE, "results", "occupancy_matrix.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\n-> results/occupancy_matrix.json")


if __name__ == "__main__":
    main()
