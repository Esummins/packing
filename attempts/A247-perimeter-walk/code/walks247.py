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
from ring247 import Ring, corner_options, option_ok, free_multisets, lemma_kill, NEXT, WALL   # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
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
    ap.add_argument('--type-f', action='store_true', help='CONDITIONAL: every corner of the PI type-F form (flat meeter + tilted partner)')
    ap.add_argument('--list-cap', type=int, default=200000, help='list walks explicitly only up to this raw count')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    t0 = time.time()
    facts = Facts([os.path.join(ATT, p) if not os.path.isabs(p) else p for p in a.pairs], lemmas=not a.no_lemmas)
    print('pair facts: %d rows, %d INFEASIBLE, level (%s, %s), lemmas %s' % (len(facts.status), facts.n_infeasible(), facts.eta, facts.eta_avoid, not a.no_lemmas))
    ring = Ring(facts, a.slotmet, a.type_f)
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
    tag = a.tag or (os.path.basename(a.pairs[0]).replace('pairs247_', '').replace('.jsonl', '') + ('_slotmet' if a.slotmet else '') + ('_nolemmas' if a.no_lemmas else '') + ('_typef' if a.type_f else ''))
    summary = {'kind': 'summary', 'pairs': a.pairs, 'slotmet': a.slotmet, 'type_f': a.type_f, 'lemmas': not a.no_lemmas, 'eta': facts.eta,
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
