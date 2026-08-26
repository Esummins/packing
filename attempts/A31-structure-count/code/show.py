import json, os, sys
here = os.path.dirname(__file__)
od = os.path.join(here, '..', 'results')
L0 = {}
for k in range(2, 12):
    p = os.path.join(od, 'level0_k%d.json' % k)
    if os.path.exists(p):
        L0[k] = json.load(open(p))
ks = sorted(L0)
names = ['R0 none', 'R2 +L5b', 'R3 +L1', 'R4 +L5d', 'R5 +L4a', 'R6 +L5a',
         'R7 +L3', 'R8 +L6', 'R9 +L4b', 'R10 +L7']
print('%-10s' % 'filter' + ''.join('%16s' % ('k=%d' % k) for k in ks))
for i, nm in enumerate(names):
    row = []
    for k in ks:
        d = L0[k]
        v = [d['R0_no_filter'], d['R2_L5b']] + list(d['cum'])
        row.append(v[i])
    print('%-10s' % nm + ''.join('%16d' % x for x in row))
print()
extra = [('MAIN', lambda d: d['branch']['main']),
         ('  thin', lambda d: d['branch']['thin_main']),
         ('  non-thin', lambda d: d['branch']['main'] - d['branch']['thin_main']),
         ('lam0=0 br', lambda d: d['branch']['lam0']),
         ('selfstress', lambda d: d['branch']['selfstress_float']),
         ('soft maxw2E', lambda d: d['soft'][0]),
         ('soft maxwE', lambda d: d['soft'][1]),
         ('soft wall<=5', lambda d: d['soft'][2]),
         ('soft kiss<=8', lambda d: d['soft'][3]),
         ('soft wall<=3', lambda d: d['soft'][4] if len(d['soft']) > 4 else -1),
         ('w<=3&nonthin', lambda d: d.get('main_wallcap3_nonthin', -1)),
         ('Emax(main)', lambda d: max(int(x) for x in d['Ehist']) if d.get('Ehist') else -1),
         ('3k+1', lambda d: 3 * d['k'] + 1),
         ('secs', lambda d: int(d['seconds']))]
for nm, fn in extra:
    print('%-12s' % nm + ''.join('%16d' % fn(L0[k]) for k in ks))
print()
for k in ks:
    d = L0[k]
    b = d['marg'][3]
    print('k=%d metric-consistent base %d: L3 %d  L6 %d  planar(+cycle) %d  '
          'planar(graph only) %d' % (k, b, d['marg'][4], d['marg'][5], d['marg'][6],
                                     d['marg'][7]))
