"""A255 task 2: the CORPUS TEST of Lemma COMMON-SENSE (before any tree).

For every corner of A244's 489 twelve-stuck rows, A217's 486 witnesses and the ring witnesses (A249
ring2 / ring, A251 joint rings with their poker), in the n-general cell system of the packing's own
side (geo255): the root meeters (squares meeting c00), the wall touchers of c's two walls that meet
c00 or a chain cell of that wall, their SENSES, the class of the corner
    NOT-DOUBLE | COMMON | FLAT+TILT | MIXED | X(45deg)
and, inside the local neighbourhood N_c, every family Pi with |M(Pi)| <= |Pi| (Lemma CELLS reduces
the corner).  A corner that VIOLATES common sense (FLAT+TILT or MIXED) and has NO reducing family in
N_c is LOCALLY STUCK: the counterexample / missing hypothesis the brief asks to draw.

    python sense255.py            -> results/sense255.jsonl, results/sense255_summary.json
"""
import collections
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
for p in ('attempts/A249-type-t-chase/code', 'attempts/A248-corner-chase/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)
import geo255 as G                                                    # noqa: E402

OUT = os.path.join(ATT, 'results', 'sense255.jsonl')
SUM = os.path.join(ATT, 'results', 'sense255_summary.json')


def corpora():
    for name, path in (('A244', 'attempts/A244-twelve-stuck/results/twelve244.jsonl'),
                       ('A217', 'attempts/A217-torque-probe/results/witnesses217.jsonl')):
        for line in open(os.path.join(ROOT, path)):
            r = json.loads(line)
            yield name, r.get('rid') or r.get('wid'), float(r['z'][-1]), G.poses_of_z(r['z'])
    import twotilted249 as W
    import geom248 as G8
    for tag, sym in (('ring2', True), ('ring', False)):
        d = json.load(open(os.path.join(ROOT, 'attempts/A249-type-t-chase/results/twotilted249_%s.json' % tag)))
        for k, v in d.items():
            if v['result']['sup_margin'] > 0:
                polys, _, _ = W.ring_polys(v['result']['x'], float(k), sym)
                yield 'RING', 'A249_%s_%s' % (tag, k), float(k), [G.pose_of_poly(P) for P in polys]
    d = json.load(open(os.path.join(ROOT, 'attempts/A251-ring-pocket/results/joint251.json')))
    for k, v in d.items():
        for i, x in enumerate(v['rings']['x']):
            polys, _, _ = W.ring_polys(x, float(k), False)
            yield 'RING', 'A251_ring%d_%s' % (i, k), float(k), [G.pose_of_poly(P) for P in polys]
        if v['fit1']['sup_margin'] > 0:
            y = v['fit1']['y']
            polys, _, _ = W.ring_polys(y[:16], float(k), False)
            polys = list(polys) + [G8.verts(y[16:19])]
            yield 'RING', 'A251_ring+poker_%s' % k, float(k), [G.pose_of_poly(P) for P in polys]


def corner_record(c, s, poses, table):
    root = table[(c, '00', 0)]
    m = G.m_of(s)
    tch = [G.touches(p[0], p[1], p[2], s) for p in poses]
    sen = [G.sense(p[2]) for p in poses]
    walls = {}
    for kind, wall in (('v', G.WALL_V[c]), ('h', G.WALL_H[c])):
        chain = [(c, '00', 0)] + [(c, kind, j) for j in range(1, m - 2)]
        ids = sorted({i for k in chain for i in table[k] if wall in tch[i]})
        walls[kind] = ids
    members = sorted(set(root) | set(walls['v']) | set(walls['h']))
    ss = [sen[i] for i in members]
    if len(root) < 2:
        cls = 'NOT-DOUBLE'
    elif 'X' in ss:
        cls = 'X45'
    elif 1 in ss and -1 in ss:
        cls = 'MIXED'
    elif 0 in ss and (1 in ss or -1 in ss):
        cls = 'FLAT+TILT'
    elif 0 in ss:
        cls = 'ALL-FLAT'
    else:
        cls = 'COMMON'
    ts = [sen[i] for i in sorted(set(walls['v']) | set(walls['h']))]
    tcls = ('NONE' if not ts else 'X45' if 'X' in ts else 'MIXED' if (1 in ts and -1 in ts) else
            'FLAT+TILT' if (0 in ts and (1 in ts or -1 in ts)) else 'ALL-FLAT' if 0 in ts else 'COMMON')
    level, red = None, None
    for lv in range(4):
        red = G.smallest_reducing(G.scope_cells(c, s, lv), s, table)
        if red is not None:
            level = lv
            break
    rootpat = '+'.join(sorted(('V' if G.WALL_V[c] in tch[i] else '') + ('H' if G.WALL_H[c] in tch[i] else '') or 'free'
                              for i in root))
    return {'corner': c, 'root': root, 'root_touch': rootpat, 'wallV': walls['v'], 'wallH': walls['h'],
            'members': members, 'senses': ss, 'phi': [round(G.phi_deg(poses[i][2]), 4) for i in members],
            'class': cls, 'tclass': tcls if len(root) >= 2 else 'NOT-DOUBLE', 'level': level,
            'reduce': red, 'locally_stuck': level != 0}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tab = collections.defaultdict(collections.Counter)
    tabr = collections.defaultdict(collections.Counter)
    fam = collections.defaultdict(collections.Counter)
    stuck_viol = []
    npack = collections.Counter()
    with open(OUT, 'w') as f:
        for corpus, rid, s, poses in corpora():
            npack[corpus] += 1
            band = corpus + ('<4' if s < 4 - 1e-9 else '>=4')
            table = G.meeter_table(poses, s, G.all_cells(s))
            recs = [corner_record(c, s, poses, table) for c in G.CORNERS]
            for r in recs:
                key = 'L%s' % r['level']
                tab[band][(r['tclass'], key)] += 1
                tabr[band][(r['class'], key)] += 1
                if r['reduce']:
                    fam[band][(r['tclass'], '{' + ','.join(r['reduce'][0]) + '}')] += 1
                if r['locally_stuck'] and r['tclass'] in ('MIXED', 'FLAT+TILT', 'X45'):
                    stuck_viol.append({'corpus': corpus, 'rid': rid, 's': s, **r})
            f.write(json.dumps({'corpus': corpus, 'rid': rid, 's': s, 'm': G.m_of(s), 'n': len(poses),
                                'corners': recs}) + '\n')
    stuck_viol.sort(key=lambda r: r['s'])
    summary = {'packings': dict(npack),
               'table': {b: {'%s|%s' % k: v for k, v in sorted(t.items())} for b, t in tab.items()},
               'table_root_class': {b: {'%s|%s' % k: v for k, v in sorted(t.items())} for b, t in tabr.items()},
               'reducing_family': {b: {'%s|%s' % k: v for k, v in t.most_common()} for b, t in fam.items()},
               'n_locally_stuck_violations': len(stuck_viol), 'locally_stuck_violations': stuck_viol[:200]}
    json.dump(summary, open(SUM, 'w'), indent=1)
    for b, t in summary['table'].items():
        print(b, t)
    print('locally stuck violations:', len(stuck_viol), [(r['rid'], round(r['s'], 5), r['corner'], r['tclass'], r['level'])
                                                          for r in stuck_viol[:12]])


if __name__ == '__main__':
    main()
