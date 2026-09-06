"""A111 -- NO side, coordinator's addendum item (2): re-solve dead-unconverged children with
(a) the conditioned bin TRIMMED by the same octagon (common-core) test used in T1, and
(b) an LP time cap of 900 s.

The question the run answers: is the NO side a CONVERGENCE-TIME problem (tau is already below budget
and only the column generation has not closed -- more seconds fix it) or a RE-PRICING problem (the
node's mass really is there and the NO child needs a different cut)?

Trim (sound direction).  The node's hypothesis asserts a square in the conditioned box B.  Subdivide
B into cells; a cell whose tight core meets a class-pin core (or whose tilt/centre pair violates
Lemma TC against a pin) can hold no square of a packing, so dropping it removes no witness.  The
surviving cells' BOUNDING BOX B' is therefore a sound replacement for B, and B' <= B makes the LP
strictly easier: fewer admissible rows, tau can only fall.  If every cell dies the NODE ITSELF is
dead with no LP (reported as trim_kills_node).

Writes results/t2_trim.jsonl and results/nodes/<tag>__TRIM.json.  Read-only on other campaigns.
"""
from __future__ import annotations

import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1
import t2_no as T2
import octagon as OC
from caselp import Box, Hyp, NoFam, solve_node, warm_from_result


def subdivide(b, nxy, nth):
    xs = [b.x0 + (b.x1 - b.x0) * i / nxy for i in range(nxy + 1)]
    ys = [b.y0 + (b.y1 - b.y0) * i / nxy for i in range(nxy + 1)]
    ts = [b.th0 + (b.th1 - b.th0) * i / nth for i in range(nth + 1)]
    for i in range(nxy):
        for j in range(nxy):
            for k in range(nth):
                yield Box(xs[i], xs[i + 1], ys[j], ys[j + 1], ts[k], ts[k + 1])


def trim_box(b, pins, nxy=4, nth=8):
    """bounding box of the cells of b that survive the octagon test against every pin box."""
    keep = []
    ndrop = 0
    for c in subdivide(b, nxy, nth):
        dead = False
        for p in pins:
            ok, _ = OC.pair_kill(c, p)
            if ok:
                dead = True
                break
        if dead:
            ndrop += 1
        else:
            keep.append(c)
    if not keep:
        return None, ndrop, 0
    nb = Box(min(c.x0 for c in keep), max(c.x1 for c in keep),
             min(c.y0 for c in keep), max(c.y1 for c in keep),
             min(c.th0 for c in keep), max(c.th1 for c in keep))
    return nb, ndrop, len(keep)


def vol(b):
    return max(b.x1 - b.x0, 1e-12) * max(b.y1 - b.y0, 1e-12) * max(b.th1 - b.th0, 1e-9)


def run_one(nid, src, tag, variant, cls, op, box_name, r, rho, lp_time, log):
    p = L.copy_node(nid, src)
    if p is None:
        return dict(nid=nid, src=src, error="node json not found")
    res0 = json.load(open(p, encoding="utf-8"))
    s, budget = res0["s"], res0["budget"]
    hyp0 = Hyp.from_json(res0["hyp"])
    # the pins are the degenerate hypothesis boxes; the conditioned bins are the rest
    is_pin = [((b.x1 - b.x0) <= 1e-9 and (b.y1 - b.y0) <= 1e-9 and (b.th1 - b.th0) <= 1e-9)
              for b in hyp0.boxes]
    pins = [b for b, q in zip(hyp0.boxes, is_pin) if q]
    trim_info, newboxes, killed = [], [], False
    for b, q in zip(hyp0.boxes, is_pin):
        if q:
            newboxes.append(b)
            continue
        nb, ndrop, nkeep = trim_box(b, pins)
        if nb is None:
            killed = True
            trim_info.append(dict(box=repr(b), cells_dropped=ndrop, cells_kept=0))
            newboxes.append(b)
            continue
        trim_info.append(dict(box=repr(b), new=repr(nb), cells_dropped=ndrop, cells_kept=nkeep,
                              vol_ratio=round(vol(nb) / vol(b), 6),
                              dth_before=round(b.th1 - b.th0, 4),
                              dth_after=round(nb.th1 - nb.th0, 4)))
        newboxes.append(nb)
    if killed:
        log("    %-40s TRIM KILLS THE NODE (every cell of a conditioned bin meets a pin core)" % nid)
        return dict(nid=nid, src=src, shadow=tag, box=box_name, trim_kills_node=True,
                    trim=trim_info)

    box_names, NB = T2.node_boxes(tag, variant, cls, r, rho, op, s)
    if box_name not in box_names:
        return dict(nid=nid, src=src, error="box %s not in %s" % (box_name, box_names))
    hyp = Hyp(newboxes, list(hyp0.nofams) + [T2.nofam_of(NB[box_name], s)])
    warm = warm_from_result(res0)
    warm["rows"] = warm["rows"][:20000]
    kw = dict(sym_kind="C1", max_iter=4000, out=None, log=lambda *x: None, prune=0,
              prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
              max_rows_add=2000, fine_slack=99.0, alternate=True)
    L.gate(log, "%s/%s" % (nid, box_name))
    t0 = time.time()
    rr = solve_node(s, hyp, budget, warm=warm, time_limit=lp_time, **kw)
    lp_s = round(time.time() - t0, 1)
    tagid = "%s__%s__%s__r%g_p%g__%s__TRIM" % (nid, tag, variant, r, rho, box_name)
    rr["a111_trim"] = dict(nid=nid, box=box_name, trim=trim_info, lp_time=lp_time)
    rr["a111_lp_s"] = lp_s
    json.dump(rr, open(os.path.join(L.NODES, tagid + ".json"), "w"))
    rec = dict(nid=nid, src=src, shadow=tag, variant=variant, cls=cls, op=op, box=box_name,
               r=r, rho=rho, budget=budget, tau0=res0["tau"], eta0=res0["tau"] - budget,
               tau=rr["tau"], eta=rr["tau"] - budget, converged=bool(rr["converged"]),
               dead=bool(rr["converged"] and rr["tau"] < budget - 1e-6),
               dead_unconv=bool(rr["tau"] < budget - 1e-6),
               minmass=rr["minmass"], maxcov=rr["maxcov"], lp_s=lp_s, lp_cap=lp_time,
               trim=trim_info, tag=tagid, trim_kills_node=False)
    log("    %-52s tau %.4f -> %.4f  eta %+.4f  conv=%s  %s  (%ss cap %s)"
        % (tagid[:52], rec["tau0"], rec["tau"], rec["eta"], rec["converged"],
           "DEAD" if rec["dead"] else ("dead-unconv" if rec["dead_unconv"] else "alive"),
           lp_s, lp_time))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--children", required=True,
                    help="semicolon list of src:nid:box, e.g. A57:k5_11_interior_Y0230:f2")
    ap.add_argument("--tag", default="S02")
    ap.add_argument("--variant", default="lpa")
    ap.add_argument("--r", type=float, default=0.1)
    ap.add_argument("--rho", type=float, default=10.0)
    ap.add_argument("--lp_time", type=float, default=900.0)
    A = ap.parse_args()
    logp = os.path.join(L.LOGS, "t2_trim.log")

    def log(*x):
        m = " ".join(str(v) for v in x)
        print(m, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + m + "\n")

    plan = {(p["src"], p["nid"]): p for p in T2.load_plan(A.tag, 0)}
    out = os.path.join(L.RES, "t2_trim.jsonl")
    log("=== A111 T2 trim + %.0fs cap  tag=%s r=%g rho=%g" % (A.lp_time, A.tag, A.r, A.rho))
    for item in A.children.split(";"):
        item = item.strip()
        if not item:
            continue
        src, nid, box = item.split(":")
        pl = plan.get((src, nid))
        if pl is None:
            log("    %s: not in the %s plan" % (nid, A.tag))
            continue
        rec = run_one(nid, src, A.tag, A.variant, pl["cls"], pl["op"], box, A.r, A.rho,
                      A.lp_time, log)
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
    log("T2 trim done")


if __name__ == "__main__":
    main()
