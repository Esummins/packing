"""A156 -- the deepen lane: split the ALIVE level-2/3 nodes and screen the children through the
deployed geometric hooks, exactly as PAUSED.md v3 §E's resume order asks.

Parents are the nodes that are ALIVE *after an LP verdict* at level >= 2 and whose ancestors are
not dead:
  * A57's canonical corpus (`tree_*.jsonl`), rows whose `cert` starts with ALIVE, minus every id
    (or ancestor of an id) in the fold-in ledgers `superseded_by_*.jsonl`;
  * plus, as the day's own LP drains, level-2/3 rows this attempt recorded `NO-KILL`
    (= ALIVE at the LP) -- their box is the CLIPPED box the LP actually ran on.

The children are emitted by A137's `emit137.py --mode deepen`, run as a subprocess and
**unmodified**: pinguard at the exact pin cores (T5/T5'), trim57 (T5''), pinclip at the same exact
core (T5'''), the polygon-vs-pin-core kill (T5''''), then the survivors to the LP queue.  Its
outputs land in A137's results directory (its BASE is fixed); this driver MOVES them into A156's
own results, so the day's rows are this attempt's and `mkqueue156.py` picks them up.

    python code\\deepen156.py --list                 # what the parent population is
    python code\\deepen156.py --key k5_11_interior_G1_D2 --name k5_11 --levels 3
"""
import argparse
import collections
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A137 = os.path.join(ROOT, "A137-night-shift-2")
EMIT137 = os.path.join(A137, "code", "emit137.py")


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def dead_ids():
    d = set()
    for f in glob.glob(os.path.join(A57, "results", "superseded_by_*.jsonl")):
        for r in jl(f):
            if "id" in r:
                d.add(r["id"])
    return d


def anc_dead(nid, dead):
    parts = nid.split("_D")
    return nid in dead or any("_D".join(parts[:i]) in dead for i in range(1, len(parts)))


def parents(min_level=2, max_level=3):
    """(key -> [parent records]) for every ALIVE level-2/3 node with no dead ancestor."""
    dead = dead_ids()
    out = collections.defaultdict(dict)
    # The corpus carries the same id in a sharded and an unsharded file (e.g.
    # tree_k5_11_interior_G1_D2.jsonl and ..._D2_s0.jsonl), and 26 of those pairs DISAGREE: a
    # later run's PASS next to an earlier FAIL.  That is not unsound -- a FAIL is the absence of a
    # proof, a PASS is a proof -- but a last-wins read would deepen a node that is already
    # certified dead.  So a node counts as ALIVE only if SOME row says ALIVE and NO row says PASS
    # or KILL-BY-LOGIC.
    certs = collections.defaultdict(set)
    rowof = {}
    for p in sorted(glob.glob(os.path.join(A57, "results", "tree_*.jsonl"))):
        key = os.path.basename(p)[5:].rsplit("_s", 1)[0].replace(".jsonl", "")
        for r in jl(p):
            nid = r.get("id")
            if not nid:
                continue
            certs[nid].add(str(r.get("cert") or ""))
            if str(r.get("cert") or "").startswith("ALIVE") and r.get("box"):
                rowof[nid] = (key, r)
    for nid, (key, r) in rowof.items():
        cs = certs[nid]
        if any(c.startswith(("PASS", "KILL-BY-LOGIC", "UNSOUND")) for c in cs):
            continue
        lv = 1 + nid.count("_D")
        if not (min_level <= lv <= max_level) or anc_dead(nid, dead):
            continue
        out[key][nid] = dict(id=nid, box=r["box"], budget=r.get("budget"), level=lv,
                             src="A57 corpus")
    # the day's own ALIVE-at-LP level-2/3 rows (their box is the clipped one the LP ran on)
    qgeo = {}
    for qp in glob.glob(os.path.join(A137, "results", "emitq_*.json")) + \
            glob.glob(os.path.join(BASE, "results", "emitq_*.json")):
        try:
            for j in json.load(open(qp)):
                qgeo[j["id"]] = j
        except Exception:
            pass
    for lp in glob.glob(os.path.join(BASE, "results", "lp156_*.jsonl")) + \
            glob.glob(os.path.join(A137, "results", "emit_lp_*.jsonl")):
        for r in jl(lp):
            if r.get("result") != "NO-KILL":
                continue
            nid = r.get("id")
            lv = 1 + nid.count("_D")
            if not (min_level <= lv <= max_level) or anc_dead(nid, dead):
                continue
            j = qgeo.get(nid)
            if not j:
                continue
            key = ("k5_11_interior_G1" if nid.startswith("k5_11") else "k5_16_interior_G1") + \
                  "_D" * 0
            key = key + ("_D2" * (lv - 1))
            out[key][nid] = dict(id=nid, box=j["box"], budget=j.get("budget"), level=lv,
                                 src="A156 LP (ALIVE at LP today)")
    return {k: list(v.values()) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--key", default=None, help="parent key, e.g. k5_11_interior_G1_D2")
    ap.add_argument("--name", default=None, help="class: k5_11 or k5_16")
    ap.add_argument("--levels", type=int, default=3)
    ap.add_argument("--nsub", type=int, default=1)
    ap.add_argument("--max_parents", type=int, default=10 ** 6)
    a = ap.parse_args()

    P = parents()
    if a.list or not a.key:
        for k, v in sorted(P.items()):
            c = collections.Counter(x["level"] for x in v)
            print(f"{k:34s} {len(v):4d} parents  levels " + dict(c).__repr__())
        print("total parents:", sum(len(v) for v in P.values()))
        return

    rows = P.get(a.key) or []
    if not rows:
        print(f"no ALIVE parents under key {a.key}")
        return
    rows = rows[:a.max_parents]
    name = a.name or ("k5_11" if rows[0]["id"].startswith("k5_11") else "k5_16")
    tag0 = a.key + "_D2"
    clash = [p for p in (os.path.join(A137, "results", f"emit_geo_{tag0}.jsonl"),
                         os.path.join(A137, "results", f"emitq_{tag0}.json")) if os.path.exists(p)]
    if clash:
        print("REFUSED: emit137 would append to A137's own night files " + json.dumps(clash) +
              " -- pick a key whose _D2 tag is unused (A156 never rewrites another chore's rows)")
        sys.exit(2)
    pf = os.path.join(BASE, "results", f"parents156_{a.key}.json")
    json.dump(rows, open(pf, "w"), indent=0)
    print(f"{len(rows)} parents -> {pf}")

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[k] = "1"
    cmd = [sys.executable, EMIT137, "--mode", "deepen", "--name", name, "--key", a.key,
           "--parents", pf, "--levels", str(a.levels), "--nsub", str(a.nsub),
           "--max_parents", str(a.max_parents)]
    print("running: " + " ".join(cmd), flush=True)
    t0 = time.time()
    p = subprocess.run(cmd, env=env, cwd=A137)
    print(f"emit137 rc={p.returncode} in {round(time.time() - t0, 1)} s", flush=True)
    if p.returncode != 0:
        sys.exit(p.returncode)

    tag = a.key + "_D2"
    moved = []
    for src, dst in ((os.path.join(A137, "results", f"emit_geo_{tag}.jsonl"),
                      os.path.join(BASE, "results", f"emit_geo_{tag}.jsonl")),
                     (os.path.join(A137, "results", f"emitq_{tag}.json"),
                      os.path.join(BASE, "results", f"emitq_{tag}.json"))):
        if os.path.exists(src):
            shutil.move(src, dst)
            moved.append(dst)
    print("moved into A156: " + json.dumps(moved))


if __name__ == "__main__":
    main()
