"""A222 Lemma CELLS / the sweep, exact: for a witness z (geom217 coordinates) the axis cells of the census
(corner frames, offsets 0..2), which squares meet each cell's open interior (SAT, tolerance 1e-9), the
deficiency d(Pi) = |M(Pi)| - |Pi| over families Pi of pairwise interior-disjoint cells containing a corner,
and the PI's perimeter sweep with its bookkeeping (picked up, placed, in hand).  No loads anywhere.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import geom217 as G          # noqa: E402

TOL = 1e-9
CORNERS = ('BL', 'BR', 'TR', 'TL')


# ---------------------------------------------------------------- cells
def cell_box(corner, i, j, s):
    """closed axis box of census cell (corner, i, j) at side s: [x0,x1] x [y0,y1]."""
    if corner == 'BL':
        return (i, i + 1, j, j + 1)
    if corner == 'BR':
        return (s - i - 1, s - i, j, j + 1)
    if corner == 'TR':
        return (s - i - 1, s - i, s - j - 1, s - j)
    return (i, i + 1, s - j - 1, s - j)


def cells_at(s, maxoff=2):
    """all census cells inside the container, deduplicated (two frames giving the same box), as
    dicts {name, corner, i, j, box}."""
    out, seen = [], []
    for c in CORNERS:
        for i in range(maxoff + 1):
            for j in range(maxoff + 1):
                b = cell_box(c, i, j, s)
                if b[0] < -TOL or b[2] < -TOL or b[1] > s + TOL or b[3] > s + TOL:
                    continue
                if any(max(abs(b[k] - bb[k]) for k in range(4)) < 1e-9 for bb in seen):
                    continue
                seen.append(b)
                out.append({'name': '%s(%d,%d)' % (c, i, j), 'corner': c, 'i': i, 'j': j, 'box': b,
                            'is_corner': i == 0 and j == 0})
    return out


def boxes_overlap(a, b):
    return a[0] < b[1] - TOL and b[0] < a[1] - TOL and a[2] < b[3] - TOL and b[2] < a[3] - TOL


def square_meets_box(z, k, box):
    """interior of square k meets the open box (SAT on the 4 axes; touching does not count)."""
    x0, x1, y0, y1 = box
    q = G.corners(z)[k]
    if q[:, 0].max() <= x0 + TOL or q[:, 0].min() >= x1 - TOL:
        return False
    if q[:, 1].max() <= y0 + TOL or q[:, 1].min() >= y1 - TOL:
        return False
    cx, cy, th, s = G.unpack(z)
    c = np.array([cx[k], cy[k]])
    n = G.normals(z)[k]
    bc = np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], float)
    for e in range(4):
        if (n[e] @ (bc - c).T).min() >= 0.5 - TOL:
            return False
    return True


def meeter_masks(z, cells):
    """per cell the bitmask of squares meeting its open interior."""
    masks = []
    for cl in cells:
        m = 0
        for k in range(G.N):
            if square_meets_box(z, k, cl['box']):
                m |= 1 << k
        masks.append(m)
    return masks


# ---------------------------------------------------------------- families (Lemma CELLS)
def min_deficiency(cells, masks, need_corner=True, max_size=4):
    """Families of pairwise interior-disjoint cells containing a corner, enumerated BY SIZE 1..max_size
    (exhaustive at each size); returns the minimum of d = popcount(OR of masks) - |Pi|, the minimiser
    (smallest size first), the best family per size, and the number of families visited.
    d <= 0 <=> Lemma CELLS applies (RAISE(0 -> |Pi|))."""
    n = len(cells)
    ov = [[boxes_overlap(cells[a]['box'], cells[b]['box']) for b in range(n)] for a in range(n)]
    best = {'d': 99, 'family': None, 'M': 0}
    per_size = {}
    count = [0]

    def rec(start, chosen, mask, size):
        if len(chosen) == size:
            count[0] += 1
            if not need_corner or any(cells[a]['is_corner'] for a in chosen):
                d = bin(mask).count('1') - size
                if size not in per_size or d < per_size[size]['d']:
                    per_size[size] = {'d': d, 'family': [cells[a]['name'] for a in chosen], 'M': mask}
                if d < best['d']:
                    best.update(d=d, family=[cells[a]['name'] for a in chosen], M=mask)
            return
        for a in range(start, n):
            if n - a < size - len(chosen) or any(ov[a][b] for b in chosen):
                continue
            rec(a + 1, chosen + [a], mask | masks[a], size)

    for size in range(1, max_size + 1):
        rec(0, [], 0, size)
    return best, per_size, count[0]


def pair_families(cells, masks):
    """corner + one adjacent cell (along either wall): d for each, and whether both are singly met by
    distinct squares (two independent teleports)."""
    out = []
    byname = {c['name']: k for k, c in enumerate(cells)}
    for c in CORNERS:
        a = byname['%s(0,0)' % c]
        for nb in ('%s(1,0)' % c, '%s(0,1)' % c):
            if nb not in byname:
                continue
            b = byname[nb]
            ma, mb = masks[a], masks[b]
            out.append({'corner': c, 'cell': nb, 'M_corner': bin(ma).count('1'), 'M_cell': bin(mb).count('1'),
                        'd': bin(ma | mb).count('1') - 2,
                        'independent': bin(ma).count('1') <= 1 and bin(mb).count('1') <= 1 and (ma & mb) == 0})
    return out


# ---------------------------------------------------------------- the sweep
def perimeter_cycle(s, start='BL', clockwise=False):
    """the perimeter cells in sweep order: corner, then the cells along the wall toward the next corner
    ([k,k+1] for k = 1 .. floor(s)-2 from the start corner's frame), next corner, ...  4*floor(s)-4 cells."""
    L = int(math.floor(s + 1e-9))
    order = ['BL', 'BR', 'TR', 'TL']
    if clockwise:
        order = ['BL', 'TL', 'TR', 'BR']
    k0 = order.index(start)
    order = order[k0:] + order[:k0]
    # the wall from corner a toward corner b, in a's frame: along x if b is the x-neighbour, else along y
    xnb = {'BL': 'BR', 'BR': 'BL', 'TR': 'TL', 'TL': 'TR'}
    out = []
    for t in range(4):
        a, b = order[t], order[(t + 1) % 4]
        out.append((a, 0, 0))
        for k in range(1, L - 1):
            out.append((a, k, 0) if xnb[a] == b else (a, 0, k))
    return out


def window_cycle(start='BL', clockwise=False):
    """the 8-cell window-shaped perimeter in sweep order (one middle per wall, in the frame of the corner the
    sweep leaves): the count of S < 4, applied at every side."""
    order = ['BL', 'BR', 'TR', 'TL'] if not clockwise else ['BL', 'TL', 'TR', 'BR']
    k0 = order.index(start)
    order = order[k0:] + order[:k0]
    xnb = {'BL': 'BR', 'BR': 'BL', 'TR': 'TL', 'TL': 'TR'}
    out = []
    for t in range(4):
        a, b = order[t], order[(t + 1) % 4]
        out.append((a, 0, 0))
        out.append((a, 1, 0) if xnb[a] == b else (a, 0, 1))
    return out


def sweep(z, start='BL', clockwise=False, window=False):
    """the PI's sweep with exact bookkeeping.  Each step: the exposed cell, M_k = remaining squares meeting
    it, the action (place from hand / teleport the single meeter / pick up all and place one), h_k.
    Success (nothing in hand) at the first k with h_k = 0: then Lemma CELLS applies to the prefix."""
    s = float(z[G.S_IDX])
    steps, consumed, h, success = [], 0, 0, None
    cyc = window_cycle(start, clockwise) if window else perimeter_cycle(s, start, clockwise)
    for k, (c, i, j) in enumerate(cyc, 1):
        box = cell_box(c, i, j, s)
        M = [q for q in range(G.N) if not (consumed >> q) & 1 and square_meets_box(z, q, box)]
        if len(M) == 0:
            action = 'place from hand' if h > 0 else 'cell free'
        elif len(M) == 1:
            action = 'teleport %d' % M[0]
        else:
            action = 'pick up %s, place one' % M
        for q in M:
            consumed |= 1 << q
        h = h + len(M) - 1 if (h > 0 or M) else 0
        steps.append({'k': k, 'cell': '%s(%d,%d)' % (c, i, j), 'M': M, 'action': action, 'h': h})
        if h == 0 and success is None:
            success = k
            break
    return {'start': start, 'clockwise': clockwise, 'steps': steps, 'success_at': success,
            'h_final': h, 'consumed': bin(consumed).count('1')}


def best_sweep(z, window=False):
    res = [sweep(z, c, cw, window) for c in CORNERS for cw in (False, True)]
    ok = [r for r in res if r['success_at'] is not None]
    if ok:
        return min(ok, key=lambda r: r['success_at']), res
    return min(res, key=lambda r: r['h_final']), res


def window_family(s):
    """the 8-cell window-shaped perimeter (corner + ONE middle per wall, in the preceding corner's frame),
    used at every side so that the count of the window (S < 4) is tested on witnesses at S >= 4 too."""
    return window_cycle('BL', False)


def window_deficiency(cells, masks):
    """min d over sub-families of the 8 window cells containing a corner (the window's own Lemma CELLS)."""
    names = ['%s(%d,%d)' % c for c in window_family(0)]
    idx = [k for k, c in enumerate(cells) if c['name'] in names]
    sub = [cells[k] for k in idx]
    return min_deficiency(sub, [masks[k] for k in idx])
