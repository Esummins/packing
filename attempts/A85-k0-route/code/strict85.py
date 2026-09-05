r"""strict85.py -- A85/A87 chore: re-classify everything under the STRICT MEETS
convention.

CONVENTION (degen87 notes/degen87.md, TOL_INTRUDER = 1e-6).  A square MEETS a
corner cell only if its CERTIFIED intrusion depth into the OPEN cell exceeds
TOL = 1e-6.  A tangency is not a block.  Depth in the corner frame is

    depth(Q) = 1 - min_{p in Q} max(p_x, p_y)          (A89 / A90 definition)

and, for a Q contained in the enclosing box anchored at that corner,

    depth(Q) > tol   <=>   int(Q) meets the OPEN axis-aligned square of side
                           (1 - tol) anchored at the same corner.

So the strict test is the k0dir87 exact INNER-slot blocked test with the slot
side 1 replaced by (1 - tol):

  BLOCK direction (sound to assert MEETS): the rational rectangle that is a
    SUBSET of the true (1-tol)-cell for EVERY realisation of the interval
    bounding box,  BL: x in [xlo.b, xlo.a + 1 - tol]  (and BR/TL/TR mirrored).
    A certified interval overlap (gap.b < 0) with it implies depth > tol.
  FREE direction (sound to assert NOT a meeter): the rational rectangle that
    CONTAINS the true (1-tol)-cell,  BL: x in [xlo.a, xlo.b + 1 - tol].  A
    certified interval separation (gap.a >= 0) from it implies depth <= tol.
  Anything between the two is UNKNOWN and is walked up the dps ladder.

WHAT IS RE-CLASSIFIED

 (1) the 8 exact K0-BLOCKED packings (record from results/k0dir87.json,
     4 rows of k0dir87.polish.jsonl, 3 anchored candidates of d2front87.json)
     plus the Trump canary: per corner, the number of meeters at depth > 1e-6.
     A packing stays K0-BLOCKED iff all four corners keep >= 2 meeters.
 (2) the 167 certified k0 FJ points (cp87_fj_polished.jsonl): confirm the
     k0blocked87 verdict (all K0-FREE) is unchanged, and that the 668-corner
     blocker histogram is unchanged.
 (3) the realisable pair census (results/realise85.pairs.json, 7044 pairs):
     re-run realise85's sound box/pair stages with DEPTH_MIN = 1e-6 and with
     the SLIDE floors 0.0155 / 0.029 / 0.044 (G2/G3/G4 sides 3.862/3.848/3.833).
     Also classify the BASELINE 7044 by the sound per-box depth upper bound.
 (4) A85's four-corner gate: re-run realise85.stage_gate on each strict census.

One process, OMP_NUM_THREADS=1.  Writes only
attempts/A85-k0-route/{results,notes}/strict85.*
Usage: python strict85.py [all|packings|fj|pairs]
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ[_v] = '1'

import json
import math
import sys
import time
from decimal import Decimal
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(BASE, '..'))
A87C = os.path.join(ATT, 'A87-drain-flow', 'code')
A87R = os.path.join(ATT, 'A87-drain-flow', 'results')
sys.path.insert(0, HERE)
sys.path.insert(0, A87C)

RES = os.path.join(BASE, 'results')
NOTES = os.path.join(BASE, 'notes')
OUT = os.path.join(RES, 'strict85.json')
LOG = os.path.join(RES, 'strict85.log')

T0 = time.time()
_fh = open(LOG, 'a')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh.flush()


TOL = 1e-6                       # the strict MEETS bar
TOL_OLD = 1e-9                   # the loose bar everything used before
S_HAT = 3.877083590022814
SLIDE_FLOORS = [('G2_3.862', 0.0155), ('G3_3.848', 0.029), ('G4_3.833', 0.044)]

CORNERS = ('BL', 'BR', 'TR', 'TL')
CSGN = {'BL': (0, 0), 'BR': (1, 0), 'TL': (0, 1), 'TR': (1, 1)}
FSGN = {'BL': (1.0, 1.0), 'BR': (-1.0, 1.0), 'TR': (-1.0, -1.0), 'TL': (1.0, -1.0)}


# ==================================================================== part 1/2
# interval machinery: t3lib + k0blocked87 (import-safe, no module-level writes)
import t3lib as T                                                  # noqa: E402
import k0blocked87 as KB                                           # noqa: E402
from mpmath import iv                                              # noqa: E402


def _rect_square_gap(rect, qs, th):
    """interval SAT gap between an exact rational rectangle and a tilted square."""
    x0, x1, y0, y1 = [T._to_iv(v) for v in rect]
    sc = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    co, si = iv.cos(th), iv.sin(th)
    axes = [(iv.mpf(1), iv.mpf(0)), (iv.mpf(0), iv.mpf(1)), (co, si), (-si, co)]
    best = None
    for nx, ny in axes:
        ps = [nx * x + ny * y for x, y in sc]
        pj = [nx * x + ny * y for x, y in qs]
        los = his = ps[0]
        for p in ps[1:]:
            los = T.iv_min(los, p)
            his = T.iv_max(his, p)
        loj = hij = pj[0]
        for p in pj[1:]:
            loj = T.iv_min(loj, p)
            hij = T.iv_max(hij, p)
        gap = T.iv_max(loj - his, los - hij)
        best = gap if best is None else T.iv_max(best, gap)
    return best


def _rects(bb, tol):
    """(inner, outer) rectangles per corner for the (1 - tol) cell."""
    xlo, xhi, ylo, yhi = bb
    L = Fraction(1) - Fraction(tol).limit_denominator(10 ** 15)
    XA, XB = KB._lo_frac(xlo), KB._hi_frac(xlo)      # true xlo in [XA, XB]
    XC, XD = KB._lo_frac(xhi), KB._hi_frac(xhi)
    YA, YB = KB._lo_frac(ylo), KB._hi_frac(ylo)
    YC, YD = KB._lo_frac(yhi), KB._hi_frac(yhi)
    # sx = 0 -> cell grows to the RIGHT from xlo; sx = 1 -> LEFT from xhi
    xin = {0: (XB, XA + L), 1: (XD - L, XC)}
    xout = {0: (XA, XB + L), 1: (XC - L, XD)}
    yin = {0: (YB, YA + L), 1: (YD - L, YC)}
    yout = {0: (YA, YB + L), 1: (YC - L, YD)}
    inner, outer = {}, {}
    for cn in CORNERS:
        sx, sy = CSGN[cn]
        inner[cn] = (xin[sx][0], xin[sx][1], yin[sy][0], yin[sy][1])
        outer[cn] = (xout[sx][0], xout[sx][1], yout[sy][0], yout[sy][1])
    return inner, outer


def meet_counts(zfrac, tol, ladder=KB.DPS_LADDER):
    """certified per-corner MEETER counts at bar `tol`.

    meeters   : certified depth > tol   (inner rect, gap.b < 0)
    freed     : certified depth <= tol  (outer rect, gap.a >= 0)
    unknown   : neither, at the top of the dps ladder
    """
    per = None
    for dps in ladder:
        KB.set_dps(dps)
        pt = KB.ivpt(zfrac)
        Q = KB.all_corners_iv(pt)
        bb = KB.bbox_iv(Q)
        inner, outer = _rects(bb, tol)
        per = {}
        unknown = 0
        for cn in CORNERS:
            mt, unk, gi = [], [], []
            for j in range(11):
                gin = _rect_square_gap(inner[cn], Q[j], pt[3 * j + 2])
                gi.append(float(T._mid(gin)))
                if gin.b < 0:
                    mt.append(j)
                    continue
                gout = _rect_square_gap(outer[cn], Q[j], pt[3 * j + 2])
                if gout.a >= 0:
                    continue
                unk.append(j)
            unknown += len(unk)
            per[cn] = {'meeters': mt, 'unknown': unk, 'n_meet': len(mt),
                       'n_meet_conservative': len(mt) + len(unk),
                       'min_gap_inner': min(gi)}
        if unknown == 0:
            break
    KB.set_dps(30)
    nb = [per[c]['n_meet'] for c in CORNERS]
    nbc = [per[c]['n_meet_conservative'] for c in CORNERS]
    return {'per_corner': per, 'dps': dps, 'n_unknown': unknown,
            'n_meet': nb, 'n_meet_conservative': nbc,
            'min_n_meet': min(nb), 'min_n_meet_conservative': min(nbc),
            'K0_BLOCKED_certified': bool(min(nb) >= 2),
            'K0_FREE_certified': bool(min(nbc) <= 1)}


def depth_at_corner_f(sq, anch, cn):
    """float A89/A90 depth of a square into the cell anchored at `anch`."""
    cx, cy, th = float(sq[0]), float(sq[1]), float(sq[2])
    c, s = math.cos(th) / 2.0, math.sin(th) / 2.0
    V = [(cx - c + s, cy - s - c), (cx + c + s, cy + s - c),
         (cx + c - s, cy + s + c), (cx - c - s, cy - s + c)]
    sx, sy = FSGN[cn]
    W = [(sx * (x - anch[0]), sy * (y - anch[1])) for x, y in V]
    cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t))
                cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return 1.0 - min(max(p[0], p[1]) for p in cand)


def float_depths(zfrac):
    """float depths of all 11 squares at all four corners, on the tight bbox."""
    sqs = [(float(zfrac[3 * i]), float(zfrac[3 * i + 1]), float(zfrac[3 * i + 2]))
           for i in range(11)]
    xs, ys = [], []
    for cx, cy, th in sqs:
        c, s = math.cos(th) / 2.0, math.sin(th) / 2.0
        for u, v in ((-c + s, -s - c), (c + s, s - c), (c - s, s + c), (-c - s, -s + c)):
            xs.append(cx + u)
            ys.append(cy + v)
    xlo, xhi, ylo, yhi = min(xs), max(xs), min(ys), max(ys)
    anc = {'BL': (xlo, ylo), 'BR': (xhi, ylo), 'TR': (xhi, yhi), 'TL': (xlo, yhi)}
    return {cn: [depth_at_corner_f(s, anc[cn], cn) for s in sqs] for cn in CORNERS}, \
        (xlo, xhi, ylo, yhi)


# ---------------------------------------------------------------- the corpora
def _z(strs):
    return [T.str_frac(v) for v in strs]


def load_packings():
    """the 8 exact K0-BLOCKED packings, exactly as exchange87/degen87 load them."""
    out = []
    d = json.load(open(os.path.join(A87R, 'k0dir87.json')))
    rec = d['record_K0_BLOCKED_packing']
    out.append({'name': 'record_%s' % rec['tag'], 'src': 'k0dir87.json',
                'sigma': rec['sigma_float'], 'z': _z(rec['z'])})
    rows = [json.loads(l) for l in open(os.path.join(A87R, 'k0dir87.polish.jsonl'))
            if l.strip()]
    for i, r in enumerate(rows):
        if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'):
            continue
        out.append({'name': 'polish%02d_%s' % (i, r['tag']),
                    'src': 'k0dir87.polish.jsonl#%d' % i,
                    'sigma': r['sigma_polished'], 'z': _z(r['z_polished'])})
    d = json.load(open(os.path.join(A87R, 'd2front87.json')))
    src_list = [('own_side_anchored', d['own_side_anchored'])]
    src_list += [('cap' + k, v) for k, v in sorted(d['per_cap_anchored'].items())]
    seen, order = set(), []
    for src, v in src_list:
        if not v.get('anchored_only'):
            continue
        for c in v.get('candidates', []):
            key = tuple(c['z'])
            if key in seen:
                continue
            seen.add(key)
            order.append((src, c))
    for i, (src, c) in enumerate(order):
        out.append({'name': 'anchored%d_%s' % (i, c['tag']),
                    'src': 'd2front87.json:%s' % src,
                    'sigma': float(c['sigma_certified_upper']), 'z': _z(c['z'])})
    return out


def load_trump():
    p = os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
    d = json.load(open(p))
    z = []
    for sq in d['squares']:
        for k in ('cx', 'cy', 'theta'):
            z.append(Fraction(Decimal(sq[k])))
    z.append(Fraction(Decimal(d['s'])))
    return {'name': 'TRUMP_canary', 'src': 'A03/trump11_exact.json',
            'sigma': float(Fraction(Decimal(d['s']))), 'z': z}


def load_fj_points():
    recs = [json.loads(ln) for ln in
            open(os.path.join(A87R, 'cp87_fj_polished.jsonl')) if ln.strip()]
    out = []
    for r in recs:
        if not r.get('survivor_tight') or not r.get('z_polished'):
            continue
        out.append((r['tag'], _z(r['z_polished']), r['sigma_polished']))
    out.sort(key=lambda t: t[2])
    return out


# ------------------------------------------------------------------- stage 1
def stage_packings():
    pks = load_packings() + [load_trump()]
    rows = []
    for pk in pks:
        zf = pk['z']
        fd, bb = float_depths(zf)
        old = meet_counts(zf, TOL_OLD)
        new = meet_counts(zf, TOL)
        per = {}
        for cn in CORNERS:
            ds = sorted(((fd[cn][j], j) for j in range(11)), reverse=True)
            per[cn] = {
                'n_meet_1e-9': old['per_corner'][cn]['n_meet'],
                'n_meet_1e-6': new['per_corner'][cn]['n_meet'],
                'meeters_1e-6': new['per_corner'][cn]['meeters'],
                'unknown_1e-6': new['per_corner'][cn]['unknown'],
                'dropped_by_strict_bar': sorted(set(old['per_corner'][cn]['meeters'])
                                                - set(new['per_corner'][cn]['meeters'])),
                'top3_float_depth': [[j, round(v, 12)] for v, j in ds[:3]],
                'm2_float_depth': round(ds[1][0], 12),
            }
        r = {'packing': pk['name'], 'src': pk['src'], 'sigma': pk['sigma'],
             'bbox_float': [round(v, 12) for v in bb],
             'n_meet_1e-9': old['n_meet'], 'n_meet_1e-6': new['n_meet'],
             'dps': new['dps'], 'n_unknown': new['n_unknown'],
             'K0_BLOCKED_1e-9': old['K0_BLOCKED_certified'],
             'K0_BLOCKED_1e-6': new['K0_BLOCKED_certified'],
             'K0_FREE_1e-6': new['K0_FREE_certified'],
             'corners_dropping_to_one_meeter':
                 [c for c in CORNERS
                  if old['per_corner'][c]['n_meet'] >= 2
                  and new['per_corner'][c]['n_meet'] <= 1],
             'per_corner': per}
        rows.append(r)
        log('  %-18s sigma %.7f  n_meet 1e-9 %s -> 1e-6 %s   BLOCKED %s -> %s'
            % (pk['name'], pk['sigma'], old['n_meet'], new['n_meet'],
               old['K0_BLOCKED_certified'], new['K0_BLOCKED_certified']))
    main = [r for r in rows if r['packing'] != 'TRUMP_canary']
    can = [r for r in rows if r['packing'] == 'TRUMP_canary'][0]
    tl = can['per_corner']['TL']
    canary_ok = (tl['n_meet_1e-6'] == 2
                 and tl['m2_float_depth'] > 0.15
                 and all(can['per_corner'][c]['n_meet_1e-6'] <= 1
                         for c in ('BL', 'BR', 'TR')))
    return {'n_packings': len(main),
            'n_still_K0_BLOCKED_at_1e-6': sum(1 for r in main if r['K0_BLOCKED_1e-6']),
            'still_blocked': [r['packing'] for r in main if r['K0_BLOCKED_1e-6']],
            'now_K0_FREE': [r['packing'] for r in main if not r['K0_BLOCKED_1e-6']],
            'corners_dropped': {r['packing']: r['corners_dropping_to_one_meeter']
                                for r in main if r['corners_dropping_to_one_meeter']},
            'canary_trump': {'n_meet_1e-6': can['n_meet_1e-6'],
                             'TL_top3': tl['top3_float_depth'],
                             'TL_n_meet': tl['n_meet_1e-6'],
                             'other_corners_free':
                                 [c for c in ('BL', 'BR', 'TR')
                                  if can['per_corner'][c]['n_meet_1e-6'] <= 1],
                             'PASS': bool(canary_ok)},
            'rows': rows}


# ------------------------------------------------------------------- stage 2
def stage_fj():
    pts = load_fj_points()
    hist_old, hist_new = {}, {}
    free_old = free_new = 0
    changed = []
    minhist = {}
    dmin = 1e9
    for tag, zf, sig in pts:
        old = meet_counts(zf, TOL_OLD)
        new = meet_counts(zf, TOL)
        for c in CORNERS:
            a = old['per_corner'][c]['n_meet_conservative']
            b = new['per_corner'][c]['n_meet_conservative']
            hist_old[a] = hist_old.get(a, 0) + 1
            hist_new[b] = hist_new.get(b, 0) + 1
        free_old += 1 if old['K0_FREE_certified'] else 0
        free_new += 1 if new['K0_FREE_certified'] else 0
        k = new['min_n_meet_conservative']
        minhist[k] = minhist.get(k, 0) + 1
        if old['n_meet_conservative'] != new['n_meet_conservative']:
            changed.append({'tag': tag, 'sigma': sig,
                            'old': old['n_meet_conservative'],
                            'new': new['n_meet_conservative']})
        fd, _bb = float_depths(zf)
        for c in CORNERS:
            for v in fd[c]:
                if v > TOL_OLD:
                    dmin = min(dmin, v)
    return {'n_points': len(pts),
            'n_K0_FREE_at_1e-9': free_old, 'n_K0_FREE_at_1e-6': free_new,
            'corner_n_block_hist_1e-9': {str(k): v for k, v in sorted(hist_old.items())},
            'corner_n_block_hist_1e-6': {str(k): v for k, v in sorted(hist_new.items())},
            'min_n_block_hist_1e-6': {str(k): v for k, v in sorted(minhist.items())},
            'n_points_with_a_changed_corner_count': len(changed),
            'changed': changed[:20],
            'shallowest_blocker_depth_over_all_corners': dmin,
            'UNCHANGED': bool(len(changed) == 0 and free_new == len(pts))}


# ================================================================= part 3 / 4
import numpy as np                                                 # noqa: E402
import realise85 as R85                                            # noqa: E402


def run_realise(depth_min, do_gate=True):
    """realise85 stages 1-3 at a given DEPTH_MIN.  Returns a summary dict."""
    R85.DEPTH_MIN = depth_min
    R85.SLOT_LIM = 1.0 - depth_min
    t0 = time.time()
    boxes, atoms, depth, alive, ob = R85.stage_boxes(verbose=False)
    pairs, keep, op = R85.stage_pairs(boxes, atoms, alive, verbose=False)
    out = {'depth_min': depth_min,
           'n_boxes': ob['n_boxes'], 'n_boxes_realisable': ob['n_realisable'],
           'n_pairs_census': op['n_pairs'],
           'n_pairs_both_boxes_realisable': op['n_pairs_both_boxes_realisable'],
           'n_pairs_surviving': op['n_pairs_surviving'],
           'secs': time.time() - t0}
    if do_gate:
        g = R85.stage_gate(boxes, pairs, keep, depth)
        fa = g['counts']['attemptable'] / float(g['n_sampled'])
        out['gate'] = {'n_sampled': g['n_sampled'], 'counts': g['counts'],
                       'attemptable_fraction': fa,
                       'd4_canonical_fraction': g['d4_canonical_fraction']}
        out['frontier'] = R85.price(op['n_pairs_surviving'], fa,
                                    'strict depth>%g' % depth_min)
    return out, boxes, pairs, keep, depth, alive


def stage_pairs_census():
    res = {}
    # -- the baseline 7044 classified by the sound per-box depth upper bound
    base = json.load(open(os.path.join(RES, 'realise85.pairs.json')))['surviving']
    bx = json.load(open(os.path.join(RES, 'realise85.boxes.json')))
    dub = bx['depth_ub_wall']
    d2 = []
    for i, j in base:
        a, b = dub[i], dub[j]
        d2.append(min(a if a is not None else -1e9, b if b is not None else -1e9))
    d2 = np.array(d2)
    res['baseline_7044'] = {
        'n_pairs': len(base),
        'depth_min_used': 1e-9,
        'n_shallower_member_depth_ub_le_1e-6': int((d2 <= TOL).sum()),
        'n_both_members_depth_ub_gt_1e-6': int((d2 > TOL).sum()),
        'd2ub': {'min': float(d2.min()), 'median': float(np.median(d2)),
                 'max': float(d2.max())},
        'n_both_ge_floor': {nm: int((d2 >= f).sum()) for nm, f in SLIDE_FLOORS},
    }
    log('  baseline 7044: both-deep(>1e-6) %d, tangency-only %d'
        % (res['baseline_7044']['n_both_members_depth_ub_gt_1e-6'],
           res['baseline_7044']['n_shallower_member_depth_ub_le_1e-6']))

    runs = {}
    order = [('strict_1e-6', TOL)] + [(nm, f) for nm, f in SLIDE_FLOORS]
    for nm, f in order:
        o, _b, _p, _k, _d, _a = run_realise(f)
        runs[nm] = o
        log('  %-12s depth>=%-8g boxes %d/%d  pairs %d  attemptable %.4f'
            % (nm, f, o['n_boxes_realisable'], o['n_boxes'],
               o['n_pairs_surviving'], o['gate']['attemptable_fraction']))
    res['runs'] = runs
    base85 = json.load(open(os.path.join(RES, 'realise85.json')))
    res['reference_A85'] = {
        'a85_pairs': 33656, 'a85_attemptable_frac': 0.179,
        'realise85_pairs_at_1e-9': base85['part2_pairs']['n_pairs_surviving'],
        'realise85_attemptable_frac_at_1e-9':
            base85['part3_gate']['counts']['attemptable']
            / float(base85['part3_gate']['n_sampled']),
        'realise85_frontier_at_1e-9': base85['part4_price']['realisable']['frontier_nodes'],
    }
    return res


# ===================================================================== driver
def main(argv):
    what = argv[0] if argv else 'all'
    res = {'attempt': 'A85/A87 chore strict85: MEETS iff certified depth > 1e-6',
           'tol_strict': TOL, 'tol_old': TOL_OLD, 's_hat': S_HAT,
           'slide_floors': {nm: f for nm, f in SLIDE_FLOORS}}
    if what in ('all', 'packings'):
        log('[1] the 8 exact K0-BLOCKED packings + Trump ...')
        res['part1_packings'] = stage_packings()
        log('  -> %d / %d remain K0-BLOCKED at 1e-6; canary PASS=%s'
            % (res['part1_packings']['n_still_K0_BLOCKED_at_1e-6'],
               res['part1_packings']['n_packings'],
               res['part1_packings']['canary_trump']['PASS']))
    if what in ('all', 'fj'):
        log('[2] the 167 certified k0 FJ points ...')
        res['part2_fj'] = stage_fj()
        log('  -> K0-FREE %d/%d, corner hist %s, UNCHANGED=%s'
            % (res['part2_fj']['n_K0_FREE_at_1e-6'], res['part2_fj']['n_points'],
               res['part2_fj']['corner_n_block_hist_1e-6'],
               res['part2_fj']['UNCHANGED']))
    if what in ('all', 'pairs'):
        log('[3/4] strict realisable pair census + four-corner gate ...')
        res['part34_pairs_and_gate'] = stage_pairs_census()
    res['secs'] = time.time() - T0
    json.dump(res, open(OUT, 'w'), indent=1, default=str)
    log('-> %s  (%.1f s)' % (OUT, time.time() - T0))


if __name__ == '__main__':
    main(sys.argv[1:])
