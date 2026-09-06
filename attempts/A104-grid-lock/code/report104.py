"""A104 report: the T1 table, the T2 m_lock table and the contact census of the fully-held packings.

Reads results/t1_close.jsonl, results/t2_endpoints.jsonl, results/t2_mlock.json; writes
notes/lock104.md fragments to stdout and results/a104_summary.json.  No geometry is recomputed except
the cone certificates already stored in the endpoint records.
Usage: python report104.py
"""
from __future__ import annotations

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A104 = os.path.dirname(HERE)
RES = os.path.join(A104, 'results')


def jl(name):
    p = os.path.join(RES, name)
    return [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


def main():
    t1 = jl('t1_close.jsonl')
    t2 = jl('t2_endpoints.jsonl')
    mlock = json.load(open(os.path.join(RES, 't2_mlock.json'), encoding='utf-8'))

    out = {'t1': [], 't2': {}, 'contact_census': {}}

    print('## T1 -- closing the corpus (Lemma ROT step, iterated)\n')
    print('| packing | side | steps | outcome | corner freed | the intruder that leaves | travel |')
    print('|---|---|---|---|---|---|---|')
    for r in t1:
        ex = []
        for rd in r['rounds']:
            for m in rd['moves']:
                if m['why'] == 'exited' or m['exits_cell']:
                    ex.append('%s sq%d d=%.2e %s' % (m['corner'], m['square'],
                                                     m['depth_before'], m['free_by']))
        trav = ['%.2e' % m['travel'] for rd in r['rounds'] for m in rd['moves']
                if m['why'] == 'exited' or m['exits_cell']]
        mc = r['final']['meet_counts']
        freed = [c for c in ('BL', 'BR', 'TR', 'TL') if mc[c] < 2]
        print('| %s | %.9f | %d | %s | %s | %s | %s |'
              % (r['tag'], r['side_orig'], r['n_steps'], r['outcome'], ','.join(freed),
                 '; '.join(ex), ', '.join(trav)))
        out['t1'].append({'tag': r['tag'], 'side': r['side_orig'], 'side_end': r['side_end'],
                          'outcome': r['outcome'], 'n_steps': r['n_steps'],
                          'meet_counts': mc, 'freed': freed, 'exits': ex,
                          'exact': r.get('exact', {}).get('disjoint_certified'),
                          'exact_n_meet': r.get('exact', {}).get('exact_n_meet'),
                          'side_upper_bound': r.get('exact', {}).get('side_upper_bound')})

    print('\n## T2 -- the empirical boundary\n')
    print('| floor | seeds | endpoints | fully held | corner freed | stalled/timeout | '
          'frac held | frac freed | m_lock | lowest endpoint |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for k, v in sorted(mlock['per_floor'].items()):
        print('| %s | %d | %d | %d | %d | %d | %.3f | %.3f | %s | %.7f |'
              % (k, v['n_seeds'], v['n_endpoints'], v['n_fully_held'], v['n_corner_freed'],
                 v['n_stalled'], v['frac_fully_held'] or 0.0, v['frac_corner_freed'] or 0.0,
                 ('%.9f' % v['m_lock']) if v['m_lock'] else '-', v['min_endpoint_side']))
    out['t2'] = mlock['per_floor']
    out['m_lock'] = mlock.get('m_lock')
    out['m_lock_tag'] = mlock.get('m_lock_tag')

    held = [r for r in t2 if r.get('outcome') == 'fully_held' and r.get('certificate')]
    print('\nfully-held packings: %d; sides %s'
          % (len(held), ' '.join('%.6f' % r['side_end'] for r in sorted(held, key=lambda q: q['side_end'])[:12])))

    # contact census over the fully-held packings
    nc, nsq, nw, lam0, ncorner = [], [], [], 0, 0
    per_depth = []
    for r in held:
        for it in r['certificate']['intruders']:
            nc.append(it['n_contacts']); nsq.append(it['n_sq_contacts']); nw.append(it['n_wall_contacts'])
            per_depth.append(it['depth'])
            ncorner += 1
            b = it['branches'][0]['cert']
            if b is not None and b['lam_total'] <= 1e-9:
                lam0 += 1
    if nc:
        print('\ncontact census over %d intruders of %d fully-held packings:' % (len(nc), len(held)))
        print('  contacts per intruder: min %d median %d mean %.2f max %d'
              % (min(nc), int(statistics.median(nc)), sum(nc) / len(nc), max(nc)))
        print('  square-square %d (%.1f%%), wall %d (%.1f%%)'
              % (sum(nsq), 100.0 * sum(nsq) / sum(nc), sum(nw), 100.0 * sum(nw) / sum(nc)))
        print('  square-square per intruder: mean %.2f;  wall per intruder: mean %.2f'
              % (sum(nsq) / len(nsq), sum(nw) / len(nw)))
        print('  Gordan certificate with lambda = 0 (wedged by contacts alone): %d / %d'
              % (lam0, ncorner))
        print('  intruder depth: min %.3e median %.3e max %.3e'
              % (min(per_depth), statistics.median(per_depth), max(per_depth)))
        out['contact_census'] = {
            'n_packings': len(held), 'n_intruders': len(nc),
            'contacts_min': min(nc), 'contacts_median': statistics.median(nc),
            'contacts_mean': sum(nc) / len(nc), 'contacts_max': max(nc),
            'n_square_square': sum(nsq), 'n_wall': sum(nw),
            'frac_square_square': sum(nsq) / sum(nc),
            'mean_sq_per_intruder': sum(nsq) / len(nsq),
            'mean_wall_per_intruder': sum(nw) / len(nw),
            'lambda_zero': lam0, 'depth_min': min(per_depth),
            'depth_median': statistics.median(per_depth), 'depth_max': max(per_depth)}
    # outcome census (the closing dichotomy, all outcomes)
    import collections
    cens = collections.Counter((r['delta'], r.get('outcome')) for r in t2)
    print('\noutcome census (delta, outcome):')
    for k in sorted(cens, key=lambda t: (t[0], str(t[1]))):
        print('  %.0e %-20s %d' % (k[0], k[1], cens[k]))
    out['outcome_census'] = {'%.0e|%s' % k: v for k, v in cens.items()}

    # the fully GORDAN-CERTIFIED subset (every intruder, every branch)
    certd = [r for r in held if all(it['all_branches_certified']
                                    for it in r['certificate']['intruders'])]
    print('\nfully held: %d;  of which every intruder carries a Gordan certificate on every '
          'branch: %d' % (len(held), len(certd)))
    out['n_fully_held'] = len(held)
    out['n_fully_certified'] = len(certd)
    if certd:
        bc = min(certd, key=lambda q: q['side_end'])
        out['m_lock_certified'] = bc['side_end']
        out['m_lock_certified_tag'] = bc['tag']
        out['m_lock_certified_record'] = {
            'tag': bc['tag'], 'side': bc['side_end'], 'delta': bc['delta'],
            'poses': bc.get('poses'), 'contact_graph': bc['certificate']['contact_graph'],
            'exact': bc['certificate']['exact'],
            'intruders': bc['certificate']['intruders']}
        print('m_lock (Gordan-certified) = %.12f  [%s, floor %.0e]'
              % (bc['side_end'], bc['tag'], bc['delta']))
        for d in sorted({r['delta'] for r in held}):
            h = [r for r in held if r['delta'] == d]
            c = [r for r in certd if r['delta'] == d]
            print('  floor %.0e: held %d (min %.9f); certified %d (min %s)'
                  % (d, len(h), min(x['side_end'] for x in h), len(c),
                     ('%.9f' % min(x['side_end'] for x in c)) if c else '-'))

    # the record holder
    best = min(held, key=lambda q: q['side_end']) if held else None
    if best is not None:
        c = best['certificate']
        print('\nm_lock packing %s at side %.12f' % (best['tag'], best['side_end']))
        print('  exact: %s' % json.dumps({k: c['exact'][k] for k in
                                          ('side_upper_bound', 'min_pair_gap_lower_bound',
                                           'disjoint_certified', 'exact_n_meet', 'exact_unknown',
                                           'K0_BLOCKED_certified')}))
        print('  contact graph: %d square-square edges, %d wall contacts'
              % (c['contact_graph']['n_square_edges'], c['contact_graph']['n_wall_contacts']))
        for it in c['intruders']:
            b = it['branches'][0]['cert']
            print('   %s sq%-2d d=%.4e tilt %.4f  contacts %d (sq %d / wall %d)  '
                  'lambda_tot %.4f  resid %.1e  branches ok %s'
                  % (it['corner'], it['square'], it['depth'], it['tilt_deg'], it['n_contacts'],
                     it['n_sq_contacts'], it['n_wall_contacts'],
                     b['lam_total'] if b else float('nan'), b['residual'] if b else float('nan'),
                     it['all_branches_certified']))
        out['m_lock_record'] = {'tag': best['tag'], 'side': best['side_end'],
                                'poses': best.get('poses'),
                                'contact_graph': c['contact_graph'],
                                'exact': c['exact'],
                                'intruders': [{k: it[k] for k in
                                               ('corner', 'square', 'depth', 'tilt_deg',
                                                'n_contacts', 'n_sq_contacts', 'n_wall_contacts',
                                                'contacts', 'contact_rows', 'virtual_rows',
                                                'branches', 'all_branches_certified')}
                                              for it in c['intruders']]}
    json.dump(out, open(os.path.join(RES, 'a104_summary.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/a104_summary.json')


if __name__ == '__main__':
    main()
