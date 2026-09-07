"""A120 T1 -- the NO-SIDE RUNNER.

One A57 node whose support lies inside A116's certified neighbourhood N is covered by

    node  =  YES  u  NO_1 u NO_2 u NO_3 u NO_4                                    (a tautology)
    YES   =  node & (for every i, some square of the packing has its pose in F_i)
    NO_i  =  node & (no square of the packing has its pose in F_i)

with F_1..F_4 the A119 boxes of N carried into the node's OWN frame by A107's `struct_op`.
The YES leaf takes NO LP: `node & (a square in each F_i)` implies A116's hypothesis YES(N)
(the boxes are pose-disjoint from each other and from the class pins, so the four squares are
distinct and distinct from the pins; the node's own conditioned bin is an EXTRA constraint), and
Theorem LOCAL says no such configuration is a packing at side <= s0.  It is recorded as

    dead by local certificate A116 S02_k5_11_r0.20_rho10 (pending A119 rational/Lean form)

and never counted with the frozen-verifier kills.  Only the four NO children reach the solver, and
they go through A112's protocol UNCHANGED, by calling A112's own code:

    stage 1  `regiontree.Runner.lp` -> `caselp.solve_node` at 240 s, warm-started from the node's
             own campaign LP result;
    verdict  eta <= -1e-3 goes straight to the frozen certifier, converged or not;
    stage 2  only a node not clearly below budget escalates to the 900 s cap, and only one still
             on the knife edge (|eta| < 1e-6) afterwards counts ALIVE;
    kill     `regiontree.certify_leaf` -> A57's `certify.py --jobs 1` -> the frozen
             `verify_case.py` (sha 521cb01f...).  A FAILing certificate leaves the child ALIVE.

SOUNDNESS.  The YES and NO sides must use THE SAME BOXES IN THE SAME FRAME.  Every record carries
`boxes_used` (the mapped boxes) and `soundness` (A1..A7 of a120lib), and every NO child carries
`box_identical_to_yes`: the NO family's zone and tilt set re-derived from the very box object the
YES claim names.  A node whose soundness record is not ok is SKIPPED, never run.

Resumable: one record per (cls, id) under results/nodes/, written after every child, and never
recomputed.  The A57/A96 pause sentinel is checked between nodes.  No campaign driver is launched.
"""
from __future__ import annotations

import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a120lib as A                                     # noqa: E402  (BLAS pin inside)
import regiontree as RT                                 # noqa: E402
from caselp import Hyp, warm_from_result                # noqa: E402

ORDERING = "a116N"


def rec_path(cls, nid):
    return os.path.join(A.NODES, "rec__" + A.key_of(cls, nid) + ".json")


def load_rec(cls, nid):
    p = rec_path(cls, nid)
    return A.jload(p) if os.path.exists(p) else None


def save_rec(rec):
    A.jdump(rec_path(rec["cls"], rec["id"]), rec)


def run_node(nid, entry, log, cert_time=300.0, wall=5400.0, stage1=240.0, lp_cap=900.0,
             nsample=2000, cert_rounds=1, cert_wall=900.0):
    """One target node.  Returns its record."""
    cls = A.node_cls(nid)
    rec = load_rec(cls, nid)
    if rec and rec.get("status") in ("CLOSED", "OPEN", "SKIP-UNSOUND"):
        log("  [cache] %-32s %s" % (nid, rec["status"]))
        return rec

    ex = A.extract_index()[nid]
    op = ex.get("struct_op") or "e"
    local, campaign_path = A.node_src(nid)
    root = A.jload(local)
    s = root["s"]
    budget = root["budget"]

    mapped = [A.map_box(b, op, s) for b in entry["boxes"]]
    mpins = [A.map_pin(p, op, s) for p in entry["pins"]]
    snd = A.soundness(nid, op, mapped, mpins, root["hyp"], entry, s=s, nsample=nsample // 4)

    if rec is None:
        rec = dict(id=nid, cls=cls, key=[cls, nid], level=A.node_level(nid), src="A57",
                   campaign_path=campaign_path, local_copy=os.path.relpath(local, A.ROOT),
                   s=s, budget=budget, struct_op=op, inv_op=A.inv_op(op),
                   N=entry["id"], N_source="attempts/A119-local-cert-lean/results/N_boxes.json",
                   boxes_used=mapped, pins_used=mpins,
                   cover=dict(law="tautology: (for every i, some square's pose in F_i) or "
                                  "(there is an i with no square's pose in F_i)",
                              yes_child="YES", no_children=["NO%d" % i for i in range(len(mapped))],
                              boxes=[m["name"] for m in mapped]),
                   yes=dict(status="DEAD-LOCAL-CERT", claim=A.YES_CLAIM,
                            certificate=entry["id"],
                            a116_verdict=entry.get("a116_verdict"),
                            hypothesis=entry.get("hypothesis"),
                            boxes=[dict(name=m["name"], x0=m["x0"], x1=m["x1"], y0=m["y0"],
                                        y1=m["y1"], th0=m["th0"], th1=m["th1"],
                                        thetas=m["thetas"]) for m in mapped],
                            note="no LP is run on the YES leaf; NOT a frozen-verifier kill"),
                   soundness=snd, no_side_window=A.NO_TAG,
                   children={}, status=None, started=time.strftime("%Y-%m-%d %H:%M:%S"),
                   lp_wall_s=0.0, cert_wall_s=0.0, flat900_s=0.0)
    else:
        rec["soundness"] = snd
        rec["boxes_used"] = mapped

    if not snd["ok"]:
        rec["status"] = "SKIP-UNSOUND"
        rec["failed_checks"] = [k for k, v in snd["checks"].items() if not v.get("ok")]
        save_rec(rec)
        log("  %-32s SKIP-UNSOUND %s" % (nid, rec["failed_checks"]))
        return rec

    hyp0 = Hyp.from_json(root["hyp"])
    warm = warm_from_result(root)
    warm["rows"] = warm["rows"][:20000]

    runner = RT.Runner(region=nid, ordering=ORDERING, s=s, budget0=budget, log=log,
                       lp_cap=lp_cap, stage1=stage1, wall=wall, kind="a57")
    runner.cert_time = cert_time

    for i, m in enumerate(mapped):
        key = "NO%d" % i
        if rec["children"].get(key, {}).get("status") in ("DEAD-CERT", "ALIVE", "CAP-GATE"):
            log("  [cache] %-32s %s %s" % (nid, key, rec["children"][key]["status"]))
            continue
        nf = A.nofam_of(m, s)
        # ---- the soundness assertion, at the point of construction: the NO family IS the box the
        # YES claim names, restricted to the admissible strip and reduced mod 90.
        F = A.as_Box(m)
        ident = dict(
            box=m["name"],
            yes_box=dict(x0=F.x0, x1=F.x1, y0=F.y0, y1=F.y1, th0=F.th0, th1=F.th1),
            no_zone=dict(x0=nf.x0, x1=nf.x1, y0=nf.y0, y1=nf.y1), no_thetas=nf.thetas,
            thetas_identical=bool([tuple(t) for t in nf.thetas] ==
                                  [tuple(t) for t in m["thetas"]]),
            zone_is_box_clamped_to_admissible=bool(
                nf.x0 == max(0.5, min(F.x0, s - 0.5)) and nf.x1 == max(0.5, min(F.x1, s - 0.5))
                and nf.y0 == max(0.5, min(F.y0, s - 0.5)) and nf.y1 == max(0.5, min(F.y1, s - 0.5))),
            frame=dict(struct_op=op, applied=A.inv_op(op), side=s))
        ident["ok"] = bool(ident["thetas_identical"] and ident["zone_is_box_clamped_to_admissible"])
        assert ident["ok"], "NO family is not the YES box: %s / %s" % (nid, m["name"])

        hyp = Hyp(list(hyp0.boxes), list(hyp0.nofams) + [nf])
        ch = dict(key=key, box=m["name"], box_identical_to_yes=ident,
                  hyp=hyp.to_json(), budget=budget, s=s, status=None)
        rr, info = runner.lp(hyp, budget, warm, "%s/%s" % (nid, key))
        if rr is None:
            ch["status"] = "CAP-GATE"
            rec["children"][key] = ch
            save_rec(rec)
            log("  %-32s %s CAP-GATE (memory gate)" % (nid, key))
            continue
        ch["lp"] = info
        rec["lp_wall_s"] = round(rec["lp_wall_s"] + info["seconds"], 1)
        rec["flat900_s"] = round(rec["flat900_s"] + info["flat900_s"], 1)
        nj = "%s%s__%s__%s.json" % (nid, A.L.SUF, ORDERING, key)
        A.jdump(os.path.join(A.NODES, nj), rr)
        ch["node_json"] = nj
        eta = info["eta"]
        log("  %-32s %s LP stage%d tau=%.6f eta=%+.6f conv=%s (%.0fs; flat-900 %.0fs)"
            % (nid, key, info["stage"], info["tau"], eta, info["converged"], info["seconds"],
               info["flat900_s"]))
        if eta <= -RT.ETA_EDGE:
            # A57's campaign practice (`--cert_rounds 6`): `certify.py` returns on the FIRST
            # PASS, so extra witness-feedback rounds cost nothing on a child that certifies at
            # once and are the only thing that converts one the first emission cannot cover.
            c = A.certify_leaf_capped(nid, ORDERING, key, nj, log, cert_time=cert_time,
                                      rounds=cert_rounds, wall=cert_wall)
            ch["cert"] = c
            ch["cert_tag"] = A.NO_TAG
            rec["cert_wall_s"] = round(rec["cert_wall_s"] + c.get("seconds", 0.0), 1)
            ch["trump_realizes"] = RT.trump_canary(
                hyp, A.L.pin_slots(A.L.split_hyp(hyp)[0]))
            if c["result"] == "PASS":
                ch["status"] = "DEAD-CERT"
            else:
                ch["status"] = "ALIVE"
                ch["cert_failed"] = True
                ch["note"] = ("LP below budget (eta %.6f) but the frozen verifier refused: the "
                              "child stays ALIVE" % eta)
        else:
            ch["status"] = "ALIVE"
            ch["note"] = ("knife edge" if abs(eta) < RT.ETA_EDGE else "not below budget")
        rec["children"][key] = ch
        save_rec(rec)
        log("  %-32s %s %s" % (nid, key, ch["status"]))

    st = [rec["children"].get("NO%d" % i, {}).get("status") for i in range(len(mapped))]
    rec["child_status"] = st
    if all(x == "DEAD-CERT" for x in st):
        rec["status"] = "CLOSED"
        rec["claim"] = ("A57 node %s (cls %s) is DEAD at s0 = %r: YES leaf dead by local "
                        "certificate A116 %s, all %d NO children dead by the frozen verify_case.py"
                        % (nid, cls, s, entry["id"], len(mapped)))
    elif any(x is None for x in st):
        rec["status"] = "PARTIAL"
    else:
        rec["status"] = "OPEN"
        rec["open_children"] = [("NO%d" % i) for i, x in enumerate(st) if x != "DEAD-CERT"]
    rec["stats"] = runner.stats
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_rec(rec)
    log("  %-32s %s  (LP %.0f s, cert %.0f s)  children=%s"
        % (nid, rec["status"], rec["lp_wall_s"], rec["cert_wall_s"], st))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1", help="i/n")
    ap.add_argument("--cpu_cap", type=float, default=21600.0, help="seconds of THIS process")
    ap.add_argument("--node_wall", type=float, default=5400.0)
    ap.add_argument("--cert_time", type=float, default=300.0)
    ap.add_argument("--stage1", type=float, default=240.0)
    ap.add_argument("--lp_cap", type=float, default=900.0)
    ap.add_argument("--only", default=None, help="comma-separated node ids")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--order", default="cone", help="cone|file")
    ap.add_argument("--cert_wall", type=float, default=900.0,
                    help="hard wall on one certification subprocess; a capped run is CAP, never "
                         "a verdict, and the child stays ALIVE")
    ap.add_argument("--cert_rounds", type=int, default=1,
                    help="witness-feedback rounds inside certify.py (A112 used 1; A57's campaign "
                         "uses 6 -- certify.py returns on the first PASS, so this is free on an "
                         "easy child)")
    a = ap.parse_args()

    i, n = (int(x) for x in a.shard.split("/"))
    log = A.mklog("run_shard%d.log" % i)
    _, entry = A.n_entry()
    ids = A.targets()
    if a.only:
        ids = [x for x in a.only.split(",") if x]
    elif a.order == "cone":
        # CONE-VALUE ORDER, declared: a closed node removes its whole A57 descendant cone, and the
        # cone is biggest at level 1 (~20.8 nodes, against ~14.1 at L2 and 8 at L3 under A96's
        # measured f2 = 0.906, f3 = 0.762, f4 = 0).  The three level-3 nodes are taken next so
        # every level is represented before the CPU cap can bind.
        rank = {1: 0, 3: 1, 2: 2}
        ids = sorted(ids, key=lambda x: (rank.get(A.node_level(x), 3), x))
    ids = [x for k, x in enumerate(ids) if k % n == i]
    if a.limit:
        ids = ids[:a.limit]
    log("A120 shard %d/%d: %d nodes, N = %s, cpu_cap %.0f s" % (i, n, len(ids), entry["id"],
                                                                a.cpu_cap))
    t0 = time.time()
    done = []
    for nid in ids:
        if A.pausegate.paused():
            log("PAUSE sentinel set (%s) -- stopping cleanly between nodes"
                % A.pausegate.reason())
            break
        el = time.time() - t0
        if el > a.cpu_cap:
            log("cpu cap reached (%.0f s) -- stopping between nodes" % el)
            break
        wall = min(a.node_wall, a.cpu_cap - el)
        if wall < 120:
            log("less than 120 s of cap left -- stopping")
            break
        r = run_node(nid, entry, log, cert_time=a.cert_time, wall=wall, stage1=a.stage1,
                     lp_cap=a.lp_cap, cert_rounds=a.cert_rounds, cert_wall=a.cert_wall)
        done.append((nid, r["status"]))
    log("shard %d done: %.0f s, %d nodes: %s" % (i, time.time() - t0, len(done),
                                                 json.dumps(done)))


if __name__ == "__main__":
    main()
