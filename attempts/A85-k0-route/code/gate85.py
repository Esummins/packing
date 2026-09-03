"""
A85 `gate85.py` -- R3: the exact ALIVE gate over the BL pair census, the D4 corner maps, and
the multi-corner node samples.  Exact; no LP.

FAST GATE (exactly equivalent to alive84.alive_verdict here, and VALIDATED against it on a
random sample).  For k0_00 the node hypotheses are cores only (no NO-families) and every
witness of every image family is admissible at s0 and the family is strictly pairwise disjoint
(class85 verified this), so alive84's verdict reduces to

    k_g = 11 - |{witnesses of image g dropped by SOME core}|,
    drop-set of a node = the UNION of the per-core drop sets,
    unkillable iff some k_g >= budget,  attemptable iff every k_g < budget.

So the per-core drop set is precomputed once per (corner, box, image) as an 11-bit mask and
every node verdict is a set union.  The subfamily of a strictly-disjoint family is strictly
disjoint, so alive84's pairwise re-check can never fail.

CORNER MAPS (exact D4, about the container centre; s0 = 969271/250000):
    BL identity | BR x -> s0 - x, theta -> 90 - theta | TR rot180 | TL y -> s0 - y, theta -> 90 - theta.
"""
import argparse, json, math, os, random, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from caselp import Box
from alivewitness import gap_exact
from pinguard import cores_meet
import tree85 as T
import alive84
import corner85 as X

RES = os.path.join(BASE, "results")
S0F = X.S0F
CORNERS = ["BL", "BR", "TR", "TL"]


def map_box(b, corner):
    if corner == "BL":
        return Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1)
    if corner == "BR":
        return Box(S0F - b.x1, S0F - b.x0, b.y0, b.y1, 90.0 - b.th1, 90.0 - b.th0)
    if corner == "TR":
        return Box(S0F - b.x1, S0F - b.x0, S0F - b.y1, S0F - b.y0, b.th0, b.th1)
    if corner == "TL":
        return Box(b.x0, b.x1, S0F - b.y1, S0F - b.y0, 90.0 - b.th1, 90.0 - b.th0)
    raise ValueError(corner)


def drop_masks(box, W):
    """{image_key: 11-bit mask of witnesses this box's core kills}."""
    c = box.core()
    out = {}
    for g, six in W.items():
        m = 0
        for bit, (nm, cc, t) in enumerate(six):
            if gap_exact(cc, t, Fr(1, 2), (c.kx, c.ky), c.tm, c.a) <= 0:
                m |= 1 << bit
        out[g] = m
    return out


def verdict(masks_list, budget, keys):
    """-> (state, k, per_image_k)"""
    per = {}
    for g in keys:
        u = 0
        for M in masks_list:
            u |= M[g]
        per[g] = 11 - bin(u).count("1")
    k = max(per.values())
    return ("unkillable" if k >= budget else "attemptable"), k, per


def contains_mod90(b, x, y, thd, tol=1e-9):
    if not (b.x0 - tol <= x <= b.x1 + tol and b.y0 - tol <= y <= b.y1 + tol):
        return False
    for th in (thd, thd + 90.0, thd - 90.0):
        if b.th0 - 1e-7 <= th <= b.th1 + 1e-7:
            return True
    return False


# ------------------------------------------------------------------ D4 bookkeeping on indices
MATS = [((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)),
        ((0, 1), (1, 0)), ((0, -1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (-1, 0))]
MC = {"BL": ((1, 0), (0, 1)), "BR": ((-1, 0), (0, 1)),
      "TR": ((-1, 0), (0, -1)), "TL": ((1, 0), (0, -1))}
SIGN = {"BL": (-1, -1), "BR": (1, -1), "TR": (1, 1), "TL": (-1, 1)}
TMAT = ((0, 1), (1, 0))


def mmul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2))
                 for i in range(2))


def mapply(A, v):
    return tuple(sum(A[i][k] * v[k] for k in range(2)) for i in range(2))


def minv(A):
    d = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    return ((A[1][1] // d, -A[0][1] // d), (-A[1][0] // d, A[0][0] // d))


def d4_canonical(node, permT):
    """node = {corner: sorted 2-tuple of BL-frame box indices}.  -> (canonical_tuple, is_min)."""
    def enc(nd):
        return tuple(tuple(nd[c]) for c in CORNERS)
    best = None
    me = enc(node)
    for g in MATS:
        nd = {}
        for c in CORNERS:
            s2 = mapply(g, SIGN[c])
            c2 = [k for k in CORNERS if SIGN[k] == s2][0]
            h = mmul(minv(MC[c2]), mmul(g, MC[c]))
            p = node[c]
            if h == TMAT:
                p = tuple(sorted(permT[i] for i in p))
            nd[c2] = tuple(sorted(p))
        e = enc(nd)
        best = e if best is None else min(best, e)
    return best, (me == best)


# ------------------------------------------------------------------ R3
def r3(seed=8501, out="a85_gate_samples.json", nvalidate=200,
       n2=300, n3=300, n4=1000):
    t0 = time.time()
    T.setup("k0_00")
    W = alive84.load_witnesses("k0_00")
    keys = sorted(W)
    R = json.load(open(os.path.join(RES, "a85_reach_BL.json")))
    P = json.load(open(os.path.join(RES, "a85_pairs_BL.json")))
    rows = [r for r in R["variants"]["sigma_closed_7"]["rows"] if r["sound"]]
    boxes = [Box.from_json(r["box"]) for r in rows]
    sense = [r["sense"] for r in rows]
    n = len(boxes)
    pairs = [(p["i"], p["j"]) for p in P["surviving_level2"]]
    part = os.path.join(RES, out + ".partial")
    json.dump(dict(phase="R3", n_boxes=n, n_pairs=len(pairs), stage="masks"),
              open(part, "w"), indent=1)

    # per-corner, per-box drop masks
    MASK = {c: [drop_masks(map_box(b, c), W) for b in boxes] for c in CORNERS}
    CBOX = {c: [map_box(b, c) for b in boxes] for c in CORNERS}
    CCORE = {c: [b.core() for b in CBOX[c]] for c in CORNERS}

    # sigma permutation on the SOUND sublist (needed for the D4 index action)
    closed, permT = X.sigma_closed_boxes(boxes)

    # ---- (a) gate every surviving BL pair at budget 9 -----------------------------------
    stA = dict(attemptable=0, unkillable=0)
    per_pair = []
    for (i, j) in pairs:
        st, k, per = verdict([MASK["BL"][i], MASK["BL"][j]], 9, keys)
        stA[st] += 1
        per_pair.append((i, j, st, k))
    # image-compatible pairs (both boxes hold a placement of the SAME image)
    inbox = {c: {} for c in CORNERS}
    for c in CORNERS:
        for bi, b in enumerate(CBOX[c]):
            for im in T.IMAGES:
                for si, (x, y, th) in enumerate(im["placements"]):
                    if contains_mod90(b, x, y, math.degrees(th) % 90.0):
                        inbox[c].setdefault(im["key"], []).append((bi, si))
    compat = {g: [] for g in keys}
    holds = {c: {g: {} for g in keys} for c in CORNERS}
    for c in CORNERS:
        for g, lst in inbox[c].items():
            for (bi, si) in lst:
                holds[c][g].setdefault(bi, []).append(si)
    for (i, j) in pairs:
        for g in keys:
            si = holds["BL"][g].get(i)
            sj = holds["BL"][g].get(j)
            if si and sj and set(si) != set(sj):
                compat[g].append(dict(i=i, j=j, squares_i=sorted(si), squares_j=sorted(sj)))
    canary_missing = [g for g in keys if not compat[g]]

    # ---- validation of the fast gate against the frozen alive84 gate --------------------
    rnd = random.Random(seed)
    val = []
    for (i, j) in rnd.sample(pairs, min(nvalidate, len(pairs))):
        gg = T.gate(boxes[j], [boxes[i]], [], 9)
        st, k, per = verdict([MASK["BL"][i], MASK["BL"][j]], 9, keys)
        val.append(dict(i=i, j=j, fast=st, fast_k=k, slow=gg["state"], slow_k=gg["k"],
                        agree=bool(st == gg["state"] and k == gg["k"])))
    val_bad = [v for v in val if not v["agree"]]

    # ---- sigma-closure of the SURVIVING pair set ----------------------------------------
    # The cover BOX set is sigma-closed, and both prunes are sigma-invariant as geometry -- but
    # the rational CORE a = (1/2 - hd)/(1 + (t1 - t0)) is built on the t-grid, and mirrored
    # t-bins of a sigma-closed t-partition have different t-widths, so core(sigma b) != sigma
    # core(b).  The surviving-pair SET is therefore not sigma-closed even though the cover is.
    PS = {(min(i, j), max(i, j)) for (i, j) in pairs}
    sig_in = 0
    for (i, j) in pairs:
        a2, b2 = permT[i], permT[j]
        if (min(a2, b2), max(a2, b2)) in PS:
            sig_in += 1
    core_a = [float(boxes[i].core().a) for i in range(n)]
    core_a_asym = max(abs(core_a[i] - core_a[permT[i]]) for i in range(n))

    # ---- (b) corner maps ----------------------------------------------------------------
    th_bins = sorted({(round(b.th0, 6), round(b.th1, 6)) for b in boxes})
    map_ok = {}
    for c in CORNERS:
        bad = [bi for bi, b in enumerate(CBOX[c])
               if (round(b.th0, 6), round(b.th1, 6)) not in th_bins]
        map_ok[c] = dict(theta_bins_preserved=(not bad), n_bad=len(bad))
    json.dump(dict(phase="R3", stage="samples", pair_gate=stA), open(part, "w"), indent=1)

    # ---- (c) multi-corner samples --------------------------------------------------------
    def sample_nodes(cs, budget, N):
        got = dict(attemptable=0, unkillable=0, contradictory=0)
        recs = []
        for _ in range(N):
            node = {c: pairs[rnd.randrange(len(pairs))] for c in cs}
            bx = [(c, k) for c in cs for k in node[c]]
            contra = False
            for u in range(len(bx)):
                for v in range(u + 1, len(bx)):
                    (cu, iu), (cv, iv) = bx[u], bx[v]
                    if cu == cv:
                        continue
                    if cores_meet(CCORE[cu][iu], CCORE[cv][iv]):
                        contra = True
                        break
                if contra:
                    break
            if contra:
                got["contradictory"] += 1
                recs.append(dict(node={c: list(node[c]) for c in cs}, state="contradictory"))
                continue
            st, k, per = verdict([MASK[c][i] for (c, i) in bx], budget, keys)
            got[st] += 1
            recs.append(dict(node={c: list(node[c]) for c in cs}, state=st, k=k,
                             per_image=per))
        return got, recs

    s2, r2s = sample_nodes(["BL", "TR"], 7, n2)
    s3, r3s = sample_nodes(["BL", "BR", "TR"], 5, n3)
    s4, r4s = sample_nodes(CORNERS, 3, n4)

    # ---- D4 canonical fraction on the 4-corner sample ------------------------------------
    ncanon = 0
    orbit_sizes = {}
    for r in r4s:
        node = {c: tuple(sorted(r["node"][c])) for c in CORNERS}
        can, ismin = d4_canonical(node, permT)
        ncanon += 1 if ismin else 0
        images = set()
        for g in MATS:
            nd = {}
            for c in CORNERS:
                s2v = mapply(g, SIGN[c])
                c2 = [k for k in CORNERS if SIGN[k] == s2v][0]
                h = mmul(minv(MC[c2]), mmul(g, MC[c]))
                p = node[c]
                if h == TMAT:
                    p = tuple(sorted(permT[i] for i in p))
                nd[c2] = tuple(sorted(p))
            images.add(tuple(tuple(nd[c]) for c in CORNERS))
        orbit_sizes[len(images)] = orbit_sizes.get(len(images), 0) + 1

    def frac(d, N):
        return {k: (v, round(v / float(N), 4)) for k, v in d.items()}

    res = dict(cls="k0_00", phase="R3_gate_samples", seconds=round(time.time() - t0, 1),
               n_sound_boxes=n, n_pairs_level2=len(pairs),
               box_set_sigma_closed=bool(closed),
               surviving_pairs_sigma_closed=dict(
                   n=len(pairs), sigma_image_also_surviving=sig_in,
                   fraction=round(sig_in / float(max(1, len(pairs))), 4),
                   max_core_a_asymmetry=core_a_asym,
                   why=("the cover box set is sigma-closed, but the rational core "
                        "a = (1/2 - hd)/(1 + (t1 - t0)) is t-grid based and mirrored t-bins "
                        "have different t-widths, so core(sigma b) != sigma core(b); the "
                        "prune is sound either way, but the surviving set is not exactly "
                        "sigma-closed")),
               pair_gate_budget9=frac(stA, max(1, len(pairs))),
               image_compatible_pairs={g: len(compat[g]) for g in keys},
               image_compatible_examples={g: compat[g][:5] for g in keys},
               canary_images_without_a_compatible_BL_pair=canary_missing,
               fast_gate_validation=dict(n=len(val), disagreements=len(val_bad),
                                         bad=val_bad[:10]),
               corner_map_check=map_ok, theta_bins=[list(t) for t in th_bins],
               sample_2corner=dict(corners=["BL", "TR"], budget=7, n=n2, counts=frac(s2, n2)),
               sample_3corner=dict(corners=["BL", "BR", "TR"], budget=5, n=n3,
                                   counts=frac(s3, n3)),
               sample_4corner=dict(corners=CORNERS, budget=3, n=n4, counts=frac(s4, n4),
                                   d4_canonical=ncanon,
                                   d4_canonical_fraction=round(ncanon / float(n4), 4),
                                   orbit_size_histogram=orbit_sizes),
               pair_states=[dict(i=i, j=j, state=st, k=k) for (i, j, st, k) in per_pair[:2000]],
               sample_records=dict(c2=r2s[:200], c3=r3s[:200], c4=r4s[:200]))
    json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    if os.path.exists(part):
        os.remove(part)
    assert not canary_missing, ("CANARY: images with no compatible BL pair: %s" % canary_missing)
    assert not val_bad, "fast gate disagrees with alive84 on %d samples" % len(val_bad)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=8501)
    a = ap.parse_args()
    r = r3(a.seed)
    print(json.dumps(dict(pair_gate=r["pair_gate_budget9"],
                          compat={g: v for g, v in r["image_compatible_pairs"].items()},
                          val=r["fast_gate_validation"]["disagreements"],
                          c2=r["sample_2corner"]["counts"], c3=r["sample_3corner"]["counts"],
                          c4=r["sample_4corner"]["counts"],
                          d4=r["sample_4corner"]["d4_canonical_fraction"],
                          orbits=r["sample_4corner"]["orbit_size_histogram"],
                          maps=r["corner_map_check"], secs=r["seconds"]), indent=1))


if __name__ == "__main__":
    main()
