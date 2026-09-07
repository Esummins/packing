"""A122 T5 - what A116's local-certificate machinery would be handed for S33min / S35min / S38min.

A116's N is a product of pose boxes around the LOAD-BEARING squares L, anchored in the class frame
at s0, together with the class pins P; its soundness canary is that no D4 image of Trump satisfies
N's hypothesis (a Trump square in every box).  Two numbers decide how big N may be before the
canary fires:

  r_max  = max over n in L of ( min over Trump squares j of |c_n(s0) - c_j| )
           -- the largest CENTRE radius at which some box of L still contains no Trump square
           (any r < r_max excludes Trump on position alone, with no tilt cut at all);
  rho_at(r) = for the box that fails first, the tilt distance to the nearest Trump square that IS
           inside it at radius r -- the tilt cut that has to be added once r >= r_max.

Anchoring: A116 dilates the shadow's pose to side s0 (c * s0/s*) for the tilted squares and puts a
load-bearing SLOT square on its slot cell at s0.  Both conventions are applied here.

Outputs results/a116_input.json.
"""
from __future__ import annotations

import json
import math
import os

import a122lib as A


def dilate(s, cfg, names, s_target):
    """A116's anchoring: tilted squares scaled by s0/s*, slot squares on their s0 cells."""
    out = []
    for i, (x, y, t) in enumerate(cfg):
        if i >= 5:
            a, b, c, d = A.MZ.slot_affine(names[i])
            out.append((a + b * s_target, c + d * s_target, 0.0))
        else:
            out.append((x * s_target / s, y * s_target / s, t))
    return out


def canary(anchor, L_idx, trump_cfg):
    rows = []
    for i in L_idx:
        cx, cy, th = anchor[i]
        best = min(((math.hypot(cx - q[0], cy - q[1]), q) for q in trump_cfg),
                   key=lambda t: t[0])
        dt = min(abs(A.tmod(th) - A.tmod(best[1][2])), 90 - abs(A.tmod(th) - A.tmod(best[1][2])))
        rows.append(dict(idx=i, centre=[cx, cy], tilt_deg=A.tmod(th),
                         nearest_trump=[best[1][0], best[1][1], A.tmod(best[1][2])],
                         d_centre=best[0], d_tilt_deg=dt))
    return rows


def main():
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    rg = json.load(open(os.path.join(A.RES, 'rigidity.json'), encoding='utf-8'))
    st, cfgt = A.load_trump()
    out = {'s0': A.S0, 'shat': A.SHAT}
    for tag, sid in (('S33min', 'S33'), ('S35min', 'S35'), ('S38min', 'S38')):
        b = d['entries'][sid]['best']
        s, cfg = b['sigma'], [tuple(c) for c in b['cfg']]
        names = A.names_for(sid)
        anchor = dilate(s, cfg, names, A.S0)
        # L = the squares carrying a nonzero Fritz-John force (A116's "load-bearing")
        force = rg[tag]['analysis']['resultant']
        loaded = set()
        for k, v in force.items():
            if v > 1e-6:
                for nm in k.split('|'):
                    if nm in names:
                        loaded.add(names.index(nm))
        L_idx = sorted(loaded)
        rows = canary(anchor, L_idx, cfgt)
        rmax = max(r['d_centre'] for r in rows)
        arg = max(rows, key=lambda r: r['d_centre'])
        # once r >= r_max the tightest box is the one with the smallest d_centre
        tight = min(rows, key=lambda r: r['d_centre'])
        out[tag] = dict(s_star=s, L=[names[i] for i in L_idx], rows=rows,
                        r_max_position_only=rmax, r_max_at=names[arg['idx']],
                        tightest_box=names[tight['idx']],
                        tightest_d_centre=tight['d_centre'],
                        tightest_d_tilt_deg=tight['d_tilt_deg'])
        print(f'\n=== {tag}  L = {[names[i] for i in L_idx]}')
        for r in rows:
            print(f"   {names[r['idx']]:9s} anchor ({r['centre'][0]:.4f},{r['centre'][1]:.4f},"
                  f"{r['tilt_deg']:7.3f})  nearest Trump square d_c {r['d_centre']:.4f}  "
                  f"d_tilt {r['d_tilt_deg']:7.3f}")
        print(f'   -> Trump is excluded on POSITION alone for every r < {rmax:.4f} '
              f'(the box of {names[arg["idx"]]} contains no Trump square)')
        print(f'   -> the first box to admit a Trump square is {names[tight["idx"]]} at '
              f'r = {tight["d_centre"]:.4f}; its tilt distance is {tight["d_tilt_deg"]:.3f} deg')

    # S07 for contrast (A116's own case)
    s07, cfg07 = A.load_s07_exact()
    anchor = dilate(s07, cfg07, list(A.FREE) + list(A.SLOTS), A.S0)
    rows = canary(anchor, [0, 2, 4], cfgt)          # A116's L = {f0, f2, f4}
    out['S07_for_contrast'] = dict(L=['f0', 'f2', 'f4'], rows=rows,
                                   r_max_position_only=max(r['d_centre'] for r in rows))
    print(f"\n=== S07 (A116's own L = f0, f2, f4), for contrast")
    for r in rows:
        print(f"   f{r['idx']}  d_c {r['d_centre']:.4f}  d_tilt {r['d_tilt_deg']:7.3f}")
    print(f"   -> position-only exclusion radius {out['S07_for_contrast']['r_max_position_only']:.4f}")

    json.dump(out, open(os.path.join(A.RES, 'a116_input.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/a116_input.json')


if __name__ == '__main__':
    main()
