"""A113 T3 -- split A99's 9,300-21,700 CPU-h k0_00 projection by distance to the k >= 1 manifold.

Branching model = A85 s.8.3 verbatim as re-parametrised by A99 (results/projection99.json):
  N2 = 1728 = 216 level-1 cells x 8 (bisect x, y and theta once)
  N3 = 8 * N2 * (1 - f2),  N4 = 8 * N3 * (1 - f2),   f2 = 2/3 (A99's measured with-repair rate)
  per-node cost c = 0.47 .. 1.1 CPU-h, window multiplier 1.05 (R3c parametric re-emission),
  + 150 CPU-h for the (D)/(D') side.
The model's f2 and c are UNIFORM over nodes, so the share of cost carried by any set of boxes is
exactly the weighted share of boxes: weight 1 per level-2 box, (1-f2) per level-3 box,
(1-f2)^2 per level-4 box.  We enumerate all 1728 + 13824 + 110592 boxes geometrically and bin
them by eta.  (D)/(D') is 150 CPU-h flat and is reported separately, not split.
"""
import os, sys, json, math, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifold as M                                                        # noqa: E402

F2 = 2.0 / 3.0
C_LO, C_HI = 0.47, 1.1
WINDOW = 1.05
DD = 150.0
ETAS = (0.05, 0.10, 0.20)

L1 = json.load(open(os.path.join(M.ROOT, "attempts/A38-root-power/results/l1_a38.json"),
                    encoding="utf-8"))["matrix"]


def kids(b):
    xm = 0.5 * (b["x0"] + b["x1"])
    ym = 0.5 * (b["y0"] + b["y1"])
    tm = 0.5 * (b["th0"] + b["th1"])
    for xs in ((b["x0"], xm), (xm, b["x1"])):
        for ys in ((b["y0"], ym), (ym, b["y1"])):
            for ts in ((b["th0"], tm), (tm, b["th1"])):
                yield dict(x0=xs[0], x1=xs[1], y0=ys[0], y1=ys[1], th0=ts[0], th1=ts[1])


def walk():
    """yield (level, parent_l1_idx, eta, d_pos, d_tilt, weight) for every level-2..4 box."""
    w3 = 1.0 - F2
    w4 = (1.0 - F2) ** 2
    for r in L1:
        idx = r["idx"]
        for b2 in kids(r["box"]):
            e2 = M.eta_box(b2)
            yield (2, idx, e2[0], e2[1], e2[2], 1.0)
            for b3 in kids(b2):
                e3 = M.eta_box(b3)
                yield (3, idx, e3[0], e3[1], e3[2], w3)
                for b4 in kids(b3):
                    e4 = M.eta_box(b4)
                    yield (4, idx, e4[0], e4[1], e4[2], w4)


def main():
    tot = 0.0
    per_level = {2: 0.0, 3: 0.0, 4: 0.0}
    near_eta = {e: 0.0 for e in ETAS}
    near_pos = {e: 0.0 for e in ETAS}
    near_eta_lvl = {e: {2: 0.0, 3: 0.0, 4: 0.0} for e in ETAS}
    # measured-cost variant: weight each level-1 subtree by that cell's measured level-1 LP wall
    lp = {r["idx"]: (r.get("seconds") or 0.0) for r in L1}
    med = st.median([v for v in lp.values() if v > 0])
    for r in L1:                                  # notrun cells get the median (no measurement)
        if lp[r["idx"]] <= 0:
            lp[r["idx"]] = med
    mtot = 0.0
    mnear = {e: 0.0 for e in ETAS}
    n_boxes = {2: 0, 3: 0, 4: 0}
    for lev, idx, eta, dp, dt, w in walk():
        tot += w
        per_level[lev] += w
        n_boxes[lev] += 1
        mw = w * lp[idx] / med
        mtot += mw
        for e in ETAS:
            if eta <= e:
                near_eta[e] += w
                near_eta_lvl[e][lev] += w
                mnear[e] += mw
            if dp <= e:
                near_pos[e] += w

    lines = []
    a = lines.append
    a("# A113 T3 -- where the k0_00 projection sits relative to the k >= 1 manifold\n")
    a("Model: A85 s.8.3 / A99 projection99 (f2 = 2/3, c = 0.47-1.1 CPU-h/node, window x1.05, "
      "+150 CPU-h for (D)/(D')).  Weighted node total = %.0f (A99's 18,624).\n" % tot)
    a("| level | boxes | model weight | share |")
    a("|---|---|---|---|")
    for lev in (2, 3, 4):
        a("| %d | %d | %.0f | %.1f%% |" % (lev, n_boxes[lev], per_level[lev],
                                           100 * per_level[lev] / tot))
    a("")
    a("## the split (combined eta = max(position, tilt-as-displacement) -- the brief's measure)\n")
    a("| eta | weight within | share of frontier cost | CPU-h within | CPU-h beyond |")
    a("|---|---|---|---|---|")
    for e in ETAS:
        f = near_eta[e] / tot
        lo = tot * C_LO * WINDOW
        hi = tot * C_HI * WINDOW
        a("| %.2f | %.0f | **%.2f%%** | %.0f-%.0f | %.0f-%.0f |" % (
            e, near_eta[e], 100 * f, f * lo, f * hi, (1 - f) * lo + DD, (1 - f) * hi + DD))
    a("")
    a("## the same split on POSITION distance alone (d_pos; the tilt term dropped)\n")
    a("| d_pos | weight within | share of frontier cost |")
    a("|---|---|---|")
    for e in ETAS:
        a("| %.2f | %.0f | %.2f%% |" % (e, near_pos[e], 100 * near_pos[e] / tot))
    a("")
    a("## by level (combined eta)\n")
    a("| eta | level 2 | level 3 | level 4 |")
    a("|---|---|---|---|")
    for e in ETAS:
        a("| %.2f | %.2f%% | %.2f%% | %.2f%% |" % (
            e, 100 * near_eta_lvl[e][2] / per_level[2],
            100 * near_eta_lvl[e][3] / per_level[3],
            100 * near_eta_lvl[e][4] / per_level[4]))
    a("")
    a("## measured-cost variant (each level-1 subtree weighted by its measured level-1 LP wall;\n"
      "the 82 notrun cells carry the median %.0f s)\n" % med)
    a("| eta | share of measured-cost-weighted frontier |")
    a("|---|---|")
    for e in ETAS:
        a("| %.2f | %.2f%% |" % (e, 100 * mnear[e] / mtot))
    a("")
    a("## by PARENT level-1 cell (what a guided tree would actually branch on: the cost that\n"
      "descends from the 216 root cells inside the near-manifold set)\n")
    a("| threshold | level-1 cells within (of 216) | share of projected cost | LP kills there "
      "| kill rate there |")
    a("|---|---|---|---|---|")
    for key, lab in (("eta", "eta(cell)"), ("d_pos", "d_pos(cell)")):
        for e in ETAS:
            sel = []
            for r in L1:
                et, dp, dt, nm = M.eta_box(r["box"])
                if (et if key == "eta" else dp) <= e:
                    sel.append(r)
            pr = [r for r in sel if r.get("tau") is not None]
            kl = [r for r in pr if r["status"] == "dead(T1)"]
            a("| %s <= %.2f | %d | %.1f%% | %d/%d | %s |" % (
                lab, e, len(sel), 100.0 * len(sel) / 216.0, len(kl), len(pr),
                "%.0f%%" % (100.0 * len(kl) / len(pr)) if pr else "-"))
    a("")
    a("Total frontier cost in the model: %.0f-%.0f CPU-h (+%.0f (D)/(D')) = "
      "%.0f-%.0f CPU-h, A99's 9,341-21,661.\n" % (tot * C_LO * WINDOW, tot * C_HI * WINDOW, DD,
                                                  tot * C_LO * WINDOW + DD,
                                                  tot * C_HI * WINDOW + DD))
    txt = "\n".join(lines) + "\n"
    open(os.path.join(M.BASE, "results", "t3_projection.md"), "w", encoding="utf-8").write(txt)
    json.dump(dict(total_weight=tot, per_level=per_level, n_boxes=n_boxes,
                   near_eta={str(k): v for k, v in near_eta.items()},
                   near_pos={str(k): v for k, v in near_pos.items()},
                   share_eta={str(k): near_eta[k] / tot for k in ETAS},
                   share_pos={str(k): near_pos[k] / tot for k in ETAS},
                   share_measured={str(k): mnear[k] / mtot for k in ETAS},
                   f2=F2, c=[C_LO, C_HI], window=WINDOW, dd=DD),
              open(os.path.join(M.BASE, "results", "t3_projection.json"), "w"), indent=1)
    print(txt)


if __name__ == "__main__":
    main()
