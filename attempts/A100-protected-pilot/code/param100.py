"""A100 step 2: the PARAMETRIC pass for a protected class.

Same shape as A96's `param96.py` (attempts/A96-a57-parametric/code/param96.py), with one
difference: the node list is not A96's `selection96.json` (an A57 artefact) but this attempt's
own cover/ladder/deepen ledgers, i.e. every leaf the A84 P-TREE engine certified at s0.

Each such leaf is
  * re-emitted as a `parametric-kill-certificate-v1` by the UNMODIFIED A96 emitter
    (`to_param96.convert`, byte-identical copy), and
  * verified over the whole window W = [191/50, 969271/250000] by the FROZEN 4-D verifier
    (`verify_param.py`, sha256 0c58485c... == A96 code/frozen.sha256).

A PASS discharges the leaf for every side in W at once.  A completed FAIL still discharges every
4-D cell no witness touched; `resolve100.py` then re-runs the same certificate on the exact
uncovered sub-windows (A96's resolver).

Resource discipline is A96's: BLAS pinned to one thread in the child env, at most --procs
verifier subprocesses, the 6144 MB commit gate before each launch, append-only resumable log.
"""
import argparse, ctypes, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
VP = os.path.join(HERE, "verify_param.py")            # frozen copy
OUT = os.path.join(BASE, "results")
PARAM = os.path.join(BASE, "certs", "param")
SLO, SHI = "191/50", "969271/250000"
SLO_F, SHI_F = 3.82, 3.877084
sys.path.insert(0, HERE)
import to_param96


class _MEMSTAT(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def commit_free_mb():
    try:
        m = _MEMSTAT()
        m.dwLength = ctypes.sizeof(_MEMSTAT)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPageFile / (1024.0 * 1024.0)
    except Exception:
        return 1e9


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


def selection(cls):
    """every s0 leaf this attempt certified: verdict PASS in a cover/ladder/deepen ledger, with
    the certificate file on disk.  `cert_path` is set by pilot59.run_child / run_eps_geo."""
    sel, seen = [], set()
    for src in sorted(glob.glob(os.path.join(OUT, "a84_%s_*.jsonl" % cls))):
        base = os.path.basename(src)
        if "waits" in base or "deferred" in base:
            continue
        phase = base.split("_")[2] if len(base.split("_")) > 2 else "?"
        for ln in open(src):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("verdict") != "PASS":
                continue
            cp = r.get("cert_path")
            if not cp:
                cp = os.path.join(BASE, "certs", cls, r["tag"] + ".json")
            if not os.path.isabs(cp):
                cp = os.path.join(BASE, cp)
            if not os.path.exists(cp) or r["tag"] in seen:
                continue
            seen.add(r["tag"])
            sel.append(dict(id=r["tag"], cls=cls, phase=phase, cert_file=cp,
                            level=r.get("level", 0), budget=r.get("budget"),
                            atoms=r.get("atoms"), tau=r.get("tau"), eta=r.get("eta"),
                            eps_geo_used=r.get("eps_geo_used"),
                            lp_s=r.get("lp_s"), cert_s=r.get("cert_s"),
                            fixed_wall_s=round((r.get("lp_s") or 0.0) + (r.get("cert_s") or 0.0), 1)))
    sel.sort(key=lambda s: s["id"])
    return sel


def finish(job, res_path):
    s, rec, t0, rp, wf, cap = job["sel"], job["rec"], job["t0"], job["rp"], job["wf"], job["cap"]
    p = job["p"]
    rc = p.returncode
    rec["param_wall_s"] = round(time.time() - t0, 1)
    rec["timeout_cap_s"] = cap
    if job.get("timed_out"):
        rec.update(verdict="TIMEOUT", coverage=None, search_complete=False)
    else:
        rec["verdict"] = {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, "rc=%s" % rc)
        if os.path.exists(rp):
            r = json.load(open(rp))
            rec["boxes"] = r["stats"]["boxes"]
            rec["s_cells"] = r["stats"].get("s_cells")
            rec["witnesses"] = r["stats"].get("witnesses")
            rec["witness_s_range"] = r.get("witness_s_range")
            complete = rc == 0 or (r["stats"].get("witnesses", 0) < job["maxwit"])
            rec["search_complete"] = bool(complete)
            rec["coverage"] = (dict(certified_subwindows=[[SLO_F, SHI_F]],
                                    certified_width=SHI_F - SLO_F, window_width=SHI_F - SLO_F,
                                    certified_frac=1.0, unproven=[]) if rc == 0
                               else covered_window(wf, complete))
    with open(res_path, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    cov = rec.get("coverage")
    print("%-8s %-22s budget=%s fixed=%8.1fs param=%8.1fs -> %-8s%s"
          % (s["cls"], s["id"], s["budget"], s["fixed_wall_s"], rec["param_wall_s"],
             rec["verdict"], (" cover=%.5f" % cov["certified_frac"]) if cov else ""), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True, help="comma list of classes")
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--node-cap", type=float, default=1500.0)
    ap.add_argument("--global-cap", type=float, default=1e9)
    ap.add_argument("--commit-gate", type=float, default=6144.0)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--max-witnesses", type=int, default=2000)
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    sel = []
    for c in a.cls.split(","):
        if c:
            sel += selection(c)
    if a.limit:
        sel = sel[:a.limit]
    res_path = a.out if a.out else os.path.join(OUT, "param100.jsonl")
    if a.out and not os.path.isabs(res_path):
        res_path = os.path.join(BASE, res_path)
    done = set()
    if os.path.exists(res_path):
        for ln in open(res_path):
            try:
                r = json.loads(ln)
                done.add((r["cls"], r["id"]))
            except Exception:
                pass
    todo = [s for s in sel if (s["cls"], s["id"]) not in done]
    print("selection=%d done=%d todo=%d procs=%d" % (len(sel), len(done), len(todo), a.procs),
          flush=True)

    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    running, i, t_all = [], 0, time.time()
    while (i < len(todo) or running) and time.time() - t_all < a.global_cap:
        for job in list(running):
            if job["p"].poll() is None:
                if time.time() - job["t0"] > job["cap"]:
                    job["p"].kill()
                    job["p"].wait()
                    job["timed_out"] = True
                else:
                    continue
            running.remove(job)
            finish(job, res_path)
        while (len(running) < a.procs and i < len(todo)
               and time.time() - t_all < a.global_cap):
            if commit_free_mb() < a.commit_gate:
                print("commit %.0f MB < %.0f: holding (running=%d)"
                      % (commit_free_mb(), a.commit_gate, len(running)), flush=True)
                break
            s = todo[i]; i += 1
            od = os.path.join(PARAM, s["cls"])
            os.makedirs(od, exist_ok=True)
            pj = os.path.join(od, s["id"] + ".param.json")
            rec = {k: s[k] for k in ("id", "cls", "phase", "level", "budget", "atoms", "tau",
                                     "eta", "eps_geo_used", "lp_s", "cert_s", "fixed_wall_s")}
            rec["src_cert"] = s["cert_file"]
            try:
                d = to_param96.convert(s["cert_file"], pj)
                rec["param_atoms"] = len(d["atoms"])
                rec["param_cores"] = len(d["hypotheses"]["cores"])
            except Exception as e:
                rec.update(verdict="EMIT-ERROR", error=repr(e)[:200], param_wall_s=0.0,
                           coverage=None, search_complete=False)
                with open(res_path, "a") as fh:
                    fh.write(json.dumps(rec) + "\n")
                print("EMIT-ERROR %s %s: %s" % (s["cls"], s["id"], repr(e)[:120]), flush=True)
                continue
            rp = os.path.join(od, s["id"] + ".report.json")
            wf = os.path.join(od, s["id"] + ".witnesses.json")
            cmd = [sys.executable, VP, pj, "--slo", SLO, "--shi", SHI, "--depth", str(a.depth),
                   "--jobs", "1", "--strict-margin", "0", "--report", rp, "--witness-file", wf,
                   "--max-witnesses", str(a.max_witnesses), "--max-witnesses-per-box", "1",
                   "--quiet"]
            p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 env=env, cwd=BASE)
            running.append(dict(p=p, sel=s, rec=rec, t0=time.time(), rp=rp, wf=wf,
                                cap=a.node_cap, maxwit=a.max_witnesses))
        time.sleep(2.0)
    for job in list(running):
        try:
            job["p"].wait(timeout=max(0.0, job["cap"] - (time.time() - job["t0"])))
        except subprocess.TimeoutExpired:
            job["p"].kill(); job["p"].wait(); job["timed_out"] = True
        finish(job, res_path)
    print("A100 parametric pass: batch done", flush=True)


if __name__ == "__main__":
    main()
