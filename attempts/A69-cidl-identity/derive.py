"""A69 phase 1 -- reduce the A22 curated system on the certified structure slice.

Substitutions (all certified EXACT at z-hat by A22 headline item 2 / notes.md S3):
  squares 0..5 axis-parallel (theta=0); c0=(1/2,1/2), c1=(3/2,1/2), c2=(S-1/2,1/2),
  c3=(1/2,3/2), c4=(1/2,y4), c5=(S-1/2,S-1/2); squares 6..10 share one angle theta,
  parametrised by t = tan(theta/2): cos=(1-t^2)/(1+t^2), sin=2t/(1+t^2).

Output: the distinct nonzero reduced rows (polynomials in Q[t][y4, x6..y10, S],
linear in the 12 non-t unknowns), their provenance, and the linear-system structure.
"""
import json, os, sys
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(HERE, '..', 'A22-local-rigidity', 'results', 'krawczyk_cert.json')

t, S, y4 = sp.symbols('t S y4')
cents = {i: (sp.Symbol(f'x{i}'), sp.Symbol(f'y{i}')) for i in range(6, 11)}
XVARS = [y4] + [v for i in range(6, 11) for v in cents[i]] + [S]  # 12 unknowns

half = sp.Rational(1, 2)
cs = (1 - t**2) / (1 + t**2)
sn = 2 * t / (1 + t**2)

# pinned data: centre (cx, cy), (cos, sin) of angle
PIN = {
    0: ((half, half), (1, 0)),
    1: ((sp.Rational(3, 2), half), (1, 0)),
    2: ((S - half, half), (1, 0)),
    3: ((half, sp.Rational(3, 2)), (1, 0)),
    4: ((half, y4), (1, 0)),
    5: ((S - half, S - half), (1, 0)),
}
for i in range(6, 11):
    PIN[i] = (cents[i], (cs, sn))

HALF = [(-half, -half), (half, -half), (half, half), (-half, half)]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def corner(i, k):
    (cx, cy), (c, s_) = PIN[i]
    hx, hy = HALF[k]
    return (cx + hx * c - hy * s_, cy + hx * s_ + hy * c)

def row_expr(con):
    kind = con['kind']
    if kind == 'wall':
        qx, qy = corner(con['i'], con['corner'])
        w = con['wall']
        return {'x=0': qx, 'y=0': qy, 'x=s': S - qx, 'y=s': S - qy}[w]
    if kind == 'edge':
        i, j = con['i'], con['j']
        qx, qy = corner(i, con['corner'])
        (cjx, cjy), (c, s_) = PIN[j]
        nhx, nhy = NHAT[con['edge']]
        nx, ny = nhx * c - nhy * s_, nhx * s_ + nhy * c
        return nx * (qx - cjx) + ny * (qy - cjy) - half
    if kind == 'dist':
        (ax, ay), _ = PIN[con['i']]
        (bx, by), _ = PIN[con['j']]
        return (ax - bx)**2 + (ay - by)**2 - 1
    raise ValueError(kind)

d = json.load(open(CERT))
rows = []
for idx, con in enumerate(d['constraints']):
    if con['kind'] == 'angeq':
        continue  # consumed by the common-angle substitution
    e = sp.together(sp.expand(row_expr(con)))
    num, den = sp.fraction(sp.cancel(e))
    poly = sp.expand(num) if den == 1 else None
    if poly is None:
        # den must be a positive rational times (1+t^2)^m
        m = sp.Poly(den, t).degree() // 2
        lc = sp.simplify(den / (1 + t**2)**m)
        assert lc.is_Rational and lc > 0, (con, den)
        poly = sp.expand(num / lc)
    rows.append((idx, con.get('name') or con, poly))

# classify
zero, nonzero = [], []
for idx, name, p in rows:
    if p == 0:
        zero.append((idx, name))
    else:
        nonzero.append((idx, name, p))

print('identically-zero reduced rows (%d):' % len(zero))
print('  ', [n for _, n in zero])
print('nonzero reduced rows (%d):' % len(nonzero))

# find duplicates up to rational multiple
def normkey(p):
    pp = sp.Poly(p, *( [t] + XVARS ))
    coeffs = pp.coeffs()
    lead = coeffs[0]
    return sp.Poly(p / lead, *([t] + XVARS))

groups = []
for idx, name, p in nonzero:
    k = normkey(p)
    for g in groups:
        if g['key'] == k:
            g['members'].append(name)
            break
    else:
        groups.append({'key': k, 'members': [name], 'poly': p, 'idx': idx})

print('distinct rows after collapsing rational multiples: %d' % len(groups))
for g in groups:
    print('  ', g['members'])

# linearity check in XVARS
for g in groups:
    for v in XVARS:
        assert sp.degree(g['poly'], v) <= 1, (g['members'], v)
    # no products of two x-vars
    pp = sp.Poly(g['poly'], *XVARS)
    for mon in pp.monoms():
        assert sum(mon) <= 1, (g['members'], mon)
print('all rows linear in the 12 unknowns: OK')

# build M x = b over QQ[t]
M = sp.zeros(len(groups), 12)
b = sp.zeros(len(groups), 1)
for r, g in enumerate(groups):
    p = sp.expand(g['poly'])
    for cidx, v in enumerate(XVARS):
        M[r, cidx] = sp.expand(sp.diff(p, v))
        assert sp.simplify(sp.diff(M[r, cidx], v)) == 0
    b[r, 0] = -sp.expand(p.subs({v: 0 for v in XVARS}))

# generic rank via a random rational t
t0 = sp.Rational(37, 101)
Mn = M.subs(t, t0)
print('generic rank of M (%dx12): %d' % (len(groups), Mn.rank()))
Aug = Mn.row_join(b.subs(t, t0))
print('generic rank of [M|b]: %d' % Aug.rank())

import pickle
with open(os.path.join(HERE, 'results', 'reduced_system.pkl'), 'wb') as f:
    pickle.dump({'groups': [(g['members'], sp.srepr(g['poly'])) for g in groups],
                 'M': sp.srepr(M), 'b': sp.srepr(b),
                 'xvars': [str(v) for v in XVARS]}, f)
print('saved results/reduced_system.pkl')
