"""A280 VERIFIER -- independent re-derivation of tree280's leaves (certs/tree280_<cell>.jsonl.gz).
Shares no code with the tree side (prune280 / geom273 / drop4273 are NOT imported); it reuses A273's VERIFIER
(verify273: mpmath.iv h_v window, shapely q-cells with inscribed-128-gon penumbras, the coverage replay, the split),
and re-types the three A280 prunes in mpmath.iv (80 bits, directed rounding):
  DLOW  D_hi < (cos th - sin ph) tan(min(th, ph)) over the box   (strip_jam.md (D-low), [T]);
  SEP   one of the 8 edge normals of T_u'' / X'' separates the two quadrilaterals for every parameter of the box;
  LOWF  h_v >= LOWB(th) - c  (ring_domain.md (F4), cases (a)-(b): 1/sqrt2 + tan(45 - th/2); case (c):
        G = cos al + (c - s) + (c + s - 1) tan al, al in 1-deg iv pieces on [45, 89] + the tail [89, 90))
        exceeds every h_v upper bound (1, X_top <= s^, the open box).
Every leaf: PRUNE:* -> one of the verifier's prunes on the leaf, else re-proved as a CERT leaf; CERT -> prunes or
q-cells down to h = 1/8192; failing that, bisected by the tree's split (depth <= 6); still open -> DISAGREE.
    python verify280.py <cell|all> -> results/verify280_<cell>.json, results/verify280_index.jsonl"""
import gzip
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'A273-disc-lemma', 'code')))
import verify273 as V                                                 # noqa: E402
from mpmath import iv                                                 # noqa: E402

iv.prec = 80
ATT = os.path.abspath(os.path.join(HERE, '..'))
CERTS, RES = os.path.join(ATT, 'certs'), os.path.join(ATT, 'results')
I, DEG = V.I, math.pi / 180
PI = iv.pi


def mp_dlow(b):
    th, ph, dd = I(*b[1]), I(*b[3]), I(*b[2])
    a = iv.cos(th) - iv.sin(ph)
    if a.a <= 0:
        return False
    m = I(min(b[1][0], b[3][0]))
    return dd.b < (a * iv.tan(m)).a


def mp_sep(b):
    s, c, sp, cp = V.trig(b)
    md = -I(*b[2])
    z = I(0)
    T = [(s, -c - s), (s + c, -c), (c, z), (z, -s)]
    X = [(sp, md), (sp + cp, md + sp), (cp, md + sp + cp), (z, md + cp)]
    for P in (T, X):
        for k in range(4):
            p, q = P[k], P[(k + 1) % 4]
            n = (p[1] - q[1], q[0] - p[0])
            g = [n[0] * (x[0] - t[0]) + n[1] * (x[1] - t[1]) for x in X for t in T]
            if min(v.a for v in g) >= 1e-12 or max(v.b for v in g) <= -1e-12:
                return True
    return False


def mp_lowb(th):
    t = I(*th)
    ab = iv.sqrt(I(0.5)) + iv.tan(PI / 4 - I(th[1]) / 2)
    c, s = iv.cos(t), iv.sin(t)
    k2 = c + s - 1
    gc = (c - s).a + max(0.0, float(k2.a)) * float(iv.tan(89 * PI / 180).a)    # tail: cos al > 0
    for i in range(45, 89):
        al = iv.mpf([i, i + 1]) * PI / 180
        gc = min(gc, float((iv.cos(al) + (c - s) + k2 * iv.tan(al)).a))
    return min(float(ab.a), gc)


def mp_lowf(b):
    s, c, sp, cp = V.trig(b)
    hu, dd = I(*b[0]), I(*b[2])
    lo = mp_lowb(b[1]) - float(c.b) - 1e-15
    ups = [1.0, float((V.SHAT - (sp + cp) - (c + s) + dd).b)]
    ob = c + s - s * c - hu * c
    if s.a > 1e-9:
        ups.append(float((ob / s).b) if ob.b > 0 else -1.0)
    return lo > min(ups) + 1e-12


def mp_prune(b):
    return b[0][0] >= 1.0 or V.hv_window_empty(b, V.trig(b)) or mp_dlow(b) or mp_sep(b) or mp_lowf(b)


def verify_box(b, depth=0):
    if mp_prune(b) or V.vcells(b)[0]:
        return True, 1
    if depth >= 6:
        return False, 1
    n = 1
    for ch in V.split(b):
        ok, nc = verify_box(ch, depth + 1)
        n += nc
        if not ok:
            return False, n
    return True, n


def verify_cell(name):
    leaves = [json.loads(l) for l in gzip.open(os.path.join(CERTS, 'tree280_%s.jsonl.gz' % name), 'rt') if l.strip()]
    ti, pj = map(int, name[1:].split('_')[:2])
    cell = [(0.0, 1.0), (ti * 5 * DEG, (ti + 1) * 5 * DEG), (0.0, V.DMAX), (pj * 5 * DEG, (pj + 1) * 5 * DEG)]
    cov_ok, cov_msg = V.coverage(cell, leaves)
    out = dict(cell=name, leaves=len(leaves), coverage=cov_ok, coverage_msg=cov_msg, cert_ok=0, prune_ok=0, open=0,
               bisected=0, disagree=[])
    for l in leaves:
        b, v = [tuple(x) for x in l['box']], l['v']
        if v == 'OPEN':
            out['open'] += 1
            continue
        if v.startswith('PRUNE') and mp_prune(b):
            out['prune_ok'] += 1
            continue
        ok, n = verify_box(b)
        out['bisected'] += (n > 1)
        if ok:
            out['cert_ok'] += 1
        else:
            out['disagree'].append(b)
    good = cov_ok and not out['disagree']
    out['verdict'] = ('PASS' if good else 'FAIL') + ('' if out['open'] == 0 else ' (%d OPEN leaves)' % out['open'])
    json.dump(out, open(os.path.join(RES, 'verify280_%s.json' % name), 'w'), indent=1)
    row = {k: out[k] for k in ('cell', 'leaves', 'coverage', 'cert_ok', 'prune_ok', 'open', 'bisected', 'verdict')}
    with open(os.path.join(RES, 'verify280_index.jsonl'), 'a') as f:
        f.write(json.dumps(dict(row, disagree=len(out['disagree']))) + '\n')
    print(json.dumps(row), flush=True)
    return out


if __name__ == '__main__':
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x00004000)
        k32.SetProcessAffinityMask(k32.GetCurrentProcess(), 0xFFFF)
    except Exception:
        pass
    os.makedirs(RES, exist_ok=True)
    verify_cell(sys.argv[1])
