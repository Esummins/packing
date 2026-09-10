"""A185 process discipline: BelowNormal priority + affinity 0xFFFF (logical CPUs 0-15) for this process
(children inherit both), the box ceiling (12 pythons by image name, relative command lines included; the
Claude desktop's `windows-mcp` venv pythons are not lab workers and are excluded) and the memory gate
(> 3 GB free physical, > 6144 MB available commit).  PYTHONDONTWRITEBYTECODE is set for children."""
import ctypes
import os
import subprocess
import time

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
BELOW_NORMAL = 0x4000


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


def n_python():
    """lab pythons on the box by IMAGE NAME (relative command lines included), minus the desktop MCP venvs."""
    cmd = ["powershell", "-NoProfile", "-Command",
           "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ForEach-Object { $_.CommandLine }"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception:                                            # noqa: BLE001
        return 99
    lines = [l for l in out.splitlines() if l.strip()]
    return len([l for l in lines if "Claude Extensions" not in l and "windows-mcp" not in l])


def n_mine():
    """this attempt's own pythons (regress185 / run185 / verify_case_v4 / fig185) by command line."""
    cmd = ["powershell", "-NoProfile", "-Command",
           "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ForEach-Object { $_.CommandLine }"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception:                                            # noqa: BLE001
        return 99
    return len([l for l in out.splitlines() if "185" in l and ("A185" in l or "regress185" in l or "run185" in l
                                                               or "verify_case_v4" in l or "fig185" in l)])


def wait_mine(limit=2, max_wait=3600, log=print):
    """the <= 2 rule: block until this attempt runs fewer than `limit` pythons (the caller is one of them)."""
    t0 = time.time()
    while n_mine() >= limit:
        if time.time() - t0 > max_wait:
            return False
        log("    A185 already runs %d pythons: waiting for the <= %d rule" % (n_mine(), limit))
        time.sleep(30)
    return True


def wait_box(ceiling=12, max_wait=1800, log=print, own=0):
    """wait until (lab pythons + own) < ceiling and the memory gate holds."""
    t0 = time.time()
    while True:
        n = n_python()
        ok, mem = mem_gate()
        if n + own < ceiling and ok:
            return True, dict(n_python=n, **mem)
        if time.time() - t0 > max_wait:
            return False, dict(n_python=n, **mem)
        log("    box busy (%d pythons + %d, %s): waiting" % (n, own, mem))
        time.sleep(60)


set_priority()
