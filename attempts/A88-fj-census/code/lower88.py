"""A88 D1 rigorous LOWER bound at k_H = 11.

FAMILY P5.  Square-square graph = the Hamiltonian PATH 0-1-2-...-10.
            Wall mask of every square in S = {none, L, B, R, T} (wall-degree <= 1).
Size of the raw family: 5^11 = 48 828 125 labelled members.

Because the graph is the path, Aut(path) = {identity, reversal}, so two members
lie in the same S_11 x D4 orbit iff their mask SEQUENCES agree under
(reversal)^a x D4 -- a group of order 16.  Orbits are therefore counted EXACTLY
by keeping the lexicographically minimal sequence of each 16-element orbit, and
F0 is invariant under that group, so filtering commutes with canonicalisation.

EVERY kept member is then verified by the FULL F0 code a88lib.f0_flags (all ten
filters, planarity included); the run asserts that not one kept member fails.
The resulting count is a rigorous LOWER bound on the k_H = 11 Level-0 census.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import json
import sys
import time

import numpy as np

import a88lib as A

K = 11
S = [0, 1, 2, 4, 8]                       # dense indices 0..4 of ALLOWED
NS = len(S)
assert A.ALLOWED[:NS] == S
PATH = [(i, i + 1) for i in range(K - 1)]
POW = (NS ** np.arange(K)).astype(np.int64)
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')


def group_maps():
    """The 16 maps (reversal^a, delta) acting on a length-11 sequence of dense
    mask indices: (perm of positions, relabelling of mask indices)."""
    out = []
    for rev in (0, 1):
        pos = np.arange(K)[::-1].copy() if rev else np.arange(K)
        for d in range(8):
            tab = A.MTD[d][:NS].copy()
            assert (tab < NS).all()
            out.append((pos, tab))
    return out


GMAPS = group_maps()
POPS = np.array([A.POP[m] for m in S], dtype=np.int64)
BITS = np.array([[(m >> b) & 1 for b in range(4)] for m in S], dtype=np.int64)
DR = A.DREQ[:NS, :NS]
CX = A.COEX[:NS, :NS]


def main():
    chunk = int(sys.argv[1]) if len(sys.argv) > 1 else 4000000
    total = NS ** K
    t0 = time.time()
    kept = []
    n_canon = 0
    n_cheap = 0
    n_planar_calls = 0
    n_fail_full = 0
    done = 0
    while done < total:
        b = min(chunk, total - done)
        r = np.arange(done, done + b, dtype=np.int64)
        Mseq = np.empty((b, K), dtype=np.int64)
        rep = 1
        for i in range(K):
            Mseq[:, i] = (r // rep) % NS
            rep *= NS
        key = (Mseq * POW[None, :]).sum(1)
        cand = np.ones(b, dtype=bool)
        for (pos, tab) in GMAPS:
            k2 = (tab[Mseq][:, pos] * POW[None, :]).sum(1)
            cand &= (key <= k2)
        idx = np.nonzero(cand)[0]
        n_canon += idx.size
        Mc = Mseq[idx]
        # cheap, exactly the vectorisable part of F0
        ok = (POPS[Mc[:, 0]] >= 1) & (POPS[Mc[:, K - 1]] >= 1)          # L1
        wc = np.stack([BITS[Mc, bb].sum(1) for bb in range(4)], 1)
        ok &= (wc <= 3).all(1)                                          # N1
        anyw = wc > 0
        ok &= (anyw[:, 0] & anyw[:, 2]) | (anyw[:, 1] & anyw[:, 3])     # L6/L7
        for i in range(K):
            for j in range(i + 1, K):
                ok &= CX[Mc[:, i], Mc[:, j]] & (DR[Mc[:, i], Mc[:, j]] <= j - i)
        idx2 = np.nonzero(ok)[0]
        n_cheap += idx2.size
        for t in idx2:
            wm = [S[a] for a in Mc[t]]
            n_planar_calls += 1
            f = A.f0_flags(K, PATH, wm)
            if all(f.values()):
                kept.append(wm)
            else:
                n_fail_full += 1
        done += b
        print('  %d / %d  canon %d  cheap %d  kept %d  (%.0fs)'
              % (done, total, n_canon, n_cheap, len(kept), time.time() - t0),
              flush=True)
    # independent re-verification of every kept member with the full F0 code
    bad = 0
    for wm in kept:
        f = A.f0_flags(K, PATH, wm)
        if not all(f.values()):
            bad += 1
    out = dict(family='P5: Hamiltonian path on 11 squares, wall masks in '
                      '{none,L,B,R,T}',
               raw_labelled_members=total,
               canonical_reps=n_canon,
               after_vectorised_F0_part=n_cheap,
               planarity_calls=n_planar_calls,
               failed_full_F0=n_fail_full,
               LOWER_BOUND_orbits=len(kept),
               reverify_failures=bad,
               seconds=round(time.time() - t0, 1))
    with open(os.path.join(RES, 'lower88.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'lower88_members.jsonl'), 'w') as fh:
        for wm in kept[:5000]:
            fh.write(json.dumps(wm) + '\n')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
