#!/usr/bin/env python
"""audit_a49.py -- A49 task (3): CANDIDATE AUDITS.

Collects every CANDIDATE produced by

  (1a) code/hunt_a49.py     -- flush-free landing of a free descent that
       analyse_landing does not call NOT-CP  (results/hunt.json, outcome_a);
  (2ii) code/stratum_a49.py -- INTERIOR-CANDIDATE stratum minimisers
       (results/stratum.json, results/stratum_local.json),

and runs the FULL A37 audit on each:

  * a37_pipeline.audit contact extraction over the tolerance ladder
    {1e-7, 1e-6, 1e-5, 1e-4}, Gauss-Newton refine, re-audit at 1e-9;
  * a37_pipeline.classify -> rank, sv_min_kept / sv_max_dropped (sv_gap),
    rattler squares, RIGID / RATTLER-CORE / VALLEY;
  * Fritz-John evidence: nnls residual for e_s in the active-row cone, min
    free-sign multiplier, KKT LP feasibility, LP descent rate;
  * constructive descent-witness hunt at SEVEN scales (1e-2 .. 1e-8);
  * flush re-check at the GN-refined point (the refine moves the point, so
    flush-freeness must be re-established there);
  * D4 x relabel x translation rematch against the A04 catalogue / A37 atlas.

SURVIVOR requires ALL of:
  - GN refine converged (residual <= 1e-30) and moved the point < 1e-6;
  - the refined point is still FLUSH-FREE at tol_f;
  - no constructive descent witness (gain <= 1e-9), where the witness set is
    the LP-direction hunt from the refined point AND a strict monotone
    always-feasible descent probe (A37 local_descent) from the point;
  - FRITZ-JOHN STATIONARITY holds numerically: nnls residual for e_s in the
    active-row cone <= 1e-6 AND LP descent rate >= -1e-6.  (A 'VALLEY' class
    label alone is not evidence: a37_pipeline.classify falls back to VALLEY
    whenever its rank test is inconclusive.)
  - class is VALLEY / RIGID / RATTLER-CORE (not NOT-CP) under the
    residual-scaled verdict.

Usage:  python audit_a49.py                 # audit all candidates
        python audit_a49.py --recheck ID    # re-audit ONE candidate from
                                            # scratch in a fresh process
                                            # (required before flagging a
                                            # SURVIVOR)
Output: results/candidates/<id>.json, results/candidates/summary.json.
[NUM] float64 -- no certificates are emitted.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a49_common as C              # noqa: E402
import hunt_a49 as H                # noqa: E402

P, D, pack11 = C.P, C.D, C.pack11
N, NV, S_IDX = C.N, C.NV, C.S_IDX
S0 = 3.877084                       # incumbent upper bound

CAND_DIR = os.path.join(C.RESULTS, 'candidates')
os.makedirs(CAND_DIR, exist_ok=True)

# Witness scales.  LOCAL = A37's own (1e-4,1e-5,1e-6) plus two smaller: these
# decide NOT-CP.  WIDE = a separate BARRIER PROBE, recorded but never used to
# reject -- a 1e-2 kick followed by polish can hop into a neighbouring basin,
# which says "a lower basin is nearby", not "this point is not critical".
WIT_SCALES = (1e-4, 1e-5, 1e-6, 1e-7, 1e-8)
WIT_SCALES_WIDE = (1e-2, 1e-3)


def collect():
    """Every candidate from tasks (1a) and (2ii)."""
    out = []
    p = os.path.join(C.RESULTS, 'hunt.json')
    if os.path.exists(p):
        with open(p) as f:
            d = json.load(f)
        for r in d['records']:
            if r.get('outcome_a'):
                out.append({'id': 'hunt-%s-r%d' % (r['seed'], r['replica']),
                            'source': '1a free-descent flush-free landing',
                            'seed': r['seed'], 'replica': r['replica'],
                            's': r['s_final'],
                            'x': list(D.z_to_a04(r['landing_z']))})
    for fn, tag in (('stratum.json', '2ii global-stratum interior'),
                    ('stratum_local.json', '2ii local-stratum interior')):
        p = os.path.join(C.RESULTS, fn)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            d = json.load(f)
        for r in d['records']:
            if r.get('candidate'):
                out.append({'id': '%s-%s-r%d' % (fn.split('.')[0],
                                                 r['seed'], r['replica']),
                            'source': tag, 'seed': r['seed'],
                            'replica': r['replica'], 's': r['s_final'],
                            'x': list(r['x_final'])})
    return out


def full_audit(cand):
    t0 = time.time()
    x = np.array(cand['x'], float)
    x, lam, s_rep = D.repair(x)
    rec = dict(cand)
    rec.pop('x', None)
    rec['s_repaired'] = s_rep
    rec['repair_lam_minus_1'] = lam
    rec['feasibility'] = list(pack11.feasibility(x))
    fr0 = C.flush_report(x, tol_f=C.TOL_F_DEG)
    rec['flush_free_before_refine'] = bool(fr0['flush_free'])
    rec['flush_min_pair_class_deg'] = fr0['min_pair_class_deg']
    rec['flush_min_wall_class_deg'] = fr0['min_wall_class_deg']
    rec['n_contacts_float'] = {'pair': fr0['n_pair_contacts'],
                               'wall': fr0['n_wall_contacts']}

    an = None
    try:
        an = D.analyse_landing(x)
    except Exception as exc:
        rec['analyse_error'] = repr(exc)[:300]
    if an is None:
        rec['verdict'] = 'AUDIT-FAILED'
        rec['survivor'] = False
        rec['wall_secs'] = time.time() - t0
        return rec

    zh = [float(v) for v in an['z']]
    xh = D.z_to_a04(zh)
    frh = C.flush_report(xh, tol_f=C.TOL_F_DEG)
    wit = D.descent_witness(x, an['descent_dir'], scales=WIT_SCALES)
    # the decisive witness hunt is from the GN-REFINED point (converged to
    # ~1e-70, so any gain there is a real descent and not convergence slack)
    wit_h = D.descent_witness(xh, an['descent_dir'], scales=WIT_SCALES)
    wit_wide = D.descent_witness(xh, an['descent_dir'],
                                 scales=WIT_SCALES_WIDE)
    lc, why = D.verdict(an['cls'], an['cp'], wit)

    cls = an['cls']
    rec['audit'] = {
        'tol_c': an['tol_c'],
        'ladder': an['ladder'],
        'gn_residual': an['gn_residual'],
        'displacement': an['displacement'],
        'n_contacts': an['n_contacts'],
        'rank': cls['rank'], 'n_rows': cls['n_rows'],
        'sv_gap': [cls['sv_min_kept'], cls['sv_max_dropped']],
        'rattler_squares': cls['rattler_squares'],
        'under_contacted': cls['under_contacted'],
        'struct_class': cls['class'],
        'rfp_ok': cls.get('rfp_ok'),
        'surprises': an['aud'].get('surprises', [])[:10]}
    rec['cp_evidence'] = an['cp']
    rec['descent_witness'] = wit
    rec['descent_witness_refined'] = wit_h
    rec['barrier_probe_wide'] = wit_wide
    rec['class'] = lc
    rec['class_why'] = why
    rec['flush_free_after_refine'] = bool(frh['flush_free'])
    rec['flush_after_refine'] = {
        'min_pair_class_deg': frh['min_pair_class_deg'],
        'min_wall_class_deg': frh['min_wall_class_deg'],
        'violations': [C.contact_key(q) for q in frh['violations']]}
    rec['s_refined'] = float(zh[S_IDX])
    rec['z_refined'] = zh
    rec['match'] = H.rematch_one(zh, float(zh[S_IDX]))

    # STRICT monotone always-feasible descent probe from the candidate (A37's
    # local_descent): if s genuinely drops, the point is not a local minimum,
    # whatever the LP direction did.  This is the decisive constructive test
    # and does not depend on the audited row set being right.
    try:
        xp, sp_, it_, nlp_ = D.local_descent(x, iters=200)
        probe = {'s_probe': float(sp_), 'gain': float(s_rep - sp_),
                 'iters': it_, 'lp_steps': nlp_,
                 'flush_free_at_probe':
                     bool(C.flush_report(xp, tol_f=C.TOL_F_DEG)['flush_free'])}
    except Exception as exc:
        probe = {'error': repr(exc)[:200], 'gain': 0.0}
    rec['strict_descent_probe'] = probe

    gain = max((wit_h or {}).get('gain', 0.0), probe.get('gain', 0.0))
    ev = an['cp']
    # Fritz-John stationarity at lambda0 = 1: e_s must lie in the cone of the
    # active-row gradients (nnls residual ~ 0) and no first-order feasible
    # descent direction may exist (LP rate ~ 0).  A 'VALLEY' label alone is
    # NOT evidence -- classify() falls back to VALLEY whenever the rank test
    # is inconclusive, so the FJ numbers are required explicitly.
    fj_ok = bool(ev['nnls_residual'] <= 1e-6
                 and ev['lp_descent_rate'] is not None
                 and ev['lp_descent_rate'] >= -1e-6)
    survivor = bool(
        an['gn_residual'] <= 1e-30
        and an['displacement'] < 1e-6
        and frh['flush_free']
        and gain <= 1e-9
        and fj_ok
        and lc in ('VALLEY', 'RIGID', 'RATTLER-CORE', 'VALLEY-MARGINAL'))
    rec['survivor'] = survivor
    rec['survivor_criteria'] = {
        'gn_converged': an['gn_residual'] <= 1e-30,
        'refine_displacement_small': an['displacement'] < 1e-6,
        'flush_free_after_refine': bool(frh['flush_free']),
        'no_descent_witness': gain <= 1e-9,
        'fritz_john_stationary': fj_ok,
        'nnls_residual': ev['nnls_residual'],
        'lp_descent_rate': ev['lp_descent_rate'],
        'strict_descent_probe_gain': probe.get('gain', 0.0),
        'max_witness_gain': gain,
        'witness_gain_unrefined': (wit or {}).get('gain', 0.0),
        'barrier_probe_gain_wide': (wit_wide or {}).get('gain', 0.0),
        'class_ok': lc in ('VALLEY', 'RIGID', 'RATTLER-CORE',
                           'VALLEY-MARGINAL')}
    rec['verdict'] = 'SURVIVOR' if survivor else 'REJECTED'
    rec['s_vs_incumbent'] = float(zh[S_IDX]) - S0
    rec['seismic_if_survivor'] = bool(survivor and float(zh[S_IDX]) <= 3.8771)
    rec['wall_secs'] = time.time() - t0
    return rec


def main():
    argv = sys.argv[1:]
    only = None
    if '--recheck' in argv:
        only = argv[argv.index('--recheck') + 1]
    cands = collect()
    if only:
        cands = [c for c in cands if c['id'] == only]
    print('candidates: %d%s' % (len(cands),
                                (' (recheck %s)' % only) if only else ''),
          flush=True)
    logp = os.path.join(C.LOGS, 'hunt_log.txt')
    recs = []
    for c in cands:
        r = full_audit(c)
        recs.append(r)
        line = ('[%s] AUDIT %-28s s=%.9f  class=%s  ff_refined=%s  '
                'wit_gain=%.2e  -> %s (%.1fs)'
                % (time.strftime('%H:%M:%S'), r['id'],
                   r.get('s_refined', r.get('s_repaired', float('nan'))),
                   r.get('class', '-'), r.get('flush_free_after_refine'),
                   (r.get('survivor_criteria') or {}).get('max_witness_gain',
                                                          float('nan')),
                   r['verdict'], r['wall_secs']))
        print(line, flush=True)
        with open(logp, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
        name = r['id'] + ('.recheck.json' if only else '.json')
        with open(os.path.join(CAND_DIR, name), 'w') as f:
            json.dump(r, f, indent=1)
    summ = {'meta': {'attempt': 'A49-flushfree-hunt',
                     'task': 'candidate audits (task 3)',
                     'producer':
                         'attempts/A49-flushfree-hunt/code/audit_a49.py',
                     'rigour': '[NUM] float64 -- no certificates',
                     'tol_f_deg': C.TOL_F_DEG,
                     'witness_scales': list(WIT_SCALES),
                     'barrier_probe_scales': list(WIT_SCALES_WIDE),
                     'incumbent_s0': S0,
                     'recheck_of': only},
            'n_candidates': len(recs),
            'n_survivors': sum(1 for r in recs if r['survivor']),
            'survivors': [r['id'] for r in recs if r['survivor']],
            'by_verdict': {},
            'records': [{k: v for k, v in r.items()
                         if k not in ('z_refined',)} for r in recs]}
    from collections import Counter
    summ['by_verdict'] = dict(Counter(r['verdict'] for r in recs))
    summ['by_class'] = dict(Counter(r.get('class', '-') for r in recs))
    summ['s_min'] = min((r.get('s_refined', r.get('s_repaired'))
                         for r in recs), default=None)
    name = 'summary.recheck.json' if only else 'summary.json'
    with open(os.path.join(CAND_DIR, name), 'w') as f:
        json.dump(summ, f, indent=1)
    print('SURVIVORS: %d %s' % (summ['n_survivors'], summ['survivors']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
