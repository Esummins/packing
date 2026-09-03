"""pilot88_fj.py -- A88 TIER 2 driver: FJ exclusion on T1 survivors.

Selection (per the T3 chore spec, <= 20 structures):
  all T1 survivors from (b)+(c); if that is more than 20, 8 from (b)+(c)
  spanning chi plus 12 drawn uniformly at random from the census-sample
  survivors.  Otherwise fill up to 20 from the census-sample survivors.

Caps: 10 minutes OR 20,000 boxes per structure, whichever comes first.

Also runs the HC4 ON/OFF ablation on two structures.

Usage: python pilot88_fj.py [--max-boxes N] [--max-secs S] [--only TAG,TAG]
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import p88_struct as S                               # noqa: E402
import p88_fj as FJ                                  # noqa: E402
import p88_census as CL                              # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
OUT = os.path.join(RES, 'pilot88_fj.jsonl')
ABL = os.path.join(RES, 'pilot88_hc4_ablation.json')
CAL = os.path.join(RES, 'pilot88_fj_calib.jsonl')

MAX_STRUCT = 20


def load_all():
    sts = {}
    for l in open(os.path.join(RES, 'pilot88_structs.jsonl')):
        st = S.struct_from_json(json.loads(l))
        st.extra['set'] = 'trump' if st.tag.startswith('trump') else 'A87'
        sts[st.tag] = st
    for path, label in CL.census_sources(RES):
        for st in CL.load_census(path, label):
            sts[st.tag] = st
    return sts


def choose(sts, triage):
    surv = [r['tag'] for r in triage if r['verdict'] == 'SURVIVE']
    bc = [t for t in surv if sts[t].extra.get('set') in ('A87', 'trump')]
    cen = [t for t in surv if sts[t].extra.get('set') not in ('A87', 'trump')]
    rng = random.Random(8801)
    if len(bc) > MAX_STRUCT:
        bysort = sorted(bc, key=lambda t: sts[t].chi)
        step = max(1, len(bysort) // 8)
        pick = bysort[::step][:8]
        for t in ('trump_1e-06', 'trump_1e-09'):
            if t in bc and t not in pick:
                pick = pick[:7] + [t]
        rest = MAX_STRUCT - len(pick)
        rng.shuffle(cen)
        return pick + cen[:rest]
    rng.shuffle(cen)
    return bc + cen[:MAX_STRUCT - len(bc)]


def main():
    args = sys.argv[1:]

    def opt(name, default, cast=int):
        if name in args:
            return cast(args[args.index(name) + 1])
        return default

    max_boxes = opt('--max-boxes', 20000)
    max_secs = opt('--max-secs', 600.0, float)
    only = opt('--only', None, str)

    sts = load_all()
    triage = [json.loads(l) for l in open(os.path.join(RES,
                                                       'pilot88_triage.jsonl'))]
    tags = only.split(',') if only else choose(sts, triage)
    print('tier-2 set (%d): %s' % (len(tags), ' '.join(tags)), flush=True)

    out = []
    t0 = time.time()
    for tag in tags:
        st = sts[tag]
        r = FJ.solve(st, max_boxes=max_boxes, max_secs=max_secs)
        r['set'] = st.extra.get('set')
        r['sigma'] = st.extra.get('sigma')
        r['label'] = st.extra.get('label')
        r['d_H'] = (3 * st.k_H + 1 - st.extra['rank']) \
            if st.extra.get('rank') else None
        r['rattlers'] = st.extra.get('rattlers')
        out.append(r)
        print('%-14s D %2d m %3d  boxes %6d  %7.1fs  %6.2f ms/box  %-10s '
              'disch 1e%s  roots %d'
              % (tag, r['D'], r['m'], r['boxes'], r['secs'],
                 r['ms_per_box'] or 0, r['stopped'],
                 ('%.2f' % r['log10_discharged_frac'])
                 if r['log10_discharged_frac'] is not None else '-inf',
                 len(r['roots'])), flush=True)
        with open(OUT, 'w') as f:
            for x in out:
                f.write(json.dumps(x) + '\n')
    print('tier-2 total %.1f s' % (time.time() - t0))

    # ---- HC4 ablation on two structures
    abl = []
    for tag in tags[:2]:
        st = sts[tag]
        for flag in (True, False):
            r = FJ.solve(st, max_boxes=min(2000, max_boxes), max_secs=120.0,
                         use_hc4=flag)
            abl.append({'tag': tag, 'hc4': flag, 'boxes': r['boxes'],
                        'secs': r['secs'], 'ms_per_box': r['ms_per_box'],
                        'log10_discharged_frac': r['log10_discharged_frac'],
                        'hist': r['hist'], 'max_depth': r['max_depth']})
            print('ablation %-14s hc4=%-5s boxes %5d  %6.1fs  disch 1e%s'
                  % (tag, flag, r['boxes'], r['secs'],
                     ('%.2f' % r['log10_discharged_frac'])
                     if r['log10_discharged_frac'] is not None else '-inf'),
                  flush=True)
    json.dump(abl, open(ABL, 'w'), indent=1)
    print('wrote', OUT, 'and', ABL)

    # ---- COST CALIBRATION (not the 20-structure pilot table).
    # c_FJ from 7 census structures is too thin a base for the cost model, so
    # a larger uniform subsample of the census T1 SURVIVORS is timed.  This is
    # a MEASUREMENT of the per-structure cost, not a run of the exclusions at
    # scale: it is capped at n_cal structures and 20 s each.
    n_cal = opt('--calib', 150)
    if n_cal > 0:
        surv = [r['tag'] for r in triage if r['verdict'] == 'SURVIVE'
                and (r.get('set') in ('census', 'k0drop'))]
        rng2 = random.Random(8802)
        rng2.shuffle(surv)
        cal = []
        t1 = time.time()
        for tag in surv[:n_cal]:
            st = sts[tag]
            r = FJ.solve(st, max_boxes=20000, max_secs=20.0)
            cal.append({'tag': tag, 'set': st.extra.get('set'),
                        'k_H': r['k_H'], 'm': r['m'], 'chi': r['chi'],
                        'D': r['D'], 'boxes': r['boxes'], 'secs': r['secs'],
                        'stopped': r['stopped'], 'hist': r['hist'],
                        'n_survivor_boxes': r['n_survivor_boxes'],
                        'max_depth': r['max_depth'],
                        'ms_per_box': r['ms_per_box'],
                        'n_roots': len(r['roots'])})
        with open(CAL, 'w') as f:
            for x in cal:
                f.write(json.dumps(x) + '\n')
        comp = [x for x in cal if x['stopped'] == 'complete']
        ss = sorted(x['secs'] for x in cal)
        print('CALIBRATION: %d census survivors, %d COMPLETE (%.3f), '
              'secs mean %.4f median %.4f p95 %.4f, total %.1f s'
              % (len(cal), len(comp), len(comp) / max(1, len(cal)),
                 sum(ss) / max(1, len(ss)), ss[len(ss) // 2],
                 ss[min(len(ss) - 1, int(0.95 * len(ss)))],
                 time.time() - t1))
        print('wrote', CAL)


if __name__ == '__main__':
    main()
