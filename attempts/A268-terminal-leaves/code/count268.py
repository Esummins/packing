"""A268 -- the JOINT COUNT made exhaustive in practice (Lemma COUNT-PRUNE, notes/terminal268.md s.2).

The diagnosis (notes/terminal268.md s.1): at every terminal start node of the k5 loop and the trump5 passes the wall
goes into A200/A203's capped cover search `tree205.count_search` -- 200,000 nodes, ~1 ms a node (pair_ok on rows),
CAPPED every time (feasible=True by convention = no claim) -- called 4-5x in the root round (count, count+chords,
count-barH per slot) and 2x per slot again by `tree205b.anon_needed` inside `candidates()`, which has no wall
check: 2,000 s of capped searches between the root round and the leaf rules, so the leaf rules never run.

This module is a DROP-IN replacement with the SAME contract (fixed roles take exactly one option each, anonymous
squares at most one option each, rows pairwise pair_ok, distinct cells via `used`, chords <= s when use_chords, every
slot demand 2 covered; feasible => a witness; infeasible => exhaustive unless capped; capped => feasible=True, i.e.
NO claim).  It changes only the ORDER of the search and adds three prunes, each a necessary condition on a
completion of the partial assignment (Lemma COUNT-PRUNE):
  (P1) forward checking: an unassigned fixed role must take one option compatible (pair_ok, distinct cell, chords
       -- chord rows are nonnegative, the premise tree205's own chords_ok prune already uses) with every option
       chosen so far; a role whose filtered domain is empty admits no completion;
  (P2) per-slot supply: each unassigned fixed role contributes at most 1 meeter to a slot p and only through a
       domain option containing p; the anonymous squares contribute at most min(n_free, caps[p]) (the anon cap of
       rec_free); residual demand above that supply admits no completion;
  (P3) dynamic order (MRV): the next role is the one with the smallest filtered domain -- any order enumerates the
       same product space.
Plus the WALL: the search stops (capped, no claim) when the page's Trace is out of time or the per-call budget
A268_COUNT_BUDGET (s) runs out.  Flag A268_COUNT=1 installs it (default OFF: tree205.count_search untouched)."""
import os
import time

ON = (os.environ.get("A268_COUNT") or "") == "1"
NODE_CAP = int(os.environ.get("A268_COUNT_NODES") or 2000000)
BUDGET = float(os.environ.get("A268_COUNT_BUDGET") or 240.0)
DUMP = os.environ.get("A268_DUMP_DIR") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "certs"))
DUMP_ALL = (os.environ.get("A268_DUMP_ALL") or "") == "1"      # TEST only: dump feasible counts too (verify268 must say FAILED)
STATS = []                                   # one row per call (the diag driver and the report read it)
_ORIG = {}


def count_search(pg, slots, free_opts, fixed_opts, n_free, lines, base_chords, s, caps, node_cap=200000, use_chords=True):
    import tree205 as T5
    FP = T5.FP
    t_start = time.time()
    T = getattr(pg, "T", None)
    nodes, capped, why = [0], [False], [None]
    pr = dict(fc=0, supply=0, free=0)
    by_slot = {p: [o for o in free_opts if p in o[1]] for p in slots}
    maxS = max((len(o[1]) for o in free_opts), default=0)

    def chords_ok(ch):
        return (not use_chords) or all(ch[L] <= s for L in lines)

    def add(ch, c):
        return {L: ch[L] + c[L] for L in lines}

    def tick():
        nodes[0] += 1
        if nodes[0] > NODE_CAP:
            capped[0], why[0] = True, "nodes"
        elif (nodes[0] & 255) == 0:
            if time.time() - t_start > BUDGET:
                capped[0], why[0] = True, "budget"
            elif T is not None and T.out_of_time():
                capped[0], why[0] = True, "wall"
        return capped[0]

    # ---- the anonymous stage: tree205's rec_free VERBATIM (same prunes, same order, same witness form)
    def compat(name, o, chosen):
        return all(pg.pair_ok(name, o, c[0], c[1]) for c in chosen)

    def rec_free(demand, used, ch, left, chosen, anon):
        if tick():
            return None
        need = [p for p in slots if demand[p] > 0]
        if not need:
            return list(chosen)
        if left == 0:
            return None
        tot = sum(demand[p] for p in need)
        best, cands = None, None
        for p in need:
            cs = [o for o in by_slot[p] if o[0] not in used and anon[p] < caps[p] and all(anon[q] < caps[q] for q in o[1] if q in anon)]
            if best is None or len(cs) < len(cands):
                best, cands = p, cs
            if not cs:
                return None
        if left * maxS < tot:
            return None
        for o in cands:
            if not compat("free", o, chosen):
                continue
            ch2 = add(ch, o[2])
            if not chords_ok(ch2):
                continue
            d2, a2 = dict(demand), dict(anon)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
                    a2[q] += 1
            r = rec_free(d2, used | {o[0]}, ch2, left - 1, chosen + [("free", o)], a2)
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    # ---- the fixed stage: MRV + forward checking + per-slot supply (Lemma COUNT-PRUNE)
    def supply_ok(demand, dom):
        for p in slots:
            d = demand[p]
            if d <= 0:
                continue
            sup = min(n_free, caps[p]) + sum(1 for opts in dom.values() if any(p in o[1] for o in opts))
            if sup < d:
                return False
        return True

    def rec_fixed(dom, demand, used, ch, chosen):
        if tick():
            return None
        if not dom:
            return rec_free(demand, used, ch, n_free, chosen, {p: 0 for p in slots})
        name = min(dom, key=lambda r: (len(dom[r]), r))
        rest = {r: v for r, v in dom.items() if r != name}
        for o in dom[name]:
            ch2 = add(ch, o[2])
            d2 = dict(demand)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
            nd, dead = {}, False
            for r, opts in rest.items():
                f = [o2 for o2 in opts if o2[0] != o[0] and chords_ok(add(ch2, o2[2])) and pg.pair_ok(r, o2, name, o)]
                if not f:
                    dead = True
                    break
                nd[r] = f
            if dead:
                pr["fc"] += 1
                continue
            if not supply_ok(d2, nd):
                pr["supply"] += 1
                continue
            r = rec_fixed(nd, d2, used | {o[0]}, ch2, chosen + [(name, o)])
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    ch0 = dict(base_chords)
    dom0 = {r: [o for o in opts if chords_ok(add(ch0, o[2]))] for r, opts in fixed_opts.items()}
    w = None
    if all(dom0.values()) or not dom0:
        w = rec_fixed(dom0, {p: 2 for p in slots}, frozenset(), ch0, [])
    res = FP.CountResult(w is not None or capped[0], w, nodes[0], capped[0])
    res.engine = "count268"
    row = dict(seconds=round(time.time() - t_start, 3), nodes=nodes[0], capped=capped[0], why=why[0], feasible=res.feasible,
               witness=w is not None, chords=use_chords, n_fixed={r: len(v) for r, v in fixed_opts.items()}, n_free_opts=len(free_opts),
               n_free=n_free, prunes=dict(pr))
    if (not res.feasible or (DUMP_ALL and not capped[0])) and DUMP:
        row["dump"] = dump(pg, slots, free_opts, fixed_opts, n_free, lines, base_chords, s, caps, use_chords, row)
    STATS.append(row)
    if T is not None:
        T.step("count268", row["seconds"], **{k: v for k, v in row.items() if k != "seconds"})
    return res


def enc(v):
    """exact, typed: a Fraction as 'q:n/d', a float as 'f:' + float.hex, an int as 'i:n', infinity as 'inf'."""
    from fractions import Fraction
    if isinstance(v, bool):
        return "i:%d" % int(v)
    if isinstance(v, int):
        return "i:%d" % v
    if isinstance(v, Fraction):
        return "q:%d/%d" % (v.numerator, v.denominator)
    v = float(v)
    return "inf" if v == float("inf") else "f:" + v.hex()


def dump(pg, slots, free_opts, fixed_opts, n_free, lines, base_chords, s, caps, use_chords, row):
    """an INFEASIBLE count's problem, self-contained, for verify268.py: every option (owner, cell, slot set, chord row)
    and the FULL pair table pair_ok over every two options of distinct owners (two anonymous rows included) -- the
    same oracle A205's count reads.  Returns the file path (recorded in the trace step and the kill's node)."""
    import hashlib
    import json
    opts = [("free", o) for o in free_opts] + [(r, o) for r in sorted(fixed_opts) for o in fixed_opts[r]]
    L = list(lines)
    rows = [dict(owner=w, cell=o[0], S=sorted(o[1]), ch=[enc(o[2][l]) for l in L]) for w, o in opts]
    comp = []
    for i, (wi, oi) in enumerate(opts):
        bits = 0
        for j in range(i + 1, len(opts)):
            wj, oj = opts[j]
            if wi == wj and wi != "free":
                continue
            if pg.pair_ok(wi, oi, wj, oj):
                bits |= 1 << j
        comp.append(hex(bits))
    doc = dict(kind="A268 count dump (tree205.count_search contract)", nid=getattr(pg, "nid", None), slots=list(slots),
               n_free=n_free, caps={p: enc(caps[p]) for p in slots}, s=enc(s), use_chords=use_chords, lines=[str(l) for l in L],
               base=[enc(base_chords[l]) for l in L], opts=rows, comp=comp, search=row)
    body = json.dumps(doc, sort_keys=True)
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    os.makedirs(DUMP, exist_ok=True)
    path = os.path.join(DUMP, "count268_%s_%s.json" % (doc["nid"] or "page", h))
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    return path.replace("\\", "/")


def install(log=print):
    """A268_COUNT=1: route every tree205.count_search call (the round's count, count-barH, anon_needed) here."""
    if not ON:
        return False
    import tree205 as T5
    if "count" not in _ORIG:
        _ORIG["count"] = T5.count_search
        T5.count_search = count_search
    log("   A268 COUNT-PRUNE installed (nodes %d, budget %.0f s, wall-aware)" % (NODE_CAP, BUDGET))
    return True
