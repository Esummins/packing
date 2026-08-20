"""Phase 4: (a) validity margin conditions for the 16 edge constraints over
N(r): tangential strictly inside (-1/2,1/2), depth > -1/2; (b) certificate
residual beta(r) = max_i,sigma ||rho||_1 (need < 1); (c) inactive-constraint
margins over N (diagnostics: pair SAT separations, wall gaps)."""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a22lib import *
from fractions import Fraction
from mpmath import mp, iv

mp.dps = 60
iv.dps = 60

z0, ex = load_z0()
cons = curated_constraints(ex)
certs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'results', 'farkas_certs.json')))
S = certs['S']
HALF_ = Fraction(1, 2)

def beta_of(r):
    B = z_box(z0, r)
    Grows = [grad_g(iv, B, cons[k]) for k in S]
    worst = 0.0
    for cert in certs['certificates']:
        i, sg = cert['i'], cert['sigma']
        nu = str_frac(cert['nu'])
        mu = [str_frac(x) for x in cert['mu']]
        acc = {}
        for m, row in zip(mu, Grows):
            if m == 0:
                continue
            mi = cnum(iv, m)
            for j, v in row.items():
                acc[j] = acc.get(j, iv.mpf(0)) + mi * v
        # rho_j = sg*delta_ij + nu*delta_j33 - acc_j
        l1 = 0.0
        for j in range(NV):
            t = acc.get(j, iv.mpf(0))
            lo, hi = -t, -t
            base = (sg if j == i else 0) + (nu if j == 33 else 0)
            rho = cnum(iv, Fraction(base)) - t if base else -t
            l1 += max(abs(float(rho.a)), abs(float(rho.b)))
        worst = max(worst, l1)
    return worst

def validity_of(r):
    B = z_box(z0, r)
    tan_margin = 1.0
    depth_ok = True
    worst_name = None
    for c in cons:
        if c['kind'] != 'edge':
            continue
        dep, tan = edge_aux(iv, B, c)
        m = 0.5 - max(abs(float(tan.a)), abs(float(tan.b)))
        if m < tan_margin:
            tan_margin, worst_name = m, con_name(c)
        if not (dep.a > -0.5):
            depth_ok = False
    return tan_margin, worst_name, depth_ok

CONTACT_PAIRS = set()
for c in ex['contacts']:
    if c['type'] == 'edge':
        CONTACT_PAIRS.add(tuple(sorted((c['square'], c['other']))))
CONTACT_PAIRS |= {(0, 1), (0, 3), (1, 3)}
print('contact pairs (%d):' % len(CONTACT_PAIRS), sorted(CONTACT_PAIRS))

def inactive_margins(r):
    B = z_box(z0, r)
    minpair, argp = None, None
    for i, j in itertools.combinations(range(11), 2):
        if (i, j) in CONTACT_PAIRS:
            continue
        sep = pair_sep_iv(B, i, j)
        lo = float(sep.a)
        if minpair is None or lo < minpair:
            minpair, argp = lo, (i, j)
    # wall gaps: all 44 corner-min-distances per wall, skipping exact contacts
    wallset = {(c['square'], c['corner'], c['wall']) for c in ex['contacts'] if c['type'] == 'wall'}
    minwall, argw = None, None
    sB = B[33]
    for i in range(11):
        for corner in range(4):
            qx, qy = corner_pos(iv, B, i, corner)
            for wname, val in (('x=0', qx), ('y=0', qy), ('x=s', sB - qx), ('y=s', sB - qy)):
                if (i, corner, wname) in wallset:
                    continue
                lo = float(val.a)
                if minwall is None or lo < minwall:
                    minwall, argw = lo, (i, corner, wname)
    return minpair, argp, minwall, argw

for rname, r in [('1e-3', Fraction(1, 1000)), ('2e-3', Fraction(2, 1000)),
                 ('3e-3', Fraction(3, 1000)), ('4e-3', Fraction(4, 1000)),
                 ('5e-3', Fraction(5, 1000))]:
    b = beta_of(r)
    tm, tn, dok = validity_of(r)
    print('r=%-5s beta=%.4f  tan_margin=%.5f (%s) depth_ok=%s' % (rname, b, tm, tn, dok))

r = Fraction(2, 1000)
mp_, ap, mw, aw = inactive_margins(r)
print('\nat r=2e-3: min inactive pair separation (lower bound): %.6f at %s' % (mp_, ap))
print('           min inactive wall gap: %.6f at %s' % (mw, aw))
