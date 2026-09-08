"""A149 -- turn the day's exact-core re-emission verdicts into A57 supersession rows.

A137's `reemit_ledger137.py` format, byte-for-byte the same fields, plus two A149 ones:

  `box`        which box the kill was proved on -- the node's RECORDED box, or A137 lane (b)'s
               T5'''-CLIPPED sub-box where one was available (`targets149.py` substitutes it only
               after checking containment).  A kill on the clipped box is a kill of the node: the
               clip certifies the discarded region pin-infeasible (A131's `pin-clip-kill-
               certificate-v1`, checker 159/159 last night).
  `verifier`   the FROZEN `verify_case.py` on every row here.  `verify_case_v3` is used ONLY where
               the frozen verifier FAILs with holes, and those rows go to a SEPARATE ledger
               (`superseded_by_exactcore_v3_A149.jsonl`) so the frozen and v3 chains never mix.

The ledger is written UNDER THIS ATTEMPT.  Nothing in A57 is rewritten; the fold-in line is one
paragraph appended to PAUSED.md v3.  NO-KILL, TOO-TIGHT, LOST-KILL-ON-RESOLVE and WALL-CAP are not
supersessions and stay in this attempt's own results only -- a capped LP is never a verdict.
"""
import collections
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
LEDGER = os.path.join(BASE, "results", "superseded_by_exactcore_A149.jsonl")
LEDGER_V3 = os.path.join(BASE, "results", "superseded_by_exactcore_v3_A149.jsonl")
SUMMARY = os.path.join(BASE, "results", "day149_summary.json")


def main():
    tgt = {}
    p = os.path.join(BASE, "results", "targets149.json")
    if os.path.exists(p):
        for t in json.load(open(p)):
            tgt[t["id"]] = t
    rows, v3rows, c = [], [], collections.Counter()
    cpu = 0.0
    bands = collections.Counter()
    kills_by_band = collections.Counter()
    for p in sorted(glob.glob(os.path.join(BASE, "results", "exact_reemit_*.jsonl"))):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            res = r.get("result")
            c[res] += 1
            cpu += float(r.get("wall_total_s") or 0.0)
            fe = r.get("frac_exact")
            band = (">=0.60" if (fe or 0) >= 0.60 else "0.45-0.60" if (fe or 0) >= 0.45 else
                    "0.30-0.45" if (fe or 0) >= 0.30 else "<0.30")
            if res != "WALL-CAP":
                bands[band] += 1
            if res != "PASS":
                continue
            kills_by_band[band] += 1
            t = tgt.get(r["id"], {})
            row = dict(
                id=r["id"], level=r.get("level"), cls=r.get("cls"),
                prior_verdict=r.get("prior"), prior_tau=r.get("tau_before"),
                prior_eta=r.get("eta_before"),
                superseded_by="LP kill on EXACT certified-maximal cores (scope %s), FROZEN "
                              "verify_case.py 521cb01f" % r.get("scope"),
                leaf="case-measure-certificate-v1 (ordinary leaf; only the core half-side "
                     "changed)",
                tau=r.get("tau"), converged=r.get("converged"),
                cert=r.get("cert"), pin_gate=r.get("pin_gate"),
                cores_exact=r.get("a_report"),
                lp_wall_s=r.get("lp_wall_s"), wall_total_s=r.get("wall_total_s"),
                box=t.get("box"),
                box_source=t.get("box_source", "the node's recorded box"),
                frac_exact=fe, frac_exact_band=band,
                verifier="FROZEN verify_case.py (521cb01f)",
                note="prior verdict RETAINED; this node is now a certified kill. Not overwritten "
                     "in the tree jsonl.",
                folded_by="A149", recorded=time.strftime("%Y-%m-%d %H:%M:%S"))
            rows.append(row)
    for path, rr in ((LEDGER, rows), (LEDGER_V3, v3rows)):
        with open(path, "w", encoding="utf-8") as f:
            for r in rr:
                f.write(json.dumps(r) + "\n")
    summ = dict(when=time.strftime("%Y-%m-%d %H:%M:%S"), attempt="A149",
                lane="exact-pin-core re-emission (day shift)",
                nodes_run=sum(c.values()), cpu_h=round(cpu / 3600, 2),
                results=dict(c),
                decided=sum(v for k, v in c.items() if k != "WALL-CAP"),
                certified_kills=len(rows),
                kill_rate=(round(len(rows) / max(1, sum(v for k, v in c.items()
                                                        if k != "WALL-CAP")), 4)),
                by_band={b: dict(decided=bands[b], kills=kills_by_band[b]) for b in bands},
                v3_rows=len(v3rows), ledger=LEDGER, ledger_v3=LEDGER_V3)
    json.dump(summ, open(SUMMARY, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
