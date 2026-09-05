"""A96 step 2: the parametric pass -- every A57 candidate node re-emitted as a
parametric-kill-certificate-v1 and verified over the WHOLE window [191/50, s0] by the FROZEN
4-D verifier (code/verify_param.py, byte-identical copy of A56's; see code/frozen.sha256).

A PASS discharges the node for every s in the window at once, replacing the four fixed-side runs.
A FAIL that ran to completion still discharges every 4-D cell no witness touched, so the covered
sub-window is W minus the union of the witness s-ranges; that claim is VOID if the run hit the
time cap or the witness cap, and is recorded as such (search_complete).

Resource discipline:
  * BLAS pinned to 1 thread in the child environment (the verifier is exact-integer work; numpy
    is only a shortlister, but OpenBLAS would still spawn ~20 threads per process).
  * At most --procs (default 2) verifier subprocesses at a time.  The parent only waits.
  * Commit gate: no new subprocess unless available commit >= --commit-gate MB (default 6144),
    the same gate A57's scaler uses.  This is a self-gating launcher: it blocks itself instead of
    being polled from outside.
  * Resumable: results/param96.jsonl is append-only and keyed by (cls, id).
"""
import argparse, ctypes, json, os, subprocess, sys, time

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


def _memstat():
    m = _MEMSTAT()
    m.dwLength = ctypes.sizeof(_MEMSTAT)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m


def commit_free_mb():
    """Available COMMIT (RAM + pagefile), in MB."""
    try:
        return _memstat().ullAvailPageFile / (1024.0 * 1024.0)
    except Exception:
        return 1e9      # non-Windows / no ctypes: do not gate


def phys_free_mb():
    """Available PHYSICAL memory, in MB.  After the pagefile raise the commit gate went slack and
    RAM became the binding constraint, so this is the gate that now actually fires."""
    try:
        return _memstat().ullAvailPhys / (1024.0 * 1024.0)
    except Exception:
        return 1e9


def covered_window(witfile, complete):
    """W minus the union of the witness s-ranges.  Meaningful only on a completed search."""
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


def finish(job, res_path):
    s, rec, t0, rp, wf, cap = job["sel"], job["rec"], job["t0"], job["rp"], job["wf"], job["cap"]
    p = job["p"]
    rc = p.returncode
    rec["param_wall_s"] = round(time.time() - t0, 1)
    rec["timeout_cap_s"] = cap
    if job.get("timed_out"):
        rec.update(verdict="TIMEOUT", coverage=None, search_complete=False)
    else:
        rec["verdict"] = {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, f"rc={rc}")
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
    rec["ratio_vs_4_fixed_sides"] = (round(rec["param_wall_s"] / (4 * s["fixed_wall_s"]), 4)
                                     if s["fixed_wall_s"] else None)
    with open(res_path, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    cov = rec.get("coverage")
    print(f"{s['group']:7s} {s['cls']:9s} {s['id']:26s} atoms={s['atoms']:4d} "
          f"fixed={s['fixed_wall_s']:8.1f}s param={rec['param_wall_s']:8.1f}s -> {rec['verdict']:8s}"
          + (f" cover={cov['certified_frac']:.5f}" if cov else ""), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--node-cap", type=float, default=1500.0)
    # A TIMEOUT is worth NOTHING: it writes no witness file, so there is no partial coverage and
    # nothing for resolve96 to close.  A completed FAIL yields 0.988-0.999 coverage plus witness
    # cells that resolve in seconds.  So the tail is fixed by RAISING the cap on the few expensive
    # (high-atom) children, never by lowering it.  One 88-atom child was 23.4% of the whole
    # level-2 verify wall purely because it hit the cap.
    ap.add_argument("--node-cap-high", type=float, default=0.0,
                    help="cap for nodes with >= --atoms-high atoms (0 = same as --node-cap)")
    ap.add_argument("--atoms-high", type=int, default=32)
    ap.add_argument("--min-free-phys-mb", type=float, default=0.0,
                    help="hold off launching while free PHYSICAL memory is below this (0 = off). "
                         "After the pagefile raise the commit gate is slack and RAM is the "
                         "binding constraint.")
    ap.add_argument("--global-cap", type=float, default=1e9)
    ap.add_argument("--commit-gate", type=float, default=6144.0, help="MB of free commit")
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--max-witnesses", type=int, default=2000)
    ap.add_argument("--groups", default="", help="comma list; default = all, in selection order")
    ap.add_argument("--tag", default="", help="restrict to one A57 tag (G1 / L1)")
    ap.add_argument("--level", type=int, default=0, help="restrict to one tree level")
    ap.add_argument("--out", default="", help="results file; default results/param96.jsonl. Use a "
                    "separate file when running a second instance alongside the main pass, so the "
                    "two do not interleave in one append-only log or redo each other's nodes.")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    sel = json.load(open(os.path.join(OUT, "selection96.json")))["selection"]
    if a.groups:
        want = set(a.groups.split(","))
        sel = [s for s in sel if s["group"] in want]
    if a.tag:
        sel = [s for s in sel if s["tag"] == a.tag]
    if a.level:
        sel = [s for s in sel if s["level"] == a.level]
    if a.limit:
        sel = sel[:a.limit]
    res_path = a.out if a.out else os.path.join(OUT, "param96.jsonl")
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
    print(f"selection={len(sel)} done={len(done)} todo={len(todo)} procs={a.procs}", flush=True)

    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    running, i, t_all = [], 0, time.time()
    while (i < len(todo) or running) and time.time() - t_all < a.global_cap:
        # reap
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
        # launch
        while (len(running) < a.procs and i < len(todo)
               and time.time() - t_all < a.global_cap):
            if commit_free_mb() < a.commit_gate:
                print(f"commit {commit_free_mb():.0f} MB < {a.commit_gate:.0f}: holding "
                      f"(running={len(running)})", flush=True)
                break
            if a.min_free_phys_mb and phys_free_mb() < a.min_free_phys_mb:
                print(f"free physical {phys_free_mb():.0f} MB < {a.min_free_phys_mb:.0f}: holding "
                      f"(running={len(running)})", flush=True)
                break
            s = todo[i]; i += 1
            od = os.path.join(PARAM, s["cls"])
            os.makedirs(od, exist_ok=True)
            pj = os.path.join(od, s["id"] + ".param.json")
            rec = {k: s[k] for k in ("id", "cls", "name", "tag", "level", "group", "cert",
                                     "atoms", "eta", "eps_geo_used", "fixed_wall_s",
                                     "lp_seconds", "cert_seconds", "epsgeo_seconds")}
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
                print(f"EMIT-ERROR {s['cls']} {s['id']}: {repr(e)[:120]}", flush=True)
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
                                cap=(a.node_cap_high if (a.node_cap_high and
                                                         s["atoms"] >= a.atoms_high)
                                     else a.node_cap),
                                maxwit=a.max_witnesses))
        time.sleep(2.0)
    for job in list(running):          # global cap hit: let the in-flight ones finish cleanly
        try:
            job["p"].wait(timeout=max(0.0, job["cap"] - (time.time() - job["t0"])))
        except subprocess.TimeoutExpired:
            job["p"].kill(); job["p"].wait(); job["timed_out"] = True
        finish(job, res_path)
    print("A96 parametric pass: batch done", flush=True)


if __name__ == "__main__":
    main()
