import sys, os, json, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G, opt217 as O, stress217 as S
here = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(here, '../../A03-upper-reconstruct/trump11_float.json')))
zt = np.concatenate([np.array(T['X']).reshape(-1), [T['s']]])
r = S.analyse(zt)
print('TRUMP fj', r['fj'], 'rows', r['n_rows'], 'tot wall torque', r['total_wall_torque_about_centre'], 'pressure', r['wall_pressure'], 'moments', r['wall_moment'])
for p in r['squares']:
    print(' sq %2d tilt %6.2f W %.4f tau_wall %+.5f pred %s hold %+.5f eq_t %.1e eq_f %.1e' % (p['i'], p['tilt_deg'], p['W'], p['tau_wall'], p['tau_wall_pred'], p['tau_contact'], p['eq_torque'], p['eq_force']))
for cn, e in r['corners'].items():
    print(cn, 'settled', e['settled'], 'T', round(e['T_corner'],5), 'range', e['T_corner_range'], [(m['i'], round(m['tilt_frame_deg'],2), m['chi'], m['walls'], round(m['tau_wall_frame'],5), round(m['tau_hold_frame'],5)) for m in e['members']])
