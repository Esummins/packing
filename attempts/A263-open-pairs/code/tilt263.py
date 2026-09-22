"""A263 (b) LOCK-TILT by exchange -- tests [M] (open_pairs.md s.4).
For an open pair (s1, W) of tilts f1 != fW on wall k:   T_e(tau) := the unit cell of s1's tilt touching the wall at
start offset tau (a translate of s1 along the wall);  symmetric T'_e(tau) := a translate of W at W's tilt.
Exchange (E6): if M(T_e) subset {W} then W -> T_e keeps Phi1, Phi2, Phi4 and raises Phi5 := #(walls whose touchers have
one common tilt).  Joint form (E6'): M(T_e) = {W, F}, F free, and a unit cell F' disjoint from T_e and from every
square other than W, F  =>  W -> T_e, F -> F'  (Lemma CELLS, |Pi| = 2).
Per open wall with |fW - f1| > 1e-9 this script scans tau (grid 0.002) and reports
   ring_free : the tau-set on which T_e meets no ring square other than W (exact SAT, interior overlap > 1e-9)
   avail     : ... and no free square either  -> (E6) applies
   joint     : T_e meets the poker F only, and F has a free LIFT F' = F + lam*v (v = T_e's edge normal off the wall,
               lam on a grid <= 0.25) disjoint from T_e and all other squares, inside the container  -> (E6') applies
for BOTH directions (W re-posed at s1's tilt; s1 re-posed at W's tilt).  Test sets: A258's corpus rings (+ poker) and
A260's adversary rows (no free squares: ring_free only).      python tilt263.py  -> results/tilt263.jsonl"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo263 as G                                                    # noqa: E402
import fact263 as F                                                   # noqa: E402
H, Z, DEG = G.H, G.Z, G.DEG
TOL = 1e-9


def meets(A, B):
    return Z.poly_gap(A, B) < -TOL


def intervals(taus, flags):
    out, start = [], None
    for t, f in zip(taus, flags):
        if f and start is None:
            start = t
        if not f and start is not None:
            out.append((round(float(start), 4), round(float(t), 4)))
            start = None
    if start is not None:
        out.append((round(float(start), 4), round(float(taus[-1]), 4)))
    return out


def scan_wall(x, s, k, free, direction):
    """direction 'W': re-pose W at s1's tilt;  's1': re-pose s1 at W's tilt."""
    a, f1, b, fW = x[4 * k:4 * k + 4]
    Vs = H.hyb_verts(x, s)
    i1, iW = 2 * k, 2 * k + 1
    mover = iW if direction == 'W' else i1
    tilt = f1 if direction == 'W' else fW
    others = [V for j, V in enumerate(Vs) if j != mover]
    taus = np.arange(0.0, s - H.w_of(tilt) + 1e-12, 0.004)
    ring_free, avail, joint = [], [], []
    for tau in taus:
        T = H.toucher(tau, tilt, s, k)
        rf = not any(meets(T, V) for V in others)
        ring_free.append(rf)
        hit = [Fq for Fq in free if meets(T, Fq)] if rf else []
        avail.append(rf and not hit)
        jt = False
        if rf and len(hit) == 1:
            vdir = np.array(H.Z.rot_k([(-math.sin(tilt), math.cos(tilt))], 0.0, k)[0])      # edge normal off the wall
            for lam in np.arange(0.0, 0.2501, 0.005):
                Fp = hit[0] + lam * vdir
                if Z.contain_margin(Fp, s) < -TOL or meets(Fp, T):
                    continue
                if any(meets(Fp, V) for V in others) or any(meets(Fp, Gq) for Gq in free if Gq is not hit[0]):
                    continue
                jt = True
                break
        joint.append(jt)
    return dict(wall=k, dir=direction, f1_deg=f1 / DEG, fW_deg=fW / DEG, e=H.shift(a, f1, b, fW, s),
                ring_free=intervals(taus, ring_free), avail=intervals(taus, avail), joint=intervals(taus, joint))


def main():
    out = os.path.join(HERE, '..', 'results', 'tilt263.jsonl')
    items = []
    rows, N = H.corpus()
    for name, s, sq in rows:
        x = F.ring_to_x(sq[:8], s, N)
        if x is not None:
            Vh = H.hyb_verts(x, s)
            mirrored = max(min(np.abs(np.sort(Vh[i], axis=0) - np.sort(np.array(q, float), axis=0)).max()
                               for q in sq[:8]) for i in range(8)) > 1e-6
            free = [np.array(V, float) for V in sq[8:]]
            if mirrored:
                free = [np.stack([s - V[:, 0], V[:, 1]], axis=1) for V in free]
            items.append(('corpus:' + name, s, x, free))
    for l in open(os.path.join(G.ROOT, 'attempts', 'A260-locked-wall', 'results', 'adv260.jsonl')):
        r = json.loads(l)
        if not r['same']:
            items.append(('adv260:' + r['key'], r['s'], np.array(r['x']), []))
    tally = dict(walls=0, ring_free=0, avail=0, joint=0, neither=0)
    with open(out, 'w') as fh:
        for key, s, x, free in items:
            for k in range(4):
                if abs(x[4 * k + 1] - x[4 * k + 3]) <= 1e-9:
                    continue
                recs = [scan_wall(x, s, k, free, d) for d in ('W', 's1')]
                tally['walls'] += 1
                rf = any(r['ring_free'] for r in recs)
                av = any(r['avail'] for r in recs)
                jt = any(r['joint'] for r in recs)
                tally['ring_free'] += rf
                tally['avail'] += av
                tally['joint'] += (jt and not av)
                tally['neither'] += not (av or jt)
                fh.write(json.dumps(dict(key=key, s=s, n_free=len(free), recs=recs)) + '\n')
                print(key[:40], 'wall', k, 'dtilt %+.2f' % (recs[0]['fW_deg'] - recs[0]['f1_deg']),
                      'ring_free', rf, 'avail', av, 'joint', jt, flush=True)
    print(json.dumps(tally))
    json.dump(tally, open(os.path.join(HERE, '..', 'results', 'tilt263_tally.json'), 'w'))


if __name__ == '__main__':
    Z.belownormal()
    main()
