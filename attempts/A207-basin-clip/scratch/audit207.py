"""A207 (copy of A206 scratch/audit206.py; certs/basinclip207_<nid>.json runs[<run key>]; every non-pin role's sampled poses are ALSO
filtered by the basins of the run -- a pose inside B_F(p) x T_B is not admissible by Lemma BASIN, so a BASIN kill is audited too) -- audit of a FULL-ROLE kill by pose sampling: every non-pin role of the node (H over A203's alive units meeting its
forced slots; each instantiated role F_i on a grid over its recorded hull box meeting every slot it is named at; a
BRANCH row role over its cell) -- a pairwise interior-disjoint, admissible configuration of ALL of them would refute a
kill that says one role has no pose left (EmptyBox / S-CLIP) or that a slot cannot be met.  Greedy depth-first over the
roles with caps per level; 0 = consistent.        python audit206.py <nid> <run key> <leaf> [--nh 200] [--step 0.03] [--tstep 3]"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "A205-clip-tree", "scratch"))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import audit205 as A5                                           # noqa: E402

S0, inside, meets_box, sat_disjoint, pin_free, grid = A5.S0, A5.inside, A5.meets_box, A5.sat_disjoint, A5.pin_free, A5.grid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid"); ap.add_argument("pad"); ap.add_argument("leaf")
    ap.add_argument("--nh", type=int, default=200); ap.add_argument("--step", type=float, default=0.03); ap.add_argument("--tstep", type=float, default=3.0)
    ap.add_argument("--cap", type=int, default=40)
    a = ap.parse_args()
    cert = json.load(open(os.path.join(HERE, "..", "certs", "basinclip207_%s.json" % a.nid), encoding="utf-8"))
    d = cert["runs"][a.pad]
    a.pad = d["pad"]
    basins = d.get("basins") or []

    def in_basin(X, Y, T):
        """inside some basin box x tilt basin (tilt folded mod 90 deg into [0, 90))."""
        m = np.zeros(len(X), bool)
        for b in basins:
            x0, x1, y0, y1 = b["box"]
            tr = float(__import__("fractions").Fraction(b["t_r"]))
            deg = np.degrees(T) % 90.0
            tin = (np.tan(np.radians(deg) / 2) <= tr + 1e-12) | (np.tan(np.radians(90.0 - deg) / 2) <= tr + 1e-12)
            m |= (X >= x0 - 1e-12) & (X <= x1 + 1e-12) & (Y >= y0 - 1e-12) & (Y <= y1 + 1e-12) & tin
        return m
    nodes = d["nodes"]
    node = [n for n in nodes if n["label"] == a.leaf][0]
    parent = nodes[max(0, nodes.index(node) - 1)]
    st = A5.P.load_start(a.nid, a.pad)
    wbox = (cert.get("wbox_pad") or {}).get(a.pad) or cert["wbox"]
    cells = cert["cells"]
    pins = [(0.5 * (v["box"][0] + v["box"][1]), 0.5 * (v["box"][2] + v["box"][3])) for k, v in nodes[0]["snapshot"]["roles"].items() if k.startswith("P")]
    forced = sorted(set(node.get("forced_H") or []))
    rs = node.get("role_slots") or {}
    rc = node.get("role_cell") or {}
    boxes = dict(parent.get("roles") or {})
    boxes.update({k: v for k, v in (node.get("roles") or {}).items() if k not in boxes})
    print("%s %s leaf %s: %s\n  H forced at %s; roles %s; cells %s" % (a.nid, a.pad, a.leaf, str(node.get("leaf"))[:160], forced, rs, rc))
    units = A5.P.unit_pieces(st["H_box"], st["units"]) if st.get("units") else []
    rng = np.random.default_rng(2051)
    H = []
    for (bn, r) in units:
        x0, x1, y0, y1 = (float(v) for v in r)
        t0, t1 = float(bn.t0), float(bn.t1)
        for _ in range(max(1, a.nh // max(1, len(units)))):
            H.append((rng.uniform(x0, x1), rng.uniform(y0, y1), 2 * math.atan(rng.uniform(t0, t1))))
    H = np.array(H)
    ok = inside(H[:, 0], H[:, 1], H[:, 2]) & pin_free(H[:, 0], H[:, 1], H[:, 2], pins)
    for p in forced:
        ok &= meets_box(H[:, 0], H[:, 1], H[:, 2], wbox[p])
    for p in (node.get("miss") or {}).get("H", []):
        ok &= ~meets_box(H[:, 0], H[:, 1], H[:, 2], wbox[p])
    nb = int((ok & in_basin(H[:, 0], H[:, 1], H[:, 2])).sum())
    ok &= ~in_basin(H[:, 0], H[:, 1], H[:, 2])
    print("  H poses inside a basin (removed by Lemma BASIN): %d" % nb)
    H = H[ok]
    if len(H) > a.nh:
        H = H[rng.choice(len(H), a.nh, replace=False)]
    print("  H poses admissible: %d" % len(H))
    R = []
    for role in sorted(rs):
        box = boxes.get(role)
        if box is None:
            print("  role %s: no box recorded, skipped" % role); continue
        W = [box[0] - 0.5, box[1] + 0.5, box[2] - 0.5, box[3] + 0.5]          # centres over the hull box, any tilt
        cell = cells[rc[role]] if rc.get(role, -1) >= 0 else None
        X, Y, T = grid(W, a.step, a.tstep, cell=cell)
        m = (X >= box[0] - 1e-9) & (X <= box[1] + 1e-9) & (Y >= box[2] - 1e-9) & (Y <= box[3] + 1e-9)
        X, Y, T = X[m], Y[m], T[m]
        okf = inside(X, Y, T) & pin_free(X, Y, T, pins)
        for p in rs[role]:
            okf &= meets_box(X, Y, T, wbox[p])
        for p in (node.get("miss") or {}).get(role, []):          # A206 Rule NS: a [role misses slot] hypothesis on the path
            okf &= ~meets_box(X, Y, T, wbox[p])
        nb = int((okf & in_basin(X, Y, T)).sum())
        okf &= ~in_basin(X, Y, T)
        print("  role %s: %d admissible poses inside a basin removed (Lemma BASIN)" % (role, nb))
        R.append((role, X[okf], Y[okf], T[okf]))
        print("  role %s: box %s, slots %s, cell %s: %d admissible poses meeting every slot" % (role, [round(v, 3) for v in box[:4]], rs[role], rc.get(role), int(okf.sum())))
    if any(len(r[1]) == 0 for r in R):
        print("  a role has NO admissible pose meeting its slots on the grid: consistent with the kill (grid-limited)")
        return
    found = [None]
    n_try = [0]

    def rec(k, chosen):
        if k == len(R):
            found[0] = list(chosen)
            return True
        role, X, Y, T = R[k]
        m = np.ones(len(X), bool)
        for (cx, cy, ct) in chosen:
            m &= sat_disjoint(cx, cy, ct, X, Y, T)
            if not m.any():
                return False
        idx = np.nonzero(m)[0]
        rng.shuffle(idx)
        for i in idx[:a.cap]:
            n_try[0] += 1
            if rec(k + 1, chosen + [(X[i], Y[i], T[i])]):
                return True
        return False

    n_conf = 0
    for (hx, hy, hth) in H:
        if rec(0, [(hx, hy, hth)]):
            n_conf += 1
            if n_conf == 1:
                print("  REFUTED: H (%.4f, %.4f, %.1f deg) + %s" % (hx, hy, math.degrees(hth), [(r[0], round(float(c[0]), 4), round(float(c[1]), 4), round(math.degrees(c[2]), 1)) for r, c in zip(R, found[0][1:])]))
    print("  pairwise-disjoint admissible configurations of H + %s: %d (%d partial tries)  %s" % ([r[0] for r in R], n_conf, n_try[0], "-> REFUTED" if n_conf else "-> 0 refutations (consistent with the kill)"))


if __name__ == "__main__":
    main()
