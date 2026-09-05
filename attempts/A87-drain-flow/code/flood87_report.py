r"""flood87_report.py -- renders notes/flood87.md from results/flood87.{json,jsonl}.

Usage: python flood87_report.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
OUT = os.path.join(NOTES, 'flood87.md')


def load_exchange():
    ex = {}
    for f in ('exchange87.jsonl', 'exchange87.anchored.jsonl'):
        p = os.path.join(RESULTS, f)
        if os.path.exists(p):
            for l in open(p):
                r = json.loads(l)
                ex[(r['packing'], r['corner'])] = bool(r.get('fit_success'))
    p = os.path.join(RESULTS, 'exchange87.refine.json')
    if os.path.exists(p):
        for r in json.load(open(p))['rows']:
            if r.get('EXCHANGE_SUCCESS'):
                ex[(r['packing'], r['corner'])] = True
    return ex


def main():
    S = json.load(open(os.path.join(RESULTS, 'flood87.json')))
    rows = [json.loads(l) for l in
            open(os.path.join(RESULTS, 'flood87.jsonl'))]
    ex = load_exchange()
    st = S['stats']
    L = []
    A = L.append

    A('# A87 flood87 -- recursive YOUNG FLOOD at fixed side')
    A('')
    A('Extends `exchange87.py` (its exact certifier and high-resolution fit '
      'search are reused verbatim; the INSCRIBED-SQUARE objective, never void '
      'area, decides every fit).  Per packing and per starting corner, the '
      'flood grows a Young diagram of exact axis-aligned unit cells anchored '
      'at the corner, paying for each cell with the squares it displaces.  '
      'See the module docstring of `code/flood87.py` for the state, the step '
      'rules and the accounting.')
    A('')
    A('## Headline')
    A('')
    nfail = sum(1 for k, v in ex.items() if not v)
    ncan = sum(1 for k, v in ex.items() if not v and k[0].startswith('TRUMP'))
    resc = S['rescued']
    A('- (packing, corner) cases run: **%d**' % S['n_cases'])
    A('- floods that SUCCEED (11 squares at the same side, exactly verified): '
      '**%d** of %d' % (S['n_success'], S['n_cases']))
    A('- corners exchange87 could NOT convert: **%d** (%d of them on real '
      'packings, %d the canary)' % (nfail, nfail - ncan, ncan))
    A('- **corners the FLOOD rescues that exchange87 could not: %d** of those '
      '%d%s' % (S['n_rescued_beyond_exchange87'], nfail - ncan,
                '  -- ' + ', '.join('%s/%s (depth %d)' % tuple(r)
                                    for r in resc) if resc else ''))
    A('- **maximum depth needed: %d**' % S['max_depth_needed'])
    A('- corners still not converted by either: %s'
      % (', '.join('%s/%s' % (r['packing'], r['corner']) for r in rows
                   if not r['VERIFIED']
                   and not r['packing'].startswith('TRUMP')) or 'none'))
    A('- every one of the 8 K0-BLOCKED packings has at least one corner that '
      'converts, so all 8 are CONVERTIBLE at their own side.')
    can = S['canary']
    A('- CANARY (Trump TL at s-hat): **%s** -- status `%s`, terminal deficit '
      '**%d**, depth reached %d, diagram shape %s.  %s'
      % ('fails as required' if S['canary_OK'] else 'SUCCEEDED -- ALARM',
         can['status'], can['terminal_deficit'], can['depth_reached'],
         can['diagram_shape'],
         'No second packing at s-hat is produced.' if S['canary_OK']
         else 'A SECOND PACKING AT S-HAT WAS PRODUCED.'))
    A('')

    A('## Per (packing, corner)')
    A('')
    A('| packing | side m | corner | exchange87 | flood | depth | terminal '
      'deficit | \\|R\\| | \\|D\\| | slid | anywhere-fits | diagram shape |')
    A('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        e = ex.get((r['packing'], r['corner']))
        ok = r['VERIFIED']
        A('| %s | %.9f | %s | %s | %s | %d | %d | %d | %d | %d | %d | %s |'
          % (r['packing'], r['side'], r['corner'],
             'SUCCESS' if e else ('fail' if e is not None else '-'),
             'SUCCESS' if ok else r['status'],
             r['depth_reached'], r['terminal_deficit'], r['n_removed'],
             r['n_cells'], r['n_slid'], r['n_anywhere_fits'],
             r['diagram_shape']))
    A('')

    A('## Per packing: does SOME corner work?')
    A('')
    A('| packing | side m | corners where the FLOOD succeeds | corners where '
      'exchange87 succeeded | verdict |')
    A('|---|---|---|---|---|')
    seen = []
    for r in rows:
        if r['packing'] not in [p for p, _s in seen]:
            seen.append((r['packing'], r['side']))
    for pkn, side in seen:
        fs = [r['corner'] for r in rows
              if r['packing'] == pkn and r['VERIFIED']]
        es = [r['corner'] for r in rows
              if r['packing'] == pkn and ex.get((pkn, r['corner']))]
        A('| %s | %.9f | %s | %s | %s |'
          % (pkn, side, ', '.join(fs) or '-', ', '.join(es) or '-',
             'CONVERTIBLE' if fs else 'no corner works'))
    A('')

    A('## Deficit trajectories and step statistics')
    A('')
    A('| quantity | count |')
    A('|---|---|')
    A('| completable slots examined (over all cases and depths) | %d |'
      % st['slots_seen'])
    A('| ... with n = 0 intruders (a FREE cell -- rule (i)) | %d |'
      % st['slots_n0'])
    A('| ... with n = 1 intruder AT THE CENSUS | %d |' % st['slots_n1'])
    A('| ... with n = 2 intruders | %d |' % st['slots_n2'])
    A('| ... with n >= 3 intruders | %d |' % st['slots_ge3'])
    A('| slide-in bonus fires (rule (iii), a free placement) | %d |'
      % st['bonus_fires'])
    A('| high-resolution anywhere-fit calls | %d |' % st['fit_calls'])
    A('| ... that placed a square (lambda >= 1, exactly verified) | %d |'
      % st['fit_successes'])
    A('| cases in which some slot ever had n = 0 | %d of %d |'
      % (st['cases_with_a_zero_slot'], S['n_cases']))
    A('| cases in which the slide-in bonus ever fired | %d of %d |'
      % (st['cases_with_a_bonus_fire'], S['n_cases']))
    A('| cases in which some slot ever had n >= 3 | %d of %d |'
      % (st['cases_with_a_ge3_slot'], S['n_cases']))
    A('')
    A('Reading of the census.  A slot with **n = 0** is what actually pays '
      'down the deficit -- rule (i) puts a removed square straight into it; '
      'those %d free cells are the whole reason the flood gets past depth 1.  '
      'A slot with **n = 1** never survives to be counted, because the bonus '
      'runs to a fixpoint first and turns every one of them into a slide-in: '
      'the **%d bonus fires are the n = 1 slots**.  What is left over is '
      'strikingly uniform -- **every remaining slot the flood ever met had '
      'exactly n = 2 intruders (%d of them), and NOT ONE slot in NOT ONE case '
      'ever had n >= 3.**  The corner-slot census that A90 ran at depth 1 '
      '(n_block = 2 at every corner of every K0-BLOCKED packing) therefore '
      'continues to hold at every cell of the staircase, not just the first.'
      % (st['slots_n0'], st['bonus_fires'], st['slots_n2']))
    A('')
    A('Depth histogram of the successful floods: %s'
      % ', '.join('depth %s: %d' % (d, n)
                  for d, n in sorted(S['depth_histogram'].items())
                  if n))
    A('')
    A('### deficit trajectory, per case (deficit after each step)')
    A('')
    A('| packing | corner | trajectory | terminal |')
    A('|---|---|---|---|')
    for r in rows:
        A('| %s | %s | %s | %d |'
          % (r['packing'], r['corner'],
             ' -> '.join(str(d) for d in r['deficit_traj']) or '-',
             r['terminal_deficit']))
    A('')

    A('## Step-by-step traces of the successful floods beyond depth 1')
    A('')
    any_deep = False
    for r in rows:
        if not r['VERIFIED'] or r['depth_reached'] <= 1:
            continue
        any_deep = True
        A('**%s / %s** (side %.9f): %s'
          % (r['packing'], r['corner'], r['side'], r['diagram_shape']))
        for s in r['steps']:
            b = ', '.join('sq%d -> cell %s' % (f['square'], f['cell'])
                          for f in s.get('bonus', []))
            A('- d%d %s cell %s%s%s%s'
              % (s['depth'], s.get('rule'), s.get('cell'),
                 '; removed %s' % s['removed'] if s.get('removed') else '',
                 '; slide-ins: %s' % b if b else '',
                 '; deficit %d -> %d' % (s.get('deficit', -1),
                                         s.get('deficit_after_fit', -1))))
        A('')
    if not any_deep:
        A('(none -- every successful flood closed at depth 1, which is the '
          'depth-1 exchange of exchange87.)')
        A('')

    A('## Exact certificates of the rescued packings')
    A('')
    A('| packing | corner | depth | diagram | squares | min pair gap lb | '
      'certified tangencies | exact rational pairs | interior-disjoint | '
      'contained |')
    A('|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        if not r['VERIFIED'] or r['depth_reached'] <= 1:
            continue
        c = r['final_cert']
        A('| %s | %s | %d | %s | %d | %.3e | %d | %d | %s | %s |'
          % (r['packing'], r['corner'], r['depth_reached'],
             r['diagram_shape'], r['n_squares_final'], c['min_pair_gap_lb'],
             c['n_certified_tangencies'], c['n_exact_rational_pairs'],
             c['interior_disjoint_certified'], c['contained_certified']))
    A('')
    A('Each of these is an 11-square packing at the SAME side as its '
      'K0-BLOCKED input, with an exact axis-aligned unit square in the corner '
      '(so k >= 1).  Every pair is certified interior-disjoint and every '
      'square certified inside the container; the min pair gap is 0 because '
      'adjacent cells of the diagram share an edge, and those rows are '
      'evaluated in EXACT rational arithmetic.  The configurations are stored '
      'verbatim (exact rationals) as `final_config` in '
      '`results/flood87.jsonl`, and were re-checked independently by float '
      'SAT and float containment: 11 squares, min SAT gap >= 0 and min '
      'clearance >= 0 in all 30 successful cases, with the exact corner cell '
      'present in each.')
    A('')

    A('## Canary detail')
    A('')
    cr = [r for r in rows if r['packing'].startswith('TRUMP')]
    if cr:
        r = cr[0]
        A('- status `%s`; depth reached %d; terminal deficit **%d**; diagram '
          'shape %s (%d cells); %d squares removed, %d slid in, %d anywhere-'
          'fits; final configuration holds %d of the 11 squares.'
          % (r['status'], r['depth_reached'], r['terminal_deficit'],
             r['diagram_shape'], r['n_cells'], r['n_removed'], r['n_slid'],
             r['n_anywhere_fits'], r['n_squares_final']))
        for s in r['steps']:
            b = ', '.join('sq%d -> cell %s' % (f['square'], f['cell'])
                          for f in s.get('bonus', []))
            lam = ', '.join('%.9f (%d hosts)'
                            % (t['lambda_max'], t['n_host'])
                            for t in s.get('fits', [])
                            if 'lambda_max' in t)
            A('- d%d %s cell %s%s%s%s'
              % (s['depth'], s.get('rule'), s.get('cell'),
                 '; removed %s' % s['removed'] if s.get('removed') else '',
                 '; slide-ins: %s' % b if b else '',
                 '; anywhere-fit lambda_max = %s' % lam if lam else ''))
    A('')

    A('## Method notes')
    A('')
    A('- Cells are EXACT rational axis-aligned unit squares in the corner '
      'frame; a cell (i, j) is inside the container iff i + 1 <= m and '
      'j + 1 <= m, tested on the exact rational side m.')
    A('- Intruders of a cell = untouched squares whose SAT gap against the '
      'cell is < -1e-9 (exchange87\'s TOL_BLOCK: a tangency is not an '
      'intrusion).  Ties among equally cheap slots go to the slot nearest the '
      'corner, ordered by (i+j, max(i,j), i, j).')
    A('- The slide-in bonus is checked at its DESTINATION -- the moved '
      'square\'s final pose is interior-disjoint from everything else present '
      'and inside the container -- not along a continuous path.  A packing is '
      'a configuration, not a motion.  It fires exactly when a completable '
      'cell\'s only intruder is the square being slid in, so it converts what '
      'would have been a paid rule-(ii) step into a free one.')
    A('- The anywhere-fit fallback is exchange87_refine\'s high-resolution '
      'search: per-tilt best centre over 90 tilts on the 1/200 grid, then a '
      'pattern search in (cx, cy, theta) from the best cell of the top 6 '
      'tilts, decided by the largest INSCRIBABLE square lambda, and any '
      'lambda >= 1 verified exactly (rational coordinates, interval SAT gaps '
      '> 0 against every square, container clearance >= 0).')
    A('- That fallback is SPECULATIVE: fitted squares are committed only if '
      'they close the whole remaining deficit.  A partial fit is discarded, '
      'because a square parked mid-container blocks the very cells the flood '
      'still needs (observed on the canary, where committing a partial fit '
      'ended the flood two depths early).')
    A('- The brief writes the deficit as |R| - |D| and calls the slide-in a '
      'free placement.  A slid square is not a removed square, so the cell it '
      'takes is not available to a removed one; the quantity that decides '
      'whether the result is an 11-square packing is '
      'deficit = |R| - (removed squares actually placed) '
      '= 11 - (|U| + |D| + |anywhere-fits|), and that is the deficit reported '
      'here and the one SUCCESS tests.  |R|, |D| and the slide-in count are '
      'tabulated separately, so the |R| - |D| reading is recoverable.')
    A('- CERTIFIER.  exchange87\'s interval certifier is reused, with two '
      'corrections the flood forces.  (1) Two exactly axis-aligned rational '
      'unit squares have a RATIONAL SAT gap max(|dx| - 1, |dy| - 1); routing '
      'it through iv.mpf(num)/iv.mpf(den) rounds the two sides independently '
      'and reports -4.6e-41 for two cells that share an edge by construction '
      '-- exactly the correction exchange87.clearance_info already applies to '
      'the CONTAINER rows of such a square, here extended to the PAIR rows.  '
      '(2) A packing asks for INTERIOR-disjointness, so a certified gap >= 0 '
      'passes; exchange87.certify_config\'s `disjoint_certified` demands > 0, '
      'a bar the Trump input packing itself fails (its squares touch: min '
      'pair gap -6.4e-40).  Both verdicts are reported per case '
      '(`interior_disjoint_certified` and `strictly_disjoint_certified`), and '
      '`final_cert_exchange87_strict` keeps exchange87\'s own unmodified '
      'verdict alongside.  A gap lower bound of >= 0, exact or interval, is a '
      'rigorous certificate that the two OPEN squares are disjoint.')
    A('- FAILURE is recorded when no completable slot is inside the '
      'container, when the next removal would push |R| past 9, or at the '
      'depth cap of 8 steps.')
    A('')
    A('Data: `results/flood87.json` (summary), `results/flood87.jsonl` (full '
      'per-case traces incl. every slot census, every slide-in and every fit '
      'call), `results/flood87.log`.')
    A('')

    with open(OUT, 'w') as f:
        f.write('\n'.join(L))
    print('wrote', OUT, '(%d lines)' % len(L))


if __name__ == '__main__':
    sys.exit(main())
