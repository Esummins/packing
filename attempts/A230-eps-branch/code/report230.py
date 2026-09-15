"""A230 -- write results/bench230.md from the re-scan (eps230.jsonl) and the two live runs (results/certs_*/...).
Idempotent; re-run at any time, including mid-chain.        python report230.py [--out ../results/bench230.md]
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
A227 = os.path.abspath(os.path.join(HERE, "..", "..", "A227-lemma-eps", "results", "eps227.jsonl"))


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


def scan_section(rows, old):
    pages = sorted({r["nid"] for r in rows})
    kills = [r for r in rows if r.get("verdict") == "DEAD"]
    wns = [r for r in rows if r.get("wedge_ns")]
    lost = [r for r in rows if r.get("verdict") != "DEAD" and any(c["struck"] for c in r["cands"])]
    surv, struck_ct, anon, added_sets = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    n_c = n_add = 0
    for r in rows:
        for c in r["cands"]:
            n_c += 1
            n_add += 1 if c.get("only_new") else 0
            surv[tuple(sorted(c["survivors"]))] += 1
            struck_ct[len(c["struck"])] += 1
            a = c.get("anon_cells")
            anon["no claim" if a is None else ("none" if a == [] else "some")] += 1
            if c.get("only_new"):
                added_sets[(c["role"], tuple(sorted(c["survivors"])))] += 1
    o_nodes, o_c = len(old), sum(len(r.get("cands") or []) for r in old)
    L = ["## 1. The re-scan -- Rule EPS with ALL candidates + the taper (`results/eps230.jsonl`)", "",
         "`epsscan230.py ALL --run g1_page` replays every recorded A211 g1 node (its snapshot padded outward, as",
         "`snapscan224` does).  A230's candidate test takes the role's position BOX (A224 took its centre) and asks",
         "only that SOME piece's tilt bin be near-aligned (A224 asked for every piece), so a role near-simple in",
         "either of two cells is evaluated in both; all candidates are evaluated, smallest box first.", "",
         "| measure | A227 | A230 |", "|---|---|---|",
         "| pages with a candidate node | %s | %d |" % (len({r["nid"] for r in old}) or "-", len(pages)),
         "| nodes with a candidate | %d | %d |" % (o_nodes, len(rows)),
         "| candidate (role, slot) evaluations | %d | %d |" % (o_c, n_c),
         "| candidates per node | %.2f | %.2f |" % (o_c / max(1, o_nodes), n_c / max(1, len(rows))),
         "| ... of which ONLY A230's wider test returns | - | %d |" % n_add,
         "| **nodes DEAD by FC+EPS** | **%d** | **%d** |" % (sum(1 for r in old if r.get("verdict") == "DEAD"), len(kills)),
         "| nodes with an NS-at-wedge split (one blocker, anon certified empty) | - | %d |" % len(wns),
         "| nodes where a candidate lost >= 1 meeter without dying | %d | %d |" % (
             sum(1 for r in old if r.get("verdict") != "DEAD" and any(c["struck"] for c in r["cands"])), len(lost)),
         "| strikes the POLYGON taper added (the bbox test failed, the polygon separated) | - | %d |" % sum(
             (r.get("taper") or {}).get("strikes") or 0 for r in rows),
         "| wedge targets carrying an exact polygon | - | %d |" % sum((r.get("taper") or {}).get("targets") or 0 for r in rows),
         "| candidates by number of roles struck | %s | %s |" % (
             ", ".join("%d: %d" % (k, v) for k, v in sorted(collections.Counter(
                 len(c["struck"]) for r in old for c in r["cands"]).items())),
             ", ".join("%d: %d" % (k, v) for k, v in sorted(struck_ct.items()))),
         "| anonymous clause (per candidate) | %s | %s |" % (
             ", ".join("%s: %d" % (k, v) for k, v in sorted(collections.Counter(
                 ("no claim" if c.get("anon_cells") is None else ("none" if c.get("anon_cells") == [] else "some"))
                 for r in old for c in r["cands"]).items())),
             ", ".join("%s: %d" % (k, v) for k, v in sorted(anon.items()))),
         "| replay seconds (sum) | %.1f | %.1f |" % (sum(r.get("seconds") or 0 for r in old),
                                                     sum(r.get("seconds") or 0 for r in rows)), ""]
    L += ["**Survivor sets** (the roles that can still reach a wedge target, per candidate):", "",
          "| survivors | candidates |", "|---|---|"]
    L += ["| %s | %d |" % (", ".join(k) if k else "(none -- DEAD)", v) for k, v in surv.most_common(14)]
    if added_sets:
        L += ["", "**What the wider candidate test added** (role, survivor set):", "", "| role | survivors | candidates |", "|---|---|---|"]
        L += ["| %s | %s | %d |" % (k[0], ", ".join(k[1]) or "(none -- DEAD)", v) for k, v in added_sets.most_common(14)]
    if kills:
        L += ["", "**Kills:**", ""]
        for r in kills[:40]:
            k = r["kill"]
            L.append("- `%s` `%s` d%s (recorded %s): %s at %s; struck %s" % (
                r["nid"], r["label"], r["depth"], r.get("verdict_recorded"), k["role"], k["slot"], ", ".join(k["struck"])))
    if wns:
        L += ["", "**NS-at-wedge splits** (the surviving blocker, the near-simple role and its cell, the targets):", "",
              "| page | node | blocker | near-simple | slot | targets |", "|---|---|---|---|---|---|"]
        for r in wns[:30]:
            w = r["wedge_ns"]
            L.append("| %s | `%s` | %s | %s | %s | %s |" % (r["nid"], r["label"], w["role"], w["F"], w["slot"],
                                                            ", ".join(t[0] for t in w["targets"])))
    return L


def live_section():
    L = ["", "## 2. The live benchmark -- run211 on Y0865 g1 from its A203 root (`--no-inherit`), isolated cert dirs", "",
         "Flag set: the pass-6 set `A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1` (OFF) vs the same + `A230_EPS=1` (ON).", "",
         "| page | run | flags | verdict | s | nodes | dead leaves | FC+EPS kills | NS-at-wedge splits / kills | EPS evals / s | first kill s |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for tag in ("off", "on"):
        for f in sorted(glob.glob(os.path.join(RES, "certs_%s" % tag, "coarsetree211_*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            for run, r in sorted((d.get("runs") or {}).items()):
                ns = r.get("nodes") or []
                kills = [n for n in ns if n.get("clip") == "FC+EPS"]
                wk = [n for n in ns if str(n.get("kind") or "").startswith("epsns-")]
                ev = [n.get("eps") for n in ns if n.get("eps")]
                L.append("| %s | %s | %s | %s | %s | %d | %d | %d | %d / %d | %d / %.1f | %s |" % (
                    d["nid"], run, tag, r.get("verdict"), r.get("seconds"), len(ns),
                    sum(1 for n in ns if n.get("verdict") == "DEAD"), len(kills),
                    r.get("eps_ns_splits") or 0, sum(1 for n in wk if n.get("verdict") == "DEAD"),
                    len(ev), sum(e.get("seconds") or 0 for e in ev), r.get("eps_first")))
    if len(L) == 6:
        L.append("| (no live run finished yet) | | | | | | | | | | |")
    return L


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "bench230.md"))
    a = ap.parse_args()
    rows, old = jl(os.path.join(RES, "eps230.jsonl")), jl(A227)
    L = ["# A230 -- Rule EPS: all candidates, the polygon taper, the NS-at-wedge branch (generated by `code/report230.py`)", "",
         "Proof object `docs/proofs/lemma_eps.md` (s.7 [C]1 and [C]3 are what A230 discharges); code `code/eps230.py`",
         "(candidates + the polygon strike) and `code/epsns230.py` (the verdict over all candidates + the split);",
         "the wiring is in `attempts/A211-coarse-tree/code/{tree211,leaves211}.py` behind `A230_EPS` (default OFF).",
         "Resume block: `bash attempts/A230-eps-branch/code/bench230.sh` (phase stamps in `logs/done/`, the re-scan",
         "resumes from its jsonl).  Notes: `notes/eps230.md`.", ""]
    L += scan_section(rows, old) + live_section()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", a.out, "(%d scan rows, %d A227 rows)" % (len(rows), len(old)))
