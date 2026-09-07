"""A122 T3 - the common-tilt family through S38, its crest, and A110's chain menu.

Two objects, kept apart on purpose:

  * the FAMILY formulas.  S38's five free squares are one flush grain at a common tilt: column
    {f2, f0, f1} (v-spacing 1) and column {f4, f3} (v-spacing 1), joined by the two u-steps
    f2 - f4 and f1 - f3 (u-spacing 1).  In strip coordinates u = c.(cos, sin), v = c.(-sin, cos)
    the SIX wall/corner rows are

      (a) f1's left vertex on the left wall     u1 c - (v2+2) s = h
      (b) f1's top vertex on the top wall       u1 s + (v2+2) c = S - h
      (c) f3's top vertex on the top wall       (u1+1) s + (v4+1) c = S - h
      (d) f2's bottom vertex on BL(1,0)'s TOP face   u2 s + v2 c = 1 + h
      (e) BR(0,1)'s corner (S-1, 2) on f4's lower edge   v4 = 1/2 - (S-1) s + 2 c
      (f) TR(0,0)'s corner (S-1, S-1) on f4's upper edge  u2 + 1 = (S-1)(c+s) - 1/2

    with h = (c + s)/2 and the grain relations v1 = v2 + 2, u3 = u1 + 1, v3 = v4 + 1, u4 = u2 + 1.
    That is six equations in five unknowns (u1, u2, v2, v4, S): OVERDETERMINED by one, so the
    structure exists at exactly one tilt.  Dropping one row at a time gives six closed forms in
    theta (sympy, `branch_formulas`); they all cross at one point, which IS S38.

  * the RELAXED path.  At each common tilt, pin the five tilts and re-minimise all eleven centres,
    the six upright tilts and s (A108's `refine_barrier` recipe: warm-started along the sweep in
    both directions plus a linear-interpolation seed, because a cold start loses the branch at the
    crest).  This is the path whose crest is the barrier to quote.

Outputs results/crest.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize, brentq

import a122lib as A
from a122lib import MZ

NV = 34
CONS = MZ.make_cons((), 11)


# ------------------------------------------------------------------ A110's chain menu
def Lam(th):
    c, s = math.cos(th), math.sin(th)
    return 2 + 2 * (c + s) / (1 + s * c)


def Y(th):
    c, s = math.cos(th), math.sin(th)
    return (1 + 3 * c + s + 2 * s * c + 2 * s * s) / (1 + s * c)


def D(th):
    c, s = math.cos(th), math.sin(th)
    return 2 + (2 + c) / (c + s)


def F_T(th):
    c, s = math.cos(th), math.sin(th)
    return 2 + (2 + s) / (c + s)


MENU = dict(Lambda=Lam, Y=Y, D=D, F_T=F_T)


# ------------------------------------------------------------------ S38's own branch formulas
def branch_formulas(th):
    """The six 'drop one row' closed forms of the S38 grain (derived with sympy, see docstring)."""
    c, s = math.cos(th), math.sin(th)
    a = (-2 * c ** 2 + c + s ** 2 + s + 1) / s ** 2
    b = ((2 * c ** 4 + c ** 3 * s + 2 * c ** 3 + 2 * c ** 2 * s + c * s ** 3 + 3 * c * s ** 2
          + s ** 4 + 2 * s ** 3 + s ** 2) / (c ** 3 * s + c ** 2 + c * s ** 3 + s ** 4))
    ce = ((c ** 3 * s + 3 * c ** 3 + c ** 2 * s ** 2 + 3 * c ** 2 * s + c ** 2 + c * s ** 3
           + 3 * c * s ** 2 + s ** 4 + 2 * s ** 3 + s ** 2)
          / (c ** 3 * s + c ** 2 * s ** 2 + c ** 2 + c * s ** 3 + s ** 4))
    df = ((2 * c ** 4 + c ** 3 * s + 2 * c ** 3 + 2 * c ** 2 * s ** 2 + 2 * c ** 2 * s
           + c * s ** 3 + 2 * c * s ** 2 + s ** 3) / (c * (c ** 2 * s + c + s ** 3)))
    return {'drop_a_f1_off_left_wall': a, 'drop_b_f1_off_top_wall': b,
            'drop_ce_f3_off_top_wall': ce, 'drop_df_f2_off_BL10': df}


# ------------------------------------------------------------------ the relaxed sweep
def solve_at_tilt(th, z0, free_idx=range(5), ntry=5, seed=0):
    lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
    hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
    for i in free_idx:
        lo[3 + 3 * i] = hi[3 + 3 * i] = th
    best = None
    for trial in range(ntry):
        z = np.array(z0, float).copy()
        if trial:
            rng = np.random.RandomState(seed * 977 + trial)
            for i in range(11):
                z[1 + 3 * i] += rng.uniform(-0.02, 0.02)
                z[2 + 3 * i] += rng.uniform(-0.02, 0.02)
        for i in free_idx:
            z[3 + 3 * i] = th
        z = np.clip(z, lo, hi)
        r = minimize(lambda v: v[0], z, jac=lambda v: np.eye(1, NV, 0)[0], method='SLSQP',
                     constraints=[{'type': 'ineq', 'fun': CONS}], bounds=list(zip(lo, hi)),
                     options={'maxiter': 600, 'ftol': 1e-14})
        if CONS(r.x).min() >= -1e-7:
            ss, cc = A.from107(r.x)
            sg = float(A.sigma(*A.normalise(ss, cc)))
            if best is None or sg < best[0]:
                best = (sg, r.x.copy())
    return best


def sweep(z_start, lo_deg, hi_deg, step, z_far=None, tag=''):
    grid = [round(x, 4) for x in np.arange(hi_deg, lo_deg - 1e-9, -step)]
    res, poses = {}, {}
    warm = np.array(z_start, float)
    for k, deg in enumerate(grid):                       # downhill
        b = solve_at_tilt(math.radians(deg), warm, seed=k)
        if b is not None:
            warm = b[1]
            res[deg] = b[0]
            poses[deg] = b[1].tolist()
    warm = np.array(z_far if z_far is not None else z_start, float)
    for k, deg in enumerate(reversed(grid)):             # uphill
        b = solve_at_tilt(math.radians(deg), warm, seed=7000 + k)
        if b is not None:
            warm = b[1]
            if deg not in res or b[0] < res[deg]:
                res[deg] = b[0]
                poses[deg] = b[1].tolist()
    rows = [dict(tilt_deg=d, s=res[d]) for d in sorted(res)]
    print(f'  [{tag}] {len(rows)} tilts, min {min(r["s"] for r in rows):.9f}, '
          f'max {max(r["s"] for r in rows):.9f}')
    return rows, poses


def main():
    t0 = time.time()
    out = {}
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    b38 = d['entries']['S38']['best']
    s38, cfg38 = b38['sigma'], [tuple(c) for c in b38['cfg']]
    z38 = A.to107(s38, cfg38)
    st, cfgt = A.load_trump()

    # -------- 1. the family formulas at S38's tilt, and the crossing
    th38 = cfg38[0][2]
    print(f'S38 common tilt {math.degrees(th38):.6f} deg, s* = {s38:.12f}')
    print('  branch formulas at that tilt:',
          {k: round(v, 9) for k, v in branch_formulas(th38).items()})
    print('  A110 menu at that tilt:', {k: round(f(th38), 9) for k, f in MENU.items()})

    def gap_ad(th):
        f = branch_formulas(th)
        return f['drop_a_f1_off_left_wall'] - f['drop_df_f2_off_BL10']

    th_star = brentq(gap_ad, math.radians(38.0), math.radians(45.0), xtol=1e-15, rtol=1e-15)
    fs = branch_formulas(th_star)
    out['family'] = dict(
        tilt_deg=math.degrees(th_star),
        s_at_crossing={k: v for k, v in fs.items()},
        s_star_from_family=fs['drop_a_f1_off_left_wall'],
        s_star_from_polish=s38,
        agreement=abs(fs['drop_a_f1_off_left_wall'] - s38),
        menu_at_tilt={k: f(th_star) for k, f in MENU.items()},
        branch_table=[dict(tilt_deg=g, **{k: v for k, v in branch_formulas(math.radians(g)).items()},
                           **{k: f(math.radians(g)) for k, f in MENU.items()})
                      for g in np.arange(38.0, 46.01, 0.5)])
    print(f'  the six rows are consistent at exactly one tilt: {math.degrees(th_star):.9f} deg, '
          f'S = {fs["drop_a_f1_off_left_wall"]:.12f}  (polish {s38:.12f}, '
          f'diff {fs["drop_a_f1_off_left_wall"] - s38:+.2e})')

    # -------- 2. the relaxed common-tilt path S38 -> Trump
    print('\n=== relaxed common-tilt path (five tilts pinned, everything else free)')
    q = math.pi / 2
    perm, tot, dt = A.match_configs(cfg38, cfgt)
    tB = [(cfgt[perm[i]][0], cfgt[perm[i]][1],
           cfgt[perm[i]][2] + q * round((cfg38[i][2] - cfgt[perm[i]][2]) / q)) for i in range(11)]
    zT = A.to107(st, tB)
    rows, poses = sweep(z38, 38.6, 43.6, 0.05, z_far=zT, tag='S38')
    out['relaxed_path'] = rows
    lo = [r for r in rows if r['tilt_deg'] < math.degrees(th_star)]
    crest = max(lo, key=lambda r: r['s']) if lo else None
    out['relaxed_path_crest_below_S38'] = crest
    if crest:
        print(f'  crest on the Trump side: s = {crest["s"]:.9f} at {crest["tilt_deg"]} deg   '
              f'(+{crest["s"]-s38:.6f} over S38, +{crest["s"]-A.SHAT:.6f} over Trump)')
        out['barrier_over_S38'] = crest['s'] - s38
        out['barrier_over_trump'] = crest['s'] - A.SHAT
        # which menu formula does the branch follow on each side of the crest?
        fit = []
        for r in rows:
            th = math.radians(r['tilt_deg'])
            best = min(MENU, key=lambda k: abs(MENU[k](th) - r['s']))
            fit.append(dict(tilt_deg=r['tilt_deg'], s=r['s'], nearest=best,
                            err=abs(MENU[best](th) - r['s']),
                            **{k: f(th) for k, f in MENU.items()},
                            **branch_formulas(th)))
        out['relaxed_path_menu_fit'] = fit
        for r in fit:
            if 38.6 <= r['tilt_deg'] <= 43.0 and abs(r['tilt_deg'] * 20 % 4) < 1e-9:
                print(f"    {r['tilt_deg']:6.2f}  s {r['s']:.9f}  nearest {r['nearest']:8s} "
                      f"err {r['err']:.2e}   F_T {r['F_T']:.6f}  Lam {r['Lambda']:.6f}")

    # -------- 3. S07's crest, exactly (A110 sec 2.4: F_T = Lambda at sin cos = 2 cos - 1)
    f = lambda th: math.sin(th) * math.cos(th) - 2 * math.cos(th) + 1
    th_c = brentq(f, math.radians(35.0), math.radians(50.0), xtol=1e-16, rtol=1e-15)
    out['s07_crest'] = dict(tilt_deg=math.degrees(th_c), s=Lam(th_c),
                            check_F_T=F_T(th_c), check_Lambda=Lam(th_c),
                            equation='sin t cos t = 2 cos t - 1  (F_T = Lambda)',
                            barrier_over_S07=Lam(th_c) - (2 + 4 * math.sqrt(2) / 3),
                            barrier_over_trump=Lam(th_c) - A.SHAT)
    print(f"\n=== S07 crest (exact crossing F_T = Lambda): tilt {math.degrees(th_c):.9f} deg, "
          f"s = {Lam(th_c):.12f}")
    print(f"    +{out['s07_crest']['barrier_over_S07']:.6f} over S07, "
          f"+{out['s07_crest']['barrier_over_trump']:.6f} over Trump")

    out['trump'] = dict(shat=A.SHAT, tilt_deg=40.181937290329714,
                        F_T_at_trump_tilt=F_T(math.radians(40.181937290329714)))
    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'crest.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/crest.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
