"""A45-B  CHARGE filter  [EXACT once a certified table exists]  --  Theorem A45.1.

Per decoration: sum, over CORNER-TYPE interface elements, of the MIN table charge over every bin
the branch windows leave reachable; kill if the sum exceeds B0 = s0^2 - 11 = 4.031780343056.

MIN-OVER-BINS SEMANTICS (Sec 4 remark 1).  A kill must hold for EVERY realization, so each
contact contributes the minimum charge over its reachable bins, and an UNCOVERED or DROPPED bin
contributes 0.  Two accounting rules from the lead (Sec 4 remark 0 / the A45 addendum):
  * a square whose decoration gives it wall-degree 2 may realize its corner exactly at the
    container corner (one uncharged WCC interface), so ALL its wall contacts are charged 0;
  * CC contacts are uncharged by design (a free wedge >= 90 deg kills the moat), so only WC and
    CE are priced.  The H1 decoration does NOT resolve a non-flush square-square contact into
    CE vs CC, so under min-over-realizations semantics every such contact contributes 0.  The
    CE-forced column below prices them as CE anyway, as an upper-bound-on-the-bite measurement
    (NOT a sound kill).

TABLE.  results/charge_table.json (agent A) if present, else the STUB defined here.  The stub is
a demonstration of the machinery, never a certificate; every stub-derived number is labelled.
"""
from fractions import Fraction as F
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
A45 = os.path.abspath(os.path.join(HERE, '..', '..'))
TABLE_PATH = os.path.join(A45, 'results', 'charge_table.json')

S0 = F(969271, 250000)
B0 = S0 * S0 - 11                       # 4.031780343056 exactly
MOAT_LADDER = [F(1, 4), F(3, 16), F(1, 8), F(3, 32), F(1, 16)]
BIN_DEG = 3


def bins_of_window(lo_deg, hi_deg, w=BIN_DEG, top=45):
    """3-deg outward bins covering [lo,hi] after the D4 reduction to (0,45]."""
    lo = max(0, min(lo_deg, top))
    hi = max(0, min(hi_deg, top))
    return list(range(int(lo) // w, int(hi - 1e-9) // w + 1))


def stub_table():
    """STUB charge table: WC and CE only, values in the size range the ownership scheme allows
    (charge(K) <= area of B(p, rho_min/2) = rho_min^2).  rho_min = 1/8 -> cap 1/64 = 0.015625.
    Bins 0 and 14 are DROPPED (charge 0) to exercise the min-over-bins semantics."""
    rho_min = F(1, 8)
    cap = rho_min * rho_min
    wc = {}
    for j in range(15):
        wc[j] = F(0) if j in (0, 14) else cap * F(2, 5) + cap * F(j, 40)
    ce = {}
    for d in range(15):
        for u in range(4):
            ce[(d, u)] = F(0) if d in (0, 14) else cap * F(1, 4) + cap * F(d, 60)
    return dict(kind='STUB', rho_min=rho_min, cap_per_contact=cap, wc=wc, ce=ce,
                dropped_wc=[0, 14], dropped_ce=[0, 14])


def load_table():
    if not os.path.exists(TABLE_PATH):
        t = stub_table()
        t['source'] = 'STUB (results/charge_table.json absent)'
        return t
    d = json.load(open(TABLE_PATH))
    wc, ce = {}, {}
    UBIN = {F(-1, 2): 0, F(-1, 4): 1, F(0): 2, F(1, 4): 3}
    rmin = F(str(d['rho_min'])) if d.get('rho_min') is not None else None
    for e in d.get('entries', d.get('table', [])):
        ty = e.get('type', e.get('kind', '')).upper()
        c = F(0) if e.get('dropped') else F(str(e.get('charge', 0)))
        b = e.get('bins', {})
        if ty == 'WC':
            wc[int(F(str(b['phi'][0])) // BIN_DEG)] = c
        elif ty == 'CE':
            ce[(int(F(str(b['d'][0])) // BIN_DEG), UBIN[F(str(b['u'][0]))])] = c
    mx = max([F(0)] + list(wc.values()) + list(ce.values()))
    return dict(kind='CERTIFIED', rho_min=rmin,
                cap_per_contact=(rmin * rmin if rmin else None),
                max_entry=mx, max_entry_float=float(mx),
                wc=wc, ce=ce, source=os.path.relpath(TABLE_PATH, A45),
                counts=d.get('counts'), R=d.get('R'),
                dropped_wc=sorted(b for b, c in wc.items() if c == 0),
                dropped_ce=sorted(set(b for (b, u), c in ce.items() if c == 0)))


def min_wc(tab, bins):
    """min over reachable bins; an uncovered bin contributes 0 (sound)."""
    m = None
    for b in bins:
        c = tab['wc'].get(b, F(0))
        m = c if m is None or c < m else m
    return F(0) if m is None else m


def min_ce(tab, dbins, ubins=(0, 1, 2, 3)):
    m = None
    for d in dbins:
        for u in ubins:
            c = tab['ce'].get((d, u), F(0))
            m = c if m is None or c < m else m
    return F(0) if m is None else m


def decoration_charge(tab, k, wall_masks, wc_edges, ce_edges, class_windows=None,
                      force_ce=False):
    """wc_edges: (i, b) square-wall CORNER contacts.  ce_edges: (i, j) square-square NON-FLUSH
    contacts.  class_windows: {square: (lo_deg, hi_deg)} tilt window of that square's class
    after propagation (default (0,90) -> D4-reduced to the full (0,45] bin range).
    Returns (charge_sum, detail)."""
    cw = class_windows or {}
    tot = F(0)
    det = []
    wdeg = [bin(m).count('1') for m in wall_masks]
    for (i, b) in wc_edges:
        if wdeg[i] >= 2:
            det.append(('WC', i, b, '0 (wall-degree 2: WCC corner-at-container-corner allowed)'))
            continue
        lo, hi = cw.get(i, (0, 45))
        c = min_wc(tab, bins_of_window(lo, hi))
        tot += c
        det.append(('WC', i, b, str(c)))
    for (i, j) in ce_edges:
        if not force_ce:
            det.append(('SS-corner', i, j, '0 (CC branch reachable; CC uncharged by design)'))
            continue
        lo, hi = cw.get(i, (0, 45))
        c = min_ce(tab, bins_of_window(lo, hi))
        tot += c
        det.append(('CE-forced', i, j, str(c)))
    return tot, det


def ceiling_analysis():
    """Table-INDEPENDENT ceiling on Theorem A45.1's census bite.
    charge(K) <= area(B(p, rho_min/2)) = rho_min^2  (Sec 4 def (ii): the region list lives inside
    the half-moat box), and rho_min <= 1/4 (top of the shipped moat ladder).  A candidate
    structure has E <= 3k+2 contacts total (A31 L4(a) Euler bound, a HARD filter of MAIN), so
    every contact being corner-type and maximally charged gives  sum <= (3k+2)/16."""
    rows = {}
    for k in range(3, 12):
        E = 3 * k + 2
        best = E * MOAT_LADDER[0] ** 2
        rows[k] = dict(max_contacts_Euler=E, ceiling_sum_at_rho_min_quarter=str(best),
                       ceiling_float=float(best), budget=str(B0), budget_float=float(B0),
                       can_ever_fire=bool(best > B0),
                       required_mean_charge_per_contact=float(B0 / E),
                       required_rho_min=float((B0 / E) ** F(1, 2))
                       if False else float((B0 / E)) ** 0.5)
    return rows


def pilot_calibration():
    """If agent A's pilot is on disk, calibrate the ceiling with the MEASURED moat radii instead
    of the ladder maximum.  rho_min is a GLOBAL minimum over every shipped bin (Sec 3), so the
    smallest pilot radius bounds it from above."""
    p = os.path.join(A45, 'results', 'pilot.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    ent = []
    for r in d.get('results', []):
        rho = r.get('moat_rho')
        ch = (r.get('charge') or {}).get('area')
        ent.append(dict(kind=r.get('kind'), bin=r.get('bin'), moat_rho=rho,
                        charge_area=ch,
                        charge_float=float(F(ch)) if ch else None,
                        dropped=(rho is None)))
    shipped = [F(e['moat_rho']) for e in ent if e['moat_rho']]
    if not shipped:
        return dict(entries=ent, note='no shipped bin in the pilot')
    rmin = min(shipped)
    rows = {}
    for k in (3, 7, 11):
        E = 3 * k + 2
        rows[k] = dict(max_contacts=E, ceiling=str(E * rmin * rmin),
                       ceiling_float=float(E * rmin * rmin),
                       shortfall_factor=float(B0 / (E * rmin * rmin)))
    return dict(entries=ent, pilot_rho_min=str(rmin), pilot_rho_min_float=float(rmin),
                cap_per_contact=str(rmin * rmin), cap_per_contact_float=float(rmin * rmin),
                per_k=rows,
                note=('the pilot ships WC at rho = 3/16 and CE at rho = 1/16 and DROPS CC '
                      '(no moat), so rho_min <= 1/16 and every charged region lives in a box of '
                      'area <= 1/256 = 0.00390625.'))


if __name__ == '__main__':
    t = load_table()
    pc = pilot_calibration()
    if pc:
        print('pilot: rho_min <= %s, cap/contact %s; k=11 ceiling %.4f, short by %.1fx'
              % (pc['pilot_rho_min'], pc['cap_per_contact'], pc['per_k'][11]['ceiling_float'],
                 pc['per_k'][11]['shortfall_factor']))
    print('table:', t['kind'], t.get('source'), 'rho_min =', t.get('rho_min'),
          'cap/contact =', float(t['cap_per_contact']) if t.get('cap_per_contact') else None)
    print('B0 =', B0, '=', float(B0))
    for k, r in ceiling_analysis().items():
        print('k=%2d  E<=%2d  ceiling=%.4f  budget=%.4f  fires=%s  need c_min=%.4f '
              '(=> rho_min >= %.4f, ladder max 0.25)'
              % (k, r['max_contacts_Euler'], r['ceiling_float'], r['budget_float'],
                 r['can_ever_fire'], r['required_mean_charge_per_contact'],
                 r['required_rho_min']))
