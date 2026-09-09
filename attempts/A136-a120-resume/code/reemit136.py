"""A136 -- re-emit every cert-blocked NO child through `certify136x.py` (EXACT cores in the loop).

THE FINDING THIS AUTOMATES.  A170's scan says all 122 of this attempt's certificates are
`kind: "stock"` / `exact_lane: false` -- A136 certifies through `caselp.make_certificate`, which
`Hyp.from_json`s the hypothesis and throws A135's exact cores away.  Two experiments, in order:

  1. `exactcert136.py` PATCHES the written certificate (cores enlarged, frozen verifier re-run, no
     LP): **2 of 16 recovered** (`Y0441/NO0` CAP -> PASS, closing that node; `Y0691/NO3`).  The 14
     that stayed FAIL split into real HOLES -- which a wider core cannot fix -- and one class the
     patch provably cannot reach, `total mass >= budget: certificate proves nothing`, where the
     emitted MEASURE is short rather than the cover leaky.  A depth-64 re-run of the low-hole
     failures recovered **0 of 6** and turned `Y1147/NO1`'s "0 HOLES" into 4 real holes, so depth
     was not the constraint either.
  2. RE-EMISSION with the wider cores inside the witness-feedback loop, which is what this driver
     does.  On `k5_16_interior_Y0941/NO3` -- the sole survivor of a node carrying an ALIVE
     docs/shadows page -- the stock-core loop had ended at `total 5.025000 >= budget 5` after the
     full round budget, and the exact-core loop **PASSed at ROUND 0 in 7.1 s** with
     `total = 2492839/500000 = 4.98568 < 5`.  The cores were 2.26 % wider; that was the whole gap.

So a cert-CAP or cert-FAIL on this lane is not evidence about the node until it has been re-emitted
with the cores the LP was entitled to use.

    python reemit136.py [--only a,b] [--wall S] [--adopt]

Each child is run as `certify136x.py` in a SUBPROCESS with a hard wall (the process TREE is killed
on timeout), so one pathological child cannot eat the budget.  Certificates go to `certs<suf>x/`;
no existing certificate is overwritten.  Results append to `results/reemit136.jsonl`, which is also
the resume set.  READ-ONLY on every other attempt.  PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402
import exactcert136 as EC                                          # noqa: E402  (candidates())

OUT = os.path.join(A6.RES, "reemit136.jsonl")
S_RAT = "969271/250000"


def kill_tree(proc):
    try:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True, timeout=60)
    except Exception:                                              # noqa: BLE001
        pass
    try:
        proc.kill()
    except Exception:                                              # noqa: BLE001
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--rounds", type=int, default=16)
    ap.add_argument("--time_limit", type=float, default=700.0)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--child_wall", type=float, default=3000.0)
    ap.add_argument("--wall", type=float, default=12000.0)
    ap.add_argument("--adopt", action="store_true")
    a = ap.parse_args()

    log = A6.mklog("reemit136.log")
    cands = EC.candidates()
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        cands = [c for c in cands if c["node"] in want]
    log("candidates %d (%d sole survivors of their node); rounds %d x %.0f s, child wall %.0f s"
        % (len(cands), sum(1 for c in cands if c["n_alive_in_node"] == 1),
           a.rounds, a.time_limit, a.child_wall))

    done = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    if r.get("result") == "KILLED":
                        continue                        # never a verdict: retry it
                    done[r["id"]] = r

    t_start = time.time()
    for c in cands:
        key = "%s%s/%s" % (c["node"], c["suf"], c["child"])
        if key in done:
            continue
        if time.time() - t_start > a.wall:
            log("wall reached -- stopping between children")
            break
        suf = "" if c["suf"] == "(base)" else c["suf"]
        node_json = os.path.join(A6.RES, "nodes" + suf,
                                 os.path.basename(c["cert"]))
        if not os.path.exists(node_json):
            log("%-44s NO NODE JSON (%s)" % (key, node_json))
            continue
        outdir = os.path.join(A6.BASE, EC.CERTDIR.get(suf, "certs" + suf) + "x")
        os.makedirs(outdir, exist_ok=True)
        outp = os.path.join(outdir, os.path.basename(c["cert"]))
        cmd = [sys.executable, "-u", os.path.join(HERE, "certify136x.py"), node_json,
               "--s_rat", S_RAT, "--rounds", str(a.rounds), "--jobs", "1",
               "--depth", str(a.depth), "--time_limit", str(a.time_limit),
               "--out", outp, "--scale", "0", "--scale_cap", "1.4",
               "--max_w", "64", "--loop_cols"]
        t0 = time.time()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        # each child streams to its OWN log so a long one can be watched while it runs
        clog = os.path.join(A6.LOGS, "reemit_%s.log" % key.replace("/", "_").replace("(", "")
                            .replace(")", ""))
        with open(clog, "w", encoding="utf-8") as lf:
            lf.write(" ".join(cmd) + "\n")
        lf = open(clog, "a", encoding="utf-8", buffering=1)
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, text=True,
                             env=env, cwd=HERE)
        try:
            p.wait(timeout=a.child_wall)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            kill_tree(p)                                           # the process TREE
            rc = None
        lf.close()
        txt = open(clog, encoding="utf-8", errors="replace").read()
        el = round(time.time() - t0, 1)
        tail = [l for l in (txt or "").splitlines()
                if l.startswith(("PASS", "FAIL", "[round", "CERTIFIED", "GAVE UP", "    PASS",
                                 "    FAIL", "a136x:"))]
        ok = os.path.exists(outp) and rc == 0 and "CERTIFIED" in (txt or "")
        # 0xC000013A is STATUS_CONTROL_C_EXIT: the child was torn down with its parent, which is a
        # RESOURCE EVENT, not a verdict.  Recording it as FAIL would poison the resume set with a
        # verdict nothing measured -- the same rule the lab applies to a CAP.  (A136, 2026-09-09,
        # after a kill of this driver wrote four such rows.)
        killed = (rc in (3221225794, -1073741510)) or (rc not in (0, None) and el < 1.0)
        result = ("PASS" if ok else
                  "WALL" if rc is None else
                  "KILLED" if killed else "FAIL")
        row = dict(id=key, node=c["node"], suf=c["suf"], child=c["child"], was=c["was"],
                   n_alive_in_node=c["n_alive_in_node"], eta=c["eta"], tau=c["tau"],
                   result=result, rc=rc, seconds=el,
                   cert=(os.path.relpath(outp, A6.ROOT).replace("\\", "/") if ok else None),
                   cert_prev=c["cert_src"] if "cert_src" in c else
                   os.path.relpath(c["cert"], A6.ROOT).replace("\\", "/"),
                   rounds=a.rounds, time_limit=a.time_limit, depth=a.depth,
                   child_wall=a.child_wall, log=os.path.relpath(clog, A6.ROOT).replace("\\", "/"),
                   tail=tail[-6:])
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        done[key] = row
        log("%-44s %-4s -> %-5s  %5.0f s  | %s"
            % (key, c["was"], result, el, (tail[-1][:70] if tail else "")))

    if a.adopt:
        n = 0
        for key, r in sorted(done.items()):
            if r["result"] != "PASS":
                continue
            suf = "" if r["suf"] == "(base)" else r["suf"]
            rp = os.path.join(A6.RES, "nodes" + suf, "rec__%s__%s.json"
                              % (r["node"].split("_interior")[0], r["node"]))
            if not os.path.exists(rp):
                log("adopt: no record %s" % rp)
                continue
            rec = A6.jload(rp)
            ch = rec["children"][r["child"]]
            if ch.get("status") == "DEAD-CERT":
                continue
            ch["status"] = "DEAD-CERT"
            ch["cert"] = dict(
                result="PASS", file=r["cert"], seconds=r["seconds"], rounds=r["rounds"],
                source="A136 certify136x.py (A170 exact cores inside the witness-feedback loop)",
                note="RE-EMITTED: the same LP solution, certified again with A135's exact "
                     "vertex-certified cores carried through caselp.make_certificate by A170's "
                     "certwrap170.carry_exact_cores (ENLARGE only) before A136's F-COVER narrow, "
                     "which re-ran the decidable ZONE subset BOX on the written rationals.  "
                     "Verified by the FROZEN verify_case.py.  Previous verdict on the stock-core "
                     "certificate: %s (kept unchanged at %s)." % (r["was"], r["cert_prev"]))
            st = [rec["children"].get("NO%d" % i, {}).get("status")
                  for i in range(len(rec.get("boxes_used") or []))]
            rec["child_status"] = st
            rec["open_children"] = [i for i, s in enumerate(st) if s != "DEAD-CERT"]
            if st and all(s == "DEAD-CERT" for s in st):
                rec["status"] = "CLOSED"
            A6.jdump(rp, rec)
            n += 1
            log("adopted %s -> node %s now %s" % (key, rec["id"], rec["status"]))
        log("adopted %d" % n)

    npass = sum(1 for r in done.values() if r["result"] == "PASS")
    log("ledger: %d children, %d PASS -> %s" % (len(done), npass, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
