"""VERIFICATION (a): with the new filters OFF, every A31 Level-0 number must reproduce EXACTLY."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.join(HERE, '..', '..', 'results', 'h1')
OLD = os.path.join(HERE, '..', '..', '..', 'A31-structure-count', 'results')


def check(k):
    a = json.load(open(os.path.join(OLD, 'level0_k%d.json' % k)))
    b = json.load(open(os.path.join(NEW, 'level0_k%d.json' % k)))
    bad = []
    for i in range(8):
        if a['cum'][i] != b['cum'][i]:
            bad.append('cum[%d] %d != %d' % (i, a['cum'][i], b['cum'][i]))
    for i in range(8):
        if a['marg'][i] != b['marg'][i]:
            bad.append('marg[%d] %d != %d' % (i, a['marg'][i], b['marg'][i]))
    for i in range(5):
        if a['soft'][i] != b['soft'][i]:
            bad.append('soft[%d] %d != %d' % (i, a['soft'][i], b['soft'][i]))
    for key in a['branch']:
        if a['branch'][key] != b['branch'][key]:
            bad.append('branch.%s %d != %d' % (key, a['branch'][key], b['branch'][key]))
    for key in ('soft_and', 'planar_calls', 'N_total', 'n_areps', 'n_areps_planar',
                'R0_no_filter', 'R2_L5b', 'main_wallcap3_nonthin'):
        if a[key] != b[key]:
            bad.append('%s %s != %s' % (key, a[key], b[key]))
    if {str(x): y for x, y in a['Ehist'].items()} != {str(x): y for x, y in b['Ehist'].items()}:
        bad.append('Ehist mismatch')
    return bad


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6, 7]
    out = {}
    allok = True
    for k in ks:
        try:
            bad = check(k)
        except FileNotFoundError as e:
            out['k%d' % k] = 'MISSING: %s' % e
            allok = False
            continue
        out['k%d' % k] = 'EXACT MATCH' if not bad else bad
        allok = allok and not bad
        print('k=%d %s' % (k, out['k%d' % k]))
    out['verdict'] = 'PASS' if allok else 'FAIL'
    print('REGRESSION:', out['verdict'])
    json.dump(out, open(os.path.join(NEW, 'regression.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
