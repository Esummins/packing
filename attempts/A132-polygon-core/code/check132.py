"""A132 -- sampled confirmations of every geometric count, reported as drawn -> tested -> hits.

  A  K' vertices: poses drawn uniformly in B; a HIT is a violation |R(-th)(v-c)|_inf > 1/2.
     (The exact rational certification in polycore.build is the proof; this is the control.)
  B  offending support columns (meet K' but not K(a)): poses drawn in B; a HIT is a pose whose
     hypothesis square Q(c,th) actually OVERLAPS the column's square -- the claim is 100%.
  C  negative control: columns that do NOT meet K'; a HIT is a pose at which the column is
     DISJOINT from Q(c,th) -- the claim is that such poses exist, i.e. the test is not vacuous.
  D  T5-polygon kills: the exact rational witness point, re-tested on drawn poses of BOTH boxes;
     a HIT is a pose of either box that fails to contain it -- the claim is 0.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A96 = os.path.join(ROOT, "A96-a57-parametric")
for p in (os.path.join(A57, "code"), os.path.join(A96, "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                               # noqa: E402
from caselp import Box, EPS_CORE                              # noqa: E402
import recheck96                                              # noqa: E402


def poses(box, n, rng):
    C = np.stack([rng.uniform(box.x0, box.x1, n), rng.uniform(box.y0, box.y1, n)], 1)
    TH = np.radians(rng.uniform(box.th0, box.th1, n))
    return C, TH


def n_disjoint(p, phi, C, TH):
    """How many of the poses (C, TH) give a unit square DISJOINT from the unit square at (p, phi).
    SAT over the four edge-normal axes of the two squares; vectorised over the poses."""
    d = C - np.asarray(p)[None, :]
    sep = np.zeros(len(C), bool)
    for (ax, ay, hphi_from_theta) in (
            (np.full(len(C), math.cos(phi)), np.full(len(C), math.sin(phi)), True),
            (np.full(len(C), -math.sin(phi)), np.full(len(C), math.cos(phi)), True),
            (np.cos(TH), np.sin(TH), False),
            (-np.sin(TH), np.cos(TH), False)):
        proj = np.abs(d[:, 0] * ax + d[:, 1] * ay)
        h1 = 0.5 * (np.abs(math.cos(phi) * ax + math.sin(phi) * ay)
                    + np.abs(-math.sin(phi) * ax + math.cos(phi) * ay))
        h2 = 0.5 * (np.abs(np.cos(TH) * ax + np.sin(TH) * ay)
                    + np.abs(-np.sin(TH) * ax + np.cos(TH) * ay))
        sep |= proj > h1 + h2
    return int(sep.sum())


def main():
    rng = np.random.default_rng(20260907)
    M = [json.loads(l) for l in open(os.path.join(BASE, "results", "measure132.jsonl")) if l.strip()]
    M = [r for r in M if "error" not in r]
    rows = {r["id"]: r for r in recheck96.alive_rows()}
    out = {}

    # ---------------- A: K' vertices
    sample = [r for r in M if r["camp"] == "A57"]
    idx = rng.choice(len(sample), size=40, replace=False)
    drawn = tested = hits = 0
    worst = 0.0
    for i in idx:
        r = sample[int(i)]
        b = Box.from_json(rows[r["id"]]["box"])
        pc = polycore.build(b)
        C, TH = poses(b, 10000, rng)
        drawn += 10000
        for (vx, vy) in pc.verts:
            d = np.stack([float(vx) - C[:, 0], float(vy) - C[:, 1]], 1)
            u = np.abs(d[:, 0] * np.cos(TH) + d[:, 1] * np.sin(TH))
            w = np.abs(-d[:, 0] * np.sin(TH) + d[:, 1] * np.cos(TH))
            m = np.maximum(u, w)
            tested += 10000
            hits += int((m > 0.5).sum())
            worst = max(worst, float(m.max()))
    out["A_vertices"] = dict(nodes=len(idx), poses_drawn=drawn, vertex_pose_tests=tested,
                             hits_violations=hits, max_linf=worst)
    print(f"A  K' vertices: drawn {drawn} poses over {len(idx)} nodes -> tested {tested} "
          f"(vertex, pose) pairs -> hits {hits} violations (max |.|_inf {worst:.9f})")

    # ---------------- B/C: the offending columns and the negative control
    npose = 1000
    dB = tB = hB = 0
    dC = tC = hC = 0
    colsB = colsC = 0
    for i in idx[:20]:
        r = sample[int(i)]
        b = Box.from_json(rows[r["id"]]["box"])
        pc = polycore.build(b)
        d = None
        for p in __import__("glob").glob(os.path.join(A57, "results", "tree", "*", r["id"] + ".json")):
            dd = json.load(open(p))
            bb = dd["hyp"]["boxes"][-1]
            if all(abs(float(bb[k]) - getattr(b, k)) < 1e-9 for k in ("x0", "x1", "y0", "y1", "th0", "th1")):
                d = dd
                break
        if d is None:
            continue
        P = np.array([[q["cx"], q["cy"], q["theta"]] for q in d["packing"]], float).reshape(-1, 3)
        if not len(P):
            continue
        dp = polycore.poly_square_depth(pc.P, P[:, :2], P[:, 2])
        kcore = b.core()
        dc = polycore.core_depth_fast(kcore, P[:, :2], P[:, 2])
        C, TH = poses(b, npose, rng)
        for k in range(len(P)):
            off = dp[k] > EPS_CORE and dc[k] <= EPS_CORE
            n_dis = n_disjoint(P[k, :2], P[k, 2], C, TH)
            if off:
                colsB += 1
                dB += npose; tB += npose; hB += npose - n_dis
            elif dp[k] <= 0.0:
                colsC += 1
                dC += npose; tC += npose; hC += n_dis
    out["B_offending"] = dict(columns=colsB, poses_drawn=dB, tested=tB, hits_overlap=hB,
                              frac=hB / max(tB, 1))
    out["C_control"] = dict(columns=colsC, poses_drawn=dC, tested=tC, hits_disjoint=hC,
                            frac=hC / max(tC, 1))
    print(f"B  offending support columns: drawn {dB} poses over {colsB} columns -> tested {tB} "
          f"(column, pose) pairs -> hits {hB} overlaps ({100.0 * hB / max(tB, 1):.2f}%, claim 100%)")
    print(f"C  negative control (columns that miss K'): drawn {dC} over {colsC} columns -> "
          f"tested {tC} -> hits {hC} disjoint poses ({100.0 * hC / max(tC, 1):.2f}%, claim > 0)")

    # ---------------- D: the T5-polygon witnesses
    from fractions import Fraction as Fr
    fire = [r for r in M if r.get("t5poly_dead")]
    dD = tD = hD = 0
    for r in fire:
        b = Box.from_json(rows[r["id"]]["box"]) if r["camp"] == "A57" else None
        if b is None:
            continue
        for h in r["t5poly_hits"]:
            if not h.get("witness"):
                continue
            vx, vy = float(Fr(h["witness"][0])), float(Fr(h["witness"][1]))
            hh = 1e-2 / math.sqrt(2.0)
            # the pin box is reconstructed from the record's own hypothesis list
            import glob as _g
            for p in _g.glob(os.path.join(A57, "results", "tree", "*", r["id"] + ".json")):
                dd = json.load(open(p))
                bb = dd["hyp"]["boxes"][-1]
                if all(abs(float(bb[k]) - getattr(b, k)) < 1e-9
                       for k in ("x0", "x1", "y0", "y1", "th0", "th1")):
                    pb = Box.from_json(dd["hyp"]["boxes"][h["pin"]])
                    break
            else:
                continue
            for box in (b, pb):
                C, TH = poses(box, 500, rng)
                d = np.stack([vx - C[:, 0], vy - C[:, 1]], 1)
                u = np.abs(d[:, 0] * np.cos(TH) + d[:, 1] * np.sin(TH))
                w = np.abs(-d[:, 0] * np.sin(TH) + d[:, 1] * np.cos(TH))
                dD += 500; tD += 500
                hD += int((np.maximum(u, w) > 0.5).sum())
    out["D_witness"] = dict(nodes=len(fire), poses_drawn=dD, tested=tD, hits_violations=hD)
    print(f"D  T5-polygon witnesses: drawn {dD} poses over {len(fire)} firing nodes (both boxes) "
          f"-> tested {tD} -> hits {hD} violations (claim 0)")

    with open(os.path.join(BASE, "results", "check132.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
