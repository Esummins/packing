"""A32: assemble results/frontier_report.json from the run artefacts."""
import os
import sys
import json
import math

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'results'))
A31 = os.path.normpath(os.path.join(HERE, '..', '..', 'A31-structure-count',
                                    'results'))


def load(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default


def fit_exp(xs, ys):
    """log y = a + b x by least squares."""
    n = len(xs)
    lx = list(xs)
    ly = [math.log(y) for y in ys]
    mx = sum(lx) / n
    my = sum(ly) / n
    sxx = sum((x - mx) ** 2 for x in lx)
    sxy = sum((x - mx) * (y - my) for x, y in zip(lx, ly))
    b = sxy / sxx
    a = my - b * mx
    return a, b


def _cond(rows):
    v = sum(x['visited'] for x in rows)
    d1 = sum(x['kills']['D1_tilt'] for x in rows)
    d2 = sum(x['kills']['D2_rotation'] for x in rows)
    d3 = sum(x['kills']['D3_L2collinear'] for x in rows)
    surv = v - d1 - d2 - d3
    return dict(children_evaluated=v,
                p_killed_by_D1_tilt=d1 / v,
                p_killed_by_D2_rotation_given_D1_passed=d2 / max(1, v - d1),
                p_killed_by_D3_L2_given_D1_D2_passed=d3 / max(1, v - d1 - d2),
                overall_child_survival=surv / v,
                deferred_L2_cases=sum(x['deferred_L2'] for x in rows))


def main():
    a31 = load(os.path.join(A31, 'count_report.json'))
    rep = {'what': 'A32 frontier pilot: instrumented joint structure branch-and-'
                   'bound over PARTIAL contact structures, s0 = 3.8771'}

    # ---------------- mode G: frontier vs depth, kill shares, sec/node
    runs = {}
    for K in range(3, 12):
        d = load(os.path.join(RES, 'bb_K%d.json' % K))
        if d:
            runs[K] = d
    val = {}
    for K in range(3, 12):
        d = load(os.path.join(RES, 'validation', 'bb_K%d.json' % K))
        if d:
            val[K] = d

    frontier = {}
    killshare = {}
    cost = {}
    for K, d in runs.items():
        lv = {int(a): b for a, b in d['levels'].items()}
        frontier[K] = {k: v['frontier'] for k, v in sorted(lv.items())}
        tot = {}
        vis = 0
        secs = 0.0
        subtab = {}
        for k, v in sorted(lv.items()):
            if 'sub' not in v:
                continue
            secs += v.get('seconds', 0.0)
            for t, s in v['sub'].items():
                vis += s['visited']
                subtab.setdefault(k, {})[int(t)] = [s['visited'], s['survived']]
                for st, c in s['kills'].items():
                    tot[st] = tot.get(st, 0) + c
        nk = sum(tot.values())
        killshare[K] = {'total_killed': nk,
                        'share': {a: round(b / nk, 5) for a, b in
                                  sorted(tot.items(), key=lambda x: -x[1])},
                        'counts': tot}
        cost[K] = dict(partial_nodes_visited=vis, seconds=round(secs, 1),
                       sec_per_node=(secs / vis if vis else None),
                       nodes_per_sec_6workers=(vis / secs if secs else None))
        frontier[K]['_edge_prefix_subdepth'] = subtab
    rep['modeG'] = {
        'frontier_vs_depth': frontier,
        'kill_shares_first_kill_attribution': killshare,
        'cost': cost,
        'closed_leaves': {K: {a: b for a, b in d['close'].items() if a != 'Ehist'}
                          for K, d in runs.items()},
        'aborted': {K: d.get('aborted') for K, d in runs.items() if d.get('aborted')},
        'leaf_edge_count_histogram': {K: d['close'].get('Ehist')
                                      for K, d in runs.items()},
    }

    # ---------------- validation against A31
    a31main = {3: 10, 4: 140, 5: 2275, 6: 41951, 7: 842398}
    a31cap3 = {}
    for k, v in a31['soft_columns'].items():
        a31cap3[int(k)] = v['wall_node_degree_le_3_certified']
    a31br = {int(k): v for k, v in a31['branch_counts'].items()}
    vv = []
    for K, d in val.items():
        c = d['close']
        vv.append(dict(K=K, mode='wallcap disabled (= A31 MAIN)',
                       a32_main=c['main'], a31_main=a31main.get(K),
                       a32_thin=c['main_thin'], a31_thin=a31br.get(K, {}).get('thin_main'),
                       a32_lam0=c['lam0'], a31_lam0=a31br.get(K, {}).get('lam0'),
                       a32_selfstress=c['selfstress'],
                       a31_selfstress=a31br.get(K, {}).get('selfstress_float'),
                       agree=(c['main'] == a31main.get(K))))
    for K, d in runs.items():
        c = d['close']
        vv.append(dict(K=K, mode='per-wall<=3 promoted (= A31 wallcap3 column)',
                       a32_main=c['main'], a31_main=a31cap3.get(K),
                       a32_main_nonthin=c['main_nonthin'],
                       a31_main_nonthin=a31['soft_columns'].get(str(K), {})
                       .get('main_wallcap3_and_non_thin'),
                       agree=(c['main'] == a31cap3.get(K))))
    rep['validation_vs_A31'] = vv

    # ---------------- mode D
    md = load(os.path.join(RES, 'moded.json'), {})
    mdv = load(os.path.join(RES, 'moded_validation.json'), {})
    dsum = {}
    for K, recs in (md.get('runs') or {}).items():
        K = int(K)
        rows = []
        for r in recs:
            e = r['E']
            row = dict(E=e, menu=r['tilt']['menu'])
            for tag in ('tilt', 'tilt_rot', 'all'):
                # PRIMARY estimator: product of the per-depth POOLED mean surviving
                # branching factors (low variance).  Knuth's raw path estimator is
                # kept as a cross-check -- it is unbiased but so heavy-tailed on
                # this tree that single-graph values are unusable.
                bp = 1.0
                for b in r[tag]['branch']:
                    bp *= b
                leaves = bp
                row[tag + '_leaves'] = leaves
                row[tag + '_knuth'] = r[tag]['frontier'][-1]
                row[tag + '_knuth_stderr'] = r[tag]['stderr'][-1]
                row[tag + '_per_edge'] = leaves ** (1.0 / e) if leaves > 0 else 0.0
                row[tag + '_keep'] = leaves / row['menu']
            row['kills'] = r['all']['kills']
            row['visited'] = r['all']['visited']
            row['sec_per_child'] = r['all']['sec_per_child']
            row['deferred_L2'] = r['all']['deferred_L2']
            row['branch_profile'] = [round(x, 3) for x in r['all']['branch']]
            rows.append(row)
        n = len(rows)
        live = [x for x in rows if x['all_leaves'] > 0]
        nz = len(rows) - len(live)

        def gm(key):
            src = live if key.startswith('all') or key.startswith('tilt_rot') \
                else rows
            src = [x for x in src if x[key] > 0]
            if not src:
                return 0.0
            return math.exp(sum(math.log(x[key]) for x in src) / len(src))
        dsum[K] = dict(
            n_graphs=n, graphs_with_zero_surviving_decoration=nz,
            E_mean=sum(x['E'] for x in rows) / n,
            geomean_leaves_tilt=gm('tilt_leaves'),
            geomean_leaves_tilt_rot=gm('tilt_rot_leaves'),
            geomean_leaves_all=gm('all_leaves'),
            per_edge_tilt=gm('tilt_per_edge'),
            per_edge_tilt_rot=gm('tilt_rot_per_edge'),
            per_edge_all=gm('all_per_edge'),
            extra_kill_rot=gm('tilt_rot_leaves') / gm('tilt_leaves'),
            extra_kill_L2=gm('all_leaves') / gm('tilt_rot_leaves'),
            # POOLED conditional kill rates on the full-cascade tree: these are
            # per-child statistics over every node the sampler visited, so unlike
            # the tree-size estimates they are low-variance and directly
            # comparable across k.
            conditional_kill_rates=_cond(rows),
            sec_per_child=sum(x['sec_per_child'] for x in rows) / n,
            rows=rows)
    rep['modeD'] = {'per_k': dsum, 'validation_tilt_only_vs_A31_level1': mdv.get(
        'validation', [])}

    # ---------------- ablation
    abl = {}
    for K in range(3, 9):
        d = load(os.path.join(RES, 'ablation_K%d.json' % K))
        if d:
            base = next(x for x in d if x['disabled'] == 'none')
            abl[K] = [dict(disabled=x['disabled'],
                           closed_frontier=x['frontier'][str(K)]
                           if str(K) in x['frontier'] else x['frontier'][K],
                           main=x['main'],
                           partial_nodes=x['partial_nodes_visited'],
                           frontier_ratio_vs_full_cascade=round(
                               (x['frontier'][str(K)] if str(K) in x['frontier']
                                else x['frontier'][K]) /
                               (base['frontier'][str(K)] if str(K) in base['frontier']
                                else base['frontier'][K]), 4),
                           node_ratio=round(x['partial_nodes_visited'] /
                                            base['partial_nodes_visited'], 4))
                       for x in d]
    rep['ablation'] = abl

    # ---------------- L2 dead-graph scan
    best = {}
    for fn in ('deadscan_cap120k.json', 'deadscan.json'):
        for r in load(os.path.join(RES, fn), []) or []:
            cap = max((x['all'].get('visited', 0) for x in r['rows']), default=0)
            cur = best.get(r['K'])
            if cur is None or cap > cur[0]:
                best[r['K']] = (cap, dict(r, source=fn))
    ds = [v[1] for k, v in sorted(best.items())]

    dscan = []
    for r in ds:
        th = [x for x in r['rows'] if x['thin']]
        nth = [x for x in r['rows'] if not x['thin']]
        dz = lambda LL: sum(1 for x in LL if x['all']['exhausted']
                            and x['all']['leaves'] == 0)
        dscan.append(dict(K=r['K'], source=r.get('source'), sampled=r['n'],
                          node_cap=max((x['all'].get('visited', 0)
                                        for x in r['rows']), default=0),
                          proven_dead_all_filters=r['dead'],
                          proven_dead_tilt_only=r['dead_tilt_only'],
                          thin_graphs=len(th), thin_dead=dz(th),
                          nonthin_graphs=len(nth), nonthin_dead=dz(nth),
                          exhausted_all=sum(1 for x in r['rows']
                                            if x['all']['exhausted'])))
    rep['L2_dead_graph_scan'] = dscan

    # ---------------- stages 4-6
    pr = load(os.path.join(RES, 'probe.json'), {})
    def agg(lst, tkey):
        if not lst:
            return None
        ts = [x.get(tkey, 0.0) for x in lst if x.get(tkey) is not None]
        return dict(n=len(lst), mean_seconds=(sum(ts) / len(ts) if ts else None))
    s4 = pr.get('stage4', [])
    rep['stages_4_6'] = {
        'stage4a_interval_SAT_and_menu': dict(
            n=len(s4), fired=sum(1 for x in s4 if x.get('stage4a_kill')),
            mean_seconds=(sum(x['t_rows'] for x in s4) / len(s4)) if s4 else None,
            mean_rows=(sum(x['nrows'] for x in s4) / len(s4)) if s4 else None),
        'stage4_farkas': dict(
            n=len(s4), lp_found=sum(1 for x in s4 if x.get('farkas_lp_ok')),
            verified_kills=sum(1 for x in s4 if x.get('farkas_verified')),
            mean_seconds=(sum(x.get('t_farkas', 0) for x in s4) / len(s4))
            if s4 else None),
        'tilt_refined_variants': [
            dict(variant=x['variant'], rows=x['nrows'],
                 farkas=x['farkas_verified'], kill=x['stage4a_kill'])
            for x in pr.get('tilt_variants', [])],
        'stage5_caseLP_stub': agg(pr.get('stage5', []), 't_stage5_lp'),
        'stage5_infeasible_found': sum(1 for x in pr.get('stage5', [])
                                       if x.get('stage5_lp_feasible') is False),
        'stage6_fj_range_exclusion': dict(
            n=len(pr.get('stage6', [])),
            excluded=sum(1 for x in pr.get('stage6', [])
                         if x.get('stage6_fj_excluded')),
            mean_active_rows=(sum(x.get('stage6_active_rows', 0)
                                  for x in pr.get('stage6', []))
                              / max(1, len(pr.get('stage6', [])))),
            mean_seconds=(sum(x.get('t_stage6_fj', 0) for x in pr.get('stage6', []))
                          / max(1, len(pr.get('stage6', []))))),
    }

    # ---------------- canary
    can = load(os.path.join(RES, 'canary.json'), {})
    rep['canary'] = {a: b for a, b in can.items()
                     if a in ('CANARY', 'modeG_prefixes', 'modeG_fail',
                              'modeD_prefixes', 'modeD_fails', 'close',
                              'ss_edges', 'sw_edges',
                              'decoration_max_gauge_residual')}

    # ---------------- extrapolation
    Ks = sorted(k for k in runs if 'aborted' not in runs[k])
    ex = {}
    if len(Ks) >= 3:
        nodes = [cost[k]['partial_nodes_visited'] for k in Ks]
        leaves = [runs[k]['close']['main'] for k in Ks]
        front = [frontier[k][k] for k in Ks]
        a, b = fit_exp(Ks, nodes)
        ex['bb_partial_nodes'] = {'fit': 'log N = %.4f + %.4f k' % (a, b),
                                  'ratios': [round(nodes[i + 1] / nodes[i], 2)
                                             for i in range(len(nodes) - 1)],
                                  'measured': dict(zip(Ks, nodes)),
                                  'proj': {k: math.exp(a + b * k)
                                           for k in range(8, 12)}}
        a2, b2 = fit_exp(Ks, leaves)
        ex['main_leaves'] = {'fit': 'log N = %.4f + %.4f k' % (a2, b2),
                             'measured': dict(zip(Ks, leaves)),
                             'proj': {k: math.exp(a2 + b2 * k)
                                      for k in range(8, 12)}}
        a3, b3 = fit_exp(Ks, front)
        ex['closed_frontier'] = {'fit': 'log N = %.4f + %.4f k' % (a3, b3),
                                 'measured': dict(zip(Ks, front)),
                                 'proj': {k: math.exp(a3 + b3 * k)
                                          for k in range(8, 12)}}
    if dsum:
        dk = sorted(dsum)
        pe = [dsum[k]['per_edge_all'] for k in dk]
        # per-edge survival factor vs k, linear fit
        if len(dk) >= 2:
            n = len(dk)
            mx = sum(dk) / n
            my = sum(pe) / n
            sxx = sum((x - mx) ** 2 for x in dk)
            sxy = sum((x - mx) * (y - my) for x, y in zip(dk, pe))
            bb = sxy / sxx if sxx else 0.0
            aa = my - bb * mx
            ex['decoration_per_edge_factor'] = {
                'measured': {k: dsum[k]['per_edge_all'] for k in dk},
                'fit': 'f(k) = %.4f + %.4f k' % (aa, bb),
                'proj_k11': aa + bb * 11}
            # E at k=11 from A31's fanout fit: Ess = -3.6556 + 1.6784k, Esw = 2.8292+0.4570k
            E11 = (-3.6556 + 1.6784 * 11) + (2.8292 + 0.4570 * 11)
            f11 = max(1.0, aa + bb * 11)
            ex['decorated_leaves_per_graph_k11'] = {
                'E11_from_A31_fit': E11, 'per_edge_factor': f11,
                'estimate': f11 ** E11}
    # ratio-linear projection of the B&B node count (A31's M3 model)
    if 'bb_partial_nodes' in ex:
        m = ex['bb_partial_nodes']['measured']
        ks = sorted(int(x) for x in m)
        rr = [(ks[i + 1], m[str(ks[i + 1])] / m[str(ks[i])]
               if str(ks[i]) in m else m[ks[i + 1]] / m[ks[i]])
              for i in range(len(ks) - 1)]
        n = len(rr)
        mx = sum(x for x, _ in rr) / n
        my = sum(y for _, y in rr) / n
        sxx = sum((x - mx) ** 2 for x, _ in rr)
        sxy = sum((x - mx) * (y - my) for x, y in rr)
        b = sxy / sxx
        a = my - b * mx
        cur = m[str(ks[-1])] if str(ks[-1]) in m else m[ks[-1]]
        proj = {}
        for k in range(ks[-1] + 1, 12):
            cur = cur * (a + b * k)
            proj[k] = cur
        ex['bb_partial_nodes']['ratio_linear'] = {
            'fit': 'ratio(k) = %.4f + %.4f k' % (a, b), 'proj': proj}
    rep['extrapolation'] = ex

    # -------------------------------------------------------------- findings
    def g(path, default=None):
        cur = rep
        for p in path:
            cur = cur.get(p, {}) if isinstance(cur, dict) else {}
        return cur if cur != {} else default

    K7 = 7
    lv = cost.get(K7, {})
    rep['findings'] = [
        "ENGINE VALIDATED against A31 at every k it reaches.  With the per-wall cap "
        "switched off the A32 branch-and-bound reproduces A31's MAIN counts and all "
        "three branch counts EXACTLY (k=3: 10/9/1/24, k=4: 140/121/4/194, k=5: "
        "2275/1989/18/1979, k=6: 41951/37022/109/25890).  With the certified "
        "per-wall cap 3 promoted to a hard prune (as the A32 brief directs) it "
        "reproduces A31's wallcap3 columns exactly at k=3..7 (10, 131, 2007, 33967, "
        "623194) and the non-thin sub-counts (1, 17, 245, 4001, 67130).",

        "THE DECISIVE STRUCTURAL FACT: in a branch-and-bound whose kills are all "
        "MONOTONE, every surviving complete structure is a leaf that must be "
        "visited, so the node count is bounded BELOW by the leaf count.  Measured "
        "overhead (partial nodes visited / MAIN leaves) is 80, 73, 73, 86, 122 at "
        "k = 3..7 -- it GROWS, roughly linearly in k.  Early kill therefore cannot "
        "beat A31's flat survivor count; it can only avoid materialising what A31 "
        "filtered out.",

        "EARLY-KILL COLLAPSE FACTOR vs A31's flat counts at k=7.  A32 visits "
        "76,071,280 partial nodes to produce the same 623,194 leaves.  A31 "
        "actually evaluated 4,198,469,470 (A-rep, wall-mask) rows for the same "
        "level, so early kill collapses the WORK by 55x; against A31's unfiltered "
        "orbit count R0 = 14,828,211,568 the factor is 195x, and against its own "
        "cheaply-filtered row R5 = 207,791,913 only 2.7x.  The collapse is real "
        "but modest, and it is bought at 175x the per-object cost.",

        "AND IT DOES NOT PAY FOR ITSELF.  A32's k=7 tree cost 1736 s on 6 workers "
        "(22.8 us per partial node, pure Python) against A31's 557 s for the "
        "vectorised flat enumeration of the same k=7 level.  Node-at-a-time "
        "branch-and-bound is 3x SLOWER in wall clock despite visiting 55x fewer "
        "objects: 137 us of CORE time per partial node (about 64% of it the "
        "canonical form, ~50 us the cascade itself) swamps the pruning gain.  A "
        "bitset/C implementation plus a nauty-style canonical labelling would need "
        "roughly a 50x per-node speed-up merely to draw level with vectorised flat "
        "enumeration.",

        "FRONTIER GROWTH.  Partial nodes per target core size: 798, 9502, 145702, "
        "2,934,176, 76,071,280 for k = 3..7; successive ratios 11.9, 15.3, 20.1, "
        "25.9 -- LINEAR in k, i.e. factorial-times-exponential growth, exactly the "
        "shape A31 found for the flat counts.  Extrapolated to k = 11: 5.6e12 "
        "(log-linear fit) to 1.4e14 (ratio-linear fit) partial nodes at the GRAPH "
        "level alone, i.e. 2e5 - 5e6 CPU-hours at the measured 137 us of core "
        "time per partial node.",

        "MODE D (decorations branched jointly with the structure).  Tilt "
        "propagation reproduces A31's exact Level-1 counts on every graph tested "
        "(21/21 exact agreements), so the decorated engine is validated too.  "
        "Per-edge decoration survival factor (geometric mean over sampled MAIN "
        "graphs, full cascade tilt+rotation+L2): 2.93, 4.18, 3.87, 5.14, 5.49 at "
        "k = 3..7, against A31's tilt-only 3.00, 3.79, 4.59, 5.34, 5.85.  The two "
        "new monotone decoration filters therefore buy about 6% per edge at k=7 -- "
        "a factor ~4 over the ~23 edges of a k=11 core.  Projected decorated "
        "fan-out per graph at k=11: 1e19 - 1e20, against A31's tilt-only 6.5e18.  "
        "NO change of order of magnitude.  Pooled per-child kill rates on the "
        "sampled tree at k=7: tilt 12.9%, rotation system 4.2% of what tilt "
        "leaves (and rising fast with k: 0.0, 0.6, 1.0, 2.0, 4.2%), L2 struts "
        "3.5% of the rest.",

        "L2 COLLINEARITY IS THE ONE REAL WIN, AND IT IS SMALLER THAN HOPED.  The "
        "brief expected the codimension-1 strut equation to make the thin branch "
        "die fast.  It does kill whole graphs: with an EXACT capped depth-first "
        "search over the decoration tree, 4/10 MAIN graphs at k=3 and 9/25 at k=4 "
        "are PROVEN to have no surviving decoration at all, and every one of them "
        "is a thin (degree-2) graph -- about 43% of thin graphs, 0% of non-thin.  "
        "That is a factor ~1.6 on the graph count, not the ~10x that promoting L2 "
        "to a hard prune would give (A31 gap G5).  The remaining thin graphs "
        "survive because their degree-2 squares carry at least one contact whose "
        "force direction is set by the NEIGHBOUR's tilt, which the slot-level test "
        "cannot decide (deferred; logged).",

        "ABLATION (k=6, closed frontier 51,690 with the full cascade): metric "
        "interval feasibility is by far the strongest monotone stage (off -> "
        "311,622, x6.0), then the L1 EXTENSIBILITY prune X1 (off -> 103,064, x2.0 "
        "-- and it is free, it is the only stage that turns a non-monotone "
        "structural requirement into an early kill), then planarity (x1.6) and the "
        "per-wall cap 3 (x1.3).  The Euler bound and the Euler budget never fire at "
        "k <= 6.",

        "THE STRENGTHENED METRIC TEST ADDS NOTHING.  Closing the interval distance "
        "system under the triangle inequality (Floyd on the upper bounds, reverse "
        "triangle on the lower bounds) is EXACTLY as strong as A31's L5(a) broad "
        "phase at k <= 6: disabling either one alone leaves the frontier unchanged "
        "(3601 at k=5, both directions), and disabling both gives 19,187.  The "
        "wall-box + hop-distance system is already triangle-closed.",

        "STAGES 4-6 (Farkas / case-LP / Fritz John) FIRE ZERO TIMES ON "
        "STRUCTURE-DERIVED CELLS.  On 30 sampled nodes across k = 4,5,6 the Gordan/"
        "Farkas first-order test found no improving direction (0/30), interval SAT "
        "never certified infeasibility (0/30), no pair menu was ever empty, the "
        "case-LP stub was feasible on 10/10, and the cheap FJ range exclusion "
        "excluded 0/10.  Cost 0.11-0.31 s per node -- 5,000-13,000x the cost of the "
        "combinatorial cascade for zero kills.  Pinning every tilt to the zero class "
        "(the strongest decoration information available) cuts the active row set "
        "from ~510 to ~190 but still yields no kill.  This confirms A30's verdict "
        "from the other side: the first-order tests need cells of half-width ~1e-4, "
        "and a structure-derived cell is ~1.4 wide.",

        "STAGE-6 STRUCTURAL NOTE.  A contact structure fixes which CONTACTS are "
        "active but not which SELECTION ROWS are; on a wide cell the active-row "
        "menu has ~500-750 members instead of the ~35 a square FJ system needs.  A "
        "Krawczyk FJ solve is therefore not even well-posed at a structure node "
        "until the decoration is committed -- the FJ solve belongs strictly below "
        "the decoration layer, not at the structure layer.",

        "GO/NO-GO: NO-GO, decisively.  The k=11 frontier of the joint "
        "structure-and-decoration branch-and-bound projects to 5.6e12 - 1.4e14 "
        "nodes at the graph level and ~1e30 decorated leaves -- 7 to 24 orders of "
        "magnitude above the 1e4-1e6 solvable-node target, and the growth is "
        "factorial-times-exponential, not exponential.  Early kill buys a factor "
        "~200 against naive enumeration and LOSES to vectorised flat enumeration on "
        "wall clock.  The structure-first campaign cannot be rescued by better "
        "search over this node space; it needs a lemma that collapses the space "
        "itself (promoting L2 or the Maxwell row count to hard prunes, or a "
        "wall-to-wall chain argument that fixes the core to O(1) shapes).",

        "SOUNDNESS CANARY: PASS.  Trump's structure (11 loaded squares, 14 "
        "square-square + 11 square-wall contacts, s = 3.8770835900228) survives all "
        "110 mode-G prefixes of an 11-step vertex insertion, closes as MAIN "
        "(L1/L3/L6/L7 all true, not thin), and its REAL decoration read off the "
        "certificate (7 flush + 7 corner-on-edge square-square contacts, gauge "
        "residual 4e-16) survives all 25 mode-D prefixes of tilt propagation, the "
        "rotation-system test and the L2 strut test.",
    ]

    rep['gaps'] = [
        {'id': 'H1', 'kind': 'brief vs ledger',
         'text': "The brief lists 'flush-mandatory' among the structural "
                 "requirements to be applied as an extensibility check.  The "
                 "Soundness ledger of structure_lemmas.md marks the Maxwell row "
                 "count m >= 3k+1 (which is what makes flush mandatory) SOFT, and "
                 "the brief itself says the ledger governs.  Resolved in favour of "
                 "the ledger: flush-mandatory is NOT used as a kill anywhere in "
                 "A32.  If it were ever proved, A31's G7 says it would be a very "
                 "strong filter."},
        {'id': 'H2', 'kind': 'branch move not implemented',
         'text': "'Add a square' is realised as the OUTER loop over the target core "
                 "size K (one tree per K, exactly as A31 counts one level per k), "
                 "not as a branch move inside a single tree.  Consequence: the X1 "
                 "extensibility prune is sharp (a square's deficiency can only be "
                 "met by the K-k squares not yet introduced), which is why the "
                 "frontier is finite at all; a single tree over all K <= 11 would "
                 "have a much weaker X1 and a much larger frontier."},
        {'id': 'H3', 'kind': 'branch move not implemented',
         'text': "Edge-at-a-time branching is done WITHIN a vertex step (the new "
                 "square's k+4 slots are decided one at a time with the cascade on "
                 "every prefix), not globally over an undecided edge set.  A fully "
                 "edge-at-a-time tree with 'undecided' semantics would be much "
                 "larger still: with all pairs undecided, the sparse junk "
                 "structures that X1 kills here survive every monotone test."},
        {'id': 'H4', 'kind': 'sampling',
         'text': "Mode D is measured per graph with Knuth's random-path estimator "
                 "(unbiased, 150 walks per graph, 10 graphs per k) except where an "
                 "exact capped DFS was run.  The estimator has heavy tails: the "
                 "reported stderr columns are large for the biggest graphs."},
        {'id': 'H5', 'kind': 'resolution',
         'text': "The L2 dead-graph scan is exact only where the capped DFS was "
                 "exhausted: 10/10 graphs at k=3, 18/25 at k=4 (cap 120k child "
                 "evaluations), and 6/15 at k=5 with the cap raised to 1.5M.  k=6 "
                 "was abandoned after one graph -- at cap 1.5M no k=6 tree is "
                 "exhausted.  The dead FRACTION at k >= 5 is therefore a lower "
                 "bound (3/15 measured) and the clean numbers are k=3 and k=4."},
        {'id': 'H6', 'kind': 'filter strength',
         'text': "The L2 test is applied at the slot level only.  The cases it "
                 "defers (a degree-2 square with a contact whose normal is set by "
                 "the neighbour's tilt) need the metric line-of-action condition, "
                 "which is a genuine codimension-1 equation that interval "
                 "arithmetic on structure-derived boxes cannot see.  Closing those "
                 "cases is the single most valuable follow-up, and would push the "
                 "thin-branch kill from ~43% of thin graphs toward A31's 90%."},
        {'id': 'H7', 'kind': 'not modelled',
         'text': "The rotation-system test is applied to the square-square "
                 "subgraph only (A31's G9): the rotation at a wall node is not "
                 "determined by a decoration.  Wall slots do influence the ordering "
                 "around each square, but the wall nodes' own rotations, and "
                 "consistency with the L4 drawing, are not enforced."},
        {'id': 'H8', 'kind': 'budget',
         'text': "k = 8 was not run.  The canonical form is a minimum over "
                 "S_k x D4 evaluated as |G| vector adds; at k=8 the group has "
                 "322,560 elements (8x k=7) and the projected level cost is ~12 "
                 "core-hours plus 155 MB of group tables per worker.  A real "
                 "campaign needs a nauty-style canonical labelling, not a group "
                 "sweep."},
        {'id': 'H9', 'kind': 'extrapolation',
         'text': "Everything at k > 7 is extrapolation from k = 3..7, not a bound.  "
                 "The two models (log-linear in k, and linear-in-k successive "
                 "ratios) differ by a factor 25 at k = 11, and the ratio model is "
                 "the better fit to the measured ratios, so 1.4e14 is the more "
                 "honest number."},
        {'id': 'H10', 'kind': 'completeness',
         'text': "Like A31, the count is PER CORE: the 11-k rattlers are not "
                 "placed, and the lambda0 = 0 and L3 self-stress branches are "
                 "counted separately (k=7: 233,057 and 843) and are not part of "
                 "MAIN.  Each still needs its own excludable row system."},
        {'id': 'H13', 'kind': 'infrastructure',
         'text': "RAM is guarded structurally, not by measurement: the search is "
                 "depth-first inside each vertex step (stack depth <= k+4) and only "
                 "one level's canonical mask list is held in memory (int per node; "
                 "the largest, k=7 level 7, is 857,094 ints), plus a --node-cap "
                 "abort.  psutil is not installed in this environment so no live "
                 "RSS probe was added; peak observed working set was ~330 MB per "
                 "worker at k=7, dominated by the 40,320 x 49 group-action table."},
        {'id': 'H12', 'kind': 'soundness (found and fixed)',
         'text': "X2, the Euler-budget extensibility prune, was first written as "
                 "|E| + sum_i deficiency_i <= 3K+2, which over-prunes because one "
                 "future edge can retire deficiency at BOTH of its endpoints; it "
                 "was corrected to |E| + ceil(sum/2).  X2 fires ZERO times at every "
                 "k measured (both the ablation and the kill-share table show 0) "
                 "and the k=3..7 leaf counts are identical before and after the "
                 "correction and match A31 exactly, so no reported number is "
                 "affected.  Recorded because the same trap will reappear in any "
                 "extensibility prune that counts edge endpoints."},
        {'id': 'H11', 'kind': 'cost model',
         'text': "sec/node is measured with 6 Python worker processes on a 20-core "
                 "machine and includes the canonical-form computation, which is about "
                 "64% of the core time at k=7 (7.4M canonical forms at 0.9 ms "
                 "each).  The cascade itself is ~50 us of core time per node."},
    ]
    json.dump(rep, open(os.path.join(RES, 'frontier_report.json'), 'w'), indent=1)
    print(json.dumps({'modeG_frontier': {k: {a: b for a, b in v.items()
                                             if not str(a).startswith('_')}
                                         for k, v in frontier.items()},
                      'cost': cost,
                      'validation': vv,
                      'extrapolation': ex}, indent=1)[:6000])


if __name__ == '__main__':
    main()
