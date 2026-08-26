"""A32 mode D: the DECORATED partial-structure branch-and-bound.

A node is a contact graph (fixed, from the mode-G frontier) together with a
decoration committed on a PREFIX of its edges.  Branch move = commit the
decoration class of the next edge (20 gauge-fixed labels per square-square edge,
2 per square-wall edge; the gauge is A31's, see level1.py).

MONOTONE kills at every node (all three only accumulate constraints):
  D1  tilt propagation fixpoint  (union-find equalities + strict-order acyclicity
      + the zero class has in-degree 0)                       -- exact, A31 level1
  D2  rotation-system consistency: the committed decoration fixes the cyclic order
      of the committed contacts around every square, and a genus-0 embedding stays
      genus-0 when edges are deleted, so a non-spherical partial rotation system
      kills every completion                                  -- A31 level1b
  D3  L2 collinearity for a square whose degree is already 2 in the (fixed) graph:
      force balance makes the two contact forces antiparallel with a common line of
      action.  Cases with an i-INTRINSIC direction on both sides are decided here:
        * both intrinsic (flush / receiving a corner / wall-flush): the two contacts
          must sit on OPPOSITE edges of i, else kill;
        * intrinsic + wall-corner: the intrinsic side forces phi_i = 0 and the
          wall-corner side forbids it -> kill;
        * two wall-corners: the two wall normals would have to be antiparallel, i.e.
          opposite walls, which L5(b) forbids -> kill.
      Cases whose direction is set by the NEIGHBOUR's tilt are DEFERRED (counted as
      surviving and logged) -- that is the thin branch the ledger keeps flagged.

Tree size is estimated with Knuth's random-path estimator (unbiased) because the
decorated tree is far too large to enumerate above k = 3; exact DFS is used on small
graphs and validated against A31's exact Level-1 counts.
"""
import os
import sys
import json
import math
import time
import random
import itertools

import core as C
import lib0 as L

WALL_FLUSH_EDGE = {0: 2, 1: 3, 2: 0, 3: 1}     # L,B,R,T
WALL_CORNER = {0: 1, 1: 2, 2: 3, 3: 0}

DSTAGES = ['D1_tilt', 'D2_rotation', 'D3_L2collinear']


def edge_list(k, adj, wm):
    ss = []
    for i in range(k):
        for j in range(i + 1, k):
            if (adj[i] >> j) & 1:
                ss.append((i, j))
    sw = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    return ss, sw


def label_effect(k, kind, e, o):
    """(constraints, slot additions) of decoration label `o` on edge `e`.
    slot addition = (square, slotindex 0..7, neighbour or None, intrinsic?)"""
    cons = []
    slots = []
    if kind == 'ss':
        i, j = e
        if o < 4:
            b = o
            a = (b + 2) % 4
            cons.append(('eq', i, j))
            slots.append((i, 2 * a, j, True))
            slots.append((j, 2 * b, i, True))
        else:
            t = o - 4
            owner = t // 8
            ee = (t % 8) // 2
            sg = t % 2
            a, b = (i, j) if owner == 0 else (j, i)
            c = (ee - 3) % 4 if sg == 0 else (ee - 2) % 4
            cons.append(('lt', b, a) if sg == 0 else ('lt', a, b))
            slots.append((a, 2 * c + 1, b, False))     # a's corner -> extrinsic
            slots.append((b, 2 * ee, a, True))         # b receives -> intrinsic
    else:
        i, b = e
        if o == 0:
            cons.append(('zero', i))
            slots.append((i, 2 * WALL_FLUSH_EDGE[b], None, True))
        else:
            cons.append(('nz', i))
            slots.append((i, 2 * WALL_CORNER[b] + 1, None, 'wallcorner'))
    return cons, slots


# ------------------------------------------------------------------ D1 tilt
def tilt_ok(k, cons):
    parent = list(range(k + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for c in cons:
        if c[0] == 'eq':
            a, b = find(c[1]), find(c[2])
            if a != b:
                parent[a] = b
        elif c[0] == 'zero':
            a, b = find(c[1]), find(k)
            if a != b:
                parent[a] = b
    z = find(k)
    for c in cons:
        if c[0] == 'nz' and find(c[1]) == z:
            return False
    lt = set()
    for c in cons:
        if c[0] == 'lt':
            a, b = find(c[1]), find(c[2])
            if a == b or b == z:
                return False
            lt.add((a, b))
    nodes = set()
    for a, b in lt:
        nodes.add(a)
        nodes.add(b)
    out = {v: [] for v in nodes}
    indeg = {v: 0 for v in nodes}
    for a, b in lt:
        out[a].append(b)
        indeg[b] += 1
    q = [v for v in nodes if indeg[v] == 0]
    seen = 0
    while q:
        v = q.pop()
        seen += 1
        for w in out[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    return seen == len(nodes)


# -------------------------------------------------------------- D2 rotation
def genus0(rot, edges):
    if not edges:
        return True
    pos = {}
    for v, r in rot.items():
        for t, u in enumerate(r):
            pos[(v, u)] = t
    darts = set()
    for a, b in edges:
        darts.add((a, b))
        darts.add((b, a))
    seen = set()
    F = 0
    for d in darts:
        if d in seen:
            continue
        F += 1
        cur = d
        while cur not in seen:
            seen.add(cur)
            u, v = cur
            r = rot[v]
            t = (pos[(v, u)] + 1) % len(r)
            cur = (v, r[t])
    adjm = {}
    for a, b in edges:
        adjm.setdefault(a, []).append(b)
        adjm.setdefault(b, []).append(a)
    vis, comps, V = set(), 0, 0
    for s in adjm:
        if s in vis:
            continue
        comps += 1
        st = [s]
        vis.add(s)
        while st:
            x = st.pop()
            V += 1
            for y in adjm[x]:
                if y not in vis:
                    vis.add(y)
                    st.append(y)
    return V - len(edges) + F == 2 * comps


def rot_ok(k, slots, ss_committed, tie_cap=48):
    """slots[i] = list of (slotindex, neighbour or None).  True iff SOME resolution
    of within-slot ties gives a genus-0 rotation system of the committed SS edges."""
    if not ss_committed:
        return True
    per = []
    total = 1
    for i in range(k):
        items = sorted(slots[i], key=lambda x: (x[0], -1 if x[1] is None else x[1]))
        groups = []
        t = 0
        while t < len(items):
            u = t
            while u < len(items) and items[u][0] == items[t][0]:
                u += 1
            groups.append([x[1] for x in items[t:u]])
            t = u
        m = 1
        for g in groups:
            m *= math.factorial(len(g))
        total *= m
        per.append(groups)
    if total > tie_cap:
        rnd = random.Random(0)
        for _ in range(tie_cap):
            rot = {}
            for i in range(k):
                seq = []
                for g in per[i]:
                    g = list(g)
                    rnd.shuffle(g)
                    seq += g
                rot[i] = [x for x in seq if x is not None]
            if genus0(rot, ss_committed):
                return True
        return False
    for choice in itertools.product(*[list(itertools.product(
            *[itertools.permutations(g) for g in per[i]])) for i in range(k)]):
        rot = {}
        for i in range(k):
            seq = []
            for g in choice[i]:
                seq += list(g)
            rot[i] = [x for x in seq if x is not None]
        if genus0(rot, ss_committed):
            return True
    return False


# ------------------------------------------------------------- D3 L2 struts
def l2_ok(k, totdeg, slots, done_count, defer):
    """L2 for squares whose (fixed) total degree is 2 and both contacts committed."""
    for i in range(k):
        if totdeg[i] != 2 or done_count[i] != 2:
            continue
        (s1, _, k1), (s2, _, k2) = slots[i][0], slots[i][1]
        i1 = k1 is True
        i2 = k2 is True
        w1 = k1 == 'wallcorner'
        w2 = k2 == 'wallcorner'
        if i1 and i2:
            if s1 % 2 or s2 % 2:
                continue
            if ((s1 // 2) + 2) % 4 != (s2 // 2) % 4:
                return False
        elif (i1 and w2) or (i2 and w1):
            return False
        elif w1 and w2:
            return False
        else:
            defer[0] += 1
    return True


# ------------------------------------------------------------------- engine
class DTree:
    def __init__(self, k, adj, wm, use_rot=True, use_l2=True):
        self.k = k
        ss, sw = edge_list(k, adj, wm)
        self.ss, self.sw = ss, sw
        self.order = [('ss', e) for e in ss] + [('sw', e) for e in sw]
        self.nedge = len(self.order)
        self.menu = [20 if kind == 'ss' else 2 for kind, _ in self.order]
        self.use_rot = use_rot
        self.use_l2 = use_l2
        self.totdeg = [0] * k
        for i, j in ss:
            self.totdeg[i] += 1
            self.totdeg[j] += 1
        for i, b in sw:
            self.totdeg[i] += 1
        self.kills = {s: 0 for s in DSTAGES}
        self.visited = 0
        self.defer = [0]

    def children(self, state, d):
        """Surviving labels at depth d given the committed state."""
        cons, slots, done, ssc = state
        kind, e = self.order[d]
        good = []
        for o in range(self.menu[d]):
            nc, ns = label_effect(self.k, kind, e, o)
            cons2 = cons + nc
            self.visited += 1
            if not tilt_ok(self.k, cons2):
                self.kills['D1_tilt'] += 1
                continue
            slots2 = [list(x) for x in slots]
            done2 = list(done)
            for (sq, si, nb, intr) in ns:
                slots2[sq].append((si, nb, intr))
                done2[sq] += 1
            ssc2 = ssc + ([e] if kind == 'ss' else [])
            if self.use_rot:
                sl = [[(a, b) for (a, b, c) in slots2[i]] for i in range(self.k)]
                if not rot_ok(self.k, sl, ssc2):
                    self.kills['D2_rotation'] += 1
                    continue
            if self.use_l2 and not l2_ok(self.k, self.totdeg, slots2, done2,
                                         self.defer):
                self.kills['D3_L2collinear'] += 1
                continue
            good.append((o, (cons2, slots2, done2, ssc2)))
        return good

    def root(self):
        return ([], [[] for _ in range(self.k)], [0] * self.k, [])

    def enumerate_exact(self, cap=2_000_000):
        """Exact DFS.  Returns (frontier per depth, leaves) or None if > cap."""
        front = [0] * (self.nedge + 1)
        front[0] = 1
        stack = [(0, self.root())]
        n = 0
        while stack:
            d, st = stack.pop()
            if d == self.nedge:
                continue
            for o, st2 in self.children(st, d):
                front[d + 1] += 1
                n += 1
                if n > cap:
                    return None
                stack.append((d + 1, st2))
        return front

    def knuth(self, trials, seed=0):
        """Knuth's random-path estimator: unbiased estimate of the node count at
        every depth, plus the mean surviving branching factor per depth."""
        rnd = random.Random(seed)
        est = [0.0] * (self.nedge + 1)
        est2 = [0.0] * (self.nedge + 1)
        bf = [[0.0, 0] for _ in range(self.nedge)]
        for _ in range(trials):
            st = self.root()
            w = 1.0
            est[0] += 1.0
            est2[0] += 1.0
            for d in range(self.nedge):
                ch = self.children(st, d)
                bf[d][0] += len(ch)
                bf[d][1] += 1
                if not ch:
                    w = 0.0
                    break
                w *= len(ch)
                est[d + 1] += w
                est2[d + 1] += w * w
                st = ch[rnd.randrange(len(ch))][1]
            if w == 0.0:
                continue
        out = []
        for d in range(self.nedge + 1):
            m = est[d] / trials
            v = est2[d] / trials - m * m
            out.append((m, math.sqrt(max(0.0, v) / trials)))
        return out, [(b[0] / b[1] if b[1] else 0.0) for b in bf]
