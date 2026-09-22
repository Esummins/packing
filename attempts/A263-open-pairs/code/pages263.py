"""A263 pages (geometry-checked; a note per panel says what it IS; slivers get a 10x inset; undecided = grey stipple):
  wedge_notch.svg   (a) the wedge notch between s1 (f1) and W (fW != f1) with the DEEPEST free square (exact centre
                    set) and the closed-form locus of the least depth vs psi;  (b) the factor map: which factor sees
                    which region of the miss-vertex (P2 / WE / WS), drawn on A260's worst adversary corner.
  nonadj_gap.svg    (c) a non-ADJ floor at common tilt with a shift e wide enough for a unit cell touching the wall
                    between s1 and W: ROOM <= 1 fails as a bare-ring statement (a free square missing O, exact check).
  near_flat.svg     (d) the all-near-flat mixed ring at tilt 0.7 deg: the LP minimiser (b_w = 1, a_w = s - 3) drawn as
                    squares, the mixed corners marked; the slab as grey stipple in the (eps, s) plane with the measured
                    margin law.       python pages263.py"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo263 as G                                                    # noqa: E402
import notch263 as NB                                                 # noqa: E402
import svg260 as S                                                    # noqa: E402
H, Z, R, DEG = G.H, G.Z, G.R, G.DEG
OUT = os.path.join(G.ROOT, 'docs', 'residue_map', 'campaigns', 'A263-open-pairs')
RES = os.path.join(HERE, '..', 'results')


def checked_free(pose, Vs, s):
    m = R.free_margin(pose, Vs, s)
    assert m >= -1e-7, m
    return Z.sq_verts(*pose)


def wedge_notch():
    s, f1, fW, gam = 8.0, 10 * DEG, 20 * DEG, 0.08
    e = gam - (math.cos(fW) - math.cos(f1)) * math.tan(f1)
    dW = 4.0
    Vs = [H.toucher(dW - e - 1.0 / math.cos(f1), f1, s, 0), H.toucher(dW, fW, s, 0)]
    assert Z.poly_gap(Vs[0], Vs[1]) >= -1e-12
    AW = np.array([dW, math.cos(fW)])
    best = None
    for psid in np.arange(0.0, 45.01, 0.5):
        got = NB.exact(gam, f1, fW, psid * DEG, 'depth')
        if got is not None and (best is None or got < best[0]):
            best = (got, psid)
    psi = best[1] * DEG
    C = R.centre_set(Vs, s, psi)
    off = G.near_offset(psi, 0)
    F = G.setup(gam, f1, fW) if hasattr(G, 'setup') else NB.setup(gam, f1, fW)
    C = C.intersection(G.halfplane(AW - off, -F['uW'])).intersection(G.halfplane(AW + F['T1'] - off, F['u1']))
    q = min((np.array(Pg.exterior.coords)[:-1] for Pg in R.polys_of(C)), key=lambda A: (A + off)[:, 1].min())
    q = q[(q + off)[:, 1].argmin()]
    Q = checked_free((q[0], q[1], psi), Vs, s)
    depth = (Q[:, 1]).min()
    P = S.Panel(20, 40, 520, 300, 2.0, 0.0, 6.5, 2.6)
    P.frame()
    for V in Vs:
        P.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
    P.poly(Q, fill='#f90', op=0.5, stroke='#a50', sw=1.0)
    P.line((2.0, 1.0), (6.5, 1.0), stroke='#888', dash='3,3')
    P.dot(AW, 3, '#c00')
    P.text((2.1, 2.45), 'panel (a): s1 (tilt %.0f) and W (tilt %.0f), gamma = %.2f; the DEEPEST free square over the notch' % (
        f1 / DEG, fW / DEG, gam), 10)
    P.text((2.1, 2.3), 'exact centre set, psi = %.1f deg: depth %.4f (closed form %.4f); dashed = depth 1' % (
        best[1], depth, NB.closed(gam, f1, fW, psi, 'depth')[0] + math.cos(fW)), 10)
    lo = Q[Q[:, 1].argmin()]
    I = S.Panel(560, 40, 200, 200, lo[0] - 0.05, lo[1] - 0.05, lo[0] + 0.05, lo[1] + 0.05, clip_id='c0')
    for V in Vs:
        I.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=1.5)
    I.poly(Q, fill='#f90', op=0.5, stroke='#a50', sw=1.5)
    I.line((lo[0] - 1, math.cos(fW)), (lo[0] + 1, math.cos(fW)), stroke='#c00', dash='3,3')
    L = S.Panel(20, 380, 520, 200, 0.0, 0.85, 1.0, 1.05)                # x = psi / 45 deg
    L.frame()
    pts, ex = [], []
    for psid in np.arange(0.0, 45.01, 1.0):
        pts.append((psid / 45.0, NB.closed(gam, f1, fW, psid * DEG, 'depth')[0] + math.cos(fW)))
        g = NB.exact(gam, f1, fW, psid * DEG, 'depth')
        if g is not None:
            ex.append((psid / 45.0, g + math.cos(fW)))
    L.path(pts, stroke='#06c', sw=1.5)
    for p in ex[::3]:
        L.dot(p, 2, '#c00')
    L.line((0, 1.0), (1, 1.0), stroke='#888', dash='3,3')
    L.line((0, math.cos(fW)), (1, math.cos(fW)), stroke='#c00', dash='2,2')
    L.text((0.02, 1.03), 'least depth vs psi (x = psi / 45 deg): closed form (blue) = exact (red dots); red dashed cos fW = %.3f; deepest at psi = %.0f' % (
        math.cos(fW), best[1]), 10)
    return [P.render(), I.render(), L.render(),
            S.note(560, 260, ['10x inset: the lowest vertex in the wedge;', 'red dashed = height of W\'s left vertex',
                              '(cos fW): the vertex dips below it', 'by first order in gamma.'], 10)]


def factor_map():
    rows = [json.loads(l) for l in open(os.path.join(G.ROOT, 'attempts', 'A260-locked-wall', 'results', 'adv260.jsonl'))]
    r = max((r for r in rows if not r['same']), key=lambda r: r['pierceO'])
    x, s = np.array(r['x']), r['s']
    k = max(range(4), key=lambda k: G.factor_margin('FULL', s, *G.corner_of_ring(x, s, k), step=3.0)[0])
    f, g = G.corner_of_ring(x, s, k)
    Vs = G.floor_sq(f, s) + G.right_sq(g, s)
    fr = G.frames(s, f, g)
    P = S.Panel(20, 620, 400, 400, 0, 0, s, s)
    P.frame()
    for j, V in enumerate(Vs):
        P.poly(V, fill=['#47c', '#9ab', '#9ab', '#47c'][j], op=0.55, stroke='#234', sw=0.8)
    P.dot((s / 2, s / 2), 3, '#000')
    AW, uW, T1, u1 = fr['AW'], fr['uW'], fr['T1'], fr['u1']
    P.line(AW - 3 * uW, AW + 3 * uW, stroke='#c00', dash='5,3')
    P.line(T1 - 3 * u1, T1 + 3 * u1, stroke='#06c', dash='5,3')
    res = {}
    for kind in ('FULL', 'P2', 'WE', 'WS'):
        m, pose = G.factor_margin(kind, s, f, g, 1.0)
        res[kind] = (m, pose)
    for kind, col in (('P2', '#0a0'), ('WE', '#c00'), ('WS', '#06c')):
        m, pose = res[kind]
        Q = checked_free(pose[:3], {'P2': [Vs[1], Vs[2]], 'WE': Vs[:2], 'WS': Vs[2:]}[kind], s)
        P.poly(Q, fill='none', stroke=col, sw=1.4)
    notes = ['panel (b): the FACTOR MAP on A260\'s worst adversary corner (independent tilts, s = %.4f):' % s,
             'floor tilts %.1f / %.1f (shift %.3f), right wall %.1f / %.1f (shift %.3f)' % (
                 f[3] / DEG, f[1] / DEG, f[2], g[1] / DEG, g[3] / DEG, g[2]),
             'red dashed = W\'s left-vertex line (RIGHT region beyond it), blue dashed = S\'\'s top-vertex line (LEFT region before it)',
             'outlined squares: the worst free square of each factor, drawn only if it passes the exact SAT check:',
             '  P2 (green) %+.4f   WE (red) %+.4f   WS (blue) %+.4f   FULL %+.4f  -- all < 0: every free square contains O' % (
                 res['P2'][0], res['WE'][0], res['WS'][0], res['FULL'][0]),
             'FULL <= max(P2, WE, WS) [T]; the principal-normal clip is what keeps P2 true (without it +0.03).']
    return [P.render(), S.note(440, 640, notes, 10)]


def nonadj_gap():
    s, phi = G.SHAT, 2.0 * DEG                                        # near-flat: the corner forms allow e up to 1.118
    e = 1.06                                                          # >= 1 + w - sec = 1.034: a flat unit cell fits the gap
    a = 0.03                                                          # >= a_min(2 deg) = 0.0175 (neighbour at 2 deg)
    b = s - a - 1.0 / math.cos(phi) - H.w_of(phi) - e                 # = 0.752 >= b_min(2 deg) = 0.707 (neighbour at 45 deg)
    Vs = G.floor_sq((b, phi, e, phi), s)
    assert Z.poly_gap(Vs[0], Vs[1]) >= -1e-12 and 0 < a < 1 and 0 < b < 1, (a, b)
    xL = a + H.w_of(phi)
    Q = checked_free((xL + 0.5 + 0.005, 0.5 + 0.02, 0.0), Vs, s)
    O = np.array([s / 2, s / 2])
    inQ = all(abs((O - Q.mean(0)) @ (Q[1] - Q[0])) < 0.5 and abs((O - Q.mean(0)) @ (Q[3] - Q[0])) < 0.5 for _ in (0,))
    P = S.Panel(20, 40, 420, 420, 0, 0, s, s)
    P.frame()
    for V in Vs:
        P.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
    P.poly(Q, fill='#f90', op=0.5, stroke='#a50', sw=1.0)
    P.dot(O, 3, '#000')
    for x0 in (1.0, 2.0, s - 2, s - 1):
        P.line((x0, 0), (x0, 1), stroke='#888', dash='2,2')
    notes = ['non-ADJ floor at common tilt %.3f deg, s = %.4f: a = %.2f (s1 does not reach the far slot: a + w = %.3f < s - 2 = %.3f),' % (
                 phi / DEG, s, a, a + H.w_of(phi), s - 2),
             'shift e = %.3f >= 1 + w - sec = %.3f: a unit square (orange, flat) sits in the gap touching depth 0.02 --' % (
                 e, 1 + H.w_of(phi) - 1 / math.cos(phi)),
             'exact SAT check passed; it does NOT contain O (%s).  This is what ROOM <= 1 must not claim on the non-ADJ family:' % (
                 'O inside' if inQ else 'O outside'),
             'the free square has a free straight drop, so P1 (TOUCH-CELL) kills it -- a structure lemma, not room (open_pairs.md s.3.3).',
             'Here b = %.3f >= b_min = 0.707 and a >= a_min = 0.0175: the corner forms with the neighbours\' offsets <= 1 admit' % b,
             'this wall (neighbour tilts 45 deg at the END corner, 2 deg at the START corner); the rest of the ring is not drawn.']
    return [P.render(), S.note(20, 480, notes, 10)]


def near_flat():
    s, eps = 3.8771, 0.7 * DEG
    x = []
    for w in range(4):
        x += [s - 3.0, eps, 1.0, eps]
    x = np.array(x)
    Vs = H.hyb_verts(x, s)
    P = S.Panel(20, 40, 420, 420, 0, 0, s, s)
    P.frame()
    for j, V in enumerate(Vs):
        P.poly(V, fill='#9ab' if j // 2 != 3 else '#c9a', op=0.55, stroke='#234', sw=0.8)
    gaps = [Z.poly_gap(Vs[i], Vs[j]) for i in range(8) for j in range(i) if i // 2 != j // 2]
    P.dot((s / 2, s / 2), 3, '#000')
    for k in range(4):
        P.text(Z.rot_k([(s - 0.5, 0.15)], s, k)[0], 'corner %d%s' % (k, ' MIXED' if k in (3, 0) else ''), 9)
    D = S.Panel(480, 40, 420, 300, 0.0, 3.0, 1.5, 4.0)
    D.frame()
    for a, bb in ((0, 0.703), (0.703, 1.5)):
        D.poly([(a, 3), (bb, 3), (bb, 4), (a, 4)], fill='url(#stip)' if a == 0 else '#dfd', op=0.6 if a else 1.0,
               stroke='none')
    D.line((0, 3.8771), (1.5, 3.8771), stroke='#000', dash='4,2')
    D.text((0.75, 3.9), 's-hat = 3.8771', 9)
    D.text((0.05, 3.1), 'grey: the slab (0, 0.703 deg) -- no box certificate', 9)
    D.text((0.8, 3.1), 'green: A261 certified (tilts >= 0.703 deg)', 9)
    notes = ['left: the LP minimiser of the + + + - pattern at all tilts 0.7 deg, s = 3.8771: a_w = s - 3, b_w = 1 -- the flat DOMINO',
             'pinwheel; wall 3 (pink) has sense -.  As drawn (b_w = 1 exactly) the END squares do NOT meet their boxes: the closed',
             'relaxation is feasible (least ring gap %.4f), the strict box condition is violated by 0.  The LP margin tau* is' % min(gaps),
             '0.00079 / 0.00039 / 0.00011 / 0.00003 at eps = 0.7 / 0.35 / 0.1 / 0.03 deg: proportional to eps (slab263).',
             'right: (tilt of a wall, s): the A261 certificates (green) stop at 0.703 deg; the slab (stipple) is UNDECIDED,',
             'certifiable by the same engine except in the all-near-flat cube of + + + - and + - + - (open_pairs.md s.5.3).']
    return [P.render(), D.render(), S.note(480, 360, notes, 10)]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    S.page(os.path.join(OUT, 'wedge_notch.svg'), 1000, 1040,
           'A263 (a): the wedge notch with the deepest free square; the factorised certificate map', wedge_notch() + factor_map())
    S.page(os.path.join(OUT, 'nonadj_gap.svg'), 900, 600,
           'A263 (c): a non-ADJ wall whose gap holds a unit cell -- ROOM <= 1 is false as a bare-ring statement', nonadj_gap())
    S.page(os.path.join(OUT, 'near_flat.svg'), 940, 480,
           'A263 (d): the near-flat mixed ring (the domino pinwheel) and the slab', near_flat())
    print('pages written to', OUT)
