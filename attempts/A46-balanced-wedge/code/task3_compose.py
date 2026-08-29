#!/usr/bin/env python3
"""A46 task 3 -- COMPOSITION VERDICT.

(a) honest minimum contact counts of a FLUSH-FREE loaded core, from the proved
    lemmas only (docs/proofs/structure_lemmas.md L1/L2/L5/L6/L7 + A44
    notes/theory.md L11);
(b) certified budget sums per profile vs B0 = s0^2 - 11;
(c) the maximum conceivable sum (with the exact along-wall Voronoi truncation);
(d) the verdict and the fire zone.

Writes results/composition.json and results/composition_report.md.
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as F

import clip_util as CU

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(A46, 'results')
W = os.path.join(A46, 'work')

S0 = F(969271, 250000)
B0 = S0 * S0 - 11
PX = F(10)

# ------------------------------------------------------- structure profiles
# Flush-free => every wall contact is WC and every pair contact is CE or CC.
# n_pw = wall contacts (all WC), n_pp = pair contacts (all CE/CC).
PROFILES = [
    dict(id='THIN-1AXIS', branch='thin (L2)', k_H=3, n_pw=2, n_pp=2,
         why='L6 span count >= 3 loaded squares on the binding axis; the '
              '3-chain A-B-C with A on W_left, C on W_right; every square has '
              'H-degree exactly 2 (L1 tight, L2 thin branch).'),
    dict(id='THIN-2AXES', branch='thin (L2)', k_H=3, n_pw=4, n_pp=2,
         why='same chain, both axes binding: A also on W_bot, C also on W_top '
              '(L5b forbids opposite walls on one square, adjacent is fine).'),
    dict(id='NONTHIN-kH3', branch='non-thin (L11)', k_H=3, n_pw=3, n_pp=3,
         why='L11: no flush rows => every loaded square has H-degree >= 3; '
              'handshake 2 E_pp + E_pw >= 3 k_H = 9 with E_pp <= C(3,2) = 3 '
              'forces E_pw >= 3; E = 6 is attained (triangle + 3 wall rows).'),
    dict(id='NONTHIN-kH4', branch='non-thin (L11)', k_H=4, n_pw=2, n_pp=5,
         why='2 E_pp + E_pw >= 12, E_pw >= 2 (L6) => E >= 7, attained at '
              'E_pp = 5, E_pw = 2.'),
    dict(id='NONTHIN-kH5', branch='non-thin (L11)', k_H=5, n_pw=2, n_pp=7,
         why='2 E_pp + E_pw >= 15, E_pw >= 2 => E >= 9, attained at '
              'E_pp = 7, E_pw = 2.'),
    dict(id='NONTHIN-kH3-2AXES', branch='non-thin (L11)', k_H=3, n_pw=4,
         n_pp=3, why='both axes binding: E_pw >= 4 (L6 per axis, L7); '
              '2*3 + 4 = 10 >= 9.'),
    dict(id='NONTHIN-kH11-full', branch='non-thin (L11)', k_H=11, n_pw=4,
         n_pp=16, why='all 11 squares loaded, 2 E_pp + E_pw >= 33 with '
              'E_pw = 4 => E_pp >= 15 (Euler L4 allows E <= 3(k+4)-6 = 39).'),
]

DELTAS = [F(1), F(2), F(5), F(10), F(15), F(20), F(25), F(30), F(35), F(40),
          F(45)]


def load():
    tab = json.load(open(os.path.join(RES, 'w_wc_table.json')))
    ent = {F(e['bin'][0]): e for e in tab['entries']}
    ce = cc = {}
    p = os.path.join(RES, 'w_ce_cc_pilot.json')
    if os.path.exists(p):
        pil = json.load(open(p))
        ce = {e['id']: e for e in pil['entries'] if e['type'] == 'CE'}
        cc = {e['id']: e for e in pil['entries'] if e['type'] == 'CC'}
    return tab, ent, ce, cc


def w_at(tab, delta0):
    """min w_WC over the bins admitted when every tilt is >= delta0, i.e. the
    LOWEST bin whose upper endpoint exceeds delta0."""
    best = None
    for e in tab['entries']:
        lo, hi = F(e['bin'][0]), F(e['bin'][1])
        if hi < delta0:
            continue                       # bin entirely excluded by delta0
        v = F(e['w_WC'])
        if best is None or v < best[0]:
            best = (v, e['id'], e['status'])
    return best


# ------------------------------------------------- along-wall Voronoi caps
def wall_cap(tab, r_list=(1, 2, 3, 4, 5, 6)):
    """Exact maximum total certified dead area of r WC contacts on ONE wall of
    length s0, after the along-wall Voronoi truncation of task 5, using the
    strongest bin (40,45].  Positions taken evenly spread over [0, s0] (the
    spread that maximises the untruncated sum)."""
    e = max(tab['entries'], key=lambda x: x['w_WC_float'])
    cells = [tuple(F(v) for v in c) for c in e['cells']]
    out = {}
    for r in r_list:
        if r == 1:
            xs = [S0 / 2]
        else:
            xs = [S0 * i / (r - 1) for i in range(r)]
        tot, per = CU.wall_profile_sum(cells, PX, xs, F(-10 ** 6), F(10 ** 6))
        out[r] = dict(total=str(tot), total_f=float(tot),
                      per=[float(a) for a in per],
                      positions=[float(x) for x in xs],
                      untruncated=float(r * F(e['w_WC'])))
    return e['id'], out


def main():
    tab, ent, ce, cc = load()
    w_max = max(F(e['w_WC']) for e in tab['entries'])
    bin_id, caps = wall_cap(tab)
    best_r = max(caps, key=lambda r: caps[r]['total_f'])
    per_wall_max = F(caps[best_r]['total'])
    wall_max_total = 4 * per_wall_max

    ce_vals = {i: F(e.get('area_exact', e['area_float'])) for i, e in ce.items()}
    cc_vals = {i: F(e.get('area_exact', e['area_float'])) for i, e in cc.items()}
    w_ce_max = max(ce_vals.values()) if ce_vals else F(0)
    w_cc_max = max(cc_vals.values()) if cc_vals else F(0)
    w_int_max = max(w_ce_max, w_cc_max)

    # ------------------------------------------------ (b) profile x delta_0
    rows = []
    for prof in PROFILES:
        for d0 in DELTAS:
            wv, wid, st = w_at(tab, d0)
            for (int_name, w_int) in (('CE-only', w_ce_max),
                                      ('worst-case interior (max CE/CC pilot)',
                                       w_int_max), ('interior = 0', F(0))):
                tot = prof['n_pw'] * wv + prof['n_pp'] * w_int
                rows.append(dict(profile=prof['id'], delta0=str(d0),
                                 wall_bin=wid, wall_bin_status=st,
                                 w_WC=str(wv), interior_model=int_name,
                                 w_int=str(w_int), n_pw=prof['n_pw'],
                                 n_pp=prof['n_pp'], sum=str(tot),
                                 sum_f=float(tot), B0_f=float(B0),
                                 fires=bool(tot > B0),
                                 shortfall_factor=float(B0 / tot) if tot else None))

    # ------------------------------------------------- (c) max conceivable
    N1 = 12                       # A45 quotes N1 <= 12 wall incidences
    NC = 3 * 11 + 2               # A31 L4a total contact cap at k = 11
    n_int_max = NC - N1
    # best distribution of at most N1 wall contacts over the 4 walls, using the
    # exact per-wall Voronoi-truncated totals (concavity is NOT assumed -- the
    # optimum is taken over all compositions)
    bestd = None
    for r1 in range(0, 7):
        for r2 in range(0, 7):
            for r3 in range(0, 7):
                for r4 in range(0, 7):
                    if r1 + r2 + r3 + r4 > N1:
                        continue
                    t = sum(F(caps[r]['total']) if r else F(0)
                            for r in (r1, r2, r3, r4))
                    if bestd is None or t > bestd[0]:
                        bestd = (t, (r1, r2, r3, r4))
    wall_cap_N1 = bestd[0]
    maxc = []
    for (name, w_int) in (('CE-only', w_ce_max),
                          ('worst-case interior (max CE/CC pilot)', w_int_max)):
        for (wname, wall_term) in (('N1 x max w_WC (no disjointness at all)',
                                    N1 * w_max),
                                   ('best N1-capped wall distribution %s with '
                                    'Voronoi truncation (task 5)'
                                    % (bestd[1],), wall_cap_N1),
                                   ('4 walls x unconstrained per-wall Voronoi '
                                    'cap (VIOLATES N1 <= 12)',
                                    wall_max_total)):
            tot = wall_term + n_int_max * w_int
            maxc.append(dict(interior_model=name, wall_model=wname,
                             wall_term=str(wall_term),
                             wall_term_f=float(wall_term),
                             n_int=n_int_max, w_int=str(w_int),
                             total=str(tot), total_f=float(tot),
                             exceeds_B0=bool(tot > B0),
                             ratio=float(tot / B0)))

    # -------------------------------------------------------- (d) fire zone
    fire = []
    for n_pw in range(0, N1 + 1):
        for n_pp in range(0, n_int_max + 1):
            if n_pw + n_pp > NC:
                continue
            for (name, w_int) in (('CE-only', w_ce_max),
                                  ('worst-case interior', w_int_max)):
                t = n_pw * w_max + n_pp * w_int
                if t > B0:
                    fire.append(dict(model=name, n_WC=n_pw, n_int=n_pp,
                                     sum=float(t)))
    minimal_fire = {}
    for f in fire:
        k = f['model']
        if k not in minimal_fire or (f['n_WC'] + f['n_int']
                                     < minimal_fire[k]['n_WC']
                                     + minimal_fire[k]['n_int']):
            minimal_fire[k] = f

    out = dict(
        what='A46 task 3: flush-free budget composition verdict',
        s0=str(S0), B0=str(B0), B0_float=float(B0),
        table='results/w_wc_table.json (exact Fractions, 11/11 bins)',
        w_WC_max=str(w_max), w_WC_max_f=float(w_max),
        w_CE_pilot=({i: str(v) for i, v in ce_vals.items()} or None),
        w_CC_pilot=({i: str(v) for i, v in cc_vals.items()} or None),
        interior_pilot_status='FLOAT-ONLY (task 4 pilot)',
        wall_voronoi_cap=dict(bin=bin_id, per_r=caps, best_r=best_r,
                              per_wall_max=str(per_wall_max),
                              per_wall_max_f=float(per_wall_max),
                              four_walls=str(wall_max_total),
                              four_walls_f=float(wall_max_total)),
        profiles=PROFILES, profile_rows=rows,
        max_conceivable=maxc,
        wall_cap_N1=str(wall_cap_N1), wall_cap_N1_f=float(wall_cap_N1),
        wall_cap_N1_distribution=list(bestd[1]),
        fire_zone=dict(n_points=len(fire), points=fire, minimal=minimal_fire,
                       note='(n_WC, n_int) pairs whose sum at the MAXIMUM per-'
                            'contact values exceeds B0; caps N1 <= 12, '
                            'n_WC + n_int <= 3k+2 = 35'),
        )
    json.dump(out, open(os.path.join(RES, 'composition.json'), 'w'), indent=1)

    # ------------------------------------------------------------- printout
    print('B0 = %s = %.9f' % (B0, float(B0)))
    print('max w_WC = %s = %.6f  (bin %s)' % (w_max, float(w_max), bin_id))
    print('\nper-wall Voronoi cap (bin %s, s0 = %.6f):' % (bin_id, float(S0)))
    for r, v in caps.items():
        print('  r=%d  truncated total = %.6f   (untruncated %.6f)'
              % (r, v['total_f'], v['untruncated']))
    print('  best r = %d -> per wall %.6f ; 4 walls %.6f'
          % (best_r, float(per_wall_max), float(wall_max_total)))
    print('\nCE pilot: %s' % {i: float(v) for i, v in ce_vals.items()})
    print('CC pilot: %s' % {i: float(v) for i, v in cc_vals.items()})
    print('\nMAX CONCEIVABLE:')
    for m in maxc:
        print('  %-40s %-45s total %.4f  (%.3f x B0)  %s'
              % (m['interior_model'], m['wall_model'], m['total_f'],
                 m['ratio'], 'FIRES' if m['exceeds_B0'] else 'inert'))
    print('\nMINIMAL PROFILES at delta_0 = 45 (the most favourable case):')
    for prof in PROFILES:
        r = [x for x in rows if x['profile'] == prof['id']
             and x['delta0'] == '45'
             and x['interior_model'].startswith('worst')][0]
        print('  %-20s n_WC=%d n_int=%d  sum=%.4f   shortfall x%.2f'
              % (prof['id'], r['n_pw'], r['n_pp'], r['sum_f'],
                 r['shortfall_factor']))
    print('\nfire zone: %d (n_WC,n_int) points; minimal: %s'
          % (len(fire), minimal_fire))
    print('-> results/composition.json')


if __name__ == '__main__':
    main()
