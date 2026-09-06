r"""lockw105.py -- A105: the LOCKED census.  For every intruder of every strictly K0-BLOCKED packing on
disk (A102's corpus, A103's loader) plus Trump, three first-order tests, all consequences of Psi-minimality
(docs/proofs/lockfree.md s.1):

  (R) HELD  -- Lemma ROT (A103): no rigid motion y=(v,w) of the square alone STRICTLY opens every active
               contact row and strictly decreases the corner depth.  lock103's LP, re-run here verbatim.
  (W) W-HELD -- Lemma ROT-W (A105): no TRANSLATION v of the square alone with every active contact row
               rate >= 0 (WEAK) and depth strictly decreasing.  Weak rows are exact for translations (rows
               are affine in the centres, Fact A of nocrit_k0_blocked.md), so a W-unheld square is moved by
               a small translation to a packing of smaller Psi.  Farkas form: -e in cone{n_k} (forces only).
  (C) the cone certificate of a held square: multipliers mu_k >= 0 on the contact rows and lambda_p >= 0 on
      the virtual rows with sum = 0; PUSHED if a certificate with sum lambda = 1 exists (Lemma LINE: the
      contacts' resultant is the corner-ward force along a line through the argmin set), WEDGED otherwise
      (lambda = 0 self-stress only).

LOCKED := HELD and W-HELD.  Conventions: contacts at SAT gap < 1e-7, meet bar 1e-9, LP strictness 1e-7,
finite-motion confirmation eps = min(1e-6, gmin/10) (A102/A103).  Pure geometry, one process, BLAS pinned,
seconds.  Writes only under attempts/A105-lockfree/{results,logs}.  Usage: python lockw105.py
"""
from __future__ import annotations
import os, sys, json, math, time, itertools
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
from decimal import Decimal
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A105 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(A105))
ATT = os.path.join(ROOT, 'attempts')
A87R = os.path.join(ATT, 'A87-drain-flow', 'results')
RES = os.path.join(A105, 'results'); LOGS = os.path.join(A105, 'logs')
os.makedirs(RES, exist_ok=True); os.makedirs(LOGS, exist_ok=True)
CONTACT_TOL, MEET_TOL, ARG_TOL, DIAG_TOL, TSTRICT, EPS_MOVE = 1e-7, 1e-9, 1e-9, 1e-9, 1e-7, 1e-6
CORNERS = ('BL', 'BR', 'TR', 'TL')
FSGN = {'BL': (1.0, 1.0), 'BR': (-1.0, 1.0), 'TR': (-1.0, -1.0), 'TL': (1.0, -1.0)}
WALLS = {'bottom': ('BL', 'BR'), 'right': ('BR', 'TR'), 'top': ('TR', 'TL'), 'left': ('TL', 'BL')}
T0 = time.time()
_fh = open(os.path.join(LOGS, 'lockw105.log'), 'a', encoding='utf-8')
def log(*a):
    m = ' '.join(str(v) for v in a); print(m, flush=True); _fh.write('[%7.1f] %s\n' % (time.time() - T0, m)); _fh.flush()

# ---------------------------------------------------------------- geometry (A102/A103 conventions, copied)
def verts(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
def sep(p, q):
    best = -9.0
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]; ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey)
            ax, ay = -ey / n, ex / n
            pp = [x * ax + y * ay for x, y in p]; qq = [x * ax + y * ay for x, y in q]
            v = max(min(qq) - max(pp), min(pp) - max(qq))
            if v > best: best = v
    return best
def wall_gap(p, s):
    return min(min(x for x, y in p), min(y for x, y in p), s - max(x for x, y in p), s - max(y for x, y in p))
def worst_gap_one(poses, i, newpose, s):
    p = verts(*newpose); worst = wall_gap(p, s)
    for j, q in enumerate(poses):
        if j == i: continue
        g = sep(p, verts(*q))
        if g < worst: worst = g
    return worst
def frame_map(cn, s):
    ox, oy = (0.0, 0.0) if cn == 'BL' else (s, 0.0) if cn == 'BR' else (s, s) if cn == 'TR' else (0.0, s)
    sx, sy = FSGN[cn]
    return (lambda p: (sx * (p[0] - ox), sy * (p[1] - oy))), (sx, sy)
def argmin_data(sq, cn, s):
    fm, _ = frame_map(cn, s); W = [fm(v) for v in verts(*sq)]; cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]; d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t)); cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    vals = [max(p[0], p[1]) for p in cand]; mu = min(vals); ext = []
    for p, v in zip(cand, vals):
        if v <= mu + ARG_TOL and not any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for q in ext): ext.append(p)
    return mu, max(0.0, 1.0 - mu), ext, W
def corner_depth(sq, cn, s): return argmin_data(sq, cn, s)[1]
def meeters(poses, s, cn, tol=MEET_TOL):
    out = [(i, corner_depth(q, cn, s)) for i, q in enumerate(poses)]
    return sorted([(i, d) for i, d in out if d > tol], key=lambda t: -t[1])
def _edge_normal_out(a, b, oc):
    ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey); nx, ny = -ey / n, ex / n
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    if (mx - oc[0]) * nx + (my - oc[1]) * ny < 0: nx, ny = -nx, -ny
    return nx, ny
def contacts_of(poses, i, s, tol=CONTACT_TOL):
    P = poses[i]; A = verts(*P); out = []
    for j, q in enumerate(poses):
        if j == i: continue
        B = verts(*q)
        if sep(A, B) >= tol: continue
        pairs = []
        for (V, E, own, sign) in ((A, B, q, +1.0), (B, A, P, -1.0)):
            for v in V:
                for k in range(4):
                    a, b = E[k], E[(k + 1) % 4]; ex, ey = b[0] - a[0], b[1] - a[1]; L = ex * ex + ey * ey
                    t = max(0.0, min(1.0, ((v[0] - a[0]) * ex + (v[1] - a[1]) * ey) / L))
                    fx, fy = a[0] + t * ex, a[1] + t * ey; d = math.hypot(v[0] - fx, v[1] - fy)
                    if d < tol:
                        nx, ny = _edge_normal_out(a, b, (own[0], own[1]))
                        pairs.append(((v[0] + fx) / 2.0, (v[1] + fy) / 2.0, sign * nx, sign * ny, d))
        for (px, py, fx, fy, d) in pairs:
            if not any(abs(c['point'][0] - px) < 1e-6 and abs(c['point'][1] - py) < 1e-6 and c['F'][0] * fx + c['F'][1] * fy > 1.0 - 1e-6 for c in out):
                out.append({'with': 'square %d' % j, 'j': j, 'point': (px, py), 'F': (fx, fy), 'gap': sep(A, B)})
    walls = (('left wall', min(x for x, y in A), (1.0, 0.0), lambda v: v[0]), ('bottom wall', min(y for x, y in A), (0.0, 1.0), lambda v: v[1]),
             ('right wall', s - max(x for x, y in A), (-1.0, 0.0), lambda v: s - v[0]), ('top wall', s - max(y for x, y in A), (0.0, -1.0), lambda v: s - v[1]))
    for name, gap, nrm, dfn in walls:
        if gap < tol:
            for v in A:
                if dfn(v) < tol: out.append({'with': name, 'j': None, 'point': (v[0], v[1]), 'F': nrm, 'gap': gap})
    return out
def virtual_rows(sq, cn, s):
    mu, d, ext, _ = argmin_data(sq, cn, s); fm, (sx, sy) = frame_map(cn, s); c_f = fm((sq[0], sq[1])); out = []
    for p in ext:
        rx, ry = p[0] - c_f[0], p[1] - c_f[1]
        gx = (sx, 0.0, -sx * sy * ry); gy = (0.0, sy, sx * sy * rx)
        if abs(p[0] - p[1]) < DIAG_TOL: rows, kind = [gx, gy], 'diagonal'
        elif p[0] > p[1]: rows, kind = [gx], 'X'
        else: rows, kind = [gy], 'Y'
        out.append({'p_frame': p, 'kind': kind, 'rows': rows})
    return mu, d, out

# ---------------------------------------------------------------- the three tests
def lp_max_t(rows_strict, rows_weak, nvar):
    """max t s.t. r.y >= t (strict rows), r.y >= 0 (weak rows), |y|_inf <= 1."""
    if not rows_strict: return 1.0, np.zeros(nvar)
    A_ub, b_ub = [], []
    for r in rows_strict: A_ub.append([-r[k] for k in range(nvar)] + [1.0]); b_ub.append(0.0)
    for r in rows_weak: A_ub.append([-r[k] for k in range(nvar)] + [0.0]); b_ub.append(0.0)
    res = linprog(c=[0] * nvar + [-1.0], A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(-1, 1)] * nvar + [(None, 1.0)], method='highs')
    if res.status != 0: return -1.0, np.zeros(nvar)
    return float(-res.fun), np.array(res.x[:nvar])
def cone_certificate(A_rows, G):
    """mu >= 0 on contact rows, lam >= 0 on the virtual rows G, sum mu A + sum lam G = 0.  Returns
    ('pushed', mu, lam) with sum lam = 1 if possible, else ('wedged', mu, None) with sum mu = 1, else None."""
    nA, nG = len(A_rows), len(G)
    rows = list(A_rows) + list(G)
    for mode in ('pushed', 'wedged'):
        n = nA + nG if mode == 'pushed' else nA
        if n == 0: continue
        A_eq = [[rows[k][d] for k in range(n)] for d in range(3)]
        A_eq.append([0.0] * nA + [1.0] * nG if mode == 'pushed' else [1.0] * nA)
        b_eq = [0.0, 0.0, 0.0, 1.0]
        res = linprog(c=[0.0] * n, A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=[(0, None)] * n, method='highs')
        if res.status == 0:
            x = [float(v) for v in res.x]
            return (mode, x[:nA], x[nA:] if mode == 'pushed' else None)
    return None
def test_intruder(poses, s, cn, i):
    P = poses[i]; C = contacts_of(poses, i, s); A_rows = []
    for c in C:
        rx, ry = c['point'][0] - P[0], c['point'][1] - P[1]
        A_rows.append((c['F'][0], c['F'][1], rx * c['F'][1] - ry * c['F'][0]))
    mu, d, vr = virtual_rows(P, cn, s)
    choices = [x['rows'] for x in vr]
    A = verts(*P); gmin = 9.0
    for j, q in enumerate(poses):
        if j != i:
            g = sep(A, verts(*q))
            if CONTACT_TOL <= g < gmin: gmin = g
    for g in (min(x for x, y in A), min(y for x, y in A), s - max(x for x, y in A), s - max(y for x, y in A)):
        if CONTACT_TOL <= g < gmin: gmin = g
    eps = min(EPS_MOVE, gmin / 10.0)
    rec = {'square': i, 'corner': cn, 'depth': d, 'tilt_deg': math.degrees(P[2]) % 90.0,
           'argmin_kind': [v['kind'] for v in vr], 'n_contacts': len(C),
           'contacts': [{'with': c['with'], 'point': [round(v, 7) for v in c['point']], 'F': [round(v, 6) for v in c['F']], 'tau': round(A_rows[k][2], 6)} for k, c in enumerate(C)],
           'min_inactive_gap': float('%.3e' % gmin)}
    # (R) strict, full rigid motion (lock103 verbatim)
    bestR = None
    for combo in itertools.product(*[range(len(ch)) for ch in choices]):
        G = [choices[k][j] for k, j in enumerate(combo)]
        t, y = lp_max_t(list(A_rows) + G, [], 3)
        if bestR is None or t > bestR[0]: bestR = (t, y, G)
    tR, yR, GR = bestR; heldR = not (tR > TSTRICT)
    if not heldR:
        newpose = (P[0] + eps * yR[0], P[1] + eps * yR[1], P[2] + eps * yR[2])
        ok = worst_gap_one(poses, i, newpose, s) >= -1e-12 and (d - corner_depth(newpose, cn, s)) >= 0.99 * min(d, 0.5 * tR * eps)
        if not ok: heldR = True; rec['noteR'] = 'LP direction not confirmed by finite motion'
    rec['R_lp_t'] = float(tR); rec['held_R'] = bool(heldR)
    # (W) weak contact rows, translation only
    bestW = None
    for combo in itertools.product(*[range(len(ch)) for ch in choices]):
        G = [choices[k][j][:2] for k, j in enumerate(combo)]
        t, v = lp_max_t(G, [r[:2] for r in A_rows], 2)
        if bestW is None or t > bestW[0]: bestW = (t, v)
    tW, vW = bestW; heldW = not (tW > TSTRICT)
    if not heldW:
        newpose = (P[0] + eps * vW[0], P[1] + eps * vW[1], P[2])
        ok = worst_gap_one(poses, i, newpose, s) >= -1e-12 and (d - corner_depth(newpose, cn, s)) >= 0.99 * min(d, 0.5 * tW * eps)
        if not ok: heldW = True; rec['noteW'] = 'LP direction not confirmed by finite motion'
        else:
            lo, hi = 0.0, eps
            while hi < 2.0 and worst_gap_one(poses, i, (P[0] + hi * vW[0], P[1] + hi * vW[1], P[2]), s) >= -1e-11: lo, hi = hi, 2 * hi
            if hi < 2.0:
                for _ in range(50):
                    mid = 0.5 * (lo + hi)
                    if worst_gap_one(poses, i, (P[0] + mid * vW[0], P[1] + mid * vW[1], P[2]), s) < -1e-11: hi = mid
                    else: lo = mid
            dend = corner_depth((P[0] + lo * vW[0], P[1] + lo * vW[1], P[2]), cn, s)
            rec['W_room'] = {'travel': lo, 'depth_at_end': dend, 'exits_cell': bool(dend <= MEET_TOL)}
    rec['W_lp_t'] = float(tW); rec['W_dir'] = [float(v) for v in vW]; rec['held_W'] = bool(heldW)
    rec['locked'] = bool(heldR and heldW)
    # (C) cone certificate for the strict system (mode of holding)
    if heldR:
        cert = cone_certificate(A_rows, GR)
        rec['hold_mode'] = cert[0] if cert else 'none(LP tol)'
        if cert:
            rec['cert_mu'] = [round(v, 6) for v in cert[1]]
            rec['cert_lambda'] = [round(v, 6) for v in cert[2]] if cert[2] is not None else None
    return rec

def load_corpus():
    C = []
    d = json.load(open(os.path.join(A87R, 'k0dir2_87.records.json')))
    for k, v in sorted(d['floors'].items()):
        if not v.get('poses'): continue
        s = float(Fraction(v['container_side_exact']))
        P = [(float(Fraction(p['cx_exact'])), float(Fraction(p['cy_exact'])), float(Fraction(p['theta_exact']))) for p in v['poses']]
        C.append({'name': 'floor_%s_%s' % (k, v['tag']), 'side': s, 'poses': P})
    dd = json.load(open(os.path.join(A87R, 'k0dir87.json'))); rec = dd['record_K0_BLOCKED_packing']; z = [Fraction(a) for a in rec['z']]
    C.append({'name': 'record_%s' % rec['tag'], 'side': float(z[33]), 'poses': [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(11)]})
    for i, line in enumerate(open(os.path.join(A87R, 'k0dir87.polish.jsonl'))):
        r = json.loads(line)
        if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'): continue
        z = [Fraction(a) for a in r['z_polished']]
        C.append({'name': 'polish%02d_%s' % (i, r['tag']), 'side': float(z[33]), 'poses': [(float(z[3 * j]), float(z[3 * j + 1]), float(z[3 * j + 2])) for j in range(11)]})
    df = json.load(open(os.path.join(A87R, 'd2front87.json')))
    src_list = [('own_side_anchored', df['own_side_anchored'])] + [('cap' + k, v) for k, v in sorted(df['per_cap_anchored'].items())]
    seen = set(); n = 0
    for src, v in src_list:
        if not v.get('anchored_only'): continue
        for c in v.get('candidates', []):
            key = tuple(c['z'])
            if key in seen: continue
            seen.add(key); z = [Fraction(a) for a in c['z']]
            C.append({'name': 'anchored%d_%s' % (n, c['tag']), 'side': float(z[33]), 'poses': [(float(z[3 * j]), float(z[3 * j + 1]), float(z[3 * j + 2])) for j in range(11)]}); n += 1
    t = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')))
    C.append({'name': 'TRUMP_canary', 'side': float(Fraction(Decimal(t['s']))),
              'poses': [(float(Fraction(Decimal(q['cx']))), float(Fraction(Decimal(q['cy']))), float(Fraction(Decimal(q['theta'])))) for q in t['squares']]})
    return C

def main():
    C = load_corpus(); outs = []
    jl = open(os.path.join(RES, 'lockw105.jsonl'), 'w', encoding='utf-8')
    for c in C:
        poses, s = c['poses'], c['side']; rows = []
        for cn in CORNERS:
            M = meeters(poses, s, cn)
            for (i, d) in M:
                r = test_intruder(poses, s, cn, i); r['is_second_meeter'] = bool((i, d) == min(M, key=lambda t: t[1])); rows.append(r)
        mc = {cn: len(meeters(poses, s, cn)) for cn in CORNERS}
        walls = {}
        for w, (c1, c2) in WALLS.items():
            rr = [r for r in rows if r['corner'] in (c1, c2)]
            walls[w] = {'both_blocked': mc[c1] >= 2 and mc[c2] >= 2, 'n_intruders': len(rr),
                        'all_locked': all(r['locked'] for r in rr), 'all_held_R': all(r['held_R'] for r in rr),
                        'unlocked': ['%s sq%d(%s)' % (r['corner'], r['square'], 'R' if not r['held_R'] else 'W') for r in rr if not r['locked']]}
        o = {'packing': c['name'], 'side': s, 'meet_counts': mc, 'K0_BLOCKED': all(v >= 2 for v in mc.values()),
             'n_intruders': len(rows), 'n_held_R': sum(r['held_R'] for r in rows), 'n_held_W': sum(r['held_W'] for r in rows),
             'n_locked': sum(r['locked'] for r in rows),
             'unlocked': [{'corner': r['corner'], 'square': r['square'], 'depth': r['depth'], 'second': r['is_second_meeter'],
                           'fails': ('R' if not r['held_R'] else '') + ('W' if not r['held_W'] else ''), 'W_lp_t': r['W_lp_t'], 'R_lp_t': r['R_lp_t'],
                           'W_room': r.get('W_room')} for r in rows if not r['locked']],
             'hold_modes': {'%s sq%d' % (r['corner'], r['square']): r.get('hold_mode') for r in rows if r['held_R']},
             'locked_walls_both_blocked': [w for w, v in walls.items() if v['both_blocked'] and v['all_locked']],
             'heldR_walls_both_blocked': [w for w, v in walls.items() if v['both_blocked'] and v['all_held_R']],
             'walls': walls, 'rows': rows}
        outs.append(o); jl.write(json.dumps(o) + '\n'); jl.flush()
        log('%-28s side %.7f blocked %s intr %d heldR %d heldW %d LOCKED %d | locked walls %s | heldR walls %s' % (
            c['name'], s, o['K0_BLOCKED'], o['n_intruders'], o['n_held_R'], o['n_held_W'], o['n_locked'], o['locked_walls_both_blocked'], o['heldR_walls_both_blocked']))
        for u in o['unlocked']:
            log('    UNLOCKED %s sq%d d=%.3e second=%s fails=%s W_t=%.2e R_t=%.2e room=%s' % (u['corner'], u['square'], u['depth'], u['second'], u['fails'], u['W_lp_t'], u['R_lp_t'], (u['W_room'] or {}).get('exits_cell')))
        for k, v in o['hold_modes'].items():
            if v == 'wedged': log('    WEDGED (held only by a self-stress, lambda = 0): %s' % k)
    summ = {'conventions': {'contact_bar': CONTACT_TOL, 'meet_bar': MEET_TOL, 'lp_strict': TSTRICT},
            'packings': len(outs),
            'blocked_all_locked': [o['packing'] for o in outs if o['K0_BLOCKED'] and o['n_locked'] == o['n_intruders']],
            'blocked_all_held_R': [o['packing'] for o in outs if o['K0_BLOCKED'] and o['n_held_R'] == o['n_intruders']],
            'per_packing': [{k: o[k] for k in ('packing', 'side', 'K0_BLOCKED', 'n_intruders', 'n_held_R', 'n_held_W', 'n_locked', 'unlocked', 'hold_modes', 'locked_walls_both_blocked', 'heldR_walls_both_blocked')} for o in outs],
            'walls_both_blocked_all_locked': {o['packing']: o['locked_walls_both_blocked'] for o in outs if o['K0_BLOCKED']},
            'trump': next(({'n_intruders': o['n_intruders'], 'n_locked': o['n_locked'], 'hold_modes': o['hold_modes']} for o in outs if o['packing'] == 'TRUMP_canary'), None)}
    json.dump(summ, open(os.path.join(RES, 'lockw105.json'), 'w', encoding='utf-8'), indent=1)
    log('summary:', json.dumps({k: v for k, v in summ.items() if k != 'per_packing'}))

if __name__ == '__main__':
    main()
