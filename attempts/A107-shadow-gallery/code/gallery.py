"""A107 T1/T2 driver: de-duplicate the minimised structures into DISTINCT SHADOWS (0.05 in position,
3 deg in tilt, modulo the class stabiliser in D4), confirm each with >=100 restarts, analyse it
(contact graph, Fritz-John contact forces, exact incidence Jacobian, flat directions with a second-
order test, rattler/load-bearing subgraph, common-tilt sweep), draw it, and write docs/shadows.md."""
import os, sys, json, math, time, random, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L, minimise as M, analyse as A, svg as SV

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
RES = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')
DOCS = os.path.join(ROOT, 'docs')
SVGD = os.path.join(DOCS, 'shadows')
S0 = L.S0
SHAT = L.SHAT

def full_config(slots, nf, z):
    s = float(z[0])
    free = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(nf)]
    fx = [(x, y, 0.0) for x, y in M.slot_centres(slots, s)]
    return s, free, fx

def scale_to_unit(cfg, s):
    """Compare packings in the unit container so different s* are commensurate."""
    return [(x / s, y / s, t) for x, y, t in cfg]

def same_shadow(a, b, dtol=0.05, atol=3.0):
    """a, b = (s, [squares]).  Compared in the container frame at their own s (so a shadow is the
    same geometric packing), with the tolerance the brief specifies."""
    (sa, ca), (sb, cb) = a, b
    if abs(sa - sb) > 2e-4 or len(ca) != len(cb):
        return None
    for nm, f in L.d4_ops(sb):
        im = [tuple(f(x, y, t)) for x, y, t in cb]
        if L.match(ca, im, dtol, atol):
            return nm
    return None

def main():
    t0 = time.time()
    ex = json.load(open(os.path.join(RES, 'extract.json')))
    mn = json.load(open(os.path.join(RES, 'minima.json')))
    nodes = ex['nodes']

    # ---------- one candidate per (structure, LANDING): each alive node's own LP seed is followed
    #            to the minimum it actually reaches, so a structure with several local minima
    #            splits its nodes between them instead of being collapsed onto the global one.
    items = []
    for gk, r in mn.items():
        if not r.get('best'):
            continue
        land = collections.defaultdict(lambda: dict(nodes=[], z=None, s=None))
        for k, (sv, z) in (r.get('seedmin') or {}).items():
            ki = int(k)
            if ki >= len(r['seed_nodes']):
                continue
            key = round(sv, 5)
            L2 = land[key]
            L2['nodes'].append(r['seed_nodes'][ki])
            if L2['z'] is None or sv < L2['s']:
                L2['z'], L2['s'] = z, sv
        if not land:
            land[round(r['best'][0], 5)] = dict(nodes=[], z=r['best'][1], s=r['best'][0])
        # members that were not seeded (beyond the seed cap, or whose seed failed) go to the
        # landing that most of the structure's seeds reached
        seeded = {i for v in land.values() for i in v['nodes']}
        rest = [i for i in r['members'] if i not in seeded]
        dom = max(land.items(), key=lambda kv: len(kv[1]['nodes']))[0]
        land[dom]['nodes'] += rest
        for key, v in land.items():
            s, free, fx = full_config(r['slots'], r['nfree'], v['z'])
            items.append(dict(gk=gk, r=r, s=s, cfg=free + fx, z=v['z'],
                              members=v['nodes'], nnodes=len(v['nodes'])))
    # cheap exact analysis of every landing: which squares actually carry force
    for it in items:
        try:
            an = A.analyse(tuple(it['r']['slots']), it['r']['nfree'], it['z'])
        except Exception:
            an = {}
        f = collections.defaultdict(float)
        for k, v in (an.get('resultant') or {}).items():
            x, y = k.split('|'); f[x] += v; f[y] += v
        names = [f'f{i}' for i in range(it['r']['nfree'])] + list(it['r']['slots'])
        it['loaded'] = [q for nm, q in zip(names, it['cfg']) if f[nm] > 1e-6]
        it['loaded_names'] = [nm for nm in names if f[nm] > 1e-6]
    items.sort(key=lambda d: (-d['nnodes'], d['s']))

    # A shadow is a VALUE of s*, not a point.  Every family here contains a strut/rattler with a
    # flat direction, so its minimum is a manifold: the three-square core of the k7 pinwheel is
    # identical in all 5 of its landings, only the loose fourth square slides (0.15 in x) -- the
    # 0.05/3 deg point rule would call those five different shadows.  A106 reached the same
    # conclusion independently (measurements.md 2.1: "a shadow is a value of s*, not a point").
    # So: group by s*, and report inside each entry how many distinct minimised configurations
    # (the brief's 0.05/3 deg rule on the load-bearing squares, modulo D4) share it.
    shadows = []
    byval = collections.OrderedDict()
    for it in items:
        byval.setdefault(round(it['s'], 5), []).append(it)
    for val, group in byval.items():
        cfgs = []
        for it in group:
            hit = None
            for c in cfgs:
                if len(c['loaded']) == len(it['loaded']):
                    for nm, fn in L.d4_ops(it['s']):
                        if L.match(c['loaded'], [tuple(fn(*q)) for q in it['loaded']]):
                            hit = c; break
                if hit:
                    break
            if hit:
                hit['n'] += it['nnodes']
            else:
                cfgs.append(dict(loaded=it['loaded'], n=it['nnodes']))
        shadows.append(dict(s=group[0]['s'], cfg=group[0]['cfg'], structs=group,
                            nnodes=sum(g['nnodes'] for g in group), nconfigs=len(cfgs)))
    shadows.sort(key=lambda sh: -sh['nnodes'])
    print(f'{len(items)} landings -> {len(shadows)} distinct shadow values '
          f'({sum(sh["nnodes"] for sh in shadows)} alive nodes)', flush=True)

    # ---------- confirm + analyse each shadow on its principal structure
    nconf = int(os.environ.get('A107_CONFIRM', 100))
    out = []
    for si, sh in enumerate(shadows):
        prim = max(sh['structs'], key=lambda d: d['nnodes'])
        r = prim['r']
        slots, nf = tuple(r['slots']), r['nfree']
        seeds = []
        for idx in (prim['members'] or prim['r']['members'])[:20]:
            F = M.canon_free(nodes[idx]['cfg'], nodes[idx]['struct_op'], S0)
            if len(F) == nf:
                seeds.append(F)
        conf = M.run_structure(slots, nf, seeds, nrand=nconf, rng=random.Random(777 + si))
        # keep the landing this shadow IS; the confirmation run's global minimum is reported
        # separately (it can be a different, lower shadow of the same slot set).
        z = np.array(prim['z'])
        s, free, fx = full_config(slots, nf, z)
        an = A.analyse(slots, nf, z)
        tilts = [math.degrees(L.tmod(f[2])) for f in free]
        common = (max(tilts) - min(tilts) < 0.5) if tilts else False
        rat = A.rattler_test(slots, nf, z)
        sweep = A.tilt_sweep(slots, nf, z) if common and nf >= 2 else None
        rec = dict(id=f'S{si+1:02d}', s=s, ds=s - SHAT, nnodes=sh['nnodes'], slots=list(slots), nfree=nf,
                   free=[list(map(float, f)) for f in free], nsquares=nf + len(slots),
                   common_tilt=(sum(tilts) / len(tilts)) if common else None, tilts=tilts,
                   analysis=an, rattlers=rat, sweep=sweep, nconfigs=sh['nconfigs'],
                   loaded=prim.get('loaded_names', []),
                   structs=[dict(gk=d['gk'], src=d['r']['src'], skel=list(d['r']['skel']),
                                 slots=d['r']['slots'], nfree=d['r']['nfree'],
                                 nnodes=d['nnodes'], members=d['members'],
                                 minima=d['r']['minima'], nfeas=d['r']['nfeas'], nstart=d['r']['nstart'])
                           for d in sh['structs']],
                   confirm=dict(nstart=conf['nstart'], nfeas=conf['nfeas'], minima=conf['minima'],
                                best=conf['best'][0] if conf['best'] else None))
        out.append(rec)
        print(f"  {rec['id']} s*={s:.6f} (shat{s-SHAT:+.6f}) k={rec['nsquares']} slots={len(slots)} "
              f"free={nf} nodes={sh['nnodes']} landings={len(sh['structs'])} cfgs={sh['nconfigs']} "
              f"flex={an.get('flexes_fixed_s')} common_tilt={rec['common_tilt']} "
              f"{round(time.time()-t0)}s", flush=True)
    json.dump(out, open(os.path.join(RES, 'shadows.json'), 'w'), indent=1)
    print('wrote results/shadows.json', round(time.time() - t0, 1), 's')

if __name__ == '__main__':
    main()
