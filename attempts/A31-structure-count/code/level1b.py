"""A31 Level 1b: how much of the Level-1 decoration fan-out survives the
ROTATION-SYSTEM (planar embedding) consistency test that Level 1 ignores.

A decoration says, for every contact of square i, WHERE on i's boundary it sits.  The
boundary of a square, counterclockwise, is the 8-cycle
      edge0, corner0, edge1, corner1, edge2, corner2, edge3, corner3
(edge e has outward normal phi_i + 90e, corner c points at phi_i + 45 + 90c), and
  * flush(i,j) on i's edge a          -> slot edge a
  * corner-of-j on i's edge e         -> slot edge e
  * corner c of i on j's edge         -> slot corner c
  * wall-flush  on wall b             -> slot edge a(b),   a = 2,3,0,1 for L,B,R,T
  * wall-corner on wall b             -> slot corner c(b), c = 1,2,3,0 for L,B,R,T
So the decoration FIXES the cyclic order of the contacts around each square (up to the
order of contacts sharing one slot), i.e. it fixes the rotation system of the contact
graph.  In L4's drawing the edge from c_i leaves through its contact point, so that
rotation system must be a genus-0 embedding.  Restricting to the square-square
subgraph (wall nodes have unknown rotation) gives a SOUND necessary test.

Measured by Monte Carlo over the gauge-fixed menu; the tilt-only rate is checked
against the exact Level-1 count.
"""
import os, sys, json, math, itertools, random
import numpy as np
import lib0 as L
import level1 as L1

WALL_FLUSH_EDGE = {0: 2, 1: 3, 2: 0, 3: 1}     # L,B,R,T
WALL_CORNER = {0: 1, 1: 2, 2: 3, 3: 0}


def genus0(k, rot, edges):
    """rot[v] = list of neighbours in cyclic order.  True iff this rotation system
    embeds in the sphere (Euler per connected component)."""
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
    # components of the SS graph restricted to vertices with degree >= 1
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    vis, comps = set(), 0
    V = 0
    for s in adj:
        if s in vis:
            continue
        comps += 1
        st = [s]
        vis.add(s)
        while st:
            x = st.pop()
            V += 1
            for y in adj[x]:
                if y not in vis:
                    vis.add(y)
                    st.append(y)
    return V - len(edges) + F == 2 * comps


def sample_once(k, ss, sw, rnd):
    """One uniform draw from the gauge menu.  Returns (constraints, slots)."""
    cons = []          # ('eq',i,j) | ('lt',i,j) | ('zero',i) | ('nz',i)
    slot = {i: [] for i in range(k)}     # (slotindex, neighbour or None)
    for (i, j) in ss:
        o = rnd.randrange(20)
        if o < 4:                                  # flush, o = which edge of j
            b = o
            a = (b + 2) % 4
            cons.append(('eq', i, j))
            slot[i].append((2 * a, j))
            slot[j].append((2 * b, i))
        else:
            t = o - 4
            owner = t // 8            # 0 -> i owns the corner
            e = (t % 8) // 2          # edge index of the receiving square
            sg = t % 2                # 0: phi_owner > phi_other, 1: <
            a, b = (i, j) if owner == 0 else (j, i)
            c = (e - 3) % 4 if sg == 0 else (e - 2) % 4
            cons.append(('lt', b, a) if sg == 0 else ('lt', a, b))
            slot[a].append((2 * c + 1, b))
            slot[b].append((2 * e, a))
    for (i, b) in sw:
        if rnd.randrange(2) == 0:
            cons.append(('zero', i))
            slot[i].append((2 * WALL_FLUSH_EDGE[b], None))
        else:
            cons.append(('nz', i))
            slot[i].append((2 * WALL_CORNER[b] + 1, None))
    return cons, slot


def tilt_ok(k, cons):
    parent = list(range(k + 1))          # k = the zero node

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
    nz = set()
    for c in cons:
        if c[0] == 'nz':
            nz.add(find(c[1]))
    z = find(k)
    if z in nz:
        return False
    lt = set()
    for c in cons:
        if c[0] == 'lt':
            a, b = find(c[1]), find(c[2])
            if a == b:
                return False
            if b == z:
                return False             # nothing can sit below phi = 0
            lt.add((a, b))
    # acyclicity
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


def rot_ok(k, ss, slot, tie_cap=64):
    """True iff SOME resolution of within-slot ties gives a genus-0 rotation system."""
    per = []
    for i in range(k):
        items = sorted(slot[i], key=lambda x: (x[0], -1 if x[1] is None else x[1]))
        groups = []
        t = 0
        while t < len(items):
            u = t
            while u < len(items) and items[u][0] == items[t][0]:
                u += 1
            groups.append([x[1] for x in items[t:u]])
            t = u
        opts = [1]
        for g in groups:
            opts[0] *= math.factorial(len(g))
        per.append((groups, opts[0]))
    total = 1
    for _, o in per:
        total *= o
    if total > tie_cap:
        # too many tie resolutions: try a bounded random subset (reported as a
        # possible OVER-acceptance, never an under-count)
        rnd = random.Random(0)
        for _ in range(tie_cap):
            rot = {}
            for i in range(k):
                seq = []
                for g in per[i][0]:
                    g = list(g)
                    rnd.shuffle(g)
                    seq += g
                rot[i] = [x for x in seq if x is not None]
            if genus0(k, rot, ss):
                return True
        return False
    for choice in itertools.product(*[list(itertools.product(
            *[itertools.permutations(g) for g in per[i][0]])) for i in range(k)]):
        rot = {}
        for i in range(k):
            seq = []
            for g in choice[i]:
                seq += list(g)
            rot[i] = [x for x in seq if x is not None]
        if genus0(k, rot, ss):
            return True
    return False


def measure(k, gmask, wm, n=20000, seed=1):
    adj, ss = L.mask_to_adj(gmask, k)
    sw = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    rnd = random.Random(seed)
    nt = nb = 0
    for _ in range(n):
        cons, slot = sample_once(k, ss, sw, rnd)
        t = tilt_ok(k, cons)
        if t:
            nt += 1
            if rot_ok(k, ss, slot):
                nb += 1
    return nt / n, nb / n


def main():
    here = os.path.dirname(__file__)
    outdir = os.path.join(here, '..', 'results')
    ks = [int(x) for x in sys.argv[1:]] or [4, 5, 6]
    ng = int(os.environ.get('A31_L1B_GRAPHS', '25'))
    ns = int(os.environ.get('A31_L1B_SAMPLES', '20000'))
    d1 = json.load(open(os.path.join(outdir, 'level1.json')))
    rep = {}
    for k in ks:
        rows = d1['k%d' % k]['rows']
        rng = np.random.default_rng(11)
        pick = rng.choice(len(rows), min(ng, len(rows)), replace=False)
        recs = []
        for t in pick:
            r = rows[int(t)]
            pt, pb = measure(k, r['gmask'], tuple(r['w']), n=ns)
            exact = r['gauge_surv'] / r['gauge_menu']
            recs.append(dict(gmask=r['gmask'], w=r['w'], E=r['E'],
                             mc_tilt=pt, exact_tilt=exact,
                             mc_tilt_and_rot=pb,
                             rot_kept_given_tilt=(pb / pt if pt else 0.0),
                             weight=r['weight']))
            print('k=%d g=%d E=%d  tilt mc=%.4f exact=%.4f   +rot=%.5f  (rot keeps '
                  '%.4f)' % (k, r['gmask'], r['E'], pt, exact, pb,
                             pb / pt if pt else 0), flush=True)
        w = np.array([x['weight'] for x in recs], dtype=float)
        w /= w.sum()
        keep = np.array([x['rot_kept_given_tilt'] for x in recs])
        err = np.array([abs(x['mc_tilt'] - x['exact_tilt']) /
                        max(1e-9, x['exact_tilt']) for x in recs])
        rep['k%d' % k] = dict(n_graphs=len(recs), samples=ns,
                              rot_keep_weighted=float((w * keep).sum()),
                              rot_keep_median=float(np.median(keep)),
                              rot_keep_min=float(keep.min()),
                              rot_keep_max=float(keep.max()),
                              mc_vs_exact_rel_err_max=float(err.max()),
                              rows=recs)
        with open(os.path.join(outdir, 'level1b.json'), 'w') as fh:
            json.dump(rep, fh, indent=1)
    print(json.dumps({a: {x: y for x, y in b.items() if x != 'rows'}
                      for a, b in rep.items()}, indent=1))


if __name__ == '__main__':
    main()
