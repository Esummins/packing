#!/usr/bin/env python3
"""images.py -- compatible Trump images per protected class (exact, at s0), and the
Trump-frame pin subsets.  For class S with pins(S) (slot centres at s0) and each g in D4:
g.trump5 contains pins(S)  <=>  g^{-1}.pins(S) is a subset of trump5's five slots.  The
Trump-frame problem for (S, g) has pin set g^{-1}.pins(S) = a set of Trump square indices.
For classes with NO compatible image: d_min(S) = the smallest sup-norm distance (in
(cx, cy, t)) from a required pin pose (slot, t = 0) to any square of any Trump image,
i.e. the trivial exclusion radius.
"""
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A53-simple-strata', 'code'))
S0 = Fr(969271, 250000)
HALF = Fr(1, 2)
TRUMP_SLOT_SQ = {(HALF, HALF): 0, (Fr(3, 2), HALF): 1, (HALF, Fr(3, 2)): 3,
                 (S0 - HALF, HALF): 2, (S0 - HALF, S0 - HALF): 5}


def d4_elements():
    """the 8 maps as (rot, refl) with the A53 convention: rot: (a,b)->(b, S0-a) repeated;
    refl: a -> S0 - a."""
    return [(rot, refl) for rot in range(4) for refl in (False, True)]


def apply(g, p):
    rot, refl = g
    a, b = p
    for _ in range(rot):
        a, b = b, S0 - a
    if refl:
        a = S0 - a
    return (a, b)


def inverse_apply(g, p):
    # brute force: find q with apply(g, q) == p among the slot grid ... use algebra: refl then rot^-1
    rot, refl = g
    a, b = p
    if refl:
        a = S0 - a
    for _ in range(rot):
        a, b = S0 - b, a      # inverse of (a,b)->(b, S0-a)
    return (a, b)


def main():
    spec = json.load(open(os.path.join(HERE, '..', '..', 'A65-low-k-closure', 'results',
                                       'h10_boxspec.json')))
    # Trump's full pose list at s0 (centres, t) from the tight certificate scaled? use A22 z0 in t
    z = json.load(open(os.path.join(HERE, '..', 'results', 'z0_t.json')))['z0_t']
    z = [Fr(x) for x in z]
    shat = z[33]
    poses = []
    for i in range(11):
        # scale centres to s0 frame by the affine slot convention is not needed for d_min
        # (both frames agree to 1e-7); use s0-frame slots exactly and Trump centres at shat.
        poses.append((z[3 * i], z[3 * i + 1], z[3 * i + 2]))
    out = {}
    for cls, v in spec['classes'].items():
        pins = [(Fr(p[0]), Fr(p[1])) for p in v['pins']]
        images = []
        for g in d4_elements():
            pre = [inverse_apply(g, p) for p in pins]
            if all(q in TRUMP_SLOT_SQ for q in pre):
                images.append({'g': g, 'trump_squares': sorted(TRUMP_SLOT_SQ[q] for q in pre)})
        # d_min for the trivial exclusion (over all images): for each image g, each pin p,
        # distance from pin pose (p, t=0) to the nearest g-image of a Trump square.
        # d_min = min over images g of [max over pins p of (distance from the pin pose (slot,
        # t=0) in Trump's frame to the nearest Trump square)]: within d_min of ANY image, some
        # required pin cannot be realised. 0 iff a compatible image exists.
        dmin = None
        for g in d4_elements():
            dg = Fr(0)
            for p in pins:
                q = inverse_apply(g, p)   # pin slot in Trump's frame
                best = None
                for (cx, cy, t) in poses:
                    # upright test: t = 0 and t = 1 are the same square mod pi/2
                    tt = min(abs(t), abs(1 - t))
                    dist = max(abs(cx - q[0]), abs(cy - q[1]), tt)
                    if best is None or dist < best:
                        best = dist
                dg = max(dg, best)
            if dmin is None or dg < dmin:
                dmin = dg
        if dmin is None:
            dmin = Fr(0)
        out[cls] = {'k': v['k'], 'pins': [[str(p[0]), str(p[1])] for p in pins],
                    'n_images': len(images),
                    'trump_frame_pinsets': sorted(set(tuple(im['trump_squares']) for im in images)),
                    'images': [{'rot': im['g'][0], 'refl': im['g'][1], 'trump_squares': im['trump_squares']} for im in images],
                    'd_min_trivial': '%d/%d' % (dmin.numerator, dmin.denominator), 'd_min_float': float(dmin)}
        print('%s k=%d images=%d trump-frame pin sets=%s d_min=%.4g'
              % (cls, v['k'], len(images), out[cls]['trump_frame_pinsets'], float(dmin)))
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'images.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
