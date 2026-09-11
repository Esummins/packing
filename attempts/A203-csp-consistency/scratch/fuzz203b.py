"""regression: Compat.ok on random trees (groups of leaves; hull-only leaves) equals the brute force over leaf pairs."""
import sys, random
sys.path.insert(0, 'attempts/A203-csp-consistency/code')
import csp203 as C
rng = random.Random(7)
def piece(x, y, w, b0, b1):
    return [0, None, (x, x + w, y, y + w), None, (b0, b1), None]
def group(x, y, n):
    ps = []
    for _ in range(n):
        b0 = rng.uniform(0, 85); ps.append(piece(x + rng.uniform(0, 0.1), y + rng.uniform(0, 0.1), rng.uniform(0.005, 0.03), b0, b0 + rng.uniform(0.3, 5)))
    return C.node_of(ps)
def tree(x, y):
    ks = [group(x + rng.uniform(0, 0.15), y + rng.uniform(0, 0.15), rng.randint(1, 6)) for _ in range(rng.randint(1, 4))]
    if len(ks) == 1:
        return C.Node(ks[0].rect, ks[0].bins, (), None, leaves=ks[0].leaves)
    rect = (min(k.rect[0] for k in ks), max(k.rect[1] for k in ks), min(k.rect[2] for k in ks), max(k.rect[3] for k in ks))
    return C.Node(rect, C.merge_bins([b for k in ks for b in k.bins]), ks)
def leaves_of(n):
    if n.leaves: return [(p[2], p[4]) for p in n.leaves]
    if not n.kids: return [(n.rect, b) for b in n.bins]
    return [l for k in n.kids for l in leaves_of(k)]
bad = 0; n_ex = 0
for it in range(3000):
    A = tree(rng.uniform(0, 1), rng.uniform(0, 1))
    ang = rng.uniform(0, 6.3); d = rng.uniform(0.7, 1.3)
    x = A.rect[0] + d * __import__('math').cos(ang); y = A.rect[2] + d * __import__('math').sin(ang)
    if rng.random() < 0.4:
        b0 = rng.uniform(0, 80); bins = sorted({(b0 + rng.uniform(0, 10), b0 + rng.uniform(0, 10)) for _ in range(3)})
        bins = [(min(b), max(b) + 0.5) for b in bins]
        B = C.Node((x, x + 0.1, y, y + 0.1), C.merge_bins(bins))            # hull-only leaf
    else:
        B = tree(x, y)
    cp = C.Compat(4.0)
    got = cp.ok(A, B)
    want = any(not C.sat_dead(ra, ba, rb, bb) for ra, ba in leaves_of(A) for rb, bb in leaves_of(B))
    if got != want:
        bad += 1
        if bad < 5: print('MISMATCH', it, got, want, B.leaves is not None and len(B.leaves) == 0)
    n_ex += (not want)
print('cases', 3000, 'excluded', n_ex, 'mismatches', bad)

# the mismatches: the numpy block uses the block's max sub-interval count (finer than the scalar per-pair count, hence
# possibly stronger); verify each mismatch by exact pose sampling over every leaf pair (a disjoint pair = a refutation)
import math
def sq(cx, cy, th):
    co, s = math.cos(th), math.sin(th); return [(cx + 0.5 * (dx * co - dy * s), cy + 0.5 * (dx * s + dy * co)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
def sep(P, Q):
    for poly in (P, Q):
        for i in range(4):
            x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % 4]; nx, ny = y0 - y1, x1 - x0
            p = [nx * x + ny * y for x, y in P]; q = [nx * x + ny * y for x, y in Q]
            if max(p) <= min(q) + 1e-12 or max(q) <= min(p) + 1e-12: return True
    return False
rng = random.Random(7)
ref = 0; checked = 0
for it in range(3000):
    A = tree(rng.uniform(0, 1), rng.uniform(0, 1))
    ang = rng.uniform(0, 6.3); d = rng.uniform(0.7, 1.3)
    x = A.rect[0] + d * math.cos(ang); y = A.rect[2] + d * math.sin(ang)
    if rng.random() < 0.4:
        b0 = rng.uniform(0, 80); bins = sorted({(b0 + rng.uniform(0, 10), b0 + rng.uniform(0, 10)) for _ in range(3)})
        bins = [(min(b), max(b) + 0.5) for b in bins]
        B = C.Node((x, x + 0.1, y, y + 0.1), C.merge_bins(bins))
    else:
        B = tree(x, y)
    cp = C.Compat(4.0)
    if cp.ok(A, B):
        continue
    checked += 1
    for ra, ba in leaves_of(A):
        for rb, bb in leaves_of(B):
            for _ in range(40):
                P = sq(rng.uniform(ra[0], ra[1]), rng.uniform(ra[2], ra[3]), math.radians(rng.uniform(*ba)))
                Q = sq(rng.uniform(rb[0], rb[1]), rng.uniform(rb[2], rb[3]), math.radians(rng.uniform(*bb)))
                if sep(P, Q): ref += 1; print('REFUTED', it); break
            for cx in (ra[0], ra[1]):
                for cy in (ra[2], ra[3]):
                    for t1 in ba:
                        for dx in (rb[0], rb[1]):
                            for dy in (rb[2], rb[3]):
                                for t2 in bb:
                                    if sep(sq(cx, cy, math.radians(t1)), sq(dx, dy, math.radians(t2))): ref += 1; print('REFUTED-corner', it); break
print('excluded node pairs sampled', checked, 'refutations', ref)
