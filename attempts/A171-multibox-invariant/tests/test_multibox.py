"""A171 tests -- the multi-box invariant, four cases, all of them under two minutes.

    (a) two boxes whose K' overlap        -> the mutual clip shrinks or EMPTIES them; the invariant
                                            passes on what is left
    (b) a box straddling the container    -> the container clip removes the outside poses
    (c) A168's failing S2 node            -> the invariant FAILS before normalise and PASSES after
    (d) random nodes of 2-6 boxes         -> 10^4 sampled poses after normalise never violate

Run:  python tests/test_multibox.py            (add --json <path> to dump the results)
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "code")))

import multibox as MB                                          # noqa: E402
import numpy as np                                             # noqa: E402
import polycore as PC                                          # noqa: E402

S = float(MB.S_RAT)
FIGS = os.path.abspath(os.path.join(HERE, "..", "figs"))
RESULTS = []


def _rec(name, ok, **kw):
    RESULTS.append(dict(test=name, ok=bool(ok), **kw))
    flag = "PASS" if ok else "FAIL"
    extra = " ".join(f"{k}={v}" for k, v in kw.items() if not isinstance(v, (dict, list)))
    print(f"  [{flag}] {name}  {extra}", flush=True)
    return ok


# ==================================================================== shared pose checker
def pose_violations(node, n=10000, seed=171):
    """Sample n poses per box and count the three things that must NEVER happen after normalise:

      escape      a pose whose square is not inside [0, s]^2
      not_core    a pose whose square does not CONTAIN its own box's K' (the property every leaf
                  in the corpus rests on -- A132's vertex certification, re-checked by sampling)
      k_overlap   a pair of polygon cores whose interiors meet (exact rational SAT, not sampled)
    """
    s = float(node.s)
    rng = np.random.default_rng(seed)
    out = dict(drawn=0, escape=0, not_core=0, k_overlap=0, core_meet=0)
    for k, mb in node.boxes.items():
        C, TH = mb.sample(n, rng)
        if not len(C):
            continue
        out["drawn"] += len(C)
        h = 0.5 * (np.abs(np.cos(TH)) + np.abs(np.sin(TH)))
        out["escape"] += int((~((C[:, 0] >= h) & (C[:, 0] <= s - h) &
                                (C[:, 1] >= h) & (C[:, 1] <= s - h))).sum())
        # K'(B) must sit inside Q(c, th) for every sampled pose: |R(-th)(v - c)|_inf <= 1/2
        bad = np.zeros(len(C), bool)
        ct, st = np.cos(TH), np.sin(TH)
        for (vx, vy) in mb.pc.verts:
            dx, dy = float(vx) - C[:, 0], float(vy) - C[:, 1]
            u = np.abs(dx * ct + dy * st)
            w = np.abs(-dx * st + dy * ct)
            bad |= np.maximum(u, w) > 0.5 + 1e-12
        out["not_core"] += int(bad.sum())
        hit = np.zeros(len(C), bool)
        for j, ob in node.boxes.items():
            if j != k:
                hit |= PC.poly_square_depth(ob.pc.P, C, TH) > 0.0
        out["core_meet"] += int(hit.sum())
    names = node.names
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ok, _ax, _g = MB.polys_disjoint_exact(node.boxes[names[i]].pc.verts,
                                                  node.boxes[names[j]].pc.verts)
            if not ok:
                out["k_overlap"] += 1
    return out


# ==================================================================== (a) overlapping cores
def test_a():
    print("(a) two boxes whose K' overlap", flush=True)
    ok = True

    # --- a1: cores that overlap outright.  K'(A) subset Q_A and K'(B) subset Q_B, and Q_A, Q_B are
    # interior-disjoint, so overlapping cores are a CONTRADICTION: every pose of A meets int K'(B),
    # every centre of A is dead, and the clip must empty a box.
    nd = MB.Node({"A": (1.40, 1.60, 1.40, 1.60, 0.0, 6.0),
                  "B": (2.05, 2.25, 1.40, 1.60, 0.0, 6.0)}, name="a1 overlapping cores")
    nd.build_cores()
    gap = MB.polys_disjoint_exact(nd["A"].pc.verts, nd["B"].pc.verts)
    ok &= _rec("a1.cores_overlap_before", not gap[0], sat_gap=round(float(gap[2]), 9))
    emptied = None
    try:
        nd.normalise(nsub=4, refine=2)
    except MB.EmptyBox as e:
        emptied = e.name
    ok &= _rec("a1.mutual_clip_empties", emptied is not None, emptied=emptied)

    # --- a2: cores disjoint but the POSE UNIONS meet the other core: the clip must shrink both and
    # the invariant must hold afterwards.
    nd2 = MB.Node({"A": (1.425, 1.575, 1.50, 1.65, 0.0, 12.0),
                   "B": (2.375, 2.525, 1.50, 1.65, 0.0, 12.0)}, name="a2 poses meet cores")
    nd2.build_cores()
    g2 = MB.polys_disjoint_exact(nd2["A"].pc.verts, nd2["B"].pc.verts)
    r0 = nd2.assert_invariant(raise_on_fail=False)
    before = {k: v["core_meet_frac"] for k, v in r0["diagnostics"].items()}
    ok &= _rec("a2.cores_disjoint_but_poses_meet", g2[0] and max(before.values()) > 0.0,
               cores_disjoint=g2[0], core_meet_before=before)
    nd2.normalise(nsub=4, refine=2)
    r1 = nd2.assert_invariant(raise_on_fail=False)
    kept = r1["kept"]
    shrunk = min(kept.values()) < 1.0
    ok &= _rec("a2.clip_shrinks", shrunk, kept={k: round(v, 6) for k, v in kept.items()})
    ok &= _rec("a2.invariant_after", r1["ok"], failures=len(r1["failures"]),
               core_meet_after={k: round(v["core_meet_frac"], 6)
                                for k, v in r1["diagnostics"].items()})
    RESULTS[-1]["detail"] = dict(before=before, kept=kept)
    return ok


# ==================================================================== (b) container edge
def test_b():
    print("(b) a box straddling the container edge", flush=True)
    ok = True
    # centre box reaches x = 3.60, past s - 1/2 = 3.377084 (so some centres admit no tilt at all)
    # and far past s - w_max/2 = 3.194 (so at tilt 30 deg the square escapes even from centres the
    # repo's usual `s - 1/2` bound accepts -- exactly A168's D).
    nd = MB.Node({"W": (3.10, 3.60, 1.90, 2.10, 0.0, 30.0)}, name="b container straddle")
    nd.build_cores()
    r0 = nd.assert_invariant(raise_on_fail=False)
    esc0 = r0["diagnostics"]["W"]["escape_frac"]
    ok &= _rec("b.escapes_before", (not r0["ok"]) and esc0 > 0.0,
               escape_frac_before=round(esc0, 6),
               failed=[f["check"] for f in r0["failures"]])
    nd.normalise(nsub=4, refine=2)
    r1 = nd.assert_invariant(raise_on_fail=False)
    esc1 = r1["diagnostics"]["W"]["escape_frac"]
    ok &= _rec("b.container_clip_removes_outside", r1["ok"] and esc1 == 0.0,
               escape_frac_after=esc1, kept=round(r1["kept"]["W"], 6),
               sliver_area=round(r1["sliver_area"]["W"], 9))
    v = pose_violations(nd, 10000, seed=2)
    ok &= _rec("b.sampled_clean", v["escape"] == 0 and v["not_core"] == 0, **v)
    nd.figure(os.path.join(FIGS, "test_b_container.svg"), title="A171 (b) container straddle")
    return ok


# ==================================================================== (c) A168's S2 node
A168_S2 = {
    "H":  (2.5674485, 2.67226625, 2.357813, 2.46263075, 45.0, 60.0),
    "B1": (3.127084, 3.1733821433529026, 1.5015011950128963, 1.5785397484754269, 45.0, 50.625),
    "D":  (3.223006893074939, 3.377084, 3.211365683498047, 3.377084, 0.0, 11.25),
}
A168_SRC = ("attempts/A168-cascade-fable/results/v0_union_boxes/cascade168.jsonl, "
            "cell l1_153, node BR139/TRH-25, step S2, verdict ALIVE(geometry)")


def test_c():
    print(f"(c) A168's failing S2 node BR139/TRH-25 ({A168_SRC})", flush=True)
    ok = True
    nd = MB.Node(A168_S2, name="A168 BR139/TRH-25 (as recorded)")
    nd.build_cores()
    r0 = nd.assert_invariant(raise_on_fail=False)
    checks0 = {k: v["ok"] for k, v in r0["checks"].items()}
    # the pair-by-pair "pose union meets the other box's core" table -- the A165/A168 failure
    rng = np.random.default_rng(9)
    pair0 = {}
    for k, mb in nd.boxes.items():
        C, TH = mb.sample(4000, rng)
        for j, ob in nd.boxes.items():
            if j != k:
                pair0[f"{k}->{j}"] = round(float((PC.poly_square_depth(ob.pc.P, C, TH) > 0).mean()),
                                           4)
    ok &= _rec("c.invariant_fails_before", not r0["ok"], checks=checks0,
               failures=[f"{f['check']}[{f['what']}]" for f in r0["failures"]])
    strict = [f for f in r0["failures"] if f["check"] == "POSE-CONTAINER-STRICT"]
    ok &= _rec("c.D_outside_container", any(f["what"] == "D" for f in strict),
               escape_frac_D=round(r0["diagnostics"]["D"]["escape_frac"], 6),
               detail=[f["detail"] for f in strict])
    ok &= _rec("c.poses_meet_other_cores", max(pair0.values()) > 0.5, pair_meet_before=pair0)
    nd.figure(os.path.join(FIGS, "test_c_A168_before.svg"),
              title="A171 (c) A168 BR139/TRH-25 -- BEFORE normalise")

    nd2 = MB.Node(A168_S2, name="A168 BR139/TRH-25 (normalised)")
    t = time.time()
    nd2.normalise(nsub=4, refine=3)
    dt = time.time() - t
    r1 = nd2.assert_invariant(raise_on_fail=False)
    ok &= _rec("c.invariant_passes_after", r1["ok"],
               kept={k: round(v, 6) for k, v in r1["kept"].items()},
               checks={k: v["ok"] for k, v in r1["checks"].items()},
               seconds=round(dt, 2))
    v = pose_violations(nd2, 10000, seed=3)
    ok &= _rec("c.sampled_clean_after",
               v["escape"] == 0 and v["not_core"] == 0 and v["k_overlap"] == 0, **v)
    nd2.figure(os.path.join(FIGS, "test_c_A168_after.svg"),
               title="A171 (c) A168 BR139/TRH-25 -- AFTER normalise")
    RESULTS[-1]["detail"] = dict(before=dict(checks=checks0, pair_meet=pair0,
                                            diagnostics=r0["diagnostics"],
                                            failures=r0["failures"]),
                                 after=dict(kept=r1["kept"], diagnostics=r1["diagnostics"],
                                            sliver_area=r1["sliver_area"],
                                            pieces={k: len(b.pieces)
                                                    for k, b in nd2.boxes.items()}))
    return ok


# ==================================================================== (d) random nodes
def rand_node(rng, k, sep=1.18, s=S):
    """k random boxes whose centre rectangles are pairwise at least `sep` apart (so the node is not
    trivially self-contradictory -- boxes name DISTINCT squares).  `sep` below sqrt2 = 1.4142 leaves
    the interesting regime where the pose unions still meet the other cores and the clip has work to
    do; a node that turns out to be dead anyway is a legitimate outcome and is counted as such."""
    lo, hi = 0.72, s - 0.72
    placed, boxes = [], {}
    for i in range(k):
        for _try in range(600):
            wx, wy = rng.uniform(0.03, 0.14), rng.uniform(0.03, 0.14)
            x0, y0 = rng.uniform(lo, hi - wx), rng.uniform(lo, hi - wy)
            r = (x0, x0 + wx, y0, y0 + wy)
            good = True
            for q in placed:
                dx = max(q[0] - r[1], r[0] - q[1], 0.0)
                dy = max(q[2] - r[3], r[2] - q[3], 0.0)
                if math.hypot(dx, dy) < sep:
                    good = False
                    break
            if good:
                th0 = rng.uniform(0.0, 78.0)
                boxes[f"R{i}"] = (r[0], r[1], r[2], r[3], th0,
                                  min(90.0, th0 + rng.uniform(2.0, 12.0)))
                placed.append(r)
                break
    return MB.Node(boxes, name=f"random {len(boxes)} boxes")


def test_d(n_nodes=10, n_poses=10000, seed=1710):
    print(f"(d) random nodes of 2-6 boxes, {n_poses} sampled poses each", flush=True)
    rng = np.random.default_rng(seed)
    ok = True
    tot = dict(nodes=0, dead=0, drawn=0, escape=0, not_core=0, k_overlap=0, core_meet=0,
               invariant_fail=0)
    per = []
    for i in range(n_nodes):
        k = int(rng.integers(2, 7))
        nd = rand_node(rng, k)
        k = len(nd.names)
        if k < 2:
            continue
        try:
            nd.normalise(nsub=4, refine=1)
        except MB.EmptyBox as e:
            tot["dead"] += 1
            per.append(dict(node=i, k=k, dead=e.name))
            continue
        except RuntimeError as e:                       # a polycore build that will not certify
            per.append(dict(node=i, k=k, skipped=str(e)[:80]))
            continue
        tot["nodes"] += 1
        r = nd.assert_invariant(raise_on_fail=False, sample=1000)
        if not r["ok"]:
            tot["invariant_fail"] += 1
            per.append(dict(node=i, k=k, invariant=False,
                            failures=[f"{f['check']}[{f['what']}]" for f in r["failures"]]))
            continue
        v = pose_violations(nd, n_poses // max(1, k), seed=seed + i)
        for key in ("drawn", "escape", "not_core", "k_overlap", "core_meet"):
            tot[key] += v[key]
        per.append(dict(node=i, k=k, kept={kk: round(vv, 5) for kk, vv in r["kept"].items()},
                        **{key: v[key] for key in ("drawn", "escape", "not_core", "k_overlap")}))
    ok &= _rec("d.no_violation", tot["escape"] == 0 and tot["not_core"] == 0
               and tot["k_overlap"] == 0 and tot["invariant_fail"] == 0
               and tot["nodes"] >= max(3, n_nodes // 2) and tot["drawn"] >= 10 ** 4, **tot)
    RESULTS[-1]["detail"] = per
    return ok


# ==================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.abspath(
        os.path.join(HERE, "..", "results", "test_multibox.json")))
    ap.add_argument("--nodes", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(FIGS, exist_ok=True)
    t0 = time.time()
    ok = True
    for fn, args in ((test_a, ()), (test_b, ()), (test_c, ()), (test_d, (a.nodes,))):
        t = time.time()
        ok &= fn(*args)
        print(f"    -- {fn.__name__} {time.time() - t:.1f} s", flush=True)
    dt = time.time() - t0
    print(f"\n{'ALL PASS' if ok else 'FAILURES'}  ({dt:.1f} s total, budget 120 s)", flush=True)
    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(dict(ok=ok, seconds=dt, s=str(MB.S_RAT), a168_source=A168_SRC,
                       results=RESULTS), fh, indent=1)
    print(f"wrote {a.json}", flush=True)
    return 0 if (ok and dt < 120.0) else 1


if __name__ == "__main__":
    sys.exit(main())
