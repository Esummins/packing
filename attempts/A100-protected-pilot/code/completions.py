"""A59 side task: the eight one-cell Young completions of trump5 (theory.md T2.1),
matched exactly (Fractions) against A53's k = 6 census up to D4."""
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A53 = os.path.join(HERE, '..', '..', 'A53-simple-strata', 'results')
RES = os.path.join(HERE, '..', 'results')

S = F(969271, 250000)

TRUMP5 = [(F(1, 2), F(1, 2)), (F(3, 2), F(1, 2)), (F(1, 2), F(3, 2)),
          (S - F(1, 2), F(1, 2)), (S - F(1, 2), S - F(1, 2))]

COMPLETIONS = [
    ('BL+(2,0)', (F(5, 2), F(1, 2))),
    ('BL+(1,1)', (F(3, 2), F(3, 2))),
    ('BL+(0,2)', (F(1, 2), F(5, 2))),
    ('BR+(1,0)', (S - F(3, 2), F(1, 2))),
    ('BR+(0,1)', (S - F(1, 2), F(3, 2))),
    ('TR+(1,0)', (S - F(3, 2), S - F(1, 2))),
    ('TR+(0,1)', (S - F(1, 2), S - F(3, 2))),
    ('TL+(0,0)', (F(1, 2), S - F(1, 2))),
]

D4 = [
    ('id',      lambda x, y: (x, y)),
    ('rot90',   lambda x, y: (S - y, x)),
    ('rot180',  lambda x, y: (S - x, S - y)),
    ('rot270',  lambda x, y: (y, S - x)),
    ('refl_x',  lambda x, y: (S - x, y)),          # mirror in the vertical mid-line
    ('refl_y',  lambda x, y: (x, S - y)),
    ('refl_d',  lambda x, y: (y, x)),              # main diagonal
    ('refl_ad', lambda x, y: (S - y, S - x)),
]


def disjoint(slots):
    """Exact pairwise interior-disjointness of unit squares at the given centres."""
    bad = []
    for i in range(len(slots)):
        for j in range(i + 1, len(slots)):
            dx = abs(slots[i][0] - slots[j][0])
            dy = abs(slots[i][1] - slots[j][1])
            if dx < 1 and dy < 1:
                bad.append((i, j, str(dx), str(dy)))
    return (not bad), bad


def load_k6():
    d = json.load(open(os.path.join(A53, 'skeletons_young.json')))
    cls = [c for c in d['classes'] if c['k'] == 6]
    n2s = json.load(open(os.path.join(A53, 'name_to_slots.json')))
    names = sorted(k for k in n2s if k.startswith('k6_'))
    assert len(cls) == len(names) == 33, (len(cls), len(names))
    out = []
    for i, c in enumerate(cls):
        # verify the index<->name correspondence via the float coordinates
        a = sorted(tuple(round(v, 6) for v in p) for p in c['slots_float'])
        b = sorted(tuple(round(v, 6) for v in p) for p in n2s[names[i]])
        assert a == b, (names[i], a, b)
        out.append((names[i], frozenset((F(p[0]), F(p[1])) for p in c['slots'])))
    return out


def main():
    k6 = load_k6()
    rows = []
    for name, cell in COMPLETIONS:
        slots = TRUMP5 + [cell]
        ok, bad = disjoint(slots)
        row = dict(completion=name,
                   added_cell=[str(cell[0]), str(cell[1])],
                   slots=[[str(a), str(b)] for a, b in slots],
                   slots_float=[[float(a), float(b)] for a, b in slots],
                   pairwise_disjoint=ok)
        if not ok:
            row.update(k6_class=None, d4_op=None,
                       note='slot squares OVERLAP for every s in (3.82, s0] '
                            '(gap = s-3 < 1): not a Young 4-tuple with disjoint '
                            'slot squares, so no packing realizes it and the '
                            'completion is vacuously killed',
                       overlaps=bad)
        else:
            hit = None
            for op, f in D4:
                img = frozenset(f(x, y) for x, y in slots)
                for cname, cs in k6:
                    if img == cs:
                        hit = (cname, op)
                        break
                if hit:
                    break
            assert hit is not None, 'completion %s matched no k6 class' % name
            row.update(k6_class=hit[0], d4_op=hit[1], note='')
        rows.append(row)
    with open(os.path.join(RES, 'completions.json'), 'w') as fh:
        json.dump(rows, fh, indent=1)
    for r in rows:
        print('%-10s -> %-7s d4=%-8s %s' % (r['completion'], r['k6_class'],
                                            r['d4_op'], r['note'][:60]))
    return rows


if __name__ == '__main__':
    main()
