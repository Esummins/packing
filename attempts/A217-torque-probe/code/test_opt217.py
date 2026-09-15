import sys, os, json, time, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G, opt217 as O
here = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(here, '../../A03-upper-reconstruct/trump11_float.json')))
zt = np.concatenate([np.array(T['X']).reshape(-1), [T['s']]])
t0 = time.time(); z, h = O.local_opt(zt); sm = O.summary(z)
print('TRUMP polish', sm['s'], 'fj_res', sm['fj_res'], 'rows', sm['n_rows'], 'settled', sm['n_settled'], 'outer', len(h), '%.1fs' % (time.time()-t0))
a = json.load(open(os.path.join(here, '../../A37-cp-atlas/results/atlas_final.json')))
e = a['entries'][11]
za = np.array([v for row in e['canonical_sig'] for v in row] + [e['s_min_float']])
sm0 = O.summary(za); print('atlas11 raw s', sm0['s'], 'fj_res', sm0['fj_res'], 'rows', sm0['n_rows'], 'gaps', sm0['min_pair_gap'], sm0['min_wall_gap'])
t0 = time.time(); z, h = O.local_opt(za); sm = O.summary(z)
print('atlas11 polish', sm['s'], 'fj_res', sm['fj_res'], 'rows', sm['n_rows'], 'settled', sm['n_settled'], 'outer', len(h), '%.1fs' % (time.time()-t0), h[-3:])
c = json.load(open(os.path.join(here, '../../A85-k0-route/results/cp85_k0_search.json')))
for idx in (0, 1, 2):
    o = c['optima'][idx]
    x = np.array(o['x']); zc = x if len(x) == 34 else None
    sm0 = O.summary(zc); print('cp85', idx, 'raw s', sm0['s'], 'fj_res', sm0['fj_res'], 'rows', sm0['n_rows'], 'settled', sm0['n_settled'])
    t0 = time.time(); z, h = O.local_opt(zc); sm = O.summary(z)
    print('   polish', sm['s'], 'fj_res', sm['fj_res'], 'rows', sm['n_rows'], 'settled', sm['n_settled'], 'k0', sm['k0'], 'outer', len(h), '%.1fs' % (time.time()-t0))
    t0 = time.time(); z, h = O.local_opt(zc, tmin=math.radians(3)); sm = O.summary(z, tmin=math.radians(3))
    print('   tilt3 ', sm['s'], 'fj_res', sm['fj_res'], 'rows', sm['n_rows'], 'tb', sm['n_tiltbound_active'], 'settled', sm['n_settled'], 'outer', len(h), '%.1fs' % (time.time()-t0))
rng = np.random.default_rng(1)
for k in range(2):
    t0 = time.time(); z0 = O.random_start(rng); t1 = time.time()
    z, h = O.local_opt(z0); sm = O.summary(z)
    print('random', k, 'start s', z0[33], 'feas %.1fs' % (t1-t0), '-> s', sm['s'], 'fj_res', sm['fj_res'], 'rows', sm['n_rows'], 'settled', sm['n_settled'], 'outer', len(h), '%.1fs' % (time.time()-t1), 'gaps', sm['min_pair_gap'], sm['min_wall_gap'])
