"""A91 driver: T2 items (3)-(6) by MC over the exact L1 stratum, then the T3
pilot.  Writes results/samples91.jsonl, results/census91.json,
results/t3pilot91.jsonl.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import time

import numpy as np

import census91 as C
import frame91 as F
import real91 as R
import geom91 as G

RESULTS = G.RESULTS
LOGS = G.LOGS
LOGF = os.path.join(LOGS, 't2t3.log')


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    with open(LOGF, 'a') as fh:
        fh.write(s + '\n')


def ci(p, n):
    if n == 0:
        return 0.0
    return 1.96 * math.sqrt(max(p * (1 - p), 1e-12) / n)


def main(nsamp=600, npilot=20, seed=20260903):
    open(LOGF, 'w').close()
    t0 = time.time()
    rng = random.Random(seed)
    lab = json.load(open(os.path.join(RESULTS, 'census91_labelled.json')))
    N_L0 = lab['L0_labelled']
    N_L1 = lab['L1_labelled']
    log('exact labelled: L0 %.6e  L1 %.6e' % (N_L0, N_L1))
    ws, tot = R.shape_weights()
    log('shape weights built (%d shapes, L0 check %.6e vs %.6e)'
        % (len(ws), tot, N_L0))

    rows = []
    fh = open(os.path.join(RESULTS, 'samples91.jsonl'), 'w')
    nfail = 0
    for k in range(nsamp):
        f, shape = R.random_frame_L0(rng, ws, tot)
        if f is None:
            nfail += 1
            continue
        nL1 = R.l1_count(f)                       # exact #L1 refinements of this L0
        if R.sample_terminals(f, rng) is None:
            nfail += 1
            continue
        orb0 = F.orbit_size(f, 'L0')
        orb1 = F.orbit_size(f, 'L1')
        nL2, per2 = R.l2_count(f)
        nL3, per3, capped = R.l3_count(f, cap=4000)
        frac, ntry = R.sign_consistent_fraction(f, rng, ntry=20, cap=2000)
        # R6 realisability on the L2/L3 representative (one random full system)
        okl3 = False
        for s in f.slots():
            ch, _ = R.chains(f, s, cap=500)
            if ch:
                f.column[s] = rng.choice(ch)
        okl3 = all(s in f.column for s in f.slots())
        r6 = None
        if okl3:
            good, marg = R.realisable(f)
            r6 = {'realisable': bool(good), 'margin': marg}
        sh = R.corner_sharing(f) if okl3 else None
        rec = {'shape': [list(shape[0]), list(shape[1]), shape[2]],
               'orbit_L0': orb0, 'orbit_L1': orb1, 'G': C.gsize(shape[0]),
               'nL1_of_L0': nL1, 'nL2_of_L1': nL2, 'nL3_of_L2': nL3,
               'l3_capped': bool(capped), 'sign_consistent_frac': frac,
               'full_system': bool(okl3), 'R6': r6, 'sharing': sh,
               'slots': len(f.slots())}
        rows.append(rec)
        fh.write(json.dumps(rec) + '\n')
        if (k + 1) % 100 == 0:
            log('  %d/%d samples %.0fs' % (k + 1, nsamp, time.time() - t0))
    fh.close()
    n = len(rows)
    log('%d L0 samples (%d rejected shapes)' % (n, nfail))

    # ---- L1 -> L2 : importance weights w = nL1 (uniform over L1 survivors)
    w = np.array([float(r['nL1_of_L0']) for r in rows])
    a2 = np.array([float(r['nL2_of_L1']) for r in rows])
    a3 = np.array([float(r['nL3_of_L2']) for r in rows])
    fr = np.array([float(r['sign_consistent_frac']) for r in rows])
    inv0 = np.array([1.0 / r['orbit_L0'] for r in rows])
    inv1 = np.array([1.0 / r['orbit_L1'] for r in rows])
    triv0 = float(np.mean([1.0 if r['orbit_L0'] == r['G'] else 0.0 for r in rows]))
    triv1 = float(np.mean([1.0 if r['orbit_L1'] == r['G'] else 0.0 for r in rows]))
    orbL0 = N_L0 * float(inv0.mean())
    seO0 = N_L0 * float(inv0.std(ddof=1) / math.sqrt(len(inv0)))
    orbL1 = N_L1 * float((w * inv1).sum() / w.sum())
    seO1 = N_L1 * float(np.sqrt((((w * (inv1 - (w * inv1).sum() / w.sum())) ** 2)
                                 ).sum()) / w.sum())
    log('MC orbit counts (unbiased, orbits = N * E[1/|orbit|]):')
    log('  L0 orbits = %.6e +- %.1e   (labelled/|G| = %.6e; trivial-stabiliser '
        'share %.4f)' % (orbL0, seO0, lab['L0_orbits_lower_bound'], triv0))
    log('  L1 orbits = %.6e +- %.1e   (labelled/|G| = %.6e; trivial-stabiliser '
        'share %.4f)' % (orbL1, seO1, lab['L1_orbits_lower_bound'], triv1))
    mL1 = w.mean()
    log('mean #L1 per L0 = %.4f  -> L1/L0 check %.4e (exact %.4e)'
        % (mL1, mL1 * N_L0, N_L1))
    ew2 = float((w * a2).sum() / w.sum())
    se2 = float(np.sqrt(((w * (a2 - ew2)) ** 2).sum()) / w.sum())
    N_L2 = N_L1 * ew2
    log('E[#L2 | L1] = %.4f +- %.4f   ->  L2 labelled = %.4e +- %.1e'
        % (ew2, se2, N_L2, N_L1 * se2))
    ew3 = float((w * a3).sum() / w.sum())
    se3 = float(np.sqrt(((w * (a3 - ew3)) ** 2).sum()) / w.sum())
    ew3c = float((w * a3 * fr).sum() / w.sum())
    N_L3_ub = N_L1 * ew3
    N_L3 = N_L1 * ew3c
    log('E[#full column systems | L1] = %.4e +- %.1e ; sign-consistent share '
        '%.4f  -> L3 labelled point %.4e, UB %.4e'
        % (ew3, se3, (ew3c / ew3 if ew3 else 0.0), N_L3, N_L3_ub))

    # ---- R6
    r6rows = [r for r in rows if r['R6'] is not None]
    nk = sum(1 for r in r6rows if not r['R6']['realisable'])
    p = nk / max(len(r6rows), 1)
    log('R6: %d frames triaged, %d killed  kill rate %.4f +- %.4f'
        % (len(r6rows), nk, p, ci(p, len(r6rows))))
    # sharing distribution
    dist = {}
    nfm = []
    for r in rows:
        if not r['sharing']:
            continue
        key = str(r['sharing']['n_shared_pairs'])
        dist[key] = dist.get(key, 0) + 1
        nfm.append(r['sharing']['n_free_middles'])
    log('corner-sharing: #shared corner pairs distribution %s ; '
        'mean #free squares acting as middles %.3f'
        % (dist, (float(np.mean(nfm)) if nfm else 0.0)))

    out = {'exact': {'L0_labelled': N_L0, 'L1_labelled': N_L1,
                     'L0_labelled_no_tangent': lab['L0_labelled_no_tangent'],
                     'L1_labelled_no_tangent': lab['L1_labelled_no_tangent'],
                     'raw_L0_no_R1': lab['raw_L0_no_R1_no_tangent'],
                     'L0_orbits_lower_bound': lab['L0_orbits_lower_bound'],
                     'L1_orbits_lower_bound': lab['L1_orbits_lower_bound']},
           'orbits_mc': {'L0': orbL0, 'L0_se': seO0, 'L1': orbL1, 'L1_se': seO1,
                         'L0_trivial_stab_share': triv0,
                         'L1_trivial_stab_share': triv1,
                         'L0_exact_lower_bound': lab['L0_orbits_lower_bound'],
                         'L1_exact_lower_bound': lab['L1_orbits_lower_bound']},
           'mc': {'n_samples': n,
                  'L1_per_L0_mean': mL1, 'L1_check': mL1 * N_L0,
                  'E_L2_per_L1': ew2, 'E_L2_per_L1_se': se2,
                  'L2_labelled_point': N_L2, 'L2_labelled_se': N_L1 * se2,
                  'E_L3_per_L1': ew3, 'E_L3_per_L1_se': se3,
                  'L3_labelled_point': N_L3, 'L3_labelled_ub': N_L3_ub,
                  'sign_consistent_share': (ew3c / ew3 if ew3 else 0.0)},
           'R6': {'n': len(r6rows), 'killed': nk, 'kill_rate': p,
                  'kill_rate_ci95': ci(p, len(r6rows)),
                  'realisable_L2_point': N_L2 * (1 - p),
                  'realisable_L2_ci': N_L2 * ci(p, len(r6rows))},
           'sharing': {'n_shared_pairs_dist': dist,
                       'mean_free_middles': (float(np.mean(nfm)) if nfm else 0.0)},
           'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(RESULTS, 'census91.json'), 'w') as fhh:
        json.dump(out, fhh, indent=1)

    # ---------------------------------------------------------- T3 pilot
    log('--- T3 pilot ---')
    pil = []
    ph = open(os.path.join(RESULTS, 't3pilot91.jsonl'), 'w')
    cand = [r for r in rows if r['R6'] is not None and r['R6']['realisable']]
    log('%d realisable-at-R6 frames available; piloting %d'
        % (len(cand), min(npilot, len(cand))))
    # rebuild frames deterministically (re-sample with the same seed stream is
    # awkward, so pilot on freshly drawn realisable frames)
    rng2 = random.Random(seed + 1)
    done = 0
    t1 = time.time()
    while done < npilot and time.time() - t1 < 900:
        f, shape = R.random_frame_L0(rng2, ws, tot)
        if f is None:
            continue
        if R.sample_terminals(f, rng2) is None:
            continue
        ok = True
        for s in f.slots():
            ch, _ = R.chains(f, s, cap=500)
            if not ch:
                ok = False
                break
            f.column[s] = rng2.choice(ch)
        if not ok:
            continue
        good, marg = R.realisable(f)
        if not good:
            continue
        r = R.bnb(f, box_cap=20000, time_cap=60.0)
        r['shape'] = [list(shape[0]), list(shape[1]), shape[2]]
        r['margin_root'] = marg
        pil.append(r)
        ph.write(json.dumps(r) + '\n')
        done += 1
        log('  pilot %2d %s boxes %d killed %d %.2fs' %
            (done, r['verdict'], r['boxes'], r['killed'], r['seconds']))
    ph.close()
    nc = sum(1 for r in pil if r['verdict'] == 'CLOSED')
    sec = [r['seconds'] for r in pil]
    log('T3 pilot: %d frames, %d CLOSED (%.1f%%), mean %.2f s/frame, '
        'median boxes %d' % (len(pil), nc, 100.0 * nc / max(len(pil), 1),
                             (float(np.mean(sec)) if sec else 0.0),
                             int(np.median([r['boxes'] for r in pil])) if pil else 0))
    out['T3'] = {'n': len(pil), 'closed': nc,
                 'closure_rate': nc / max(len(pil), 1),
                 'mean_seconds': (float(np.mean(sec)) if sec else 0.0),
                 'median_boxes': (int(np.median([r['boxes'] for r in pil]))
                                  if pil else 0)}
    with open(os.path.join(RESULTS, 'census91.json'), 'w') as fhh:
        json.dump(out, fhh, indent=1)
    log('total %.1fs' % (time.time() - t0))
    return out


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    main(n, p)
