"""Tabulate results/t3_exits.jsonl (A90 T3 task 1)."""
import json
import os
import collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, '..', 'results')

rows = [json.loads(l) for l in open(os.path.join(R, 't3_exits.jsonl')) if l.strip()]
B = [b for r in rows for b in r['blockers']]
TAG = {id(b): r['tag'] for r in rows for b in r['blockers']}
print('exit events           : %d' % len(rows))
print('reproduce stored      : %d  (|d sigma_exit| < 1e-9 and same corner)'
      % sum(1 for r in rows if r['reproduces_stored']))
print('sliding blockers      : %d' % len(B))
print('events with 1 blocker : %d' % sum(1 for r in rows if len(r['blockers']) == 1))
print('corners freed         : %s' % dict(collections.Counter(
    c for r in rows for c in r['corners_freed'])))
print('modes                 : %s' % dict(collections.Counter(r['mode'] for r in rows)))
print()
n = len(B)


def frac(p, lbl):
    k = sum(1 for b in B if p(b))
    print('%-44s %4d/%d  %.4f' % (lbl, k, n, k / n))


frac(lambda b: b['non_deepest'], 'non-deepest at its corner')
frac(lambda b: b['RETREATABLE'], 'RETREATABLE (cardinal translation test)')
frac(lambda b: b['diag_free'], 'C_(1,1) free (diagonal retreat)')
frac(lambda b: b['RETREATABLE'] or b['diag_free'], 'retreatable by SOME e in K')
frac(lambda b: not b['LOCKED'], 'NOT flush-locked (Lemma LOCK (b) LP)')
frac(lambda b: b['n_contacts'] == 0, 'rattler (0 active contacts)')
frac(lambda b: b['menu']['applies'], 'MENU applies (tilted + wall contact)')
frac(lambda b: b['menu'].get('MENU_LOCKED') is True, 'MENU-LOCKED')
frac(lambda b: b['menu']['applies'] and not b['menu'].get('MENU_LOCKED'),
     'MENU-UNLOCKED (menu applies, no far side)')
frac(lambda b: b['K']['e_x'] and b['K']['e_y'], 'both cardinals in K')
frac(lambda b: not b['K']['e_x'] and not b['K']['e_y'], 'no cardinal in K')
frac(lambda b: b['K']['(1,1)'], '(1,1) in K')
print()
q = np.quantile([b['depth'] for b in B], [0, .5, 1])
print('depth of the sliding blocker at x_ok  : min %.3e median %.3e max %.3e' % tuple(q))
print('MENU reason breakdown                 : %s' % dict(collections.Counter(
    b['menu'].get('reason', 'applies') for b in B)))
print('n active contacts histogram           : %s' % dict(sorted(
    collections.Counter(b['n_contacts'] for b in B).items())))
print()
print('CARDINAL cluster size histogram (one entry per (blocker, cardinal e in K)):')
h = collections.Counter()
for b in B:
    for lbl in b['cardinals']:
        h[b['clusters'][lbl]['size']] += 1
for k in sorted(h):
    print('  size %2d : %4d' % (k, h[k]))
tot = sum(h.values())
print('  total %d cardinal clusters' % tot)
print('  wall-anchored     : %d' % sum(1 for b in B for lb in b['cardinals']
                                       if b['clusters'][lb]['wall_anchored']))
print('  intruder-anchored : %d' % sum(1 for b in B for lb in b['cardinals']
                                       if b['clusters'][lb]['intruder_anchored']))
print('  free (neither)    : %d' % sum(1 for b in B for lb in b['cardinals']
                                       if b['clusters'][lb]['free']))
print('DIAGONAL cluster size histogram: %s' % dict(sorted(
    collections.Counter(b['clusters']['(1,1)']['size'] for b in B).items())))
print()
mot = [b['motion'] for b in B if 'motion' in b]
print('exit motion (x_ok -> x_bad, the two bisection endpoints):')
print('  Q is the SOLE moving square         : %d/%d' % (
    sum(1 for m in mot if m['Q_is_sole_mover']), len(mot)))
print('  n squares moving histogram          : %s' % dict(sorted(
    collections.Counter(m['n_squares_moving'] for m in mot).items())))
print('  Q rotation exceeds Q translation    : %d/%d' % (
    sum(1 for m in mot if m['rotation_dominates_Q']), len(mot)))
print('  Q carries the largest displacement  : %d/%d' % (
    sum(1 for m in mot if m['Q_dc'] >= m['dc_max_other']), len(mot)))
print()
bad = [b for b in B if not b['RETREATABLE']]
print('=' * 78)
print('NOT RETREATABLE by the cardinal translation test, yet the flow exited: %d'
      % len(bad))
print('=' * 78)
for b in bad:
    print('--- %s  sq%d at %s   depth %.3e  tilt %.3e rad  contacts %d  '
          'LOCKED %s  MENU %s  C_(1,1) free %s'
          % (TAG[id(b)], b['sq'], b['corner'], b['depth'], b['tilt'],
             b['n_contacts'], b['LOCKED'],
             b['menu'].get('MENU_LOCKED', b['menu'].get('reason')),
             b['diag_free']))
    print('    K: %s   cardinals %s   kept at corner %s   n_intruders %d'
          % (b['K'], b['cardinals'], b['kept_at_corner'],
             b['n_intruders_at_corner']))
    for lbl in b['cardinals']:
        cl = b['clusters'][lbl]
        print('    C_%s e_world %s size %d members %s' % (
            lbl, cl['e_world'], cl['size'], cl['members']))
        print('        wall_anchored %s %s' % (cl['wall_anchored'], cl['wall_hits']))
        print('        intruder_anchored %s %s' % (
            cl['intruder_anchored'],
            [(h['sq'], h['corner'], round(h['depth'], 6), round(h['rate'], 6),
              round(h['fd'], 6)) for h in cl['intruder_hits']]))
        print('        blocking contacts of Q for this e: %s'
              % [(s['kind'], s['other'], round(s['ndote'], 6))
                 for s in cl['sides'] if s['blocking']])
        print('        corner-side contacts of Q:         %s'
              % [(s['kind'], s['other'], round(s['ndote'], 6))
                 for s in cl['sides'] if not s['blocking']])
        print('        cluster growth edges (member -> outsider): %s' % cl['edges'])
    cd = b['clusters']['(1,1)']
    print('    C_(1,1) size %d members %s wall %s intruder %s free %s'
          % (cd['size'], cd['members'], cd['wall_anchored'],
             cd['intruder_anchored'], cd['free']))
    for c in b['contacts']:
        print('    contact %-5s %-4s n=(%+.6f,%+.6f) pt=(%.6f,%.6f) gap=%.2e %s%s'
              % (c['kind'], c['other'], c['n'][0], c['n'][1], c['pt'][0],
                 c['pt'][1], c['gap'], c['type'],
                 ('  admissible axes %d' % c['n_admissible'])
                 if c['n_admissible'] > 1 else ''))
    m = b.get('motion')
    if m:
        print('    exit motion: ds %+.3e  linf %.3e  moving squares %s  '
              '(Q dc %.3e = %.2f of max, Q dth %.3e)'
              % (m['ds'], m['linf'], m['moving'], m['Q_dc'], m['Q_dc_rel'],
                 m['Q_dth']))
        print('                 per-square |dc|: %s'
              % ' '.join('%d:%.2e' % (i, v) for i, v in enumerate(m['dc'])
                         if v > 1e-3 * m['linf']))
        print('                 per-square |dth|: %s'
              % ' '.join('%d:%.2e' % (i, v) for i, v in enumerate(m['dth'])
                         if v > 1e-3 * m['linf']))
        print('                 rotation dominates Q: %s   Q sole mover: %s'
              % (m['rotation_dominates_Q'], m['Q_is_sole_mover']))
print()
nb = [b for b in B if not b['non_deepest']]
print('sliding blocker was the DEEPEST at its corner: %d' % len(nb))
