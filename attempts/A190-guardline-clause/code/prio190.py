"""A190 process discipline (A185's prio185 pattern): BelowNormal priority + affinity 0xFFFF (logical CPUs 0-15)
for this process (children inherit both), the box ceiling (12 lab pythons by image name, relative command lines
included; the Claude desktop's "Claude Extensions" / `windows-mcp` pythons are not lab workers and are excluded),
the memory gate (> 3 GB free physical, > 6144 MB available commit) and the <= 2 rule for this attempt's own
pythons.  PYTHONDONTWRITEBYTECODE is set for children."""
import ctypes
import os
import subprocess
import time

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
BELOW_NORMAL = 0x4000
MINE = ("A190", "run190", "regress190", "verify_case_v5", "fig190", "test190", "emit190")


def set_priority(mask=0xFFFF):
    try:
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, BELOW_NORMAL)
        k.SetProcessAffinityMask(h, ctypes.c_size_t(mask))
        return True
    except Exception:                                            # noqa: BLE001
        return False


class _MemStat(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem_gate(min_phys_mb=3072, min_commit_mb=6144):
    m = _MemStat()
    m.dwLength = ctypes.sizeof(_MemStat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    phys, commit = m.ullAvailPhys / 2 ** 20, m.ullAvailPageFile / 2 ** 20
    return (phys > min_phys_mb and commit > min_commit_mb), dict(avail_phys_mb=round(phys), avail_commit_mb=round(commit))


def _cmdlines():
    cmd = ["powershell", "-NoProfile", "-Command",
           "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ForEach-Object { $_.CommandLine }"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception:                                            # noqa: BLE001
        return None
    return [l for l in out.splitlines() if l.strip()]


def n_python():
    """lab pythons on the box (the Claude-extension pythons excluded)."""
    ls = _cmdlines()
    if ls is None:
        return 99
    return len([l for l in ls if "Claude Extensions" not in l and "windows-mcp" not in l])


def n_mine():
    ls = _cmdlines()
    if ls is None:
        return 99
    return len([l for l in ls if any(m in l for m in MINE)])


def wait_mine(limit=2, max_wait=3600, log=print):
    """the <= 2 rule: block until this attempt runs fewer than `limit` pythons (the caller is one of them)."""
    t0 = time.time()
    while n_mine() >= limit:
        if time.time() - t0 > max_wait:
            return False
        log("    A190 already runs %d pythons: waiting for the <= %d rule" % (n_mine(), limit))
        time.sleep(30)
    return True


def wait_box(ceiling=12, max_wait=1800, log=print, own=0):
    """wait until (lab pythons + own) <= ceiling and the memory gate holds."""
    t0 = time.time()
    while True:
        n = n_python()
        ok, mem = mem_gate()
        if n + own <= ceiling and ok:
            return True, dict(n_python=n, **mem)
        if time.time() - t0 > max_wait:
            return False, dict(n_python=n, **mem)
        log("    box busy (%d pythons + %d, %s): waiting" % (n, own, mem))
        time.sleep(60)


set_priority()
