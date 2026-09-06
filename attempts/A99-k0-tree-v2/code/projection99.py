"""A99: the stacked projection.  Reads only A99's own measured results and re-prices A85's
interior-first k0_00 tree (docs/proofs/k0_route.md s.8.3) with R1/R2/R3 separately and stacked.

A85's model, kept verbatim so the comparison is like-for-like:
    N2 = 1728 = 216 level-1 cells x b, b = 8 per level
    N3 = 8*N2*(1-f2),  N4 = 8*N3*(1-f3),  f3 = f2
    per-node CPU-h c in [0.47, 1.1]  (0.47 = 1000 s LP + ~690 s certification, first-pass PASS;
                                      1.1  = the same plus two eps_geo repair rounds)
    + 150 CPU-h for the (D)/(D') side
A99 replaces f2 by what R1 measured, c by what R3 measured, multiplies by the branch count R2
forces, and prices the window from R3(c).
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")

N1 = 216
B = 8
DSIDE = 150.0
LP_S = 1000.0          # A85 measured, per depth-2 node
CERT_S_LO, CERT_S_HI = 630.0, 860.0
REPAIR_S_LO, REPAIR_S_HI = 800.0, 1200.0


def nodes(f2, f3=None, levels=3):
    f3 = f2 if f3 is None else f3
    n2 = N1 * B
    n3 = B * n2 * (1 - f2)
    n4 = B * n3 * (1 - f3)
    return dict(N2=n2, N3=n3, N4=n4, total=n2 + n3 + n4)


def cost(lp_s, cert_s, repairs, n):
    return n * (lp_s + cert_s + repairs) / 3600.0


def row(name, f2, lp_s, cert_lo, cert_hi, rep_lo, rep_hi, branches, sides, dside=DSIDE):
    N = nodes(f2)
    lo = cost(lp_s, cert_lo, rep_lo, N["total"]) * branches * sides + dside
    hi = cost(lp_s, cert_hi, rep_hi, N["total"]) * branches * sides + dside
    return dict(scenario=name, f2=f2, nodes=N, lp_s=lp_s,
                cert_s=[cert_lo, cert_hi], repair_s=[rep_lo, rep_hi],
                branches=branches, sides=sides,
                cpu_h=[round(lo), round(hi)],
                desktop_days_3slots=[round(lo / 72, 1), round(hi / 72, 1)],
                desktop_days_1slot=[round(lo / 24), round(hi / 24)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f2-measured", type=float, required=True)
    ap.add_argument("--lp-warm-s", type=float, default=LP_S)
    ap.add_argument("--cert-lo", type=float, default=CERT_S_LO)
    ap.add_argument("--cert-hi", type=float, default=CERT_S_HI)
    ap.add_argument("--branches", type=float, default=1.0)
    ap.add_argument("--window-sides", type=float, default=4.0)
    ap.add_argument("--out", default="projection99.json")
    a = ap.parse_args()

    rows = []
    # A85's two published rows, s0-only and x4 for the window as a 4-side grid
    rows.append(row("A85 baseline, repairs succeed (f2=0.85), s0", 0.85,
                    LP_S, CERT_S_LO, CERT_S_HI, 0.0, 2 * REPAIR_S_HI * 0.15, 1, 1))
    rows.append(row("A85 baseline, first pass only (f2=1/3), s0", 1.0 / 3,
                    LP_S, CERT_S_LO, CERT_S_HI, 0.0, 0.0, 1, 1))
    rows.append(row("A85 baseline f2=0.85, window as 4 fixed sides", 0.85,
                    LP_S, CERT_S_LO, CERT_S_HI, 0.0, 2 * REPAIR_S_HI * 0.15, 1, 4))
    # A99 measured
    rows.append(row("A99 R1 alone (f2 measured), s0", a.f2_measured,
                    LP_S, CERT_S_LO, CERT_S_HI, 0.0, 2 * REPAIR_S_HI * (1 - a.f2_measured), 1, 1))
    rows.append(row("A99 R3 alone (measured per-node cost), s0", 0.85,
                    a.lp_warm_s, a.cert_lo, a.cert_hi, 0.0, 2 * REPAIR_S_HI * 0.15, 1, 1))
    rows.append(row("A99 R2 alone (root shallow/deep branching), s0", 0.85,
                    LP_S, CERT_S_LO, CERT_S_HI, 0.0, 2 * REPAIR_S_HI * 0.15, a.branches, 1))
    rows.append(row("A99 STACKED, s0", a.f2_measured, a.lp_warm_s, a.cert_lo, a.cert_hi,
                    0.0, 2 * REPAIR_S_HI * (1 - a.f2_measured), a.branches, 1))
    rows.append(row("A99 STACKED, window-valid", a.f2_measured, a.lp_warm_s, a.cert_lo,
                    a.cert_hi, 0.0, 2 * REPAIR_S_HI * (1 - a.f2_measured), a.branches,
                    a.window_sides))
    json.dump(rows, open(os.path.join(RES, a.out), "w"), indent=1)
    hdr = f"{'scenario':52s} {'f2':>5s} {'nodes':>8s} {'br':>4s} {'sides':>5s} {'CPU-h':>16s} {'d-days@3':>14s}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['scenario']:52s} {r['f2']:5.2f} {r['nodes']['total']:8.0f} "
              f"{r['branches']:4.1f} {r['sides']:5.1f} "
              f"{r['cpu_h'][0]:7.0f}-{r['cpu_h'][1]:8.0f} "
              f"{r['desktop_days_3slots'][0]:6.1f}-{r['desktop_days_3slots'][1]:7.1f}")


if __name__ == "__main__":
    main()
