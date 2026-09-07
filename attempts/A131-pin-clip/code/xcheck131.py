"""A131 control C: `pinclip.dead_q` against an INDEPENDENT direct separating-axis computation.

`dead_q` decides "the unit square at centre offset d meets the pin core's interior at EVERY tilt of
the sub-bin" from closed-form sinusoid maxima in exact rational arithmetic.  This checks it against
the brute-force alternative: evaluate the four SAT axes in floats at every tilt of a fine grid over
the sub-bin.  Two failure directions are counted separately:

  UNSOUND   dead_q says dead, but some grid tilt separates      -> must be 0
  MISSED    every grid tilt overlaps, but dead_q says alive     -> conservatism; measured, not required

    python code/xcheck131.py [--samples 40000] [--grid 2001]
"""
import argparse, math, os, random, sys, json
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees", "code")))

import pinclip
from caselp import t_lo, t_hi

A_PIN_F = 0.49


def overlap(dx, dy, th_deg):
    r = math.radians(th_deg)
    c, s = math.cos(r), math.sin(r)
    w = abs(c) + abs(s)
    A = w / 2 + A_PIN_F
    B = 0.5 + A_PIN_F * w
    return (abs(dx) < A and abs(dy) < A and
            abs(dx * c + dy * s) < B and abs(dy * c - dx * s) < B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=40000)
    ap.add_argument("--grid", type=int, default=2001)
    ap.add_argument("--seed", type=int, default=4242)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    n = nT = unsound = missed = 0
    while n < a.samples:
        d0 = rng.uniform(0.0, 89.0)
        d1 = min(90.0, d0 + rng.choice([0.5, 2.0, 7.6, 14.2, 45.0, 90.0 - d0]))
        if d1 <= d0:
            continue
        t0, t1 = t_lo(d0), t_hi(d1)
        o = pinclip.Oct(t0, t1, Fr(49, 100))
        dx = rng.uniform(-1.2, 1.2)
        dy = rng.uniform(-1.2, 1.2)
        dq = pinclip.dead_q(Fr(dx).limit_denominator(10 ** 12),
                            Fr(dy).limit_denominator(10 ** 12), o)
        a0, a1 = pinclip.deg_of_t(t0), pinclip.deg_of_t(t1)
        allov = True
        for i in range(a.grid):
            if not overlap(dx, dy, a0 + (a1 - a0) * i / (a.grid - 1)):
                allov = False
                break
        n += 1
        if dq:
            nT += 1
            if not allov:
                unsound += 1
        elif allov:
            missed += 1
    out = dict(samples=n, dead_true=nT, grid=a.grid, seed=a.seed,
               unsound=unsound, missed=missed, clean=(unsound == 0 and missed == 0))
    json.dump(out, open(os.path.join(BASE, "results", "xcheck131.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
