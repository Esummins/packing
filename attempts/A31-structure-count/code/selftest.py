"""A31 self-tests.  Independent re-implementations, deliberately naive, to check the
fast Level-0 pipeline.  Any disagreement is a completeness bug and must be fixed."""
import math, itertools, json, sys, os
import numpy as np
import networkx as nx
import lib0 as L
import run_level0 as R

SQRT2 = math.sqrt(2.0)
FAILS = []


def check(name, a, b):
    ok = (a == b)
    print(('PASS ' if ok else 'FAIL ') + name, a, b)
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------- naive reference
def naive_all(k, verbose=False):
    """Brute force over EVERY edge subset on k squares + 4 walls (no wall-wall edges),
    dedupe by orbit under S_k x D4, and apply every filter from scratch."""
    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    npair = len(pairs)
    perms = list(itertools.permutations(range(k)))
    reps = {}
    cnt = dict(R0=0, R2=0, R3=0, R4=0, R5=0, R6=0, R7=0, R8=0, R9=0, R10=0,
               main=0, lam0=0, sfloat=0, both=0, thin_main=0)
    seen = set()
    for ss in range(1 << npair):
        for wm in itertools.product(range(16), repeat=k):
            key = canon_key(k, ss, wm, perms, pairs)
            if key in seen:
                continue
            seen.add(key)
            cnt['R0'] += 1
            if not all(m in L.ALLOWED_SET for m in wm):
                continue
            cnt['R2'] += 1
            adj = [0] * k
            for e, (i, j) in enumerate(pairs):
                if (ss >> e) & 1:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
            deg = [bin(adj[i]).count('1') for i in range(k)]
            if any(deg[i] + bin(wm[i]).count('1') < 2 for i in range(k)):
                continue
            cnt['R3'] += 1
            if max(deg) > 12:
                continue
            cnt['R4'] += 1
            E = bin(ss).count('1') + sum(bin(m).count('1') for m in wm)
            if E > 3 * k + 2:
                continue
            cnt['R5'] += 1
            if not metric_ok(k, adj, wm):
                continue
            cnt['R6'] += 1
            cw = comp_walls(k, adj, wm)
            nofloat = all(c != 0 for c in cw)
            span = any((c & 5) == 5 or (c & 10) == 10 for c in cw)
            if nofloat:
                cnt['R7'] += 1
                if span:
                    cnt['R8'] += 1
            pl = planar(k, adj, wm, True)
            if nofloat and span and pl:
                cnt['R9'] += 1
                allw = 0
                for m in wm:
                    allw |= m
                if (allw & 5) == 5 or (allw & 10) == 10:
                    cnt['R10'] += 1
            if pl:
                if nofloat and span:
                    cnt['main'] += 1
                    if any(deg[i] + bin(wm[i]).count('1') == 2 for i in range(k)):
                        cnt['thin_main'] += 1
                elif nofloat and not span:
                    cnt['lam0'] += 1
                if not nofloat:
                    cnt['sfloat'] += 1     # L3 case-(ii) branch, span or not
                    if not span:
                        cnt['both'] += 1
    return cnt


def naive_from_L1(k):
    """Same naive reference but starting from the L5b alphabet and L1 (so it is fast
    enough for k=4): canonicalisation happens AFTER the two local filters, which is
    legitimate because both are orbit-invariant."""
    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    perms = list(itertools.permutations(range(k)))
    cnt = dict(R3=0, R4=0, R5=0, R6=0, R7=0, R8=0, R9=0, R10=0,
               main=0, lam0=0, sfloat=0, both=0, thin_main=0)
    seen = set()
    for ss in range(1 << len(pairs)):
        adj = [0] * k
        for e, (i, j) in enumerate(pairs):
            if (ss >> e) & 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
        deg = [bin(adj[i]).count('1') for i in range(k)]
        for wm in itertools.product(L.ALLOWED, repeat=k):
            if any(deg[i] + bin(wm[i]).count('1') < 2 for i in range(k)):
                continue
            key = canon_key(k, ss, wm, perms, pairs)
            if key in seen:
                continue
            seen.add(key)
            cnt['R3'] += 1
            if max(deg) > 12:
                continue
            cnt['R4'] += 1
            E = bin(ss).count('1') + sum(bin(m).count('1') for m in wm)
            if E > 3 * k + 2:
                continue
            cnt['R5'] += 1
            if not metric_ok(k, adj, wm):
                continue
            cnt['R6'] += 1
            cw = comp_walls(k, adj, wm)
            nofloat = all(c != 0 for c in cw)
            span = any((c & 5) == 5 or (c & 10) == 10 for c in cw)
            if nofloat:
                cnt['R7'] += 1
                if span:
                    cnt['R8'] += 1
            pl = planar(k, adj, wm, True)
            if nofloat and span and pl:
                cnt['R9'] += 1
                allw = 0
                for m in wm:
                    allw |= m
                if (allw & 5) == 5 or (allw & 10) == 10:
                    cnt['R10'] += 1
            if pl:
                if nofloat and span:
                    cnt['main'] += 1
                    if any(deg[i] + bin(wm[i]).count('1') == 2 for i in range(k)):
                        cnt['thin_main'] += 1
                elif nofloat and not span:
                    cnt['lam0'] += 1
                if not nofloat:
                    cnt['sfloat'] += 1
                    if not span:
                        cnt['both'] += 1
    return cnt


def canon_key(k, ss, wm, perms, pairs):
    best = None
    pidx = {p: e for e, p in enumerate(pairs)}
    for p in perms:
        ss2 = 0
        for e, (i, j) in enumerate(pairs):
            if (ss >> e) & 1:
                a, b = p[i], p[j]
                if a > b:
                    a, b = b, a
                ss2 |= 1 << pidx[(a, b)]
        for d in range(8):
            tab = L.MT[d]
            w2 = [0] * k
            for i in range(k):
                w2[p[i]] = int(tab[wm[i]])
            t = (ss2, tuple(w2))
            if best is None or t < best:
                best = t
    return best


def metric_ok(k, adj, wm):
    D = L.hop_matrix(adj, k)
    for i in range(k):
        for j in range(i + 1, k):
            b1, b2 = L._box(wm[i]), L._box(wm[j])
            lo, hi = L._rect_range(b1, b2)
            lo = max(1.0, lo)
            if lo > hi + 1e-12:
                return False
            reach = SQRT2 * D[i][j] if D[i][j] < 90 else 1e9
            if lo > min(hi, reach) + 1e-12:
                return False
    return True


def comp_walls(k, adj, wm):
    comps = L.components(adj, k)
    cw = [0] * len(comps)
    for c, vs in enumerate(comps):
        for v in vs:
            cw[c] |= wm[v]
    changed = True
    while changed:
        changed = False
        for a in range(len(cw)):
            for b in range(a + 1, len(cw)):
                if cw[a] & cw[b] and cw[a] != cw[b]:
                    u = cw[a] | cw[b]
                    cw[a] = cw[b] = u
                    changed = True
    return cw


def planar(k, adj, wm, cyc):
    G = nx.Graph()
    G.add_nodes_from(range(k + 4))
    for i in range(k):
        for j in range(i + 1, k):
            if (adj[i] >> j) & 1:
                G.add_edge(i, j)
        for b in range(4):
            if (wm[i] >> b) & 1:
                G.add_edge(i, k + b)
    if cyc:
        for b in range(4):
            G.add_edge(k + b, k + (b + 1) % 4)
    return nx.check_planarity(G, counterexample=False)[0]


def pipeline(k):
    reps = L.graph_reps(k)
    pset = set(g for g, _ in reps if L.planar_graph(g, k))
    agg = dict(cum=[0] * 8, marg=[0] * 8, branch=dict(main=0, thin_main=0,
               selfstress_float=0, lam0=0, both=0))
    for g, aut in reps:
        r = R.run_arep((k, g, aut, False, g in pset))
        for i in range(8):
            agg['cum'][i] += r['cum'][i]
            agg['marg'][i] += r['marg'][i]
        for key in agg['branch']:
            agg['branch'][key] += r['branch'][key]
    return agg


if __name__ == '__main__':
    # 1. graph rep counts = OEIS A000088
    check('A000088', [len(L.graph_reps(n)) for n in range(1, 8)],
          [1, 2, 4, 11, 34, 156, 1044])
    # 2. D4 mask tables form a group and ALLOWED is invariant
    ok = all(sorted(int(L.MT[d][m]) for m in L.ALLOWED) == sorted(L.ALLOWED)
             for d in range(8))
    check('ALLOWED D4-invariant', ok, True)
    # 3. Burnside vs naive orbit count, k=2,3
    for k in [2, 3]:
        n = naive_all(k)
        r0, r2 = L.burnside_rows(k)
        check('burnside R0 k=%d' % k, r0, n['R0'])
        check('burnside R2 k=%d' % k, r2, n['R2'])
        p = pipeline(k)
        check('R3 k=%d' % k, p['cum'][0], n['R3'])
        check('R4 k=%d' % k, p['cum'][1], n['R4'])
        check('R5 k=%d' % k, p['cum'][2], n['R5'])
        check('R6 k=%d' % k, p['cum'][3], n['R6'])
        check('R7 k=%d' % k, p['cum'][4], n['R7'])
        check('R8 k=%d' % k, p['cum'][5], n['R8'])
        check('R9 k=%d' % k, p['cum'][6], n['R9'])
        check('R10 k=%d' % k, p['cum'][7], n['R10'])
        check('main k=%d' % k, p['branch']['main'], n['main'])
        check('lam0 k=%d' % k, p['branch']['lam0'], n['lam0'])
        check('sfloat k=%d' % k, p['branch']['selfstress_float'], n['sfloat'])
        check('both k=%d' % k, p['branch']['both'], n['both'])
        check('thin k=%d' % k, p['branch']['thin_main'], n['thin_main'])
    # 4. independent naive check at k=4 (from the L1 stage on)
    if '--k4' in sys.argv:
        n = naive_from_L1(4)
        p = pipeline(4)
        for i, nm in enumerate(['R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']):
            check('%s k=4' % nm, p['cum'][i], n[nm])
        for nm, key in [('main', 'main'), ('lam0', 'lam0'),
                        ('sfloat', 'selfstress_float'), ('both', 'both'),
                        ('thin_main', 'thin_main')]:
            check('%s k=4' % nm, p['branch'][key], n[nm])
    print('\n%d failures' % len(FAILS), FAILS)
