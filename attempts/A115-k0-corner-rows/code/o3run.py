"""A89-O3 -- the SHALLOW-corner root kill driver (Lemma ID's LP row, docs/proofs/tilt_floor_k0.md sec 7).

One run = one k0_00 ROOT node at s0 = 969271/250000, no pins, no cores, budget 11, whose only
hypotheses are the SHALLOW(delta) NO-families of a chosen set of corners (o3fam.py).  The chain
is A85's frozen one, copied verbatim into this attempt's code/:
    caselp.solve_node  ->  (tau < 11)  ->  certify.py  ->  verify_case.py
with the A85 canary in front of it (a node realised by any of the 8 D4 Trump images is NEVER
certified: the engine REFUSES) and A85's eps_geo repair behind it.

Resource discipline: BLAS pinned to 1 thread (blas1, imported first), at most one LP process,
and free COMMIT (MEMORYSTATUSEX.ullAvailPageFile) > 6144 MB checked before every LP and before
every certify launch.
"""
import argparse, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
from caselp import Hyp, NoFam, solve_node
import class85 as K85
import o3fam as F
from corner85 import f_min_max

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
NODES = os.path.join(RES, "nodes", "k0_00")
for d in (RES, LOGS, CERTS, NODES, os.path.join(CERTS, "k0_00")):
    os.makedirs(d, exist_ok=True)

S_RAT = "969271/250000"
S0F = float(Fr(S_RAT))
MIN_FREE_COMMIT_MB = 6144.0
LOGP = os.path.join(LOGS, "o3.log")
SINK = os.path.join(RES, "o3_runs.jsonl")


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


def wait_for_commit(tag, deadline=None):
    n = 0
    while True:
        mb = free_commit_mb()
        if mb > MIN_FREE_COMMIT_MB:
            if n:
                logline("  commit OK %.0f MB after %d x 60 s wait (%s)" % (mb, n, tag))
            return mb
        if deadline is not None and time.time() > deadline:
            logline("  commit STILL LOW %.0f MB, deadline passed -- SKIP %s" % (mb, tag))
            return None
        logline("  commit dip %.0f MB < %.0f: sleep 60 s (%s)" % (mb, MIN_FREE_COMMIT_MB, tag))
        time.sleep(60)
        n += 1


# ---------------------------------------------------------------- per-image per-corner depth
def corner_depth_table():
    """exact per-image, per-corner intrusion DEPTH(c) = 1 - min over squares of f_c."""
    C = K85.load_class("k0_00", K85.DELTA_PIN)
    S = Fr(S_RAT)
    out = []
    for im in C["images"]:
        row = dict(image=im["key"], sym=im.get("sym"))
        for c in F.CORNERS:
            best = None
            arg = None
            for (x, y, th) in im["placements"]:
                xq = Fr(round(x * 10 ** 12), 10 ** 12)
                yq = Fr(round(y * 10 ** 12), 10 ** 12)
                t = Fr(round(math.tan(th / 2.0) * 2 ** 30), 2 ** 30)
                if c in ("BR", "TR"):
                    u = S - xq
                else:
                    u = xq
                if c in ("TL", "TR"):
                    v = S - yq
                else:
                    v = yq
                # a reflection of the frame maps theta -> 90 - theta  (t -> (1-t)/(1+t))
                tt = t if c in ("BL", "TR") else (1 - t) / (1 + t)
                val = f_min_max(u, v, tt)
                if best is None or val < best:
                    best, arg = val, (float(x), float(y), math.degrees(th) % 90.0)
            row[c] = dict(depth=float(1 - best), f_min=float(best), argmin=arg)
        out.append(row)
    return out


def images_realizing(hyp, tol=1e-9):
    """A85 semantics: the images whose placements satisfy the node hypotheses (no core boxes
    here, so: no placement lies in any NO-family).  Such a node must NEVER be certified."""
    C = K85.load_class("k0_00", K85.DELTA_PIN)
    out = []
    for im in C["images"]:
        Pl = [(x, y, math.degrees(th) % 90.0) for (x, y, th) in im["placements"]]
        if not any(f.contains(x, y, thd) for f in hyp.nofams for (x, y, thd) in Pl):
            out.append(im["key"])
    return out


# ---------------------------------------------------------------- the run
FAM_CACHE = {}
WARM_CACHE = {}


def warm_pool():
    """columns-only warm start (A57 T4).  Read-only harvest of atom POSITIONS from certificates
    this lab already produced for the same container: A38's D4 root at s0 (652 atoms) and A07's
    unstratified roots at 3.80-3.83 (rescaled to s0).  Columns can only help -- the LP still
    optimises the weights, and soundness rests on the exact verifier."""
    if "w" in WARM_CACHE:
        return WARM_CACHE["w"]
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
            from lpbox import Sym
            for (x, y) in Sym("D4", float(d["s"])).point_images(rep[0], rep[1]):
                add(x * sc, y * sc)
    atoms = atoms[:1600]        # A57 T4 cap: columns help, but the first tableau must stay small
    WARM_CACHE["w"] = dict(atoms=atoms, rows=[])
    logline("  warm pool: %d columns (A38 root_s0 + A07 3.82/3.83, rescaled)" % len(atoms))
    return WARM_CACHE["w"]


def get_fams(delta, window, nsteps, drop_all_theta=True):
    key = (delta, window, nsteps)
    if key in FAM_CACHE:
        return FAM_CACHE[key]
    a = F.a_win(delta) if window else F.a_s0(delta)
    fams = F.build_bl(a, nsteps=nsteps)
    if drop_all_theta:
        fams = [f for f in fams if f[2] != (0.0, 90.0)]
    ok, rows = F.certify_bl(fams, a)
    if not ok:
        raise AssertionError("UNSOUND family in the BL set at delta=%s window=%s" % (delta, window))
    mm = min(r["margin"] for r in rows)
    FAM_CACHE[key] = (a, fams, rows, mm)
    logline("  fams: a=%.6f (%s) n_BL=%d all-sound=True min-margin=%.3e"
            % (float(a), "window" if window else "s0-only", len(fams), mm))
    return FAM_CACHE[key]


def run(pattern, delta, window=True, nsteps=8, lp_time=600.0, cert_time=300.0, jobs=1,
        do_cert=True, deadline=None, tag=None):
    pat = list(pattern)
    tag = tag or ("o3_%s_d%s_%s" % ("".join(p[0] + p[1].lower() for p in pat),
                                    str(delta).replace(".", ""), "win" if window else "s0"))
    a, fams, famrows, mm = get_fams(delta, window, nsteps)
    # anchor every rect BELOW the admissible domain floor 0.5 so that domain-edge boxes of the
    # verifier are provably inside the rect (sound: f is nondecreasing in both coordinates)
    nofams = []
    for c in pat:
        for nf in F.corner_fams(fams, c):
            nf.x0 = 0.45 if nf.x0 <= 0.5 + 1e-12 else nf.x0
            nf.y0 = 0.45 if nf.y0 <= 0.5 + 1e-12 else nf.y0
            nf.x1 = S0F - 0.45 if nf.x1 >= S0F - 0.5 - 1e-12 else nf.x1
            nf.y1 = S0F - 0.45 if nf.y1 >= S0F - 0.5 - 1e-12 else nf.y1
            nofams.append(nf)
    hyp = Hyp([], nofams)
    sym = "D4" if hyp.is_symmetric_D4(S0F) else "C1"
    real = images_realizing(hyp)
    rec = dict(tag=tag, pattern=pat, delta=delta, window=bool(window), a=float(a), a_rat=str(a),
               lambda_max=str(F.LAM_MAX), n_exempt_boxes=len(nofams), n_fams_BL=len(fams),
               fam_min_margin=mm, sym=sym, budget=11, canary_images=real,
               tau=None, converged=None, eta=None, lp_s=0.0, cert_s=0.0,
               verdict=None, cert_path=None, ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    logline("[RUN] %s pattern=%s delta=%s a=%.6f boxes=%d sym=%s canary=%s"
            % (tag, "+".join(pat), delta, float(a), len(nofams), sym, real or "none"))
    if real:
        rec["verdict"] = "REFUSED (CANARY: realised by %s)" % ",".join(real)
        logline("  " + rec["verdict"])
        _put(rec)
        return rec
    node_path = os.path.join(NODES, tag + ".json")
    if os.path.exists(node_path):
        res = json.load(open(node_path))
        logline("  LP reused from %s" % node_path)
    else:
        if wait_for_commit(tag, deadline) is None:
            rec["verdict"] = "SKIPPED (commit headroom)"
            _put(rec)
            return rec
        t0 = time.time()
        logline("  [LP] sym=%s tl=%.0fs" % (sym, lp_time))
        res = solve_node(S0F, hyp, 11, sym_kind=sym, warm=warm_pool(), time_limit=lp_time,
                         max_iter=900, out=None, log=lambda *x: None, prune=0, prune_cols=3,
                         col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                         max_rows_add=2000, fine_slack=99.0, alternate=True)
        res["child_id"] = tag
        json.dump(res, open(node_path, "w"))
        rec["lp_s"] = round(time.time() - t0, 1)
    rec.update(tau=res["tau"], converged=bool(res["converged"]), eta=res["tau"] - 11,
               minmass=res["minmass"], maxcov=res["maxcov"], rows=res.get("n_rows"),
               atoms=len([x for x in res.get("atoms_all", []) if x[2] > 1e-10]))
    logline("  tau=%.6f eta=%.6f conv=%s rows=%s lp_s=%.0f"
            % (rec["tau"], rec["eta"], rec["converged"], rec["rows"], rec["lp_s"]))
    if res["tau"] >= 11:
        rec["verdict"] = "refused (tau %.6f >= budget 11)" % res["tau"]
        _put(rec)
        return rec
    if not do_cert:
        rec["verdict"] = "LP-only (tau < 11, certificate not attempted)"
        _put(rec)
        return rec
    if wait_for_commit(tag + ":cert", deadline) is None:
        rec["verdict"] = "LP-only (tau < 11; cert SKIPPED, commit headroom)"
        _put(rec)
        return rec
    cert_out = os.path.join(CERTS, "k0_00", tag + ".json")
    t1 = time.time()
    rc, log = _certify(node_path, cert_out, cert_time, jobs)
    rec["cert_s"] = round(time.time() - t1, 1)
    if rc == 0:
        open(cert_out + ".PASS", "w").write("ok")
        rec.update(verdict="PASS", cert_path=cert_out)
    else:
        rec["verdict"] = "FAIL(rc=%d)" % rc
        for m in (0.002, 0.004):
            if wait_for_commit(tag + ":epsgeo%g" % m, deadline) is None:
                break
            co = os.path.join(CERTS, "k0_00", "%s_epsgeo%g.json" % (tag, m))
            t2 = time.time()
            rc2, _ = _certify(node_path, co, cert_time, jobs, eps_geo=m)
            rec["cert_s"] += round(time.time() - t2, 1)
            if rc2 == 0:
                open(co + ".PASS", "w").write("ok")
                rec.update(verdict="PASS", cert_path=co, eps_geo_used=m)
                break
            rec["verdict"] = "FAIL(eps_geo %g rc=%d)" % (m, rc2)
    if rec["verdict"] == "PASS" and images_realizing(hyp):
        logline("ENGINE BUG: PASS on an image-realizable node " + tag)
        sys.exit(9)
    logline("  verdict=%s cert_s=%.0f" % (rec["verdict"], rec["cert_s"]))
    _put(rec)
    return rec


def _certify(node_path, cert_out, cert_time, jobs, eps_geo=None):
    cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_path, "--s_rat", S_RAT,
           "--rounds", "2", "--jobs", str(jobs), "--depth", "56",
           "--time_limit", str(cert_time), "--resolve_time", str(cert_time),
           "--out", cert_out, "--scale", "0", "--scale_cap", "1.40000",
           "--max_w", "32", "--loop_cols"]
    if eps_geo is not None:
        cmd += ["--eps_geo", "%g" % eps_geo]
    p = subprocess.run(cmd, capture_output=True, text=True)
    with open(os.path.join(LOGS, "cert_%s.log" % os.path.basename(cert_out)[:-5]), "w") as f:
        f.write(p.stdout + "\n---stderr---\n" + p.stderr)
    for l in p.stdout.splitlines():
        if l.startswith(("[round", "    PASS", "    FAIL", "CERTIFIED", "certificate")):
            logline("    " + l.strip())
    return p.returncode, p.stdout


def _put(rec):
    with open(SINK, "a") as f:
        f.write(json.dumps(rec) + "\n")


PATTERNS = dict(
    R1=[("BL", "BR", "TL", "TR")],
    R2=[("BL", "BR", "TR")],
    R3adj=[("BL", "BR")],
    R3diag=[("BL", "TR")],
    R4=[("BL",)],
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True, help="comma-separated corners, or an R-name")
    ap.add_argument("--delta", type=float, required=True)
    ap.add_argument("--s0only", action="store_true")
    ap.add_argument("--nsteps", type=int, default=8)
    ap.add_argument("--lp_time", type=float, default=600.0)
    ap.add_argument("--cert_time", type=float, default=300.0)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--no_cert", action="store_true")
    ap.add_argument("--budget_min", type=float, default=0.0, help="wall minutes still available")
    A = ap.parse_args()
    pat = PATTERNS[A.pattern][0] if A.pattern in PATTERNS else tuple(A.pattern.split(","))
    dl = time.time() + 60 * A.budget_min if A.budget_min > 0 else None
    r = run(pat, A.delta, window=not A.s0only, nsteps=A.nsteps, lp_time=A.lp_time,
            cert_time=A.cert_time, jobs=A.jobs, do_cert=not A.no_cert, deadline=dl)
    print(json.dumps({k: r[k] for k in ("tag", "pattern", "delta", "a", "n_exempt_boxes",
                                        "sym", "tau", "eta", "converged", "lp_s", "cert_s",
                                        "verdict", "canary_images")}))


if __name__ == "__main__":
    main()
