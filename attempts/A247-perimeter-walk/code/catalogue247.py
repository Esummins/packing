"""A247 task 1 -- the CATALOGUE: every subset of the twelve cells a single unit square can meet.

  (i)  Necessity [T] (PROJECTION): a square meeting two cells whose along-wall intervals are
       (0,1) and (s-1,s) has extent > s - 2 > sqrt2 in that coordinate.  Hence a realisable set
       lies in some N_c = the five ring cells centred at c00.  Every minimal set outside the
       N_c (a pair of cells) is ALSO certified infeasible by the single-square B&B, on the
       window [3.82, s-hat] and on the corpus range [3.82, 4.4].
  (ii) Sufficiency: every subset of N_c has an exactly verified witness at s in the window
       (a MEETER set contains c00; a FREE set avoids all four boxes -- the box-avoiding
       realisability is the non-trivial part: {c01, c10} without c00 needs the diagonal pose).
  (iii) Pose conditions: for each set, the tilt bins (5 deg) in which it is realisable.
  (iv) The corpus check: every square of the 282 + 34 twelve-stuck packings has its cell-set
       (meeting depth > 0 and > 1e-5) inside some N_c, and, when it meets no box, in the
       free catalogue.
    python catalogue247.py [--bins 18] -> results/catalogue247.jsonl, results/catalogue247.md
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import bb247 as B
import geo247 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A246-construct-towards', 'code'))
WINDOW = (G.S_LO, G.SHAT)
CORPUS = (G.S_LO, 4.4)


def single(spec, s_range, theta=None, eta=1e-3, budget=400_000):
    p = B.problem_of([spec], s_range, eta=eta)
    if theta is not None:
        p['squares'][0]['theta'] = theta
    r = B.solve(p, hmin=1e-5, budget_boxes=budget)
    return r


def minimal_bad_pairs():
    out = []
    for a, b in itertools.combinations(G.RING, 2):
        if not G.in_some_nbr((a, b)):
            out.append((a, b))
    return out


def d4_orbit_key(cells):
    keys = []
    for m in G.D4:
        keys.append(tuple(sorted(m[c] for c in cells)))
    return min(keys)


def witness_row(r):
    if not r['witness']:
        return None
    w = r['witness']
    return {'s': w['s'], 'pose': w['poses'][0], 'exact': w['exact']}


def corpus_packings():
    import check246 as K
    return K.corpus_282() + K.certified_34()


def corpus_check(free_ok):
    rows = []
    bad = []
    for rid, z, kind in corpus_packings():
        s = float(z[33])
        for i in range(11):
            pose = (float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2]))
            for tol in (0.0, 1e-5):
                cells = G.cells_met_pt(pose, s, tol)
                if not cells:
                    continue
                boxes = [c for c in cells if c.endswith('00')]
                in_nbr = G.in_some_nbr(cells)
                in_free = (not boxes) and (G.canon_cells(cells) in free_ok)
                if not in_nbr or (not boxes and not in_free):
                    bad.append((rid, i, tol, cells))
                rows.append((rid, i, tol, len(cells), bool(boxes)))
    return rows, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bins', type=int, default=18)
    ap.add_argument('--eta', type=float, default=1e-3)
    a = ap.parse_args()
    t0 = time.time()
    out = []
    # (i) necessity: the minimal sets outside every N_c
    bad_pairs = minimal_bad_pairs()
    nec = []
    for pr in bad_pairs:
        for rng_name, rng in (('window', WINDOW), ('corpus', CORPUS)):
            r = single(('P', pr), rng, eta=0.0)
            nec.append({'pair': pr, 'range': rng_name, 'status': r['status'], 'boxes': r['processed']})
    out.append({'kind': 'necessity', 'n_bad_pairs': len(bad_pairs), 'results': nec,
                'all_infeasible': all(x['status'] == 'INFEASIBLE' for x in nec)})
    # (ii)+(iii) sufficiency with tilt bins
    bins = [(k * math.pi / 2 / a.bins, (k + 1) * math.pi / 2 / a.bins) for k in range(a.bins)]
    free_ok = set()
    for kind, sets in (('M', G.meeter_sets('BL')), ('F', G.free_sets())):
        for cells in sets:
            spec = ('M', 'BL', cells) if kind == 'M' else ('F', cells)
            r = single(spec, WINDOW, eta=a.eta)
            tilt = []
            for b in bins:
                rb = single(spec, WINDOW, theta=b, eta=a.eta, budget=150_000)
                tilt.append(rb['status'][0])
            row = {'kind': kind, 'cells': list(cells), 'orbit': list(d4_orbit_key(cells)),
                   'status': r['status'], 'boxes': r['processed'], 'witness': witness_row(r),
                   'tilt_bins_deg': ''.join(tilt), 'bin_deg': 90.0 / a.bins}
            out.append(row)
            if kind == 'F' and r['status'] == 'FEASIBLE':
                free_ok.add(G.canon_cells(cells))
            print('%s %-40s %-10s %s' % (kind, '+'.join(cells), r['status'], ''.join(tilt)), flush=True)
    # (iv) corpus
    rows, bad = corpus_check(free_ok)
    out.append({'kind': 'corpus', 'squares_checked': len(rows), 'violations': [list(map(str, b)) for b in bad],
                'max_cells': max(r[3] for r in rows)})
    os.makedirs(os.path.join(ATT, 'results'), exist_ok=True)
    with open(os.path.join(ATT, 'results', 'catalogue247.jsonl'), 'w') as f:
        for row in out:
            f.write(json.dumps(row) + '\n')
    n_m = sum(1 for r in out if r.get('kind') == 'M')
    n_f = sum(1 for r in out if r.get('kind') == 'F')
    fe_m = sum(1 for r in out if r.get('kind') == 'M' and r['status'] == 'FEASIBLE')
    fe_f = sum(1 for r in out if r.get('kind') == 'F' and r['status'] == 'FEASIBLE')
    orb_m = len({tuple(r['orbit']) for r in out if r.get('kind') == 'M'})
    orb_f = len({tuple(r['orbit']) for r in out if r.get('kind') == 'F'})
    L = ['# A247 -- the catalogue of realisable cell-sets (generated by `code/catalogue247.py`, %.0f s)' % (time.time() - t0), '',
         '* necessity: %d minimal cell pairs outside every N_c, all certified INFEASIBLE by the single-square B&B '
         '(eta = 0, window and corpus range): %s' % (len(bad_pairs), out[0]['all_infeasible']),
         '* meeter sets at BL ({BL00} + subset of its 4 slots): %d, realisable %d (%d D4 orbits); free sets (box-avoiding, '
         'inside a window): %d, realisable %d (%d D4 orbits); eta = %g' % (n_m, fe_m, orb_m, n_f, fe_f, orb_f, a.eta),
         '* corpus: %d (square, tol) pairs checked over the 282 + 34 packings, violations %d, max cells %d' % (
             len(rows), len(bad), max(r[3] for r in rows)), '',
         '| kind | cells | status | tilt bins (%.0f deg each, F = realisable) | witness (s; cx, cy, tilt) |' % (90.0 / a.bins),
         '|---|---|---|---|---|']
    for r in out:
        if r.get('kind') in ('M', 'F'):
            w = r['witness']
            ws = '%.4f; %.3f, %.3f, %.1f deg' % (w['s'], w['pose'][0], w['pose'][1], math.degrees(w['pose'][2])) if w else ''
            L.append('| %s | %s | %s | `%s` | %s |' % (r['kind'], ' '.join(r['cells']), r['status'], r['tilt_bins_deg'], ws))
    with open(os.path.join(ATT, 'results', 'catalogue247.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L[:5]))


if __name__ == '__main__':
    main()
