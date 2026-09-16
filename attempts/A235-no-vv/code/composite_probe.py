"""Coordinator's probe (2026-09-15): re-classify vertex-on-vertex contacts between non-parallel squares with the
PI's COMPOSITE-EDGE test -- a vertex sitting on the seam of two parallel squares whose edges through the point are
collinear is vertex-on-(composite)-edge, not VV.  Runs on A226's survey records and A217's witnesses."""
import json, math, collections
def verts(c):
    cx, cy, th = c; co, si = math.cos(th), math.sin(th)
    return [(cx + co * x - si * y, cy + si * x + co * y) for x, y in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
def edges(c):
    v = verts(c); return [(v[i], v[(i + 1) % 4]) for i in range(4)]
def tilted(c):
    m = abs(c[2]) % (math.pi / 2); return min(m, math.pi / 2 - m) > 1e-6
def parallel(a, b):
    d = abs((a[2] - b[2]) % (math.pi / 2)); return min(d, math.pi / 2 - d) < 1e-5
def on_line(p, e, tol=1e-5):
    (x1, y1), (x2, y2) = e; return abs((x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1)) < tol
def near(p, q, tol=1e-5): return math.hypot(p[0] - q[0], p[1] - q[1]) < tol
def sep(a, b):
    best = -1e9
    for c in (a, b):
        th = c[2]
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            pa = [ax[0] * x + ax[1] * y for x, y in verts(a)]; pb = [ax[0] * x + ax[1] * y for x, y in verts(b)]
            best = max(best, min(pa) - max(pb), min(pb) - max(pa))
    return best
def composite_side(sq, s, P):
    for c in range(len(sq)):
        if c == s or not parallel(sq[s], sq[c]) or not any(near(P, q) for q in verts(sq[c])): continue
        for es in edges(sq[s]):
            if not on_line(P, es): continue
            for ec in edges(sq[c]):
                if on_line(P, ec) and on_line(es[0], ec) and on_line(es[1], ec): return True
    return False
def vv_contacts(sq):
    out = []
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            if parallel(sq[i], sq[j]) or not (tilted(sq[i]) or tilted(sq[j])) or abs(sep(sq[i], sq[j])) > 1e-6: continue
            for P in verts(sq[i]):
                if any(near(P, q) for q in verts(sq[j])):
                    out.append((i, j, 'VE-composite' if composite_side(sq, i, P) or composite_side(sq, j, P) else 'VV-genuine'))
    return out
if __name__ == '__main__':
    tot = collections.Counter()
    for l in open('attempts/A226-one-flush/results/survey226.jsonl', encoding='utf-8', errors='replace'):
        r = json.loads(l); z = r.get('z') or r.get('poses') or r.get('squares')
        sq = [tuple(p[:3]) for p in z] if isinstance(z[0], (list, tuple)) else [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(r['n'])]
        c = collections.Counter(k for _, _, k in vv_contacts(sq)); tot.update(c)
        if c: print(r['label'], dict(c))
    print('survey total:', dict(tot))
    per = collections.defaultdict(collections.Counter)
    for l in open('attempts/A217-torque-probe/results/witnesses217.jsonl', encoding='utf-8', errors='replace'):
        r = json.loads(l); z = r['z']; n = (len(z) - 1) // 3; sq = [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(n)]
        per[r.get('cls')].update(k for _, _, k in vv_contacts(sq))
    for cls in sorted(per, key=str): print(cls, dict(per[cls]))
