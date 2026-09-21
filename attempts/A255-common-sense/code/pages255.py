"""A255 pages (geometry-checked; a note per panel saying what it IS; undecided = grey stipple, never green).
  local_witnesses.svg   the local counter-hypothesis realised: mixed-sense corners with every CELLS family of
                        {c00, c01, c10} over-met (local255), and the same WITH the slide-block clause (blocked255)
  corpus_violators.svg  the corpus corners below side 4 that violate common sense, with the reducing family
                        (Lemma CELLS) drawn; and the witness against the literal form of the PI's claim (c)
Every panel is checked before it is drawn: containment and pairwise SAT gaps >= -1e-7 (exact poses of the rows).
Colours: sense + blue, sense - red, flat grey-blue outline; cells dashed; the normal cell T dotted orange.
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import geo255 as G                                                    # noqa: E402
from local255 import sat_gap                                          # noqa: E402

PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A255-common-sense')
COL = {1: '#2b6cb0', -1: '#c53030', 0: '#4a5568', 'X': '#805ad5'}
SC = 120.0


def check(poses, side=None):
    V = [G.corners_of(*p) for p in poses]
    g = min([sat_gap(V[i], V[j]) for i in range(len(V)) for j in range(i)] or [1.0])
    lo = min(v.min() for v in V)
    hi = max(v.max() for v in V)
    ok = g >= -1e-7 and lo >= -1e-7 and (side is None or hi <= side + 1e-7)
    return ok, g


class Panel:
    def __init__(self, x0, y0, size, title):
        self.x0, self.y0, self.size, self.out = x0, y0, size, []
        self.out.append('<text x="%.1f" y="%.1f" font-size="13" font-weight="bold">%s</text>' % (x0, y0 - 8, title))

    def pt(self, x, y):
        return self.x0 + x * SC, self.y0 + (self.size - y) * SC

    def poly(self, V, **kw):
        pts = ' '.join('%.2f,%.2f' % self.pt(x, y) for x, y in V)
        style = ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
        self.out.append('<polygon points="%s" %s/>' % (pts, style))

    def rect(self, R, **kw):
        self.poly([(R[0], R[2]), (R[1], R[2]), (R[1], R[3]), (R[0], R[3])], **kw)

    def label(self, x, y, s, size=11, fill='#1a202c'):
        px, py = self.pt(x, y)
        self.out.append('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="middle">%s</text>'
                        % (px, py + 4, size, fill, s))

    def square(self, pose, name):
        sg = G.sense(pose[2])
        self.poly(G.corners_of(*pose), fill=COL[sg], fill_opacity='0.22', stroke=COL[sg], stroke_width='1.6')
        self.label(pose[0], pose[1], '%s %s%.1f' % (name, '' if sg == 0 else ('+' if sg > 0 else ''), G.phi_deg(pose[2])))

    def note(self, lines):
        for k, ln in enumerate(lines):
            self.out.append('<text x="%.1f" y="%.1f" font-size="11" fill="#2d3748">%s</text>'
                            % (self.x0, self.y0 + self.size * SC + 16 + 14 * k, ln))


def local_panel(row, x0, y0, blocked):
    names = ['B', 'A', 'C', 'D'] + (['E'] if blocked else [])
    poses = [tuple(row['poses'][n]) for n in names]
    ok, g = check(poses)
    P = Panel(x0, y0, 3.5, 'type %s   sup-margin %.4f' % (row['type'], row['sup_margin']))
    P.rect((0, 3.5, 0, 3.5), fill='none', stroke='#a0aec0', stroke_width='0.6')
    P.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" stroke-width="3"/>' % (P.pt(0, 0) + P.pt(3.5, 0)))
    P.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" stroke-width="3"/>' % (P.pt(0, 0) + P.pt(0, 3.5)))
    for nm, R in (('c00', (0, 1, 0, 1)), ('c01', (0, 1, 1, 2)), ('c10', (1, 2, 0, 1))):
        P.rect(R, fill='none', stroke='#718096', stroke_width='1', stroke_dasharray='5,4')
        P.label(R[0] + 0.12, R[3] - 0.1, nm, 9, '#718096')
    if blocked:
        P.poly(G.corners_of(*row['T']), fill='none', stroke='#dd6b20', stroke_width='1.6', stroke_dasharray='2,3')
    for n, p in zip(names, poses):
        P.square(p, n)
    what = ('IS: a corner (walls bold) whose root c00 is met by B, A only, c01 also by C, c10 also by D -- every CELLS '
            'family in {c00,c01,c10} is over-met --')
    P.note([what, 'with designated wall touchers of DIFFERENT sense (blue +, red -, grey flat).' +
            ('  Dotted orange: the normal cell T; a square other than the slider meets it (slide BLOCKED).' if blocked else ''),
            'check: %s, least pair gap %.4f, all in the quadrant.  [M] optimiser witness, not a packing of n squares.'
            % ('PASS' if ok else 'FAIL', g)])
    return P.out if ok else []


def corpus_panel(corpus, rid, corner, x0, y0, extra=None):
    from sense255 import corpora
    for c, r, s, poses in corpora():
        if c == corpus and r == rid:
            break
    ok, g = check(poses, s)
    rec = next(x for x in (json.loads(l) for l in open(os.path.join(ATT, 'results', 'sense255.jsonl')))
               if x['rid'] == rid and x['corpus'] == corpus)
    cr = next(k for k in rec['corners'] if k['corner'] == corner)
    P = Panel(x0, y0, s, '%s  s = %.6f  corner %s: %s, reduces at L%s' % (rid, s, corner, cr['tclass'], cr['level']))
    P.rect((0, s, 0, s), fill='none', stroke='#1a202c', stroke_width='2.5')
    allc = {G.cell_name(k): k for k in G.all_cells(s)}
    for nm in (cr['reduce'][0] if cr['reduce'] else []):
        P.rect(G.cell_rect(allc[nm], s), fill='#ecc94b', fill_opacity='0.35', stroke='#b7791f', stroke_width='1.2',
               stroke_dasharray='5,3')
    for i, p in enumerate(poses):
        P.square(p, str(i))
    lines = ['IS: a corpus packing (not family-stuck).  Corner %s: wall touchers %s, senses %s.' %
             (corner, cr['wallV'] + cr['wallH'], cr['senses']),
             'Yellow: the smallest CELLS family that reduces it: %s met by squares %s only.' %
             (cr['reduce'][0] if cr['reduce'] else '-', cr['reduce'][1] if cr['reduce'] else '-')]
    if extra:
        T, txt = extra(poses, s)
        P.poly(G.corners_of(*T), fill='none', stroke='#dd6b20', stroke_width='1.8', stroke_dasharray='2,3')
        lines.append(txt)
    lines.append('check: %s, least pair gap %.2e, inside [0,s]^2.' % ('PASS' if ok else 'FAIL', g))
    P.note(lines)
    return P.out if ok else [], s


def claim_c(poses, s):
    p = poses[9]
    sec = 1.0 / math.cos(math.radians(G.phi_deg(p[2])))
    return (p[0], p[1] - sec, p[2]), ('Dotted orange: normal cell T of toucher 9 (down the wall), met by 6 (flat, settled) and 10: '
                                      '10 is second-layer, at 9\'s tilt, and MEETS BL01 (depth 0.265): claim (c) literal [F].')


def write(name, body, w, h):
    os.makedirs(PAGES, exist_ok=True)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (w, h),
           '<rect width="100%" height="100%" fill="white"/>'] + body + ['</svg>']
    open(os.path.join(PAGES, name), 'w', encoding='utf-8').write('\n'.join(svg))
    print('wrote', name)


def main():
    rows = {json.loads(l)['type']: json.loads(l) for l in open(os.path.join(ATT, 'results', 'local255.jsonl'))}
    bl = {}
    if os.path.exists(os.path.join(ATT, 'results', 'blocked255.jsonl')):
        bl = {json.loads(l)['type']: json.loads(l) for l in open(os.path.join(ATT, 'results', 'blocked255.jsonl'))}
    body, k = [], 0
    picks = [(rows[t], False) for t in ('P1:+-', 'P1:-+', 'P1:0+', 'P2:+-', 'P2:-+', 'P2:0-') if t in rows]
    picks += [(bl[t], True) for t in ('W:+-', 'W:-+', 'K:+-', 'K:-+') if t in bl and bl[t]['sup_margin'] > 1e-6]
    for row, blocked in picks:
        body += local_panel(row, 30 + (k % 3) * 460, 40 + (k // 3) * 520, blocked)
        k += 1
    write('local_witnesses.svg', body, 1420, 40 + ((k + 2) // 3) * 520)
    body, y = [], 40
    for corpus, rid, corner, extra in (('A217', 'rand_0_0163|t3', 'TL', None), ('A217', 'rand_0_0441|free', 'BL', claim_c)):
        out, s = corpus_panel(corpus, rid, corner, 30, y, extra)
        body += out
        y += int(s * SC) + 110
    write('corpus_violators.svg', body, 760, y)


if __name__ == '__main__':
    main()
