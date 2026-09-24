"""A280 DIAGNOSE A273's OPEN leaves at steep C.  Per cell: every OPEN leaf through prune280 (the missing H2 half:
int X meets int T_u), survivors counted; for sampled leaves (the smallest OPEN boxes, where the tree gave up) the
midpoint's H2 status by exact polygon geometry (shapely area of X n T_u, and of X n C), the [M] DROP slack of
slack273.best (exact support-function gap, grid + Nelder-Mead) and the failing q-cell of A273's own box test.
    python diag280.py <cell> [<cell> ...] -> results/diag280_<cell>.json"""
import gzip
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prune280 as P8                                                 # noqa: E402
import drop4273 as D4                                                 # noqa: E402
import slack273 as SL                                                 # noqa: E402
from shapely.geometry import Polygon                                  # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
A273C = os.path.join(ATT, '..', 'A273-disc-lemma', 'certs')
RES = os.path.join(ATT, 'results')
DEG = math.pi / 180


def polys(m):
    hu, th, dd, ph = m
    c, s, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    T = Polygon([(s, -c - s), (s + c, -c), (c, 0.0), (0.0, -s)])
    C = Polygon([(hu + s, -c - s), (hu + s + c, -c), (hu + c, 0.0), (hu, -s)])
    X = Polygon([(sp, -dd), (sp + cp, -dd + sp), (cp, -dd + sp + cp), (0.0, -dd + cp)])
    return T, C, X


def five(m, hv=0.05):
    """the 5-parameter point (h_u, h_v, theta, X_low, phi) of slack273 at an h_v (the lemma is h_v-invariant)."""
    hu, th, dd, ph = m
    return [hu, hv, th, hv + math.cos(th) + math.sin(th) - dd, ph]


def sample(m):
    T, C, X = polys(m)
    sl, z = SL.best(five(m))
    return dict(m=[m[0], m[1] / DEG, m[2], m[3] / DEG], XnTu=X.intersection(T).area, XnC=X.intersection(C).area,
                dlow_bound=(math.cos(m[1]) - math.sin(m[3])) * math.tan(min(m[1], m[3])), slack=sl, qp=z)


def run(cell, nsamp=4):
    rows = [json.loads(l) for l in gzip.open(os.path.join(A273C, 'tree273_%s.jsonl.gz' % cell), 'rt')]
    op = [r for r in rows if r['v'] == 'OPEN']
    kill, surv = {}, []
    for r in op:
        k = P8.prune280(r['box'])
        if k:
            kill[k] = kill.get(k, 0) + 1
        else:
            surv.append(r)
    vol = lambda b: math.prod((x[1] - x[0]) for x in b)
    vo, vs = sum(vol(r['box']) for r in op), sum(vol(r['box']) for r in surv)
    op.sort(key=lambda r: vol(r['box']))
    out = dict(cell=cell, leaves=len(rows), open=len(op), killed=kill, survivors=len(surv),
               open_vol=vo, surv_vol=vs, samples=[], surv_samples=[])
    for r in op[:nsamp]:
        b = r['box']
        m = [0.5 * (x[0] + x[1]) for x in b]
        v, st = D4.box_test4(b)
        out['samples'].append(dict(box=b, box_test=v, at=st.get('at'), prune280=P8.prune280(b), **sample(m)))
    surv.sort(key=lambda r: vol(r['box']))
    for r in surv[:nsamp]:
        b = r['box']
        m = [0.5 * (x[0] + x[1]) for x in b]
        out['surv_samples'].append(dict(box=b, **sample(m)))
    os.makedirs(RES, exist_ok=True)
    json.dump(out, open(os.path.join(RES, 'diag280_%s.json' % cell), 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('cell', 'leaves', 'open', 'killed', 'survivors', 'open_vol', 'surv_vol')}))
    for s in out['samples'] + out['surv_samples']:
        print('  m', [round(v, 4) for v in s['m']], 'XnTu %.2e XnC %.2e dlow %.3f slack %+.5f' % (
            s['XnTu'], s['XnC'], s['dlow_bound'], s['slack']), s.get('box_test'), s.get('prune280'), flush=True)


def lower_priority():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


if __name__ == '__main__':
    lower_priority()
    for c in sys.argv[1:]:
        run(c)
