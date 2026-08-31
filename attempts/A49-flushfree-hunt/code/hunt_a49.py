#!/usr/bin/env python
"""hunt_a49.py -- A49 task (1): FREE-DESCENT CENSUS + FLUSH-ACQUISITION MAP.

For each of the 12 A49 seeds (results/seeds.json) plus NREP perturbed
replicas, run the A37 free descent with a per-outer-iteration TRACE, and
classify the run:

  (a) FLUSH-FREE LANDING -- landing is flush-free at tol_f AND analyse_landing
      does not classify it clearly NOT-CP (generous: anything not NOT-CP is a
      CANDIDATE at this stage; the audit filters later);
  (b) FLUSH ACQUIRED -- record the first trace point where flush-freeness
      fails: which pair / wall row, the ROLES involved, the mismatch
      trajectory of that contact, s at the event, whether s kept dropping;
  (c) DRAIN TO KNOWN -- rematch the landing against the A04 102-family
      catalogue + the A37 atlas + the A37-NEW attractors (D4 x relabelling x
      translation, tol 1e-6, s-key 1e-8).

(b) and (c) can both fire; (a) excludes (b).

Modes:  python hunt_a49.py [--reps N] [--control] [--fresh]
  --control : negative control (task 4) on atlas VALLEY families 27, 31 and
              A37-NEW-0.  Writes results/control.json.

Checkpoints to work/hunt_ckpt.json (resume-safe) every 25 runs.
[NUM] float64 throughout -- a hunt, not a certificate run.
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
N, NV, HP = C.N, C.NV, C.HP

TOL_F = C.TOL_F_DEG
MAX_OUTER = 30


# ------------------------------------------------------------ traced descent
def _polish_traced(x0, rounds, maxiter, sink, tag):
    """pack11.polish with a per-SLSQP-ITERATE callback.  The body below is
    pack11.polish's body verbatim (same objective, same fixed-axis
    constraints, same accept test); the only addition is scipy's `callback`,
    which is pure instrumentation and does not touch the arithmetic."""
    x = x0.copy()
    for r in range(rounds):
        ov, _ = pack11.pair_overlaps(x)
        kfix = np.argmin(ov, axis=1)
        cons = [dict(type='ineq',
                     fun=lambda z, k=kfix: pack11._pair_con_fixed(z, k)[0],
                     jac=lambda z, k=kfix: pack11._pair_con_fixed(z, k)[1]),
                dict(type='ineq', fun=lambda z: pack11._cont_con(z)[0],
                     jac=lambda z: pack11._cont_con(z)[1])]
        sink.tag = '%s.polish%d' % (tag, r)
        res = minimize(lambda z: z[3 * N], x,
                       jac=lambda z: np.eye(3 * N + 1)[3 * N],
                       constraints=cons, method='SLSQP',
                       options=dict(maxiter=maxiter, ftol=1e-14),
                       callback=sink)
        xn = res.x
        xn[2 * N:3 * N] = np.mod(xn[2 * N:3 * N], np.pi / 2)
        ovn = pack11.sat_min_overlap(xn)
        cv = pack11.container_viol(xn)
        if (ovn.max() < 1e-7 and cv.max() < 1e-7
                and xn[3 * N] <= x[3 * N] + 1e-9):
            x = xn
        else:
            break
        if np.array_equal(np.argmin(pack11.pair_overlaps(x)[0], axis=1), kfix):
            break
    return x


def _penalty_traced(x0, mus, maxiter, sink, tag):
    """pack11.penalty_solve with a per-L-BFGS-B-iterate callback (body
    verbatim; callback is instrumentation only)."""
    x = x0.copy()
    for mu in mus:
        sink.tag = '%s.mu%.0e' % (tag, mu)
        res = minimize(pack11.obj_grad, x, args=(mu,), jac=True,
                       method='L-BFGS-B',
                       options=dict(maxiter=maxiter, maxcor=20, ftol=1e-15,
                                    gtol=1e-9),
                       callback=sink)
        x = res.x
        x[2 * N:3 * N] = np.mod(x[2 * N:3 * N], np.pi / 2)
        sink(x)
    return x


def free_descent_traced(x0, max_outer=MAX_OUTER):
    """a37_drain.free_descent (verbatim control flow; the A37 file is never
    edited) traced at SOLVER-ITERATE resolution: every SLSQP polish iterate
    and every L-BFGS-B penalty iterate is sampled.  Each trace point stores s,
    the 11 tilts, the feasibility residual and the flush violations of the RAW
    iterate (contact = SAT gap < 1e-6, which includes overlapping pairs, per
    the A49 definition)."""
    x = x0.copy()
    x[2 * N:3 * N] = np.mod(x[2 * N:3 * N], HP)
    best, _, s = D.repair(x)
    hist = [s]
    trace = []

    def sink(y, tag=None):
        try:
            trace.append(snap_raw(y, tag or sink.tag))
        except Exception:
            pass
    sink.tag = 'seed'
    sink(x, 'seed')
    stall = 0
    cur = x
    it = -1
    for it in range(max_outer):
        try:
            xp = _polish_traced(cur, 4, 400, sink, 'it%d.a' % it)
        except Exception:
            xp = cur
        try:
            xq = _penalty_traced(xp, (1e4, 1e5, 1e6, 1e7, 1e8), 500, sink,
                                 'it%d.p' % it)
            xq = _polish_traced(xq, 4, 400, sink, 'it%d.b' % it)
        except Exception:
            xq = xp
        improved = False
        for y in (xp, xq):
            yr, _, sy = D.repair(y)
            if sy < s - 1e-12:
                best, s = yr, sy
                improved = True
        hist.append(s)
        cur_next = xq if xq[3 * N] <= xp[3 * N] else xp
        if improved:
            stall = 0
        else:
            stall += 1
            if stall >= 2:
                break
        cur = cur_next
    for _ in range(6):
        try:
            y = pack11.polish(best, rounds=6, maxiter=600)
        except Exception:
            break
        yr, _, sy = D.repair(y)
        if sy < s - 1e-13:
            best, s = yr, sy
        else:
            break
    trace.append(snap_raw(best, 'landing'))
    return best, s, hist, trace, it + 1


FEAS_EVENT = 1e-7      # an acquisition event must sit on a FEASIBLE iterate
STEP_CAP = 0.02        # micro-descent trust radius (max coordinate move)


def _unwrap_step(x0, x1):
    """x1 - x0 with the angle block unwrapped to (-pi/4, pi/4] (polish returns
    angles reduced mod pi/2, so a raw difference can read ~pi/2)."""
    d = np.array(x1, float) - np.array(x0, float)
    a = d[2 * N:3 * N]
    d[2 * N:3 * N] = np.mod(a + HP / 2, HP) - HP / 2
    return d


def micro_descent(x0, max_dirs=12, step_cap=STEP_CAP):
    """FEASIBLE-PATH micro-trace of the descent, used ONLY to resolve the
    flush-acquisition event.

    Why it exists: one `pack11.polish` call is a full SLSQP solve, and from
    the A49 seeds it carries s from ~4.5 to the landing in a SINGLE step whose
    intermediate SLSQP iterates are infeasible by O(1e-1).  Neither
    `free_descent` nor A37's `local_descent` (whose unit step is that same
    solve) can therefore say WHERE along the path flush is acquired.

    This routine takes exactly the same SLSQP steps, but SUBDIVIDES each one:
    the segment from x to polish(x) is walked in increments of `step_cap` in
    the sup norm, and every intermediate point is repaired to exact
    feasibility.  Every trace point is thus a genuine feasible 11-square
    packing to which the flush definition applies verbatim.  It is a
    diagnostic path, never a landing claim.
    """
    x, _, s = D.repair(x0)
    trace = [snap_raw(x, 'micro.d0.t0')]
    for dk in range(max_dirs):
        try:
            x1 = pack11.polish(x, rounds=4, maxiter=400)
        except Exception:
            break
        d = _unwrap_step(x, x1)
        nrm = float(np.abs(d).max())
        if nrm < 1e-11:
            break
        nseg = int(min(200, max(1, math.ceil(nrm / step_cap))))
        for m in range(1, nseg + 1):
            y = x + (float(m) / nseg) * d
            y[2 * N:3 * N] = np.mod(y[2 * N:3 * N], HP)
            try:
                yr, _, sy = D.repair(y)
            except Exception:
                continue
            trace.append(snap_raw(yr, 'micro.d%d.t%d' % (dk, m)))
        xr, _, sr = D.repair(x1)
        x, s = x1, sr
    return x, s, trace


def snap_raw(x, tag):
    """Cheap trace point on the RAW iterate: no repair, no audit."""
    fr = C.flush_report(x, tol_f=TOL_F)
    _, th, sv = pack11.unpack(x)
    ov = float(pack11.sat_min_overlap(x).max())
    cv = float(pack11.container_viol(x).max())
    sp = {'tag': tag, 's': float(sv),
          'th': [float(v % HP) for v in th],
          'feas': max(ov, cv),
          'flush_free': fr['flush_free'],
          'viol': [C.contact_key(q) for q in fr['violations']],
          'n_contacts': fr['n_pair_contacts'] + fr['n_wall_contacts']}
    if fr['violations']:
        sp['vrecs'] = [{'k': C.contact_key(q), 'type': q['type'], 'i': q['i'],
                        'j': q.get('j'), 'cls': q['class_deg'],
                        'gap': q['gap']} for q in fr['violations']]
    return sp


def key_class_traj(trace, rec):
    """Class-distance trajectory of one contact across the whole trace
    (computed from the tilts, so it is defined even where the contact is not
    active)."""
    out = []
    for sp in trace:
        th = sp['th']
        if rec['type'] == 'pair':
            out.append(C.class_dist_deg(th[rec['i']], th[rec['j']]))
        else:
            out.append(C.class_from_axis_deg(th[rec['i']]))
    return out


# ------------------------------------------------------------------ refs
_REFS = {}


def refs():
    if not _REFS:
        t = time.time()
        atlas_entries, ref_atlas, ref_cat, fid_of_cat, missing = D.build_refs()
        # add the four A37-NEW attractors from the drain
        with open(os.path.join(C.ATT, 'A37-cp-atlas', 'results',
                               'drain.json')) as f:
            dr = json.load(f)
        ref_new = {g['id']: {'z': g['z'], 's': g['s']}
                   for g in dr.get('new_families', [])}
        _REFS.update(atlas=ref_atlas, cat=ref_cat, fid=fid_of_cat,
                     new=ref_new, missing=missing, secs=time.time() - t)
    return _REFS


def rematch_one(zl, sl):
    """Match one landing against catalogue / atlas / A37-NEW."""
    R = refs()
    out = {'family': None, 'where': None, 'why': None}
    best = None
    for tag, ref, keyname in (('catalogue', R['cat'], 'catalogue_index'),
                              ('atlas', R['atlas'], 'family_id'),
                              ('A37-NEW', R['new'], 'new_id')):
        cand = sorted(ref, key=lambda k: abs(ref[k]['s'] - sl))[:6]
        for k in cand:
            ok, why, ds, da, g = D.same_family(zl, sl, ref[k]['z'],
                                               ref[k]['s'])
            if ok:
                out['family'] = str(k)
                out['where'] = tag
                out['why'] = why
                out['ds'] = ds
                out['d_geom'] = g[0]
                out['n_aligned'] = g[1]
                if tag == 'catalogue':
                    out['atlas_family_id'] = R['fid'].get(k)
                return out
            if best is None or ds < best[0]:
                best = (ds, tag, k, why, g[0], g[1])
    out['nearest'] = {'ds': best[0], 'where': best[1], 'key': str(best[2]),
                      'why': best[3], 'd_geom': best[4],
                      'n_aligned': best[5]} if best else None
    return out


# ------------------------------------------------------------------ one run
def do_run(seed_id, replica, x0, roles, mode, profile):
    t0 = time.time()
    xl, sl, hist, trace, nout = free_descent_traced(x0)
    fr = C.flush_report(xl, tol_f=TOL_F)

    rec = {'seed': seed_id, 'replica': replica, 'mode': mode,
           'profile': profile,
           's0': hist[0], 's_final': sl, 's_traj': hist, 'n_outer': nout,
           'n_snapshots': len(trace),
           'landing_flush_free': bool(fr['flush_free']),
           'landing_min_pair_class_deg': fr['min_pair_class_deg'],
           'landing_min_wall_class_deg': fr['min_wall_class_deg'],
           'landing_n_contacts': {'pair': fr['n_pair_contacts'],
                                  'wall': fr['n_wall_contacts']},
           'landing_violations': [{'k': C.contact_key(q), 'type': q['type'],
                                   'i': q['i'], 'j': q.get('j'),
                                   'cls': q['class_deg'],
                                   'cat': C.role_pair_category(q, roles),
                                   'roles': ([C.role_of(roles, q['i']),
                                              C.role_of(roles, q['j'])]
                                             if q['type'] == 'pair'
                                             else [C.role_of(roles, q['i'])])}
                                  for q in fr['violations']],
           'seed_flush_free': bool(trace[0]['flush_free']),
           'landing_nontrivial': bool(sl < 4.0 - 1e-6)}

    # ---- (b) flush acquisition event.
    # PRIMARY resolver = the FEASIBLE-PATH micro-descent (every point an exact
    # feasible packing).  The free-descent solver-iterate trace is recorded
    # alongside, restricted to iterates that are feasible to 1e-7 (an iterate
    # the penalty phase left infeasible is not a packing and cannot define an
    # event); the first non-flush-free iterate of ANY feasibility is kept as
    # `acquisition_any_feas` for completeness.
    def mk_event(k, sp, tr, s_end):
        worst = min(sp['vrecs'], key=lambda q: q['cls'])
        r = {'type': worst['type'], 'i': worst['i'], 'j': worst['j']}
        return {'snapshot': k, 'n_snapshots': len(tr), 'tag': sp.get('tag'),
                's_at_event': sp['s'], 'feas_at_event': sp['feas'],
                'key': worst['k'], 'type': worst['type'],
                'i': worst['i'], 'j': worst['j'],
                'class_deg': worst['cls'], 'gap': worst['gap'],
                'all_keys': sp['viol'], 'n_simultaneous': len(sp['vrecs']),
                'all_categories': sorted({C.role_pair_category(
                    {'type': q['type'], 'i': q['i'], 'j': q['j']}, roles)
                    for q in sp['vrecs']}),
                'roles': ([C.role_of(roles, worst['i']),
                           C.role_of(roles, worst['j'])]
                          if worst['type'] == 'pair'
                          else [C.role_of(roles, worst['i'])]),
                'category': C.role_pair_category(r, roles),
                'mismatch_traj': key_class_traj(tr, r),
                's_traj_micro': [round(q['s'], 9) for q in tr],
                'continued_down': bool(s_end < sp['s'] - 1e-12),
                's_drop_after_event': float(sp['s'] - s_end)}

    def first_event(tr, s_end, need_feas):
        for k, sp in enumerate(tr):
            if sp['flush_free'] or not sp.get('vrecs'):
                continue
            if need_feas is None or sp['feas'] <= need_feas:
                return mk_event(k, sp, tr, s_end)
        return None

    # feasible-path micro-descent from the same start
    try:
        xm, sm, mtrace = micro_descent(x0)
    except Exception as exc:
        rec['micro_error'] = repr(exc)[:200]
        xm, sm, mtrace = None, None, []
    rec['micro'] = {'s_end': sm, 'n_points': len(mtrace),
                    'flush_free_at_end': (bool(mtrace[-1]['flush_free'])
                                          if mtrace else None),
                    's_start': mtrace[0]['s'] if mtrace else None}
    ev = first_event(mtrace, sm if sm is not None else sl, None) if mtrace \
        else None
    rec['acquisition'] = ev
    ev_fd = first_event(trace, sl, FEAS_EVENT)
    ev_any = first_event(trace, sl, None)
    rec['acquisition_fd'] = ({k: v for k, v in ev_fd.items()
                              if k not in ('mismatch_traj', 's_traj_micro')}
                             if ev_fd else None)
    rec['acquisition_any_feas'] = ({'snapshot': ev_any['snapshot'],
                                    'tag': ev_any['tag'], 'key': ev_any['key'],
                                    'category': ev_any['category'],
                                    's_at_event': ev_any['s_at_event'],
                                    'feas_at_event': ev_any['feas_at_event']}
                                   if ev_any else None)
    rec['outcome_b'] = bool(ev is not None or ev_fd is not None
                            or not fr['flush_free'])
    rec['flush_released'] = bool(rec['outcome_b'] and fr['flush_free'])

    # ---- (a) flush-free landing + CP-ish classification
    rec['outcome_a'] = False
    an = None
    if fr['flush_free']:
        try:
            an = D.analyse_landing(xl)
        except Exception as exc:
            rec['analyse_error'] = repr(exc)[:200]
        if an is not None:
            wit = D.descent_witness(xl, an['descent_dir'])
            lc, why = D.verdict(an['cls'], an['cp'], wit)
            rec['landing_class'] = lc
            rec['landing_class_why'] = why
            rec['landing_struct_class'] = an['cls']['class']
            rec['landing_rank'] = an['cls']['rank']
            rec['cp_evidence'] = an['cp']
            rec['descent_witness'] = wit
            rec['outcome_a'] = (lc != 'NOT-CP')
    if rec['outcome_a']:          # (a) is exclusive of (b), per the brief
        rec['outcome_b'] = False

    # ---- (c) rematch
    zl = [float(v) for v in D.a04_to_z(xl)]
    rec['landing_z'] = zl
    m = rematch_one(zl, sl)
    if m['family'] is not None:
        rec['outcome_c'] = True
        rec['family'] = '%s:%s' % (m['where'], m['family'])
        rec['family_why'] = m['why']
    else:
        rec['outcome_c'] = False
        rec['family'] = ('NEW-NONFLUSH-FREE' if not fr['flush_free']
                         else 'NEW-FLUSH-FREE')
        rec['family_why'] = m.get('nearest')
    rec['wall_secs'] = time.time() - t0
    if rec['outcome_a']:
        rec['candidate'] = True
    return rec, xl


# --------------------------------------------------------------- aggregate
def aggregate(records, tag):
    from collections import Counter
    agg = {'n_runs': len(records),
           'n_a_flushfree_candidate': sum(1 for r in records
                                          if r.get('outcome_a')),
           'n_a_flushfree_landing': sum(1 for r in records
                                        if r['landing_flush_free']),
           'n_b_flush_acquired': sum(1 for r in records if r['outcome_b']),
           'n_c_drain_to_known': sum(1 for r in records if r['outcome_c'])}
    per_seed = {}
    for r in records:
        d = per_seed.setdefault(r['seed'], {'n': 0, 'a': 0, 'b': 0, 'c': 0,
                                            'mode': r['mode'],
                                            'profile': r['profile'],
                                            's_min': float('inf'),
                                            'families': Counter()})
        d['n'] += 1
        d['a'] += bool(r.get('outcome_a'))
        d['b'] += bool(r['outcome_b'])
        d['c'] += bool(r['outcome_c'])
        d['s_min'] = min(d['s_min'], r['s_final'])
        d['families'][r['family']] += 1
    for d in per_seed.values():
        d['families'] = dict(d['families'])
    agg['per_seed'] = per_seed

    ev = [r['acquisition'] for r in records if r['acquisition']]
    cat = Counter(e['category'] for e in ev)
    bymode, byprof = {}, {}
    for r in records:
        e = r['acquisition']
        if not e:
            continue
        bymode.setdefault(r['mode'], Counter())[e['category']] += 1
        byprof.setdefault(r['profile'], Counter())[e['category']] += 1
    s_ev = sorted(e['s_at_event'] for e in ev)
    amap = {
        'n_events': len(ev),
        'by_category': dict(cat),
        'modal_category': cat.most_common(1)[0][0] if cat else None,
        'by_mode': {k: dict(v) for k, v in bymode.items()},
        'modal_by_mode': {k: v.most_common(1)[0][0] for k, v in bymode.items()},
        'by_profile': {k: dict(v) for k, v in byprof.items()},
        'modal_by_profile': {k: v.most_common(1)[0][0]
                             for k, v in byprof.items()},
        'median_s_at_acquisition': (s_ev[len(s_ev) // 2] if s_ev else None),
        'min_s_at_acquisition': (s_ev[0] if s_ev else None),
        'max_s_at_acquisition': (s_ev[-1] if s_ev else None),
        'acquired_at_snapshot0': sum(1 for e in ev if e['snapshot'] == 0),
        'by_stage_tag': dict(Counter(
            (e.get('tag') or '?').split('.')[-1][:6] for e in ev)),
        'by_outer_round': dict(Counter(
            (e.get('tag') or '?').split('.')[0] for e in ev)),
        'median_snapshot': sorted(e['snapshot'] for e in ev)[len(ev) // 2]
        if ev else None,
        'continued_down_after_event': sum(1 for e in ev
                                          if e['continued_down']),
        'by_role_pair': dict(Counter(
            '+'.join(sorted(e['roles'])) if len(e['roles']) == 2
            else e['roles'][0] + '+wall' for e in ev)),
    }
    agg['flush_acquisition_map'] = amap
    agg['s_final_min'] = min(r['s_final'] for r in records) if records else None
    agg['family_census'] = dict(Counter(r['family'] for r in records))
    agg['tag'] = tag
    return agg


# ------------------------------------------------------------------- main
def load_seeds():
    with open(os.path.join(C.RESULTS, 'seeds.json')) as f:
        return json.load(f)['seeds']


def control_seeds():
    """Task 4: 3 atlas VALLEY entries as seeds.  Full-precision sources: the
    A04 catalogue point for the numbered families (atlas_final's
    `canonical_sig` is rounded to 6 decimals, which alone costs ~2e-6 of s and
    would fake a descent witness), and the A37 drain record for A37-NEW-0."""
    out = []
    at = os.path.join(C.ATT, 'A37-cp-atlas', 'results', 'atlas_final.json')
    with open(at) as f:
        cls_of = {str(e['family_id']): e['class'] for e in json.load(f)
                  ['entries']}
    for fid in (27, 31):
        z, fam, ci = P.load_family(fid)
        out.append({'id': 'CTRL-%d' % fid, 'mode': 'control',
                    'profile': cls_of.get(str(fid), '?'), 'roles': None,
                    'x_a04': [float(v) for v in fam['best_x']],
                    'true_family': str(fid),
                    's_ref': float(fam['s_min'])})
    with open(os.path.join(C.ATT, 'A37-cp-atlas', 'results',
                           'drain.json')) as f:
        dr = json.load(f)
    for g in dr.get('new_families', []):
        if g['id'] != 'A37-NEW-0':
            continue
        out.append({'id': 'CTRL-A37-NEW-0', 'mode': 'control',
                    'profile': cls_of.get('A37-NEW-0', g.get('landing_class')),
                    'roles': None,
                    'x_a04': list(D.z_to_a04(g['z'])),
                    'true_family': 'A37-NEW-0', 's_ref': float(g['s'])})
    return out


def main():
    argv = sys.argv[1:]
    control = '--control' in argv
    fresh = '--fresh' in argv
    nrep = 20
    if '--reps' in argv:
        nrep = int(argv[argv.index('--reps') + 1])

    seeds = control_seeds() if control else load_seeds()
    tag = 'control' if control else 'hunt'
    ck = os.path.join(C.WORK, '%s_ckpt.json' % tag)
    logp = os.path.join(C.LOGS, 'hunt_log.txt')

    def log(msg):
        line = '[%s] %s' % (time.strftime('%H:%M:%S'), msg)
        print(line, flush=True)
        with open(logp, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

    jobs = []
    for sd in seeds:
        jobs.append((sd['id'], -1))
        for k in range(nrep):
            jobs.append((sd['id'], k))
    byid = {sd['id']: sd for sd in seeds}

    records = []
    done = set()
    if os.path.exists(ck) and not fresh:
        with open(ck) as f:
            records = json.load(f)['records']
        done = {(r['seed'], r['replica']) for r in records}
        log('%s: resumed from checkpoint, %d runs already done'
            % (tag, len(records)))

    refs()          # warm the reference sets once
    log('%s: refs built in %.1fs; %d jobs, nrep=%d'
        % (tag, refs()['secs'], len(jobs), nrep))

    t0 = time.time()
    for n, (sid, rep) in enumerate(jobs):
        if (sid, rep) in done:
            continue
        sd = byid[sid]
        x0 = np.array(sd['x_a04'], dtype=float)
        if rep >= 0:
            rng = np.random.default_rng(abs(hash((sid, rep))) % (2 ** 32))
            x0 = C.jitter(x0, rng)
        x0, _, _ = D.repair(x0)
        try:
            rec, _ = do_run(sid, rep, x0, sd.get('roles'), sd['mode'],
                            sd['profile'])
        except Exception as exc:
            log('  %s/%d FAILED %r' % (sid, rep, exc))
            continue
        if control:
            rec['true_family'] = sd.get('true_family')
            rec['s_ref'] = sd.get('s_ref')
        records.append(rec)
        log('  %-8s r%-3d s %.6f -> %.9f  ff=%s  acq=%s  fam=%s  (%.1fs)'
            % (sid, rep, rec['s0'], rec['s_final'],
               rec['landing_flush_free'],
               (rec['acquisition'] or {}).get('key', '-'),
               rec['family'], rec['wall_secs']))
        if len(records) % 25 == 0:
            with open(ck, 'w') as f:
                json.dump({'records': records}, f)
            log('  ... checkpoint %d runs, %.1f min elapsed'
                % (len(records), (time.time() - t0) / 60.0))
    with open(ck, 'w') as f:
        json.dump({'records': records}, f)

    agg = aggregate(records, tag)
    out = {'meta': {'attempt': 'A49-flushfree-hunt',
                    'task': 'free-descent census + flush-acquisition map'
                    if not control else 'negative control (atlas VALLEYs)',
                    'producer': 'attempts/A49-flushfree-hunt/code/hunt_a49.py',
                    'rigour': '[NUM] float64 -- hunt, no certificates',
                    'tol_f_deg': TOL_F, 'gap_tol': C.GAP_TOL,
                    'n_seeds': len(seeds), 'n_replicas': nrep,
                    'max_outer': MAX_OUTER,
                    'jitter': {'centres_sigma': 0.02, 'angles_sigma_deg': 0.3},
                    'wall_secs': time.time() - t0},
           'aggregate': agg, 'records': records}
    name = 'control.json' if control else 'hunt.json'
    with open(os.path.join(C.RESULTS, name), 'w') as f:
        json.dump(out, f, indent=1)
    log('%s: WROTE results/%s  %s' % (tag, name,
                                      json.dumps({k: v for k, v in agg.items()
                                                  if k in ('n_runs',
                                                           'n_a_flushfree_candidate',
                                                           'n_a_flushfree_landing',
                                                           'n_b_flush_acquired',
                                                           'n_c_drain_to_known',
                                                           's_final_min')})))
    return 0


if __name__ == '__main__':
    sys.exit(main())
