"""A154 T2a' -- the (R6) screen over EVERY open k0_00 cell A115 left with an LP record.

Same rule as screen154.py; this is the population-level statement the price paragraph needs.
Writes results/screenall154.jsonl and results/screenall154_summary.json.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a154lib as L  # noqa: E402
from screen154 import one  # noqa: E402


def main():
    log = L.logger("screenall154.log")
    t0 = time.time()
    fam = L.get_fam(0.0, log=lambda *a: None)
    famID = L.get_fam(0.3, log=lambda *a: None)
    pool = L.open_pool()
    log("A154 screen-all: %d open k0 cells with an LP record" % len(pool))
    out = []
    for (nid, verdict, lp) in pool:
        try:
            r = one(fam, dict(nid=nid, group="openpool", cls="k0_00", level=None, lp=lp),
                    L.CORNERS, famID=famID)
        except Exception as ex:                                   # noqa: BLE001
            log("  !! %s %s: %s" % (nid, type(ex).__name__, ex))
            continue
        r["a115_verdict"] = verdict
        out.append(r)
    with open(os.path.join(L.RES, "screenall154.jsonl"), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    conv = [r for r in out if r["converged0"]]
    summ = dict(
        n=len(out), n_converged=len(conv), wall_s=round(time.time() - t0, 1),
        proved_useless=sum(1 for r in out if r["screen"] == "PROVED-USELESS"),
        proved_useless_of_converged=sum(1 for r in conv if r["screen"] == "PROVED-USELESS"),
        candidates=sum(1 for r in out if r["screen"].startswith("CANDIDATE")),
        candidates_converged=sum(1 for r in conv if r["screen"].startswith("CANDIDATE")),
        c_ge_B=sum(1 for r in out if r["c_ge_B"]),
        cID_ge_BID=sum(1 for r in out if r.get("cID_ge_BID")),
        B_ID_zero=sum(1 for r in out if r.get("B_ID") == 0),
        mean_c=round(sum(r["c_stored"] for r in out) / max(1, len(out)), 4),
        mean_B=round(sum(r["B"] for r in out) / max(1, len(out)), 4),
        mean_cID=round(sum(r.get("c_ID", 0.0) for r in out) / max(1, len(out)), 4),
        candidate_nids=[r["nid"] for r in out if r["screen"].startswith("CANDIDATE")])
    json.dump(summ, open(os.path.join(L.RES, "screenall154_summary.json"), "w"), indent=1)
    log(json.dumps({k: v for k, v in summ.items() if k != "candidate_nids"}, indent=1))


if __name__ == "__main__":
    main()
