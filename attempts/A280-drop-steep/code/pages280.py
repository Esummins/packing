"""A280 page: docs/residue_map/campaigns/A280-drop-steep/drop_steep.svg -- (a) an A273 OPEN leaf at steep C and its
bad-centre test set (undecided q-cells grey stipple), (b) the nearest tree280 CERT leaf's test set (every cell
decided), (c) the h_u -> 1 near-miss that LOWF removes, (d) the (theta, phi) map.  Geometry checks -> results/
pages280.json (each panel's note quotes them).    python pages280.py"""
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pagegeom280 as PG                                              # noqa: E402
import prune280 as P8                                                 # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A280-drop-steep')
A273 = os.path.join(ATT, '..', 'A273-disc-lemma')
DEG = math.pi / 180
COL = {'K01': '#f4f4f4', 'KL': '#f4f4f4', 'K4': '#eeeeee', 'K2': '#cfe0f3', 'K5': '#f9dcb8', 'fine': '#c9e7c1'}
DEFS = ('<defs><pattern id="stip" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" '
        'fill="#ddd"/><circle cx="1.5" cy="1.5" r="0.9" fill="#666"/></pattern></defs>')


def panel(ox, oy, sc, x0, y1):
    def P(x, y):
        return ox + (x - x0) * sc, oy + (y1 - y) * sc
    return P


def poly(P, pts, fill, stroke='#333', extra=''):
    s = ' '.join('%.1f,%.1f' % P(*p) for p in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1" %s/>' % (s, fill, stroke, extra)


def text(x, y, s, size=11, w='normal'):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="%d" font-weight="%s">%s</text>' % (x, y, size, w, s)


def scene(P, sc, pol, cells):
    o = []
    for x, y, k in cells:
        (a, b) = P(x - PG.H, y + PG.H)
        f = 'url(#stip)' if k is None else COL[k]
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"%s/>' % (
            a, b, 2 * PG.H * sc, 2 * PG.H * sc, f, ' stroke="#000" stroke-width="1.5"' if k is None else ''))
    o.append(poly(P, pol['C'], '#d9534f', extra='fill-opacity="0.45"'))
    o.append(poly(P, pol['X'], '#428bca', extra='fill-opacity="0.45"'))
    o.append(poly(P, pol['T'], 'none', '#222', 'stroke-dasharray="5,3"'))
    return o


def nearest_cert(box, path):
    mid = [0.5 * (a + b) for a, b in box]
    best = None
    for l in gzip.open(path, 'rt'):
        r = json.loads(l)
        if r['v'] != 'CERT':
            continue
        m = [0.5 * (a + b) for a, b in r['box']]
        d = sum(((m[i] - mid[i]) / (1.0, 45 * DEG, 1.01, 45 * DEG)[i]) ** 2 for i in range(4))
        if best is None or d < best[0]:
            best = (d, r['box'])
    return best[1]


def mapcells(P):
    i273 = {r['cell']: r for r in map(json.loads, open(os.path.join(A273, 'certs', 'index273.jsonl')))}
    v280 = {}
    vi = os.path.join(ATT, 'results', 'verify280_index.jsonl')
    if os.path.exists(vi):
        for r in map(json.loads, open(vi)):
            v280[r['cell'].replace('_bench', '')] = r
    o, cnt = [], {}
    for ti in range(9):
        for pj in range(9):
            nm = 'c%d_%d' % (ti, pj)
            r3, r8 = i273.get(nm), v280.get(nm)
            if r8 and r8['verdict'] == 'PASS':
                f, k = '#5cb85c', 'A280'
            elif r3 and r3['verdict'] == 'CERT':
                f, k = '#9fd49f', 'A273'
            elif r3 or (ti == 0 and pj == 0):
                f, k = 'url(#stip)', 'open'
            else:
                f, k = 'white', 'pending'
            cnt[k] = cnt.get(k, 0) + 1
            a, b = P(pj * 5, ti * 5 + 5)
            o.append('<rect x="%.1f" y="%.1f" width="25" height="25" fill="%s" stroke="#555"/>' % (a, b, f))
    return o, cnt


def main():
    d = json.load(open(os.path.join(ATT, 'results', 'diag280_c7_6.json')))
    LA = d['samples'][0]['box']
    tp = os.path.join(ATT, 'certs', 'tree280_c7_6.jsonl.gz')
    LB = nearest_cert(LA, tp if os.path.exists(tp) else tp.replace('.jsonl', '_bench.jsonl'))
    mA, mB = [0.5 * (a + b) for a, b in LA], [0.5 * (a + b) for a, b in LB]
    cA, cB = PG.testset(LA), PG.testset(LB)
    cor = PG.corner_panel()
    und = lambda cs: sum(1 for c in cs if c[2] is None)
    js = dict(A=dict(box=LA, prune280=P8.prune280(LA), checks=PG.checks(mA), undecided=und(cA), cells=len(cA),
                     slack_M=d['samples'][0]['slack']),
              B=dict(box=LB, prune280=P8.prune280(LB), checks=PG.checks(mB), undecided=und(cB), cells=len(cB)),
              C={k: v for k, v in cor.items() if k != 'polys'})
    sc, x0, y1 = 105.0, -0.25, 1.45
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="1420" height="700" viewBox="0 0 1420 700">', DEFS,
         '<rect width="1420" height="700" fill="white"/>',
         text(20, 24, 'A280 -- the DROP LEMMA at steep C (theta >= 25 deg): the OPEN layer was a missing prune, not a '
              'miss (C_top frame, part R; q-cells of half-side 1/32)', 14, 'bold')]
    for k, (ox, m, cs, ttl) in enumerate([(20, mA, cA, '(a) A273 OPEN leaf, c7_6 (before); black box = undecided'),
                                          (365, mB, cB, '(b) nearest tree280 CERT leaf (after)')]):
        P = panel(ox, 60, sc, x0, y1)
        o += [text(ox, 52, ttl, 12, 'bold')] + scene(P, sc, PG.polys(m), cs)
        o.append(text(ox, 445, 'h_u %.4f  theta %.3f  D %.4f  phi %.3f' % (m[0], m[1] / DEG, m[2], m[3] / DEG), 10))
    P = panel(710, 60, sc, x0, y1)
    pc = cor['polys']
    o += [text(710, 52, '(c) the h_u -> 1 near-miss (removed by LOWF)', 12, 'bold'),
          poly(P, pc['C'], '#d9534f', extra='fill-opacity="0.45"'), poly(P, pc['X'], '#428bca', extra='fill-opacity="0.45"'),
          poly(P, pc['T'], 'none', '#222', 'stroke-dasharray="5,3"')]
    qx, qy = P(*cor['q'])
    o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f0ad4e" fill-opacity="0.35" stroke="#b36b00"/>' % (qx, qy, 0.5 * sc))
    o.append(poly(P, [(0, cor['q'][1] - .5), (1, cor['q'][1] - .5), (1, cor['q'][1] + .5), (0, cor['q'][1] + .5)],
                  'none', '#b36b00', 'stroke-dasharray="3,2"'))
    Pm = panel(1080, 70, 5.0, 0, 45)
    mc, cnt = mapcells(Pm)
    o += [text(1080, 52, '(d) (theta, phi) cells, 5 deg', 12, 'bold')] + mc
    o += [text(1080, 70 + 240, 'phi 0 -> 45 (right); theta 0 (bottom) -> 45 (top)', 10),
          text(1080, 70 + 256, 'dark green: A280 tree + verify280 PASS', 10),
          text(1080, 70 + 272, 'light green: A273 CERT;  grey stipple: OPEN / queued', 10),
          text(1080, 70 + 288, 'white: not yet run.  counts %s' % json.dumps(cnt).replace('"', ''), 10)]
    cA_, cB_ = js['A']['checks'], js['B']['checks']
    notes = [
        '(a) A273 leaf (smallest OPEN box of c7_6): X (blue) sits wholly ABOVE T_u (dashed): exact area X n T_u = %.1e, '
        'dip D = %.4f < the (D-low) bound %.3f -- H2 fails, the box is outside H1-H3.  Its test set has %d of %d q-cells '
        'UNDECIDED at 1/4096 (grey stipple); [M] drop slack there %+.5f (negative but -> 0 as D -> 0).' % (
            cA_['XnTu'], cA_['D'], cA_['dlow'], js['A']['undecided'], js['A']['cells'], js['A']['slack_M']),
        '(b) tree280: that leaf is PRUNE:%s (int X misses int T_u).  Nearest CERT leaf: X meets T_u (area %.2e), D = %.3f '
        '>= %.3f; every q-cell decided (%d undecided): pale blue K2 (disc meets a core), orange K5 (drop penumbra), '
        'green = closed after refinement, light grey K0/K1/K4.' % (js['A']['prune280'], cB_['XnTu'], cB_['D'], cB_['dlow'],
                                                                   js['B']['undecided']),
        '(c) h_u = %.4f, theta 40, phi 32.88, D = D-low + 0.001: q = (1/2, L_h) -- D(q,1/2) touches the wall (%.1e), C\'s '
        'left vertex (%.1e) and X (%.1e); the unit square (dashed) fits between wall and C.  [M] slack -0.0012 -> 0 as '
        'h_u -> 1.  LOWF: L_h >= LOWB gives h_v >= %.3f, the open box h_v < %.3f: no h_v; h_u <= %.3f at theta 40.' % (
            cor['m'][0], cor['disc_wall'], cor['disc_Cleft'], cor['disc_X'], cor['hv_low'], cor['hv_up_openbox'],
            cor['hu_max'])]
    for i, n in enumerate(notes):
        for j in range(0, len(n), 205):
            o.append(text(20, 480 + 50 * i + 13 * (j // 205), n[j:j + 205], 10))
    o.append('</svg>')
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'drop_steep.svg'), 'w').write(''.join(o))
    json.dump(js, open(os.path.join(ATT, 'results', 'pages280.json'), 'w'), indent=1)
    print(json.dumps(js['A']['checks']), json.dumps(js['B']['checks']), js['A']['undecided'], js['B']['undecided'], cnt)


if __name__ == '__main__':
    main()
