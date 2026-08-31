#!/usr/bin/env python
"""seeds_a51.py -- A51 seed constructor: MID-TILT flush-free seed families.

A49 sampled only the near-upright evasion world (all tilts < 8 deg) and every
drain landed on the s = 4 axis-aligned grid.  A49's own sampling caveat: the
MID-TILT non-thin flush-free world was never sampled.  A51 builds seeds there.

Four families, per the A51 brief:

 (i)   ATLAS-OPENED.  Take an A37 atlas critical family (these ARE the mid-tilt
       world: 3-5 squares at 33-45 deg plus an axis-aligned complement) and
       OPEN its flush contacts: comb the 11 tilt classes apart on the circle
       R/90deg by eps_open (axis class 0 pinned), so every flush pair contact
       and every wall-flush becomes a small-gap corner/edge contact, while the
       mid-tilt values themselves are essentially intact (the comb moves a
       tilt by <= a few tenths of a degree).  repair() then restores exact
       feasibility (it scales CENTRES only, so the tilt comb -- hence
       flush-freeness as a stratum property -- survives verbatim).

 (ii)  MID-TILT CORNER LATTICE.  Diamond-ish staggered lattices at base tilt
       22 / 30 / 38 deg: rows of 4/4/3, alternate rows offset by half the
       x-pitch, pitches set BELOW the bounding width so the seed starts
       overlapping and `repair` finds the least scale that separates it --
       which manufactures corner-on-edge contacts rather than flush ones.

 (iii) [45,0,45]-ADJACENT, FATTENED TO NON-THIN.  A47's s* = 2sqrt2+1 thin
       chain (D_L diamond at 45, U axis-aligned unit square, D_R diamond) is
       the ONLY flush-free thin spanning chain in the live window; A47 killed
       it by showing the 8-square complement cannot exist AT s*.  Here the
       chain is (a) de-quantized -- U is given a genuine mid tilt tU and the
       diamonds are combed off exactly 45 -- and (b) FATTENED: the 8
       complement squares are placed in contact with the chain so the chain
       squares acquire H-degree >= 3, i.e. non-thin, which is precisely the
       branch A47 left open.

 (iv)  RANDOM MID-TILT.  Rejection-sampled feasible flush-free configurations
       with all 11 tilts drawn uniform in [15, 45] deg (combed), centres
       uniform, accepted on repair feasibility + flush-freeness.

Every seed is checked flush-free at tol_f = 0.05 deg AND stratum-flush-free
(min pairwise/axis tilt-class gap >= EPS_MIN_DEG) after repair.
Float [NUM] -- seeds are basin selectors, not certificates.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A51 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A51, '..'))
A49C = os.path.join(ATT, 'A49-flushfree-hunt', 'code')
if A49C not in sys.path:
    sys.path.insert(0, A49C)

import a49_common as C                    # noqa: E402  (FIXED repair_ok)
import stratum_a49 as S                   # noqa: E402  (comb_angles)

pack11, P, D = C.pack11, C.P, C.D
N, HP = C.N, C.HP
DEG = math.pi / 180.0

RESULTS = os.path.join(A51, 'results')
os.makedirs(RESULTS, exist_ok=True)

EPS_MIN_DEG = 0.30        # required min tilt-class gap of an accepted seed
EPS_OPEN_DEG = 0.50       # default comb margin used to OPEN flush contacts
S_CAP = 6.20              # accepted repaired side (mid-tilt seeds are wide)
LAM_CAP = 3.00            # accepted repair inflation (lattices start dense)


# --------------------------------------------------------------- utilities
def half_extent(th):
    return 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))


def min_class_gap_deg(x):
    """min over the 55 pair class distances and the 11 class-from-axis."""
    th = np.mod(np.asarray(x[2 * N:3 * N], float), HP)
    g = [C.class_from_axis_deg(t) for t in th]
    for i in range(N):
        for j in range(i + 1, N):
            g.append(C.class_dist_deg(th[i], th[j]))
    return float(min(g))


def finish(x, eps_open=EPS_OPEN_DEG):
    """Comb the tilt classes apart by eps_open, then exact-feasibility repair
    (centres only -- the comb survives)."""
    y = S.comb_angles(np.array(x, float), eps_open)
    xr, lam, s, ok = C.repair_ok(y, lam_hi=8.0)
    return xr, lam, s, ok


# TILT-REGIME roles.  A49 labelled squares by their architectural deck
# (B binding chain / M presser / T top deck) and its `role_pair_category`
# reads role[0].  A51's seeds have no deck architecture; what matters here is
# the TILT REGIME, so the same one-letter slots are reused with A51 meanings
# and the report always prints the translated names:
#     B = UPRIGHT  (tilt class < 12 deg)
#     M = MID      (12 <= tilt class < 30 deg)
#     T = HIGH     (tilt class >= 30 deg, diamond-ish)
ROLE_LEGEND = {'B': 'UPRIGHT (<12 deg)', 'M': 'MID (12-30 deg)',
               'T': 'HIGH (>=30 deg)'}


def tilt_roles(x):
    _, th, _ = pack11.unpack(x)
    out = []
    for i, t in enumerate(th):
        c = C.class_from_axis_deg(t)
        out.append(('B' if c < 12.0 else 'M' if c < 30.0 else 'T') + str(i))
    return out


def make_rec(sid, family, note, x, meta=None):
    xr, lam, s, ok = x
    fr = C.flush_report(xr, tol_f=C.TOL_F_DEG)
    gap = min_class_gap_deg(xr)
    _, th, _ = pack11.unpack(xr)
    tdeg = sorted(round(C.class_from_axis_deg(t), 2) for t in th)
    n_mid = sum(1 for v in tdeg if v >= 12.0)
    acc = bool(ok and fr['flush_free'] and gap >= EPS_MIN_DEG
               and s <= S_CAP and lam <= LAM_CAP)
    rec = {'id': sid, 'family': family, 'profile': family, 'mode': note,
           'roles': tilt_roles(xr),
           'lam_minus_1': float(lam), 's_repaired': float(s),
           'repair_feasible': bool(ok),
           'min_class_gap_deg': gap,
           'flush_free': bool(fr['flush_free']),
           'n_pair_contacts': fr['n_pair_contacts'],
           'n_wall_contacts': fr['n_wall_contacts'],
           'tilt_classes_deg': tdeg, 'n_mid_tilt_ge12deg': n_mid,
           'mean_tilt_class_deg': float(np.mean(tdeg)),
           'accepted': acc,
           'x_a04': [float(v) for v in xr],
           'z': [float(v) for v in D.a04_to_z(xr)]}
    if meta:
        rec.update(meta)
    return rec


# ------------------------------------------------- (i) atlas-opened families
# chosen for mid-tilt content and class variety (see notes/seed_design.md)
ATLAS_PICKS = [
    ('M01', 0, 0.50, 'RIGID Trump 5x40.18'),
    ('M02', 1, 0.50, 'VALLEY 5x~45'),
    ('M03', 6, 0.50, 'VALLEY 4x41.56'),
    ('M04', 13, 0.50, 'VALLEY 5x33.90'),
    ('M05', 26, 0.50, 'mixed 19.7/22.4/38.4/44.8'),
    ('M06', 31, 0.50, 'VALLEY 3x42.06+44.33'),
    ('M07', 0, 1.75, 'Trump, WIDE opening'),
    ('M08', 13, 1.75, 'VALLEY 33.9, WIDE opening'),
]


def seeds_atlas():
    out = []
    for sid, fid, eps, note in ATLAS_PICKS:
        z, fam, ci = P.load_family(fid)
        x = np.array(fam['best_x'], float)
        out.append(make_rec(sid, 'atlas-opened', 'open%.2f' % eps,
                            finish(x, eps),
                            {'source_family': fid, 'eps_open_deg': eps,
                             'note': note,
                             's_family': float(fam['s_min'])}))
    return out


# ------------------------------------------ (ii) mid-tilt corner lattices
def tiling_sites(base_deg, pack_frac=1.0, k=N, centre=(0.0, 0.0)):
    """The COMPACT k-site blob of the unit-square TILING lattice at tilt
    base_deg: lattice vectors u = (cos t, sin t), v = (-sin t, cos t) (a unit
    square tiles the plane along its own edge directions), scaled by
    pack_frac, and the k sites nearest the centroid -- so the blob is as close
    to round as the lattice allows, which minimises the axis-aligned bounding
    box the CONTAINER has to supply."""
    t = base_deg * DEG
    u = np.array([math.cos(t), math.sin(t)]) * pack_frac
    v = np.array([-math.sin(t), math.cos(t)]) * pack_frac
    pts = [(i * u + j * v) for i in range(-4, 5) for j in range(-4, 5)]
    pts.sort(key=lambda p: float(np.hypot(*(p - np.array(centre)))))
    return np.array(pts[:k])


def build_lattice(base_deg, spread_deg=0.60, pack_frac=1.0, s_init=4.8):
    """Compact mid-tilt tiling-lattice blob; the 11 tilts are combed apart by
    spread_deg about base_deg, so the perfect tiling is broken into a
    corner-on-edge network (no two members share a tilt class, none is
    axis-parallel).  pack_frac < 1 makes the seed overlap on purpose: the
    repair scale-search then separates it into corner contacts."""
    tilts = [base_deg + (k - 5) * spread_deg for k in range(N)]
    Cs = tiling_sites(base_deg, pack_frac)
    Cs = Cs - Cs.min(axis=0) + 0.75
    x = pack11.pack(Cs, np.mod(np.radians(tilts), HP), s_init)
    return x


def seeds_lattice():
    spec = [('M09', 22.0, 0.60, 1.00), ('M10', 30.0, 0.60, 1.00),
            ('M11', 38.0, 0.60, 1.00), ('M12', 30.0, 1.40, 0.94)]
    out = []
    for sid, base, spread, pf in spec:
        x = build_lattice(base, spread, pf)
        out.append(make_rec(sid, 'midtilt-lattice',
                            'base%.0f' % base, finish(x, EPS_OPEN_DEG),
                            {'base_tilt_deg': base, 'spread_deg': spread,
                             'pack_frac': pf,
                             'note': 'compact 11-site tiling-lattice blob'}))
    return out


# ------------------------------- (iii) [45,0,45]-adjacent, fattened non-thin
R2 = math.sqrt(2.0)
S_STAR = 2.0 * R2 + 1.0            # 3.828427...


def build_chain(tU_deg, tD_deg=44.2, s=4.45, comp_tilt=28.0, fatten=0.97):
    """A47's s* thin chain de-quantized and fattened to NON-THIN.

    D_L: diamond (tilt ~45, combed off exactly 45) with its left corner on
         x = 0 at height y0 = s/2;
    U  : the middle square, given a genuine MID tilt tU -- A47's chain has it
         axis-aligned, which is BOTH wall-flush and at mismatch exactly 45 to
         the diamonds, i.e. precisely the quantization flush-freeness forbids;
    D_R: mirror diamond with its right corner on x = s.

    The 8 complement squares are taken from a mid-tilt tiling lattice
    (comp_tilt) restricted to the two bands outside the chain, pulled toward
    the chain by `fatten` so they PRESS on it: every chain square then has
    H-degree >= 3 (non-thin), which is exactly the branch A47's thin theorem
    does not cover."""
    eD = half_extent(tD_deg * DEG)
    eU = half_extent(tU_deg * DEG)
    y0 = max(eD, eU) + 0.02             # chain sits ON the bottom wall band
    Cs = [[eD, y0], [0.5 * s, y0], [s - eD, y0]]
    TH = [tD_deg * DEG, tU_deg * DEG, -tD_deg * DEG]
    # complement: 8 squares in 3 rows (3/3/2) stacked on the chain and pulled
    # DOWN onto it by `fatten`, so the chain squares are pressed from above
    # (H-degree >= 3 = non-thin) instead of carrying a bare thin line of action
    ctil = [comp_tilt - 6.0, comp_tilt, comp_tilt + 6.0]
    e0 = max(half_extent(t * DEG) for t in ctil)
    rows = [3, 3, 2]
    y = y0 + max(eD, eU) + e0
    k = 0
    for r, nr in enumerate(rows):
        xs = [(m + 0.5) * s / nr + (0.14 if r % 2 else -0.14) for m in range(nr)]
        for m in range(nr):
            th = ctil[(k + r) % 3] * DEG
            Cs.append([min(max(xs[m], e0), s - e0),
                       y0 + fatten * (y - y0)])
            TH.append(th)
            k += 1
        y += 2.0 * e0 * 0.97
    x = pack11.pack(np.array(Cs[:N]), np.mod(np.array(TH[:N]), HP), s)
    return x


def seeds_chain():
    spec = [('M13', 8.0, 22.0), ('M14', 20.0, 28.0), ('M15', 32.0, 34.0)]
    out = []
    for sid, tU, ct in spec:
        x = build_chain(tU, s=4.45, comp_tilt=ct)
        out.append(make_rec(sid, 'chain-45-0-45-fat', 'tU%.0f' % tU,
                            finish(x, EPS_OPEN_DEG),
                            {'tU_deg': tU, 'comp_tilt_deg': ct,
                             's_star': S_STAR, 's_seed': 4.45,
                             'note': 'A47 s* chain de-quantized + fattened '
                                     'to non-thin'}))
    return out


# ------------------------------------------------- (iv) random mid-tilt
def seeds_random(n=4, seed0=51, ntry=250):
    """Rejection sampling in the mid-tilt world: the 11 TILTS are drawn
    uniform in [15, 45] deg (the defining randomisation) and the centres are a
    random compact site pattern -- a tiling-lattice blob at a random base
    orientation, randomly permuted and jittered.  (Uniform-random centres are
    rejected almost surely: they repair to s > 6.5, which is not a packing
    seed but a scatter.)  Accepted on repair feasibility + flush-freeness;
    the best (smallest repaired s) of `ntry` draws is kept."""
    out = []
    for k in range(n):
        rng = np.random.default_rng(seed0 + k)
        best, ntried, nacc = None, 0, 0
        for _ in range(ntry):
            ntried += 1
            tilts = rng.uniform(15.0, 45.0, N)
            base = float(rng.uniform(15.0, 45.0))
            pf = float(rng.uniform(0.97, 1.10))
            Cs = tiling_sites(base, pf)
            Cs = Cs[rng.permutation(N)]
            Cs = Cs + rng.normal(0.0, 0.06, Cs.shape)
            Cs = Cs - Cs.min(axis=0) + 0.75
            x = pack11.pack(Cs, np.mod(np.radians(tilts), HP), 5.0)
            r = finish(x, EPS_OPEN_DEG)
            xr, lam, s, ok = r
            if not ok:
                continue
            if not C.flush_report(xr, tol_f=C.TOL_F_DEG)['flush_free']:
                continue
            nacc += 1
            if best is None or s < best[2]:
                best = r
        if best is None:
            continue
        out.append(make_rec('M%02d' % (16 + k), 'random-midtilt',
                            'rng%d' % (seed0 + k), best,
                            {'rng_seed': seed0 + k, 'n_draws': ntried,
                             'n_accepted_draws': nacc,
                             'note': 'rejection-sampled tilts U[15,45] deg, '
                                     'random compact site pattern'}))
    return out


def main():
    seeds = seeds_atlas() + seeds_lattice() + seeds_chain() + seeds_random()
    for r in seeds:
        print('%s %-18s %-10s lam-1=%.3f s=%.4f gap=%.3f ff=%s mid=%d/11  %s'
              % (r['id'], r['family'], r['mode'], r['lam_minus_1'],
                 r['s_repaired'], r['min_class_gap_deg'], r['flush_free'],
                 r['n_mid_tilt_ge12deg'],
                 'OK' if r['accepted'] else 'REJECT'))
    out = {'what': 'A51 MID-TILT flush-free seeds: (i) atlas families with '
                   'their flush contacts OPENED by a tilt comb, (ii) mid-tilt '
                   'staggered diamond lattices, (iii) A47 s* [45,0,45] chain '
                   'de-quantized + fattened to non-thin, (iv) random '
                   'rejection-sampled mid-tilt flush-free configurations',
           'role_legend': ROLE_LEGEND,
           'role_note': 'roles are TILT-REGIME labels (not A49 decks); the '
                        'letters B/M/T are reused so that a49_common.'
                        'role_pair_category works verbatim -- see '
                        'role_legend and summary_a51.CATMAP',
           'float_only': True, 'eps_min_deg': EPS_MIN_DEG,
           'eps_open_default_deg': EPS_OPEN_DEG,
           'tol_f_deg': C.TOL_F_DEG,
           's_cap': S_CAP, 'lam_cap': LAM_CAP,
           'n_seeds': len(seeds),
           'n_accepted': sum(r['accepted'] for r in seeds),
           'seeds': seeds}
    with open(os.path.join(RESULTS, 'seeds.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('accepted %d/%d -> results/seeds.json'
          % (out['n_accepted'], len(seeds)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
