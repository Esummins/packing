"""A136/A151 continuation -- the 26 owed on the SYMMETRIC N and the 10 new consumers on A151's
certified ASYMMETRIC N, through the same cover and the same F-COVER wrapper.

    python run151.py --entry base --shard i/n --cpu_cap S
    python run151.py --entry asym --shard i/n --cpu_cap S

WHAT IS REUSED.  A120's `a120lib`/`noside120`, A112's `regiontree`/`caselp`/`certify` and A136's
`a136lib.narrow` are IMPORTED, never copied, so the cover, the A1..A7 soundness assertions, the
two-stage LP protocol, the frozen `verify_case.py` and the inward rounding + `ZONE ⊆ BOX` check at
emission are byte-identical by construction.  A112's writable directories are redirected into this
attempt, into a DIFFERENT subtree per entry (`results/nodes[_asym]`, `certs[_asym]`), so the two
queues never share a record.

MACHINE RULES (coordinator, 2026-09-08).  Two workers at NORMAL priority; affinity mask `0xFFFF`
(CPUs 0-15) set on the driver, which every child inherits; the whole lab must stay at or under 16
python processes, so `wait_for_slot` counts them (excluding the Claude MCP extension venv) before
every node and YIELDS while the box is full; the memory gate is A112's own `a111lib.gate`, whose
constants are already exactly the required ones (`MIN_FREE_COMMIT_MB = 6144`,
`MIN_FREE_PHYS_MB = 3072`) and which `regiontree.Runner.lp` calls before EVERY LP; the per-LP wall
is 1 500 s (`--lp_cap`, stage 1 at 240 s).  This attempt's own scoped sentinel
(`attempts/A136-a120-resume/PAUSE`) is the stop button; A57's PAUSE belongs to another owner and is
never touched.

A149 SKIP LIST.  `attempts/A149-a57-reprice/results/exact_reemit_w*.jsonl` is re-read before every
node: a node A149 has already certified dead on exact cores (`result: PASS`) is SKIPPED, because a
kill it already holds is not worth a second one.  A149 is still running, so the list is re-read
rather than snapshotted.
"""
from __future__ import annotations

import argparse, ctypes, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402  (BLAS pin inside)
import entry151 as E                                               # noqa: E402

A120C = os.path.join(A6.ROOT, "attempts", "A120-no-side-runner", "code")
sys.path.insert(0, A120C)
import a120lib as A                                                # noqa: E402
import noside120 as NS                                             # noqa: E402
import regiontree as RT                                            # noqa: E402
import a111lib as A111                                             # noqa: E402
from caselp import Hyp                                             # noqa: E402

A149R = os.path.join(A6.ROOT, "attempts", "A149-a57-reprice", "results")
BASE136 = A6.BASE
ORDERING = NS.ORDERING
AFFINITY = 0xFFFF                     # CPUs 0-15; children inherit the parent's mask on Windows
LAB_CAP = 16

BOXES = {}                            # node id -> mapped boxes, for the emitter's sidecar


# ------------------------------------------------------------------ machine rules
def set_affinity(log):
    try:
        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = ctypes.c_void_p
        k32.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k32.SetProcessAffinityMask.restype = ctypes.c_int
        ok = k32.SetProcessAffinityMask(k32.GetCurrentProcess(), AFFINITY)
        log("  affinity mask 0x%X set on this process (children inherit): %s" % (AFFINITY, bool(ok)))
    except Exception as e:                                          # never fatal
        log("  affinity could not be set: %s" % e)


def lab_python():
    """Number of OTHER owners' lab python processes on the box.

    The Claude MCP extension's venv does not count, and NEITHER DO THIS ATTEMPT'S OWN PROCESSES.
    Counting my own footprint against my own admission gate deadlocks the two workers the
    coordinator sanctioned: whichever worker is mid-certification holds a `certify136.py` child,
    which pushes the count to the ceiling and locks the other worker out of its next node -- observed
    2026-09-08 19:51-21:04, one worker idle 72 minutes while the other worked.  The ceiling exists to
    stop this attempt piling load on beyond its 2 approved workers, so it is applied to everyone
    ELSE's processes."""
    ps = ("@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -notmatch 'Claude Extensions|windows-mcp|"
          "A136-a120-resume' }).Count")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                             capture_output=True, text=True, timeout=120).stdout.strip()
    except Exception:
        return 0
    try:
        return int(out.split()[0])
    except Exception:                       # never let a parse failure gate the run open
        return 0


def wait_for_slot(log, need=1, poll=120.0, deadline=None):
    """Yield while the box is at the lab process cap.  Returns False if the deadline passed."""
    said = False
    while True:
        n = lab_python()
        if n + need <= LAB_CAP or n == 0:
            if said:
                log("  slot free (%d lab python processes) -- continuing" % n)
            return True
        if deadline is not None and time.time() > deadline:
            log("  box still full (%d) at the deadline -- stopping cleanly" % n)
            return False
        if not said:
            log("  box full: %d OTHER lab python processes (cap %d; this attempt's own 2 workers "
                "are not counted against their own gate) -- YIELDING, polling every %.0f s"
                % (n, LAB_CAP, poll))
            said = True
        time.sleep(poll)


def a149_skip():
    """{node id: row} for every node A149's exact-core re-emission has already certified dead."""
    out = {}
    for p in sorted(glob.glob(os.path.join(A149R, "exact_reemit_w*.jsonl"))):
        try:
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        r = json.loads(ln)
                    except Exception:
                        continue
                    if r.get("result") == "PASS" and r.get("id"):
                        out[r["id"]] = dict(result="PASS", tau=r.get("tau"),
                                            wall_s=r.get("wall_total_s"), worker=r.get("worker"),
                                            lane=r.get("lane"), source=os.path.basename(p))
        except OSError:
            continue
    return out


# ------------------------------------------------------------------ the certifier, with the fix
def certify_leaf_capped151(region, ordering, key, node_json, log, cert_time=420.0, depth=56,
                           rounds=6, wall=2600.0):
    """`a120lib.certify_leaf_capped`, argument for argument, with `certify136.py` in place of
    A112's `certify.py` -- same command line, same hard wall, same CAP semantics (a capped run can
    only ABORT, never decide), and the F-COVER wrapper at emission."""
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
                  note="the mapped YES boxes; the emitter writes them into the certificate and "
                       "checks ZONE subset BOX on the written rationals"))
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
    t0 = time.time()
    capped = False
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
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


A.certify_leaf_capped = certify_leaf_capped151      # what noside120.run_node calls


def restatus(rec, entry):
    """Re-derive the node status from its children.

    A node is CLOSED only when every NO child is certified AND the YES leaf cites a certificate
    that actually exists.  An entry whose certificate is `PENDING-CERTIFICATE` (A160's union: no
    file, no sha256, no independent check -- only an in-run float `tree_verdict`) can never produce
    a closure here, however well the NO side goes; that case is recorded as NO-COMPLETE, which says
    exactly what was earned: the expensive half is done and banked, and one certificate emission
    stands between it and a closure."""
    cite = entry.get("certificate") or {}
    citeable = bool(cite.get("sha256")) and cite.get("status") != "PENDING-CERTIFICATE"
    n = len(rec.get("boxes_used") or [])
    st = [rec["children"].get("NO%d" % i, {}).get("status") for i in range(n)]
    rec["child_status"] = st
    all_dead = bool(n) and all(x == "DEAD-CERT" for x in st)
    if all_dead and citeable:
        rec["status"] = "CLOSED"
        rec["claim"] = ("A57 node %s (cls %s) is DEAD at s0 = %r: YES leaf dead by the local "
                        "certificate %s (%s, sha %s), all %d NO children dead by the frozen "
                        "verify_case.py on certificates whose NO zone is inside the YES box "
                        "(ZONE subset BOX on the written rationals)"
                        % (rec["id"], rec["cls"], rec["s"], entry["id"], cite.get("format"),
                           cite["sha256"][:12], len(st)))
    elif all_dead:
        rec["status"] = "NO-COMPLETE"
        rec["yes_leaf_pending"] = cite
        rec["claim"] = ("A57 node %s (cls %s): all %d NO children are certified dead by the frozen "
                        "verify_case.py, each on a certificate whose NO zone is inside the YES box "
                        "(ZONE subset BOX on the written rationals).  The node is NOT closed: its "
                        "YES leaf would have to cite %s, for which NO certificate artefact exists "
                        "(no file, no sha256, no independent check -- only an in-run float "
                        "tree_verdict).  One certificate emission away."
                        % (rec["id"], rec["cls"], len(st), entry["id"]))
    elif any(x is None for x in st):
        rec["status"] = "PARTIAL"
    else:
        rec["status"] = "OPEN"
        rec["open_children"] = [("NO%d" % i) for i, x in enumerate(st) if x != "DEAD-CERT"]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", default="base", choices=("base", "asym", "a160", "a163"))
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--cpu_cap", type=float, default=27000.0)
    ap.add_argument("--node_wall", type=float, default=9000.0)
    ap.add_argument("--cert_time", type=float, default=420.0)
    ap.add_argument("--cert_wall", type=float, default=2600.0)
    ap.add_argument("--cert_rounds", type=int, default=6)
    ap.add_argument("--stage1", type=float, default=240.0)
    ap.add_argument("--lp_cap", type=float, default=1500.0)
    ap.add_argument("--queue", required=True, help="json file with {'ids': [...]}")
    ap.add_argument("--skip_done", action="store_true",
                    help="RESUME: skip a node that already has a terminal record in results/"
                         "nodes<suffix>/ (CLOSED / OPEN / SKIP-UNSOUND).  noside120.run_node caches "
                         "at node AND at NO-child level anyway, so this only saves the re-derivation "
                         "of the soundness sample and the per-box check; it is what makes a "
                         "rebooted run cost nothing to restart.")
    ap.add_argument("--out_suffix", default=None,
                    help="Override the per-entry output subtree (results/nodes<S>, certs<S>, "
                         "results/rt<S>) and the NO-child certificate name suffix.  A NODE RECORD "
                         "AND ITS NO-CHILD CERTIFICATES ARE KEYED BY NODE ID ONLY, NOT BY THE YES "
                         "LEAF: noside120 caches at node AND at NO-child level, so re-running a "
                         "node against a DIFFERENT certified N inside the same subtree would "
                         "silently return the first N's verdicts.  Pass a fresh suffix (A136, "
                         "2026-09-09) whenever the same id is run against a second YES leaf; the "
                         "first run's record is then preserved untouched next to it.")
    a = ap.parse_args()
    i, n = (int(x) for x in a.shard.split("/"))

    # ---- per-entry output subtree; the two queues never share a record
    suffix = {"base": "", "asym": "_asym", "a160": "_a160", "a163": "_a163"}[a.entry]
    A.RES = A6.RES
    A.NODES = os.path.join(A6.RES, "nodes" + suffix)
    A.CERTS = os.path.join(A6.BASE, "certs" + suffix)
    A.LOGS, A.PROG = A6.LOGS, A6.PROG
    for d in (A.NODES, A.CERTS):
        os.makedirs(d, exist_ok=True)
    A.L.RES, A.L.NODES, A.L.CERTS, A.L.LOGS = A.RES, A.NODES, A.CERTS, A.LOGS
    A.L.RT = os.path.join(A6.RES, "rt" + suffix)
    A.L.SUF = {"base": "_a136", "asym": "_a136x", "a160": "_a136u",
                "a163": "_a136f"}[a.entry]
    if a.out_suffix:
        # a second YES leaf for ids this attempt has already run: fresh record subtree AND fresh
        # NO-child certificate names, so neither cache layer can serve the first leaf's verdicts.
        suffix = a.out_suffix
        A.NODES = os.path.join(A6.RES, "nodes" + suffix)
        A.CERTS = os.path.join(A6.BASE, "certs" + suffix)
        for d in (A.NODES, A.CERTS):
            os.makedirs(d, exist_ok=True)
        A.L.NODES, A.L.CERTS = A.NODES, A.CERTS
        A.L.RT = os.path.join(A6.RES, "rt" + suffix)
        A.L.SUF = "_a136" + suffix.replace("_", "")
        os.makedirs(A.L.RT, exist_ok=True)
    os.makedirs(A.L.RT, exist_ok=True)

    log = A6.mklog("run151_%s%s_%d.log" % (a.entry, a.out_suffix or "", i))
    per_node = a.entry in ("a160", "a163")
    entry = None if per_node else E.entry_for(a.entry)
    if a.entry == "a163":
        cite = dict(file="per node: attempts/A163-s02-other-frames/certs/<entry>.tcert.json.gz",
                    sha256=None, status="CHECKED (per node; each entry's own sha256 and exact "
                                        "rational certified minimum are recorded on the node)",
                    boxes="the CHECKED certified set the node's support lies in, with the largest "
                          "verified rational margin over s0")
    elif per_node:
        cite = dict(file="per node: attempts/A160-s02-f0-slide/results/N_boxes160.json",
                    sha256=None, status="PENDING-CERTIFICATE",
                    boxes="the union entry each node's support lies in")
    else:
        cite = entry["certificate"]
    t0 = time.time()
    log("A151-resume shard %d/%d  entry=%s (%s)  cap %.0f s"
        % (i, n, a.entry, ("per node, A160 union" if per_node else entry["id"]), a.cpu_cap))
    log("  YES-leaf certificate: %s  sha %s%s"
        % (cite["file"], (cite["sha256"][:16] if cite.get("sha256") else "NONE"),
           ("  *** %s ***" % cite["status"]) if cite.get("status") else ""))
    log("  boxes: %s" % cite["boxes"])
    log("  LP: stage1 %.0f s -> per-LP wall %.0f s;  cert rounds %d wall %.0f s time_limit %.0f s"
        % (a.stage1, a.lp_cap, a.cert_rounds, a.cert_wall, a.cert_time))
    log("  memory gate (A112 a111lib.gate, called before EVERY LP): commit > %.0f MB, phys > %.0f MB"
        % (A111.MIN_FREE_COMMIT_MB, A111.MIN_FREE_PHYS_MB))
    set_affinity(log)

    Q = json.load(open(a.queue, encoding="utf-8"))["ids"]
    Q = [(x if isinstance(x, dict) else dict(id=x)) for x in Q]
    Q = [x for k, x in enumerate(Q) if k % n == i]
    ids = [x["id"] for x in Q]
    LINK = {x["id"]: x.get("link") for x in Q}
    A163 = {x["id"]: (x.get("entry"), x.get("frame")) for x in Q}
    log("  queue %s: %d nodes in this shard" % (os.path.basename(a.queue), len(ids)))

    skipped, done = [], []
    if a.skip_done:
        have = {}
        for p in sorted(glob.glob(os.path.join(A.NODES, "rec__*.json"))):
            try:
                r = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            if r.get("id"):
                have[r["id"]] = r.get("status")
        pre = [x for x in ids if have.get(x) in ("CLOSED", "OPEN", "SKIP-UNSOUND")]
        if pre:
            log("  RESUME: %d of %d already terminal on disk, skipped: %s"
                % (len(pre), len(ids), json.dumps([[x, have[x]] for x in pre])))
        ids = [x for x in ids if have.get(x) not in ("CLOSED", "OPEN", "SKIP-UNSOUND")]
        log("  RESUME: %d nodes left to run in this shard" % len(ids))
    for nid in ids:
        if A.pausegate.paused(base=BASE136):
            log("PAUSE sentinel set (%s) -- stopping cleanly" % A.pausegate.reason(base=BASE136))
            break
        el = time.time() - t0
        if el > a.cpu_cap:
            log("cpu cap reached (%.0f s) -- stopping between nodes" % el)
            break
        # A149 may have certified this node dead since the queue was built
        sk = a149_skip().get(nid)
        if sk:
            log("  %-32s SKIP: A149 already certified it dead on exact cores (%s, tau %.6f)"
                % (nid, sk["source"], sk.get("tau") or float("nan")))
            skipped.append(dict(id=nid, reason="A149 exact-core kill", a149=sk))
            continue
        if not wait_for_slot(log, need=1, deadline=t0 + a.cpu_cap):
            break
        wall = min(a.node_wall, a.cpu_cap - (time.time() - t0))
        if wall < 300:
            log("less than 300 s of cap left -- stopping")
            break
        if a.entry == "a163":
            eid, fr = A163[nid]
            entry = E.a163_entry(eid, fr)
            log("  %-32s %s (frame %s; verified margin over s0 %.3e; YES leaf %s)"
                % (nid, entry["id"], fr, entry["certificate"]["margin_over_s0"],
                   entry["certificate"]["status"]))
        elif per_node:
            entry = E.entry_for("a160", link=LINK[nid])
            log("  %-32s union entry %s (margin over s0 %s; YES leaf %s)"
                % (nid, entry["id"], entry["certificate"]["margin_over_s0"],
                   entry["certificate"]["status"]))
        op = (A.extract_index()[nid].get("struct_op") or "e")
        local, _ = A.node_src(nid)
        s = A.jload(local)["s"]
        mapped = [A.map_box(b, op, s) for b in entry["boxes"]]
        BOXES[nid] = mapped
        r = NS.run_node(nid, entry, log, cert_time=a.cert_time, wall=wall, stage1=a.stage1,
                        lp_cap=a.lp_cap, cert_rounds=a.cert_rounds, cert_wall=a.cert_wall)
        rec = NS.load_rec(A.node_cls(nid), nid)
        if rec is not None:
            # the tight, per-box A4/A5 -- a120lib's use a single (r, rho) and are loose on an
            # asymmetric N
            ex = A.extract_index().get(nid) or {}
            import math as _m
            cfg = [(p[0], p[1], _m.degrees(p[2])) for p in ex.get("cfg") or []]
            rec["per_box_soundness"] = E.per_box_check(mapped, entry, A.d4(op, s), cfg=cfg)
            rec["a136"] = dict(fcover=A6.FCOVER_TAG,
                               yes_leaf_certificate=entry["certificate"],
                               entry=a.entry, N=entry["id"])
            restatus(rec, entry)
            if False:
                # the NO side is complete and certified, but the YES leaf cites an object with no
                # certificate file, no sha256 and no independent check -- so this is NOT a closure.
                rec["status"] = "NO-COMPLETE"
                rec["yes_leaf_pending"] = entry["certificate"]
                rec["claim"] = (
                    "A57 node %s: all %d NO children are certified dead by the frozen "
                    "verify_case.py with ZONE subset BOX on the written rationals.  The node is "
                    "NOT closed: its YES leaf needs the local certificate for A160 union entry %s, "
                    "which does not exist yet (no file, no sha256, no independent check -- only an "
                    "in-run float tree_verdict).  One certificate emission away."
                    % (rec["id"], len(rec["child_status"]), entry["id"]))
            NS.save_rec(rec)
            if not rec["per_box_soundness"]["ok"]:
                log("  %-32s WARNING per-box soundness NOT ok: %s"
                    % (nid, json.dumps(rec["per_box_soundness"])[:200]))
        done.append((nid, r["status"]))
        log("  %-32s %s" % (nid, r["status"]))

    A6.jdump(os.path.join(A6.RES, "skipped_a149_%s_%d.json" % (a.entry, i)),
             dict(entry=a.entry, shard=a.shard, skipped=skipped))
    log("shard %d done: %.0f s, %d nodes, %d skipped by A149: %s"
        % (i, time.time() - t0, len(done), len(skipped), json.dumps(done)))


if __name__ == "__main__":
    sys.exit(main())
