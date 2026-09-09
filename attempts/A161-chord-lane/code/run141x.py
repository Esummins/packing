"""A161 T6 -- A141's OWN leaf (`LANE_K' + M <= 1`), re-run with the exact separating-axis test.

A141's `t2_a5760` pass early-exits: `lane_corner_generic` skips the covers as soon as the SAMPLED
lower bounds give `lane_lb + M_lb >= 2`, and its `M` is decided by `cond_can_meet`, whose
`box_misses_cell` separates only along the CELL's two normals.  That test can never fire for a
conditioned box whose square clears the cell along one of its OWN edge normals, so a `NEAR-MISS-OR-
WORSE` row with `M_lb = 1` may be a budget artefact rather than geometry (A161 T1: on
`k5_16_interior_Y0842 / BL(1,0)` the exact test excludes `H` at the ROOT box, and `M` is 0).

This driver re-decides those rows with `chordlane.box_misses_cell_exact` (the FULL SAT test over the
parameter box, exact Fractions) in BOTH covers, and NO chord row and NO band prune -- so every kill
here is a kill under A141's leaf exactly as A141 states it, in A141's own certificate format
(`polycore_lane_v1`, `kind = "polycore_slot_lane"`), with one documented extension: a `misses_cell`
leaf now carries an `axis` field naming which of the eight (axis, sign) pairs discharged it.
`check141x.py` verifies these with A141's own `check_lane_cert` plus that extension.

    python run141x.py --shard 0/1 --out ../results/t6_a141x.jsonl
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import chordlane as CL  # noqa: E402
import numpy as np  # noqa: E402
import polylane as P  # noqa: E402
import polycore as PC  # noqa: E402
import emit141 as EM  # noqa: E402  READ-ONLY (A141's certificate writer)
from caselp import Box  # noqa: E402

A141_T2 = [os.path.join(ROOT, "attempts", "A141-polycore-lane", "results", f)
           for f in ("t2_a5760_s0.jsonl", "t2_a5760_s1.jsonl")]
EARLY = ("UNDECIDED", "NEAR-MISS", "NEAR-MISS-OR-WORSE")


def eligible():
    killed, rows = set(), []
    for f in A141_T2:
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.append(r)
            if r.get("kill"):
                killed.add(r["nid"])
    out = []
    for r in rows:
        if r["nid"] in killed:
            continue
        for cl in r["cells"]:
            if cl.get("verdict") in EARLY and (cl.get("lane_lb") or 0) <= 1:
                out.append(dict(nid=r["nid"], src=r["src"], cls=r["cls"], level=r["level"],
                                slot=cl["cell"], a141_verdict=cl["verdict"],
                                a141_lane_lb=cl.get("lane_lb"), a141_lane_ub=cl.get("lane_ub"),
                                a141_M=cl.get("M"), a141_skipped=cl.get("skipped_covers")))
    return out, killed


def sample_line(cell, conds, s, n, rng):
    """A118's confirmation, in A141's shape: poses in R'(C), the free ones, and the widest gap of
    any free pair (a positive gap would REFUTE `LANE <= 1`)."""
    pool = CL.sample_pool(cell, conds, s, n, rng)
    Cs, Ts, hit = pool["C"], pool["T"], pool["hit"]
    out = dict(drawn=n, meeting=int(len(Cs)), per_core=pool["per_core"],
               overlapping_some_core=int(hit.sum()), free=int((~hit).sum()))
    ix = np.nonzero(~hit)[0][:800]
    if len(ix) >= 2:
        G = CL.LANE.L.pair_gaps(Cs[ix], Ts[ix])
        np.fill_diagonal(G, -1e9)
        out["max_free_pair_gap"] = float(G.max())
    return out


def run_pair(rec, slot, rng, sample, max_open, max_depth, budget_s, keep_cert=True,
             m_only=False):
    dl = time.time() + budget_s
    conds, meet, cell, corner, i, j = CL.frame_boxes(rec, slot)
    n_pins = len(conds) - len(meet)
    res = dict(cell=list(cell), lane_lb=None, lane_ub=None, M=None, verdict="UNDECIDED")
    # ---- M, with the exact SAT test in the exclusion cover
    Mdet, Mcert = [], []
    for cs in conds:
        if cs.idx not in meet:
            continue
        hit, nhit = CL.cond_meets_sample(cs, cell, conds, CL.S0, 4000, rng)
        if hit:
            Mdet.append(dict(j=cs.idx, excluded=False, by="sample"))
            Mcert.append(None)
            continue
        r = CL.cond_excluded(cs, cell, conds, s=CL.S0, max_depth=max_depth, deadline=dl)
        Mdet.append(dict(j=cs.idx, excluded=bool(r["ok"]), by="cover"))
        Mcert.append(r["leaves"] if (keep_cert and r["ok"]) else None)
    M = sum(0 if e["excluded"] else 1 for e in Mdet)
    res.update(M=M, M_exact=True, M_detail=Mdet, M_cert=Mcert,
               meeters=[e["j"] for e in Mdet if not e["excluded"]])
    if M >= 2:
        res["verdict"] = "M>=2"
        return res, conds, None
    if m_only:
        res["verdict"] = "M-ONLY"
        return res, conds, None
    # ---- LANE, with the exact SAT test and NO band prune (A141's leaf verbatim)
    cov = CL.lane_out(cell, conds, None, s=CL.S0, max_depth=max_depth, max_open=max_open,
                      deadline=dl)
    res.update(lane_ub=cov["lane"], root=cov["root"], cover_cert=cov["leaves"],
               cover_open_cert=cov["open"], cover_leaves=len(cov["leaves"]),
               cover_open=len(cov["open"]), cover_reason=cov.get("reason"))
    if cov["lane"] is None:
        res["verdict"] = "UNDECIDED"
        return res, conds, None
    sm = sample_line(cell, conds, CL.S0, sample, rng)
    res["sample"] = sm
    res["lane_lb"] = 1 if sm.get("free") else 0
    if sm.get("max_free_pair_gap", -1.0) > 0.0:
        res["verdict"] = "INCONSISTENT (a free interior-disjoint pair was sampled)"
        return res, conds, None
    tot = cov["lane"] + M
    res["verdict"] = "KILL" if tot <= 1 else ("NEAR-MISS" if tot == 2 else "UNDECIDED")
    res["n_pins"] = n_pins
    return res, conds, (cell, corner, i, j)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t6_a141x.jsonl"))
    ap.add_argument("--progress", default=os.path.join(BASE, "progress", "t6.json"))
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--maxopen", type=int, default=6000)
    ap.add_argument("--maxdepth", type=int, default=38)
    ap.add_argument("--pair_s", type=float, default=12.0)
    ap.add_argument("--cap_s", type=float, default=6000.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--m_only", action="store_true", help="stage-M pass: exact M for every pair, no LANE cover")
    ap.add_argument("--from_rows", default="", help="only pairs whose row in this jsonl has M <= m_max")
    ap.add_argument("--m_max", type=int, default=0)
    a = ap.parse_args()

    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    pairs, killed = eligible()
    k, n = (int(v) for v in a.shard.split("/"))
    pairs = [p for idx, p in enumerate(pairs) if idx % n == k and p["nid"] in recs]
    if a.from_rows and os.path.exists(a.from_rows):
        keep = set()
        for ln in open(a.from_rows, encoding="utf-8"):
            r = json.loads(ln)
            if r.get("M") is not None and r["M"] <= a.m_max and r.get("verdict") != "ERROR":
                keep.add((r["nid"], r["slot"]))
        pairs = [p for p in pairs if (p["nid"], p["slot"]) in keep]
        print("  filtered to %d pairs with exact M <= %d" % (len(pairs), a.m_max), flush=True)
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                r = json.loads(ln)
                done.add((r["nid"], r["slot"]))
            except Exception:
                pass
    print("shard %s: %d early-exit (node, slot) pairs (%d done)" % (a.shard, len(pairs),
                                                                    len(done)), flush=True)
    fh = open(a.out, "a", encoding="utf-8")
    rng = np.random.default_rng(1615 + k)
    t0 = time.time()
    nrun, tally = 0, {}
    for p in pairs:
        if (p["nid"], p["slot"]) in done:
            continue
        if time.time() - t0 > a.cap_s:
            print("wall cap reached", flush=True)
            break
        rec = recs[p["nid"]]
        row = dict(p)
        try:
            res, conds, meta = run_pair(rec, p["slot"], rng, a.sample, a.maxopen, a.maxdepth,
                                        a.pair_s, m_only=a.m_only)
            row.update(verdict=res["verdict"], lane_ub=res.get("lane_ub"),
                       lane_lb=res.get("lane_lb"), M=res.get("M"),
                       meeters=res.get("meeters"), cover_leaves=res.get("cover_leaves"),
                       cover_open=res.get("cover_open"), n_pins=res.get("n_pins"),
                       M_by=[e["by"] for e in (res.get("M_detail") or [])],
                       free=(res.get("sample") or {}).get("free"),
                       max_free_pair_gap=(res.get("sample") or {}).get("max_free_pair_gap"))
            if res["verdict"] == "KILL":
                d = EM.cert_dict("polycore_slot_lane", p["nid"], p["slot"], conds,
                                 [c.box for c in conds], res,
                                 extra=dict(cell_kind="usable_slot", cls=rec["cls"],
                                            level=rec["level"], src=rec["src"],
                                            extension=CL.CP.CLASSES[rec["cls"]]["usable"][
                                                p["slot"]],
                                            extension_window="[191/50, 969271/250000] FULL "
                                                             "(A56/A61/A114 scoreboard)",
                                            n_pins=res["n_pins"],
                                            leaf_rule_ext="A161: `misses_cell` leaves carry an "
                                                          "`axis` field -- the full separating-"
                                                          "axis test over the parameter box "
                                                          "(cell normals AND the square's own, "
                                                          "both signs, exact Fractions). "
                                                          "check141x.py verifies it.",
                                            emitted_by="A161 run141x.py"))
                q = os.path.join(BASE, "certs141x", "slot_%s__%s.json"
                                 % (p["nid"], p["slot"].replace("(", "").replace(")", "")
                                    .replace(",", "_")))
                row["cert"] = os.path.relpath(q, ROOT)
                row["sha256"] = EM.write_cert(q, d)
        except Exception as e:                                       # noqa: BLE001
            row["verdict"] = "ERROR"
            row["error"] = repr(e)[:200]
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        tally[row["verdict"]] = tally.get(row["verdict"], 0) + 1
        nrun += 1
        if row["verdict"] == "KILL":
            print("  %-36s %-9s KILL LANE=%s M=%s (A141 said %s, M=%s)"
                  % (p["nid"], p["slot"], row["lane_ub"], row["M"], p["a141_verdict"],
                     p["a141_M"]), flush=True)
        if nrun % 25 == 0:
            el = time.time() - t0
            json.dump(dict(done=nrun, elapsed=round(el, 1), tally=tally),
                      open(a.progress, "w", encoding="utf-8"))
            print("  %d/%d  %.0f s  %.2f s/pair  %s" % (nrun, len(pairs), el, el / nrun, tally),
                  flush=True)
        if a.limit and nrun >= a.limit:
            break
    fh.close()
    json.dump(dict(done=nrun, elapsed=round(time.time() - t0, 1), tally=tally, finished=True),
              open(a.progress, "w", encoding="utf-8"))
    print("done %d pairs, %.0f s, %s" % (nrun, time.time() - t0, tally), flush=True)


if __name__ == "__main__":
    main()
