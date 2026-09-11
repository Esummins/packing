"""A207 -- the BASIN of a FULL extension class T = S u {p} around p's simple pose (notes/basin.md, Lemma BASIN).

The slot's exact pin in T's case-measure certificate is replaced by the BOXED square
    |c - c_p|_inf <= r_c,   |tan(theta/2)| <= t_r   (theta folded to (-45, 45] deg),
whose core is the axis-aligned square K_p = [c_p +- a]^2, a = 1/(2 (cos + sin)(t_r)) - r_c, rounded DOWN to 1e-9
(every square of the box contains K_p: Lemma BASIN (i)).  The class LP is RE-SOLVED with that core (A53 caselp,
read-only), certified at s0 by the A54 certify loop against the FROZEN A53 verify_case.py (sha asserted), made
parametric by A56 make_param (gap anchoring) and verified over the window by the FROZEN A56 verify_param.py (sha
asserted), then the C2 canary (specialisations at lo / mid / hi under verify_case).  Every output lands under
attempts/A207-basin-clip/; A53 / A54 / A56 files are only read.
"""
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
A53 = os.path.join(ATT, "A53-simple-strata")
A54C = os.path.join(ATT, "A54-stragglers", "code")
A56C = os.path.join(ATT, "A56-sparametric", "code")
OUT = os.path.abspath(os.path.join(HERE, ".."))
CERTS, NODES, LOGS = os.path.join(OUT, "certs"), os.path.join(OUT, "results", "nodes"), os.path.join(OUT, "logs")
for _p in (A54C, A56C):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import hashlib                                                  # noqa: E402

VERIFY_CASE = os.path.join(A53, "code", "verify_case.py")
VERIFY_PARAM = os.path.join(A56C, "verify_param.py")
SHA_CASE = "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"
SHA_PARAM = "0c58485c1a662453188af5b0aaf42099cf41c15f82a6647404598a44e8a505ec"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


assert _sha(VERIFY_CASE) == SHA_CASE, "frozen A53 verify_case.py is not the frozen one"
assert _sha(VERIFY_PARAM) == SHA_PARAM, "frozen A56 verify_param.py is not the frozen one"
import caselp                                                   # noqa: E402  (A54's copy of A53's; read-only)
from caselp import Box, Core, Hyp, solve_node, warm_from_result  # noqa: E402
import lpbox                                                    # noqa: E402
import make_param                                               # noqa: E402  (A56)
import specialize                                               # noqa: E402  (A56)
import resolve_margin as RM                                     # noqa: E402  (A56: build_warm reads A53 / A56 files)

S0 = Fr(969271, 250000)
S_LO = Fr(191, 50)
S_G1 = Fr(3861637, 1000000)
S0F = float(S0)
NAME_TO_SLOTS = os.path.join(A53, "results", "name_to_slots.json")
ENV = dict(os.environ)
BELOW_NORMAL = 0x4000


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, BELOW_NORMAL)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


# ----------------------------------------------------------------------------- the basin core (Lemma BASIN (i))
def t_of_deg(d):
    """rational t >= tan(d/2): the tilt basin is DEFINED by t_r, its degrees are 2 atan(t_r) >= d."""
    return Fr(math.ceil(math.tan(math.radians(float(d)) / 2) * 10 ** 6), 10 ** 6) if float(d) > 0 else Fr(0)


def core_half_side(rc, tr):
    """a = 1/(2 w(t_r)) - r_c rounded down to 1e-9, w = cos + sin = (1 + 2t - t^2)/(1 + t^2); (a + r_c) w <= 1/2 exactly."""
    w = (1 + 2 * tr - tr * tr) / (1 + tr * tr)
    a = Fr(math.floor((1 / (2 * w) - rc) * 10 ** 9), 10 ** 9)
    assert a > 0 and (a + rc) * w <= Fr(1, 2)
    return a


def basin_hyp(ext, idx, rc, tr):
    """T's pins as exact cores except cores[idx], the boxed slot square with the axis-aligned basin core."""
    slots = [tuple(Fr(str(v)) for v in p) for p in json.load(open(NAME_TO_SLOTS))[ext]]
    boxes = [Box(float(x), float(x), float(y), float(y), 0.0, 0.0) for (x, y) in slots]
    kx, ky = slots[idx]
    deg = math.degrees(2 * math.atan(float(tr)))
    boxes[idx] = Box(float(kx - rc), float(kx + rc), float(ky - rc), float(ky + rc), -deg, deg)
    hyp = Hyp(boxes, [])
    a = core_half_side(rc, tr)
    hyp.cores[idx] = Core(kx, ky, Fr(0), a, boxes[idx])
    return hyp, slots, a


def make_cert(res, hyp, scale, basin):
    """caselp.make_certificate with the hypothesis object given (its cores are the basin cores, not Box.core())."""
    seen, atoms, weights = {}, [], []
    for (x, y, w) in res["atoms_all"]:
        if w <= 1e-10:
            continue
        p = (Fr(round(x * 10 ** 6), 10 ** 6), Fr(round(y * 10 ** 6), 10 ** 6))
        wq = Fr(math.ceil(w * scale * 10 ** 6), 10 ** 6)
        if p in seen:
            weights[seen[p]] += wq
        else:
            seen[p] = len(atoms)
            atoms.append(p)
            weights.append(wq)
    total = sum(weights, Fr(0))
    return dict(format="case-measure-certificate-v1", n=11, s=str(S0), budget=res["budget"],
                atoms=[[str(p[0]), str(p[1])] for p in atoms], weights=[str(w) for w in weights], total=str(total),
                hypotheses=dict(cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a), box=c.box.to_json()) for c in hyp.cores], nofams=[]),
                claim="every admissible closed unit square Q in [0,%s]^2 disjoint from every core has mu(Q) >= 1, and mu(total) = %.6f < budget %d = 11 - #cores; "
                      "hence no packing of 11 unit squares in side <= %s satisfies the hypotheses (core %d = the BASIN core of the slot square, Lemma BASIN)" % (S0, float(total), res["budget"], S0, basin["idx"]),
                basin=basin,
                provenance=dict(method="A207 basin207: A53 caselp.solve_node with the slot pin's core replaced by the basin core; weights x %.4f rounded up to 1e-6, atoms to 1e-6" % scale,
                                lp_tau=res["tau"], eps_geo=lpbox.EPS_GEO, eps_core=caselp.EPS_CORE, eps_zone=caselp.EPS_ZONE, eps_th=caselp.EPS_TH))


# ----------------------------------------------------------------------------- the frozen verifiers as subprocesses
_MODS = {}


def frozen_main(path, argv, log):
    """the frozen verifier run IN-PROCESS (imported, sha asserted at import; never copied, never edited): one process in all."""
    import contextlib
    import importlib.util
    if path not in _MODS:
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MODS[path] = mod
    with open(log, "a", encoding="utf-8") as fh, contextlib.redirect_stdout(fh), contextlib.redirect_stderr(fh):
        print("\n$ %s %s" % (os.path.basename(path), " ".join(str(c) for c in argv)), flush=True)
        try:
            rc = int(_MODS[path].main([str(c) for c in argv]) or 0)
        except SystemExit as e:
            rc = int(e.code or 0)
    return rc


def sh(cmd, log, timeout=None):
    """cmd = [python, verifier.py, args...]: the verifier's main() in this process (timeout unused: the runs are depth-bounded)."""
    t0 = time.time()
    rc = frozen_main(cmd[1], cmd[2:], log)
    return rc, time.time() - t0


def verify_case(cert, log, depth=56, max_w=96, timeout=1800):
    assert os.path.abspath(cert).startswith(os.path.abspath(OUT)), "verify_case writes beside the certificate: only under A207"
    rep = cert.replace(".json", ".report.json")
    rc, dt = sh([sys.executable, VERIFY_CASE, cert, "--jobs", "1", "--depth", str(depth), "--max-witnesses", str(max_w), "--report", rep,
                 "--witness-file", cert.replace(".json", ".witnesses.json"), "--quiet"], log, timeout)
    return rc, dt, rep


def witness_rows(wf):
    new = []
    for w in json.load(open(wf))["witnesses"]:
        p = w.get("placement")
        if not p:
            continue
        th = math.radians(p["theta_deg"])
        new.append((p["cx_float"], p["cy_float"], th))
        for d in (0.002, 0.005):
            for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                new.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
            for dth in (d, -d):
                new.append((p["cx_float"], p["cy_float"], th + dth))
    return new


def certify(res, hyp, out, basin, log, L, rounds=3, time_limit=300, depth=56, scale_cap=1.06):
    """A54 certify.py's loop (auto scale, witness feedback, column generation in the re-solves) with the basin hypothesis."""
    budget, extra, hist = res["budget"], [], []
    for rd in range(rounds + 1):
        scale = max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
        cert = make_cert(res, hyp, scale, basin)
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(out, "w"), indent=0)
        L("    [certify round %d] tau=%.5f conv=%s scale=%.4f total=%.5f budget=%d atoms=%d" % (rd, res["tau"], res["converged"], scale, tot, budget, len(cert["atoms"])))
        if tot >= budget:
            hist.append(dict(round=rd, tau=res["tau"], total=tot, rc=3))
            return "FAIL(total>=budget)", hist
        rc, dt, rep = verify_case(out, log, depth=depth)
        hist.append(dict(round=rd, tau=res["tau"], total=tot, rc=rc, seconds=round(dt, 1)))
        L("    verify_case rc=%d (%.1f s)" % (rc, dt))
        if rc == 0:
            return "PASS", hist
        if rd == rounds:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            return "FAIL(no witnesses)", hist
        extra += witness_rows(wf)
        res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm_from_result(res), time_limit=time_limit, out=None, log=lambda *x: None,
                         extra_rows=extra, neigh_rows=0, col_stop_iter=10 ** 6, col_stop_cov=1.01, max_cols_add=1000, max_rows_add=1500,
                         fine_slack=99.0, max_iter=1000, prune=6, prune_cols=2, alternate=True)
    return "FAIL", hist


def param_verify(base, name, par, log, depth=48, slo=S_LO, shi=S0, timeout=2400):
    p = make_param.build(json.load(open(base)), name=name, slots=json.load(open(NAME_TO_SLOTS)), gap_band=(Fr(19, 10), Fr(27, 10)))
    p["basin"] = json.load(open(base)).get("basin")
    json.dump(p, open(par, "w"), indent=1)
    rep, wit = par.replace(".json", ".report.json"), par.replace(".json", ".wit.json")
    rc, dt = sh([sys.executable, VERIFY_PARAM, par, "--slo", str(slo), "--shi", str(shi), "--depth", str(depth), "--sscale", "8", "--jobs", "1",
                 "--split", "3", "--report", rep, "--max-witnesses", "20", "--witness-file", wit, "--quiet"], log, timeout)
    return {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc), round(dt, 1), rep


def c2(par, tag, log, slo=S_LO, depth=44):
    out = []
    p = json.load(open(par))
    for lbl, s in (("lo", slo), ("mid", (slo + S0) / 2), ("hi", S0)):
        spec = os.path.join(CERTS, "c2", "%s.%s.json" % (tag, lbl))
        os.makedirs(os.path.dirname(spec), exist_ok=True)
        json.dump(specialize.specialize(p, s), open(spec, "w"), indent=1)
        rc, dt, _ = verify_case(spec, log, depth=depth, max_w=20)
        out.append(dict(s=str(s), s_float=float(s), result={0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc), time_s=round(dt, 1)))
        if rc != 0:
            break
    return out


def warm_from_prev(ext, idx, warm, used):
    """the atoms / rows of every earlier basin node of the same (class, slot) join the warm start (a row is only a demand
    mu(Q) >= 1 at a placement -- always legitimate; the near-pin rows of a smaller basin are exactly what a larger one needs)."""
    import glob
    seen_a = set((round(a[0], 7), round(a[1], 7)) for a in warm["atoms"])
    seen_r = set((round(r[0], 6), round(r[1], 6), round(r[2], 7)) for r in warm["rows"])
    atoms, rows = list(warm["atoms"]), list(warm["rows"])
    for f in sorted(glob.glob(os.path.join(NODES, "basin207_%s_c%d_*.json" % (ext, idx)))):
        if f.endswith("_state.json") or f.endswith(".rec.json"):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        used.append(os.path.basename(f))
        for a in d.get("atoms_all", []):
            k = (round(a[0], 7), round(a[1], 7))
            if k not in seen_a:
                seen_a.add(k)
                atoms.append((a[0], a[1]))
        for r in d.get("rows_all", []):
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k)
                rows.append((r[0], r[1], r[2]))
    return dict(atoms=atoms, rows=rows), used


# ----------------------------------------------------------------------------- one (class, slot, r_c, r_t) run
def run(ext, idx, rc, tdeg, lp_time=600, cert_time=300, cert_rounds=3, eps_geo=0.003, depth=48, slab_fallback=True, log=print):
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(NODES, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    lpbox.EPS_GEO = eps_geo
    rc, tr = Fr(rc), t_of_deg(tdeg)
    tag = "basin207_%s_c%d_rc%s_t%s" % (ext, idx, str(rc).replace("/", "d"), str(tr).replace("/", "d"))
    lf = os.path.join(LOGS, tag + ".log")

    def L(*x):
        with open(lf, "a", encoding="utf-8") as fh:
            print(*x, file=fh, flush=True)
        log(*x)

    hyp, slots, a = basin_hyp(ext, idx, rc, tr)
    kx, ky = slots[idx]
    basin = dict(ext=ext, idx=idx, slot_centre=[str(kx), str(ky)], r_c=str(rc), t_r=str(tr), r_t_deg=math.degrees(2 * math.atan(float(tr))), a=str(a),
                 core="[c_p +- a]^2 axis-aligned; every unit square with |c - c_p|_inf <= r_c and |tan(theta/2)| <= t_r contains it (Lemma BASIN (i))")
    rec = dict(tag=tag, ext=ext, idx=idx, r_c=float(rc), r_c_rat=str(rc), t_r=str(tr), r_t_deg=basin["r_t_deg"], a=float(a), eps_geo=eps_geo, started=time.strftime("%Y-%m-%d %H:%M:%S"))
    warm, used, n_lp_rows, n_wit = RM.build_warm(ext)
    warm, used = warm_from_prev(ext, idx, warm, used)
    budget = 11 - len(slots)
    L("=== %s: slot %d at (%s, %s), r_c = %s, t_r = %s (%.3f deg), a = %.9f; warm %d atoms / %d rows from %s" % (tag, idx, float(kx), float(ky), float(rc), tr, basin["r_t_deg"], float(a), len(warm["atoms"]), len(warm["rows"]), used))
    t0 = time.time()
    res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=lp_time, max_iter=4000, out=None, log=lambda *x: None, prune=0, prune_cols=0,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=1200, max_rows_add=2500, fine_slack=99.0, alternate=True,
                     checkpoint=os.path.join(NODES, tag + "_state.json"))
    res["basin"] = basin
    json.dump(res, open(os.path.join(NODES, tag + ".json"), "w"))
    rec.update(lp_seconds=round(time.time() - t0, 1), tau=res["tau"], converged=res["converged"], budget=budget, n_rows=res.get("n_rows"), n_orbits=res.get("n_orbits"))
    L("    LP: tau = %.6f (budget %d, converged %s) in %.1f s" % (res["tau"], budget, res["converged"], rec["lp_seconds"]))
    if res["tau"] >= budget - 0.01:
        rec["verdict"] = "NO KILL (tau >= budget - 0.01)"
        return finish(rec, t0, L)
    base = os.path.join(CERTS, tag + ".json")
    t1 = time.time()
    v, hist = certify(res, hyp, base, basin, lf, L, rounds=cert_rounds, time_limit=cert_time)
    rec.update(certify=v, certify_rounds=hist, certify_seconds=round(time.time() - t1, 1))
    if v != "PASS":
        rec["verdict"] = "s0 certification FAILED (%s)" % v
        return finish(rec, t0, L)
    cj = json.load(open(base))
    rec["cert"] = dict(path=os.path.relpath(base, ROOT).replace("\\", "/"), atoms=len(cj["atoms"]), total=cj["total"], margin=budget - float(Fr(cj["total"])))
    par = os.path.join(CERTS, tag + ".param.json")
    v, dt, rep = param_verify(base, ext, par, lf, depth=depth)
    rec.update(param=v, param_seconds=dt, param_report=os.path.relpath(rep, ROOT).replace("\\", "/"), window=[str(S_LO), str(S0)])
    L("    verify_param over [%s, %s]: %s (%.1f s)" % (S_LO, S0, v, dt))
    if v != "PASS" and slab_fallback:
        par2 = os.path.join(CERTS, tag + ".g1.param.json")
        v2, dt2, rep2 = param_verify(base, ext, par2, lf, depth=depth, slo=S_G1)
        rec.update(param_g1=v2, param_g1_seconds=dt2, param_g1_report=os.path.relpath(rep2, ROOT).replace("\\", "/"))
        L("    verify_param over the G1 slab [%s, %s]: %s (%.1f s)" % (S_G1, S0, v2, dt2))
        if v2 == "PASS":
            rec.update(window=[str(S_G1), str(S0)], param_cert=os.path.relpath(par2, ROOT).replace("\\", "/"))
            rec["c2"] = c2(par2, tag + ".g1", lf, slo=S_G1)
            rec["verdict"] = "BASIN on the G1 slab" if all(x["result"] == "PASS" for x in rec["c2"]) else "C2-DISCREPANCY"
            return finish(rec, t0, L)
        rec["verdict"] = "window verification FAILED"
        return finish(rec, t0, L)
    if v != "PASS":
        rec["verdict"] = "window verification FAILED"
        return finish(rec, t0, L)
    rec["param_cert"] = os.path.relpath(par, ROOT).replace("\\", "/")
    rec["c2"] = c2(par, tag, lf)
    rec["verdict"] = "BASIN" if all(x["result"] == "PASS" for x in rec["c2"]) else "C2-DISCREPANCY"
    return finish(rec, t0, L)


def finish(rec, t0, L):
    rec["seconds"] = round(time.time() - t0, 1)
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(rec, open(os.path.join(NODES, rec["tag"] + ".rec.json"), "w"), indent=1)
    L("    => %s (%s s)" % (rec["verdict"], rec["seconds"]))
    return rec
