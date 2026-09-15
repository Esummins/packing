import sys, os, json, time, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G, opt217 as O
here = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(os.path.join(here, '../../A85-k0-route/results/cp85_k0_search.json')))
def load(o):
    z = np.zeros(34)
    for i, (x, y) in enumerate(o['centres']):
        z[3*i], z[3*i+1], z[3*i+2] = x, y, math.radians(o['tilts_deg'][i])
    z[33] = o['s']; return z
opt = sorted(c['optima'], key=lambda o: o['s'])
for idx in range(int(sys.argv[1]), int(sys.argv[2])):
    o = opt[idx]; zc = load(o)
    sm0 = O.summary(zc)
    t0 = time.time(); z, h = O.local_opt(zc); sm = O.summary(z)
    print('cp85', idx, 'raw s %.6f res %.2e rows %d' % (sm0['s'], sm0['fj_res'], sm0['n_rows']), '| polish s %.6f res %.2e rows %d settled %d k0 %s outer %d %.1fs' % (sm['s'], sm['fj_res'], sm['n_rows'], sm['n_settled'], sm['k0'], len(h), time.time()-t0), flush=True)
    for tm in (3, 10):
        t0 = time.time(); z, h = O.local_opt(zc, tmin=math.radians(tm)); sm = O.summary(z, tmin=math.radians(tm))
        print('   tilt%d s %.6f res %.2e rows %d tb %d settled %d outer %d %.1fs' % (tm, sm['s'], sm['fj_res'], sm['n_rows'], sm['n_tiltbound_active'], sm['n_settled'], len(h), time.time()-t0), flush=True)
