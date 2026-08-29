"""A45-B regression duty: regenerate A43-H1 Level 0 from scratch into a private results dir
and require an EXACT match to BOTH A31 (rows R0..R10) and A43 (rows R11/R12 + all new columns).

Protocol = attempts/A43-spine-census/code/h1/regress_h1.py, extended: A43's script compares the
STORED A43 artifact against A31.  We additionally RE-RUN the enumeration (k = 3..7 as requested)
so the reproduction is a genuine recomputation, not a file comparison.

Usage:  python regress_b.py 3 4 5 6 [7]
"""
import os, sys, json, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
A45 = os.path.abspath(os.path.join(HERE, '..', '..'))
A43H1 = os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'code', 'h1'))
A43RES = os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'results', 'h1'))
A31RES = os.path.abspath(os.path.join(A45, '..', 'A31-structure-count', 'results'))
WORK = os.path.join(A45, 'work', 'regen_l0')
sys.path.insert(0, A43H1)


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6]
    os.makedirs(WORK, exist_ok=True)
    src = os.path.join(A43RES, 'mlow_grid_a39.npz')
    if os.path.exists(src) and not os.path.exists(os.path.join(WORK, 'mlow_grid_a39.npz')):
        shutil.copy(src, WORK)
    import run_level0_h1 as R
    R.RES = WORK                      # redirect output; A43/A31 artifacts stay read-only
    out = {'ks': ks, 'per_k': {}}
    allok = True
    for k in ks:
        t0 = time.time()
        sys.argv = ['run_level0_h1.py', str(k)]
        R.main()
        new = json.load(open(os.path.join(WORK, 'level0_k%d.json' % k)))
        a31 = json.load(open(os.path.join(A31RES, 'level0_k%d.json' % k)))
        a43 = json.load(open(os.path.join(A43RES, 'level0_k%d.json' % k)))
        bad = []
        for i in range(8):                        # R0..R10 ladder = A31 verbatim
            if a31['cum'][i] != new['cum'][i]:
                bad.append('A31 cum[%d] %d != %d' % (i, a31['cum'][i], new['cum'][i]))
        for i in range(8):
            if a31['marg'][i] != new['marg'][i]:
                bad.append('A31 marg[%d]' % i)
        for i in range(5):
            if a31['soft'][i] != new['soft'][i]:
                bad.append('A31 soft[%d]' % i)
        for key in a31['branch']:
            if a31['branch'][key] != new['branch'][key]:
                bad.append('A31 branch.%s' % key)
        for key in ('soft_and', 'planar_calls', 'N_total', 'n_areps', 'n_areps_planar',
                    'R0_no_filter', 'R2_L5b', 'main_wallcap3_nonthin'):
            if a31[key] != new[key]:
                bad.append('A31 %s' % key)
        for i in range(10):                       # R11/R12 = A43
            if a43['cum'][i] != new['cum'][i]:
                bad.append('A43 cum[%d] %d != %d' % (i, a43['cum'][i], new['cum'][i]))
        for key in a43['new']:
            if a43['new'][key] != new['new'][key]:
                bad.append('A43 new.%s %s != %s' % (key, a43['new'][key], new['new'][key]))
        out['per_k']['k%d' % k] = dict(
            verdict='EXACT MATCH' if not bad else bad,
            R10=new['cum'][7], R11=new['cum'][8], R12=new['cum'][9],
            MAIN=new['branch']['main'], MAINprime=new['new']['mainprime'],
            seconds=round(time.time() - t0, 1))
        allok = allok and not bad
        print('k=%d %s  R10=%d R11=%d R12=%d (%.1fs)'
              % (k, out['per_k']['k%d' % k]['verdict'], new['cum'][7], new['cum'][8],
                 new['cum'][9], time.time() - t0), flush=True)
    out['verdict'] = 'PASS' if allok else 'FAIL'
    print('A45-B REGRESSION:', out['verdict'])
    json.dump(out, open(os.path.join(A45, 'results', 'regression_b.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
