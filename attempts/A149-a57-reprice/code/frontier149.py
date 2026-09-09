"""A149 -- size the A57 side-1 (tag G1) frontier EXACTLY, id by id, with no double counting.

Why id by id.  The three obvious populations overlap badly:

  * A137's "893 fresh level-1 children" are 573 re-screens of ids already in the corpus and only
    276 genuinely new ones (the shard index changed between runs, so `emit137`'s `done` check --
    which reads one shard file -- did not see them);
  * 129 of the 454 cover children absent from the shard files are sitting in A137's LP queue,
    so counting "unemitted" and "queued" separately counts them twice;
  * 286 of the 415 queued level-1 jobs are re-solves of ids that ALREADY carry a verdict, and
    two thirds of those verdicts are PASS.

So the frontier is built as a set of ids, each with exactly ONE entry point:

  NEW      never screened, never recorded          -> pays the geometry screen, then E_L
  QUEUED   screened (geometry passed), LP not run   -> F_L
  ALIVE_D  recorded ALIVE, its 8 children already emitted (they are in QUEUED)
                                                    -> only the exact-core re-solve, if owed
  ALIVE_U  recorded ALIVE, children NOT emitted      -> 8 * E_{L+1}
  FAILN    recorded FAIL, not otherwise represented  -> F_L
  DEAD     PASS, logic kill, or superseded (itself or an ancestor) -> 0

Read-only.  `tree57.build_children` is imported UNCHANGED (the same call `emit137.py --mode l1`
makes: w=0.15 nth=8 cw=0.6 a_min=0.34 delta=1e-2 side=969271/250000).
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57R = os.path.join(ROOT, "A57-shadow-trees", "results")
A137R = os.path.join(ROOT, "A137-night-shift-2", "results")
sys.path.insert(0, os.path.join(ROOT, "A57-shadow-trees", "code"))
import tree57                                                              # noqa: E402

TREES = ("k5_11", "k5_16")
OUT = os.path.join(BASE, "results", "frontier149.json")


def lvl(i):
    return 1 + i.count("_D")


def cat(cert):
    c = cert or ""
    for pre, n in (("PASS", "PASS"), ("KILL-BY-LOGIC", "logic"), ("ALIVE", "ALIVE"),
                   ("FAIL", "FAIL"), ("UNSOUND", "parent"), ("CANARY", "CANARY"),
                   ("SKIPPED", "skipped")):
        if c.startswith(pre):
            return n
    return "other"


def main():
    # ---- recorded corpus (side 1 / G1 trees only; last verdict wins, but a DEAD verdict is
    #      absorbing: a node recorded PASS in one shard file and ALIVE in another is dead).
    rec, recdead = {}, set()
    for p in glob.glob(os.path.join(A57R, "tree_k5_1*_interior_G1*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            v = cat(r.get("cert"))
            rec[r["id"]] = v if r["id"] not in recdead else rec.get(r["id"], v)
            if v in ("PASS", "logic"):
                recdead.add(r["id"])
    for i in recdead:
        rec[i] = "PASS/logic"

    # ---- supersessions (a kill folded in from another attempt), ancestors included
    dead = set(recdead)
    for p in [os.path.join(A57R, f) for f in ("superseded_by_backlog_A137.jsonl",
                                              "superseded_by_exactcore_A137.jsonl")] + \
             [os.path.join(BASE, "results", f) for f in
              ("superseded_by_exactcore_A149.jsonl", "superseded_by_exactcore_v3_A149.jsonl")]:
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                try:
                    dead.add(json.loads(ln)["id"])
                except Exception:
                    pass

    def anc_dead(i):
        parts = i.split("_D")
        return i in dead or any("_D".join(parts[:k]) in dead for k in range(1, len(parts)))

    # ---- A137's emission: geometry-dead rows and the LP queue
    geo = set()
    for p in glob.glob(os.path.join(A137R, "emit_geo_*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            geo.add(json.loads(ln)["id"])
    queue = {}
    for p in glob.glob(os.path.join(A137R, "emitq_*.json")):
        for j in json.load(open(p)):
            queue[j["id"]] = j
    solved = set()
    for p in glob.glob(os.path.join(A137R, "emit_lp_*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            solved.add(json.loads(ln)["id"])
    # parents whose 8 children were emitted tonight
    deepened = {i.rsplit("_D", 1)[0] for i in (geo | set(queue)) if "_D" in i}
    # the exact-core re-emission lane's remaining targets
    tleft = {t["id"] for t in json.load(open(os.path.join(BASE, "results", "targets149.json")))}

    # ---- the level-1 cover, from the emitter itself
    cover = {}
    for name in TREES:
        kids, bad, _, _, _ = tree57.build_children(name, "interior", 0.15, 8, 0.6, 0.34, 1e-2,
                                                   side="969271/250000")
        if bad:
            raise SystemExit("FATAL: %d boxes with no rational core" % len(bad))
        cover[name] = [k["id"] for k in kids if k["kind"] == "YES"]

    # ---- classify every id that could owe work
    universe = set(rec) | geo | set(queue) | {i for v in cover.values() for i in v}
    klass = collections.Counter()
    detail = collections.defaultdict(collections.Counter)
    for i in sorted(universe):
        L = lvl(i)
        if anc_dead(i) or i in geo:
            k = "DEAD"
        elif i in queue and i not in solved:
            k = "QUEUED"
        elif rec.get(i) == "ALIVE":
            k = "ALIVE_D" if i in deepened else "ALIVE_U"
        elif rec.get(i) == "FAIL":
            k = "FAILD" if i in deepened else "FAILN"
        elif i not in rec:
            k = "NEW"
        else:
            k = "CLOSED"          # PASS/logic already absorbed, parent/canary/skipped
        klass[k] += 1
        detail[k][L] += 1
    owes_exactcore = len(tleft & {i for i in universe if not anc_dead(i)})
    # queued LP jobs that are already dead by a supersession of the node or an ancestor: work
    # A137's `mkqueue137.py` would still hand out, because it checks recorded ids, not ancestry
    orph = collections.Counter(lvl(i) for i in queue
                               if i not in solved and i not in geo and anc_dead(i))

    out = dict(
        counts={k: dict(total=v, by_level=dict(detail[k])) for k, v in sorted(klass.items())},
        cover_size={n: len(v) for n, v in cover.items()},
        recorded=len(rec), geo_dead=len(geo), queued=len(queue), solved=len(solved),
        deepened_parents=len(deepened), exactcore_targets_left=owes_exactcore,
        orphaned_queue=sum(orph.values()), orphaned_queue_by_level=dict(orph),
        note="side 1 (tag G1) only; DEAD absorbs PASS, logic kills and every supersession "
             "including inherited ones")
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
