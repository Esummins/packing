"""m4_cascade.py -- A35 / M4: escape CASCADE tree sampling from Trump's jam.

[NUM] EVERYWHERE.  Float64 predictor-corrector path following along the
escape strata of z-hat, with event detection, branching and termination
taxonomy per notes/theory.md (C).  Rigour is M2/M3's job.

Work queue: the 81 survivors of M1 (results/m1_strata.json,
synthesis.global_exhaustive.survivors).

Route model
-----------
A SEGMENT is one maximal arc on a fixed contact set with a fixed continuation
branch.  A ROUTE is a root-to-leaf path in the segment tree.  Segments carry:
  B          broken rows (subset of the 38 geometric rows), inequality >= 0
  gained     list of extra 'edge' rows maintained at 0 (gained contacts)
  z0, v0     entry point and entry tangent
Events (theory (C)):
  E1  gained contact  (a non-contact pair's SAT gap hits 0)           -> BRANCH
  E2  broken row re-closes (g_b returns to 0)                          -> BRANCH
  E3  wedge (no feasible continuation direction)                       -> stop
  E4  rank change along the route ([NUM] spectral gap)                 -> record
Terminations:
  MARGIN  s >= s_hat + DELTA_STOP        REJAM   dof -> 0
  SLACK   all 18 pair rows broken and min pair gap > 0.005
  TRAVEL  ||z - z_hat||_inf > 0.05       DEPTH / STEPS / BLOCKED / FAIL
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import strata_lib as SL          # noqa: E402
import m4_geom as G              # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
NV = G.NV
S_IDX = G.S_IDX

# ------------------------------------------------------------------ parameters
RANK_TOL = 1e-8          # relative singular-value cut for kernel
PROJ_TOL = 1e-11         # Newton projection residual (inf norm)
PROJ_ITERS = 12
FEAS_TOL = 1e-9          # allowed negativity on any inequality
EV_EPS = 1e-9            # "was positive" threshold for crossing detection
BISECT_TOL = 1e-11
H0 = 1.5e-3
HMIN = 1e-7
HMAX = 6e-3
DELTA_STOP = 1e-3        # MARGIN: s_hat + 1e-3
DELTA_REC = 1e-4         # recorded first crossing
TRAVEL_CAP = 0.05
SLACK_GAP = 5e-3
MAX_DEPTH = 6
MAX_STEPS = 500
N_RAYS = 8
ALARM_TOL = 1e-12

CORR_MAX = 2.0        # corrector displacement <= CORR_MAX * h
BRANCH_JUMP = 1e-5    # re-projection at a branch must not move the point
N_K3_SAMPLE = 1200
N_K3_KEEP = 500
MAX_SEGMENTS = 24000
TIME_BUDGET = 105 * 60.0
CKPT_EVERY = 90.0


# ------------------------------------------------------------------ static data
REPAIR_DIST = os.environ.get('M4_REPAIR_DIST', '0') == '1'
CONS = SL.geo_constraints()
if REPAIR_DIST:
    # A22's two 'dist' rows (|c_i-c_j|^2 >= 1) are a WEAK surrogate: holding
    # them at 0 does NOT hold the contact, and the squares interpenetrate as
    # soon as anything rotates.  Replace them by the TRUE SAT contact row.
    for _k, _c in enumerate(CONS):
        if _c['kind'] == 'dist':
            CONS[_k] = {'kind': 'sat', 'i': _c['i'], 'j': _c['j'],
                        'name': 'S%d-%d' % (_c['i'], _c['j'])}
NGEO = len(CONS)
ROW_NAMES = [c['name'] for c in CONS]
ZHAT = np.array([float(x) for x in SL.z_hat()])
S_HAT = float(ZHAT[S_IDX])
CONTACT_PAIRS = set(SL.contact_pairs())
NONCONTACT_PAIRS = [p for p in G.ALL_PAIRS if p not in CONTACT_PAIRS]
PAIR_ROWS = [k for k, c in enumerate(CONS)
             if c['kind'] in ('edge', 'dist', 'sat')]
M1_CANDIDATES = {(6, 7), (8, 9), (3, 4), (7, 10)}
# pairs already touching at z-hat but NOT represented by any of the 38 rows
_g0, _ = G.sat_all(ZHAT)
TOUCHING_EXTRA = [p for p in NONCONTACT_PAIRS if _g0[p[0], p[1]] < 1e-9]


# ------------------------------------------------------------------ core numerics

def project(z, M, iters=PROJ_ITERS):
    """Gauss-Newton projection onto {g_m = 0, m in M}.  Returns (z, resid, ok)."""
    z = z.copy()
    res = np.inf
    for _ in range(iters):
        f = G.rows_val(z, M)
        res = float(np.abs(f).max()) if len(f) else 0.0
        if res < PROJ_TOL:
            return z, res, True
        A = G.rows_jac(z, M)
        dz, *_ = np.linalg.lstsq(A, -f, rcond=None)
        if not np.all(np.isfinite(dz)):
            return z, res, False
        nz = float(np.abs(dz).max())
        if nz > 0.25:
            dz *= 0.25 / nz
        z = z + dz
    f = G.rows_val(z, M)
    res = float(np.abs(f).max()) if len(f) else 0.0
    return z, res, res < 1e-9


def kernel(z, M):
    """(kernel basis rows K [d x 34], dof, spectral gap)."""
    if not M:
        return np.eye(NV), NV, (0.0, 0.0)
    A = G.rows_jac(z, M)
    sv = np.linalg.svd(A, compute_uv=False)
    _, s2, Vt = np.linalg.svd(A)
    smax = sv[0] if len(sv) else 1.0
    r = int((sv > RANK_TOL * max(smax, 1.0)).sum())
    d = NV - r
    kept = float(sv[r - 1]) if r > 0 else float('inf')
    dropped = float(sv[r]) if r < len(sv) else 0.0
    return Vt[r:], d, (kept, dropped)


def admissible(K, Aact, nrays, prefer=None, rng=None):
    """Rays v in row-space(K) with Aact.v >= 0.  Returns list of unit vectors."""
    d = K.shape[0]
    if d == 0:
        return []
    Mk = (Aact @ K.T) if len(Aact) else np.zeros((0, d))
    out = []

    def push(c):
        if not np.all(np.isfinite(c)):
            return
        n = np.linalg.norm(c)
        if n < 1e-9:
            return
        v = (c / n) @ K
        nv = np.linalg.norm(v)
        if nv < 1e-12:
            return
        v = v / nv
        for w in out:
            if abs(float(w @ v)) > 1 - 1e-6:
                return
        out.append(v)

    if Mk.shape[0] == 0:
        if d == 1:
            push(np.array([1.0])); push(np.array([-1.0]))
        else:
            if prefer is not None:
                push(K @ prefer)
            for _ in range(nrays):
                push(rng.standard_normal(d))
        return out

    objs = []
    if prefer is not None:
        objs.append(K @ prefer)
    if d == 1:
        objs += [np.array([1.0]), np.array([-1.0])]
    else:
        objs += [rng.standard_normal(d) for _ in range(nrays)]
    for r in objs:
        n = np.linalg.norm(r)
        if n < 1e-12:
            continue
        r = r / n
        try:
            sol = linprog(-r, A_ub=-Mk, b_ub=np.zeros(Mk.shape[0]),
                          bounds=[(-1, 1)] * d, method='highs')
        except Exception:
            continue
        if not sol.success:
            continue
        push(np.array(sol.x))
    return out


def build_M(B, gained):
    return [CONS[k] for k in range(NGEO) if k not in B] + list(gained)


ZERO_RATE = 1e-6


def refine(B, gained, z, v):
    """Move zero-rate broken rows back into the maintained set.

    An LP ray on the BOUNDARY of the escape cone leaves some broken gap at 0 to
    first order; the true route then lives on the smaller stratum B minus Z.  This
    both fixes the numerical sign slop of the LP vertex and identifies the
    stratum correctly.  Returns (B_eff, v_eff) or None if the ray dies.
    """
    B = set(B)
    for _ in range(8):
        if not B:
            return B, v
        idx = sorted(B)
        A = G.rows_jac(z, [CONS[b] for b in idx])
        rates = A @ v
        scale = max(1.0, float(np.abs(rates).max()))
        Z = {b for b, r in zip(idx, rates) if r <= ZERO_RATE * scale}
        if not Z:
            return B, v
        B = B - Z
        M = build_M(B, gained)
        K, d, _ = kernel(z, M)
        if d == 0:
            return None
        vv = K.T @ (K @ v)
        n = np.linalg.norm(vv)
        if n < 1e-8:
            return None
        v = vv / n
    return None


def wedge_test(z, B):
    """First-order escape cone {v in ker A_M : A_B v >= 0}.

    Returns (max_total_rate, dof).  The LP maximises  sum_b (grad g_b . v)
    over {v in ker A_M : A_B v >= 0, |coeffs| <= 1}.  Since rank(A) = 34,
    A_M v = 0 and A_B v = 0 force v = 0, so the cone is NONTRIVIAL iff the
    optimum is > 0.  Optimum = 0  <=>  WEDGED at first order, and then the
    closed stratum meets a neighbourhood of z-hat in {z-hat} only.
    """
    M = build_M(set(B), [])
    K, d, _ = kernel(z, M)
    if d == 0:
        return -1.0, 0
    A = G.rows_jac(z, [CONS[b] for b in sorted(B)])
    Mk = A @ K.T
    m, dd = Mk.shape
    r = linprog(-Mk.sum(axis=0), A_ub=-Mk, b_ub=np.zeros(m),
                bounds=[(-1, 1)] * dd, method='highs')
    if not r.success:
        return -1.0, d
    return float(-r.fun), d


# ------------------------------------------------------------------ the follower

class Cascade:
    def __init__(self, seed=20260827):
        self.rng = np.random.default_rng(seed)
        self.segments = []
        self.events = []
        self.seen = set()
        self.alarms = []
        self.rejams = []
        self.offlist_E1 = []
        self.branch_reason = {}
        self.t0 = time.time()
        self.stack = []
        self.next_id = 0

    # ------------------------------------------------------------------ helpers
    def dedupe_key(self, B, gained, v):
        gk = tuple(sorted((r['i'], r['j'], r['corner'], r['edge']) for r in gained))
        vh = tuple(np.round(v, 4))
        return (tuple(sorted(B)), gk, vh)

    def push(self, seg):
        k = self.dedupe_key(seg['B'], seg['gained'], seg['v0'])
        if k in self.seen:
            return False
        self.seen.add(k)
        seg['id'] = self.next_id
        self.next_id += 1
        self.stack.append(seg)
        return True

    # ------------------------------------------------------------------ follow
    def follow(self, seg):
        B = set(seg['B'])
        gained = list(seg['gained'])
        M = build_M(B, gained)
        z = seg['z0'].copy()
        v = seg['v0'].copy()
        broken_idx = sorted(B)

        rec = {'id': seg['id'], 'parent': seg['parent'], 'depth': seg['depth'],
               'root': seg['root'], 'B': broken_idx,
               'gained': [(r['i'], r['j'], r['corner'], r['edge']) for r in gained],
               'gained_pairs': sorted({tuple(sorted((r['i'], r['j'])))
                                       for r in gained}),
               'dof0': None, 'events': [], 'n_steps': 0,
               'arclen': 0.0, 's_start': float(z[S_IDX]), 's_end': None,
               's_min': float(z[S_IDX]), 's_max': float(z[S_IDX]),
               'travel_end': 0.0, 'termination': None,
               'dsdtau_obs': None, 'dsdtau_pred': float(v[S_IDX]),
               'dsdtau_min': None,
               'first_cross_1e4_arclen': None, 'rank_changes': 0}

        K, d, sg = kernel(z, M)
        rec['dof0'] = int(d)
        if d == 0:
            rec['termination'] = 'REJAM'
            self.record_rejam(z, B, gained, rec)
            self.segments.append(rec)
            return
        dof_prev = d
        gap, wit = G.sat_all(z)
        prev_pair = {p: float(gap[p[0], p[1]]) for p in NONCONTACT_PAIRS}
        prev_brk = {b: float(G.row_val(z, CONS[b])) for b in broken_idx}
        h = H0
        arclen = 0.0
        nsteps = 0
        z_prev_acc = z.copy()

        while True:
            if nsteps >= MAX_STEPS:
                rec['termination'] = 'STEPS'
                break
            if time.time() - self.t0 > TIME_BUDGET:
                rec['termination'] = 'TIMEOUT'
                break
            # ---------------- trial step
            ok = False
            while h >= HMIN:
                zp = z + h * v
                zt, res, pok = project(zp, M)
                # the corrector must stay a CORRECTION: a Gauss-Newton
                # excursion far from the predictor means the step was too big
                # and the arc was left (this is how a route can jump off the
                # feasible branch entirely).
                if pok and float(np.abs(zt - zp).max()) <= CORR_MAX * h:
                    ok = True
                    break
                h *= 0.4
            if not ok:
                rec['termination'] = 'PROJFAIL'
                break

            # ---------------- feasibility + events on [z, zt]
            ev = self.scan(z, zt, B, gained, prev_pair, prev_brk, M, h, v)
            if ev is not None:
                zt = ev['z']
                h_used = ev['h']
            else:
                h_used = h

            step = float(np.linalg.norm(zt - z))
            arclen += step
            nsteps += 1
            if step > 1e-12:
                rate = float((zt[S_IDX] - z[S_IDX]) / step)
                if rec['dsdtau_obs'] is None:
                    rec['dsdtau_obs'] = rate
                rec['dsdtau_min'] = (rate if rec['dsdtau_min'] is None
                                     else min(rec['dsdtau_min'], rate))
            z_prev_acc = z.copy()
            z = zt
            s = float(z[S_IDX])
            rec['s_min'] = min(rec['s_min'], s)
            rec['s_max'] = max(rec['s_max'], s)
            if rec['first_cross_1e4_arclen'] is None and s >= S_HAT + DELTA_REC:
                rec['first_cross_1e4_arclen'] = arclen
            if s < S_HAT - ALARM_TOL:
                self.alarms.append({'segment': seg['id'], 'B': broken_idx,
                                    'gained': rec['gained'], 's': s,
                                    'deficit': S_HAT - s, 'arclen': arclen,
                                    'z': z.tolist()})

            gap, wit = G.sat_all(z)
            prev_pair = {p: float(gap[p[0], p[1]]) for p in NONCONTACT_PAIRS}
            prev_brk = {b: float(G.row_val(z, CONS[b])) for b in sorted(B)}

            # ---------------- new tangent
            K, d, sg = kernel(z, M)
            if d != dof_prev:
                rec['rank_changes'] += 1
                rec['events'].append({'type': 'E4', 'arclen': arclen,
                                      'dof_from': int(dof_prev), 'dof_to': int(d),
                                      'sv_kept': sg[0], 'sv_dropped': sg[1]})
                dof_prev = d
            if d == 0:
                rec['termination'] = 'REJAM'
                self.record_rejam(z, B, gained, rec)
                break
            act = [b for b in sorted(B) if prev_brk[b] <= EV_EPS]
            Aact = (G.rows_jac(z, [CONS[b] for b in act]) if act
                    else np.zeros((0, NV)))
            vc = K @ v
            vn = K.T @ vc
            nn = np.linalg.norm(vn)
            newv = None
            if nn > 0.2 and (len(act) == 0 or np.all(Aact @ (vn / nn) >= -1e-8)):
                newv = vn / nn
            else:
                cand = admissible(K, Aact, 3, prefer=v, rng=self.rng)
                cand = [c for c in cand if float(c @ v) > 0.2]
                if cand:
                    newv = max(cand, key=lambda c: float(c @ v))
            if newv is None:
                rec['termination'] = 'WEDGE'
                rec['events'].append({'type': 'E3', 'arclen': arclen})
                break
            v = newv

            # ---------------- event branching
            if ev is not None:
                rec['events'].append({'type': ev['type'], 'arclen': arclen,
                                      'what': ev['what'], 's': s})
                if ev['type'] == 'BLOCK':
                    rec['termination'] = 'BLOCKED'
                    rec['branch_factor'] = 0
                    break
                self.branch(seg, rec, ev, z, v, B, gained, arclen)
                rec['termination'] = ('EVENT:' + ev['type']
                                      if rec.get('branch_factor')
                                      else 'EVENT:' + ev['type'] + '-dead')
                break
            if ev is None and h_used == h:
                h = min(HMAX, h * 1.4)

            # ---------------- terminations
            travel = float(np.abs(z - ZHAT).max())
            if s >= S_HAT + DELTA_STOP:
                rec['termination'] = 'MARGIN'
                break
            if travel > TRAVEL_CAP:
                rec['termination'] = 'TRAVEL'
                break
            if all(p in B for p in PAIR_ROWS):
                mg = float(min(gap[i, j] for (i, j) in G.ALL_PAIRS))
                if mg > SLACK_GAP:
                    rec['termination'] = 'SLACK'
                    break

        rec['n_steps'] = nsteps
        rec['arclen'] = arclen
        rec['s_end'] = float(z[S_IDX])
        rec['travel_end'] = float(np.abs(z - ZHAT).max())
        rec['s_gain'] = rec['s_end'] - rec['s_start']
        rec['z_end'] = z.tolist()
        if rec['termination'] is None:
            rec['termination'] = 'UNKNOWN'
        self.segments.append(rec)

    # ------------------------------------------------------------------ scanning
    def scan(self, z0, z1, B, gained, prev_pair, prev_brk, M, h, v):
        """Detect the FIRST event / feasibility violation on the step.

        Returns None or {'type','what','z','h'}.
        """
        gap1, _ = G.sat_all(z1)
        hits = []
        for p in G.ALL_PAIRS:
            # TRUE feasibility: no pair may overlap.  This also catches a
            # maintained A22 'edge' row whose dominance selection has flipped
            # (theory.md G5) -- the row still reads 0 while the squares
            # actually interpenetrate.
            if float(gap1[p[0], p[1]]) < -FEAS_TOL:
                hits.append(('BLOCK', ('overlap',) + p, lambda zz, p=p:
                             float(G.sat_all(zz)[0][p[0], p[1]]), -FEAS_TOL))
        for p in NONCONTACT_PAIRS:
            g1 = float(gap1[p[0], p[1]])
            g0 = prev_pair[p]
            if g0 > EV_EPS and g1 <= 0.0:
                hits.append(('E1', ('pair',) + p, lambda zz, p=p:
                             float(G.sat_all(zz)[0][p[0], p[1]]), 0.0))
            elif g0 <= EV_EPS and g1 < -FEAS_TOL:
                # already-touching pair being driven negative -> blocked
                hits.append(('BLOCK', ('pair',) + p, lambda zz, p=p:
                             float(G.sat_all(zz)[0][p[0], p[1]]), -FEAS_TOL))
        for b in sorted(B):
            v1 = float(G.row_val(z1, CONS[b]))
            if prev_brk[b] > EV_EPS and v1 <= 0.0:
                hits.append(('E2', ('row', b), lambda zz, b=b:
                             float(G.row_val(zz, CONS[b])), 0.0))
        c1 = G.containment_min(z1)
        if c1 < -FEAS_TOL:
            hits.append(('BLOCK', ('containment',), G.containment_min,
                         -FEAS_TOL))
        if not hits:
            return None
        # bisect on the earliest event
        best = None
        for typ, what, fn, thr in hits:
            lo, hi = 0.0, h
            zb = z1
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                zm, res, ok = project(z0 + mid * v, M)
                if not ok:
                    hi = mid
                    continue
                if fn(zm) > thr:
                    lo = mid
                else:
                    hi = mid
                    zb = zm
                if hi - lo < BISECT_TOL:
                    break
            if best is None or hi < best[0]:
                best = (hi, typ, what, zb)
        hh, typ, what, zb = best
        return {'type': typ, 'what': list(what), 'z': zb, 'h': hh}

    # ------------------------------------------------------------------ branching
    def _br(self, k):
        self.branch_reason[k] = self.branch_reason.get(k, 0) + 1

    def branch(self, seg, rec, ev, z, v, B, gained, arclen):
        if seg['depth'] + 1 > MAX_DEPTH:
            self._br('depth_cap')
            return
        typ = ev['type']
        kids = []
        if typ == 'E1':
            i, j = ev['what'][1], ev['what'][2]
            if (i, j) not in M1_CANDIDATES:
                trav = float(np.abs(z - ZHAT).max())
                self.offlist_E1.append({'segment': seg['id'], 'pair': [i, j],
                                        'travel': trav, 'arclen': arclen,
                                        's': float(z[S_IDX])})
            gap, wit = G.sat_all(z)
            o, e, k = G.sat_pair_witness(wit, i, j)
            p = j if o == i else i
            newrow = G.gained_row(o, e, k, p)
            # child A: maintain the new contact
            gained_A = gained + [newrow]
            M_A = build_M(B, gained_A)
            zA, res, ok = project(z.copy(), M_A)
            if not ok:
                self._br('E1_projfail')
            elif float(np.abs(zA - z).max()) >= BRANCH_JUMP:
                self._br('E1_jump')
                ok = False
            if ok:
                K, d, _ = kernel(zA, M_A)
                if d == 0:
                    self._br('E1_rejam')
                    self.record_rejam(zA, B, gained_A, rec, tag='branch')
                else:
                    n0 = len(kids)
                    act = [b for b in sorted(B)
                           if float(G.row_val(zA, CONS[b])) <= EV_EPS]
                    Aact = (G.rows_jac(zA, [CONS[b] for b in act]) if act
                            else np.zeros((0, NV)))
                    for c in admissible(K, Aact, 2, prefer=v, rng=self.rng):
                        if float(c @ v) <= 0.0:
                            continue
                        rf = refine(B, gained_A, zA, c)
                        if rf is None:
                            continue
                        kids.append((rf[0], gained_A, zA, rf[1]))
                    if len(kids) == n0:
                        self._br('E1_maintain_wedged')
                    else:
                        self._br('E1_maintain_ok')
            # child B: keep it broken (graze) if the direction reopens the gap
            gnew = G.rows_jac(z, [newrow])[0]
            if float(gnew @ v) > 1e-9:
                self._br('E1_graze')
                kids.append((set(B), list(gained), z.copy(), v.copy()))
        elif typ == 'E2':
            b = ev['what'][1]
            # child A: re-maintain the row
            B_A = set(B) - {b}
            M_A = build_M(B_A, gained)
            zA, res, ok = project(z.copy(), M_A)
            ok = ok and float(np.abs(zA - z).max()) < BRANCH_JUMP
            if ok:
                K, d, _ = kernel(zA, M_A)
                if d == 0:
                    self.record_rejam(zA, B_A, gained, rec, tag='branch')
                else:
                    act = [q for q in sorted(B_A)
                           if float(G.row_val(zA, CONS[q])) <= EV_EPS]
                    Aact = (G.rows_jac(zA, [CONS[q] for q in act]) if act
                            else np.zeros((0, NV)))
                    for c in admissible(K, Aact, 2, prefer=v, rng=self.rng):
                        if float(c @ v) <= 0.0:
                            continue
                        rf = refine(B_A, gained, zA, c)
                        if rf is None:
                            continue
                        kids.append((rf[0], list(gained), zA, rf[1]))
            # child B: keep broken
            gb = G.rows_jac(z, [CONS[b]])[0]
            if float(gb @ v) > 1e-9:
                kids.append((set(B), list(gained), z.copy(), v.copy()))
        rec['branch_factor'] = len(kids)
        for (Bc, gc, zc, vc) in kids:
            self.push({'B': set(Bc), 'gained': gc, 'z0': zc, 'v0': vc,
                       'depth': seg['depth'] + 1, 'parent': seg['id'],
                       'root': seg['root']})

    # ------------------------------------------------------------------ rejam
    def record_rejam(self, z, B, gained, rec, tag='route'):
        gap, _ = G.sat_all(z)
        act_pairs = sorted([list(p) for p in G.ALL_PAIRS
                            if gap[p[0], p[1]] < 1e-7])
        maintained = sorted(set(range(NGEO)) - set(B))
        # is e_s in cone{grad g_m : m maintained (incl. gained)}?  If yes the
        # point is a candidate LOCAL MIN of sigma on its stratum (a genuine new
        # jam); if no it is a rank-34 point that is not a minimiser.
        Mrows = build_M(set(B), gained)
        AM = G.rows_jac(z, Mrows)
        es = np.zeros(NV); es[S_IDX] = 1.0
        lp = linprog(np.zeros(AM.shape[0]), A_eq=AM.T, b_eq=es,
                     bounds=[(0, None)] * AM.shape[0], method='highs')
        cone_ok = bool(lp.success)
        lam_min = float(min(lp.x)) if lp.success else None
        # Chebyshev floor for the multiplier vector (the theory.md lambda_floor)
        floor = None
        if cone_ok:
            n = AM.shape[0]
            c = np.zeros(n + 1); c[-1] = -1.0
            Aeq = np.hstack([AM.T, np.zeros((NV, 1))])
            Aub = np.hstack([-np.eye(n), np.ones((n, 1))])
            r2 = linprog(c, A_ub=Aub, b_ub=np.zeros(n), A_eq=Aeq, b_eq=es,
                         bounds=[(0, None)] * n + [(None, 10)], method='highs')
            if r2.success:
                floor = float(r2.x[-1])
        self.rejams.append({
            'from_segment': rec['id'], 'tag': tag,
            'B': sorted(B),
            'maintained_rows': maintained,
            'gained': [(r['i'], r['j'], r['corner'], r['edge']) for r in gained],
            'sigma': float(z[S_IDX]),
            'sigma_minus_shat': float(z[S_IDX]) - S_HAT,
            'travel': float(np.abs(z - ZHAT).max()),
            'contact_pairs': act_pairs,
            'n_contact_pairs': len(act_pairs),
            'es_in_cone': cone_ok, 'lambda_min': lam_min,
            'lambda_floor': floor,
            'key': '%s|%s|%.9f' % (sorted(B),
                                   sorted((r['i'], r['j'], r['corner'],
                                           r['edge']) for r in gained),
                                   float(z[S_IDX])),
            'z': z.tolist()})

    # ------------------------------------------------------------------ driver
    def run(self, survivors, out_path, labels=None):
        # ---- seed the stack with root segments
        roots = []
        for si, Bl in enumerate(survivors):
            B = set(Bl)
            M = build_M(B, [])
            K, d, sg = kernel(ZHAT, M)
            Aact = G.rows_jac(ZHAT, [CONS[b] for b in sorted(B)])
            nr = N_RAYS if d >= 2 else 2
            rays = admissible(K, Aact, nr, rng=self.rng)
            # LP returns cone VERTICES (boundary rays, some gap rate = 0).
            # Add random positive mixtures to reach the cone's relative
            # interior, where ALL broken gaps open at first order.
            if len(rays) >= 2:
                for _ in range(N_RAYS):
                    w = self.rng.random(len(rays))
                    vv = np.tensordot(w, np.array(rays), axes=(0, 0))
                    n = np.linalg.norm(vv)
                    if n > 1e-9:
                        rays.append(vv / n)
            kept, kept_full = [], []
            for v in rays:
                rates = Aact @ v
                if float(rates.max()) <= 1e-9:
                    continue                 # does not open any broken gap
                rf = refine(B, [], ZHAT, v)
                if rf is None:
                    continue
                (kept_full if set(rf[0]) == set(B) else kept).append(
                    (rf[0], rf[1]))
            # prefer rays that genuinely open EVERY broken gap; fall back to
            # boundary rays (which live on a lower stratum) only if none exist
            degenerate = not kept_full
            kept = kept_full if kept_full else kept[:2]
            roots.append({'idx': si, 'B': sorted(Bl), 'dof': int(d),
                          'queue': (labels[si] if labels else '?'),
                          'n_rays': len(kept),
                          'sv_kept': sg[0], 'sv_dropped': sg[1],
                          'B_eff': [sorted(b) for b, _ in kept],
                          'cone_interior_empty': bool(degenerate),
                          'es_v': [float(v[S_IDX]) for _, v in kept]})
            for (Be, v) in kept:
                self.push({'B': set(Be), 'gained': [], 'z0': ZHAT.copy(),
                           'v0': v, 'depth': 0, 'parent': None, 'root': si})
        self.roots = roots

        last_ck = time.time()
        while self.stack:
            if len(self.segments) >= MAX_SEGMENTS:
                self.stop_reason = 'MAX_SEGMENTS'
                break
            if time.time() - self.t0 > TIME_BUDGET:
                self.stop_reason = 'TIME_BUDGET'
                break
            seg = self.stack.pop()
            self.follow(seg)
            if time.time() - last_ck > CKPT_EVERY:
                self.dump(out_path, partial=True)
                last_ck = time.time()
                print('  [ckpt] segments=%d stack=%d t=%.0fs'
                      % (len(self.segments), len(self.stack),
                         time.time() - self.t0), flush=True)
        else:
            self.stop_reason = 'EXHAUSTED'
        self.dump(out_path, partial=False)

    # ------------------------------------------------------------------ output
    def dump(self, path, partial):
        segs = self.segments
        from collections import Counter
        term = Counter(s['termination'] for s in segs)
        depth = Counter(s['depth'] for s in segs)
        bf = [s.get('branch_factor') for s in segs if 'branch_factor' in s]
        nev = [len([e for e in s['events'] if e['type'] in ('E1', 'E2')])
               for s in segs]
        leaves = [s for s in segs if not s['termination'].startswith('EVENT')]
        out = {
            'meta': {
                'partial': partial,
                'stop_reason': getattr(self, 'stop_reason', 'running'),
                'elapsed_s': time.time() - self.t0,
                's_hat': S_HAT,
                'params': {'H0': H0, 'HMAX': HMAX, 'RANK_TOL': RANK_TOL,
                           'PROJ_TOL': PROJ_TOL, 'TRAVEL_CAP': TRAVEL_CAP,
                           'DELTA_STOP': DELTA_STOP, 'MAX_DEPTH': MAX_DEPTH,
                           'MAX_STEPS': MAX_STEPS, 'N_RAYS': N_RAYS,
                           'SLACK_GAP': SLACK_GAP, 'ALARM_TOL': ALARM_TOL},
                'tag': '[NUM] float64 path following; rigour deferred to M2',
                'repair_dist_rows': REPAIR_DIST,
                'touching_pairs_not_in_38_rows':
                    [list(p) for p in TOUCHING_EXTRA],
            },
            'roots': getattr(self, 'roots', []),
            'summary': {
                'n_segments': len(segs),
                'n_leaves': len(leaves),
                'n_root_segments': sum(1 for s in segs if s['depth'] == 0),
                'termination_counts': dict(term),
                'leaf_termination_counts':
                    dict(Counter(s['termination'] for s in leaves)),
                'depth_counts': {str(k): v for k, v in sorted(depth.items())},
                'branch_factor_mean': float(np.mean(bf)) if bf else 0.0,
                'branch_factor_max': int(max(bf)) if bf else 0,
                'branch_factor_hist':
                    {str(k): v for k, v in sorted(Counter(bf).items())},
                'events_per_segment_mean': float(np.mean(nev)) if nev else 0.0,
                'n_E1': sum(1 for s in segs for e in s['events']
                            if e['type'] == 'E1'),
                'n_E2': sum(1 for s in segs for e in s['events']
                            if e['type'] == 'E2'),
                'n_E3': sum(1 for s in segs for e in s['events']
                            if e['type'] == 'E3'),
                'n_E4': sum(1 for s in segs for e in s['events']
                            if e['type'] == 'E4'),
                'arclen_total': float(sum(s['arclen'] for s in segs)),
                'n_alarms': len(self.alarms),
                'n_rejams': len(self.rejams),
                'n_distinct_rejams':
                    len({r['key'] for r in self.rejams}),
                'n_offlist_E1': len(self.offlist_E1),
                'branch_reasons': dict(self.branch_reason),
                # ---- ALARM CHECK
                'min_s_minus_shat_over_all_routes':
                    (min(x['s_min'] for x in segs) - S_HAT) if segs else None,
                'n_segments_s_below_own_start':
                    sum(1 for x in segs if x['s_min'] < x['s_start'] - 1e-14),
                'n_depth0_negative_dsdtau':
                    sum(1 for x in segs if x['depth'] == 0
                        and x['dsdtau_min'] is not None
                        and x['dsdtau_min'] < -1e-9),
                'n_any_negative_dsdtau':
                    sum(1 for x in segs if x['dsdtau_min'] is not None
                        and x['dsdtau_min'] < -1e-9),
                'dsdtau_pred_vs_obs_maxabs_depth0':
                    max([abs(x['dsdtau_obs'] - x['dsdtau_pred'])
                         for x in segs if x['depth'] == 0
                         and x['dsdtau_obs'] is not None] or [0.0]),
                'arclen_mean': float(np.mean([x['arclen'] for x in segs]))
                    if segs else 0.0,
                'sgain_mean': float(np.mean([x['s_gain'] for x in segs]))
                    if segs else 0.0,
                'first_cross_1e4_arclen_median':
                    float(np.median([x['first_cross_1e4_arclen'] for x in segs
                                     if x['first_cross_1e4_arclen'] is not None]
                                    or [float('nan')])),
                'routes_by_queue': dict(Counter(
                    (getattr(self, 'roots', [{}])[x['root']].get('queue', '?')
                     if x['root'] < len(getattr(self, 'roots', [])) else '?')
                    for x in segs)),
            },
            'alarms': self.alarms,
            'rejams': self.rejams,
            'offlist_E1': self.offlist_E1,
            'segments': segs,
        }
        tmp = path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(out, f)
        os.replace(tmp, path)
        return out


def build_queues():
    """Q1 = M1's 81 survivors; Q2 = k=1 movable; Q3 = k=2 movable."""
    import itertools
    with open(os.path.join(RES, 'm1_strata.json')) as f:
        m1 = json.load(f)
    Q1 = [list(b) for b in m1['synthesis']['global_exhaustive']['survivors']]
    q1_wedge = []
    for B in Q1:
        t, d = wedge_test(ZHAT, B)
        q1_wedge.append({'B': B, 'dof': d, 'max_min_rate': t,
                         'wedged': bool(t <= 1e-8)})
    Q2, Q3 = [], []
    for k in range(NGEO):
        t, d = wedge_test(ZHAT, [k])
        if d > 0 and t > 1e-9:
            Q2.append([k])
    for a, b in itertools.combinations(range(NGEO), 2):
        t, d = wedge_test(ZHAT, [a, b])
        if d > 0 and t > 1e-8:
            Q3.append([a, b])
    # Q4: a random sample of k=3 strata, wedge-tested (scaling / tree estimate)
    rng = np.random.default_rng(4242)
    all3 = list(itertools.combinations(range(NGEO), 3))
    idx = rng.choice(len(all3), size=min(N_K3_SAMPLE, len(all3)), replace=False)
    Q4, n3_tested, n3_movable = [], 0, 0
    for t3 in idx:
        B = list(all3[int(t3)])
        t, d = wedge_test(ZHAT, B)
        n3_tested += 1
        if d > 0 and t > 1e-8:
            n3_movable += 1
            Q4.append(B)
    Q4 = Q4[:N_K3_KEEP]
    return q1_wedge, Q2, Q3, Q4, {'k3_tested': n3_tested,
                                  'k3_movable': n3_movable,
                                  'k3_total': len(all3)}


def main():
    print('s_hat =', S_HAT, flush=True)
    print('touching pairs not among the 38 rows:', TOUCHING_EXTRA, flush=True)
    t0 = time.time()
    q1_wedge, Q2, Q3, Q4, k3stat = build_queues()
    nw = sum(1 for r in q1_wedge if r['wedged'])
    print('Q1 (M1 survivors): %d, wedged %d  [%.0f s]'
          % (len(q1_wedge), nw, time.time() - t0), flush=True)
    print('Q2 (k=1 movable): %d   Q3 (k=2 movable): %d   Q4 (k=3 sample): %d'
          % (len(Q2), len(Q3), len(Q4)), flush=True)
    print('k=3 sample: %d tested, %d movable of %d total'
          % (k3stat['k3_tested'], k3stat['k3_movable'], k3stat['k3_total']),
          flush=True)
    with open(os.path.join(RES, ('m4_queues_repaired.json' if REPAIR_DIST else 'm4_queues.json')), 'w') as f:
        json.dump({'q1_wedge_survey': q1_wedge, 'Q2': Q2, 'Q3': Q3, 'Q4': Q4,
                   'k3_stats': k3stat,
                   'note': '[NUM] first-order escape cone LP at z-hat'}, f)

    queue = [list(r['B']) for r in q1_wedge] + Q2 + Q3 + Q4
    labels = (['Q1'] * len(q1_wedge) + ['Q2'] * len(Q2) + ['Q3'] * len(Q3)
              + ['Q4'] * len(Q4))
    global DELTA_STOP, TIME_BUDGET
    budget = TIME_BUDGET

    # ---- pass A: full taxonomy (MARGIN active)
    DELTA_STOP = 1e-3
    TIME_BUDGET = budget * 0.42
    cA = Cascade(seed=20260827)
    cA.run(queue, os.path.join(RES, ('m4_cascade_repaired.json' if REPAIR_DIST else 'm4_cascade.json')), labels)
    print('pass A: segments %d alarms %d rejams %d stop %s (%.0f s)'
          % (len(cA.segments), len(cA.alarms), len(cA.rejams),
             cA.stop_reason, time.time() - cA.t0), flush=True)

    # ---- pass B: event survey (MARGIN disabled -> run to the travel cap)
    DELTA_STOP = 1e9
    TIME_BUDGET = budget * 0.5
    cB = Cascade(seed=770077)
    cB.run(queue, os.path.join(RES, ('m4_cascade_repaired_eventsurvey.json' if REPAIR_DIST else 'm4_cascade_eventsurvey.json')), labels)
    print('pass B: segments %d alarms %d rejams %d stop %s (%.0f s)'
          % (len(cB.segments), len(cB.alarms), len(cB.rejams),
             cB.stop_reason, time.time() - cB.t0), flush=True)
    print('TOTAL %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
