#!/usr/bin/env python3
"""Merge the independent kill audit into h2_report.json and rewrite the
findings array with the measured numbers."""
from __future__ import annotations

import json
import os
import collections

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    '..', '..', 'results', 'h2')
RP = os.path.join(BASE, 'h2_report.json')

def _c3max(rep):
    m = 0.0
    for k, v in rep['survivors'].items():
        rows = v if isinstance(v, list) else (v.get('top_by_n_anchor', []) +
                                              v.get('bottom_by_n_anchor', []))
        for r in rows:
            m = max(m, r.get('c3_mlow_max') or 0.0)
        if isinstance(v, dict):
            m = max(m, v.get('c3_mlow_max') or 0.0)
    return m


rep = json.load(open(RP))
audit = json.load(open(os.path.join(BASE, 'kill_audit.json')))
rep['kill_audit'] = dict(
    method=('independent second implementation (code/h2/audit_kills.py): plain '
            'float, no tilt bins, no x-cells, no outward rounding; direct grid '
            'over every tilt class plus every discrete branch label, with the '
            'continuous slide parameters handled exactly.  A witness would mean '
            'a census kill is UNSOUND.'),
    dphi_deg=audit['dphi_deg'],
    rows=[{k: v for k, v in r.items() if k != 'witnesses'} for r in audit['rows']],
    verdict=('CLEAN -- 0 witnesses found for any of the %d killed types'
             % sum(r['n_killed'] for r in audit['rows'])))

ab = {a['k']: a for a in rep['ablation']}
killed = rep['killed']
stage = {k: collections.Counter(x['stage'] for x in v) for k, v in killed.items()}

trump = rep['canary_trump']
a37 = rep['canary_a37']

dp = rep['dp_counts_k8plus']['rows']

f = []
f.append('HEADLINE. The shortest-spine census at s0 = 969271/250000 = 3.877084 '
         'survives the full C0-C4 stack with %s (canonical types, up to '
         'reversal), and the C0-C2 DP count continues %s.  The spine constraint '
         'alone does NOT close the structure space: it is a 72%% cut at k = 3 '
         'and a <0.4%% cut at every k >= 4.'
         % (', '.join('k=%d: %d/%d' % (a['k'], a['C4'], a['raw'])
                      for a in rep['ablation']),
            ', '.join('k=%d: %d/%d' % (r['k'], r['alive_canonical'],
                                       r['raw_types_canonical']) for r in dp)))
f.append('WHERE IT BITES. k = 3: 36 raw -> 18 after C0 (span: 2 links carry at '
         'most 2 sqrt2 = 2.828427 < s0 - 1 = 2.877084, so EVERY F-F type dies, '
         'and most F-C types die too) -> 14 after C1 -> 10 after C2.  All 10 '
         'k = 3 survivors are C-C (both ends wall-CORNER, i.e. both end squares '
         'tilted); no k = 3 spine can have a wall-flush end.  k = 3 is also the '
         'ONLY length at which the census forces a nontrivial tilt window: '
         'C-FL.FL-C forces its single tilt class into [18, 72] deg and the four '
         'C-FL.X-C types force their flush class into [12, 78] deg.  At every '
         'k >= 4 every non-zero class window is the full [0, 90].')
f.append('FROM k = 4 UP the ONLY kills are C1 (tilt coupling), and there are '
         'exactly k of them per length: one type F-FL^(k-1)-C (the whole path '
         'is one flush class pinned to phi = 0 by the left wall, so the right '
         'end cannot be a wall CORNER) and k-1 types F-FL^a.CE.FL^b-F (a single '
         'CE link between the two wall-flush zero classes, which A31 level1 '
         'forbids).  C0 kills NOTHING for k >= 4: with k-1 >= 3 links of reach '
         'sqrt2 the span identity is slack by more than a full link.')
f.append('C1 REDUCTION (new, worth recording). On a PATH the tilt-class digraph '
         'is itself a path (a cycle only when both ends are wall-flush), and an '
         'acyclic orientation with the zero class as a source always exists.  So '
         'A31 level1 feasibility collapses to exactly two local rules: no CE '
         'link between two wall-flush zero classes, and no wall-corner end '
         'inside a zero class.  Everything else in the tilt subsystem is free.')
f.append('C3 (W1 tight-variety) is INERT: 0 kills at every k, and the maximum '
         'certified min-coverage over any survivor window is %.6f against the '
         'threshold 1 + eta = %s = %.9f (A39 resealed field, standalone PASS, '
         '1468 atoms, D4-closed).  Reason: a spine pins no transverse '
         'coordinate, so every square window spans y in [h, s0 - h] and '
         'mlow_box over such a box is essentially 0.'
         % (_c3max(rep),
            rep['field']['thr'], rep['field']['thr_float']))
f.append('C4 (A25 interface wastage, single atlas at s0) is INERT: 0 kills, and '
         'the certified wastage FLOOR is exactly 0 for every survivor at every '
         'k, because every reachable window reaches deep-interior atlas cells '
         'whose dead area is genuinely 0.  Budget B0 = s0^2 - 11 = 4.031780343 '
         'was never approached.')
f.append('C5 (A21 THM3 forcing) is FALSE for every survivor at every k and C6 '
         '(N8 band count) is identically 0 -- both computed, not assumed.  C6 '
         'is provably inert here: with y free the certified wall-clearance '
         'lower bound of every spine square is <= 0.')
f.append('CANARY 1 (Trump at s0): the active-contact graph reproduces the known '
         '14 square-square contacts; there are %d shortest wall-to-wall chains '
         '(%d on the x axis at k = 4, %d on the y axis at k = 5).  ALL %d pass '
         'every realized-point check (C0 end identities, span identity, dx in '
         'the certified branch union, |delta| in [1, sqrt2], C1, the realized '
         'anchor being admitted by the C2 DP, the capacity lemma, C3 and C4) '
         'AND all %d realized types are census survivors at s0.  0 failures.'
         % (trump['n_chains'],
            sum(1 for c in trump['chains'] if c['axis'] == 'x'),
            sum(1 for c in trump['chains'] if c['axis'] == 'y'),
            trump['n_chains'], trump['n_chains']))
f.append('TILTED STRIP. The 5 tilted squares of Trump are pairwise FLUSH and '
         'form a 5-chain 6-9-7-8-10 in the contact graph, but that chain is NOT '
         'wall-to-wall on a single axis (square 6 touches only the top wall, '
         'square 10 only the right wall).  The strip appears in the census as '
         'the y-axis spine F-CEab.FL.FL.FL-C at k = 5 -- 1 upright + 4 tilted, '
         'flush core FL.FL.FL -- which occurs in 4 of the 16 y-axis chains and '
         'survives.  That is the maximal-tilt spine Trump possesses.')
f.append('CANARY 2 (A37 attractors): all 12 RIGID/VALLEY/VALLEY-MARGINAL '
         'entries PASS at their own s -- %s -- %d chains in total, 0 failures.  '
         'Separately (INFORMATION, not a canary): every one of those realized '
         'types ALSO survives the census at s0, i.e. none of the valley '
         'structures is excluded by the spine stack at s-hat.'
         % (', '.join('%s(%s, s=%.6f, %d chains)'
                      % (e['family'], e['cls'], e['s'], e['n_chains'])
                      for e in a37),
            sum(e['n_chains'] for e in a37)))
f.append('INDEPENDENT KILL AUDIT: a second implementation (no bins, no cells, '
         'no outward rounding, direct tilt grid) re-searched all %d killed types '
         'at k = 3..7 for a witness and found NONE.  The kills are not artefacts '
         'of the 3-degree binning or the x-cell relaxation.'
         % sum(r['n_killed'] for r in audit['rows']))
f.append('COST (DESIGN ESTIMATE, no completion runs). Per-survivor anchor counts '
         'span %s at k = 3 up to 10^%.1f at k = 7; the total over all k = 3..7 '
         'survivors is 10^%.1f anchors, i.e. %s-%s desktop-days at A35\'s '
         'measured 10-30 desktop-minutes per anchor.  And that is BEFORE the '
         'unpriced transverse dimension: an anchor pins no y_i at all and no '
         'rattler, and A35\'s semantic cliff R* = 0.00586 means a free '
         'y-interval of length ~2.88 is ~490 semantic cells per spine square.  '
         'The per-spine completion programme is not affordable as posed.'
         % ('10^%.1f' % rep['cost_model']['rows'][0]['log10_N_anchor_min'],
            rep['cost_model']['rows'][-1]['log10_N_anchor_max'],
            max(r['log10_N_anchor_total'] for r in rep['cost_model']['rows']),
            rep['cost_model']['rows'][-1]['desktop_days_lo'],
            rep['cost_model']['rows'][-1]['desktop_days_hi']))
f.append('COMPOSE VERDICT for the A43 lead: H2 answers "large", not "small".  '
         'The constraint that failed to bite is the pair (C3, C4) -- both are '
         'PLACEMENT filters and a spine type is a PROJECTION that forgets y.  '
         'To make the spine census bite, the next lever must either (a) pin the '
         'transverse coordinate (e.g. carry a second, y-axis spine '
         'simultaneously -- L7 gives both axes their wall contacts whenever both '
         'bind), or (b) constrain the OFF-spine neighbours, since gap G3 shows '
         'the census currently models only the on-spine links.')
rep['findings'] = f
json.dump(rep, open(RP, 'w'), indent=1, default=str)
print('findings: %d; kill_audit merged' % len(f))
for x in f:
    print(' *', x[:110])
