"""A193 -- probes on corners4 (k4_13) and k4_05 with the k0 toolkit.  READ-ONLY on every other attempt
(runtime patches in memory only: classes178.pins_of for the two k4 classes, journal182's directories).

    python probe193.py --cls corners4|k4_05 [--mode s0|window] [--root-lp 1] [--search 1] [--max-lp 4]
    python probe193.py --certify                      # phase B: certify the LP-dead leaves under verify_case_v5

Per class: (1) the frame + forced cells (Theorem FC on the window; at s0 also the cells whose extension is
k5_11 / k5_16, dead at s0 by A57's s0 trees, window form A57 G1 [P]); (2) the pins-only root LP with guard lines
at budget 7 (the K1 datum); (3) A182's assignment search from the root (pins + anonymous windowed meeters), chord
rows at every tree node, the no-room leaf and the windows + guard-line LP at every complete leaf; (4) records in
results/probe193_<cls>.jsonl, lpres_*.json, certs/.  One process; the LP in-process; the verifier a child.
"""
import argparse
import ctypes
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for d in (RES, LOGS, CERTS, os.path.join(RES, "journal")):
    os.makedirs(d, exist_ok=True)
for p in ("A180-forced-first-assignment", "A178-gallery-geometry", "A171-multibox-invariant", "A189-noroom",
          "A185-boxed-windows-clause", "A190-guardline-clause", "A144-guard-lines", "A161-chord-lane",
          "A57-shadow-trees", "A135-polycore-verifier"):
    sys.path.insert(0, os.path.join(ATT, p, "code"))

# ---------------------------------------------------------------- process discipline (A190's prio190 pattern)
BELOW_NORMAL = 0x4000
MINE = ("probe193", "A193")


def set_priority(mask=0xFFFF):
    try:
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, BELOW_NORMAL)
        k.SetProcessAffinityMask(h, ctypes.c_size_t(mask))
    except Exception:                                            # noqa: BLE001
        pass


class _MemStat(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem_gate(min_phys_mb=3072, min_commit_mb=6144):
    m = _MemStat()
    m.dwLength = ctypes.sizeof(_MemStat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    phys, commit = m.ullAvailPhys / 2 ** 20, m.ullAvailPageFile / 2 ** 20
    return (phys > min_phys_mb and commit > min_commit_mb), dict(avail_phys_mb=round(phys), avail_commit_mb=round(commit))


def _cmdlines():
    cmd = ["powershell", "-NoProfile", "-Command",
           "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ForEach-Object { $_.CommandLine }"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception:                                            # noqa: BLE001
        return None
    return [l for l in out.splitlines() if l.strip()]


def n_python():
    ls = _cmdlines()
    return 99 if ls is None else len([l for l in ls if "Claude Extensions" not in l and "windows-mcp" not in l])


def n_mine():
    ls = _cmdlines()
    return 99 if ls is None else len([l for l in ls if any(m in l for m in MINE)])


def wait_box(ceiling=12, own=0, max_wait=1800, log=print):
    t0 = time.time()
    while True:
        n = n_python()
        ok, mem = mem_gate()
        if n + own <= ceiling and ok:
            return True, dict(n_python=n, **mem)
        if time.time() - t0 > max_wait:
            return False, dict(n_python=n, **mem)
        log("    box busy (%d pythons + %d, %s): waiting" % (n, own, mem))
        time.sleep(60)


set_priority()

import assign180 as A                                            # noqa: E402  READ-ONLY (A180)
import assign182 as A2                                           # noqa: E402  READ-ONLY (A182)
import journal182 as J                                           # noqa: E402  READ-ONLY (A182)
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)
import classes178 as CL                                          # noqa: E402  READ-ONLY (A178)
import multibox as MB                                            # noqa: E402  READ-ONLY (A171)
import noroom189 as NR                                           # noqa: E402  READ-ONLY (A189)

J.RES, J.LOGS, J.JDIR = RES, LOGS, os.path.join(RES, "journal")   # journals under THIS attempt only
A.MAXF = 7                                                        # seven free squares in a k = 4 class

S0 = CL.S0
S_RAT = Fr(969271, 250000)
N = 11
D_CORNER, D_SLOT1 = 0.01, 0.025          # pin slack: (lambda_max - 1)(i + 1/2) = 0.0075 (corner), 0.0224 (BL(0,1))
PINS = {
    "corners4": [(0.5, 0.5), (0.5, S0 - 0.5), (S0 - 0.5, 0.5), (S0 - 0.5, S0 - 0.5)],
    "k4_05": [(0.5, 0.5), (0.5, 1.5), (0.5, S0 - 0.5), (S0 - 0.5, 0.5)],
}
S0_DEAD = ("k5_11", "k5_16")             # dead at s0 (A57's s0 shadow trees); window form = A57 G1 [P]

_pins_of0 = CL.pins_of


def _pins_of(cls):
    if cls in PINS:
        return [tuple(p) for p in PINS[cls]]
    return _pins_of0(cls)


CL.pins_of = _pins_of
MODE = {"mode": "s0"}
_forced_items0 = G.forced_items


def frame(cls):
    """[T] the completable unclipped non-pin cells with their extension class and where FC applies."""
    out = []
    for r in CL.forced_cells(cls):
        ext = r["extension"]
        r["fc_window"] = bool(r["usable"])
        r["fc_s0_only"] = (not r["usable"]) and ext in S0_DEAD
        r["fc_none"] = not (r["fc_window"] or r["fc_s0_only"])
        out.append(r)
    return out


def forced_items(cls, rec, s=S0):
    cells = []
    for r in frame(cls):
        if r["fc_window"] or (MODE["mode"] == "s0" and r["fc_s0_only"]):
            cells.append(dict(r))
    for r in cells:
        r["wbox"] = CL.widened_box(r["corner"], r["i"], r["j"], s)
        r["window"] = CL.meeter_window(r["corner"], r["i"], r["j"], s)
    return cells


G.forced_items = forced_items
A.G.forced_items = forced_items


def record(cls):
    pins = []
    for (kx, ky) in PINS[cls]:
        dp = D_SLOT1 if (abs(ky - 1.5) < 1e-9 or abs(kx - 1.5) < 1e-9) else D_CORNER
        pins.append(dict(kx=kx, ky=ky, dpin=dp, a=0.5 - dp))
    return dict(pins=pins, H=[], budget=N - len(pins), s=S0)


def emit(path, rec):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


# ---------------------------------------------------------------- guard lines for a pins (+ roles) node
def line_family(pins_xy, s=S_RAT):
    import guardline as GL                                       # READ-ONLY (A144)
    a_pin = Fr(1, 2) - Fr(1, 100) / GL.SQRT2_LO
    cand = []
    for (kx, ky) in pins_xy:
        cx, cy = Fr(round(kx * 10 ** 6), 10 ** 6), Fr(round(ky * 10 ** 6), 10 ** 6)
        cand += [("v", cx, "pin midline x"), ("h", cy, "pin midline y"), ("v", cx - a_pin, "pin core x0"),
                 ("v", cx + a_pin, "pin core x1"), ("h", cy - a_pin, "pin core y0"), ("h", cy + a_pin, "pin core y1")]
    for v in (Fr(3, 2), s - Fr(3, 2), Fr(1), s - 1, Fr(2), s - 2):
        cand += [("v", v, "slot line x"), ("h", v, "slot line y")]
    cand += [("h", Fr(k, 16) * s, "grid h %d/16" % k) for k in range(1, 16)]
    cand += [("v", Fr(k, 16) * s, "grid v %d/16" % k) for k in range(1, 16)]
    out, seen = [], set()
    for (o, off, tg) in cand:
        off = Fr(round(off * GL.LDEN), GL.LDEN)
        if not (Fr(0) < off < s) or (o, off) in seen:
            continue
        seen.add((o, off))
        out.append(GL.Line(o, off, tg))
    return out


def select_lines(lines, res_support, k=10):
    """the k lines with the largest offline violation on a dual support (or the pin/slot lines first)."""
    import guardline as GL
    scored = []
    for L in lines:
        lhs = 0.0
        for p in (res_support or []):
            lhs += GL.chord_float(0.5, float(p["theta"]), L.offset_of(float(p["cx"]), float(p["cy"]))) * float(p.get("y", 0.0))
        pri = 0 if L.tag.startswith(("pin midline", "slot line")) else (1 if L.tag.startswith("pin core") else 2)
        scored.append((-(lhs - float(L.cost)), pri, L))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in scored[:k]]


# ---------------------------------------------------------------- (2) the pins-only root LP with guard lines (K1 datum)
def root_lp(cls, cap=420.0, k_lines=10):
    import emit190 as E                                          # READ-ONLY (A190)
    import guardlp                                               # READ-ONLY (A144)
    import guardline as GL
    from caselp import Box, warm_from_result                     # READ-ONLY (A57)
    from warm57 import merged_warm                               # READ-ONLY (A57)
    t0 = time.time()
    rec = record(cls)
    boxes = [Box(p["kx"] - p["dpin"], p["kx"] + p["dpin"], p["ky"] - p["dpin"], p["ky"] + p["dpin"], 0.0, 0.0) for p in rec["pins"]]
    H = E.ExactHyp(boxes, [])
    budget = N - len(boxes)
    fam = line_family(PINS[cls])
    rows = []
    for L in fam:
        terms = [GL.minchord_box(b, L, a=Fr(1, 2))["lo"] for b in boxes]
        rows.append(dict(rhs=S_RAT - sum(terms, Fr(0))))
    fam = guardlp.attach_costs(fam, rows)
    warm = merged_warm(cls, max_rows=14000)[0]
    support = warm.get("packing") or []
    lines = select_lines(fam, support, k=k_lines)
    ok, mem = wait_box(own=0)
    out = dict(kind="root_lp", cls=cls, budget=budget, n_pins=len(boxes), a_exact=H.a_exact, exact_ok=H.exact_ok,
               lines=[dict(line=L.to_json(), rhs=float(L.rhs_exact)) for L in lines], gate=mem, cap=cap,
               when=time.strftime("%Y-%m-%d %H:%M"))
    if not ok:
        out.update(verdict="[P] box gate (LP not run)")
        return out
    try:
        res, z = E.solve_guarded(H, budget, lines, warm, cap)
    except Exception as e:                                       # noqa: BLE001
        out.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return out
    tau = res.get("tau")
    json.dump(dict(tau=tau, converged=res.get("converged"), atoms_all=res.get("atoms_all"), rows_all=res.get("rows_all"),
                   packing=res.get("packing"), n_rows=res.get("n_rows"), minmass=res.get("minmass"), hyp=res.get("hyp"),
                   z=z, lines=[L.to_json() for L in lines], budget=budget, form="pins-only ExactHyp + guard lines (A190)"),
              open(os.path.join(RES, "lpres_root_%s.json" % cls), "w"))
    out.update(tau=tau, eta=(tau - budget) if tau is not None else None, converged=bool(res.get("converged")),
               minmass=res.get("minmass"), n_rows=res.get("n_rows"), support=len(res.get("packing") or []),
               z=[dict(line=L.tag, off=float(L.off), orient=L.orient, z=zz) for L, zz in zip(lines, z)],
               n_active=sum(1 for zz in z if zz > 1e-6), kills=bool(tau is not None and tau < budget - 1e-3),
               packing_rows=[[q["cx"], q["cy"], q["theta"], q["y"]] for q in (res.get("packing") or [])][:200],
               wall_s=round(time.time() - t0, 1))
    out["verdict"] = "LP-dead (kill candidate, v5 pending)" if out["kills"] else "ALIVE(LP, guard lines)"
    return out


# ---------------------------------------------------------------- (3) the leaf: no-room + windows/guard-line LP
def node_pieces(nd):
    out = {}
    for k, mb in nd.boxes.items():
        ps = []
        for (bn, r) in mb.pieces:
            ps.append((float(r[0]), float(r[1]), float(r[2]), float(r[3]), MB.deg_of_t(bn.t0), MB.deg_of_t(bn.t1)))
        out[k] = ps
    return out


def make_certificate_v5w(res, hyp, lines, z, scale, tag):
    """A185's v4 certificate (windows + cores) with A190's `guardlines` field: read by verify_case_v5 ONLY."""
    import winlp185 as W
    cert = W.make_certificate_v4(res, S_RAT, hyp, scale=scale)
    gls, ltot = [], Fr(0)
    for L, zz in zip(lines, z):
        if zz <= 1e-10:
            continue
        zq = Fr(math.ceil(zz * scale * 10 ** 6), 10 ** 6)
        gls.append(dict(orient=L.orient, off=str(L.off), z=str(zq), rhs=str(L.rhs_exact), tag=L.tag,
                        z_lp=float(zz), rhs_float=float(L.rhs_exact)))
        ltot += zq * L.rhs_exact
    cert["format"] = "case-measure-certificate-v5-guardlines"
    cert["hypotheses"]["guardlines"] = gls
    cert["total_v5"] = str(Fr(cert["total"]) + ltot)
    cert["claim"] = ("Theorem W + Theorem G (docs/proofs/boxed_windows.md, guardline_clause.md): with mu = atoms + the "
                     "declared guard-line densities, every non-exempt free pose and every non-exempt_i pose of each window "
                     "has mu >= 1 and SUM w + SUM z*rhs* < budget_v4 = %d; a PASS of verify_case_v5 kills the node "
                     "[C under v5 ONLY -- the frozen v1 chain and A185's v4 do not read `guardlines`]" % hyp.budget4)
    cert["provenance"]["method"] = ("A193 probe193 (A185 winlp185 WindowsHyp + A144 guardlp columns, A57 caselp.solve_node), "
                                    "node %s; " % tag) + cert["provenance"]["method"]
    return cert


def run_v5(cert_path, timeout, depth=56, max_w=64, log=print):
    verifier = os.path.join(ATT, "A190-guardline-clause", "code", "verify_case_v5.py")
    cmd = [sys.executable, verifier, cert_path, "--jobs", "1", "--depth", str(depth), "--max-witnesses", str(max_w),
           "--report", "--quiet"]
    t0 = time.time()
    while n_mine() >= 2 and time.time() - t0 < timeout:
        log("    A193 already runs %d pythons: waiting for the <= 2 rule" % n_mine())
        time.sleep(30)
    ok, mem = wait_box(own=1, max_wait=max(60, min(600, timeout / 2)), log=log)
    if not ok:
        # the box is at the lab ceiling: run the FROZEN verifier in THIS process (jobs 1 is inline in
        # verify_case_v5.main; no new python), the wall enforced by the caller's deadline only
        import contextlib
        import io
        import verify_case_v5 as V5                              # READ-ONLY (A190), frozen
        log("    box at the ceiling (%s): verifier in-process" % mem)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = V5.main(cmd[2:])
        return rc, buf.getvalue()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    try:
        out, _ = p.communicate(timeout=max(30, timeout))
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        return -9, "verifier timeout %.0fs (process tree killed)" % timeout


def certify_leaf(lp_path, tag, deadline, rounds=1, verify_cap=360.0, log=print):
    """re-solve-free certification of a stored LP result (phase B): round 0 = the stored LP; a FAIL with witnesses
    feeds ONE re-solve (A190's loop, one round) inside the wall."""
    import winlp185 as W
    import guardlp
    import guardline as GL
    from caselp import solve_node, warm_from_result
    d = json.load(open(lp_path, encoding="utf-8"))
    wroles = [W.WRole(k, [tuple(p) for p in v]) for k, v in d["roles_pieces"].items()]
    H = W.WindowsHyp(wroles)
    lines = [GL.Line(e["orient"], Fr(e["off"]), e.get("tag", "")) for e in d["lines"]]
    lines = guardlp.attach_costs(lines, [dict(rhs=Fr(e["rhs"])) for e in d["lines"]])
    res = dict(tau=d["tau"], converged=d["converged"], atoms_all=d["atoms_all"], rows_all=d["rows_all"], packing=d["packing"])
    z = list(d["z"])
    budget = H.budget4
    out = os.path.join(CERTS, tag + ".json")
    log_ = []
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = max(1.005, min(1.03, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
        cert = make_certificate_v5w(res, H, lines, z, scale, tag)
        json.dump(cert, open(out, "w"), indent=0)
        tot = float(Fr(cert["total_v5"]))
        if tot >= budget:
            log_.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", log_, out
        rc, txt = run_v5(out, min(verify_cap, deadline - time.time()), log=log)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "free clause", "window clause", "MALFORMED", "  guard", "Traceback", "ValueError"))]
        log_.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:12], tail=txt[-600:]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=log_, result="PASS", verifier="verify_case_v5 (A190)", label="[C] under v5 only"),
                      open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", log_, out
        if rc == 2:
            json.dump(dict(cert=out, rounds=log_, result="REJECTED"), open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "REJECTED", log_, out
        if rd == rounds or rc == -9 or time.time() > deadline - 120:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            break
        extra = []
        for w in json.load(open(wf))["witnesses"]:
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            extra.append((p["cx_float"], p["cy_float"], th))
            for dd in (0.002, 0.005):
                for dx, dy in ((dd, 0), (-dd, 0), (0, dd), (0, -dd), (dd, dd), (-dd, -dd), (dd, -dd), (-dd, dd)):
                    extra.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
                for dth in (dd, -dd):
                    extra.append((p["cx_float"], p["cy_float"], th + dth))
        ok, _ = wait_box(own=0, log=log)
        with guardlp.installed(lines):
            res = solve_node(S0, H, budget, sym_kind="C1", warm=warm_from_result(res),
                             time_limit=min(240, max(30, deadline - time.time() - 150)), out=None, log=lambda *x: None,
                             extra_rows=extra, neigh_rows=0, col_stop_iter=0, fine_slack=99.0, max_iter=1000)
            z = [float(v) for v in guardlp._ACTIVE["z"]] if guardlp._ACTIVE["z"] is not None else [0.0] * len(lines)
        if not (res["tau"] < budget - 1e-6):
            log_.append(dict(round=rd + 1, tau=res["tau"], result="re-solve lost the kill"))
            break
    json.dump(dict(cert=out, rounds=log_, result="FAIL", verifier="verify_case_v5 (A190)"),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log_, out


def leaf_lp(cls, tag, nd, st, cap=300.0, k_lines=10, warm=None, log=print):
    """the windows + guard-line LP at the leaf's fixed point (A185 WindowsHyp, A144 guardlp columns)."""
    import winlp185 as W
    import guardlp
    import guardline as GL
    from caselp import solve_node
    t0 = time.time()
    pieces = node_pieces(nd)
    wroles = [W.WRole(k, v) for k, v in pieces.items()]
    H = W.WindowsHyp(wroles)
    rec = dict(kind="leaf_lp", cls=cls, node=tag, label=st["label"], n_roles=H.r, n_cores=H.m, attached=H.rc,
               budget_v4=H.budget4, free=H.free, core_kind={w.name: w.core_kind for w in wroles},
               a_core={w.name: (float(w.core.a) if w.core else None) for w in wroles},
               n_pieces={k: len(v) for k, v in pieces.items()}, cap=cap)
    fam = line_family(PINS[cls])
    # rhs = s - SUM over UNATTACHED cores (none when every cored role is windowed): re-derived by the verifier
    unatt = [w for i, w in enumerate(wroles) if w.core is not None and H.attach.get(i) is None]
    rows = []
    for L in fam:
        terms = [GL.minchord_box(w.bbox, L, a=Fr(1, 2))["lo"] for w in unatt]
        rows.append(dict(rhs=S_RAT - sum(terms, Fr(0))))
    fam = guardlp.attach_costs(fam, rows)
    lines = select_lines(fam, (warm or {}).get("packing"), k=k_lines)
    rec["lines"] = [dict(line=L.to_json(), rhs=float(L.rhs_exact)) for L in lines]
    ok, mem = wait_box(own=0, log=log)
    rec["gate"] = mem
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    try:
        with guardlp.installed(lines):
            s = solve_node(S0, H, H.budget4, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900, out=None,
                           log=lambda *x: None, prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                           max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
            z = [float(v) for v in guardlp._ACTIVE["z"]] if guardlp._ACTIVE["z"] is not None else [0.0] * len(lines)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = s.get("tau")
    lp_path = os.path.join(RES, "lpres_%s.json" % tag)
    json.dump(dict(tau=tau, converged=s.get("converged"), atoms_all=s.get("atoms_all"), rows_all=s.get("rows_all"),
                   packing=s.get("packing"), n_rows=s.get("n_rows"), minmass=s.get("minmass"), hyp=s.get("hyp"),
                   z=z, lines=[dict(orient=L.orient, off=str(L.off), rhs=str(L.rhs_exact), tag=L.tag) for L in lines],
                   roles_pieces=pieces, budget_v4=H.budget4, cls=cls, label=st["label"]),
              open(lp_path, "w"))
    rec.update(tau=tau, eta=(tau - H.budget4) if tau is not None else None, converged=bool(s.get("converged")),
               minmass=s.get("minmass"), n_rows=s.get("n_rows"), support=len(s.get("packing") or []),
               z=[dict(line=L.tag, off=float(L.off), orient=L.orient, z=zz) for L, zz in zip(lines, z)],
               n_active=sum(1 for zz in z if zz > 1e-6), lp_s=round(time.time() - t0, 1),
               kills=bool(tau is not None and tau < H.budget4 - 1e-6),
               kills_converged=bool(s.get("converged") and tau is not None and tau < H.budget4 - 1e-6),
               packing_rows=[[p["cx"], p["cy"], p["theta"], p["y"]] for p in (s.get("packing") or [])][:400],
               lpres=os.path.relpath(lp_path, ROOT).replace("\\", "/"))
    rec["verdict"] = ("DEAD(LP, v5 certificate pending)" if rec["kills_converged"]
                      else ("LP-dead unconverged (kill candidate, v5)" if rec["kills"] else "ALIVE(LP, windows + guard lines)"))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def make_leaf(cls, out_path, cap, max_lp, warm, noroom_s, log):
    count = {"n": 0}

    def leaf(search, st):
        nd = st.get("nd")
        k = len(st["roles"])
        tag = ("%s_%s" % (cls, st["label"])).replace("/", "_").replace("(", "").replace(")", "").replace(",", "")
        tag = tag.replace("+", "-").replace("=", "-").replace(":", "-").replace("@", "-")[:120]
        res = dict(k=k, m=N - k, label=st["label"])
        # (a) the NO-ROOM leaf at the fixed point (Lemma 1; the meeter roles have empty K' -- recorded either way)
        t0 = time.time()
        if nd is not None and not getattr(nd, "replayed", False) and N - k > 0:
            try:
                nr = NR.noroom(st["roles"], budget=dict(total_deadline=noroom_s, lane_deadline=min(60.0, noroom_s / 4)),
                               name=tag, nd=nd)
            except Exception as e:                               # noqa: BLE001
                nr = dict(verdict="ERROR", reason=repr(e)[:200])
            res["noroom"] = {kk: v for kk, v in nr.items() if kk in ("verdict", "bound", "reason", "seconds", "pocket_area")}
            res["noroom"]["n_pockets"] = len(nr.get("pockets") or [])
            log("  NO-ROOM %s: %s (%.0f s) %s" % (st["label"][-50:], nr.get("verdict"), time.time() - t0, nr.get("reason", "")[:80]))
            emit(out_path, dict(kind="noroom", cls=cls, node=tag, label=st["label"], **{kk: v for kk, v in nr.items() if kk != "lanes"}))
            if nr.get("verdict") == "DEAD":
                return dict(verdict="DEAD", leaf="NO-ROOM leaf: %s" % nr.get("reason"), noroom=res["noroom"])
        # (b) the windows + guard-line LP
        if count["n"] >= max_lp:
            res["lp"] = dict(verdict="[P] LP quota (%d) spent" % max_lp)
            emit(out_path, dict(kind="leaf_skipped", cls=cls, node=tag, label=st["label"], k=k))
            return dict(verdict="UNDECIDED", leaf="[P] LP quota spent", **res)
        if nd is None or getattr(nd, "replayed", False):
            nd2, info = G.run_node(st["roles"], corners=st.get("corners") or None, nsub=4, refine=2, label=tag)
            if nd2 is None:
                return dict(verdict="DEAD", leaf="pair leaf at re-normalise: %s" % info.get("dead"))
            nd = nd2
        count["n"] += 1
        log("  LP leaf %s (%d roles)" % (st["label"][-60:], k))
        r = leaf_lp(cls, tag, nd, st, cap=cap, warm=warm, log=log)
        emit(out_path, r)
        log("  LP: %s tau=%s / b4=%s (%.0f s)" % (r.get("verdict"), r.get("tau"), r.get("budget_v4"), r.get("wall_s") or 0))
        res["lp"] = {kk: r.get(kk) for kk in ("verdict", "tau", "budget_v4", "converged", "n_active", "wall_s", "lpres")}
        v = r.get("verdict", "")
        return dict(verdict=("DEAD(LP pending v5)" if v.startswith("DEAD") else ("ALIVE(LP)" if v.startswith("ALIVE") else "UNDECIDED")),
                    leaf=v, **res)
    return leaf


def summarise(tree):
    c = dict(nodes=0, dead=0, alive=0, undecided=0, leaves=[])

    def walk(t):
        if t is None:
            return
        c["nodes"] += 1
        v = t.get("verdict", "")
        if "children" not in t:
            c["leaves"].append(dict(label=t.get("label"), verdict=v, leaf=str(t.get("leaf"))[:160]))
            if v.startswith("DEAD"):
                c["dead"] += 1
            elif v.startswith("ALIVE"):
                c["alive"] += 1
            else:
                c["undecided"] += 1
        for ch in t.get("children") or []:
            walk(ch)
    walk(tree)
    return c


def run_search(cls, a, out_path, log):
    from warm57 import merged_warm
    rec = record(cls)
    warm = merged_warm(cls, max_rows=14000)[0]
    leaf = make_leaf(cls, out_path, a.lp_cap, a.max_lp, warm, a.noroom_s, log)
    jn = J.Journal("%s_%s" % (cls, MODE["mode"]), wall=a.wall)
    log("   journal: %d nodes, %d subtrees, %d lanes on disk" % (len(jn.nodes), len(jn.subtrees), len(jn.lanes)))
    S = A2.Search(rec, cls, jn, sharp=a.sharp, chords=1, lanes=1, lane_s=a.lane_s, commit_branches=0,
                  nsub=4, refine=2, log=log, max_nodes=a.max_nodes, deadline=a.deadline, leaf=leaf,
                  refine_opts=1, side=0.36, max_combos=a.max_combos)
    t0 = time.time()
    try:
        r = S.run()
    except Exception as ex:                                      # noqa: BLE001
        import traceback
        traceback.print_exc()
        r = dict(verdict="ERROR", leaf=str(ex)[:200], tree=None)
    jn.idle()
    row = dict(kind="search", cls=cls, mode=MODE["mode"], verdict=r["verdict"], leaf=r.get("leaf"), n_nodes=S.n_nodes,
               n_fresh=S.n_fresh, n_replayed=jn.n_replayed, compute_s=round(S.compute_s, 1), seconds=round(time.time() - t0, 1),
               forced=[dict(cell=c, extension=it.get("extension"), fc_window=it.get("fc_window"), fc_s0_only=it.get("fc_s0_only"))
                       for c, it in S.items.items()],
               summary=summarise(r.get("tree")), max_nodes=a.max_nodes, deadline=a.deadline,
               journal=os.path.relpath(jn.path, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    json.dump(dict(row=row, tree=r.get("tree"), steps=S.steps), open(os.path.join(RES, "tree_%s_%s.json" % (cls, MODE["mode"])), "w"), indent=0)
    emit(out_path, row)
    log("== %s search: %s (%d nodes, %d fresh, %.0f s) %s" % (cls, r["verdict"], S.n_nodes, S.n_fresh, time.time() - t0, r.get("leaf") or ""))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="corners4")
    ap.add_argument("--mode", default="s0", help="s0: k5_11/k5_16-extension cells forced too; window: FC only")
    ap.add_argument("--root-lp", type=int, default=1)
    ap.add_argument("--search", type=int, default=1)
    ap.add_argument("--root-cap", type=float, default=420.0)
    ap.add_argument("--lp-cap", type=float, default=300.0)
    ap.add_argument("--max-lp", type=int, default=4)
    ap.add_argument("--max-nodes", type=int, default=150)
    ap.add_argument("--deadline", type=float, default=2400.0, help="search compute seconds")
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--sharp", type=int, default=0)
    ap.add_argument("--lane-s", type=float, default=30.0)
    ap.add_argument("--max-combos", type=int, default=40)
    ap.add_argument("--noroom-s", type=float, default=240.0)
    ap.add_argument("--certify", action="store_true")
    ap.add_argument("--certify-wall", type=float, default=1500.0)
    ap.add_argument("--frame-only", action="store_true")
    a = ap.parse_args()
    MODE["mode"] = a.mode
    out_path = os.path.join(RES, "probe193_%s.jsonl" % (a.cls if not a.certify else "certify"))

    def log(s):
        print(s, flush=True)

    if a.certify:
        for cls in ("corners4", "k4_05"):
            for ln in open(os.path.join(RES, "probe193_%s.jsonl" % cls), encoding="utf-8"):
                if not ln.strip():
                    continue
                r = json.loads(ln)
                if r.get("kind") != "leaf_lp" or not r.get("kills"):
                    continue
                tag = r["node"]
                if os.path.exists(os.path.join(CERTS, tag + ".certify.json")):
                    continue
                t0 = time.time()
                log("== certify %s (tau %s / b4 %s, converged %s)" % (tag, r.get("tau"), r.get("budget_v4"), r.get("converged")))
                v, lg, path = certify_leaf(os.path.join(ROOT, r["lpres"]), tag, t0 + a.certify_wall, log=log)
                emit(out_path, dict(kind="certify", cls=cls, node=tag, label=r.get("label"), tau=r.get("tau"), budget_v4=r.get("budget_v4"),
                                    certified=v, cert_log=lg, cert=os.path.relpath(path, ROOT).replace("\\", "/"),
                                    verdict=("DEAD(LP, v5 certified) [C under v5 ONLY]" if v == "PASS" else "LP-dead, v5 certificate %s" % v),
                                    wall_s=round(time.time() - t0, 1), when=time.strftime("%Y-%m-%d %H:%M")))
                log("== %s: %s (%.0f s)" % (tag, v, time.time() - t0))
        return
    fr = frame(a.cls)
    emit(out_path, dict(kind="frame", cls=a.cls, mode=a.mode, pins=PINS[a.cls],
                        cells=[{k: v for k, v in r.items() if k in ("cell", "extension", "status", "fc_window", "fc_s0_only", "fc_none", "is_corner")} for r in fr],
                        when=time.strftime("%Y-%m-%d %H:%M")))
    for r in fr:
        log("  %-9s ext %-8s %s" % (r["cell"], r["extension"], "FC on the window" if r["fc_window"] else ("FC at s0 only (A57 s0 tree; window = G1 [P])" if r["fc_s0_only"] else "NOT forced (extension open)")))
    if a.frame_only:
        return
    if a.root_lp:
        r = root_lp(a.cls, cap=a.root_cap)
        emit(out_path, r)
        log("== %s root LP (pins only + guard lines): tau %s / budget %s conv=%s active lines %s (%.0f s)" % (
            a.cls, r.get("tau"), r.get("budget"), r.get("converged"), r.get("n_active"), r.get("wall_s") or 0))
    if a.search:
        run_search(a.cls, a, out_path, log)


if __name__ == "__main__":
    main()
