"""A125 -- certify neighbourhoods N of A122's S33 minimum (and S38 as a second data point).

L = the FULL load-bearing set in the class frame (every non-pin square of the minimum: all eleven
squares carry force at S33min, A122 rigidity.json, no rattler), P = the class pins in A57's
delta-cores.  The tree is A119's `RecTree` (one interval census per tilt cell, shared by every
leaf that meets it; the parent's Farkas vector inherited into each child).

Grid: (r, rho) in {0.05, 0.1, 0.2} x {5, 10, 20 deg}, LARGEST FIRST.  No Trump cut is applied
unless `--cut` is given: the census reports whether any D4 image of Trump satisfies N's
hypothesis (A122: at S33min the keystone f0 is upright while Trump's is at 40.18 deg, so f0's box
excludes Trump on position alone out to r = 0.2054).

Every DEAD verdict is followed by
  * SAMPLING: uniform poses in N, drawn -> tested (the free block is pairwise disjoint, so the
    sample is carried to 30 sides in [s_lo, s0]) -> hits; drawing continues until at least
    `--tested` samples have been TESTED,
  * the SLSQP measured minimum over N (an upper bound on the true minimum), and
  * the Trump canary.

Appends to results/grid_<tag>.jsonl (resumable).  Read-only on every campaign and on A116/A119/A122.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a125lib as G
import a116lib as A
import a119lib as L
import sample125 as SMP

GRID =[(0.2, 20.0), (0.2, 10.0), (0.1, 20.0), (0.2, 5.0), (0.1, 10.0),
        (0.05, 20.0), (0.1, 5.0), (0.05, 10.0), (0.05, 5.0)]


def sample_until(bodies, nv, tested_target, seed0, batch=25000, draw_cap=6000000):
    """A116's sampler, repeated with fresh seeds until `tested_target` samples have passed the
    free-pair screen and been tested at 30 sides.  Reports drawn -> tested -> hits."""
    drawn = tested = hits = 0
    worst = None
    ex = []
    k = 0
    while tested < tested_target and drawn < draw_cap:
        s = A.sample_check(bodies, nv, n_samples=batch, seed=seed0 + 7919 * k,
                           s_lo=G.S_LO, s_hi=G.S0, n_side=30)
        drawn += s["n_samples"]
        tested += s["free_pairs_disjoint"]
        hits += s["hits"]
        ex += s["examples"]
        w = s["worst_free_overlap_of_rejects"]
        if w is not None:
            worst = w if worst is None else max(worst, w)
        k += 1
        if s["free_pairs_disjoint"] == 0 and k >= 8:
            break                       # the free block never fits: nothing more to learn
    return dict(drawn=drawn, tested=tested, hits=hits, sides_tested=30,
                side_range=[G.S_LO, G.S0], worst_free_overlap_of_rejects=worst,
                examples=ex[:3], batches=k, tested_target=tested_target)


def one(tag, r, rho, cut, time_cap, tested, starts, min_cell_deg, node_cap, log):
    t0 = time.time()
    bodies, nv, s_sh, P = G.build_bodies125(tag, r, rho, anchor_side=G.S0,
                                            pin_slack=G.PIN_SLACK, tilt_floor_deg=cut)
    _, Pe, _, _ = G.anchored125(tag, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    T = L.RecTree(bodies, nv, s_lo=G.S_LO, s_hi=G.S_HI, contact_pairs=list(ss),
                  min_cell_deg=min_cell_deg, node_cap=node_cap, time_cap=time_cap,
                  record=False, inherit=True)
    v = T.run()
    rec = dict(tag=tag, cls=G.SHADOWS[tag]["cls"], frame=G.SHADOWS[tag]["frame"], r=r, rho=rho,
               cut=cut, s_star=s_sh, anchor_side=G.S0, window=[G.S_LO, G.S_HI],
               L=[b.name for b in bodies if b.kind == "free"],
               P=[b.name for b in bodies if b.kind == "pin"],
               shadow_contacts=len(ss), tree=v, seconds_tree=round(time.time() - t0, 1))
    rec["n_witnesses"] = len(T.witnesses)
    rec["n_unresolved"] = len(T.unresolved)
    rec["witnesses"] = T.witnesses[:2]
    rec["unresolved"] = T.unresolved[:2]
    rec["trump"] = A.trump_in_N(bodies, pin_slack=G.PIN_SLACK)
    if v["dead"]:
        t1 = time.time()
        rec["sampling"] = SMP.run(bodies, tested, seed=int(1000 * r + rho),
                                  batch_size=200000, log=lambda *z: None)
        rec["local_min"] = A.local_min(bodies, nv, starts=starts, seed=7)
        rec["seconds_checks"] = round(time.time() - t1, 1)
    rec["seconds"] = round(time.time() - t0, 1)
    st = v["stats"]
    log("%s/%s r=%.2f rho=%4.1f cut=%s L=%d: %-12s nodes %-8d lp %-7d inh %-7d near %d "
        "leaves %.3g closed %-6d certmin %s  lm %s  samp %s  trump %s (%.0fs)"
        % (tag, rec["cls"], r, rho, cut, len(rec["L"]),
           "DEAD" if v["dead"] else ("CAP" if v["capped"] else
                                     "ALIVE(%dw,%du)" % (rec["n_witnesses"], rec["n_unresolved"])),
           st["nodes"], st["lp_calls"], st["dead_inherited"], v["n_near"],
           v["leaves_after_interval"], v["n_closed"],
           ("%.6f" % v["certified_min"]) if v["certified_min"] else "-",
           ("%.6f" % rec["local_min"]["side"]) if rec.get("local_min") else "-",
           ("%d/%d/%d" % (rec["sampling"]["drawn"], rec["sampling"]["tested"],
                          rec["sampling"]["hits"])) if rec.get("sampling") else "-",
           rec["trump"]["inside"], rec["seconds"]))
    if T.witnesses:
        w = T.witnesses[0]
        log("   witness side %.6f valid %s  cfg %s"
            % (w["witness_side"], w["witness_valid"], json.dumps(w.get("witness_cfg", {}))[:360]))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--grid", default="")
    ap.add_argument("--cut", type=float, default=None)
    ap.add_argument("--time_cap", type=float, default=1200.0)
    ap.add_argument("--tested", type=int, default=10000)
    ap.add_argument("--starts", type=int, default=60)
    ap.add_argument("--min_cell_deg", type=float, default=0.05)
    ap.add_argument("--node_cap", type=int, default=4000000)
    ap.add_argument("--suffix", default="")
    a = ap.parse_args()
    grid = GRID if not a.grid else [tuple(float(q) for q in c.split(":")) for c in a.grid.split(",")]
    out = os.path.join(G.RES, "grid_%s%s.jsonl" % (a.tag, a.suffix))
    logp = os.path.join(G.LOGS, "grid_%s%s.log" % (a.tag, a.suffix))

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                d = json.loads(line)
                done.add((d["tag"], d["r"], d["rho"], d["cut"]))
            except Exception:
                pass
    for (r, rho) in grid:
        if (a.tag, r, rho, a.cut) in done:
            continue
        try:
            rec = one(a.tag, r, rho, a.cut, a.time_cap, a.tested, a.starts,
                      a.min_cell_deg, a.node_cap, log)
        except Exception as e:
            log("ERROR %s r=%s rho=%s: %r" % (a.tag, r, rho, e))
            continue
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    log("grid %s%s done" % (a.tag, a.suffix))


if __name__ == "__main__":
    main()
