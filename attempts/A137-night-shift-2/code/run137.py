"""A137 -- the night's worker supervisor.

One process per node, with a hard **process** wall (default 1,500 s: A124's Y0381 diagnosis --
`LPModel` sets no LP time limit and `solve_node` only checks its own between iterations, so a
single `h.run()` can spin unbounded on one thread).  A node that hits the wall is recorded as
`WALL-CAP`, which is **not a verdict**: the node keeps its prior state and is simply not claimed.

Gates, checked before every node is launched:
  * this attempt's OWN pause sentinel (`attempts/A137-night-shift-2/PAUSE`, PAUSED.md v2 Sec.7a
    scoped-sentinel mechanism -- A57's own sentinel is reported at start and never touched);
  * free physical > `--min_free_phys_mb` (default 3072) and free commit > `--min_commit_mb`
    (default 6144);
  * a per-shard claim file, so two workers never take the same node.

BLAS is pinned to one thread per worker in the child's environment.
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
sys.path.insert(0, os.path.join(A57, "code"))
from pausegate import paused, reason                                       # noqa: E402


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=os.path.join(BASE, "results", "targets137.json"))
    ap.add_argument("--worker", default="w0")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out", default=None)
    ap.add_argument("--wall", type=float, default=1500.0, help="per-node PROCESS wall, seconds")
    ap.add_argument("--cap", type=float, default=420.0, help="LP time limit inside the node")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--min_free_phys_mb", type=float, default=3072.0)
    ap.add_argument("--min_commit_mb", type=float, default=6144.0)
    ap.add_argument("--deadline", default=None, help="local HH:MM after which no node is launched")
    a = ap.parse_args()

    out = a.out or os.path.join(BASE, "results", "exact_reemit.jsonl")
    claims = os.path.join(BASE, "progress", "claims")
    tmp = os.path.join(BASE, "progress", "tmp")
    os.makedirs(claims, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    prog = os.path.join(BASE, "progress", f"{a.worker}.json")

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
                 done=0, PASS=0, NO_KILL=0, FAIL=0, WALL_CAP=0, ERROR=0, other=0)

    def flush(cur=None):
        stats["updated"] = time.strftime("%F %T")
        stats["current"] = cur
        json.dump(stats, open(prog, "w"), indent=1)

    print(f"[{a.worker}] A57 sentinel: {paused()} ({reason()!r:.50}) -- reported, untouched; this "
          f"worker watches {os.path.join(BASE, 'PAUSE')}", flush=True)
    print(f"[{a.worker}] {len(T)} targets in shard {a.shard}, wall {a.wall} s, LP cap {a.cap} s",
          flush=True)
    flush()

    for j in T:
        if paused(base=BASE):
            print(f"[{a.worker}] A137 pause sentinel set ({reason(base=BASE)!r:.60}); "
                  f"stopping cleanly between nodes", flush=True)
            break
        if dl and time.time() > dl:
            print(f"[{a.worker}] launch deadline {a.deadline} passed; stopping cleanly", flush=True)
            break
        if j["id"] in done:
            continue
        cl = os.path.join(claims, j["id"] + ".claim")
        try:
            fd = os.open(cl, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, (a.worker + " " + str(int(time.time()))).encode())
            os.close(fd)
        except FileExistsError:
            continue
        pf, cf = phys_free_mb(), commit_free_mb()
        while pf < a.min_free_phys_mb or cf < a.min_commit_mb:
            print(f"[{a.worker}] memory gate: phys {pf:.0f} MB / commit {cf:.0f} MB "
                  f"(need {a.min_free_phys_mb:.0f}/{a.min_commit_mb:.0f}); holding 120 s",
                  flush=True)
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
        cmd = [sys.executable, os.path.join(HERE, "node137.py"), "--job", jobf, "--out", resf,
               "--cap", str(a.cap), "--rounds", str(a.rounds), "--jobs", str(a.jobs)]
        t0 = time.time()
        flush(j["id"])
        print(f"[{a.worker}] {time.strftime('%H:%M:%S')} START {j['id']} L{j['level']} "
              f"eta_before={j.get('eta')} phys={pf:.0f} MB", flush=True)
        logp = os.path.join(BASE, "logs", f"{a.worker}_nodes.log")
        with open(logp, "a", encoding="utf-8") as lg:
            lg.write(f"\n===== {j['id']} {time.strftime('%F %T')}\n")
            lg.flush()
            p = subprocess.Popen(cmd, stdout=lg, stderr=subprocess.STDOUT, env=child_env(),
                                 cwd=BASE)
            try:
                rc = p.wait(timeout=a.wall)
            except subprocess.TimeoutExpired:
                p.kill()
                try:
                    p.wait(timeout=60)
                except Exception:
                    pass
                rc = "WALL"
                lg.write(f"===== WALL-CAP {a.wall}s, process killed (NOT a verdict)\n")
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
            rec = dict(id=j["id"], scope=j.get("scope"), result="NO-RESULT",
                       rc=rc, level=j.get("level"), cls=j.get("cls"),
                       lane="exact-core re-emission")
            stats["other"] += 1
        rec["wall_total_s"] = round(time.time() - t0, 1)
        rec["worker"] = a.worker
        rec["when"] = time.strftime("%F %T")
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        stats["done"] += 1
        print(f"[{a.worker}] {time.strftime('%H:%M:%S')} {j['id']}: {rec.get('result')} "
              f"tau={rec.get('tau')} in {rec['wall_total_s']} s", flush=True)
        flush()
        for f_ in (jobf, resf):
            if os.path.exists(f_):
                os.remove(f_)
    stats["finished"] = time.strftime("%F %T")
    flush()
    print(f"[{a.worker}] done " + json.dumps(stats), flush=True)


if __name__ == "__main__":
    main()
