"""A145 T1 -- the IMPOSSIBLE dual-support weight of every surviving A57 node.

For a node whose hypothesis is "some square Q0 of the packing has (centre, tilt) in one of the
boxes B_0..B_5" (five PINS plus the conditioned box H), a dual-support column -- a placement the
node's LP is charging weight y to -- is IMPOSSIBLE if the unit square it draws overlaps one of
those hypothesis squares at EVERY pose of that square's box: two unit squares of the same packing
cannot overlap, so no packing satisfying the hypothesis contains that placement, and the weight
the LP puts on it is weight it should never have had.

Two tests, both reported:

  * GRID (the PI's reading, A142 `gallery142.gap_over_box`): the SAT gap on a 7^3 pose grid of the
    box is negative at every sampled pose.  A screen -- a grid can miss a pose.
  * EXACT (the sound one): the column meets K'(B) = INTERSECTION over all poses of Q(c,theta),
    A132's certified polygon core, and for a PIN box the exact axis square of half-side
    a_pin = 33873816211/68719476736 (A135 `exactcore`), which for zero tilt width IS that whole
    intersection.  Meeting K' implies overlapping at every pose, with no grid in the argument.

EXACT is a subset of GRID up to the grid's own error, and EXACT is exactly the set of rows A135's
`poly` arm prunes -- so `w_imposs_exact / w_total` is a prediction of how much of the node's LP
objective the re-solve of T2 can take away.  The `> EPS_CORE` column is the LP's own drop margin.

Read-only on every campaign and on A132/A135/A142 (imported, never written).

    set PYTHONDONTWRITEBYTECODE=1 && python code/measure145.py [--limit N] [--lo I --hi J]
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
A142 = os.path.join(ATT, "A142-a57-review-gallery")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), os.path.join(A135, "code"),
           os.path.join(A142, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                            # noqa: E402
import polycore                                               # noqa: E402
import exactcore                                              # noqa: E402
from caselp import Box, EPS_CORE                              # noqa: E402

NPOSE = 7                       # A142/gen_a57_lp's 7^3 pose grid
POP = os.path.join(A142, "results", "population142.json")
CLIPKILL = os.path.join(A142, "results", "exactclip_kills_a57.jsonl")


# ------------------------------------------------------------------ population
def population():
    """The 448 surviving A57 nodes: A142's 465 minus A142's own 17 exact-pin-clip kills."""
    d = json.load(open(POP, encoding="utf-8"))
    killed = set()
    for ln in open(CLIPKILL, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            killed.add(json.loads(ln)["id"])
    rows = [r for r in d["rank_a57"] if r["id"] not in killed]
    return rows, d, killed


_IDX = None


def load_node(nid):
    """The node's stored LP record -- the one with the most dual support if several match."""
    global _IDX
    if _IDX is None:
        import glob
        _IDX = {}
        for f in glob.glob(os.path.join(A57, "results", "tree", "*", "*.json")):
            _IDX.setdefault(os.path.basename(f)[:-5], []).append(f)
    best = None
    for p in sorted(_IDX.get(nid, [])):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if d.get("hyp", {}).get("boxes"):
            if best is None or len(d.get("packing") or []) > len(best[0].get("packing") or []):
                best = (d, os.path.relpath(p, ROOT).replace("\\", "/"))
    return best


# ------------------------------------------------------------------ cores, cached by box key
_KP = {}


def kprime(bj):
    """(P, kind) -- the vertex array of the box's exact all-poses core.

    A PIN box (zero tilt width) gets A135's certified exact axis square, which for zero tilt width
    IS the full intersection; every other box gets A132's certified polygon K'(B)."""
    b = Box.from_json(bj)
    k = b.key()
    hit = _KP.get(k)
    if hit is not None:
        return hit
    is_pin = (b.th1 <= b.th0 + 1e-12)
    if is_pin:
        a, a0, ok = exactcore.exact_a(b)
        af = float(a if a is not None else a0)
        cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
        P = np.array([[cx - af, cy - af], [cx + af, cy - af],
                      [cx + af, cy + af], [cx - af, cy + af]], float)
        hit = (P, "exact-pin-core", af, bool(ok))
    else:
        pc = polycore.build(b)
        hit = (np.asarray(pc.P, float), "K'(B) polygon", None, bool(pc.certified))
    _KP[k] = hit
    return hit


def box_poses(bj, n=NPOSE):
    """the 7^3 grid of poses of the hypothesis square over its box (A142's `box_poses`)."""
    def ax(lo, hi):
        return [lo] if hi <= lo else [lo + (hi - lo) * i / (n - 1.0) for i in range(n)]
    xs, ys = ax(bj["x0"], bj["x1"]), ax(bj["y0"], bj["y1"])
    ts = ax(bj["th0"], bj["th1"])
    C, T = [], []
    for x in xs:
        for y in ys:
            for t in ts:
                C.append((x, y))
                T.append(math.radians(t))
    return np.array(C, float), np.array(T, float)


def col_square(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c)]
                     for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], float)


# ------------------------------------------------------------------ the measurement
def measure(rec, d, recpath):
    boxes = d["hyp"]["boxes"]
    npin = len(boxes) - 1
    pk = d.get("packing") or []
    poses = [box_poses(b) for b in boxes]
    kp = [kprime(b) for b in boxes]

    out = dict(rec)
    out["record"] = recpath
    out["n_boxes"] = len(boxes)
    out["tau_rec"] = d.get("tau")
    out["budget"] = d.get("budget")
    out["eta_rec"] = (d["tau"] - d["budget"]) if d.get("tau") is not None else None
    out["converged_rec"] = d.get("converged")
    out["minmass_rec"] = d.get("minmass")
    out["box"] = boxes[-1]
    out["core_certified"] = all(k[3] for k in kp)
    out["a_pin_exact"] = kp[0][2]

    w_tot = 0.0
    n = len(pk)
    n_grid = n_ex = n_ex_eps = 0
    w_grid = w_ex = w_ex_eps = 0.0
    n_ex_H = n_ex_pin = 0
    w_ex_H = w_ex_pin = 0.0
    cols = []
    for k, p in enumerate(pk):
        cx, cy, th = float(p["cx"]), float(p["cy"]), float(p["theta"])
        y = float(p.get("y", 0.0))
        w_tot += y
        P = col_square(cx, cy, th)
        # --- GRID: overlaps that hypothesis square at every one of the 7^3 sampled poses
        gmin, gowner = 9e9, None
        for j, (C, T) in enumerate(poses):
            g = float(-polycore.poly_square_depth(P, C, T).min())   # max SAT gap over the grid
            if g < gmin:
                gmin, gowner = g, j
        grid = gmin < -1e-9
        # --- EXACT: meets the box's certified all-poses core
        dmax, downer = -9e9, None
        for j, (KP, _kind, _a, _ok) in enumerate(kp):
            dep = float(polycore.poly_square_depth(KP, [[cx, cy]], [th])[0])
            if dep > dmax:
                dmax, downer = dep, j
        ex = dmax > 0.0
        ex_eps = dmax > EPS_CORE
        if grid:
            n_grid += 1
            w_grid += y
        if ex:
            n_ex += 1
            w_ex += y
            if downer == npin:
                n_ex_H += 1
                w_ex_H += y
            else:
                n_ex_pin += 1
                w_ex_pin += y
        if ex_eps:
            n_ex_eps += 1
            w_ex_eps += y
        if grid or ex:
            cols.append(dict(col=k, y=round(y, 6),
                             grid=bool(grid), grid_owner=gowner, grid_overlap=round(-gmin, 6),
                             exact=bool(ex), exact_owner=downer,
                             exact_kind=(kp[downer][1] if downer is not None else None),
                             exact_depth=round(dmax, 9),
                             owner_name=("H" if downer == npin else f"P{downer}"),
                             pose=[round(cx, 6), round(cy, 6),
                                   round(math.degrees(th) % 90.0, 4)]))
    out.update(n_support_meas=n, w_total=round(w_tot, 6),
               n_imposs_grid=n_grid, w_imposs_grid=round(w_grid, 6),
               n_imposs_exact=n_ex, w_imposs_exact=round(w_ex, 6),
               n_imposs_exact_eps=n_ex_eps, w_imposs_exact_eps=round(w_ex_eps, 6),
               n_imposs_exact_H=n_ex_H, w_imposs_exact_H=round(w_ex_H, 6),
               n_imposs_exact_pin=n_ex_pin, w_imposs_exact_pin=round(w_ex_pin, 6),
               frac_grid=(round(w_grid / w_tot, 6) if w_tot > 0 else None),
               frac_exact=(round(w_ex / w_tot, 6) if w_tot > 0 else None),
               frac_exact_eps=(round(w_ex_eps / w_tot, 6) if w_tot > 0 else None),
               frac_cols_exact=(round(n_ex / n, 6) if n else None),
               columns=cols[:64])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "impossible_weight.jsonl"))
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    rows, pop, killed = population()
    if a.hi:
        rows = rows[a.lo:a.hi]
    elif a.lo:
        rows = rows[a.lo:]
    if a.limit:
        rows = rows[:a.limit]
    print(f"A145 T1: {len(rows)} of the 448 surviving A57 nodes "
          f"(A142's 465 minus its {len(killed)} exact-pin-clip kills)", flush=True)
    t0 = time.time()
    n_err = n_norec = 0
    with open(a.out, "w", encoding="utf-8") as fh:
        for i, r in enumerate(rows):
            got = load_node(r["id"])
            if got is None:
                n_norec += 1
                fh.write(json.dumps(dict(r, status="no-record")) + "\n")
                continue
            d, recpath = got
            try:
                out = measure(r, d, recpath)
                out["status"] = "ok"
            except Exception as e:
                n_err += 1
                out = dict(r, status="error", error=repr(e)[:300])
            fh.write(json.dumps(out) + "\n")
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/{len(rows)}  {time.time() - t0:.0f} s  "
                      f"no-record {n_norec}  errors {n_err}", flush=True)
    print(f"done {len(rows)} nodes in {time.time() - t0:.0f} s "
          f"({n_norec} without a stored record, {n_err} errors) -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
