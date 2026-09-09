"""A149 -- re-verify, with NO re-solve, every non-PASS certificate this attempt wrote.

The coordinator's instruction after A166's finding: re-run the FAIL / TOO-TIGHT /
LOST-KILL-ON-RESOLVE records through the fixed emit path, cheapest first, with no re-solve where
the measure is stored.

For A149 the measure IS stored -- every non-PASS outcome except NO-KILL wrote its certificate to
disk before the verdict was taken (`emit135.certify` dumps the certificate and only then tests the
total), so the atoms and weights are on disk and nothing needs re-solving.  And `certaudit149.py`
shows this attempt was never on the broken path: all 137 A57 certificates carry A135's EXACT cores
on every box, because both node paths emit through A135's `make_cert` (which reads the live `Hyp`)
and never through `caselp.make_certificate`.

So this pass is a MEASUREMENT, not a repair.  It re-runs the FROZEN `verify_case.py` on each
stored certificate and records the verdict and the hole count, which is what A170's audit needs to
tell a real hole from A166's spurious annulus:

  * TOO-TIGHT cannot PASS by construction -- its written total is >= budget, which the verifier's
    claim forbids -- so it is reported as such without a run;
  * LOST-KILL-ON-RESOLVE and FAIL are re-verified, and their holes are real if they reproduce.
"""
import argparse
import glob
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A135 = os.path.join(ROOT, "A135-polycore-verifier", "code")
if A135 not in sys.path:
    sys.path.insert(0, A135)
OUT = os.path.join(BASE, "results", "recheck149.jsonl")


def rows():
    out = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "exact_reemit_*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            r["_cert"] = os.path.join(BASE, "certs",
                                      "%s__%s.json" % (r["id"], r.get("scope", "exall")))
            r["_camp"] = "A57"
            out.append(r)
    for f in sorted(glob.glob(os.path.join(BASE, "results", "a60_reemit_*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            r["_cert"] = os.path.join(BASE, "certs", "a60", "%s__exH.json" % r["id"])
            r["_camp"] = "A60"
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--max", type=int, default=10 ** 6)
    a = ap.parse_args()
    import emit135                                                       # noqa: E402

    done = set()
    if os.path.exists(OUT):
        for ln in open(OUT, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass

    cand = [r for r in rows()
            if r["result"] in ("TOO-TIGHT", "LOST-KILL-ON-RESOLVE", "FAIL", "FAIL-NO-WITNESS")
            and os.path.exists(r["_cert"]) and r["id"] not in done]
    cand.sort(key=lambda r: os.path.getsize(r["_cert"]))          # cheapest first
    print("%d stored non-PASS certificates to re-verify (no re-solve)" % len(cand), flush=True)

    for r in cand[:a.max]:
        d = json.load(open(r["_cert"]))
        tot = float(Fr(d["total"]))
        budget = r.get("budget", 5)
        rec = dict(id=r["id"], camp=r["_camp"], prior_result=r["result"], cert=r["_cert"],
                   total=tot, budget=budget, atoms=len(d.get("atoms") or []),
                   cores=[c["a"] for c in (d.get("hypotheses") or {}).get("cores", [])],
                   when=time.strftime("%F %T"))
        if tot >= budget:
            rec.update(recheck="NOT-RUN", why="written total %.6f >= budget %s; the verifier's "
                                              "claim requires total < budget, so this certificate "
                                              "cannot PASS without a better tau" % (tot, budget))
        else:
            t0 = time.time()
            rc, txt = emit135.run_case(r["_cert"], a.jobs, a.depth)
            tail = emit135.tail_lines(txt)
            holes = None
            for l in tail:
                if "holes" in l:
                    holes = l
            rec.update(recheck=("PASS" if rc == 0 else "FAIL"), rc=rc,
                       verify_s=round(time.time() - t0, 1), verifier=tail, holes=holes)
        with open(OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print("  %-34s %-22s -> %s" % (rec["id"], rec["prior_result"], rec["recheck"]), flush=True)
    print("done -> " + OUT)


if __name__ == "__main__":
    main()
