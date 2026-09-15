"""A219 task 3: the finite structure question behind Lemma RING, counted.
A LOADED FOUR-CROWD contact structure (wall_torque.md s.6): 8 meeters m_{c,w} (corner c, the meeter in the
cell against wall w in {u, v}), each with  wall bit (touches its wall, loaded or not), the corner's partner
bit (the two meeters press on each other), and <= 2 HOLDERS, a holder being another meeter (not the partner)
or one of h <= 3 interior squares; every interior square touches >= 1 meeter; interior squares may touch
each other; every meeter carries >= 1 loaded contact (LOADED).  Counted: labelled structures, then / 8 (D4)
and / h! (interior squares unlabelled) as the orbit estimate; with and without the TWO-CONTACT prune (a
meeter with wall + exactly one other contact needs the 45-degree diamond or a flat pose: a codimension-1
tilt condition, counted separately).  Price: 0.78 s per structure (fj_census_k0.md s.4, Lemma H-LOC).
    python structures219.py   -> results/structures219.json, prints the table
"""
import itertools
import json
import math
import os
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'results', 'structures219.json')
CORNERS = ('BL', 'BR', 'TR', 'TL')
MEETERS = [(c, w) for c in CORNERS for w in ('u', 'v')]         # 8 meeters
IDX = {m: k for k, m in enumerate(MEETERS)}
PARTNER = {IDX[(c, 'u')]: IDX[(c, 'v')] for c in CORNERS}
PARTNER.update({v: k for k, v in PARTNER.items()})
CROSS = [(a, b) for a in range(8) for b in range(a + 1, 8) if PARTNER[a] != b]     # 24 cross pairs
COST_S = 0.78


def cross_graphs():
    """subgraphs of the 24 cross pairs with holder-degree <= 2 at every meeter -> Counter of degree vectors."""
    deg_count = Counter()
    deg = [0] * 8

    def rec(k):
        if k == len(CROSS):
            deg_count[tuple(deg)] += 1
            return
        rec(k + 1)
        a, b = CROSS[k]
        if deg[a] < 2 and deg[b] < 2:
            deg[a] += 1
            deg[b] += 1
            rec(k + 1)
            deg[a] -= 1
            deg[b] -= 1
    rec(0)
    return deg_count


def interior_count(res, h, need):
    """number of h-tuples of NONEMPTY meeter subsets (the interior squares' contact sets) with meeter m
    touching at most res[m] of them, and every meeter in `need` touching >= 1 (inclusion-exclusion over
    the squares left empty)."""
    total = 0
    for T in range(h + 1):                                  # T squares forced empty
        k = h - T
        prod = 1
        for m in range(8):
            if m in need:
                f = sum(math.comb(k, j) for j in range(1, min(res[m], k) + 1))
            else:
                f = sum(math.comb(k, j) for j in range(0, min(res[m], k) + 1))
            prod *= f
        total += (-1) ** T * math.comb(h, T) * prod
    return total


def wallpartner_patterns(need_set):
    """(p_c, w_a, w_b) patterns per corner such that every meeter in need_set has w = 1 or p_c = 1."""
    prod = 1
    for c in CORNERS:
        a, b = IDX[(c, 'u')], IDX[(c, 'v')]
        na, nb = a in need_set, b in need_set
        prod *= 8 if not (na or nb) else (6 if na != nb else 5)
    return prod


def count(prune_two_contact=False):
    degs = cross_graphs()
    labelled = 0
    by_h = Counter()
    for dvec, mult in degs.items():
        res = [2 - d for d in dvec]
        U = [m for m in range(8) if dvec[m] == 0]           # meeters not loaded by a cross edge
        for h in range(4):
            for r in range(len(U) + 1):
                for V in itertools.combinations(U, r):     # meeters of U loaded by an interior square
                    Vs = set(V)
                    others = set(U) - Vs                    # loaded by wall or partner only
                    # interior tuples with V forced >= 1 interior contact and others forced 0
                    res2 = [0 if m in others else res[m] for m in range(8)]
                    n_int = interior_count(res2, h, Vs) if h > 0 else (1 if not Vs else 0)
                    if n_int == 0:
                        continue
                    n_wp = wallpartner_patterns(others)
                    if prune_two_contact:
                        n_wp = wallpartner_patterns_pruned(others, dvec, Vs, h)
                    n = mult * n_int * n_wp * 2 ** math.comb(h, 2)
                    labelled += n
                    by_h[h] += n
    return labelled, by_h


def wallpartner_patterns_pruned(others, dvec, Vs, h):
    """as wallpartner_patterns but a meeter whose contacts are exactly {wall, one other} (generic tilt) is
    excluded: wall = 1 and (partner + cross degree + interior contacts) = 1.  Interior contact counts are
    not resolved here, so the prune is applied where they are known to be 0 (meeters in `others` and
    meeters with cross degree >= 1 and no interior slot): a LOWER bound on the pruned count is not needed --
    this is the count with the prune applied to the wall/partner bits only (an UPPER bound on survivors)."""
    prod = 1
    for c in CORNERS:
        a, b = IDX[(c, 'u')], IDX[(c, 'v')]
        n = 0
        for p in (0, 1):
            for wa in (0, 1):
                for wb in (0, 1):
                    ok = True
                    for m, wm in ((a, wa), (b, wb)):
                        if m in others and not (wm or p):
                            ok = False
                        if m in others and wm and p and dvec[m] == 0:      # wall + partner only: dead
                            ok = False
                    if ok:
                        n += 1
        prod *= n
    return prod


def main():
    t0 = time.time()
    raw, by_h = count(False)
    pruned, by_hp = count(True)
    out = {'labelled': raw, 'labelled_by_h': dict(by_h), 'labelled_two_contact_pruned_upper': pruned,
           'orbit_estimate': raw / 8, 'orbit_estimate_unlabelled_interior': sum(v / (8 * math.factorial(h)) for h, v in by_h.items()),
           'price_s_per_structure': COST_S, 't_s': round(time.time() - t0, 1)}
    out['price_cpu_days_orbits'] = out['orbit_estimate_unlabelled_interior'] * COST_S / 86400
    out['price_cpu_days_pruned_upper'] = pruned / 8 * COST_S / 86400
    json.dump(out, open(OUT, 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
