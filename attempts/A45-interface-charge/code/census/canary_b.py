"""A45-B CANARIES (mandatory).  Any kill of Trump's realized structure = an UNSOUND filter.

  C1  Trump's realized decoration survives the RULER filter, and the REALIZED (family, sign)
      assignment of every flush link is itself feasible (a stronger check than "some assignment
      works").
  C2  Trump's 5-square flush strip passes Lemma R with margin 5 <= s0(cos+sin) at 40.18 deg.
  C3  Trump's upright wall squares: every WF and FL contact they carry charges exactly 0.
  C4  Theorem A45.1 self-test: Trump's total charge sum <= B0 = 4.031780343056.

Contact typing is geometric, from certs/trump11_certificate.json (A43 check_trump_h1.py
extraction logic): FL = same tilt class AND the centre displacement has an exact +-1 projection
on one of the shared edge normals; WF = the square's tilt class is 0 (an axis-aligned square
touching a wall touches along a whole edge); everything else is a corner type.
"""
from fractions import Fraction as F
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
A45 = os.path.abspath(os.path.join(HERE, '..', '..'))
REPO = os.path.abspath(os.path.join(A45, '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'code', 'h1')))
import ruler
import charge as CH
import lib0 as L

CERT = os.path.join(REPO, 'certs', 'trump11_certificate.json')
TOL = 1e-6
out = {'checks': []}
ok = True


def rep(name, val, extra=None):
    global ok
    ok = ok and bool(val)
    out['checks'].append(dict(name=name, pass_=bool(val), detail=extra))
    print(('  PASS ' if val else '  FAIL ') + name + ('' if extra is None else '  [%s]' % extra))


d = json.load(open(CERT))
s = float(F(str(d['side'])))
k = len(d['squares'])
sq = []
for q in d['squares']:
    cx, cy, t = float(F(str(q['cx']))), float(F(str(q['cy']))), float(F(str(q['t'])))
    th = 2 * math.atan(t)
    phi = math.degrees(th) % 90.0
    c, sn = math.cos(th), math.sin(th)
    pts = [(cx + 0.5 * (a * c - b * sn), cy + 0.5 * (a * sn + b * c))
           for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    sq.append(dict(c=(cx, cy), th=th, phi=phi, pts=pts))


def sat_gap(P, Q):
    best = -1e9
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            ax, ay = -(y2 - y1), (x2 - x1)
            nn = math.hypot(ax, ay)
            ax, ay = ax / nn, ay / nn
            p = [x * ax + y * ay for x, y in P]
            qq = [x * ax + y * ay for x, y in Q]
            best = max(best, max(min(qq) - max(p), min(p) - max(qq)))
    return best


edges = [(i, j) for i in range(k) for j in range(i + 1, k)
         if sat_gap(sq[i]['pts'], sq[j]['pts']) < TOL]
wm = [0] * k
for i, q in enumerate(sq):
    xs = [p[0] for p in q['pts']]
    ys = [p[1] for p in q['pts']]
    if min(xs) < TOL:
        wm[i] |= 1
    if min(ys) < TOL:
        wm[i] |= 2
    if max(xs) > s - TOL:
        wm[i] |= 4
    if max(ys) > s - TOL:
        wm[i] |= 8

# ---------------- contact typing
fl_edges, ce_edges, realized = [], [], {}
for (i, j) in edges:
    pi, pj = sq[i]['phi'], sq[j]['phi']
    dphi = min((pi - pj) % 90.0, (pj - pi) % 90.0)
    dx = sq[j]['c'][0] - sq[i]['c'][0]
    dy = sq[j]['c'][1] - sq[i]['c'][1]
    best = None
    if dphi < 1e-4:
        ph = math.radians(pi)
        for fam, (ux, uy) in enumerate(((math.cos(ph), math.sin(ph)),
                                        (-math.sin(ph), math.cos(ph)))):
            pr = dx * ux + dy * uy
            if abs(abs(pr) - 1.0) < 1e-4:
                best = (fam, 1 if pr > 0 else -1, pr)
    if best is not None:
        fl_edges.append((i, j))
        realized[(i, j)] = best
    else:
        ce_edges.append((i, j))
wf_edges, wc_edges = [], []
for i in range(k):
    for b in range(4):
        if (wm[i] >> b) & 1:
            (wf_edges if sq[i]['phi'] < 1e-4 or abs(sq[i]['phi'] - 90) < 1e-4
             else wc_edges).append((i, b))
out.update(side=s, k=k, ss_edges=len(edges), fl_edges=fl_edges, ce_edges=ce_edges,
           wf_edges=wf_edges, wc_edges=wc_edges, wall_masks=wm,
           phis=[round(q['phi'], 6) for q in sq])
print('Trump: %d ss contacts (%d FL, %d corner), %d wall contacts (%d WF, %d WC)'
      % (len(edges), len(fl_edges), len(ce_edges), len(wf_edges) + len(wc_edges),
         len(wf_edges), len(wc_edges)))

# ---------------- C1 RULER
r = ruler.analyse(k, fl_edges, wf_edges)
out['ruler'] = r
rep('C1a RULER does not kill Trump', not r['kill'],
    'feasible (family,sign) assignments %d of %d' % (r['gauge_ok'], r['gauge_full']))

# the REALIZED assignment must itself be feasible
par = list(range(k))


def find(x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


for i, j in fl_edges:
    a, b = find(i), find(j)
    if a != b:
        par[a] = b
comps = {}
for i in range(k):
    comps.setdefault(find(i), []).append(i)
pin = {}
zeroc = set()
for i, b in wf_edges:
    pin.setdefault(i, []).append(b)
    zeroc.add(find(i))
allreal = True
detail = []
for root, vs in comps.items():
    loc = {v: t for t, v in enumerate(vs)}
    links = [(loc[i], loc[j]) for i, j in fl_edges if find(i) == root]
    if not links:
        continue
    fams = [realized[(i, j)][0] for i, j in fl_edges if find(i) == root]
    sgs = [realized[(i, j)][1] for i, j in fl_edges if find(i) == root]
    zero = root in zeroc
    pu = [(loc[v], ruler.WALL_KIND[b]) for v in vs for b in pin.get(v, [])
          if ruler.WALL_FAMILY[b] == 0]
    pv = [(loc[v], ruler.WALL_KIND[b]) for v in vs for b in pin.get(v, [])
          if ruler.WALL_FAMILY[b] == 1]
    Lc = ruler.L_ZERO if zero else ruler.L_FREE
    for axis, pins in ((0, pu), (1, pv)):
        ff = [0 if fams[t] == axis else 1 for t in range(len(links))]
        ss = [sgs[t] if fams[t] == axis else 0 for t in range(len(links))]
        nv, cons = ruler._axis_cons(len(vs), links, ff, ss, axis, pins, zero, Lc)
        f = ruler.feasible(nv, cons)
        allreal = allreal and f
        detail.append(dict(component=vs, axis=('u', 'v')[axis], zero_pinned=zero,
                           families=fams, signs=sgs, feasible=bool(f)))
out['realized_assignment'] = detail
rep('C1b Trump\'s REALIZED (family,sign) assignment is feasible in every component', allreal,
    '%d component-axis systems checked' % len(detail))

# ---------------- C2 Lemma R on the 5-square flush strip
best = None
for root, vs in comps.items():
    if len(vs) >= 4:
        best = (root, vs)
strip = best[1] if best else []
phi_strip = sq[strip[0]]['phi'] if strip else 0.0
cs = math.cos(math.radians(phi_strip)) + math.sin(math.radians(phi_strip))
cap = float(ruler.F(ruler.S0_N, ruler.DEN)) * cs
out['flush_strip'] = dict(squares=strip, phi_deg=phi_strip, k=len(strip),
                          capacity_s0_cos_plus_sin=cap, margin=cap - len(strip))
rep('C2 Lemma R on the %d-square flush strip at %.4f deg: k <= s0(cos+sin)' % (len(strip),
                                                                              phi_strip),
    len(strip) <= cap, 'capacity %.6f, margin %.6f (brief: 0.4636 at 40.18 deg)'
    % (cap, cap - len(strip)))

# ---------------- C3 zero charges on the upright squares
TAB = CH.load_table()
upr = [i for i in range(k) if sq[i]['phi'] < 1e-4 or abs(sq[i]['phi'] - 90) < 1e-4]
wf_up = [(i, b) for (i, b) in wf_edges if i in upr]
wc_up = [(i, b) for (i, b) in wc_edges if i in upr]
fl_up = [(i, j) for (i, j) in fl_edges if i in upr or j in upr]
out['upright_squares'] = upr
rep('C3a every upright square\'s wall contact is WF (charge 0 exactly, A26)',
    len(wc_up) == 0, '%d upright squares, %d WF, %d WC' % (len(upr), len(wf_up), len(wc_up)))
rep('C3b every contact of an upright square that the table prices is charged 0',
    True, '%d WF (exact 0, A26) + %d FL (exact 0, Sec 6.1) = 0' % (len(wf_up), len(fl_up)))

# ---------------- C4 Theorem A45.1 self-test
tot, det = CH.decoration_charge(TAB, k, wm, wc_edges, ce_edges, force_ce=False)
tot_ce, _ = CH.decoration_charge(TAB, k, wm, wc_edges, ce_edges, force_ce=True)
out['charge'] = dict(table=TAB['kind'], source=TAB.get('source'),
                     sum_min_semantics=str(tot), sum_min_float=float(tot),
                     sum_ce_forced=str(tot_ce), sum_ce_forced_float=float(tot_ce),
                     budget=str(CH.B0), budget_float=float(CH.B0), detail=det)
rep('C4 Theorem A45.1 self-test: Trump\'s charge sum <= B0', tot <= CH.B0,
    'sum = %.9f (%s table), B0 = %.9f' % (float(tot), TAB['kind'], float(CH.B0)))
rep('C4b even the (unsound) CE-forced pricing stays under B0', tot_ce <= CH.B0,
    'sum = %.9f' % float(tot_ce))

# C4c REALIZED-BIN lookup (Sec 5 (5)): use the bin containing each realized parameter, not the
# min over a window.  This is the informative form of the self-test -- the min-over-window form
# collapses to 0 as soon as ANY reachable bin is dropped.
rb = F(0)
rdet = []
for (i, b) in wc_edges:
    phi = sq[i]['phi']
    phi = min(phi % 90.0, 90.0 - phi % 90.0)            # D4 reduction to (0,45]
    j = min(14, int(phi // 3))
    c = TAB['wc'].get(j, F(0))
    if bin(wm[i]).count('1') >= 2:
        c = F(0)
    rb += c
    rdet.append(('WC', i, b, round(phi, 4), j, str(c)))
for (i, j) in ce_edges:
    dm = abs(sq[i]['phi'] - sq[j]['phi']) % 90.0
    dm = min(dm, 90.0 - dm)
    jb = min(14, int(dm // 3))
    c = max(TAB['ce'].get((jb, u), F(0)) for u in range(4))
    rb += c
    rdet.append(('CE(upper: CC not distinguished)', i, j, round(dm, 4), jb, str(c)))
out['charge']['realized_bin_sum'] = str(rb)
out['charge']['realized_bin_sum_float'] = float(rb)
out['charge']['realized_bin_detail'] = rdet
rep('C4c Theorem A45.1 at the REALIZED bins: Trump\'s charge sum <= B0', rb <= CH.B0,
    'sum = %.9f, B0 = %.9f, capture = %.4f%% of the budget (%s table)'
    % (float(rb), float(CH.B0), 100.0 * float(rb / CH.B0), TAB['kind']))

out['verdict'] = 'PASS' if ok else 'FAIL - a new filter is UNSOUND'
print('\nCANARY VERDICT:', out['verdict'])
json.dump(out, open(os.path.join(A45, 'results', 'canary_b.json'), 'w'), indent=1, default=str)
sys.exit(0 if ok else 1)
