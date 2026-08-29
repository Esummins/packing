#!/usr/bin/env python3
"""A46 task 6 -- MANDATORY CANARIES before the verdict ships.

(i)  TRUMP.  His 11-square packing at s0 EXISTS, so by A23 Lemma 2 the total
     area of pairwise interior-disjoint dead regions attributable to his
     contacts must be <= B0 = s0^2 - 11 = 4.031780343056.  We price every
     contact with the A46 tables (w_WC exact; CE/CC pilot) and check.
(ii) ATLAS VALLEYS at their OWN s (budget s^2 - 11), from the task-1 audit.

A violation would mean the tables are UNSOUND -> stop and debug.

Two pricing models per configuration:
  `table`  -- A45's convention: min over the table bins containing the realised
              parameter; an uncovered parameter is priced 0.
  `upper`  -- every CE priced at the MAXIMUM measured CE value and every CC at
              the MAXIMUM measured CC value, regardless of its own parameter.
              This is the STRONGER canary (it can only overstate).
Both ignore disjointness between the regions, which again can only overstate.
Exactness: Trump's certificate stores t = tan(theta/2) rationally, so his
extraction (a45 canary.py, copied verbatim) is exact Fractions with the A43
1e-6 contact tolerance.  The atlas entries are float (theta in radians).
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction as F

import canary as CN          # the A45 extraction, copied verbatim

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(A46, 'results')
REPO = os.path.abspath(os.path.join(A46, '..', '..'))
CERT = os.path.join(REPO, 'certs', 'trump11_certificate.json')

B0 = F(969271, 250000) ** 2 - 11


def load_tables():
    wc = json.load(open(os.path.join(RES, 'w_wc_table.json')))['entries']
    pil = json.load(open(os.path.join(RES, 'w_ce_cc_pilot.json')))['entries']
    ce = [e for e in pil if e['type'] == 'CE']
    cc = [e for e in pil if e['type'] == 'CC']
    return wc, ce, cc


def val(e):
    return F(e.get('area_exact', e.get('area_float', e.get('w_WC'))))


def price_wc(wc, phi):
    hits = [e for e in wc if float(F(e['bin'][0])) - 1e-9 <= phi
            <= float(F(e['bin'][1])) + 1e-9]
    if not hits:
        return F(0), []
    return min(F(e['w_WC']) for e in hits), [e['id'] for e in hits]


def price_ce(ce, d):
    hits = [e for e in ce if float(F(e['bin']['d'][0])) - 1e-9 <= d
            <= float(F(e['bin']['d'][1])) + 1e-9]
    if not hits:
        return F(0), []
    return min(val(e) for e in hits), [e['id'] for e in hits]


def price_cc(cc, wedge):
    """lookup by the SHARP free wedge angle (deg)."""
    hits = []
    for e in cc:
        d0, d1 = float(F(e['bin']['delta'][0])), float(F(e['bin']['delta'][1]))
        w0, w1 = sorted((min(d0 - 90, 270 - d0), min(d1 - 90, 270 - d1)))
        if w0 - 1e-9 <= wedge <= w1 + 1e-9:
            hits.append(e)
    if not hits:
        return F(0), []
    return min(val(e) for e in hits), [e['id'] for e in hits]


def wedge_of(A, B, P):
    """sharp free-wedge angle at a shared corner (exact-ish, floats)."""
    def cone(S):
        V = [(float(x), float(y)) for (x, y) in S.V]
        k = min(range(4), key=lambda k: (V[k][0] - P[0]) ** 2
                + (V[k][1] - P[1]) ** 2)
        d1 = (V[(k + 1) % 4][0] - V[k][0], V[(k + 1) % 4][1] - V[k][1])
        d2 = (V[(k - 1) % 4][0] - V[k][0], V[(k - 1) % 4][1] - V[k][1])
        a1 = math.degrees(math.atan2(d1[1], d1[0])) % 360.0
        a2 = math.degrees(math.atan2(d2[1], d2[0])) % 360.0
        if (a2 - a1) % 360.0 <= 180.0:
            return a1, (a2 - a1) % 360.0
        return a2, (a1 - a2) % 360.0
    s1, w1 = cone(A)
    s2, w2 = cone(B)
    return min((s2 - (s1 + w1)) % 360.0, (s1 - (s2 + w2)) % 360.0)


def price_contacts(contacts, wc, ce, cc, w_ce_max, w_cc_max):
    tot_t = tot_u = F(0)
    det = []
    for c in contacts:
        t = c['type']
        if t == 'WC':
            phi = c['phi_reduced']
            a, ids = price_wc(wc, phi)
            b = a
        elif t == 'CE':
            a, ids = price_ce(ce, c['d_reduced'])
            b = w_ce_max
        elif t == 'CC':
            a, ids = price_cc(cc, c.get('wedge', 90.0))
            b = w_cc_max
        else:
            a, b, ids = F(0), F(0), []
        tot_t += a
        tot_u += b
        det.append(dict(type=t, param=c.get('phi_reduced', c.get('d_reduced',
                                                                 c.get('wedge'))),
                        table=str(a), table_f=float(a),
                        upper=str(b), upper_f=float(b), bins=ids))
    return tot_t, tot_u, det


def trump(wc, ce, cc, w_ce_max, w_cc_max):
    d = json.load(open(CERT))
    s = F(d['side'])
    sq = [CN.Sq(q['cx'], q['cy'], q['t'], i) for i, q in enumerate(d['squares'])]
    k = len(sq)
    contacts = []
    for i in range(k):
        contacts += CN.wall_contacts(sq[i], s)
    for i in range(k):
        for j in range(i + 1, k):
            r = CN.classify_pair(sq[i], sq[j])
            if r:
                r['pair'] = [i, j]
                if r['type'] == 'CC':
                    r['wedge'] = wedge_of(sq[i], sq[j], r['point'])
                contacts.append(r)
    for c in contacts:
        if c['type'] == 'WC':
            c['phi_reduced'] = CN.reduce_wc(c['phi_deg'])
        elif c['type'] == 'CE':
            c['d_reduced'], c['u_reduced'] = CN.reduce_ce(c['d_deg'],
                                                          c['u_float'])
    tt, tu, det = price_contacts(contacts, wc, ce, cc, w_ce_max, w_cc_max)
    budget = s * s - 11
    cnt = {}
    for c in contacts:
        cnt[c['type']] = cnt.get(c['type'], 0) + 1
    return dict(name='trump11', side=str(s), budget=str(budget),
                budget_f=float(budget), n_contacts=len(contacts),
                type_counts=cnt, sum_table=str(tt), sum_table_f=float(tt),
                sum_upper=str(tu), sum_upper_f=float(tu),
                pass_table=bool(tt <= budget), pass_upper=bool(tu <= budget),
                capture_table=float(tt / budget),
                capture_upper=float(tu / budget), detail=det,
                wc_tilts=[c['phi_reduced'] for c in contacts
                          if c['type'] == 'WC'],
                extraction='exact Fractions (a45 canary.py verbatim), TOL 1e-6')


def atlas(wc, ce, cc, w_ce_max, w_cc_max):
    aud = json.load(open(os.path.join(RES, 'atlas_mismatch_audit.json')))
    out = []
    for e in aud['entries']:
        cs = []
        for c in e['contacts']:
            if c['rattler_incident']:
                continue
            d = dict(type=c['type'])
            if c['type'] == 'WC':
                d['phi_reduced'] = (90.0 - c['phi_deg'] if c['phi_deg'] > 45
                                    else c['phi_deg'])
            elif c['type'] == 'CE':
                d['d_reduced'] = c['delta']
            elif c['type'] == 'CC':
                d['wedge'] = min(c['free_wedges'])
            cs.append(d)
        tt, tu, det = price_contacts(cs, wc, ce, cc, w_ce_max, w_cc_max)
        budget = F(e['s']).limit_denominator(10 ** 12) ** 2 - 11
        out.append(dict(family_id=e['family_id'], cls=e['cls'], s=e['s'],
                        budget_f=float(budget), n_contacts=len(cs),
                        sum_table_f=float(tt), sum_upper_f=float(tu),
                        pass_table=bool(tt <= budget),
                        pass_upper=bool(tu <= budget),
                        capture_table=float(tt / budget),
                        capture_upper=float(tu / budget),
                        note='FLOAT contact extraction (atlas theta in radians)'))
    return out


def main():
    wc, ce, cc = load_tables()
    w_ce_max = max(val(e) for e in ce)
    w_cc_max = max(val(e) for e in cc)
    T = trump(wc, ce, cc, w_ce_max, w_cc_max)
    A = atlas(wc, ce, cc, w_ce_max, w_cc_max)
    allpass = (T['pass_table'] and T['pass_upper']
               and all(a['pass_table'] and a['pass_upper'] for a in A))
    out = dict(what='A46 task 6 canaries', B0=str(B0), B0_f=float(B0),
               w_ce_max=str(w_ce_max), w_cc_max=str(w_cc_max),
               trump=T, atlas=A,
               verdict='PASS' if allpass else 'FAIL -- TABLES UNSOUND, STOP')
    json.dump(out, open(os.path.join(RES, 'canaries.json'), 'w'), indent=1)
    print('TRUMP  s=%s  contacts=%d %s' % (T['side'], T['n_contacts'],
                                           T['type_counts']))
    print('  WC tilts (reduced): %s' % [round(x, 4) for x in T['wc_tilts']])
    print('  sum(table) = %.6f   sum(upper) = %.6f   budget = %.6f  -> %s / %s'
          % (T['sum_table_f'], T['sum_upper_f'], T['budget_f'],
             'PASS' if T['pass_table'] else 'FAIL',
             'PASS' if T['pass_upper'] else 'FAIL'))
    print('\nATLAS (own s):')
    for a in A:
        print('  fam %-9s %-16s s=%.6f  B=%.4f  table=%.4f upper=%.4f  %s/%s'
              % (str(a['family_id']), a['cls'], a['s'], a['budget_f'],
                 a['sum_table_f'], a['sum_upper_f'],
                 'PASS' if a['pass_table'] else 'FAIL',
                 'PASS' if a['pass_upper'] else 'FAIL'))
    print('\nVERDICT:', out['verdict'])


if __name__ == '__main__':
    main()
