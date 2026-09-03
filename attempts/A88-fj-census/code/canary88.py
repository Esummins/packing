"""A88 D4 CANARY: derive Trump's DECORATED structure by code from
certs/trump11_certificate.json and assert the contract of the chore.

Contract:
  * Trump's graph passes F0 (incl. N1 per-wall = 3/3/3/2);
  * his actual decoration is tilt-feasible and passes K0-3;
  * it is EXCLUDED by K0-1 (wall-degree-2 squares 0, 2, 5 sit in class 0);
  * it is INCLUDED when K0-1 is dropped (K0-2 in the A58-general form).
Any failure => STOP and report, do not "fix" the filter.

Geometry is EXACT rational: cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2).
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import json
import math
from fractions import Fraction as F

import a88lib as A

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
HALFOFF = [(F(-1, 2), F(-1, 2)), (F(1, 2), F(-1, 2)),
           (F(1, 2), F(1, 2)), (F(-1, 2), F(1, 2))]           # t3lib HALF
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]                     # t3lib NHAT
TOL = F(1, 10 ** 6)


def load():
    d = json.load(open(os.path.join(ROOT, 'certs', 'trump11_certificate.json')))
    s = F(d['side'])
    sq = []
    for q in d['squares']:
        cx, cy, t = F(q['cx']), F(q['cy']), F(q['t'])
        c = (1 - t * t) / (1 + t * t)
        sn = 2 * t / (1 + t * t)
        pts = [(cx + a * c - b * sn, cy + a * sn + b * c) for a, b in HALFOFF]
        phi = 2 * math.atan(float(t)) * 180 / math.pi
        sq.append(dict(c=(cx, cy), t=t, cos=c, sin=sn, pts=pts, phi=phi))
    return s, sq


def edge_normal(q, e):
    nx, ny = NHAT[e]
    return (q['cos'] * nx - q['sin'] * ny, q['sin'] * nx + q['cos'] * ny)


def classify_pair(i, j, sqs):
    """SAT over all 8 edge normals of the two squares.  Returns None if the pair is
    separated by more than TOL, else a dict with
        owner o, edge e of o, hit corners of p, tangential overlap length, kind in
        {'flush','corner-on-edge','corner-corner'}.
    'corner-corner' = two corners of p on the edge LINE but the contact set is a
    single point (overlap 0): a degenerate kiss, NOT in A31's gauge-fixed menu."""
    best = None
    for (o, p) in ((i, j), (j, i)):
        for e in range(4):
            nx, ny = edge_normal(sqs[o], e)
            cox, coy = sqs[o]['c']
            vals = [nx * (qx - cox) + ny * (qy - coy) - F(1, 2)
                    for qx, qy in sqs[p]['pts']]
            mn = min(vals)
            if best is None or mn > best[0]:
                best = (mn, o, p, e, vals)
    mn, o, p, e, vals = best
    if abs(mn) > TOL:
        return None
    hits = [t for t in range(4) if abs(vals[t]) <= TOL]
    nx, ny = edge_normal(sqs[o], e)
    tx, ty = -ny, nx
    co, cp = sqs[o]['pts'], sqs[p]['pts']
    to = [co[e][0] * tx + co[e][1] * ty,
          co[(e + 1) % 4][0] * tx + co[(e + 1) % 4][1] * ty]
    tp = [cp[h][0] * tx + cp[h][1] * ty for h in hits]
    ov = (min(max(to), max(tp)) - max(min(to), min(tp))) if len(tp) >= 2 else F(0)
    if len(hits) >= 2 and ov > TOL:
        kind = 'flush'
    elif len(hits) >= 2:
        kind = 'corner-corner'
    else:
        kind = 'corner-on-edge'
    return dict(o=o, p=p, e=e, hits=hits, overlap=ov, kind=kind, resid=mn)


def derive():
    s, sqs = load()
    k = 11
    # ---- wall masks and wall-contact types
    wm = [0] * k
    swtype = {}
    wres = []
    for i, q in enumerate(sqs):
        xs = [pt[0] for pt in q['pts']]
        ys = [pt[1] for pt in q['pts']]
        for b, (vals, tgt, sgn) in enumerate([(xs, F(0), 1), (ys, F(0), 1),
                                              (xs, s, -1), (ys, s, -1)]):
            d = [sgn * (v - tgt) for v in vals]
            mn = min(d)
            if abs(mn) <= TOL:
                wm[i] |= 1 << b
                hits = [t for t in range(4) if abs(d[t]) <= TOL]
                swtype[(i, b)] = 'WF' if len(hits) >= 2 else 'CW'
                wres.append(dict(sq=i, wall=A.WALL_NAMES[b], n_hits=len(hits),
                                 corners=hits, type=swtype[(i, b)],
                                 residual=float(mn)))
    # ---- square-square contacts
    edges = []
    sstype_raw = {}
    sres = []
    degen = []
    for i in range(k):
        for j in range(i + 1, k):
            c = classify_pair(i, j, sqs)
            if c is None:
                continue
            edges.append((i, j))
            o, p, e = c['o'], c['p'], c['e']
            sres.append(dict(pair=[i, j], kind=c['kind'], owner=o, edge=e,
                             corners=c['hits'], overlap=float(c['overlap']),
                             residual=float(c['resid']),
                             phi=[sqs[i]['phi'], sqs[j]['phi']]))
            if c['kind'] == 'flush':
                # a88lib gauge: the LARGER index owns the flush edge
                e_j = e if o == j else (e + 2) % 4
                sstype_raw[(i, j)] = ('F', e_j)
            elif c['kind'] == 'corner-on-edge':
                hi = sqs[p]['phi'] > sqs[o]['phi']
                sstype_raw[(i, j)] = ('C', o, e, hi)
            else:
                degen.append((i, j))
                sstype_raw[(i, j)] = None
    ss_edges = sorted(edges)
    ss_edges_H = [e for e in ss_edges if sstype_raw[e] is not None]
    dec = A.Decoration(k, ss_edges_H, wm, [sstype_raw[e] for e in ss_edges_H],
                       swtype)
    return dict(s=s, sqs=sqs, wm=wm, ss_edges=ss_edges, ss_edges_H=ss_edges_H,
                degenerate=degen, dec=dec, wall_rows=wres, ss_rows=sres,
                max_resid=max([abs(float(r['residual'])) for r in wres + sres]))


def main():
    d = derive()
    dec = d['dec']
    k = 11
    wm, ss_edges = d['wm'], d['ss_edges']
    rep = {'tolerance': float(TOL), 'max_abs_residual': d['max_resid'],
           'degenerate_corner_corner': [list(e) for e in d['degenerate']],
           'ss_edges_G': [list(e) for e in ss_edges],
           'ss_edges_H': [list(e) for e in d['ss_edges_H']]}
    ss_edges = d['ss_edges_H']
    print('side = %s' % d['s'])
    print('wall masks:', wm)
    print('ACTIVE graph G: %d square-square edges' % len(d['ss_edges']))
    print('DEGENERATE corner-corner kisses (outside the 20-type menu):',
          d['degenerate'])
    print('SUPPORT graph H used for the decoration (%d edges):' % len(ss_edges),
          ss_edges)
    print('wall edges: %d' % sum(A.POP[m] for m in wm))
    perwall = [sum(1 for m in wm if (m >> b) & 1) for b in range(4)]
    print('per-wall degrees L,B,R,T =', perwall)
    print('tilt phi (deg):', ['%.4f' % q['phi'] for q in d['sqs']])
    rep['wall_masks'] = wm
    rep['ss_edges'] = [list(e) for e in ss_edges]
    rep['n_ss'] = len(ss_edges)
    rep['n_sw'] = sum(A.POP[m] for m in wm)
    rep['per_wall'] = perwall
    rep['phi_deg'] = [q['phi'] for q in d['sqs']]
    rep['contacts'] = dict(walls=d['wall_rows'], pairs=d['ss_rows'])

    fG = A.f0_flags(k, d['ss_edges'], wm)
    rep['F0_on_G'] = {a: bool(b) for a, b in fG.items()}
    rep['F0_on_G_pass'] = all(fG.values())
    print('F0 on the ACTIVE graph G (14 edges):', rep['F0_on_G'], '->',
          'PASS' if rep['F0_on_G_pass'] else 'FAIL')
    f = A.f0_flags(k, ss_edges, wm)
    rep['F0'] = {a: bool(b) for a, b in f.items()}
    rep['F0_pass'] = all(f.values())
    print('F0 on the SUPPORT graph H:', rep['F0'], '->',
          'PASS' if rep['F0_pass'] else 'FAIL')

    ts = dec.tilt_system()
    rep['tilt_feasible'] = bool(ts['feasible'])
    rep['tilt'] = {a: (b if a != 'strict' else [list(x) for x in b])
                   for a, b in ts.items() if a != 'reason'}
    print('tilt feasible:', ts['feasible'], ts.get('cls'), 'zero class',
          ts.get('zero_class'))
    ok3, i3 = dec.k0_3(ts)
    rep['K0_3'] = bool(ok3)
    rep['K0_3_info'] = {a: (b if not isinstance(b, tuple) else list(b))
                        for a, b in i3.items()}
    print('K0-3 (Lemma R ruler):', ok3, i3)
    slots = dec.slot_squares()
    rep['slot_squares'] = slots
    rep['K0_1'] = bool(dec.k0_1())
    print('slot squares (2 wall-flush contacts):', slots, ' K0-1 pass:', rep['K0_1'])
    ok2, i2 = A.k0_2(k, ss_edges, wm, general=False)
    ok2g, i2g = A.k0_2(k, ss_edges, wm, general=True, slots=slots)
    rep['K0_2_strict'] = bool(ok2)
    rep['K0_2_strict_info'] = {a: b for a, b in i2.items() if a != 'assign'}
    rep['K0_2_general'] = bool(ok2g)
    rep['K0_2_general_info'] = {a: (b if a != 'assign' else
                                    ({str(x): y for x, y in b.items()} if b else None))
                                for a, b in i2g.items()}
    print('K0-2 strict:', ok2, '  K0-2 A58-general:', ok2g, i2g)

    cnt = dec.counts()
    rep['counts'] = cnt
    print('counts:', cnt)
    rows = dec.rows(ts)
    rep['n_rows'] = len(rows)
    rep['rows'] = rows
    print('t3lib rows: %d (= E + F = %d)' % (len(rows), cnt['m']))

    checks = {
        'C0 F0 passes on the ACTIVE graph G': rep['F0_on_G_pass'],
        'C1 F0 passes': rep['F0_pass'],
        'C2 per-wall degrees are 3/3/3/2': sorted(perwall) == [2, 3, 3, 3],
        'C3 decoration tilt-feasible': rep['tilt_feasible'],
        'C4 decoration passes K0-3': rep['K0_3'],
        'C5 EXCLUDED by K0-1': (not rep['K0_1']),
        'C6 slot squares are exactly {0,2,5}': slots == [0, 2, 5],
        'C7 INCLUDED with K0-1 dropped (A58-general crowding)': rep['K0_2_general'],
        'C8 rows count = m = E + F': len(rows) == cnt['m'],
    }
    rep['checks'] = {a: bool(b) for a, b in checks.items()}
    rep['CANARY'] = 'PASS' if all(checks.values()) else 'FAIL'
    for a, b in checks.items():
        print(('  PASS ' if b else '  FAIL ') + a)
    print('CANARY:', rep['CANARY'])

    p = os.path.join(HERE, '..', 'results', 'canary88.json')
    with open(p, 'w') as fh:
        json.dump(rep, fh, indent=1)
    print('wrote', p)
    return rep


if __name__ == '__main__':
    main()
