"""A111 -- certify a NO child with the FROZEN verifier.

A NO child is an ordinary A57 case-LP node: hypothesis = the parent's cores + ONE NO-family, budget
unchanged.  Its certificate is therefore exactly caselp.make_certificate's (the file already carries
`hypotheses.nofams` with rational t-intervals) and the arbiter is the frozen verify_case.py, run
through A57's own certify.py at --jobs 1 (tree57.VERIFY_JOBS_CAP: at --jobs 1 verify_case takes its
in-process branch and spawns no pool).  Nothing here re-implements a verifier.

Note for the record: A96's PARAMETRIC verifier verify_param.py refuses NO-families
(`nofams unsupported`), so a load-path NO child can only be certified at a FIXED side -- i.e. on
A57's four-side slack-core grid, one certificate per grid side, not as one window certificate.
"""
from __future__ import annotations

import argparse, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L

S_RAT = L.S_RAT


def certify(tag, rounds=1, depth=56, cert_time=240.0, scale_cap=1.4, log=print):
    node = os.path.join(L.NODES, tag + ".json")
    out = os.path.join(L.CERTS, tag + ".json")
    cmd = [sys.executable, os.path.join(HERE, "certify.py"), node, "--s_rat", S_RAT,
           "--rounds", str(rounds), "--jobs", "1", "--depth", str(depth),
           "--time_limit", str(cert_time), "--out", out, "--scale", "0",
           "--scale_cap", "%.5f" % scale_cap, "--max_w", "64", "--loop_cols"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    txt = p.stdout + p.stderr
    tail = [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "[round", "certificate", "CERTIFIED",
                             "NOT certified", "MALFORMED"))]
    log("  %-58s rc=%d (%.0fs)" % (tag, p.returncode, time.time() - t0))
    for l in tail[-8:]:
        log("      " + l)
    return dict(tag=tag, rc=p.returncode, result=("PASS" if p.returncode == 0 else "FAIL"),
                cert=out if p.returncode == 0 else None, seconds=round(time.time() - t0, 1),
                verifier=tail[-8:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--from_runs", default=None, help="pick DEAD children from a t2 runs jsonl")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--sink", default=None)
    A = ap.parse_args()
    logp = os.path.join(L.LOGS, "certify111.log")

    def log(*x):
        m = " ".join(str(v) for v in x)
        print(m, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + m + "\n")

    tags = list(A.tags)
    if A.from_runs:
        # prefer converged-DEAD children; fall back to the LP-dead-but-unconverged ones, which is
        # what the measurement actually produced (A57 would never certify those either -- reporting
        # the exact verifier's answer on them is the point).
        prim, sec, seen = [], [], set()
        for pat in A.from_runs.split(","):
            if not os.path.exists(pat):
                continue
            for line in open(pat, encoding="utf-8"):
                d = json.loads(line)
                t = d.get("tag")
                if not t or t in seen:
                    continue
                if d.get("dead"):
                    seen.add(t); prim.append(t)
                elif d.get("dead_unconv"):
                    seen.add(t); sec.append(t)
        tags = (tags + prim + sec)[:A.n]
    sink = A.sink or os.path.join(L.RES, "t2_certs.jsonl")
    log("certifying %d NO children (frozen verify_case.py, --jobs 1, depth %d)" % (len(tags), A.depth))
    for t in tags:
        if not L.gate(log, t):
            continue
        try:
            r = certify(t, rounds=A.rounds, depth=A.depth, cert_time=A.cert_time, log=log)
        except BaseException as ex:
            r = dict(tag=t, result="ERROR", error=repr(ex)[:200])
        with open(sink, "a") as f:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
