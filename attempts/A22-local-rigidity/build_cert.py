"""Build results/krawczyk_cert.json for the standalone re-checker.

Contents: rational centre z0 (60-digit decimals as exact fractions), radii
r_N (theorem box) and r_0 (tight enclosure), the 38 curated geometric
constraints + 4 angle-equality rows, the two square subsystems
  S  (34 rows, strict-complementarity KKT system; Krawczyk #1)
  S2 (34 rows, angle-equality variant; Krawczyk #2 -> exact structure of z-hat)
with rational preconditioners Y, Y2, the unique multiplier vector lambda > 0
on S, the 68 rational Farkas certificates, pair lists for the feasibility
check, and the claimed numeric bounds the checker verifies."""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a22lib import *
from fractions import Fraction
from mpmath import mp

mp.dps = 80

z0, ex = load_z0()
cons = curated_constraints(ex)
fc = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'results', 'farkas_certs.json')))
S = fc['S']

# append the 4 angle-equality rows (indices 38..41)
for a, b in ((6, 7), (7, 8), (8, 9), (9, 10)):
    cons.append({'kind': 'angeq', 'i': a, 'j': b, 'a03_index': None})

name2idx = {}
for i, c in enumerate(cons):
    name2idx[con_name(c) if c['kind'] != 'angeq' else 'A%d-%d' % (c['i'], c['j'])] = i

# S2: walls minus the three redundant drops, upright-tilted edge rows,
# one row per flush tilted pair, the two dist rows, the four angle rows.
DROPW = {'W0c0[y=0]', 'W2c2[x=s]', 'W5c3[y=s]'}
S2 = []
for i, c in enumerate(cons[:38]):
    nm = con_name(c)
    if c['kind'] == 'wall' and nm not in DROPW:
        S2.append(i)
    elif c['kind'] == 'dist':
        S2.append(i)
    elif c['kind'] == 'edge' and nm in ('E1c2-8e3', 'E2c3-8e0', 'E3c2-7e3',
                                        'E4c1-7e2', 'E4c2-6e3', 'E5c0-9e1',
                                        'E6c1-9e2', 'E7c1-8e2', 'E7c2-9e3',
                                        'E8c2-10e3', 'E9c1-10e2'):
        S2.append(i)
S2 += [name2idx['A6-7'], name2idx['A7-8'], name2idx['A8-9'], name2idx['A9-10']]
assert len(S2) == NV, len(S2)

R_N = Fraction(1, 2000)
R_0 = Fraction(1, 10 ** 50)

zm = z_point(mp, z0)
QY = 10 ** 30


def precond(rows):
    A = mp.zeros(NV, NV)
    for r, k in enumerate(rows):
        for kk, v in grad_g(mp, zm, cons[k]).items():
            A[r, kk] = v
    Yr = mp.inverse(A)
    return [[Fraction(int(mp.floor(Yr[i, j] * QY + mp.mpf('0.5'))), QY)
             for j in range(NV)] for i in range(NV)]


Y = precond(S)
Y2 = precond(S2)

# contact pair bookkeeping
FLUSH_TILTED = {(6, 9): ('E6c1-9e2', 'E9c3-6e0'), (7, 8): ('E7c1-8e2', 'E8c3-7e0'),
                (7, 9): ('E7c2-9e3', 'E9c0-7e1'), (8, 10): ('E8c2-10e3', 'E10c0-8e1'),
                (9, 10): ('E9c1-10e2', 'E10c3-9e0')}
UPRIGHT_TILTED = {(1, 8): 'E1c2-8e3', (2, 8): 'E2c3-8e0', (3, 7): 'E3c2-7e3',
                  (4, 6): 'E4c2-6e3', (4, 7): 'E4c1-7e2', (5, 9): 'E5c0-9e1'}
FLUSH_UPRIGHT = [(0, 1), (0, 3), (1, 3)]
allcontact = set(FLUSH_TILTED) | set(UPRIGHT_TILTED) | set(FLUSH_UPRIGHT)
NONCONTACT = [list(p) for p in itertools.combinations(range(11), 2)
              if p not in allcontact]
assert len(NONCONTACT) == 55 - 14

exact_sanity = [name2idx[b] for _, b in FLUSH_TILTED.values()]
exact_sanity += [name2idx['A%d-%d' % ab] for ab in ((6, 7), (7, 8), (8, 9), (9, 10))]

spec = []
for c in cons:
    d = {k: v for k, v in c.items() if k != 'a03_index'}
    d['name'] = con_name(c) if c['kind'] != 'angeq' else 'A%d-%d' % (c['i'], c['j'])
    spec.append(d)

cert = {
    'description': 'A22 strict local optimality certificate for the Trump 11-square packing',
    'variables': '(cx_i, cy_i, theta_i) for squares 0..10, then s; 34 coordinates',
    'z0': [frac_str(x) for x in z0],
    'r_N': frac_str(R_N),
    'r_0': frac_str(R_0),
    'constraints': spec,
    'S': S,
    'S2': S2,
    'Y': [[frac_str(v) for v in row] for row in Y],
    'Y2': [[frac_str(v) for v in row] for row in Y2],
    'lambda': fc['lambda'],
    'certificates': fc['certificates'],
    'contact_edge_pairs': [{'pair': list(p), 'con': name2idx[nm]}
                           for p, nm in sorted(UPRIGHT_TILTED.items())],
    'flush_tilted_pairs': [{'pair': list(p), 'row_in_S2': name2idx[a],
                            'second_row': name2idx[b]}
                           for p, (a, b) in sorted(FLUSH_TILTED.items())],
    'flush_upright_pairs': FLUSH_UPRIGHT,
    'noncontact_pairs': NONCONTACT,
    'exact_rows_sanity': exact_sanity,
    'claims': {
        'beta_max': 0.65,
        'krawczyk_ratio_at_r_N': 0.12,
        'centre_residual_max': 1e-55,
        'tan_margin_min': 0.015,
        'lambda_residual_max': 1e-30,
        'nu_max': 58.0,
    },
}
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'krawczyk_cert.json')
json.dump(cert, open(path, 'w'))
print('wrote', path, '(%.1f KB)' % (os.path.getsize(path) / 1024))
