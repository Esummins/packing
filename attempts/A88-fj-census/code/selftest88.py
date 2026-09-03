"""A88 self-tests: tables, D4 equivariance, decoration menu bijection, tilt-count
agreement with the A31/A44 exact formula."""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import itertools
import json
import sys

import numpy as np

import a88lib as A


def exact_tilt_count(k, ss_edges, wm):
    """A31 level1.fanout / A44 census_l1.fanout_we_branch, copied (unmodified logic):
    exact number of tilt-feasible gauge-fixed decorations, with the chi split."""
    Ess = len(ss_edges)
    wedges = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    Esw = len(wedges)
    E = Ess + Esw
    N = 3 * k + 1
    tot = 0
    tot_ge1 = 0
    chi_hist = {}
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
                ao = A.acyclic_orientations(nn, qe)
            else:
                rm = {}
                t = 0
                for x in range(nn):
                    if x == zpos:
                        continue
                    rm[x] = t
                    t += 1
                qe2 = [(rm[a], rm[b]) for a, b in qe if a != zpos and b != zpos]
                ao = A.acyclic_orientations(nn - 1, qe2)
            v = mult * ao
            if not v:
                continue
            m = E + nf + nwf
            chi = m - N
            tot += v
            chi_hist[chi] = chi_hist.get(chi, 0) + v
            if chi >= 0:
                tot_ge1 += v
    return dict(Ess=Ess, Esw=Esw, E=E, tot=tot, m_ge_3k1=tot_ge1,
                gauge_menu=20 ** Ess * 2 ** Esw,
                chi_hist={str(a): b for a, b in sorted(chi_hist.items())})


def enumerate_decorations(k, ss_edges, wm):
    """Explicit enumeration of the gauge-fixed menu (20 per SS, 2 per SW)."""
    wedges = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    ss_menu = []
    for (i, j) in ss_edges:
        opts = [('F', e) for e in range(4)]
        for owner in (i, j):
            for e in range(4):
                for hi in (False, True):
                    opts.append(('C', owner, e, hi))
        assert len(opts) == 20
        ss_menu.append(opts)
    for ss in itertools.product(*ss_menu):
        for ws in range(1 << len(wedges)):
            sw = {we: ('WF' if (ws >> t) & 1 else 'CW')
                  for t, we in enumerate(wedges)}
            yield A.Decoration(k, ss_edges, wm, ss, sw)


def main():
    out = {}
    bad = A.check_d4_equivariance()
    out['d4_equivariance'] = 'PASS' if not bad else 'FAIL %s' % bad
    sf = A.check_structural_facts()
    out['structural_facts'] = dict(coex_ok=sf['coex_ok'], touch_ok=sf['touch_ok'],
                                   coex_fail=sf['coex_fail_pairs'][:5],
                                   touch_fail=sf['touch_fail_pairs'][:5])
    out['window'] = [A.S_LO, A.S_HI]
    out['DREQ'] = A.DREQ.tolist()
    out['ALLOWED'] = A.ALLOWED
    out['W_PAIR'] = A.W_PAIR.tolist()
    out['n_touch_pairs_9x9'] = int(A.TOUCH.sum())

    # -------- decoration menu bijection + tilt-count agreement (brute force)
    cases = [
        (3, [(0, 1), (1, 2)], [1, 0, 4]),
        (3, [(0, 1), (1, 2), (0, 2)], [1, 0, 4]),
        (3, [(0, 1), (1, 2)], [3, 0, 12]),
        (4, [(0, 1), (1, 2), (2, 3)], [1, 0, 0, 4]),
        (4, [(0, 1), (1, 2), (2, 3), (0, 3)], [3, 0, 0, 6]),
        (3, [(0, 1), (1, 2), (0, 2)], [3, 2, 6]),
    ]
    rows = []
    for k, ss, wm in cases:
        ex = exact_tilt_count(k, ss, wm)
        n_menu = 0
        n_feas = 0
        n_k01 = 0
        n_k03 = 0
        seen_rows = set()
        for dec in enumerate_decorations(k, ss, wm):
            n_menu += 1
            ts = dec.tilt_system()
            if not ts['feasible']:
                continue
            n_feas += 1
            key = tuple(sorted(tuple(sorted(r.items())) for r in dec.rows(ts)))
            seen_rows.add(key)
            if dec.k0_1():
                n_k01 += 1
            ok3, _ = dec.k0_3(ts)
            if ok3:
                n_k03 += 1
        rows.append(dict(k=k, ss=ss, wm=wm, menu=n_menu,
                         menu_expected=ex['gauge_menu'],
                         feasible_enum=n_feas, feasible_exact=ex['tot'],
                         agree=bool(n_feas == ex['tot']),
                         distinct_rowsets=len(seen_rows),
                         rows_injective=bool(len(seen_rows) == n_feas),
                         k0_1=n_k01, k0_3=n_k03, E=ex['E'],
                         chi_hist=ex['chi_hist']))
        print(rows[-1], flush=True)
    out['decoration_cases'] = rows
    out['decoration_all_agree'] = all(r['agree'] for r in rows)
    out['rows_map_injective'] = all(r['rows_injective'] for r in rows)

    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, '..', 'results', 'selftest88.json')
    with open(p, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({a: b for a, b in out.items()
                      if a not in ('DREQ', 'W_PAIR', 'decoration_cases')},
                     indent=1))
    print('wrote', p)


if __name__ == '__main__':
    main()
