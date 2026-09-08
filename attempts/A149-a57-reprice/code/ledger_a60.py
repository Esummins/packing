"""A149 -- A60 (trump5) exact-core re-emission verdicts into A60 supersession rows.

Same field set as A137's `reemit_ledger137.py` / this attempt's `ledger149.py`, with the A60
specifics named on every row: the scope is `exH` (only the conditioned square's core is made
exact; A60's five pins keep the corpus core `16383999967232/32768001953125`, because at `a = 1/2`
the cores of two slots exactly 1.0 apart would touch and the `budget = n - #cores` bridge would
lose pairwise disjointness -- the measured gap at the corpus core is 6.2e-8), and the verifier is
the FROZEN `verify_case.py`, whose A57 and A60 copies are byte-identical (sha256 521cb01f...).

Written UNDER THIS ATTEMPT.  Nothing in A60 is rewritten; the fold-in is one paragraph appended to
A60's `notes/ledger.md`.  NO-KILL / TOO-TIGHT / LOST-KILL-ON-RESOLVE / WALL-CAP are not
supersessions: a capped LP is never a verdict, and a NO-KILL leaves the node as it was.
"""
import collections
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
LEDGER = os.path.join(BASE, "results", "superseded_by_exactcore_a60_A149.jsonl")
LEDGER_V3 = os.path.join(BASE, "results", "superseded_by_exactcore_a60_v3_A149.jsonl")
SUMMARY = os.path.join(BASE, "results", "day149_a60_summary.json")


def main():
    rows, c, cpu = [], collections.Counter(), 0.0
    core_gain = []
    for p in sorted(glob.glob(os.path.join(BASE, "results", "a60_reemit_*.jsonl"))):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            c[r.get("result")] += 1
            cpu += float(r.get("wall_total_s") or r.get("wall_s") or 0.0)
            ar = r.get("a_report") or []
            if ar:
                from fractions import Fraction as Fr
                h = ar[-1]
                try:
                    core_gain.append(float(Fr(h["a_used"])) / float(Fr(h["a_stock"])))
                except Exception:
                    pass
            if r.get("result") != "PASS":
                continue
            rows.append(dict(
                id=r["id"], camp="A60", cls="trump5", level=r.get("level"),
                families=r.get("families"),
                prior_verdict="ALIVE (A107 shadow gallery, src A60)",
                prior_tau=r.get("tau_before"), prior_converged=r.get("converged_before"),
                superseded_by="LP kill with A135's EXACT certified-maximal core on the "
                              "CONDITIONED square (scope exH; A60's pins keep the corpus core), "
                              "FROZEN verify_case.py 521cb01f",
                leaf="case-measure-certificate-v1 (ordinary leaf; only the conditioned square's "
                     "core half-side changed)",
                tau=r.get("tau"), converged=r.get("converged"), cert=r.get("cert"),
                pin_gate=r.get("pin_gate"), cores_exact=r.get("a_report"), sym=r.get("sym"),
                node=r.get("node"), lpbox=r.get("lpbox"),
                lp_wall_s=r.get("lp_wall_s"), wall_total_s=r.get("wall_total_s"),
                verifier="FROZEN verify_case.py (521cb01f)",
                note="prior verdict RETAINED; this node is now a certified kill. Not overwritten "
                     "in A60's node files.",
                folded_by="A149", recorded=time.strftime("%Y-%m-%d %H:%M:%S")))
    for path, rr in ((LEDGER, rows), (LEDGER_V3, [])):
        with open(path, "w", encoding="utf-8") as f:
            for r in rr:
                f.write(json.dumps(r) + "\n")
    dec = sum(v for k, v in c.items() if k != "WALL-CAP")
    summ = dict(when=time.strftime("%Y-%m-%d %H:%M:%S"), attempt="A149", camp="A60",
                lane="exact-core re-emission, scope exH (conditioned square only)",
                nodes_run=sum(c.values()), cpu_h=round(cpu / 3600, 2), results=dict(c),
                decided=dec, certified_kills=len(rows),
                kill_rate=round(len(rows) / dec, 4) if dec else None,
                h_core_gain_mean=(round(sum(core_gain) / len(core_gain), 4)
                                  if core_gain else None),
                h_core_gain_max=round(max(core_gain), 4) if core_gain else None,
                ledger=LEDGER, ledger_v3=LEDGER_V3)
    json.dump(summ, open(SUMMARY, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
