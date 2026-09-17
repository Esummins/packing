"""A244 seed families for the twelve-cell crowd search."""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G
import opt217 as O

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def _z(poses, s):
    z = np.zeros(G.NV)
    for i, (x, y, t) in enumerate(poses[:11]):
        z[3 * i], z[3 * i + 1], z[3 * i + 2] = x, y, t
    z[G.S_IDX] = s
    return z


def random_start(rng, S):
    return O.random_start(rng, S=S)


def grid_start(rng, S=4.3):
    """11 of the 16 cells of the 4 x 4 grid, scaled to side S, jittered and tilted."""
    cells = [(i + 0.5, j + 0.5) for i in range(4) for j in range(4)]
    border = [c for c in cells if c[0] in (0.5, 3.5) or c[1] in (0.5, 3.5)]
    inner = [c for c in cells if c not in border]
    keep = list(border) if len(border) <= 11 else [border[k] for k in rng.permutation(len(border))[:11]]
    keep = keep + [inner[k] for k in rng.permutation(len(inner))[:11 - len(keep)]]
    f = S / 4.0
    poses = [(x * f + rng.normal(0, 0.06), y * f + rng.normal(0, 0.06),
              math.radians(rng.uniform(0, 12)) * rng.choice([-1, 1])) for x, y in keep]
    return _z(poses, S)


def corner_triple_start(rng, S=4.3):
    """the count-driven construction: four squares straddling the frame point (1,1) of each corner
    (each meets that corner's three cells), four wall-hugging squares, three free."""
    poses = []
    for (ux, uy) in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        x = 1.0 if ux > 0 else S - 1.0
        y = 1.0 if uy > 0 else S - 1.0
        poses.append((x + rng.normal(0, 0.05), y + rng.normal(0, 0.05),
                      math.radians(rng.uniform(-15, 15))))
    m = S / 2
    for (x, y) in ((m, 0.5), (S - 0.5, m), (m, S - 0.5), (0.5, m)):
        poses.append((x + rng.normal(0, 0.08), y + rng.normal(0, 0.08),
                      math.radians(rng.uniform(-10, 10))))
    for _ in range(3):
        poses.append((rng.uniform(1.2, S - 1.2), rng.uniform(1.2, S - 1.2),
                      rng.uniform(0, math.pi / 2)))
    return O.feasible_start(_z(poses, S))


def ring_starts():
    """A226's rattler rings, A239's window / contact / jutting rings, padded to 11 squares."""
    out = []
    p = os.path.join(ROOT, 'attempts/A239-rings-below-4/results/rings239.jsonl')
    if os.path.exists(p):
        for line in open(p):
            r = json.loads(line)
            out.append((r['label'], [tuple(q) for q in r['poses']], float(r['S'])))
    p = os.path.join(ROOT, 'attempts/A226-one-flush/results/ring11_226.jsonl')
    if os.path.exists(p):
        for k, line in enumerate(open(p)):
            r = json.loads(line)
            if r.get('poses'):
                out.append(('a226_%d' % k, [tuple(q) for q in r['poses']], float(r['S'])))
    return out


def pad_ring(poses, S, rng, grow=0.35):
    """place the missing squares in the middle of a ring widened by `grow`."""
    f = (S + grow) / S
    poses = [(x * f, y * f, t) for x, y, t in poses]
    S2 = S + grow
    while len(poses) < 11:
        poses.append((rng.uniform(1.0, S2 - 1.0), rng.uniform(1.0, S2 - 1.0),
                      rng.uniform(0, math.pi / 2)))
    return O.feasible_start(_z(poses, S2))


def make(kind, rng, S):
    if kind == 'random':
        return random_start(rng, S)
    if kind == 'grid':
        return grid_start(rng, S)
    if kind == 'corner':
        return corner_triple_start(rng, S)
    raise ValueError(kind)
