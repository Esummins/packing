"""A260 page 3: corner_notch.svg -- the CORNER-NOTCH layer and Lemma PLUG, + the certificate status grids.
 (a) corner BR at b = a' = 0.99: the END square W, the START square S', the plug [0, 1/4]^2, the open box
     (0.604, 1)^2 that every unit square reaching the plug must contain, S''s lowest vertex V' inside it, and the
     unit square of the quadrant that comes closest to fitting (it swallows V': NOT free; drawn in red outline);
     10x inset at V'.  Checked: V' in the box; V' strictly inside the drawn square (exact SAT gap < 0).
 (b) status grids over the 9 x 9 tilt cells (phi, phi'): A259's tree, layer260, hybA, hybB, hybAB.  GREEN only for a
     cell whose index row says ok (all leaves CERT / PRUNE, 0 OPEN); not yet run = grey stipple; a cell with OPEN
     leaves = red.  Read from the certs' index files at draw time."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import pairh260 as PH                                                 # noqa: E402
import svg260 as S                                                    # noqa: E402
Z = H.Z
OUT = os.path.join(H.ROOT, 'docs', 'residue_map', 'campaigns', 'A260-locked-wall')


def index(path):
    if not os.path.exists(path):
        return {}
    return {json.loads(l)['cell']: json.loads(l) for l in open(path) if l.strip()}


def grid(x0, y0, title, idx, cellpx=16):
    out = ['<text x="%d" y="%d" font-size="11">%s</text>' % (x0, y0 - 6, title)]
    n_ok = 0
    for i in range(9):
        for j in range(9):
            r = idx.get('%d,%d' % (i, j))
            if r is None:
                fill = 'url(#stip)'
            elif r['ok'] and r['stats'].get('OPEN', 0) == 0 and r['stats'].get('LAYER', 0) >= 0:
                fill, n_ok = '#5b5', n_ok + 1
            else:
                fill = '#d33'
            out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#666" stroke-width="0.5"/>'
                       % (x0 + i * cellpx, y0 + (8 - j) * cellpx, cellpx, cellpx, fill))
    out.append('<text x="%d" y="%d" font-size="10">%d / 81 cells ok</text>' % (x0, y0 + 9 * cellpx + 12, n_ok))
    return '\n'.join(out), n_ok


def main():
    s = 3.8771
    b, f, a1, f1 = 0.99, 12.5 * Z.DEG, 0.99, 17.5 * Z.DEG
    Vs = PH.pairh_verts((b, f, a1, f1, 0.0, 0.0), s)
    W, S1 = Vs[1], Vs[2]
    Vp = np.array([s - math.cos(f1), a1])                             # S''s lowest vertex V' = (cos phi', a') in corner coords
    assert min(np.linalg.norm(S1 - Vp, axis=1)) < 1e-12
    lo = 0.354 + PH.RHO
    assert lo < math.cos(f1) < 1 and lo < a1 < 1
    rogue = np.array([(s - 1, 0.0), (s, 0.0), (s, 1.0), (s - 1, 1.0)])
    gapV = Z.poly_gap(rogue, S1)
    assert gapV < 0                                                   # the corner square is NOT free: it overlaps S'
    parts = []
    P = S.Panel(20, 40, 430, 430, s - 2.3, 0.0, s, 2.3)
    I = S.Panel(470, 40, 250, 250, Vp[0] - 0.04, Vp[1] - 0.04, Vp[0] + 0.04, Vp[1] + 0.04, clip_id='k1')
    for Pn in (P, I):
        Pn.frame()
        for V in (W, S1):
            Pn.poly(V, fill='#9ab', op=0.55, stroke='#234', sw=0.8)
        Pn.poly(PH.plug(s), fill='#a6d', op=0.45, stroke='#639', sw=1.0)
        Pn.poly([(s - 1, lo), (s - lo, lo), (s - lo, 1.0), (s - 1, 1.0)], fill='#fd6', op=0.30, stroke='#a80', sw=1.0, dash='3,2')
        Pn.poly(rogue, stroke='#c00', sw=1.4)
        Pn.dot(Vp, 3, '#c00')
    P.poly([(Vp[0] - 0.04, Vp[1] - 0.04), (Vp[0] + 0.04, Vp[1] - 0.04), (Vp[0] + 0.04, Vp[1] + 0.04), (Vp[0] - 0.04, Vp[1] + 0.04)],
           stroke='#b00', sw=1)
    parts += [P.render(), I.render(), S.note(470, 305, ['10x inset at V\' = (cos phi\', a\'): it lies 1 - a\' = %.3f' % (1 - a1),
              'inside the unit corner square (red outline)'])]
    parts.append(S.note(20, 490, [
        '(a) IS: corner BR at b = a\' = 0.99 (tilts 12.5 / 17.5 deg), in the CORNER-NOTCH layer {b, a\' > 63/64} that A259\'s tree could not certify.',
        'Violet: the PLUG [0, 1/4]^2.  Yellow: the open box (0.604, 1)^2 -- Lemma PLUG [T]: EVERY unit square of the quadrant that meets the plug',
        'contains it (kernel of half-side 1/(2w) about a centre within 1/4 of (w/2, w/2)).  Red dot: S\'s lowest vertex V\', inside the box because',
        'a\' < 1 and cos(phi\') < 1 (D2 / D1 strict).  Red outline: the unit corner square -- NOT free (exact SAT gap to S\' = %+.4f < 0); it becomes' % gapV,
        'free only at a\' = 1, outside D\'.  So no free square meets the plug, and with the plug as an obstacle the layer certifies (grid "layer260").']))
    A9 = os.path.join(H.ROOT, 'attempts', 'A259-normal-room', 'certs', 'pair259_index.jsonl')
    C = os.path.join(HERE, '..', 'certs')
    x, tallies = 780, []
    for title, path in (('A259 tree (D\' minus layer)', A9), ('layer260 (PLUG)', os.path.join(C, 'layer260_index.jsonl')),
                        ('hybA260', os.path.join(C, 'hybA260_index.jsonl')), ('hybB260', os.path.join(C, 'hybB260_index.jsonl')),
                        ('hybAB260', os.path.join(C, 'hybAB260_index.jsonl'))):
        g, n = grid(x, 70, title, index(path))
        parts.append(g)
        tallies.append((title, n))
        x += 165
    parts.append(S.note(780, 260, [
        '(b) IS: certificate status per 5 x 5 degree tilt cell (phi across, phi\' up), read from the index files when this page was drawn.',
        'GREEN = the cell\'s tree finished with every leaf CERT or PRUNE and 0 OPEN;  grey stipple = not run yet (UNDECIDED, never green);',
        'red = a cell with OPEN leaves.  A259\'s tree and hybA / hybB / hybAB are detached runs: redraw (python pages260b.py) to refresh.',
        'layer260 is complete and verified (verify260: 93 leaves re-derived with independent tilt bins, exact tiling, 0 bad).',
        'Tallies at draw time: ' + ';  '.join('%s %d/81' % t for t in tallies)]))
    S.page(os.path.join(OUT, 'corner_notch.svg'), 1620, 580, 'A260 -- CORNER-NOTCH: Lemma PLUG and the certificate status', parts)
    print(tallies)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    main()
