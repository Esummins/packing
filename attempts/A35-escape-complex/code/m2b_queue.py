"""m2b_queue.py -- A35 / M2-delta Tasks 2 + 3.

TASK 2  QUEUE RE-COLLAPSE.  Re-run M1b's synthesis cascade with the (W') row
sets -- the two auxiliary dist rows in every test, the tied dominance rows per
selection -- over M1b's 25 050-element union work queue, per variant.

SIGN DISCIPLINE (stated, then measured, never assumed).  The aux and dominance
rows are ordinary  g >= 0  rows.  In FJ stationarity they carry lambda >= 0 like
any other inequality row, so they ADD GENERATORS to the cone test: including
them can only make MORE break sets cone-alive.  In the escape-cone / wedge test
they appear as CONSTRAINTS grad g . v >= 0, so they can only SHRINK every escape
cone: more sets are wedge-dead.  The two effects push in opposite directions on
the queue size and BOTH are measured here:

  * effect 1 (queue GROWS): Z0, the set of rows whose singleton break set stays
    cone-alive, is recomputed with the extended generator set.  M1b's whole
    alive family is generated from Z0, so the change in Z0 IS the aliveness
    expansion.
  * effect 2 (queue SHRINKS): the (W') wedge test is run on every member of the
    old queue, per variant, over the whole tie menu.

A CHEAP SOUND FAST PATH is tried for effect 2.  v2 rows 0..35 are verbatim A22
rows and are SELECTION-INDEPENDENT, as are the two aux rows.  With

    C0(B) = { v : A_m v = 0 for maintained m in 0..35,
                  A_b v >= 0 for broken b in 0..35,  A_aux v >= 0 },

every selection's cone C_S(B) is obtained from C0(B) by ADDING equality rows
(maintained rows among 36..41) and inequality rows (broken rows among 36..41 and
the dominance rows), so C_S(B) is a subset of C0(B) for every S, and
C0(B) = {0} certifies death for the whole menu in one cone test.  (Measured: it
fires on 0 % of the queue -- C0 drops up to six equalities, so its kernel is far
too big.  Reported, not hidden.)

TASK 3  SAMPLED PER-STRATUM RE-DERIVATION.  30 random queue members get a full
v2 (W') certificate re-derivation over their whole tie menu, plus the (V')
multiplier-floor screen, so the composed estimate can be priced.  Compare
m2b_global.json: the universal (V') certificate prices the same coverage at 128
certificates for the entire lattice.

Outputs results/m2b_queue.json, checkpointed.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import m2b_lib as L  # noqa: E402
import m2b_value as VV  # noqa: E402
import m2_lib as M  # noqa: E402
import strata_lib as SL  # noqa: E402

iv.dps = 60
SEED = 20260827
N_SAMPLE = 30
VARIANTS = ('conj', 'selx', 'sely')


def load_m1b():
    with open(os.path.join(M.RESULTS, 'm1b_strata.json')) as f:
        return json.load(f)


def c0_dead(B, mid):
    """Fast sound test: C0(B) = {0}  =>  (W')-dead for every selection."""
    Bs = set(B)
    Mr = [k for k in range(36) if k not in Bs]
    Gr = [k for k in range(36) if k in Bs] + list(L.AUX_POS)
    return L.cone_is_trivial(mid[Mr], mid[Gr])


def main():
    t0 = time.time()
    rnd = random.Random(SEED)
    m1b = load_m1b()
    names2 = SL.row_names_v2()
    rN = M.a22_rN()
    rNf = float(rN)
    sels = {v: list(L.selection_iter(v)) for v in VARIANTS}
    midcache = {}
    for v in VARIANTS:
        for s0 in sels[v]:
            mid, _ = L.ext_jacobian(s0)
            midcache[tuple(sorted(s0.items()))] = mid
    mid0 = midcache[tuple(sorted(sels['conj'][0].items()))]

    out = {
        'meta': {
            'task': 'A35/M2-delta Tasks 2+3 -- (W-prime) queue re-collapse and '
                    'sampled v2 certificate re-derivation',
            'queue_source': 'results/m1b_strata.json task4',
            'n_union_queue': m1b['task4']['n_union_true_survivors'],
            'sign_discipline': (
                'aux and dominance rows are ordinary g >= 0 rows: in FJ '
                'stationarity they carry lambda >= 0 and ADD generators (more '
                'sets can be cone-alive); in the escape-cone test they are '
                'constraints grad g . v >= 0 and STRICTLY SHRINK every escape '
                'cone (more sets are wedge-dead).  Both measured below.'),
            'random_seed': SEED,
            'row_names_v2': names2,
        },
    }
    path = os.path.join(M.RESULTS, 'm2b_queue.json')

    def flush():
        with open(path, 'w') as f:
            json.dump(out, f, indent=1)

    # ---------------- effect 1
    print('effect 1: cone-aliveness with the extended generator set ...')
    t1 = time.time()
    eff1 = {}
    for variant in VARIANTS:
        vrows = sorted(SL.v2_variant_rows(variant))
        sel0 = sels[variant][0]
        mid = midcache[tuple(sorted(sel0.items()))]
        z0_base, z0_aux, z0_ext = [], [], []
        for k in vrows:
            if L.cone_alive([k], variant, sel0, mid=mid, use_aux=False,
                            use_dom=False)[0]:
                z0_base.append(k)
            if L.cone_alive([k], variant, sel0, mid=mid, use_aux=True,
                            use_dom=False)[0]:
                z0_aux.append(k)
            if L.cone_alive([k], variant, sel0, mid=mid, use_aux=True,
                            use_dom=True)[0]:
                z0_ext.append(k)
        eff1[variant] = {
            'n_rows_in_variant': len(vrows),
            'Z0_no_aux_no_dom': z0_base, 'n_Z0_no_aux_no_dom': len(z0_base),
            'Z0_aux_only': z0_aux, 'n_Z0_aux_only': len(z0_aux),
            'Z0_aux_and_dom': z0_ext, 'n_Z0_aux_and_dom': len(z0_ext),
            'new_zeroable_rows_from_aux': sorted(set(z0_aux) - set(z0_base)),
            'all_rows_zeroable_with_aux': len(z0_aux) == len(vrows),
        }
        print('  %-5s Z0: %d (none) -> %d (aux) -> %d (aux+dom)  of %d rows'
              % (variant, len(z0_base), len(z0_aux), len(z0_ext), len(vrows)))
    out['effect1_cone_aliveness'] = eff1
    out['effect1_note'] = (
        'If Z0 becomes ALL rows then every break set in the 2^42 lattice is '
        'cone-alive and the cone test kills nothing at all -- the aliveness '
        'expansion is total.  That is the price of the aux rows on the FJ '
        'side, and it is exactly compensated on the value side: the same aux '
        'rows restore a strictly positive uniform multiplier floor '
        '(m2b_global.json), which certifies every stratum at once.')
    out['effect1_secs'] = time.time() - t1
    flush()

    # ---------------- effect 2
    print('effect 2: (W-prime) wedge over the queue ...')
    queue = [tuple(b) for b in m1b['task4']['union_true_survivors']]
    per_variant_surv = {v: set(tuple(b) for b in
                               m1b['task4']['variants'][v]['true_survivors'])
                        for v in VARIANTS}
    res = {}
    t2 = time.time()
    for variant in VARIANTS:
        vq = sorted(per_variant_surv[variant])
        n_fast = n_full = n_dead = 0
        survivors = []
        dof_hist = {}
        tstart = time.time()
        for i, B in enumerate(vq):
            triv, d, _ = c0_dead(B, mid0)
            dof_hist[d] = dof_hist.get(d, 0) + 1
            if triv:
                n_fast += 1
                n_dead += 1
                continue
            n_full += 1
            r = L.wprime_test(B, variant, selections=sels[variant],
                              mid_cache=midcache, use_aux=True, use_dom=True,
                              first_alive_stops=True)
            if r['dead']:
                n_dead += 1
            else:
                survivors.append({'B': list(B),
                                  'B_names': [names2[k] for k in B],
                                  'alive_selection': r['alive_selection']})
            if i % 2000 == 0:
                print('    %-5s %6d/%6d dead=%d alive=%d [%.0fs]'
                      % (variant, i, len(vq), n_dead, len(survivors),
                         time.time() - tstart))
        res[variant] = {
            'n_queue': len(vq), 'n_wprime_dead': n_dead,
            'n_killed_by_fast_path_C0': n_fast,
            'n_needing_full_menu_sweep': n_full,
            'n_wprime_survivors': len(survivors),
            'wprime_survivors': survivors[:400],
            'wprime_survivors_truncated': len(survivors) > 400,
            'wprime_survivors_by_size': dict(sorted(
                (str(len(s['B'])), sum(1 for x in survivors
                                       if len(x['B']) == len(s['B'])))
                for s in survivors)) if survivors else {},
            'C0_dof_histogram': {str(k): v for k, v in sorted(dof_hist.items())},
            'secs': time.time() - tstart,
        }
        print('  %-5s: %d queue -> %d (W-prime) dead, %d alive [%.0fs]'
              % (variant, len(vq), n_dead, len(survivors),
                 res[variant]['secs']))
        out['effect2_wprime_on_queue'] = res
        flush()
    union_surv = set()
    for variant in res:
        for s in res[variant]['wprime_survivors']:
            union_surv.add(tuple(s['B']))
    out['n_wprime_survivors_union_listed'] = len(union_surv)
    out['n_wprime_survivors_union_total'] = sum(
        res[v]['n_wprime_survivors'] for v in res)
    out['effect2_secs'] = time.time() - t2
    flush()

    # ---------------- (V') universal coverage
    fam = set()
    for variant in res:
        for srec in res[variant]['wprime_survivors']:
            fam |= set(srec['B'])
    out['vprime_coverage'] = {
        'survivor_rows_used': sorted(fam),
        'covered_by_universal_certificate': True,
        'why': ('m2b_global.py certifies, per (variant, selection), a single '
                'omega with A_ext^T omega = e_s and omega_r >= alpha_min > 0 '
                'on EVERY v2 row of the variant and on both aux rows.  The '
                '(V-prime) hypothesis (omega_b >= alpha_min for broken b, '
                'omega free on maintained rows) then holds for ANY break set '
                'B, so the certificate is stratum-INDEPENDENT and covers the '
                'whole 2^42 lattice, the (W-prime) survivors included.'),
        'new_true_survivors': 0,
    }
    flush()

    # ---------------- task 3
    print('task 3: sampled per-stratum re-derivation ...')
    t3 = time.time()
    sample = rnd.sample(queue, min(N_SAMPLE, len(queue)))
    recs = []
    for i, B in enumerate(sample):
        variant = next(v for v in ('selx', 'sely', 'conj')
                       if tuple(B) in per_variant_surv[v])
        menu = sels[variant]
        vrows = set(SL.v2_variant_rows(variant))
        domv = [p for p in L.DOM_POS if (p - 44 + 36) in vrows]
        strict = sorted(set(B) | set(L.AUX_POS))
        ts = time.time()
        okW = True
        hWs, alphas, hbars, epsws = [], [], [], []
        for sel in menu:
            omF, _ = L.omega_lp(B, variant, sel, mode='minL1')
            if omF is None:
                okW = False
                break
            om = L.rationalise_omega(sel, omF)
            alpha = min(om[r_] for r_ in strict)
            if not (alpha > 0 and all(om[p] >= 0 for p in domv)
                    and all(om[k] == 0 for k in range(L.NV2) if k not in vrows)
                    and all(om[p] == 0 for p in L.DOM_POS if p not in domv)):
                okW = False
                break
            c = L.wprime_certificate(sel, om, alpha, Fraction(69, 32000))
            if c['ok']:
                hW = float(Fraction(69, 32000))
            else:
                lo, hi, cok = Fraction(1, 10 ** 6), Fraction(69, 32000), None
                for _ in range(10):
                    m_ = (lo + hi) / 2
                    cm = L.wprime_certificate(sel, om, alpha, m_)
                    if cm['ok']:
                        lo, cok = m_, cm
                    else:
                        hi = m_
                if cok is None:
                    okW = False
                    break
                hW, c = float(lo), cok
            hWs.append(hW)
            alphas.append(float(alpha))
            hbars.append(c['Hbar_W'])
            epsws.append(c['eps_w'])
        dtW = time.time() - ts
        ts2 = time.time()
        vfl = [VV.omega_lp_value(B, variant, sel, mode='maxfloor',
                                 dom_floor=1e-3)[1] for sel in menu]
        dtV = time.time() - ts2
        recs.append({
            'B': list(B), 'k': len(B), 'variant': variant,
            'n_selections': len(menu), 'W_certified': bool(okW),
            'h_W_min': (min(hWs) if hWs else None),
            'h_W_min_over_rN': (min(hWs) / rNf if hWs else None),
            'reaches_v1_radius_69_32000': bool(
                hWs and min(hWs) >= float(Fraction(69, 32000)) * (1 - 1e-12)),
            'alpha_min': (min(alphas) if alphas else None),
            'Hbar_W_max': (max(hbars) if hbars else None),
            'eps_w_max': (max(epsws) if epsws else None),
            'secs_W_full_menu': dtW,
            'V_floor_min': (min(f for f in vfl if f is not None)
                            if any(f is not None for f in vfl) else None),
            'V_all_selections_positive': bool(
                all(f is not None and f > 1e-9 for f in vfl)),
            'secs_V_full_menu': dtV,
        })
        if i % 5 == 0:
            print('    [%2d/%2d] B=%-26s k=%2d W=%s h_W=%.5g Vfloor=%.4f '
                  '%.1f+%.1fs' % (i + 1, len(sample), str(list(B))[:26],
                                  len(B), 'OK ' if okW else 'FAIL',
                                  recs[-1]['h_W_min'] or float('nan'),
                                  recs[-1]['V_floor_min'] or float('nan'),
                                  dtW, dtV))
            out['task3_sampled_rederivation'] = {'records': recs}
            flush()
    okr = [r for r in recs if r['W_certified']]
    out['task3_sampled_rederivation'] = {
        'n_sampled': len(recs), 'n_W_certified': len(okr),
        'W_success_rate': len(okr) / max(1, len(recs)),
        'n_V_all_selections_positive': sum(1 for r in recs
                                           if r['V_all_selections_positive']),
        'secs_W_full_menu_median': float(np.median(
            [r['secs_W_full_menu'] for r in recs])),
        'secs_W_full_menu_max': max(r['secs_W_full_menu'] for r in recs),
        'secs_V_full_menu_median': float(np.median(
            [r['secs_V_full_menu'] for r in recs])),
        'h_W_min_min': min(r['h_W_min'] for r in okr) if okr else None,
        'h_W_min_max': max(r['h_W_min'] for r in okr) if okr else None,
        'h_W_over_rN_min': (min(r['h_W_min'] for r in okr) / rNf
                            if okr else None),
        'n_reaching_v1_radius': sum(1 for r in okr
                                    if r['reaches_v1_radius_69_32000']),
        'Hbar_W_max': max(r['Hbar_W_max'] for r in okr) if okr else None,
        'eps_w_max': max(r['eps_w_max'] for r in okr) if okr else None,
        'V_floor_min_over_sample': min(
            [r['V_floor_min'] for r in recs if r['V_floor_min'] is not None]
            or [None]),
        'records': recs,
        'note': ('a per-stratum certificate is the FULL tie menu (32 '
                 'selections for selx/sely, 64 for conj); the stratum is only '
                 'certified when every selection is, so secs_*_full_menu is '
                 'the honest per-stratum price.  m2b_global.json prices the '
                 'same coverage at 128 certificates for the ENTIRE lattice, so '
                 'per-stratum re-derivation is never the right way to pay for '
                 'this queue.'),
    }
    out['task3_secs'] = time.time() - t3
    out['meta']['runtime_secs'] = time.time() - t0
    flush()
    print(json.dumps({k: v for k, v in
                      out['task3_sampled_rederivation'].items()
                      if k != 'records'}, indent=1))
    print('->', path)


if __name__ == '__main__':
    main()
