"""A107: emit docs/shadows/*.svg and docs/shadows.md from results/{extract,shadows,minima}.json."""
import os, sys, json, math, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L, minimise as M, svg as SV

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
RES = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')
DOCS = os.path.join(ROOT, 'docs')
SVGD = os.path.join(DOCS, 'shadows')
S0, SHAT = L.S0, L.SHAT

CLASS = {
    ('A57', 'k5_11'): 'k5_11', ('A57', 'k5_16'): 'k5_16', ('A60', ''): 'trump5',
}

def class_of(node):
    if node['src'] == 'A57':
        return 'k5_11' if node['shard'].startswith('k5_11') else 'k5_16'
    if node['src'] == 'A60':
        return 'trump5'
    return node.get('skeleton') or node['nid'].split('.')[0]

def main():
    ex = json.load(open(os.path.join(RES, 'extract.json')))
    shs = json.load(open(os.path.join(RES, 'shadows.json')))
    nodes = ex['nodes']
    os.makedirs(SVGD, exist_ok=True)

    # ---------- per-shadow node lists
    for sh in shs:
        mem = sorted({i for st in sh['structs'] for i in st['members']})
        sh['members'] = mem
        sh['classes'] = collections.Counter(class_of(nodes[i]) for i in mem)
        sh['levels'] = collections.Counter(nodes[i]['level'] for i in mem)
        sh['srcs'] = collections.Counter(nodes[i]['src'] for i in mem)
        sh['via'] = collections.Counter(nodes[i].get('via') for i in mem)

    # ---------- drawings
    for sh in shs:
        prim = max(sh['structs'], key=lambda d: d['nnodes'])
        rep = nodes[prim['members'][0]] if prim['members'] else nodes[sh['members'][0]]
        sc = 118
        oy = 56 + S0 * sc
        body = []
        p1, gap = SV.panel_lp(30, oy, sc, f"{sh['id']} panel 1 - raw LP dual support of {rep['nid']}",
                              rep['cores'], [q for q in rep['cfg'][len(rep['cores']):]])
        body += p1
        W1 = S0 * sc + 60
        p2, _ = SV.panel_pack(30 + W1, oy, sc, f"{sh['id']} panel 2 - the shadow at s* = {sh['s']:.6f}",
                              f"{len(sh['slots'])} snapped slot squares + {sh['nfree']} free squares; "
                              f"s* - s-hat = {sh['ds']:+.6f}", sh['s'], sh['free'], sh['slots'])
        body += p2
        W = 2 * W1 + 60
        H = int(oy + 40)
        if sh.get('sweep'):
            body += SV.tilt_panel(30 + 2 * W1, oy - 60, 300, 190, sh['sweep'], sh['s'],
                                  sh['common_tilt'] or 0.0)
            W = 2 * W1 + 400
        SV.write_svg(os.path.join(SVGD, f"{sh['id']}.svg"), body, int(W), H)

    # ---------- unexplained
    unexp = ex['unexplained']
    un = [nodes[i] for i in unexp]
    un_by = collections.Counter((n['src'], class_of(n), n['level']) for n in un)

    # ---------- markdown
    L_ = []
    a = L_.append
    a('# The shadow gallery (A107)\n')
    a('What the LP is looking at when it stalls.  For every ALIVE-at-LP node of A57 (both classes, all')
    a('shards, levels 1-4), A60 (trump5) and A61 (window stragglers), the LP dual support was loaded,')
    a('turned into a candidate near-packing, snapped to named slot cells, and minimised directly over')
    a('the side.  Distinct shadows are listed once, ordered by the number of alive nodes they explain.\n')
    a('Part I below is the pinned classes (A57 k5_11 / k5_16, A60 trump5, A61 window stragglers).')
    a('**Part II, at the end of this file, is the k0_00 cells** of A38-root-power, A85-k0-route and')
    a('A99-k0-tree-v2, which have no pins and so are de-duplicated over the full D4.\n')
    a('## Method\n')
    a('1. **Alive-at-LP** = `dead == False` in the node json (the LP did not certify the case).')
    a(f'   {len(nodes)} such nodes on disk: ' +
      ', '.join(f'{k} {v}' for k, v in collections.Counter(n["src"] for n in nodes).items()) + '.')
    a('2. **Shadow** = the hypothesis cores (the class skeleton + every conditioned square, taken at')
    a('   its box centre) together with the integral part of the dual support (weights 1).  The LP rows')
    a('   are configuration-space *cells* of pitch 0.192 in position and 5 deg in tilt, so the drawn')
    a('   representatives overlap by up to that pitch - this is the "overlaps and all" panel, and the')
    a('   numbers are reported on every drawing.  Verified integral LP solutions in this corpus have')
    a('   worst pairwise SAT gap -0.2045, which fixes the disjointness tolerance at -0.21.')
    a('3. **Fractional supports** are split into integral components: a weight-greedy maximum-')
    a('   independent-set search over the placements with y > 0.02 in the cell-disjointness graph,')
    a('   looking for `budget` many.  A node is *explained* only if a full-size component exists.')
    a('4. **Snapping**: a placement within 0.05 of a corner-stacked unit cell and 3 deg of axis is')
    a('   named BL(i,j)/BR(i,j)/TL(i,j)/TR(i,j); the rest are the free squares f0..fn.')
    a('5. **Minimisation**: slot squares fixed as affine functions of s, free squares (cx, cy, theta)')
    a('   and s variable, SLSQP, restarts = every alive node\'s own LP seed + >= 100 random')
    a('   (pinwheel rings and scatters).  Generalises `docs/residue_map/gen_pinwheel_k7.py`.')
    a('6. **De-duplication.**  Each alive node is followed from its OWN LP seed to the minimum it')
    a('   actually reaches, so a structure with several local minima splits its nodes between them.')
    a('   The landings are then de-duplicated.  The unit of the gallery is a **value of s\\***, not a')
    a('   point in configuration space, for a reason the k7 family makes concrete: its five landings')
    a('   share the same three-square 48.435 deg core and the same seven slot squares, and differ')
    a('   only in where the loose fourth square sits along its flat direction (0.15 in x) - the')
    a("   brief's 0.05 / 3 deg point rule would call those five different shadows.  A106 reached the")
    a('   same conclusion independently ("a shadow is a value of s*, not a point", `measurements.md`')
    a('   2.1).  The column **#cfg** counts how many distinct minimised configurations share the')
    a("   value, under the brief's 0.05 / 3 deg rule applied modulo D4 to the **load-bearing**")
    a('   squares (nonzero Fritz-John force); rattlers and struts are excluded from that comparison')
    a('   for exactly the reason above.  Different slot/free splittings of one packing collapse')
    a('   automatically - that is why 5-slot+6-free, 6-slot+5-free and 7-slot+4-free structures land')
    a('   on one entry.')
    a('7. **Contacts and forces**: contacts at gap < 1e-7, classified vertex-on-edge / flush /')
    a('   exactly-opposite (vertex-vertex).  The Jacobian rows are the exact analytic derivatives of')
    a('   the vertex-to-supporting-line distance (including the lever term from the edge owner\'s')
    a('   rotation) - never a finite difference of a SAT gap, which is wrong at flush and opposite')
    a('   contacts.  Contact forces are the Fritz-John multipliers from nnls(J^T, e_s), rows unit-')
    a('   normalised.  Every flat direction is then tested at SECOND order along the exact gaps.\n')
    a('### What "explains" means, and what it does not\n')
    a("A shadow explains a node when that node's own LP dual support, snapped and then released,")
    a("minimises to it.  It does **not** mean the node's pose box contains the shadow: A106")
    a('(`attempts/A106-shadow-diameter/notes/measurements.md` 2.2) measured exactly that and found')
    a('**zero** of 62 landed open boxes contains a shadow - the box-constrained minimum always sits')
    a('on the box boundary and flows out of B when released, median inf-gap 0.3166, about 9 basin')
    a('radii.  A107 reuses that finding rather than re-deriving it; what is new here is *which*')
    a("shadow each alive node's support flows to, and the contact graph of that shadow.  The s*")
    a("spectrum below reproduces A106's census (3.886746, 3.902674, 3.912232, 3.914214, 3.924003,")
    a('3.942809, 4.000000) to 6-7 digits from an independent minimiser, with the slot squares held')
    a("exactly on their slot lines rather than sliding inside A57's delta = 1e-2 slack cores.\n")
    a('### Shadows with fewer than 11 squares\n')
    a('A node whose LP run did not converge can be ALIVE-at-LP with an integral support SHORTER than')
    a('its budget.  Its shadow then has k < 11 squares and its s* falls below s-hat - correctly so:')
    a('a k9 or k10 packing has room to spare.  Those entries are the LP telling you it never found')
    a('the last square, not a near-solution.\n')
    a('## Gallery table\n')
    a('| shadow | class(es) of the alive nodes | k of the shadow | s* | s* - s-hat | alive nodes | #cfg | levels | free sq | common tilt | flexes at fixed s |')
    a('|---|---|---|---|---|---|---|---|---|---|---|')
    for sh in shs:
        an = sh['analysis']
        cls = ', '.join(f'{k} x{v}' for k, v in sh['classes'].most_common())
        lv = ', '.join(f'L{k}:{v}' for k, v in sorted(sh['levels'].items()))
        ct = f"{sh['common_tilt']:.3f} deg" if sh['common_tilt'] is not None else 'no'
        a(f"| **{sh['id']}** | {cls} | k{sh['nsquares']} ({len(sh['slots'])} slot + {sh['nfree']} free) | "
          f"{sh['s']:.6f} | {sh['ds']:+.6f} | {sh['nnodes']} | {sh.get('nconfigs', 1)} | {lv} | {sh['nfree']} | {ct} | "
          f"{an.get('flexes_fixed_s')} |")
    a('')
    a(f"Total alive nodes explained by an integral shadow: **{sum(sh['nnodes'] for sh in shs)}** of "
      f"**{len(nodes)}**.  Not explained: **{len(unexp)}** (see the last section).\n")

    a('### What the table says\n')
    a('* **Half of the explained alive nodes (620 of 1260) sit on S01, whose shadow minimises to a')
    a("  side of exactly 4.000000** - s-hat + 0.1229, thirteen times the k7 pinwheel's own slack.")
    a('  For those nodes the LP is not near a critical packing at all; its integral support is a')
    a('  side-4 arrangement, and 62 combinatorially distinct ones share the value.  That is the LP')
    a('  saying "this branch has room", not "this branch is nearly feasible".')
    a("* **S02 is the PI's k7 pinwheel** (7 slot squares, 4 free at one tilt 48.4351 deg,")
    a('  s* = 3.886746 = s-hat + 0.009662), reproduced here to 7 digits from an independent')
    a("  minimiser and from 267 different nodes' own LP seeds across THREE classes (k5_11, k5_16,")
    a('  trump5).  It carries the deep tree: of the 19 explained level-3 and 9 explained level-4')
    a('  nodes, 10 and 4 respectively are on S02 - more than any other entry, and 97 of the 232')
    a('  explained level-2 nodes as well.  The deeper A57 goes, the more of what is left is this one')
    a('  shadow.')
    a('* **S07 is new: s\\* = 3.885618 = s-hat + 0.008534, BELOW the k7 pinwheel.**  A k11 packing on')
    a('  the trump5 skeleton `BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)` with five free')
    a("  squares near 44.88 deg.  A106's census floor for these classes was 3.886746, so that floor")
    a('  was not the true one.  Verified: containment exact, worst pairwise SAT -9.5e-8 (inside')
    a("  SLSQP's own tolerance), and feasibility restoration at s = s* + 1e-7 reaches a")
    a('  configuration with every non-degenerate gap >= 0.  NOT verified: an exact interval')
    a("  endpoint certificate in A106's style; treat it as numerically verified only.")
    a('* Entries with s\\* **below** s-hat are the k9/k10 shadows of non-converged LP runs: fewer')
    a('  than 11 squares, so a smaller side is expected and means nothing.')
    a('* **13 of the 53 entries are clean stationary points** (KKT residual <= 1e-6), among them S01,')
    a('  S02, S03, S05, S08 and S09 - between them 1065 of the 1260 explained nodes.  The other 40')
    a('  (S04, S06, S07, S10-S18, S20, S21, S23-S29, S31, S33-S35, S37-S43, S45-S47, S49-S53) lean on')
    a('  a variable bound or stopped short; each carries a convergence caveat in its section and its')
    a('  s* is an upper bound on that shadow.')
    a('* Across the gallery: 38 k11 shadows (1132 nodes) and 15 k9/k10 ones (128 nodes); 207 distinct')
    a('  minimised configurations; 160 flat directions in all, of which 71 are genuine flexes and 80')
    a('  are blocked at second order (the exactly-opposite point contacts - 15 entries carry one);')
    a('  20 of 238 free squares are rattlers whose removal leaves s* unchanged.\n')
    for sh in shs:
        an = sh['analysis']
        a(f"## {sh['id']} - a k{sh['nsquares']} packing at s* = {sh['s']:.6f} on the boundary of class "
          f"{', '.join(sh['classes'])}\n")
        a(f"![{sh['id']}](shadows/{sh['id']}.svg)\n")
        a(f"* **s\\*** = {sh['s']:.9f} = s-hat {sh['ds']:+.9f}  (s0 = {S0:.6f}, s\\* - s0 = {sh['s']-S0:+.6f})")
        a(f"* **shadow** = {len(sh['slots'])} slot squares `{' '.join(sh['slots'])}` + {sh['nfree']} free "
          f"squares f0..f{sh['nfree']-1}; a k{sh['nsquares']} packing.")
        a(f"* **explains** {sh['nnodes']} alive-at-LP nodes: " +
          ', '.join(f'{k} x{v}' for k, v in sh['classes'].most_common()) + '; levels ' +
          ', '.join(f'L{k}:{v}' for k, v in sorted(sh['levels'].items())) + '; ' +
          ', '.join(f'{k} {v}' for k, v in sh['via'].most_common()) + ' support.')
        a(f"* **load-bearing squares at this landing**: `{'` `'.join(sh.get('loaded', []))}` "
          f"({len(sh.get('loaded', []))} of {sh['nsquares']}); "
          f"**{sh.get('nconfigs', 1)} distinct minimised configuration(s)** share this s*.")
        a(f"* **multiplicity**: {len(sh['structs'])} landings / slot-free splittings "
          f"(" + '; '.join(f"{len(st['slots'])} slot + {st['nfree']} free ({st['nnodes']} nodes)"
                           for st in sh['structs'][:6]) +
          (f"; +{len(sh['structs'])-6} more" if len(sh['structs']) > 6 else '') + ").")
        if sh['common_tilt'] is not None:
            a(f"* **the free squares share one tilt**: {sh['common_tilt']:.4f} deg "
              f"(spread {max(sh['tilts'])-min(sh['tilts']):.2e} deg).")
        else:
            a("* the free squares do **not** share a tilt: " +
              ', '.join(f'f{i} {t:.3f} deg' for i, t in enumerate(sh['tilts'])) + '.')
        a(f"* **restarts**: {sh['confirm']['nfeas']} feasible of {sh['confirm']['nstart']}; distinct minima "
          f"{sh['confirm']['minima'][:8]}.")
        a('')
        a('**Free square poses at s\\***')
        a('')
        a('| square | cx | cy | tilt (deg) |')
        a('|---|---|---|---|')
        for i, f in enumerate(sh['free']):
            a(f"| f{i} | {f[0]:.6f} | {f[1]:.6f} | {math.degrees(L.tmod(f[2])):.4f} |")
        a('')
        a('**Contact graph at s\\*** (gap < 1e-7; contact force = Fritz-John multiplier, rows unit-normalised)')
        a('')
        a('| contact | type | gap | force |')
        a('|---|---|---|---|')
        forces = collections.defaultdict(float)
        for k, v in (an.get('resultant') or {}).items():
            x, y = k.split('|')
            forces[(x, y)] = v
        for c in an['contacts']:
            f = forces.get((c['a'], c['b']), 0.0)
            a(f"| `{c['a']}` - `{c['b']}` | {c['kind']} | {c['gap']:+.1e} | {f:.4f} |")
        for w in sorted({(w['a'], w['b']) for w in an['walls']}):
            a(f"| `{w[0]}` - {w[1]} | wall | 0 | {forces.get(w, 0.0):.4f} |")
        a('')
        bind = sorted(((v, k) for k, v in forces.items() if v > 1e-6), reverse=True)
        if bind:
            a('**Binding** (largest Fritz-John resultant first): ' +
              ', '.join(f"`{k[0]}`-`{k[1]}` ({v:.3f})" for v, k in bind[:6]) +
              f".  KKT residual {an['kkt_residual']:.1e}." +
              ('  Exactly-opposite (vertex-vertex) contacts, whose normal is a cone and whose '
               'individual multipliers are therefore ill-conditioned: ' +
               ', '.join('`%s`-`%s`' % (u, v2) for u, v2 in an.get('degenerate', [])) + '.'
               if an.get('degenerate') else ''))
        if an['kkt_residual'] > 1e-6:
            a(f"**Convergence caveat**: KKT residual {an['kkt_residual']:.1e} (> 1e-6).  The residual "
              f"measures how far e_s is from the cone of the active CONTACT rows; it is nonzero when "
              f"the landing also leans on a variable BOUND (s in [3.4, 4.6], centres in [0, 4.6]), "
              f"which is not a contact and so is not in the Jacobian, or when SLSQP stopped short of "
              f"a stationary point.  Either way s* = {sh['s']:.6f} is an upper bound on this "
              f"shadow's true value and the contact set may be mis-counted at the 1e-7 threshold.")
        a(f"**Rank**: {an['nrows']} contact rows, {an['nvars']} variables (s + 3 per free square); "
          f"rank {an['rank']}; at fixed s rank {an['rank_fixed_s']} of {an['nvars']-1}, so "
          f"**{an['flexes_fixed_s']} flat direction(s)**.")
        if an['flat']:
            for fl in an['flat']:
                a(f"  * flat direction {fl['dir']}: {fl['verdict']} "
                  f"(worst active gap changes by {fl['delta_1e_3']:+.2e} at |t| = 1e-3 and "
                  f"{fl['delta_3e_3']:+.2e} at 3e-3 and {fl.get('delta_1e_2', 0):+.2e} at 1e-2, "
                  + (f"ratios {round(fl['ratio'],2)} / {round(fl['ratio10'],1)}; 9 and 100 are the "
                     f"quadratic signature - curvature {fl['curvature']:+.3e})."
                     if fl.get('ratio') is not None and fl.get('ratio10') is not None
                     else "no change at any step - a genuine one-parameter motion)."))
        else:
            a('  * no flat directions: the shadow is first-order rigid at fixed s.')
        a('')
        a('**T2 drain hint - the load-bearing subgraph** (remove one free square and re-minimise)')
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
        idle = sorted({k for k, v in forces.items() if v <= 1e-6})
        if idle:
            a('')
            a('**Idle contacts** (zero Fritz-John force - struts, not load paths): ' +
              ', '.join(f'`{u}`-`{v}`' for u, v in idle) + '.')
        a('')
        a(f"Load-bearing free squares: {', '.join('`%s`' % x for x in lb) or 'none'}.  "
          f"Rattlers/struts (removal leaves s\\* unchanged): {', '.join('`%s`' % x for x in rt) or 'none'}.")
        if sh.get('sweep'):
            pts = [(d['tilt_deg'], d['s']) for d in sh['sweep'] if d['s'] is not None]
            if pts:
                a('')
                a('**Common-tilt sweep** (all free squares held at one tilt, slot squares fixed, s minimised)')
                a('')
                a('| tilt (deg) | ' + ' | '.join(f'{t:.2f}' for t, _ in pts) + ' |')
                a('|---|' + '---|' * len(pts))
                a('| s* | ' + ' | '.join(f'{v:.6f}' for _, v in pts) + ' |')
        a('')
        a('**Alive nodes explained** (' + str(len(sh['members'])) +
          '; each id is src/shard/node(level).  Their pose boxes: A57 level-1 boxes are '
          '0.1398 x 0.1398 x 9.73 deg and halve in every coordinate per level (A106 T1); the '
          'conditioned square pose of every node below is in '
          '`attempts/A107-shadow-gallery/results/shadow_nodes.json`): ')
        ids = [f"{nodes[i]['src']}/{nodes[i]['shard']}/{nodes[i]['nid']}(L{nodes[i]['level']})"
               for i in sh['members']]
        a('`' + '` `'.join(ids[:200]) + '`' + ('' if len(ids) <= 200 else f' ... (+{len(ids)-200} more, full list in `attempts/A107-shadow-gallery/results/shadow_nodes.json`)'))
        a('')

    a('## Alive nodes not explained by any integral shadow\n')
    a(f'{len(unexp)} of {len(nodes)} alive-at-LP nodes have a dual support that is fractional AND contains')
    a('no full-size integral component (no `budget` many pairwise cell-disjoint placements among those')
    a('with y > 0.02).  For these the LP is stalling on a genuinely fractional object, not on a')
    a('near-packing, so there is no drawing to hand back.\n')
    a('| source | class | level | count | largest independent set found (of budget) |')
    a('|---|---|---|---|---|')
    agg = collections.defaultdict(list)
    for n in un:
        agg[(n['src'], class_of(n), n['level'])].append(n)
    for k in sorted(agg):
        g = agg[k]
        hist = collections.Counter(f"{x.get('comp')}/{x.get('budget')}" for x in g)
        a(f"| {k[0]} | {k[1]} | L{k[2]} | {len(g)} | " +
          ', '.join(f'{a_} x{b}' for a_, b in hist.most_common(5)) + ' |')
    a('')
    a('Full list: `attempts/A107-shadow-gallery/results/unexplained.json`.')
    a('')
    open(os.path.join(DOCS, 'shadows.md'), 'w', encoding='utf-8').write('\n'.join(L_))
    json.dump({sh['id']: [dict(nid=nodes[i]['nid'], src=nodes[i]['src'], shard=nodes[i]['shard'],
                               level=nodes[i]['level'], budget=nodes[i]['budget'], tau=nodes[i]['tau'],
                               via=nodes[i].get('via'),
                               conditioned=[list(map(float, q)) for q in
                                            nodes[i]['cores'][len(nodes[i]['skel_slots']):]])
                          for i in sh['members']] for sh in shs},
              open(os.path.join(RES, 'shadow_nodes.json'), 'w'), indent=1)
    json.dump([dict(nid=n['nid'], src=n['src'], shard=n['shard'], level=n['level'],
                    budget=n['budget'], tau=n['tau'], nsig=n['nsig'], comp=n.get('comp'))
               for n in un], open(os.path.join(RES, 'unexplained.json'), 'w'), indent=1)
    print('wrote docs/shadows.md and', len(shs), 'svgs')

if __name__ == '__main__':
    main()
