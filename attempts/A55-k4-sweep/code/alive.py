"""
A54: the ALIVE side of the ledger -- a rigorous lower bound tau* >= budget for a stratum.

A kill needs a measure certificate. The opposite verdict needs a DUAL witness, and the cheapest
sound one is integral (A53's V6 argument for trump5): if the residual region of a node contains
B = budget pairwise interior-disjoint admissible unit squares, each disjoint from every pinned
square, then any measure with mu(Q) >= 1 on all of them has total >= B, so tau* >= budget and
NO measure certificate can ever kill the node -- the guard-LP route is closed for that stratum.
(If in addition the pins and the B placements are pairwise disjoint, the union is an 11-square
packing in [0,s0]^2, i.e. the stratum is REALIZED, not merely unkillable.)

Search: candidates = the node LP's rows (all admissible and filtered against the pins), ranked by
dual weight y; greedy + randomized-restart maximum independent set in the overlap graph, then a
local polish (each accepted placement is re-tested for exact interior-disjointness with margin).
Float SAT with an explicit margin is reported; a positive margin is a float proof modulo the
printed slack (the pins are exact rationals, so a margin > 1e-6 is not in doubt).
"""
import argparse, json, math, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
S0 = 969271 / 250000


def sat_gap(c1, t1, c2, t2):
    """min over the 4 SAT axes of (separation - required); >= 0 iff interior-disjoint."""
    best = -1e9
    for (cc, tt, oc, ot) in ((c1, t1, c2, t2), (c2, t2, c1, t1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = (abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) +
                 abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot)))
            best = max(best, d - 0.5 - 0.5 * g)
    return best


def admissible(cx, cy, th):
    w = (math.cos(th) + math.sin(th)) / 2
    return w - 1e-12 <= cx <= S0 - w + 1e-12 and w - 1e-12 <= cy <= S0 - w + 1e-12


def load_node(name, nodedir=None):
    for p in ([os.path.join(nodedir, f"{name}.json")] if nodedir else []) + [
            os.path.join(BASE, "results", "nodes", f"{name}.json"),
            os.path.join(A53, "results", "nodes", f"{name}.json")]:
        if os.path.exists(p):
            return json.load(open(p)), p
    raise SystemExit(f"no node json for {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--nodedir", default=None)
    ap.add_argument("--margin", type=float, default=1e-6, help="required SAT gap (interior-disjointness with slack)")
    ap.add_argument("--restarts", type=int, default=4000)
    ap.add_argument("--pool", type=int, default=1500, help="candidate placements (dual-weight ranked rows + all rows)")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    node, path = load_node(a.name, a.nodedir)
    pins = [tuple(p) for p in node["skeleton_slots"]]
    budget = node["budget"]
    # candidates: dual support first (LP thinks they are packable), then a sample of all rows
    cand = [(p["cx"], p["cy"], p["theta"], p["y"]) for p in node.get("packing", [])]
    cand.sort(key=lambda r: -r[3])
    rest = [(r[0], r[1], r[2], 0.0) for r in node.get("rows_all", [])]
    random.Random(a.seed).shuffle(rest)
    cand = cand + rest[: max(0, a.pool - len(cand))]
    # keep only placements exactly disjoint from every pin (the LP row filter allows 2e-3 of core penetration)
    ok = []
    for (cx, cy, th, y) in cand:
        if not admissible(cx, cy, th):
            continue
        if min(sat_gap((cx, cy), th, p, 0.0) for p in pins) < a.margin:
            continue
        ok.append((cx, cy, th, y))
    n = len(ok)
    print(f"{a.name}: node={os.path.relpath(path, BASE)} budget={budget} tau={node['tau']:.6f} "
          f"candidates {n}/{len(cand)} clear of the pins")
    if n == 0:
        print("no candidate clears the pins"); return
    C = np.array([[c[0], c[1]] for c in ok]); TH = np.array([c[2] for c in ok])
    G = np.zeros((n, n), bool)          # True = compatible (interior-disjoint)
    for i in range(n):
        for j in range(i + 1, n):
            g = sat_gap((C[i, 0], C[i, 1]), TH[i], (C[j, 0], C[j, 1]), TH[j]) >= a.margin
            G[i, j] = G[j, i] = g
    rng = random.Random(a.seed)
    best = []
    order0 = list(range(n))
    for r in range(a.restarts):
        order = order0 if r == 0 else rng.sample(order0, n)
        sel = []
        for i in order:
            if all(G[i, j] for j in sel):
                sel.append(i)
                if len(sel) >= budget:
                    break
        if len(sel) > len(best):
            best = list(sel)
            if len(best) >= budget:
                break
    out = dict(name=a.name, budget=budget, tau=node["tau"], node=os.path.relpath(path, BASE),
               max_disjoint_found=len(best), margin=a.margin,
               placements=[dict(cx=float(C[i, 0]), cy=float(C[i, 1]), theta_deg=float(math.degrees(TH[i])),
                                y=float(ok[i][3])) for i in best])
    if best:
        gmin = min([sat_gap((C[i, 0], C[i, 1]), TH[i], (C[j, 0], C[j, 1]), TH[j])
                    for ii, i in enumerate(best) for j in best[ii + 1:]] or [float("inf")])
        gpin = min(sat_gap((C[i, 0], C[i, 1]), TH[i], p, 0.0) for i in best for p in pins)
        out["min_pairwise_sat_gap"] = gmin
        out["min_gap_to_pins"] = gpin
    out["verdict"] = ("ALIVE: tau* >= budget (integral dual witness)" if len(best) >= budget
                      else f"inconclusive: only {len(best)}/{budget} disjoint placements found")
    print(json.dumps({k: v for k, v in out.items() if k != "placements"}, indent=1))
    for p in out["placements"]:
        print(f"    ({p['cx']:.6f}, {p['cy']:.6f}, {p['theta_deg']:7.3f} deg)  y={p['y']:.3f}")
    json.dump(out, open(os.path.join(BASE, "results", f"{a.name}_alive.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
