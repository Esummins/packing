"""A113 T1 part 2 -- rates (not counts) of verdict against eta, and the tau/eta relation,
plus the interior-first-order confound check."""
import os, sys, json, math, statistics as st, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifold as M                                                        # noqa: E402

rs = [json.loads(l) for l in open(os.path.join(M.RES, "t1_cells.jsonl"), encoding="utf-8")]
L1 = [r for r in rs if r["src"] == "A38-l1"]
BUD = 10.0


def spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            for k in range(i, j + 1):
                r[s[k]] = (i + j) / 2.0
            i = j + 1
        return r
    a, b = rank(xs), rank(ys)
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((x - mb) ** 2 for x in b))
    return num / (da * db) if da and db else float("nan")


out = []
w = out.append
w("# A113 T1 -- verdict RATES and LP resistance vs eta (level-1, the 216-cell root)\n")

BINS = [(0.0, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 0.40), (0.40, 9e9)]
w("| eta bin | cells | processed | LP kills | kill rate | ALIVE(LP) | tau >= budget "
  "| median tau | max tau | median LP s |")
w("|---|---|---|---|---|---|---|---|---|---|")
for lo, hi in BINS:
    sel = [r for r in L1 if lo <= r["eta"] < hi]
    if not sel:
        continue
    pr = [r for r in sel if r["tau"] is not None]
    kl = [r for r in pr if r["status"] == "dead(T1)"]
    al = [r for r in pr if r["status"] == "alive(LP)"]
    ge = [r for r in pr if r["tau"] >= BUD - 1e-9]
    taus = [r["tau"] for r in pr]
    w("| [%.2f,%s) | %d | %d | %d | %s | %d | %d | %s | %s | %s |" % (
        lo, ("inf" if hi > 1e8 else "%.2f" % hi), len(sel), len(pr), len(kl),
        ("%.0f%%" % (100.0 * len(kl) / len(pr))) if pr else "-", len(al), len(ge),
        "%.3f" % st.median(taus) if taus else "-", "%.3f" % max(taus) if taus else "-",
        "%.0f" % st.median([r["lp_s"] for r in pr]) if pr else "-"))

w("")
w("## the same, binned on POSITION distance alone (d_pos) -- the term that actually predicts\n")
w("| d_pos bin | cells | processed | LP kills | kill rate | ALIVE(LP) | tau >= budget "
  "| median tau |")
w("|---|---|---|---|---|---|---|---|")
for lo, hi in BINS:
    sel = [r for r in L1 if lo <= r["d_pos"] < hi]
    if not sel:
        continue
    pr = [r for r in sel if r["tau"] is not None]
    kl = [r for r in pr if r["status"] == "dead(T1)"]
    al = [r for r in pr if r["status"] == "alive(LP)"]
    ge = [r for r in pr if r["tau"] >= BUD - 1e-9]
    w("| [%.2f,%s) | %d | %d | %d | %s | %d | %d | %s |" % (
        lo, ("inf" if hi > 1e8 else "%.2f" % hi), len(sel), len(pr), len(kl),
        ("%.0f%%" % (100.0 * len(kl) / len(pr))) if pr else "-", len(al), len(ge),
        "%.3f" % st.median([r["tau"] for r in pr]) if pr else "-"))

w("")
w("## every level-1 cell whose LP is at or above budget (un-killable at the measured LP state)\n")
w("| cell | eta | d_pos | d_tilt deg | nearest slot | status | tau | LP s | dist_centre |")
w("|---|---|---|---|---|---|---|---|---|")
for r in sorted([r for r in L1 if r["tau"] is not None and r["tau"] >= BUD - 1e-9],
                key=lambda r: -r["tau"]):
    w("| %s | %.4f | %.4f | %.1f | %s | %s | %.6f | %.0f | %.3f |" % (
        r["cid"], r["eta"], r["d_pos"], r["d_tilt_deg"], r["slot"], r["status"],
        r["tau"], r["lp_s"], r["dist_centre"]))

w("")
w("## rank correlations over the 134 processed level-1 cells\n")
pr = [r for r in L1 if r["tau"] is not None]
w("| pair | Spearman rho | n |")
w("|---|---|---|")
for nm, xs, ys in (
        ("eta  vs tau", [r["eta"] for r in pr], [r["tau"] for r in pr]),
        ("d_pos vs tau", [r["d_pos"] for r in pr], [r["tau"] for r in pr]),
        ("d_tilt vs tau", [r["d_tilt_deg"] for r in pr], [r["tau"] for r in pr]),
        ("dist_centre vs tau", [r["dist_centre"] for r in pr], [r["tau"] for r in pr]),
        ("eta vs dist_centre", [r["eta"] for r in pr], [r["dist_centre"] for r in pr]),
        ("eta vs LP seconds", [r["eta"] for r in pr], [r["lp_s"] for r in pr]),
        ("tau vs LP seconds", [r["tau"] for r in pr], [r["lp_s"] for r in pr]),
):
    w("| %s | %+.3f | %d |" % (nm, spearman(xs, ys), len(xs)))

# the confound: eta is (mostly) tilt, dist_centre is position.  Split by tilt bin.
w("")
w("## eta vs tau inside each tilt bin (removes the tilt term; pure position effect)\n")
w("| d_tilt deg | cells | processed | kill rate | Spearman(d_pos, tau) | median tau |")
w("|---|---|---|---|---|---|")
for dt in (0.0, 15.0, 30.0):
    sel = [r for r in L1 if abs(r["d_tilt_deg"] - dt) < 1e-9]
    p = [r for r in sel if r["tau"] is not None]
    k = [r for r in p if r["status"] == "dead(T1)"]
    w("| %.0f | %d | %d | %s | %+.3f | %.3f |" % (
        dt, len(sel), len(p), "%.0f%%" % (100.0 * len(k) / len(p)) if p else "-",
        spearman([r["d_pos"] for r in p], [r["tau"] for r in p]) if len(p) > 2 else float("nan"),
        st.median([r["tau"] for r in p]) if p else float("nan")))

w("")
w("## the three Trump-image cells (A38 census_l1survivors canary) in eta\n")
C = json.load(open(os.path.join(M.ROOT,
              "attempts/A38-root-power/results/census_l1survivors.json"), encoding="utf-8"))
byid = {r["cid"]: r for r in L1}
w("| cell | Trump placement tilt deg | eta | d_pos | d_tilt deg | status | tau |")
w("|---|---|---|---|---|---|---|")
for c in C["canary"]["cells"]:
    r = byid["l1_%03d" % c["idx"]]
    th = c["hits"][0]["xytheta"][2]
    w("| %s | %.2f | %.4f | %.4f | %.1f | %s | %s |" % (
        r["cid"], th, r["eta"], r["d_pos"], r["d_tilt_deg"], r["status"],
        "%.6f" % r["tau"] if r["tau"] else "-"))
# and the pose-level eta of the conditioned placement itself
w("")
w("| cell | conditioned Trump placement (x,y,theta) | eta of that POSE |")
w("|---|---|---|")
for c in C["canary"]["cells"]:
    x, y, t = c["hits"][0]["xytheta"]
    w("| l1_%03d | (%.4f, %.4f, %.2f) | %.4f |" % (c["idx"], x, y, t, M.eta_point(x, y, t)[0]))

txt = "\n".join(out) + "\n"
open(os.path.join(M.BASE, "results", "t1_summary.md"), "w", encoding="utf-8").write(txt)
print(txt)
