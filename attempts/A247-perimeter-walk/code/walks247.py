"""A247 task 2 -- the WALKS (exact form): every incidence structure of a 12-stuck packing that
the catalogue, the closed-form lemmas and the pair table allow, at meeting level eta.

Squares: two meeters per corner box (the hypothesis; THREE-IN-BOX is tested separately) and
three free squares.  At level eta a square's CELL-SET is the set of cells it meets with depth
> eta; a meeter of c has {c00} + a subset of c's four slots, a free square a subset of one
window (possibly empty).  A WALK is the multiset of the eleven cell-sets with every slot in at
least two of them; two walks are the same up to relabelling and D4.  A walk containing two
squares whose pair is killed -- by NOT-SELF-SUFFICIENT, by TWO-FAR, or by an INFEASIBLE row of
the pair table (bb247, exact form, level (eta, eta_avoid)) -- is not the walk of any packing at
that level and is dropped.  The count is a transfer-matrix count over the four corners for
each free multiset (exact, no sampling); the list is written when it is small enough.
    python walks247.py --pairs results/pairs247_window_exact_0.05.jsonl [--corpus] [--slotmet] [--list-cap N]
"""
import argparse
import collections
import itertools
import json
import os
import sys
import time

import numpy as np

import geo247 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
NEXT = {'BL': 'BR', 'BR': 'TR', 'TR': 'TL', 'TL': 'BL'}          # ring order of the corners
# the two slots on the wall between c and NEXT[c]: (c's slot, NEXT[c]'s slot)
WALL = {'BL': ('BL10', 'BR10'), 'BR': ('BR01', 'TR01'), 'TR': ('TR10', 'TL10'), 'TL': ('TL01', 'BL01')}


def lemma_kill(a, b):
    """closed-form [T] pair kills (monotone, any level, n-general, s in (3.5, 4)): NOT-SELF-
    SUFFICIENT (A246): two meeters of c cannot both meet c01 and c10; TWO-FAR (A247): two
    meeters of c cannot both meet the same far slot."""
    if a[0] != 'M' or b[0] != 'M' or a[1] != b[1]:
        return False
    c = a[1]
    A, B = set(a[2]), set(b[2])
    if {'%s01' % c, '%s10' % c} <= A and {'%s01' % c, '%s10' % c} <= B:
        return True
    return any(f[:2] != c and f in A and f in B for f in G.SLOTS_OF[c])


class Facts(object):
    def __init__(self, paths, lemmas=True):
        self.lemmas, self.status, self.eta, self.eta_avoid, self.cache = lemmas, {}, None, None, {}
        for p in paths:
            for line in open(p):
                r = json.loads(line)
                self.eta, self.eta_avoid = r['eta'], r.get('eta_avoid', r['eta'])
                if r['status'] == 'INFEASIBLE' or r['key'] not in self.status:
                    self.status[r['key']] = r['status']

    def forbidden(self, *specs):
        k = tuple(sorted(G.spec_str(s) for s in specs))
        if k not in self.cache:
            self.cache[k] = (self.status.get(G.tuple_key(list(specs))) == 'INFEASIBLE') or \
                (self.lemmas and lemma_kill(*specs))
        return self.cache[k]

    def n_infeasible(self):
        return sum(1 for v in self.status.values() if v == 'INFEASIBLE')


def corner_options(c, facts, slotmet=False):
    subs = [tuple(sorted(comb, key=G.RING.index)) for r in range(5)
            for comb in itertools.combinations(G.SLOTS_OF[c], r)]
    out = []
    for i, d1 in enumerate(subs):
        for d2 in subs[i:]:
            s1, s2 = ('M', c, ('%s00' % c,) + d1), ('M', c, ('%s00' % c,) + d2)
            if facts.forbidden(s1, s2):
                continue
            if slotmet and not all(z in d1 or z in d2 for z in ('%s01' % c, '%s10' % c)):
                continue
            out.append((d1, d2, s1, s2))
    return out


def option_ok(o1, o2, facts):
    return not (facts.forbidden(o1[2], o2[2]) or facts.forbidden(o1[2], o2[3]) or
                facts.forbidden(o1[3], o2[2]) or facts.forbidden(o1[3], o2[3]))


def free_multisets(facts):
    F = [()] + G.free_sets()
    specs = {f: ('F', f) for f in F if f}
    ok2 = {(a, b): (not a or not b or not facts.forbidden(specs[a], specs[b])) for a in F for b in F}
    out = []
    for comb in itertools.combinations_with_replacement(F, 3):
        if any(not ok2[(comb[i], comb[j])] for i in range(3) for j in range(i + 1, 3)):
            continue
        cnt = collections.Counter(z for f in comb for z in f)
        out.append((tuple(cnt.get(z, 0) for z in G.SLOT_RING), comb))
    return out, specs


class Ring(object):
    """the transfer matrices: options per corner, pair-fact adjacency, slot counts on each wall."""

    def __init__(self, facts, slotmet=False):
        self.facts = facts
        self.opts = {c: corner_options(c, facts, slotmet) for c in G.CORNERS}
        self.adj = {}
        self.cnt = {}
        for c in G.CORNERS:
            c2 = NEXT[c]
            o1, o2 = self.opts[c], self.opts[c2]
            A = np.array([[option_ok(a, b, facts) for b in o2] for a in o1], bool)
            z1, z2 = WALL[c]
            n1 = np.array([[sum(z1 in d for d in (a[0], a[1])) + sum(z1 in d for d in (b[0], b[1])) for b in o2] for a in o1])
            n2 = np.array([[sum(z2 in d for d in (a[0], a[1])) + sum(z2 in d for d in (b[0], b[1])) for b in o2] for a in o1])
            self.adj[c], self.cnt[c] = A, (n1, n2)
        self.fms, self.fspecs = free_multisets(facts)
        self.compat = {}

    def compat_mask(self, c, comb):
        key = (c, comb)
        if key not in self.compat:
            m = np.ones(len(self.opts[c]), bool)
            for f in comb:
                if f:
                    for i, o in enumerate(self.opts[c]):
                        if m[i] and (self.facts.forbidden(self.fspecs[f], o[2]) or self.facts.forbidden(self.fspecs[f], o[3])):
                            m[i] = False
            self.compat[key] = m
        return self.compat[key]

    def matrices(self, vec, comb):
        need = {z: max(0, 2 - v) for z, v in zip(G.SLOT_RING, vec)}
        M = {}
        for c in G.CORNERS:
            z1, z2 = WALL[c]
            n1, n2 = self.cnt[c]
            m = self.adj[c] & (n1 >= need[z1]) & (n2 >= need[z2])
            m &= self.compat_mask(c, comb)[:, None] & self.compat_mask(NEXT[c], comb)[None, :]
            M[c] = m.astype(np.int64)
        return M

    def count(self, vec, comb):
        M = self.matrices(vec, comb)
        P = M['BL'] @ M['BR'] @ M['TR'] @ M['TL']
        return int(np.trace(P)), M

    def enumerate(self, M, comb, cap):
        out = []
        oBL, oBR, oTR, oTL = (self.opts[c] for c in G.CORNERS)
        for i in range(len(oBL)):
            for j in np.flatnonzero(M['BL'][i]):
                for k in np.flatnonzero(M['BR'][j]):
                    for l in np.flatnonzero(M['TR'][k]):
                        if M['TL'][l, i]:
                            o = (oBL[i], oBR[j], oTR[k], oTL[l])
                            out.append((tuple((c, oc[0], oc[1]) for c, oc in zip(G.CORNERS, o)), tuple(sorted(comb))))
                            if len(out) >= cap:
                                return out
        return out


def canon_walk(rec):
    corners, frees = rec
    best = None
    for m in G.D4:
        cs = []
        for c, d1, d2 in corners:
            e1 = tuple(sorted((m[z] for z in d1), key=G.RING.index))
            e2 = tuple(sorted((m[z] for z in d2), key=G.RING.index))
            cs.append((m['%s00' % c][:2], min(e1, e2), max(e1, e2)))
        cs.sort()
        fs = tuple(sorted(tuple(sorted((m[z] for z in f), key=G.RING.index)) for f in frees))
        k = (tuple(cs), fs)
        if best is None or k < best:
            best = k
    return best


def letters(rec):
    corners, frees = rec
    sup = {z: [] for z in G.SLOT_RING}
    for c, d1, d2 in corners:
        for d in (d1, d2):
            for z in d:
                sup[z].append('O' if z[:2] == c else 'A')
    for f in frees:
        for z in f:
            sup[z].append('F')
    return {z: ''.join(sorted(v)) for z, v in sup.items()}


def walk_allowed(rec, ring):
    """is this (corpus) walk allowed by the lemmas, the pair table and the counts?"""
    facts = ring.facts
    corners, frees = rec
    spec = {}
    for c, d1, d2 in corners:
        spec[c] = (('M', c, ('%s00' % c,) + tuple(d1)), ('M', c, ('%s00' % c,) + tuple(d2)))
        if facts.forbidden(*spec[c]):
            return False, 'same-corner pair %s' % c
    for c in G.CORNERS:
        for a in spec[c]:
            for b in spec[NEXT[c]]:
                if facts.forbidden(a, b):
                    return False, 'adjacent pair %s-%s' % (c, NEXT[c])
    fs = [('F', tuple(f)) for f in frees if f]
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            if facts.forbidden(fs[i], fs[j]):
                return False, 'free pair'
        for c in G.CORNERS:
            for a in spec[c]:
                if facts.forbidden(fs[i], a):
                    return False, 'free-meeter pair'
    cnt = collections.Counter(z for c, d1, d2 in corners for d in (d1, d2) for z in d)
    cnt.update(z for f in frees for z in f)
    if any(cnt.get(z, 0) < 2 for z in G.SLOT_RING):
        return False, 'a slot below 2'
    return True, 'ok'


def corpus_walks(eta):
    sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A246-construct-towards', 'code'))
    import check246 as K
    out = []
    for rid, z, kind in K.corpus_282() + K.certified_34():
        s = float(z[33])
        sets = [G.cells_met_pt((z[3 * i], z[3 * i + 1], z[3 * i + 2]), s, eta) for i in range(11)]
        meet = {cell: [i for i in range(11) if cell in sets[i]] for cell in G.RING}
        if any(len(v) < 2 for v in meet.values()):
            out.append((rid, s, None, 'not 12-stuck at level %g' % eta))
            continue
        if any(len(meet[b]) != 2 for b in G.BOXES):
            out.append((rid, s, None, 'a box with 3 meeters'))
            continue
        corners = []
        for c in G.CORNERS:
            d = [tuple(x for x in sets[i] if not x.endswith('00')) for i in meet['%s00' % c]]
            corners.append((c, min(d), max(d)))
        frees = tuple(sorted(sets[i] for i in range(11) if not any(b in sets[i] for b in G.BOXES)))
        out.append((rid, s, (tuple(corners), frees), 'ok'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pairs', nargs='+', required=True)
    ap.add_argument('--slotmet', action='store_true')
    ap.add_argument('--corpus', action='store_true')
    ap.add_argument('--no-lemmas', action='store_true')
    ap.add_argument('--list-cap', type=int, default=200000, help='list walks explicitly only up to this raw count')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    t0 = time.time()
    facts = Facts([os.path.join(ATT, p) if not os.path.isabs(p) else p for p in a.pairs], lemmas=not a.no_lemmas)
    print('pair facts: %d rows, %d INFEASIBLE, level (%s, %s), lemmas %s' % (len(facts.status), facts.n_infeasible(), facts.eta, facts.eta_avoid, not a.no_lemmas))
    ring = Ring(facts, a.slotmet)
    print('corner options: ' + ', '.join('%s %d' % (c, len(ring.opts[c])) for c in G.CORNERS) + '; free multisets %d' % len(ring.fms))
    raw = 0
    per_free = collections.Counter()
    listed = []
    for vec, comb in ring.fms:
        n, M = ring.count(vec, comb)
        if n:
            raw += n
            per_free[sum(1 for f in comb if f)] += n
            if raw <= a.list_cap:
                listed += ring.enumerate(M, comb, a.list_cap)
    walks = {}
    if raw <= a.list_cap:
        for rec in listed:
            k = canon_walk(rec)
            walks.setdefault(k, rec)
    print('raw walks %d (by free squares used: %s); up to D4 %s (%.0f s)' % (
        raw, dict(sorted(per_free.items())), len(walks) if raw <= a.list_cap else 'not listed (cap %d)' % a.list_cap, time.time() - t0))
    tag = a.tag or (os.path.basename(a.pairs[0]).replace('pairs247_', '').replace('.jsonl', '') + ('_slotmet' if a.slotmet else '') + ('_nolemmas' if a.no_lemmas else ''))
    summary = {'kind': 'summary', 'pairs': a.pairs, 'slotmet': a.slotmet, 'lemmas': not a.no_lemmas, 'eta': facts.eta,
               'eta_avoid': facts.eta_avoid, 'n_infeasible_pairs': facts.n_infeasible(),
               'corner_options': {c: len(ring.opts[c]) for c in G.CORNERS}, 'free_multisets': len(ring.fms),
               'raw_walks': raw, 'raw_by_free_used': dict(per_free), 'walks_d4': len(walks) if raw <= a.list_cap else None,
               'seconds': time.time() - t0}
    if a.corpus:
        cw = corpus_walks(facts.eta)
        verdicts = [(rid, s) + walk_allowed(rec, ring) for rid, s, rec, why in cw if rec]
        skipped = collections.Counter(why for rid, s, rec, why in cw if not rec)
        miss = [v for v in verdicts if not v[2]]
        summary.update(corpus_packings=len(cw), corpus_checked=len(verdicts), corpus_allowed=len(verdicts) - len(miss),
                       corpus_missing=len(miss), corpus_skipped=dict(skipped), corpus_missing_examples=miss[:5],
                       corpus_side_range=[min(s for _, s, _, _ in cw), max(s for _, s, _, _ in cw)])
        print('corpus at level %g: %d packings, %d walks checked, %d allowed, %d MISSING, skipped %s' % (
            facts.eta, len(cw), len(verdicts), len(verdicts) - len(miss), len(miss), dict(skipped)))
    out = os.path.join(ATT, 'results', 'walks247_%s.jsonl' % tag)
    with open(out, 'w') as f:
        f.write(json.dumps(summary) + '\n')
        for k, rec in sorted(walks.items()):
            corners, frees = k
            f.write(json.dumps({'corners': [[c, list(d1), list(d2)] for c, d1, d2 in corners],
                                'free': [list(x) for x in frees], 'n_free_used': sum(1 for x in frees if x),
                                'free_incidences': sum(len(x) for x in frees), 'letters': letters(k)}) + '\n')
    print('wrote %s' % out)


if __name__ == '__main__':
    main()
