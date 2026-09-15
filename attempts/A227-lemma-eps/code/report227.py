"""A227 -- write results/eps227.md from the replay (eps227.jsonl: every A211 g1 node with a near-simple candidate put
through Rule EPS) and the live runs (results/certs_on/coarsetree211_<nid>.json, the patched engine with A227_EPS=1),
compared with A211's own certificate of the same page.  Idempotent; re-run at any time, including mid-chain.

    python report227.py [--out ../results/eps227.md]
"""
import argparse
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211CERTS = os.path.join(ROOT, "attempts", "A211-coarse-tree", "certs")


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:                              # noqa: BLE001
                    pass
    return out


def scan_section(rows):
    pages = sorted({r["nid"] for r in rows})
    kills = [r for r in rows if r.get("verdict") == "DEAD"]
    lost = [r for r in rows if r.get("verdict") != "DEAD" and any(c["struck"] for c in r["cands"])]
    surv, reach, anon, pairs, struck_ct = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    n_c = 0
    for r in rows:
        for c in r["cands"]:
            n_c += 1
            pairs[(c["role"], c["slot"])] += 1
            surv[tuple(sorted(c["survivors"]))] += 1
            for m, d in c["survivors"].items():
                reach[(m, (d.get("reach") or "?").split("-")[0] + ("-" + (d.get("reach") or "").split("-")[-1] if d.get("reach") else ""))] += 1
            a = c.get("anon_cells")
            anon["no claim" if a is None else ("none" if a == [] else "some")] += 1
            struck_ct[len(c["struck"])] += 1
    L = ["## 1. The offline replay -- Rule EPS over every recorded A211 g1 node (`results/eps227.jsonl`)", "",
         "`epsscan227.py ALL --run g1_page` puts each node's recorded pose set (padded outward, as `snapscan224`) through the",
         "rule; a row per node with at least one near-simple (role, forced cell) candidate (A224's filter).", "",
         "| measure | value |", "|---|---|",
         "| pages with a candidate node | %d |" % len(pages),
         "| nodes with a candidate | %d |" % len(rows),
         "| candidate (role, slot) evaluations | %d |" % n_c,
         "| **nodes DEAD by FC+EPS** | **%d** |" % len(kills),
         "| nodes where a candidate lost >= 1 meeter without dying | %d |" % len(lost),
         "| candidates by number of roles struck | %s |" % ", ".join("%d struck: %d" % (k, v) for k, v in sorted(struck_ct.items())),
         "| anonymous clause (per candidate) | %s |" % ", ".join("%s: %d" % (k, v) for k, v in sorted(anon.items())),
         "| replay seconds (sum) | %.1f |" % sum(r.get("seconds") or 0 for r in rows), ""]
    L += ["**Survivor sets** (the roles that can still reach a wedge target, per candidate):", ""]
    L += ["| survivors | candidates |", "|---|---|"]
    L += ["| %s | %d |" % (", ".join(k) if k else "(none -- DEAD)", v) for k, v in surv.most_common(12)]
    L += ["", "**Which target the survivor reaches** (role, first reachable target family):", "", "| role | target | count |", "|---|---|---|"]
    L += ["| %s | %s | %d |" % (k[0], k[1], v) for k, v in reach.most_common(14)]
    if kills:
        L += ["", "**Kills:**", ""]
        for r in kills[:40]:
            k = r["kill"]
            L.append("- `%s` `%s` d%s (recorded %s%s): %s at %s; struck %s" % (
                r["nid"], r["label"], r["depth"], r.get("verdict_recorded"), "/" + str(r.get("clip_recorded")) if r.get("clip_recorded") else "",
                k["role"], k["slot"], ", ".join(k["struck"])))
    return L


def live_section():
    L = ["", "## 2. The live wiring -- run211 with `integration227.diff` applied (patched copies), `A227_EPS=1`, isolated cert dir", "",
         "| page | run | live verdict | live s | live nodes | FC+EPS kills | EPS evals / s | A211 verdict | A211 s | A211 nodes |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(glob.glob(os.path.join(RES, "certs_on", "coarsetree211_*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        nid = d["nid"]
        ref = os.path.join(A211CERTS, "coarsetree211_%s.json" % nid)
        rd = json.load(open(ref, encoding="utf-8")) if os.path.exists(ref) else {}
        for run, r in sorted((d.get("runs") or {}).items()):
            ns = r.get("nodes") or []
            kills = [n for n in ns if n.get("clip") == "FC+EPS"]
            ev = [n.get("eps") for n in ns if n.get("eps")]
            rr = ((rd.get("runs") or {}).get(run) or {})
            L.append("| %s | %s | %s | %s | %d | %d | %d / %.1f | %s | %s | %d |" % (
                nid, run, r.get("verdict"), r.get("seconds"), len(ns), len(kills), len(ev), sum(e.get("seconds") or 0 for e in ev),
                rr.get("verdict"), rr.get("seconds"), len(rr.get("nodes") or [])))
    if len(L) == 5:
        L.append("| (no live run finished yet) | | | | | | | | | |")
    return L


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "eps227.md"))
    a = ap.parse_args()
    rows = jl(os.path.join(RES, "eps227.jsonl"))
    L = ["# A227 -- Rule EPS: what it measures (generated by `code/report227.py`)", "",
         "Proof object `docs/proofs/lemma_eps.md`; code `code/eps227.py`; the wiring `code/integration227.diff`.  Resume block:",
         "`bash attempts/A227-lemma-eps/code/bench227.sh` (phase stamps in `logs/done/`, the scan resumes from its jsonl).", ""]
    L += scan_section(rows) + live_section()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", a.out, "(%d scan rows)" % len(rows))
