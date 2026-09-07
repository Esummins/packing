"""A132 T1 -- measure the polygon core K'(B) over every ALIVE node of A57 (and A60).

For each alive node:
  * build and CERTIFY K'(B) for the node box and for every pin box of the hypothesis;
  * (i)  DUAL-SUPPORT columns (`packing`: the LP's dual support, weight y) that meet K' but not
         K(a) -- the columns the LP is charging weight to that cannot exist under the node's own
         hypothesis -- and the weight they carry against the slack;
  * (ii) the same over the FULL placement pool (`rows_all`: every row the LP ever generated; the
         record's `atoms_all` are the primal ATOM points, not placements, so the pool of columns
         in the dual sense is `rows_all`);
  * (iii) the T5-polygon logic test: K'(B) meets some pin's K'(P) => the node is dead by logic.

"meets" uses the LP's own margin EPS_CORE = 2e-3 (a row is dropped only if it penetrates by more
than that); the strict depth > 0 count is reported alongside.  Read-only on every campaign.

    python code/measure132.py [--out results/measure132.json] [--limit N]
"""
import argparse
import glob
import json
import math
import os
import sys
import time
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A96 = os.path.join(ROOT, "A96-a57-parametric")
A60 = os.path.join(ROOT, "A60-trump5-campaign")
for p in (os.path.join(A57, "code"), os.path.join(A96, "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                              # noqa: E402
from caselp import Box, EPS_CORE                             # noqa: E402
import pinguard                                              # noqa: E402
import recheck96                                             # noqa: E402

EPS = EPS_CORE          # 2e-3, the LP's own drop margin


# ------------------------------------------------------------------ node discovery
def _node_index(pattern):
    idx = defaultdict(list)
    for f in glob.glob(pattern):
        idx[os.path.basename(f)[:-5]].append(f)
    return idx


def _match_box(path, box_json):
    try:
        d = json.load(open(path))
    except Exception:
        return None
    bs = d.get("hyp", {}).get("boxes") or []
    if not bs:
        return None
    b = bs[-1]
    for k in ("x0", "x1", "y0", "y1", "th0", "th1"):
        if abs(float(b[k]) - float(box_json[k])) > 1e-9:
            return None
    return d


def a57_alive():
    """[(key, record, node-json)] over A57's ALIVE population."""
    idx = _node_index(os.path.join(A57, "results", "tree", "*", "*.json"))
    out = []
    for r in recheck96.alive_rows():
        d = None
        for p in idx.get(r["id"], []):
            d = _match_box(p, r["box"])
            if d is not None:
                break
        if d is None:
            continue
        out.append((dict(camp="A57", id=r["id"], cls=r["_cls"],
                         level=1 + r["id"].count("_D"), budget=r.get("budget") or 5,
                         tau=r.get("tau"), eta=r.get("eta")), d))
    return out


def a60_alive():
    idx = _node_index(os.path.join(A60, "results", "nodes", "*.json"))
    out, seen = [], set()
    for f in glob.glob(os.path.join(A60, "results", "*.jsonl")):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if not str(r.get("verdict") or "").startswith("refused"):
                continue
            tag = r.get("tag")
            if not tag or tag in seen or not r.get("box"):
                continue
            d = None
            for p in idx.get(tag, []):
                d = _match_box(p, r["box"])
                if d is not None:
                    break
            if d is None:
                continue
            seen.add(tag)
            out.append((dict(camp="A60", id=tag, cls="trump5_j%s" % r.get("depth_j"),
                             level=int(r.get("depth_j") or 0) + 1, budget=r.get("budget") or 5,
                             tau=r.get("tau"), eta=r.get("eta")), d))
    return out


# ------------------------------------------------------------------ per-node measurement
_PC_CACHE = {}


def polycore_for(box):
    k = box.key()
    pc = _PC_CACHE.get(k)
    if pc is None:
        pc = polycore.build(box)
        _PC_CACHE[k] = pc
    return pc


def measure(meta, d):
    boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
    nb = boxes[-1]                                    # the conditioned box
    pins = boxes[:-1]
    cores = [b.core() for b in boxes]
    pcs = [polycore_for(b) for b in boxes]

    rec = dict(meta)
    rec["n_boxes"] = len(boxes)
    rec["poly_verts"] = len(pcs[-1].verts)
    rec["a_axis"] = float(cores[-1].a)
    rec["area_core"] = (2.0 * float(cores[-1].a)) ** 2
    rec["area_poly"] = pcs[-1].area()
    rec["area_ratio"] = rec["area_poly"] / rec["area_core"] if rec["area_core"] > 0 else None
    rec["theta_width_deg"] = nb.th1 - nb.th0
    rec["box_width"] = max(nb.x1 - nb.x0, nb.y1 - nb.y0)

    def scan(P):
        """P = (m,4) [cx, cy, theta, w] -> counts and weights"""
        if len(P) == 0:
            return dict(n=0, n_poly_only=0, n_poly_only_strict=0, w=0.0, w_poly_only=0.0)
        C = P[:, :2]
        TH = P[:, 2]
        W = P[:, 3]
        core_hit = np.zeros(len(P), bool)
        poly_hit = np.zeros(len(P), bool)
        poly_hit_s = np.zeros(len(P), bool)
        for c, pc in zip(cores, pcs):
            core_hit |= polycore.core_depth_fast(c, C, TH) > EPS
            dp = polycore.poly_square_depth(pc.P, C, TH)
            poly_hit |= dp > EPS
            poly_hit_s |= dp > 0.0
        only = poly_hit & ~core_hit
        only_s = poly_hit_s & ~core_hit
        return dict(n=int(len(P)), n_core=int(core_hit.sum()), n_poly=int(poly_hit.sum()),
                    n_poly_only=int(only.sum()), n_poly_only_strict=int(only_s.sum()),
                    w=float(W.sum()), w_poly_only=float(W[only].sum()),
                    w_poly_only_strict=float(W[only_s].sum()))

    pk = np.array([[p["cx"], p["cy"], p["theta"], p["y"]] for p in d.get("packing", [])],
                  dtype=float).reshape(-1, 4)
    rec["support"] = scan(pk)
    rows = np.array(d.get("rows_all") or [], dtype=float).reshape(-1, 3)
    if len(rows):
        rows = np.hstack([rows, np.zeros((len(rows), 1))])
    rec["pool"] = scan(rows)
    rec["n_atoms_all"] = len(d.get("atoms_all") or [])

    tau = d.get("tau")
    bud = d.get("budget") or meta["budget"]
    rec["tau_rec"] = tau
    rec["budget_rec"] = bud
    if tau is not None:
        rec["slack_brief"] = tau - (bud - 1)          # the brief's slack
        rec["slack_tight"] = tau - bud                # objective headroom to the kill threshold
        w = rec["support"]["w_poly_only"]
        rec["kills_brief"] = bool(w >= rec["slack_brief"])
        rec["kills_tight"] = bool(w > rec["slack_tight"] + 1e-12)

    # ---- (iii) T5-polygon logic test.  K'(B) subset Q0 and K'(P) subset Q_pin; if their interiors
    # meet, Q0 IS the pinned square (T5), so a witness distinct from the pins does not exist and the
    # node is empty -- PROVIDED no pin placement lies in B (pinguard's `parent` case, in which the
    # identification is consistent and it is the reduced budget that is unsound, not the node).
    hits = []
    for j, (pb, pcp, pcore) in enumerate(zip(pins, pcs[:-1], cores[:-1])):
        dpp = polycore.poly_poly_depth(pcs[-1].P, pcp.P)
        dpc = polycore.poly_poly_depth(pcs[-1].P, polycore.core_verts(pcore))
        if dpp > 0.0:
            hits.append(dict(pin=j, depth_polypoly=float(dpp), depth_polycore=float(dpc),
                             witness=polycore.overlap_witness(pcs[-1], pcp)))
    rec["t5poly_hits"] = hits
    rec["t5poly_dead"] = bool(hits)
    slots = [(0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)) for b in pins]
    rec["pinguard_now"] = pinguard.classify(nb, pins, slots)[0]
    rec["t5poly_new"] = bool(hits) and rec["pinguard_now"] == "ok"
    rec["witness_certified"] = bool(hits) and all(h["witness"] is not None for h in hits)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "measure132.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--camp", default="both", choices=("A57", "A60", "both"))
    a = ap.parse_args()
    nodes = []
    if a.camp in ("A57", "both"):
        nodes += a57_alive()
    if a.camp in ("A60", "both"):
        nodes += a60_alive()
    if a.limit:
        nodes = nodes[:a.limit]
    print(f"{len(nodes)} alive nodes with a stored record", flush=True)
    t0 = time.time()
    n_err = 0
    with open(a.out, "w") as fh:
        for i, (meta, d) in enumerate(nodes):
            try:
                rec = measure(meta, d)
            except Exception as e:
                n_err += 1
                rec = dict(meta, error=repr(e)[:200])
            fh.write(json.dumps(rec) + "\n")
            if (i + 1) % 25 == 0:
                print(f"  {i + 1}/{len(nodes)}  {time.time() - t0:.0f} s  errors {n_err}", flush=True)
    print(f"done {len(nodes)} nodes, {n_err} errors, {time.time() - t0:.0f} s -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
