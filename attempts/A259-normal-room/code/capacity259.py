"""A259: a LOWER bound on the pocket capacity of a ring by explicit witnesses: candidate free poses from the exact centre
sets C(theta) (vertices shrunk toward an interior point + representative points), then the largest pairwise
interior-disjoint subset (exact SAT, hard containment) up to 3.  Every reported witness passes free_margin >= 0."""
import itertools, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, room259 as R

def candidates(Vs, s, step=3.0, eps=1e-4):
    out = []
    for td in np.arange(0.0, 90.0, step):
        th = td * Z.DEG
        for Pg in R.polys_of(R.centre_set(Vs, s, th)):
            rp = Pg.representative_point(); pts = [(rp.x, rp.y)]
            for x, y in list(Pg.exterior.coords)[:-1]:
                pts.append((x + eps * (rp.x - x), y + eps * (rp.y - y)))
            for p in pts:
                pose = (float(p[0]), float(p[1]), float(th))
                if R.free_margin(pose, Vs, s) >= 0: out.append(pose)
    return out

def best_set(Vs, s, kmax=3):
    cand = candidates(Vs, s); polys = [Z.sq_verts(*p) for p in cand]; n = len(cand)
    ok = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i):
            ok[i, j] = ok[j, i] = Z.poly_gap(polys[i], polys[j]) >= 0
    best = [0] if n else []
    for i in range(n):
        J = [j for j in range(i) if ok[i, j]]
        if J and len(best) < 2: best = [i, J[0]]
        if kmax >= 3:
            for a, b in itertools.combinations(J, 2):
                if ok[a, b]: return [cand[i], cand[a], cand[b]], n
    return [cand[k] for k in best], n

if __name__ == '__main__':
    rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 'adv259.jsonl'))]
    out = []
    for r in rows:
        if r['pierceO'] <= 0 and not r['key'].startswith('shat|1|1|45|0'): continue
        x, s = np.array(r['x']), r['s']; Vs = Z.ring_verts(x, s)
        W, n = best_set(Vs, s)
        row = {'key': r['key'], 's': s, 'x': r['x'], 'boxes': r['boxes'], 'pierceO': r['pierceO'], 'capacity_lb': len(W), 'witness': W,
               'witness_margins': [R.free_margin(p, Vs, s) for p in W], 'box_terms': [[1 - x[k], x[k] + Z.span(x[4 + k]) - (s - 1)] for k in range(4)]}
        out.append(row); print(r['key'], 'pierceO %+.3f' % r['pierceO'], 'cands', n, 'capacity >=', len(W), 'box terms', [[round(v, 3) for v in b] for b in row['box_terms']])
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'capacity259.json'), 'w'), indent=1)
