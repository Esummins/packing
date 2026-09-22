"""A263 (d) the SLAB jobs for A261's LP-certificate engine (cert261 / verify261 / price261 imported, never edited):
the tilt domain [0, 45 deg]^4 minus A261's [TMIN, 45 deg]^4, per pattern, as the 15 boxes  [0, TMIN]^S x [TMIN, 1]^(rest)
(S a nonempty set of walls), reduced by the pattern's symmetries.  On [0, TMIN] the near-flat wall's forms stay
ADMISSIBLE (cert261.admissible: only an exactly-flat domain drops them) -- a RELAXATION of the true condition (at tilt 0
the flat square owns no axis), hence SOUND.  The engine's interval bounds (ivl261.wall) are monotone on [0, 45 deg].
Job names  S<pattern>_<walls>  e.g. SM1_3 (wall 3 in the slab), SM1_03, SR3222_pppp_0.
Everything is written to attempts/A263-open-pairs/certs/ (never A261's).
    python slabjobs263.py list | price JOB NSAMP | run JOB [SECONDS] | verify JOB"""
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
sys.dont_write_bytecode = True
import cert261 as C                                                   # noqa: E402
import verify261 as V                                                 # noqa: E402

CERTS = os.path.join(HERE, '..', 'certs')
STOP = os.path.join(HERE, '..', 'logs', 'STOP')
TMIN = C.TMIN


def canon(sg, l, S):
    """canonical key of (senses, lengths, slab set) under rotation and reflection."""
    orb = set()
    n = 4
    for r in range(n):
        lr, sr = tuple(l[r:] + l[:r]), tuple(sg[r:] + sg[:r])
        Sr = tuple(sorted((w - r) % n for w in S))
        orb.add((lr, sr, Sr))
        lf, sf = lr[::-1], tuple(-v for v in sr[::-1])
        Sf = tuple(sorted((n - 1 - w) % n for w in Sr))
        orb.add((lf, sf, Sf))
    return min(orb)


def slab_jobs():
    base = C.jobs()
    out, seen = {}, set()
    for name, (sg, l, dom) in base.items():
        if name.startswith('F'):
            continue
        for k in range(1, 5):
            for S in itertools.combinations(range(4), k):
                key = canon(list(sg), list(l), S)
                if key in seen:
                    continue
                seen.add(key)
                td = [[0.0, TMIN] if w in S else [TMIN, 1.0] for w in range(4)]
                out['S%s_%s' % (name, ''.join(map(str, S)))] = (tuple(sg), tuple(l), td)
    return out


def price(name, ns):
    sg, l, dom = slab_jobs()[name]
    job = dict(senses=list(sg), lengths=list(l), tdomain=dom)
    rng = np.random.default_rng(7)
    vol = float(np.prod([b - a for a, b in dom]))
    inv, ks, t0, feas = [], [], time.time(), 0
    for _ in range(ns):
        t = [rng.uniform(a, b) for a, b in dom]
        rows, k = [], 2
        while k <= 18:
            h = 2.0 ** -k
            box = tuple((max(a, v - h), min(b, v + h)) for v, (a, b) in zip(t, dom))
            leaf, f, rows = C.try_box(job, box, rows)
            if f is not None:
                feas += 1
                break
            if leaf is not None:
                break
            k += 1
        ks.append(k)
        inv.append(1.0 / float(np.prod([b - a for a, b in box])))
    inv = np.array(inv)
    rec = dict(job=name, samples=ns, feasible=feas, k_hist=np.bincount(ks).tolist(), N_est=float(vol * inv.mean()),
               top_share=float(inv.max() / inv.sum()), sec=round(time.time() - t0, 1))
    print(json.dumps(rec), flush=True)
    return rec


def main():
    cmd = sys.argv[1]
    J = slab_jobs()
    if cmd == 'list':
        for k, v in J.items():
            print(k, v[0], v[1], [[round(a, 4), round(b, 4)] for a, b in v[2]])
        print(len(J), 'jobs')
        return
    if cmd == 'price':
        rec = price(sys.argv[2], int(sys.argv[3]))
        with open(os.path.join(HERE, '..', 'results', 'slabprice263.jsonl'), 'a') as fh:
            fh.write(json.dumps(rec) + '\n')
        return
    C.jobs, C.CERTS, C.STOP = (lambda: J), CERTS, STOP
    if cmd == 'run':
        sys.argv = ['cert261.py', '--job', sys.argv[2]] + (['--seconds', sys.argv[3]] if len(sys.argv) > 3 else [])
        C.main()
        return
    if cmd == 'verify':
        sys.argv = ['verify261.py', os.path.join(CERTS, sys.argv[2])]
        sys.exit(V.main())


if __name__ == '__main__':
    main()
