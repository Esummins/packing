"""A88 D5: emit results/census88_sample.jsonl -- a UNIFORM sample of DECORATED
k_H = 11 structures for the T3 cost pilot.

Level 0: uniform over LABELLED F0 survivors (results/level0_survivors.jsonl,
produced by plain uniform sampling of the factorable set -- every survivor found
is an exactly uniform draw; the <~3.3% orbit-weight caveat of A59 applies when
these are read as orbit samples).
Level 1: uniform among the tilt-feasible decorations that satisfy K0-1 and K0-3,
by rejection from the raw gauge-fixed menu 20^Ess * 2^Esw.

Format documented in notes/sample_format.md.
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
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
MAXTRY = 150000


def emit(struct, dec, ts, k0_2, tag):
    """One JSONL record."""
    zc = ts['zero_class']
    # relabel classes so the pinned (phi = 0) class is id 0 when it exists
    ncls = ts['ncls']
    if zc is None:
        remap = {c: c for c in range(ncls)}
    else:
        remap = {}
        nxt = 1
        for c in range(ncls):
            if c == zc:
                remap[c] = 0
            else:
                remap[c] = nxt
                nxt += 1
    cls = [remap[c] for c in ts['cls']]
    strict = sorted(set((remap[a], remap[b]) for a, b in ts['strict']))
    cnt = dec.counts()
    return dict(
        tag=tag,
        k=K, loaded_core=list(range(K)),
        wall_mask=struct['wm'],
        wall_mask_names=[''.join(A.WALL_NAMES[b] for b in range(4)
                                 if (m >> b) & 1) for m in struct['wm']],
        ss_edges=[list(e) for e in dec.ss_edges],
        rows=dec.rows(ts),
        tilt_class=cls, n_classes=ncls,
        class_order_strict=[list(x) for x in strict],
        zero_class_pinned=bool(zc is not None),
        Ess=cnt['Ess'], Esw=cnt['Esw'], E=cnt['E'], F=cnt['F'], m=cnt['m'],
        chi=cnt['chi'], n_flush_ss=cnt['nf'], n_wall_flush=cnt['nwf'],
        rigid_possible=bool(cnt['chi'] >= 0),
        slot_squares=dec.slot_squares(),
        K0_1=bool(dec.k0_1()), K0_2=bool(k0_2), K0_3=bool(dec.k0_3(ts)[0]),
    )


def draw_decoration(struct, rng, want_k01, maxtry=MAXTRY):
    wm = struct['wm']
    edges = [tuple(e) for e in struct['edges']]
    tries = 0
    while tries < maxtry:
        tries += 1
        dec = A.random_decoration(K, edges, wm, rng)
        ts = dec.tilt_system()
        if not ts['feasible']:
            continue
        if want_k01 and not dec.k0_1():
            continue
        ok3, _ = dec.k0_3(ts)
        if not ok3:
            continue
        return dec, ts, tries
    return None, None, tries


def main():
    n_main = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    n_drop = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    rng = np.random.default_rng(88088)
    surv = [json.loads(l) for l in
            open(os.path.join(RES, 'level0_survivors.jsonl'))]
    print('Level-0 uniform survivors available: %d' % len(surv))
    out = []
    stats = dict(n_struct_tried=0, n_struct_no_decoration=0, tries=[])
    t0 = time.time()
    order = rng.permutation(len(surv))
    ptr = 0
    while len(out) < n_main and ptr < len(order):
        s = surv[int(order[ptr])]
        ptr += 1
        stats['n_struct_tried'] += 1
        dec, ts, tr = draw_decoration(s, rng, True)
        stats['tries'].append(tr)
        if dec is None:
            stats['n_struct_no_decoration'] += 1
            continue
        out.append(emit(s, dec, ts, s.get('k0_2'), 'F0+K0-1+K0-3'))
        if len(out) % 100 == 0:
            print('  %d / %d  (%.1fs)' % (len(out), n_main, time.time() - t0),
                  flush=True)
    n_pass1 = len(out)
    # 100 more with K0-1 DROPPED (K0-3 still on)
    got = 0
    while got < n_drop and ptr < len(order):
        s = surv[int(order[ptr])]
        ptr += 1
        dec, ts, tr = draw_decoration(s, rng, False)
        if dec is None:
            continue
        out.append(emit(s, dec, ts, s.get('k0_2'), 'F0+K0-3 (K0-1 dropped)'))
        got += 1
    p = os.path.join(RES, 'census88_sample.jsonl')
    with open(p, 'w') as fh:
        for r in out:
            fh.write(json.dumps(r) + '\n')
    tries = np.array(stats['tries'], dtype=float)
    summ = dict(n_records=len(out), n_main=n_pass1, n_k01_dropped=got,
                structures_consumed=ptr,
                structures_with_no_admissible_decoration=
                stats['n_struct_no_decoration'],
                mean_rejection_tries=float(tries.mean()) if len(tries) else None,
                median_rejection_tries=float(np.median(tries)) if len(tries) else None,
                maxtry=MAXTRY, seconds=round(time.time() - t0, 1))
    with open(os.path.join(RES, 'census88_sample_meta.json'), 'w') as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ, indent=1))
    print('wrote', p)


if __name__ == '__main__':
    main()
