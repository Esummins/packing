"""A260 pages 1-2 (geometry-checked; a note per panel says what it IS; slivers get a 10x inset):
  unlock.svg      a corpus locked wall BEFORE / AFTER the two-cell exchange W -> T, F -> Q (Lemma UNLOCK + LIFT)
  open_notch.svg  the open notch: exact least-depth locus of the lowest vertex (shift e vs the closed tooth), two locks,
                  and a hybrid ring (adversary's worst) with the boxes R_cos, R^h, the centre O and the worst free square
Every drawn free square passes the exact SAT + hard containment check before it is drawn (assert)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
import svg260 as S                                                    # noqa: E402
import tooth260 as TT                                                 # noqa: E402
from shapely.geometry import box as sbox                              # noqa: E402
Z = H.Z
OUT = os.path.join(H.ROOT, 'docs', 'residue_map', 'campaigns', 'A260-locked-wall')
RES = os.path.join(HERE, '..', 'results')


def draw_cfg(P, s, ring, hi=None, T=None, F=None, Fcol='#f90'):
    P.frame()
    for j, V in enumerate(ring):
        P.poly(V, fill='#9ab' if j != hi else '#47c', op=0.55, stroke='#234', sw=0.8)
    if T is not None:
        P.poly(T, stroke='#c00', sw=1.2, dash='4,3')
    if F is not None:
        P.poly(F, fill=Fcol, op=0.55, stroke='#a50', sw=1.0)
    P.dot((s / 2, s / 2), 3, '#000')


def unlock():
    rows, N = H.corpus()
    name = 'A253 tau=14.545 s=3.877084'
    _, s, sq = [r for r in rows if r[0] == name][0]
    rec = [json.loads(l) for l in open(os.path.join(RES, 'corpus260.jsonl')) if json.loads(l)['name'] == name][0]
    ring, F = [np.array(V, float) for V in sq[:8]], np.array(sq[8], float)
    lk = rec['lock'][0]
    w = lk['wall']
    i1, iW = N.wall_pair(ring, s, w)
    T = ring[i1] + (1.0 / math.cos(lk['phi_deg'] * Z.DEG)) * np.array(N.EW[w], float)
    Q = Z.sq_verts(*rec['lift']['pose'])
    ring2 = [V for j, V in enumerate(ring) if j != iW] + [T]
    before = min([Z.contain_margin(V, s) for V in ring + [F]] +
                 [Z.poly_gap(A, B) for k, A in enumerate(ring + [F]) for B in (ring + [F])[:k]])
    after = min([Z.contain_margin(V, s) for V in ring2 + [Q]] +
                [Z.poly_gap(A, B) for k, A in enumerate(ring2 + [Q]) for B in (ring2 + [Q])[:k]])
    dip = -Z.poly_gap(F, T)
    assert before >= -1e-7 and after >= -1e-7 and dip > 0, (before, after, dip)
    vin = min(F, key=lambda p: np.linalg.norm(p - T.mean(0)))          # F's vertex nearest T: the dipping one
    parts = []
    for col, (rg, hi, Fq, lab) in enumerate(((ring, iW, F, 'BEFORE'), (ring2, 7, Q, 'AFTER'))):
        P = S.Panel(20 + col * 600, 40, 380, 380, 0, 0, s, s)
        draw_cfg(P, s, rg, hi, T if col == 0 else None, Fq)
        I = S.Panel(420 + col * 600, 40, 170, 170, vin[0] - 0.085, vin[1] - 0.085, vin[0] + 0.085, vin[1] + 0.085,
                    clip_id='c%d' % col)
        draw_cfg(I, s, rg, hi, T if col == 0 else None, Fq)
        P.poly([(vin[0] - 0.085, vin[1] - 0.085), (vin[0] + 0.085, vin[1] - 0.085), (vin[0] + 0.085, vin[1] + 0.085),
                (vin[0] - 0.085, vin[1] + 0.085)], stroke='#b00', sw=1)
        parts += [P.render(), I.render(), S.note(420 + col * 600, 225, ['10x inset at the notch'])]
    parts.append(S.note(20, 440, [
        '(a) BEFORE.  IS: corpus row "%s" (A253), ring of eight + the poker F (orange), exact coordinates; wall %d is an OPEN PAIR:' % (name, w),
        'its END toucher W (blue) stands e = %.4f past the normal cell T = s1 + sec(phi) e (red dashes); M(T) = {W, F}: the wall is LOCKED.' % lk['e'],
        'Checked: nine squares a packing (least gap / containment %+.1e); F dips %.5f into T (= the sliver in the inset; e sin(phi) = %.5f).' % (before, dip, lk['e'] * math.sin(lk['phi_deg'] * Z.DEG)),
        '(b) AFTER the two-cell exchange of Lemma UNLOCK: W -> T (the wall is a ROW OF TWO), F -> Q = F lifted %.5f along s1\'s edge direction.' % rec['lift']['dist'],
        'Checked: nine squares a packing (least gap / containment %+.1e); Q contains the centre O (margin %+.4f).  IS NOT a proof that a' % (after, rec['lift']['has_O']),
        'lock always lifts: with G, H present the lift may be HELD (P1 saturated) -- then the hybrid PAIR certificate (open_notch.svg) is what excludes it.']))
    S.page(os.path.join(OUT, 'unlock.svg'), 1220, 540, 'A260 -- a locked wall before / after the two-cell exchange (Lemma UNLOCK)', parts)


def exact_P(phi, e, psi, a=3.0, s=9.0):
    Vs = [H.toucher(a, phi, s, 0), H.toucher(a + 1 / math.cos(phi) + e, phi, s, 0)]
    C = R.centre_set(Vs, s, psi)
    cp, sp = math.cos(psi), math.sin(psi)
    x0, x1 = a + math.cos(phi), a + 1 / math.cos(phi) + e + math.cos(phi)
    best = None
    for Pg in R.polys_of(C.intersection(sbox(x0 + (cp - sp) / 2, -1, x1 + (cp - sp) / 2, s + 1))):
        X = np.array(Pg.exterior.coords)
        i = int(X[:, 1].argmin())
        if best is None or X[i, 1] < best[1]:
            best = (X[i, 0], X[i, 1])
    return (best[0] - (cp - sp) / 2, best[1] - (cp + sp) / 2), Vs


def open_notch():
    phi, e, a, s = 14.545 * Z.DEG, 0.13, 3.0, 9.0
    parts = []
    A = (a + 1 / math.cos(phi), math.cos(phi))
    P = S.Panel(20, 40, 400, 460, A[0] - 0.75, 0.0, A[0] + 1.25, 2.3, clip_id='n0')
    I = S.Panel(450, 40, 300, 300, A[0] - 0.05, A[1] - 0.12, A[0] + 0.25, A[1] + 0.18, clip_id='n1')
    locus, locus0 = [], []
    for pd in np.arange(0.0, 60.1, 1.0):
        locus.append(exact_P(phi, e, pd * Z.DEG)[0])
        locus0.append(exact_P(phi, 0.0, pd * Z.DEG)[0])
    (_, Vs) = exact_P(phi, e, phi)
    Tc = H.toucher(a + 1 / math.cos(phi), phi, s, 0)
    locks = []
    for pd in (14.545, 24.0):
        p, _ = exact_P(phi, e, pd * Z.DEG)
        psi = pd * Z.DEG
        q = (p[0] + (math.cos(psi) - math.sin(psi)) / 2 + 0.0, p[1] + (math.cos(psi) + math.sin(psi)) / 2 + 1e-9)
        V = Z.sq_verts(q[0], q[1], psi)
        assert min(Z.poly_gap(V, W) for W in Vs) >= -1e-8
        locks.append((pd, p, V))
    for Pn in (P, I):
        for V in Vs:
            Pn.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
        Pn.poly(Tc, stroke='#c00', sw=1.0, dash='4,3')
        for (pd, p, V), colr in zip(locks, ('#f90', '#3a3')):
            Pn.poly(V, fill=colr, op=0.30, stroke=colr, sw=1.0)
        Pn.path(locus0, '#06c', 1.4)
        Pn.path(locus, '#c00', 1.6)
        Pn.line((A[0] - 0.75, 0), (A[0] + 1.25, 0), '#000', 1.5)
    P.poly([(A[0] - 0.05, A[1] - 0.12), (A[0] + 0.25, A[1] - 0.12), (A[0] + 0.25, A[1] + 0.18), (A[0] - 0.05, A[1] + 0.18)],
           stroke='#b00', sw=1)
    dmin = min(p[1] for p in locus)
    parts += [P.render(), I.render(), S.note(450, 355, ['10x inset: the SLOT (width e cos(phi) = %.4f)' % (e * math.cos(phi)),
              'red: exact locus of the lowest vertex, shift e = %.2f' % e, 'blue: the closed tooth (e = 0), apex depth cos(phi)'])]
    parts.append(S.note(20, 520, [
        '(a) IS: an open pair of common tilt 14.545 deg, shift e = 0.13 (s1 left, W right, T = the normal cell in red dashes), with the EXACT locus of the lowest',
        'vertex of a free unit square at its least depth, tilt psi = 0 .. 60 deg (red), against the closed tooth e = 0 (blue); centre sets of room259.',
        'Two free squares drawn (exact SAT vs s1, W >= 0): psi = phi (orange) seated at the virtual apex, depth cos(phi)(1 - e sin(phi)) = %.4f;' % (math.cos(phi) * (1 - e * math.sin(phi))),
        'psi = 24 deg (green) with its vertex IN the slot.  Least depth over all tilts %.4f >= cos(phi) - e/2 = %.4f (POKE form); closed tooth: %.4f.' % (dmin, math.cos(phi) - e / 2, math.cos(phi)),
        'IS NOT the room bound: the box R^h built from these depths breaks HOLE-ONE beyond ~17 deg; the hybrid PAIR certificate (cert260) is the bound.']))
    # panel (b): the adversary's worst hybrid ring
    rows = [json.loads(l) for l in open(os.path.join(RES, 'adv260.jsonl'))]
    rows = [r for r in rows if abs(r['s'] - H.SHAT) < 1e-9 and r['adj'] == 1]
    r = max(rows, key=lambda t: t['pierceO'])
    s2, x = r['s'], np.array(r['x'])
    Vr = H.hyb_verts(x, s2)
    pose = r['pose']
    fm, hasO = R.free_margin(pose, Vr, s2), R.contains_O(pose, s2)
    assert fm >= -1e-9 and H.hyb_margin(x, s2, True) >= 0
    B = S.Panel(800, 40, 390, 390, 0, 0, s2, s2)
    draw_cfg(B, s2, Vr, None, None, Z.sq_verts(*pose), '#f90')
    cs = [math.cos(x[4 * k + 3]) for k in range(4)]
    dh = [cs[k] - max(0.0, r['shift'][k]) / 2 for k in range(4)]
    B.poly([(cs[3], cs[0]), (s2 - cs[1], cs[0]), (s2 - cs[1], s2 - cs[2]), (cs[3], s2 - cs[2])], stroke='#06c', sw=1.0, dash='5,3')
    B.poly([(dh[3], dh[0]), (s2 - dh[1], dh[0]), (s2 - dh[1], s2 - dh[2]), (dh[3], s2 - dh[2])], stroke='#c00', sw=1.0, dash='2,2')
    parts.append(B.render())
    parts.append(S.note(800, 450, [
        '(b) IS: the adversary\'s worst all-ADJ HYBRID ring at s-hat (adv260, hard feasibility; shifts %s),' % [round(v, 3) for v in r['shift']],
        'the box R_cos (blue dashes, sides %.3f x %.3f) and the enlarged R^h (red dots), the centre O, and the free square that comes' % (s2 - cs[1] - cs[3], s2 - cs[0] - cs[2]),
        'closest to missing O: margin %+.4f < -(4-s)/2 = %+.4f; exact free margin %+.1e, contains O by %+.4f.' % (r['pierceO'], -(4 - s2) / 2, fm, hasO),
        'IS NOT a certificate: [M].  The certificate is cert260 (hybA / hybB / hybAB), common tilt per wall.']))
    S.page(os.path.join(OUT, 'open_notch.svg'), 1500, 610, 'A260 -- the open notch (OPEN-TOOTH) and the hybrid pocket', parts)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    unlock()
    open_notch()
    print('pages written to', OUT)
