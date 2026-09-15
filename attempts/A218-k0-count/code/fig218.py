"""A218 pages: the witnesses the count lemma turns on, drawn with A217's force-arrow page.
    python fig218.py
Pages -> docs/residue_map/campaigns/A218-k0-count/count218_<wid>.svg:
  a4065_held   the force-balanced RING: 8 meeters + 1 holder, four 2-crowds, only the tilt bound missing;
  a1344_crowd  the rattler crowd: 7 of 8 meeters carry no load, one crowd row active;
  the K0FREE witness with three 2-crowds (10 squares in the count, side 4.2855);
  the lowest CROWD witness (4.0015).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A217 = os.path.abspath(os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
sys.path.insert(0, A217)
import collect217 as K       # noqa: E402
import fig217 as F           # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A218-k0-count')
RES = os.path.abspath(os.path.join(HERE, '..', 'results'))


def picks():
    """from results/count218.jsonl: the HELD and CROWD four-crowds with the smallest count
    |meeters| + |non-meeter holders| + pulled corners, every K0FREE witness with >= 3 crowds."""
    import collections
    by = collections.defaultdict(list)
    for l in open(os.path.join(RES, 'count218.jsonl')):
        r = json.loads(l)
        by[r['wid']].append(r)
    best = {}
    for wid, rs in by.items():
        cls = rs[0]['cls']
        meet = set(b for r in rs for b in r['meeters'])
        hold = set(h['c'] for r in rs for m in r['members'] for h in m['holders'] if not h['meeter_of'])
        npull = sum(1 for r in rs if any(m['pulls'] for m in r['members']))
        cnt = len(meet) + len(hold) + npull
        if cls in ('HELD', 'CROWD') and len(rs) == 4 and (cls not in best or cnt < best[cls][0]):
            best[cls] = (cnt, wid)
        if cls == 'K0FREE' and len(rs) >= 3:
            best['K0FREE' + wid] = (cnt, wid)
    return {v[1]: k for k, v in best.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    want = picks()
    ws = K.load_witnesses()
    for r in ws:
        r['wid'] = r.get('wid') or r['rid']
    pick = [w for w in ws if w['wid'] in want]
    pick += sorted([w for w in ws if w['cls'] == 'CROWD'], key=lambda w: w['s'])[:1]
    gal = []
    for w in pick:
        t, _ = K.stress_record(w)
        tag = w['wid'].replace('|', '_').replace('/', '_')
        svg = F.page(w, t).replace('A217 %s' % w['wid'], 'A218 (drawn with A217 fig) %s' % w['wid'])
        fn = 'count218_%s_%s.svg' % (w['cls'].lower(), tag)
        open(os.path.join(OUT, fn), 'w').write(svg)
        gal.append((w['wid'], w['cls'], w['s'], w['n2'], fn))
        print('drew', fn, w['cls'], w['s'], 'n2', w['n2'])
    json.dump(gal, open(os.path.join(OUT, 'count218_pages.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
