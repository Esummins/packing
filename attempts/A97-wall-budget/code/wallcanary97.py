"""wallcanary97.py -- A97 Lemma WALL canary on exact Trump (A03 60-digit data).

For each wall w of Trump's packing (side s = s-hat), with the wall frame y = 0 and the
FOOTPRINT LINE at height h0 = 1/sqrt2, compute for every square:
  * y_min (distance of the square's lowest point from w), whether it touches w,
  * tilt (dist to 90 deg Z), 1/cos(tilt) (the footprint of a wall-toucher),
  * cos+sin (the projection width -- NOT a valid disjoint footprint, see wall_budget.md 1.3),
  * the exact chord of the square's interior on the footprint line (its footprint phi_w),
and report the per-wall sums against Lemma WALL-F: sum_Q phi_w(Q) <= s, and the count of
wall-touchers (<= 3), and the slack s - sum.

Also checks Lemma WALL-F at the two alternative heights 1/2 (A91's chord lemma) and 1
to show 1/sqrt2 is the dominant choice on Trump.

One process, OMP_NUM_THREADS=1 (no BLAS used; mpmath only).  Writes only
attempts/A97-wall-budget/results/trump_wall_canary.{json,md}.
"""
from __future__ import annotations
import os, sys, json
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_v] = '1'
import mpmath as mp

mp.mp.dps = 70
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'attempts', 'A03-upper-reconstruct', 'trump11_exact.json')
OUT = os.path.join(HERE, '..', 'results')
os.makedirs(OUT, exist_ok=True)

d = json.load(open(SRC, encoding='utf-8'))
s = mp.mpf(d['s'])
sq = [(mp.mpf(q['cx']), mp.mpf(q['cy']), mp.mpf(q['theta'])) for q in d['squares']]
TOL = mp.mpf('1e-40')
H0 = 1 / mp.sqrt(2)
HALF = mp.mpf(1) / 2


def verts(cx, cy, th):
    c, sn = mp.cos(th), mp.sin(th)
    out = []
    for (u, v) in ((-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF)):
        out.append((cx + u * c - v * sn, cy + u * sn + v * c))
    return out


def tilt(th):
    t = th % (mp.pi / 2)
    return min(t, mp.pi / 2 - t)


def chord(poly, h):
    """[xmin, xmax] of the convex polygon's intersection with the line y = h (interior
    chord if the line crosses the polygon's interior; returns 0 length otherwise)."""
    xs = []
    n = len(poly)
    for k in range(n):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % n]
        if (y1 - h) * (y2 - h) < 0:
            t = (h - y1) / (y2 - y1)
            xs.append(x1 + t * (x2 - x1))
        elif abs(y1 - h) <= TOL:
            xs.append(x1)
    if len(xs) < 2:
        return mp.mpf(0)
    ymin = min(p[1] for p in poly); ymax = max(p[1] for p in poly)
    if not (ymin < h - TOL and ymax > h + TOL):
        return mp.mpf(0)          # line only touches the boundary: interior chord empty
    return max(xs) - min(xs)


# wall frames: map container coordinates so that wall w becomes y = 0
FRAMES = {
    'bottom (y=0)': lambda x, y: (x, y),
    'left (x=0)':   lambda x, y: (y, x),
    'right (x=s)':  lambda x, y: (y, s - x),
    'top (y=s)':    lambda x, y: (x, s - y),
}

report = {'s': str(s), 'h0': str(H0), 'walls': {}}
lines = ['# Trump wall canary (exact, 70 dps) -- Lemma WALL-F on every wall', '',
         f's = {mp.nstr(s, 20)}, footprint line h0 = 1/sqrt2 = {mp.nstr(H0, 12)}', '']
for wname, fr in FRAMES.items():
    rows = []
    tot = {str(h): mp.mpf(0) for h in (H0, HALF, mp.mpf(1))}
    ntouch = 0
    for i, (cx, cy, th) in enumerate(sq):
        poly = [fr(x, y) for (x, y) in verts(cx, cy, th)]
        ymin = min(p[1] for p in poly)
        touch = ymin <= TOL
        tl = tilt(th)
        r = {'sq': i, 'y_min': mp.nstr(ymin, 12), 'touches': bool(touch),
             'tilt_deg': mp.nstr(tl * 180 / mp.pi, 10),
             'inv_cos': mp.nstr(1 / mp.cos(tl), 12),
             'proj_width': mp.nstr(mp.cos(tl) + mp.sin(tl), 12)}
        for h in (H0, HALF, mp.mpf(1)):
            c = chord(poly, h)
            r['phi_h%s' % mp.nstr(h, 6)] = mp.nstr(c, 12)
            tot[str(h)] += c
        if touch:
            ntouch += 1
        if touch or ymin < 1:
            rows.append(r)
    slack = s - tot[str(H0)]
    report['walls'][wname] = {'n_touch': ntouch, 'sum_phi_h0': mp.nstr(tot[str(H0)], 20),
                              'sum_phi_half': mp.nstr(tot[str(HALF)], 20),
                              'sum_phi_1': mp.nstr(tot[str(mp.mpf(1))], 20),
                              'slack_h0': mp.nstr(slack, 20),
                              'pass': bool(tot[str(H0)] <= s and ntouch <= 3), 'rows': rows}
    lines.append(f'## {wname}: touchers {ntouch} (<= 3 {"OK" if ntouch <= 3 else "FAIL"}); '
                 f'sum phi(h0) = {mp.nstr(tot[str(H0)], 10)} <= s: '
                 f'{"OK" if tot[str(H0)] <= s else "FAIL"}, slack {mp.nstr(slack, 8)}; '
                 f'[sum at h=1/2: {mp.nstr(tot[str(HALF)], 8)}; at h=1: {mp.nstr(tot[str(mp.mpf(1))], 8)}]')
    lines.append('')
    lines.append('| sq | y_min | touches | tilt deg | 1/cos | cos+sin | phi(h0) | phi(1/2) | phi(1) |')
    lines.append('|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        f6 = lambda v: mp.nstr(mp.mpf(v), 6)
        lines.append(f"| {r['sq']} | {f6(r['y_min'])} | {r['touches']} | {f6(r['tilt_deg'])} | "
                     f"{f6(r['inv_cos'])} | {f6(r['proj_width'])} | {f6(r['phi_h0.707107'])} | "
                     f"{f6(r['phi_h0.5'])} | {f6(r['phi_h1.0'])} |")
    lines.append('')

allpass = all(w['pass'] for w in report['walls'].values())
report['PASS'] = allpass
lines.append(f'**Lemma WALL-F on all four walls: {"PASS" if allpass else "FAIL"}.**')
json.dump(report, open(os.path.join(OUT, 'trump_wall_canary.json'), 'w'), indent=1)
open(os.path.join(OUT, 'trump_wall_canary.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
