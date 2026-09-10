"""A180 -- the LEAF at a complete assignment: the multi-box case LP (A168 lp168 pattern) on the
role HULLS (bounding box of each role's surviving pieces: a sound superset), A135 exact cores,
certificate through A170's certwrap170.make_certificate_exact, checked by the FROZEN verify_case.py
(sha 521cb01f...).  Budget = 11 - #roles.  Gates: every role hull must carry an exact core (else
[P] "no core"), > 3 GB free physical and > 6144 MB available commit, box < 12 pythons (A182) before the
verifier is spawned.  Wall: LP cap + certificate cap + verifier timeout <= 1,500 s per node.
"""
import ctypes
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
sys.path.insert(0, os.path.join(ATT, "A168-cascade-fable", "code"))
import lp168 as LP                                               # noqa: E402  READ-ONLY (A168)
from lp168 import ExactHyp, cores_disjoint_exact, K, CW          # noqa: E402
from caselp import Box, solve_node, warm_from_result             # noqa: E402  READ-ONLY (A57)
import exactcore                                                 # noqa: E402  READ-ONLY (A135)

VERIFIER = LP.VERIFIER
VERIFIER_SHA = LP.VERIFIER_SHA


class MemStat(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem_gate(min_phys_mb=3072, min_commit_mb=6144):
    m = MemStat()
    m.dwLength = ctypes.sizeof(MemStat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    phys, commit = m.ullAvailPhys / 2 ** 20, m.ullAvailPageFile / 2 ** 20
    return (phys > min_phys_mb and commit > min_commit_mb), dict(avail_phys_mb=round(phys), avail_commit_mb=round(commit))


def n_python():
    """every python on the box, counted by IMAGE NAME (catches relative command lines: A182)."""
    try:
        cmd = ["powershell", "-NoProfile", "-Command",
               "(Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | Where-Object { $_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object).Count"]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()
        return int(out.splitlines()[-1])
    except Exception:                                            # noqa: BLE001
        return 99


def wait_box(ceiling=12, max_wait=1800, log=print):
    t0 = time.time()
    while True:
        n = n_python()
        ok, mem = mem_gate()
        if n < ceiling and ok:
            return True, dict(n_python=n, **mem)
        if time.time() - t0 > max_wait:
            return False, dict(n_python=n, **mem)
        log("    box busy (%d pythons, %s): waiting" % (n, mem))
        time.sleep(60)


def verify(cert_path, jobs=2, depth=56, timeout=600):
    cmd = [sys.executable, VERIFIER, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", "64", "--report", "--quiet"]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return -9, "verifier timeout %ss" % timeout


def role_box(h):
    return Box(h[0], h[1], h[2], h[3], h[4], h[5])


def lp_node(tag, hulls, budget, record_path, cap=600.0, cert_time=150.0, log=print):
    """hulls = {role: [x0,x1,y0,y1,th0,th1]}.  -> dict(verdict, ...)."""
    os.makedirs(CERTS, exist_ok=True)
    t0 = time.time()
    rec = dict(node=tag, budget=budget, cap=cap, roles=list(hulls), boxes={k: list(v) for k, v in hulls.items()})
    boxes = []
    for k, h in hulls.items():
        b = role_box(h)
        a, a0, ok = exactcore.exact_a(b)
        if a is None or not ok or float(a) <= 0:
            rec.update(verdict="[P] no exact core on the hull of %s (LP not run)" % k, wall_s=round(time.time() - t0, 1))
            return rec
        boxes.append(b)
    ok, gate = wait_box(log=log)
    rec["gate"] = gate
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    H = ExactHyp(boxes, [])
    rec["a_exact"] = H.a_exact
    dis = [cores_disjoint_exact(H.cores[i], H.cores[j])[0] for i in range(len(H.cores)) for j in range(i + 1, len(H.cores))]
    if not all(dis):
        rec.update(verdict="UNDECIDED(core gate: exact cores not certifiably disjoint)", wall_s=round(time.time() - t0, 1))
        return rec
    d = json.load(open(os.path.join(ROOT, record_path), encoding="utf-8"))
    warm = warm_from_result(d)
    warm["rows"] = warm["rows"][:14000]
    try:
        s = solve_node(K.S0, H, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900, out=None,
                       log=lambda *x: None, prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                       max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = s.get("tau")
    rec.update(tau=tau, eta=(tau - budget) if tau is not None else None, converged=bool(s.get("converged")),
               n_rows=s.get("n_rows"), kills=bool(tau is not None and tau < budget - 1e-6),
               kills_converged=bool(s.get("converged") and tau is not None and tau < budget - 1e-6),
               lp_s=round(time.time() - t0, 1))
    rec["window_transfer"] = "by dilation (Lemma B.0 + K0-WIDEN pad: the boxes are stated on F at s0)"
    verdict = "ALIVE(LP)" if not rec["kills"] else ("LP-dead unconverged (kill candidate)" if not rec["kills_converged"]
                                                    else "DEAD(LP, certificate pending)")
    if rec["kills_converged"]:
        out = os.path.join(CERTS, tag + ".json")
        scale = max(1.005, min(1.30, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
        cert = CW.make_certificate_exact(s, K.S_RAT, scale=scale, hyp=H)
        json.dump(cert, open(out, "w"), indent=0)
        tot = float(Fr(cert["total"]))
        rec["cert"] = os.path.relpath(out, ROOT).replace("\\", "/")
        rec["cert_total"] = tot
        if tot >= budget:
            rec["certified"] = "MARGIN"
        else:
            ok, _ = wait_box(log=log)
            rc, txt = verify(out, timeout=max(60, 1500 - (time.time() - t0)))
            tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
            rec["verifier"] = tail[:4]
            if rc != 0 and ("undecided" in txt or "hole" not in txt):
                for dp in (64, 72):
                    if time.time() - t0 > 1300:
                        break
                    rc, txt = verify(out, depth=dp, timeout=max(60, 1500 - (time.time() - t0)))
                    if rc == 0:
                        break
            rec["certified"] = "PASS" if rc == 0 else "FAIL"
            json.dump(dict(cert=out, result=rec["certified"], verifier=VERIFIER, verifier_sha=VERIFIER_SHA,
                           verifier_tail=rec["verifier"]), open(out.replace(".json", ".certify.json"), "w"), indent=1)
        if rec["certified"] == "PASS":
            verdict = "DEAD(LP)"
    rec["verdict"] = verdict
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def make_leaf(record_path, cap=600.0, log=print, max_lp=6):
    """the Search leaf function: LP at a complete assignment; at most `max_lp` LPs per page."""
    count = {"n": 0}

    def leaf(search, st):
        budget = 11 - len(st["roles"])
        if budget <= 0:
            return dict(lp=dict(verdict="[P] budget 0: all five free squares instantiated, geometry is the only leaf"))
        if count["n"] >= max_lp:
            return dict(lp=dict(verdict="[P] LP quota (%d) spent on this page" % max_lp))
        count["n"] += 1
        tag = (search.cls + "_" + st["label"]).replace("/", "_").replace("(", "").replace(")", "").replace(",", "")
        tag = tag.replace("+", "-").replace("=", "-").replace(":", "-").replace("@", "-")[:120]
        log("  LP leaf %s budget %d" % (st["label"], budget))
        r = lp_node(tag, st["roles"], budget, record_path, cap=cap, log=log)
        log("  LP: %s tau=%s (%.0f s)" % (r.get("verdict"), r.get("tau"), r.get("wall_s") or 0))
        v = r.get("verdict", "")
        return dict(lp=r, verdict=("DEAD" if v == "DEAD(LP)" else ("ALIVE(LP)" if v == "ALIVE(LP)" else "UNDECIDED")),
                    leaf=("LP certificate %s" % r.get("cert")) if v == "DEAD(LP)" else v)
    return leaf
