"""A261 pages (geometry-checked; a note per panel saying what it IS; slivers with a 10x inset; undecided = grey
stipple, never green).   python pages261.py  ->  docs/residue_map/campaigns/A261-box-meeters/
  floating_meeter.svg   (a) LIFT: a floating box meeter with BOTH drop cells blocked, and the any-pose cell that lands
                        it;  (b) JAM: the jammed floater -- no wall cell receives it (the freest one drawn, 10x inset)
  same_wall.svg         (a) two touchers of one wall cannot both meet the box (PUSH ii): NOT a packing, overlap red;
                        (b) the corpus same-wall pair (toucher + second-layer floater, rand_0_0441) and its free drop
  exclusion_map.svg     the four COMPLETE two-flat-wall certificates F02_* as leaf maps over (tilt 1, tilt 3)
Every packing panel asserts containment and pairwise SAT gaps >= -1e-9 before it is drawn.
"""
import html
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import local261 as L                                                   # noqa: E402
G8 = L.G8
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A261-box-meeters')
from svg261 import BLUE, GREEN, GREY, ORANGE, RED, Panel, clip       # noqa: E402
STIP = ('<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" '
        'r="0.9" fill="#a0aec0"/></pattern></defs>')


def checked(P, tol=-1e-9):
    assert min(float(p.min()) for p in P) >= tol, 'containment'
    assert min(G8.sat_gap(P[i], P[j]) for i in range(len(P)) for j in range(i)) >= tol, 'overlap'


def land_cell(C, th):
    """C slid along -(cos, sin) of its own tilt until it touches x = 0."""
    d = float(C[:, 0].min()) / math.cos(th)
    return C - d * np.array([math.cos(th), math.sin(th)])


def page_floating():
    lift = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'local261_seeded.jsonl'))][-1]
    jam = json.load(open(os.path.join(ATT, 'results', 'jam261_polished.json')))
    chk = json.load(open(os.path.join(ATT, 'results', 'checkjam261.json')))
    out = [STIP]
    # (a) LIFT
    P = {k: L.verts(*v) for k, v in lift['poses'].items()}
    checked(list(P.values()))
    C = P['C']
    Tu, Tv = C - [C[:, 0].min(), 0], C - [0, C[:, 1].min()]
    Tl = land_cell(C, lift['poses']['C'][2])
    free = min(G8.sat_gap(Tl, P['A']), G8.sat_gap(Tl, P['X']))
    assert G8.depth(P['X'], Tu) > 0 and G8.depth(P['A'], Tv) > 0 and free >= -1e-9 and abs(Tl[:, 0].min()) < 1e-12
    a = Panel(30, 40, 3.3, 100, '(a) LIFT [M, exact check]: floating meeter C, both straight DROPS blocked -- and the cell that lands it')
    a.walls()
    for k in ('A', 'X'):
        a.sq(P[k], BLUE, k)
    a.sq(C, ORANGE, 'C')
    for T, B in ((Tu, P['X']), (Tv, P['A'])):
        a.sq(T, RED, dash='4,3')
        a.poly(clip(T, B), fill=RED, fill_opacity='0.55', stroke='none')
    a.sq(Tl, GREEN, dash='6,2')
    a.note(['IS: three unit squares in the corner frame (pairwise gaps >= %.3f): A touches the floor, X the wall,' % lift['check']['pair_gap'],
            'C floats %.3f off the wall and %.3f off the floor; C and A meet the box (yellow).' % tuple(lift['check']['touch']['C']),
            'Red dashed: C dropped straight onto each wall -- BLOCKED (overlap red: X by %.3f, A by %.3f).' % (
                G8.depth(P['X'], Tu), G8.depth(P['A'], Tv)),
            'Green dashed: C slid along its own edge direction to the wall: met by C only (gap to A, X >= %.4f),' % free,
            'so (E2) lands C and Phi1 rises.  A straight drop is the WRONG test; any-pose P1 is the right one.'])
    out += a.o
    # (b) JAM
    P = {k: L.verts(*v) for k, v in jam['poses'].items()}
    checked(list(P.values()))
    import jam261 as J
    j = np.minimum(np.minimum(J.gaps(P['A']), J.gaps(P['X'])), -J.gaps(P['C']))
    i = int(np.argmax(j))
    T = J.CELLS[i]
    assert chk['ok'] and chk['J_receiving_cell'] < 0 and j[i] < 0
    b = Panel(760, 40, 3.3, 100, '(b) JAM [M, exact check]: the JAMMED floater -- NO wall cell receives C (freest cell drawn)')
    b.walls()
    for k in ('A', 'X'):
        b.sq(P[k], BLUE, k)
    b.sq(P['C'], ORANGE, 'C')
    b.sq(T, RED, dash='4,3')
    blk = 'A' if G8.sat_gap(T, P['A']) < G8.sat_gap(T, P['X']) else 'X'
    ov = clip(T, P[blk])
    b.poly(ov, fill=RED, fill_opacity='0.7', stroke='none')
    if ov:
        c = np.mean(ov, 0)
        ins = Panel(1120, 48, 0.12, 1000, '', origin=(c[0] - 0.06, c[1] - 0.06))
        ins.o = ['<rect x="%.1f" y="%.1f" width="120" height="120" fill="white" stroke="#1a202c"/>' % (1120, 48),
                 '<clipPath id="ci"><rect x="1120" y="48" width="120" height="120"/></clipPath><g clip-path="url(#ci)">']
        for k, col in (('A', BLUE), ('X', BLUE), ('C', ORANGE)):
            ins.sq(P[k], col)
        ins.sq(T, RED, dash='4,3')
        ins.poly(ov, fill=RED, fill_opacity='0.7', stroke='none')
        ins.o.append('</g><text x="1122" y="182" font-size="9.5">10x inset at the overlap</text>')
        b.o += ins.o
    td = chk['tilts_deg']
    b.note(['IS: A (floor, %.2f deg) and C (floats %.3f off the wall, %.2f deg) meet the box; X (wall, %.2f deg) does not.' % (
                td['A'], chk['float_C'][0], td['C'], td['X']),
            'Pairwise gaps >= %.4f, box depths C %.4f, A %.4f.  Every wall-touching unit cell (any tilt, either wall)' % (
                min(chk['gaps'].values()), chk['meet']['C'], chk['meet']['A']),
            'that meets C overlaps A or X by >= %.4f (inner sup, fine grid + Nelder-Mead [M]); no EMPTY wall cell' % -chk['J_receiving_cell'],
            'either (%.3f).  Red dashed: the freest receiving cell, overlapping %s (sliver, inset).  The wedge between' % (chk['E_empty_cell'], blk),
            "X's edge (steep) and A's edge (shallow) closes TOWARDS the wall: C fits where no wall toucher does.",
            'A LOCAL counterexample to TOUCH-NORMAL-from-P1; whether a ring closes round it on the window is open.'])
    out += b.o
    return 1500, 480, out


def page_same_wall():
    out = [STIP]
    A1, A2 = L.verts(0.5 * L.w(0.35) + 0.30, 0.5 * L.w(0.35), 0.35), L.verts(0.5 * L.w(1.1) + 0.72, 0.5 * L.w(1.1), 1.1)
    gap = G8.sat_gap(A1, A2)
    assert gap < 0 and G8.depth(A1, L.BOX) > 0 and G8.depth(A2, L.BOX) > 0
    a = Panel(30, 40, 2.6, 120, '(a) NOT a packing [T: PUSH (ii)]: two FLOOR touchers both meeting the box overlap (depth %.3f)' % -gap)
    a.walls()
    a.sq(A1, BLUE, 'A1')
    a.sq(A2, BLUE, 'A2')
    a.poly(clip(A1, A2), fill=RED, fill_opacity='0.6', stroke='none')
    a.note(['IS: an ILLUSTRATION of the lemma, not a witness: any two unit squares touching the same wall of the',
            'corner and both meeting the open box (yellow) overlap.  Proof: a separating line would have a normal n',
            '(from A1 to A2) with n_u > 0 because A2 touches the floor, and -n_u > 0 because A1 does (Lemma PUSH (ii)).',
            'With WEDGED-SEAL: a doubly-met box has AT MOST one toucher per wall; every further meeter FLOATS.'])
    out += a.o
    # (b) the corpus same-wall pair
    rec = None
    for ln in open(os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'results', 'witnesses217.jsonl')):
        r = json.loads(ln)
        if (r.get('rid') or r.get('wid')) == 'rand_0_0441|free':
            rec = r
            break
    z, s = rec['z'], float(rec['z'][-1])
    P = [L.verts(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range((len(z) - 1) // 3)]
    assert min(float(p.min()) for p in P) >= -1e-7 and max(float(p.max()) for p in P) <= s + 1e-7
    pg = min(G8.sat_gap(P[i], P[j]) for i in range(len(P)) for j in range(i))
    assert pg >= -1e-7
    b = Panel(760, 40, s, 78, '(b) corpus [M]: rand_0_0441, s = %.4f (k1, not family-stuck): TR box met by toucher 8 + FLOATER 1' % s)
    b.poly([(0, 0), (s, 0), (s, s), (0, s)], fill='none', stroke='#1a202c', stroke_width='2.2')
    b.poly([(s - 1, s - 1), (s, s - 1), (s, s), (s - 1, s)], fill='#faf089', fill_opacity='0.35', stroke='#b7791f',
           stroke_width='0.8', stroke_dasharray='4,3')
    for i, Q in enumerate(P):
        b.sq(Q, ORANGE if i == 1 else BLUE if i == 8 else GREY, str(i), op='0.25' if i in (1, 8) else '0.10')
    T = P[1] + [0, s - P[1][:, 1].max()]
    blockers = [i for i in range(len(P)) if i != 1 and G8.depth(P[i], T) > 1e-9]
    b.sq(T, GREEN, dash='6,2')
    b.note(['IS: a corpus packing of 11 (least pair gap %.1e).  The only SAME-WALL pattern below side 4: a wall' % pg,
            'toucher (8) and a second-layer floater (1) %.1e under the ceiling.  Its straight drop onto the ceiling' % (s - P[1][:, 1].max()),
            '(green dashed) is met by %s: FREE, so (E2) lands it -- it is a rattler, not a structure.' % (blockers or 'no other square'),
            'Corpus below 4: 29 PAIR corners, 2 FLOAT1, 1 FLOAT2 -- every floater has a free straight drop (census261).'])
    out += b.o
    return 1500, 440, out


def page_map():
    sys.path.insert(0, HERE)
    import verify261 as V
    out = [STIP]
    rows = {}
    p = os.path.join(ATT, 'results', 'cert261.jsonl')
    if os.path.exists(p):
        rows = {json.loads(l)['job']: json.loads(l) for l in open(p)}
    for n, name in enumerate(('F02_pp', 'F02_pm', 'F02_mp', 'F02_mm')):
        base = os.path.join(ATT, 'certs', name)
        x0, y0, sc = 40 + 200 * n, 50, 170.0
        ok = name in rows and rows[name].get('verified')
        out.append('<text x="%d" y="%d" font-size="11.5" font-weight="bold">%s  %s</text>' % (
            x0, y0 - 10, name, 'verifier PASS' if ok else 'NOT VERIFIED'))
        out.append('<rect x="%d" y="%d" width="%.0f" height="%.0f" fill="url(#stip)" stroke="#1a202c"/>' % (x0, y0, sc, sc))
        if not os.path.exists(base + '.tree'):
            continue
        job = json.load(open(base + '.json'))
        stack = [tuple((float(a), float(b)) for a, b in job['tdomain'])]
        with open(base + '.leaves', 'rb') as fh:
            it = V.read_leaves(fh)
            for tok in open(base + '.tree', 'rb').read():
                box = stack.pop()
                if tok < 4:
                    lo, hi = box[tok]
                    mid = 0.5 * (lo + hi)
                    stack.append(box[:tok] + ((mid, hi),) + box[tok + 1:])
                    stack.append(box[:tok] + ((lo, mid),) + box[tok + 1:])
                else:
                    pats, ys = next(it)
                    Lb = V.lower_bound(job, box, pats, ys).min() if len(ys) else -1
                    (a, b), (c, d) = box[1], box[3]
                    col = GREEN if (ok and Lb > 0) else 'url(#stip)'
                    out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" fill-opacity="%.2f" stroke="#22543d" '
                               'stroke-width="0.3"/>' % (x0 + a * sc, y0 + (1 - d) * sc, (b - a) * sc, (d - c) * sc, col,
                                                         0.25 + 0.5 * min(1.0, max(0.0, (math.log10(max(Lb, 1e-7)) + 7) / 6))))
        out.append('<text x="%d" y="%.0f" font-size="10">tilt of wall 1 (0.7 .. 45 deg) -&gt;;  up: tilt of wall 3</text>' % (x0, y0 + sc + 14))
    notes = ['IS: the four COMPLETE box-valid certificates "no pinwheel of rows of two with walls 0 and 2 exactly FLAT at side <= 3.8771"',
             '(senses of walls 1, 3 = the two letters).  Each green rectangle is a LEAF tilt box carrying LP dual multipliers whose',
             'outward-rounded mean-value bound is > 0 for every admissible choice of separating edge normals (verify261.py); darker =',
             'larger bound.  Grey stipple = NOT covered: the slab "some tilt < 0.703 deg" (no closed-LP certificate exists at flat,',
             'box_meeters.md s.3.2) and any job the verifier has not passed.  Status of all jobs at draw time:',
             '  ' + ', '.join('%s:%s' % (k, 'PASS' if v.get('verified') else 'running/partial') for k, v in sorted(rows.items())) or '  (none)']
    for i, s in enumerate(notes):
        out.append('<text x="40" y="%d" font-size="10.5" fill="#2d3748">%s</text>' % (265 + 13 * i, html.escape(s[:230])))
    return 860, 360, out


def main():
    os.makedirs(PAGES, exist_ok=True)
    for name, fn in (('floating_meeter', page_floating), ('same_wall', page_same_wall), ('exclusion_map', page_map)):
        W, H, body = fn()
        with open(os.path.join(PAGES, name + '.svg'), 'w', encoding='utf-8') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">'
                    '<rect width="100%%" height="100%%" fill="white"/>%s</svg>' % (W, H, '\n'.join(body)))
        print('wrote', name)


if __name__ == '__main__':
    main()
