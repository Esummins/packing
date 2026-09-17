"""A242 -- the run report and the PRICE, benchmarked from the cells actually decided.

    python report242.py [--bands W,B3] [--bench 50] > ../results/crowd242.md

THE PRICE MODEL (stated before it is used; `notes/crowd242.md` s.5).
The cascade's leaves need CORES, and A172's K'(role) is empty until the role box is small: A60's
working scale is a centre box of width 0.15 and a sigma-closed tilt cell of ~90/7 deg.  From the
root box (width Wc = 1 + w + sqrt2/2 - 1/2, tilt 90 deg) that is
    d_role = 2*ceil(log2(Wc/0.15)) + ceil(log2(90/12.86))  binary splits per role,
    D = 8 * d_role  splits to a cell every one of whose roles is at working scale,
so 2^D cells before the pruning.  The measured pruning is the EMPTYBOX rate per level; the
census-based figure A85 s.4.4 measured independently is N_pair ~ 3.4e4 surviving core-disjoint
pairs per corner at exactly that scale, giving N_pair^4 four-corner cells (/8 with the D4 quotient
A242 does not take).  The report prints both, and the CPU-h price is the measured mean seconds per
cell times the cell count.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import root242 as R                                                # noqa: E402

N_PAIR = 3.4e4                                                     # A85 s.4.4 [M], per corner


def rows_of(band):
    f = os.path.join(BASE, "results", "crowd242_%s.jsonl" % band)
    if not os.path.exists(f):
        return []
    return [json.loads(x) for x in open(f, encoding="utf-8") if x.strip()]


def price(band, rows, bench):
    tag, lo, hi = [b for b in R.BANDS if b[0] == band][0]
    c = R.root_cell(band)
    Wc = c["roles"]["BLA"][1] - c["roles"]["BLA"][0]
    d_role = 2 * math.ceil(math.log2(Wc / 0.15)) + math.ceil(math.log2(90.0 / (90.0 / 7)))
    D = 8 * d_role
    first = [r for r in rows if r.get("verdict") in ("DEAD", "UNDECIDED")][:bench]
    secs = [r.get("t") or 0.0 for r in first]
    mean = sum(secs) / max(1, len(secs))
    dead = [r for r in first if r["verdict"] == "DEAD"]
    by_clip = {}
    for r in first:
        if r["verdict"] == "DEAD":
            by_clip[r.get("clip") or "?"] = by_clip.get(r.get("clip") or "?", 0) + 1
    deep = max([r["depth"] for r in rows] or [0])
    tail = [r.get("t") or 0.0 for r in rows[-10:]]
    return dict(band=band, m_lo=lo, m_hi=hi, root_width=round(Wc, 4), d_role=d_role, D=D,
                cells_naive=2.0 ** D, cells_census=N_PAIR ** 4, cells_census_d4=N_PAIR ** 4 / 8,
                n=len(rows), bench=len(first), mean_s=round(mean, 2),
                tail_mean_s=round(sum(tail) / max(1, len(tail)), 2),
                dead=len(dead), dead_by_clip=by_clip, max_depth=deep,
                cpu_h_census=N_PAIR ** 4 / 8 * mean / 3600.0,
                cpu_h_so_far=sum(r.get("t") or 0.0 for r in rows) / 3600.0)


def capacity(r):
    """The pocket CAPACITY L1 established for the cell (the PI's addendum, 15:40): an UPPER bound on the
    number of free unit squares the cell can hold.  0 = no free square at all (A221 POCKET-DEAD);
    `cn_bound` = A209's Lemma CN group count on the pockets that survive; None = undecided (>= 3)."""
    if r.get("verdict") != "DEAD":
        return r.get("cn_bound")
    clip = r.get("clip") or ""
    if clip in ("NOROOM", "NOROOM-POCKET"):
        return 0
    if clip == "NOROOM-CN":
        return r.get("cn_bound")
    return "n/a"                                                   # EMPTYBOX: the hypothesis is unsatisfiable


def corner_frame(role, box, S):
    """The role box in ITS CORNER's frame: (u-range, v-range, tilt range), u/v = the centre's distance
    from the corner's two walls.  u = v = 1/2 is a square flush in the corner; u, v -> 1.73 is the
    deep / corner-wasting end of the reach set."""
    c = role[:2]
    x0, x1, y0, y1, t0, t1 = box
    u = (x0, x1) if c in ("BL", "TL") else (S - x1, S - x0)
    v = (y0, y1) if c in ("BL", "BR") else (S - y1, S - y0)
    return u, v, (t0, t1)


def survivors(band, rows, S, n=6):
    alive = sorted([r for r in rows if r.get("verdict") == "UNDECIDED"], key=lambda r: -r["depth"])[:n]
    print("\n### band %s -- the deepest surviving cells: capacity and the meeters' poses\n" % band)
    print("| cell | depth | capacity | pockets alive | L2 gate | corner | A: u, v, tilt | B: u, v, tilt |")
    print("|---|---|---|---|---|---|---|---|")
    for r in alive:
        cap = capacity(r)
        g = (r.get("l2_gate") or {}).get("worst_gap")
        first = True
        for c in ("BL", "BR", "TR", "TL"):
            fa = corner_frame(c + "A", r["roles"][c + "A"], S)
            fb = corner_frame(c + "B", r["roles"][c + "B"], S)
            f = lambda q: "[%.2f,%.2f] [%.2f,%.2f] %.0f-%.0f" % (q[0][0], q[0][1], q[1][0], q[1][1], q[2][0], q[2][1])
            print("| %s | %s | %s | %s | %s | %s | %s | %s |"
                  % (r["label"][-26:] if first else "", r["depth"] if first else "",
                     ("%s" % cap if cap is not None else ">= 3 (undecided)") if first else "",
                     r.get("n_alive") if first else "", g if first else "", c, f(fa), f(fb)))
            first = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bands", default="W,B3")
    ap.add_argument("--bench", type=int, default=50)
    a = ap.parse_args()
    print("# A242 -- the k0 cascade from the crowd root H_B: what the leaves killed and what it costs\n")
    print("Generated by `code/report242.py`; the cells are `results/crowd242_<band>.jsonl`, the live DFS")
    print("stacks `results/stack242_<band>.json`.  Every DEAD row is a certificate for its cell's")
    print("hypothesis; every UNDECIDED row is an open obligation.  L1 uses no LOCKED hypothesis, so a")
    print("DEAD row kills every K0-BLOCKED packing of that cell, locked or not.\n")
    print("| band | sides | cells | DEAD | by clip | max depth | mean s/cell (first %d) | last-10 mean | CPU-h so far |" % a.bench)
    print("|---|---|---|---|---|---|---|---|---|")
    ps = []
    for b in a.bands.split(","):
        rows = rows_of(b)
        if not rows:
            continue
        p = price(b, rows, a.bench)
        ps.append(p)
        print("| %s | [%.4f, %.4f] | %d | %d | %s | %d | %.1f | %.1f | %.3f |"
              % (b, p["m_lo"], p["m_hi"], p["n"], p["dead"],
                 ", ".join("%s %d" % kv for kv in sorted(p["dead_by_clip"].items())) or "-",
                 p["max_depth"], p["mean_s"], p["tail_mean_s"], p["cpu_h_so_far"]))
    print("\n## The price to completion\n")
    print("| band | role box width | splits/role to A60 scale | splits total D | 2^D | A85 census N_pair^4/8 | CPU-h at the measured rate |")
    print("|---|---|---|---|---|---|---|")
    for p in ps:
        print("| %s | %.4f | %d | %d | %.2e | %.2e | %.2e |"
              % (p["band"], p["root_width"], p["d_role"], p["D"], p["cells_naive"],
                 p["cells_census_d4"], p["cpu_h_census"]))
    for b in a.bands.split(","):
        rows = rows_of(b)
        if rows:
            survivors(b, rows, [x for x in R.BANDS if x[0] == b][0][2])
    print("\nThe two cell counts are independent: `2^D` is this cascade's own tree, `N_pair^4/8` is A85")
    print("s.4.4's MEASURED corner-pair census at the same box scale (with the D4 quotient A242 does not")
    print("take).  They agree to within an order of magnitude on the exponent, and both say the same")
    print("thing: the cascade from H_B is a PRODUCT over four corners and is not affordable.\n")
    for p in ps:
        print("- band %s: %d cells decided, %d DEAD (%s), deepest %d, %.3f CPU-h spent."
              % (p["band"], p["n"], p["dead"],
                 ", ".join("%s %d" % kv for kv in sorted(p["dead_by_clip"].items())) or "no kills",
                 p["max_depth"], p["cpu_h_so_far"]))


if __name__ == "__main__":
    main()
