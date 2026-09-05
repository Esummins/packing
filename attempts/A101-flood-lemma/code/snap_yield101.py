r"""snap_yield101.py -- A101 chore 2: where do A57's certification witnesses sit relative
to the LATTICE CELLS (all four corner lattices, every cell, not only the class's
completable slots), and how many are eta-disturbances of a cell in the sense of Lemma
SNAP (whole box within eta of a cell centre in both coordinates AND tilt within theta_0
of 0 mod 90)?  Extends pocket96 (which tested the 8-9 completable slots only) to
(a) every lattice cell, (b) the 'flush' pattern (ONE coordinate within eta of a cell
coordinate, tilt within theta_0: a square resting against a pin / wall / another
near-cell square but displaced ALONG it), (c) per-cell status (pin / completable-usable
/ completable-unusable / clipped / other).

READ-ONLY on attempts/A57-shadow-trees/certs (witness files as pocket96 read them).
One process, seconds, < 100 MB.  Writes attempts/A101-flood-lemma/results/snap_yield101.json.
"""
from __future__ import annotations

import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import glob
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..', '..'))
CERTS = os.path.join(ATT, 'A57-shadow-trees', 'certs')
OUT = os.path.join(HERE, '..', 'results', 'snap_yield101.json')

PINS = {'k5_11': {('BL', 0, 0), ('BL', 0, 1), ('BL', 1, 0), ('TL', 0, 0), ('BR', 0, 0)},
        'k5_16': {('BL', 0, 0), ('BL', 0, 1), ('TL', 0, 0), ('BR', 0, 0), ('TR', 0, 0)}}
# pocket96 / slots94: completable (Young-ready) and usable (extension dead on the window)
COMPLETABLE = {'k5_11': {('BL', 2, 0), ('BL', 1, 1), ('BL', 0, 2), ('TL', 1, 0), ('TL', 0, 1),
                         ('BR', 1, 0), ('BR', 0, 1), ('TR', 0, 0)},
               'k5_16': {('BL', 1, 0), ('BL', 1, 1), ('BL', 0, 2), ('TL', 1, 0), ('TL', 0, 1),
                         ('BR', 1, 0), ('BR', 0, 1), ('TR', 1, 0), ('TR', 0, 1)}}
USABLE = {'k5_11': {('BL', 1, 1), ('BR', 0, 1), ('TL', 1, 0), ('TR', 0, 0)},
          'k5_16': {('BL', 1, 0), ('BR', 0, 1), ('TR', 0, 1), ('TR', 1, 0)}}
CLIPPED = {'k5_11': {('BL', 0, 2), ('BL', 2, 0), ('BR', 1, 0), ('TL', 0, 1)},
           'k5_16': {('BL', 0, 2), ('TL', 0, 1)}}
CORNERS = ('BL', 'BR', 'TR', 'TL')
ETAS = (0.01, 0.02, 0.05)
THETAS = (1.0, 2.0, 5.0)


def frac(a):
    if isinstance(a, str) and '/' in a:
        n, d = a.split('/')
        return Fraction(int(n), int(d))
    return Fraction(a)


def cell_centre(cn, i, j, m):
    h = Fraction(1, 2)
    if cn == 'BL':
        return (i + h, j + h)
    if cn == 'BR':
        return (m - i - h, j + h)
    if cn == 'TR':
        return (m - i - h, m - j - h)
    return (i + h, m - j - h)


def cells(m):
    out = []
    n = int(math.floor(float(m))) + 1
    for cn in CORNERS:
        for i in range(n):
            for j in range(n):
                if i + 1 <= m and j + 1 <= m:
                    out.append((cn, i, j))
    return out


def tilt_deg_range(t0, t1):
    """theta = 2 atan t; tilt mod 90 = distance to {0, 90}; range over [t0, t1]."""
    a = [2 * math.degrees(math.atan(float(t))) for t in (t0, t1)]
    lo, hi = min(a), max(a)
    # distance of the interval [lo, hi] to {0, 90}: min and max over the interval
    dmin = min(lo, 90 - hi) if lo >= 0 else 0.0
    if lo <= 45 <= hi:
        dmax = 45.0
    else:
        dmax = max(min(x, 90 - x) for x in (lo, hi))
    return dmin, dmax


def status(cls, c):
    if c in PINS[cls]:
        return 'pin'
    if c in USABLE[cls]:
        return 'completable_usable'
    if c in COMPLETABLE[cls] and c in CLIPPED[cls]:
        return 'completable_clipped'
    if c in COMPLETABLE[cls]:
        return 'completable_unusable'
    return 'other'


def main():
    files = sorted(glob.glob(os.path.join(CERTS, '**', '*.witnesses.json'), recursive=True))
    rows = []
    n_files = 0
    for f in files:
        base = os.path.basename(f)
        cls = 'k5_11' if 'k5_11' in base else ('k5_16' if 'k5_16' in base else None)
        if cls is None:
            continue
        group = os.path.relpath(os.path.dirname(f), CERTS).replace('\\', '/')
        try:
            d = json.load(open(f))
        except Exception:
            continue
        wits = d.get('witnesses', d if isinstance(d, list) else [])
        if not wits:
            continue
        m = frac(d.get('s', '969271/250000'))
        cl = cells(m)
        cc = {c: cell_centre(*c, m) for c in cl}
        n_files += 1
        for w in wits:
            b = w.get('box')
            if not b:
                continue
            x0, x1 = (float(frac(v)) for v in b['cx'])
            y0, y1 = (float(frac(v)) for v in b['cy'])
            t0, t1 = (frac(v) for v in b['t'])
            tmin, tmax = tilt_deg_range(t0, t1)
            # per-cell L_inf distance of the WHOLE box (max over the box) and of its midpoint
            best = None
            for c in cl:
                px, py = float(cc[c][0]), float(cc[c][1])
                dx = max(abs(x0 - px), abs(x1 - px))
                dy = max(abs(y0 - py), abs(y1 - py))
                dmax = max(dx, dy)
                if best is None or dmax < best[0]:
                    best = (dmax, dx, dy, c)
            # flush pattern: min over cells of the smaller coordinate distance
            flush = None
            for c in cl:
                px, py = float(cc[c][0]), float(cc[c][1])
                dx = max(abs(x0 - px), abs(x1 - px))
                dy = max(abs(y0 - py), abs(y1 - py))
                dmin = min(dx, dy)
                if flush is None or dmin < flush[0]:
                    flush = (dmin, c)
            rows.append({'file': os.path.relpath(f, CERTS).replace('\\', '/'), 'group': group,
                         'cls': cls, 'kind': w.get('kind', '?'),
                         'tilt_min_deg': tmin, 'tilt_max_deg': tmax,
                         'nearest_cell': '%s%d,%d' % best[3], 'nearest_cell_status': status(cls, best[3]),
                         'Linf_box_to_cell': best[0], 'dx': best[1], 'dy': best[2],
                         'flush_dmin': flush[0], 'flush_cell': '%s%d,%d' % flush[1],
                         'flush_cell_status': status(cls, flush[1])})
    # census
    summ = {'n_witness_files': n_files, 'n_boxes': len(rows),
            'by_kind': dict(Counter(r['kind'] for r in rows)),
            'by_cls_kind': {'%s|%s' % k: v for k, v in Counter((r['cls'], r['kind']) for r in rows).items()},
            'eta_ball': {}, 'flush': {}, 'nearest_status_all_holes': {},
            'distance_percentiles': {}}
    holes = [r for r in rows if r['kind'] == 'hole']
    und = [r for r in rows if r['kind'] != 'hole']
    for name, sub in (('hole', holes), ('undecided', und)):
        ds = sorted(r['Linf_box_to_cell'] for r in sub)
        if ds:
            summ['distance_percentiles'][name] = {
                'n': len(ds), 'min': ds[0], 'p01': ds[len(ds) // 100], 'p05': ds[len(ds) // 20],
                'p10': ds[len(ds) // 10], 'median': ds[len(ds) // 2]}
        tl = sorted(r['tilt_max_deg'] for r in sub)
        if tl:
            summ['distance_percentiles'][name + '_tiltmax'] = {
                'n_le_1deg': sum(1 for x in tl if x <= 1), 'n_le_2deg': sum(1 for x in tl if x <= 2),
                'n_le_5deg': sum(1 for x in tl if x <= 5), 'median': tl[len(tl) // 2]}
    for eta in ETAS:
        for th in THETAS:
            key = 'eta%.2f_th%.0f' % (eta, th)
            cnt = Counter()
            for r in rows:
                if r['Linf_box_to_cell'] <= eta and r['tilt_max_deg'] <= th:
                    cnt[(r['cls'], r['kind'], r['nearest_cell_status'])] += 1
            summ['eta_ball'][key] = {'%s|%s|%s' % k: v for k, v in sorted(cnt.items())}
            cntf = Counter()
            for r in rows:
                if r['flush_dmin'] <= eta and r['tilt_max_deg'] <= th and r['Linf_box_to_cell'] > eta:
                    cntf[(r['cls'], r['kind'], r['flush_cell_status'])] += 1
            summ['flush'][key] = {'%s|%s|%s' % k: v for k, v in sorted(cntf.items())}
    summ['nearest_status_all_holes'] = {'%s|%s' % k: v for k, v in sorted(
        Counter((r['cls'], r['nearest_cell_status']) for r in holes).items())}
    # the eta-ball boxes themselves, listed
    listed = [r for r in rows if r['Linf_box_to_cell'] <= 0.05 and r['tilt_max_deg'] <= 5]
    listed.sort(key=lambda r: r['Linf_box_to_cell'])
    out = {'summary': summ, 'eta_ball_boxes_eta0.05_th5': listed[:400]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), indent=1)
    print(json.dumps(summ, indent=1))
    print('listed', len(listed), 'wrote', OUT)


if __name__ == '__main__':
    main()
