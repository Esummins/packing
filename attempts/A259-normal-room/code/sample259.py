"""A259: sample normal rings across D (rejection, hard feasibility), measure PIERCE-by-O margin per ring.
    python sample259.py --n 40 --sides 3.82,shat --seed 1 --out ../results/sample259.jsonl   (resumable by key)"""
import argparse, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, room259 as R

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=40); ap.add_argument('--sides', default='3.82,shat')
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--boxes', type=int, default=1)
    ap.add_argument('--step', type=float, default=1.0)
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'results', 'sample259.jsonl'))
    a = ap.parse_args()
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)['key'] for l in open(a.out) if l.strip()}
    for sd in a.sides.split(','):
        s = Z.SHAT if sd == 'shat' else float(sd)
        rng = np.random.default_rng(a.seed)
        xs = Z.sample_D(rng, s, a.n, boxes=bool(a.boxes))
        for i, x in enumerate(xs):
            key = '%s|%d|%d|%d' % (sd, a.seed, a.boxes, i)
            if key in done: continue
            if os.path.exists(stop): return
            t = time.time()
            Vs = Z.ring_verts(x, s)
            w, pose, nc = R.pierce_O(x, s, a.step, Vs)
            row = {'key': key, 's': s, 'x': [float(v) for v in x], 'ring_margin': Z.ring_margin(x, s, bool(a.boxes)),
                   'pierceO': w, 'pose': pose, 'ncomp': nc,
                   'pose_margin': None if pose is None else R.free_margin(pose, Vs, s), 'sec': round(time.time() - t, 2)}
            with open(a.out, 'a') as f: f.write(json.dumps(row) + '\n')
            print(key, 'phi', [round(v / Z.DEG, 1) for v in x[4:]], 'd', [round(v, 3) for v in x[:4]], 'pierceO %+.4f' % w, 'nc', nc, flush=True)
Z.belownormal()
main()
