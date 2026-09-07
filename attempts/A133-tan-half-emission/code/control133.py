"""A133 T1 -- the control: a checker that accepts everything proves nothing.

    python control133.py ../certs/<id>.tcert.json.gz [more...]

Section (a) re-checks the certificate as emitted.  Section (b) MUTATES it, one mutation at a
time, and requires `check_local_t.Checker` to REJECT every mutant; a mutation the checker does
not notice is a hole in the check, and is reported as such.  Section (c) is a survivor count:
random configurations are drawn from the neighbourhood `N` in the t parametrisation, the ones
that are genuinely packings of `L u P` at a side in the window are counted, and the count must be
0 -- a Monte-Carlo shadow of the DEAD verdict, necessary and not sufficient, but it would catch
an `N` that was emitted with the wrong boxes.

The mutations (each applied to a bounded sample of leaves, never to the file on disk):

  zero-y     every Farkas multiplier of one leaf set to 0
  halve-y    every multiplier of one leaf halved
  negate-y   one multiplier's sign flipped
  drop-row   one row deleted from the combination
  widen-box  one tilt coordinate of the leaf's box widened by 1/1000
  bump-k     one row's constant raised by 1/1000 (a row that is NOT implied any more)
  env-h      one recorded `h` chord raised by 1/1000 (no longer a lower bound)
  env-w      one recorded `w` plane raised by 1/1000 (no longer a lower bound)
  drop-leaf  one leaf removed from the tree's reach (the cover then has a hole)
"""
from __future__ import annotations

import copy, gzip, json, os, random, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_local_t as K                                    # noqa: E402

BASE = os.path.abspath(os.path.join(HERE, ".."))


def load(p):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return json.load(f)


def verdict(cert, only_leaf=None):
    C = K.Checker(cert, only_leaf=only_leaf)
    return C.run(), C


def env_verdict(cert):
    """the envelope table alone -- what an `env-*` mutation has to break."""
    C = K.Checker(cert)
    C.verify_env()
    return not C.errors, C


def leaf_nodes(root):
    """every `dead` node of the tree, in DFS order."""
    out, st = [], [root]
    while st:
        n = st.pop()
        k = n.get("k")
        if k == "dead":
            out.append(n)
        for c in n.get("ch", []) or []:
            st.append(c)
    return out


BUMP = Q(1, 1000)


def h_slack(key, v, n=16):
    """an upper bound on min over the cell of h(t) - (m t + c) (a grid minimum)."""
    a, b = (Q(x) for x in key.split("|"))
    m, c = Q(v[0]), Q(v[1])
    return min(K.hw_of(a + Q(i, n) * (b - a)) - (m * (a + Q(i, n) * (b - a)) + c)
               for i in range(n + 1))


def w_slack(key, v, n=10):
    """an upper bound on min over the cell product of W_eps - (mw tw + mo to + c)."""
    p = key.split("|")
    eps = int(p[0])
    aw, bw, ao, bo = (Q(x) for x in p[1:])
    mw, mo, c = (Q(x) for x in v)
    best = None
    for i in range(n + 1):
        tw = aw + Q(i, n) * (bw - aw)
        for j in range(n + 1):
            to = ao + Q(j, n) * (bo - ao)
            W = (K.cT(tw) * K.cT(to) + K.sT(tw) * K.sT(to))                 + eps * (K.sT(tw) * K.cT(to) - K.cT(tw) * K.sT(to))
            d = W - (mw * tw + mo * to + c)
            best = d if best is None else min(best, d)
    return best


MUT = ["zero-y", "halve-y", "negate-y", "drop-row", "widen-box", "bump-k",
       "env-h", "env-w", "drop-leaf"]

# `drop-row` is INFORMATIONAL: a leaf whose Farkas bound clears s0 with room to spare can lose a
# row and still clear it, so the mutant is a different but valid certificate.  Every other
# mutation must be caught on every leaf it applies to.
MUST_CATCH = [m for m in MUT if m != "drop-row"]


def mutate(cert, kind, li, rng):
    c = copy.deepcopy(cert)
    lf = c["leaves"][li]
    if kind == "halve-y" and lf["infeas"]:
        # halving a Farkas RAY halves a positive bound and it stays positive: the mutant is a
        # different but still VALID certificate, so this mutation is not expected to be caught
        # on a ray leaf (A126 measured the same, and the count came out at the ray count).
        return None
    if kind == "zero-y":
        for r in lf["rows"]:
            r["y"] = "0"
    elif kind == "halve-y":
        for r in lf["rows"]:
            r["y"] = str(Q(r["y"]) / 2)
    elif kind == "negate-y":
        r = lf["rows"][rng.randrange(len(lf["rows"]))]
        r["y"] = str(-Q(r["y"]))
    elif kind == "drop-row":
        if len(lf["rows"]) < 2:
            return None
        del lf["rows"][rng.randrange(len(lf["rows"]))]
    elif kind == "widen-box":
        j = rng.randrange(len(lf["box"]))
        lf["box"][j][1] = str(Q(lf["box"][j][1]) + Q(1, 1000))
    elif kind == "bump-k":
        r = lf["rows"][rng.randrange(len(lf["rows"]))]
        r["k"] = str(Q(r["k"]) + Q(1, 1000))
    elif kind == "env-h":
        ks = [k for k in sorted(c["env"]["h"]) if h_slack(k, c["env"]["h"][k]) < BUMP]
        if not ks:
            return None
        k0 = ks[rng.randrange(len(ks))]
        c["env"]["h"][k0][1] = str(Q(c["env"]["h"][k0][1]) + BUMP)
    elif kind == "env-w":
        # only entries whose plane is within BUMP of the function it bounds: an envelope with
        # MORE slack than that stays a valid lower bound after the bump, so the mutant is a
        # different but SOUND certificate and its acceptance is not a hole (measured on
        # S02 (0.05, 20 deg): 13 of 312 w-entries have >= 1/1000 of slack, up to 3.5e-2).
        ks = [k for k in sorted(c["env"]["w"]) if w_slack(k, c["env"]["w"][k]) < BUMP]
        if not ks:
            return None
        k0 = ks[rng.randrange(len(ks))]
        c["env"]["w"][k0][2] = str(Q(c["env"]["w"][k0][2]) + BUMP)
    elif kind == "drop-leaf":
        # point a `dead` node at a DIFFERENT leaf: the cover then misses this cell
        nodes = leaf_nodes(c["root"])
        tgt = [n for n in nodes if n["leaf"] == li]
        if not tgt or len(c["leaves"]) < 2:
            return None
        tgt[0]["leaf"] = (li + 1) % len(c["leaves"])
    else:
        raise ValueError(kind)
    return c


def survivors(cert, draws=10000, seed=1):
    """section (c): draw configurations from `N` in the t parametrisation at a side in
    [s_lo, s0] and count the ones that are genuinely interior-disjoint AND inside the container.

    DEAD says there are none, so the count must be 0.  Necessary, not sufficient -- but it would
    catch an `N` emitted with the wrong boxes, the wrong slack cores or the wrong t-cells, which
    is exactly the part of the pipeline the Farkas arithmetic cannot see."""
    rng = random.Random(seed)
    m = cert["meta"]
    s_lo, s_hi = float(Q(m["s_lo"])), min(float(Q(m["s_hi"])), 969271.0 / 250000.0)
    bodies = m["bodies"]
    tol = 1e-9
    drawn = tested = hits = 0
    worst = -1e18
    for _ in range(draws):
        drawn += 1
        s = rng.uniform(s_lo, s_hi)
        poses = []
        for b in bodies:
            if b["kind"] == "free":
                x = rng.uniform(float(Q(b["x0"])), float(Q(b["x1"])))
                y = rng.uniform(float(Q(b["y0"])), float(Q(b["y1"])))
                t = rng.uniform(float(Q(b["t0"])), float(Q(b["t1"])))
            else:
                hh = float(Q(b["hh"]))
                x = float(Q(b["ax"][0])) + float(Q(b["ax"][1])) * s + rng.uniform(-hh, hh)
                y = float(Q(b["ay"][0])) + float(Q(b["ay"][1])) * s + rng.uniform(-hh, hh)
                t = 0.0
            poses.append((x, y, t))
        tested += 1
        gmin = 1e18
        for (x, y, t) in poses:                                     # walls
            c, sn = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
            h = 0.5 * (abs(c) + abs(sn))
            gmin = min(gmin, x - h, s - h - x, y - h, s - h - y)
        for i in range(len(poses)):                                 # pairs
            for j in range(i + 1, len(poses)):
                gmin = min(gmin, pair_gap(poses[i], poses[j]))
        worst = max(worst, gmin)
        if gmin >= -tol:
            hits += 1
    return dict(drawn=drawn, tested=tested, hits=hits, best_margin=worst, seed=seed)


def pair_gap(p, q):
    """max over the eight signed selections of the separating-axis gap: >= 0 iff the two unit
    squares have disjoint interiors."""
    best = -1e18
    for (owner, k, eps) in [(o, kk, e) for o in (0, 1) for kk in (0, 1) for e in (1, -1)]:
        (xw, yw, tw), (xo, yo, to) = (p, q) if owner == 0 else (q, p)
        cw, sw = (1 - tw * tw) / (1 + tw * tw), 2 * tw / (1 + tw * tw)
        co, so = (1 - to * to) / (1 + to * to), 2 * to / (1 + to * to)
        ax, ay = (cw, sw) if k == 0 else (-sw, cw)
        proj = (xo - xw) * ax + (yo - yw) * ay
        w = abs(cw * co + sw * so) + abs(cw * so - sw * co)
        best = max(best, eps * proj - 0.5 - 0.5 * w)
    return best


def run(path, sample=6, seed=0):
    rng = random.Random(seed)
    cert = load(path)
    cid = cert["meta"]["id"]
    t0 = time.time()
    ok, C = verdict(cert)
    base = dict(id=cid, as_emitted=bool(ok), errors=C.errors[:3], counts=dict(C.n),
                seconds=round(time.time() - t0, 1),
                certified_min=(None if C.min_bound is None else float(C.min_bound)))
    print("%-28s as emitted: %s   (%d leaves, %d rows, %d env entries)"
          % (cid, "VALID" if ok else "INVALID", len(cert["leaves"]), C.n["rows"],
             C.n["env_h"] + C.n["env_S"] + C.n["env_w"]))
    n = len(cert["leaves"])
    idx = sorted(rng.sample(range(n), min(sample, n)))
    tab = {}
    for kind in MUT:
        caught = tried = 0
        for li in idx:
            m = mutate(cert, kind, li, rng)
            if m is None:
                continue
            tried += 1
            if kind.startswith("env-"):
                mok, _ = env_verdict(m)
            elif kind == "drop-leaf":
                mok, _ = verdict(m, only_leaf=-1)      # the leaf-reference bookkeeping alone
            else:
                mok, _ = verdict(m, only_leaf=li)
            if not mok:
                caught += 1
        tab[kind] = [caught, tried]
        print("   %-10s rejected %d / %d" % (kind, caught, tried))
    sv = survivors(cert)
    base["survivors"] = sv
    print("   survivors  drawn %d -> tested %d -> hits %d   (best packing margin %.3e)"
          % (sv["drawn"], sv["tested"], sv["hits"], sv["best_margin"]))
    base["mutations"] = tab
    base["mutation_holes"] = sorted(k for k, (c_, t_) in tab.items()
                                    if k in MUST_CATCH and t_ and c_ < t_)
    return base


def main(paths, sample=4):
    out = []
    for p in paths:
        out.append(run(p, sample=sample))
    res = os.path.join(BASE, "results", "control.json")
    with open(res, "w", encoding="utf-8") as f:
        json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=out), f, indent=1)
    bad = [r["id"] for r in out
           if not r["as_emitted"] or r["mutation_holes"] or r["survivors"]["hits"]]
    print("control: %d certificate(s), %s" % (len(out), "ALL CLEAN" if not bad else "HOLES " + str(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
