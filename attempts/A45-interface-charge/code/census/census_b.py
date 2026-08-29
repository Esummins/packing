"""A45-B census driver: A43-H1 Level-1 decoration fan-out, re-run with the A45 columns.

Reproduces A43's `we_surv` EXACTLY (regression duty on the L1 side: same A31 sampling protocol,
seed 7, cap 160 / 40 at k=7, budget 22) and adds, per decoration (fl-pattern x ws-pattern):

  RULER_kill        [EXACT]  no (family, sign) assignment of the FL normals is feasible
  RULER_refined     [EXACT]  4^nf replaced by the number of FEASIBLE (family, sign) assignments
                             -- strictly stronger than the kill column and still one-sided
  ZERO_CHARGE       [report] the all-FL / all-WF decoration (Sec 6.5)
  CHARGE_min        [EXACT]  Theorem A45.1 with min-over-reachable-bins semantics
  CHARGE_ceforced   [report] the same with every non-flush square-square contact PRICED as CE
                             (not sound as a kill: CC is reachable and uncharged)

Usage:  python census_b.py 3 4 5 6 7
"""
import os, sys, json, math, time, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A45 = os.path.abspath(os.path.join(HERE, '..', '..'))
A43H1 = os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'code', 'h1'))
A43RES = os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'results', 'h1'))
sys.path.insert(0, A43H1)
sys.path.insert(0, HERE)

import lib0 as L                                    # A43/A31 level-0 library, read-only
from level1_ao import acyclic_orientations          # A31 acyclic-orientation counter, read-only
import ruler
import charge as CH
from fractions import Fraction as F

TAB = CH.load_table()
B0 = CH.B0


def fanout_a45(k, gmask, wm, budget=22):
    """A43 fanout_we, verbatim in its accounting, with the A45 columns bolted on."""
    adj, ss_edges = L.mask_to_adj(gmask, k)
    Ess = len(ss_edges)
    wedges = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    Esw = len(wedges)
    if budget is not None and Ess + Esw > budget:
        return None
    tot = 0
    tot_ruler_kill = 0
    tot_ruler_refined = 0
    tot_zero = 0
    tot_zero_ruler_kill = 0
    tot_charge_kill = 0
    tot_ceforced_kill = 0
    n_capped = 0
    max_ceforced = F(0)
    max_chargeable = 0
    zero_comp_all_walled = True
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
        fl_edges = [(i, j) for e, (i, j) in enumerate(ss_edges) if (fl >> e) & 1]
        cls = sorted(set(find(i) for i in range(k)))
        cid = {c: t for t, c in enumerate(cls)}
        mult = (4 ** nf) * (8 ** (Ess - nf))
        for ws in range(1 << Esw):
            nwf = bin(ws).count('1')
            pinned = set()
            corner_cls = set()
            for t, (i, b) in enumerate(wedges):
                if (ws >> t) & 1:
                    pinned.add(find(i))
                else:
                    corner_cls.add(find(i))
            if pinned & corner_cls:
                continue
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
            # ---------------- A45 columns
            wf_edges = [wedges[t] for t in range(Esw) if (ws >> t) & 1]
            wc_edges = [wedges[t] for t in range(Esw) if not ((ws >> t) & 1)]
            if nf == 0:
                rk, gok, gfull, cap = False, 1, 1, 0
            else:
                r = ruler.analyse(k, fl_edges, wf_edges)
                rk, gok, gfull, cap = r['kill'], r['gauge_ok'], r['gauge_full'], r['capped']
                n_capped += cap
            if rk:
                tot_ruler_kill += v
            tot_ruler_refined += (8 ** (Ess - nf)) * ao * gok
            zero = (nf == Ess and nwf == Esw)
            if zero:
                tot_zero += v
                if rk:
                    tot_zero_ruler_kill += v
                comps = {}
                for i in range(k):
                    comps.setdefault(find(i), []).append(i)
                walled = set(find(i) for i, b in wedges)
                if any(r not in walled for r in comps):
                    zero_comp_all_walled = False
            # CHARGE, min-over-reachable-bins (the sound form)
            cs, _ = CH.decoration_charge(TAB, k, wm, wc_edges, rest, force_ce=False)
            if cs > B0:
                tot_charge_kill += v
            cs2, _ = CH.decoration_charge(TAB, k, wm, wc_edges, rest, force_ce=True)
            if cs2 > B0:
                tot_ceforced_kill += v
            if cs2 > max_ceforced:
                max_ceforced = cs2
            nch = sum(1 for (i, b) in wc_edges if bin(wm[i]).count('1') < 2) + len(rest)
            max_chargeable = max(max_chargeable, nch)
    return dict(Ess=Ess, Esw=Esw, E=Ess + Esw, we_surv=tot,
                ruler_kill=tot_ruler_kill, ruler_refined=tot_ruler_refined,
                zero_charge=tot_zero, zero_charge_ruler_kill=tot_zero_ruler_kill,
                charge_kill=tot_charge_kill, ceforced_kill=tot_ceforced_kill,
                capped_components=n_capped,
                max_ceforced_charge=str(max_ceforced),
                max_ceforced_charge_float=float(max_ceforced),
                max_chargeable_contacts=max_chargeable,
                zero_charge_every_component_walled=zero_comp_all_walled,
                frac_ruler_kill=(tot_ruler_kill / tot if tot else 0.0),
                frac_ruler_refined=(tot_ruler_refined / tot if tot else 1.0),
                frac_zero_charge=(tot_zero / tot if tot else 0.0))


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6, 7]
    cap = int(os.environ.get('A43_L1_CAP', '160'))
    budget = int(os.environ.get('A43_L1_BUDGET', '22'))
    A43L1 = json.load(open(os.path.join(A43RES, 'level1.json')))
    report = {}
    outp = os.path.join(A45, 'results', 'census_l1.json')
    for k in ks:
        p = os.path.join(A43RES, 'level0_k%d.json' % k)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        items = []
        for s in d['samples']:
            w = s['main'] / max(1, s['nsample'])
            for wmv in s['w']:
                items.append((s['gmask'], tuple(wmv), w))
        rng = np.random.default_rng(7)              # A31/A43 protocol, verbatim
        cap_k = cap if k <= 6 else max(30, cap // 4)
        if len(items) > cap_k:
            idx = rng.choice(len(items), cap_k, replace=False)
            items = [items[i] for i in idx]
        rows = []
        t0 = time.time()
        for gmask, wmv, w in items:
            r = fanout_a45(k, gmask, wmv, budget)
            if r is None:
                continue
            r['gmask'] = gmask
            r['w'] = list(wmv)
            r['weight'] = w
            rows.append(r)
        wts = np.array([r['weight'] for r in rows], dtype=float)
        wts /= wts.sum()

        def wavg(key):
            return float((wts * np.array([r[key] for r in rows], dtype=float)).sum())
        a43 = A43L1.get('k%d' % k)
        a43rows = {(rr['gmask'], tuple(rr['w'])): rr['we']['we_surv']
                   for rr in a43['rows'] if rr.get('we')} if a43 else {}
        mism = [(r['gmask'], r['w']) for r in rows
                if (r['gmask'], tuple(r['w'])) in a43rows
                and a43rows[(r['gmask'], tuple(r['w']))] != r['we_surv']]
        report['k%d' % k] = dict(
            n_graphs=len(rows), seconds=round(time.time() - t0, 1),
            a43_we_surv_rows_compared=len(a43rows),
            a43_we_surv_mismatches=len(mism),
            we_surv_geomean_weighted=float(np.exp(
                (wts * np.array([math.log(max(1, r['we_surv'])) for r in rows])).sum())),
            frac_ruler_kill_weighted=wavg('frac_ruler_kill'),
            frac_ruler_kill_max=max(r['frac_ruler_kill'] for r in rows),
            ruler_refined_keep_weighted=wavg('frac_ruler_refined'),
            ruler_refined_keep_min=min(r['frac_ruler_refined'] for r in rows),
            frac_zero_charge_weighted=wavg('frac_zero_charge'),
            frac_zero_charge_max=max(r['frac_zero_charge'] for r in rows),
            zero_charge_ruler_kill_weighted=float((wts * np.array(
                [(r['zero_charge_ruler_kill'] / r['zero_charge']) if r['zero_charge'] else 0.0
                 for r in rows])).sum()),
            frac_charge_kill_weighted=wavg('frac_ruler_kill') * 0.0 + float((wts * np.array(
                [r['charge_kill'] / r['we_surv'] if r['we_surv'] else 0.0
                 for r in rows])).sum()),
            frac_ceforced_kill_weighted=float((wts * np.array(
                [r['ceforced_kill'] / r['we_surv'] if r['we_surv'] else 0.0
                 for r in rows])).sum()),
            max_ceforced_charge=max(r['max_ceforced_charge_float'] for r in rows),
            max_chargeable_contacts=max(r['max_chargeable_contacts'] for r in rows),
            capped_components=sum(r['capped_components'] for r in rows),
            zero_charge_every_component_walled=all(
                r['zero_charge_every_component_walled'] for r in rows),
            rows=rows)
        rr = report['k%d' % k]
        print('k=%d n=%d we_geo=%.4e  A43 we_surv match %d/%d  ruler_kill=%.3e '
              'ruler_refined_keep=%.4f  zero_charge=%.3e  charge_kill=%.1e  '
              'ceforced_kill=%.1e maxQ=%.4f  (%.1fs)'
              % (k, rr['n_graphs'], rr['we_surv_geomean_weighted'],
                 rr['a43_we_surv_rows_compared'] - rr['a43_we_surv_mismatches'],
                 rr['a43_we_surv_rows_compared'], rr['frac_ruler_kill_weighted'],
                 rr['ruler_refined_keep_weighted'], rr['frac_zero_charge_weighted'],
                 rr['frac_charge_kill_weighted'], rr['frac_ceforced_kill_weighted'],
                 rr['max_ceforced_charge'], rr['seconds']), flush=True)
        json.dump(report, open(outp, 'w'), indent=1, default=float)
    print(json.dumps({kk: {a: b for a, b in v.items() if a != 'rows'}
                      for kk, v in report.items()}, indent=1, default=float))


if __name__ == '__main__':
    main()
