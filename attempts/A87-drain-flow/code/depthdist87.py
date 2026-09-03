"""depthdist87.py -- A87 chore: HOW DEEP do the intruders of a K0-BLOCKED packing get?

Question.  In a K0-BLOCKED packing (every one of the four open unit corner slots
met by >= 2 squares) let, per corner c,

    d1(c) = intrusion depth of the DEEPEST intruder of c
    d2(c) = intrusion depth of the SECOND-deepest intruder of c

with A89's definition (attempts/A89-tilt-floor/code/t2b_depth.py)

    depth(Q) = 1 - f_min_max(Q)   in the corner frame,
    f_min_max(Q) = min over Q of max(x, y),

so depth in (0, 1]: depth > 0 <=> Q meets the open unit slot, depth = 1 <=> Q
reaches the corner point itself.  Is there a packing where ALL FOUR corners are
deep (min_c d1(c) large), and if so at what side sigma?

Data / exactness
  (1) the exact-verified K0-BLOCKED packings of the 520 directed flows
      (results/k0dir87.{json,polish.jsonl}).  Those are the ONLY A87 rows that
      carry a rational z AND an exact K0-BLOCKED verdict: the record packing
      s0115 at sigma 3.985483724948 plus the 4 stuck confined endpoints.  For
      each, z is 34 EXACT rationals, so depth is computed in outward-rounded
      mpmath interval arithmetic on that rational input (the only inexactness is
      cos/sin of a rational angle): every depth below is a CERTIFIED enclosure,
      and the reported width is the certificate.  The blocker set per corner is
      k0dir87's own sound INNER-slot certified blocker list, re-derived here.
  (2) the A85 4-corner gate samples (A85/results/a85_gate_samples.json,
      sample_records.c4, 200 nodes, 30 attemptable).  A node assigns each corner
      a PAIR of cover boxes; the box-level UPPER bound on d1(c) is
      max over the corner's two boxes of t2b_depth's depth_ub(box), which is
      sound over the whole box (exact in (c_x, c_y) by monotonicity of
      f_min_max, Lipschitz-slacked in theta).  depth is defined in the CORNER
      frame and A85's corner maps are the D4 isometries BL-frame -> c-frame, so
      depth_ub of a box index is the same number at every corner.

Canary: Trump (sigma = s_hat).  BL / BR / TR each hold ONE flush slot square, so
d1 = 1 exactly there and d2 does not exist; TL is the genuine 2-crowd with
d1 = 0.168321 (squares 4 / 6).  Same code path, no special casing.

One process, BLAS pinned.  Writes only results/depthdist87.{jsonl,json} and
notes/depthdist87.md.  Usage: python depthdist87.py {selftest|run|report|all}
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ.setdefault(_v, "1")

import json
import math
import time
from fractions import Fraction

import numpy as np
from mpmath import iv

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A87, '..'))
A85 = os.path.join(ATT, 'A85-k0-route')
A89 = os.path.join(ATT, 'A89-tilt-floor')

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A85, 'code'))
sys.path.insert(0, os.path.join(A89, 'code'))

import t3lib as T                 # noqa: E402
import k0blocked87 as KB          # noqa: E402
import k0dir87 as KD              # noqa: E402

RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')

OUT_JL = os.path.join(RESULTS, 'depthdist87.jsonl')
OUT_JS = os.path.join(RESULTS, 'depthdist87.json')
OUT_MD = os.path.join(NOTES, 'depthdist87.md')

CORNERS = ('BL', 'BR', 'TL', 'TR')
DELTAS = (0.3, 0.5, 0.7, 0.9)
N = 11
HALFPI = math.pi / 2.0
DPS_LADDER = (40, 80, 160)
TILT_BINS = [('exactly 0', -1.0, 1e-9), ('(0,1e-6]', 1e-9, 1e-6),
             ('(1e-6,1e-3]', 1e-6, 1e-3), ('(1e-3,0.1]', 1e-3, 0.1),
             ('(0.1,1]', 0.1, 1.0), ('(1,5]', 1.0, 5.0), ('(5,15]', 5.0, 15.0),
             ('(15,30]', 15.0, 30.0), ('(30,45]', 30.0, 45.0001)]
DEPTH_BINS = [('[0,0.1)', 0.0, 0.1), ('[0.1,0.3)', 0.1, 0.3),
              ('[0.3,0.5)', 0.3, 0.5), ('[0.5,0.7)', 0.5, 0.7),
              ('[0.7,0.9)', 0.7, 0.9), ('[0.9,1)', 0.9, 1.0 - 1e-12),
              ('=1 (corner reached)', 1.0 - 1e-12, 2.0)]


def _bin(v, bins):
    for nm, a, b in bins:
        if a <= v < b:
            return nm
    return bins[-1][0]


# ==================================================== certified corner depth

def _ivlo(x):
    """float <= the exact lower endpoint (outward rounded)."""
    q = KB._lo_frac(x)
    f = float(q)
    return f if Fraction(f) <= q else math.nextafter(f, -math.inf)


def _ivhi(x):
    q = KB._hi_frac(x)
    f = float(q)
    return f if Fraction(f) >= q else math.nextafter(f, math.inf)


def frame(px, py, corner, xlo, xhi, ylo, yhi):
    """corner frame: the corner goes to the origin, the unit slot to [0,1]^2."""
    if corner == 'BL':
        return px - xlo, py - ylo
    if corner == 'BR':
        return xhi - px, py - ylo
    if corner == 'TL':
        return px - xlo, yhi - py
    return xhi - px, yhi - py


def f_minmax_iv(Q):
    """Certified enclosure of min over the quad Q of max(x, y).

    max(x,y) restricted to an edge is a max of two affine functions, hence
    convex: its minimum on the edge is at an endpoint, or at the interior
    crossing x = y.  The crossing is used only when the two endpoint values of
    d = x - y have CERTIFIED opposite signs (then |d0 - d1| >= |d0| + |d1| > 0
    and the division is safe).  When a sign is inconclusive that endpoint has
    x = y to within its own interval width w, and the crossing value differs
    from the endpoint value by at most w (slope of x and of y along the edge is
    bounded by the edge length <= sqrt 2, and |s*| <= w / |d0 - d1|), so the
    result is widened downwards by sqrt(2) * w.  Returns (interval, n_skipped).
    """
    best = None
    for k in range(4):
        v = T.iv_max(Q[k][0], Q[k][1])
        best = v if best is None else T.iv_min(best, v)
    skipped = 0
    for k in range(4):
        px, py = Q[k]
        qx, qy = Q[(k + 1) % 4]
        d0 = px - py
        d1 = qx - qy
        opp = (d0.b < 0 and d1.a > 0) or (d0.a > 0 and d1.b < 0)
        if opp:
            s = d0 / (d0 - d1)
            val = px + s * (qx - px)
            best = T.iv_min(best, val)
        else:
            if (d0.a <= 0 <= d0.b) or (d1.a <= 0 <= d1.b):
                w = max(float(d0.delta), float(d1.delta))
                pad = iv.mpf([-math.sqrt(2.0) * w, 0.0])
                best = best + pad
                skipped += 1
    return best, skipped


def tilt_deg_iv(th):
    """dist(theta, (pi/2) Z) in degrees, as a certified enclosure."""
    k = int(round(float(T._mid(th)) / HALFPI))
    d = th - iv.pi / 2 * k
    a = abs(float(d.a)) if float(d.a) > 0 else 0.0
    lo = min(abs(float(d.a)), abs(float(d.b)))
    hi = max(abs(float(d.a)), abs(float(d.b)))
    if float(d.a) <= 0.0 <= float(d.b):
        lo = 0.0
    del a
    return math.degrees(lo), math.degrees(hi)


def corner_depths(zfrac, blockers, ladder=DPS_LADDER):
    """Certified depth of every square at every corner of a rational config.

    blockers: {corner: [square indices]} -- the certified blocker list.
    Returns per-corner rows sorted by depth, descending, plus the bbox side.
    """
    for dps in ladder:
        KB.set_dps(dps)
        pt = KB.ivpt(zfrac)
        Q = KB.all_corners_iv(pt)
        xlo, xhi, ylo, yhi = KB.bbox_iv(Q)
        side = T.iv_max(xhi - xlo, yhi - ylo)
        out, worst_w, nskip = {}, 0.0, 0
        for cn in CORNERS:
            rows = []
            for j in range(N):
                Qc = [frame(px, py, cn, xlo, xhi, ylo, yhi) for px, py in Q[j]]
                f, sk = f_minmax_iv(Qc)
                nskip += sk
                d = 1 - f
                tl, th_ = tilt_deg_iv(pt[3 * j + 2])
                rows.append({'sq': j,
                             'depth_lo': _ivlo(d), 'depth_hi': _ivhi(d),
                             'depth': float(T._mid(d)),
                             'width': float(d.delta),
                             'tilt_deg_lo': tl, 'tilt_deg_hi': th_,
                             'tilt_deg': 0.5 * (tl + th_),
                             'is_blocker': j in blockers[cn]})
                worst_w = max(worst_w, float(d.delta))
            rows.sort(key=lambda r: -r['depth'])
            out[cn] = rows
        # every certified blocker must have a certified POSITIVE depth and every
        # non-blocker a certified non-positive one; if not, tighten.
        clean = True
        for cn in CORNERS:
            for r in out[cn]:
                if r['is_blocker'] and not r['depth_lo'] > 0.0:
                    clean = False
                if (not r['is_blocker']) and not r['depth_hi'] <= 1e-9:
                    clean = False
        if clean and nskip == 0:
            break
    KB.set_dps(30)
    return out, float(T._mid(side)), dps, worst_w, nskip, clean


def d12(rows):
    """(d1, d2) over the BLOCKERS of one corner; d2 = None if < 2 blockers."""
    b = [r for r in rows if r['is_blocker']]
    if not b:
        return None, None, b
    d1 = b[0]
    d2 = b[1] if len(b) > 1 else None
    return d1, d2, b


# ============================================== the K0-BLOCKED packing corpus

def corpus():
    """Every A87 configuration with a rational z AND an exact K0-BLOCKED verdict,
    plus Trump as the canary (K0-FREE, three 1-crowds -- deliberately included so
    the same code path is exercised on the depth-1 case)."""
    items = []
    js = json.load(open(os.path.join(RESULTS, 'k0dir87.json')))
    rec = js['record_K0_BLOCKED_packing']
    items.append({'src': 'k0dir87.json:record_K0_BLOCKED_packing',
                  'tag': rec['tag'], 'kind': 'K0_BLOCKED',
                  'sigma': rec['sigma_float'],
                  'z': [Fraction(v) for v in rec['z']],
                  'stored_n_block': rec['exact_n_block'],
                  'stored_m1': rec['m1'], 'stored_m2': rec['m2']})
    p = os.path.join(RESULTS, 'k0dir87.polish.jsonl')
    for ln in open(p):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if not (r.get('exact_K0_BLOCKED') and r.get('z_polished')):
            continue
        items.append({'src': 'k0dir87.polish.jsonl', 'tag': r['tag'],
                      'kind': 'K0_BLOCKED',
                      'sigma': r['sigma_polished'],
                      'z': [Fraction(v) for v in r['z_polished']],
                      'stored_n_block': r['exact_n_block'],
                      'stored_m1': None, 'stored_m2': r.get('polished_m2')})
    items.append(trump_item())
    return items


def trump_item():
    d = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct',
                                    'trump11_exact.json')))
    z = []
    for sq in d['squares']:
        z.append(Fraction(sq['cx']))
        z.append(Fraction(sq['cy']))
        z.append(Fraction(sq['theta']))
    z.append(Fraction(d['s']))
    return {'src': 'A03/trump11_exact.json', 'tag': 'trump', 'kind': 'CANARY',
            'sigma': float(Fraction(d['s'])), 'z': z,
            'stored_n_block': None, 'stored_m1': None, 'stored_m2': None}


# =================================================== A85 box-level upper bound

def box_depth_ubs(nth=2001):
    """t2b_depth's sound per-box depth upper bound over the 644 sound BL boxes."""
    import t2b_reach as TB
    _R, _V, _rows, boxes = TB.load_boxes()
    lip = math.sqrt(2.0) / 2.0
    ub = np.empty(len(boxes))
    for k, b in enumerate(boxes):
        th = np.linspace(math.radians(b.th0), math.radians(b.th1), nth)
        cx = np.full(nth, b.x0)
        cy = np.full(nth, b.y0)
        f = TB.f_minmax_np(TB.verts_np(cx, cy, th))
        slack = lip * (th[1] - th[0]) / 2.0 if nth > 1 else 0.0
        ub[k] = 1.0 - (float(f.min()) - slack)
    return ub, len(boxes)


def gate_analysis(ub):
    g = json.load(open(os.path.join(A85, 'results', 'a85_gate_samples.json')))
    c4 = g['sample_records']['c4']
    att = [r for r in c4 if r['state'] == 'attemptable']
    out = {'n_c4_records': len(c4),
           'state_counts': {s: sum(1 for r in c4 if r['state'] == s)
                            for s in ('attemptable', 'unkillable',
                                      'contradictory')},
           'full_sample_counts_from_file': g['sample_4corner']['counts'],
           'note': ('d1_ub(c) = max over the corner PAIR of depth_ub(box); a '
                    'node can host d1 >= delta at all four corners only if '
                    'min_c d1_ub(c) >= delta.  d2_ub(c) = min over the pair '
                    '(both boxes must be deep for the SECOND intruder to be).'),
           'per_delta': {}}

    def mins(recs):
        m1, m2 = [], []
        for r in recs:
            v1 = [max(ub[i], ub[j]) for (i, j) in
                  (tuple(r['node'][c]) for c in CORNERS)]
            v2 = [min(ub[i], ub[j]) for (i, j) in
                  (tuple(r['node'][c]) for c in CORNERS)]
            m1.append(min(v1))
            m2.append(min(v2))
        return m1, m2

    a1, a2 = mins(att)
    n1, n2 = mins(c4)
    for dl in DELTAS:
        out['per_delta']['%g' % dl] = {
            'attemptable_n': len(att),
            'attemptable_all4_can_host_d1': int(sum(1 for v in a1 if v >= dl)),
            'attemptable_frac_all4_can_host_d1':
                (sum(1 for v in a1 if v >= dl) / len(att)) if att else None,
            'attemptable_all4_can_host_d2': int(sum(1 for v in a2 if v >= dl)),
            'attemptable_frac_all4_can_host_d2':
                (sum(1 for v in a2 if v >= dl) / len(att)) if att else None,
            'all_nodes_n': len(c4),
            'all_nodes_frac_all4_can_host_d1':
                sum(1 for v in n1 if v >= dl) / len(c4)}
    out['min_c_d1_ub_attemptable'] = sorted(a1, reverse=True)
    out['min_c_d1_ub_all_nodes_stats'] = {
        'min': min(n1), 'median': float(np.median(n1)), 'max': max(n1)}
    # marginal: attemptable BL PAIRS from the 2000-row pair_states census
    ps = g['pair_states']
    pa = [(r['i'], r['j']) for r in ps if r['state'] == 'attemptable']
    out['pair_marginal'] = {
        'n_pair_states_rows': len(ps), 'n_attemptable': len(pa),
        'per_delta': {'%g' % dl: {
            'frac_pairs_with_a_deep_capable_member':
                sum(1 for (i, j) in pa if max(ub[i], ub[j]) >= dl) / len(pa),
            'frac_pairs_with_both_deep_capable':
                sum(1 for (i, j) in pa if min(ub[i], ub[j]) >= dl) / len(pa)}
            for dl in DELTAS}}
    out['box_depth_ub'] = {'n_boxes': int(len(ub)), 'min': float(ub.min()),
                           'max': float(ub.max()), 'mean': float(ub.mean()),
                           'frac_ge': {'%g' % dl: float((ub >= dl).mean())
                                       for dl in DELTAS}}
    return out


# ================================================================== selftest

def selftest():
    ok = []
    KB.set_dps(60)

    def chk(name, cond, extra=''):
        ok.append((name, bool(cond), extra))
        print('%-46s %s %s' % (name, 'ok' if cond else 'FAIL', extra),
              flush=True)

    # (a) axis-aligned square [a,a+1]x[b,b+1] in the BL frame -> depth 1-max(a,b)
    for (a, b) in ((Fraction(1, 4), Fraction(1, 8)),
                   (Fraction(0), Fraction(3, 5)), (Fraction(7, 10), Fraction(0))):
        cx, cy = a + Fraction(1, 2), b + Fraction(1, 2)
        Qs = [(T._to_iv(cx - Fraction(1, 2)), T._to_iv(cy - Fraction(1, 2))),
              (T._to_iv(cx + Fraction(1, 2)), T._to_iv(cy - Fraction(1, 2))),
              (T._to_iv(cx + Fraction(1, 2)), T._to_iv(cy + Fraction(1, 2))),
              (T._to_iv(cx - Fraction(1, 2)), T._to_iv(cy + Fraction(1, 2)))]
        f, _sk = f_minmax_iv(Qs)
        want = Fraction(1) - max(a, b)          # EXACT reference
        d = 1 - f
        chk('axis-aligned depth 1-max(a,b) a=%s b=%s' % (a, b),
            KB._lo_frac(d) <= want <= KB._hi_frac(d)
            and float(d.delta) < 1e-25,
            'enclosure width %.2g' % float(d.delta))
    # (b) 45-degree diamond, lowest vertex in the slot -> depth 1 - max(vx, vy)
    th = iv.pi / 4
    cx, cy = T._to_iv(Fraction(3, 5)), T._to_iv(Fraction(1, 2))
    h = iv.sqrt(2) / 2
    Qs = [(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)]
    f, _sk = f_minmax_iv(Qs)
    # the min of max(x,y) is attained at the lower-left EDGE crossing x=y
    want_lo = float((cx - h).a)
    chk('45-deg diamond f_min_max in range',
        want_lo - 1e-12 <= float(T._mid(f)) <= float(cy.b),
        'f=%.18f' % float(T._mid(f)))
    del th
    # (c) the slot square itself -> depth exactly 1
    Qs = [(T._to_iv(Fraction(0)), T._to_iv(Fraction(0))),
          (T._to_iv(Fraction(1)), T._to_iv(Fraction(0))),
          (T._to_iv(Fraction(1)), T._to_iv(Fraction(1))),
          (T._to_iv(Fraction(0)), T._to_iv(Fraction(1)))]
    f, _sk = f_minmax_iv(Qs)
    chk('slot square depth = 1', abs(float(T._mid(1 - f)) - 1.0) < 1e-30)
    # (d) a square fully outside the slot -> depth <= 0
    Qs = [(T._to_iv(Fraction(3, 2)), T._to_iv(Fraction(0))),
          (T._to_iv(Fraction(5, 2)), T._to_iv(Fraction(0))),
          (T._to_iv(Fraction(5, 2)), T._to_iv(Fraction(1))),
          (T._to_iv(Fraction(3, 2)), T._to_iv(Fraction(1)))]
    f, _sk = f_minmax_iv(Qs)
    chk('disjoint square depth <= 0', float((1 - f).b) <= 0.0)
    # (e) tilt: theta = pi/2 - 1e-3 -> tilt 1e-3 rad
    lo, hi = tilt_deg_iv(iv.pi / 2 - iv.mpf('0.001'))
    chk('tilt_deg of pi/2-1e-3', abs(0.5 * (lo + hi) - math.degrees(1e-3)) < 1e-12)
    lo, hi = tilt_deg_iv(iv.mpf(0))
    chk('tilt_deg of 0 is 0', hi < 1e-30)
    KB.set_dps(30)
    return all(c for _n, c, _e in ok)


# ==================================================================== driver

def run():
    t0 = time.time()
    items = corpus()
    print('corpus: %d configurations' % len(items), flush=True)
    rows, packs = [], []
    for it in items:
        zf = it['z']
        blk = KD.exact_blocked_test(zf)
        blockers = {c: blk['per_corner'][c]['blockers'] for c in CORNERS}
        dep, side, dps, wmax, nskip, clean = corner_depths(zf, blockers)
        rec = {'tag': it['tag'], 'src': it['src'], 'kind': it['kind'],
               'sigma': it['sigma'], 'sigma_bbox_iv_mid': side,
               'n_block_certified': blk['n_block_certified'],
               'stored_n_block': it['stored_n_block'],
               'exact_dps': dps, 'max_depth_interval_width': wmax,
               'n_edge_sign_inconclusive': nskip, 'blocker_depth_clean': clean,
               'per_corner': {}}
        for cn in CORNERS:
            d1, d2, b = d12(dep[cn])
            rec['per_corner'][cn] = {
                'blockers': blockers[cn],
                'd1': (None if d1 is None else d1['depth']),
                'd1_lo': (None if d1 is None else d1['depth_lo']),
                'd1_hi': (None if d1 is None else d1['depth_hi']),
                'd1_sq': (None if d1 is None else d1['sq']),
                'd1_tilt_deg': (None if d1 is None else d1['tilt_deg']),
                'd2': (None if d2 is None else d2['depth']),
                'd2_lo': (None if d2 is None else d2['depth_lo']),
                'd2_hi': (None if d2 is None else d2['depth_hi']),
                'd2_sq': (None if d2 is None else d2['sq']),
                'd2_tilt_deg': (None if d2 is None else d2['tilt_deg']),
                'all_depths': [{'sq': r['sq'], 'depth': r['depth'],
                                'tilt_deg': r['tilt_deg'],
                                'is_blocker': r['is_blocker']}
                               for r in dep[cn] if r['is_blocker']]}
            rows.append({'tag': it['tag'], 'kind': it['kind'],
                         'sigma': it['sigma'], 'corner': cn,
                         'n_blockers': len(b),
                         'd1': rec['per_corner'][cn]['d1'],
                         'd2': rec['per_corner'][cn]['d2'],
                         'd1_sq': rec['per_corner'][cn]['d1_sq'],
                         'd1_tilt_deg': rec['per_corner'][cn]['d1_tilt_deg'],
                         'd1_lo': rec['per_corner'][cn]['d1_lo'],
                         'd1_hi': rec['per_corner'][cn]['d1_hi']})
        v = [rec['per_corner'][c]['d1'] for c in CORNERS]
        rec['d1'] = v
        rec['max_c_d1'] = max(x for x in v if x is not None)
        rec['min_c_d1'] = (min(v) if all(x is not None for x in v) else None)
        rec['d2'] = [rec['per_corner'][c]['d2'] for c in CORNERS]
        d2v = [x for x in rec['d2'] if x is not None]
        rec['min_c_d2'] = (min(rec['d2']) if len(d2v) == 4 else None)
        packs.append(rec)
        print('  %-6s %-11s sigma %.12f  d1 %s  min %s' %
              (it['tag'], it['kind'], it['sigma'],
               ' '.join('%.6f' % x if x is not None else '  --  ' for x in v),
               ('%.6f' % rec['min_c_d1']) if rec['min_c_d1'] is not None
               else 'n/a'), flush=True)

    with open(OUT_JL, 'w') as fo:
        for r in rows:
            fo.write(json.dumps(r) + '\n')

    blocked = [p for p in packs if p['kind'] == 'K0_BLOCKED']
    out = {'attempt': 'A87 depthdist87: intruder depth in K0-BLOCKED packings',
           'definition': ('depth(Q) = 1 - f_min_max(Q) in the corner frame '
                          '(A89 t2b_depth); d1(c) / d2(c) = depth of the '
                          'deepest / second-deepest CERTIFIED blocker of c'),
           'exactness': ('z is exactly rational for every row; depth is an '
                         'outward-rounded mpmath interval enclosure (only '
                         'inexactness: cos/sin of a rational angle).  Blockers '
                         'are k0dir87 exact_blocked_test INNER-slot certified '
                         'blockers, which is the sound direction for BLOCKED.'),
           'n_K0_BLOCKED_packings': len(blocked),
           'max_depth_interval_width': max(p['max_depth_interval_width']
                                           for p in packs),
           'deltas': list(DELTAS)}
    out['counts_min_c_d1_ge_delta'] = {
        '%g' % dl: int(sum(1 for p in blocked if p['min_c_d1'] >= dl))
        for dl in DELTAS}
    out['counts_min_c_d2_ge_delta'] = {
        '%g' % dl: int(sum(1 for p in blocked
                           if p['min_c_d2'] is not None and p['min_c_d2'] >= dl))
        for dl in DELTAS}
    mx = [p['max_c_d1'] for p in blocked]
    mn = [p['min_c_d1'] for p in blocked]
    out['max_c_d1'] = {'values': sorted(mx, reverse=True), 'min': min(mx),
                       'max': max(mx), 'median': float(np.median(mx)),
                       'hist': {nm: sum(1 for v in mx if a <= v < b)
                                for nm, a, b in DEPTH_BINS}}
    out['min_c_d1'] = {'values': sorted(mn, reverse=True), 'min': min(mn),
                       'max': max(mn), 'median': float(np.median(mn)),
                       'hist': {nm: sum(1 for v in mn if a <= v < b)
                                for nm, a, b in DEPTH_BINS}}
    out['sigma_vs_min_c_d1'] = sorted(
        [{'tag': p['tag'], 'sigma': p['sigma'], 'min_c_d1': p['min_c_d1'],
          'max_c_d1': p['max_c_d1'], 'min_c_d2': p['min_c_d2'],
          'd1': p['d1']} for p in blocked], key=lambda r: r['sigma'])
    if len(blocked) > 2:
        s = np.array([p['sigma'] for p in blocked])
        m = np.array([p['min_c_d1'] for p in blocked])
        out['sigma_vs_min_c_d1_pearson'] = (
            float(np.corrcoef(s, m)[0, 1]) if s.std() > 0 and m.std() > 0
            else None)
        rs = np.argsort(np.argsort(s)).astype(float)
        rm = np.argsort(np.argsort(m)).astype(float)
        out['sigma_vs_min_c_d1_spearman'] = float(np.corrcoef(rs, rm)[0, 1])
        out['argmin_sigma_is_argmax_min_c_d1'] = bool(
            int(np.argmin(s)) == int(np.argmax(m)))
    # scatter: tilt of the deepest intruder vs its depth (all corners, all rows)
    sc = [r for r in rows if r['d1'] is not None]
    out['tilt_vs_depth_of_deepest'] = tilt_scatter(sc)
    out['tilt_vs_depth_of_deepest_K0_BLOCKED_only'] = tilt_scatter(
        [r for r in sc if r['kind'] == 'K0_BLOCKED'])
    # the deep pass / record rows store m1, m2 = -(SAT gap), a DIFFERENT depth:
    # the smallest translation along one of the 4 candidate SAT axes that would
    # separate the square from the slot.  Line them up so nobody reads the two
    # as the same number.
    cmp_rows = []
    for p, it in zip(packs, items):
        if it['stored_m1'] is None and it['stored_m2'] is None:
            continue
        for k, cn in enumerate(CORNERS):
            cmp_rows.append({
                'tag': p['tag'], 'corner': cn,
                'A89_depth_d1': p['per_corner'][cn]['d1'],
                'stored_SATgap_m1': (it['stored_m1'][k] if it['stored_m1']
                                     else None),
                'A89_depth_d2': p['per_corner'][cn]['d2'],
                'stored_SATgap_m2': (it['stored_m2'][k] if it['stored_m2']
                                     else None)})
    dd = [abs(r['A89_depth_d1'] - r['stored_SATgap_m1']) for r in cmp_rows
          if r['stored_SATgap_m1'] is not None]
    out['A89_depth_vs_stored_SAT_m1m2'] = {
        'why': ('k0dir87 m1/m2 = -(SAT gap) = the smallest separating '
                'translation along one of the 4 candidate axes; the A89 depth '
                'is 1 - f_min_max, the reach towards the corner POINT.  They '
                'coincide whenever the binding SAT axis is an axis of the slot '
                'and the binding vertex is the one nearest the corner, which is '
                'most but not all of the time -- so the m1/m2 columns of '
                'k0dir87.deep.jsonl are a good PROXY for d1/d2 but not equal '
                'to them.'),
        'rows': cmp_rows,
        'n_columns_compared': sum(1 for r in cmp_rows
                                  if r['stored_SATgap_m2'] is not None),
        'n_columns_equal_to_1e-12': sum(
            1 for r in cmp_rows if r['stored_SATgap_m2'] is not None
            and r['A89_depth_d2'] is not None
            and abs(r['A89_depth_d2'] - r['stored_SATgap_m2']) < 1e-12),
        'max_abs_diff_d1_vs_m1': (max(dd) if dd else None),
        'max_abs_diff_d2_vs_m2': max(
            abs(r['A89_depth_d2'] - r['stored_SATgap_m2']) for r in cmp_rows
            if r['stored_SATgap_m2'] is not None
            and r['A89_depth_d2'] is not None)}
    print('A85 gate / box upper bounds ...', flush=True)
    ub, nb = box_depth_ubs()
    out['a85_gate'] = gate_analysis(ub)
    out['packings'] = packs
    out['secs'] = time.time() - t0
    json.dump(out, open(OUT_JS, 'w'), indent=1, default=str)
    print('-> %s  (%.1f s)' % (OUT_JS, out['secs']), flush=True)
    return out


def tilt_scatter(rows):
    if not rows:
        return None
    t = np.array([r['d1_tilt_deg'] for r in rows])
    d = np.array([r['d1'] for r in rows])
    o = {'n': len(rows),
         'tilt_deg': {'min': float(t.min()), 'max': float(t.max()),
                      'median': float(np.median(t))},
         'depth': {'min': float(d.min()), 'max': float(d.max()),
                   'median': float(np.median(d))},
         'pearson_tilt_depth': (float(np.corrcoef(t, d)[0, 1])
                                if t.std() > 0 and d.std() > 0 else None),
         'by_tilt_bin': {}, 'points': []}
    rs = np.argsort(np.argsort(t)).astype(float)
    rd = np.argsort(np.argsort(d)).astype(float)
    o['spearman_tilt_depth'] = (float(np.corrcoef(rs, rd)[0, 1])
                                if rs.std() > 0 and rd.std() > 0 else None)
    for nm, a, b in TILT_BINS:
        v = [r['d1'] for r in rows if a <= r['d1_tilt_deg'] < b]
        if v:
            o['by_tilt_bin'][nm] = {'n': len(v), 'depth_min': min(v),
                                    'depth_max': max(v),
                                    'depth_mean': sum(v) / len(v)}
    o['points'] = sorted([{'tag': r['tag'], 'corner': r['corner'],
                           'sq': r['d1_sq'], 'tilt_deg': r['d1_tilt_deg'],
                           'depth': r['d1']} for r in rows],
                         key=lambda r: -r['depth'])
    return o


# ==================================================================== report

def report():
    o = json.load(open(OUT_JS))
    L = []
    A = L.append
    A('# A87 chore: how deep do the intruders of a K0-BLOCKED packing get?\n')
    A('## Headline\n')
    A('Packings with `min_c d1(c) >= delta` (over the %d exact-verified '
      'K0-BLOCKED packings A87 has):\n' % o['n_K0_BLOCKED_packings'])
    A('| delta | 0.3 | 0.5 | 0.7 | 0.9 |')
    A('| --- | ---: | ---: | ---: | ---: |')
    c = o['counts_min_c_d1_ge_delta']
    A('| count | %d | %d | %d | %d |\n' % tuple(c['%g' % d] for d in DELTAS))
    A('* deepest corner over the corpus: `max_c d1` in [%.6f, %.6f], median '
      '%.6f' % (o['max_c_d1']['min'], o['max_c_d1']['max'],
                o['max_c_d1']['median']))
    A('* shallowest corner: `min_c d1` in [%.6g, %.6g], median %.6g'
      % (o['min_c_d1']['min'], o['min_c_d1']['max'], o['min_c_d1']['median']))
    A('* NO packing has all four corners deep at any of the four deltas.'
      if max(c.values()) == 0 else
      '* some packings ARE deep at all four corners; see the table.')
    A('* certified: every depth is an interval enclosure of width <= %.2g\n'
      % o['max_depth_interval_width'])
    A('## Per packing (sorted by sigma)\n')
    A('| tag | sigma | d1 BL | d1 BR | d1 TL | d1 TR | max_c d1 | min_c d1 | '
      'min_c d2 |')
    A('| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    for r in o['sigma_vs_min_c_d1']:
        A('| %s | %.12f | %s | %.6f | %.6f | %s |'
          % (r['tag'], r['sigma'],
             ' | '.join('%.6g' % v for v in r['d1']),
             r['max_c_d1'], r['min_c_d1'],
             ('%.4g' % r['min_c_d2']) if r['min_c_d2'] is not None else '--'))
    A('')
    A('sigma vs min_c d1: Pearson %s, Spearman %s; the LOWEST-sigma packing is '
      '%s the deepest-at-every-corner one.\n'
      % (_f(o.get('sigma_vs_min_c_d1_pearson')),
         _f(o.get('sigma_vs_min_c_d1_spearman')),
         'also' if o.get('argmin_sigma_is_argmax_min_c_d1') else 'NOT'))
    A('## Full per-corner detail (d1 / d2 of every corner)\n')
    A('| tag | corner | #blockers | d1 | sq | tilt of d1 (deg) | d2 |')
    A('| --- | --- | ---: | ---: | ---: | ---: | ---: |')
    for p in o['packings']:
        for cn in CORNERS:
            q = p['per_corner'][cn]
            A('| %s | %s | %d | %s | %s | %s | %s |'
              % (p['tag'], cn, len(q['blockers']), _f(q['d1'], 6),
                 q['d1_sq'], _f(q['d1_tilt_deg'], 6), _f(q['d2'], 6)))
    A('')
    A('## Tilt of the deepest intruder vs its depth\n')
    for key, ttl in (('tilt_vs_depth_of_deepest_K0_BLOCKED_only',
                      'K0-BLOCKED packings only'),
                     ('tilt_vs_depth_of_deepest', 'all rows incl. the canary')):
        s = o.get(key)
        if not s:
            continue
        A('**%s** (n = %d).  Pearson %s, Spearman %s.  tilt in [%.4g, %.4g] '
          'deg, depth in [%.4g, %.4g].\n'
          % (ttl, s['n'], _f(s['pearson_tilt_depth']),
             _f(s['spearman_tilt_depth']), s['tilt_deg']['min'],
             s['tilt_deg']['max'], s['depth']['min'], s['depth']['max']))
        A('| tilt bin (deg) | n | depth min | depth mean | depth max |')
        A('| --- | ---: | ---: | ---: | ---: |')
        for nm, v in s['by_tilt_bin'].items():
            A('| %s | %d | %.6g | %.6g | %.6g |'
              % (nm, v['n'], v['depth_min'], v['depth_mean'], v['depth_max']))
        A('')
    g = o['a85_gate']
    A('## A85 4-corner gate samples: can all four boxes host a deep d1?\n')
    A('Box-level UPPER bound (sound over the whole cover box): '
      'd1_ub(c) = max over the corner pair of depth_ub(box).  '
      '%d stored 4-corner nodes, %d attemptable.\n'
      % (g['n_c4_records'], g['state_counts']['attemptable']))
    A('| delta | attemptable nodes that CAN host d1 >= delta at all 4 corners | '
      'fraction | ... and d2 >= delta at all 4 | fraction | all 200 nodes frac |')
    A('| --- | ---: | ---: | ---: | ---: | ---: |')
    for dl in DELTAS:
        v = g['per_delta']['%g' % dl]
        A('| %g | %d / %d | %.4f | %d / %d | %.4f | %.4f |'
          % (dl, v['attemptable_all4_can_host_d1'], v['attemptable_n'],
             v['attemptable_frac_all4_can_host_d1'],
             v['attemptable_all4_can_host_d2'], v['attemptable_n'],
             v['attemptable_frac_all4_can_host_d2'],
             v['all_nodes_frac_all4_can_host_d1']))
    A('')
    b = g['box_depth_ub']
    A('Per-box depth upper bound over the %d sound BL cover boxes: '
      'min %.4g, mean %.4g, max %.4g; fraction with depth_ub >= delta: %s\n'
      % (b['n_boxes'], b['min'], b['mean'], b['max'],
         ', '.join('%g: %.4f' % (d, b['frac_ge']['%g' % d]) for d in DELTAS)))
    pm = g['pair_marginal']
    A('Marginal over the %d attemptable BL pairs of the pair_states census: '
      'fraction with a deep-capable member / with both deep-capable: %s\n'
      % (pm['n_attemptable'],
         ', '.join('%g: %.4f / %.4f'
                   % (d, pm['per_delta']['%g' % d]
                      ['frac_pairs_with_a_deep_capable_member'],
                      pm['per_delta']['%g' % d]
                      ['frac_pairs_with_both_deep_capable'])
                   for d in DELTAS)))
    A('## Reading\n')
    A('* **Every K0-BLOCKED packing A87 has is deep at ONE OR TWO corners and '
      'razor-thin at another.**  `max_c d1` never drops below %.4g (four of the '
      'five have a corner intruded past 0.94, i.e. essentially to the corner '
      'point), while `min_c d1` never exceeds %.4g.  The four counts at '
      'delta = 0.3 / 0.5 / 0.7 / 0.9 are all ZERO: there is no '
      'deep-at-all-four-corners packing in the corpus, and the corpus misses '
      'the FIRST threshold by a factor of 3.'
      % (o['max_c_d1']['min'], o['min_c_d1']['max']))
    A('* **The second intruder is what is thin, everywhere.**  `min_c d2` is at '
      'most 1e-4 in every packing but s0115, where it is 8e-9 -- i.e. the K0 '
      'row sits on (or below) the constrained pass\'s artificial depth floor '
      'EPS_KEEP = 1e-4.  The four stuck endpoints are boundary points of the '
      'CONSTRAINED problem, exactly as notes/k0dir87.md reports; s0115 is the '
      'only row where the second intruders are held by the packing (BL/BR d2 = '
      '1.47e-2 / 1.45e-2) rather than by the floor -- and even there TL/TR '
      'second intruders are at 8e-9 / 1.7e-8.')
    A('* **Deep does NOT mean high sigma -- if anything the reverse, on this '
      'corpus.**  The lowest-sigma packing (s0115, sigma = 3.9855) is also the '
      'one with the largest `min_c d1` and the largest `max_c d1`; Pearson '
      'corr(sigma, min_c d1) = %s.  But the correlation is an artefact of the '
      'cluster: the other four all sit at sigma = 4.0000000-4.0000119, so the '
      'rank correlation is only %s.  The honest statement is that the corpus '
      'gives NO evidence that four-corner depth costs side, and one data point '
      '(s0115) against it.'
      % (_f(o.get('sigma_vs_min_c_d1_pearson')),
         _f(o.get('sigma_vs_min_c_d1_spearman'))))
    A('* **Tilt of the deepest intruder does not predict its depth.**  Over the '
      '20 K0-BLOCKED corners, Pearson %s / Spearman %s -- a weak NEGATIVE '
      'trend at best: the three deepest-corner rows (0.9757, 0.9432, 0.9407) '
      'have tilts 0.47, 0.020 and 0.126 deg, i.e. nearly axis-aligned squares '
      'shoved into the corner, while the only two rows with tilt above 15 deg '
      'have depth 0.0997 and 0.2267.  Trump\'s genuine 2-crowd is the extreme '
      'of the other kind: tilt 40.18 deg at depth 0.1683.'
      % (_f(o['tilt_vs_depth_of_deepest_K0_BLOCKED_only']
            ['pearson_tilt_depth']),
         _f(o['tilt_vs_depth_of_deepest_K0_BLOCKED_only']
            ['spearman_tilt_depth'])))
    A('* **The A85 box bound says the geometry is not the obstruction at 0.3, '
      'and is at 0.7.**  %.1f%% of attemptable 4-corner nodes could host '
      'd1 >= 0.3 at all four corners and %.1f%% could at 0.5, but NONE could at '
      '0.7 or 0.9 -- and 0%% could host the SECOND intruder at 0.3 at all four '
      'corners.  Since this is an UPPER bound, "0" is a hard exclusion: no '
      % (100.0 * g['per_delta']['0.3']['attemptable_frac_all4_can_host_d1'],
         100.0 * g['per_delta']['0.5']['attemptable_frac_all4_can_host_d1']) +
      'attemptable 4-corner node in the stored sample admits a packing with '
      'min_c d1 >= 0.7.  The contrast with the flow corpus (which cannot even '
      'reach 0.3) is the size of the gap between what the boxes permit and what '
      'a feasible packing achieves.')
    A('* **Caveat on n.**  Five packings and 30 attemptable stored nodes.  '
      'These are the only A87/A85 rows that carry both a rational z (or a sound '
      'box) and an exact verdict; everything else along the 520 flows is float '
      'and was NOT counted.\n')
    A('## m1 / m2 in k0dir87 are a proxy for d1 / d2, not equal to them\n')
    cm = o.get('A89_depth_vs_stored_SAT_m1m2')
    if cm:
        A(cm['why'])
        A('')
        A('| tag | corner | A89 d1 | stored m1 | A89 d2 | stored m2 |')
        A('| --- | --- | ---: | ---: | ---: | ---: |')
        for r in cm['rows']:
            A('| %s | %s | %s | %s | %s | %s |'
              % (r['tag'], r['corner'], _f(r['A89_depth_d1'], 6),
                 _f(r['stored_SATgap_m1'], 6), _f(r['A89_depth_d2'], 6),
                 _f(r['stored_SATgap_m2'], 6)))
        A('')
        A('largest |d1 - m1| over the rows that store m1: %s; largest '
          '|d2 - m2|: %s; %d of the %d m2 columns agree to 1e-12.\n'
          % (_f(cm['max_abs_diff_d1_vs_m1'], 4),
             _f(cm['max_abs_diff_d2_vs_m2'], 4),
             cm['n_columns_equal_to_1e-12'], cm['n_columns_compared']))
    A('## Canary\n')
    tr = [p for p in o['packings'] if p['tag'] == 'trump'][0]
    A('Trump at sigma %.12f, certified n_block %s: '
      % (tr['sigma'], tr['n_block_certified']))
    A('')
    for cn in CORNERS:
        q = tr['per_corner'][cn]
        A('* %s: blockers %s, d1 = %s (square %s, tilt %s deg), d2 = %s'
          % (cn, q['blockers'], _f(q['d1'], 12), q['d1_sq'],
             _f(q['d1_tilt_deg'], 6), _f(q['d2'], 6)))
    A('')
    A('Handled by exactly the same code path: the three 1-crowd corners come '
      'out at depth 1 (a flush slot square reaches the corner point, '
      'f_min_max = 0) and TL at 0.168321, matching A89 t2b_depth\'s exact '
      'Decimal value.  Trump is K0-FREE, so it has no min_c d1 and is excluded '
      'from every count above.\n')
    open(OUT_MD, 'w').write('\n'.join(L))
    print('-> %s' % OUT_MD, flush=True)
    print('\n'.join(L))


def _f(v, nd=4):
    if v is None:
        return '--'
    return ('%.' + str(nd) + 'g') % v


def main():
    a = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if a in ('selftest', 'all'):
        if not selftest():
            print('SELFTEST FAILED', flush=True)
            sys.exit(1)
    if a in ('run', 'all'):
        run()
    if a in ('report', 'all'):
        report()


if __name__ == '__main__':
    main()
