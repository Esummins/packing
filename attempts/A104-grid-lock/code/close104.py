r"""close104.py -- A104: the CLOSING ITERATION of Lemma ROT, and the empirical boundary m_lock.

T1  close the grid.  Start from polish12 (4.0000001) and floor-1e-4 (4.0000044) -- and, for context,
    every strictly K0-BLOCKED packing on disk.  Repeat Lemma ROT's own step: pick an UNHELD intruder
    (lock103's exact first-order test, imported VERBATIM from attempts/A103-noroom/code/lock103.py, no
    change to the test), move it along its unheld motion to its FIRST COLLISION (lock103's own bisected
    travel), re-canonicalise + re-inflate (A87's fjpolish87.canonical/inflate: the new contact rows are
    pinned at gap 1e-11, i.e. active at lock103's 1e-7 contact bar, and the side is re-read as the tight
    enclosing side + 2e-9), and re-run lock103.  Stop when (a) every intruder is HELD, (b) a corner drops
    below two meeters (a corner FREES -- the drain), or (c) the iteration stalls / hits the cap.

T2  the empirical boundary m_lock.  k0dir2_87's confined descent at floors 1e-3 and 1e-2, plus the corpus
    packings as seeds; the closing iteration of T1 at every endpoint; m_lock = the lowest side at which a
    packing HELD AT ALL EIGHT intruders appears.

Gordan certificate.  For a HELD intruder and each branch of the diagonal disjunctions, the multipliers
mu_k >= 0 (contact rows) and lambda_p >= 0 (virtual corner rows) with sum mu_k (n_k, tau_k) +
sum lambda_p g_p = 0, sum(mu) + sum(lambda) = 1 -- Gordan's alternative to the strict system of Lemma ROT.

One process, BLAS pinned, pure geometry + A87's SQP.  Writes only under attempts/A104-grid-lock/.
Usage: python close104.py {canary|t1|t2 [nseeds] [wall]|report}
"""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True          # do not touch A87/A103 __pycache__
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import random
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A104 = os.path.dirname(HERE)
ATT = os.path.dirname(A104)
ROOT = os.path.dirname(ATT)
RES = os.path.join(A104, 'results')
LOGS = os.path.join(A104, 'logs')
NOTES = os.path.join(A104, 'notes')
for _d in (RES, LOGS, NOTES):
    os.makedirs(_d, exist_ok=True)

sys.path.insert(0, os.path.join(ATT, 'A87-drain-flow', 'code'))
sys.path.insert(0, os.path.join(ATT, 'A103-noroom', 'code'))

import lock103 as L                # noqa: E402  (the held test, verbatim; never call L.log)
import fjpolish87 as F             # noqa: E402  (canonical / inflate / verify_exact)
import k0dir87 as K                # noqa: E402
import k0dir2_87 as D              # noqa: E402  (the confined descent + exact block certifier)
import t3lib as T                  # noqa: E402

MEET_TOL = L.MEET_TOL
CORNERS = L.CORNERS
MAX_ROUNDS = 25                    # outer rounds of the closing iteration
ROLL_STEPS = 160                   # Lemma-ROT steps per intruder per round
H_INIT = 1e-5                      # initial travel per ROT step
H_MAX = 3e-4
H_MIN = 1e-13
GAP_TARGET = 1e-11                 # the pinned contact gap (A87's GAP_FLOOR)
PROJ_IT = 10                       # Gauss-Newton projections per step
WALL_T1 = 180.0                    # per-packing closing budget, T1
WALL_T2 = 9.0                      # per-endpoint closing budget, T2

T0 = time.time()
_LOGNAME = [os.path.join(LOGS, 'close104.log')]
_fh = [None]


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    if _fh[0] is None:
        _fh[0] = open(_LOGNAME[0], 'a', encoding='utf-8')
    _fh[0].write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh[0].flush()


# ==================================================================== z <-> poses

def z_of(poses, s):
    z = np.empty(34)
    for i, p in enumerate(poses):
        z[3 * i], z[3 * i + 1], z[3 * i + 2] = p
    z[33] = float(s)
    return z


def poses_of(z):
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(11)]


def normalise(poses, s):
    """A87's canonical + inflate: an exact packing (all pair gaps >= 1e-11) with the side re-read as the
    tight enclosing side + 2*PAD.  Motions of size 1e-11 are far below lock103's 1e-7 contact bar, so
    every contact pinned by the closing step stays ACTIVE."""
    z = F.canonical(F.inflate(F.canonical(z_of(poses, s))))
    return poses_of(z), float(z[33])


# ==================================================================== Gordan certificate

def gordan_multipliers(A_rows, G_rows):
    """Non-trivial non-negative (mu, lambda) with sum mu_k a_k + sum lambda_p g_p = 0, sum = 1.
    Exists iff the strict system <a_k, y> > 0, <g_p, y> > 0 is infeasible (Gordan)."""
    M = np.array(list(A_rows) + list(G_rows), float)   # (n, 3)
    n = len(M)
    if n == 0:
        return None
    A_eq = np.vstack([M.T, np.ones((1, n))])           # 3 equalities + normalisation
    b_eq = np.array([0.0, 0.0, 0.0, 1.0])
    res = linprog(c=np.zeros(n), A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * n, method='highs')
    if res.status != 0:
        return None
    w = np.array(res.x, float)
    return {'mu': [float(v) for v in w[:len(A_rows)]],
            'lam': [float(v) for v in w[len(A_rows):]],
            'lam_total': float(w[len(A_rows):].sum()),
            'residual': float(np.abs(M.T @ w).max())}


def certify_intruder(poses, s, cn, i):
    """Per-branch Gordan multipliers for a HELD intruder (one branch per choice of diagonal disjunct)."""
    import itertools
    P = poses[i]
    C = L.contacts_of(poses, i, s)
    A_rows = []
    for c in C:
        rx, ry = c['point'][0] - P[0], c['point'][1] - P[1]
        A_rows.append((c['F'][0], c['F'][1], rx * c['F'][1] - ry * c['F'][0]))
    mu, d, vr = L.virtual_rows(P, cn, s)
    choices = [x['rows'] for x in vr]
    out = []
    for combo in itertools.product(*[range(len(ch)) for ch in choices]):
        G = [choices[k][j] for k, j in enumerate(combo)]
        g = gordan_multipliers(A_rows, G)
        out.append({'branch': list(combo), 'cert': g})
    return {'corner': cn, 'square': i, 'depth': d,
            'tilt_deg': math.degrees(P[2]) % 90.0,
            'n_contacts': len(C),
            'contacts': [{'with': c['with'], 'j': c['j'],
                          'point': [round(v, 12) for v in c['point']],
                          'F': [round(v, 12) for v in c['F']],
                          'gap': float('%.3e' % c['gap'])} for c in C],
            'n_sq_contacts': sum(1 for c in C if c['j'] is not None),
            'n_wall_contacts': sum(1 for c in C if c['j'] is None),
            'contact_rows': [[float(v) for v in r] for r in A_rows],
            'virtual_rows': [{'p_frame': [float(v) for v in x['p_frame']], 'kind': x['kind'],
                              'rows': [[float(v) for v in r] for r in x['rows']]} for x in vr],
            'branches': out,
            'all_branches_certified': all(b['cert'] is not None and b['cert']['residual'] < 1e-8
                                          for b in out)}


def contact_graph(poses, s):
    edges = set()
    walls = []
    for i in range(len(poses)):
        for c in L.contacts_of(poses, i, s):
            if c['j'] is None:
                walls.append((i, c['with']))
            else:
                edges.add((min(i, c['j']), max(i, c['j'])))
    return {'square_edges': sorted(edges),
            'wall_contacts': sorted(set(walls)),
            'n_square_edges': len(edges), 'n_wall_contacts': len(set(walls))}


# ==================================================================== the closing iteration

def _rows_at(poses, i, pose, s, tol):
    """Contact rows of square i at `pose` (everything else fixed), with their gap values:
    row = (n_x, n_y, tau) = d(gap)/d(c_x, c_y, theta), exactly lock103's contact row."""
    tmp = list(poses)
    tmp[i] = pose
    C = L.contacts_of(tmp, i, s, tol=tol)
    rows, vals = [], []
    for c in C:
        rx, ry = c['point'][0] - pose[0], c['point'][1] - pose[1]
        rows.append((c['F'][0], c['F'][1], rx * c['F'][1] - ry * c['F'][0]))
        vals.append(c['gap'] if c['j'] is not None else c['dist'])
    return np.array(rows, float).reshape(len(rows), 3), np.array(vals, float)


PROJ_TOL = 5e-3           # capture radius for the rows the projection may have to lift


def project_pose(poses, i, pose, s):
    """Re-polish with the contact rows pinned: least-norm Gauss-Newton correction of square i's own
    three coordinates lifting every violated separation/wall row back to the contact gap 1e-11.
    Only square i moves, so the rest of the packing is untouched and the step stays a single-square
    rigid motion in the sense of Lemma ROT."""
    pose = np.array(pose, float)
    for _ in range(PROJ_IT):
        M, v = _rows_at(poses, i, tuple(pose), s, tol=PROJ_TOL)
        if not len(v) or v.min() >= GAP_TARGET:
            break
        bad = v < GAP_TARGET
        try:
            d, *_ = np.linalg.lstsq(M[bad], (GAP_TARGET - v[bad]), rcond=1e-12)
        except np.linalg.LinAlgError:
            return None
        if not np.all(np.isfinite(d)) or np.max(np.abs(d)) > 0.05:
            return None
        pose = pose + d
    return tuple(pose) if L.worst_gap_one(poses, i, tuple(pose), s) >= 0.0 else None


def fast_dir(poses, s, cn, i):
    """The Lemma ROT direction, assembled from lock103's own pieces (contacts_of, virtual_rows,
    lp_strict) without its ROOM bisection -- the roll only needs a descent direction; the HELD/UNHELD
    verdict itself is always lock103's test_intruder / test_packing, unchanged."""
    import itertools
    P = poses[i]
    C = L.contacts_of(poses, i, s)
    A_rows = []
    for c in C:
        rx, ry = c['point'][0] - P[0], c['point'][1] - P[1]
        A_rows.append((c['F'][0], c['F'][1], rx * c['F'][1] - ry * c['F'][0]))
    mu, d, vr = L.virtual_rows(P, cn, s)
    choices = [x['rows'] for x in vr]
    best = (-1.0, np.zeros(3))
    for combo in itertools.product(*[range(len(ch)) for ch in choices]):
        G = [choices[k][j] for k, j in enumerate(combo)]
        t, y = L.lp_strict(A_rows, G)
        if t > best[0]:
            best = (t, y)
    return best[0], np.asarray(best[1], float), d


def roll_intruder(poses, s, cn, i, deadline, nsteps=ROLL_STEPS):
    """Lemma ROT's own step, iterated on ONE intruder: LP direction (lock103's test, verbatim) ->
    travel to the first collision -> pin the new contact rows and re-polish -> repeat.  Stops when the
    intruder is HELD, leaves its cell, jams (no admissible strictly-decreasing step remains) or the
    budget runs out."""
    h = H_INIT
    total = 0.0
    nmoved = 0
    d0 = None
    why = 'cap'
    for _ in range(nsteps):
        if time.time() > deadline:
            why = 'timeout'
            break
        t, y, dcur = fast_dir(poses, s, cn, i)
        if d0 is None:
            d0 = dcur
        if dcur <= MEET_TOL:
            why = 'exited'
            break
        if t <= L.TSTRICT:
            why = 'held' if L.test_intruder(poses, s, cn, i)['held'] else 'jammed'
            break
        P = poses[i]
        ok = False
        while h >= H_MIN:
            cand = project_pose(poses, i, (P[0] + h * y[0], P[1] + h * y[1], P[2] + h * y[2]), s)
            if cand is not None and L.corner_depth(cand, cn, s) < dcur - 1e-16:
                poses = list(poses)
                poses[i] = cand
                total += h
                nmoved += 1
                h = min(H_MAX, h * 1.6)
                ok = True
                break
            h *= 0.35
        if not ok:
            why = 'jammed'
            break
    dend = L.corner_depth(poses[i], cn, s)
    return poses, {'corner': cn, 'square': i, 'why': why, 'n_moves': nmoved,
                   'travel': total, 'depth_before': d0, 'depth_after': dend,
                   'retraction_fraction': (float((d0 - dend) / d0) if d0 else None),
                   'exits_cell': bool(dend <= MEET_TOL)}


def close_packing(poses, s, tag='x', wall=WALL_T2, max_rounds=MAX_ROUNDS, verbose=False):
    """The closing iteration.  Outcome in {fully_held, corner_freed, stalled, timeout, cap}."""
    poses, s = normalise(list(poses), s)
    s0 = s
    t0 = time.time()
    deadline = t0 + wall
    rounds = []
    outcome = 'cap'
    o = None
    for rnd in range(max_rounds):
        o = L.test_packing(tag, poses, s)
        if not o['K0_BLOCKED']:
            outcome = 'corner_freed'
            break
        if o['all_held']:
            outcome = 'fully_held'
            break
        if time.time() > deadline:
            outcome = 'timeout'
            break
        # Order: SHALLOWEST unheld intruder first.  A corner frees exactly when one of its meeters
        # leaves its cell, and A102/A103's dichotomy lives on the SECOND meeter, so the shallow ones
        # decide the outcome; the deep first meeters (a whole square sitting in the corner cell) would
        # need a retraction of order 1 and only consume budget.  The verdict itself is order-free:
        # 'fully held' needs every intruder held, 'corner freed' needs any one meeter out.
        unheld = sorted([q for q in o['rows'] if not q['held']], key=lambda q: q['depth'])
        moves = []
        for k, r in enumerate(unheld):
            share = (deadline - time.time()) / max(1, len(unheld) - k)
            poses, m = roll_intruder(poses, s, r['corner'], r['square'],
                                     min(deadline, time.time() + max(0.05, share)))
            m['lp_t'] = r['lp_t']
            m['free_by'] = r['free_by']
            moves.append(m)
            if time.time() > deadline:
                break
        poses, s = normalise(poses, s)
        nmv = sum(m['n_moves'] for m in moves)
        rounds.append({'round': rnd, 'n_unheld': o['n_unheld'], 'side': s,
                       'n_moves': nmv, 'moves': moves})
        if verbose:
            log('    round %2d  unheld %d  moves %d  side %.10f  [%s]'
                % (rnd, o['n_unheld'], nmv,
                   s, ' '.join('%s%d:%s/%.1e' % (m['corner'], m['square'], m['why'], m['travel'])
                               for m in moves)))
        if nmv == 0:
            outcome = 'stalled'
            o = L.test_packing(tag, poses, s)
            if not o['K0_BLOCKED']:
                outcome = 'corner_freed'
            elif o['all_held']:
                outcome = 'fully_held'
            break
    rec = {'tag': tag, 'outcome': outcome, 'side_start': s0, 'side_end': s,
           'n_rounds': len(rounds), 'n_steps': sum(r['n_moves'] for r in rounds),
           'rounds': rounds, 'secs': time.time() - t0,
           'final': {k: o[k] for k in ('n_intruders', 'n_held', 'n_unheld', 'meet_counts',
                                       'K0_BLOCKED', 'all_held', 'unheld')} if o else None,
           'poses': [[float(v) for v in p] for p in poses]}
    return rec, poses, s, o


def exact_certify(poses, s, delta_meet=1e-9):
    """A87's exact certifier: rational z, interval SAT gaps and side upper bound (fjpolish87.verify_exact)
    and the certified per-corner meeter count at the meet bar (k0dir2_87.exact_blocked_test_d)."""
    z = F.canonical(z_of(poses, s))
    zf = K.zfrac_of(z)
    ver = F.verify_exact(zf)
    try:
        tel = D.exact_blocked_test_d(zf, delta_meet)
    except Exception as e:                                     # pragma: no cover
        tel = {'error': repr(e)}
    return {'side_upper_bound': ver['side_upper_bound'],
            'min_pair_gap_lower_bound': ver['min_pair_gap_lower_bound'],
            'disjoint_certified': ver['disjoint_certified'],
            'exact_n_meet': tel.get('n_meet_certified'),
            'exact_unknown': tel.get('n_unknown_per_corner'),
            'exact_d1': tel.get('d1_per_corner'),
            'exact_d2': tel.get('d2_per_corner'),
            'K0_BLOCKED_certified': tel.get('K0_BLOCKED_certified'),
            'z_exact': [T.frac_str(v) for v in zf]}


def full_certificate(poses, s, tag):
    o = L.test_packing(tag, poses, s)
    certs = []
    for cn in CORNERS:
        for (i, d) in L.meeters(poses, s, cn):
            certs.append(certify_intruder(poses, s, cn, i))
    return {'tag': tag, 'side': s, 'lock': {k: o[k] for k in
                                            ('n_intruders', 'n_held', 'n_unheld', 'meet_counts',
                                             'K0_BLOCKED', 'all_held', 'unheld')},
            'contact_graph': contact_graph(poses, s),
            'intruders': certs,
            'poses': [[float(v) for v in p] for p in poses],
            'exact': exact_certify(poses, s)}


# ==================================================================== canary

def canary():
    C = L.load_corpus()
    t = [c for c in C if c['name'] == 'TRUMP_canary'][0]
    o = L.test_packing('TRUMP_canary', t['poses'], t['side'])
    ok = (o['n_intruders'] == 5 and o['n_held'] == 5 and o['n_unheld'] == 0
          and not o['K0_BLOCKED'])
    log('CANARY Trump: side %.12f  intruders %d  held %d  unheld %d  K0_BLOCKED %s  ->  %s'
        % (t['side'], o['n_intruders'], o['n_held'], o['n_unheld'], o['K0_BLOCKED'],
           'PASS' if ok else 'FAIL'))
    return ok, {'side': t['side'], 'n_intruders': o['n_intruders'], 'n_held': o['n_held'],
                'n_unheld': o['n_unheld'], 'K0_BLOCKED': o['K0_BLOCKED'],
                'meet_counts': o['meet_counts'], 'pass': bool(ok)}


# ==================================================================== T1

T1_PRIMARY = ('polish12_s0380', 'floor_1e-04_d1em04_s0202')


def t1(wall=1500.0):
    t0 = time.time()
    C = [c for c in L.load_corpus() if c['name'] != 'TRUMP_canary']
    order = [c for c in C if c['name'] in T1_PRIMARY] + [c for c in C if c['name'] not in T1_PRIMARY]
    out = []
    jl = open(os.path.join(RES, 't1_close.jsonl'), 'w', encoding='utf-8')
    for c in order:
        if time.time() - t0 > wall:
            log('T1 wall cap reached; %d packings not closed' % (len(order) - len(out)))
            break
        tt = time.time()
        log('T1 closing %-28s side %.9f' % (c['name'], c['side']))
        rec, poses, s, o = close_packing(c['poses'], c['side'], tag=c['name'],
                                         wall=WALL_T1, verbose=True)
        rec['side_orig'] = c['side']
        rec['secs'] = time.time() - tt
        if rec['outcome'] == 'fully_held':
            rec['certificate'] = full_certificate(poses, s, c['name'] + '_closed')
        else:
            rec['exact'] = exact_certify(poses, s)
        out.append(rec)
        jl.write(json.dumps(rec) + '\n')
        jl.flush()
        log('  -> %-13s side %.9f (from %.9f) steps %d  [%.1fs]'
            % (rec['outcome'], rec['side_end'], rec['side_orig'], rec['n_steps'], rec['secs']))
        if rec['outcome'] == 'corner_freed':
            log('     freed: meet_counts %s' % rec['final']['meet_counts'])
    jl.close()
    summ = {'n': len(out),
            'fully_held': [r['tag'] for r in out if r['outcome'] == 'fully_held'],
            'corner_freed': [r['tag'] for r in out if r['outcome'] == 'corner_freed'],
            'stalled': [r['tag'] for r in out if r['outcome'] in ('stalled', 'cap')],
            'per_packing': [{'tag': r['tag'], 'side_orig': r['side_orig'],
                             'side_end': r['side_end'], 'outcome': r['outcome'],
                             'n_steps': r['n_steps'],
                             'n_unheld_end': r['final']['n_unheld'] if r['final'] else None,
                             'meet_counts_end': r['final']['meet_counts'] if r['final'] else None}
                            for r in out]}
    json.dump(summ, open(os.path.join(RES, 't1_close.json'), 'w', encoding='utf-8'), indent=1)
    log('T1 summary: %s' % json.dumps({k: v for k, v in summ.items() if k != 'per_packing'}))
    return summ


# ==================================================================== T2

def corpus_seed_xs():
    """The corpus packings as descent seeds (the four floor records, the 3.985 record, the four
    polish and the three anchored A87 packings)."""
    out = []
    for c in L.load_corpus():
        if c['name'] == 'TRUMP_canary':
            continue
        out.append((c['name'], K.z_to_x(z_of(c['poses'], c['side']))))
    return out


def t2(nseeds=200, wall=6000.0, seed=20260905):
    t_start = time.time()
    rng = random.Random(seed)
    jl = open(os.path.join(RES, 't2_endpoints.jsonl'), 'w', encoding='utf-8')
    allrec = []
    per_floor = {}
    for delta in (1e-3, 1e-2):
        tf = time.time()
        budget = (wall - (time.time() - t_start)) * (0.5 if delta == 1e-3 else 1.0)
        sub = D.pool_for(delta, rng, log)
        recs = []
        # (a) the corpus seeds, closed at their own endpoints of the confined descent
        seeds = [('corpus:' + n, x) for n, x in corpus_seed_xs()]
        nsd = 0
        for (tag, x0) in seeds:
            if time.time() - tf > budget:
                break
            r = _t2_one(tag, delta, x0=x0)
            recs.append(r); allrec.append(r); jl.write(json.dumps(r) + '\n'); jl.flush()
            nsd += 1
        # (b) fresh random seeds
        k = 0
        while k < nseeds and time.time() - tf < budget:
            k += 1
            r = _t2_one('rnd%04d' % k, delta, sub=sub, rng=rng)
            recs.append(r); allrec.append(r); jl.write(json.dumps(r) + '\n'); jl.flush()
            if k % 20 == 0:
                fh = [q for q in recs if q.get('outcome') == 'fully_held']
                log('  floor %.0e: %d seeds, %d endpoints, %d fully_held (min side %s)  [%.0fs]'
                    % (delta, k, sum(1 for q in recs if q.get('endpoint_side')), len(fh),
                       ('%.9f' % min(q['side_end'] for q in fh)) if fh else '-',
                       time.time() - tf))
        per_floor[('%.0e' % delta)] = _floor_summary(delta, recs, time.time() - tf)
        log('floor %.0e done: %s' % (delta, json.dumps(per_floor['%.0e' % delta])))
    jl.close()
    held = [r for r in allrec if r.get('outcome') == 'fully_held']
    m_lock = min((r['side_end'] for r in held), default=None)
    best = min(held, key=lambda r: r['side_end']) if held else None
    summ = {'nseeds_requested': nseeds, 'wall': wall, 'per_floor': per_floor,
            'n_records': len(allrec),
            'm_lock': m_lock,
            'm_lock_tag': best['tag'] if best else None,
            'held_sides': sorted(r['side_end'] for r in held)[:40]}
    if best is not None:
        summ['m_lock_certificate'] = best.get('certificate')
    json.dump(summ, open(os.path.join(RES, 't2_mlock.json'), 'w', encoding='utf-8'), indent=1)
    log('T2 summary: m_lock = %s' % m_lock)
    return summ


def _floor_summary(delta, recs, secs):
    ep = [r for r in recs if r.get('endpoint_side') is not None]
    fh = [r for r in ep if r['outcome'] == 'fully_held']
    cf = [r for r in ep if r['outcome'] == 'corner_freed']
    st = [r for r in ep if r['outcome'] in ('stalled', 'cap')]
    return {'delta': delta, 'secs': round(secs, 1), 'n_seeds': len(recs), 'n_endpoints': len(ep),
            'n_fully_held': len(fh), 'n_corner_freed': len(cf), 'n_stalled': len(st),
            'frac_fully_held': (len(fh) / len(ep)) if ep else None,
            'frac_corner_freed': (len(cf) / len(ep)) if ep else None,
            'm_lock': min((r['side_end'] for r in fh), default=None),
            'min_endpoint_side': min((r['endpoint_side'] for r in ep), default=None),
            'min_freed_side': min((r['side_end'] for r in cf), default=None)}


def _t2_one(tag, delta, sub=None, rng=None, x0=None):
    t0 = time.time()
    rec = {'tag': tag, 'delta': delta}
    try:
        if x0 is None:
            for _ in range(40):
                x0 = D.build_seed_d(rng, sub, delta)
                if x0 is not None:
                    break
            if x0 is None:
                rec['outcome'] = 'seed_failed'
                rec['secs'] = time.time() - t0
                return rec
        # k0dir2_87's CONFINED descent, verbatim
        xc, best_c, _em, nc = D.sqp_flow_d(x0, delta, True, D.ROUNDS_CONF)
        xb = best_c[1] if best_c else xc
        if xb is None or not D.is_blocked_d(xb, delta):
            rec['outcome'] = 'no_blocked_endpoint'
            rec['secs'] = time.time() - t0
            return rec
        rec['confined_steps'] = nc
        z = K.x_to_z(xb)
        poses, s = poses_of(z), float(z[33])
        rec['endpoint_side'] = float(K.enclosing_side_x(xb))
        cr, cposes, cs, o = close_packing(poses, s, tag=tag, wall=WALL_T2)
        rec['outcome'] = cr['outcome']
        rec['side_start'] = cr['side_start']
        rec['side_end'] = cr['side_end']
        rec['n_steps'] = cr['n_steps']
        rec['n_unheld_end'] = cr['final']['n_unheld'] if cr['final'] else None
        rec['meet_counts_end'] = cr['final']['meet_counts'] if cr['final'] else None
        rec['n_rounds'] = cr['n_rounds']
        rec['rounds'] = cr['rounds']
        if cr['outcome'] == 'fully_held':
            rec['certificate'] = full_certificate(cposes, cs, tag + '_closed')
            rec['poses'] = cr['poses']
    except Exception as e:                                       # pragma: no cover
        rec['outcome'] = 'error'
        rec['error'] = repr(e)
    rec['secs'] = time.time() - t0
    return rec


# ==================================================================== main

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'canary'
    if cmd == 'canary':
        ok, _ = canary()
        sys.exit(0 if ok else 1)
    elif cmd == 't1':
        ok, cinfo = canary()
        if not ok:
            log('CANARY FAIL -- abort')
            sys.exit(1)
        s = t1(wall=float(sys.argv[2]) if len(sys.argv) > 2 else 1500.0)
        s['canary'] = cinfo
        json.dump(s, open(os.path.join(RES, 't1_close.json'), 'w', encoding='utf-8'), indent=1)
    elif cmd == 't2':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 200
        w = float(sys.argv[3]) if len(sys.argv) > 3 else 6000.0
        ok, cinfo = canary()
        if not ok:
            log('CANARY FAIL -- abort')
            sys.exit(1)
        s = t2(nseeds=n, wall=w)
        s['canary'] = cinfo
        ok2, cinfo2 = canary()
        s['canary_after'] = cinfo2
        json.dump(s, open(os.path.join(RES, 't2_mlock.json'), 'w', encoding='utf-8'), indent=1)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
