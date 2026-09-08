#!/usr/bin/env python3
"""
supervise146.py -- run A61's UNMODIFIED resolve61.py under a hard per-LP-call process wall.

A124 (`attempts/A124-recheck-day/notes/y0381_hang.md`) proved the failure mode: lpbox.LPModel
sets only `output_flag=False` and `threads=1` on the Highs object -- **no `time_limit` option** --
and solve_node's own `time_limit` is checked only BETWEEN iterations, so a single `h.run()` can
spin forever on one thread with no output.  k5_13 lost ~40 CPU-h to exactly that on 2026-09-06.

lpbox.py / resolve61.py / campaign61.py are NOT edited and NOT copied-with-edits: this supervisor
is a plain subprocess parent.  It cannot see inside h.run(), so it infers "we are inside an LP"
from two facts about the driver:

  * the driver prints ONE LINE PER LP ITERATION (`  it   N tau=... t=...s`) on stdout, and
  * every other long phase of the driver -- certify.py, verify_param.py, specialize.py,
    verify_case.py -- runs as a CHILD PROCESS.

so silence WITH a living descendant is a certifier/verifier doing its job (it must not be
disturbed), while silence WITHOUT any descendant is the driver itself burning CPU between two
log lines, i.e. `h.run()`.  The wall is applied to the second case only.

On a trip the process tree is killed with taskkill /T /F and a **CAP** record is appended --
never a verdict.  The relaunch is the driver's own resume: `enriched_warm()` globs
`results/nodes/<name>*.json`, so the checkpoint the killed LP had already written
(`solve_node(checkpoint=...)`, one write per iteration) is folded back into the column pool and
the next attempt starts strictly better off than the one before.

Usage:
  python supervise146.py --name k5_13 [--wall 1500] [--deadline_h 3.5] [--attempts 3] -- <driver args>
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse                                                        # noqa: E402
import ctypes                                                          # noqa: E402
import ctypes.wintypes as wt                                           # noqa: E402
import json                                                            # noqa: E402
import queue                                                           # noqa: E402
import subprocess                                                      # noqa: E402
import sys                                                             # noqa: E402
import threading                                                       # noqa: E402
import time                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A146 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A146, ".."))
A61 = os.path.join(ATT, "A61-window-stragglers")
DRIVER = os.path.join(A61, "code", "resolve61.py")
RESULTS = os.path.join(A146, "results")
LOGS = os.path.join(A146, "logs")
for _d in (RESULTS, LOGS):
    os.makedirs(_d, exist_ok=True)


# ------------------------------------------------------------------ descendant detection
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD),
                ("th32ParentProcessID", wt.DWORD), ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wt.DWORD), ("szExeFile", ctypes.c_char * 260)]


_k32 = ctypes.windll.kernel32


def process_table():
    """[(pid, ppid, exe)] for every process on the box, via CreateToolhelp32Snapshot.
    Pure ctypes: no extra process is spawned to answer the question (psutil is not installed
    and a PowerShell/CIM probe would itself count against the process budget)."""
    snap = _k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE:
        return []
    out = []
    try:
        e = PROCESSENTRY32()
        e.dwSize = ctypes.sizeof(PROCESSENTRY32)
        ok = _k32.Process32First(snap, ctypes.byref(e))
        while ok:
            out.append((int(e.th32ProcessID), int(e.th32ParentProcessID),
                        e.szExeFile.decode("mbcs", "replace")))
            ok = _k32.Process32Next(snap, ctypes.byref(e))
    finally:
        _k32.CloseHandle(snap)
    return out


def descendants(pid):
    tab = process_table()
    kids = {}
    for p, pp, exe in tab:
        kids.setdefault(pp, []).append((p, exe))
    out, stack = [], [pid]
    seen = {pid}
    while stack:
        cur = stack.pop()
        for p, exe in kids.get(cur, []):
            if p in seen:
                continue
            seen.add(p)
            out.append((p, exe))
            stack.append(p)
    return out


def kill_tree(pid, log):
    r = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       capture_output=True, text=True)
    log(f"    taskkill rc={r.returncode} {r.stdout.strip()} {r.stderr.strip()}")


# ------------------------------------------------------------------ supervisor
def run_once(argv, name, wall, deadline, log, rec, attempt):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[v] = "1"
    cmd = [sys.executable, DRIVER, "--name", name] + list(argv)
    log("    $ " + " ".join(cmd))
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=os.path.join(A61, "code"), env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, bufsize=1, encoding="utf-8", errors="replace",
                         creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    q = queue.Queue()

    def reader():
        try:
            for ln in p.stdout:
                q.put(ln.rstrip("\n"))
        except Exception as ex:                                     # pragma: no cover
            q.put(f"<<reader error: {ex}>>")
        finally:
            q.put(None)

    th = threading.Thread(target=reader, daemon=True)
    th.start()

    last = time.time()
    ev = {"attempt": attempt, "pid": p.pid, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "cmd": cmd, "lines": 0, "quiet_probes": []}
    rec.setdefault("runs", []).append(ev)
    save(rec)
    done = False
    while not done:
        try:
            ln = q.get(timeout=30.0)
        except queue.Empty:
            ln = ""
        if ln is None:
            done = True
            break
        if ln:
            last = time.time()
            ev["lines"] += 1
            log(f"    | {ln}")
        quiet = time.time() - last
        if quiet > 120.0:
            kids = descendants(p.pid)
            if kids:
                # a certifier / verifier is running: this is legitimate silence, and the wall
                # must NOT be applied to it (the driver caps those with its own --cert_time /
                # --param_timeout).  Reset the clock so the wall only ever measures LP silence.
                last = time.time()
                ev["quiet_probes"].append({"t": round(time.time() - t0, 1),
                                           "quiet_s": round(quiet, 1),
                                           "children": [f"{k}:{e}" for k, e in kids][:6]})
                save(rec)
            elif quiet > wall:
                ev["event"] = "CAP"
                ev["cap_reason"] = (f"no stdout for {quiet:.0f}s (> {wall:.0f}s wall) with NO "
                                    f"live descendant process: the driver is inside a single "
                                    f"h.run() (A124 hang mode). Killed; NOT a verdict.")
                ev["capped_after_s"] = round(time.time() - t0, 1)
                log("    *** CAP: " + ev["cap_reason"])
                save(rec)
                kill_tree(p.pid, log)
                try:
                    p.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    pass
                ev["rc"] = "killed"
                ev["seconds"] = round(time.time() - t0, 1)
                save(rec)
                return "CAP"
        if time.time() > deadline:
            ev["event"] = "DEADLINE"
            ev["capped_after_s"] = round(time.time() - t0, 1)
            log("    *** DEADLINE reached; killing the tree (NOT a verdict).")
            save(rec)
            kill_tree(p.pid, log)
            try:
                p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                pass
            ev["rc"] = "killed"
            ev["seconds"] = round(time.time() - t0, 1)
            save(rec)
            return "DEADLINE"
    rc = p.wait()
    ev["rc"] = rc
    ev["seconds"] = round(time.time() - t0, 1)
    ev["event"] = "EXIT"
    save(rec)
    log(f"    driver exited rc={rc} after {ev['seconds']}s")
    return f"EXIT:{rc}"


REC = None


def save(rec):
    tmp = REC + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    os.replace(tmp, REC)


def main(argv=None):
    global REC
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--wall", type=float, default=1500.0,
                    help="hard per-LP-call process wall (s)")
    ap.add_argument("--deadline_h", type=float, default=3.5)
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--tag", default="run")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    rest = [x for x in a.rest if x != "--"]

    REC = os.path.join(RESULTS, f"supervisor_{a.name}_{a.tag}.json")
    lp = os.path.join(LOGS, f"supervise_{a.name}_{a.tag}.log")
    lf = open(lp, "a", buffering=1, encoding="utf-8")

    def log(*x):
        print(*x, file=lf, flush=True)
        print(*x, flush=True)

    rec = {"attempt": "A146", "name": a.name, "driver": DRIVER, "wall_s": a.wall,
           "deadline_h": a.deadline_h, "driver_args": rest,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "note": "A CAP is a resource event, never a verdict (soundness.md: only the "
                   "verifier decides).  lpbox.py/resolve61.py/campaign61.py are unmodified."}
    save(rec)
    t0 = time.time()
    deadline = t0 + a.deadline_h * 3600.0
    log(f"=== A146 supervisor: {a.name}, per-LP wall {a.wall:.0f}s, "
        f"deadline {a.deadline_h}h, up to {a.attempts} attempts")
    outcome = None
    for i in range(1, a.attempts + 1):
        log(f"--- attempt {i}/{a.attempts} (t+{time.time() - t0:.0f}s)")
        outcome = run_once(rest, a.name, a.wall, deadline, log, rec, i)
        rec["last_outcome"] = outcome
        save(rec)
        if outcome.startswith("EXIT") or outcome == "DEADLINE":
            break
        if time.time() > deadline:
            rec["last_outcome"] = "DEADLINE"
            break
    rec["total_wall_s"] = round(time.time() - t0, 1)
    rec["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save(rec)
    log(f"=== done: {rec['last_outcome']} after {rec['total_wall_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
