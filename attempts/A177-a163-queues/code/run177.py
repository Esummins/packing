"""A177 -- A136's `run151.py`, argument for argument, with THREE changes and no edit to A136.

    python run177.py --entry a163 --queue <q> --out_suffix _a177h10 --cpu_cap S [--skip_done]

1. **The certifier is `certify136x.py`, not `certify136.py`** -- A170's exact cores are carried
   INSIDE the witness-feedback loop (`caselp.make_certificate -> carry_exact_cores (ENLARGE only)
   -> a136lib.narrow`), so every round's certificate exempts A135's certified exact core rather
   than `caselp`'s stock one.  A136 measured the difference: on `Y0941/NO3` the stock-core loop
   ended at `total 5.025 >= budget 5` after its full round budget and the exact-core loop PASSed at
   ROUND 0 in 7.1 s.  Nothing else about the certification changes -- same command line, same hard
   wall, same CAP semantics (a capped run can only ABORT, never decide), the same frozen
   `verify_case.py`, and the F-COVER `narrow` still runs last so `ZONE subset BOX` is established
   on the file that is actually written.
2. **The process-cap gate does not count THIS attempt's own processes.**  A136's `lab_python`
   excludes command lines matching `A136-a120-resume`; run from here the pattern would not match,
   so the two sanctioned workers would count each other and their certifier children and lock
   themselves out -- the exact deadlock A136 recorded on 2026-09-08 (one worker idle 72 minutes).
   The pattern is extended to this attempt's directory and nothing else: A136's still-running base
   worker, A176's, A168's, coex174's and the coordinator's processes all still count, and the
   ceiling is still 16.
3. **The PAUSE sentinel is this attempt's own** (`attempts/A177-a163-queues/PAUSE`).  A136's and
   A57's sentinels belong to other owners and are never read as this run's stop button, and never
   written.

Every record it writes is stamped `a177` so `report177.py` can tag the closure rows with the
attempt that earned them; the records themselves go into A136's `results/nodes<suffix>/` and the
certificates into A136's `certs<suffix>/`, because that is where `report136.py` and
`docs/shadows/status_gallery.py` look, and this attempt is finishing A136's owed queue rather than
opening a second board.

Both frozen verifiers are asserted byte-identical before a single node runs:
`verify_case.py` sha `521cb01f...` (A112, the NO certificates) and `verify_param.py` v1 sha
`0c58485c...` (A96, the parametric layer).  PYTHONDONTWRITEBYTECODE=1.  READ-ONLY on A112, A119,
A120, A133, A151, A163 and A170.
"""
from __future__ import annotations

import hashlib, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A136C = os.path.join(ROOT, "attempts", "A136-a120-resume", "code")

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, A136C)

import a136lib as A6                                               # noqa: E402  (BLAS pin inside)
import run151 as R                                                 # noqa: E402
A = R.A                                                            # a120lib, shared instance

FROZEN = {
    os.path.join(ROOT, "attempts", "A112-dual-branching", "code", "verify_case.py"):
        "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af",
    os.path.join(ROOT, "attempts", "A96-a57-parametric", "code", "verify_param.py"):
        "0c58485c",                                                # prefix; the full sha is A96's
}


def assert_frozen():
    for p, want in FROZEN.items():
        with open(p, "rb") as f:
            got = hashlib.sha256(f.read()).hexdigest()
        if not got.startswith(want):
            raise SystemExit("A177: %s is NOT the frozen verifier: %s != %s..."
                             % (os.path.basename(p), got, want))
    return True


# ---------------------------------------------------------------- 1. the certifier
def certify_leaf_capped177(region, ordering, key, node_json, log, cert_time=420.0, depth=56,
                           rounds=6, wall=2600.0):
    """`run151.certify_leaf_capped151`, with `certify136x.py` (exact cores in the loop) in place of
    `certify136.py` (stock cores).  Same CAP semantics; the wall kills the process TREE."""
    tag = "%s%s__%s__%s" % (region, A.L.SUF, ordering, key)
    node = os.path.join(A.L.NODES, node_json)
    out = os.path.join(A.L.CERTS, tag + ".json")
    if os.path.exists(out + ".done"):
        return A.L.jload(out + ".done")
    boxes = R.BOXES.get(region)
    if not boxes:
        return dict(tag=tag, result="NO-BOXES")
    A6.jdump(node + ".a136box.json",
             dict(node=region, boxes=boxes,
                  note="the mapped YES boxes; the emitter writes them into the certificate and "
                       "checks ZONE subset BOX on the written rationals"))
    if not A.L.gate(log, tag):
        return dict(tag=tag, result="SKIP-GATE")
    cmd = [sys.executable, os.path.join(A136C, "certify136x.py"), node, "--s_rat", A.L.S_RAT,
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
        except Exception:                                          # noqa: BLE001
            txt = ""
        rc = 124
    tail = [ln for ln in txt.splitlines()
            if ln.startswith(("PASS", "FAIL", "boxes", "[round", "certificate", "CERTIFIED",
                              "NOT certified", "MALFORMED", "a136"))]
    r = dict(tag=tag, rc=rc, result=("PASS" if rc == 0 else ("CAP" if capped else "FAIL")),
             capped=capped, wall_cap_s=wall, rounds=rounds, cert_time=cert_time,
             seconds=round(time.time() - t0, 1), verifier=tail[-8:], fcover=A6.FCOVER_TAG,
             a177=dict(certifier="certify136x.py",
                       cores="A170 carry_exact_cores (ENLARGE only) INSIDE the loop"))
    A.L.jdump(out + ".done", r)
    log("    cert %-46s %s (%.0fs)  [exact cores in the loop]" % (key, r["result"], r["seconds"]))
    return r


# ---------------------------------------------------------------- 2. the gate
def lab_python177():
    ps = ("@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -notmatch 'Claude Extensions|windows-mcp|"
          "A177-a163-queues' }).Count")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                             capture_output=True, text=True, timeout=120).stdout.strip()
    except Exception:                                              # noqa: BLE001
        return 0
    try:
        return int(out.split()[0])
    except Exception:                                              # noqa: BLE001
        return 0


# ---------------------------------------------------------------- 3. the record stamp
_RESTATUS = R.restatus


def restatus177(rec, entry):
    out = _RESTATUS(rec, entry)
    out["a177"] = dict(
        attempt="A177", certifier="certify136x.py (A170 exact cores INSIDE the loop)",
        entry_rule="widest citeable N (min tilt width, then log-volume; margin as tie-break)",
        frozen=dict(verify_case="521cb01f", verify_param_v1="0c58485c"),
        note="A136's owed a163 queues, finished under the two findings of its notes/frames151.md "
             "sections 6 and 7")
    return out


def main():
    assert_frozen()
    A6.LOGS = os.path.join(BASE, "logs")                            # this attempt's own logs
    os.makedirs(A6.LOGS, exist_ok=True)
    R.BASE136 = BASE                                                # this attempt's own sentinel
    R.lab_python = lab_python177
    R.restatus = restatus177
    A.certify_leaf_capped = certify_leaf_capped177
    return R.main()


if __name__ == "__main__":
    sys.exit(main())
