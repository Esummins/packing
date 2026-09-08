"""A137 -- the hourly board: rows by level, kills by leaf, wall-caps, memory holds, free physical.

Reads only tonight's own result files (no LP, no re-solve), so it is safe to run at any time.
"""
import collections
import ctypes
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))


class _M(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem():
    m = _M()
    m.dwLength = ctypes.sizeof(_M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2**20, m.ullAvailPageFile / 2**20


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def leaf_of(r):
    c = r.get("cert") or ""
    if c.startswith("KILL-BY-LOGIC"):
        lf = r.get("leaf") or ""
        if "pin-clip" in lf:
            return "T5''' pin-clip"
        if "polygon" in lf or "T5''''" in lf:
            return "T5'''' polygon"
        return "T5' logic"
    if c == "PASS":
        return "PASS (frozen cert)"
    if c.startswith("ALIVE"):
        return "ALIVE"
    if c.startswith("FAIL"):
        return "FAIL -> resolver"
    if c.startswith("CANARY"):
        return "CANARY"
    if c.startswith("UNSOUND"):
        return "parent box"
    return c[:28] or "?"


def main():
    print(f"=== A137 board {time.strftime('%F %T')}")
    ph, cm = mem()
    print(f"free physical {ph:.0f} MB   free commit {cm:.0f} MB")

    # ---- lane (a): exact-pin-core re-emission of the surviving ALIVE population
    A = collections.Counter()
    lvl = collections.Counter()
    kills = []
    for p in glob.glob(os.path.join(BASE, "results", "exact_reemit*.jsonl")):
        for r in jl(p):
            A[r.get("result")] += 1
            lvl[(r.get("level"), r.get("result"))] += 1
            if r.get("result") == "PASS":
                kills.append((r["id"], r.get("level"), r.get("tau"), r.get("tau_before")))
    n = sum(A.values())
    print(f"\n(a) exact-core re-emission: {n} nodes done  " + json.dumps(dict(A)))
    if n:
        dec = n - A.get("WALL-CAP", 0) - A.get("ERROR", 0) - A.get("NO-RESULT", 0)
        print(f"    kill rate {A.get('PASS', 0)}/{dec} decided = "
              f"{100.0 * A.get('PASS', 0) / max(1, dec):.1f} %")
    for k in kills:
        print(f"    KILL {k[0]} L{k[1]} tau {k[3]} -> {k[2]}")

    # ---- lane (b)/(c): emission through the hooks
    G = collections.Counter()
    GL = collections.Counter()
    for p in sorted(glob.glob(os.path.join(BASE, "results", "emit_geo_*.jsonl"))):
        for r in jl(p):
            G[leaf_of(r)] += 1
            GL[(1 + r["id"].count("_D"), leaf_of(r))] += 1
    L = collections.Counter()
    for p in sorted(glob.glob(os.path.join(BASE, "results", "emit_lp_*.jsonl"))):
        for r in jl(p):
            L[r.get("result")] += 1
            GL[(1 + r["id"].count("_D"), "LP:" + str(r.get("result")))] += 1
    q = 0
    for p in glob.glob(os.path.join(BASE, "results", "emitq_*.json")):
        q += len(json.load(open(p)))
    print(f"\n(b)/(c) emission through the hooks: {sum(G.values())} geometry verdicts, "
          f"{sum(L.values())} LP verdicts, {q} queued for LP")
    for k, v in sorted(G.items()):
        print(f"    {k:24s} {v}")
    for k, v in sorted(L.items(), key=lambda x: str(x[0])):
        print(f"    LP {str(k):21s} {v}")
    print("\n  by level:")
    for k in sorted(GL, key=lambda x: (x[0] or 0, str(x[1]))):
        print(f"    L{k[0]} {str(k[1]):26s} {GL[k]}")

    # ---- workers
    print("\nworkers:")
    for p in sorted(glob.glob(os.path.join(BASE, "progress", "*.json"))):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if "worker" not in d:
            continue
        print(f"    {d['worker']}: done {d.get('done')}  PASS {d.get('PASS')} "
              f"NO-KILL {d.get('NO_KILL')} FAIL {d.get('FAIL')} WALL-CAP {d.get('WALL_CAP')} "
              f"ERR {d.get('ERROR')} holds {d.get('mem_holds', 0)} :: {d.get('current')}")


if __name__ == "__main__":
    main()
