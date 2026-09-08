"""A149 -- the day's worker supervisor for the exact-pin-core re-emission.

This is A137's `run137.py` rebased on THIS attempt: same per-node PROCESS wall (1,500 s; CAP is
never a verdict), same memory gates, same claim protocol, same BLAS pinning -- but

  * every path it writes (claims, tmp, progress, logs, certs, out) is under A149, so A137 and
    every other prior attempt stay read-only;
  * the pause sentinel it watches is THIS attempt's (`attempts/A149-a57-reprice/PAUSE`);
    A57's own sentinel is reported at start and never touched;
  * a cumulative CPU-hour budget (`--cpu_budget_h`) stops the worker cleanly between nodes;
  * PROCESSOR AFFINITY 0xFFFF (logical CPUs 0-15, the P-core threads) on this process and on every
    child, re-applied on every loop pass -- the PI's E-cores 16-19 are reserved for the remote
    session (coordinator, 2026-09-08);
  * a BOX gate: the worker holds rather than launch a node if the number of lab python processes
    on the machine would exceed `--max_box_py` (16).  A156 is draining `queue_bc.json` at the same
    time and the two lanes coordinate ONLY through this ceiling.

Priority is `--priority` (default `Normal`; the shift started at `BelowNormal` while the PI had
the machine and was raised when it was released).

The node itself is A137's `node137.py`, imported by path and UNCHANGED, which calls A135's
`emit135.certify` (exact certified-maximal cores) and the FROZEN `verify_case.py`.
"""
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A137 = os.path.join(ROOT, "A137-night-shift-2")
sys.path.insert(0, os.path.join(A57, "code"))
from pausegate import paused, reason                                       # noqa: E402

PRIORITY = dict(Normal=0x00000020, BelowNormal=0x00004000, Idle=0x00000040)
AFFINITY_PCORES = 0xFFFF          # logical CPUs 0-15; 16-19 are the PI's E-cores
PROCESS_SET_INFORMATION = 0x0200
PROCESS_QUERY_INFORMATION = 0x0400


def set_affinity(pid, mask=AFFINITY_PCORES):
    """SetProcessAffinityMask on one pid.  Returns True on success; never raises."""
    try:
        k = ctypes.windll.kernel32
        h = k.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, int(pid))
        if not h:
            return False
        try:
            return bool(k.SetProcessAffinityMask(h, ctypes.c_size_t(mask)))
        finally:
            k.CloseHandle(h)
    except Exception:
        return False


def lab_python_count():
    """python.exe processes running lab code, from the whole box (A156's workers included)."""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             "Where-Object { $_.CommandLine -like '*packing*attempts*' }).Count"],
            capture_output=True, text=True, timeout=60)
        return int((out.stdout or "0").strip() or 0)
    except Exception:
        return 0                      # a failed count must never block the queue


class _MEMSTAT(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def _memstat():
    m = _MEMSTAT()
    m.dwLength = ctypes.sizeof(_MEMSTAT)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m


def phys_free_mb():
    try:
        return _memstat().ullAvailPhys / (1024.0 * 1024.0)
    except Exception:
        return 1e9


def commit_free_mb():
    try:
        return _memstat().ullAvailPageFile / (1024.0 * 1024.0)
    except Exception:
        return 1e9


def child_env(threads=1):
    e = dict(os.environ)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        e[k] = str(threads)
    return e


def cpu_hours_spent(resdir):
    """Total node wall recorded by every A149 worker so far, in CPU-hours (one core per node)."""
    tot = 0.0
    for fn in os.listdir(resdir):
        if fn.startswith(("exact_reemit_", "a60_reemit_")) and fn.endswith(".jsonl"):
            for ln in open(os.path.join(resdir, fn), encoding="utf-8"):
                try:
                    tot += float(json.loads(ln).get("wall_total_s") or 0.0)
                except Exception:
                    pass
    return tot / 3600.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=os.path.join(BASE, "results", "targets149.json"))
    ap.add_argument("--worker", default="w0")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out", default=None)
    ap.add_argument("--wall", type=float, default=1500.0, help="per-node PROCESS wall, seconds")
    ap.add_argument("--cap", type=float, default=420.0, help="LP time limit inside the node")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--min_free_phys_mb", type=float, default=3072.0)
    ap.add_argument("--min_commit_mb", type=float, default=6144.0)
    ap.add_argument("--cpu_budget_h", type=float, default=30.0,
                    help="cumulative CPU-hours across ALL A149 workers; stop between nodes")
    ap.add_argument("--priority", default="Normal", choices=sorted(PRIORITY))
    ap.add_argument("--lane", default="a57", choices=("a57", "a60"),
                    help="a57: A137's node137.py -> A135's emit135.certify (exact cores on the "
                         "pins and the conditioned box).  a60: this attempt's node_a60.py -> the "
                         "same certificate emitter and the same FROZEN verify_case.py, with the "
                         "hypothesis taken from A60's own node record and ONLY H's core made "
                         "exact (A60's pins are exact boxes and their cores must stay just under "
                         "1/2 or the slot cores touch).")
    ap.add_argument("--max_box_py", type=int, default=16,
                    help="ceiling on lab python processes for the WHOLE box, A156 included; the "
                         "worker holds rather than launch a node that would exceed it")
    ap.add_argument("--deadline", default=None, help="local HH:MM after which no node is launched")
    a = ap.parse_args()

    a60 = a.lane == "a60"
    if a60 and a.targets == os.path.join(BASE, "results", "targets149.json"):
        a.targets = os.path.join(BASE, "results", "targets_a60.json")
    out = a.out or os.path.join(BASE, "results", "%s_%s.jsonl"
                                % ("a60_reemit" if a60 else "exact_reemit", a.worker))
    resdir = os.path.join(BASE, "results")
    claims = os.path.join(BASE, "progress", "claims_a60" if a60 else "claims")
    tmp = os.path.join(BASE, "progress", "tmp")
    certdir = os.path.join(BASE, "certs", "a60") if a60 else os.path.join(BASE, "certs")
    for d in (claims, tmp, certdir, os.path.join(BASE, "logs")):
        os.makedirs(d, exist_ok=True)
    prog = os.path.join(BASE, "progress", "%s.json" % a.worker)
    with open(os.path.join(BASE, "progress", "%s.pid" % a.worker), "w") as f:
        f.write(str(os.getpid()))
    set_affinity(os.getpid())

    T = json.load(open(a.targets))
    si, sn = map(int, a.shard.split("/"))
    T = [j for i, j in enumerate(T) if i % sn == si]

    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass

    dl = None
    if a.deadline:
        hh, mm = map(int, a.deadline.split(":"))
        lt = time.localtime()
        dl = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, hh, mm, 0, 0, 0, -1))
        if dl < time.time():
            dl += 86400

    stats = dict(worker=a.worker, shard=a.shard, queued=len(T), started=time.strftime("%F %T"),
                 done=0, PASS=0, NO_KILL=0, FAIL=0, WALL_CAP=0, ERROR=0, other=0,
                 cpu_budget_h=a.cpu_budget_h)

    def flush(cur=None):
        stats["updated"] = time.strftime("%F %T")
        stats["current"] = cur
        stats["cpu_h_all_workers"] = round(cpu_hours_spent(resdir), 3)
        json.dump(stats, open(prog, "w"), indent=1)

    print("[%s] A57 sentinel: %s (%.50r) -- reported, untouched; this worker watches %s"
          % (a.worker, paused(base=A57), reason(base=A57), os.path.join(BASE, "PAUSE")),
          flush=True)
    print("[%s] %d targets in shard %s, wall %.0f s, LP cap %.0f s, budget %.1f CPU-h"
          % (a.worker, len(T), a.shard, a.wall, a.cap, a.cpu_budget_h), flush=True)
    flush()

    for j in T:
        if paused(base=BASE):
            print("[%s] A149 pause sentinel set (%.60r); stopping cleanly between nodes"
                  % (a.worker, reason(base=BASE)), flush=True)
            break
        spent = cpu_hours_spent(resdir)
        if spent >= a.cpu_budget_h:
            print("[%s] CPU budget reached (%.2f of %.1f CPU-h across all A149 workers); "
                  "stopping cleanly between nodes" % (a.worker, spent, a.cpu_budget_h), flush=True)
            break
        if dl and time.time() > dl:
            print("[%s] launch deadline %s passed; stopping cleanly" % (a.worker, a.deadline),
                  flush=True)
            break
        if j["id"] in done:
            continue
        set_affinity(os.getpid())            # re-applied every pass, per the PI's box rule
        nb = lab_python_count()
        while nb >= a.max_box_py:
            print("[%s] box gate: %d lab python processes (ceiling %d, A156 included); "
                  "holding 120 s" % (a.worker, nb, a.max_box_py), flush=True)
            stats["box_holds"] = stats.get("box_holds", 0) + 1
            flush("BOX-HOLD " + j["id"])
            time.sleep(120)
            if paused(base=BASE):
                break
            nb = lab_python_count()
        if paused(base=BASE):
            break
        cl = os.path.join(claims, j["id"] + ".claim")
        try:
            fd = os.open(cl, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, (a.worker + " " + str(int(time.time()))).encode())
            os.close(fd)
        except FileExistsError:
            continue
        pf, cf = phys_free_mb(), commit_free_mb()
        while pf < a.min_free_phys_mb or cf < a.min_commit_mb:
            print("[%s] memory gate: phys %.0f MB / commit %.0f MB (need %.0f/%.0f); holding 120 s"
                  % (a.worker, pf, cf, a.min_free_phys_mb, a.min_commit_mb), flush=True)
            stats["mem_holds"] = stats.get("mem_holds", 0) + 1
            flush("HOLD " + j["id"])
            time.sleep(120)
            if paused(base=BASE):
                break
            pf, cf = phys_free_mb(), commit_free_mb()
        if paused(base=BASE):
            os.remove(cl)
            break
        jobf = os.path.join(tmp, j["id"] + ".job.json")
        resf = os.path.join(tmp, j["id"] + ".res.json")
        json.dump(j, open(jobf, "w"))
        node = (os.path.join(HERE, "node_a60.py") if a60
                else os.path.join(A137, "code", "node137.py"))
        cmd = [sys.executable, node, "--job", jobf, "--out", resf, "--cap", str(a.cap),
               "--rounds", str(a.rounds), "--jobs", str(a.jobs), "--certdir", certdir]
        t0 = time.time()
        flush(j["id"])
        print("[%s] %s START %s L%s frac_exact=%s eta_before=%s phys=%.0f MB"
              % (a.worker, time.strftime("%H:%M:%S"), j["id"], j.get("level"),
                 j.get("frac_exact"), j.get("eta"), pf), flush=True)
        logp = os.path.join(BASE, "logs", "%s_nodes.log" % a.worker)
        with open(logp, "a", encoding="utf-8") as lg:
            lg.write("\n===== %s %s\n" % (j["id"], time.strftime("%F %T")))
            lg.flush()
            p = subprocess.Popen(cmd, stdout=lg, stderr=subprocess.STDOUT, env=child_env(),
                                 cwd=BASE, creationflags=PRIORITY[a.priority])
            if not set_affinity(p.pid):
                lg.write("===== WARNING: could not set affinity 0x%X on child %d\n"
                         % (AFFINITY_PCORES, p.pid))
            try:
                rc = p.wait(timeout=a.wall)
            except subprocess.TimeoutExpired:
                p.kill()
                try:
                    p.wait(timeout=60)
                except Exception:
                    pass
                rc = "WALL"
                lg.write("===== WALL-CAP %.0fs, process killed (NOT a verdict)\n" % a.wall)
        if rc == "WALL":
            rec = dict(id=j["id"], scope=j.get("scope"), result="WALL-CAP",
                       note="per-node process wall %.0f s reached; the process was killed. "
                            "CAP IS NEVER A VERDICT: the node keeps its prior state." % a.wall,
                       level=j.get("level"), cls=j.get("cls"), eta_before=j.get("eta"),
                       lane="exact-core re-emission")
            stats["WALL_CAP"] += 1
        elif os.path.exists(resf):
            rec = json.load(open(resf))
            r = rec.get("result")
            if r == "PASS":
                stats["PASS"] += 1
            elif r == "NO-KILL":
                stats["NO_KILL"] += 1
            elif r == "ERROR":
                stats["ERROR"] += 1
            elif r and r.startswith("FAIL"):
                stats["FAIL"] += 1
            else:
                stats["other"] += 1
        else:
            rec = dict(id=j["id"], scope=j.get("scope"), result="NO-RESULT", rc=str(rc),
                       level=j.get("level"), cls=j.get("cls"), lane="exact-core re-emission")
            stats["other"] += 1
        rec["wall_total_s"] = round(time.time() - t0, 1)
        rec["worker"] = a.worker
        rec["attempt"] = "A149"
        rec["frac_exact"] = j.get("frac_exact")
        rec["when"] = time.strftime("%F %T")
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        stats["done"] += 1
        print("[%s] %s %s: %s tau=%s in %.1f s" % (a.worker, time.strftime("%H:%M:%S"), j["id"],
                                                   rec.get("result"), rec.get("tau"),
                                                   rec["wall_total_s"]), flush=True)
        flush()
        for f_ in (jobf, resf):
            if os.path.exists(f_):
                os.remove(f_)
    stats["finished"] = time.strftime("%F %T")
    flush()
    print("[%s] done %s" % (a.worker, json.dumps(stats)), flush=True)


if __name__ == "__main__":
    main()
