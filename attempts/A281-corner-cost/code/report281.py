"""A281: render the computation tables of part 7 from results/wall281_pairs.json, wall281_rings.json, fslots281.json.
    python report281.py  -> prints markdown (appended to notes/cost281_part7.md by hand / by run)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')


def load(name):
    fn = os.path.join(RES, name)
    return json.load(open(fn, encoding='utf-8')) if os.path.exists(fn) else {}


def main():
    pairs, rings, fs = load('wall281_pairs.json'), load('wall281_rings.json'), load('fslots281.json')
    out = ['**7.1 Wall pair types (4 squares, corners BL + TL on the wall x = 0; `wall281 pairs`, 12 restarts).**',
           'sup margin of the least constraint (gaps, containment, box incidences, tilt / offset windows); "exact" = the',
           'rationalised witness passes every check in Fractions.  A negative sup with the constraint set is [M] evidence',
           'of infeasibility; a positive exact witness is [T-computed].', '',
           '  type              s        sup margin  exact   note']
    for k, v in pairs.items():
        name, s = k.split('@')
        note = ''
        if 'thA_TL_deg' in v:
            note = 'TL wall-meeter frame tilt %.2f deg' % v['thA_TL_deg']
        out.append('  %-17s %-8s %+.5f    %-5s   %s' % (name, s, v['sup_margin'], v['exact_ok'], note))
    out += ['', '**7.2 The 8-square outer structures of the 15 D4 orbits (`wall281 rings`, 8 restarts; SIDE only: the eight',
            'meeters, every box doubly met, no free squares).**', '',
            '  orbit           f  walls                                 s         sup margin  exact']
    for k, v in rings.items():
        for s, run in v['runs'].items():
            out.append('  %-15s %d  %-37s %-9s %+.5f    %s%s' % (
                k, v['f'], ' '.join('-'.join(p) for p in v['walls']), s, run['sup_margin'], run['exact_ok'],
                '   (Pi-Pi wall: dead [T])' if v['side_dead_PiPi'] else ''))
    if fs:
        out += ['', '**7.3 F-SLOTS-ONE (`fslots281`): one free square meeting both own slots of an F corner.**']
        for s, v in fs.items():
            out.append('  s = %s: sup margin %+.5f over %d restarts (negative = impossible [M])' % (s, v['sup_margin'], v['restarts']))
    print('\n'.join(out))


if __name__ == '__main__':
    main()
