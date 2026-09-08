"""A136 T2 -- resume A120's NO-side runner with the F-COVER fix in the emitter.

    python run136.py --queue children|targets [--shard i/n] [--cpu_cap 34200]

WHAT IS REUSED AND WHAT IS NEW.  A120's `a120lib` / `noside120` and A112's `regiontree` /
`caselp` / `certify` are IMPORTED, never copied, so the cover, the A1..A7 soundness assertions,
the two-stage LP protocol (240 s -> certify on eta <= -1e-3; 900 s only at the knife edge) and
the frozen `verify_case.py` are byte-identical by construction.  Three things are new:

  1. every certificate is emitted through `certify136.py`, i.e. through `a136lib.narrow`: the NO
     zone written INWARD, the YES box written into the certificate, `ZONE subset BOX` checked on
     the WRITTEN rationals and raising on failure (finding F-COVER, A126/A133);
  2. A112's writable directories -- which A120 redirected into A120 -- are redirected AGAIN, into
     this attempt.  A120 is read-only: its node records and LP results are only ever READ, and
     the LP result of an open child is COPIED here before it is certified;
  3. the pause sentinel is SCOPED (`pausegate.paused(base=<this attempt>)`, PAUSED.md v2 s7a), so
     A123's `attempts/A57-shadow-trees/PAUSE` -- which is another owner's control file and is
     left exactly where it is -- does not stop this driver, while every driver that calls the
     bare `paused()` stays paused.  This attempt's own stop button is
     `attempts/A136-a120-resume/PAUSE`.

QUEUES (disjoint by node, so two processes never write one record -- A120's operational note):

  `--queue children`  the open NO children of the 11 nodes A120 processed whose LP put them
                      CLEARLY below budget (eta <= -1e-3) and whose certificate FAILed or was
                      CAPped: a certifier shortfall, not a survivor.  A child with eta > -1e-3 is
                      a GENUINE survivor and is never retried -- no certifier budget changes a
                      converged LP at tau = budget.
  `--queue targets`   the 24 targets A120 never reached, in its cone-value order.

A120's DEAD-CERT children are NOT inherited as kills: under the fix each one is a kill only if
its certificate re-certifies with the narrowed zone, which is T1 (`recert136.py`).  This driver
reads T1's result and seeds each record accordingly.

CAP is never a verdict.  A capped certification is recorded as CAP and the child stays ALIVE.
"""
from __future__ import annotations

import argparse, glob, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402  (BLAS pin inside)

A120C = os.path.join(A6.ROOT, "attempts", "A120-no-side-runner", "code")
sys.path.insert(0, A120C)
import a120lib as A                                                # noqa: E402
import noside120 as NS                                             # noqa: E402
import regiontree as RT                                            # noqa: E402
from caselp import Hyp                                             # noqa: E402

# ---- REDIRECT A112's (and A120's) writable directories into A136.  A120 is READ-ONLY.
A.RES, A.NODES, A.LOGS, A.CERTS, A.PROG = A6.RES, A6.NODES, A6.LOGS, A6.CERTS, A6.PROG
A.L.RES, A.L.NODES, A.L.CERTS, A.L.LOGS = A6.RES, A6.NODES, A6.CERTS, A6.LOGS
A.L.RT = os.path.join(A6.RES, "rt")
A.L.SUF = "_a136"
os.makedirs(A.L.RT, exist_ok=True)

A120B = os.path.join(A6.ROOT, "attempts", "A120-no-side-runner")
A120N = os.path.join(A120B, "results", "nodes")
ORDERING = NS.ORDERING                       # "a116N"
ETA_CLEAR = -1e-3
BASE136 = A6.BASE

# A133's t-parametrised local certificate for the very N A120's YES leaf cites (same L, same P,
# same boxes; `dead: true`).  Sharper than A116's prose form and the citation the Lean hand-off
# should carry.
A133_TCERT = dict(id="S02_k5_11_r0.20_rho10", format="local-cert-t-v1",
                  file="attempts/A133-tan-half-emission/certs/S02_k5_11_r0.20_rho10.tcert.json.gz",
                  sha256="a8d95682490e5caeae5512d8db11f5927bb1e53725fa31cf48ce073101a9ab72",
                  dead=True, leaves=16406, L=["f1", "f2", "f3", "BR(0,1)"],
                  P=["BL(0,0)", "BL(0,1)", "TL(0,0)", "BL(1,0)", "BR(0,0)"])

BOXES = {}                                   # node id -> mapped A119 boxes (for the emitter)


# ------------------------------------------------------------------ the certifier, with the fix
def certify_leaf_capped136(region, ordering, key, node_json, log, cert_time=420.0, depth=56,
                           rounds=6, wall=2600.0):
    """`a120lib.certify_leaf_capped`, argument for argument, with `certify136.py` in place of
    A112's `certify.py` -- the same command line, the same hard wall, the same CAP semantics
    (a capped run can only ABORT, never decide), and the F-COVER wrapper at emission."""
    tag = "%s%s__%s__%s" % (region, A.L.SUF, ordering, key)
    node = os.path.join(A.L.NODES, node_json)
    out = os.path.join(A.L.CERTS, tag + ".json")
    if os.path.exists(out + ".done"):
        return A.L.jload(out + ".done")
    boxes = BOXES.get(region)
    if not boxes:
        return dict(tag=tag, result="NO-BOXES")
    A6.jdump(node + ".a136box.json",
             dict(node=region, boxes=boxes,
                  note="the mapped A119 boxes of the YES side; the emitter writes them into the "
                       "certificate and checks ZONE subset BOX on the written rationals"))
    if not A.L.gate(log, tag):
        return dict(tag=tag, result="SKIP-GATE")
    cmd = [sys.executable, os.path.join(HERE, "certify136.py"), node, "--s_rat", A.L.S_RAT,
           "--rounds", str(rounds), "--jobs", "1", "--depth", str(depth),
           "--time_limit", str(cert_time), "--out", out, "--scale", "0",
           "--scale_cap", "1.4", "--max_w", "64", "--loop_cols"]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[v] = "1"
    flags = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    t0 = time.time()
    capped = False
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=env, creationflags=flags)
    try:
        txt = p.communicate(timeout=wall)[0] or ""
        rc = p.returncode
    except subprocess.TimeoutExpired:
        capped = True
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        try:
            txt = p.communicate(timeout=60)[0] or ""
        except Exception:
            txt = ""
        rc = 124
    tail = [ln for ln in txt.splitlines()
            if ln.startswith(("PASS", "FAIL", "boxes", "[round", "certificate", "CERTIFIED",
                              "NOT certified", "MALFORMED", "a136"))]
    r = dict(tag=tag, rc=rc, result=("PASS" if rc == 0 else ("CAP" if capped else "FAIL")),
             capped=capped, wall_cap_s=wall, rounds=rounds, cert_time=cert_time,
             seconds=round(time.time() - t0, 1), verifier=tail[-8:], fcover=A6.FCOVER_TAG)
    A.L.jdump(out + ".done", r)
    log("    cert %-46s %s (%.0fs)" % (key, r["result"], r["seconds"]))
    return r


A.certify_leaf_capped = certify_leaf_capped136          # what noside120.run_node calls


# ------------------------------------------------------------------ T1's verdicts
def t1_index():
    """tag -> T1 row (the re-certification of A120's PASSing certificates under the fix)."""
    idx = {}
    for p in sorted(glob.glob(os.path.join(A6.RES, "t1_recert_*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                idx[r["tag"]] = r
    return idx


def seed_record(nid, entry, log):
    """A136's own record for a node A120 processed: A120's record READ, every DEAD-CERT child
    re-judged by T1 (a kill under the fix only if its certificate re-certified with the narrowed
    zone), everything else carried over as ALIVE."""
    cls = A.node_cls(nid)
    p = NS.rec_path(cls, nid)
    if os.path.exists(p):
        return A.jload(p)
    src = os.path.join(A120N, "rec__%s__%s.json" % (cls, nid))
    rec = A.jload(src)
    t1 = t1_index()
    rec["src_record"] = os.path.relpath(src, A6.ROOT)
    rec["a136"] = dict(fcover=A6.FCOVER_TAG, yes_leaf_certificate=A133_TCERT)
    rec["a120_status"] = rec.get("status")
    for k, c in sorted(rec.get("children", {}).items()):
        c["a120_status"] = c.get("status")
        tags = [((c.get(f) or {}).get("tag"), f) for f in ("cert", "cert_retry")]
        hit = None
        for tg, f in tags:
            if tg and t1.get(tg, {}).get("result") == "PASS":
                hit = t1[tg]
        if c.get("status") == "DEAD-CERT" and hit:
            c["status"] = "DEAD-CERT"
            c["cert_fcover"] = dict(tag=hit["tag"], result="PASS", seconds=hit["verify"]["seconds"],
                                    zone_sub_box=True, file=hit["cert_file"],
                                    max_abs_delta=hit["max_abs_delta"])
            c["cert_failed"] = False
        else:
            if c.get("status") == "DEAD-CERT":
                c["status"] = "ALIVE"
                c["note"] = ("A120 kill NOT inherited: its certificate did not re-certify with "
                             "the inward-rounded zone (F-COVER)")
                c["cert_failed"] = True
            c.setdefault("note", c.get("note") or "")
    _restatus(rec)
    NS.save_rec(rec)
    log("  seeded %-32s %s  %s" % (nid, rec["status"], rec.get("child_status")))
    return rec


def _restatus(rec):
    n = len(rec.get("boxes_used") or [])
    st = [rec["children"].get("NO%d" % i, {}).get("status") for i in range(n)]
    rec["child_status"] = st
    if n and all(x == "DEAD-CERT" for x in st):
        rec["status"] = "CLOSED"
        rec["claim"] = ("A57 node %s (cls %s) is DEAD at s0 = %r: YES leaf dead by the local "
                        "certificate for %s (A133 t-form, %s), all %d NO children dead by the "
                        "frozen verify_case.py on certificates whose NO zone is inside the YES "
                        "box (ZONE subset BOX on the written rationals)"
                        % (rec["id"], rec["cls"], rec["s"], rec["N"], A133_TCERT["sha256"][:12],
                           len(st)))
    elif any(x is None for x in st):
        rec["status"] = "PARTIAL"
    else:
        rec["status"] = "OPEN"
        rec["open_children"] = [("NO%d" % i) for i, x in enumerate(st) if x != "DEAD-CERT"]
    return rec


# ------------------------------------------------------------------ queue 1: the open children
def child_queue(log):
    """Open NO children of A120's processed nodes that are a CERTIFIER SHORTFALL (eta <= -1e-3),
    ordered by A120's rule: the node closest to closing first, most clearly-dead child first."""
    _, entry = A.n_entry()
    out = []
    for p in sorted(glob.glob(os.path.join(A120N, "rec__*.json"))):
        a120rec = A.jload(p)
        nid = a120rec["id"]
        rec = seed_record(nid, entry, log)
        for k, c in sorted(rec.get("children", {}).items()):
            if c.get("status") == "DEAD-CERT":
                continue
            eta = (c.get("lp") or {}).get("eta")
            if eta is None or eta > ETA_CLEAR:
                continue                       # genuine survivor: no certifier budget helps
            out.append((nid, k, eta))
    # A120's priority (the node CLOSEST TO CLOSING first, most clearly-dead child first) with one
    # refinement: a node that has a GENUINE survivor among its open children cannot be closed by
    # this cover at any certifier budget, so its shortfall children -- however cheap -- are worth
    # nothing on their own and go last.
    nopen, nalive = {}, {}
    for (nid, k, eta) in out:
        nopen[nid] = nopen.get(nid, 0) + 1
    for p in sorted(glob.glob(os.path.join(A120N, "rec__*.json"))):
        nid = A.jload(p)["id"]
        rec = NS.load_rec(A.node_cls(nid), nid)
        if rec:
            nalive[nid] = sum(1 for v in (rec.get("child_status") or []) if v != "DEAD-CERT")
    out.sort(key=lambda t: (nalive.get(t[0], 99) != nopen[t[0]], nopen[t[0]], t[2]))
    return out


def run_child(nid, key, log, cert_time, cert_wall, rounds, entry):
    cls = A.node_cls(nid)
    rec = NS.load_rec(cls, nid)
    ch = rec["children"][key]
    if ch.get("status") == "DEAD-CERT":
        return rec
    op = rec["struct_op"]
    s = rec["s"]
    BOXES[nid] = [A.map_box(b, op, s) for b in entry["boxes"]]
    # A120's LP result for this child, COPIED here (A120 is read-only), under this attempt's tag.
    src = os.path.join(A120N, ch["node_json"])
    nj = "%s%s__%s__%s.json" % (nid, A.L.SUF, ORDERING, key)
    dst = os.path.join(A6.NODES, nj)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
    ch["node_json_a136"] = nj
    ch["lp_source"] = os.path.relpath(src, A6.ROOT)
    c = certify_leaf_capped136(nid, ORDERING, key, nj, log, cert_time=cert_time,
                               rounds=rounds, wall=cert_wall)
    ch["cert_fcover"] = c
    rec["cert_wall_s"] = round(rec.get("cert_wall_s", 0.0) + c.get("seconds", 0.0), 1)
    if c["result"] == "PASS":
        ch["status"] = "DEAD-CERT"
        ch["cert_failed"] = False
        ch["promoted_by"] = "A136 run136 --queue children (rounds=%d, wall=%.0f s)" % (rounds,
                                                                                       cert_wall)
        h = Hyp.from_json(ch["hyp"])
        ch["trump_realizes"] = RT.trump_canary(h, A.L.pin_slots(A.L.split_hyp(h)[0]))
    else:
        ch["status"] = "ALIVE"
        ch["cert_failed"] = True
    _restatus(rec)
    NS.save_rec(rec)
    log("  %-32s %s -> %s   node now %s" % (nid, key, c["result"], rec["status"]))
    return rec


# ------------------------------------------------------------------ queue 2: the 24 targets
def target_queue():
    ids = A.targets()
    have = {A.jload(p)["id"] for p in glob.glob(os.path.join(A120N, "rec__*.json"))}
    rank = {1: 0, 3: 1, 2: 2}                 # A120's cone-value order, verbatim
    return sorted([x for x in ids if x not in have],
                  key=lambda x: (rank.get(A.node_level(x), 3), x))


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", default="children", choices=("children", "targets", "both"))
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--cpu_cap", type=float, default=34200.0)
    ap.add_argument("--node_wall", type=float, default=7200.0)
    ap.add_argument("--cert_time", type=float, default=420.0)
    ap.add_argument("--cert_wall", type=float, default=2600.0)
    ap.add_argument("--cert_rounds", type=int, default=6)
    ap.add_argument("--stage1", type=float, default=240.0)
    ap.add_argument("--lp_cap", type=float, default=900.0)
    ap.add_argument("--target_slice", default=None, help="i/n slice of the target queue")
    a = ap.parse_args()
    i, n = (int(x) for x in a.shard.split("/"))
    log = A6.mklog("run136_%d.log" % i)
    _, entry = A.n_entry()
    t0 = time.time()
    log("A136 T2 shard %d/%d queue=%s  cap %.0f s  cert rounds=%d wall=%.0f s time_limit=%.0f s"
        % (i, n, a.queue, a.cpu_cap, a.cert_rounds, a.cert_wall, a.cert_time))
    log("  scoped sentinel: %s (A57's PAUSE is another owner's file and is left in place)"
        % os.path.join(BASE136, "PAUSE"))

    def stop():
        if A.pausegate.paused(base=BASE136):
            log("PAUSE sentinel set (%s) -- stopping cleanly"
                % A.pausegate.reason(base=BASE136))
            return True
        if time.time() - t0 > a.cpu_cap:
            log("cpu cap reached (%.0f s) -- stopping" % (time.time() - t0))
            return True
        return False

    if a.queue in ("children", "both"):
        q = child_queue(log)
        log("  queue children: %d certifier-shortfall NO children (eta <= %g)" % (len(q), ETA_CLEAR))
        for (nid, key, eta) in q:
            if stop():
                break
            log("  %-32s %s eta=%+.6f -> certify (rounds %d, wall %.0f s)"
                % (nid, key, eta, a.cert_rounds, a.cert_wall))
            run_child(nid, key, log, a.cert_time, a.cert_wall, a.cert_rounds, entry)

    if a.queue in ("targets", "both"):
        ids = target_queue()
        if a.target_slice:
            j, m = (int(x) for x in a.target_slice.split("/"))
            ids = [x for k, x in enumerate(ids) if k % m == j]
        log("  queue targets: %d nodes" % len(ids))
        for nid in ids:
            if stop():
                break
            el = time.time() - t0
            wall = min(a.node_wall, a.cpu_cap - el)
            if wall < 300:
                log("less than 300 s of cap left -- stopping")
                break
            op = (A.extract_index()[nid].get("struct_op") or "e")
            local, _ = A.node_src(nid)
            s = A.jload(local)["s"]
            BOXES[nid] = [A.map_box(b, op, s) for b in entry["boxes"]]
            r = NS.run_node(nid, entry, log, cert_time=a.cert_time, wall=wall, stage1=a.stage1,
                            lp_cap=a.lp_cap, cert_rounds=a.cert_rounds, cert_wall=a.cert_wall)
            rec = NS.load_rec(A.node_cls(nid), nid)
            if rec is not None:
                rec["a136"] = dict(fcover=A6.FCOVER_TAG, yes_leaf_certificate=A133_TCERT)
                _restatus(rec)
                NS.save_rec(rec)
            log("  %-32s %s" % (nid, r["status"]))

    log("shard %d done: %.0f s" % (i, time.time() - t0))


if __name__ == "__main__":
    sys.exit(main())
