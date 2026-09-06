"""A107 follow-up: append Part II (the k0_00 cells of A38 / A85 / A99) to docs/shadows.md, draw
docs/shadows/K*.svg, and report where a k0 shadow coincides with a Part I S-entry.

The k0_00 class has NO pins: a node's only hypothesis core is the conditioned square, so the class
symmetry group is the full D4 (8 elements), not the stabiliser of a pin set."""
import os, sys, json, math, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L, minimise as M, svg as SV

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
RES = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')
DOCS = os.path.join(ROOT, 'docs')
SVGD = os.path.join(DOCS, 'shadows')
S0, SHAT = L.S0, L.SHAT

def cfg_of(sh):
    return [tuple(f) for f in sh['free']] + [(x, y, 0.0) for x, y in M.slot_centres(sh['slots'], sh['s'])]

def best_overlap(A, sA, B, sB, dtol=0.05, atol=3.0):
    """Best alignment of two square lists over the full D4 of the container: how many squares of A
    have a partner in the image of B.  Returns (op, matched, jaccard)."""
    best = ('e', 0, 0.0)
    for nm, f in L.d4_ops(sB):
        im = [tuple(f(x, y, t)) for x, y, t in B]
        used = [False] * len(im)
        hit = 0
        for p in A:
            for j, q in enumerate(im):
                if used[j]:
                    continue
                if math.hypot(p[0] - q[0], p[1] - q[1]) <= dtol and L.tilt_close(p[2], q[2], atol):
                    used[j] = True
                    hit += 1
                    break
        jac = hit / float(len(A) + len(im) - hit) if (len(A) + len(im) - hit) else 0.0
        if (hit, jac) > (best[1], best[2]):
            best = (nm, hit, jac)
    return best

def slot_images(names):
    """The 8 D4 images of a slot-NAME set (the action on named corner cells is combinatorial)."""
    out = []
    for nm, f in L.d4_ops(S0):
        im = set()
        for n in names:
            x, y = M.slot_centres([n], S0)[0]
            xx, yy, _ = f(x, y, 0.0)
            k = L.snap(xx, yy, 0.0, S0)
            if k:
                im.add(k)
        out.append((nm, im))
    return out

def slot_jaccard(A, B):
    """Best Jaccard between two slot-NAME sets over D4.  This is A113's comparison: it asks which
    slot CELLS the LP filled, not what the minimised packing looks like."""
    A = set(A)
    best = (0.0, 'e')
    for nm, im in slot_images(B):
        u = len(A | im)
        j = len(A & im) / float(u) if u else 0.0
        if j > best[0]:
            best = (j, nm)
    return best

def main():
    ks = json.load(open(os.path.join(RES, 'shadows_k0.json')))
    ex = json.load(open(os.path.join(RES, 'extract_k0.json')))
    ss = json.load(open(os.path.join(RES, 'shadows.json')))
    nodes = ex['nodes']
    os.makedirs(SVGD, exist_ok=True)

    for sh in ks:
        mem = sorted({i for st in sh['structs'] for i in st['members']})
        sh['members'] = mem
        sh['srcs'] = collections.Counter(nodes[i]['src'] for i in mem)
        sh['levels'] = collections.Counter(nodes[i]['level'] for i in mem)
        sh['via'] = collections.Counter(nodes[i].get('via') for i in mem)
        sh['at_budget'] = sum(1 for i in mem if nodes[i].get('at_budget'))
        sh['cfg'] = cfg_of(sh)

    # ---- coincidences with Part I
    for sh in ks:
        rows = []
        for t in ss:
            tc = [tuple(f) for f in t['free']] + [(x, y, 0.0) for x, y in M.slot_centres(t['slots'], t['s'])]
            op, hit, jac = best_overlap(sh['cfg'], sh['s'], tc, t['s'])
            sj, sop = slot_jaccard(sh['slots'], t['slots'])
            if jac >= 0.5 or sj >= 0.999:
                rows.append(dict(sid=t['id'], s=t['s'], op=op, matched=hit, of=len(sh['cfg']),
                                 other=len(tc), jaccard=round(jac, 4), ds=round(sh['s'] - t['s'], 9),
                                 slot_jaccard=round(sj, 4), slot_op=sop))
        rows.sort(key=lambda r: (-r['jaccard'], -r.get('slot_jaccard', 0)))
        sh['coincide'] = rows[:4]

    # ---- drawings
    for sh in ks:
        prim = max(sh['structs'], key=lambda d: d['nnodes'])
        rep = nodes[prim['members'][0]] if prim['members'] else nodes[sh['members'][0]]
        sc = 118
        oy = 56 + S0 * sc
        body = []
        p1, _ = SV.panel_lp(30, oy, sc, f"{sh['id']} panel 1 - raw LP dual support of {rep['nid']}",
                            rep['cores'], [q for q in rep['cfg'][len(rep['cores']):]])
        body += p1
        W1 = S0 * sc + 60
        p2, _ = SV.panel_pack(30 + W1, oy, sc, f"{sh['id']} panel 2 - the k0 shadow at s* = {sh['s']:.6f}",
                              f"{len(sh['slots'])} snapped slot squares + {sh['nfree']} free squares; "
                              f"s* - s-hat = {sh['ds']:+.6f}", sh['s'], sh['free'], sh['slots'])
        body += p2
        W = 2 * W1 + 60
        if sh.get('sweep'):
            body += SV.tilt_panel(30 + 2 * W1, oy - 60, 300, 190, sh['sweep'], sh['s'], sh['common_tilt'] or 0.0)
            W = 2 * W1 + 400
        SV.write_svg(os.path.join(SVGD, f"{sh['id']}.svg"), body, int(W), int(oy + 40))

    # ---- markdown
    A = []
    a = A.append
    a('')
    a('# Part II - the k0_00 cells (A38 / A85 / A99)\n')
    a('The k0_00 class has **no pins**: a node\'s only hypothesis core is the conditioned square, so')
    a('the class symmetry group is the **full D4** (8 elements), not the stabiliser of a pin set, and')
    a('every de-duplication below runs over all 8.  Everything else is the Part I pipeline unchanged:')
    a('the near-simple placements of the dual support are snapped to named slot cells and fixed as')
    a('affine functions of s, the rest are free, and s is minimised.\n')
    a('Sources and the alive test.  A38-root-power `results/{l1,l2,l3}_nodes/*.json` (134 + 49 + 11')
    a('with an LP support), A85-k0-route `results/nodes/k0_00/*.json` (12) and A99-k0-tree-v2')
    a('`results/nodes/k0_00/*.json` (54) - 260 node jsons in the same format as Part I (tau, budget,')
    a('`hyp.cores`, `packing` with y, `rows_all`).  A node counts as alive when the LP did not certify')
    a('it (`dead == False`) **or** its LP value already reaches the budget (tau >= budget); on this')
    a(f'corpus the second condition is contained in the first.  **{len(nodes)} alive k0 cells**: ' +
      ', '.join(f'{k} {v}' for k, v in collections.Counter(n['src'] for n in nodes).most_common()) +
      f'; {sum(1 for n in nodes if n.get("at_budget"))} of them sit at tau >= budget.')
    a('Budget is 10 (n = 10) on 214 of them, so a k0 shadow is a k11 packing when the support is full')
    a('and shorter otherwise.  All are at the certified side s0 = 3.877084.\n')
    ncov = sum(sh['nnodes'] for sh in ks)
    a(f'**{len(ks)} distinct k0 shadow values explain {ncov} of the {len(nodes)} alive cells**; '
      f'{len(ex["unexplained"])} are explained by no integral shadow.\n')
    a('| shadow | sources | k of the shadow | s* | s* - s-hat | k0 cells | #cfg | levels | free sq | common tilt | flexes | coincides with |')
    a('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for sh in ks:
        an = sh['analysis']
        src = ', '.join(f'{k} x{v}' for k, v in sh['srcs'].most_common())
        lv = ', '.join(f'L{k}:{v}' for k, v in sorted(sh['levels'].items()))
        ct = f"{sh['common_tilt']:.3f} deg" if sh['common_tilt'] is not None else 'no'
        co = '; '.join(f"{r['sid']} ({r['jaccard']:.2f}{', exact' if r['jaccard'] >= 0.999 else ''})"
                       for r in sh['coincide'][:2] if r['jaccard'] >= 0.5) or '-'
        a(f"| **{sh['id']}** | {src} | k{sh['nsquares']} ({len(sh['slots'])} slot + {sh['nfree']} free) | "
          f"{sh['s']:.6f} | {sh['ds']:+.6f} | {sh['nnodes']} | {sh.get('nconfigs', 1)} | {lv} | "
          f"{sh['nfree']} | {ct} | {an.get('flexes_fixed_s')} | {co} |")
    a('')
    hits = [(sh, r) for sh in ks for r in sh['coincide']]
    exact = [(sh, r) for sh, r in hits if r['jaccard'] >= 0.999]
    a('## Coincidences with Part I\n')
    a('Each k0 shadow\'s minimised packing was aligned against every Part I S-entry over the full D4')
    a('of the container, matching squares at 0.05 in position and 3 deg in tilt; the score is the')
    a('Jaccard index (matched / (|A| + |B| - matched)).  Two different comparisons are reported and')
    a('they do not agree, which is the point:\n')
    a('* **packing Jaccard** - the whole MINIMISED packing, free squares included.  This is the')
    a('  strong claim: 1.000 means the two shadows are the same 11-square configuration.')
    a("* **slot-set Jaccard** - only which named slot CELLS the LP filled, compared modulo D4.  This")
    a("  is A113's comparison (`attempts/A113-k0-manifold-distance/results/t2_supports.md`, column")
    a('  "best shadow (Jaccard @ s\\*)"), and it is much coarser: one slot skeleton carries different')
    a('  free-square arrangements with different s*.  A113 read cell `l1_100` (= A38')
    a('  `l1_nodes/node_100.json`) as S38 at 1.00 on slot sets; here that cell lands in **K04** and')
    a('  minimises to 3.914214 while S38 minimises to 3.928915 - the slot skeleton is shared, the')
    a("  packing is not.  Likewise A113's `s1int_l1_043` -> S07 at 0.83 on slot sets: that cell is in")
    a('  **K01** here and minimises to 4.000000, packing Jaccard against S07 0.29.\n')
    a('Rows are listed when either score is high (packing Jaccard >= 0.5, or slot-set Jaccard 1.0).\n')
    if hits:
        a('| k0 shadow | s* | Part I entry | its s* | s* difference | D4 map | squares matched | packing Jaccard | slot-set Jaccard |')
        a('|---|---|---|---|---|---|---|---|---|')
        for sh, r in sorted(hits, key=lambda t: (-t[1]['jaccard'], -t[1].get('slot_jaccard', 0))):
            a(f"| {sh['id']} | {sh['s']:.6f} | {r['sid']} | {r['s']:.6f} | {r['ds']:+.9f} | `{r['op']}` | "
              f"{r['matched']} of {r['of']} vs {r['other']} | {r['jaccard']:.3f} | "
              f"{r.get('slot_jaccard', 0):.3f} (`{r.get('slot_op','e')}`) |")
        a('')
        a(f'{len(exact)} exact coincidence(s) (Jaccard 1.000): ' +
          (', '.join(f"{sh['id']} = {r['sid']}" for sh, r in exact) or 'none') + '.')
    else:
        a('No k0 shadow reaches Jaccard 0.5 against any Part I entry.')
    a('')

    for sh in ks:
        an = sh['analysis']
        a(f"## {sh['id']} - a k{sh['nsquares']} packing at s* = {sh['s']:.6f} on the boundary of class k0_00\n")
        a(f"![{sh['id']}](shadows/{sh['id']}.svg)\n")
        a(f"* **s\\*** = {sh['s']:.9f} = s-hat {sh['ds']:+.9f}  (s0 = {S0:.6f}, s\\* - s0 = {sh['s']-S0:+.6f})")
        a(f"* **shadow** = {len(sh['slots'])} slot squares `{' '.join(sh['slots']) or '(none)'}` + "
          f"{sh['nfree']} free squares f0..f{sh['nfree']-1}; a k{sh['nsquares']} packing.")
        a(f"* **explains** {sh['nnodes']} alive k0 cells: " +
          ', '.join(f'{k} x{v}' for k, v in sh['srcs'].most_common()) + '; levels ' +
          ', '.join(f'L{k}:{v}' for k, v in sorted(sh['levels'].items())) + '; ' +
          ', '.join(f'{k} {v}' for k, v in sh['via'].most_common()) + f" support; {sh['at_budget']} at tau >= budget.")
        a(f"* **load-bearing squares**: `{'` `'.join(sh.get('loaded', [])) or '(none)'}` "
          f"({len(sh.get('loaded', []))} of {sh['nsquares']}); "
          f"**{sh.get('nconfigs', 1)} distinct minimised configuration(s)** share this s*.")
        if sh['common_tilt'] is not None:
            a(f"* the free squares share one tilt: {sh['common_tilt']:.4f} deg.")
        if sh['coincide']:
            a('* **coincides with Part I**: ' + '; '.join(
                f"`{r['sid']}` (s* {r['s']:.6f}, D4 map `{r['op']}`, {r['matched']} squares matched, "
                f"Jaccard {r['jaccard']:.3f})" for r in sh['coincide']) + '.')
        a(f"* **restarts**: {sh['confirm']['nfeas']} feasible of {sh['confirm']['nstart']}; distinct minima "
          f"{sh['confirm']['minima'][:8]}.")
        a('')
        a('| square | cx | cy | tilt (deg) |')
        a('|---|---|---|---|')
        for i, f in enumerate(sh['free']):
            a(f"| f{i} | {f[0]:.6f} | {f[1]:.6f} | {math.degrees(L.tmod(f[2])):.4f} |")
        a('')
        a('**Contact graph at s\\*** (gap < 1e-7; force = Fritz-John resultant, rows unit-normalised)')
        a('')
        a('| contact | type | gap | force |')
        a('|---|---|---|---|')
        forces = {}
        for k, v in (an.get('resultant') or {}).items():
            x, y = k.split('|')
            forces[(x, y)] = v
        for c in an['contacts']:
            a(f"| `{c['a']}` - `{c['b']}` | {c['kind']} | {c['gap']:+.1e} | {forces.get((c['a'], c['b']), 0.0):.4f} |")
        for w in sorted({(w['a'], w['b']) for w in an['walls']}):
            a(f"| `{w[0]}` - {w[1]} | wall | 0 | {forces.get(w, 0.0):.4f} |")
        a('')
        bind = sorted(((v, k) for k, v in forces.items() if v > 1e-6), reverse=True)
        if bind:
            a('**Binding**: ' + ', '.join(f"`{k[0]}`-`{k[1]}` ({v:.3f})" for v, k in bind[:6]) +
              f".  KKT residual {an['kkt_residual']:.1e}." +
              ('  Exactly-opposite (cone-degenerate) contacts: ' +
               ', '.join('`%s`-`%s`' % (u, v2) for u, v2 in an.get('degenerate', [])) + '.'
               if an.get('degenerate') else ''))
        if an['kkt_residual'] > 1e-6:
            a(f"**Convergence caveat**: KKT residual {an['kkt_residual']:.1e} - the landing leans on a "
              f"variable bound or SLSQP stopped short, so s* = {sh['s']:.6f} is an upper bound.")
        a(f"**Rank**: {an['nrows']} contact rows, {an['nvars']} variables; rank {an['rank']}; at fixed s "
          f"rank {an['rank_fixed_s']} of {an['nvars']-1}, so **{an['flexes_fixed_s']} flat direction(s)**"
          + (': ' + ', '.join(f"{f['verdict']}" for f in an['flat'][:8]) if an['flat'] else '.'))
        a('')
        a('**T2 drain hint - the load-bearing subgraph**')
        a('')
        a('| removed | s* without it | drop | role |')
        a('|---|---|---|---|')
        for r in sh['rattlers']:
            sw = f"{r['s_without']:.6f}" if r['s_without'] is not None else 'infeasible'
            dr = f"{r['drop']:+.6f}" if r['drop'] is not None else '-'
            a(f"| `{r['removed']}` | {sw} | {dr} | {r['role']} |")
        a('')
        lb = [r['removed'] for r in sh['rattlers'] if r['role'] == 'load-bearing']
        rt = [r['removed'] for r in sh['rattlers'] if r['role'] == 'rattler']
        a(f"Load-bearing: {', '.join('`%s`' % x for x in lb) or 'none'}.  "
          f"Rattlers: {', '.join('`%s`' % x for x in rt) or 'none'}.")
        if sh.get('sweep'):
            pts = [(d['tilt_deg'], d['s']) for d in sh['sweep'] if d['s'] is not None]
            if pts:
                a('')
                a('**Common-tilt sweep**')
                a('')
                a('| tilt (deg) | ' + ' | '.join(f'{t:.2f}' for t, _ in pts) + ' |')
                a('|---|' + '---|' * len(pts))
                a('| s* | ' + ' | '.join(f'{v:.6f}' for _, v in pts) + ' |')
        a('')
        ids = [f"{nodes[i]['src']}/{nodes[i]['shard']}/{nodes[i]['nid']}(L{nodes[i]['level']})"
               for i in sh['members']]
        a(f"**k0 cells explained** ({len(ids)}): `" + '` `'.join(ids[:200]) + '`' +
          ('' if len(ids) <= 200 else f' ... (+{len(ids)-200} more)'))
        a('')

    un = [nodes[i] for i in ex['unexplained']]
    a('## k0 cells not explained by any integral shadow\n')
    a(f'{len(un)} of {len(nodes)}.  Their dual supports are fractional and contain no budget-many')
    a('pairwise cell-disjoint placements among those with y > 0.02.\n')
    a('| source | level | count | largest independent set found (of budget) |')
    a('|---|---|---|---|')
    agg = collections.defaultdict(list)
    for n in un:
        agg[(n['src'], n['level'])].append(n)
    for k in sorted(agg):
        g = agg[k]
        h = collections.Counter(f"{x.get('comp')}/{x.get('budget')}" for x in g)
        a(f"| {k[0]} | L{k[1]} | {len(g)} | " + ', '.join(f'{u} x{v}' for u, v in h.most_common(5)) + ' |')
    a('')
    a('Full list: `attempts/A107-shadow-gallery/results/unexplained_k0.json`.')
    a('')

    with open(os.path.join(DOCS, 'shadows.md'), 'r', encoding='utf-8') as f:
        cur = f.read()
    cut = cur.find('\n# Part II - the k0_00 cells')
    if cut >= 0:
        cur = cur[:cut]
    open(os.path.join(DOCS, 'shadows.md'), 'w', encoding='utf-8').write(cur + '\n'.join(A))
    json.dump({sh['id']: [dict(nid=nodes[i]['nid'], src=nodes[i]['src'], shard=nodes[i]['shard'],
                               level=nodes[i]['level'], tau=nodes[i]['tau'], budget=nodes[i]['budget'],
                               at_budget=nodes[i].get('at_budget'), via=nodes[i].get('via'),
                               conditioned=[list(map(float, q)) for q in nodes[i]['cores']])
                          for i in sh['members']] for sh in ks},
              open(os.path.join(RES, 'shadow_nodes_k0.json'), 'w'), indent=1)
    json.dump([dict(nid=n['nid'], src=n['src'], shard=n['shard'], level=n['level'], budget=n['budget'],
                    tau=n['tau'], nsig=n['nsig'], comp=n.get('comp'), at_budget=n.get('at_budget'))
               for n in un], open(os.path.join(RES, 'unexplained_k0.json'), 'w'), indent=1)
    print('appended Part II:', len(ks), 'k0 shadows,', len(hits), 'coincidences,', len(exact), 'exact')

if __name__ == '__main__':
    main()
