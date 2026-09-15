"""A222 tests: the cell meeting test against geom217.meets_box on the corner cells; Lemma CELLS on a settled
packing; every exchanged configuration in swap222.jsonl is a packing at the witness's side (the frozen SAT / wall check)
and contains the claimed slot squares.    python test222.py"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cells222 as C          # noqa: E402
import region222 as RG        # noqa: E402
import raise222 as R          # noqa: E402
import geom217 as G           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))


def test_meeting_vs_geom217():
    ws = R.load(True)[:60]
    for w in ws:
        z = np.array(w['z'], float)
        s = float(z[G.S_IDX])
        for c in C.CORNERS:
            box = C.cell_box(c, 0, 0, s)
            mine = [q for q in range(G.N) if C.square_meets_box(z, q, box)]
            ref = G.corner_meeters(z, c)
            assert mine == ref, (w['wid'], c, mine, ref)
    print('meeting test = geom217.meets_box on %d witnesses x 4 corners' % len(ws))


def test_cells_on_settled():
    # a packing with a slot square at BL: the family {BL(0,0)} is met by that square only -> d = 0
    ws = [w for w in R.load(True) if w['settled']['BL'] is not None][:5]
    for w in ws:
        z = np.array(w['z'], float)
        cells = C.cells_at(float(z[G.S_IDX]))
        masks = C.meeter_masks(z, cells)
        k = [i for i, c in enumerate(cells) if c['name'] == 'BL(0,0)'][0]
        assert masks[k] == 1 << w['settled']['BL'], (w['wid'], bin(masks[k]))
    print('settled corner: the corner cell is met by its slot square only (%d witnesses)' % len(ws))


def test_swapped_are_packings():
    path = os.path.join(ATT, 'results', 'swap222.jsonl')
    if not os.path.exists(path):
        print('no swap222.jsonl yet')
        return
    n = 0
    for l in open(path, encoding='utf-8'):
        r = json.loads(l)
        for name, sr in r['searches'].items():
            if not sr.get('z_swapped'):
                continue
            z = np.array(sr['z_swapped'], float)
            assert abs(float(z[G.S_IDX]) - r['s']) < 1e-12
            ok, gap, wall = RG.exact_check(z)
            assert ok, (r['wid'], name, gap, wall)
            for c in sr['settled']:
                assert G.settled(z, c) is not None, (r['wid'], name, c)
            n += 1
    print('%d exchanged configurations are packings at the witness side with the claimed slot squares' % n)


if __name__ == '__main__':
    test_meeting_vs_geom217()
    test_cells_on_settled()
    test_swapped_are_packings()
