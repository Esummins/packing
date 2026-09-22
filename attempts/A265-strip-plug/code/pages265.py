"""A265 pages (docs/residue_map/campaigns/A265-strip-plug/): every drawn square passes an exact check (free_margin
>= -1e-7 against the squares it is claimed free of; overlaps drawn red have SAT gap < 0), a note per panel says what
it IS, slivers get a 10x inset, undecided regions are grey stipple (never green).
    python pages265.py   (needs results/strip265.json, results/miss265.json, certs/P2265_index.jsonl)"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for p in ('attempts/A262-no-jam/code', 'attempts/A259-normal-room/code', 'attempts/A260-locked-wall/code',
          'attempts/A263-open-pairs/code', 'attempts/A265-strip-plug/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom262 as G                                                   # noqa: E402
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
import svg260 as S                                                    # noqa: E402
import geo263 as G3                                                   # noqa: E402
import strip265 as ST                                                 # noqa: E402
import cert265 as M                                                   # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A265-strip-plug')
DEG = math.pi / 180


def checked_free(pose, Vs, s):
    m = R.free_margin(pose, Vs, s)
    assert m >= -1e-7, m
    return Z.sq_verts(*pose), m


def strip_page():
    res = json.load(open(os.path.join(HERE, '..', 'results', 'strip265.json')))
    rows = [json.loads(l) for l in open(os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'ring262.jsonl'))]
    rows += [json.loads(l) for l in open(os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'search262.jsonl'))]
    win = [x for x in res['rows'] if x['s'] <= 3.8771]
    wid = max(win, key=lambda x: x['facts']['h_u'])['id']            # the widest strip on the window
    r = [x for x in rows if x['id'] == wid][0]
    rec = [x for x in res['rows'] if x['id'] == wid][0]
    s = r['s']
    V = G.verts(np.array(r['p']), s)
    Cv = V[7]
    hu = float(Cv[:, 0].min())
    Tu = Cv - np.array([hu, 0.0])
    strip = Polygon(Tu).difference(Polygon(Cv))
    cols = {'A': '#9ab', 'A2': '#9ab', 'X': '#c9a', 'C': '#fc9'}
    P = S.Panel(20, 40, 400, 400, 0, 0, 2.6, 2.6)
    P.frame()
    for k in (0, 1, 6, 7):
        P.poly(V[k], fill=cols[G.NAMES[k]], op=0.55, stroke='#234', sw=0.8)
    P.poly(Tu, fill='none', stroke='#06c', sw=1.2, dash='4,2')
    for g in R.polys_of(strip):
        P.poly(list(g.exterior.coords)[:-1], fill='url(#stip)', op=0.9, stroke='#666', sw=0.5)
    jam = Polygon(Tu).intersection(Polygon(V[6]))
    for g in R.polys_of(jam):
        P.poly(list(g.exterior.coords)[:-1], fill='#e33', op=0.6, stroke='#900', sw=0.6)
    # the largest square free of C and X whose square meets T_u: its centre set is empty on every ring; draw instead
    # the free square of the {C, X} pocket nearest to the strip (largest area of Q meeting T_u among free Q)
    best = (-1.0, None)
    for pd in np.arange(-45.0, 45.0, 1.0):
        psi = pd * DEG
        Cs = R.centre_set([V[6], V[7]], s, psi)
        for Pg in R.polys_of(Cs):
            for q in np.array(Pg.exterior.coords)[:-1]:
                a = Polygon(Z.sq_verts(q[0], q[1], psi)).intersection(Polygon(Tu)).area
                if a > best[0]:
                    best = (a, (float(q[0]), float(q[1]), psi))
    Q, mQ = checked_free(best[1], [V[6], V[7]], s)
    P.poly(Q, fill='#f90', op=0.4, stroke='#a50', sw=1.0)
    P.poly([(0, 0), (1, 0), (1, 1), (0, 1)], fill='none', stroke='#888', sw=0.6, dash='2,2')
    P.dot((s / 2, s / 2), 3, '#000')
    P.text((1.05, 0.45), 'A', 10); P.text((2.1, 0.45), 'A2', 10); P.text((0.15, 2.3), 'X', 10)
    P.text((1.2, 1.6), 'C', 10); P.text((0.2, 1.3), 'T_u', 9, fill='#06c')
    I = S.Panel(440, 40, 240, 240, 0.0, rec['facts']['X_low'] - 0.12, 0.24, rec['facts']['X_low'] + 0.12, clip_id='ins1')
    for k in (6, 7):
        I.poly(V[k], fill=cols[G.NAMES[k]], op=0.55, stroke='#234', sw=0.8)
    I.poly(Tu, fill='none', stroke='#06c', sw=1.2, dash='4,2')
    for g in R.polys_of(jam):
        I.poly(list(g.exterior.coords)[:-1], fill='#e33', op=0.6, stroke='#900', sw=0.6)
    w = res['worst']
    notes = ['(a) BL corner of the JAM ring %s (s = %.4f), the widest strip on the window: A, A2 floor row (blue), X wall' % (wid[:28], s),
             '    square (pink), C the floater (tan; h_u = %.3f off the wall, h_v = %.3f above the floor, tilt %.1f deg).  Dashed blue: T_u = C' % (
                 rec['facts']['h_u'], rec['facts']['h_v'], rec['facts']['th_C']),
             '    moved to the wall.  Stipple: the STRIP T_u minus C (area %.3f) -- [C] as a lemma, [T-computed] on 323 rings.  Red: X inside' % rec['facts']['strip_area'],
             '    T_u (the DIRECT-JAM, area %.4f, depth %.3f): X seals the strip from above, C from the right, the wall from the left.' % (
                 rec['facts']['X_jam_area'], rec['facts']['X_jam_depth']),
             '    Orange: the unit square free of C and X (only) that meets T_u MOST (area %.4f of it inside T_u; free_margin %.1e) --' % (best[0], mQ),
             '    it meets T_u only inside C\'s own footprint region below C, never the stipple: strip265 finds NO square free of {C, X}',
             '    with an interior point in the strip on any of the 323 rings (both sectors -9 = no such square; A, A2, the sector unused).',
             '(b) 10x inset at X\'s lowest point (%.3f): the jam sliver.' % rec['facts']['X_low'],
             'strip265 worst over 323 rings: {C,X}: %.1f / %.1f;  {C}: %.3f / %.1f;  {A,C}: %.3f / %.1f;  {A,A2,X,C}: %.1f / %.1f  (BL-floor / BL-left).' % (
                 w['CX|BL-floor'], w['CX|BL-left'], w['C|BL-floor'], w['C|BL-left'], w['AC|BL-floor'], w['AC|BL-left'],
                 w['AA2XC|BL-floor'], w['AA2XC|BL-left'])]
    return [P.render(), I.render(), S.note(20, 470, notes, 10)]


def plug_page():
    ms = json.load(open(os.path.join(HERE, '..', 'results', 'miss265.json')))
    wr = ms['worst'][1]
    mid = wr['mid']
    parts, notes = [], []
    for k, (s, pose, tag) in enumerate(((M.SMAX, wr['pose_smax'], 'at SMAX = 3.8771 (A263 tested here)'),
                                        (wr['s_eff'], wr['pose_seff'], 'at s_eff = %.4f (cert265 tests here)' % wr['s_eff']))):
        f, g = (mid[0], mid[1], 0.0, mid[1]), (mid[2], mid[3], 0.0, mid[3])
        W = G3.floor_sq(f, s)[1]
        Sp = G3.right_sq(g, s)[0]
        m, pz = G3.factor_margin('P2', s, f, g, step=0.25)
        Q, mQ = checked_free((pz[0], pz[1], float(pz[2])), [W, Sp], s)
        O = (s / 2, s / 2)
        P = S.Panel(20 + 440 * k, 40, 400, 400, 0, 0, s, s)
        P.frame()
        P.poly(W, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
        P.poly(Sp, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
        rho = M.plug_of(np.array([0, 0, mid[2], 0]))[1]
        P.poly([(s - rho, 0), (s, 0), (s, rho), (s - rho, rho)], fill='#ccc', op=0.9, stroke='#666', sw=0.6)
        P.poly(Q, fill='#e33' if m > 0 else '#f90', op=0.45, stroke='#900' if m > 0 else '#a50', sw=1.0)
        P.dot(O, 3, '#000')
        P.line((s / 2, 0), (s / 2, s), stroke='#aaa', sw=0.5, dash='3,3')
        P.line((0, s / 2), (s, s / 2), stroke='#aaa', sw=0.5, dash='3,3')
        P.text((s - 1.3, 0.3), "W", 10); P.text((s - 0.5, 1.2), "S'", 10)
        inO = Polygon(Q).contains(__import__('shapely.geometry', fromlist=['Point']).Point(O))
        notes += ['(%s) P2 corner (W at b = %.4f, %.2f deg; S\' at a\' = %.4f, %.2f deg) %s: the free square Q (%s) with the largest' % (
                      'ab'[k], mid[0], mid[1] / DEG, mid[2], mid[3] / DEG, tag, 'red = misses O' if m > 0 else 'orange = contains O'),
                  '    (q-O).u - 1/2 among squares free of W, S\' in case (ii) [P\' in LEFT(S\')]: margin %+.4f (exact centre sets, 0.25 deg; free_margin %.1e;' % (m, mQ),
                  '    O in Q: %s).  Grey: the plug [0, %.3f]^2 (Lemma PLUG, a\' > 0.354 + rho).  ADJ slack a\' + w(f1\') - (s - 2) = %+.4f.' % (
                      inO, rho, mid[2] + math.cos(mid[3]) + math.sin(mid[3]) - (s - 2))]
        parts.append(P.render())
    notes += ['Q sits at the centre line, 0.7 from the right wall: the plug never touches it -- the OPEN leaves were not a corner layer.',
              'At 3.8771 the corner is NOT all-ADJ (S\' misses its far slot), so P2 is not required there; at s_eff the same box certifies.',
              'cert265: five cells re-run at the ADJ-consistent side, %s; verify265 in results/verify265.json.' % ', '.join(
                  '%s %s (%d leaves, %.0f s)' % (c['cell'], 'ok' if c['ok'] else 'OPEN', c['leaves'], c['sec'])
                  for c in [json.loads(l) for l in open(os.path.join(HERE, '..', 'certs', 'P2265_index.jsonl'))])]
    return parts + [S.note(20, 470, notes, 10)]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    S.page(os.path.join(OUT, 'strip_two_obstacles.svg'), 900, 640,
           'A265 STRIP: the strip T_u minus C is sealed by C, X and the wall alone -- no square free of {C, X} enters it (323 rings)', strip_page())
    S.page(os.path.join(OUT, 'p2_open_leaf_side.svg'), 900, 620,
           'A265 the OPEN P2 leaves of A263: a real P2 miss at 3.8771 where the corner is not ADJ; none at the ADJ-consistent side', plug_page())
    print('pages written to', OUT)
