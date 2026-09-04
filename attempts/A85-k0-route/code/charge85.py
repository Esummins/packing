"""charge85.py -- A85 chore: CERTIFIED corner CHARGE of pinned intruder PAIRS.

PI mechanism (A85).  In k0 every corner slot is non-free, so each of the four
corners carries a CHARGE = the stranded area near that corner (area that no
legal unit square, disjoint from the two corner intruders, can meet).  Dead
regions at distinct corners are interior-disjoint, so the budget lemma (A23
notes Lemma 2) gives

    charge(BL) + charge(BR) + charge(TR) + charge(TL)  <=  E(s) = s^2 - 11
    E(s0) = (969271/250000)^2 - 11 = 4.03178...

Trump spends most of that budget in ONE corner (the TL 2-crowd: an upright
square at offset g = 0.8445 plus a 40 deg partner) and has three zero-charge
slot corners.  This script MEASURES the charge of the A85 corner-crowd pair
boxes by case, so the PI can ask which four-corner combinations are already
dead by area.

WHAT IS CERTIFIED.  For a pair box (K_i, K_j) -- two hypothesis boxes
[t0,t1] x [x0,x1] x [y0,y1] in the BL corner frame -- the reported charge is a
rational number A such that:

    there is a set of pairwise interior-disjoint rational rectangles inside the
    BL QUADRANT [0, s/2]^2, of total area A, such that for EVERY placement pair
    (P_i, P_j) with parameters in (K_i, K_j) and every closed unit square Q with
    Q subset [0,s]^2 and int(Q) disjoint from int(P_i) and int(P_j), Q meets
    none of those rectangles.

The uniformity over the boxes is A23/A25's `PlacedBox` semantics; every accept
decision is taken in exact Fraction arithmetic by dead_region.Certifier in
mode='exact'.  Rectangles are clipped to the BL quadrant so that the four
corners' dead sets are automatically interior-disjoint and the budget lemma
applies to the SUM of four charges.

Method (A25's efficiency idea, kept sound):
  (1) map the wall/inter-square windows in mode='float' -- a fast NEGATIVE
      screen that only proposes candidate tiles;
  (2) RE-CERTIFY every proposed tile in mode='exact'; only tiles that pass are
      counted.  Dropped, unvisited, capped or failed tiles simply do not count,
      so the reported number is always a certified LOWER bound.

REFINEMENT.  A25's known cliff (floors collapse to 0 once a hypothesis
half-width exceeds ~0.10-0.15) is handled by bisecting the pair hypothesis in
its widest dimension (tilt widths compared in t = tan(theta/2) units, scaled by
TSCALE) and taking the MINIMUM certified area over the 2^L sub-boxes: that
minimum is still valid uniformly over the whole box (each placement lies in
some sub-box and strands at least that sub-box's area, inside the quadrant).

Canaries: Trump's TL pair at its exact placement (a 1e-7 point box), and the
flushest JAM pair (expected ~0).

One process, OMP_NUM_THREADS=1.  Writes only
attempts/A85-k0-route/{results,notes}/charge85.*
"""
from __future__ import annotations

import os
import sys

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import argparse
import bisect
import json
import math
import random
import time
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(BASE, '..'))
A25 = os.path.join(ATT, 'A25-wastage-atlas')
sys.path.insert(0, A25)

import atlas_lib as AL                                              # noqa: E402
from atlas_lib import (_mid_corners, between_rect, clip_box,        # noqa: E402
                       disjointify, map_windows, snap, wall_rects)
from dead_region import Certifier, PlacedBox, Region                # noqa: E402

RES = os.path.join(BASE, 'results')
NOTES = os.path.join(BASE, 'notes')

S0 = F(969271, 250000)                 # 3.877084
E_S0 = S0 * S0 - 11                    # 4.0317804...
QUAD = S0 / 2                          # BL quadrant half-side
TSCALE = F(3, 2)                       # tilt-width scale when picking the widest dim
TOL_AX = 1e-9
G_BINS = ((0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0))
SEED = 85

# certifier knobs (all caps only LOWER the reported bound)
CELL0 = F(1, 8)
MIN_CELL = F(1, 16)
WORK_BUDGET = 2500
DEPTH_MAX = 30
MAX_BOXES = 200_000
MAX_EXACT_CELLS = 600


# ---------------------------------------------------------------- inputs
def load_boxes():
    R = json.load(open(os.path.join(RES, 'a85_reach_BL.json')))
    rows = [r for r in R['variants']['sigma_closed_7']['rows'] if r['sound']]
    return [r['box'] for r in rows]


def load_labels():
    out = []
    with open(os.path.join(RES, 'cases85.pairs.jsonl')) as f:
        for line in f:
            d = json.loads(line)
            out.append((d['i'], d['j'], d['label']))
    return out


def is_axis(b):
    return b['th0'] <= TOL_AX or b['th1'] >= 90.0 - TOL_AX


def g_lo(b):
    """sound LOWER bound on the axis member's offset from its corner slot."""
    return max(b['x0'], b['y0']) - 0.5


def fr(v, d=10 ** 7):
    return F(v).limit_denominator(d)


def tbox_of(b):
    """box tilt range in degrees -> OUTWARD rational t = tan(theta/2) bounds."""
    return AL.tanhalf(b['th0'], False), AL.tanhalf(b['th1'], True)


def hyp_of(b):
    """(t0, t1, x0, x1, y0, y1) rational hypothesis box."""
    t0, t1 = tbox_of(b)
    return (t0, t1, fr(b['x0']), fr(b['x1']), fr(b['y0']), fr(b['y1']))


# ---------------------------------------------------------------- the charge
def _one_cell(hyps, cap_cells=MAX_EXACT_CELLS):
    """certified dead area in the BL quadrant for ONE pair hypothesis.

    hyps = [(t0,t1,x0,x1,y0,y1), (t0,t1,x0,x1,y0,y1)]
    Returns dict(area=Fraction, ...) or None if the hypothesis is vacuous.
    """
    out = []
    for h in hyps:
        cl = clip_box(h[0], h[1], h[2], h[3], h[4], h[5], S0)
        if cl is None:
            return None                     # no admissible placement: vacuous
        out.append((h[0], h[1]) + cl)
    boxes = [(o[2], o[3], o[4], o[5]) for o in out]
    # two interior-disjoint unit squares need centre distance >= 1
    dmax = math.hypot(max(abs(float(boxes[0][1] - boxes[1][0])),
                          abs(float(boxes[1][1] - boxes[0][0]))),
                      max(abs(float(boxes[0][3] - boxes[1][2])),
                          abs(float(boxes[1][3] - boxes[0][2]))))
    if dmax < 1.0:
        return dict(infeasible=True, area=F(0), n_cells=0, n_pass=0,
                    seconds=0.0, truncated=False)
    P = [PlacedBox(*o) for o in out]
    for B in P:
        B.filter_corners = _mid_corners(B)
    rects = []
    for b in boxes:
        rects += wall_rects(b[0], b[1], b[2], b[3], S0)
    rects.append(between_rect(boxes, S0))
    # CLIP TO THE BL QUADRANT: makes the four corners' dead sets disjoint
    rects = [(max(F(0), a), min(QUAD, b), max(F(0), c), min(QUAD, d))
             for (a, b, c, d) in rects]
    rects = [r for r in rects if r[1] > r[0] and r[3] > r[2]]
    if not rects:
        return dict(area=F(0), n_cells=0, n_pass=0, seconds=0.0, truncated=False,
                    screened='no window')
    rects = disjointify(snap(rects, CELL0, S0))
    ctr = ((boxes[0][0] + boxes[0][1] + boxes[1][0] + boxes[1][1]) / 4,
           (boxes[0][2] + boxes[0][3] + boxes[1][2] + boxes[1][3]) / 4)
    t0 = time.time()
    r = map_windows(P, S0, rects, ctr, cell0=CELL0, min_cell=MIN_CELL,
                    mode='float', depth_max=DEPTH_MAX,
                    max_boxes_per_cell=1500, work_budget=WORK_BUDGET)
    t_float = time.time() - t0
    # ---- exact re-certification (this is the proof step)
    cert = Certifier(S0, P, mode='exact', depth_max=DEPTH_MAX)
    t0 = time.time()
    area = F(0)
    npass = 0
    cells = r['cells'][:cap_cells]
    good = []
    for (x0, y0, x1, y1) in cells:
        D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        if cert.certify(D, max_boxes=MAX_BOXES)['passed']:
            area += D.area
            npass += 1
            good.append((x0, y0, x1, y1))
    return dict(area=area, cells_pass=good, n_cells=len(r['cells']), n_exact=len(cells),
                n_pass=npass, seconds=t_float + (time.time() - t0),
                float_area=r['area'], truncated=bool(r['truncated']),
                capped=len(r['cells']) > cap_cells)


def _widest_dim(hyps):
    """index (member, dim) of the widest hypothesis dimension; dim in 't','x','y'."""
    best, bd = None, F(-1)
    for m, h in enumerate(hyps):
        for dim, (a, b, sc) in (('t', (h[0], h[1], TSCALE)),
                                ('x', (h[2], h[3], F(1))),
                                ('y', (h[4], h[5], F(1)))):
            w = (b - a) * sc
            if w > bd:
                bd, best = w, (m, dim)
    return best, bd


def _bisect(hyps, m, dim):
    lo, hi = {'t': (0, 1), 'x': (2, 3), 'y': (4, 5)}[dim]
    mid = (hyps[m][lo] + hyps[m][hi]) / 2
    out = []
    for half in (0, 1):
        h = list(hyps[m])
        if half == 0:
            h[hi] = mid
        else:
            h[lo] = mid
        nh = list(hyps)
        nh[m] = tuple(h)
        out.append(nh)
    return out


def charge(hyps, max_level=2, cliff=F(1, 100), budget_s=120.0):
    """certified charge with adaptive bisection.  Returns (area, level, detail)."""
    t_start = time.time()
    r = _one_cell(hyps)
    if r is None:
        return F(0), 0, dict(vacuous=True)
    best, lvl = r['area'], 0
    detail = dict(level0=dict(area=str(r['area']), area_f=float(r['area']),
                              n_pass=r['n_pass'], n_cells=r.get('n_cells', 0),
                              seconds=round(r['seconds'], 2),
                              truncated=r.get('truncated', False),
                              capped=r.get('capped', False),
                              infeasible=r.get('infeasible', False)))
    if r.get('infeasible'):
        return F(0), 0, detail
    cur = [hyps]
    while best < cliff and lvl < max_level and time.time() - t_start < budget_s:
        nxt = []
        for h in cur:
            (m, dim), _w = _widest_dim(h)
            nxt += _bisect(h, m, dim)
        vals = []
        for h in nxt:
            rr = _one_cell(h)
            if rr is None:                       # vacuous sub-box: no constraint
                continue
            vals.append(rr['area'])
        lvl += 1
        cur = nxt
        if not vals:                             # every sub-box vacuous
            detail['level%d' % lvl] = dict(all_vacuous=True)
            break
        v = min(vals)
        detail['level%d' % lvl] = dict(area=str(v), area_f=float(v),
                                       n_sub=len(nxt), n_live=len(vals),
                                       seconds=round(time.time() - t_start, 2))
        if v > best:
            best = v
    return best, lvl, detail


# ---------------------------------------------------------------- canaries
def trump_TL_hyp(eps=F(1, 10 ** 7)):
    """Trump's TL corner pair mapped to the BL frame, as a 1e-7 point box."""
    getcontext().prec = 200
    d = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct',
                                    'trump11_exact.json')))
    s = Decimal(d['s'])
    si = Decimal(d['sin_theta'])
    th = math.degrees(math.asin(float(si)))
    hyps = []
    meta = []
    for idx, thd in ((4, 0.0), (6, th)):
        sq = d['squares'][idx]
        cx, cy = Decimal(sq['cx']), Decimal(sq['cy'])
        # TL corner -> BL frame: reflect in the horizontal mid-line,
        # (x, y) -> (x, s - y), theta -> -theta = 90 - theta (mod 90).
        # This reproduces cases85.trump_TL's reported cx_BL / cy_BL exactly.
        bx = float(cx)
        by = float(s - cy)
        bt = (90.0 - thd) % 90.0
        t = math.tan(math.radians(bt) / 2.0)
        hyps.append((fr(t, 10 ** 9) - eps if t > 0 else F(0), fr(t, 10 ** 9) + eps,
                     fr(bx, 10 ** 9) - eps, fr(bx, 10 ** 9) + eps,
                     fr(by, 10 ** 9) - eps, fr(by, 10 ** 9) + eps))
        meta.append(dict(square=idx, cx_BL=bx, cy_BL=by, th_BL_deg=bt,
                         tilt_deg=min(bt, 90.0 - bt), g=max(bx, by) - 0.5))
    return hyps, meta, float(s)


# ---------------------------------------------------------------- 4-corner count
def _count_gt(sorted_vals, thr):
    """#{v in sorted_vals : v > thr}"""
    return len(sorted_vals) - bisect.bisect_right(sorted_vals, thr)


def four_corner_orbits(vals, T):
    """#D4-orbits of 4-tuples from `vals` with sum > T, and the total #orbits.

    Burnside on the D4-stable set {sum > T}: cycle types on the four corners are
      e            (1 elt) : free 4-tuples
      r90, r270    (2 elts): a=b=c=d
      r180, 2 edge reflections (3 elts): two free values, each used twice
      2 diagonal reflections (2 elts): one value twice + two free values
    """
    n = len(vals)
    v = sorted(float(x) for x in vals)
    # N4: #{(a,b,c,d) : a+b+c+d > T}
    pairs = sorted(a + b for a in v for b in v)
    N4 = 0
    for x in pairs:
        N4 += _count_gt(pairs, T - x)
    # N1: 4a > T
    N1 = _count_gt(v, T / 4.0)
    # N2: 2(a+b) > T
    N2 = _count_gt(pairs, T / 2.0)
    # N3: 2a + b + c > T
    N3 = 0
    for a in v:
        N3 += _count_gt(pairs, T - 2.0 * a)
    good = (N4 + 2 * N1 + 3 * N2 + 2 * N3) // 8
    total = (n ** 4 + 2 * n ** 3 + 3 * n ** 2 + 2 * n) // 8
    assert (N4 + 2 * N1 + 3 * N2 + 2 * N3) % 8 == 0
    return good, total


# ---------------------------------------------------------------- driver
def stats(xs):
    if not xs:
        return None
    y = sorted(float(x) for x in xs)
    n = len(y)
    return dict(n=n, min=y[0], p25=y[n // 4], median=y[n // 2],
                p75=y[(3 * n) // 4], max=y[-1], mean=sum(y) / n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-jam', type=int, default=40)
    ap.add_argument('--n-block', type=int, default=40)
    ap.add_argument('--n-wedge', type=int, default=40)
    ap.add_argument('--n-other-bin', type=int, default=20)
    ap.add_argument('--max-level', type=int, default=2)
    ap.add_argument('--wall', type=float, default=9600.0)
    ap.add_argument('--out', default=os.path.join(RES, 'charge85.json'))
    ap.add_argument('--jsonl', default=os.path.join(RES, 'charge85.pairs.jsonl'))
    a = ap.parse_args()

    t00 = time.time()
    box = load_boxes()
    lab = load_labels()
    rng = random.Random(SEED)

    pools = defaultdict(list)
    for (i, j, L) in lab:
        if L in ('JAM', 'BLOCK', 'WEDGE'):
            pools[L].append((i, j))
        elif L == 'OTHER':
            cand = [k for k in (i, j) if is_axis(box[k])]
            if not cand:
                continue
            k = max(cand, key=lambda k: g_lo(box[k]))
            g = g_lo(box[k])
            for (lo, hi) in G_BINS:
                if lo <= g < hi:
                    pools['OTHER[%.1f,%.1f)' % (lo, hi)].append((i, j))
                    break

    want = {'JAM': a.n_jam, 'BLOCK': a.n_block, 'WEDGE': a.n_wedge}
    for (lo, hi) in G_BINS:
        want['OTHER[%.1f,%.1f)' % (lo, hi)] = a.n_other_bin
    sample = []
    for k in sorted(pools):
        p = sorted(set(pools[k]))
        m = min(want.get(k, 0), len(p))
        sample += [(k, i, j) for (i, j) in rng.sample(p, m)]
    rng.shuffle(sample)
    print('pool sizes: %s' % {k: len(set(v)) for k, v in sorted(pools.items())},
          flush=True)
    print('sample: %d  %s' % (len(sample), Counter(s[0] for s in sample)), flush=True)

    res = dict(attempt='A85 charge85 -- certified corner charge of pinned pairs',
               s0=str(S0), s0_float=float(S0), E_s0=str(E_S0),
               E_s0_float=float(E_S0), quadrant=str(QUAD), seed=SEED,
               params=dict(cell0=str(CELL0), min_cell=str(MIN_CELL),
                           work_budget=WORK_BUDGET, depth_max=DEPTH_MAX,
                           max_boxes=MAX_BOXES, max_exact_cells=MAX_EXACT_CELLS,
                           max_level=a.max_level, tscale=str(TSCALE)),
               pool_sizes={k: len(set(v)) for k, v in sorted(pools.items())})

    # ---- canary A: Trump TL at its exact placement
    print('\n=== canary: Trump TL pair (point box) ===', flush=True)
    th, tmeta, s_hat = trump_TL_hyp()
    A, lv, det = charge(th, max_level=0)
    res['canary_trump_TL'] = dict(squares=tmeta, s_hat=s_hat,
                                  charge=str(A), charge_f=float(A),
                                  level=lv, detail=det)
    print('  Trump TL charge = %.6f  (%.1fs)' % (float(A), det['level0']['seconds']),
          flush=True)

    # ---- canary B: flushest JAM pair (box level)
    print('=== canary: flushest JAM pair ===', flush=True)
    jam = [(i, j) for (i, j, L) in lab if L == 'JAM']
    jflush = min(jam, key=lambda ij: min(g_lo(box[k]) for k in ij if is_axis(box[k])))
    A2, lv2, det2 = charge([hyp_of(box[jflush[0]]), hyp_of(box[jflush[1]])],
                           max_level=a.max_level)
    res['canary_jam_flush'] = dict(i=jflush[0], j=jflush[1],
                                   box_i=box[jflush[0]], box_j=box[jflush[1]],
                                   g=min(g_lo(box[k]) for k in jflush if is_axis(box[k])),
                                   charge=str(A2), charge_f=float(A2),
                                   level=lv2, detail=det2)
    print('  flush JAM (%d,%d) charge = %.6f level=%d' % (jflush[0], jflush[1],
                                                          float(A2), lv2), flush=True)

    # ---- the sample
    print('\n=== sample of %d pair boxes ===' % len(sample), flush=True)
    recs = []
    fj = open(a.jsonl, 'w')
    for n, (strat, i, j) in enumerate(sample):
        if time.time() - t00 > a.wall:
            print('WALL BUDGET hit at %d/%d' % (n, len(sample)), flush=True)
            break
        A, lv, det = charge([hyp_of(box[i]), hyp_of(box[j])],
                            max_level=a.max_level)
        cand = [k for k in (i, j) if is_axis(box[k])]
        rec = dict(stratum=strat, i=i, j=j, charge=str(A), charge_f=float(A),
                   level=lv, g=(max(g_lo(box[k]) for k in cand) if cand else None),
                   detail=det)
        recs.append(rec)
        fj.write(json.dumps(rec) + '\n')
        fj.flush()
        if n % 10 == 0 or float(A) > 0.5:
            print('  [%3d/%3d] %-16s (%3d,%3d) charge=%.5f lvl=%d  %.0fs elapsed'
                  % (n + 1, len(sample), strat, i, j, float(A), lv,
                     time.time() - t00), flush=True)
    fj.close()
    res['n_measured'] = len(recs)

    # ---- per-stratum table
    by = defaultdict(list)
    for r in recs:
        by[r['stratum']].append(r)
    tab = {}
    for k in sorted(by):
        v = by[k]
        tab[k] = dict(stats(x['charge_f'] for x in v),
                      levels=dict(Counter(x['level'] for x in v)),
                      g=stats([x['g'] for x in v if x['g'] is not None]))
    res['per_stratum'] = tab

    # ---- four-corner dead fractions
    vals = [r['charge_f'] for r in recs]
    res['four_corner'] = {}
    for name, T in (('E_s0_4.0318', float(E_S0)), ('interior_waste_3.5', 3.5)):
        good, total = four_corner_orbits(vals, T)
        res['four_corner'][name] = dict(threshold=T, orbits_dead=good,
                                        orbits_total=total,
                                        fraction=good / total if total else 0.0)
    # non-JAM restricted pool (JAM corners are the ~0 ones)
    vnj = [r['charge_f'] for r in recs if r['stratum'] != 'JAM']
    res['four_corner_nonJAM'] = {}
    for name, T in (('E_s0_4.0318', float(E_S0)), ('interior_waste_3.5', 3.5)):
        good, total = four_corner_orbits(vnj, T)
        res['four_corner_nonJAM'][name] = dict(threshold=T, orbits_dead=good,
                                               orbits_total=total,
                                               fraction=good / total if total else 0.0)

    # ---- the PI cap: max g for an OTHER corner + 3 min-charge non-JAM corners
    m_nonjam = min(vnj) if vnj else 0.0
    oth = sorted([(r['g'], r['charge_f'], r['i'], r['j'])
                  for r in recs if r['stratum'].startswith('OTHER') and r['g'] is not None])
    cap = dict(min_nonJAM_charge=m_nonjam, budget=float(E_S0),
               head_for_OTHER=float(E_S0) - 3 * m_nonjam)
    ok = [o for o in oth if o[1] + 3 * m_nonjam <= float(E_S0)]
    bad = [o for o in oth if o[1] + 3 * m_nonjam > float(E_S0)]
    cap['max_g_under_budget'] = max((o[0] for o in ok), default=None)
    cap['min_g_over_budget'] = min((o[0] for o in bad), default=None)
    cap['n_ok'] = len(ok)
    cap['n_over'] = len(bad)
    # per-bin: the bin-MINIMUM charge is what a sound cap must use
    per_bin = {}
    for (lo, hi) in G_BINS:
        key = 'OTHER[%.1f,%.1f)' % (lo, hi)
        v = [r['charge_f'] for r in recs if r['stratum'] == key]
        if v:
            per_bin[key] = dict(min=min(v), median=sorted(v)[len(v) // 2],
                                max=max(v),
                                min_plus_3m=min(v) + 3 * m_nonjam,
                                over_budget=(min(v) + 3 * m_nonjam) > float(E_S0),
                                max_plus_3m=max(v) + 3 * m_nonjam,
                                any_over=(max(v) + 3 * m_nonjam) > float(E_S0))
    cap['per_bin'] = per_bin
    res['pi_cap'] = cap
    res['seconds'] = time.time() - t00
    json.dump(res, open(a.out, 'w'), indent=1)
    print('\nwrote %s  (%.0fs)' % (a.out, res['seconds']), flush=True)


if __name__ == '__main__':
    main()
