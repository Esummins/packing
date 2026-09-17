"""A247 task 2 -- the WALKS: every assignment of two designated meeters to each of the twelve
cells that the catalogue and the pair table allow.

Squares: two meeters per corner box (the hypothesis; THREE-IN-BOX is tested separately) and
three free squares.  A meeter of c carries {c00} + a subset of c's four slots (its own two and
the far slot of each of its walls); a free square carries a nonempty subset of one window or
nothing.  A WALK is the multiset of the eleven designated sets, each slot designated exactly
twice; two walks are the same if they differ by relabelling squares or by a D4 symmetry.
Pair facts: a walk containing two squares whose pair is INFEASIBLE in the pair table cannot
be the designated walk of any packing (the designated sets are subsets of the actual ones and
the pair verdicts are monotone), so it is dropped.
    python walks247.py --pairs results/pairs247_window_0.01.jsonl [--slotmet] -> results/walks247_<tag>.jsonl
"""
import argparse
import collections
import itertools
import json
import os
import sys
import time

import geo247 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ADJ_CORNER = {('BL', 'BL10'): 'BR', ('BL', 'BL01'): 'TL', ('BR', 'BR10'): 'BL', ('BR', 'BR01'): 'TR',
              ('TR', 'TR10'): 'TL', ('TR', 'TR01'): 'BR', ('TL', 'TL10'): 'TR', ('TL', 'TL01'): 'BL'}
SLOT_CORNERS = {z: (z[:2], ADJ_CORNER[(z[:2], z)]) for z in G.SLOT_RING}     # (own, adjacent)


class Facts(object):
    def __init__(self, paths):
        self.status = {}
        for p in paths:
            for line in open(p):
                r = json.loads(line)
                if r['status'] == 'INFEASIBLE' or r['key'] not in self.status:
                    self.status[r['key']] = r['status']
        self.cache = {}

    def forbidden(self, *specs):
        k = tuple(sorted(G.spec_str(s) for s in specs))
        if k not in self.cache:
            self.cache[k] = self.status.get(G.tuple_key(list(specs))) == 'INFEASIBLE'
        return self.cache[k]

    def n_infeasible(self):
        return sum(1 for v in self.status.values() if v == 'INFEASIBLE')


def corner_options(c, facts, slotmet=False):
    """unordered pairs (D1, D2) of slot subsets for c's two meeters, pair-fact filtered."""
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


def adj_ok(o1, o2, facts):
    return not (facts.forbidden(o1[2], o2[2]) or facts.forbidden(o1[2], o2[3]) or
                facts.forbidden(o1[3], o2[2]) or facts.forbidden(o1[3], o2[3]))


def free_covers(facts):
    """multisets of <= 3 free sets grouped by their slot-count vector (entries <= 2), FF-filtered."""
    F = G.free_sets()
    specs = {f: ('F', f) for f in F}
    ok2 = {(a, b): not facts.forbidden(specs[a], specs[b]) for a in F for b in F}
    groups = collections.defaultdict(list)
    for r in range(0, 4):
        for comb in itertools.combinations_with_replacement(F, r):
            if any(not ok2[(comb[i], comb[j])] for i in range(r) for j in range(i + 1, r)):
                continue
            cnt = collections.Counter(z for f in comb for z in f)
            if any(v > 2 for v in cnt.values()):
                continue
            groups[tuple(cnt.get(z, 0) for z in G.SLOT_RING)].append(comb)
    return groups, specs


def walk_record(opts, cover):
    """the walk as (per corner sorted pair of slot subsets, free multiset)."""
    return tuple((c, opts[c][0], opts[c][1]) for c in G.CORNERS), tuple(sorted(cover))


def canon_walk(rec):
    corners, frees = rec
    best = None
    for m in G.D4:
        cs = []
        for c, d1, d2 in corners:
            c2 = m['%s00' % c][:2]
            e1 = tuple(sorted((m[z] for z in d1), key=G.RING.index))
            e2 = tuple(sorted((m[z] for z in d2), key=G.RING.index))
            cs.append((c2, min(e1, e2), max(e1, e2)))
        cs.sort()
        fs = tuple(sorted(tuple(sorted((m[z] for z in f), key=G.RING.index)) for f in frees))
        k = (tuple(cs), fs)
        if best is None or k < best:
            best = k
    return best


def letters(rec):
    """per slot the two suppliers' kinds O (own) A (adjacent corner) F (free), sorted."""
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


def enumerate_walks(facts, slotmet=False, log=print):
    opts = {c: corner_options(c, facts, slotmet) for c in G.CORNERS}
    log('corner options: ' + ', '.join('%s %d' % (c, len(opts[c])) for c in G.CORNERS))
    groups, fspecs = free_covers(facts)
    log('free covers: %d demand vectors, %d multisets' % (len(groups), sum(len(v) for v in groups.values())))
    # compatibility of a free set with a corner option
    fcomp = {}

    def compat(f, o):
        k = (f, o[0], o[1], o[2][1])
        if k not in fcomp:
            fcomp[k] = not (facts.forbidden(fspecs[f], o[2]) or facts.forbidden(fspecs[f], o[3]))
        return fcomp[k]

    def profile(c, o):
        cnt = collections.Counter(z for d in (o[0], o[1]) for z in d)
        return cnt
    n_config = 0
    walks = {}
    raw = 0
    for oBL in opts['BL']:
        for oBR in opts['BR']:
            if not adj_ok(oBL, oBR, facts):
                continue
            for oTR in opts['TR']:
                if not adj_ok(oBR, oTR, facts):
                    continue
                for oTL in opts['TL']:
                    if not (adj_ok(oTR, oTL, facts) and adj_ok(oTL, oBL, facts)):
                        continue
                    o = {'BL': oBL, 'BR': oBR, 'TR': oTR, 'TL': oTL}
                    cnt = collections.Counter()
                    for c in G.CORNERS:
                        cnt.update(profile(c, o[c]))
                    if any(v > 2 for v in cnt.values()):
                        continue
                    r = tuple(2 - cnt.get(z, 0) for z in G.SLOT_RING)
                    n_config += 1
                    for cover in groups.get(r, ()):
                        if all(compat(f, o[c]) for f in cover for c in G.CORNERS):
                            raw += 1
                            rec = walk_record({c: (o[c][0], o[c][1]) for c in G.CORNERS}, cover)
                            k = canon_walk(rec)
                            if k not in walks:
                                walks[k] = rec
    log('corner configurations %d, raw walks %d, walks up to D4 %d' % (n_config, raw, len(walks)))
    return walks, raw, n_config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pairs', nargs='+', required=True)
    ap.add_argument('--slotmet', action='store_true')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    t0 = time.time()
    facts = Facts([os.path.join(ATT, p) if not os.path.isabs(p) else p for p in a.pairs])
    print('pair facts: %d rows, %d INFEASIBLE' % (len(facts.status), facts.n_infeasible()))
    walks, raw, n_config = enumerate_walks(facts, a.slotmet)
    tag = a.tag or (os.path.basename(a.pairs[0]).replace('pairs247_', '').replace('.jsonl', '') + ('_slotmet' if a.slotmet else ''))
    out = os.path.join(ATT, 'results', 'walks247_%s.jsonl' % tag)
    with open(out, 'w') as f:
        f.write(json.dumps({'kind': 'summary', 'pairs': a.pairs, 'slotmet': a.slotmet, 'n_infeasible_pairs': facts.n_infeasible(),
                            'corner_configs': n_config, 'raw_walks': raw, 'walks_d4': len(walks), 'seconds': time.time() - t0}) + '\n')
        for k, rec in sorted(walks.items()):
            corners, frees = k
            f.write(json.dumps({'corners': [[c, list(d1), list(d2)] for c, d1, d2 in corners],
                                'free': [list(x) for x in frees], 'n_free_used': len(frees),
                                'free_incidences': sum(len(x) for x in frees), 'letters': letters(k)}) + '\n')
    print('wrote %s (%.0f s)' % (out, time.time() - t0))


if __name__ == '__main__':
    main()
