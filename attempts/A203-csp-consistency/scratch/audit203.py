"""audit of the CSP kills (rule H / F) by sampling: for a dead option row (cell, S) look for an admissible pose (container,
pin cores) meeting every slot of S that is interior-disjoint from SOME admissible H pose (H's record box x window).
A find = a refutation (bug).   python audit203.py <cert.json> [n_grid] [n_tilt]"""
import json, math, sys, itertools, random
S0 = 969271 / 250000
def sq(cx, cy, th):
    co, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * co - dy * s), cy + 0.5 * (dx * s + dy * co)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
def sep(P, Q):
    for poly in (P, Q):
        for i in range(4):
            x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % 4]; nx, ny = y0 - y1, x1 - x0
            p = [nx * x + ny * y for x, y in P]; q = [nx * x + ny * y for x, y in Q]
            if max(p) <= min(q) + 1e-12 or max(q) <= min(p) + 1e-12: return True
    return False
def inside(P): return all(-1e-9 <= x <= S0 + 1e-9 and -1e-9 <= y <= S0 + 1e-9 for x, y in P)
def R(B): return [(B[0], B[2]), (B[1], B[2]), (B[1], B[3]), (B[0], B[3])]
cert = json.load(open(sys.argv[1], encoding="utf-8"))
ng = int(sys.argv[2]) if len(sys.argv) > 2 else 7
nt = int(sys.argv[3]) if len(sys.argv) > 3 else 25
pins = [sq(0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]), 0.0) for n, b in cert["roles"].items() if n.startswith("P")]
wb = cert["wbox"]
def adm(P): return inside(P) and all(sep(P, Q) for Q in pins)
def poses(h, b0, b1, serve):
    out = []
    xs = [h[0] + (h[1] - h[0]) * i / (ng - 1) for i in range(ng)]
    ys = [h[2] + (h[3] - h[2]) * i / (ng - 1) for i in range(ng)]
    ts = [b0 + (b1 - b0) * i / (nt - 1) for i in range(nt)]
    for x in xs:
        for y in ys:
            for t in ts:
                P = sq(x, y, math.radians(t))
                if adm(P) and all(not sep(P, R(wb[s])) for s in serve): out.append(P)
    return out
Hb = cert["H_record"]
H = poses(Hb[:4], Hb[4], Hb[5], [])
print("H poses", len(H))
refuted = 0
for rd in cert.get("csp") or []:
    for d in rd.get("dead_opts") or []:
        h = d["hull"]; total = 0; found = 0
        for b0, b1 in d["bins"]:
            A = poses(h, b0, b1, d["S"]); total += len(A)
            for P in A:
                if any(sep(P, Q) for Q in H): found += 1
        print("round", rd["round"], "cell", d["cell"], "+".join(d["S"]), d["rule"], "meeting admissible poses", total, "disjoint from some H pose:", found)
        refuted += found > 0
print("REFUTATIONS", refuted)

# ---- the count's pair exclusions (rule S between two rows, one of them possibly H's row): sample both sides over the
# hull x the FULL tilt range [0, 90] (a superset of every row's tilt set), admissible and meeting every slot of the row
def poses_full(h, serve):
    return poses(h, 0.0, 90.0, serve)
seen = set()
for t in cert.get("tests") or []:
    for e in t.get("pair_excl") or []:
        k = (tuple(e["a"][0:1]), tuple(e["a"][1]), tuple(e["b"][0:1]), tuple(e["b"][1]))
        if k in seen: continue
        seen.add(k)
        A = poses_full(e["hull_a"], e["a"][1]); Bp = poses_full(e["hull_b"], e["b"][1])
        found = sum(1 for P in A if any(sep(P, Q) for Q in Bp))
        print("pair", e["rule"], e["a"], e["b"], "maxdist", e["maxdist"], "poses", len(A), "x", len(Bp), "disjoint pairs found for", found, "poses of a")
        refuted += found > 0
print("REFUTATIONS incl. pairs", refuted)
