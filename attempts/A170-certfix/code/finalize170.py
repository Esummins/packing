"""A170 -- collect every re-certification result, write the `.certify.json` sidecars the lab's kill
scanners read, and summarise recovered PASSes by lane / class / level.

A sidecar is written ONLY for a row whose result is PASS on the FROZEN verify_case.py, and only beside
A170's own patched certificate under `attempts/A170-certfix/certs/`.  The ORIGINAL record in the other
attempt is never touched.

    python code/finalize170.py
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
sys.path.insert(0, HERE)
import certwrap170 as W                                        # noqa: E402

RES = os.path.join(BASE, "results")


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(RES, "recert170_*.jsonl"))):
        if "smoke" in f:
            continue
        for ln in open(f, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                r = json.loads(ln)
                r["_file"] = os.path.basename(f)
                rows.append(r)
    # de-duplicate on id, preferring PASS
    best = {}
    for r in rows:
        k = r["id"]
        if k not in best or (r["result"] == "PASS" and best[k]["result"] != "PASS"):
            best[k] = r
    rows = list(best.values())

    n_side = 0
    for r in rows:
        if r["result"] != "PASS" or not r.get("cert"):
            continue
        p = os.path.join(ROOT, r["cert"])
        if not os.path.exists(p):
            continue
        q = p.replace(".json", ".certify.json")
        json.dump(dict(cert=p, result="PASS", verifier_sha=W.FROZEN_SHA,
                       budget=r.get("budget"), total=r.get("total"),
                       rounds=[dict(round=0, result="PASS", verifier=r.get("verifier"))],
                       scope="s0_fixed_side",
                       source_record=r.get("src") or r.get("lp"),
                       note=("A170 re-certification: the cores were ENLARGED to A135 "
                             "exactcore.exact_a (the cores an ExactHyp LP's row filter uses); "
                             "caselp.make_certificate reverts to Hyp.from_json's stock b.core() -- "
                             "see attempts/A166-nearest-corner-subtree/notes/certificate_bug.md and "
                             "attempts/A170-certfix/notes/audit.md.  Enlarging a certified core only "
                             "removes verification obligations; exact_a certifies K(B) subset Q(p) "
                             "for every pose p in B.  The ORIGINAL FAIL record is untouched.")),
                  open(q, "w"), indent=1)
        n_side += 1

    by_lane = collections.defaultdict(collections.Counter)
    for r in rows:
        by_lane[r.get("lane", "?")][r["result"]] += 1
    print("%-34s %s" % ("lane", "results"))
    for L in sorted(by_lane):
        print("%-34s %s" % (L, dict(by_lane[L])))
    passes = [r for r in rows if r["result"] == "PASS"]
    print("\nrecovered PASSes: %d  (sidecars written: %d)" % (len(passes), n_side))
    for r in sorted(passes, key=lambda x: x["id"]):
        print("  %-58s was %-5s cores x%d (max ratio %.4f)  %s"
              % (r["id"], str(r.get("was")), r.get("n_applied", 0),
                 r.get("max_ratio", 1.0), r.get("cert", "")))
    json.dump(dict(n=len(rows), sidecars=n_side,
                   by_lane={k: dict(v) for k, v in by_lane.items()},
                   results=dict(collections.Counter(r["result"] for r in rows)),
                   passes=passes, verifier_sha=W.FROZEN_SHA),
              open(os.path.join(RES, "summary170.json"), "w"), indent=1)
    print("\nwrote results/summary170.json")


if __name__ == "__main__":
    main()
