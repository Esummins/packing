"""A159 T2/T3 -- the JOINT split, run properly, on the k0 NEAR-MISS corners.

The leaf (A141 T5, the PI's refinement).  A corner cell C is NEAR-MISS when `LANE_K'(C) <= 1` and
`M = 1`: at most one non-conditioned square can reach C, and the one conditioned square H MIGHT
reach it.  Split H's parameter box `B` into a complete binary partition; the actual pose of H is
in exactly one piece `B_k`, and on that piece the ORDINARY leaf runs with the strictly larger core
`K'(B_k)`:

    B_miss  (`box_misses_cell(B_k)` certified over the whole sub-box by one separating axis)
            -> m_k = 0, so `LANE_k <= 1` already gives "C met by at most one square";
    B_meet  (everything else) -> m_k = 1, so the piece needs `LANE_k = 0`: C met by H alone.

Either way C is singly met, for every realisation of the hypothesis => K0-FREE => the cell is
dead (conditional on K0-O1, as every lane kill is).

THE CANARY.  `l1_153` is a Trump-image cell; a Trump image is doubly met at every corner in the
widened sense by construction (A143/A150), and A159 T1 exhibits an EXACT interior-disjoint pair
(free square, H in B) both meeting int(widened TR box) for it.  If this split closes l1_153's TR
the leaf is UNSOUND.  `--canary` runs it there and refuses to go on if it kills.

    python split159.py --canary
    python split159.py --nowitness            # the near-misses with no realised two-crowd
"""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")
sys.path.insert(0, os.path.join(A141, "code"))     # READ-ONLY import of A141's emitter

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import polycore as PC             # noqa: E402
import emit141 as EM              # noqa: E402
from caselp import Box            # noqa: E402


def t2_rows():
    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)
    return rows


def near_misses(rows):
    out = []
    for cid, r in rows.items():
        for c in ("BL", "BR", "TR", "TL"):
            v = r["corners"][c]
            if v["verdict"].startswith("NEAR-MISS"):
                out.append((cid, c, v))
    return sorted(out)


def with_witness():
    p = os.path.join(BASE, "results", "xwitness159.jsonl")
    keep = set()
    for ln in open(p, encoding="utf-8"):
        z = json.loads(ln)
        if z["SURVIVES"]:
            keep.add((z["cell"], z["corner"]))
    return keep


def run_one(nid, corner, v, row, args):
    raw = [Box(*b) for b in row["boxes"]]
    conds = P.build_cond(raw)
    cell = P.corner_cell(corner)
    meet = v.get("meeters") or [c.idx for c in conds]
    t0 = time.time()
    best = None
    for j in meet:
        sp = P.lane_corner_split(cell, conds, j, rng=np.random.default_rng(1590 + j),
                                 max_pieces=args.maxpieces, max_depth=args.maxdepth,
                                 sample=args.sample, keep_cert=True)
        if best is None or sp["ok"]:
            best = sp
        if sp["ok"]:
            break
    row_out = dict(cell=nid, corner=corner, split_index=best["split_index"],
                   n_pieces=best["n_pieces"], closed=bool(best["ok"]), open=len(best["open"]),
                   secs=round(time.time() - t0, 1), lane_ub_before=v["lane_ub"],
                   M_before=v["M"], meeters=meet,
                   n_meet_pieces=sum(1 for p in best["pieces"] if not p["misses_cell"]),
                   n_miss_pieces=sum(1 for p in best["pieces"] if p["misses_cell"]),
                   # WHY the open pieces are open: `no_lane_bound` = the LANE cover ran out of
                   # budget (more depth would help); `lane_ge_1` = a free meeter survives the
                   # certified cover on that piece (only a finer split of B, or nothing, helps).
                   open_reasons=dict(
                       no_lane_bound=sum(1 for p in best["open"]
                                         if p.get("lane_ub") is None),
                       lane_ge_1=sum(1 for p in best["open"]
                                     if (p.get("lane_ub") or 0) >= 1),
                       depth_capped=sum(1 for p in best["open"]
                                            if len(p.get("path", "")) >= args.maxdepth)),
                   open_paths=[p.get("path") for p in best["open"]][:64])
    if best["ok"]:
        # sample line: poses meeting the widened corner cell, tested against K'(piece) per piece
        rng = np.random.default_rng(159)
        C, T = P.sample_meeting(cell, P.S0, args.draws, rng)
        worst = None
        for p in best["pieces"]:
            pc = P.build_cond([Box(*p["box"])], tighten=False)[0]
            cs = [c.pc for c in conds if c.idx != best["split_index"]] + [pc.pc]
            hit = np.zeros(len(C), bool)
            for k in cs:
                hit |= PC.poly_square_depth(k.P, C, T) > 0.0
            free = int((~hit).sum())
            if worst is None or free > worst[1]:
                worst = (p["path"], free, p["m_j"])
        row_out["sample_line"] = dict(drawn=args.draws, meeting=int(len(C)),
                                      worst_piece=worst[0], free_on_worst_piece=worst[1],
                                      m_j_on_worst_piece=worst[2])
        d = EM.split_cert_dict(nid, corner, conds, raw, cell, best,
                               extra=dict(sample_line=row_out["sample_line"],
                                          attempt="A159"))
        cp = os.path.join(BASE, "certs", f"split_{nid}_{corner}.json")
        row_out["cert"] = os.path.relpath(cp, ROOT)
        row_out["sha256"] = EM.write_cert(cp, d)
    return row_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--nowitness", action="store_true")
    ap.add_argument("--cells", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--maxpieces", type=int, default=192)
    ap.add_argument("--maxdepth", type=int, default=10)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--draws", type=int, default=200000)
    a = ap.parse_args()

    rows = t2_rows()
    nm = near_misses(rows)
    if a.canary:
        jobs = [(c, cc, v) for (c, cc, v) in nm if c == "l1_153"]
        out = a.out or os.path.join(BASE, "results", "canary159.jsonl")
    elif a.nowitness:
        w = with_witness()
        jobs = [(c, cc, v) for (c, cc, v) in nm if (c, cc) not in w]
        out = a.out or os.path.join(BASE, "results", "split159.jsonl")
    else:
        want = set(a.cells.split(",")) if a.cells else set()
        jobs = [(c, cc, v) for (c, cc, v) in nm if c in want]
        out = a.out or os.path.join(BASE, "results", "split159.jsonl")
    print("%d (cell, corner) jobs" % len(jobs), flush=True)

    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add((json.loads(ln)["cell"], json.loads(ln)["corner"]))
            except Exception:                                     # noqa: BLE001
                pass
    # Several cell ids share ONE conditioned box (e.g. l1_159 / l1_159_plain_warm /
    # l1_159_sh3_warm / node_159 are the same box at the same corner).  The leaf depends only on
    # (boxes, corner), so the split is run once per class and the verdict is transcribed to the
    # rest with `same_as` naming the representative -- the certificate is the representative's.
    rep, seen = {}, {}
    for (nid, corner, v) in jobs:
        key = (json.dumps(rows[nid]["boxes"]), corner)
        if key in seen:
            rep[(nid, corner)] = seen[key]
        else:
            seen[key] = nid
    fh = open(out, "a", encoding="utf-8")
    nk = 0
    cache = {}
    for (nid, corner, v) in jobs:
        if (nid, corner) in done:
            continue
        src = rep.get((nid, corner))
        if src is not None and (src, corner) in cache:
            r = dict(cache[(src, corner)])
            r.update(cell=nid, same_as=src, secs=0.0)
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            nk += int(r["closed"])
            print("%-26s %s  == %s (same box)  %s"
                  % (nid, corner, src, "KILL" if r["closed"] else "open"), flush=True)
            continue
        r = run_one(nid, corner, v, rows[nid], a)
        cache[(nid, corner)] = r
        fh.write(json.dumps(r) + "\n")
        fh.flush()
        nk += int(r["closed"])
        print("%-26s %s split@%d pieces=%d (meet %d / miss %d) %s %.0fs"
              % (nid, corner, r["split_index"], r["n_pieces"], r["n_meet_pieces"],
                 r["n_miss_pieces"], "KILL" if r["closed"] else "open(%d)" % r["open"],
                 r["secs"]), flush=True)
        if a.canary and r["closed"]:
            print("\n*** CANARY FIRED: the joint split KILLED l1_153 %s, which A159 T1 shows "
                  "has an EXACT realised two-crowd.  THE LEAF IS UNSOUND.  Stopping." % corner,
                  flush=True)
            fh.close()
            sys.exit(3)
    fh.close()
    print("done: %d of %d closed" % (nk, len(jobs)))


if __name__ == "__main__":
    main()
