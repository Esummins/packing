"""A158b -- the YES child as an LP NODE, not a lane leaf (the coordinator's correction).

`SomeIn S` is an ordinary case-LP hypothesis: "some square of P has its (centre, tilt) in the box
S".  So the YES child of the slot split is the node

    hypothesis : the class pins  +  the node's conditioned box H  +  the SLOT BOX S
    budget     : 11 - (#pins + #conditioned + 1)        (= 4 for a level-1 trump5/k5 node)

solved by `caselp.solve_node` with A135 exact cores on EVERY box (`ExactHyp`, scope "exall"), and
certified by the FROZEN `verify_case.py`: `S` is an ORDINARY second core in the
`case-measure-certificate-v1` schema, so nothing about the format or the verifier changes.
`tau < budget` kills the YES child.

THREE soundness points, all enforced here:

1. **The budget bridge needs the cores pairwise disjoint.**  `budget = 11 - #cores` is only valid
   if the `#cores` hypothesis squares are DISTINCT.  A135's `ExactHyp` gates
   `cores[:len(boxes)-1]`; with `S` appended that leaves `K(S)` unchecked, and if `K(S)` met
   `K(H)` the two hypotheses could be witnessed by the SAME square and the budget would be 5, not
   4.  `cores_pairwise_disjoint` is therefore re-run here over ALL cores, and a failure ABORTS.

2. **The frame.**  The lane leaf lives in the cell's corner frame on the original packing at side
   `m`; the LP lives in the world frame at `s0` on the DILATED family.  For a CORE box the sound
   direction is the HULL over `m in [m_lo, s0]` of the pullbacks (every realisation must land
   inside the box) -- the opposite of the NO child's zone, which is the INTERSECTION.  For A60
   (`m_lo = s0`) the two coincide and the map is exact.

3. **The clamp.**  The centre box is clamped to `[1/2, s0 - 1/2]`, sound by
   `LocalCompose.centre_in_slab` (no square of a packing has a centre nearer a wall than 1/2),
   and it only SHRINKS the box, which ENLARGES `K(S)` -- the strong direction for a core.  The
   tautology is still over the unclamped `S`, because `SomeIn S` for a packing implies
   `SomeIn (S n admissible)`.

`S`'s tilt set `[0, tt] u [90 - tt, 90]` is two boxes, so the YES child is TWO LP sub-cases; the
YES child is dead only when BOTH die.

    python yeslp158.py --jobs ../results/all_jobs.jsonl --r 0.10 --tt 10 --cap 240
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A135 = os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code")
for _p in (HERE, A135):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import slotlib158 as SL                                            # noqa: E402
import emit135 as EM                                               # noqa: E402  READ-ONLY (A135)
import exactcore as EC                                             # noqa: E402  READ-ONLY (A135)
from caselp import Box, solve_node                                 # noqa: E402  READ-ONLY

S0 = SL.S0
FROZEN_CASE = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code", "verify_case.py")
FROZEN_SHA = "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"


def free_mb():
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 20, m.ullAvailPageFile / 2 ** 20


def s_boxes_world(rec, slot, r, tt):
    """The two tilt pieces of S as world-at-s0 caselp.Box, HULL over m then clamped to the
    admissible centre strip."""
    c, i, j = SL.LANE.L.parse_cell(slot)
    m_lo = SL.LANE.M_LO.get(rec["src"], 3.82)
    flipx, flipy = SL.LANE._corner_xy(c)
    cx, cy = float(i) + 0.5, float(j) + 0.5
    X0, X1, Y0, Y1 = cx - r, cx + r, cy - r, cy + r

    def hull(A0, A1, flip):
        los, his = [], []
        for m in (m_lo, S0):
            if flip:
                los.append(S0 * (m - A1) / m)
                his.append(S0 * (m - A0) / m)
            else:
                los.append(A0 * S0 / m)
                his.append(A1 * S0 / m)
        return min(los), max(his)                        # HULL: outward, the sound way for a core

    x0, x1 = hull(X0, X1, flipx)
    y0, y1 = hull(Y0, Y1, flipy)
    lo, hi = 0.5, S0 - 0.5                               # centre_in_slab
    x0, x1 = max(x0, lo), min(x1, hi)
    y0, y1 = max(y0, lo), min(y1, hi)
    if x1 <= x0 or y1 <= y0:
        return []
    return [Box(x0, x1, y0, y1, 0.0, tt), Box(x0, x1, y0, y1, 90.0 - tt, 90.0)]


def run_case(cert_path, jobs=1, depth=56, max_w=64, timeout=1500):
    import hashlib
    import subprocess
    with open(FROZEN_CASE, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != FROZEN_SHA:
        return None, "FROZEN VERIFIER SHA MISMATCH %s" % got
    cmd = [sys.executable, FROZEN_CASE, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    tail = [l for l in (p.stdout + p.stderr).splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED", "Traceback"))][:6]
    return p.returncode, " | ".join(tail)


def solve_piece(node, rec, slot, piece_box, piece, cap, log):
    boxes = [Box.from_json(b) for b in node["hyp"]["boxes"]] + [piece_box]
    hyp = EM.ExactHyp(boxes, [], scope="exall")
    # SOUNDNESS GATE 1: the budget bridge needs ALL cores pairwise disjoint (A135 only checks
    # cores[:n-1], which with S appended would leave K(S) unchecked)
    ok, pair, gap = EC.cores_pairwise_disjoint(hyp.cores)
    if not ok:
        return dict(error="cores NOT pairwise disjoint (pair %s, gap %s): the budget bridge "
                          "11 - #cores would be unsound" % (pair, gap))
    budget = node["budget"] - 1
    warm = dict(atoms=[(x, y) for (x, y, w) in node["atoms_all"]],
                rows=[tuple(t) for t in node["rows_all"]])
    ap_, cp_ = free_mb()
    log("      free phys %.0f MB, free commit %.0f MB" % (ap_, cp_))
    if ap_ < 3072 or cp_ < 6144:
        return dict(error="memory gate %.0f/%.0f" % (ap_, cp_))
    t0 = time.time()
    res = solve_node(S0, hyp, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                     out=None, log=lambda *x: None, prune=0, prune_cols=3,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                     max_rows_add=2000, fine_slack=99.0, alternate=True, fine=True)
    return dict(res=res, hyp=hyp, budget=budget, secs=round(time.time() - t0, 1),
                core_gap=float(gap) if gap is not None else None,
                a_report=hyp.a_report)


def slot_tag(slot):
    return slot.replace("(", "").replace(")", "").replace(",", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "all_jobs.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--cap2", type=float, default=900.0, help="knife-edge re-solve cap")
    ap.add_argument("--knife", type=float, default=0.05)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "yeslp158.jsonl"))
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--emit", type=int, default=1)
    ap.add_argument("--budget_s", type=float, default=5400.0)
    a = ap.parse_args()

    def log(*x):
        print(*x, flush=True)

    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                d = json.loads(ln)
                done.add((d["nid"], d["slot"], d.get("piece"), d.get("r"), d.get("tt")))
            except Exception:                                      # noqa: BLE001
                pass
    fh = open(a.out, "a", encoding="utf-8")
    t0 = time.time()
    for j in jobs:
        rec = recs[j["nid"]]
        node = json.load(open(os.path.join(ROOT, rec["path"]), encoding="utf-8"))
        pieces = s_boxes_world(rec, j["slot"], a.r, a.tt)
        log("%s %s (%s %s L%s) tau0 %.12g budget %s -> YES budget %s ; S pieces %d"
            % (j["nid"], j["slot"], rec["src"], rec["cls"], rec["level"], node["tau"],
               node["budget"], node["budget"] - 1, len(pieces)))
        for piece, pb in enumerate(pieces):
            key = (j["nid"], j["slot"], piece, a.r, a.tt)
            if key in done:
                continue
            if time.time() - t0 > a.budget_s:
                log("process budget reached")
                fh.close()
                return
            log("   piece %d  S = %s" % (piece, pb))
            out = solve_piece(node, rec, j["slot"], pb, piece, a.cap, log)
            if "res" not in out:
                fh.write(json.dumps(dict(nid=j["nid"], slot=j["slot"], piece=piece, r=a.r,
                                         tt=a.tt, **out)) + "\n")
                fh.flush()
                log("      ERROR %s" % out["error"])
                continue
            res, budget = out["res"], out["budget"]
            tau = res.get("tau")
            # knife edge -> one longer re-solve
            if (tau is not None and abs(tau - budget) < a.knife
                    and not res.get("converged")) or (
                    tau is not None and tau >= budget and abs(tau - budget) < a.knife):
                log("      knife edge (tau %.12g vs budget %s); re-solving at %ss"
                    % (tau, budget, a.cap2))
                out2 = solve_piece(node, rec, j["slot"], pb, piece, a.cap2, log)
                if "res" in out2:
                    out, res, tau = out2, out2["res"], out2["res"].get("tau")
            row = dict(nid=j["nid"], slot=j["slot"], src=rec["src"], cls=rec["cls"],
                       level=rec["level"], piece=piece, r=a.r, tt=a.tt,
                       S_box=pb.to_json(), budget=budget, tau0=node["tau"],
                       node_budget=node["budget"], tau=tau,
                       eta=(None if tau is None else round(budget - tau, 12)),
                       converged=res.get("converged"), minmass=res.get("minmass"),
                       maxcov=res.get("maxcov"), n_dual=len(res.get("packing") or []),
                       core_gap=out["core_gap"], secs=out["secs"],
                       kill=bool(tau is not None and tau < budget - 1e-9))
            log("      tau %.12g  eta %.6g  conv=%s  (%.1f s)  %s"
                % (tau if tau is not None else float("nan"), row["eta"], row["converged"],
                   out["secs"], "KILL" if row["kill"] else "NO-KILL"))
            if row["kill"] and a.emit:
                try:
                    scale = max(1.005, min(1.03, (budget - 0.005) / tau - 0.002))
                    cert = EM.make_cert(res, out["hyp"], S0, scale=scale)
                    cert["provenance"]["a158_yes"] = (
                        "A158 YES child of the slot split, as an LP NODE: hypothesis = the class "
                        "pins + the node's conditioned box(es) + the SLOT BOX S (near-simple poses "
                        "of usable slot %s, centre within %g of the exact slot centre, tilt within "
                        "%g deg of 0/90, tilt piece %d of 2), budget = 11 - #cores = %d; S is an "
                        "ordinary core in this schema.  The box is the HULL over m in [m_lo, s0] of "
                        "the pullbacks of the corner-frame box (the sound direction for a CORE), "
                        "clamped to [1/2, s-1/2] (centre_in_slab).  All %d cores certified "
                        "pairwise disjoint, min gap %.6g, so the budget bridge holds."
                        % (slot_tag(j["slot"]), a.r, a.tt, piece, budget, len(out["hyp"].cores),
                           out["core_gap"]))
                    tot = float(Fr(cert["total"]))
                    if tot >= budget:
                        row["emit"] = dict(result="TOO-TIGHT", total=tot)
                    else:
                        p = os.path.join(a.certs, "yeslp_%s__%s__p%d__r%g_tt%g.json"
                                         % (j["nid"], slot_tag(j["slot"]), piece, a.r, a.tt))
                        json.dump(cert, open(p, "w", encoding="utf-8"), indent=0)
                        rc, tail = run_case(p)
                        row["cert"] = os.path.relpath(p, ROOT)
                        row["emit"] = dict(result="EMITTED", total=tot, scale=scale,
                                           atoms=len(cert["atoms"]), verify_rc=rc,
                                           verifier=tail)
                        log("      cert %s  verify_case rc=%s :: %s"
                            % (row["cert"], rc, tail[:150]))
                except Exception as e:                             # noqa: BLE001
                    import traceback
                    row["emit"] = dict(result="EMIT-ERROR", error=repr(e)[:200],
                                       tb=traceback.format_exc()[-600:])
                    log("      EMIT-ERROR %r" % (e,))
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    fh.close()


if __name__ == "__main__":
    main()
