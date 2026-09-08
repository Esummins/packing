"""A158 -- the NO child: the node LP re-solved with one NoFam(S) exclusion.

    NO(S):  no square of the packing has its pose in S.

That is exactly A112's `caselp` NO-family clause.  The zone is the slot box S written in the WORLD
frame at s0 (`slotlib158.s_zone_world`, the INTERSECTION over m of the pullbacks) and clamped to
the admissible centre strip [1/2, s-1/2] by A136's `zone_of_box` (sound: every admissible centre
has h(theta) >= 1/2).  The LP is A135's exact-core re-solve, unchanged:

    ExactHyp(node boxes, [NoFam(zone)], scope="exall")  ->  caselp.solve_node(s0, ..., budget)

warm-started from the node's OWN recorded atoms and rows.  Dropping rows can only LOWER tau, so
tau' <= tau always; the node dies iff tau' < budget.  A certificate is emitted with A135's
`make_cert` (the frozen `case-measure-certificate-v1` emitter with the live Hyp), post-processed
by A136's `a136lib.narrow` (NO zone rounded INWARD, `ZONE subset BOX` decided on the written
rationals) and then handed to the FROZEN `verify_case.py` in a separate process (stage `verify`),
so only ONE lab python of this attempt is ever live.

    python no158.py --nid c0_Y0076 --slot "TL(0,0)" --radii 0.10,0.05 --tt 10
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
A136 = os.path.join(ROOT, "attempts", "A136-a120-resume", "code")
A57C = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for _p in (HERE, A135, A136, A57C):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import slotlib158 as SL                                            # noqa: E402
import emit135 as EM                                               # noqa: E402  READ-ONLY (A135)
import a136lib as A136L                                            # noqa: E402  READ-ONLY (A136)
from caselp import Box, NoFam, solve_node                          # noqa: E402  READ-ONLY

S0 = SL.S0


def free_mb():
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / 2 ** 20, m.ullAvailPageFile / 2 ** 20
    except Exception:                                              # noqa: BLE001
        return 1e9, 1e9


def zone_for(rec, slot, r, tt):
    """(exact clamped zone, the named BOX) for the NO family, both in the world frame at s0."""
    c, i, j = SL.LANE.L.parse_cell(slot)
    z = SL.s_zone_world(rec, c, i, j, r, tt)
    if z is None:
        return None, None
    box = dict(name="S(%s,%s) r=%g tt=%g" % (rec["nid"], slot, r, tt), **z)
    return A136L.zone_of_box(box, S0), box


def solve(node, rec, slot, r, tt, cap, log):
    """r < 0 is the CONTROL: the same exact-core re-solve with NO NoFam at all.

    Without it a `tau < budget` cannot be attributed to the slot box — A135's exact cores are
    strictly larger than the stored ones, so the re-solve alone can move `tau` (and several A57
    records are `converged = false, dead_unconverged = true`, i.e. their stored `tau` is not a
    bound at all).  Every kill reported by A158 is quoted against its own control."""
    if r < 0:
        zex, box, nfs = None, None, []
    else:
        zex, box = zone_for(rec, slot, r, tt)
        if zex is None:
            return dict(error="empty zone")
        nfs = [NoFam(zex["x0"], zex["x1"], zex["y0"], zex["y1"], zex["thetas"])]
    boxes = [Box.from_json(b) for b in node["hyp"]["boxes"]]
    hyp = EM.ExactHyp(boxes, nfs, scope="exall")
    budget = node["budget"]
    warm = dict(atoms=[(x, y) for (x, y, w) in node["atoms_all"]],
                rows=[tuple(t) for t in node["rows_all"]])
    ap_, cp_ = free_mb()
    log("    free phys %.0f MB, free commit %.0f MB" % (ap_, cp_))
    if ap_ < 3072 or cp_ < 6144:
        return dict(error="memory gate: %.0f MB phys / %.0f MB commit" % (ap_, cp_))
    t0 = time.time()
    res = solve_node(S0, hyp, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                     out=None, log=lambda *x: None, prune=0, prune_cols=3,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                     max_rows_add=2000, fine_slack=99.0, alternate=True, fine=True)
    return dict(zone=zex, box=box, hyp=hyp, res=res, budget=budget,
                secs=round(time.time() - t0, 1))


def emit(nid, slot, r, tt, out, certdir, scale_cap=1.03):
    """A135 make_cert + A136 narrow -> a written, ZONE-subset-BOX certificate."""
    res, hyp, budget = out["res"], out["hyp"], out["budget"]
    scale = max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
    cert = EM.make_cert(res, hyp, S0, scale=scale)
    tot = float(Fr(cert["total"]))
    if tot >= budget:
        return None, dict(result="TOO-TIGHT", total=tot, scale=scale)
    cert, rep = A136L.narrow(cert, [out["zone"]], [out["box"]], S0,
                             tag="A158 %s %s r=%g tt=%g" % (nid, slot, r, tt))
    cert["provenance"]["a158"] = (
        "A158 NO child of the slot split: node LP re-solved with one NoFam(S), S = the "
        "near-simple poses of usable slot %s (centre within %g of the exact slot centre, tilt "
        "within %g deg of 0/90), zone written in the world frame at s0 as the INTERSECTION over "
        "m in [m_lo, s0] of the pullbacks of the corner-frame box, then clamped to [1/2, s-1/2]"
        % (slot, r, tt))
    p = os.path.join(certdir, "no_%s__%s__r%g_tt%g.json" % (nid, slot.replace("(", "")
                                                            .replace(")", "").replace(",", "_"),
                                                            r, tt))
    json.dump(cert, open(p, "w", encoding="utf-8"), indent=0)
    return p, dict(result="EMITTED", total=tot, scale=scale, atoms=len(cert["atoms"]),
                   fcover=[dict(max_abs_delta_vs_exact=e["max_abs_delta_vs_exact"],
                                zone=e["zone"], box=e["box_written"]) for e in rep])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="c0_Y0076")
    ap.add_argument("--slot", default="TL(0,0)")
    ap.add_argument("--radii", default="0.10")
    ap.add_argument("--tt", default="10")
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "no158.jsonl"))
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--emit", type=int, default=1)
    ap.add_argument("--budget", type=float, default=3300.0)
    ap.add_argument("--jobs", default="", help="jsonl of {nid, slot}; overrides --nid/--slot")
    a = ap.parse_args()

    def log(*x):
        print(*x, flush=True)

    recs = json.load(open(a.recs, encoding="utf-8"))
    cells = []
    if a.jobs:
        for ln in open(a.jobs, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                j = json.loads(ln)
                cells.append((j["nid"], j["slot"]))
    else:
        cells = [(a.nid, a.slot)]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                d = json.loads(ln)
                done.add((d["nid"], d["slot"], d.get("r"), d.get("tt")))
            except Exception:                                      # noqa: BLE001
                pass
    fh = open(a.out, "a", encoding="utf-8")
    t0 = time.time()
    for (nid, slot) in cells:
        rec = recs[nid]
        node = json.load(open(os.path.join(ROOT, rec["path"]), encoding="utf-8"))
        log("%s %s (%s %s L%s) tau %.12g budget %s  -- %d hyp boxes, %d dual squares"
            % (nid, slot, rec["src"], rec["cls"], rec["level"], node["tau"], node["budget"],
               len(node["hyp"]["boxes"]), len(node.get("packing") or [])))
        for tt in [float(v) for v in a.tt.split(",")]:
            for r in [float(v) for v in a.radii.split(",")]:
                if (nid, slot, r, tt) in done:
                    continue
                if time.time() - t0 > a.budget:
                    log("budget reached")
                    fh.close()
                    return
                log("  r=%g tt=%g ..." % (r, tt))
                try:
                    out = solve(node, rec, slot, r, tt, a.cap, log)
                except Exception as e:                             # noqa: BLE001
                    import traceback
                    out = dict(error=repr(e)[:300], tb=traceback.format_exc()[-800:])
                if "res" not in out:
                    row = dict(nid=nid, slot=slot, r=r, tt=tt,
                               **{k: v for k, v in out.items() if k != "hyp"})
                    fh.write(json.dumps(row) + "\n"); fh.flush()
                    log("    ERROR %s" % out.get("error"))
                    continue
                res, budget = out["res"], out["budget"]
                tau = res.get("tau")
                row = dict(nid=nid, slot=slot, src=rec["src"], cls=rec["cls"],
                           level=rec["level"], r=r, tt=tt, budget=budget,
                           tau0=node["tau"], tau=tau,
                           eta=(None if tau is None else round(budget - tau, 12)),
                           converged=res.get("converged"), minmass=res.get("minmass"),
                           maxcov=res.get("maxcov"), n_dual=len(res.get("packing") or []),
                           control=bool(r < 0),
                           zone=(None if out["zone"] is None else
                                 {k: round(v, 9) for k, v in out["zone"].items()
                                  if k != "thetas"}),
                           thetas=(None if out["zone"] is None
                                   else out["zone"]["thetas"]), secs=out["secs"],
                           kill=bool(tau is not None and tau < budget - 1e-9))
                log("    tau %.12g -> eta %.3g  conv=%s  (%.1f s)  %s"
                    % (tau if tau is not None else float("nan"), row["eta"], row["converged"],
                       out["secs"], "KILL" if row["kill"] else "NO-KILL"))
                if row["kill"] and a.emit and r >= 0:
                    try:
                        p, info = emit(nid, slot, r, tt, out, a.certs)
                        row["cert"] = os.path.relpath(p, ROOT) if p else None
                        row["emit"] = info
                        log("    cert %s (%s)" % (row["cert"], info["result"]))
                    except Exception as e:                         # noqa: BLE001
                        row["emit"] = dict(result="EMIT-ERROR", error=repr(e)[:300])
                        log("    EMIT-ERROR %r" % (e,))
                fh.write(json.dumps(row) + "\n")
                fh.flush()
    fh.close()


if __name__ == "__main__":
    main()
