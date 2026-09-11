"""Y0044 g1 round-2 kills of cell 17's BR(1,0) rows: the refuting H poses -- are they in units the round-1 mutual clip
killed (then the H-consistency kill stands on Lemma MC) -- and is Lemma MC itself refutable for them (an admissible free
pose meeting BL(1,0), in any alive BL(1,0) row, disjoint from that H pose)?"""
import json, math, sys
sys.argv = ['x', 'attempts/A203-csp-consistency/certs/csp203_k5_16_interior_Y0044_g1_s0.json', '7', '25']
exec(open('attempts/A203-csp-consistency/scratch/audit203.py', encoding='utf-8').read().split('refuted = 0')[0])
csp1 = cert['csp'][0]
ur = {tuple(int(v) for v in k.strip('[]').split(',')): v for k, v in csp1['unit_rects'].items()}
alive1 = {tuple(u) for u in csp1['unit_alive']}
def unit_of(P):
    cx = sum(x for x, y in P) / 4; cy = sum(y for x, y in P) / 4
    e = P[1][0] - P[0][0], P[1][1] - P[0][1]; th = math.degrees(math.atan2(e[1], e[0])) % 90
    if th < 1e-9: th = 90.0 if th + 90 <= Hb[5] + 1e-6 else th
    hb = Hb; T0, T1 = math.tan(math.radians(hb[4]) / 2), math.tan(math.radians(hb[5]) / 2)
    t = math.tan(math.radians(th) / 2)
    ix = min(7, int((cx - hb[0]) / ((hb[1] - hb[0]) / 8))); iy = min(7, int((cy - hb[2]) / ((hb[3] - hb[2]) / 8)))
    ib = min(7, max(0, int((t - T0) / (T1 - T0) * 8)))
    return (ix, iy, ib)
HH = [P for P in H if not sep(P, R(wb['BL(1,0)']))]
d = [x for x in cert['csp'][1]['dead_opts'] if x['cell'] == 17 and x['S'] == ['BR(1,0)']][0]
A = []
for b0, b1 in d['bins']:
    A += poses(d['hull'], b0, b1, d['S'])
ref = [(P, Q) for P in A for Q in HH if sep(P, Q)]
units = {}
for P, Q in ref:
    u = unit_of(Q); units[u] = units.get(u, 0) + 1
print('refuting pairs', len(ref), 'H units of the refuting H poses (alive1?):', {u: (n, u in alive1) for u, n in units.items()})
# Lemma MC check on the refuting H poses: an admissible free pose meeting BL(1,0) in some alive BL(1,0) row, disjoint?
rows = [o for o in cert['rounds'][0]['free_opts'] if 'BL(1,0)' in o[1]]
hulls = {}
for ci, S, h in rows:
    hulls[ci] = h
Hq = {id(Q): Q for P, Q in ref}
bad = 0
for Q in list(Hq.values())[:40]:
    ok = False
    for ci, h in hulls.items():
        for P in poses(h, 0, 90, ['BL(1,0)']):
            if sep(P, Q): ok = True; break
        if ok: break
    bad += ok
print('refuting H poses checked', min(40, len(Hq)), 'with a disjoint admissible BL(1,0) meeter (Lemma MC refuted):', bad)
