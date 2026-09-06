"""A113 T1 -- every k0_00 tree cell on disk, its distance to the k >= 1 manifold, its verdict
and its LP cost.  Pure geometry; READ-ONLY on A38/A85/A99.

Cell sources (all of the k0_00 tree that has ever been solved):
  L1  attempts/A38-root-power/results/l1_a38.json     216 level-1 cells of T(s0) x [0,90)
  L2  attempts/A38-root-power/results/l2_a38.json      80 level-2 children (10 parents)
  L3  attempts/A38-root-power/results/l3_a38.json      24 level-3 children (3 parents)
  A85 attempts/A85-k0-route/results/a85_lp_samples.jsonl + results/nodes/k0_00/*.json
      12 nodes solved with certification-in-the-loop (the PASS/FAIL verdicts)
  A99 attempts/A99-k0-tree-v2/results/r2_screen.jsonl  52 level-1 LP re-screens (20 cells)
"""
import os, sys, json, glob, math, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifold as M                                                        # noqa: E402

BASE = M.BASE
ROOT = M.ROOT
RES = M.RES


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def verdict_l1(r):
    """map A38 level-1 status onto the brief's PASS / logic / FAIL / ALIVE vocabulary."""
    s, kl = r["status"], r.get("kill_label")
    if s == "dead(T1)":
        if kl == "kill(certified)":
            return "PASS"
        if kl == "kill(FAILED-CERT)":
            return "FAIL"
        return "KILL(LP,uncertified)"
    if s == "alive(LP)":
        return "ALIVE"
    return s.upper() if s == "notrun" else "UNDECIDED"


def rows():
    out = []
    # ---------------- A38 level 1 -------------------------------------------------
    d = json.load(open(os.path.join(ROOT, "attempts/A38-root-power/results/l1_a38.json"),
                       encoding="utf-8"))
    for r in d["matrix"]:
        b = r["box"]
        eta, dp, dt, nm = M.eta_box(b)
        out.append(dict(src="A38-l1", level=1, cid="l1_%03d" % r["idx"], box=b,
                        eta=eta, d_pos=dp, d_tilt_deg=dt, slot=nm,
                        verdict=verdict_l1(r), status=r["status"], kill_label=r.get("kill_label"),
                        tau=r.get("tau"), budget=d["budget"],
                        eta_lp=(None if r.get("tau") is None else r["tau"] - d["budget"]),
                        lp_s=r.get("seconds"), cert_s=None,
                        converged=r.get("converged"), maxcov=r.get("maxcov"),
                        dist_centre=r.get("dist_centre")))
    # ---------------- A38 levels 2, 3 ---------------------------------------------
    for tag, f, lev in (("A38-l2", "l2_a38.json", 2), ("A38-l3", "l3_a38.json", 3)):
        d = json.load(open(os.path.join(ROOT, "attempts/A38-root-power/results", f),
                           encoding="utf-8"))
        for r in d["records"]:
            b = r["box"]
            eta, dp, dt, nm = M.eta_box(b)
            v = {"undecided": "UNDECIDED", "notrun": "NOTRUN",
                 "dead(T1)": "KILL(LP,uncertified)", "alive(LP)": "ALIVE"}.get(
                     r.get("status"), str(r.get("status")).upper())
            out.append(dict(src=tag, level=lev, cid=r["cid"], box=b,
                            eta=eta, d_pos=dp, d_tilt_deg=dt, slot=nm,
                            verdict=v, status=r.get("status"), kill_label=None,
                            tau=r.get("tau"), budget=r.get("budget"),
                            eta_lp=(None if r.get("tau") is None
                                    else r["tau"] - r.get("budget", 10)),
                            lp_s=r.get("seconds_lp"), cert_s=r.get("seconds_cert"),
                            converged=r.get("converged"), maxcov=r.get("maxcov"),
                            dist_centre=None))
    # ---------------- A85 solved nodes (verdict = certification-in-the-loop) -------
    samp = jl(os.path.join(ROOT, "attempts/A85-k0-route/results/a85_lp_samples.jsonl"))
    best = {}
    for r in samp:                       # keep the LAST record per tag (the final verdict)
        best[r["tag"]] = r
    for p in sorted(glob.glob(os.path.join(
            ROOT, "attempts/A85-k0-route/results/nodes/k0_00/*.json"))):
        tag = os.path.basename(p)[:-5]
        d = json.load(open(p, encoding="utf-8"))
        cores = d["hyp"]["cores"]
        es = [M.eta_box(c["box"]) for c in cores]
        eta, dp, dt, nm = min(es)
        r = best.get(tag, {})
        v = r.get("verdict", "not-run")
        vv = ("PASS" if v.startswith("PASS") else
              "FAIL" if v.startswith("FAIL") else
              "REFUSED" if v.startswith("refused") else v.upper())
        out.append(dict(src="A85", level=("l1" if "_l1_" in tag else
                                          "l2" if "_l2_" in tag else "cor/multi"),
                        cid=tag, box=cores[0]["box"], n_cores=len(cores),
                        eta=eta, d_pos=dp, d_tilt_deg=dt, slot=nm,
                        eta_per_core=[e[0] for e in es],
                        verdict=vv, status=v, kill_label=None,
                        tau=r.get("tau"), budget=r.get("budget"), eta_lp=r.get("eta"),
                        lp_s=r.get("lp_s"), cert_s=r.get("cert_s"),
                        converged=r.get("converged"), maxcov=r.get("maxcov"),
                        dead=d.get("dead")))
    # ---------------- A99 level-1 LP re-screen ------------------------------------
    for r in jl(os.path.join(ROOT, "attempts/A99-k0-tree-v2/results/r2_screen.jsonl")):
        b = r["box"]
        eta, dp, dt, nm = M.eta_box(b)
        out.append(dict(src="A99-r2", level=1, cid="l1_%03d_%s" % (r["idx"], r["pattern"]),
                        box=b, eta=eta, d_pos=dp, d_tilt_deg=dt, slot=nm,
                        verdict=("ALIVE" if r.get("verdict") == "LP" and not r.get("dead")
                                 else str(r.get("verdict")).upper()),
                        status=r.get("verdict"), kill_label=None,
                        tau=r.get("tau"), budget=r.get("budget"), eta_lp=r.get("eta"),
                        lp_s=r.get("lp_s"), cert_s=None, converged=r.get("converged"),
                        maxcov=r.get("maxcov"), pattern=r.get("pattern"),
                        a38_status=r.get("a38_status"), minmass=r.get("minmass")))
    return out


BINS = [(0.0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 1e9)]


def binlab(e):
    for lo, hi in BINS:
        if lo <= e < hi:
            return "[%.2f,%s)" % (lo, ("inf" if hi > 1e8 else "%.2f" % hi))
    return "?"


def table(rs, title, fh):
    import collections
    print("\n### %s (n = %d)\n" % (title, len(rs)), file=fh)
    vs = sorted(set(r["verdict"] for r in rs))
    print("| eta bin | n | " + " | ".join(vs) + " | median tau-budget | median LP s |", file=fh)
    print("|---|---|" + "---|" * (len(vs) + 2), file=fh)
    for lo, hi in BINS:
        sel = [r for r in rs if lo <= r["eta"] < hi]
        if not sel:
            continue
        c = collections.Counter(r["verdict"] for r in sel)
        el = [r["eta_lp"] for r in sel if r.get("eta_lp") is not None]
        ls = [r["lp_s"] for r in sel if r.get("lp_s")]
        print("| %s | %d | " % (binlab(lo + 1e-12), len(sel))
              + " | ".join(str(c.get(v, 0)) for v in vs)
              + " | %s | %s |" % ("%.3f" % st.median(el) if el else "-",
                                  "%.0f" % st.median(ls) if ls else "-"), file=fh)


def main():
    rs = rows()
    with open(os.path.join(RES, "t1_cells.jsonl"), "w", encoding="utf-8") as f:
        for r in rs:
            f.write(json.dumps(r) + "\n")
    fh = open(os.path.join(BASE, "results", "t1_table.md"), "w", encoding="utf-8")
    print("# A113 T1 -- k0_00 cells vs distance to the k >= 1 manifold\n", file=fh)
    print("eta = max(L-inf position distance to the nearest of the 36 corner-lattice cell "
          "centres, sqrt(2) sin(tilt-gap/2)); tilt gap = distance of the cell's theta interval "
          "to 0 mod 90.\n", file=fh)
    for tag in ("A38-l1", "A38-l2", "A38-l3", "A85", "A99-r2"):
        sel = [r for r in rs if r["src"] == tag]
        if sel:
            table(sel, tag, fh)
    # the level-1 geometry, spelled out
    l1 = [r for r in rs if r["src"] == "A38-l1"]
    print("\n### level-1 geometry\n", file=fh)
    import collections
    c = collections.Counter((round(r["d_pos"], 6), r["d_tilt_deg"]) for r in l1)
    print("| d_pos | d_tilt deg | eta | n cells |", file=fh)
    print("|---|---|---|---|", file=fh)
    for (dp, dt), n in sorted(c.items()):
        print("| %.4f | %.1f | %.4f | %d |" % (dp, dt, max(dp, M.rot_len(dt)), n), file=fh)
    fh.close()
    print(open(os.path.join(BASE, "results", "t1_table.md"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
