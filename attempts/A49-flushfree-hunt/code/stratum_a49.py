#!/usr/bin/env python
"""stratum_a49.py -- A49 task (2): STRATUM-CONSTRAINED DESCENT.

Minimise s subject to non-overlap + containment (pack11 / SLSQP, exactly the
structure `pack11.polish` uses) PLUS *stratum* constraints that keep the
configuration FLUSH-FREE by a global margin eps_s = 0.25 deg:

    for all i < j :  class-distance(th_i, th_j) >= eps_s
    for all i     :  class-from-axis(th_i)     >= eps_s

SMOOTH ENCODING (C-infinity, so a fortiori C1 for SLSQP).  Write
Delta = th_i - th_j.  The folded class distance is
    delta = min_k |Delta - k*pi/2|  in [0, pi/4],
and  sin^2(2 Delta)  has period pi/2 in Delta, vanishes exactly on
Delta = 0 mod pi/2, and is strictly increasing in delta on [0, pi/4].  Hence

    g_ij(th) = sin^2(2 (th_i - th_j)) - sin^2(2 eps_s)  >= 0
       <=>    class-distance(th_i, th_j) >= eps_s          (EXACTLY)

and likewise g_i(th) = sin^2(2 th_i) - sin^2(2 eps_s) >= 0 for the
class-from-axis rows (the "wall class" is the class distance to angle 0).
Gradients: dg_ij/dth_i = 2 sin(4(th_i - th_j)) = -dg_ij/dth_j,
dg_i/dth_i = 2 sin(4 th_i).  55 + 11 = 66 stratum rows.

This global stratum is STRONGER than flush-freeness needs (flush-freeness only
constrains CONTACTING pairs and WALL-TOUCHING squares, and only at tol_f =
0.05 deg).  That is deliberate and stated: a point that is interior to this
stronger stratum is a fortiori interior to the flush-free set.

At each stratum minimiser:
  (i)  record which stratum rows are ACTIVE (margin <= 1e-6 deg).  Active =>
       the minimiser is pressed against the flush boundary = evidence that the
       unconstrained descent wants to acquire flush there;
  (ii) if NO stratum row is active, the point is an INTERIOR flush-free local
       minimiser: run the full Fritz-John test (A37 audit of the TRUE active
       rows, stationarity LP at lambda0 = 1, nnls residual, LP descent rate,
       constructive descent witness).  A point that passes is a CANDIDATE.

Output: results/stratum.json.   [NUM] float64 -- no certificates.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a49_common as C              # noqa: E402

P, D, pack11 = C.P, C.D, C.pack11
N, HP = C.N, C.HP
I_IDX, J_IDX = pack11.I_IDX, pack11.J_IDX

EPS_S_DEG = 0.25
ACTIVE_TOL_DEG = 1e-6
NREP = 5
ROUNDS = 60


# ------------------------------------------------------- stratum constraints
def strat_con(x, eps_rad):
    """(values, jacobian) of the 66 stratum rows; value >= 0 required."""
    th = x[2 * N:3 * N]
    thr = math.sin(2.0 * eps_rad) ** 2
    dpair = th[I_IDX] - th[J_IDX]
    vp = np.sin(2.0 * dpair) ** 2 - thr
    va = np.sin(2.0 * th) ** 2 - thr
    val = np.concatenate([vp, va])
    J = np.zeros((len(val), 3 * N + 1))
    gp = 2.0 * np.sin(4.0 * dpair)
    for p in range(len(I_IDX)):
        J[p, 2 * N + I_IDX[p]] = gp[p]
        J[p, 2 * N + J_IDX[p]] = -gp[p]
    ga = 2.0 * np.sin(4.0 * th)
    for i in range(N):
        J[len(I_IDX) + i, 2 * N + i] = ga[i]
    return val, J


def strat_margins_deg(x):
    """Class distance (deg) of every stratum row, and its margin over eps_s."""
    th = np.mod(x[2 * N:3 * N], HP)
    rows = []
    for p in range(len(I_IDX)):
        i, j = int(I_IDX[p]), int(J_IDX[p])
        d = C.class_dist_deg(th[i], th[j])
        rows.append({'row': 'pair:%d-%d' % (i, j), 'i': i, 'j': j,
                     'class_deg': d, 'margin_deg': d - EPS_S_DEG})
    for i in range(N):
        d = C.class_from_axis_deg(th[i])
        rows.append({'row': 'axis:%d' % i, 'i': i, 'j': None,
                     'class_deg': d, 'margin_deg': d - EPS_S_DEG})
    return rows


def comb_angles(x, eps_deg=EPS_S_DEG, iters=4000):
    """Restore the stratum by combing the 11 tilt classes apart on the circle
    R / 90deg, with the axis class 0 pinned (class-from-axis is the class
    distance to 0).  Used only to make a JITTERED start feasible for the
    stratum; the packing is then repaired for overlap."""
    a = np.degrees(np.mod(x[2 * N:3 * N], HP)) % 90.0
    pts = np.concatenate([[0.0], a])          # index 0 is the pinned axis
    n = len(pts)
    for _ in range(iters):
        order = np.argsort(pts)
        bad = False
        for k in range(n):
            i, j = int(order[k]), int(order[(k + 1) % n])
            gap = (pts[j] - pts[i]) % 90.0
            if gap >= eps_deg - 1e-12:
                continue
            bad = True
            need = eps_deg - gap
            wi, wj = (0.0 if i == 0 else 1.0), (0.0 if j == 0 else 1.0)
            if wi + wj == 0:
                continue
            pts[i] = (pts[i] - need * wi / (wi + wj)) % 90.0
            pts[j] = (pts[j] + need * wj / (wi + wj)) % 90.0
        if not bad:
            break
    y = np.array(x, float).copy()
    y[2 * N:3 * N] = np.radians(pts[1:])
    return y


# ---------------------------------------------------------- stratum descent
def stratum_descent(x0, eps_rad, rounds=ROUNDS, maxiter=500):
    """pack11.polish's SLSQP loop with the 66 stratum rows appended.  Fixed
    separating axis per round (as in polish), containment rows, stratum rows;
    accepted only when the result is feasible AND stratum-feasible AND s did
    not increase.  Exact-feasibility repair (which scales centres only, so it
    leaves every angle -- hence the whole stratum -- untouched) after each
    accepted round."""
    x, _, s, _ = C.repair_ok(x0)
    hist = [s]
    nacc = 0
    stall = 0
    for r in range(rounds):
        ov, _ = pack11.pair_overlaps(x)
        kfix = np.argmin(ov, axis=1)
        cons = [dict(type='ineq',
                     fun=lambda z, k=kfix: pack11._pair_con_fixed(z, k)[0],
                     jac=lambda z, k=kfix: pack11._pair_con_fixed(z, k)[1]),
                dict(type='ineq', fun=lambda z: pack11._cont_con(z)[0],
                     jac=lambda z: pack11._cont_con(z)[1]),
                dict(type='ineq', fun=lambda z: strat_con(z, eps_rad)[0],
                     jac=lambda z: strat_con(z, eps_rad)[1])]
        try:
            res = minimize(lambda z: z[3 * N], x,
                           jac=lambda z: np.eye(3 * N + 1)[3 * N],
                           constraints=cons, method='SLSQP',
                           options=dict(maxiter=maxiter, ftol=1e-14))
        except Exception:
            break
        xn = res.x.copy()
        xn[2 * N:3 * N] = np.mod(xn[2 * N:3 * N], HP)
        # damped acceptance: walk back along the SLSQP step until the result is
        # feasible, stratum-feasible and decreases s (the fixed-axis
        # linearisation can overshoot).
        d = np.array(xn, float) - np.array(x, float)
        a = d[2 * N:3 * N]
        d[2 * N:3 * N] = np.mod(a + HP / 2, HP) - HP / 2
        acc = None
        for t in (1.0, 0.5, 0.25, 0.1, 0.03, 0.01, 3e-3, 1e-3):
            y = x + t * d
            y[2 * N:3 * N] = np.mod(y[2 * N:3 * N], HP)
            try:
                yr, _, sr, ok = C.repair_ok(y)
            except Exception:
                continue
            if not ok or sr >= s - 1e-13:
                continue
            if strat_con(yr, eps_rad)[0].min() < -1e-10:
                continue
            acc = (yr, sr)
            break
        if acc is None:
            break
        x, s = acc
        hist.append(s)
        nacc += 1
        stall = 0
    return x, s, hist, nacc


# --------------------------------------------- LOCAL stratum (sharper test)
GAP_NEAR = 1e-3          # "in or near contact" for the local stratum
EPS_L_DEG = 0.05         # local stratum margin = tol_f exactly


def local_rows(x, gap_near=GAP_NEAR):
    """The rows flush-freeness ACTUALLY requires at this point: contacting (or
    near-contacting) pairs, and squares in or near contact with a wall."""
    gaps = -pack11.sat_min_overlap(x)
    v = pack11.container_viol(x)
    pairs = [(int(I_IDX[p]), int(J_IDX[p])) for p in range(len(I_IDX))
             if gaps[p] < gap_near]
    axes = [i for i in range(N) if v[i].max() > -gap_near]
    return pairs, axes


def local_strat_con(x, pairs, axes, eps_rad):
    th = x[2 * N:3 * N]
    thr = math.sin(2.0 * eps_rad) ** 2
    n = len(pairs) + len(axes)
    val = np.zeros(n)
    J = np.zeros((n, 3 * N + 1))
    for k, (i, j) in enumerate(pairs):
        dd = th[i] - th[j]
        val[k] = math.sin(2.0 * dd) ** 2 - thr
        g = 2.0 * math.sin(4.0 * dd)
        J[k, 2 * N + i] = g
        J[k, 2 * N + j] = -g
    for k, i in enumerate(axes):
        val[len(pairs) + k] = math.sin(2.0 * th[i]) ** 2 - thr
        J[len(pairs) + k, 2 * N + i] = 2.0 * math.sin(4.0 * th[i])
    return val, J


def local_stratum_descent(x0, eps_rad, rounds=ROUNDS, maxiter=500):
    """Same SLSQP loop, but the stratum rows are re-selected every round from
    the CURRENT contact set (exactly the rows the flush-free definition
    constrains, at eps = tol_f = 0.05 deg).  Within a round the constraint set
    is fixed, so the problem SLSQP sees is C-infinity.  If a round produces a
    point that is not flush-free (a contact that was not in the row set formed
    flush), the run stops and is recorded as ACQUIRED-VIA-NEW-CONTACT: the
    descent left the flush-free set through a contact the constraints were not
    watching, which is itself a flush-acquisition event."""
    x, _, s, _ = C.repair_ok(x0)
    hist = [s]
    nacc, stall, escaped, nlp = 0, 0, None, 0
    for r in range(rounds):
        ov, _ = pack11.pair_overlaps(x)
        kfix = np.argmin(ov, axis=1)
        pairs, axes = local_rows(x)
        cons = [dict(type='ineq',
                     fun=lambda z, k=kfix: pack11._pair_con_fixed(z, k)[0],
                     jac=lambda z, k=kfix: pack11._pair_con_fixed(z, k)[1]),
                dict(type='ineq', fun=lambda z: pack11._cont_con(z)[0],
                     jac=lambda z: pack11._cont_con(z)[1]),
                dict(type='ineq',
                     fun=lambda z, p=pairs, a=axes:
                     local_strat_con(z, p, a, eps_rad)[0],
                     jac=lambda z, p=pairs, a=axes:
                     local_strat_con(z, p, a, eps_rad)[1])]
        try:
            res = minimize(lambda z: z[3 * N], x,
                           jac=lambda z: np.eye(3 * N + 1)[3 * N],
                           constraints=cons, method='SLSQP',
                           options=dict(maxiter=maxiter, ftol=1e-14))
        except Exception:
            break
        xn = res.x.copy()
        xn[2 * N:3 * N] = np.mod(xn[2 * N:3 * N], HP)
        # DAMPED acceptance.  The local stratum row set is only valid near the
        # current contact set, so the full SLSQP step is not automatically
        # admissible: walk back along it until the step is feasible, decreases
        # s and stays flush-free.  If every improving step size leaves the
        # flush-free set, the SMALLEST one is the acquisition event.
        d = np.array(xn, float) - np.array(x, float)
        a = d[2 * N:3 * N]
        d[2 * N:3 * N] = np.mod(a + HP / 2, HP) - HP / 2
        acc = None
        esc = None
        for t in (1.0, 0.5, 0.25, 0.1, 0.03, 0.01, 3e-3, 1e-3):
            y = x + t * d
            y[2 * N:3 * N] = np.mod(y[2 * N:3 * N], HP)
            try:
                yr, _, sr, ok = C.repair_ok(y)
            except Exception:
                continue
            if not ok or sr >= s - 1e-13:
                continue
            fr = C.flush_report(yr, tol_f=EPS_L_DEG)
            if fr['flush_free']:
                acc = (yr, sr)
                break
            esc = {'round': r, 't': t, 's': sr,
                   'keys': [C.contact_key(q) for q in fr['violations']],
                   'min_class_deg': min(q['class_deg']
                                        for q in fr['violations'])}
        if acc is None:
            # SLSQP's fixed-axis linearisation has stalled.  Fall back to the
            # LP descent direction of the AUDITED active rows (A37's own
            # fallback in local_descent), line-searched with the same
            # feasibility + flush-free acceptance test.
            dl = D.lp_dir_at(x)
            if dl is not None:
                for t in (3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5):
                    z = D.a04_to_z(x)
                    w = D.z_to_a04([z[k] + t * float(dl[k])
                                    for k in range(C.NV)])
                    try:
                        w = pack11.polish(w, rounds=2, maxiter=300)
                    except Exception:
                        pass
                    try:
                        wr, _, sw, ok = C.repair_ok(w)
                    except Exception:
                        continue
                    if not ok or sw >= s - 1e-13:
                        continue
                    fw = C.flush_report(wr, tol_f=EPS_L_DEG)
                    if fw['flush_free']:
                        acc = (wr, sw)
                        nlp += 1
                        break
                    esc = {'round': r, 't': t, 's': sw, 'via': 'lp',
                           'keys': [C.contact_key(q) for q in fw['violations']],
                           'min_class_deg': min(q['class_deg']
                                                for q in fw['violations'])}
        if acc is None:
            if esc is not None:
                escaped = esc
            break
        x, s = acc
        hist.append(s)
        nacc += 1
        stall = 0
    return x, s, hist, nacc, escaped, nlp


def do_run_local(seed_id, replica, x0, mode, profile, eps_rad):
    t0 = time.time()
    xs, ss, hist, nacc, escaped, nlp = local_stratum_descent(x0, eps_rad)
    pairs, axes = local_rows(xs)
    th = np.mod(xs[2 * N:3 * N], HP)
    rows = ([{'row': 'pair:%d-%d' % (i, j),
              'class_deg': C.class_dist_deg(th[i], th[j])}
             for i, j in pairs]
            + [{'row': 'axis:%d' % i, 'class_deg': C.class_from_axis_deg(th[i])}
               for i in axes])
    for q in rows:
        q['margin_deg'] = q['class_deg'] - EPS_L_DEG
    active = [q for q in rows if q['margin_deg'] <= ACTIVE_TOL_DEG]
    fr = C.flush_report(xs, tol_f=EPS_L_DEG)
    rec = {'seed': seed_id, 'replica': replica, 'mode': mode,
           'profile': profile, 'eps_l_deg': EPS_L_DEG, 'stratum': 'local',
           's_start': hist[0], 's_final': ss, 'n_accepted_rounds': nacc,
           's_traj': hist, 'escaped': escaped, 'lp_fallback_steps': nlp,
           'n_local_rows': len(rows),
           'min_local_margin_deg': min((q['margin_deg'] for q in rows),
                                       default=None),
           'n_active_stratum': len(active),
           'active_stratum': sorted(active, key=lambda q: q['margin_deg'])[:12],
           'landing_flush_free': bool(fr['flush_free']),
           'feasibility': list(pack11.feasibility(xs))}
    if escaped:
        # every improving step (down to t = 1e-3 of the SLSQP step) leaves the
        # flush-free set: the descent can only continue by acquiring flush.
        rec['verdict'] = 'BLOCKED-BY-FLUSH-BOUNDARY'
        rec['fj'] = None
    elif nacc == 0:
        rec['verdict'] = 'NO-PROGRESS'
        rec['fj'] = None
    elif active:
        rec['verdict'] = 'PRESSED-ON-FLUSH-BOUNDARY'
        rec['fj'] = None
    else:
        try:
            an = D.analyse_landing(xs)
        except Exception as exc:
            an = None
            rec['fj_error'] = repr(exc)[:200]
        if an is None:
            rec['verdict'] = 'INTERIOR-ANALYSIS-FAILED'
            rec['fj'] = None
        else:
            wit = D.descent_witness(xs, an['descent_dir'],
                                    scales=(1e-3, 1e-4, 1e-5, 1e-6, 1e-7))
            lc, why = D.verdict(an['cls'], an['cp'], wit)
            rec['fj'] = {'struct_class': an['cls']['class'],
                         'rank': an['cls']['rank'],
                         'n_contacts': an['n_contacts'],
                         'tol_c': an['tol_c'],
                         'gn_residual': an['gn_residual'],
                         'cp_evidence': an['cp'], 'descent_witness': wit,
                         'class': lc, 'why': why}
            rec['verdict'] = ('INTERIOR-NOT-CP' if lc == 'NOT-CP'
                              else 'INTERIOR-CANDIDATE')
            if lc != 'NOT-CP':
                rec['candidate'] = True
                rec['z'] = [float(v) for v in an['z']]
    rec['x_final'] = [float(v) for v in xs]
    rec['wall_secs'] = time.time() - t0
    return rec, xs


# ------------------------------------------------------------------- one run
def do_run(seed_id, replica, x0, mode, profile, eps_rad):
    t0 = time.time()
    xs, ss, hist, nacc = stratum_descent(x0, eps_rad)
    rows = strat_margins_deg(xs)
    active = [r for r in rows if r['margin_deg'] <= ACTIVE_TOL_DEG]
    near = [r for r in rows if r['margin_deg'] <= 1e-4]
    fr = C.flush_report(xs, tol_f=C.TOL_F_DEG)
    rec = {'seed': seed_id, 'replica': replica, 'mode': mode,
           'profile': profile, 'eps_s_deg': EPS_S_DEG,
           's_start': hist[0], 's_final': ss, 'n_accepted_rounds': nacc,
           's_traj': hist,
           'min_stratum_margin_deg': min(r['margin_deg'] for r in rows),
           'n_active_stratum': len(active),
           'active_stratum': [{'row': r['row'], 'class_deg': r['class_deg'],
                               'margin_deg': r['margin_deg']}
                              for r in sorted(active,
                                              key=lambda q: q['margin_deg'])],
           'n_near_active_1e-4': len(near),
           'near_active_stratum': [r['row'] for r in
                                   sorted(near,
                                          key=lambda q: q['margin_deg'])[:8]],
           'landing_flush_free_tol_f': bool(fr['flush_free']),
           'landing_min_pair_class_deg': fr['min_pair_class_deg'],
           'landing_min_wall_class_deg': fr['min_wall_class_deg'],
           'feasibility': list(pack11.feasibility(xs))}

    if active:
        rec['verdict'] = 'PRESSED-ON-FLUSH-BOUNDARY'
        rec['fj'] = None
    else:
        # interior flush-free local minimiser -> full Fritz-John test
        try:
            an = D.analyse_landing(xs)
        except Exception as exc:
            an = None
            rec['fj_error'] = repr(exc)[:200]
        if an is None:
            rec['verdict'] = 'INTERIOR-ANALYSIS-FAILED'
            rec['fj'] = None
        else:
            wit = D.descent_witness(xs, an['descent_dir'],
                                    scales=(1e-3, 1e-4, 1e-5, 1e-6, 1e-7))
            lc, why = D.verdict(an['cls'], an['cp'], wit)
            rec['fj'] = {'struct_class': an['cls']['class'],
                         'rank': an['cls']['rank'],
                         'n_contacts': an['n_contacts'],
                         'tol_c': an['tol_c'],
                         'gn_residual': an['gn_residual'],
                         'displacement': an['displacement'],
                         'cp_evidence': an['cp'],
                         'descent_witness': wit,
                         'class': lc, 'why': why}
            rec['verdict'] = ('INTERIOR-NOT-CP' if lc == 'NOT-CP'
                              else 'INTERIOR-CANDIDATE')
            if lc != 'NOT-CP':
                rec['candidate'] = True
                rec['z'] = [float(v) for v in an['z']]
    rec['x_final'] = [float(v) for v in xs]
    rec['wall_secs'] = time.time() - t0
    return rec, xs


def main():
    argv = sys.argv[1:]
    nrep = NREP
    if '--reps' in argv:
        nrep = int(argv[argv.index('--reps') + 1])
    local = '--local' in argv
    eps_rad = math.radians(EPS_L_DEG if local else EPS_S_DEG)
    runner = do_run_local if local else do_run
    with open(os.path.join(C.RESULTS, 'seeds.json')) as f:
        seeds = json.load(f)['seeds']
    logp = os.path.join(C.LOGS, 'hunt_log.txt')

    def log(msg):
        line = '[%s] %s %s' % (time.strftime('%H:%M:%S'),
                               'LSTRAT' if local else 'STRAT', msg)
        print(line, flush=True)
        with open(logp, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

    ck = os.path.join(C.WORK, 'stratum%s_ckpt.json'
                      % ('_local' if local else ''))
    records, done = [], set()
    if os.path.exists(ck) and '--fresh' not in argv:
        with open(ck) as f:
            records = json.load(f)['records']
        done = {(r['seed'], r['replica']) for r in records}
        log('resumed, %d runs done' % len(records))

    t0 = time.time()
    for sd in seeds:
        for rep in range(-1, nrep):
            if (sd['id'], rep) in done:
                continue
            x0 = np.array(sd['x_a04'], float)
            if rep >= 0:
                rng = np.random.default_rng(
                    abs(hash(('strat', sd['id'], rep))) % (2 ** 32))
                x0 = C.jitter(x0, rng)
            x0 = comb_angles(x0, EPS_L_DEG if local else EPS_S_DEG)
            x0, _, _, _ = C.repair_ok(x0)
            m0 = (local_strat_con(x0, *local_rows(x0), eps_rad)[0].min()
                  if local else strat_con(x0, eps_rad)[0].min())
            try:
                rec, _ = runner(sd['id'], rep, x0, sd['mode'],
                                sd['profile'], eps_rad)
            except Exception as exc:
                log('  %s/%d FAILED %r' % (sd['id'], rep, exc))
                continue
            rec['start_stratum_min'] = float(m0)
            records.append(rec)
            mm = rec.get('min_stratum_margin_deg')
            if mm is None:
                mm = rec.get('min_local_margin_deg')
            log('  %-5s r%-3d s %.5f -> %.9f  act=%d  minmarg=%s  %s (%.1fs)'
                % (sd['id'], rep, rec['s_start'], rec['s_final'],
                   rec['n_active_stratum'],
                   ('%.3e' % mm) if mm is not None else 'n/a',
                   rec['verdict'], rec['wall_secs']))
            if len(records) % 10 == 0:
                with open(ck, 'w') as f:
                    json.dump({'records': records}, f)
    with open(ck, 'w') as f:
        json.dump({'records': records}, f)

    from collections import Counter
    agg = {'n_runs': len(records),
           'n_pressed_on_flush_boundary':
               sum(1 for r in records
                   if r['verdict'] == 'PRESSED-ON-FLUSH-BOUNDARY'),
           'n_interior': sum(1 for r in records
                             if r['verdict'].startswith('INTERIOR')),
           'n_interior_candidate': sum(1 for r in records
                                       if r['verdict'] == 'INTERIOR-CANDIDATE'),
           'n_interior_not_cp': sum(1 for r in records
                                    if r['verdict'] == 'INTERIOR-NOT-CP'),
           'verdicts': dict(Counter(r['verdict'] for r in records)),
           's_final_min': min((r['s_final'] for r in records), default=None),
           's_final_median': (sorted(r['s_final'] for r in records)
                              [len(records) // 2] if records else None),
           'n_blocked_by_flush_boundary':
               sum(1 for r in records
                   if r['verdict'] == 'BLOCKED-BY-FLUSH-BOUNDARY'),
           'n_no_progress': sum(1 for r in records
                                if r['verdict'] == 'NO-PROGRESS'),
           'active_row_types': dict(Counter(
               a['row'].split(':')[0] for r in records
               for a in r['active_stratum'])),
           'by_mode': {}}
    for md in sorted({r['mode'] for r in records}):
        sub = [r for r in records if r['mode'] == md]
        agg['by_mode'][md] = {
            'n': len(sub),
            'pressed': sum(1 for r in sub
                           if r['verdict'] == 'PRESSED-ON-FLUSH-BOUNDARY'),
            's_min': min(r['s_final'] for r in sub)}
    out = {'meta': {'attempt': 'A49-flushfree-hunt',
                    'task': 'stratum-constrained descent (flush-free stratum)',
                    'producer':
                        'attempts/A49-flushfree-hunt/code/stratum_a49.py',
                    'rigour': '[NUM] float64 -- no certificates',
                    'eps_s_deg': EPS_S_DEG,
                    'active_tol_deg': ACTIVE_TOL_DEG,
                    'n_stratum_rows': 66,
                    'encoding': 'g = sin^2(2*(th_i - th_j)) - sin^2(2*eps_s) '
                                '>= 0 (pairs) and sin^2(2*th_i) - '
                                'sin^2(2*eps_s) >= 0 (class-from-axis); '
                                'C-infinity, and EXACTLY equivalent to the '
                                'folded class distance >= eps_s because '
                                'sin^2(2.) has period pi/2 and is strictly '
                                'increasing on [0, pi/4]',
                    'note': 'the global stratum constrains ALL pairs, not '
                            'only contacting ones, and at 0.25 deg rather '
                            'than tol_f = 0.05 deg: strictly stronger than '
                            'flush-freeness, so interiority here implies '
                            'interiority of the flush-free set',
                    'n_seeds': len(seeds), 'n_replicas': nrep,
                    'wall_secs': time.time() - t0},
           'aggregate': agg, 'records': records}
    name = 'stratum_local.json' if local else 'stratum.json'
    out['meta']['stratum'] = 'local (contacting pairs / wall-touching squares '        'only, eps = tol_f = 0.05 deg, rows re-selected each round)' if local         else 'global (all 55 pairs + all 11 class-from-axis, eps_s = 0.25 deg)'
    with open(os.path.join(C.RESULTS, name), 'w') as f:
        json.dump(out, f, indent=1)
    log('WROTE results/%s %s' % (name, json.dumps(
        {k: agg[k] for k in ('n_runs', 'n_pressed_on_flush_boundary',
                             'n_blocked_by_flush_boundary', 'n_interior',
                             'n_interior_candidate', 's_final_min')})))
    return 0


if __name__ == '__main__':
    sys.exit(main())
