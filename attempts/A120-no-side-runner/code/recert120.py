"""A120 T3(b) -- re-certification pass for NO children the LP put CLEARLY below budget but whose
first certificate the frozen verifier refused.

Two different things make a NO child ALIVE and the report must not blur them:

  (a) `eta ~ 0` -- the node LP, converged, says the child is NOT below budget.  No amount of
      certifier time changes that: the child is a genuine survivor.
  (b) `eta <= -1e-3` with a FAILing certificate -- the LP says clearly dead, but the measure
      `certify.py` emitted was not coverable: the verifier came back with witnesses (uncovered
      admissible boxes).  A112's protocol runs `--rounds 1`, i.e. ONE witness-feedback re-solve,
      and leaves such a child ALIVE.  That is a certifier-shortfall, not a survivor.

This pass retries (b) only, with more witness-feedback rounds and a longer emission limit.  It
changes nothing about the verdict rule: the FROZEN `verify_case.py` is still the only arbiter, the
same code path (`regiontree.certify_leaf` -> `certify.py --jobs 1`) is used, and a child is
promoted to DEAD-CERT only on a PASS.  The retry is recorded separately from the first attempt, so
the A112-protocol numbers stay readable on their own.

(Emission nondeterminism is expected and documented: `certify.py --loop_cols` re-solves the node
LP under a time limit before emitting, so the atom set is wall-clock dependent -- A57
`code/FREEZE_TAGS.txt`.  The VERIFIER is deterministic; T2 replays certificates, never re-emits.)
"""
from __future__ import annotations

import argparse, glob, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a120lib as A                                     # noqa: E402
import regiontree as RT                                 # noqa: E402
import noside120 as NS                                  # noqa: E402
from caselp import Hyp                                  # noqa: E402

ETA_CLEAR = -1e-3


def candidates():
    out = []
    for p in sorted(glob.glob(os.path.join(A.NODES, "rec__*.json"))):
        r = A.jload(p)
        # ONLY finished nodes.  A record is written by exactly one process; running this pass
        # against a node a worker is still inside would let the worker's next save clobber the
        # promotion (observed once, 2026-09-07 00:54 -- Y0637/NO0).  A finished node has status
        # OPEN, and the runner never touches it again (its cache branch returns at once).
        if r.get("status") != "OPEN":
            continue
        for k, c in sorted(r.get("children", {}).items()):
            if c.get("status") != "ALIVE" or not c.get("cert_failed"):
                continue
            eta = (c.get("lp") or {}).get("eta")
            if eta is None or eta > ETA_CLEAR:
                continue
            out.append((r, k, c, eta))
    # PRIORITY: nodes that are CLOSEST TO CLOSING first.  A node closes only when all four NO
    # children certify, so a certificate on the last open child of a 3-of-4 node is worth a whole
    # closure (and its A57 descendant cone), while one on a 1-of-4 node is worth nothing on its
    # own.  Within a node, the most clearly-dead child first.
    nopen = {}
    for (r, k, c, eta) in out:
        nopen[r["id"]] = nopen.get(r["id"], 0) + 1
    out.sort(key=lambda t: (nopen[t[0]["id"]], t[3]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--cert_time", type=float, default=600.0)
    ap.add_argument("--cpu_cap", type=float, default=7200.0)
    ap.add_argument("--cert_wall", type=float, default=1200.0)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    i, n = (int(x) for x in a.shard.split("/"))
    log = A.mklog("recert%d.log" % i)
    # shard by NODE, never by candidate: two shards must never write the same record.
    allc = candidates()
    order = []
    for (r, k, c, eta) in allc:
        if r["id"] not in order:
            order.append(r["id"])
    mine = {nid for j, nid in enumerate(order) if j % n == i}
    cands = [x for x in allc if x[0]["id"] in mine]
    log("A120 re-certification: %d candidate NO children (eta <= %g, first certificate FAILed), "
        "rounds=%d, cert_time=%.0f s, cap %.0f s" % (len(cands), ETA_CLEAR, a.rounds,
                                                     a.cert_time, a.cpu_cap))
    t0 = time.time()
    promoted = 0
    for (r, k, c, eta) in cands:
        # Do not redo work a first attempt has already settled.  A FAIL at >= these rounds is a
        # real refusal of the frozen verifier and more of the same loop will not change it; a CAP
        # is right-censored, so it is retried only when this pass offers a STRICTLY larger wall.
        first = c.get("cert") or {}
        fr = first.get("rounds") or 0
        if first.get("result") == "FAIL" and fr >= a.rounds:
            log("  %-32s %s skip: FAIL already at rounds %d" % (r["id"], k, fr))
            continue
        if (first.get("result") == "CAP" and fr >= a.rounds
                and (first.get("wall_cap_s") or 0) >= a.cert_wall):
            log("  %-32s %s skip: CAP at rounds %d with wall %.0f s (no larger wall offered)"
                % (r["id"], k, fr, first.get("wall_cap_s") or 0))
            continue
        if A.pausegate.paused():
            log("PAUSE sentinel set -- stopping cleanly")
            break
        if time.time() - t0 > a.cpu_cap:
            log("cap reached -- stopping")
            break
        rec = NS.load_rec(r["cls"], r["id"]) or r
        ch = rec["children"][k]
        if ch.get("status") == "DEAD-CERT":
            continue
        key2 = "%s_r%d" % (k, a.rounds)
        cc = A.certify_leaf_capped(rec["id"], NS.ORDERING, key2, ch["node_json"], log,
                                   cert_time=a.cert_time, rounds=a.rounds, wall=a.cert_wall)
        ch["cert_retry"] = dict(cc)
        rec["cert_wall_s"] = round(rec.get("cert_wall_s", 0.0) + cc.get("seconds", 0.0), 1)
        if cc["result"] == "PASS":
            ch["status"] = "DEAD-CERT"
            ch["cert_failed"] = False
            ch["cert_tag"] = A.NO_TAG
            ch["promoted_by"] = "recert120 rounds=%d" % a.rounds
            h = Hyp.from_json(ch["hyp"])
            ch["trump_realizes"] = RT.trump_canary(h, A.L.pin_slots(A.L.split_hyp(h)[0]))
            promoted += 1
        st = [rec["children"].get("NO%d" % j, {}).get("status")
              for j in range(len(rec["boxes_used"]))]
        rec["child_status"] = st
        if all(x == "DEAD-CERT" for x in st):
            rec["status"] = "CLOSED"
            rec["claim"] = ("A57 node %s (cls %s) is DEAD at s0 = %r: YES leaf dead by local "
                            "certificate A116 %s, all %d NO children dead by the frozen "
                            "verify_case.py" % (rec["id"], rec["cls"], rec["s"], rec["N"], len(st)))
        elif any(x is None for x in st):
            rec["status"] = "PARTIAL"
        else:
            rec["status"] = "OPEN"
            rec["open_children"] = [("NO%d" % j) for j, x in enumerate(st) if x != "DEAD-CERT"]
        NS.save_rec(rec)
        log("  %-32s %s eta=%+.4f -> %s (%s, %.0f s)  node now %s"
            % (rec["id"], k, eta, cc["result"], key2, cc.get("seconds", 0.0), rec["status"]))
    log("re-certification done: %.0f s, %d promoted of %d candidates"
        % (time.time() - t0, promoted, len(cands)))


if __name__ == "__main__":
    main()
