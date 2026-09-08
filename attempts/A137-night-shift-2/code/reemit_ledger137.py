"""A137 -- turn tonight's exact-core re-emission verdicts into A57 supersession rows.

A PASS here is a node that was recorded ALIVE-at-LP and is now certified dead by the FROZEN
`verify_case.py` on a certificate whose only change is the core half-side (A135's exact
certified-maximal rational cores).  It supersedes the ALIVE verdict; the tree jsonl is not
rewritten, exactly as `superseded_by_tight_core.jsonl` does it.

NO-KILL and WALL-CAP rows are NOT supersessions and are written only to this attempt's own
results: a capped LP is never a verdict (A124), and a NO-KILL leaves the node exactly as it was.
"""
import collections
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
LEDGER = os.path.join(A57, "results", "superseded_by_exactcore_A137.jsonl")


def main():
    rows, c = [], collections.Counter()
    for p in sorted(glob.glob(os.path.join(BASE, "results", "exact_reemit_*.jsonl"))):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            c[r.get("result")] += 1
            if r.get("result") != "PASS":
                continue
            rows.append(dict(
                id=r["id"], level=r.get("level"), cls=r.get("cls"),
                prior_verdict=r.get("prior"), prior_tau=r.get("tau_before"),
                prior_eta=r.get("eta_before"),
                superseded_by="LP kill on EXACT certified-maximal cores (scope %s), FROZEN "
                              "verify_case.py 521cb01f" % r.get("scope"),
                leaf="case-measure-certificate-v1 (ordinary leaf; only the core half-side changed)",
                tau=r.get("tau"), converged=r.get("converged"),
                cert=r.get("cert"), pin_gate=r.get("pin_gate"),
                cores_exact=r.get("a_report"),
                lp_wall_s=r.get("lp_wall_s"), wall_total_s=r.get("wall_total_s"),
                note="prior verdict RETAINED; this node is now a certified kill. Not overwritten "
                     "in the tree jsonl.",
                folded_by="A137", recorded=time.strftime("%Y-%m-%d %H:%M:%S")))
    with open(LEDGER, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} certified exact-core kills -> {LEDGER}")
    print(json.dumps(dict(c), indent=1))


if __name__ == "__main__":
    main()
