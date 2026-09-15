"""A224 -- write results/bench224.md from the benchmark's two outputs: the OFFLINE scan (snapscan224.jsonl, every
A211 page's recorded nodes put through Rule SNAP) and the LIVE A/B rows (bench224.jsonl, run211 with the flag ON and
OFF on the brief's five pages, isolated cert dirs).  Idempotent: re-run at any time, including mid-benchmark.

    python report224.py [--out ../results/bench224.md]
"""
import argparse
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))


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
    hand = [r for r in rows if r.get("verdict") == "HANDOFF"]
    blk = collections.Counter()
    pairs = collections.Counter()
    for r in rows:
        for c in r.get("cands") or []:
            pairs[(c["role"], c["slot"])] += 1
            blk[tuple(c.get("blockers") or ()) if c.get("anon") else ("(clause b)",)] += 1
    L = ["## 1. The offline scan -- Rule SNAP over every recorded A211 node (`results/snapscan224.jsonl`)", "",
         "`snapscan224.py ALL --run g1_page` replays the rule on the pose set each node actually had (its recorded",
         "snapshot, padded outward), so it measures where SNAP WOULD fire without spending any search.", "",
         "| measure | value |", "|---|---|",
         "| pages with a candidate | %d |" % len(pages),
         "| nodes with a SNAP candidate | %d |" % len(rows),
         "| SNAP / SNAP-DIAG kills | **%d** |" % len(kills),
         "| hand-offs (snapped into an open stratum) | %d |" % len(hand), ""]
    if pairs:
        L += ["Most frequent (role, slot) candidates: " +
              ", ".join("%s@%s x%d" % (r, s, n) for (r, s), n in pairs.most_common(8)) + ".", ""]
    if blk:
        L += ["Why a candidate does not fire (blocker set, `(clause b)` = an anonymous square could still meet the cell):",
              "", "| blocking roles | candidates |", "|---|---|"]
        L += ["| %s | %d |" % (", ".join(k) if k else "**none -- SNAP fires**", v) for k, v in blk.most_common(10)]
        L += [""]
    if kills:
        L += ["Kills:", "", "| page | node | depth | recorded verdict | snap | target stratum |", "|---|---|---|---|---|---|"]
        for r in kills[:40]:
            L.append("| %s | %s | %s | %s %s | %s | %s |" % (
                r["nid"], r["label"], r.get("depth"), r.get("verdict_recorded"), r.get("clip_recorded") or "",
                ", ".join("%s:=%s" % (c["role"], c["slot"]) for c in r["snapped"]), (r.get("target") or {}).get("stratum")))
        L += [""]
    return L


def live_section(rows):
    by = collections.OrderedDict()
    for r in rows:
        if r.get("mode") != "page":
            continue
        mode = "ON" if "certs_on" in str(r.get("cert") or "") else ("OFF" if "certs_off" in str(r.get("cert") or "") else "?")
        by[(r.get("nid"), mode)] = r
    L = ["## 2. The live A/B -- run211 with the flag ON and OFF (`results/bench224.jsonl`)", "",
         "Same wall, same pads (g1), same inheritance, isolated cert dirs, `--no-fig`.  With `A224_SNAP` unset the",
         "engine is byte-for-byte the pass-5 engine; the OFF column is the control.", "",
         "| page | flag | verdict | nodes | dead leaves | alive | SNAP eval / cand / kill / hand-off / partial | SNAP s | first SNAP kill | run s |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for (nid, mode), r in by.items():
        s = r.get("snap") or {}
        L.append("| %s | %s | %s | %s | %s | %s | %s / %s / **%s** / %s / %s | %s | %s | %s |" % (
            nid, mode, r.get("verdict"), r.get("n_nodes"), r.get("dead_leaves"), r.get("alive_leaves"),
            s.get("runs"), s.get("cands"), s.get("kills"), s.get("handoffs"), s.get("partial"),
            s.get("seconds"), s.get("first_kill_t"), r.get("seconds")))
    L += [""]
    dis = [nid for (nid, m) in by if m == "ON" and (nid, "OFF") in by
           and by[(nid, "ON")].get("verdict") != by[(nid, "OFF")].get("verdict")]
    L += ["**Verdict agreement:** " + ("every paired run agrees." if not dis else "DISAGREE on %s -- investigate." % dis), ""]
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "bench224.md"))
    a = ap.parse_args()
    scan = jl(os.path.join(RES, "snapscan224.jsonl"))
    live = jl(os.path.join(RES, "bench224.jsonl"))
    head = ["# A224 -- Rule SNAP: the benchmark", "",
            "Flag `A224_SNAP=1` (default OFF).  Rule SNAP is leaf rule (0) at a fully named leaf and a cheap test after",
            "the coarse round at every internal node; the rule, its soundness chain and its certificate are",
            "`docs/proofs/snap_rule.md` and `attempts/A224-snap-rule/code/snap224.py`.", ""]
    body = scan_section(scan) + live_section(live)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(head + body) + "\n")
    print("wrote %s (%d scan rows, %d live rows)" % (a.out, len(scan), len(live)))


if __name__ == "__main__":
    main()
