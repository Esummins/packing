"""A32 driver: joint structure branch-and-bound with early kills, per target core K.

Tree.  Level k holds every ORBIT (under S_k x D4) of a partial structure on k
introduced squares that survives the monotone + extensibility cascade.  A child is
produced by introducing square k and DECIDING all k + 4 of its slots (k
square-square slots, 4 wall slots) -- and that decision is itself branched
EDGE-AT-A-TIME, with the cascade run on every prefix, which is where the early
kill happens.  Level K nodes are CLOSED and get the structural checks.

Duplicate-freeness: children are canonicalised under S_{k+1} x D4 and deduplicated,
so each level holds exactly one node per orbit; and because every kill is monotone
(or a certified extensibility kill) no live descendant is ever cut off.
"""
import os
import sys
import json
import math
import time
import argparse
import multiprocessing as mp

import numpy as np

import core as C
from core import STAGES

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'results'))
STATE = os.environ.get('A32_STATE') or os.path.normpath(
    os.path.join(HERE, '..', 'state'))
os.makedirs(RES, exist_ok=True)
os.makedirs(STATE, exist_ok=True)


def _new_counters(k):
    return {'sub': {}, 'closed': {}}


def expand_one(K, k, mask, out, cnt):
    """Introduce square k into the k-square structure `mask`; edge-at-a-time DFS
    over its k + 4 slots with the monotone cascade on every prefix.
    Appends surviving (k+1)-structures (as raw bit lists) to `out`."""
    adj0, wm0 = C.decode(k, mask)
    kk = k + 1
    nslot = k + 4
    R = K - kk                       # squares still to come after this one
    adj = adj0 + [0]
    wm = wm0 + [0]

    def rec(t):
        # slots 0..t-1 of the new square are decided, t..nslot-1 undecided
        for bit in (0, 1):
            if bit:
                if t < k:
                    adj[t] |= 1 << k
                    adj[k] |= 1 << t
                else:
                    wm[k] |= 1 << (t - k)
            # how many further edges each square may still gain
            avail = [R + (1 if i >= t + 1 else 0) for i in range(k)]
            undec_ss = max(0, k - (t + 1))
            undec_w = 4 - max(0, (t + 1) - k)
            avail.append(R + undec_ss + undec_w)
            last = (t + 1 == nslot)
            st = cnt['sub'].setdefault(t + 1, [0, 0, {}])
            st[0] += 1
            r = C.monotone_kill(kk, adj, wm, K, avail,
                                planar=last, triangle=last)
            if r is None:
                st[1] += 1
                if last:
                    out.append((list(adj), list(wm)))
                else:
                    rec(t + 1)
            else:
                st[2][r] = st[2].get(r, 0) + 1
            if bit:
                if t < k:
                    adj[t] &= ~(1 << k)
                    adj[k] &= ~(1 << t)
                else:
                    wm[k] &= ~(1 << (t - k))
    rec(0)


def _worker(args):
    K, k, masks = args
    cnt = {'sub': {}, 'nodes': 0}
    ck = C.ctx(k + 1)
    kids = set()
    t0 = time.perf_counter()
    ncand = 0
    for mask in masks:
        out = []
        expand_one(K, k, mask, out, cnt)
        ncand += len(out)
        for adj, wm in out:
            bits = C.encode(k + 1, adj, wm)
            kids.add(ck.canon(bits))
        cnt['nodes'] += 1
    cnt['seconds'] = time.perf_counter() - t0
    cnt['ncand'] = ncand
    cnt['nkids'] = len(kids)
    return sorted(kids), cnt


def merge(a, b):
    for t, v in b.get('sub', {}).items():
        d = a['sub'].setdefault(int(t), [0, 0, {}])
        d[0] += v[0]
        d[1] += v[1]
        for s, c in v[2].items():
            d[2][s] = d[2].get(s, 0) + c
    for key in ('nodes', 'seconds', 'ncand', 'nkids'):
        a[key] = a.get(key, 0) + b.get(key, 0)
    return a


def level0(K):
    """Level 1: a single square with a wall mask, up to D4."""
    c = C.ctx(1)
    seen = set()
    for m in C.ALLOWED:
        adj = [0]
        wm = [m]
        if C.monotone_kill(1, adj, wm, K, [K - 1]) is None:
            seen.add(c.canon(C.encode(1, adj, wm)))
    return sorted(seen)


def close_level(K, masks):
    """Structural checks on the closed nodes of the final level."""
    agg = dict(closed=len(masks), L1=0, main=0, main_thin=0, main_nonthin=0,
               selfstress=0, lam0=0, L7=0, Ehist={})
    for m in masks:
        adj, wm = C.decode(K, m)
        r = C.close_checks(K, adj, wm)
        if r['L1']:
            agg['L1'] += 1
        if r['main']:
            agg['main'] += 1
            agg['main_thin'] += int(r['thin'])
            agg['main_nonthin'] += int(not r['thin'])
            agg['Ehist'][r['E']] = agg['Ehist'].get(r['E'], 0) + 1
        if r['selfstress']:
            agg['selfstress'] += 1
        if r['lam0']:
            agg['lam0'] += 1
        if r['L7'] and r['L1']:
            agg['L7'] += 1
    return agg


def run(K, workers=6, node_cap=None, time_cap=None, resume=True):
    t_start = time.time()
    rep = {'K': K, 'levels': {}, 'workers': workers}
    lv = None
    k0 = 1
    if resume:
        for k in range(K, 0, -1):
            p = os.path.join(STATE, 'K%d_level%d.json' % (K, k))
            if os.path.exists(p):
                d = json.load(open(p))
                lv = d['masks']
                k0 = k
                rep['levels'] = {int(a): b for a, b in d['levels'].items()}
                print('[K=%d] resumed at level %d (%d nodes)' % (K, k, len(lv)),
                      flush=True)
                break
    if lv is None:
        lv = level0(K)
        rep['levels'][1] = dict(frontier=len(lv), seconds=0.0)
        k0 = 1
    for k in range(k0, K):
        t0 = time.time()
        cnt = {'sub': {}}
        if workers > 1 and len(lv) > 200:
            nch = max(workers * 4, 1)
            chunk = max(1, (len(lv) + nch - 1) // nch)
            jobs = [(K, k, lv[i:i + chunk]) for i in range(0, len(lv), chunk)]
            kids = set()
            with mp.Pool(workers) as pool:
                for kk, cc in pool.imap_unordered(_worker, jobs):
                    kids.update(kk)
                    merge(cnt, cc)
            lv = sorted(kids)
        else:
            kk, cc = _worker((K, k, lv))
            merge(cnt, cc)
            lv = kk
        el = time.time() - t0
        sub = {int(t): dict(visited=v[0], survived=v[1], kills=v[2])
               for t, v in sorted(cnt['sub'].items())}
        nvis = sum(v['visited'] for v in sub.values())
        rep['levels'][k + 1] = dict(
            frontier=len(lv), parents=cnt.get('nodes', 0),
            candidates=cnt.get('ncand', 0), subnodes_visited=nvis,
            seconds=round(el, 2),
            sec_per_subnode=(el / nvis if nvis else 0.0),
            sub=sub)
        print('[K=%d] level %d: frontier=%d  (visited %d partial nodes, %.1fs, '
              '%.1f us/node)' % (K, k + 1, len(lv), nvis, el,
                                 1e6 * el / max(1, nvis)), flush=True)
        json.dump({'masks': lv, 'levels': rep['levels']},
                  open(os.path.join(STATE, 'K%d_level%d.json' % (K, k + 1)), 'w'))
        if node_cap and len(lv) > node_cap:
            rep['aborted'] = 'node_cap at level %d' % (k + 1)
            print('  ABORT: node cap', flush=True)
            return rep
        if time_cap and time.time() - t_start > time_cap:
            rep['aborted'] = 'time_cap at level %d' % (k + 1)
            print('  ABORT: time cap', flush=True)
            return rep
    rep['close'] = close_level(K, lv)
    rep['total_seconds'] = round(time.time() - t_start, 1)
    json.dump(rep, open(os.path.join(RES, 'bb_K%d.json' % K), 'w'), indent=1)
    print('[K=%d] CLOSED: %s' % (K, {a: b for a, b in rep['close'].items()
                                     if a != 'Ehist'}), flush=True)
    return rep


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('K', type=int, nargs='+')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--node-cap', type=int, default=None)
    ap.add_argument('--time-cap', type=float, default=None)
    ap.add_argument('--no-resume', action='store_true')
    a = ap.parse_args()
    for K in a.K:
        run(K, workers=a.workers, node_cap=a.node_cap, time_cap=a.time_cap,
            resume=not a.no_resume)
