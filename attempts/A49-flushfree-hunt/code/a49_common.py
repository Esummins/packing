#!/usr/bin/env python
"""a49_common.py -- shared machinery for the A49 flush-free hunt.

Imports (never edits) the A04 pack11 machinery and the A37 audit/drain
machinery.  Provides the FLUSH detector used by every A49 task.

DEFINITIONS (as fixed by the A49 brief)
  tilt class distance of a, b (degrees):   dd = |a-b| mod 90, folded to [0,45]
  class-from-axis of a (degrees):          min(a mod 90, 90 - (a mod 90))
  FLUSH-FREE at tol_f: every CONTACTING pair (SAT gap < 1e-6) has class
  distance >= tol_f, AND every square touching a wall (containment row active
  at 1e-6) has class-from-axis >= tol_f.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A49 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A49, '..'))
A37C = os.path.join(ATT, 'A37-cp-atlas', 'code')
A04 = os.path.join(ATT, 'A04-upper-search')
for p in (A37C, A04):
    if p not in sys.path:
        sys.path.insert(0, p)

import pack11                      # noqa: E402
import a37_pipeline as P           # noqa: E402
import a37_drain as D              # noqa: E402

N = pack11.N                       # 11
NV = P.NV                          # 34
NSQ = P.NSQ                        # 11
S_IDX = P.S_IDX                    # 33
HP = math.pi / 2

GAP_TOL = 1e-6                     # contact / wall-activity tolerance
TOL_F_DEG = 0.05                   # default flush tolerance (degrees)

I_IDX, J_IDX = pack11.I_IDX, pack11.J_IDX

RESULTS = os.path.join(A49, 'results')
WORK = os.path.join(A49, 'work')
LOGS = os.path.join(A49, 'logs')
for d in (RESULTS, WORK, LOGS):
    os.makedirs(d, exist_ok=True)


# ------------------------------------------------------------------ angles
def class_from_axis_deg(th_rad):
    """min(a mod 90, 90 - a mod 90) in degrees."""
    a = math.degrees(float(th_rad)) % 90.0
    return min(a, 90.0 - a)


def class_dist_deg(a_rad, b_rad):
    """|a-b| mod 90 folded to [0,45], in degrees."""
    d = abs(math.degrees(float(a_rad)) - math.degrees(float(b_rad))) % 90.0
    return min(d, 90.0 - d)


# ------------------------------------------------------------ flush detector
def flush_report(x, tol_f=TOL_F_DEG, gap_tol=GAP_TOL):
    """x = A04 layout vector.  Returns the full flush report.

    contacting pair  <=>  |sat_min_overlap| < gap_tol  (<=0 is separated, so a
    feasible packing has gap = -sat_min_overlap >= 0 and contact means gap
    below gap_tol).
    wall-active      <=>  containment slack |v| < gap_tol (v <= 0 feasible).
    """
    c, th, s = pack11.unpack(x)
    thm = np.mod(th, HP)
    smo = pack11.sat_min_overlap(x)              # (55,)  <=0 separated
    gaps = -smo
    v = pack11.container_viol(x)                 # (11,4) <=0 feasible
    viol = []
    contacts = []
    for k in range(len(I_IDX)):
        if gaps[k] < gap_tol:
            i, j = int(I_IDX[k]), int(J_IDX[k])
            dd = class_dist_deg(thm[i], thm[j])
            contacts.append({'type': 'pair', 'i': i, 'j': j,
                             'gap': float(gaps[k]), 'class_deg': dd})
            if dd < tol_f:
                viol.append(contacts[-1])
    wallnames = ['x=0', 'x=s', 'y=0', 'y=s']
    for i in range(N):
        rows = [wallnames[q] for q in range(4) if abs(v[i, q]) < gap_tol]
        if not rows:
            continue
        cfa = class_from_axis_deg(thm[i])
        rec = {'type': 'wall', 'i': i, 'j': None, 'walls': rows,
               'gap': float(min(abs(v[i, q]) for q in range(4)
                                if abs(v[i, q]) < gap_tol)),
               'class_deg': cfa}
        contacts.append(rec)
        if cfa < tol_f:
            viol.append(rec)
    return {'flush_free': not viol, 'violations': viol, 'contacts': contacts,
            'n_pair_contacts': sum(1 for q in contacts if q['type'] == 'pair'),
            'n_wall_contacts': sum(1 for q in contacts if q['type'] == 'wall'),
            'min_pair_class_deg': min([q['class_deg'] for q in contacts
                                       if q['type'] == 'pair'], default=None),
            'min_wall_class_deg': min([q['class_deg'] for q in contacts
                                       if q['type'] == 'wall'], default=None)}


def contact_key(rec):
    if rec['type'] == 'pair':
        return 'pair:%d-%d' % (rec['i'], rec['j'])
    return 'wall:%d:%s' % (rec['i'], '|'.join(rec['walls']))


def pair_class_at(x, i, j):
    _, th, _ = pack11.unpack(x)
    return class_dist_deg(th[i] % HP, th[j] % HP)


def wall_class_at(x, i):
    _, th, _ = pack11.unpack(x)
    return class_from_axis_deg(th[i] % HP)


# ------------------------------------------------------------------- roles
ROLE_CATS = ['chain B-B', 'press M-B', 'top T-T', 'T-wall', 'B-wall',
             'M-wall', 'M-M', 'B-T', 'M-T', 'other']


def role_of(roles, i):
    return roles[i] if roles and i < len(roles) else '?'


def deck_of(role):
    return role[0] if role and role[0] in 'BMT' else '?'


def role_pair_category(rec, roles):
    """Category of a flush event for the acquisition map."""
    if rec['type'] == 'wall':
        d = deck_of(role_of(roles, rec['i']))
        return {'B': 'B-wall', 'M': 'M-wall', 'T': 'T-wall'}.get(d, 'other')
    a, b = deck_of(role_of(roles, rec['i'])), deck_of(role_of(roles, rec['j']))
    p = ''.join(sorted([a, b]))
    return {'BB': 'chain B-B', 'BM': 'press M-B', 'TT': 'top T-T',
            'MM': 'M-M', 'BT': 'B-T', 'MT': 'M-T'}.get(p, 'other')


# --------------------------------------------------------- layout helpers
a04_to_z = D.a04_to_z
z_to_a04 = D.z_to_a04
repair = D.repair


FEAS_OK = 1e-9


def repair_ok(x, lam_hi=8.0):
    """`a37_drain.repair` with a WIDE scale search and an explicit feasibility
    check.

    A37's repair bisects the least scale lam >= 1 that kills every overlap,
    but its search is capped at lam_hi = 1.10; handed a badly overlapping
    point it returns a STILL-OVERLAPPING configuration (with a spuriously
    small s).  A37 never hit that because its inputs were near-feasible.  Any
    A49 acceptance test that trusts repair() must therefore verify.

    Returns (x_repaired, lam - 1, s, ok) with ok = the point really is a
    feasible packing (max pair overlap and containment violation <= 1e-9)."""
    xr, lam, s = repair(x, lam_hi=lam_hi)
    ov, cv = pack11.feasibility(xr)
    return xr, lam, s, bool(max(ov, cv) <= FEAS_OK)


def jitter(x, rng, sig_c=0.02, sig_a_deg=0.3):
    y = np.array(x, dtype=float).copy()
    y[:2 * N] += rng.normal(0.0, sig_c, 2 * N)
    y[2 * N:3 * N] += rng.normal(0.0, math.radians(sig_a_deg), N)
    return y
