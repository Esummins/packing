"""A206 audit of a DEAD node by pose sampling INSIDE THE NODE'S OWN PIECES (the parent's last snapshot: every role's pieces
after the parent's fixed point, a superset of the dead node's starting hypothesis; a role the branch instantiated from a
row is sampled over its recorded hull box in its cell).  Each role's poses: uniform in each piece (centre rect x tilt
bin), kept when inside the container, pin-free (A204's samplers), meeting every slot the node names the role at, and
MISSING every slot of a Rule-NS miss hypothesis; then a greedy depth-first search for a pairwise interior-disjoint
configuration of ALL roles -- one would REFUTE the kill; 0 = consistent.  A role with no admissible sampled pose makes
the audit vacuous for that role (reported as such, not as a refutation).
      python audit206b.py <nid> <run key> <leaf> [--per-piece 6] [--cap 40] [--seed 206]"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "A205-clip-tree", "scratch"))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import audit205 as A5                                           # noqa: E402  (A205's samplers, read-only; A204's underneath)

S0, inside, sat_disjoint, pin_free = A5.S0, A5.inside, A5.sat_disjoint, A5.pin_free


def meets_box(cx, cy, th, B):
    """EXACT (separating axes): the open unit square at (cx, cy, th) meets the open box B iff the open projections overlap
    on the box's two axes and on the square's two axes (both convex)."""
    c, s_ = np.cos(th), np.sin(th)
    r = (np.abs(c) + np.abs(s_)) / 2                                # the square's half-extent on the x / y axes
    ok = (np.maximum(cx - r, B[0]) < np.minimum(cx + r, B[1])) & (np.maximum(cy - r, B[2]) < np.minimum(cy + r, B[3]))
    bx = np.array([B[0], B[1], B[0], B[1]]); by = np.array([B[2], B[2], B[3], B[3]])
    for (ux, uy) in ((c, s_), (-s_, c)):                            # the square's edge normals
        pc = cx * ux + cy * uy
        pb = ux[..., None] * bx + uy[..., None] * by
        ok &= np.maximum(pc - 0.5, pb.min(axis=-1)) < np.minimum(pc + 0.5, pb.max(axis=-1))
    return ok


def sample_pieces(pieces, per_piece, rng):
    X, Y, T = [], [], []
    for (x0, x1, y0, y1, d0, d1) in pieces:
        n = per_piece
        X.append(rng.uniform(x0, x1, n)); Y.append(rng.uniform(y0, y1, n)); T.append(np.radians(rng.uniform(d0, d1, n)))
        for cx in (x0, x1):                                       # the piece's corners at its extreme tilts too
            for cy in (y0, y1):
                for d in (d0, d1):
                    X.append([cx]); Y.append([cy]); T.append([math.radians(d)])
    return np.concatenate(X), np.concatenate(Y), np.concatenate(T)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid"); ap.add_argument("key"); ap.add_argument("leaf")
    ap.add_argument("--per-piece", type=int, default=6); ap.add_argument("--cap", type=int, default=40); ap.add_argument("--seed", type=int, default=206)
    ap.add_argument("--nh", type=int, default=0, help="ignored (auditor compatibility)")
    a = ap.parse_args()
    cert = json.load(open(os.path.join(HERE, "..", "certs", "namedsplit206_%s.json" % a.nid), encoding="utf-8"))
    d = cert["runs"][a.key]
    pad = d["pad"]
    nodes = d["nodes"]
    node = [n for n in nodes if n["label"] == a.leaf][0]
    i = nodes.index(node)
    parent = None
    for j in range(i - 1, -1, -1):                                # the nearest earlier record with a snapshot on the path (a prefix label)
        lab = nodes[j]["label"]
        if nodes[j].get("snapshot") and (a.leaf.startswith(lab) and (len(a.leaf) == len(lab) or a.leaf[len(lab)] in ".us")):
            parent = nodes[j]
            break
    if parent is None:
        parent = nodes[0]
    wbox = (cert.get("wbox_pad") or {}).get(pad) or cert["wbox"]
    cells = cert["cells"]
    snap_roles = (parent.get("snapshot") or {}).get("roles") or {}
    pins = [(0.5 * (v["box"][0] + v["box"][1]), 0.5 * (v["box"][2] + v["box"][3])) for k, v in snap_roles.items() if k.startswith("P")]
    forced = sorted(set(node.get("forced_H") or []))
    rs = dict(node.get("role_slots") or {})
    rs["H"] = forced
    rc = node.get("role_cell") or {}
    miss = node.get("miss") or {}
    boxes = dict(parent.get("roles") or {}); boxes.update({k: v for k, v in (node.get("roles") or {}).items() if k not in boxes})
    print("%s %s leaf %s: %s\n  parent snapshot %s (round %s); H forced at %s; roles %s; cells %s; misses %s" % (
        a.nid, a.key, a.leaf, str(node.get("leaf"))[:160], parent["label"], (parent.get("snapshot") or {}).get("round"), forced, rs, rc, miss))
    rng = np.random.default_rng(a.seed)
    R, vacuous = [], []
    for role in ["H"] + sorted(k for k in rs if k != "H"):
        v = snap_roles.get(role)
        if v and v.get("pieces") and len(v["pieces"]) >= v.get("n_pieces", 0):
            X, Y, T = sample_pieces(v["pieces"], a.per_piece, rng)
            src = "%d pieces of the parent's snapshot" % len(v["pieces"])
        else:
            box = boxes.get(role)
            if box is None:
                print("  role %s: no pieces and no box recorded: skipped" % role); continue
            cell = cells[rc[role]] if rc.get(role, -1) >= 0 else None
            X, Y, T = A5.grid([box[0] - 0.5, box[1] + 0.5, box[2] - 0.5, box[3] + 0.5], 0.02, 2.0, cell=cell)
            m = (X >= box[0] - 1e-9) & (X <= box[1] + 1e-9) & (Y >= box[2] - 1e-9) & (Y <= box[3] + 1e-9)
            X, Y, T = X[m], Y[m], T[m]
            src = "grid over its hull box%s" % (" in cell %d" % rc[role] if cell else "")
        ok = inside(X, Y, T) & pin_free(X, Y, T, pins)
        for p in rs.get(role, []):
            ok &= meets_box(X, Y, T, wbox[p])
        for p in miss.get(role, []):
            ok &= ~meets_box(X, Y, T, wbox[p])
        X, Y, T = X[ok], Y[ok], T[ok]
        if len(X) > 4000:
            idx = rng.choice(len(X), 4000, replace=False); X, Y, T = X[idx], Y[idx], T[idx]
        R.append((role, X, Y, T))
        print("  role %s (%s): %d admissible poses (slots %s, misses %s)" % (role, src, len(X), rs.get(role, []), miss.get(role, [])))
        if len(X) == 0:
            vacuous.append(role)
    if vacuous:
        print("  VACUOUS for %s (no admissible sampled pose: the role's own constraints already exclude the samples; consistent, not a refutation)" % vacuous)
        return
    found, n_try = [None], [0]

    def rec(k, chosen):
        if k == len(R):
            found[0] = list(chosen); return True
        role, X, Y, T = R[k]
        m = np.ones(len(X), bool)
        for (cx, cy, ct) in chosen:
            m &= sat_disjoint(cx, cy, ct, X, Y, T)
            if not m.any():
                return False
        idx = np.nonzero(m)[0]; rng.shuffle(idx)
        for i_ in idx[:a.cap]:
            n_try[0] += 1
            if rec(k + 1, chosen + [(X[i_], Y[i_], T[i_])]):
                return True
        return False

    n_conf = 0
    role0, X0, Y0, T0 = R[0]
    order = rng.permutation(len(X0))[:400]
    for i_ in order:
        if rec(1, [(X0[i_], Y0[i_], T0[i_])]):
            n_conf += 1
            if n_conf == 1:
                print("  REFUTED (sampled): %s" % [(r[0], round(float(c[0]), 4), round(float(c[1]), 4), round(math.degrees(float(c[2])), 1)) for r, c in zip(R, found[0])])
    print("  pairwise-disjoint admissible configurations of %s: %d over %d H poses (%d partial tries)  %s" % (
        [r[0] for r in R], n_conf, len(order), n_try[0], "-> REFUTED (investigate: the parent's pieces are a superset of the node's)" if n_conf else "-> 0 refutations (consistent with the kill)"))


if __name__ == "__main__":
    main()
