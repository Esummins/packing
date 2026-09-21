"""A261 O3 -- the GENERATOR (untrusted) of the box-valid LP certificates checked by verify261.py.

Depth-first bisection of the job's tilt domain (t = tilt / 45 deg, dyadic boxes).  Per box: try the PARENT's
(pattern, y) rows with the verifier's own rigorous bound; for every form choice still uncovered solve the centre LP
    min tau  s.t.  row_i(x; phi_c) <= tau,  x in [0,1]^4 x [S_LO, S0]
(tau* > 0 <=> no ring at the centre for that choice), take the duals y (float32, corners with zero weight become
'any'), and keep the row if the verifier's bound over the WHOLE box is > 0; otherwise split the widest dimension.
A centre with tau* <= 0 is a FEASIBLE ring at side <= S0: written to <job>.feasible.jsonl (a result, not an error)
and the box is split until MAXDEPTH, then left UNDECIDED (token stream still complete: leaf with no rows -> FAIL).

Output certs/<job>.{json,tree,leaves}; state in <job>.state.json (resume: tokens + pending stack); logs/STOP stops.
    python cert261.py --job M1 [--seconds 3000000] [--bench 100]
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import linprog

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import verify261 as V                                                 # noqa: E402

CERTS = os.path.join(ATT, 'certs')
STOP = os.path.join(ATT, 'logs', 'STOP')
MAXDEPTH = 60
TMIN = 1.0 / 64                                   # 0.703 deg: see box_meeters.md s.3.2 (no closed-LP certificate at flat)
FULL = [[TMIN, 1.0]] * 4


def jobs():
    """name -> (senses, lengths, tdomain).  M*: the three mixed-sense classes of rings of PAIRS; FLAT: the one-sense
    ring with wall 0 within FLAT_T * 45 deg of flat; R*: every ring with a row of THREE, up to rotation/reflection."""
    out = {'M1': ((1, 1, 1, -1), (2, 2, 2, 2), FULL), 'M2': ((1, 1, -1, -1), (2, 2, 2, 2), FULL),
           'M3': ((1, -1, 1, -1), (2, 2, 2, 2), FULL)}
    Z = [0.0, 0.0]                                   # an exactly FLAT wall (its sense is immaterial; listed as +)
    for sg in itertools.product((1, -1), repeat=3):  # F0: wall 0 flat;  F02: walls 0 and 2 flat (adjacent: [T] overlap)
        out['F0_' + ''.join('p' if v > 0 else 'm' for v in sg)] = ((1,) + sg, (2, 2, 2, 2), [Z] + [[TMIN, 1.0]] * 3)
    for sg in itertools.product((1, -1), repeat=2):
        out['F02_' + ''.join('p' if v > 0 else 'm' for v in sg)] = ((1, sg[0], 1, sg[1]), (2, 2, 2, 2),
                                                                   [Z, [TMIN, 1.0], Z, [TMIN, 1.0]])
    seen = set()
    for l in itertools.product((2, 3), repeat=4):
        if 3 not in l:
            continue
        for sg in itertools.product((1, -1), repeat=4):
            orb = set()
            for r in range(4):
                lr, sr = l[r:] + l[:r], sg[r:] + sg[:r]
                orb.add((lr, sr))
                orb.add((lr[::-1], tuple(-v for v in sr[::-1])))   # reflection: reverse the walls, flip the senses
            key = min(orb)
            if key in seen:
                continue
            seen.add(key)
            out['R%s_%s' % (''.join(map(str, key[0])), ''.join('p' if v > 0 else 'm' for v in key[1]))] = (
                key[1], key[0], FULL)
    return out


def centre_lp(job, tc, ch):
    """duals of the centre LP for form choice ch (tuple of 0/1).  Returns (tau*, y[12], x)."""
    sg, l = job['senses'], job['lengths']
    phi = [t * V.PI4 for t in tc]
    kap = [(l[w] - 1) / math.cos(phi[w]) + math.cos(phi[w]) + math.sin(phi[w]) for w in range(4)]
    wv = [math.cos(p) + math.sin(p) for p in phi]
    A, b = [], []
    for w in range(4):
        r = [0.0] * 6; r[w] = -1.0; r[4] = 1.0; r[5] = -1.0
        A.append(r); b.append(kap[w] + 1.0)
    for w in range(4):
        r = [0.0] * 6; r[w] = 1.0; r[4] = -1.0; r[5] = -1.0
        A.append(r); b.append(-kap[w])
    for k in range(4):
        p = (k - 1) % 4
        ca, cb, c0 = point_form(ch[k], sg[k], sg[p], phi[k], phi[p], wv[k], wv[p])
        r = [0.0] * 6; r[k] -= ca; r[p] += cb; r[4] -= cb; r[5] = -1.0
        A.append(r); b.append(c0 - cb * kap[p])
    res = linprog([0, 0, 0, 0, 0, 1.0], A_ub=A, b_ub=b, bounds=[(0, 1)] * 4 + [(V.S_LO, V.S0), (-10, 10)],
                  method='highs')
    if res.status != 0:
        return None, None, None
    y = np.maximum(-np.asarray(res.ineqlin.marginals), 0.0)
    return float(res.fun), y, res.x[:5]


def point_form(which, sA, sB, al, be, wa, wb):
    own, sg = (al, sA) if which == 0 else (be, sB)
    c, g = math.cos(own), math.sin(own)
    ca, cb, P = (g, c, c - g) if sg > 0 else (c, g, g - c)
    arg = (al - be) if sA * sB > 0 else (al + be)
    return ca, cb, 0.5 * P * (wb - wa) - 0.5 * (1 + math.cos(arg) + abs(math.sin(arg)))


def try_box(job, box, rows):
    """rows: list of (pattern, y32).  Returns (leaf_rows or None, feasible_point or None)."""
    keep = []
    if rows:
        L = V.lower_bound(job, box, [r[0] for r in rows], [r[1] for r in rows])
        keep = [r for r, v in zip(rows, L) if v > 0]
    tc = [0.5 * (a + b) for a, b in box]
    for ch in V.admissible(job):
        if any(all(p[k] == 2 or p[k] == ch[k] for k in range(4)) for p, _ in keep):
            continue
        tau, y, x = centre_lp(job, tc, ch)
        if tau is None:
            return None, None, keep
        if tau <= 1e-9:
            return None, dict(t=tc, choice=list(ch), x=[float(v) for v in x], tau=tau), keep
        y32 = np.asarray(y / max(y.sum(), 1e-300), np.float32)
        y32[y32 < 1e-7] = 0.0
        pat = tuple(2 if y32[8 + k] == 0 else ch[k] for k in range(4))
        if V.lower_bound(job, box, [pat], [y32.astype(float)])[0] > 0:
            keep.append((pat, y32))
        else:
            return None, None, keep
    return keep, None, keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--job', required=True)
    ap.add_argument('--seconds', type=float, default=3e6)
    ap.add_argument('--bench', type=int, default=0)
    a = ap.parse_args()
    sg, l, dom = jobs()[a.job]
    job = dict(name=a.job, senses=list(sg), lengths=list(l), tdomain=dom, S0=V.S0, S_LO=V.S_LO)
    os.makedirs(CERTS, exist_ok=True)
    base = os.path.join(CERTS, a.job)
    sp = base + '.state.json'
    if os.path.exists(sp):
        st = json.load(open(sp))
        if st.get('done'):
            print(a.job, 'already DONE', flush=True)
            return
    else:
        json.dump(job, open(base + '.json', 'w'))
        open(base + '.tree', 'wb').close()
        open(base + '.leaves', 'wb').close()
        st = dict(stack=[dict(box=dom, rows=[], depth=0)], n_tree=0, n_leafbytes=0, boxes=0, leaves=0, vol=0.0,
                  undecided=0, feasible=0, seconds=0.0)
    # truncate the streams to the last saved state (a crash may have written past it)
    for ext, key in (('.tree', 'n_tree'), ('.leaves', 'n_leafbytes')):
        with open(base + ext, 'r+b') as fh:
            fh.truncate(st[key])
    stack = [(tuple(map(tuple, e['box'])), [(tuple(p), np.asarray(y, np.float32)) for p, y in e['rows']], e['depth'])
             for e in st['stack']]
    ft, fl = open(base + '.tree', 'ab'), open(base + '.leaves', 'ab')
    t0 = tlast = time.time()
    vol0 = float(np.prod([b - c for c, b in dom]))

    def save(done=False):
        ft.flush(); fl.flush()
        st.update(stack=[dict(box=[list(b) for b in bx], rows=[[list(p), [float(v) for v in y]] for p, y in rw],
                              depth=d) for bx, rw, d in stack], n_tree=ft.tell(), n_leafbytes=fl.tell(),
                  seconds=st['seconds'] + time.time() - save.t, done=done)
        save.t = time.time()
        json.dump(st, open(sp + '.tmp', 'w'))
        os.replace(sp + '.tmp', sp)
    save.t = t0
    while stack:
        if os.path.exists(STOP) or time.time() - t0 > a.seconds or (a.bench and st['boxes'] >= a.bench):
            save()
            print('%s PAUSED boxes=%d leaves=%d vol=%.4f undecided=%d feasible=%d pending=%d  %.0fs' % (
                a.job, st['boxes'], st['leaves'], st['vol'] / vol0, st['undecided'], st['feasible'], len(stack),
                st['seconds']), flush=True)
            return
        box, rows, depth = stack.pop()
        st['boxes'] += 1
        leaf, feas, keep = try_box(job, box, rows)
        if feas is not None:                      # a ring at side <= S0 exists for this job: the claim is FALSE
            st['feasible'] += 1
            with open(base + '.feasible.jsonl', 'a') as fh:
                fh.write(json.dumps(feas) + '\n')
            stack.append((box, rows, depth))
            save()
            print('%s FEASIBLE centre (claim false for this job): %s' % (a.job, json.dumps(feas)), flush=True)
            return
        if leaf is None and depth >= MAXDEPTH:
            leaf = []
            st['undecided'] += 1
        if leaf is not None:
            ft.write(bytes([4]))
            fl.write(bytes([len(leaf)]))
            for p, y in leaf:
                fl.write(V.REC.pack(*p, *[float(v) for v in y]))
            st['leaves'] += 1
            st['vol'] += float(np.prod([b - c for c, b in box]))
        else:
            d = max(range(4), key=lambda w: (box[w][1] - box[w][0], -((w - depth) % 4)))
            lo, hi = box[d]
            mid = 0.5 * (lo + hi)
            ft.write(bytes([d]))
            stack.append((box[:d] + ((mid, hi),) + box[d + 1:], keep, depth + 1))
            stack.append((box[:d] + ((lo, mid),) + box[d + 1:], keep, depth + 1))
        if time.time() - tlast > 300:
            tlast = time.time()
            save()
            print('%s boxes=%d leaves=%d vol=%.5f pending=%d' % (a.job, st['boxes'], st['leaves'], st['vol'] / vol0,
                                                                  len(stack)), flush=True)
    save(done=True)
    print('%s DONE boxes=%d leaves=%d undecided=%d feasible=%d  %.0fs' % (
        a.job, st['boxes'], st['leaves'], st['undecided'], st['feasible'], st['seconds']), flush=True)


if __name__ == '__main__':
    main()
