"""A132 T2 -- the in-vitro nodes: axis arm vs polygon arm (and the polybox attribution arm).

Only a pair in which BOTH arms CONVERGED decides anything: in this column-generation scheme tau
rises as rows are added, so a below-budget tau on an unconverged run is the cap talking, not the
mathematics (A124: "CAP is never a verdict").  The table therefore reports convergence per arm and
counts only converged-vs-converged pairs as verdicts.
"""
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))


def main():
    R = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "invitro132_*.jsonl"))):
        if "superseded" in f:
            continue          # the aborted 30,000-warm-row run, kept for provenance only
        R += [json.loads(l) for l in open(f) if l.strip()]
    jobs = json.load(open(os.path.join(BASE, "results", "t2_jobs.json")))
    meta = {j["id"]: j for j in jobs}
    order = []
    for j in jobs:
        if j["id"] not in order:
            order.append(j["id"])

    # keep, per (node, arm), the run with the strongest evidence: converged first, then longest
    best = {}
    for r in R:
        if "tau" not in r:
            continue
        k = (r["id"], r["arm"])
        cur = best.get(k)
        score = (bool(r.get("converged")), r.get("wall_s", 0.0))
        if cur is None or score > (bool(cur.get("converged")), cur.get("wall_s", 0.0)):
            best[k] = r

    hdr = (f"{'node':30s} {'L':>2s} {'cls':>9s} {'w+':>5s} | {'tau_axis':>9s} {'c':>1s} "
           f"{'s':>5s} | {'tau_poly':>9s} {'c':>1s} {'s':>5s} | {'tau_pbox':>9s} {'c':>1s} | "
           f"{'verdict':<26s}")
    print(hdr)
    print("-" * len(hdr))
    verdicts = defaultdict(int)
    for nid in order:
        a = best.get((nid, "axis"))
        p = best.get((nid, "poly"))
        b = best.get((nid, "polybox"))
        m = meta[nid]
        if a is None and p is None:
            continue

        def f(r, key="tau"):
            return f"{r[key]:9.6f}" if r else " " * 9

        def c(r):
            return ("Y" if r.get("converged") else "n") if r else " "

        def w(r):
            return f"{r['wall_s']:5.0f}" if r else " " * 5
        if a and p and a.get("converged") and p.get("converged"):
            if p["tau"] < m["budget"] - 1e-6 <= a["tau"] + 1e-6:
                v = "LP-DEAD under K' (cert pend)"
                verdicts["kill"] += 1
            elif abs(p["tau"] - a["tau"]) < 1e-6:
                v = "no change"
                verdicts["nochange"] += 1
            else:
                v = f"tau moved {p['tau'] - a['tau']:+.3f}"
                verdicts["moved"] += 1
        elif m.get("t5poly"):
            v = "dead by T5-poly LOGIC"
            verdicts["logic"] += 1
        else:
            v = "no verdict (unconverged)"
            verdicts["undecided"] += 1
        print(f"{nid:30s} {m['level']:2d} {m['cls']:>9s} {m['w_poly_only']:5.2f} | "
              f"{f(a)} {c(a)} {w(a)} | {f(p)} {c(p)} {w(p)} | {f(b)} {c(b)} | {v:<26s}")
    print("-" * len(hdr))
    print("c = converged (Y/n); s = wall seconds; tau_pbox = polygon core on the CONDITIONED BOX "
          "only (pins keep K(a)) -- the attribution arm")
    print(f"\nverdicts over {len(order)} nodes: {dict(verdicts)}")
    dec = [nid for nid in order
           if best.get((nid, "axis"), {}).get("converged")
           and best.get((nid, "poly"), {}).get("converged")]
    kills = [nid for nid in dec if best[(nid, "poly")]["tau"] < meta[nid]["budget"] - 1e-6]
    print(f"pairs where BOTH arms converged: {len(dec)}  ->  LP-dead under the polygon core: "
          f"{len(kills)}  ({', '.join(kills)})")
    print("Every such kill is 'LP-dead under polygon core, CERTIFICATE PENDING': the frozen "
          "verifier knows only K(a).")
    print("\nattribution (polygon core on the conditioned box only):")
    for nid in kills:
        b = best.get((nid, "polybox"))
        if not b:
            continue
        if b.get("converged") and b["tau"] >= meta[nid]["budget"] - 1e-6:
            note = "kill NEEDS the pin polygon cores (box alone converges back to budget)"
        elif b.get("converged"):
            note = "the conditioned box ALONE suffices"
        else:
            note = "inconclusive (unconverged)"
        print(f"  {nid:30s} tau_pbox {b['tau']:.6f} conv={b.get('converged')} -> {note}")
    print(f"\ntotal in-vitro CPU: {sum(r.get('wall_s', 0.0) for r in R) / 3600.0:.2f} CPU-h "
          f"over {len(R)} solves")


if __name__ == "__main__":
    main()
