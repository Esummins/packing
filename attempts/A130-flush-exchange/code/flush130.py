r"""flush130.py -- A130: the flush-aware coupled moves, decided EXACTLY on neighbourhoods.

Three moves beyond A128's menu (docs/proofs/drain_sel.md sect T2), each an interval certificate on a pose box
B = B(z, m, r) (every pose coordinate and the side within r):

  FIELD   Lemma BOX-FIELD-W: a NON-rigid velocity field y = (v_i, w_i)_{i in C} (one exact screw per member,
          C = any set of squares, here every square) such that on the padded box every possibly-separating pair
          axis (member-outsider AND member-member) and every possibly-active wall row of a member has derivative
          >= 0 (WEAK; the flush kink h'(Delta) is charged through the exact difference w_b - w_a), Q's depth
          candidates have derivative > 0 (STRICT), every other (member, corner) depth candidate >= 0.  Then every
          packing in B at which Q intrudes c has a Psi^(w)-smaller packing at the same side, for every positive
          weight vector.  Weak rows are sound on a box of radius r > 0 (the derivative bound holds along the whole
          path, so a row is nondecreasing and stays >= its value at z', which is >= 0 at a packing); at r = 0 the
          rows must be strict (Lemma ROT / CLUSTER-ROT).  The column-straightening + row-slide field of the brief is
          a point of this LP's feasible set; the LP finds the best field.
  EX2     Lemma EXCHANGE-2: the exchange of A128 (slot square S_c + re-fit Q0 fixed in the corner frame) whose
          re-fit is FLUSH against untouched squares F, combined with a finite exact motion (eps* along a field on a
          cluster C of untouched squares, C ∩ {A, Q} = ∅) that opens the flush contacts: for each U in F one axis k*
          with sep_k*(Q0, U) >= -rho_U on B and derivative >= delta_U > 0 on the padded box; every other row of the
          movers weak; eps* = max rho_U / delta_U; the motion stays inside the padded box.  Then for EVERY packing
          z' in B the configuration (z' moved by eps*) \ {A, Q} ∪ {S_c, Q0} is a packing at the same side with a
          corner slot square (dead on [3.82, s-hat) by K0-O1).  forall-packings, no selection.
  KINK    the point tests: (i) FIELD at r = 1e-8 with strict rows (lock103 semantics); (ii) the weak cone
          {rows >= 0, depth rate >= 0}: its maximal depth rate and whether it is {0} (Lemma ISOLATED: then z is a
          strict local minimiser of Psi^(w) on the packings at side m, by the curve selection lemma); (iii) if the
          cone has a flat direction y, the second-order test of Lemma KINK: exists w with
          <g_k, w> + y^T H_k y - kink_k(w) > 0 on every row with zero first-order rate (Hessians by sympy, exact
          symbolic differentiation, evaluated at 30 digits), and the depth's second-order rate > 0 if its first-order
          rate is 0.

Every certificate is re-sampled (>= 10^4 configurations drawn uniformly in the box, the certified quantity
evaluated in floating point, hits = violations).  Pure geometry / interval arithmetic (mpmath.iv, 64 bits,
outward rounded); the LPs are the direction search only (as lock103 / lockw105 / coupled128).  One process,
BLAS pinned, BelowNormal, PYTHONDONTWRITEBYTECODE=1.  Writes only under attempts/A130-flush-exchange/{results,logs}.
A128's coupled128.py is COPIED to geom130.py (A128 is read-only), never imported from A128.

Usage:  python flush130.py [names...] [--radii 1e-3,1e-4,1e-5,1e-6] [--nsamp 10000] [--no-second]
"""
from __future__ import annotations
import os, sys, json, math, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception:
    pass
import numpy as np
from scipy.optimize import linprog
from mpmath import iv, mp
import geom130 as gm
from geom130 import I, lo, hi, hull, signs, hderiv, SqBox, BoxGeom, verts, sep, wall_gap, argmin_data, meeters, \
    frame_pt, frame_to_container, cell_pose, depth_cands, CORNERS, FR, PI, BAR

HERE = os.path.dirname(os.path.abspath(__file__)); A130 = os.path.dirname(HERE)
RES = os.path.join(A130, 'results'); LOGS = os.path.join(A130, 'logs')
os.makedirs(RES, exist_ok=True); os.makedirs(LOGS, exist_ok=True)
T0 = time.time()
_fh = open(os.path.join(LOGS, 'run130.log'), 'a', encoding='utf-8')
SHAT = 3.877083590022814


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%8.1f] %s\n' % (time.time() - T0, m)); _fh.flush()


# ============================================================================ rows with per-square variables
def pair_axis2(A, B, k):
    """Axis k of A against B: separation interval and the derivative coefficients on A's screw (vx, vy, w) WITHOUT
    the kink term, on B's screw, and the kink hull H, so that d sep = cA.yA + cB.yB + H (wB - wA)."""
    n = A.N[k]
    d = (B.c[0] - A.c[0], B.c[1] - A.c[1])
    D = A.th - B.th + (k - 1) * PI / 2
    cD, sD = iv.cos(D), iv.sin(D)
    h = (abs(cD) + abs(sD)) / 2
    s = n[0] * d[0] + n[1] * d[1] - I(0.5) - h
    H = hderiv(cD, sD)
    Jn = (-n[1], n[0]); JcA = (-A.c[1], A.c[0]); JcB = (-B.c[1], B.c[0])
    cA = (-n[0], -n[1], Jn[0] * d[0] + Jn[1] * d[1] - (n[0] * JcA[0] + n[1] * JcA[1]))
    cB = (n[0], n[1], n[0] * JcB[0] + n[1] * JcB[1])
    return s, cA, cB, H


class Row:
    """An affine interval form in the field variables: terms = [(slot, coef)] with slot = 3*i + j for square i's
    (vx, vy, w) and kink = (i_a, i_b, H) meaning + H (w_b - w_a) (i_b = None: the H (-w_a) part folded, i.e. a
    single mover)."""
    __slots__ = ('terms', 'kink', 'tag', 'strict', 'kind', 'meta')

    def __init__(self, terms, kink, tag, strict, kind, meta):
        self.terms, self.kink, self.tag, self.strict, self.kind, self.meta = terms, kink, tag, strict, kind, meta

    def value(self, y, drift):
        """Interval lower bound of the form at the float field y (v components +- drift[i])."""
        v = I(0)
        for (slot, c) in self.terms:
            i, j = divmod(slot, 3)
            yi = I(y[slot] - drift[i], y[slot] + drift[i]) if j < 2 else I(y[slot])
            v = v + c * yi
        if self.kink is not None:
            ia, ib, H = self.kink
            u = (y[3 * ib + 2] if ib is not None else 0.0) - y[3 * ia + 2]
            v = v + H * I(u)
        return lo(v)


def field_rows(G, C, Q, cn, weak_rows, bar=BAR):
    """All rows for the field on the member set C retreating Q from corner cn (Q may be None: pure feasibility)."""
    n = len(G.S); C = set(C); rows = []
    for a in range(n):
        for b in range(a + 1, n):
            if a not in C and b not in C:
                continue
            axes = []
            for (own, oth, k) in [(a, b, kk) for kk in range(4)] + [(b, a, kk) for kk in range(4)]:
                s, cA, cB, H = pair_axis2(G.S[own], G.S[oth], k)
                axes.append((s, own, oth, k, cA, cB, H))
            if any(s.a > bar for (s, *_ ) in axes):
                continue
            for (s, own, oth, k, cA, cB, H) in axes:
                if s.b < -1e-9:
                    continue
                terms = []
                if own in C:
                    terms += [(3 * own + j, cA[j]) for j in range(3)]
                if oth in C:
                    terms += [(3 * oth + j, cB[j]) for j in range(3)]
                if own in C and oth in C:
                    kink = (own, oth, H)
                elif own in C:
                    kink = (own, None, H)
                else:
                    terms.append((3 * oth + 2, H)); kink = None
                rows.append(Row(terms, kink, 'ax%d of %d vs %d' % (k, own, oth), not weak_rows, 'pair', (own, oth, k)))
    for a in sorted(C):
        for (s, coef, name) in G.walls[a]:
            if s.a > bar:
                continue
            rows.append(Row([(3 * a + j, coef[j]) for j in range(3)], None, '%s wall of %d' % (name, a), not weak_rows, 'wall', (a, name)))
    for i in sorted(C):
        for c2 in CORNERS:
            (mlo, mhi), act = G.depth[(i, c2)]
            if mlo >= 1.0:
                continue
            for (val, rws, tag) in act:
                for coef in rws:
                    strict = (Q is not None and i == Q and c2 == cn)
                    rows.append(Row([(3 * i + j, coef[j]) for j in range(3)], None, 'depth %s of %d %s' % (c2, i, coef[3]), strict, 'depth', (i, c2, coef[3])))
    return rows


def robust_lp(rows, nvar, extra_strict_scale=None, ybound=1.0):
    """max t s.t. strict rows >= t, weak rows >= 0, robust in the interval coefficients (y = y+ - y-), kink terms
    through exact difference variables u = w_b - w_a (split u = u+ - u-).  Returns (t, y)."""
    kinks = sorted({(r.kink[0], r.kink[1]) for r in rows if r.kink is not None and r.kink[1] is not None})
    kidx = {kk: nvar + i for i, kk in enumerate(kinks)}
    N = nvar + len(kinks)                       # base variables, each split
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    strict_any = False
    for r in rows:
        row = [0.0] * (2 * N + 1)
        for (slot, c) in r.terms:
            row[slot] += -lo(c); row[N + slot] += hi(c)
        if r.kink is not None:
            ia, ib, H = r.kink
            if ib is None:
                row[3 * ia + 2] += -lo(-H); row[N + 3 * ia + 2] += hi(-H)
            else:
                s = kidx[(ia, ib)]
                row[s] += -lo(H); row[N + s] += hi(H)
        if r.strict:
            row[2 * N] = 1.0; strict_any = True
        A_ub.append(row); b_ub.append(0.0)
    for (ia, ib), s in kidx.items():
        row = [0.0] * (2 * N + 1)
        row[s] = 1.0; row[N + s] = -1.0
        row[3 * ib + 2] -= 1.0; row[N + 3 * ib + 2] += 1.0
        row[3 * ia + 2] += 1.0; row[N + 3 * ia + 2] -= 1.0
        A_eq.append(row); b_eq.append(0.0)
    if not strict_any:
        return -1.0, np.zeros(nvar)
    opts = {'primal_feasibility_tolerance': 1e-10, 'dual_feasibility_tolerance': 1e-10}
    A_ub = np.array(A_ub); b_ub = np.array(b_ub)
    res = linprog(c=[0.0] * (2 * N) + [-1.0], A_ub=A_ub, b_ub=b_ub,
                  A_eq=np.array(A_eq) if A_eq else None, b_eq=np.array(b_eq) if b_eq else None,
                  bounds=[(0, ybound)] * (2 * N) + [(None, 1.0)], method='highs', options=opts)
    if res.status != 0:
        return -1.0, np.zeros(nvar)
    t1 = float(-res.fun)
    y = np.array(res.x[:nvar]) - np.array(res.x[N:N + nvar])
    if t1 > 1e-10:
        # phase 2: the L1-smallest field at (almost) the same rate -- kills the tolerance-level garbage components
        # that a degenerate optimum carries (exact zeros make structurally-zero rows evaluate to exactly 0)
        A2 = np.vstack([A_ub, np.array([[0.0] * (2 * N) + [-1.0]])]); b2 = np.concatenate([b_ub, [-t1 * (1 - 1e-6)]])
        res2 = linprog(c=[1.0] * (2 * N) + [0.0], A_ub=A2, b_ub=b2, A_eq=np.array(A_eq) if A_eq else None,
                       b_eq=np.array(b_eq) if b_eq else None, bounds=[(0, ybound)] * (2 * N) + [(None, 1.0)], method='highs', options=opts)
        if res2.status == 0:
            y = np.array(res2.x[:nvar]) - np.array(res2.x[N:N + nvar]); t1 = float(res2.x[2 * N])
    return t1, y


def evaluate_rows(rows, y, drift):
    ms, ws, mt, wt = math.inf, math.inf, None, None; bounds = []
    for r in rows:
        v = r.value(y, drift)
        bounds.append((r.tag, v, r.strict))
        if r.strict:
            if v < ms:
                ms, mt = v, r.tag
        else:
            if v < ws:
                ws, wt = v, r.tag
    return ms, ws, mt, wt, bounds


def drift_of(y, n, pad=1e-6):
    return [pad * abs(y[3 * i + 2]) * math.hypot(y[3 * i], y[3 * i + 1]) for i in range(n)]


# ============================================================================ float evaluation of a row (sampling)
N0 = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def float_row(r, Z, M, y):
    """Derivative of row r along the field y at the sampled poses Z (nsamp, n, 3), sides M (nsamp,)."""
    kind = r.kind
    if kind == 'pair':
        own, oth, k = r.meta
        A_c, A_th = Z[:, own, :2], Z[:, own, 2]; B_c, B_th = Z[:, oth, :2], Z[:, oth, 2]
        n0 = N0[k]
        nx = n0[0] * np.cos(A_th) - n0[1] * np.sin(A_th); ny = n0[0] * np.sin(A_th) + n0[1] * np.cos(A_th)
        D = A_th - B_th + (k - 1) * np.pi / 2
        cD, sD = np.cos(D), np.sin(D)
        Hd = (-np.sign(cD) * sD + np.sign(sD) * cD) / 2
        d = B_c - A_c
        Jn_d = -ny * d[:, 0] + nx * d[:, 1]
        n_JcA = nx * (-A_c[:, 1]) + ny * A_c[:, 0]
        n_JcB = nx * (-B_c[:, 1]) + ny * B_c[:, 0]
        ya = y[3 * own:3 * own + 3]; yb = y[3 * oth:3 * oth + 3]
        return (-nx * ya[0] - ny * ya[1] + ya[2] * (Jn_d - n_JcA)) + (nx * yb[0] + ny * yb[1] + yb[2] * n_JcB) + Hd * (yb[2] - ya[2])
    if kind == 'wall':
        i, name = r.meta
        c = Z[:, i, :2]; th = Z[:, i, 2]; vx, vy, w = y[3 * i:3 * i + 3]
        Hd = (-np.sign(np.cos(th)) * np.sin(th) + np.sign(np.sin(th)) * np.cos(th)) / 2
        if name == 'left':
            return vx + w * (-c[:, 1] - Hd)
        if name == 'bottom':
            return vy + w * (c[:, 0] - Hd)
        if name == 'right':
            return -vx + w * (c[:, 1] - Hd)
        return -vy + w * (-c[:, 0] - Hd)
    i, c2, ctag = r.meta
    sx, sy, fx, fy = FR[c2]
    ox = M if fx else 0.0; oy = M if fy else 0.0
    c = Z[:, i, :2]; th = Z[:, i, 2]; vx, vy, w = y[3 * i:3 * i + 3]
    if ctag.startswith('V'):
        kk = int(ctag[1:2]); dx, dy = ((-1, -1), (1, -1), (1, 1), (-1, 1))[kk]
        px = c[:, 0] + 0.5 * (dx * np.cos(th) - dy * np.sin(th)); py = c[:, 1] + 0.5 * (dx * np.sin(th) + dy * np.cos(th))
        return (sx * vx - sx * w * py) if ctag.endswith('x') else (sy * vy + sy * w * px)
    kk = int(ctag[1:]); n0 = N0[kk]
    nx = n0[0] * np.cos(th) - n0[1] * np.sin(th); ny = n0[0] * np.sin(th) + n0[1] * np.cos(th)
    nfx, nfy = -sx * nx, -sy * ny; S_ = nfx + nfy
    cfx, cfy = sx * (c[:, 0] - ox), sy * (c[:, 1] - oy)
    mu = (cfx * nfx + cfy * nfy - 0.5) / S_; wf = sx * sy
    return (sx * nfx * vx + sy * nfy * vy + w * (-sx * c[:, 1] * nfx + sy * c[:, 0] * nfy + wf * (cfy * nfx - cfx * nfy) - mu * wf * (nfx - nfy))) / S_


def draw_box(z, m, r, nsamp, rng, tilt=None):
    z = np.asarray(z); n = len(z)
    Z = z[None] + rng.uniform(-r, r, size=(nsamp, n, 3)); M = m + rng.uniform(-r, r, size=nsamp)
    for i, (a, b) in (tilt or {}).items():
        Z[:, i, 2] = rng.uniform(a, b, size=nsamp)
    return Z, M


def sample_rows(z, m, r, rows, y, bounds, nsamp, rng, tilt=None):
    Z, M = draw_box(z, m, r, nsamp, rng, tilt)
    hits, worst = 0, math.inf
    for r_, (tag, b, strict) in zip(rows, bounds):
        der = float_row(r_, Z, M, y)
        worst = min(worst, float((der - b).min()))
        hits += int((der < b - 1e-9).sum())
    return {'drawn': nsamp, 'tested': nsamp, 'hits': hits, 'min_derivative_minus_bound': worst}


# ============================================================================ FIELD certificate
def float_sep_axis(Z, own, oth, k):
    A_c, A_th = Z[:, own, :2], Z[:, own, 2]; B_c, B_th = Z[:, oth, :2], Z[:, oth, 2]
    n0 = N0[k]
    nx = n0[0] * np.cos(A_th) - n0[1] * np.sin(A_th); ny = n0[0] * np.sin(A_th) + n0[1] * np.cos(A_th)
    D = A_th - B_th + (k - 1) * np.pi / 2
    h = (np.abs(np.cos(D)) + np.abs(np.sin(D))) / 2
    d = B_c - A_c
    return nx * d[:, 0] + ny * d[:, 1] - 0.5 - h


def mode_cases(rows, focus, cap=6):
    """CONTACT-MODE split (Lemma MODE): a pair with >= 2 possibly-separating axis rows is, at every packing of the
    box, separated by the axis of largest separation; on the piece {sep_k >= sep_k' for all k'} only row k is
    needed.  Returns a list of cases, each = (description, rows-to-drop).  Only pairs in `focus` (a set of
    frozensets) are split, at most `cap` of them (the rest keep every row)."""
    import itertools
    groups = {}
    for idx, rw in enumerate(rows):
        if rw.kind == 'pair':
            groups.setdefault(frozenset(rw.meta[:2]), []).append(idx)
    split = [g for g in groups if len(groups[g]) >= 2 and g in focus][:cap]
    if not split:
        return [({}, set())]
    cases = []
    for choice in itertools.product(*[groups[g] for g in split]):
        drop = set()
        desc = {}
        for g, keep in zip(split, choice):
            drop |= set(groups[g]) - {keep}
            desc[rows[keep].tag] = 'separating'
        cases.append((desc, drop))
    return cases


def in_mode(Z, rows, desc):
    """Sample membership of the mode piece: for every kept row of a split pair, its float separation is >= that of
    every dropped row of the same pair (ties count as inside)."""
    ok = np.ones(Z.shape[0], dtype=bool)
    tags = {rw.tag: rw for rw in rows}
    kept = [tags[t] for t in desc]
    for kw in kept:
        pair = frozenset(kw.meta[:2])
        sk = float_sep_axis(Z, kw.meta[0], kw.meta[1], kw.meta[2])
        for rw in rows:
            if rw.kind == 'pair' and frozenset(rw.meta[:2]) == pair and rw.tag != kw.tag:
                so = float_sep_axis(Z, rw.meta[0], rw.meta[1], rw.meta[2])
                ok &= (sk >= so - 1e-12)
    return ok


def mode_vacuous(G, rows_all, desc):
    """True if for some split pair the kept axis has separation < every dropped axis on the whole box (then no
    packing of the box is in this mode piece)."""
    tags = {rw.tag: rw for rw in rows_all}
    for t_ in desc:
        kw = tags[t_]; pair = frozenset(kw.meta[:2])
        sk, *_ = pair_axis2(G.S[kw.meta[0]], G.S[kw.meta[1]], kw.meta[2])
        for rw in rows_all:
            if rw.kind == 'pair' and frozenset(rw.meta[:2]) == pair and rw.tag != t_:
                so, *_ = pair_axis2(G.S[rw.meta[0]], G.S[rw.meta[1]], rw.meta[2])
                if hi(sk - so) < 0:
                    return True
    return False


def certify_field_sub(z, m, r, C, Q, cn, nsamp, rng, geoms, tilt, focus=None):
    """One tilt-sign sub-box: for every contact-mode case (Lemma MODE) an LP on the box, an interval verification on
    the padded box (tilts of w = 0 squares unpadded), a sampled confirmation restricted to the case's piece."""
    n = len(z)
    Gl = geoms.get(r, False, pad=3e-6, tilt=tilt)      # the LP sees a box slightly LARGER than the verification box
    rows_all = field_rows(Gl, C, Q, cn, weak_rows=True)
    cases = mode_cases(rows_all, focus or set())
    out = {'cases': len(cases), 'n_rows': len(rows_all), 'case_results': []}
    allok = True; lp_ts = []; ms_all = math.inf; hits = 0; drawn = 0; movers = set()
    for desc, drop in cases:
        if desc and mode_vacuous(Gl, rows_all, desc):
            out['case_results'].append({'mode': desc, 'certified': True, 'vacuous': True, 'lp_t': math.inf}); lp_ts.append(math.inf); continue
        tags_drop = {rows_all[i].tag for i in drop}
        rows = [rw for i, rw in enumerate(rows_all) if i not in drop]
        t, y = robust_lp(rows, 3 * n); y = snap_y(y)
        # a split square that rotates crosses its axis: re-solve with its tilt interval padded (both branches)
        tilt_lp = dict(tilt)
        for _it in range(4):
            rot = [i for i in tilt if y[3 * i + 2] != 0.0 and tilt_lp[i] == tilt[i]]
            if t <= 1e-10 or not rot:
                break
            for i in rot:
                tilt_lp[i] = (tilt[i][0] - 1e-6, tilt[i][1] + 1e-6)
            G2 = geoms.get(r, False, pad=3e-6, tilt=tilt_lp)
            rows = [rw for rw in field_rows(G2, C, Q, cn, weak_rows=True) if rw.tag not in tags_drop]
            t, y = robust_lp(rows, 3 * n); y = snap_y(y)
        lp_ts.append(t)
        crec = {'mode': desc, 'lp_t': t}
        if t <= 1e-10:
            crec['certified'] = False; allok = False; out['case_results'].append(crec); continue
        Gv = geoms.get(r, True, tilt=pad_tilt(tilt, y, 1e-6))
        rows2_all = field_rows(Gv, C, Q, cn, weak_rows=True)
        rows2 = [rw for rw in rows2_all if rw.tag not in tags_drop]
        dr = drift_of(y, n)
        ms, ws, mt, wt, bounds = evaluate_rows(rows2, y, dr)
        ok = ms > 0 and ws >= 0
        crec.update({'certified': bool(ok), 'min_strict': ms, 'min_weak': ws, 'worst_strict': mt, 'worst_weak': wt,
                     'movers': sorted(i for i in C if any(abs(v) > 0 for v in y[3 * i:3 * i + 3])), 'y': [float(v) for v in y]})
        if ok:
            ns = max(nsamp // len(cases), 500)
            Z, M = draw_box(z, m, r, ns, rng, tilt)
            inside = in_mode(Z, rows2_all, desc)
            h = 0; worst = math.inf
            for rw, (tag, b, st) in zip(rows2, bounds):
                der = float_row(rw, Z, M, y)
                bad = (der < b - 1e-9) & inside
                h += int(bad.sum()); worst = min(worst, float((der - b)[inside].min()) if inside.any() else math.inf)
            crec['sample'] = {'drawn': ns, 'in_piece': int(inside.sum()), 'tested': int(inside.sum()), 'hits': h, 'min_derivative_minus_bound': worst}
            hits += h; drawn += int(inside.sum()); ms_all = min(ms_all, ms); movers |= set(crec['movers'])
        else:
            allok = False
        out['case_results'].append(crec)
    out['vacuous_cases'] = sum(1 for c in out['case_results'] if c.get('vacuous'))
    out.update({'certified': allok, 'lp_t': min(lp_ts) if lp_ts else -1.0, 'min_strict': (ms_all if ms_all < math.inf else None) if allok else None,
                'movers': sorted(movers), 'sample': {'drawn': drawn, 'tested': drawn, 'hits': hits} if allok else None,
                'worst_strict': next((c.get('worst_strict') for c in out['case_results'] if not c['certified']), None),
                'worst_weak': next((c.get('worst_weak') for c in out['case_results'] if not c['certified']), None),
                'min_weak': next((c.get('min_weak') for c in out['case_results'] if not c['certified']), None),
                'failed_modes': [c['mode'] for c in out['case_results'] if not c['certified']][:6]})
    return out


def certify_field(z, m, r, C, Q, cn, nsamp, rng, geoms, split=True, nsub=None):
    """FIELD on the box B(z, m, r): with split, the box is the union of the tilt-sign sub-boxes of the axis-aligned
    squares among Q and its row partners; certified iff every sub-box is (each with its own field)."""
    n = len(z)
    if not split:
        o = certify_field_sub(z, m, r, C, Q, cn, nsamp, rng, geoms, {}, set())
        o['subboxes'] = 1; return o
    G0 = geoms.get(r, False)
    partners = {Q} | {rw.meta[1] if rw.meta[0] == Q else rw.meta[0] for rw in field_rows(G0, {Q}, Q, cn, True) if rw.kind == 'pair'}
    spl = axis_aligned(z, partners & set(C))
    pats = tilt_patterns(z, spl, r)
    focus = {frozenset((a, b)) for a in partners for b in partners if a != b}
    subs = []; allok = True; worst = None
    for sg, tilt in pats:
        o = certify_field_sub(z, m, r, C, Q, cn, max(nsamp // len(pats), 1000), rng, geoms, tilt, focus)
        o['pattern'] = dict(zip([str(i) for i in spl], sg))
        subs.append(o)
        if not o['certified']:
            allok = False
    hits = sum((o.get('sample') or {}).get('hits', 0) for o in subs); drawn = sum((o.get('sample') or {}).get('drawn', 0) for o in subs)
    return {'certified': allok, 'split_squares': spl, 'subboxes': len(pats), 'subboxes_certified': sum(o['certified'] for o in subs),
            'mode_cases_per_subbox': subs[0]['cases'] if subs else 0, 'failed_modes': [o.get('failed_modes') for o in subs if not o['certified']][:4],
            'lp_t': min(o['lp_t'] for o in subs), 'min_strict': min((o['min_strict'] for o in subs if o.get('min_strict') is not None), default=None),
            'sample': {'drawn': drawn, 'tested': drawn, 'hits': hits} if allok else None,
            'failed_patterns': [o['pattern'] for o in subs if not o['certified']][:8],
            'fail_reasons': [{'pattern': o['pattern'], 'lp_t': o['lp_t'], 'worst_strict': o.get('worst_strict'), 'worst_weak': o.get('worst_weak'), 'min_weak': o.get('min_weak')} for o in subs if not o['certified']][:4],
            'certified_patterns': [{'pattern': o['pattern'], 'movers': o['movers'], 'min_strict': o['min_strict']} for o in subs if o['certified']][:8]}



# ============================================================================ EX2: depth-2 exchange
def frame_square_box(cn, mI, u, v, phi):
    sx, sy, fx, fy = FR[cn]
    oxI = mI if fx else I(0); oyI = mI if fy else I(0)
    S = SqBox(0, 0, sx * sy * phi, 0)
    S.c = (oxI + I(sx) * u, oyI + I(sy) * v)
    cs, sn = S.cs, S.sn
    S.V = [(S.c[0] + (dx * cs - dy * sn) / 2, S.c[1] + (dx * sn + dy * cs) / 2) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return S


def best_axis_lo(P, U):
    best = (-math.inf, None)
    for k in range(4):
        s1, *_ = pair_axis2(P, U, k)
        if lo(s1) > best[0]:
            best = (lo(s1), ('P', k))
        s2, *_ = pair_axis2(U, P, k)
        if lo(s2) > best[0]:
            best = (lo(s2), ('U', k))
    return best


def ex2_rows(G, C, F, Q0, Sc, A, Qi, weak_rows=True, bar=BAR):
    """Rows of the depth-2 exchange: the movers C (untouched squares), against untouched outsiders, walls, each
    other (all weak), the slot square Sc (weak), and the re-fit Q0: for U in F one STRICT axis (the best one),
    for U in C \\ F weak rows on the possibly-separating axes."""
    n = len(G.S); C = set(C)
    rows = [rw for rw in field_rows(G, C, None, None, weak_rows=weak_rows) if rw.kind != 'depth'
            and not (rw.kind == 'pair' and (rw.meta[0] in (A, Qi) or rw.meta[1] in (A, Qi)))]
    strict_axes = {}
    for U in sorted(C):
        for (P, pname) in ((Sc, 'S'), (Q0, 'Q0')):
            axes = []
            for k in range(4):
                s1, cA, cB, H = pair_axis2(G.S[U], P, k)      # U's axis, U moves
                axes.append((s1, 'U', k, [(3 * U + j, cA[j]) for j in range(3)], (U, None, H)))
                s2, cA2, cB2, H2 = pair_axis2(P, G.S[U], k)   # P's axis, U moves (as B)
                axes.append((s2, 'P', k, [(3 * U + j, cB2[j]) for j in range(3)] + [(3 * U + 2, H2)], None))
            if pname == 'Q0' and U in F:
                s, side, k, terms, kink = max(axes, key=lambda a: a[0].a)
                rows.append(Row(terms, kink, 'Q0 %s-ax%d vs %d STRICT' % (side, k, U), True, 'ex', (U, pname, side, k)))
                strict_axes[U] = (side, k, lo(s))
                continue
            if any(a[0].a > bar for a in axes):
                continue
            for (s, side, k, terms, kink) in axes:
                if s.b < -1e-9:
                    continue
                rows.append(Row(terms, kink, '%s %s-ax%d vs %d' % (pname, side, k, U), False, 'ex', (U, pname, side, k)))
    return rows, strict_axes


def float_ex_row(r, Z, M, y, cn, m, Q0f, Scf):
    U, pname, side, k = r.meta
    nsamp = Z.shape[0]
    P = np.array([frame_to_container(cn, M[t], *(Q0f if pname == 'Q0' else Scf)) for t in range(nsamp)])
    Zu = Z[:, U, :]
    if side == 'U':
        A_c, A_th, B_c, B_th = Zu[:, :2], Zu[:, 2], P[:, :2], P[:, 2]
    else:
        A_c, A_th, B_c, B_th = P[:, :2], P[:, 2], Zu[:, :2], Zu[:, 2]
    n0 = N0[k]
    nx = n0[0] * np.cos(A_th) - n0[1] * np.sin(A_th); ny = n0[0] * np.sin(A_th) + n0[1] * np.cos(A_th)
    D = A_th - B_th + (k - 1) * np.pi / 2; cD, sD = np.cos(D), np.sin(D)
    Hd = (-np.sign(cD) * sD + np.sign(sD) * cD) / 2
    d = B_c - A_c; vx, vy, w = y[3 * U:3 * U + 3]
    if side == 'U':
        Jn_d = -ny * d[:, 0] + nx * d[:, 1]; n_JcA = nx * (-A_c[:, 1]) + ny * A_c[:, 0]
        return -nx * vx - ny * vy + w * (Jn_d - n_JcA - Hd)
    n_JcB = nx * (-B_c[:, 1]) + ny * B_c[:, 0]
    return nx * vx + ny * vy + w * (n_JcB + Hd)


def screw_apply(pose, y3, eps):
    cx, cy, th = pose; vx, vy, w = y3
    c, s = math.cos(eps * w), math.sin(eps * w)
    return (c * cx - s * cy + eps * vx, s * cx + c * cy + eps * vy, th + eps * w)


def certify_ex2(z, m, cn, A, Qi, Q0f, radii, nsamp, rng, geoms, clusters_fn):
    """Depth-2 exchange at corner cn with meeters (A, Qi) and A128's re-fit frame pose Q0f = (u, v, phi)."""
    n = len(z); untouched = [j for j in range(n) if j not in (A, Qi)]
    u, v, phi = Q0f
    if abs(phi % (math.pi / 2)) < 1e-6 or abs(phi % (math.pi / 2) - math.pi / 2) < 1e-6:
        phi = 0.0
        if abs(u - round(u * 2) / 2) < 1e-6 and abs(v - round(v * 2) / 2) < 1e-6:
            u, v = round(u * 2) / 2, round(v * 2) / 2
    mu0 = argmin_data((u, v, phi), 'BL', 10.0)[0]
    if mu0 < 1.0:
        u += (1.0 - mu0) + 1e-9; v += (1.0 - mu0) + 1e-9     # translation by (t, t) raises mu_c by exactly t
    Q0f = (u, v, phi)
    Scf = (0.5, 0.5, 0.0)
    out = {'Q0_frame': list(Q0f), 'tried': []}
    for r in radii:
        Gb = geoms.get(r, False)
        Q0 = frame_square_box(cn, Gb.m, u, v, phi); Sc = frame_square_box(cn, Gb.m, 0.5, 0.5, 0.0)
        # static checks: Q0 in the container, mu_c(Q0) >= 1, and the flush set F on this box
        Q0f_ = SqBox(u, v, phi, 0)      # the re-fit in its corner frame: container and mu_c are m'-free there
        okc = all(px.a >= 0 and py.a >= 0 and hi(px) <= lo(Gb.m) and hi(py) <= lo(Gb.m) for (px, py) in Q0f_.V)
        (mlo, mhi), _ = depth_cands(Q0f_, 'BL', Gb.m)
        margins = {j: best_axis_lo(Q0, Gb.S[j])[0] for j in untouched}
        F = [j for j in untouched if margins[j] < 0]
        rec = {'r': r, 'container_ok': okc, 'mu_lo': mlo, 'flush_set': F, 'flush_margins': {str(j): margins[j] for j in F}}
        if not okc or mlo < 1 - 1e-15:
            rec['verdict'] = 'Q0 invalid on the box'; out['tried'].append(rec); continue
        if not F:
            rec['verdict'] = 'depth-1 exchange already certifies (no flush set)'; out['tried'].append(rec); out['certified_radius'] = r; return out
        # tilt-sign sub-boxes on the axis-aligned squares of F and their contact neighbours among the untouched
        V_ = [verts(*p) for p in z]
        nbF = set(F) | {j for j in untouched for f in F if j != f and sep(V_[j], V_[f]) < 5e-3}
        spl = axis_aligned(z, nbF); pats = tilt_patterns(z, spl, r)
        rec['split_squares'] = spl; rec['subboxes'] = len(pats)
        subs = []
        for sg, tilt in pats:
            Gb_s = geoms.get(r, False, tilt=tilt)
            Q0s = frame_square_box(cn, Gb_s.m, u, v, phi); Scs = frame_square_box(cn, Gb_s.m, 0.5, 0.5, 0.0)
            best = None; best_modes = {}; n_modes = None
            for C in clusters_fn(F, untouched):
              rows_all_B, sax = ex2_rows(Gb_s, C, F, Q0s, Scs, A, Qi)     # sax: the flush rows' deficits rho on B itself
              for pad_mult in (1.0, 3.0, 10.0):
                pad = pad_mult * r
                G_lp = geoms.get(r, False, pad=pad + 3e-6, tilt=tilt)
                Q0l = frame_square_box(cn, G_lp.m, u, v, phi); Scl = frame_square_box(cn, G_lp.m, 0.5, 0.5, 0.0)
                rows_all, _ = ex2_rows(G_lp, C, F, Q0l, Scl, A, Qi)
                focus = {frozenset((a, b)) for a in nbF for b in nbF if a != b}
                for desc, drop in mode_cases(rows_all, focus):
                  if desc and mode_vacuous(G_lp, rows_all, desc):
                      best_modes.setdefault(json.dumps(desc, sort_keys=True), []).append({'pattern': dict(zip([str(i) for i in spl], sg)), 'mode': desc, 'vacuous': True, 'cluster': sorted(C), 'lp_t': math.inf, 'eps_star': 0.0, 'min_strict': math.inf, 'y': [0.0] * (3 * n)})
                      continue
                  tags_drop0 = {rows_all[i].tag for i in drop}
                  rows = [rw for i, rw in enumerate(rows_all) if i not in drop]
                  t, y = robust_lp(rows, 3 * n); y = snap_y(y)
                  tilt_lp = dict(tilt)
                  for _it in range(4):
                    rot = [i for i in tilt if y[3 * i + 2] != 0.0 and tilt_lp[i] == tilt[i]]
                    if t <= 1e-10 or not rot:
                        break
                    for i in rot:
                        tilt_lp[i] = (tilt[i][0] - 1e-6, tilt[i][1] + 1e-6)
                    G2 = geoms.get(r, False, pad=pad + 3e-6, tilt=tilt_lp)
                    Q02 = frame_square_box(cn, G2.m, u, v, phi); Sc2 = frame_square_box(cn, G2.m, 0.5, 0.5, 0.0)
                    rows_all2, _ = ex2_rows(G2, C, F, Q02, Sc2, A, Qi)
                    rows = [rw for rw in rows_all2 if rw.tag not in tags_drop0]
                    t, y = robust_lp(rows, 3 * n); y = snap_y(y)
                  if t <= 1e-10:
                    continue
                  if True:
                    Gv = geoms.get(r, False, pad=pad + 1e-6, tilt=pad_tilt(tilt, y, pad + 1e-6))
                    Q0v = frame_square_box(cn, Gv.m, u, v, phi); Scv = frame_square_box(cn, Gv.m, 0.5, 0.5, 0.0)
                    rows2_all, sax2 = ex2_rows(Gv, C, F, Q0v, Scv, A, Qi)
                    tags_drop = {rows_all[i].tag for i in drop}
                    rows2 = [rw for rw in rows2_all if rw.tag not in tags_drop]
                    dr = drift_of(y, n, pad=pad + 1e-6)
                    ms, ws, mt, wt, bounds = evaluate_rows(rows2, y, dr)
                    if not (ms > 0 and ws >= 0):
                        continue
                    eps_need = 0.0
                    for U, (side, k, s_lo) in sax.items():
                        rate = min(b for (tag, b, st) in bounds if st and tag.endswith('vs %d STRICT' % U))
                        eps_need = max(eps_need, max(0.0, -s_lo) / rate)
                    motion = max(eps_need * (math.hypot(y[3 * i], y[3 * i + 1]) + abs(y[3 * i + 2]) * (m + 2)) for i in C)
                    if motion <= pad:
                        cand = {'pattern': dict(zip([str(i) for i in spl], sg)), 'mode': desc, 'cluster': sorted(C), 'lp_t': t, 'pad': pad, 'eps_star': eps_need, 'max_motion': motion,
                                'min_strict': ms, 'min_weak': ws, 'worst_weak': wt, 'strict_axes': {str(k_): v_ for k_, v_ in sax.items()}, 'y': [float(a) for a in y], 'n_rows': len(rows2)}
                        best_modes.setdefault(json.dumps(desc, sort_keys=True), []).append(cand)
            # every contact-mode case of the (largest) cluster's row set must be certified; the number of cases is
            # that of the first cluster's rows (the mode split is on pairs among nbF, common to all clusters)
            G_pr = geoms.get(r, False, pad=r + 3e-6, tilt=tilt); Q0p = frame_square_box(cn, G_pr.m, u, v, phi); Scp = frame_square_box(cn, G_pr.m, 0.5, 0.5, 0.0)
            rows_probe, _ = ex2_rows(G_pr, list(clusters_fn(F, untouched))[-1], F, Q0p, Scp, A, Qi)
            n_modes = len(mode_cases(rows_probe, {frozenset((a, b)) for a in nbF for b in nbF if a != b}))
            if len(best_modes) < n_modes:
                subs.append({'pattern': dict(zip([str(i) for i in spl], sg)), 'certified': False, 'modes_certified': len(best_modes), 'modes': n_modes}); continue
            ns = max(nsamp // len(pats), 1000)
            Z, M = draw_box(z, m, r, ns, rng, tilt)
            rows_probe_all = rows_probe
            hits = 0; worst = math.inf; tested = 0
            cands = [max(v, key=lambda c: c['min_strict']) for v in best_modes.values()]
            for cand in cands:
                inside = in_mode(Z, rows_probe_all, cand['mode'])
                y = np.array(cand['y']); eps = cand['eps_star']; C = cand['cluster']
                for t_ in np.nonzero(inside)[0]:
                    poses = [tuple(Z[t_, j]) for j in range(n)]
                    for j in C:
                        poses[j] = screw_apply(poses[j], y[3 * j:3 * j + 3], eps)
                    P = [verts(*poses[j]) for j in untouched]
                    P.append(verts(*frame_to_container(cn, M[t_], *Scf))); P.append(verts(*frame_to_container(cn, M[t_], u, v, phi)))
                    wg = min(min(sep(P[a], P[b]) for a in range(len(P)) for b in range(a + 1, len(P))), min(wall_gap(p, M[t_]) for p in P))
                    worst = min(worst, wg); tested += 1
                    if wg < -1e-9 or argmin_data(frame_to_container(cn, M[t_], u, v, phi), cn, M[t_])[0] < 1 - 1e-12:
                        hits += 1
            best = max(cands, key=lambda c: -c['min_strict'])
            best = dict(best); best['modes'] = n_modes; best['all_modes'] = [{'mode': c['mode'], 'cluster': c['cluster'], 'eps_star': c['eps_star'], 'min_strict': c['min_strict']} for c in cands]
            best['sample'] = {'drawn': ns, 'tested': tested, 'hits': hits, 'worst_gap_seen': worst}; best['certified'] = True
            subs.append(best)
        rec['subboxes_certified'] = sum(1 for o in subs if o['certified'])
        rec['sub'] = subs
        if all(o['certified'] for o in subs):
            rec['verdict'] = 'EX2 certified on the box r=%g (%d sub-boxes): every packing in B yields a k>=1 packing at the same side' % (r, len(pats))
            rec['sample'] = {'drawn': sum(o['sample']['drawn'] for o in subs), 'tested': sum(o['sample']['tested'] for o in subs), 'hits': sum(o['sample']['hits'] for o in subs)}
            rec['eps_star'] = max(o['eps_star'] for o in subs); rec['min_strict'] = min(o['min_strict'] for o in subs)
            out['tried'].append(rec); out['certified_radius'] = r; out['best'] = rec
            return out
        rec['verdict'] = 'not certified: %d of %d sub-boxes fail (patterns %s)' % (len(pats) - rec['subboxes_certified'], len(pats), [o['pattern'] for o in subs if not o['certified']][:4])
        out['tried'].append(rec); continue
    out['certified_radius'] = None
    return out


# ============================================================================ geometry cache
class Geoms:
    def __init__(self, poses, m):
        self.poses, self.m, self.cache = poses, m, {}

    def get(self, r, ver=False, pad=None, tilt=None):
        """Box of radius r (+1e-6 if ver, or +pad); tilt = {i: (lo, hi)} overrides square i's tilt interval
        (a tilt-sign sub-box); the side and centres always use the full radius."""
        rr = r + (1e-6 if ver else 0.0) if pad is None else r + pad
        key = (rr, tuple(sorted(tilt.items())) if tilt else None)
        if key not in self.cache:
            self.cache[key] = BoxGeom(self.poses, self.m, rr, exact_axis=(rr == 0), tilt_override=tilt)
        return self.cache[key]


def axis_aligned(poses, S):
    return [i for i in sorted(S) if min(abs(poses[i][2] % (math.pi / 2)), math.pi / 2 - abs(poses[i][2] % (math.pi / 2))) < 1e-7]


def tilt_patterns(poses, split, r):
    """All sign patterns of the tilt sub-boxes [th - r, th] / [th, th + r] for the squares in split."""
    import itertools
    pats = []
    for sg in itertools.product((-1, 1), repeat=len(split)):
        t = {}
        for i, s_ in zip(split, sg):
            th = poses[i][2]
            t[i] = (th - r, th) if s_ < 0 else (th, th + r)
        pats.append((sg, t))
    return pats


def pad_tilt(tilt, y, pad):
    """The verification tilt intervals: a square with w = 0 EXACTLY keeps its tilt along the exact motion, so
    its sub-box interval is not padded; every other square's interval is padded on both sides."""
    out = {}
    for i, (a, b) in tilt.items():
        if y[3 * i + 2] == 0.0:
            out[i] = (a, b)
        else:
            out[i] = (a - pad, b + pad)
    return out


def snap_y(y):
    y = np.array(y, dtype=float)
    y[np.abs(y) < 1e-12] = 0.0
    return y


# ============================================================================ point tests: weak cone, ISOLATED, KINK
def weak_cone(G, Q, cn, n):
    """max rho s.t. every pair/wall/other-depth row >= 0 and every depth candidate row of Q >= rho, |y| <= 1.
    Then, if rho* ~ 0, test whether the cone {rows >= 0, depth rows >= 0} is {0}."""
    rows = field_rows(G, set(range(n)), Q, cn, weak_rows=True)
    t, y = robust_lp(rows, 3 * n)
    out = {'max_depth_rate': t, 'y': [float(v) for v in y]}
    if t > 1e-6:          # above the near-packings' residual (KKT 1e-6..1e-5, gaps 1e-8): a genuine first-order drain
        return out, rows
    # the cone with all rows weak
    for r in rows:
        r.strict = False
    kinks = sorted({(r.kink[0], r.kink[1]) for r in rows if r.kink is not None and r.kink[1] is not None})
    kidx = {kk: 3 * n + i for i, kk in enumerate(kinks)}; N = 3 * n + len(kinks)
    A_ub, A_eq = [], []
    for r in rows:
        row = [0.0] * (2 * N)
        for (slot, c) in r.terms:
            row[slot] += -lo(c); row[N + slot] += hi(c)
        if r.kink is not None:
            ia, ib, H = r.kink
            if ib is None:
                row[3 * ia + 2] += -lo(-H); row[N + 3 * ia + 2] += hi(-H)
            else:
                s = kidx[(ia, ib)]; row[s] += -lo(H); row[N + s] += hi(H)
        A_ub.append(row)
    for (ia, ib), s in kidx.items():
        row = [0.0] * (2 * N); row[s] = 1.0; row[N + s] = -1.0
        row[3 * ib + 2] -= 1.0; row[N + 3 * ib + 2] += 1.0; row[3 * ia + 2] += 1.0; row[N + 3 * ia + 2] -= 1.0
        A_eq.append(row)
    ext = 0.0; ybest = None
    for j in range(3 * n):
        for sgn in (1.0, -1.0):
            c = [0.0] * (2 * N); c[j] = -sgn; c[N + j] = sgn
            res = linprog(c=c, A_ub=np.array(A_ub), b_ub=np.zeros(len(A_ub)), A_eq=np.array(A_eq) if A_eq else None,
                          b_eq=np.zeros(len(A_eq)) if A_eq else None, bounds=[(0, 1)] * (2 * N), method='highs')
            if res.status == 0 and -res.fun > ext:
                ext = -res.fun; ybest = np.array(res.x[:3 * n]) - np.array(res.x[N:N + 3 * n])
    out['cone_extent'] = ext
    out['isolated'] = ext <= 1e-9
    if ybest is not None:
        out['flat_y'] = [float(v) for v in ybest]
    return out, rows


# ---- second order (sympy Hessians at the point)
_SYM = None


def sym_setup():
    global _SYM
    if _SYM is not None:
        return _SYM
    import sympy as sp
    ax, ay, ta, bx, by, tb, mm = sp.symbols('ax ay ta bx by tb mm', real=True)
    _SYM = {'sp': sp, 'vars6': (ax, ay, ta, bx, by, tb), 'vars3': (ax, ay, ta), 'm': mm}
    return _SYM


def hess_of(expr, vars_):
    S = sym_setup(); sp = S['sp']
    g = [sp.diff(expr, v) for v in vars_]
    H = [[sp.diff(gi, v) for v in vars_] for gi in g]
    f_g = sp.lambdify(vars_ + (S['m'],), g, 'mpmath'); f_H = sp.lambdify(vars_ + (S['m'],), H, 'mpmath')
    return f_g, f_H


_HC = {}


def row_second_order(r, poses, m):
    """(grad over the 33 pose coordinates as a dict slot->float, y^T H y as a function) for row r at the point:
    returns (gslots, Hfun) where Hfun(yvec) = y^T H y, using the branch signs at the point; kink rows flagged."""
    S = sym_setup(); sp = S['sp']; ax, ay, ta, bx, by, tb = S['vars6']; mm = S['m']
    mp.dps = 30
    if r.kind == 'pair':
        own, oth, k = r.meta
        n0 = N0[k]
        n = (n0[0] * sp.cos(ta) - n0[1] * sp.sin(ta), n0[0] * sp.sin(ta) + n0[1] * sp.cos(ta))
        D = ta - tb + (k - 1) * sp.pi / 2
        Dv = poses[own][2] - poses[oth][2] + (k - 1) * math.pi / 2
        sc, ss = math.copysign(1, math.cos(Dv)), math.copysign(1, math.sin(Dv))
        kinkD = min(abs(math.cos(Dv)), abs(math.sin(Dv))) < 1e-9
        h = (sc * sp.cos(D) + ss * sp.sin(D)) / 2
        expr = n[0] * (bx - ax) + n[1] * (by - ay) - sp.Rational(1, 2) - h
        key = ('pair', k, sc, ss)
        if key not in _HC:
            _HC[key] = hess_of(expr, S['vars6'])
        fg, fH = _HC[key]
        pt = (poses[own][0], poses[own][1], poses[own][2], poses[oth][0], poses[oth][1], poses[oth][2], m)
        slots = [3 * own, 3 * own + 1, 3 * own + 2, 3 * oth, 3 * oth + 1, 3 * oth + 2]
        kink = (own, oth) if kinkD else None
    elif r.kind == 'wall':
        i, name = r.meta
        th = poses[i][2]; sc, ss = math.copysign(1, math.cos(th)), math.copysign(1, math.sin(th))
        kinkD = min(abs(math.cos(th)), abs(math.sin(th))) < 1e-9
        h = (sc * sp.cos(ta) + ss * sp.sin(ta)) / 2
        expr = {'left': ax - h, 'bottom': ay - h, 'right': mm - ax - h, 'top': mm - ay - h}[name]
        key = ('wall', name, sc, ss)
        if key not in _HC:
            _HC[key] = hess_of(expr, S['vars3'])
        fg, fH = _HC[key]
        pt = (poses[i][0], poses[i][1], poses[i][2], m); slots = [3 * i, 3 * i + 1, 3 * i + 2]
        kink = (i, None) if kinkD else None
    else:
        i, c2, ctag = r.meta
        sx, sy, fx, fy = FR[c2]
        ox = mm if fx else 0; oy = mm if fy else 0
        if ctag.startswith('V'):
            kk = int(ctag[1:2]); dx, dy = ((-1, -1), (1, -1), (1, 1), (-1, 1))[kk]
            px = ax + (dx * sp.cos(ta) - dy * sp.sin(ta)) / 2; py = ay + (dx * sp.sin(ta) + dy * sp.cos(ta)) / 2
            expr = sx * (px - ox) if ctag.endswith('x') else sy * (py - oy)
            key = ('V', c2, ctag)
        else:
            kk = int(ctag[1:]); n0 = N0[kk]
            n = (n0[0] * sp.cos(ta) - n0[1] * sp.sin(ta), n0[0] * sp.sin(ta) + n0[1] * sp.cos(ta))
            nf = (-sx * n[0], -sy * n[1]); cf = (sx * (ax - ox), sy * (ay - oy))
            expr = (cf[0] * nf[0] + cf[1] * nf[1] - sp.Rational(1, 2)) / (nf[0] + nf[1])
            key = ('E', c2, kk)
        if key not in _HC:
            _HC[key] = hess_of(expr, S['vars3'])
        fg, fH = _HC[key]
        pt = (poses[i][0], poses[i][1], poses[i][2], m); slots = [3 * i, 3 * i + 1, 3 * i + 2]
        kink = None
    g = [float(v) for v in fg(*pt)]; Hm = [[float(v) for v in row] for row in fH(*pt)]
    return dict(zip(slots, g)), (slots, np.array(Hm)), kink


def second_order_test(rows, y, poses, m, n, Qrows_strict):
    """Along the flat direction y (all rows >= 0 at first order): E = rows with first-order rate |.| < 1e-9.
    LP in w: <g_k, w> + y^T H_k y - kink_k(w) >= tau for k in E (and the depth rows of Q must have the second-order
    rate > 0 when their first-order rate is 0); max tau, |w| <= 1e3."""
    E = []
    for r in rows:
        v = r.value(list(y), [0.0] * n)
        if abs(v) < 1e-9:
            E.append(r)
    if not E:
        return {'E': 0, 'verdict': 'no zero-rate rows: first-order direction'}
    NW = 3 * n
    kinks = sorted({k for r in E for k in [row_second_order(r, poses, m)[2]] if k is not None})
    kidx = {kk: NW + i for i, kk in enumerate(kinks)}; N = NW + len(kinks)
    A_ub, b_ub, A_eq = [], [], []
    tags = []
    for r in E:
        g, (slots, Hm), kink = row_second_order(r, poses, m)
        yv = np.array([y[s] for s in slots]); q = float(yv @ Hm @ yv)
        row = [0.0] * (2 * N + 1)
        for s, gv in g.items():
            row[s] -= gv; row[N + s] += gv
        if kink is not None:
            ia, ib = kink; s = kidx[kink]
            row[s] += 0.5; row[N + s] += 0.5          # -|u|/2 with u = w_b - w_a (u = 0 - w_a for a wall)
        row[2 * N] = 1.0
        A_ub.append(row); b_ub.append(q); tags.append((r.tag, q))
    for (ia, ib), s in kidx.items():
        row = [0.0] * (2 * N + 1); row[s] = 1.0; row[N + s] = -1.0
        if ib is not None:
            row[3 * ib + 2] -= 1.0; row[N + 3 * ib + 2] += 1.0
        row[3 * ia + 2] += 1.0; row[N + 3 * ia + 2] -= 1.0
        A_eq.append(row)
    res = linprog(c=[0.0] * (2 * N) + [-1.0], A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq) if A_eq else None,
                  b_eq=np.zeros(len(A_eq)) if A_eq else None, bounds=[(0, 1e3)] * (2 * N) + [(None, 1e3)], method='highs')
    tau = float(-res.fun) if res.status == 0 else -math.inf
    return {'E': len(E), 'E_tags': tags[:40], 'tau': tau, 'second_order_escape': bool(tau > 1e-9),
            'verdict': ('second-order escape along the flat direction (tau=%.3e)' % tau) if tau > 1e-9 else 'blocked at second order along the flat direction (tau=%.3e)' % tau}


# ============================================================================ T1 flush geometry
def flush_contacts(poses, m, tol=1e-7):
    """Edge-on-edge contacts of positive length: parallel touching edges and the overlap of their projections."""
    n = len(poses); V = [verts(*p) for p in poses]; out = []
    for i in range(n):
        for j in range(i + 1, n):
            if sep(V[i], V[j]) >= tol:
                continue
            for a in range(4):
                for b in range(4):
                    p0, p1 = V[i][a], V[i][(a + 1) % 4]; q0, q1 = V[j][b], V[j][(b + 1) % 4]
                    e = (p1[0] - p0[0], p1[1] - p0[1]); f = (q1[0] - q0[0], q1[1] - q0[1])
                    cr = e[0] * f[1] - e[1] * f[0]
                    if abs(cr) > 1e-6:
                        continue
                    nx, ny = -e[1], e[0]
                    dist = abs((q0[0] - p0[0]) * nx + (q0[1] - p0[1]) * ny)
                    if dist > tol:
                        continue
                    t = [((q[0] - p0[0]) * e[0] + (q[1] - p0[1]) * e[1]) for q in (q0, q1)]
                    L = max(0.0, min(1.0, max(t)) - max(0.0, min(t)))
                    if L > 1e-6:
                        out.append({'pair': (i, j), 'edge_i': a, 'edge_j': b, 'length': L, 'gap': sep(V[i], V[j]),
                                    'segment': [(p0[0] + max(0.0, min(t)) * e[0], p0[1] + max(0.0, min(t)) * e[1]),
                                                (p0[0] + min(1.0, max(t)) * e[0], p0[1] + min(1.0, max(t)) * e[1])]})
    for i in range(n):
        for (name, dfn, nrm) in (('left', lambda p: p[0], (1, 0)), ('bottom', lambda p: p[1], (0, 1)), ('right', lambda p: m - p[0], (-1, 0)), ('top', lambda p: m - p[1], (0, -1))):
            on = [p for p in V[i] if dfn(p) < tol]
            if len(on) == 2:
                out.append({'pair': (i, name), 'length': math.hypot(on[0][0] - on[1][0], on[0][1] - on[1][1]), 'gap': 0.0, 'segment': [on[0], on[1]]})
    return out


def gordan_support(G, Q, cn, n):
    """Motzkin multipliers (single square, strict rows) at the point box: mu >= 0, sum over strict = 1, the
    combination's coefficient boxes contain 0.  Returns the support with weights, or None if unheld."""
    rows = field_rows(G, {Q}, Q, cn, weak_rows=False)
    slots = [3 * Q, 3 * Q + 1, 3 * Q + 2]
    K = len(rows)
    A_ub, b_ub = [], []
    for j in slots:
        lo_row = []; hi_row = []
        for r in rows:
            c = I(0)
            for (s, cc) in r.terms:
                if s == j:
                    c = c + cc
            if r.kink is not None and j == 3 * Q + 2:
                c = c - r.kink[2]
            lo_row.append(lo(c)); hi_row.append(hi(c))
        A_ub.append(lo_row); b_ub.append(0.0)            # sum mu lo <= 0
        A_ub.append([-v for v in hi_row]); b_ub.append(0.0)  # sum mu hi >= 0
    A_eq = [[1.0 if r.strict else 0.0 for r in rows]]
    res = linprog(c=[0.0] * K, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=[1.0], bounds=[(0, None)] * K, method='highs')
    if res.status != 0:
        return None
    return [(rows[k].tag, float(res.x[k])) for k in range(K) if res.x[k] > 1e-9]


# ============================================================================ driver
def cluster_menu_ex2(F, untouched, poses):
    V = [verts(*p) for p in poses]
    adj = {i: set() for i in untouched}
    for i in untouched:
        for j in untouched:
            if i < j and sep(V[i], V[j]) < 5e-3:
                adj[i].add(j); adj[j].add(i)
    out = [frozenset(F)]
    nb = set(F)
    for f in F:
        nb |= adj[f]
    out.append(frozenset(nb))
    comp, front = set(F), list(F)
    while front:
        x = front.pop(); [(comp.add(y), front.append(y)) for y in adj[x] if y not in comp]
    out.append(frozenset(comp)); out.append(frozenset(untouched))
    seen, res = set(), []
    for C in out:
        if C not in seen:
            seen.add(C); res.append(C)
    return res


def run(name, poses, m, radii, nsamp, rng, a128, do_second=True):
    n = len(poses)
    log('=== %s side %.9f' % (name, m))
    geoms = Geoms(poses, m)
    out = {'packing': name, 'side': m, 'radii': radii, 'nsamp': nsamp}
    out['flush_contacts'] = flush_contacts(poses, m)
    log('  flush contacts (edge-on-edge, positive length): %s' % [(f['pair'], round(f['length'], 6)) for f in out['flush_contacts']])
    meet = {cn: meeters(poses, m, cn) for cn in CORNERS}
    out['meeters'] = {k: [(i, d) for i, d in v] for k, v in meet.items()}
    G8 = geoms.get(1e-8, False); Gx = geoms.get(0.0, False)
    out['corners'] = {}
    for cn in CORNERS:
        pm = geoms.get(radii[0], False).possible_meeters(cn)
        crec = {'possible_meeters_box': pm, 'subjects': {}}
        for Q in pm:
            d = dict(meet[cn]).get(Q, 0.0)
            srec = {'depth_point': d, 'tilt_deg': math.degrees(poses[Q][2]) % 90.0}
            # point tests
            srec['ROT_gordan_support'] = gordan_support(G8, Q, cn, n)
            rows8 = field_rows(G8, set(range(n)), Q, cn, weak_rows=False)
            t8, y8 = robust_lp(rows8, 3 * n)
            srec['FIELD_point_strict'] = {'lp_t': t8, 'unheld': bool(t8 > 1e-10)}
            wc, wrows = weak_cone(G8, Q, cn, n)
            srec['weak_cone'] = {k: v for k, v in wc.items() if k not in ('y', 'flat_y')}
            if wc['max_depth_rate'] < 0:
                srec['weak_cone']['note'] = 'no depth row: the square cannot intrude the corner on the 1e-8 point box (tangent square)'
            if do_second and 0 <= wc['max_depth_rate'] <= 1e-6:
                yflat = wc.get('y') if wc['max_depth_rate'] > 1e-9 else wc.get('flat_y')
                if yflat is not None and not wc.get('isolated', False):
                    try:
                        srec['second_order'] = second_order_test(wrows, np.array(yflat), poses, m, n, None)
                    except Exception as e:
                        srec['second_order'] = {'error': repr(e)}
            # FIELD on boxes, largest first
            srec['FIELD_box'] = {'certified_radius': None}
            for r in radii:
                c1 = certify_field(poses, m, r, set(range(n)), Q, cn, nsamp, rng, geoms)
                if c1['certified']:
                    srec['FIELD_box'] = {'certified_radius': r, **c1}; break
                srec['FIELD_box'].setdefault('fail', {})[str(r)] = {k: c1.get(k) for k in ('lp_t', 'min_strict', 'worst_strict', 'min_weak', 'worst_weak')}
            # single-square weak-row ROT for comparison
            srec['ROTW_box'] = {'certified_radius': None}
            for r in radii:
                c1 = certify_field(poses, m, r, {Q}, Q, cn, nsamp, rng, geoms)
                if c1['certified']:
                    srec['ROTW_box'] = {'certified_radius': r, 'lp_t': c1['lp_t'], 'min_strict': c1['min_strict'], 'sample': c1.get('sample')}; break
            crec['subjects'][str(Q)] = srec
            log('  %s sq%d d=%.3e tilt %.3f | FIELD point strict t=%.2e | weak cone: rate %.2e isolated %s | 2nd: %s | FIELD box r=%s | ROT-W box r=%s | Gordan %s' % (
                cn, Q, d, srec['tilt_deg'], t8, wc['max_depth_rate'], wc.get('isolated'), srec.get('second_order', {}).get('verdict', '-'),
                srec['FIELD_box']['certified_radius'], srec['ROTW_box']['certified_radius'], [(t, round(w, 3)) for t, w in (srec['ROT_gordan_support'] or [])]))
        # EX2
        ex = a128['exchange'].get(cn, {}) if a128 else {}
        if len(pm) == 2 and ex.get('Q0_frame'):
            A, Qi = pm
            crec['EX2'] = certify_ex2(poses, m, cn, A, Qi, tuple(ex['Q0_frame']), radii, nsamp, rng, geoms, lambda F, U: [frozenset(U)])
            crec['EX2']['A128_point_margin'] = ex.get('best_refit_margin_point'); crec['EX2']['A128_certified_radius'] = ex.get('certified_radius')
            log('  EX2 %s: %s' % (cn, crec['EX2'].get('best', {}).get('verdict', [t.get('verdict') for t in crec['EX2']['tried']])))
            for t_ in crec['EX2']['tried']:
                log('     r=%g flush set %s margins %s -> %s' % (t_['r'], t_['flush_set'], t_.get('flush_margins'), t_.get('verdict')))
        else:
            crec['EX2'] = {'verdict': 'n/a (%d possible meeters)' % len(pm)}
        out['corners'][cn] = crec
    return out


def main():
    args = sys.argv[1:]
    radii = [1e-3, 1e-4, 1e-5, 1e-6]; nsamp = 10000; names = []; do_second = True
    i = 0
    while i < len(args):
        if args[i] == '--radii':
            radii = [float(x) for x in args[i + 1].split(',')]; i += 2
        elif args[i] == '--nsamp':
            nsamp = int(args[i + 1]); i += 2
        elif args[i] == '--no-second':
            do_second = False; i += 1
        else:
            names.append(args[i]); i += 1
    S = gm.load_sample()
    if names:
        S = [s for s in S if s['name'] in names]
    a128 = {}
    for line in open(os.path.join(gm.A128, 'results', 'moves128.jsonl'), encoding='utf-8'):
        if line.strip():
            o = json.loads(line); a128[o['packing']] = o
    rng = np.random.default_rng(130)
    jl = open(os.path.join(RES, 'moves130.jsonl'), 'a', encoding='utf-8')
    for s in S:
        poses = [(cx, cy, gm.snap_tilt(th)) for (cx, cy, th) in s['poses']]
        t0 = time.time()
        o = run(s['name'], poses, s['side'], radii, nsamp, rng, a128.get(s['name']), do_second)
        o['seconds'] = time.time() - t0
        jl.write(json.dumps(o) + '\n'); jl.flush()
        log('  [%s done in %.0f s]' % (s['name'], o['seconds']))
    log('all done')


if __name__ == '__main__':
    main()
