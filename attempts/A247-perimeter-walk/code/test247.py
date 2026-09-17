"""A247 self-tests: D4 on the cells, enclosure soundness, the exact layer, and a few pair problems
whose answers are known from A246 (NSS infeasible, the wall-grain pair feasible, TWO-FAR).
    python test247.py [--eta 1e-3]
"""
import argparse
import time

import bb247 as B
import geo247 as G
import verify247 as V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eta', type=float, default=1e-3)
    ap.add_argument('--budget', type=int, default=1_500_000)
    a = ap.parse_args()
    ok, bad = G.check_d4()
    print('D4 on the ring: %s %s' % (ok, bad or ''))
    assert ok
    w = V.soundness(5000)
    print('enclosure soundness on 5000 random boxes: worst excess %.3e' % w)
    assert w <= 1e-12
    S = (G.S_LO, G.SHAT)
    tests = {
        'NSS (A246 [T]: infeasible)': [('M', 'BL', ('BL00', 'BL01', 'BL10')), ('M', 'BL', ('BL00', 'BL01', 'BL10'))],
        'TWO-FAR (both far floor)': [('M', 'BL', ('BL00', 'BR10')), ('M', 'BL', ('BL00', 'BR10'))],
        'wall grain (A246 (b): feasible)': [('M', 'BL', ('BL00', 'BL10', 'BR10')), ('M', 'BL', ('BL00', 'BL01'))],
        'far+wall with a partner': [('M', 'BL', ('BL00', 'BL01', 'BR10')), ('M', 'BL', ('BL00',))],
        'A{00,F,FF} + B{00,F}': [('M', 'BL', ('BL00', 'BL10', 'BR10')), ('M', 'BL', ('BL00', 'BL10'))],
        'free diagonal + flat A': [('M', 'BL', ('BL00', 'BL10')), ('F', ('BL01', 'BL10'))],
        'three in a box': [('M', 'BL', ('BL00',)), ('M', 'BL', ('BL00',)), ('M', 'BL', ('BL00',))],
    }
    for name, specs in tests.items():
        t = time.time()
        r = B.solve(B.problem_of(specs, S, eta=a.eta), hmin=1e-5, budget_boxes=a.budget)
        wit = ''
        if r['witness']:
            wit = 's=%.4f ' % r['witness']['s'] + ' '.join('(%.3f,%.3f,%.1fdeg)' % (p[0], p[1], p[2] * 57.2958)
                                                          for p in r['witness']['poses'])
        print('%-34s %-10s boxes %8d undecided %6d %6.1fs %s' % (name, r['status'], r['processed'],
                                                                   r['undecided'], time.time() - t, wit), flush=True)


if __name__ == '__main__':
    main()
