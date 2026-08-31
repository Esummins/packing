#!/usr/bin/env python
"""A51-NEW-0: run the A51 side-find attractor (s = 3.8853914) through the A37
certification pipeline.

Stage A -- contact audit + GN refine + classify + CP evidence + constructive
           descent witness + residual-scaled verdict (a37_drain.analyse_landing
           / descent_witness / verdict: the lead's discipline, NOT-CP requires
           a witness).
Stage B -- A37 step 3S (soft value certificate; VALLEY has no 34-row pin
           basis so the 3R/Krawczyk path does not apply).

Nothing in A37 is edited: a37_pipeline is imported, its CERTDIR is re-aimed at
attempts/A51-midtilt-hunt/atlas_ext/certs, and load_family is patched for the
single index 2000 = A51-NEW-0.  The atlas is written to atlas_ext/atlas_a51.json
and merged into atlas_final.json by a51_append.py.

Usage: python a51_certify.py [--hit N]
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ATT, 'A37-cp-atlas', 'code'))

import a37_pipeline as P                                    # noqa: E402
import a37_drain as D                                       # noqa: E402

FIDX = 2000
LABEL = 'A51-NEW-0'
CERTDIR = os.path.join(HERE, 'certs')
os.makedirs(CERTDIR, exist_ok=True)
P.CERTDIR = CERTDIR

HITS = json.load(open(os.path.join(HERE, 'hits_3.8853914.json')))


def rep_z(k=0):
    return [float(v) for v in HITS[k]['z']]


_FAM = {}


def patched_load_family(fidx):
    if fidx == FIDX:
        return _FAM['z'], _FAM['fam'], -1
    return _ORIG_LOAD(fidx)


_ORIG_LOAD = P.load_family
P.load_family = patched_load_family


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hit', type=int, default=0)
    ap.add_argument('--bisect', type=int, default=14)
    ap.add_argument('--hmax-num', type=int, default=1, dest='hmax_num')
    ap.add_argument('--hmax-den', type=int, default=20, dest='hmax_den')
    a = ap.parse_args()
    args = argparse.Namespace(
        bisect=a.bisect, hmax_num=a.hmax_num, hmax_den=a.hmax_den,
        tol0=[1e-7, 1e-6, 1e-5, 1e-4], tol1=1e-9, soft_only=False)

    z = rep_z(a.hit)
    t0 = time.time()
    log = []

    # ---------------------------------------------------------- STAGE A
    print('=' * 74)
    print('STAGE A  contact audit + residual-scaled classification')
    x = D.z_to_a04(z)
    x, _, s_rep = D.repair(x)
    an = D.analyse_landing(x)
    wit = D.descent_witness(x, an['descent_dir'])
    vd, why = D.verdict(an['cls'], an['cp'], wit)
    stageA = {
        'representative': {'source': HITS[a.hit]['src'],
                           'seed': HITS[a.hit]['seed'],
                           'replica': HITS[a.hit]['rep'],
                           's_landing': HITS[a.hit]['s'],
                           's_after_repair': s_rep},
        'tol_c': an['tol_c'], 'gn_residual': an['gn_residual'],
        'displacement': an['displacement'],
        'n_contacts': an['n_contacts'],
        'pipeline_class': an['cls']['class'], 'rank': an['cls']['rank'],
        'sv_min_kept': an['cls']['sv_min_kept'],
        'sv_max_dropped': an['cls']['sv_max_dropped'],
        'rattler_squares': an['cls']['rattler_squares'],
        'cp_evidence': an['cp'], 'descent_witness': wit,
        'verdict': vd, 'verdict_why': why, 'ladder': an['ladder'],
    }
    print('  representative: %s seed %s replica %s, s = %.16f'
          % (HITS[a.hit]['src'], HITS[a.hit]['seed'], HITS[a.hit]['rep'],
             HITS[a.hit]['s']))
    print('  tol_c %.0e, GN residual %.3e, |dz| %.3e, contacts %s'
          % (an['tol_c'], an['gn_residual'], an['displacement'],
             an['n_contacts']))
    print('  classify: %s rank %d/34 (sv_min_kept %.3e, sv_max_dropped %.3e)'
          % (an['cls']['class'], an['cls']['rank'], an['cls']['sv_min_kept'],
             an['cls']['sv_max_dropped']))
    print('  CP evidence: nnls residual %.3e, LP feasible %s, LP descent '
          'rate %s, min free-sign multiplier %.3e'
          % (an['cp']['nnls_residual'], an['cp']['lp_feasible'],
             an['cp']['lp_descent_rate'],
             an['cp']['min_multiplier_free_sign']))
    print('  constructive witness: %s' % wit)
    print('  VERDICT (residual-scaled): %s  [%s]' % (vd, why))

    # ---------------------------------------------------------- STAGE B
    zh = an['z']
    thetas = sorted(round(math.degrees(float(zh[3 * i + 2])) % 90.0, 4)
                    for i in range(P.NSQ))
    _FAM['z'] = [Fraction(v) for v in zh]
    _FAM['fam'] = {
        's_min': float(zh[P.S_IDX]),
        'n_pair_contacts': an['n_contacts']['pairs'],
        'n_wall_contacts': an['n_contacts']['walls'],
        'tilt_pattern_deg': thetas,
        'count': len(HITS),
        'drain_id': LABEL,
    }
    print('\n' + '=' * 74)
    print('STAGE B  A37 pipeline (step 3S soft path)')
    entry, plog = P.process_family(FIDX, args)
    print('\n'.join(plog))

    sig = P.canonical_sig([float(v) for v in _FAM['z']])
    entry['canonical_sig'] = [list(p) for p in sig]
    entry['dedupe_merges'] = []
    entry['wall_secs'] = time.time() - t0
    entry['stage_a'] = stageA

    atlas = {'entries': [entry],
             'meta': {'attempt': 'A51-midtilt-hunt (atlas extension)',
                      'spec': 'attempts/A37-cp-atlas/notes/cookbook.md',
                      'producer': 'attempts/A51-midtilt-hunt/atlas_ext/'
                                  'a51_certify.py',
                      'pipeline': 'attempts/A37-cp-atlas/code/a37_pipeline.py',
                      'checker': 'attempts/A37-cp-atlas/code/a37_check.py'}}
    with open(os.path.join(HERE, 'atlas_a51.json'), 'w') as f:
        json.dump(atlas, f, indent=1)
    with open(os.path.join(HERE, 'stage_a.json'), 'w') as f:
        json.dump(stageA, f, indent=1)
    print('\nwrote atlas_ext/atlas_a51.json  (%.1fs)' % entry['wall_secs'])
    print('class %s | h_certified %s | V@1e-3 %.15f'
          % (entry['class'], entry['h_certified'],
             entry['value']['V_soft_at_1e-3']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
