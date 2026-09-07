"""A115 T1 -- which corner cell each K01 support leaves empty / singly met, and at what depth the
existing meeters sit.

For every one of the 84 K01 cells (A107 results/shadow_nodes_k0.json) we take

  * the node's SHADOW cfg = hypothesis cores + an integral support component (A107's own object,
    11 placements: the configuration the LP dual support minimises to), and
  * the node's FRACTIONAL dual support (every placement of the LP packing with weight > 0), read
    from the COPY of the campaign json in results/nodes/<nid>.src.json,

and evaluate, at each corner c, mu_c of every placement (corner85.f_min_max in c's frame), the
A90 depth d_c = max(0, 1 - mu_c), the number of meeters of the CLOSED corner cell [0,1]^2 and of
the WIDENED box [0, 1+w]^2 (w = 0.025509, K0-WIDEN), and the fractional crowd weight in each.
"""
import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a115lib as L

W_WIDE = float(L.a_w(0))          # 1.02551 = lambda_max + (lambda_max - 1)/sqrt2  (K0-WIDEN)
OUT = os.path.join(L.RES, "t1_corners.json")
MD = os.path.join(L.RES, "t1_table.md")


def depth_bin(d):
    if d <= 0.0:
        return "0 (touch/none)"
    if d < 0.05:
        return "(0,0.05)"
    if d < 0.10:
        return "[0.05,0.10)"
    if d < 0.155:
        return "[0.10,0.155)"
    if d < 0.30:
        return "[0.155,0.30)"
    return ">=0.30"


def main():
    log = L.logger("t1.log")
    idx = L.extract_index()
    sn = L.shadow_nodes()
    k01 = sn["K01"]
    log("A115 T1: %d K01 cells, a_w(0) = %.6f (widened corner box)" % (len(k01), W_WIDE))

    recs = []
    for ent in k01:
        nid = ent["nid"]
        e = idx[nid]
        src = L.src_copy(nid, e["path"])
        d = json.load(open(src))
        cfg = [tuple(q) for q in e.get("cfg", [])]
        ncore = len(e.get("cores", []))
        frac = [(float(q["cx"]), float(q["cy"]), float(q["theta"]), float(q.get("y", 0.0)))
                for q in d.get("packing", []) if float(q.get("y", 0.0)) > 1e-9]
        cores = [tuple(q) for q in e.get("cores", [])]

        per = {}
        for c in L.CORNERS:
            mu_cfg = sorted(L.mu_corner(x, y, t, c) for (x, y, t) in cfg)
            mu_core = [L.mu_corner(x, y, t, c) for (x, y, t) in cores]
            n_closed = sum(1 for m in mu_cfg if m <= 1.0 + 1e-12)
            n_open = sum(1 for m in mu_cfg if m < 1.0 - 1e-12)
            n_wide = sum(1 for m in mu_cfg if m <= W_WIDE + 1e-12)
            wt_closed = sum(w for (x, y, t, w) in frac
                            if L.mu_corner(x, y, t, c) <= 1.0 + 1e-12)
            wt_wide = sum(w for (x, y, t, w) in frac
                          if L.mu_corner(x, y, t, c) <= W_WIDE + 1e-12)
            per[c] = dict(mu_sorted=[round(m, 6) for m in mu_cfg[:4]],
                          depths=[round(max(0.0, 1.0 - m), 6) for m in mu_cfg[:4]],
                          n_closed=n_closed, n_open=n_open, n_wide=n_wide,
                          core_min_mu=round(min(mu_core), 6) if mu_core else None,
                          frac_wt_closed=round(wt_closed, 6), frac_wt_wide=round(wt_wide, 6))
        rec = dict(nid=nid, src=e["src"], shard=e["shard"], level=e["level"],
                   budget=e["budget"], tau=e["tau"], at_budget=e["at_budget"],
                   converged=e.get("converged"), via=e.get("via"), ncore=ncore,
                   n_frac=len(frac), frac_total=round(sum(w for *_, w in frac), 6),
                   corners=per,
                   room_closed=[c for c in L.CORNERS if per[c]["n_closed"] <= 1],
                   room_wide=[c for c in L.CORNERS if per[c]["n_wide"] <= 1],
                   frac_wt_all_wide=round(sum(w for (x, y, t, w) in frac
                                              if min(L.mu_corner(x, y, t, cc) for cc in L.CORNERS)
                                              <= W_WIDE + 1e-12), 6))
        recs.append(rec)
        log("  %-24s lvl%d bud%2d tau=%.4f room(closed)=%s room(wide)=%s crowdwt=%.3f/%.3f"
            % (nid, rec["level"], rec["budget"], rec["tau"], ",".join(rec["room_closed"]) or "-",
               ",".join(rec["room_wide"]) or "-", rec["frac_wt_all_wide"], rec["frac_total"]))

    json.dump(dict(a_w_wide=W_WIDE, n=len(recs), recs=recs), open(OUT, "w"), indent=1)

    # ---------------- tables
    lines = []
    lines.append("# A115 T1 -- the K01 room: which corner cell the support leaves empty or singly met\n")
    lines.append("`closed` = meets [0,1]^2 (mu_c <= 1, the s0 convention); `wide` = meets the "
                 "K0-WIDEN box [0, %.6f]^2.  84 K01 cells.\n" % W_WIDE)

    cnt_closed = collections.Counter()
    cnt_wide = collections.Counter()
    occ = collections.Counter()
    for r in recs:
        for c in L.CORNERS:
            occ[(c, r["corners"][c]["n_closed"])] += 1
        cnt_closed[tuple(r["room_closed"])] += 1
        cnt_wide[tuple(r["room_wide"])] += 1

    lines.append("## corner-cell occupancy of the shadow (11 placements), by corner\n")
    lines.append("| corner | 0 meeters | 1 meeter | 2 meeters | >=3 |")
    lines.append("|---|---|---|---|---|")
    for c in L.CORNERS:
        lines.append("| %s | %d | %d | %d | %d |"
                     % (c, occ[(c, 0)], occ[(c, 1)], occ[(c, 2)],
                        sum(v for (cc, k), v in occ.items() if cc == c and k >= 3)))
    lines.append("")

    lines.append("## which corners are 'room' (met by <= 1), as a set\n")
    lines.append("| room set (closed) | cells | room set (widened) | cells |")
    lines.append("|---|---|---|---|")
    a = cnt_closed.most_common()
    b = cnt_wide.most_common()
    for i in range(max(len(a), len(b))):
        la = "%s | %d" % ("+".join(a[i][0]) or "(none)", a[i][1]) if i < len(a) else " | "
        lb = "%s | %d" % ("+".join(b[i][0]) or "(none)", b[i][1]) if i < len(b) else " | "
        lines.append("| %s | %s |" % (la, lb))
    lines.append("")

    lines.append("## depth of the meeters that ARE there, by corner (shadow placements with mu_c <= 1)\n")
    bins = ["0 (touch/none)", "(0,0.05)", "[0.05,0.10)", "[0.10,0.155)", "[0.155,0.30)", ">=0.30"]
    tab = collections.Counter()
    for r in recs:
        for c in L.CORNERS:
            for m in r["corners"][c]["mu_sorted"]:
                if m <= 1.0 + 1e-12:
                    tab[(c, depth_bin(max(0.0, 1.0 - m)))] += 1
    lines.append("| corner | " + " | ".join(bins) + " | total |")
    lines.append("|---|" + "---|" * (len(bins) + 1))
    for c in L.CORNERS:
        row = [tab[(c, bn)] for bn in bins]
        lines.append("| %s | %s | %d |" % (c, " | ".join(str(v) for v in row), sum(row)))
    lines.append("")

    lines.append("## the SECOND meeter's depth d2 (the quantity Lemma CW conditions on), by corner\n")
    lines.append("| corner | no 2nd meeter | d2 = 0 | d2 in (0,.05) | [.05,.10) | [.10,.155) | [.155,.30) | >= .30 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in L.CORNERS:
        none2 = 0
        cc = collections.Counter()
        for r in recs:
            mus = [m for m in r["corners"][c]["mu_sorted"] if m <= 1.0 + 1e-12]
            if len(mus) < 2:
                none2 += 1
            else:
                cc[depth_bin(max(0.0, 1.0 - mus[1]))] += 1
        lines.append("| %s | %d | %s |" % (c, none2, " | ".join(str(cc[bn]) for bn in bins)))
    lines.append("")

    lines.append("## fractional crowd weight of the LP dual support (what the rows charge)\n")
    lines.append("| level | cells | mean budget | mean total LP weight | mean weight in U_c F_c(widened) | mean weight per corner |")
    lines.append("|---|---|---|---|---|---|")
    bylvl = collections.defaultdict(list)
    for r in recs:
        bylvl[r["level"]].append(r)
    for lv in sorted(bylvl):
        g = bylvl[lv]
        lines.append("| %d | %d | %.2f | %.3f | %.3f | %s |"
                     % (lv, len(g), sum(x["budget"] for x in g) / len(g),
                        sum(x["frac_total"] for x in g) / len(g),
                        sum(x["frac_wt_all_wide"] for x in g) / len(g),
                        " / ".join("%s %.2f" % (c, sum(x["corners"][c]["frac_wt_wide"] for x in g) / len(g))
                                   for c in L.CORNERS)))
    lines.append("")
    open(MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    log("wrote %s and %s" % (OUT, MD))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
