"""A92 -- the CROWD-WEIGHTED root certificate driver (chore_crowd_cert.md sec 5).

One run = one k0_00 ROOT node at s0 = 969271/250000, no pins, no cores, NO NO-families; the whole
hypothesis lives in the LP right-hand sides:  mu(Q) >= 1 + e * [Q in G]  with G an outer cover of
the crowd family F_c(a_w(delta)) at every corner c (crowdfam92).  Budget n = 11 + 8e.  The
certificate is the PAIR of frozen-verifier files of certify92.

Resource discipline: BLAS pinned to 1 thread (blas1 imported before numpy in every entry point),
at most one LP/certify at a time (the LP runs in THIS process, certify92 is the one subprocess),
and free COMMIT (MEMORYSTATUSEX.ullAvailPageFile) > 6144 MB checked before every LP and before
every certify launch, with a 60 s sleep-and-recheck loop.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import lpbox92
from caselp92 import Hyp, solve_node
import crowdfam92 as CF

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
NODES = os.path.join(RES, "nodes")
for d in (RES, LOGS, CERTS, NODES):
    os.makedirs(d, exist_ok=True)

S_RAT = "969271/250000"
S0F = float(Fr(S_RAT))
MIN_FREE_COMMIT_MB = 6144.0
LOGP = os.path.join(LOGS, "crowd92.log")
SINK = os.path.join(RES, "crowd92_runs.jsonl")

PHASE1_DELTAS = [0.3, 0.2, 0.1, 0.05]
E_ORDER = [Fr(1), Fr(1, 2), Fr(2), Fr(1, 4)]


def logline(*x):
    s = " ".join(str(v) for v in x)
    print(s, flush=True)
    with open(LOGP, "a") as f:
        f.write(time.strftime("[%H:%M:%S] ") + s + "\n")


def free_commit_mb():
    import ctypes

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


def wait_for_commit(tag, deadline=None, need=2):
    """poll free COMMIT every 60 s; proceed only after `need` CONSECUTIVE readings > 6144 MB."""
    n, ok = 0, 0
    while True:
        mb = free_commit_mb()
        if mb > MIN_FREE_COMMIT_MB:
            ok += 1
            if ok >= need:
                logline("  commit OK %.0f MB (%d consecutive) after %d x 60 s wait (%s)"
                        % (mb, ok, n, tag))
                return mb
        else:
            if ok:
                logline("  commit fell back to %.0f MB after %d good reading(s) (%s)" % (mb, ok, tag))
            ok = 0
        if deadline is not None and time.time() > deadline:
            logline("  commit STILL LOW %.0f MB, deadline passed -- SKIP %s" % (mb, tag))
            return None
        if n % 10 == 0:
            logline("  commit %.0f MB (need > %.0f x%d): sleep 60 s (%s)"
                    % (mb, MIN_FREE_COMMIT_MB, need, tag))
        time.sleep(60)
        n += 1


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if p and os.path.exists(p) else None


def _put(rec):
    with open(SINK, "a") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------- families (cached on disk)
FAMC = {}


def get_fam(delta):
    key = round(float(delta), 6)
    if key in FAMC:
        return FAMC[key]
    p = os.path.join(RES, "fam_d%g.json" % key)
    if os.path.exists(p):
        d = json.load(open(p))
        fam = CF.from_json(d)
        meta = dict(overshoot=d.get("overshoot"), canary=d.get("canary"), d4_defect=d.get("d4_defect"))
        logline("  fams reused %s: a_w=%s G/corner=%d E=%d overshoot=%.4f"
                % (p, str(fam["a"]), fam["n_g_per_corner"], fam["n_e"],
                   (meta["overshoot"] or {}).get("overshoot", float("nan"))))
    else:
        t0 = time.time()
        fam = CF.build(delta, log=logline)
        ov = CF.overshoot(fam, n=20000)
        can = CF.image_crowd_counts(fam["a"])
        d4 = CF.d4_closure_defect(fam)
        d = CF.to_json(fam)
        d.update(overshoot=ov, canary=can, d4_defect=d4, build_s=round(time.time() - t0, 1))
        json.dump(d, open(p, "w"))
        meta = dict(overshoot=ov, canary=can, d4_defect=d4)
        logline("  fams built delta=%g a_w=%s (%.6f) G/corner=%d E=%d overshoot=%.4f F-not-G=%d "
                "d4=%.1e realising=%d  %.0fs"
                % (delta, str(fam["a"]), float(fam["a"]), fam["n_g_per_corner"], fam["n_e"],
                   ov["overshoot"], ov["n_in_F_not_G"], d4,
                   sum(1 for r in can if r["realises"]), time.time() - t0))
    FAMC[key] = (fam, meta, p)
    return FAMC[key]


# ---------------------------------------------------------------- warm pool (A57 T4, as o3run)
WARM = {}


def warm_pool():
    if "w" in WARM:
        return WARM["w"]
    ATT = os.path.abspath(os.path.join(BASE, ".."))
    atoms, seen = [], set()

    def add(x, y):
        k = (round(x, 7), round(y, 7))
        if k not in seen and 0.0 <= x <= S0F and 0.0 <= y <= S0F:
            seen.add(k)
            atoms.append((x, y))
    p = os.path.join(ATT, "A38-root-power", "results", "certs_l1_sample", "root_s0_cert.json")
    if os.path.exists(p):
        d = json.load(open(p))
        for (a, b) in d["atoms"]:
            add(float(Fr(a)), float(Fr(b)))
    for nm in ("v2_s3.82_rowonly.json", "v2_s3.82.json", "v2_s3.83.json"):
        q = os.path.join(ATT, "A07-lp-dual", "results", nm)
        if not os.path.exists(q):
            continue
        try:
            d = json.load(open(q))
        except Exception:
            continue
        sc = S0F / float(d.get("s", S0F))
        for a in d.get("atoms", []):
            rep = a.get("rep") if isinstance(a, dict) else a
            if not rep:
                continue
            from lpbox92 import Sym
            for (x, y) in Sym("D4", float(d["s"])).point_images(rep[0], rep[1]):
                add(x * sc, y * sc)
    atoms = atoms[:1600]
    WARM["w"] = dict(atoms=atoms, rows=[])
    logline("  warm pool: %d columns (A38 root_s0 + A07 3.82/3.83, rescaled)" % len(atoms))
    return WARM["w"]


# ---------------------------------------------------------------- one node
def canary_ok(meta, tag):
    can = meta["canary"]
    real = [r["image"] for r in can if r["realises"]]
    return real


def run_lp(delta, e, lp_time, deadline, tag, fam=None, meta=None, famp=None, pattern="S(D2^4)"):
    if fam is None:
        fam, meta, famp = get_fam(delta)
    nA = int(11 + 8 * e)
    real = canary_ok(meta, tag)
    rec = dict(tag=tag, pattern=pattern, delta=float(delta), e=str(e), n=nA,
               a_w=str(fam["a"]), a_w_float=float(fam["a"]),
               n_G_boxes_per_corner=fam["n_g_per_corner"], n_E_boxes=fam["n_e"],
               overshoot=(meta["overshoot"] or {}).get("overshoot"),
               d4_defect=meta["d4_defect"],
               canary_realising=real,
               canary_counts=[{k: r[k] for k in ("image", "BL", "BR", "TL", "TR")} for r in meta["canary"]],
               tau=None, eta=None, minmass=None, maxcov=None, rows=None, lp_s=0.0,
               verdictA=None, verdictB=None, cert_s=0.0, sha256_A=None, sha256_B=None,
               verdict=None, ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    logline("[RUN] %s delta=%g e=%s n=%d a_w=%.6f G/corner=%d E=%d canary=%s"
            % (tag, delta, str(e), nA, float(fam["a"]), fam["n_g_per_corner"], fam["n_e"],
               real or "none"))
    if real:
        rec["verdict"] = "REFUSED (CANARY: realised by %s)" % ",".join(real)
        logline("  " + rec["verdict"])
        _put(rec)
        return rec, None, fam, famp
    node_path = os.path.join(NODES, tag + ".json")
    if os.path.exists(node_path):
        res = json.load(open(node_path))
        logline("  LP reused from %s" % node_path)
    else:
        if wait_for_commit(tag, deadline) is None:
            rec["verdict"] = "SKIPPED (commit headroom)"
            _put(rec)
            return rec, None, fam, famp
        rmax = CF.install_rhs(fam, e, lpbox92)
        t0 = time.time()
        logline("  [LP] sym=D4 tl=%.0fs rhs_max=%.4f" % (lp_time, rmax))
        res = solve_node(S0F, Hyp([], []), nA, sym_kind="D4", warm=warm_pool(),
                         time_limit=lp_time, max_iter=900, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
        res["child_id"] = tag
        res["e"] = str(e)
        res["delta"] = float(delta)
        json.dump(res, open(node_path, "w"))
        rec["lp_s"] = round(time.time() - t0, 1)
        CF.install_rhs(None, None, lpbox92)
    rec.update(tau=res["tau"], eta=res["tau"] - nA, converged=bool(res["converged"]),
               minmass=res["minmass"], maxcov=res["maxcov"], rows=res.get("n_rows"),
               atoms=len([x for x in res.get("atoms_all", []) if x[2] > 1e-10]))
    logline("  tau=%.6f eta=%.6f conv=%s minmass=%s maxcov=%s rows=%s lp_s=%.0f"
            % (rec["tau"], rec["eta"], rec["converged"], rec["minmass"], rec["maxcov"],
               rec["rows"], rec["lp_s"]))
    if res["tau"] >= nA:
        rec["verdict"] = "refused (tau %.6f >= n = %d)" % (res["tau"], nA)
    else:
        rec["verdict"] = "LP-PASS (tau < n; certificate not attempted yet)"
    _put(rec)
    return rec, node_path, fam, famp


def certify(tag, node_path, famp, e, cert_time, deadline, jobs=1, rounds=2, eps_geo=None):
    if wait_for_commit(tag + ":cert", deadline) is None:
        return "SKIPPED (commit headroom)", 0.0, None, None
    cmd = [sys.executable, os.path.join(HERE, "certify92.py"), node_path, "--s_rat", S_RAT,
           "--fam", famp, "--e", str(e), "--certdir", CERTS, "--tag", tag,
           "--rounds", str(rounds), "--jobs", str(jobs), "--depth", "56",
           "--time_limit", str(cert_time), "--scale", "0", "--scale_cap", "1.40000",
           "--max_w", "32", "--loop_cols"]
    if eps_geo is not None:
        cmd += ["--eps_geo", "%g" % eps_geo]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = round(time.time() - t0, 1)
    with open(os.path.join(LOGS, "cert_%s.log" % tag), "a") as f:
        f.write(p.stdout + "\n---stderr---\n" + p.stderr + "\n")
    for l in p.stdout.splitlines():
        if l.startswith(("[round", "    A|", "    B|", "CERTIFIED", "certificate", "NOT certified")):
            logline("    " + l.strip())
    outA = os.path.join(CERTS, "runA_%s.json" % tag)
    outB = os.path.join(CERTS, "runB_%s.json" % tag)
    verdict = "PASS" if p.returncode == 0 else "FAIL(rc=%d)" % p.returncode
    return verdict, dt, outA, outB


def _verdict_of(cert_json):
    try:
        d = json.load(open(cert_json))
        r = d["rounds"][-1]
        return ("PASS" if r["rcA"] == 0 else "FAIL"), ("PASS" if r["rcB"] == 0 else "FAIL")
    except Exception:
        return None, None


# ---------------------------------------------------------------- the campaign
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=360.0)
    ap.add_argument("--lp_time", type=float, default=900.0)
    ap.add_argument("--cert_time", type=float, default=300.0)
    ap.add_argument("--reserve_min", type=float, default=80.0,
                    help="minutes of the wall budget reserved for certification")
    ap.add_argument("--fams_only", action="store_true")
    ap.add_argument("--phase2", action="store_true")
    A = ap.parse_args()
    T_END = time.time() + 60 * A.minutes
    logline("=" * 100)
    logline("A92 crowd92 campaign start; wall budget %.0f min; s0 = %s" % (A.minutes, S_RAT))
    logline("OUT OF SCOPE (side > s0): the certified K0-BLOCKED packings of d2front87 at "
            "4.03-4.36 and s0115 at 3.985 are NOT checked against this certificate (it only "
            "speaks about side <= s0 = 3.877084).")

    # ---- families + canary FIRST, before any LP
    for d in PHASE1_DELTAS:
        fam, meta, famp = get_fam(d)
        real = [r["image"] for r in meta["canary"] if r["realises"]]
        logline("  CANARY delta=%g a_w=%.6f : per-image corner counts %s -> realising=%s"
                % (d, float(fam["a"]),
                   ";".join("%s[%d%d%d%d]" % (r["image"], r["BL"], r["BR"], r["TL"], r["TR"])
                            for r in meta["canary"]), real or "NONE"))
        if real:
            logline("REFUSED before any LP: images realise the crowd hypothesis at delta=%g" % d)
            sys.exit(1)
    if A.fams_only:
        return

    # ---- Phase 1: LP-only sweep.  The sweep stops early if it would eat the certification
    # reserve: a certified two-run PASS is the headline deliverable, an extra LP row is not.
    T_SWEEP = T_END - 60 * A.reserve_min
    passed = {}          # delta -> (e, tag, node_path, famp)
    for d in PHASE1_DELTAS:
        if time.time() > T_SWEEP:
            logline("LP sweep stops before delta=%g (certification reserve of %.0f min)"
                    % (d, A.reserve_min))
            break
        for e in E_ORDER:
            if time.time() > T_SWEEP:
                break
            tag = "S_d%g_e%s" % (d, str(e).replace("/", "o"))
            rec, node_path, fam, famp = run_lp(d, e, A.lp_time, T_SWEEP, tag)
            if node_path is not None and rec["tau"] is not None and rec["tau"] < rec["n"]:
                passed[d] = (e, tag, node_path, famp)
                logline("  delta=%g PASSES the LP at e=%s (eta=%.6f); skipping the remaining e"
                        % (d, str(e), rec["eta"]))
                break

    json.dump({str(k): [str(v[0]), v[1]] for k, v in passed.items()},
              open(os.path.join(RES, "phase1_passed.json"), "w"), indent=1)
    logline("Phase 1 LP sweep done: %d deltas pass -> %s"
            % (len(passed), ", ".join("%g@e=%s" % (k, str(v[0])) for k, v in sorted(passed.items()))))

    # ---- Phase 1 certification: largest delta first, then the smallest that passed
    order = []
    if passed:
        ds = sorted(passed, reverse=True)
        order = [ds[0]] + ([ds[-1]] if len(ds) > 1 else []) + ds[1:-1]
    n_pass = n_fail = 0
    for d in order:
        if time.time() > T_END:
            logline("wall budget gone before certifying delta=%g" % d)
            break
        if n_pass >= 2 and n_fail >= 1:
            logline("stopping certification after 2 PASSes + 1 FAIL")
            break
        e, tag, node_path, famp = passed[d]
        logline("[CERT] %s (delta=%g e=%s)" % (tag, d, str(e)))
        verdict, dt, outA, outB = certify(tag, node_path, famp, e, A.cert_time, T_END)
        vA, vB = _verdict_of(os.path.join(CERTS, "%s.certify.json" % tag))
        rec = dict(tag=tag, phase="cert", delta=d, e=str(e), n=int(11 + 8 * e),
                   verdict=verdict, verdictA=vA, verdictB=vB, cert_s=dt,
                   certA=outA, certB=outB, sha256_A=sha256(outA), sha256_B=sha256(outB),
                   ts=time.strftime("%Y-%m-%d %H:%M:%S"))
        if verdict == "PASS":
            open(os.path.join(CERTS, tag + ".PASS"), "w").write("ok")
            n_pass += 1
            fam, meta, _ = get_fam(d)
            if [r for r in meta["canary"] if r["realises"]]:
                logline("ENGINE BUG: PASS on an image-realisable node " + tag)
                sys.exit(9)
        else:
            n_fail += 1
            # A85 eps_geo repair
            for m in (0.002, 0.004):
                if time.time() > T_END:
                    break
                tag2 = "%s_epsgeo%g" % (tag, m)
                logline("[CERT] eps_geo repair %g -> %s" % (m, tag2))
                v2, dt2, oA, oB = certify(tag2, node_path, famp, e, A.cert_time, T_END, eps_geo=m)
                rec["cert_s"] += dt2
                if v2 == "PASS":
                    open(os.path.join(CERTS, tag2 + ".PASS"), "w").write("ok")
                    vA2, vB2 = _verdict_of(os.path.join(CERTS, "%s.certify.json" % tag2))
                    rec.update(verdict="PASS", verdictA=vA2, verdictB=vB2, eps_geo_used=m,
                               certA=oA, certB=oB, sha256_A=sha256(oA), sha256_B=sha256(oB))
                    n_pass += 1
                    n_fail -= 1
                    break
                rec["verdict"] = "FAIL(eps_geo %g)" % m
        logline("  verdict=%s (A=%s B=%s) cert_s=%.0f" % (rec["verdict"], rec["verdictA"],
                                                          rec["verdictB"], rec["cert_s"]))
        _put(rec)

    logline("campaign done; %.0f min left of the budget" % ((T_END - time.time()) / 60.0))


MARKER = os.path.join(RES, "CAMPAIGN_DONE")

if __name__ == "__main__":
    if os.path.exists(MARKER):
        os.remove(MARKER)
    status, err = "done", None
    t_start = time.time()
    try:
        main()
    except SystemExit as ex:
        status = "exit(%s)" % ex.code
    except BaseException as ex:
        import traceback
        status = "CRASH"
        err = traceback.format_exc()
        logline("CAMPAIGN CRASH\n" + err)
    finally:
        try:
            import report92
            report92.build()
            logline("report written: notes/crowd92_report.md")
        except BaseException:
            import traceback
            logline("report generation failed\n" + traceback.format_exc())
        with open(MARKER, "w") as f:
            json.dump(dict(status=status, error=err, minutes=round((time.time() - t_start) / 60.0, 1),
                           ts=time.strftime("%Y-%m-%d %H:%M:%S")), f, indent=1)
        logline("MARKER written: %s (status=%s)" % (MARKER, status))
