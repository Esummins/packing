"""A137 -- the state table: where A57 stood at 22:42, what the fold-in killed, what tonight's
emission added, and what is open at the pause.

The corpus is split into rows that existed BEFORE tonight and rows A137 emitted (they carry
`emitter`/`emitted_by` = A137 or a `synced` stamp), so the fold-in's effect is measured against
the state it was actually applied to and tonight's fresh children are never double-counted.
"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def verdict(rec):
    c = rec.get("cert") or ""
    for pre, name in (("PASS", "PASS"), ("KILL-BY-LOGIC", "logic kill"), ("ALIVE", "ALIVE"),
                      ("FAIL", "FAIL"), ("UNSOUND", "parent box"), ("CANARY", "CANARY"),
                      ("SKIPPED", "skipped")):
        if c.startswith(pre):
            return name
    return "other"


def mine(rec):
    return str(rec.get("emitter", "")).startswith("A137") or rec.get("emitted_by") == "A137"


def main():
    old, new = collections.defaultdict(dict), collections.defaultdict(dict)
    for p in sorted(glob.glob(os.path.join(A57, "results", "tree_*.jsonl"))):
        key = os.path.basename(p)[5:].rsplit("_s", 1)[0].replace(".jsonl", "")
        for r in jl(p):
            if "id" not in r:
                continue
            (new if mine(r) else old)[key][r["id"]] = r

    dead = {}
    for f, tag in (("superseded_by_backlog_A137.jsonl", "fold-in"),
                   ("superseded_by_exactcore_A137.jsonl", "exact-core re-emission")):
        for r in jl(os.path.join(A57, "results", f)):
            dead.setdefault(r["id"], []).append((tag, r.get("leaf") or r.get("superseded_by"),
                                                 r.get("source", "")))

    def anc_dead(nid):
        parts = nid.split("_D")
        return any("_D".join(parts[:i]) in dead for i in range(1, len(parts))) or nid in dead

    print("=" * 78)
    print("A57 state BEFORE tonight (rows that existed at 22:42), by tree")
    print("=" * 78)
    tot = collections.Counter()
    for key in sorted(old):
        c = collections.Counter(verdict(r) for r in old[key].values())
        openrows = sum(1 for nid, r in old[key].items()
                       if verdict(r) in ("ALIVE", "FAIL"))
        killed = sum(1 for nid, r in old[key].items()
                     if verdict(r) in ("ALIVE", "FAIL") and anc_dead(nid))
        print(f"{key:32s} n={len(old[key]):5d}  " +
              "  ".join(f"{k} {v}" for k, v in sorted(c.items())) +
              f"   || work-owing {openrows}, of which now DEAD {killed}")
        tot.update(c)
        tot["work_owing"] += openrows
        tot["work_owing_now_dead"] += killed
    print(f"{'TOTAL':32s} " + "  ".join(f"{k} {v}" for k, v in sorted(tot.items())))
    print(f"  -> work-owing before: {tot['work_owing']}, killed by tonight's fold-in and "
          f"re-emission: {tot['work_owing_now_dead']}, "
          f"REMAINING: {tot['work_owing'] - tot['work_owing_now_dead']}")

    print()
    print("=" * 78)
    print("Rows A137 EMITTED tonight (fresh children through the hooks), by tree and level")
    print("=" * 78)
    lv = collections.Counter()
    for key in sorted(new):
        c = collections.Counter(verdict(r) for r in new[key].values())
        print(f"{key:32s} n={len(new[key]):5d}  " +
              "  ".join(f"{k} {v}" for k, v in sorted(c.items())))
        for nid, r in new[key].items():
            lv[(1 + nid.count("_D"), verdict(r))] += 1
    print("  by level:")
    for k in sorted(lv):
        print(f"    L{k[0]}  {k[1]:12s} {lv[k]}")

    print()
    print("=" * 78)
    print("Kills folded in tonight, by source and leaf")
    print("=" * 78)
    src = collections.Counter()
    leaf = collections.Counter()
    for nid, entries in dead.items():
        for (tag, lf, s) in entries[:1]:
            src[s.split("/")[0] or tag] += 1
            leaf[(lf or "?")[:52]] += 1
    for k, v in sorted(src.items(), key=lambda x: -x[1]):
        print(f"    {k:44s} {v}")
    print("  by leaf:")
    for k, v in sorted(leaf.items(), key=lambda x: -x[1]):
        print(f"    {k:54s} {v}")


if __name__ == "__main__":
    main()
