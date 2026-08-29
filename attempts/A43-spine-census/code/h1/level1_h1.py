"""A43-H1 Level 1: A31's decoration fan-out (verbatim, for regression) + the new columns.

A31 path (`fanout`) is unchanged -> gauge_surv reproduces attempts/A31-structure-count/
results/level1.json exactly under the same sampling protocol (seed 7, cap 160).

NEW, computed in a WALL-EDGE-RESOLVED re-enumeration (`fanout_we`, see gap G-A43-L1):
  N3  no zero-pinned tilt class      EXACT-EXISTENTIAL  (necessary for A21 THM3 to bite at k=11)
  N4  #flush >= 3k+1-E               CONDITIONAL        (Maxwell-conditional flush-mandatory)
  N7d 4-cycle with all four links corner-on-edge, tilt classes admitting a common assignment
      in (18,45) deg                 APPROX             (never composed)
"""
import os, sys, json, math, itertools, time
import numpy as np
import lib0 as L
from level1_ao import acyclic_orientations

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'h1')


# ------------------------------------------------------------------ A31 fanout (verbatim)
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
            continue
        cls = sorted(set(find(i) for i in range(k)))
        cid = {c: t for t, c in enumerate(cls)}
        wcls = sorted(set(find(i) for i in wall_sq))
        mult = (4 ** nf) * (8 ** (Ess - nf))
        for zsel in range(1 << len(wcls)):
            pinned = set(wcls[t] for t in range(len(wcls)) if (zsel >> t) & 1)
            if pinned:
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


# ------------------------------------------------------- wall-edge-resolved fanout + columns
def cycles4(k, ss_edges):
    """edge-index 4-tuples of every 4-cycle of the square-square graph (each cycle once)."""
    ei = {}
    for e, (i, j) in enumerate(ss_edges):
        ei[(i, j)] = e
        ei[(j, i)] = e
    adj = [set() for _ in range(k)]
    for i, j in ss_edges:
        adj[i].add(j)
        adj[j].add(i)
    out = set()
    for a, b, c, d in itertools.permutations(range(k), 4):
        if a != min(a, b, c, d) or b > d:
            continue
        if b in adj[a] and c in adj[b] and d in adj[c] and a in adj[d]:
            out.add(tuple(sorted((ei[(a, b)], ei[(b, c)], ei[(c, d)], ei[(d, a)]))))
    return sorted(out)


def fanout_we(k, gmask, wm, budget=None):
    """Wall-edge-resolved decoration count with the N3/N4/N7d columns.

    Each square-wall edge independently carries flush (phi = 0 for that square's class) or
    corner (phi != 0), which is the 2-per-SW-edge gauge menu A31 declares; A31's own loop
    instead enumerates subsets of wall CLASSES (see gap G-A43-L1), so `we_surv` >= `gauge_surv`.
    """
    adj, ss_edges = L.mask_to_adj(gmask, k)
    Ess = len(ss_edges)
    wedges = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    Esw = len(wedges)
    if budget is not None and Ess + Esw > budget:
        return None
    gauge_menu = 20 ** Ess * 2 ** Esw
    E = Ess + Esw
    need_flush = 3 * k + 1 - E              # N4 threshold on #flush
    C4 = cycles4(k, ss_edges)
    tot = tot_nozero = tot_n4 = tot_n7 = tot_nozero_n4 = 0
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
            continue
        # N7d: some 4-cycle all of whose links are corner-on-edge (strict).  Any acyclic
        # orientation of a 4-cycle is realisable by 4 distinct tilt values inside ANY open
        # interval, in particular (18,45) deg, so the band condition adds nothing here.
        ce4 = any(all(not ((fl >> e) & 1) for e in cyc) for cyc in C4)
        cls = sorted(set(find(i) for i in range(k)))
        cid = {c: t for t, c in enumerate(cls)}
        mult = (4 ** nf) * (8 ** (Ess - nf))
        for ws in range(1 << Esw):
            nwf = bin(ws).count('1')
            pinned = set()
            corner_cls = set()
            okw = True
            for t, (i, b) in enumerate(wedges):
                if (ws >> t) & 1:
                    pinned.add(find(i))
                else:
                    corner_cls.add(find(i))
            if pinned & corner_cls:
                continue                       # phi = 0 and phi != 0 for the same class
            if pinned:
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
                rm = {}
                t = 0
                for x in range(nn):
                    if x == zpos:
                        continue
                    rm[x] = t
                    t += 1
                qe2 = [(rm[a], rm[b]) for a, b in qe if a != zpos and b != zpos]
                ao = acyclic_orientations(nn - 1, qe2)
            v = mult * ao
            tot += v
            nozero = (zpos is None)
            n4 = (nf + nwf) >= need_flush
            if nozero:
                tot_nozero += v
            if n4:
                tot_n4 += v
            if nozero and n4:
                tot_nozero_n4 += v
            if ce4:
                tot_n7 += v
    return dict(Ess=Ess, Esw=Esw, E=E, gauge_menu=gauge_menu, we_surv=tot,
                we_surv_nozero=tot_nozero, we_surv_N4=tot_n4, we_surv_N7d=tot_n7,
                we_surv_nozero_N4=tot_nozero_n4, n_4cycles=len(C4),
                N4_flush_threshold=need_flush,
                frac_N3_nozero=(tot_nozero / tot if tot else 0.0),
                frac_N4=(tot_n4 / tot if tot else 0.0),
                frac_N7d=(tot_n7 / tot if tot else 0.0))


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6, 7]
    cap = int(os.environ.get('A43_L1_CAP', '160'))
    budget = int(os.environ.get('A43_L1_BUDGET', '22'))
    report = {}
    for k in ks:
        p = os.path.join(RES, 'level0_k%d.json' % k)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        items = []
        for s in d['samples']:
            w = s['main'] / max(1, s['nsample'])
            for wmv in s['w']:
                items.append((s['gmask'], tuple(wmv), w))
        rng = np.random.default_rng(7)
        cap_k = cap if k <= 6 else max(30, cap // 4)
        if len(items) > cap_k:
            idx = rng.choice(len(items), cap_k, replace=False)
            items = [items[i] for i in idx]
        rows = []
        t0 = time.time()
        for gmask, wmv, w in items:
            r = fanout(k, gmask, wmv)
            we = fanout_we(k, gmask, wmv, budget)
            r['gmask'] = gmask
            r['w'] = list(wmv)
            r['weight'] = w
            r['E'] = r['Ess'] + r['Esw']
            r['kill_gauge'] = 1.0 - r['gauge_surv'] / r['gauge_menu']
            r['per_edge'] = r['gauge_surv'] ** (1.0 / r['E']) if r['E'] else 1.0
            r['we'] = we
            rows.append(r)
            print('k=%d gmask=%d E=%d(%d+%d) surv=%.3e kill=%.4f  we=%s'
                  % (k, gmask, r['E'], r['Ess'], r['Esw'], r['gauge_surv'], r['kill_gauge'],
                     ('skip' if we is None else 'surv=%.3e N3=%.4f N4=%.4f N7d=%.4f'
                      % (we['we_surv'], we['frac_N3_nozero'], we['frac_N4'],
                         we['frac_N7d']))), flush=True)
        if not rows:
            continue
        wts = np.array([r['weight'] for r in rows], dtype=float)
        wts /= wts.sum()
        lg = np.array([math.log(max(1, r['gauge_surv'])) for r in rows])
        pe = np.array([r['per_edge'] for r in rows])
        kill = np.array([r['kill_gauge'] for r in rows])
        E = np.array([r['E'] for r in rows], dtype=float)
        ok = [i for i, r in enumerate(rows) if r['we'] is not None]
        wok = wts[ok] / wts[ok].sum() if ok else np.zeros(0)

        def wavg(key):
            if not ok:
                return None
            return float((wok * np.array([rows[i]['we'][key] for i in ok])).sum())
        report['k%d' % k] = dict(
            n_graphs=len(rows), n_we=len(ok), seconds=round(time.time() - t0, 1),
            E_mean=float((wts * E).sum()), E_median=float(np.median(E)),
            gauge_surv_median=float(np.exp(np.median(lg))),
            gauge_surv_max=float(np.exp(lg.max())),
            gauge_surv_geomean_weighted=float(np.exp((wts * lg).sum())),
            per_edge_median=float(np.median(pe)), per_edge_max=float(pe.max()),
            per_edge_weighted=float((wts * pe).sum()),
            kill_median=float(np.median(kill)),
            kill_weighted=float((wts * kill).sum()),
            zero_surv=int((np.array([r['gauge_surv'] for r in rows]) == 0).sum()),
            we_surv_geomean_weighted=(float(np.exp((wok * np.array(
                [math.log(max(1, rows[i]['we']['we_surv'])) for i in ok])).sum())) if ok else None),
            we_over_a31_ratio=(float((wok * np.array(
                [rows[i]['we']['we_surv'] / max(1, rows[i]['gauge_surv']) for i in ok])).sum())
                if ok else None),
            N3_frac_nozero_weighted=wavg('frac_N3_nozero'),
            N4_frac_weighted=wavg('frac_N4'),
            N7d_frac_weighted=wavg('frac_N7d'),
            N3_frac_nozero_median=(float(np.median([rows[i]['we']['frac_N3_nozero']
                                                    for i in ok])) if ok else None),
            N4_frac_median=(float(np.median([rows[i]['we']['frac_N4'] for i in ok]))
                            if ok else None),
            N7d_frac_median=(float(np.median([rows[i]['we']['frac_N7d'] for i in ok]))
                             if ok else None),
            rows=rows)
        with open(os.path.join(RES, 'level1.json'), 'w') as fh:
            json.dump(report, fh, indent=1)
    print(json.dumps({kk: {a: b for a, b in v.items() if a != 'rows'}
                      for kk, v in report.items()}, indent=1))


if __name__ == '__main__':
    main()
