"""A31 Level 1: decoration fan-out of a Level-0 survivor.

Decoration menu (as in the brief):
  square-square edge : corner-of-i on edge-of-j (4 corners x 4 edges x 2 owners = 32)
                       + flush (4x4 edge pairings = 16)                      = 48 raw
  square-wall  edge  : corner-on-wall (4) + flush (4)                        =  8 raw

GAUGE.  A square carries no marking, so rotating its corner/edge labels by 90 deg is
the same physical square.  Fixing the gauge phi_i = theta_i mod 90 in [0,90) fixes the
labels, and then
  * flush(i,j): 4 surviving pairings (which side of j; i's side is then forced)
  * corner(i on j): the touching corner of i is the extreme point of i in the direction
    -n(edge of j), i.e. (theta_i+45+90c) is within 45 deg of (theta_j+90e+180); with
    phi in [0,90) this forces (e-c) mod 4 = 3 when phi_i > phi_j and = 2 when
    phi_i < phi_j, and is IMPOSSIBLE for (e-c) mod 4 in {0,1}.  So 2 owners x 2 signs
    x 4 index choices = 16 survive out of 32.
  * square-wall: flush pins phi_i = 0 exactly (1 labelling in gauge); corner needs
    phi_i in (0,90) (1 labelling in gauge).
So the gauge-fixed menu is 20 per SS edge and 2 per SW edge, and each gauge-fixed
label is one distinct physical arrangement type.  The brief's raw menu (48 per SS edge,
8 per SW edge) is the same information in an un-gauge-fixed encoding: it is redundant,
and non-uniformly so (16 flush labels cover 4 arrangements, 32 corner labels cover 16),
so all counts below are reported in the gauge-fixed encoding with the raw menu quoted
only as the brief's baseline.

TILT PROPAGATION (complete for the tilt subsystem, to a fixpoint):
  flush           -> phi_i = phi_j                    (union-find class)
  wall-flush      -> phi_i = 0                        (class merged into the zero class)
  corner-on-edge  -> strict inequality between the two classes, direction given
  wall-corner     -> phi_i != 0
Feasible  <=>  no strict edge inside a class, the strict digraph on classes is
ACYCLIC, and the zero class has in-degree 0 (nothing can sit below phi = 0).
Any such system is realisable in [0,90) by topological value assignment, so this test
is exact for the tilt subsystem (positions are NOT checked - see the gap list).
"""
import os, sys, json, math, itertools, statistics
import numpy as np
import lib0 as L

_ao_cache = {}


def acyclic_orientations(n, edges):
    """Number of acyclic orientations of a simple graph on n labelled vertices."""
    if n == 0:
        return 1
    key = (n, tuple(sorted(edges)))
    v = _ao_cache.get(key)
    if v is not None:
        return v
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    full = (1 << n) - 1
    memo = {0: 1}

    def a(S):
        if S in memo:
            return memo[S]
        tot = 0
        # inclusion-exclusion over non-empty independent subsets T of S (the sources)
        sub = S
        while True:
            if sub:
                ok = True
                t = sub
                while t:
                    b = t & -t
                    i = b.bit_length() - 1
                    t ^= b
                    if adj[i] & sub:
                        ok = False
                        break
                if ok:
                    sgn = -1 if (bin(sub).count('1') % 2 == 0) else 1
                    tot += sgn * a(S & ~sub)
            if sub == 0:
                break
            sub = (sub - 1) & S
        memo[S] = tot
        return tot

    v = a(full)
    _ao_cache[key] = v
    return v


def fanout(k, gmask, wm):
    adj, ss_edges = L.mask_to_adj(gmask, k)
    Ess = len(ss_edges)
    Esw = sum(L.POP[m] for m in wm)
    raw_menu = 48 ** Ess * 8 ** Esw
    gauge_menu = 20 ** Ess * 2 ** Esw
    wall_sq = [i for i in range(k) if wm[i]]
    total = 0
    for fl in range(1 << Ess):
        parent = list(range(k))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        nf = 0
        for e, (i, j) in enumerate(ss_edges):
            if (fl >> e) & 1:
                nf += 1
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
        rest = [(i, j) for e, (i, j) in enumerate(ss_edges) if not ((fl >> e) & 1)]
        if any(find(i) == find(j) for i, j in rest):
            continue                       # a strict edge inside a flush class
        cls = sorted(set(find(i) for i in range(k)))
        cid = {c: t for t, c in enumerate(cls)}
        wcls = sorted(set(find(i) for i in wall_sq))
        mult = (4 ** nf) * (8 ** (Ess - nf))
        for zsel in range(1 << len(wcls)):
            pinned = set(wcls[t] for t in range(len(wcls)) if (zsel >> t) & 1)
            # merge all pinned classes into one node z
            if pinned:
                zid = min(cid[c] for c in pinned)
                remap = {}
                nxt = 0
                for c in cls:
                    if c in pinned:
                        continue
                    remap[cid[c]] = nxt
                    nxt += 1
                zpos = nxt
                nn = nxt + 1
                for c in pinned:
                    remap[cid[c]] = zpos
            else:
                remap = {t: t for t in range(len(cls))}
                zpos = None
                nn = len(cls)
            bad = False
            qe = set()
            for i, j in rest:
                u, v = remap[cid[find(i)]], remap[cid[find(j)]]
                if u == v:
                    bad = True
                    break
                qe.add((min(u, v), max(u, v)))
            if bad:
                continue
            if zpos is None:
                ao = acyclic_orientations(nn, qe)
            else:
                # z must be a source: orientations with z a source correspond
                # bijectively to acyclic orientations of Q - z
                rm = {}
                t = 0
                for x in range(nn):
                    if x == zpos:
                        continue
                    rm[x] = t
                    t += 1
                qe2 = [(rm[a], rm[b]) for a, b in qe if a != zpos and b != zpos]
                ao = acyclic_orientations(nn - 1, qe2)
            total += mult * ao
    return dict(Ess=Ess, Esw=Esw, raw_menu=raw_menu, gauge_menu=gauge_menu,
                gauge_surv=total)


def main():
    here = os.path.dirname(__file__)
    outdir = os.path.join(here, '..', 'results')
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6]
    cap = int(os.environ.get('A31_L1_CAP', '160'))
    report = {}
    for k in ks:
        p = os.path.join(outdir, 'level0_k%d.json' % k)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        items = []
        for s in d['samples']:
            w = s['main'] / max(1, s['nsample'])
            for wm in s['w']:
                items.append((s['gmask'], tuple(wm), w))
        rng = np.random.default_rng(7)
        cap_k = cap if k <= 6 else max(30, cap // 4)
        if len(items) > cap_k:
            idx = rng.choice(len(items), cap_k, replace=False)
            items = [items[i] for i in idx]
        rows = []
        for gmask, wm, w in items:
            r = fanout(k, gmask, wm)
            r['gmask'] = gmask
            r['w'] = list(wm)
            r['weight'] = w
            r['E'] = r['Ess'] + r['Esw']
            r['kill_gauge'] = 1.0 - r['gauge_surv'] / r['gauge_menu']
            r['per_edge'] = r['gauge_surv'] ** (1.0 / r['E']) if r['E'] else 1.0
            rows.append(r)
            print('k=%d gmask=%d E=%d(%d+%d) menu=%.3e surv=%.3e kill=%.4f pe=%.2f'
                  % (k, gmask, r['E'], r['Ess'], r['Esw'], r['gauge_menu'],
                     r['gauge_surv'], r['kill_gauge'], r['per_edge']), flush=True)
        if not rows:
            continue
        wts = np.array([r['weight'] for r in rows], dtype=float)
        wts /= wts.sum()
        lg = np.array([math.log(max(1, r['gauge_surv'])) for r in rows])
        pe = np.array([r['per_edge'] for r in rows])
        kill = np.array([r['kill_gauge'] for r in rows])
        E = np.array([r['E'] for r in rows], dtype=float)
        report['k%d' % k] = dict(
            n_graphs=len(rows),
            E_mean=float((wts * E).sum()), E_median=float(np.median(E)),
            gauge_surv_median=float(np.exp(np.median(lg))),
            gauge_surv_max=float(np.exp(lg.max())),
            gauge_surv_geomean_weighted=float(np.exp((wts * lg).sum())),
            per_edge_median=float(np.median(pe)), per_edge_max=float(pe.max()),
            per_edge_weighted=float((wts * pe).sum()),
            kill_median=float(np.median(kill)),
            kill_weighted=float((wts * kill).sum()),
            zero_surv=int((np.array([r['gauge_surv'] for r in rows]) == 0).sum()),
            rows=rows)
        with open(os.path.join(outdir, 'level1.json'), 'w') as fh:
            json.dump(report, fh, indent=1)
    print(json.dumps({kk: {a: b for a, b in v.items() if a != 'rows'}
                      for kk, v in report.items()}, indent=1))


if __name__ == '__main__':
    main()
