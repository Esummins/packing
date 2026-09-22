"""A266 pages (docs/residue_map/campaigns/A266-last-two/): strip_tilted.svg (the tilted-C strip: the [F] witness for the
h_u, h_v < 1 reading, an in-domain configuration with the empty pocket, the left-shadow crescent) and miss_region.svg
(the miss region of the worst cap266 ring and its best-separated pair).  Every drawn square passes the exact geometry
check (probe266.witness_check / cap266.exact_pair) and each panel carries a note saying what it IS; undecided = grey
stipple, never green.    python pages266.py"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import strip266 as M                                                  # noqa: E402
import probe266 as P                                                  # noqa: E402
Z = M.Z
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A266-last-two')
RES = os.path.join(HERE, '..', 'results')
SC = 150.0


def poly(V, fill, stroke='#333', op=0.5, w=1.2, extra=''):
    pts = ' '.join('%.2f,%.2f' % (p[0], p[1]) for p in V)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f" %s/>' % (pts, fill, op, stroke, w, extra)


def T(x, y, s, sc=SC, ox=40, oy=40, H=560):
    return (ox + sc * x, oy + H - sc * y)


def tv(V, **kw):
    return [T(p[0], p[1], 0, **kw) for p in V]


def shp(g, fill, **kw):
    out = []
    for Pg in getattr(g, 'geoms', [g]):
        if Pg.geom_type == 'Polygon' and Pg.area > 1e-12:
            out.append(poly(tv(np.array(Pg.exterior.coords)[:-1], **kw), fill, op=0.55, w=0.8))
    return ''.join(out)


def strip_panel(x, ox, note, Q=None):
    C, X, Tu = P.verts_of(x)
    S = Polygon(Tu).difference(Polygon(C))
    kw = dict(ox=ox)
    g = ['<rect x="%d" y="40" width="450" height="560" fill="#fafafa" stroke="#999"/>' % ox]
    g.append(poly(tv(M.UNIT, **kw), 'none', stroke='#bbb', w=0.8, extra='stroke-dasharray="4,3"'))
    g.append(poly(tv(Tu, **kw), '#dde', stroke='#88a', op=0.35))
    g.append(shp(S, '#e8a000', **kw))
    g.append(poly(tv(C, **kw), '#c33', op=0.35))
    g.append(poly(tv(X, **kw), '#36c', op=0.35))
    if Q is not None:
        g.append(poly(tv(Z.sq_verts(*Q), **kw), '#2a2', stroke='#060', op=0.45, w=1.6))
    hu, hv, th, yx, ph = x
    g.append('<text x="%d" y="30" font-size="13" font-family="sans-serif">h_u=%.3f h_v=%.3f th_C=%.1f° y_X=%.2f phi_X=%.1f°</text>'
             % (ox, hu, hv, th / M.DEG, yx, ph / M.DEG))
    y = 620
    for line in note:
        g.append('<text x="%d" y="%d" font-size="11.5" font-family="sans-serif">%s</text>' % (ox, y, line))
        y += 15
    return ''.join(g)


def crescent_panel(x, ox, psi_deg):
    """the exact bad-centre region at tilt psi: (T_u (+) Q)^o \\ (C (+) Q)^o \\ (X (+) Q)^o /\\ quadrant-admissible."""
    C, X, Tu = P.verts_of(x)
    psi = psi_deg * M.DEG
    q0 = Z.sq_verts(0.0, 0.0, psi)
    h = 0.5 * (abs(math.cos(psi)) + abs(math.sin(psi)))
    Pc = Polygon(M.mink(C, q0))
    Pt = Polygon(M.mink(Tu, q0))
    Px = Polygon(M.mink(X, q0))
    from shapely.geometry import box as sbox
    cres = Pt.difference(Pc)
    bad = cres.intersection(sbox(h, h, 9, 9)).difference(Px)
    kw = dict(ox=ox)
    g = ['<rect x="%d" y="40" width="450" height="560" fill="#fafafa" stroke="#999"/>' % ox]
    g.append(poly(tv(np.array(Pc.exterior.coords)[:-1], **kw), '#c33', op=0.12))
    g.append(poly(tv(np.array(Pt.exterior.coords)[:-1], **kw), '#88a', op=0.12))
    g.append(shp(cres, '#e8a000', **kw))
    g.append(poly(tv(np.array(Px.exterior.coords)[:-1], **kw), '#36c', op=0.15))
    g.append('<line x1="%.1f" y1="40" x2="%.1f" y2="600" stroke="#000" stroke-dasharray="3,3"/>' % (T(h, 0, 0, **kw)[0], T(h, 0, 0, **kw)[0]))
    g.append(shp(bad, '#000', **kw) if not bad.is_empty else '')
    g.append(poly(tv(C, **kw), 'none', stroke='#c33', w=1.0))
    g.append(poly(tv(Tu, **kw), 'none', stroke='#88a', w=1.0))
    g.append(poly(tv(X, **kw), 'none', stroke='#36c', w=1.0))
    note = ['CENTRE SETS at tilt psi = %.0f°: red = C (+) Q (centres of Q overlapping C), violet = T_u (+) Q,' % psi_deg,
            'orange = their difference = the LEFT SHADOW of C (+) Q of horizontal width h_u (the bad centres before X and',
            'the wall); dashed = the wall constraint q_x >= w(psi)/2; blue = X (+) Q.  Bad centres = orange, right of the dash,',
            'outside blue: area %.2e (%s).  strip266 over-approximates exactly this set per tilt bin.' % (bad.area, 'EMPTY' if bad.area < 1e-9 else 'NONEMPTY')]
    y = 620
    for line in note:
        g.append('<text x="%d" y="%d" font-size="11.5" font-family="sans-serif">%s</text>' % (ox, y, line))
        y += 15
    return ''.join(g)


def page_strip():
    d = json.load(open(os.path.join(RES, 'probe266_jam.json')))
    fn = os.path.join(RES, 'probe266_jam_nobox.json')
    bad = [r for r in json.load(open(fn))['rows'] if 'witness' in r and r['witness']['check']['gap_C'] > 0.02
           and r['witness']['check']['gap_X'] > 0.02] if os.path.exists(fn) else []
    cert = [r for r in d['rows'] if r['radii']['0.02'][0] == 'CERT' and r['x'][2] > 0.3]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="720" font-family="sans-serif">',
             '<text x="40" y="18" font-size="15" font-weight="bold">A266 -- STRIP_2 for a TILTED C: the strip S = T_u \\ C (orange), C (red), its wall drop T_u (violet), X (blue); dashed = the unit box</text>']
    if bad:
        r = bad[0]
        chk = r['witness']['check']
        parts.append(strip_panel(r['x'], 40, [
            '[F] WITNESS for the reading "domain = h_u, h_v < 1": Q (green, flat, centre (%.2f, %.2f)) is in the quadrant,' % tuple(r['witness']['pose'][:2]),
            'interior-disjoint from C (gap %+.3f) and X (gap %+.3f), and meets int T_u (depth %.2f) -- a free square in the strip.' % (chk['gap_C'], chk['gap_X'], chk['depth_Tu']),
            'But C MISSES the open unit box (its lower-left edge passes x = 1 above y = 1): this C is not a JAM floater.',
            'STRIP_2 needs the true domain "C meets (0,1)^2", i.e. h_u cos + h_v sin < cos + sin - sin cos (Lean open_box_tilted).'], r['witness']['pose']))
    else:
        parts.append(strip_panel(d['rows'][0]['x'], 40, ['(no [F] witness recorded in probe266_jam.json)']))
    if cert:
        r = cert[0]
        parts.append(strip_panel(r['x'], 530, [
            'IN-DOMAIN configuration (C meets the open box, X above C meets T_u): NO unit square free of C and X in the',
            'quadrant meets S -- the box of radius 0.02 (positions) / 0.02 rad (tilts) around it is CERT by strip266.check_box',
            '(every 1° tilt bin of Q has an empty over-approximated bad set).  [T-computed] for this box; the 27-cell tree',
            'per lane is the certificate of the whole domain (its index says how far it is).']))
        parts.append(crescent_panel(r['x'], 1020, 20.0))
    parts.append('</svg>')
    open(os.path.join(OUT, 'strip_tilted.svg'), 'w', encoding='utf-8').write('\n'.join(parts))


def page_miss():
    fn = os.path.join(RES, 'cap266.json')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="720" font-family="sans-serif">',
             '<text x="40" y="18" font-size="15" font-weight="bold">A266 -- CAPACITY-2 on the non-ADJ family: the MISS REGION of the worst ring (cap266) and its best-separated pair</text>',
             '<defs><pattern id="st" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,0 l6,6" stroke="#888" stroke-width="1"/></pattern></defs>']
    if not os.path.exists(fn):
        parts.append('<rect x="40" y="40" width="600" height="560" fill="url(#st)" stroke="#999"/>')
        parts.append('<text x="40" y="620" font-size="12">cap266.json not written yet: UNDECIDED (grey stipple).  The chain writes it first.</text>')
    else:
        import cap266 as K
        d = json.load(open(fn))
        w = d['worst']
        s = w['s']
        x = np.array(w.get('x_climbed', w['x']))
        Vs = K.H.hyb_verts(x, s)
        sc = 560.0 / s
        kw = dict(sc=sc, ox=40)
        parts.append('<rect x="40" y="40" width="%.0f" height="560" fill="#fafafa" stroke="#999"/>' % (560))
        for V in Vs:
            parts.append(poly(tv(V, **kw), '#ccc', stroke='#555', op=0.6))
        pair = w.get('pair_climbed') or w.get('pair')
        g, wit = K.cap2(Vs, s, 1.0)
        area = 0.0
        best_psi = None
        for pd in np.arange(-45.0, 45.0, 1.0):
            Mr = K.miss_region(Vs, s, pd * M.DEG)
            if not Mr.is_empty and Mr.area > area:
                area, best_psi = Mr.area, pd
        if best_psi is not None:
            parts.append(shp(K.miss_region(Vs, s, best_psi * M.DEG), '#e8a000', **kw))
        if wit is not None:
            for pose, col in ((wit[0], '#2a2'), (wit[1], '#26c')):
                parts.append(poly(tv(Z.sq_verts(*pose), **kw), col, stroke='#000', op=0.35, w=1.4))
        O = T(s / 2, s / 2, 0, **kw)
        parts.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#000"/>' % O)
        note = ['Ring %s at s = %.4f (grey; shifts %s).  Orange = the MISS REGION at the tilt with the largest one (psi = %s°): centres of' % (w['name'], s, [round(t, 2) for t in w.get('shifts_climbed', w['shifts'])], best_psi),
                'free squares NOT containing O (dot).  Green / blue = the two misses the SAT search separates best: cap2 = %+.4f' % g,
                '(< 0: they OVERLAP by that much along the best axis -- no two interior-disjoint misses at 1° tilts; [M], one ring).',
                'Exact check of the pair: %s.' % json.dumps({k: round(v, 4) for k, v in (pair or {}).items() if isinstance(v, float)}),
                'This is a MEASUREMENT on the rings cap266 tried, not a certificate: CAPACITY-2 stays [C] (last_two.md s.2).']
        y = 620
        for line in note:
            parts.append('<text x="40" y="%d" font-size="11.5">%s</text>' % (y, line))
            y += 15
    parts.append('</svg>')
    open(os.path.join(OUT, 'miss_region.svg'), 'w', encoding='utf-8').write('\n'.join(parts))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    page_strip()
    page_miss()
    print('pages written to', OUT)
