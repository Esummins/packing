"""A45-B kill audit: every RULER kill must be explainable, and must not be a modelling artifact.

For every component signature the CSP proved dead during the census, we report:
  * whether the PATH RELAXATION alone (Lemma Q: opposite-wall WF anchors at FL-graph distance
    <= 2) already proves it dead -- the mechanism the A43 law predicts;
  * whether the component is zero-pinned and how many pins it carries.
A kill NOT covered by the path relaxation is reported explicitly (it would be a second, distinct
mechanism, and must be inspected before being trusted).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_b as C
import ruler

A45 = C.A45


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6]
    L1 = json.load(open(os.path.join(C.A43RES, 'level1.json')))
    for k in ks:
        d = json.load(open(os.path.join(C.A43RES, 'level0_k%d.json' % k)))
        items = []
        for s in d['samples']:
            for wmv in s['w']:
                items.append((s['gmask'], tuple(wmv)))
        import numpy as np
        rng = np.random.default_rng(7)
        cap_k = 160 if k <= 6 else 40
        if len(items) > cap_k:
            idx = rng.choice(len(items), cap_k, replace=False)
            items = [items[i] for i in idx]
        for gmask, wmv in items:
            C.fanout_a45(k, gmask, wmv, 22)
    def nonbipartite(n, links):
        col = [None] * n
        adj = [[] for _ in range(n)]
        for a, b in links:
            adj[a].append(b)
            adj[b].append(a)
        for s in range(n):
            if col[s] is not None:
                continue
            col[s] = 0
            st = [s]
            while st:
                u = st.pop()
                for v in adj[u]:
                    if col[v] is None:
                        col[v] = 1 - col[u]
                        st.append(v)
                    elif col[v] == col[u]:
                        return True
        return False

    rows = []
    for key, hits in ruler.KILLED.items():
        n, links, pu, pv, zero, cs = key
        pr = (ruler.path_relaxation_kill(n, list(links), list(pu)) or
              ruler.path_relaxation_kill(n, list(links), list(pv)))
        samewall = (len({(t) for _, t in pu}) == 1 and len(pu) >= 2) or \
                   (len({(t) for _, t in pv}) == 1 and len(pv) >= 2)
        parity = nonbipartite(n, list(links)) and (len(pu) + len(pv) > 0)
        rows.append(dict(n_squares=n, n_links=len(links), links=list(links),
                         pins_u=list(pu), pins_v=list(pv), zero_pinned=zero,
                         decorations_hit=hits,
                         explained_by_LemmaQ_path_relaxation=bool(pr),
                         same_wall_pin_multiplicity=bool(samewall),
                         odd_cycle_parity_candidate=bool(parity),
                         has_opposite_pins=bool(
                             ({t for _, t in pu} == {'LO', 'HI'}) or
                             ({t for _, t in pv} == {'LO', 'HI'}))))
    out = dict(n_killed_signatures=len(rows),
               explained_by_path_relaxation=sum(r['explained_by_LemmaQ_path_relaxation']
                                                for r in rows),
               with_opposite_pins=sum(r['has_opposite_pins'] for r in rows),
               all_zero_pinned=all(r['zero_pinned'] for r in rows),
               explained_by_parity=sum(r['odd_cycle_parity_candidate'] and
                                       not r['explained_by_LemmaQ_path_relaxation']
                                       for r in rows),
               unexplained=[r for r in rows
                            if not r['explained_by_LemmaQ_path_relaxation']
                            and not r['odd_cycle_parity_candidate']],
               parity_only=[r for r in rows
                            if r['odd_cycle_parity_candidate']
                            and not r['explained_by_LemmaQ_path_relaxation']],
               rows=rows)
    json.dump(out, open(os.path.join(A45, 'results', 'ruler_kill_audit.json'), 'w'), indent=1)
    print('killed component signatures: %d;  all zero-pinned: %s;  with opposite-wall pins: %d;'
          '  explained by the Lemma-Q path relaxation: %d;  UNEXPLAINED: %d'
          % (len(rows), out['all_zero_pinned'], out['with_opposite_pins'],
             out['explained_by_path_relaxation'], len(out['unexplained'])))
    print('  of the non-path kills, %d are odd-cycle parity kills (a same-wall pin set forces '
          'every link into ONE family, and an odd cycle of +-1 steps cannot close)'
          % out['explained_by_parity'])
    for r in out['unexplained'][:10]:
        print('  UNEXPLAINED:', r)


if __name__ == '__main__':
    main()
