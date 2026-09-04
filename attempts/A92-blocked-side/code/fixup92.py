"""A92 follow-up driver: re-certify a node with the REBUILT (overlapping-strip) complement cover.

Same resource discipline as crowd92.py: BLAS pinned, at most ONE certify92/verify_case subprocess
at a time, free COMMIT gate of two consecutive readings > 6144 MB, 60 s apart.
"""
import argparse, ctypes, hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
LOGS = os.path.join(BASE, "logs")
S_RAT = "969271/250000"
MIN_FREE_COMMIT_MB = 6144


def free_commit_mb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 1048576.0


def gate(tag, deadline, need=2):
    ok = n = 0
    while True:
        mb = free_commit_mb()
        if mb > MIN_FREE_COMMIT_MB:
            ok += 1
            if ok >= need:
                print("  commit OK %.0f MB (%d consecutive, %d waits) [%s]" % (mb, ok, n, tag),
                      flush=True)
                return mb
        else:
            ok = 0
            print("  commit LOW %.0f MB [%s]" % (mb, tag), flush=True)
        if deadline and time.time() > deadline:
            return None
        n += 1
        time.sleep(60)


def sha16(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    except OSError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)          # e.g. S_d0.3_e1
    ap.add_argument("--delta", type=float, required=True)
    ap.add_argument("--e", default="1")
    ap.add_argument("--eps_geo", type=float, default=0.004)
    ap.add_argument("--resolve_time", type=float, default=1500)
    ap.add_argument("--time_limit", type=float, default=600)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--max_w", type=int, default=128)
    ap.add_argument("--minutes", type=float, default=60)
    a = ap.parse_args()

    T_END = time.time() + a.minutes * 60
    node = os.path.join(RES, "nodes", "%s.json" % a.tag)
    famp = os.path.join(RES, "fam_d%g.json" % round(a.delta, 6))
    ctag = "%s_fix_epsgeo%g" % (a.tag, a.eps_geo)
    if gate(ctag, T_END) is None:
        print("STOPPED: commit headroom")
        return 4
    cmd = [sys.executable, os.path.join(HERE, "certify92.py"), node, "--s_rat", S_RAT,
           "--fam", famp, "--e", a.e, "--certdir", CERTS, "--tag", ctag,
           "--rounds", str(a.rounds), "--jobs", "1", "--depth", "56",
           "--time_limit", str(a.time_limit), "--resolve_time", str(a.resolve_time),
           "--scale", "0", "--scale_cap", "1.40000", "--max_w", str(a.max_w),
           "--loop_cols", "--eps_geo", "%g" % a.eps_geo]
    print("RUN " + " ".join(cmd), flush=True)
    t0 = time.time()
    logp = os.path.join(LOGS, "cert_%s.log" % ctag)
    with open(logp, "a", buffering=1) as f:      # stream, so the run is watchable live
        f.write("\n==== %s ====\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
        p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
    dt = round(time.time() - t0, 1)
    out = open(logp, encoding="utf-8", errors="replace").read()
    out = out[out.rfind("==== "):]
    outA = os.path.join(CERTS, "runA_%s.json" % ctag)
    outB = os.path.join(CERTS, "runB_%s.json" % ctag)

    def verdict(rep):
        try:
            d = json.load(open(rep))
            return "PASS" if d.get("ok") or d.get("result") == "PASS" else "FAIL"
        except Exception:
            return "?"

    vA = vB = "?"
    holes = None
    for l in out.splitlines():
        if l.startswith("    A| PASS"):
            vA = "PASS"
        elif l.startswith("    A| FAIL"):
            vA = "FAIL"
        elif l.startswith("    B| PASS"):
            vB = "PASS"
        elif l.startswith("    B| FAIL"):
            vB = "FAIL"
            try:
                holes = int(l.split(":")[1].split("witness")[0])
            except Exception:
                pass
    ok = (p.returncode == 0)
    rec = dict(kind="certify_fix", tag=ctag, base_tag=a.tag, delta=a.delta, e=a.e,
               eps_geo=a.eps_geo, resolve_time=a.resolve_time, time_limit=a.time_limit,
               rounds=a.rounds, max_w=a.max_w, fam=os.path.basename(famp), fam_build=2,
               verdict=("PASS" if ok else "FAIL(rc=%d)" % p.returncode),
               verdictA=vA, verdictB=vB, holesB=holes, cert_s=dt,
               shaA=sha16(outA), shaB=sha16(outB),
               note="complement cover E rebuilt with the one-cell y-overlap (fam_build=2)",
               t=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(os.path.join(RES, "crowd92_runs.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    if ok:
        with open(os.path.join(CERTS, "%s.PASS" % ctag), "w") as f:
            f.write("two-run PASS %s\nrunA %s sha256-16 %s\nrunB %s sha256-16 %s\n%s\n"
                    % (ctag, outA, sha16(outA), outB, sha16(outB), rec["t"]))
    print("VERDICT %s A=%s B=%s cert_s=%.0f" % (rec["verdict"], vA, vB, dt), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
