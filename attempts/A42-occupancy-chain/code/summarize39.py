#!/usr/bin/env python3
"""A39 aggregation: the three numbers that re-run A38's GO/NO-GO arithmetic."""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A39 = os.path.abspath(os.path.join(HERE, ".."))
A38R = os.path.abspath(os.path.join(HERE, "..", "..", "A38-root-power", "results"))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pop_summary(pop):
    lp = os.path.join(A39, "results", "p2a", pop, "ledger.json")
    if not os.path.exists(lp):
        return None
    L = json.load(open(lp))
    A = {r["cid"]: r for r in L.get("A", [])}
    B = {r["cid"]: r for r in L.get("B", [])}
    C = {r["cid"]: r for r in L.get("C", [])}
    # results whose worker finished but whose ledger line was never written (ordered ex.map, or a
    # run cut short): recover them from the per-node record files.
    import glob as _g
    d = os.path.dirname(lp)
    for suf, tgt in (("_B", B), ("_C", C)):
        for f in _g.glob(os.path.join(d, "*%s.rec.json" % suf)):
            cid = os.path.basename(f)[:-len(suf + ".rec.json")]
            if cid in tgt:
                continue
            try:
                rec = json.load(open(f))
            except Exception:
                continue
            a = A.get(cid, {})
            tgt[cid] = dict(cid=cid, stage=suf[1], result=rec.get("status"),
                            decided=rec.get("decided"), certified=rec.get("certified"),
                            tau=rec.get("tau"), status_a27=rec.get("status_a27"),
                            n_cert_attempts=rec.get("n_cert_attempts"),
                            cert_verify_s=rec.get("cert_verify_s"),
                            rows_fed_back=rec.get("rows_fed_back"),
                            t_decide=rec.get("t_decide"), t_marginal=rec.get("seconds"),
                            attempts=rec.get("cert_attempts"),
                            a38_seconds=a.get("a38_seconds"), recovered=True)
    cids = list(A) or list(B)
    rows = []
    for cid in cids:
        a = A.get(cid, {})
        b = B.get(cid)
        cached = a.get("a38_seconds") or (b or {}).get("a38_seconds") or 0.0
        if a.get("result") == "PASS":
            rows.append(dict(cid=cid, decided=True, how="stageA",
                             t_marginal=a["t_marginal"], t_total=cached + a["t_marginal"],
                             a38_seconds=cached))
        elif b is not None:
            dec = bool(b.get("certified")) or b.get("result") == "alive(LP)"
            rows.append(dict(cid=cid, decided=dec, how=("stageB" if dec else None),
                             status=b.get("result"),
                             t_marginal=a.get("t_marginal", 0.0) + b["t_marginal"],
                             t_total=cached + a.get("t_marginal", 0.0) + b["t_marginal"],
                             a38_seconds=cached, n_cert_attempts=b.get("n_cert_attempts"),
                             rows_fed_back=b.get("rows_fed_back"), tau=b.get("tau")))
        else:
            rows.append(dict(cid=cid, decided=False, how=None, status=a.get("result"),
                             t_marginal=a.get("t_marginal", 0.0),
                             t_total=cached + a.get("t_marginal", 0.0), a38_seconds=cached))
    n = len(rows)
    dec = [r for r in rows if r["decided"]]
    out = dict(pop=pop, n=n, n_decided=len(dec), frac_decided=(len(dec) / n if n else 0.0),
               ci95_frac_decided=wilson(len(dec), n),
               n_stageA=sum(1 for r in rows if r["how"] == "stageA"),
               n_stageB=sum(1 for r in rows if r["how"] == "stageB"),
               median_t_decide_marginal=(st.median([r["t_marginal"] for r in dec]) if dec else None),
               median_t_decide_total=(st.median([r["t_total"] for r in dec]) if dec else None),
               median_t_node_marginal=st.median([r["t_marginal"] for r in rows]) if rows else None,
               median_t_node_total=st.median([r["t_total"] for r in rows]) if rows else None,
               a38_median_seconds=(st.median([r["a38_seconds"] for r in rows if r["a38_seconds"]])
                                   if any(r["a38_seconds"] for r in rows) else None),
               rows=rows)
    if C:
        cr = list(C.values())
        cd = [r for r in cr if r.get("certified")]
        out["cold"] = dict(n=len(cr), n_decided=len(cd),
                           frac_decided=len(cd) / len(cr) if cr else 0.0,
                           median_seconds=st.median([r["t_marginal"] for r in cr]),
                           median_t_decide=(st.median([r["t_marginal"] for r in cd]) if cd else None))
    # certification-attempt trajectories: does the loop move tau at all?
    traj = []
    for src in (B, C):
        for r in src.values():
            at = [x for x in (r.get("attempts") or []) if "rc" in x]
            if not at:
                continue
            traj.append(dict(cid=r["cid"], n=len(at), tau_first=at[0]["tau"],
                             tau_last=at[-1]["tau"], d_tau=at[-1]["tau"] - at[0]["tau"],
                             rows_fed=r.get("rows_fed_back"),
                             verify_s=sum(x.get("verify_s", 0) for x in at)))
    if traj:
        out["trajectory"] = dict(
            n=len(traj), median_attempts=st.median([t["n"] for t in traj]),
            median_d_tau=st.median([t["d_tau"] for t in traj]),
            n_tau_increased=sum(1 for t in traj if t["d_tau"] > 1e-6),
            n_tau_decreased=sum(1 for t in traj if t["d_tau"] < -1e-6),
            median_rows_fed=st.median([t["rows_fed"] or 0 for t in traj]),
            median_verify_s=st.median([t["verify_s"] for t in traj]),
            rows=traj)
    f = out["frac_decided"]
    out["b_eff"] = 8.0 * (1 - f)
    lo, hi = out["ci95_frac_decided"]
    out["b_eff_pessimistic"] = 8.0 * (1 - lo)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(A39, "results", "a39_summary.json"))
    a = ap.parse_args()
    S = dict(when=__import__("time").strftime("%FT%T"))

    # --- G1 debt
    g1p = os.path.join(A39, "results", "p2a", "g1", "g1_debt.json")
    if os.path.exists(g1p):
        g = json.load(open(g1p))
        S["G1"] = dict(n=len(g["records"]), n_pass=g["n_pass"], n_fail=g["n_fail"],
                       n_error=g.get("n_error", 0), wall=g["wall"],
                       median_seconds=st.median([r["wall"] for r in g["records"]]),
                       max_seconds=max(r["wall"] for r in g["records"]))

    for pop in ("l2", "l1u"):
        s = pop_summary(pop)
        if s:
            S[pop] = s

    # --- level-1 kill fractions after the debt discharge + the all-node probe
    l1 = json.load(open(os.path.join(A38R, "l1_a38.json")))
    m = l1["matrix"]
    n_proc = sum(1 for r in m if r["status"] != "notrun")
    n_dead = sum(1 for r in m if r["status"] == "dead(T1)")
    ncert = S.get("G1", {}).get("n_pass", 0) + 6
    probe = os.path.join(A39, "results", "p2a", "l1all", "l1all_probe.json")
    n_new = 0
    if os.path.exists(probe):
        pr = json.load(open(probe))
        n_new = pr["n_pass"]
        S["l1all_probe"] = dict(n=len(pr["records"]), n_pass=n_new, wall=pr["wall"],
                                median_seconds=st.median([r["wall"] for r in pr["records"]]),
                                passed=[r["idx"] for r in pr["records"] if r["result"] == "PASS"],
                                n_skipped_tau_ge_budget=sum(
                                    1 for r in pr["records"]
                                    if any("skipped" in x for x in r.get("rounds", []))))
    tot = ncert + n_new
    S["level1"] = dict(n_total=len(m), n_processed=n_proc, n_dead=n_dead,
                       n_certified_debt=ncert, n_certified_new_from_undecided=n_new,
                       n_certified_now=tot,
                       f1_certified_A38=6 / n_proc,
                       f1_optimistic_A38=n_dead / n_proc,
                       f1_certified_A39=tot / n_proc,
                       f1_over_216_A39=tot / len(m),
                       b_eff_A38_certified=8 * (1 - 6 / n_proc),
                       b_eff_A39=8 * (1 - tot / n_proc))

    # --- P2b
    lp = os.path.join(A39, "results", "p2b", "reseal_ledger.json")
    if os.path.exists(lp):
        S["P2b"] = json.load(open(lp))
    for f in ("w1_depth_baseline.json", "w1_depth_resealed.json"):
        p = os.path.join(A39, "results", "p2b", f)
        if os.path.exists(p):
            d = json.load(open(p))
            S.setdefault("W1", {})[f.replace(".json", "")] = dict(
                eta_cert=d["eta_cert"], thresholds=d["thresholds"], summary=d["summary"],
                c_core_max_by_depth=d["c_core_max_by_depth"])

    json.dump(S, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in S.items() if k not in ("P2b",)}, indent=1, default=str)[:6000])
    print("->", a.out)


if __name__ == "__main__":
    main()
