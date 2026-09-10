"""A201 -- A200's count_search (per-slot caps) with the pairwise test replaced by pairtab201.PairTable.compatible
(Lemma A1 + Lemma CN + the exact multibox pair node): the copy of quick200.count_search, modified in one place."""
import fastprop as FP                                          # READ-ONLY (A198)
import pairtab201 as PT


def count_search(slots, free_opts, fixed_opts, n_free, lines, base_chords, s, caps, table, node_cap=200000, use_chords=True):
    """A200's count_search (per-slot caps) with `table.compatible` as the pairwise test (A1 + CN + EXACT)."""
    names = list(fixed_opts)
    nodes, capped = [0], [False]
    by_slot = {p: [o for o in free_opts if p in o[1]] for p in slots}
    table.begin_search()

    def chords_ok(ch):
        return (not use_chords) or all(ch[L] <= s for L in lines)

    def add(ch, c):
        return {L: ch[L] + c[L] for L in lines}

    def compat(who, o, chosen):
        k = PT.okey(who, o)
        return all(table.compatible(k, PT.okey(w2, o2)) for w2, o2 in chosen)

    def rec_free(demand, used, ch, left, chosen, anon):
        nodes[0] += 1
        if nodes[0] > node_cap:
            capped[0] = True
            return None
        need = [p for p in slots if demand[p] > 0]
        if not need:
            return list(chosen)
        if left == 0:
            return None
        tot = sum(demand[p] for p in need)
        best, cands = None, None
        for p in need:
            cs = [o for o in by_slot[p] if o[0] not in used and anon[p] < caps[p]
                  and all(anon[q] < caps[q] for q in o[1] if q in anon)]
            if best is None or len(cs) < len(cands):
                best, cands = p, cs
            if not cs:
                return None
        maxS = max(len(o[1]) for o in free_opts) if free_opts else 0
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

    def rec_fixed(k, demand, used, ch, chosen):
        if k == len(names):
            return rec_free(demand, used, ch, n_free, chosen, {p: 0 for p in slots})
        for o in fixed_opts[names[k]]:
            if o[0] in used or not compat(names[k], o, chosen):
                continue
            ch2 = add(ch, o[2])
            if not chords_ok(ch2):
                continue
            d2 = dict(demand)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
            r = rec_fixed(k + 1, d2, used | {o[0]}, ch2, chosen + [(names[k], o)])
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    w = rec_fixed(0, {p: 2 for p in slots}, frozenset(), dict(base_chords), [])
    return FP.CountResult(w is not None or capped[0], w, nodes[0], capped[0])


