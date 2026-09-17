"""A246 pages (docs/residue_map/campaigns/A246-construct-towards/):
  corner_propagation.svg  (A) a type-F corner: own incidences 4 of 6, the two forced outside suppliers;
                          (B) NOT-SELF-SUFFICIENT: the descending separating line and its triangle;
                          (B') the sharp example (two squares share c00 and c10, one misses c01);
                          (C) the mutual-ADJ wall at s-hat: a packing below 4 -- and the side wall it breaks.
  tight_case.svg          (D) the certified 12-stuck at 4.000022 with its supply letters;
                          (E) the fresh attempt at s-hat with its self-sufficient corners;
                          (F) SLOT-MET's cap reduction and the B&B verdict.
Every configuration panel is geometry-checked as drawn; the check is printed in the panel's note.
    python pages246.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
import geom246 as G                      # noqa: E402
import interval246 as IV                 # noqa: E402
import cells244 as C                     # noqa: E402
from draw244 import Page                 # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A246-construct-towards')
BLUE, RED, GREEN, GREY, ORANGE = '#3b6fd6', '#d63b3b', '#3a9d5d', '#999', '#e08a1e'
SHAT = G.SHAT


def from_vertex(V, th):
    """pose of the square whose LOWEST vertex is V and whose right-going edge has angle th."""
    c, s = math.cos(th), math.sin(th)
    return (V[0] + (c - s) / 2, V[1] + (s + c) / 2, th)


def fg(g):
    return '0 (contact)' if abs(g) < 1e-9 else '%.3f' % g


def gaps(poses, side=None):
    """(min pair SAT gap, min wall gap) -- gap = -depth for pairs."""
    gp = min(-IV.depth_pair_pt(poses[i], poses[j]) for i in range(len(poses)) for j in range(i + 1, len(poses))) \
        if len(poses) > 1 else 9.0
    gw = 9.0
    for p in poses:
        q = C.square_corners(*p)
        gw = min(gw, q.min(), (side - q.max()) if side else 9.0)
    return gp, gw


def cells_met(pose, s, names):
    return [n for n in names if C.overlap_depth(*pose, C.cell_rect(n, s)) > 1e-9]


def corner_cells(pg, key, s=None):
    for n, col in (('BL00', '#fff3cc'), ('BL01', '#e3f0ff'), ('BL10', '#e3f0ff')):
        pg.rect(key, C.cell_rect(n, 4.0), col, '#bbb', 0.7)


def panel_A(pg):
    pg.panel('A', 20, 30, 280, 280, 2.6, win=(0, 2.6, 0, 2.6))
    corner_cells(pg, 'A')
    d, th = 0.6, math.radians(25)
    A = (d + 0.5, 0.5, 0.0)
    xv, yv = math.sin(th), 1 - (d - math.sin(th)) * math.tan(th)
    B = from_vertex((xv, yv), th)
    pg.rect('A', (1 + d, 2, 0, 1), '#ffd6d6', RED, 0.8, dash='3,2')
    pg.square('A', A, BLUE, '#123', label='A')
    pg.square('A', B, GREEN, '#123', label='B')
    pg.line(*pg._t('A', (0, 0)), *pg._t('A', (0, 2.6)), '#222', 1.6)
    pg.line(*pg._t('A', (0, 0)), *pg._t('A', (2.6, 0)), '#222', 1.6)
    s4 = 4.0
    mA, mB = cells_met(A, s4, ('BL00', 'BL01', 'BL10')), cells_met(B, s4, ('BL00', 'BL01', 'BL10'))
    gp, gw = gaps([A, B])
    W = (xv - math.sin(th), yv + math.cos(th))
    pg.text(30, 24, '(A) a type-F corner: own incidences 4 of 6', 11, weight='bold')
    pg.note(20, 326, ['delta = %.2f, theta = 25 deg, partner in mode (a): x_v = sin theta, y_v = 1 - (delta - sin theta) tan theta' % d,
                      'A meets %s, B meets %s: each slot has ONE own meeter [T, rule E]' % (mA, mB),
                      'B\'s leftmost vertex at height %.3f > 1; its part below v = 1 has u <= delta = %.2f' % (W[1], d),
                      'c10\'s second meeter lives in the red strip (1+delta, 2) x (0, 1): a jut or the BR flat meeter',
                      'c01\'s second meeter: TL\'s meeter reaching y < 2, or a free square above B\'s edge (notch)',
                      'check: pair gap %s (B rests on A\'s corner), quadrant gap %s, B\'s top at %.3f >= 2 (R\' = %.3f >= 1)'
                      % (fg(gp), fg(gw), yv + G.w(th), G.w(th) - (d - math.sin(th)) * math.tan(th))])


def panel_B(pg):
    pg.panel('B', 320, 30, 280, 280, 2.2, win=(0, 2.2, 0, 2.2))
    corner_cells(pg, 'B')
    u0 = v0 = 1.7
    pg.polyline([pg._t('B', (0, v0)), pg._t('B', (u0, 0))], RED, 1.6)
    side = u0 * v0 / (u0 + v0)
    pg.rect('B', (0, side, 0, side), 'none', RED, 1.0, dash='4,2')
    pg.line(*pg._t('B', (0, 0)), *pg._t('B', (0, 2.2)), '#222', 1.6)
    pg.line(*pg._t('B', (0, 0)), *pg._t('B', (2.2, 0)), '#222', 1.6)
    pg.text(330, 24, '(B) NOT-SELF-SUFFICIENT: the separating line', 11, weight='bold')
    pg.note(320, 326, ['two disjoint squares both meeting c00, c01, c10: their separating line meets all three',
                       'cells, so it DESCENDS (u0, v0 > 0) and crosses the box iff 1/u0 + 1/v0 > 1 (here %.3f)' % (1 / u0 + 1 / v0),
                       'the lower square sits in the triangle; its largest inscribed square has side',
                       'u0 v0 / (u0 + v0) = %.3f < 1 (SQUARE-IN-TRIANGLE, any tilt) -- contradiction [T]' % side])


def panel_Bp(pg):
    pg.panel('Bp', 20, 360, 280, 250, 2.4, win=(0, 2.4, 0, 2.4))
    corner_cells(pg, 'Bp')
    A = (0.6, 1.35, 0.0)
    ph = math.radians(70)
    Wb = (0.95, math.cos(ph))                # leftmost vertex; the lowest vertex then sits ON the floor
    B = from_vertex((Wb[0] + math.sin(ph), Wb[1] - math.cos(ph)), ph)
    pg.square('Bp', A, BLUE, '#123', label='A')
    pg.square('Bp', B, GREEN, '#123', label='B')
    pg.line(*pg._t('Bp', (0, 0)), *pg._t('Bp', (0, 2.4)), '#222', 1.6)
    pg.line(*pg._t('Bp', (0, 0)), *pg._t('Bp', (2.4, 0)), '#222', 1.6)
    mA, mB = cells_met(A, 4.0, ('BL00', 'BL01', 'BL10')), cells_met(B, 4.0, ('BL00', 'BL01', 'BL10'))
    gp, gw = gaps([A, B])
    pg.text(30, 354, "(B') sharp: two squares share c00 AND c10", 11, weight='bold')
    pg.note(20, 620, ['A = [0.1, 1.1] x [0.85, 1.85] meets %s; B (70 deg, leftmost vertex (0.95, 0.342)) meets %s' % (mA, mB),
                      'check: pair gap %s (disjoint), quadrant gap %s -- the lemma needs all THREE cells' % (fg(gp), fg(gw))])


def panel_C(pg):
    s = SHAT
    pg.panel('C', 320, 360, 560, 250, s, win=(0, s, 0, 2.9))
    for n in C.CELLS:
        if n in ('BL00', 'BL10', 'BR10', 'BR00', 'BL01', 'TL01'):
            pg.rect('C', C.cell_rect(n, s), '#fff3cc' if n.endswith('00') else '#e3f0ff', '#bbb', 0.7)
    d, th = 0.9, math.radians(45)
    A = (d + 0.5, 0.5, 0.0)
    Ap = (s - d - 0.5, 0.5, 0.0)
    xv, yv = math.sin(th), 1 - (d - math.sin(th)) * math.tan(th)
    B = from_vertex((xv, yv), th)
    Bp = (s - B[0], B[1], th)
    Btl = (B[0], s - B[1], th)
    for p, lab in ((A, 'A'), (Ap, "A'"), (B, 'B'), (Bp, "B'")):
        pg.square('C', p, BLUE if lab[0] == 'A' else GREEN, '#123', label=lab)
    pg.square('C', Btl, 'none', RED, 1.2, label='B(TL)', dash='4,2', op=0.0)
    pg.line(*pg._t('C', (0, 0)), *pg._t('C', (s, 0)), '#222', 1.6)
    pg.line(*pg._t('C', (0, 0)), *pg._t('C', (0, 2.9)), '#222', 1.6)
    pg.line(*pg._t('C', (s, 0)), *pg._t('C', (s, 2.9)), '#222', 1.6)
    ps = [A, Ap, B, Bp]
    gp, gw = gaps(ps, s)
    sup = {n: [lab for p, lab in zip(ps, ('A', "A'", 'B', "B'")) if C.overlap_depth(*p, C.cell_rect(n, s)) > 1e-9]
           for n in ('BL00', 'BL10', 'BR10', 'BR00')}
    ov = IV.depth_pair_pt(B, Btl)
    pg.text(330, 354, '(C) the mutual-ADJ wall at s-hat: a packing below 4 -- the side wall is where it breaks', 11, weight='bold')
    pg.note(320, 620, ['s = %.6f: flat meeters at delta = delta\' = 0.9 > s - 3 = %.3f, partners 45 deg in mode (a)' % (s, s - 3),
                       'bottom cells: ' + ', '.join('%s <- %s' % (n, '+'.join(v)) for n, v in sup.items()) + '  (AO / AO)',
                       'check: pair gap %s, wall gap %s: a packing; B\'s top at %.3f > s - 2 = %.3f (meets TL01)' % (fg(gp), fg(gw), B[1] + G.w(th) / 2, s - 2),
                       'TL\'s mirror partner (dashed) would overlap B by %.3f: the left wall cannot hold both crowds' % ov])


def load_rows():
    return [json.loads(l) for l in open(os.path.join(ATT, 'results', 'construct246.jsonl'))]


def z_of(rid):
    src = {'a217:': os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'results', 'twelve244.jsonl')}
    for line in open(src['a217:']):
        r = json.loads(line)
        if r['rid'] == rid:
            return r['z']


def panel_packing(pg, key, x, y, w, h, z, title, rep, extra):
    ps, s = G.poses(z)
    pg.panel(key, x, y, w, h, s)
    for n in C.CELLS:
        pg.rect(key, C.cell_rect(n, s), '#fff3cc' if n.endswith('00') else '#e3f0ff', '#bbb', 0.6)
    pg.frame(key, s)
    ms = G.meeters(z)
    cm = {i for c in C.CORNERS for i in ms['%s00' % c]}
    for i, p in enumerate(ps):
        pg.square(key, p, BLUE if i in cm else ORANGE, '#123', label=str(i))
    gp, gw = gaps(ps, s)
    letters = rep['pattern']['letters']
    pg.text(x + 10, y - 6, title, 11, weight='bold')
    pg.note(x, y + h + 16, ['side %.6f, corner types %s, f = %d free squares (orange), max cells %d' % (
        s, rep['pattern']['types'], rep['pattern']['free_squares'], rep['max_cells']),
        'slots: ' + ', '.join('%s %s' % (n, letters[n]) for n in C.SLOTS),
        'check: pair gap %.1e, wall gap %.1e' % (gp, gw)] + extra)


def page2(rows):
    pg = Page(900, 660, 'A246 tight case')
    best = [r for r in rows if r['rid'] == 'a217:crowd_10_0113|crowd0.02|twelve|d1e-05'][0]
    panel_packing(pg, 'D', 20, 30, 300, 300, z_of(best['rid']), '(D) the certified 12-stuck at 4.000022', best['report'],
                  ['every rule of the note holds; outside demand %d = ADJ %d + FREE %d' % (
                      sum(best['report']['pattern']['outside_demand'].values()), best['report']['pattern']['adj_inc'],
                      best['report']['pattern']['free_inc'])])
    fr = [r for r in rows if r['rid'].startswith('fresh|s3.877')][0]
    z = fr['report'].get('z')
    if z is None:
        z = json.load(open(os.path.join(ATT, 'results', 'fresh246.json')))[fr['rid']]
    bad = [c for c, v in fr['report']['D_not_self_sufficient'].items() if v] + \
          [c for c, v in fr['report']['F_type_f'].items() if v]
    panel_packing(pg, 'E', 340, 30, 300, 300, z, '(E) the best attempt at s-hat (not a packing)', fr['report'],
                  [fr['note'], 'rules broken: %s' % (', '.join('%s (%s)' % (c, 'D' if fr['report']['D_not_self_sufficient'][c] else 'E') for c in bad) or 'none'),
                   'the candidate cheats on the packing itself (overlaps 2.8e-2); 21 of the 306 attempts',
                   'buy a self-sufficient corner (rule D) or a type-F corner with 3 own incidences (rule E)'])
    # (F) SLOT-MET caps
    pg.panel('F', 660, 30, 230, 300, 2.0, win=(0, 2.2, 0, 2.0))
    corner_cells(pg, 'F')
    thA, aA, vA = math.radians(4.5), 0.03, 0.997        # A243's extreme pair (86 deg, 4.5 deg)
    thB, aB, vB = math.radians(86), 0.03, 0.5
    A = (1 - aA + (math.cos(thA) + math.sin(thA)) / 2, vA + (math.sin(thA) - math.cos(thA)) / 2, thA)
    B = (1 - aB + (math.cos(thB) + math.sin(thB)) / 2, vB + (math.sin(thB) - math.cos(thB)) / 2, thB)
    pg.square('F', A, BLUE, '#123', label='A', op=0.5)
    pg.square('F', B, GREEN, '#123', label='B', op=0.5)
    pg.line(*pg._t('F', (1, 0)), *pg._t('F', (1, 2)), RED, 1.0, dash='3,2')
    pg.line(*pg._t('F', (0, 0)), *pg._t('F', (0, 2)), '#222', 1.6)
    pg.line(*pg._t('F', (0, 0)), *pg._t('F', (2.2, 0)), '#222', 1.6)
    ov = IV.depth_pair_pt(A, B)
    res = {}
    for fn in sorted(os.listdir(os.path.join(ATT, 'results'))):
        if fn.startswith('slotmet246_'):
            r = json.load(open(os.path.join(ATT, 'results', fn)))
            res[r['eta']] = (r['status'], r['processed'], r['seconds'])
    pg.text(670, 24, '(F) SLOT-MET: the cap reduction', 11, weight='bold')
    pg.note(660, 346, ['each square of a counterexample has exactly its leftmost vertex',
                       'W = (1 - a, v) left of u = 1, in the box [T CAP-REDUCTION];',
                       'here A: 4.5 deg, a = 0.03, v = 0.997; B: 86 deg, a = 0.03, v = 0.5',
                       'check: they overlap by %.3f (SLOT-MET says they must)' % ov,
                       'B&B over (theta, a, v)^2, guard 1e-9:'] +
            ['  eta = %g: %s, %d boxes, %.0f s' % (e, v[0], v[1], v[2]) for e, v in sorted(res.items(), reverse=True)])
    pg.save(os.path.join(OUT, 'tight_case.svg'))


def main():
    os.makedirs(OUT, exist_ok=True)
    pg = Page(900, 660, 'A246 corner propagation')
    panel_A(pg)
    panel_B(pg)
    panel_Bp(pg)
    panel_C(pg)
    pg.save(os.path.join(OUT, 'corner_propagation.svg'))
    page2(load_rows())
    print('pages written to', OUT)


if __name__ == '__main__':
    main()
