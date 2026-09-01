"""
A57 — the ALIVE-side arbiter the lab was missing (GAP-A54-2 / GAP-A55-2), generalised from
A53's `check_trump_feasible.py`.

**Lemma (disjoint-family bound).**  Let N be a node with pins/cores C_1..C_r and budget
m = 11 - r.  Suppose Q_1..Q_m are closed unit squares in [0,s]^2 that are
  (i) admissible (contained in the container),
  (ii) pairwise disjoint with a STRICTLY positive separating gap, and
  (iii) strictly disjoint from every core C_j.
Then every measure mu feasible for the node LP has mu(Q_i) >= 1 for each i (each Q_i is a
non-exempt row: `verify_case.py` exempts a placement only if it provably meets a core), and the
Q_i are disjoint, so mu(total) >= sum_i mu(Q_i) >= m.  Hence tau* >= m = budget and **no
certificate for N can exist** -- N is LP-unkillable, whatever compute is spent on it.
The strict gap matters: mu is atomic, so squares that merely touch could share an atom.

Everything is checked in exact rational arithmetic (Fraction), with cos/sin from a rational
t = tan(theta/2): cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2).  Floats are used only to SEARCH.
"""
import argparse, json, math, os, random, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from caselp import Box, Hyp
from run_skel import S0F

S_RAT = Fr(969271, 250000)


# ------------------------------------------------------------------ exact geometry
def cs(t):
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def gap_exact(c1, t1, h1, c2, t2, h2):
    """exact min over the 4 SAT axes of (separation - required); > 0 iff the closed squares
    are disjoint.  c = (cx, cy) Fractions, t = tan(theta/2) Fraction, h = half-side Fraction."""
    best = None
    for (cc, tt, hh, oc, ot, oh) in ((c1, t1, h1, c2, t2, h2), (c2, t2, h2, c1, t1, h1)):
        co, si = cs(tt)
        oco, osi = cs(ot)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = oh * (abs(ax[0] * oco + ax[1] * osi) + abs(-ax[0] * osi + ax[1] * oco))
            v = d - hh - g
            best = v if best is None else max(best, v)
    return best


def admissible_exact(c, t, s=S_RAT, h=Fr(1, 2)):
    co, si = cs(t)
    w = h * (abs(co) + abs(si))
    return w <= c[0] <= s - w and w <= c[1] <= s - w


def rat(x, den=10 ** 6):
    return Fr(round(x * den), den)


# ------------------------------------------------------------------ float search helpers
def gap_f(c1, th1, h1, c2, th2, h2):
    best = -1e9
    for (cc, tt, hh, oc, ot, oh) in ((c1, th1, h1, c2, th2, h2), (c2, th2, h2, c1, th1, h1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = oh * (abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) +
                      abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot)))
            best = max(best, d - hh - g)
    return best


def obstacles(name, box=None):
    """list of (centre, theta_rad, half_side) for the pins and (optionally) a YES core box."""
    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[name]]
    obs = [((x, y), 0.0, 0.5) for (x, y) in slots]
    core = None
    if box is not None:
        c = box.core()
        obs.append(((float(c.kx), float(c.ky)), math.atan(float(c.tm)) * 2, float(c.a)))
        core = c
    return slots, obs, core


def candidates(obs, s=S0F, step=0.02, margin=2e-4, tilts=(0.0,)):
    """grid of placements that clear every obstacle by > margin."""
    out = []
    for th in tilts:
        w = (math.cos(th) + math.sin(th)) / 2
        n = int((s - 2 * w) / step)
        for i in range(n + 1):
            cx = w + i * step
            for j in range(n + 1):
                cy = w + j * step
                if all(gap_f((cx, cy), th, 0.5, o[0], o[1], o[2]) > margin for o in obs):
                    out.append(((cx, cy), th))
    return out


def search(obs, m, s=S0F, tries=400000, seed=0, margin=2e-4, tilts=(0.0,), step=0.02,
           node_cap=400000):
    """DFS over a grid candidate pool for m pairwise-separated unit squares.
    seed 0 = lexicographic (bottom-left greedy backbone); seed > 0 shuffles the pool."""
    C = candidates(obs, s, step, margin, tilts)
    if len(C) < m:
        return []
    C.sort(key=lambda q: (q[0][0], q[0][1], q[1]))
    if seed:
        rng = random.Random(seed)
        rng.shuffle(C)
    n = len(C)
    best = []
    nodes = [0]

    def dfs(i, chosen):
        if len(chosen) >= m:
            return list(chosen)
        if len(chosen) > len(best):
            best[:] = list(chosen)
        for k in range(i, n):
            if nodes[0] > node_cap:
                return None
            nodes[0] += 1
            if n - k < m - len(chosen):
                return None
            q = C[k]
            if all(gap_f(q[0], q[1], 0.5, p[0], p[1], 0.5) > margin for p in chosen):
                chosen.append(q)
                r = dfs(k + 1, chosen)
                if r:
                    return r
                chosen.pop()
        return None

    r = dfs(0, [])
    return r or best


def snap_and_verify(chosen, obs_exact, m, den=10 ** 6, tden=1 << 40):
    """snap to rationals and re-check EXACTLY; returns (ok, records, min_gap)."""
    Q = []
    for ((cx, cy), th) in chosen:
        t = rat(math.tan(th / 2), tden)
        Q.append(((rat(cx, den), rat(cy, den)), t, Fr(1, 2)))
    recs, gmin = [], None
    ok = True
    for i, (c, t, h) in enumerate(Q):
        adm = admissible_exact(c, t)
        ok &= adm
        og = None
        for (oc, ot, oh) in obs_exact:
            g = gap_exact(c, t, h, oc, ot, oh)
            og = g if og is None else min(og, g)
        ok &= (og > 0)
        recs.append(dict(i=i, cx=str(c[0]), cy=str(c[1]), t=str(t),
                         theta_deg=float(math.degrees(2 * math.atan(float(t)))),
                         admissible=bool(adm), min_gap_to_cores=str(og), min_gap_float=float(og)))
        gmin = og if gmin is None else min(gmin, og)
    for i in range(len(Q)):
        for j in range(i + 1, len(Q)):
            g = gap_exact(Q[i][0], Q[i][1], Q[i][2], Q[j][0], Q[j][1], Q[j][2])
            ok &= (g > 0)
            gmin = min(gmin, g)
    ok &= (len(Q) >= m)
    return ok, recs, gmin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--box", default=None, help='json {"x0":..,"x1":..,"y0":..,"y1":..,"th0":..,"th1":..}')
    ap.add_argument("--child", default=None, help="child id: read its box from results/tree/<key>/<id>.json")
    ap.add_argument("--m", type=int, default=None, help="target family size (default = node budget)")
    ap.add_argument("--tries", type=int, default=400000)
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--tilts", default="0")
    ap.add_argument("--placements", default=None, help="verify a supplied family: json [[cx,cy,theta_deg],...]")
    ap.add_argument("--den", type=int, default=10**6, help="rational snapping denominator for centres")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    box = None
    if a.box:
        box = Box.from_json(json.loads(a.box))
    slots, obs, core = obstacles(a.name, box)
    budget = 11 - len(slots) - (1 if box is not None else 0)
    m = a.m or budget
    obs_exact = [((Fr(round(x * 10 ** 9), 10 ** 9), Fr(round(y * 10 ** 9), 10 ** 9)), Fr(0), Fr(1, 2))
                 for (x, y) in slots]
    if core is not None:
        obs_exact.append(((core.kx, core.ky), core.tm, core.a))
    tilts = tuple(math.radians(float(x)) for x in a.tilts.split(","))
    found, rec = None, None
    if a.placements:                      # verify a SUPPLIED family exactly (self-test route)
        P = json.loads(a.placements)      # [[cx, cy, theta_deg], ...]
        ch = [((p[0], p[1]), math.radians(p[2])) for p in P]
        ok, recs, gmin = snap_and_verify(ch, obs_exact, m, den=a.den)
        if ok:
            found, rec = ch, (recs, gmin)
        else:
            out_bad = dict(checked=recs, min_gap=str(gmin))
            print(json.dumps(out_bad, indent=1)[:2000])
    else:
        for sd in range(a.seeds):
            ch = search(obs, m, tries=a.tries, seed=sd, tilts=tilts)
            if len(ch) >= m:
                ok, recs, gmin = snap_and_verify(ch, obs_exact, m)
                if ok:
                    found, rec = ch, (recs, gmin)
                    break
    out = dict(name=a.name, slots=[list(p) for p in slots], box=(box.to_json() if box else None),
               budget=budget, m=m, tilts=a.tilts)
    if found is None:
        out.update(result="NO-WITNESS", note=f"no {m}-family found in {a.seeds} seeds x {a.tries} tries "
                                             "(this proves nothing: the node may still be unkillable)")
    else:
        recs, gmin = rec
        out.update(result="ALIVE-CERTIFIED", squares=recs, min_gap=str(gmin), min_gap_float=float(gmin),
                   unkillable=bool(m >= budget),
                   claim=(f"tau*({a.name}{' + core' if box else ''}) >= {m}"
                          + (f" = budget {budget} => NO certificate can exist for this node (LP-UNKILLABLE)"
                             if m >= budget else
                             f" (budget {budget}: this is a lower bound only, not an unkillability proof)")))
    p = a.out or os.path.join(BASE, "results", "alive", f"{a.name}{'_box' if box else ''}.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(out, open(p, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "squares"}, indent=1))


if __name__ == "__main__":
    main()
