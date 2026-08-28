#!/usr/bin/env python
"""Probe one face at one ring: what does the LP want, which branches fail."""
import sys
import os
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A36-levers', 'code'))
import a40_grow as G                    # noqa: E402
import strata_lib as SL                 # noqa: E402
import m2_lib as M                      # noqa: E402


def probe(ars, i, sgn, h_in, h_out):
    print('=== face %s ring [%.5f, %.5f]' % (G.face_label(i, sgn),
                                             float(h_in), float(h_out)))
    ff = G.Facts(ars, G.face_subbox(i, sgn, h_in, h_out),
                 G.face_label(i, sgn))
    status = {k: ff.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    cond = [k for k in range(ars.n) if status[k] == 'cond']
    mA, xA = G.anchor_lp(ars, unc, i, sgn, h_in, h_out)
    print('tier2 uncond LP margin:', mA)
    full = unc + cond
    mB, xB = G.anchor_lp(ars, full, i, sgn, h_in, h_out)
    print('tier3 mixed LP margin:', mB)
    if mB is None:
        return
    loads = [(ars.rows[k][0], status[k], float(q), ars.rows[k][3])
             for k, q in zip(full, xB[:len(full)]) if q > 1e-6]
    loads.sort(key=lambda t: -t[2])
    print('top loads:')
    for t in loads[:18]:
        print('   %-24s %-7s %9.4f  pair=%s' % t)
    prs = sorted({ars.rows[k][3] for k, q in zip(full, xB[:len(full)])
                  if q > 1e-9 and status[k] == 'cond'})
    for pr in prs:
        cls, sel, alive = ff.pair_class[pr]
        print(' pair %s class %s alive %s' % (pr, cls, alive))
        for ax in alive:
            sel2 = list(unc) + [k for k in ars.by_axis.get(ax, ())
                                if status[k] == 'cond']
            mC, xC = G.anchor_lp(ars, sel2, i, sgn, h_in, h_out)
            print('   solo-branch %s -> margin %s' % (ax, mC))


def probe_branch(ars, i, sgn, h_in, h_out, ctx):
    print('=== face %s ring [%.5f, %.5f] branch %s'
          % (G.face_label(i, sgn), float(h_in), float(h_out), ctx))
    ff = G.Facts(ars, G.face_subbox(i, sgn, h_in, h_out),
                 G.face_label(i, sgn))
    status = {k: ff.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    sel = list(unc)
    for pr, ax in ctx.items():
        sel += [k for k in ars.by_axis.get(ax, ())
                if status[k] == 'cond']
    others = [k for k in range(ars.n)
              if status[k] == 'cond' and ars.rows[k][3] not in ctx]
    full = sel + others
    mD, xD = G.anchor_lp(ars, full, i, sgn, h_in, h_out)
    print('full-arsenal-on-branch margin:', mD)
    if mD is None:
        return
    om = xD[:len(full)]
    ob = xD[len(full)]
    print('omega_b = %.4f  gain = %.6f' % (ob, ob * float(h_in)))
    v0 = sum(ars.gmid[k] * q for k, q in zip(full, om))
    hm = 0.5 * sum(ars.wmass[k] * q for k, q in zip(full, om))
    print('V0(mid) = %.6f   Hmass = %.4f  quad = %.6f'
          % (v0, hm, hm * float(h_out) ** 2))
    loads = [(ars.rows[k][0], status[k], float(q), ars.gmid[k],
              ars.wmass[k]) for k, q in zip(full, om) if q > 1e-6]
    loads.sort(key=lambda t: -t[2] * t[4])
    print('top loads by curvature contribution:')
    for t in loads[:20]:
        print('   %-24s %-7s om=%9.4f gval=%9.5f w=%7.3f' % t)


def probe_cuts(ars, i, sgn, h_in, h_out, ctx, pr_cut):
    print('=== tie-cut probe face %s branch %s cut pair %s'
          % (G.face_label(i, sgn), ctx, pr_cut))
    ff = G.Facts(ars, G.face_subbox(i, sgn, h_in, h_out),
                 G.face_label(i, sgn))
    status = {k: ff.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    sel = list(unc)
    for pr, ax in ctx.items():
        sel += [k for k in ars.by_axis.get(ax, ())
                if status[k] == 'cond']
    fcut = G.face_cut(i, sgn, h_in)
    for s in (+1, -1):
        for div in (2, 8, 32):
            tau = h_in / div
            anc, cst = G.tie_cuts(pr_cut, s, tau)
            ma, xa, ca = G.anchor_lp(ars, ars.masses(h_out), sel,
                                     [fcut, anc], h_out)
            mc, xc, cc = G.anchor_lp(ars, ars.masses(h_out), sel,
                                     [fcut, cst], h_out)
            print('  s=%+d tau=h/%d: anchor-side %.3g  cost-side %.3g'
                  % (s, div, ma if ma is not None else float('nan'),
                     mc if mc is not None else float('nan')),
                  'cut omegas', ca, cc)


def probe_ctx(ars, i, sgn, h_in, h_out, ctx):
    print('=== ctx probe face %s branch %s' % (G.face_label(i, sgn), ctx))
    ff = G.Facts(ars, G.face_subbox(i, sgn, h_in, h_out),
                 G.face_label(i, sgn))
    status = {k: ff.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    sel = list(unc)
    for pr, ax in ctx.items():
        sel += [k for k in ars.by_axis.get(ax, ())
                if status[k] == 'cond']
    w = ars.masses(h_out)
    fcut = G.face_cut(i, sgn, h_in)
    m, x, c = G.anchor_lp(ars, w, sel, [fcut], h_out)
    print('anchor LP margin:', m, 'omega_b', c)
    mE, xE = G.empty_lp(ars, w, sel, h_out)
    print('empty LP margin:', mE)
    # what would help: full arsenal on this branch
    others = [k for k in range(ars.n)
              if status[k] == 'cond' and ars.rows[k][3] not in ctx]
    full = sel + others
    mD, xD, _ = G.anchor_lp(ars, w, full, [fcut], h_out)
    print('with all other cond rows:', mD)
    if mD is not None:
        loads = {}
        for k, q in zip(full, xD):
            if q > 1e-6 and status[k] == 'cond' and \
                    ars.rows[k][3] not in ctx:
                loads[ars.rows[k][0]] = (round(float(q), 4),
                                         ars.rows[k][3])
        print('cond loads outside ctx:', loads)


def deep_face(ars, i, sgn, h_in, h_out, budget=600.0):
    import time
    print('=== deep search face %s ring [%.6f, %.6f] budget %.0fs'
          % (G.face_label(i, sgn), float(h_in), float(h_out), budget))
    rf = G.Facts(ars, __import__('m2_lib').box_around(
        __import__('strata_lib').z_hat(), h_out), 'ring')
    w = ars.masses(h_out)
    floors = G.ring_floors(ars, h_out)
    G.FACE_BUDGET = budget
    t0 = time.time()
    mode, certs, info = G.do_face(ars, rf, w, floors, i, sgn, h_in, h_out)
    print('mode:', mode, 'info:', str(info)[:400])
    if certs:
        print('n_certs:', len(certs),
              'min margin:', min(c['claims']['margin'] for c in certs
                                 if 'claims' in c))
    print('%.1f s' % (time.time() - t0))
    return mode


def probe_ctx2(ars, i, sgn, h_in, h_out, ctx):
    """LP margins for a ctx: raw, with floors, with others; and the empty."""
    ff = G.Facts(ars, G.face_subbox(i, sgn, h_in, h_out),
                 G.face_label(i, sgn))
    status = {k: ff.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    floors = G.ring_floors(ars, h_out)
    sel = list(unc)
    for pr, ax in ctx.items():
        sel += [k for k in ars.by_axis.get(ax, ())
                if status[k] == 'cond']
    cols = [(k, None) for k in sel] + G.floor_cols(ars, floors, status,
                                                   set(sel))
    w = ars.masses(h_out)
    cuts = [G.face_cut(i, sgn, h_in)]
    m, x, c = G.anchor_lp(ars, w, cols, cuts, h_out)
    mE, _ = G.empty_lp(ars, w, sel, h_out)
    others = [k for k in range(ars.n)
              if status[k] == 'cond' and ars.rows[k][3] not in ctx and
              ff.pair_class[ars.rows[k][3]][0] != 'SAFE']
    full = cols + [(k, None) for k in others]
    mD, xD, _ = G.anchor_lp(ars, w, full, cuts, h_out)
    loads = {}
    if mD is not None:
        for (k, lb), q in zip(full, xD):
            if lb is None and q > 1e-6 and status[k] == 'cond' and \
                    ars.rows[k][3] not in ctx:
                loads.setdefault(ars.rows[k][3], 0.0)
                loads[ars.rows[k][3]] += float(q)
    print('  ctx %-40s m=%.3g mE=%.3g mD=%.3g wants=%s'
          % (str(ctx)[:40],
             m if m is not None else float('nan'),
             mE if mE is not None else float('nan'),
             mD if mD is not None else float('nan'),
             {str(p): round(v, 3) for p, v in loads.items()}))
    return loads


def main():
    ars = G.Arsenal()
    h_in = Fraction(1277, 200000)
    h_out = Fraction(668, 100000)
    ff = G.Facts(ars, G.face_subbox(20, -1, h_in, h_out), 'probe')
    print('pair (7,8) class:', ff.pair_class[(7, 8)])
    for ax in ff.pair_class[(7, 8)][2]:
        loads = probe_ctx2(ars, 20, -1, h_in, h_out, {(7, 8): ax})
    # descend the heaviest demand chain under (7,0,8)
    ctx = {(7, 8): (7, 0, 8)}
    for _ in range(5):
        loads = probe_ctx2(ars, 20, -1, h_in, h_out, ctx)
        if not loads:
            break
        pr = max(loads, key=loads.get)
        pr = eval(pr) if isinstance(pr, str) else pr
        for ax in ff.pair_class[pr][2]:
            probe_ctx2(ars, 20, -1, h_in, h_out, {**ctx, pr: ax})
        ctx[pr] = ff.pair_class[pr][2][0]


if __name__ == '__main__':
    main()
