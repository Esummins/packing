"""A156 -- the A57 state table in PAUSED.md v3 §B's columns, so v3 -> v4 is a like-for-like diff.

Per tree: rows, ALIVE, FAIL, PASS, logic kill, work-owing (ALIVE + FAIL) and how many of those are
now dead through a fold-in ledger (their own id or an ancestor's).  Verdict is read from `cert`,
exactly as A137's `state137.py` reads it; where the corpus holds more than one row for an id (the
sharded and unsharded D2 files overlap, and 26 pairs disagree), the STRONGEST verdict wins --
PASS/logic kill over ALIVE/FAIL -- because a FAIL is the absence of a proof and a PASS is a proof.

    python code\\state156.py            # table
    python code\\state156.py --json
"""
import argparse
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")

RANK = {"PASS": 0, "logic kill": 1, "parent box": 2, "CANARY": 3, "skipped": 4, "ALIVE": 5,
        "FAIL": 6, "other": 7}


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
    c = str(rec.get("cert") or "")
    for pre, name in (("PASS", "PASS"), ("KILL-BY-LOGIC", "logic kill"), ("ALIVE", "ALIVE"),
                      ("FAIL", "FAIL"), ("UNSOUND", "parent box"), ("CANARY", "CANARY"),
                      ("SKIPPED", "skipped")):
        if c.startswith(pre):
            return name
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    trees = collections.defaultdict(dict)
    for p in sorted(glob.glob(os.path.join(A57, "results", "tree_*.jsonl"))):
        key = os.path.basename(p)[5:].rsplit("_s", 1)[0].replace(".jsonl", "")
        for r in jl(p):
            if "id" not in r:
                continue
            v = verdict(r)
            cur = trees[key].get(r["id"])
            if cur is None or RANK[v] < RANK[cur[0]]:
                trees[key][r["id"]] = (v, r)

    dead = set()
    for f in glob.glob(os.path.join(A57, "results", "superseded_by_*.jsonl")):
        for r in jl(f):
            if "id" in r:
                dead.add(r["id"])

    def anc_dead(nid):
        parts = nid.split("_D")
        return nid in dead or any("_D".join(parts[:i]) in dead for i in range(1, len(parts)))

    rows, tot = [], collections.Counter()
    for key in sorted(trees):
        c = collections.Counter(v for v, _ in trees[key].values())
        owing = [nid for nid, (v, _) in trees[key].items() if v in ("ALIVE", "FAIL")]
        nowdead = [nid for nid in owing if anc_dead(nid)]
        rows.append(dict(tree=key, n=len(trees[key]), ALIVE=c["ALIVE"], FAIL=c["FAIL"],
                         PASS=c["PASS"], logic_kill=c["logic kill"], work_owing=len(owing),
                         now_dead=len(nowdead)))
        for k in ("ALIVE", "FAIL", "PASS"):
            tot[k] += c[k]
        tot["logic_kill"] += c["logic kill"]
        tot["n"] += len(trees[key])
        tot["work_owing"] += len(owing)
        tot["now_dead"] += len(nowdead)
    out = dict(rows=rows, total=dict(tot),
               open_work=tot["work_owing"] - tot["now_dead"])
    if a.json:
        print(json.dumps(out, indent=1))
        return
    print(f"{'tree':34s} {'n':>6} {'ALIVE':>6} {'FAIL':>5} {'PASS':>6} {'logic':>6} "
          f"{'owing':>6} {'nowdead':>8}")
    for r in rows:
        print(f"{r['tree']:34s} {r['n']:6d} {r['ALIVE']:6d} {r['FAIL']:5d} {r['PASS']:6d} "
              f"{r['logic_kill']:6d} {r['work_owing']:6d} {r['now_dead']:8d}")
    print(f"{'TOTAL':34s} {tot['n']:6d} {tot['ALIVE']:6d} {tot['FAIL']:5d} {tot['PASS']:6d} "
          f"{tot['logic_kill']:6d} {tot['work_owing']:6d} {tot['now_dead']:8d}")
    print(f"  -> open work (work-owing minus those a ledger already kills): {out['open_work']}")


if __name__ == "__main__":
    main()
