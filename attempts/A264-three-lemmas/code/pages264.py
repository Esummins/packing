"""A264 pages (docs/residue_map/campaigns/A264-three-lemmas/): every drawn square passes an exact check
(free_margin >= -1e-7 for free squares; SAT gap < 0 for the overlaps drawn red), a note per panel says what it IS,
slivers get a 10x inset, undecided regions are grey stipple (never green), decided ones light green.
    python pages264.py
"""
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
          'attempts/A263-open-pairs/code', 'attempts/A264-three-lemmas/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom262 as G                                                   # noqa: E402
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
import svg260 as S                                                    # noqa: E402
import geo263 as G3                                                   # noqa: E402
import corner264 as C4                                                # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A264-three-lemmas')
DEG = math.pi / 180
SHAT = 3.877083590022814


def checked_free(pose, Vs, s):
    m = R.free_margin(pose, Vs, s)
    assert m >= -1e-7, m
    return Z.sq_verts(*pose), m


def worst_bl_floor(Vs, s, step=1.0):
    """the free square of the BL-floor sector with the largest (q - O).(-v) - 1/2 (exact centre sets)."""
    from shapely.geometry import box as sbox
    O = np.array([s / 2, s / 2])
    best, arg = -9.0, None
    for pd in np.arange(-45.0, 45.0, step):
        psi = pd * DEG
        C = R.centre_set(Vs, s, psi)
        if C.is_empty:
            continue
        v = np.array([-math.sin(psi), math.cos(psi)])
        for Pg in R.polys_of(C.intersection(sbox(-1, -1, s / 2, s + 1))):
            A = np.array(Pg.exterior.coords)[:-1]
            vals = (A - O) @ (-v) - 0.5
            i = int(vals.argmax())
            if vals[i] > best:
                best, arg = float(vals[i]), (float(A[i, 0]), float(A[i, 1]), psi)
    return best, arg


def draw_ring(P, V, names, cols):
    for k, Vk in enumerate(V):
        P.poly(Vk, fill=cols.get(names[k], '#9ab'), op=0.55, stroke='#234', sw=0.8)


def jammed_sector():
    rows = [json.loads(l) for l in open(os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'ring262.jsonl'))]
    r = rows[0]                                                     # A261's witness installed at s-hat
    s = r['s']
    V = G.verts(np.array(r['p']), s)
    Cv = V[7]
    hu = float(Cv[:, 0].min())
    Tu = Cv - np.array([hu, 0.0])
    strip = Polygon(Tu).difference(Polygon(Cv))
    Vs = [V[0], V[1], V[6], V[7]]
    best, pose = worst_bl_floor(Vs, s)
    Q, mQ = checked_free(pose, Vs, s)
    cols = {'A': '#9ab', 'A2': '#9ab', 'X': '#c9a', 'C': '#fc9'}
    P = S.Panel(20, 40, 400, 400, 0, 0, 2.6, 2.6)
    P.frame()
    for k in (0, 1, 6, 7):
        P.poly(V[k], fill=cols[G.NAMES[k]], op=0.55, stroke='#234', sw=0.8)
    P.poly(Tu, fill='none', stroke='#06c', sw=1.2, dash='4,2')
    for g in R.polys_of(strip):
        P.poly(list(g.exterior.coords)[:-1], fill='url(#stip)', op=0.9, stroke='#666', sw=0.5)
    P.poly(Q, fill='#f90', op=0.45, stroke='#a50', sw=1.0)
    P.poly([(0, 0), (1, 0), (1, 1), (0, 1)], fill='none', stroke='#888', sw=0.6, dash='2,2')
    P.dot((s / 2, s / 2), 3, '#000')
    P.text((1.05, 0.45), 'A', 10); P.text((2.1, 0.45), 'A2', 10); P.text((0.15, 2.3), 'X', 10)
    P.text((1.2, 1.6), 'C', 10); P.text((0.25, 1.25), 'T_u', 9, fill='#06c')
    gapCA = Z.poly_gap(V[7], V[0])
    I = S.Panel(440, 40, 240, 240, 0.9, 0.9, 1.4, 1.4, clip_id='ins1')
    for k in (0, 7):
        I.poly(V[k], fill=cols[G.NAMES[k]], op=0.55, stroke='#234', sw=0.8)
    I.poly(Tu, fill='none', stroke='#06c', sw=1.2, dash='4,2')
    I.poly(Q, fill='#f90', op=0.45, stroke='#a50', sw=1.0)
    # panel (c): the worst window ring (lifted-end near-flat jam)
    sub = json.load(open(os.path.join(HERE, '..', 'results', 'sub264.json')))
    W = [x for x in sub['rows'] if x['s'] <= 3.8771]
    wid = max(W, key=lambda x: x['sectors']['AA2XC']['BL-floor'])['id']
    allrows = rows + [json.loads(l) for l in open(os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'search262.jsonl'))]
    r2 = [x for x in allrows if x['id'] == wid][0]
    V2 = G.verts(np.array(r2['p']), r2['s'])
    Vs2 = [V2[0], V2[1], V2[6], V2[7]]
    best2, pose2 = worst_bl_floor(Vs2, r2['s'])
    Q2, _ = checked_free(pose2, Vs2, r2['s'])
    P2 = S.Panel(20, 470, 400, 400, 0, 0, 2.6, 2.6)
    P2.frame()
    for k in (0, 1, 6, 7):
        P2.poly(V2[k], fill=cols[G.NAMES[k]], op=0.55, stroke='#234', sw=0.8)
    P2.poly(Q2, fill='#f90', op=0.45, stroke='#a50', sw=1.0)
    P2.dot((r2['s'] / 2, r2['s'] / 2), 3, '#000')
    notes = ['(a) BL corner of the JAM ring %s (A261 witness installed at s = %.4f): A, A2 floor row (blue), X wall square (pink), C the' % (r['id'][:22], s),
             '    floater (tan; %.3f off the wall, gap to A %.4f).  Dashed blue: T_u = C moved to the wall (the comparison obstacle).' % (hu, gapCA),
             '    Stipple: T_u minus C, the STRIP -- undecided [C]; on 323/323 rings no free square of the BL sectors enters it (cmp264).',
             '    Orange: the free square of the BL-floor sector with the largest (q-O).(-v) - 1/2 = %.4f < 0 (exact centre sets;' % best,
             '    free_margin %.1e).  Its obstacles are A and C only: X and A2 never touch a sector square (sub264, 323 rings).' % mQ,
             '(b) 10x inset on the C-A contact: the sliver of width %.4f that jams C; T_u shares C\'s right flank.' % gapCA,
             '(c) the worst ring of the window (%s, s = %.4f): the NEAR-FLAT LIFTED-END jam -- C %.3f off the wall, A at offset %.3f;' % (
                 wid, r2['s'], r2['facts']['h_u'] if 'facts' in r2 else float(V2[7][:, 0].min()), float(V2[0][:, 0].min())),
             '    worst BL-floor free square (orange) has margin %.4f = the flush value -(4-s)/2 = %.4f: A259\'s PAIR bound is sharp here.' % (
                 best2, -(4 - r2['s']) / 2)]
    return [P.render(), I.render(), S.text_at(700, 60, '(b) 10x inset') if hasattr(S, 'text_at') else '',
            P2.render(), S.note(440, 320, notes[:6], 10), S.note(440, 520, notes[6:], 10)]


def nonadj_gap():
    s, phi, e, a = SHAT, 2.0 * DEG, 1.06, 0.03
    c, g = math.cos(phi), math.sin(phi)
    w = c + g
    b = s - a - 1.0 / c - w - e
    Vs = G3.floor_sq((b, phi, e, phi), s)
    assert Z.poly_gap(Vs[0], Vs[1]) >= -1e-12
    xL = a + w
    Q, mQ = checked_free((xL + 0.5 + 0.005, 0.5 + 0.02, 0.0), Vs, s)
    # strip between L1 (s1's upper-right edge line through (a+w, g), direction (-g, c)) and L_W (W's left flank)
    n = np.array([c, g])
    o1, oW = c * (a + w) + g * g, c * (a + 1 / c + e) + g * c
    assert abs((oW - o1) - e * c) < 1e-12
    L = 3.0
    def line_pts(o):
        p0 = n * o
        d = np.array([-g, c])
        return [p0 - 3 * d, p0 + 3 * d]
    strip = Polygon([tuple(line_pts(o1)[0]), tuple(line_pts(o1)[1]), tuple(line_pts(oW)[1]), tuple(line_pts(oW)[0])])
    strip = strip.intersection(Polygon([(0, 0), (s, 0), (s, s), (0, s)]))
    below = Polygon([(a + w, g), (a + w + 3 * g, g - 3 * c), (a + 1 / c + e + 3 * g, g - 3 * c), (a + 1 / c + e, c)])
    below = below.intersection(Polygon([(0, 0), (s, 0), (s, 2), (0, 2)])).difference(Polygon(Vs[0])).difference(Polygon(Vs[1]))
    drop = Z.sq_verts(xL + 0.5 + 0.005, 0.5, 0.0)
    P = S.Panel(20, 40, 520, 320, 0, 0, s, 2.3)
    P.frame()
    for gg in R.polys_of(strip):
        P.poly(list(gg.exterior.coords)[:-1], fill='#dfd', op=0.8, stroke='none')
    for gg in R.polys_of(below):
        P.poly(list(gg.exterior.coords)[:-1], fill='url(#stip)', op=0.9, stroke='none')
    for V in Vs:
        P.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
    P.poly(drop, fill='none', stroke='#06c', sw=1.0, dash='4,2')
    P.poly(Q, fill='#f90', op=0.5, stroke='#a50', sw=1.0)
    P.line((xL + 1.0, 1.02), (xL + 1.0 + 0.6 * g, 1.02 - 0.6 * c), stroke='#a50', sw=1.5)
    P.dot((s / 2, s / 2), 3, '#000')
    P.text((a + 0.3, 0.5), 's1', 10); P.text((s - b - 0.7, 0.5), 'W', 10); P.text((xL + 0.3, 1.3), 'Q', 10)
    I = S.Panel(560, 40, 200, 200, xL - 0.05, -0.02, xL + 0.15, 0.18, clip_id='ins2')
    for V in Vs:
        I.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
    I.poly(Q, fill='#f90', op=0.5, stroke='#a50', sw=1.0)
    I.poly(drop, fill='none', stroke='#06c', sw=1.0, dash='4,2')
    notes = ['(a) A263\'s non-ADJ floor at common tilt 2 deg, s = %.4f: s1 at a = %.2f, W at shift e = %.2f >= sec 2 deg = %.4f.' % (s, a, e, 1 / c),
             '    Green: the STRIP between s1\'s upper-right edge line and W\'s left flank line (width e cos phi = %.4f >= 1) -- decided [T]:' % (e * c),
             '    a free square inside it slides along the flank direction (arrow) to a floor cell met by itself alone (dashed) unless a chain',
             '    of free squares below-right ends at the next wall\'s START square; here the orange flat Q (exact check, free_margin %.1e)' % mQ,
             '    has a free drop of 0.02: P1 kills it.  Stipple: the region under s1\'s vertex line, the case 1 + w - sec <= e < sec -- undecided [C].',
             '(b) 10x inset at Q\'s floor gap (0.02) and its drop cell.']
    return [P.render(), I.render(), S.note(20, 400, notes, 10)]


def near_flat_cube():
    eps0 = math.pi / 256
    lam = eps0 / 2 + eps0 ** 2 / 2
    a = b = 1 - lam
    al, be = eps0, eps0
    A, B = C4.vertsA(a, al, 1), C4.vertsB(b, be, -1)
    gap = C4.sat_gap(A, B)
    assert gap < 0, gap
    EA, EB = C4.forms(1, -1, a, al, b, be)
    P = S.Panel(20, 40, 360, 360, 0.0, 0.0, 2.2, 2.2)
    P.frame()
    P.poly(A, fill='#9ab', op=0.5, stroke='#234', sw=0.8)
    P.poly(B, fill='#c9a', op=0.5, stroke='#234', sw=0.8)
    ov = Polygon(A).intersection(Polygon(B))
    for gg in R.polys_of(ov):
        P.poly(list(gg.exterior.coords)[:-1], fill='#e00', op=0.9, stroke='#900', sw=0.8)
    P.text((0.3, 1.6), 'A (+), a = 1 - lam', 10); P.text((1.2, 0.4), 'B (-), b = 1 - lam', 10)
    I = S.Panel(400, 40, 240, 240, 0.95, 0.95, 1.05, 1.05, clip_id='ins3')
    I.poly(A, fill='#9ab', op=0.5, stroke='#234', sw=0.8)
    I.poly(B, fill='#c9a', op=0.5, stroke='#234', sw=0.8)
    for gg in R.polys_of(ov):
        I.poly(list(gg.exterior.coords)[:-1], fill='#e00', op=0.9, stroke='#900', sw=0.8)
    # (c) the (eps0, s) map: the cube [0, eps0]^4 is excluded for s < 4 - lam - nu
    D = S.Panel(20, 470, 620, 220, 0.0, 3.8, 1.5, 4.0)
    D.frame()
    mu = eps0 ** 2 / 2 + math.tan(eps0) * (1 + math.sin(eps0))
    thr = 4 - lam - (eps0 ** 2 / 2 + (0.8771 + mu + 0.011) * math.tan(eps0))
    D.poly([(0, 3.8), (0.703, 3.8), (0.703, thr), (0, thr)], fill='#dfd', op=1.0, stroke='none')
    D.poly([(0, thr), (0.703, thr), (0.703, 4.0), (0, 4.0)], fill='url(#stip)', op=0.9, stroke='none')
    D.poly([(0.703, 3.8), (1.5, 3.8), (1.5, 4.0), (0.703, 4.0)], fill='#dfd', op=0.6, stroke='none')
    D.line((0, SHAT), (1.5, SHAT), stroke='#000', dash='4,2')
    D.text((0.75, 3.885), 's-hat = 3.8771', 9); D.text((0.02, thr + 0.008), 'cube excluded below s = %.4f [T]' % thr, 9)
    D.text((0.8, 3.95), 'tilts >= 0.703 deg: A261 / A263 certificates', 9)
    notes = ['(a) the mixed corner (+,-) at tilts eps0 = 0.703 deg with BOTH offsets at 1 - lam = %.5f: the squares OVERLAP (red, SAT gap' % a,
             '    %.2e; E_A = %.2e, E_B = %.2e < 0).  Lemma MC(+,-): interior-disjoint with a, b < 1 forces a, b > 1 - lam.' % (gap, EA, EB),
             '(b) 10x inset on the overlap: A\'s lowest vertex (cos eps0, a) against B\'s top edge.',
             '(c) (largest tilt in degrees, s): the all-near-flat cube of every mixed pattern is excluded for s < %.4f by the chain of' % thr,
             '    three_lemmas.md s.3.3 (green, [T]); above it (stipple) nothing is claimed; right of 0.703 deg the A261 / A263 certificates.']
    return [P.render(), I.render(), S.note(20, 720, notes, 10)]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    S.page(os.path.join(OUT, 'near_flat_cube.svg'), 900, 840,
           'A264 Lemma 3: the near-flat MIXED corner forces both offsets to 1 - O(eps0); the cube is excluded [T]', near_flat_cube())
    S.page(os.path.join(OUT, 'nonadj_gap_strip.svg'), 900, 520,
           'A264 Lemma 2: the STRIP of a wide non-ADJ gap -- every free square in it slides to the floor or is chained to S\'', nonadj_gap())
    S.page(os.path.join(OUT, 'jammed_sector.svg'), 900, 900,
           'A264 Lemma 1: the BL sectors of a JAM ring see A and C only; C is dominated by its wall drop T_u (pair3 + STRIP)', jammed_sector())
    print('pages written to', OUT)
