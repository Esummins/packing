"""A247: the RING of corner options and its transfer matrices (used by walks247).
Closed-form pair kills (lemma_kill), the per-corner option lists, the free multisets and the
adjacency / slot-count matrices between consecutive corners; Ring.count is the exact number of
labelled walks for one free multiset (trace of the product of the four wall matrices)."""
import collections
import itertools

import numpy as np

import geo247 as G

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


def type_f_pair(c, d1, d2):
    """the PI's TYPE-F picture (A246 rule E): a flat meeter on one wall meets c00, its own slot
    on that wall and possibly the far slot of that wall; the tilted partner meets c00, the other
    own slot and possibly the far slot of the other wall.  A CONDITIONAL filter (the type-F / T
    dichotomy is not a proved exhaustive case split at level eta)."""
    own = ('%s01' % c, '%s10' % c)
    far = {z: [f for f in G.SLOTS_OF[c] if f[:2] != c and f[2:] == z[2:]] for z in own}
    for a, b in ((own[0], own[1]), (own[1], own[0])):
        A = [(a,), (a,) + tuple(far[a])]
        B = [(b,), (b,) + tuple(far[b])]
        for x in A:
            for y in B:
                if {tuple(sorted(x, key=G.RING.index)), tuple(sorted(y, key=G.RING.index))} == {d1, d2}:
                    return True
    return False


def corner_options(c, facts, slotmet=False, typef=False):
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
            if typef and not type_f_pair(c, d1, d2):
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

    def __init__(self, facts, slotmet=False, typef=False):
        self.facts = facts
        self.opts = {c: corner_options(c, facts, slotmet, typef) for c in G.CORNERS}
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


