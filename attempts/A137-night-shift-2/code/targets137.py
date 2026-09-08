"""A137 -- build the exact-pin-core re-emission queue: the ALIVE population that SURVIVES the
T1 fold-in (A135's named chore, priority (a) for tonight's LP slots).

A node is a target iff its recorded verdict is ALIVE-at-LP (any depth), it carries a centre box,
and neither it nor any ancestor appears in tonight's fold-in ledger
(`superseded_by_backlog_A137.jsonl`) -- there is no point re-solving a box that is already dead
by geometry.

Ordering (the LP slots are the scarce resource) -- A145's threshold predictor, `frac_exact`, the
fraction of the node's dual-support WEIGHT that is impossible under the exact hypothesis
(`attempts/A145-impossible-weight/results/impossible_weight.jsonl`): 4 of 5 nodes at
frac_exact >= 0.60 fell to the exact-core/K' re-solve, 0 of 7 below 0.45 moved at all.  So:
  1. frac_exact DESCENDING (nodes with no measurement sort with the >= 0.45 band, not ahead of it);
  2. level ascending  -- an L1 kill takes its whole subtree with it (monotonicity, A124 Sec.4);
  3. |eta| ascending, then id for reproducibility.

Scope is `exall` (exact certified-maximal cores on EVERY box, pins and conditioned box): A135
measured expin NO-KILL / exall PASS on `k5_16_interior_Y0281_D03`, and exall is never weaker --
a larger core exempts more rows, so tau can only fall.  Every half-side is certified by A132's
exact rational vertex test inside exactcore before it is written (the frozen verifiers take `a`
verbatim, so soundness is the emitter's obligation).
"""
import argparse
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")


def jl(p):
    out = []
    if not os.path.exists(p):
        return out
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="exall")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "targets137.json"))
    ap.add_argument("--include_fail", type=int, default=0,
                    help="also queue FAIL rows (they own a configuration too); off by default -- "
                         "priority (a) is the ALIVE population")
    a = ap.parse_args()

    R = {}
    for p in sorted(glob.glob(os.path.join(A57, "results", "tree_*.jsonl"))):
        for r in jl(p):
            if "id" in r:
                R[r["id"]] = r
    dead = {r["id"] for r in jl(os.path.join(A57, "results",
                                             "superseded_by_backlog_A137.jsonl"))}
    dead |= {r["id"] for r in jl(os.path.join(A57, "results",
                                              "superseded_by_tight_core.jsonl"))}

    def ancestor_dead(nid):
        parts = nid.split("_D")
        for i in range(1, len(parts)):
            if "_D".join(parts[:i]) in dead:
                return True
        return nid in dead

    # A145's predictor, keyed by node id
    FR = {}
    for r in jl(os.path.join(ROOT, "A145-impossible-weight", "results",
                             "impossible_weight.jsonl")):
        if r.get("camp") == "A57" and r.get("frac_exact") is not None:
            FR[r["id"]] = float(r["frac_exact"])

    T = []
    for nid, r in R.items():
        cert = r.get("cert") or ""
        want = cert.startswith("ALIVE") or (a.include_fail and cert.startswith("FAIL"))
        if not want or not r.get("box"):
            continue
        if ancestor_dead(nid):
            continue
        eta = r.get("eta")
        T.append(dict(id=nid, box=r["box"], budget=r.get("budget", 5), scope=a.scope,
                      level=1 + nid.count("_D"), eta=eta, tau=r.get("tau"),
                      frac_exact=FR.get(nid), prior=cert[:40],
                      cls=nid.split("_interior")[0]))
    # unmeasured nodes sort at 0.45 -- the top of the band A145 measured as never moving, so they
    # queue behind every measured >= 0.45 node and ahead of the measured dead weight below it
    T.sort(key=lambda j: (-(j["frac_exact"] if j["frac_exact"] is not None else 0.45),
                          j["level"], abs(j["eta"]) if j["eta"] is not None else 9e9, j["id"]))
    json.dump(T, open(a.out, "w"), indent=0)
    import collections
    c = collections.Counter((j["level"], j["cls"]) for j in T)
    print(f"{len(T)} targets -> {a.out}")
    for k in sorted(c):
        print("   L%d %s: %d" % (k[0], k[1], c[k]))


if __name__ == "__main__":
    main()
