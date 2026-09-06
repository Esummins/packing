"""A99 R3(c): price the WINDOW for the k0_00 tree.

A85's kills are s0-ONLY.  A96 showed that an A57 leaf can be re-emitted as a
parametric-kill-certificate-v1 and discharged over the whole window [3.82, s0] in one run.
This does the same for A85's k0_00 certificates and measures

    param wall  vs  fixed-side wall  (the window factor),
    window coverage on a FAIL that ran to completion.

Emission is A96's `to_param96.convert` (unchanged); verification is the FROZEN
`verify_param.py` (byte-identical to A56's, code/frozen.sha256).  The k0_00 cell grid turns out
to lie in A96's (P-aff) family already: the A38/T(s0) column step is exactly (s0 - 2*c0)/16 with
c0 = 11/10, so every cell edge is e_q(s0) with q a dyadic multiple of 1/16 and 12q dyadic --
`core_affine` accepts it with no new anchoring rule and the exact reconstruction assert holds.
"""
import argparse, ctypes, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
VP = os.path.join(HERE, "verify_param.py")
RES = os.path.join(BASE, "results")
PARAM = os.path.join(BASE, "certs", "param")
A85 = os.path.join(ROOT, "attempts", "A85-k0-route")
A85C = os.path.join(A85, "certs", "k0_00")
SLO, SHI = "191/50", "969271/250000"
SLO_F, SHI_F = 3.82, 3.877084
sys.path.insert(0, HERE)
import to_param96


class _MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def commit_free_mb():
    try:
        m = _MS(); m.dwLength = ctypes.sizeof(_MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPageFile / 1048576.0
    except Exception:
        return 1e9


def gate(tag, floor=6144.0, nap=60.0, cap=3600.0):
    t0 = time.time(); n = 0
    f = commit_free_mb()
    while f < floor:
        if time.time() - t0 > cap:
            raise RuntimeError(f"commit gate never opened for {tag} ({f:.0f} MB)")
        n += 1
        print(f"  COMMIT-WAIT {tag}: {f:.0f} MB < {floor:.0f} MB, sleeping {nap:.0f}s (#{n})",
              flush=True)
        time.sleep(nap)
        f = commit_free_mb()
    return n, round(f, 1)


def covered_window(witfile, complete):
    if not complete or not os.path.exists(witfile):
        return None
    W = json.load(open(witfile))["witnesses"]
    iv = sorted([w["s_range_float"] for w in W if "s_range_float" in w])
    if not iv:
        return None
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1] + 1e-15:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    gaps, cur = [], SLO_F
    for a, b in merged:
        if a > cur:
            gaps.append([cur, min(a, SHI_F)])
        cur = max(cur, b)
    if cur < SHI_F:
        gaps.append([cur, SHI_F])
    width = sum(b - a for a, b in gaps)
    return dict(certified_subwindows=gaps, certified_width=width,
                window_width=SHI_F - SLO_F, certified_frac=width / (SHI_F - SLO_F),
                unproven=merged)


def a85_passes():
    """(tag, cert path, fixed-side certification wall from A85's own report)."""
    out = []
    for f in sorted(os.listdir(A85C)):
        if not f.endswith(".json") or f.endswith((".report.json", ".witnesses.json",
                                                  ".certify.json", ".resolve.json",
                                                  ".resolve1.json", ".resolve2.json")):
            continue
        rp = os.path.join(A85C, f.replace(".json", ".report.json"))
        if not os.path.exists(rp):
            continue
        try:
            R = json.load(open(rp))
        except Exception:
            continue
        if R.get("result") != "PASS":
            continue
        out.append(dict(tag=f[:-5], cert=os.path.join(A85C, f),
                        fixed_wall_s=round(R.get("time_s", 0.0), 2),
                        fixed_depth=R.get("depth"), fixed_jobs=R.get("jobs"),
                        atoms=R.get("atoms"), budget=None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--cap", type=float, default=1800.0)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--maxw", type=int, default=200)
    ap.add_argument("--out", default="r3c_param99.jsonl")
    a = ap.parse_args()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    os.makedirs(PARAM, exist_ok=True)
    outp = os.path.join(RES, a.out)
    done = set()
    if os.path.exists(outp):
        for ln in open(outp):
            try:
                done.add(json.loads(ln)["tag"])
            except Exception:
                pass
    S = [s for s in a85_passes() if s["tag"] not in done]
    print(f"{len(S)} A85 PASS certificate(s): {[s['tag'] for s in S]}", flush=True)
    for s in S:
        rec = dict(s)
        pj = os.path.join(PARAM, s["tag"] + ".param.json")
        try:
            d = to_param96.convert(s["cert"], pj)
            rec.update(emitted=True, param_atoms=len(d["atoms"]),
                       param_cores=len(d["hypotheses"]["cores"]), total=d["total"],
                       budget=d["budget"])
        except Exception as e:
            rec.update(emitted=False, error=repr(e)[:240], verdict="EMIT-ERROR",
                       param_wall_s=0.0, coverage=None, search_complete=False)
            with open(outp, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(f"  {s['tag']:44s} EMIT-ERROR {rec['error'][:110]}", flush=True)
            continue
        rp = os.path.join(PARAM, s["tag"] + ".report.json")
        wf = os.path.join(PARAM, s["tag"] + ".witnesses.json")
        w, mb = gate(s["tag"])
        cmd = [sys.executable, VP, pj, "--slo", SLO, "--shi", SHI, "--depth", str(a.depth),
               "--jobs", str(a.jobs), "--max-witnesses", str(a.maxw), "--strict-margin", "0",
               "--report", rp, "--witness-file", wf, "--quiet"]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=a.cap)
            rc, tail = p.returncode, (p.stdout + p.stderr)[-300:]
        except subprocess.TimeoutExpired:
            rc, tail = None, "TIMEOUT"
        rec["param_wall_s"] = round(time.time() - t0, 1)
        rec["commit_waits"], rec["commit_free_mb_at_launch"] = w, mb
        rec["verdict"] = {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, "TIMEOUT" if rc is None
                                                                    else f"rc={rc}")
        rec["search_complete"] = rc in (0, 1) and "stopped at" not in tail
        rec["tail"] = tail
        rec["coverage"] = (dict(certified_subwindows=[[SLO_F, SHI_F]],
                                certified_width=SHI_F - SLO_F, window_width=SHI_F - SLO_F,
                                certified_frac=1.0, unproven=[]) if rc == 0
                           else covered_window(wf, rec["search_complete"]))
        rec["window_factor_vs_fixed"] = (round(rec["param_wall_s"] / s["fixed_wall_s"], 3)
                                         if s["fixed_wall_s"] else None)
        with open(outp, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        cov = rec.get("coverage")
        print(f"  {s['tag']:44s} fixed={s['fixed_wall_s']:8.2f}s param={rec['param_wall_s']:8.1f}s "
              f"x{rec['window_factor_vs_fixed']} -> {rec['verdict']}"
              + (f" cover={cov['certified_frac']:.5f}" if cov else ""), flush=True)
    print("param99 done", flush=True)


if __name__ == "__main__":
    main()
