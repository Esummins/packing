"""A161 T3 -- the chord-limited lane over every alive A57/A60 node with a wall-adjacent usable slot
whose A141 verdict is UNDECIDED or NEAR-MISS with `lane_lb <= 1`.

STAGED, because the population is 2522 (node, slot) pairs and the budget is 3 CPU-h.  Each stage is
a SOUND retirement of the pair (it says the leaf cannot fire with the swept line family), never a
claim about the packing:

  S1  beta_min over the swept wall lines, exact, from the hypothesis boxes alone (no K' build);
  S2  M, by the exact-SAT cover of each conditioned box (A141's `cond_can_meet` with the stronger
      `misses_cell`);  retire if beta_min + M >= 2;
  S3  one pose pool, then the line sweep: retire if every line with beta + M <= 1 has a FREE
      OUTSIDE pose (that pose realises LANE_out >= 1 exactly -- A159's witness rule, and its
      two-crowd form when two of them are interior-disjoint);
  S4  the outside lane cover on the best line -> beta + LANE_out + M, verdict, certificate.

    python run161.py --shard 0/2 --out ../results/t3_s0.jsonl
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import chordlane as CL  # noqa: E402
import numpy as np  # noqa: E402
import polylane as P  # noqa: E402
from caselp import Box  # noqa: E402
from fractions import Fraction as Fr  # noqa: E402

WALL_SLOTS = {"BL(1,0)", "BR(1,0)", "TL(1,0)", "TR(1,0)", "BL(0,1)", "BR(0,1)", "TR(0,1)",
              "TL(0,0)", "BL(0,2)"}
A141_T2 = [os.path.join(ROOT, "attempts", "A141-polycore-lane", "results", f)
           for f in ("t2_a5760_s0.jsonl", "t2_a5760_s1.jsonl")]


def eligible():
    """(pairs, A141-killed node ids).  A141's own kills are excluded -- those nodes are dead."""
    killed, rows = set(), []
    for f in A141_T2:
        if not os.path.exists(f):
            continue
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.append(r)
            if r.get("kill"):
                killed.add(r["nid"])
    out = []
    for r in rows:
        if r["nid"] in killed:
            continue
        for cl in r["cells"]:
            if cl.get("cell") not in WALL_SLOTS:
                continue
            v, lb = cl.get("verdict"), cl.get("lane_lb")
            if v in ("UNDECIDED", "NEAR-MISS", "NEAR-MISS-OR-WORSE") and (lb is None or lb <= 1):
                out.append(dict(nid=r["nid"], src=r["src"], cls=r["cls"], level=r["level"],
                                slot=cl["cell"], a141_verdict=v, a141_lane_lb=lb,
                                a141_M=cl.get("M"), a141_lane_ub=cl.get("lane_ub")))
    return out, killed


def stage1_beta(rec, slot, n_lines):
    """S1: the frame boxes (NO K' build) and beta_min over the swept lines."""
    c, i, j = CL.LANE.L.parse_cell(slot)
    pin_b, cond_b = CL.LANE.cframe_boxes(rec, c, i, j)
    boxes = [Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b + cond_b]
    n_pins = len(pin_b)
    orients = CL.WALL_ORIENT.get((i, j)) or ()
    best = None
    contra = None
    for orient in orients:
        for ln in CL.line_candidates(orient, n=n_lines):
            rhs, beta, _ = CL.guard_rhs(boxes, ln, s=CL.S_RAT)
            if beta is None:
                contra = dict(orient=orient, off=str(ln.off), rhs=str(rhs))
                continue
            if best is None or beta < best[0]:
                best = (beta, orient, str(ln.off), str(rhs))
    return dict(n_pins=n_pins, cell=(float(i), float(i) + 1.0, float(j), float(j) + 1.0),
                corner=c, ij=[i, j], beta_min=(None if best is None else best[0]),
                beta_line=(None if best is None else best[1:]), contradiction=contra,
                n_cond=len(cond_b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t3.jsonl"))
    ap.add_argument("--progress", default="")
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--maxopen", type=int, default=20000)
    ap.add_argument("--maxdepth", type=int, default=40)
    ap.add_argument("--nlines", type=int, default=48)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pairs_file", default="", help="json list of [nid, slot] to run instead of the full population")
    ap.add_argument("--cap_s", type=float, default=4200.0, help="wall-clock cap for this shard")
    ap.add_argument("--pair_s", type=float, default=45.0, help="per-pair cover budget")
    ap.add_argument("--nlines_try", type=int, default=1, help="how many ranked guard lines to try")
    a = ap.parse_args()
    prog = a.progress or (a.out.rsplit(".", 1)[0].replace("results", "progress") + ".json")

    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    pairs, killed = eligible()
    if a.pairs_file:
        want = {tuple(x) for x in json.load(open(a.pairs_file, encoding="utf-8"))}
        pairs = [p for p in pairs if (p["nid"], p["slot"]) in want]
    k, n = (int(v) for v in a.shard.split("/"))
    pairs = [p for idx, p in enumerate(pairs) if idx % n == k and p["nid"] in recs]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                r = json.loads(ln)
                done.add((r["nid"], r["slot"]))
            except Exception:
                pass
    print("shard %s: %d pairs (%d already done); %d nodes A141-killed and skipped"
          % (a.shard, len(pairs), len(done), len(killed)), flush=True)

    fh = open(a.out, "a", encoding="utf-8")
    rng = np.random.default_rng(1610 + k)
    t0 = time.time()
    nrun = 0
    tally = {}
    for p in pairs:
        if (p["nid"], p["slot"]) in done:
            continue
        if time.time() - t0 > a.cap_s:
            print("wall cap reached, stopping", flush=True)
            break
        rec = recs[p["nid"]]
        row = dict(p)
        try:
            s1 = stage1_beta(rec, p["slot"], a.nlines)
            row.update({kk: vv for kk, vv in s1.items() if kk != "beta_line"})
            row["beta_line"] = s1["beta_line"]
            if s1["contradiction"] is not None:
                row["verdict"] = "CHORD-CONTRADICTION"
            elif s1["beta_min"] is None:
                row["verdict"] = "NO-WALL-LINE"
            elif s1["beta_min"] >= 2:
                row["verdict"] = "RETIRED-beta>=2"
            else:
                r2, cert = CL.run_slot(rec, p["slot"], rng=rng, sample=a.sample,
                                       max_open=a.maxopen, max_depth=a.maxdepth,
                                       n_lines=a.nlines, budget_s=a.pair_s,
                                       cover_budget=a.nlines_try)
                row.update({kk: vv for kk, vv in r2.items() if kk != "scan"})
                row["n_scan"] = len(r2.get("scan") or [])
                if cert is not None:
                    q = os.path.join(BASE, "certs", "cl_%s__%s.json"
                                     % (p["nid"], p["slot"].replace("(", "").replace(")", "")
                                        .replace(",", "_")))
                    blob = json.dumps(cert, sort_keys=True, indent=1).encode("utf-8")
                    open(q, "wb").write(blob)
                    row["cert"] = os.path.relpath(q, ROOT)
                    row["sha256"] = hashlib.sha256(blob).hexdigest()
        except Exception as e:                                       # noqa: BLE001
            row["verdict"] = "ERROR"
            row["error"] = repr(e)[:200]
        row.pop("sample", None) if row.get("verdict") not in ("KILL",) else None
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        tally[row["verdict"]] = tally.get(row["verdict"], 0) + 1
        nrun += 1
        if row["verdict"] in ("KILL", "CHORD-CONTRADICTION", "NEAR-MISS"):
            print("  %-36s %-9s %s beta=%s LANE_out=%s M=%s"
                  % (p["nid"], p["slot"], row["verdict"], row.get("beta"),
                     row.get("lane_out"), row.get("M")), flush=True)
        if nrun % 25 == 0:
            el = time.time() - t0
            json.dump(dict(done=nrun, elapsed=round(el, 1), tally=tally),
                      open(prog, "w", encoding="utf-8"))
            print("  %d/%d  %.0f s  %.2f s/pair  %s"
                  % (nrun, len(pairs), el, el / nrun, tally), flush=True)
        if a.limit and nrun >= a.limit:
            break
    fh.close()
    json.dump(dict(done=nrun, elapsed=round(time.time() - t0, 1), tally=tally, finished=True),
              open(prog, "w", encoding="utf-8"))
    print("done %d pairs, %.0f s, %s" % (nrun, time.time() - t0, tally), flush=True)


if __name__ == "__main__":
    main()
