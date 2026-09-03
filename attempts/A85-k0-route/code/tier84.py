#!/usr/bin/env python3
"""tier84.py -- the 16 protected classes: compatible Trump images G_S, Trump-frame pin sets I_g
(the tube directions), A_S = max|alpha| (the Lemma B' drift constant), T_K(delta_pin).

Exact rationals throughout (pins from A65 h10_boxspec.json; Trump's five simple squares at
slots(s) -- the census is s-stable, so the image test is a slot-pattern test, done at s0).
Writes results/tier84_classes.json.  Read-only elsewhere.
"""
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SPEC = os.path.join(ROOT, 'attempts', 'A65-low-k-closure', 'results', 'h10_boxspec.json')
OUT = os.path.join(HERE, '..', 'results', 'tier84_classes.json')

S0 = F(969271, 250000)
SHAT = 3.877083590022814
H = F(1, 2)
# Trump's simple squares in A03/A22 indexing: (alpha_x, beta_x, alpha_y, beta_y), slot = alpha + beta*s
TRUMP_SIMPLE = {0: (H, 0, H, 0), 1: (F(3, 2), 0, H, 0), 2: (-H, 1, H, 0), 3: (H, 0, F(3, 2), 0),
                5: (-H, 1, -H, 1)}
SYMS = ['id', 'xflip', 'yflip', 'rot180', 'transpose', 'rot90', 'rot270', 'antitranspose']


def apply(k, x, y, s):
    """crowdfam.symmetry: bit0 x-flip, bit1 y-flip, bit2 transpose (applied in that order)."""
    if k & 1:
        x = s - x
    if k & 2:
        y = s - y
    if k & 4:
        x, y = y, x
    return x, y


def alpha_of(v):
    """|alpha| of a slot coordinate at s0 (L-family: v; R-family: s0 - v)."""
    return min(abs(v), abs(S0 - v))


def main():
    spec = json.load(open(SPEC))
    out = {}
    for name, cl in spec['classes'].items():
        pins = [(F(p[0]), F(p[1])) for p in cl['pins']]
        images = []
        for k in range(8):
            img = {}
            for i, (ax, bx, ay, by) in TRUMP_SIMPLE.items():
                img[i] = apply(k, ax + bx * S0, ay + by * S0, S0)
            inv = {v: i for i, v in img.items()}
            if all(p in inv for p in pins):
                images.append(dict(sym=k, sym_name=SYMS[k], trump_frame_pins=sorted(inv[p] for p in pins)))
        A = max([alpha_of(c) for p in pins for c in p], default=F(0))
        d = F(2, 100)
        TK = None if A == 0 else ((d / A) * F(SHAT).limit_denominator(10 ** 12) - (S0 - F(SHAT).limit_denominator(10 ** 12))) / (1 + d / A)
        out[name] = dict(k=cl['k'], N=cl['N'], pins=[[str(a), str(b)] for a, b in pins],
                         A_S=str(A), A_S_float=float(A),
                         T_K_delta_2e_2=(float(TK) if TK is not None else None),
                         images=images, n_images=len(images),
                         distinct_trump_frame_pin_sets=sorted({tuple(im['trump_frame_pins']) for im in images}))
    json.dump(out, open(OUT, 'w'), indent=1)
    for name, r in out.items():
        print('%-6s k=%d N=%2d A=%-4s T_K(2e-2)=%s images=%s I_g=%s'
              % (name, r['k'], r['N'], r['A_S'], ('%.4f' % r['T_K_delta_2e_2']) if r['T_K_delta_2e_2'] is not None else 'inf',
                 [im['sym_name'] for im in r['images']], r['distinct_trump_frame_pin_sets']))


if __name__ == '__main__':
    main()
