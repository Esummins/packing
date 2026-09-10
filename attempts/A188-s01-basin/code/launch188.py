"""A188 -- the slot gate and launcher.  Waits until the box has room, then runs ONE python job at
BelowNormal priority with affinity 0xFFFF (logical CPUs 0-15), killing the whole process TREE at
the wall.  Counts LAB python processes by CIM command line (relative command lines included; the
Claude-extension pythons are not lab jobs and are excluded) and refuses to start above the ceiling.

    python launch188.py --wall 2400 --tag tree_trump5 -- tree188.py --cls trump5 --time-cap 300

Gates (the brief): <= 10 other lab pythons (so this one keeps the box at <= 12 with A188's second),
> 3 GB free physical, commit charge headroom >= 6144 MB.
"""
from __future__ import annotations

import argparse, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.abspath(os.path.join(HERE, "..", "logs"))
os.makedirs(LOGS, exist_ok=True)
PS = ("$ps = Get-CimInstance Win32_Process -Filter \"Name='python.exe'\"; "
      "$n = 0; foreach ($p in $ps) { $c = [string]$p.CommandLine; if ($c -notmatch 'Claude Extensions') { $n++ } }; "
      "$os = Get-CimInstance Win32_OperatingSystem; "
      "Write-Output ($n.ToString() + ' ' + [int]($os.FreePhysicalMemory/1024) + ' ' + "
      "[int](($os.TotalVirtualMemorySize - $os.FreeVirtualMemory)/1024) + ' ' + [int]($os.TotalVirtualMemorySize/1024))")


def box_state():
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS], capture_output=True, text=True).stdout.split()
    n, free_mb, commit_used, commit_lim = (int(x) for x in out[:4])
    return n, free_mb, commit_lim - commit_used


def wait_for_slot(max_lab=10, min_free_mb=3072, min_commit_mb=6144, poll=60, log=None):
    while True:
        n, free_mb, commit_room = box_state()
        ok = n <= max_lab and free_mb > min_free_mb and commit_room > min_commit_mb
        msg = "%s lab pythons %d free %d MB commit room %d MB -> %s" % (
            time.strftime("%H:%M:%S"), n, free_mb, commit_room, "GO" if ok else "wait")
        print(msg, flush=True)
        if log:
            log.write(msg + "\n"); log.flush()
        if ok:
            return
        time.sleep(poll)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=2400.0)
    ap.add_argument("--tag", default="job")
    ap.add_argument("--max-lab", type=int, default=10)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = [c for c in a.cmd if c != "--"]
    log = open(os.path.join(LOGS, "%s.log" % a.tag), "a", encoding="utf-8")
    wait_for_slot(max_lab=a.max_lab, log=log)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1")
    BELOW_NORMAL = 0x00004000
    out = open(os.path.join(LOGS, "%s.out" % a.tag), "a", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u"] + cmd, cwd=HERE, env=env, stdout=out, stderr=subprocess.STDOUT,
                         creationflags=BELOW_NORMAL)
    try:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x0200 | 0x0400, False, p.pid)   # SET_INFORMATION | QUERY
        ctypes.windll.kernel32.SetProcessAffinityMask(h, 0xFFFF)
        ctypes.windll.kernel32.CloseHandle(h)
    except Exception as e:                                                      # noqa: BLE001
        log.write("affinity not set: %r\n" % (e,))
    log.write("%s started pid %d: %s\n" % (time.strftime("%H:%M:%S"), p.pid, " ".join(cmd))); log.flush()
    t0 = time.time()
    while p.poll() is None:
        if time.time() - t0 > a.wall:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
            log.write("%s WALL %.0fs: killed tree of pid %d\n" % (time.strftime("%H:%M:%S"), a.wall, p.pid))
            break
        time.sleep(5)
    log.write("%s exit %s after %.0fs\n" % (time.strftime("%H:%M:%S"), p.poll(), time.time() - t0)); log.flush()


if __name__ == "__main__":
    main()
