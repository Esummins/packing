"""A268 verifier clause for a COUNT268 kill: re-prove, from the self-contained dump alone, that the JOINT COUNT has no
cover.  Independent of count268's search: no MRV, no supply prune, no shared code -- a plain depth-first enumeration
of one option per fixed role in a FIXED order (the dump's role order), with only the definition's own constraints
checked on each new row against every chosen row (pair table, distinct cells, chord rows <= s when use_chords) and
one look-ahead (a later role with NO row pairwise compatible with every chosen row ends the branch), and
at a full fixed assignment an exhaustive search over SETS of at most n_free anonymous rows (combinations, i.e. MORE
permissive than tree205's rec_free, which only picks rows meeting a still-needed slot) with the anon caps.  Every
slot must reach 2 meeters.  EVERY fixed role must take a row: a role with no row at all (the dump's fixed_roles) makes
the count infeasible outright, exactly as in tree205.  Arithmetic exact (Fractions from the typed encoding).

    python verify268.py <dump.json> [...]
"""
import json
import sys
from fractions import Fraction


def dec(t):
    if t == "inf":
        return None
    k, v = t.split(":", 1)
    if k == "i":
        return Fraction(int(v))
    if k == "q":
        return Fraction(v)
    return Fraction(float.fromhex(v))


def verify(path):
    d = json.load(open(path, encoding="utf-8"))
    slots, n_free, use = d["slots"], d["n_free"], d["use_chords"]
    s = dec(d["s"])
    caps = {p: dec(v) for p, v in d["caps"].items()}
    base = [dec(v) for v in d["base"]]
    opts = d["opts"]
    n = len(opts)
    comp = [int(h, 16) for h in d["comp"]]
    ok = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if (comp[i] >> j) & 1:
                ok[i][j] = ok[j][i] = True
    ch = [[dec(v) for v in o["ch"]] for o in opts]
    owners = list(d.get("fixed_roles") or sorted((d.get("search") or {}).get("n_fixed") or {}))   # EVERY fixed role, a row-less one too
    for o in opts:
        if o["owner"] != "free" and o["owner"] not in owners:
            owners.append(o["owner"])
    by_owner = {w: [i for i, o in enumerate(opts) if o["owner"] == w] for w in owners}
    free = [i for i, o in enumerate(opts) if o["owner"] == "free"]
    nodes = [0]

    def fits(i, chosen, acc):
        if any(opts[i]["cell"] == opts[j]["cell"] or not ok[i][j] for j in chosen):
            return None
        a = [x + y for x, y in zip(acc, ch[i])]
        if use and any(x > s for x in a):
            return None
        return a

    def covered(chosen):
        m = {p: 0 for p in slots}
        for j in chosen:
            for p in opts[j]["S"]:
                if p in m:
                    m[p] += 1
        return m

    def free_stage(chosen, acc, start, left, anon):
        nodes[0] += 1
        if all(v >= 2 for v in covered(chosen).values()):
            return True
        if left == 0:
            return False
        for k in range(start, len(free)):
            i = free[k]
            if any(caps[p] is not None and anon[p] + 1 > caps[p] for p in opts[i]["S"] if p in anon):
                continue
            a = fits(i, chosen, acc)
            if a is None:
                continue
            an = dict(anon)
            for p in opts[i]["S"]:
                if p in an:
                    an[p] += 1
            if free_stage(chosen + [i], a, k + 1, left - 1, an):
                return True
        return False

    # the pairwise mask of option i: the options of OTHER owners it may coexist with (pair table + distinct cells)
    mask = [sum(1 << j for j in range(n) if ok[i][j] and opts[i]["cell"] != opts[j]["cell"]) for i in range(n)]
    omask = {w: sum(1 << i for i in v) for w, v in by_owner.items()}

    def fixed_stage(k, chosen, acc, live):
        nodes[0] += 1
        if k == len(owners):
            return free_stage(chosen, acc, 0, n_free, {p: 0 for p in slots})
        if any(not (omask[w] & live) for w in owners[k:]):     # some later role has no row compatible with every chosen row
            return False
        for i in by_owner[owners[k]]:
            if not (live >> i) & 1:
                continue
            a = fits(i, chosen, acc)
            if a is None:
                continue
            if fixed_stage(k + 1, chosen + [i], a, live & mask[i]):
                return True
        return False

    feasible = fixed_stage(0, [], base, (1 << n) - 1)
    return dict(path=path, verdict="FAILED (a cover exists)" if feasible else "VERIFIED (no cover: the JOINT COUNT kill stands)",
                nodes=nodes[0], n_opts=n, owners={w: len(v) for w, v in by_owner.items()}, n_free_rows=len(free), n_free=n_free)


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        r = verify(p)
        bad += r["verdict"].startswith("FAILED")
        print(json.dumps(r), flush=True)
    sys.exit(1 if bad else 0)
