"""A142 T1 -- the surviving-alive population and the subtree-cost ranking.

POPULATION.  Start from A131's corpus (`attempts/A131-pin-clip/results/corpus131.jsonl`, the 1,744
open boxes of A96's 2,418-box corpus) and keep the WORK-OWING rows: the 414 ALIVE
("ALIVE-at-LP" + "ALIVE-at-LP at depth 2") and the 193 FAIL, 607 in all.  Then remove, in order,
with the overlaps printed:

    (a) A131's 132 pin-clip kills            results/backlog_kills.jsonl
    (b) A135's 64 polygon (T5-poly) kills    results/polycore_kills.jsonl  kind = T5-poly-logic
    (c) A135's 3 LP kills certified          results/polycore_kills.jsonl  kind = LP-certified
    (d) A124's 54 trim-empty ALIVE nodes     results/recheck124.jsonl      rows with
                                             `excluded_intervals` (the zero-LP trimsweep)
    (e) every DESCENDANT of any node killed by (a)-(d) or already recorded KILL-BY-LOGIC --
        monotonicity: a child's centre box is a sub-box of its parent's and its tilt bin a
        sub-interval, so every geometric exclusion is inherited (A124 notes/trim_empty_alive.md
        section 4, checked there on 24 of 24 level-4 children).  Descendant = id has the killer's
        id as a "<killer>_D.." prefix.

SUBTREE COST.  docs/budget.md section B gives the per-outcome cost of a node:
KILL-BY-LOGIC ~0 s, PASS ~850 s (LP 240-400 + exact verify 100 at s0 + 4-D window verify 545 at
level 2), FAIL ~900 s (LP + verify + resolver), ALIVE-at-LP 300 s of LP and then EIGHT children.
With p_K(L), p_L(L), p_A(L) the MEASURED per-level verdict shares of A57's own corpus, the
expected wall of a node emitted at level L and of everything under it is

    C(L) = p_K(L).0 + p_L(L).c_leaf + p_A(L).( c_LP + 8.C(L+1) ),      C(5) = 0

(the tree terminates at level 4: budget.md section A, "level-4 descent 0 of 30").  For a node that
is ALREADY emitted the LP it has paid is sunk, so its subtree cost is

    subtree(n) = residual(n) + SUM over still-open emitted descendants d of residual(d)
    residual(ALIVE at L with no still-open emitted child) = 8.C(L+1) . kept8(n)
    residual(ALIVE at L that already has still-open emitted children)   = 0
    residual(FAIL)                                                      = c_fail = 900 s

kept8(n) is A131's measured pin-clip kept VOLUME fraction at 8 tilt sub-bins: the fraction of the
node's box that survives exact pin geometry, i.e. the measured per-node alive fraction that
multiplies the 8^(levels remaining) of the crude model.  A node clipped to 12% of its box carries
12% of the modelled subtree.

    set PYTHONDONTWRITEBYTECODE=1 && python code/pop142.py
"""
import collections
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A60 = os.path.join(ATT, "A60-trump5-campaign")
A107 = os.path.join(ATT, "A107-shadow-gallery")
A118 = os.path.join(ATT, "A118-lane-count")
A124 = os.path.join(ATT, "A124-recheck-day")
A131 = os.path.join(ATT, "A131-pin-clip")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")

C_LEAF = 850.0
C_FAIL = 900.0
C_LP = 300.0
MAXLEVEL = 4

ALIVE_VERDICTS = ("ALIVE-at-LP", "ALIVE-at-LP at depth 2")


def jl(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def level_of(nid):
    return 1 + nid.count("_D")


# ------------------------------------------------------------------ A57's whole corpus
def a57_corpus():
    """A96's 2,418-box corpus, re-read here (A131 t1_check.corpus, re-implemented; read-only)."""
    out, seen = [], set()
    pats = ("tree_k5_1*_interior_G1_s*.jsonl", "tree_k5_1*_interior_G1_D2*.jsonl")
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(A57, "results", pat))):
            if "_s0.jsonl" in f and "_D2" in f:
                continue
            for r in jl(f):
                if not r.get("box") or r.get("id") in seen:
                    continue
                seen.add(r["id"])
                r["_name"] = "k5_11" if r["id"].startswith("k5_11") else "k5_16"
                r["_level"] = level_of(r["id"])
                out.append(r)
    return out


def verdict_class(cert):
    c = str(cert or "")
    if c.startswith("KILL-BY-LOGIC"):
        return "LOGIC"
    if c.startswith("ALIVE"):
        return "ALIVE"
    if c.startswith("FAIL"):
        return "FAIL"
    return "PASS"


def per_level_mix(corpus):
    by = collections.defaultdict(collections.Counter)
    for r in corpus:
        by[r["_level"]][verdict_class(r.get("cert"))] += 1
    mix = {}
    for L, c in sorted(by.items()):
        n = sum(c.values())
        mix[L] = dict(n=n, logic=c["LOGIC"], leaf=c["PASS"] + c["FAIL"], alive=c["ALIVE"],
                      pK=c["LOGIC"] / n, pL=(c["PASS"] + c["FAIL"]) / n, pA=c["ALIVE"] / n)
    return mix


def cost_curve(mix):
    """C(L) by backward recursion from C(MAXLEVEL+1) = 0."""
    C = {MAXLEVEL + 1: 0.0}
    for L in range(MAXLEVEL, 0, -1):
        m = mix.get(L) or mix[max(mix)]
        C[L] = m["pL"] * C_LEAF + m["pA"] * (C_LP + 8.0 * C[L + 1])
    return C


# ------------------------------------------------------------------ kill sets
def kill_sets():
    ks = collections.OrderedDict()
    ks["pinclip_A131"] = {r["id"] for r in jl(os.path.join(A131, "results",
                                                           "backlog_kills.jsonl"))}
    poly = jl(os.path.join(A135, "results", "polycore_kills.jsonl"))
    ks["polycore_A135"] = {r["id"] for r in poly if r.get("kind") == "T5-poly-logic"}
    ks["lp_certified_A135"] = {r["id"] for r in poly if r.get("kind") == "LP-certified"}
    ks["trimempty_A124"] = {r["id"] for r in jl(os.path.join(A124, "results",
                                                             "recheck124.jsonl"))
                            if r.get("excluded_intervals")}
    return ks


def descendants_of(killset, ids):
    """ids that sit strictly below some killed id (monotonic inheritance of a geometric kill)."""
    out = set()
    kk = sorted(killset)
    for i in ids:
        if i in killset:
            continue
        for k in kk:
            if i.startswith(k + "_D"):
                out.add(i)
                break
    return out


# ------------------------------------------------------------------ main
def main():
    corpus = a57_corpus()
    mix = per_level_mix(corpus)
    C = cost_curve(mix)

    open_rows = jl(os.path.join(A131, "results", "corpus131.jsonl"))
    orow = {r["id"]: r for r in open_rows}
    work = [r for r in open_rows if r["verdict"] in ALIVE_VERDICTS or r["verdict"] == "FAIL"]
    alive = [r for r in work if r["verdict"] in ALIVE_VERDICTS]
    fail = [r for r in work if r["verdict"] == "FAIL"]

    ks = kill_sets()
    workids = {r["id"] for r in work}
    arith, removed = [], set()
    for nm, S in ks.items():
        hit = (S & workids) - removed
        arith.append(dict(step=nm, n_in_list=len(S), n_hits_work_owing=len(S & workids),
                          n_new=len(hit), running_removed=len(removed | hit)))
        removed |= hit

    # (e) descendants of anything geometrically dead: the four kill lists AND the tree's own
    # recorded KILL-BY-LOGIC rows (their subtrees were emitted before T5'/T5''/pin-clip existed).
    logic_ids = {r["id"] for r in corpus if verdict_class(r.get("cert")) == "LOGIC"}
    allkilled = set().union(*ks.values()) | logic_ids
    desc = descendants_of(allkilled, workids - removed)
    arith.append(dict(step="descendants_of_killed (monotonicity)",
                      n_in_list=len(allkilled), n_hits_work_owing=len(desc),
                      n_new=len(desc), running_removed=len(removed | desc)))
    removed |= desc

    surv = [r for r in work if r["id"] not in removed]
    surv_alive = [r for r in surv if r["verdict"] in ALIVE_VERDICTS]
    surv_fail = [r for r in surv if r["verdict"] == "FAIL"]

    # ---------------------------------------------------------- subtree cost
    survset = {r["id"] for r in surv}
    kids = collections.defaultdict(list)
    for i in survset:
        for j in survset:
            if i != j and j.startswith(i + "_D"):
                kids[i].append(j)

    def residual(r):
        if r["verdict"] == "FAIL":
            return C_FAIL
        if kids[r["id"]]:
            return 0.0
        L = r["level"]
        k8 = float(r.get("kept8", 1.0) or 0.0)
        return 8.0 * C.get(L + 1, 0.0) * k8

    res = {r["id"]: residual(r) for r in surv}
    rank = []
    for r in surv:
        sub = res[r["id"]] + sum(res[d] for d in kids[r["id"]])
        rank.append(dict(id=r["id"], camp="A57", cls=r["cls"], level=r["level"],
                         verdict=r["verdict"], kept8=round(float(r.get("kept8", 1.0)), 6),
                         emptied8=bool(r.get("emptied8")), n_open_desc=len(kids[r["id"]]),
                         residual_s=round(res[r["id"]], 1), subtree_s=round(sub, 1),
                         subtree_cpuh=round(sub / 3600.0, 3)))
    # ---------------------------------------------------------- A60
    sn = json.load(open(os.path.join(A107, "results", "shadow_nodes.json"), encoding="utf-8"))
    fam = {}
    a60 = {}
    for sid, lst in sn.items():
        for n in lst:
            fam.setdefault(n["nid"], []).append(sid)
            if n["src"] == "A60":
                a60[n["nid"]] = n
    a60rank = []
    for nid, n in sorted(a60.items()):
        L = int(n.get("level") or 1)
        a60rank.append(dict(id=nid, camp="A60", cls="trump5_j%d" % (L - 1), level=L,
                            verdict="refused (tau >= budget)", kept8=None, emptied8=False,
                            n_open_desc=0, residual_s=round(8.0 * C.get(L + 1, 0.0), 1),
                            subtree_s=round(8.0 * C.get(L + 1, 0.0), 1),
                            subtree_cpuh=round(8.0 * C.get(L + 1, 0.0) / 3600.0, 3),
                            tau=n.get("tau"), shadow=fam.get(nid, [])))
    # A60 is FLAT (all 283 at depth j = 0, no emitted descendants), so the model gives every node
    # the same subtree cost; the ranking key that separates them is the LP's own distance from
    # death -- tau (all at budget) then the polygon core's bite, added by rank142 below.
    m132 = {r["id"]: r for r in jl(os.path.join(A132, "results", "measure132.jsonl"))}
    for d in a60rank:
        m = m132.get(d["id"])
        d["w_poly_only"] = round(float(m["support"]["w_poly_only"]), 4) if m else None
        d["n_poly_only"] = int(m["support"]["n_poly_only"]) if m else None
        d["n_support"] = int(m["support"]["n"]) if m else None
        d["t5poly_dead"] = bool(m and m.get("t5poly_dead"))
        d["area_ratio"] = round(float(m["area_ratio"]), 4) if m else None
    a60rank.sort(key=lambda d: (-d["subtree_s"], -(d["w_poly_only"] or 0.0), d["id"]))
    for d in rank:
        m = m132.get(d["id"])
        d["w_poly_only"] = round(float(m["support"]["w_poly_only"]), 4) if m else None
        d["n_poly_only"] = int(m["support"]["n_poly_only"]) if m else None
        d["n_support"] = int(m["support"]["n"]) if m else None
        d["area_ratio"] = round(float(m["area_ratio"]), 4) if m else None
        d["shadow"] = fam.get(d["id"], [])
    # The model gives every level-1 ALIVE node with kept8 = 1 and no emitted child the SAME
    # subtree cost (the model cannot see inside an un-descended box), so ties are broken by the
    # polygon core's measured bite on that node's own dual support: among equally expensive
    # nodes, the ones where K' already excludes the most dual weight are the ones a geometric
    # reading is most likely to close.
    rank.sort(key=lambda d: (-d["subtree_s"], -(d["w_poly_only"] or 0.0), d["id"]))

    out = dict(
        generated="A142 T1 population + subtree-cost ranking",
        cost_model=dict(c_leaf=C_LEAF, c_fail=C_FAIL, c_lp=C_LP, maxlevel=MAXLEVEL,
                        per_level_mix=mix, C=C,
                        formula="C(L) = pL(L)*c_leaf + pA(L)*(c_LP + 8*C(L+1)), C(5)=0; "
                                "subtree(n) = residual(n) + sum over still-open emitted "
                                "descendants; residual(ALIVE leaf-of-tree at L) = "
                                "8*C(L+1)*kept8(n); residual(FAIL) = 900 s"),
        start=dict(corpus_total=2418, corpus_open=len(open_rows),
                   work_owing=len(work), alive=len(alive), fail=len(fail),
                   by_verdict=dict(collections.Counter(r["verdict"] for r in work))),
        arithmetic=arith,
        surviving=dict(n=len(surv), alive=len(surv_alive), fail=len(surv_fail),
                       by_level=dict(collections.Counter(r["level"] for r in surv)),
                       by_class=dict(collections.Counter(r["cls"] for r in surv)),
                       by_verdict=dict(collections.Counter(r["verdict"] for r in surv))),
        a60=dict(n=len(a60rank), source="A107 shadow_nodes.json (nodes with an LP support)"),
        rank_a57=rank, rank_a60=a60rank)
    p = os.path.join(BASE, "results", "population142.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)

    print("A57 corpus %d rows; per-level mix / cost curve:" % len(corpus))
    for L in sorted(mix):
        m = mix[L]
        print("  L%d n=%-5d logic %5.1f%%  leaf %5.1f%%  alive %5.1f%%   C(L) = %9.1f s"
              % (L, m["n"], 100 * m["pK"], 100 * m["pL"], 100 * m["pA"], C[L]))
    print("\npopulation arithmetic")
    print("  start: %d work-owing = %d ALIVE + %d FAIL" % (len(work), len(alive), len(fail)))
    for a in arith:
        print("  - %-38s list %5d, hits %4d, NEW %4d  -> removed %4d"
              % (a["step"], a["n_in_list"], a["n_hits_work_owing"], a["n_new"],
                 a["running_removed"]))
    print("  = SURVIVING %d (%d alive + %d fail)" % (len(surv), len(surv_alive), len(surv_fail)))
    print("  by level", dict(collections.Counter(r["level"] for r in surv)))
    print("\ntop 12 by subtree cost")
    for d in rank[:12]:
        print("  %-34s L%d %-22s kept8 %.3f desc %d  %8.1f s = %.2f CPU-h"
              % (d["id"], d["level"], d["verdict"], d["kept8"], d["n_open_desc"],
                 d["subtree_s"], d["subtree_cpuh"]))
    print("\nA60 %d nodes, all level 1; top 5 by K'-excluded support weight" % len(a60rank))
    for d in a60rank[:5]:
        print("  %-20s subtree %8.1f s  w_poly_only %s of %s columns"
              % (d["id"], d["subtree_s"], d["w_poly_only"], d["n_support"]))
    print("\nwrote", p)


if __name__ == "__main__":
    main()
