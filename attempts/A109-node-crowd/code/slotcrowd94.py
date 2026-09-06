"""A94 -- the SLOT-CROWD certificate campaign driver (`notes/chore_slot_cert.md` sec 4, 6, 7).

One run = one node of a PINNED class S (k5_11 / k5_16) at the side s of a window (s, m_lo):
  * hypothesis  Hyp(boxes = the k pin Boxes of half-width h = rho/sqrt2, nofams = []),
  * budget      N + 2 m_u e  (n = 11 + 2 m_u e, an integer),
  * right-hand sides  rhs(Q) = 1 + e * r_G(Q),  r_G = #{usable slots p whose dilated outer cover
    G_p contains Q},   sym_kind = "C1"  (a pinned class is NOT D4-symmetric).
The certificate is the 1 + r_max frozen-verifier files of certify94.

Resource discipline: BLAS pinned to 1 thread (blas1 imported before numpy in every entry point),
at most one LP/certify at a time (the LP runs in THIS process, certify94 is the one subprocess),
and free COMMIT (MEMORYSTATUSEX.ullAvailPageFile) > 6144 MB on TWO CONSECUTIVE 60 s readings
before every LP and before every certify launch.  VERIFY_JOBS_CAP = 1.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import lpbox94
from caselp94 import Hyp, Box, solve_node, warm_from_result
import slotfam94 as SF
import canary94 as CAN

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
NODES = os.path.join(RES, "nodes")
FAMS = os.path.join(RES, "fams")
for d in (RES, LOGS, CERTS, NODES, FAMS):
    os.makedirs(d, exist_ok=True)

MIN_FREE_COMMIT_MB = 6144.0
VERIFY_JOBS_CAP = 1
LOGP = os.path.join(LOGS, "slotcrowd94.log")
SINK = os.path.join(RES, "slotcrowd94_runs.jsonl")
MARKER = os.path.join(RES, "CAMPAIGN_DONE")

E_ORDER = [Fr(1, 2), Fr(1, 4), Fr(1), Fr(1, 8)]
CLS = ("k5_11", "k5_16")
PLAN = [                                   # (phase, class, window, deltas) -- chore sec 7
    ("P1", "k5_11", "s0_G2", [0.05, 0.02, 0.03, 0.10, 0.20, 0.30]),
    ("P1", "k5_16", "s0_G2", [0.05, 0.02, 0.03, 0.10, 0.20, 0.30]),
    ("P4", "k5_11", "G4_lo", [0.04, 0.02, 0.10]),
    ("P4", "k5_16", "G4_lo", [0.04, 0.02, 0.10]),
    ("P6", "k5_11", "s0_lo", [0.05, 0.10]),
    ("P6", "k5_16", "s0_lo", [0.05, 0.10]),
    ("P7", "k5_11", "G3_G4", [0.025, 0.02]),
    ("P7", "k5_16", "G3_G4", [0.025, 0.02]),
    ("P7", "k5_11", "G2_G3", [0.014, 0.012]),
    ("P7", "k5_16", "G2_G3", [0.014, 0.012]),
]
REGRESSION_TARGET = {"k5_11": 5.9064, "k5_16": 5.9731}
REG_TOL = 0.05


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
    refresh_report()


def refresh_report():
    """rewrite notes/slotcrowd94_report.md after every record, so that a hard kill (which never
    reaches the finally block) still leaves a current report on disk."""
    try:
        import report94
        report94.build()
    except BaseException:
        pass


# ---------------------------------------------------------------- families (cached on disk)
FAMC = {}


def fam_path(cls, win, delta):
    return os.path.join(FAMS, "fam_%s_%s_d%g.json" % (cls, win, delta))


def get_fam(cls, win, delta):
    key = (cls, win, round(float(delta), 6))
    if key in FAMC:
        return FAMC[key]
    p = fam_path(cls, win, delta)
    if os.path.exists(p):
        d = json.load(open(p))
        if d.get("skip"):
            FAMC[key] = (d, p)
            return FAMC[key]
        fam = SF.from_json(d)
        logline("  fams reused %s: a_w=%s rho=%s E=%s"
                % (os.path.basename(p), d["a_w"], d["rho"], {r: len(v) for r, v in fam["E"].items()}))
    else:
        t0 = time.time()
        fam = SF.build(cls, win, delta, log=logline)
        if fam.get("skip"):
            json.dump(fam, open(p, "w"))
            logline("  fams SKIP %s %s delta=%g: %s (a_w=%s)"
                    % (cls, win, delta, fam["skip"], fam["a_w"]))
            FAMC[key] = (fam, p)
            return FAMC[key]
        SF.check_cores(fam, log=logline)
        SF.build_all_E(fam, log=logline)
        fam["overshoot"] = SF.overshoot(fam, n=3000)
        d = SF.to_json(fam)
        d["build_s"] = round(time.time() - t0, 1)
        json.dump(d, open(p, "w"))
        logline("  fams built %s %s delta=%g in %.0fs; overshoot=%s"
                % (cls, win, delta, time.time() - t0,
                   [(o["slot"], None if o["overshoot"] is None else round(o["overshoot"], 4))
                    for o in fam["overshoot"]]))
    FAMC[key] = (fam, p)
    return FAMC[key]


# ---------------------------------------------------------------- warm pool
WARM = {}


def warm_pool(cls, s, max_atoms=2500, max_rows=6000):
    key = (cls, round(float(s), 9))
    if key in WARM:
        return WARM[key]
    sc = float(s) / float(SF.S0)
    atoms, seen, rows = [], set(), []
    srcs = []
    for att, nm in (("A54-stragglers", cls + ".json"), ("A54-stragglers", cls + "_state.json"),
                    ("A53-simple-strata", cls + ".json")):
        p = os.path.join(ATT, att, "results", "nodes", nm)
        if os.path.exists(p):
            srcs.append(p)
    # previously solved A94 nodes of the SAME class (any window/delta) -- the strongest warm start
    for f in sorted(os.listdir(NODES)):
        if f.startswith(cls + "_") and f.endswith(".json"):
            srcs.append(os.path.join(NODES, f))
    for p in srcs:
        try:
            d = json.load(open(p))
        except Exception:
            continue
        s_src = float(d.get("s", float(SF.S0)))
        r = float(s) / s_src
        for a in d.get("atoms_all", []):
            x, y = a[0] * r, a[1] * r
            k = (round(x, 7), round(y, 7))
            if k not in seen and 0.0 <= x <= float(s) and 0.0 <= y <= float(s):
                seen.add(k)
                atoms.append((x, y))
        for w in d.get("rows_all", [])[:20000]:
            rows.append((w[0] * r, w[1] * r, w[2]))
        if len(atoms) >= max_atoms:
            break
    atoms = atoms[:max_atoms]
    rows = rows[:max_rows]
    WARM[key] = dict(atoms=atoms, rows=rows)
    logline("  warm pool %s @ s=%.6f: %d columns, %d rows from %d source(s)"
            % (cls, float(s), len(atoms), len(rows), len(srcs)))
    return WARM[key]


# ---------------------------------------------------------------- one LP node
def run_lp(phase, cls, win, delta, e, lp_time, deadline, gate=True, probe_time=300.0):
    fam, famp = get_fam(cls, win, delta)
    tag = "%s_%s_d%g_e%s" % (cls, win, delta, str(e).replace("/", "o"))
    C = SF.CLASSES[cls]
    s, m_lo = SF.WINDOWS[win]
    base = dict(tag=tag, phase=phase, cls=cls, window=win, s=str(s), m_lo=str(m_lo),
                delta=float(delta), e=str(e), k=C["k"], N=C["N"], m_u=C["m_u"],
                slots=["%s(%d,%d)" % c for c in C["slots"]],
                slot_ext=C["slot_ext"], ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    if isinstance(fam, dict) and fam.get("skip"):
        base.update(verdict="SKIPPED (%s)" % fam["skip"], a_w=fam["a_w"], lam=fam.get("lam"),
                    rho=fam.get("rho"))
        logline("[RUN] %s SKIPPED: %s a_w=%s" % (tag, fam["skip"], fam["a_w"]))
        _put(base)
        return base, None, None
    nA = 11 + 2 * C["m_u"] * e
    assert nA.denominator == 1
    nA = int(nA)
    budget = nA - C["k"]
    rec = dict(base)
    rec.update(lam=str(fam["lam"]), rho=str(fam["rho"]), rho_f=float(fam["rho"]),
               a_w=[str(a) for a in fam["a_w"]], a_w_f=[float(a) for a in fam["a_w"]],
               n=nA, budget=budget, n_G_cells=fam["n_g_cells"],
               n_E_boxes={str(r): len(v) for r, v in fam["E"].items()},
               overshoot=[o.get("overshoot") for o in (fam.get("overshoot") or [])],
               r_max_grid=fam["r_hist"]["r_max_grid"], r_hist=fam["r_hist"]["hist"],
               tau=None, eta=None, minmass=None, maxcov=None, rows=None, atoms=None, lp_s=0.0,
               verdict=None)
    logline("[RUN] %s n=%d budget=%d rho=%.6f a_w=%s r_max_grid=%d E=%s"
            % (tag, nA, budget, float(fam["rho"]), ["%.5f" % float(a) for a in fam["a_w"]],
               fam["r_hist"]["r_max_grid"], {r: len(v) for r, v in fam["E"].items()}))
    ok, _rows = CAN.image_gate(cls, s, SF.pin_boxes(fam)[1], log=logline)
    rec["image_gate"] = bool(ok)
    if not ok:
        rec["verdict"] = "REFUSED (IMAGE GATE)"
        logline("  " + rec["verdict"])
        _put(rec)
        return rec, None, famp
    node_path = os.path.join(NODES, tag + ".json")
    if os.path.exists(node_path):
        res = json.load(open(node_path))
        logline("  LP reused from %s" % os.path.basename(node_path))
    else:
        if gate and wait_for_commit(tag, deadline) is None:
            rec["verdict"] = "SKIPPED (commit headroom)"
            _put(rec)
            return rec, None, famp
        boxes, h = SF.pin_boxes(fam)
        hyp = Hyp(boxes, [])
        rmax = SF.install_rhs(fam, e, lpbox94)
        t0 = time.time()
        tp = min(probe_time, lp_time)
        logline("  [LP] sym=C1 probe=%.0fs full=%.0fs rhs_max=%.4f h=%.9f" % (tp, lp_time, rmax, h))
        kw = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None, prune=0,
                  prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                  max_rows_add=2000, fine_slack=99.0, alternate=True)
        try:
            res = solve_node(float(s), hyp, budget, warm=warm_pool(cls, s), time_limit=tp, **kw)
            rec["tau_probe"] = res["tau"]
            rec["probe_s"] = round(time.time() - t0, 1)
            logline("    probe: tau=%.6f conv=%s minmass=%s rows=%s (%.0f s)"
                    % (res["tau"], res["converged"], res["minmass"], res.get("n_rows"),
                       rec["probe_s"]))
            # tau only ever rises as the row oracle keeps finding violated poses, so a probe
            # already at or above the budget is refused without spending the full lp_time.
            if res["tau"] < budget and not res["converged"] and lp_time > tp + 30:
                res = solve_node(float(s), hyp, budget, warm=warm_from_result(res),
                                 time_limit=lp_time - tp, **kw)
        finally:
            SF.install_rhs(None, None, lpbox94)
        res["child_id"] = tag
        res["e"] = str(e)
        res["delta"] = float(delta)
        res["cls"] = cls
        res["window"] = win
        json.dump(res, open(node_path, "w"))
        rec["lp_s"] = round(time.time() - t0, 1)
    rec.update(tau=res["tau"], eta=res["tau"] - budget, converged=bool(res["converged"]),
               minmass=res["minmass"], maxcov=res["maxcov"], rows=res.get("n_rows"),
               atoms=len([x for x in res.get("atoms_all", []) if x[2] > 1e-10]))
    logline("  tau=%.6f eta=%+.6f conv=%s minmass=%s maxcov=%s rows=%s atoms=%s lp_s=%.0f"
            % (rec["tau"], rec["eta"], rec["converged"], rec["minmass"], rec["maxcov"],
               rec["rows"], rec["atoms"], rec["lp_s"]))
    rec["verdict"] = ("LP-PASS (tau < budget; certificate not attempted yet)"
                      if res["tau"] < budget else "refused (tau %.6f >= budget %d)"
                      % (res["tau"], budget))
    _put(rec)
    return rec, (node_path if res["tau"] < budget else None), famp


# ---------------------------------------------------------------- certification
def certify(tag, node_path, famp, e, cert_time, deadline, rounds=2, eps_geo=None):
    if wait_for_commit(tag + ":cert", deadline) is None:
        return "SKIPPED (commit headroom)", 0.0, None
    cmd = [sys.executable, os.path.join(HERE, "certify94.py"), node_path,
           "--fam", famp, "--e", str(e), "--certdir", CERTS, "--tag", tag,
           "--rounds", str(rounds), "--jobs", str(VERIFY_JOBS_CAP), "--depth", "56",
           "--time_limit", str(cert_time), "--verify_timeout", str(max(600.0, cert_time * 2)),
           "--scale", "0", "--scale_cap", "1.40000", "--max_w", "32", "--loop_cols"]
    if eps_geo is not None:
        cmd += ["--eps_geo", "%g" % eps_geo]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = round(time.time() - t0, 1)
    with open(os.path.join(LOGS, "cert_%s.log" % tag), "a") as f:
        f.write(p.stdout + "\n---stderr---\n" + p.stderr + "\n")
    for l in p.stdout.splitlines():
        if l.startswith(("[round", "    A|", "    B", "CERTIFIED", "certificate", "NOT certified")):
            logline("    " + l.strip())
    if p.returncode not in (0, 1, 3):
        logline("    certify94 rc=%d; stderr tail: %s" % (p.returncode, p.stderr[-400:]))
    return ("PASS" if p.returncode == 0 else "FAIL(rc=%d)" % p.returncode), dt, p.returncode


def cert_files(tag, m_u):
    outA = os.path.join(CERTS, "runA_%s.json" % tag)
    outB = [os.path.join(CERTS, "runB%d_%s.json" % (r, tag)) for r in range(1, m_u + 1)]
    return outA, outB


def _verdicts(tag):
    try:
        d = json.load(open(os.path.join(CERTS, "%s.certify.json" % tag)))
        r = d["rounds"][-1]
        return ("PASS" if r["rcA"] == 0 else "FAIL"), \
               {k: ("PASS" if v == 0 else "FAIL") for k, v in r["rcB"].items()}
    except Exception:
        return None, None


def do_certify(entry, cert_time, T_END, spent):
    """entry = (cls, win, delta, e, tag, node_path, famp).  Returns seconds spent."""
    cls, win, delta, e, tag, node_path, famp = entry
    C = SF.CLASSES[cls]
    logline("[CERT] %s (delta=%g e=%s)" % (tag, delta, str(e)))
    verdict, dt, rc = certify(tag, node_path, famp, e, cert_time, T_END)
    vA, vB = _verdicts(tag)
    outA, outB = cert_files(tag, C["m_u"])
    rec = dict(tag=tag, phase="cert", cls=cls, window=win, delta=float(delta), e=str(e),
               n=int(11 + 2 * C["m_u"] * e), budget=int(11 + 2 * C["m_u"] * e) - C["k"],
               verdict=verdict, verdictA=vA, verdictB=vB, cert_s=dt,
               certA=outA, certB=outB, sha256_A=sha256(outA),
               sha256_B=[sha256(p) for p in outB], eps_geo_used=None,
               ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    if verdict != "PASS":
        for m in (0.002, 0.004):
            if time.time() > T_END - 60:
                break
            tag2 = "%s_epsgeo%g" % (tag, m)
            logline("[CERT] eps_geo repair %g -> %s" % (m, tag2))
            v2, dt2, _ = certify(tag2, node_path, famp, e, cert_time, T_END, eps_geo=m)
            dt += dt2
            rec["cert_s"] = dt
            if v2 == "PASS":
                vA2, vB2 = _verdicts(tag2)
                oA, oB = cert_files(tag2, C["m_u"])
                rec.update(verdict="PASS", verdictA=vA2, verdictB=vB2, eps_geo_used=m,
                           certA=oA, certB=oB, sha256_A=sha256(oA),
                           sha256_B=[sha256(p) for p in oB], tag=tag2)
                break
            rec["verdict"] = "FAIL(eps_geo %g)" % m
    if rec["verdict"] == "PASS":
        open(os.path.join(CERTS, rec["tag"] + ".PASS"), "w").write("ok")
        fam, _ = get_fam(cls, win, delta)
        ok, _r = CAN.image_gate(cls, SF.WINDOWS[win][0], SF.pin_boxes(fam)[1], log=logline)
        if not ok:
            logline("ENGINE BUG: certified PASS on an image-realisable node " + tag)
            _put(rec)
            sys.exit(9)
    logline("  verdict=%s (A=%s B=%s) cert_s=%.0f" % (rec["verdict"], rec["verdictA"],
                                                      rec["verdictB"], rec["cert_s"]))
    _put(rec)
    return dt, rec["verdict"] == "PASS"


# ---------------------------------------------------------------- Phase 0
def phase0(A, T_END):
    logline("=" * 100)
    logline("A94 slotcrowd94 campaign start; wall budget %.0f min; reserve %.0f min"
            % (A.minutes, A.reserve_min))
    sb = os.path.join(ATT, "A56-sparametric", "results", "scoreboard.json")
    mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(sb)))
    st = json.load(open(sb))["rows"]
    logline("A56 scoreboard mtime %s ; k6_27 = %s" % (mt, (st.get("k6_27") or {}).get("status", "?")))
    logline("U_S per chore sec 2 (m_u = 4 for both classes): k5_11 %s ; k5_16 %s"
            % (SF.CLASSES["k5_11"]["slot_ext"], SF.CLASSES["k5_16"]["slot_ext"]))
    logline("SCOPE: every certificate here speaks about ONE side s and, via Lemma B/CW-S, about "
            "sides m in [m_lo, s); NOTHING here claims anything at any side > s.  A57's G1 records "
            "are s0 slack-core tree kills of the same classes and are neither read nor contradicted.")
    logline("k6_23's window top is 3877/1000 = s-hat - 8.4e-5: for the two windows with s = s0 the "
            "slot BL(1,0)/TR(0,0) is certified usable only up to 3877/1000 (see the report).")
    res = dict(scoreboard_mtime=mt, k6_27=(st.get("k6_27") or {}).get("status", "?"))
    # (i) Trump slot canary
    ok1, worst, rows = CAN.trump_slot_canary(log=logline)
    res["trump_slot_canary"] = dict(ok=bool(ok1), max_dev=worst, rows=rows)
    if not ok1:
        logline("REFUSED: the Trump slot canary does not reproduce the lead's depths")
        sys.exit(1)
    # (ii) image gate, every window x class
    res["image_gate"] = {}
    for cls in CLS:
        for win in ("s0_G2", "G4_lo", "s0_lo", "G3_G4", "G2_G3"):
            s, m_lo = SF.WINDOWS[win]
            rho = SF.rho_of(s, m_lo, SF.CLASSES[cls]["A_S"])
            h = float(rho) / math.sqrt(2.0) * (1 + 1e-12)
            ok, rr = CAN.image_gate(cls, s, h, log=logline)
            res["image_gate"]["%s/%s" % (cls, win)] = dict(ok=bool(ok), rows=rr)
            if not ok:
                logline("REFUSED: an image realises the pin hypothesis (%s %s)" % (cls, win))
                sys.exit(1)
    # (iii) the e = 0 exact-pin regression LP
    res["regression"] = {}
    for cls in CLS:
        tag = "reg_%s_e0" % cls
        np_ = os.path.join(NODES, tag + ".json")
        C = SF.CLASSES[cls]
        if os.path.exists(np_):
            r = json.load(open(np_))
            logline("  regression %s reused: tau=%.6f" % (cls, r["tau"]))
        else:
            if wait_for_commit(tag, T_END) is None:
                logline("  regression %s SKIPPED (commit headroom)" % cls)
                res["regression"][cls] = dict(skipped=True)
                continue
            boxes = [Box(float(x), float(x), float(y), float(y), 0.0, 0.0)
                     for (x, y) in (SF.pin_at(p, SF.S0) for p in C["pins"])]
            SF.install_rhs(None, None, lpbox94)
            t0 = time.time()
            r = solve_node(float(SF.S0), Hyp(boxes, []), C["N"], sym_kind="C1",
                           warm=warm_pool(cls, SF.S0), time_limit=min(A.lp_time, 420.0),
                           max_iter=900, out=None, log=lambda *x: None, prune=0, prune_cols=3,
                           col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                           max_rows_add=2000, fine_slack=99.0, alternate=True)
            r["lp_s"] = round(time.time() - t0, 1)
            json.dump(r, open(np_, "w"))
        tgt = REGRESSION_TARGET[cls]
        okr = abs(r["tau"] - tgt) <= REG_TOL
        logline("  REGRESSION %s (e=0, rho=0, s0, budget %d): tau=%.6f (target ~%.4f, |d|=%.4f) %s"
                % (cls, C["N"], r["tau"], tgt, abs(r["tau"] - tgt), "OK" if okr else "**OFF**"))
        res["regression"][cls] = dict(tau=r["tau"], target=tgt, ok=bool(okr),
                                      minmass=r.get("minmass"), rows=r.get("n_rows"),
                                      lp_s=r.get("lp_s"))
        _put(dict(tag=tag, phase="regression", cls=cls, s=str(SF.S0), e="0", delta=None,
                  budget=C["N"], tau=r["tau"], eta=r["tau"] - C["N"], target=tgt, ok=bool(okr),
                  minmass=r.get("minmass"), maxcov=r.get("maxcov"), rows=r.get("n_rows"),
                  lp_s=r.get("lp_s"), verdict="regression", ts=time.strftime("%Y-%m-%d %H:%M:%S")))
    json.dump(res, open(os.path.join(RES, "phase0.json"), "w"), indent=1, default=str)
    return res


# ---------------------------------------------------------------- the campaign
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=480.0)
    ap.add_argument("--lp_time", type=float, default=900.0)
    ap.add_argument("--cert_time", type=float, default=300.0)
    ap.add_argument("--reserve_min", type=float, default=150.0)
    ap.add_argument("--probe_time", type=float, default=300.0,
                    help="short first stage of every LP; tau >= budget there refuses the node")
    ap.add_argument("--max_e", type=int, default=3, help="max e values tried per (class, window, delta)")
    ap.add_argument("--phase0_only", action="store_true")
    A = ap.parse_args()
    T_END = time.time() + 60 * A.minutes
    P0 = phase0(A, T_END)
    if A.phase0_only:
        return

    # smoke test of the rhs hook + the certificate format through the frozen verifier's loader
    fam0, famp0 = get_fam("k5_11", "s0_G2", PLAN[0][3][0])
    sm = subprocess.run([sys.executable, os.path.join(HERE, "smoke94.py"), "--fam", famp0],
                        capture_output=True, text=True)
    open(os.path.join(LOGS, "smoke94.out"), "w").write(sm.stdout + "\n---\n" + sm.stderr)
    for l in sm.stdout.splitlines():
        logline("  " + l)
    if sm.returncode != 0:
        logline("REFUSED: smoke94 failed (see logs/smoke94.out)")
        sys.exit(1)

    cert_spent = [0.0]
    passed = {}       # (cls, win) -> {delta: (e, tag, node_path, famp)}

    def lp_deadline():
        return T_END - max(0.0, 60 * A.reserve_min - cert_spent[0])

    def sweep(phases):
        for (ph, cls, win, deltas) in PLAN:
            if ph not in phases:
                continue
            # eta(delta) is MONOTONE DECREASING in delta (a_w decreases with delta, so every
            # family shrinks, so tau falls, while the budget does not depend on delta), so the
            # passing set is upward-closed: scan delta DOWNWARDS and stop at the first failure.
            ok_seen = False
            for d in sorted(deltas, reverse=True):
                if time.time() > lp_deadline():
                    logline("LP sweep stops before %s %s delta=%g (certification reserve)"
                            % (cls, win, d))
                    return
                es, tried, hit = list(E_ORDER), 0, False
                while es and tried < A.max_e:
                    e = es.pop(0)
                    if time.time() > lp_deadline():
                        return
                    rec, npth, famp = run_lp(ph, cls, win, d, e, A.lp_time, lp_deadline(),
                                             probe_time=A.probe_time)
                    if rec.get("verdict", "").startswith("SKIPPED (a_w"):
                        break
                    tried += 1
                    if npth is not None:
                        passed.setdefault((cls, win), {})[d] = (e, rec["tag"], npth, famp)
                        ok_seen = hit = True
                        logline("  %s %s delta=%g PASSES the LP at e=%s (eta=%+.6f); "
                                "skipping the remaining e" % (cls, win, d, str(e), rec["eta"]))
                        break
                    if rec.get("tau") is None:
                        break
                    # eta(e) ~ (tau0 - N) + (c - 2 m_u) e with c = (tau - tau0)/e: reorder the
                    # remaining e by the predicted eta, cheapest (most negative) first.
                    C0 = SF.CLASSES[cls]
                    tau0 = REGRESSION_TARGET[cls]
                    c = (rec["tau"] - tau0) / float(e)
                    es.sort(key=lambda x: (tau0 - C0["N"]) + (c - 2 * C0["m_u"]) * float(x))
                    logline("    e-model: c = dtau/de ~ %.3f (break-even %d); remaining e order %s"
                            % (c, 2 * C0["m_u"], [str(x) for x in es]))
                if not hit:
                    logline("  %s %s delta=%g does NOT pass; every SMALLER delta has a strictly "
                            "larger a_w, hence a larger tau and a larger eta -- the rest of this "
                            "window's delta list is skipped (monotonicity)." % (cls, win, d))
                    break

    def cert_group(wins, want="smallest", limit=99):
        n = 0
        for cls in CLS:
            for win in wins:
                P = passed.get((cls, win))
                if not P:
                    continue
                ds = sorted(P)
                order = [ds[0]] if want == "smallest" else [ds[-1]]
                if want == "both" and len(ds) > 1:
                    order = [ds[0], ds[-1]]
                for d in order:
                    if n >= limit or time.time() > T_END - 120:
                        return
                    if os.path.exists(os.path.join(CERTS, P[d][1] + ".PASS")):
                        continue
                    e, tag, npth, famp = P[d]
                    dt, _ok = do_certify((cls, win, d, e, tag, npth, famp), A.cert_time, T_END,
                                         cert_spent)
                    cert_spent[0] += dt
                    n += 1

    sweep(("P1",))
    logline("Phase 1 done: %s" % {("%s/%s" % k): sorted(v) for k, v in passed.items()})
    cert_group(("s0_G2",), want="smallest")
    sweep(("P4",))
    cert_group(("G4_lo",), want="smallest")
    sweep(("P6", "P7"))
    cert_group(("s0_lo", "G3_G4", "G2_G3"), want="smallest")
    cert_group(("s0_G2", "G4_lo"), want="largest")
    json.dump({("%s|%s" % k): {str(d): [str(v[0]), v[1]] for d, v in val.items()}
               for k, val in passed.items()},
              open(os.path.join(RES, "lp_passed.json"), "w"), indent=1)
    logline("campaign done; %.1f min left of the budget; certification used %.1f min"
            % ((T_END - time.time()) / 60.0, cert_spent[0] / 60.0))


if __name__ == "__main__":
    if os.path.exists(MARKER):
        os.remove(MARKER)
    status, err = "done", None
    t_start = time.time()
    try:
        main()
    except SystemExit as ex:
        status = "exit(%s)" % ex.code
    except BaseException:
        import traceback
        status = "CRASH"
        err = traceback.format_exc()
        logline("CAMPAIGN CRASH\n" + err)
    finally:
        try:
            import report94
            report94.build()
            logline("report written: notes/slotcrowd94_report.md")
        except BaseException:
            import traceback
            logline("report generation failed\n" + traceback.format_exc())
        with open(MARKER, "w") as f:
            json.dump(dict(status=status, error=err,
                           minutes=round((time.time() - t_start) / 60.0, 1),
                           ts=time.strftime("%Y-%m-%d %H:%M:%S")), f, indent=1)
        logline("MARKER written: %s (status=%s)" % (MARKER, status))
