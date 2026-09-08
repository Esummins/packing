"""A154 T2a -- the ZERO-LP-COST screen for the (R6) row.

For every cell of every corpus: read the stored dual (fractional) packing of its LP record, count
the corner incidence it realises, and compare with the row's guaranteed budget B.

    c_stored >= B  AND the record is CONVERGED   ==>   PROVED: no e > 0 makes eta smaller,
                                                       i.e. the (R6) row cannot kill this cell.
    c_stored >= B  but the record is UNCONVERGED ==>   diagnostic only (tau0 is a lower bound).
    c_stored <  B                                ==>   inconclusive: needs the LP.

Writes results/screen154.jsonl.  Read-only everywhere else.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a154lib as L  # noqa: E402


def one(fam, item, corners, pins_note=None, famID=None):
    d = json.load(open(item["lp"], encoding="utf-8"))
    hyp = d.get("hyp") or {}
    boxes = list(hyp.get("boxes") or [])
    # trump5: the first 5 boxes are the class PINS (degenerate boxes), not conditioned squares.
    npin = item.get("npin", 0)
    cond = boxes[npin:]
    B, rmax = L.crowd_budget(fam, cond, corners=corners)
    inc = L.incidence_of_packing(fam, d.get("packing") or [], corners=corners)
    tau0 = d.get("tau")
    budget0 = d.get("budget")
    conv = bool(d.get("converged"))
    rec = dict(nid=item["nid"], group=item["group"], cls=item["cls"], level=item.get("level"),
               lp=os.path.relpath(item["lp"], L.ROOT).replace("\\", "/"),
               corners=list(corners), n_cond=len(cond), n_pin=npin,
               a_w=float(fam["a"]), B=B, rmax_cores=rmax,
               tau0=tau0, budget0=budget0, eta0=(tau0 - budget0) if tau0 is not None else None,
               converged0=conv, dual_mass=inc["mass"], c_stored=inc["c"],
               per_corner={k: round(v, 6) for k, v in inc["per_corner"].items()},
               n_dual=len(d.get("packing") or []))
    rec["c_ge_B"] = bool(inc["c"] >= B - 1e-9)
    if famID is not None:
        # Lemma ID's certified corollary (A89-O3 R1 PASS, tilt_floor_k0.md sec 8.6"): at least
        # ONE corner has DEPTH >= 0.3, i.e. >= 1 square meets the corner box of side a_w(0.3).
        # Same rhs-lift machinery, weight 1 instead of 8.
        B2, rmax2 = L.crowd_budget(famID, cond, corners=corners)
        B2 = 1 - sum(rmax2)
        if npin:
            # Lemma ID is "SOME corner has DEPTH >= 0.3".  A PINNED class has a pin sitting in
            # its simple corners at depth 1, so the statement is already realised by a pin and
            # the row is VACUOUS for every class with at least one pinned corner.
            B2 = 0
        inc2 = L.incidence_of_packing(famID, d.get("packing") or [], corners=corners)
        rec.update(a_w_ID=float(famID["a"]), B_ID=B2, rmax_ID=rmax2, c_ID=inc2["c"])
        rec["cID_ge_BID"] = bool(inc2["c"] >= B2 - 1e-9)
    if rec["c_ge_B"] and rec.get("cID_ge_BID", True) and conv:
        rec["screen"] = "PROVED-USELESS"
    elif rec["c_ge_B"] and rec.get("cID_ge_BID", True):
        rec["screen"] = "useless (unconverged record: diagnostic)"
    else:
        rec["screen"] = "CANDIDATE (c < B%s)" % ("" if rec["c_ge_B"] else "")
        if not rec.get("cID_ge_BID", True):
            rec["screen"] = "CANDIDATE (%s%s)" % ("" if rec["c_ge_B"] else "c<B ",
                                                  "cID<BID")
    if pins_note:
        rec["pins_note"] = pins_note
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(L.RES, "screen154.jsonl"))
    A = ap.parse_args()
    log = L.logger("screen154.log")
    fam = L.get_fam(0.0, log=log)
    famID = L.get_fam(0.3, log=log)
    log("A154 screen: a_w(0) = %s = %.6f ; G/corner = %d ; ID a_w(0.3) = %s = %.6f" %
        (str(fam["a"]), float(fam["a"]), fam["n_g_per_corner"], str(famID["a"]), float(famID["a"])))

    items = L.corpus_eleven()
    ex = {it["nid"] for it in items}
    nm = L.corpus_nearmiss(20)
    ex |= {it["nid"] for it in nm}
    rl = L.corpus_rand_l1(20, exclude=ex)
    t5 = L.corpus_trump5(10)
    for it in t5:
        it["npin"] = 5

    out = []
    for it in items + nm + rl:
        r = one(fam, it, L.CORNERS, famID=famID)
        out.append(r)
        log("  %-28s %-9s B=%d c=%7.3f | BID=%d cID=%6.3f | eta0=%+9.2e conv=%-5s %s"
            % (r["nid"], r["group"], r["B"], r["c_stored"], r.get("B_ID", 0), r.get("c_ID", 0.0),
               r["eta0"] if r["eta0"] is not None else float("nan"), r["converged0"], r["screen"]))

    # trump5: only the NON-SIMPLE corners carry the row, and only FREE squares meet them.
    pn = ("trump5 pins occupy BL/BR/TR; the R6 row runs on TL only; Lemma ID is vacuous "
          "(the BL pin already has DEPTH 1 >= 0.3)")
    for it in t5:
        r = one(fam, it, L.TRUMP5_NONSIMPLE, pins_note=pn, famID=famID)
        out.append(r)
        log("  %-28s %-9s B=%d c=%7.3f | BID=%d cID=%6.3f | eta0=%+9.2e conv=%-5s %s"
            % (r["nid"], r["group"], r["B"], r["c_stored"], r.get("B_ID", 0), r.get("c_ID", 0.0),
               r["eta0"] if r["eta0"] is not None else float("nan"), r["converged0"], r["screen"]))

    with open(A.out, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    n = len(out)
    pr = sum(1 for r in out if r["screen"] == "PROVED-USELESS")
    ca = sum(1 for r in out if r["screen"].startswith("CANDIDATE"))
    log("screen done: %d cells, %d PROVED-USELESS, %d candidates, %d useless-unconverged"
        % (n, pr, ca, n - pr - ca))


if __name__ == "__main__":
    main()
