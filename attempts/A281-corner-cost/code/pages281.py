"""A281 page: docs/residue_map/campaigns/A281-corner-cost/corner_cost.svg -- (a) the six wall pair types with their
exact witnesses at s-hat (PiPi: the best attempt, DEAD [T]), (b) the poker's slot supplied by a T-meeter of either
global sense, (c) the f-table, (d) exact 8-square witnesses of the surviving f-classes.  Every panel's note quotes
the exact-check flags from results/wall281_*.json; undecided = grey stipple, never green.    python pages281.py"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom281 as G  # noqa: E402
import wall281 as W  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
OUT = os.path.join(HERE, '..', '..', '..', 'docs', 'residue_map', 'campaigns', 'A281-corner-cost')
DEFS = ('<defs><pattern id="stip" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" '
        'fill="#ddd"/><circle cx="1.5" cy="1.5" r="0.9" fill="#666"/></pattern></defs>')
COL = {'flat': '#c9d6ea', 'poker': '#f2c9a0', 'tau': '#d9c3e6', 'free': '#eeeeee', 'slot': '#fff3b0', 'box': '#f7f7f7'}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=10, w='normal', anchor='start'):
    return ('<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="%d" font-weight="%s" text-anchor="%s">%s</text>'
            % (x, y, size, w, anchor, esc(t)))


def panel(ox, oy, sc, s):
    def P(x, y):
        return ox + x * sc, oy + (s - y) * sc
    return P


def poly(P, pts, fill, stroke='#333', sw=1.0, extra=''):
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" %s/>' % (
        ' '.join('%.1f,%.1f' % P(*p) for p in pts), fill, stroke, sw, extra)


def role_colour(roles, c, kind):
    r = roles[c]
    if r == 'T':
        return COL['tau']
    if (r == 'Ff') == (kind == 'A'):
        return COL['flat']
    return COL['poker']


def draw_config(svg, ox, oy, sc, s, roles, x, active, title, note, extra_cells=()):
    P = panel(ox, oy, sc, s)
    svg.append(poly(P, [(0, 0), (s, 0), (s, s), (0, s)], '#ffffff', '#000', 1.2))
    for c in active:
        cl = G.cells(s, c)
        svg.append(poly(P, cl['c00'], COL['box'], '#bbb', 0.6, 'stroke-dasharray="2,2"'))
        svg.append(poly(P, cl['c01'], COL['slot'], '#c9b200', 0.6, 'stroke-dasharray="2,2"'))
        svg.append(poly(P, cl['c10'], COL['slot'], '#c9b200', 0.6, 'stroke-dasharray="2,2"'))
    for (c, cell) in extra_cells:
        svg.append(poly(P, G.cells(s, c)[cell], 'none', '#c00', 1.2, 'stroke-dasharray="3,2"'))
    params = W.unpack(x, roles, active)
    sq = W.squares(params, s)
    for (c, kind), Q in sq.items():
        svg.append(poly(P, Q, role_colour(roles, c, kind), '#333', 1.0))
        cx, cy = sum(q[0] for q in Q) / 4, sum(q[1] for q in Q) / 4
        svg.append(text(*P(cx, cy), '%s%s' % (G.CORNERS[c], kind), 8, anchor='middle'))
    svg.append(text(ox, oy - 6, title, 11, 'bold'))
    for k, line in enumerate(note):
        svg.append(text(ox, oy + s * sc + 12 + 11 * k, line, 8))


def main():
    pairs = json.load(open(os.path.join(RES, 'wall281_pairs.json'), encoding='utf-8'))
    rings_fn = os.path.join(RES, 'wall281_rings.json')
    rings = json.load(open(rings_fn, encoding='utf-8')) if os.path.exists(rings_fn) else {}
    count = json.load(open(os.path.join(RES, 'count281.json'), encoding='utf-8'))
    s = G.SHAT
    key = '%.6f' % s
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1900" font-family="sans-serif">', DEFS,
           '<rect width="1500" height="1900" fill="#fff"/>',
           text(20, 24, 'A281 CORNER COST -- the two corner classes F (flat + poker) / T (both tilted), their wall '
                'roles Phi / Pi / tau, and the f-table on the window [3.82, s-hat]', 14, 'bold'),
           text(20, 40, 'Every witness is a set of unit squares verified EXACTLY (rational tilt on the unit circle, '
                'SAT gaps >= 0, containment, box / slot incidences strict).  Colours: flat blue, poker orange, '
                'T-meeter violet; slots yellow, boxes dotted; red dashed = the slot the witness was asked to meet.  '
                'Grey stipple = undecided.  Dead by [T] is written on the panel.', 9)]
    checks = {}
    sc = 58
    # (a) the six wall pair types at s-hat
    names = ['PhiPhi', 'PhiPi', 'PiPi', 'Phi-tau', 'Pi-tau', 'tau-tau']
    for k, name in enumerate(names):
        rec = pairs['%s@%s' % (name, key)]
        ox, oy = 20 + k * 245, 75
        m = rec['sup_margin']
        if name == 'PiPi':
            note = ['(a%d) %s: DEAD on W [T] (TWO-POKERS, s* = 3.9342).' % (k + 1, name),
                    'best attempt at s-hat: sup margin %.5f < 0 (overlap drawn).' % m,
                    'Exact witness: none (as it must be).']
        else:
            note = ['(a%d) %s: sup margin %+.4f at s-hat; exact check %s.' % (k + 1, name, m, rec['exact_ok']),
                    'container / disjoint / boxes: %s / %s / %s.' % tuple(rec['exact'].get(t) for t in ('container', 'disjoint', 'boxes')),
                    'Alive by SIDE on W [T-computed].']
        draw_config(svg, ox, oy, sc, s, {int(k): v for k, v in rec['roles'].items()}, rec['x'], [0, 3], '(a%d) %s' % (k + 1, name), note)
        if name == 'PiPi':
            P = panel(ox, oy, sc, s)
            svg.append(poly(P, [(0, 1), (1, 1), (1, s - 1), (0, s - 1)], 'url(#stip)', 'none', 0, 'opacity="0.5"'))
            svg.append(text(ox + 8, oy + s * sc / 2, 'DEAD [T]', 12, 'bold'))
        checks['a%d' % (k + 1)] = {'name': name, 'sup_margin': m, 'exact_ok': rec['exact_ok'], 'exact': rec['exact']}
    # (b) the poker's slot supplied by a T-meeter: both senses; and the flat CANNOT (PhiPi+ADJ?)
    y1 = 75 + s * sc + 60
    for k, name in enumerate(['Pi-tau+ADJ<45', 'Pi-tau+ADJ>45', 'Pi-tau+ROW', 'Phi-tau+ADJ', 'PhiPi+ADJ?', 'tau-tau+ADJ']):
        rec = pairs.get('%s@%s' % (name, key))
        if rec is None:
            continue
        ox, oy = 20 + k * 245, y1
        m = rec['sup_margin']
        extra = [(e[2], e[3]) for e in rec['extra'] if e[0] != 'tilt']
        sense = ''
        if 'Pi-tau' in name:
            th = rec['thA_TL_deg']
            sense = 'TL wall meeter frame tilt %.1f deg: global sense %s the poker' % (th, 'OPPOSITE to' if th < 45 else 'SAME as')
        if m > 0:
            note = ['(b%d) %s: sup margin %+.4f, exact %s.' % (k + 1, name, m, rec['exact_ok']),
                    'red dashed slot(s) met by the named square: exact %s.' % rec['exact'].get('extra'), sense]
        else:
            note = ['(b%d) %s: sup margin %+.4f < 0: IMPOSSIBLE' % (k + 1, name, m),
                    '(a flat never meets the poker slot: FLAT-ABOVE [T])' if 'PhiPi' in name else '(not found)', sense]
        draw_config(svg, ox, oy, sc, s, {int(k): v for k, v in rec['roles'].items()}, rec['x'], [0, 3], '(b%d) %s' % (k + 1, name), note, extra)
        checks['b%d' % (k + 1)] = {'name': name, 'sup_margin': m, 'exact_ok': rec['exact_ok'], 'exact': rec['exact']}
    # (c) the f-table
    y2 = y1 + s * sc + 60
    svg.append(text(20, y2, '(c) The f-table (count281.py): SIDE = no Pi-Pi wall [T]; h = least free squares by the room count '
                    '(FAMILY-STUCK + ninth square + PROJECTION) [T]; h_sep = with SEPARATE-NOTCHES [M]; locks = normal-form '
                    'locked walls / 2 [T-prose]; 3 free squares.', 10, 'bold'))
    hdr = '%-14s %-2s %-38s %-5s %-3s %-5s %-5s %-9s %-9s' % ('orbit', 'f', 'walls', 'SIDE', 'h', 'h_sep', 'locks', 'alive[T]', 'alive[T+M]')
    svg.append('<text x="20" y="%d" font-family="monospace" font-size="9" xml:space="preserve">%s</text>' % (y2 + 14, esc(hdr)))
    for k, r in enumerate(count['rows']):
        line = '%-14s %-2d %-38s %-5s %-3d %-5d %-5d %-9s %-9s' % (
            r['roles'], r['f'], ' '.join(r['walls']), 'DEAD' if r['side_dead'] else 'ok', r['h_count'], r['h_count_sep'],
            r['h_locks'], r['alive_all_T'], r['alive_all_TM'])
        svg.append('<text x="20" y="%d" font-family="monospace" font-size="9" xml:space="preserve">%s</text>' % (y2 + 26 + 11 * k, esc(line)))
    y3 = y2 + 26 + 11 * len(count['rows']) + 20
    svg.append(text(20, y3, 'Count alone kills nothing (h <= 2 everywhere; A250); side kills every orbit with a Pi-Pi wall; '
                    '[M] SEPARATE-NOTCHES kills the f = 4 pinwheel (A248).  Survivors all contain a T corner; what closes them is ROOM '
                    '(the free square contains O), not a count.', 9))
    # (d) 8-square witnesses of the surviving classes
    y4 = y3 + 30
    k = 0
    for name, rec in rings.items():
        run = rec['runs'].get(key)
        if run is None or rec['side_dead_PiPi']:
            continue
        ox, oy = 20 + (k % 6) * 245, y4 + (k // 6) * (s * sc + 70)
        m = run['sup_margin']
        roles = {c: rec['roles'][c] for c in range(4)}
        if m > 0 and run['exact_ok']:
            note = ['(d%d) f=%d %s: 8 outer squares at s-hat, margin %+.4f,' % (k + 1, rec['f'], name, m),
                    'exact %s -- alive by SIDE; walls %s.' % (run['exact_ok'], ' '.join('-'.join(p) for p in rec['walls'])),
                    'closed only by ROOM / holders, not by side.']
            draw_config(svg, ox, oy, sc, s, roles, run['x'], [0, 1, 2, 3], '(d%d) %s' % (k + 1, name), note)
        else:
            P = panel(ox, oy, sc, s)
            svg.append(poly(P, [(0, 0), (s, 0), (s, s), (0, s)], 'url(#stip)', '#000', 1.2))
            svg.append(text(ox, oy - 6, '(d%d) %s' % (k + 1, name), 11, 'bold'))
            svg.append(text(ox, oy + s * sc + 12, '(d%d) f=%d: no exact witness found (sup %+.4f): UNDECIDED by side (grey).' % (k + 1, rec['f'], m), 8))
        checks['d%d' % (k + 1)] = {'name': name, 'f': rec['f'], 'sup_margin': m, 'exact_ok': run['exact_ok']}
        k += 1
    svg.append('</svg>')
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'corner_cost.svg'), 'w', encoding='utf-8').write('\n'.join(svg))
    json.dump(checks, open(os.path.join(RES, 'pages281.json'), 'w'), indent=1)
    print('wrote', os.path.join(OUT, 'corner_cost.svg'), len(checks), 'panels')


if __name__ == '__main__':
    main()
