"""A107 T1(b): direct side minimisation per structure -- the snapped slot squares fixed as functions
of s, the remaining squares free (cx, cy, theta), minimise s by SLSQP with >=100 restarts including
every alive node's own LP seed.  Generalises docs/residue_map/gen_pinwheel_k7.py to an arbitrary slot
set and free count.  Writes attempts/A107-shadow-gallery/results/minima.json."""
import os, sys, json, math, time, random, collections
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
RES = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')
S = L.S0
SHAT = L.SHAT

# ---- slot centres as affine functions of s: (ax, bx, ay, by) with c = (ax + bx*s, ay + by*s)
def slot_affine(name):
    fam, ij = name[:2], name[2:].strip('()')
    i, j = (int(v) for v in ij.split(','))
    if fam == 'BL': return (0.5 + i, 0.0, 0.5 + j, 0.0)
    if fam == 'BR': return (-0.5 - i, 1.0, 0.5 + j, 0.0)
    if fam == 'TL': return (0.5 + i, 0.0, -0.5 - j, 1.0)
    if fam == 'TR': return (-0.5 - i, 1.0, -0.5 - j, 1.0)
    raise ValueError(name)

def slot_centres(slots, s):
    return [(a + b * s, c + d * s) for (a, b, c, d) in (slot_affine(n) for n in slots)]

def make_cons(slots, nf):
    """Vectorised feasibility vector (all entries >= 0 <=> admissible): free-square walls, every
    free-free / free-slot / slot-slot SAT gap, and slot containment."""
    aff = np.array([slot_affine(n) for n in slots], float) if slots else np.zeros((0, 4))
    ns = len(slots)
    n = nf + ns
    I, Jx = np.triu_indices(n, 1)
    keep = I < nf                       # drop slot-slot pairs inside one corner stack later
    def cons(z):
        s = float(z[0])
        C = np.empty((n, 2)); T = np.zeros(n)
        if nf:
            zz = np.asarray(z[1:1 + 3 * nf]).reshape(nf, 3)
            C[:nf] = zz[:, :2]; T[:nf] = zz[:, 2]
        if ns:
            C[nf:, 0] = aff[:, 0] + aff[:, 1] * s
            C[nf:, 1] = aff[:, 2] + aff[:, 3] * s
        g = L.gaps_pairs(C, T, I, Jx)
        out = [g]
        if nf:
            w = (np.abs(np.cos(T[:nf])) + np.abs(np.sin(T[:nf]))) / 2.0
            out.append(C[:nf, 0] - w); out.append(s - w - C[:nf, 0])
            out.append(C[:nf, 1] - w); out.append(s - w - C[:nf, 1])
        if ns:
            out.append(C[nf:, 0] - 0.5); out.append(s - 0.5 - C[nf:, 0])
            out.append(C[nf:, 1] - 0.5); out.append(s - 0.5 - C[nf:, 1])
        return np.concatenate(out)
    return cons

def solve(cons, z0, nf):
    r = minimize(lambda z: z[0], z0, jac=lambda z: np.eye(1, len(z0), 0)[0], method='SLSQP',
                 constraints=[{'type': 'ineq', 'fun': cons}],
                 bounds=[(3.4, 4.6)] + [(0.0, 4.6), (0.0, 4.6), (-3.2, 3.2)] * nf,
                 options={'maxiter': 200, 'ftol': 1e-12})
    return r.x, float(r.x[0]), float(cons(r.x).min())

def canon_free(cfg, opname, s):
    f = dict(L.d4_ops(s))[opname]
    im = [tuple(f(x, y, t)) for x, y, t in cfg]
    return [q for q in im if L.snap(q[0], q[1], q[2], s) is None]

def run_structure(slots, nf, seeds, nrand=100, rng=None, tlim=1e9):
    cons = make_cons(slots, nf)
    rng = rng or random.Random(12345)
    starts = []
    for F in seeds:
        starts.append(('lp', np.array([S + 0.02] + [v for q in F for v in q])))
    for k in range(nrand):
        s0 = rng.uniform(3.88, 4.15)
        F = []
        cx0, cy0, r = rng.uniform(1.4, 2.6), rng.uniform(1.4, 2.6), rng.uniform(0.45, 1.25)
        th = rng.uniform(0, math.pi / 2)
        phi = rng.uniform(0, 2 * math.pi)
        for i in range(nf):
            if rng.random() < 0.5:      # pinwheel-ish ring
                a = phi + 2 * math.pi * i / nf
                F.append((cx0 + r * math.cos(a), cy0 + r * math.sin(a), th))
            else:                        # free scatter
                F.append((rng.uniform(0.8, s0 - 0.8), rng.uniform(0.8, s0 - 0.8), rng.uniform(0, math.pi / 2)))
        starts.append(('rand', np.array([s0] + [v for q in F for v in q])))
    best = None
    sols = []
    seedmin = {}
    t0 = time.time()
    for k, (kind, z0) in enumerate(starts):
        if time.time() - t0 > tlim and kind == 'rand':
            break
        try:
            z, sv, feas = solve(cons, z0, nf)
        except Exception:
            continue
        if feas < -1e-7 or not np.isfinite(sv):
            continue
        sols.append((sv, z.tolist(), kind, k))
        if best is None or sv < best[0]:
            best = (sv, z.tolist())
        if kind == 'lp':
            seedmin[k] = (sv, z.tolist())
    sols.sort(key=lambda t: t[0])
    return dict(slots=list(slots), nfree=nf, best=best, nfeas=len(sols), nstart=len(starts),
                minima=sorted({round(sv, 5) for sv, _, _, _ in sols})[:15],
                sols=[(round(sv, 8), z) for sv, z, _, _ in sols[:6]],
                seedmin={str(k): (round(v[0], 8), v[1]) for k, v in seedmin.items()},
                seconds=round(time.time() - t0, 1))

def main():
    t0 = time.time()
    ex = json.load(open(os.path.join(RES, 'extract.json')))
    nodes = ex['nodes']
    groups = {k: v for k, v in ex['groups'].items()}
    order = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(order)
    nrand = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    out = {}
    for gi, (gk, mem) in enumerate(order[:limit]):
        src, skel, (slots, nf) = json.loads(gk)
        slots = tuple(slots)
        seeds, seed_nodes = [], []
        for idx in mem[:(20 if len(mem) >= 8 else 6)]:
            n = nodes[idx]
            F = canon_free(n['cfg'], n['struct_op'], S)
            if len(F) == nf:
                seeds.append(F); seed_nodes.append(idx)
        nr = nrand if len(mem) >= 8 else max(8, nrand // 2)
        r = run_structure(slots, nf, seeds, nrand=nr)
        r['src'] = src; r['skel'] = skel; r['members'] = mem; r['seed_nodes'] = seed_nodes
        r['gk'] = gk
        out[gk] = r
        b = r['best']
        print(f"[{gi+1}/{min(limit,len(order))}] {src} nodes={len(mem):3d} slots={len(slots)} free={nf} "
              f"feas={r['nfeas']}/{r['nstart']} s*={b[0]:.6f} (shat{b[0]-SHAT:+.6f}) {r['seconds']}s"
              if b else f"[{gi+1}] {src} nodes={len(mem)} slots={len(slots)} free={nf} INFEASIBLE {r['seconds']}s",
              flush=True)
    json.dump(out, open(os.path.join(RES, 'minima.json'), 'w'), indent=1)
    print('total', round(time.time() - t0, 1), 's -> results/minima.json')

if __name__ == '__main__':
    main()
