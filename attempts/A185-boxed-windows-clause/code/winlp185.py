"""A185 -- the multi-box case LP with per-square POSE WINDOWS (Theorem W, docs/proofs/boxed_windows.md).

A boxed ROLE (name + surviving pieces, A168/A181/A183 or A182's journal capture) contributes
  * its WINDOW rows: every placement whose pose lies in one of its pieces (kept with an outward margin
    EPS_WC / EPS_WT so the certificate covers the closed window) must have mass >= 1, exempt only when it
    meets the core ATTACHED TO ANOTHER window (never its own, never an unattached core);
  * its CORE (A183 `grow_core` of the union-box exact core inside K'(role); else the role's certified AXIS
    square inside K'; else none): it exempts the FREE rows and the other windows' rows.
Budget b4 = n - #cores + #attached = n when every role is windowed and cored; the FREE rows (v1's) are kept
only when f = n - #roles > 0.  The certificate carries v1's fields (budget = n - #cores, for v1's loader)
plus `hypotheses.windows` and is checked by verify_case_v4 ONLY -- a kill here is [C] under v4.
"""
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
CERTS = os.path.join(BASE, "certs")
os.makedirs(CERTS, exist_ok=True)
sys.path.insert(0, HERE)
import prio185                                                   # noqa: E402,F401
sys.path.insert(0, os.path.join(ATT, "A168-cascade-fable", "code"))
import cas168 as K                                               # noqa: E402  READ-ONLY (A168)
import roles168 as R                                             # noqa: E402  READ-ONLY (A168)
import lp168 as L                                                # noqa: E402  READ-ONLY (A168)
import lp183 as L83                                              # noqa: E402  READ-ONLY (A183)
import exactcore as EC                                           # noqa: E402  READ-ONLY (A135)
import numpy as np                                               # noqa: E402
from caselp import (Box, Core, Hyp, solve_node, warm_from_result,   # noqa: E402  READ-ONLY (A57)
                    EPS_CORE, t_lo, t_hi, XDEN)
from lpbox import centre_range                                   # noqa: E402  READ-ONLY (A57)

VERIFIER = os.path.join(HERE, "verify_case_v4.py")
EPS_WC = 2e-3          # centre margin: rows this close OUTSIDE a piece are still kept (closed window covered)
EPS_WT = 0.3           # tilt margin, degrees (> the fine oracle step)
N = 11


def q_dn(x):
    return Fr(math.floor(x * XDEN) - 1, XDEN)


def q_up(x):
    return Fr(math.ceil(x * XDEN) + 1, XDEN)


# ===================================================================== roles -> windows + cores
class WRole:
    """a windowed role: name, pieces (caselp.Box, degrees), bbox, core (Core or None) and how it was obtained."""

    def __init__(self, name, pieces):
        self.name, self.pieces = name, [Box(*p) if not isinstance(p, Box) else p for p in pieces]
        P = self.pieces
        self.bbox = Box(min(b.x0 for b in P), max(b.x1 for b in P), min(b.y0 for b in P), max(b.y1 for b in P),
                        min(b.th0 for b in P), max(b.th1 for b in P))
        self.core, self.core_kind = None, "none"
        k = self.bbox.core()
        if k is not None:
            try:
                a, _a0, ok = EC.exact_a(self.bbox)
            except Exception:                                    # noqa: BLE001
                a, ok = None, False
            if ok and a is not None and a > 0:
                g, okk = L83.grow_core(Core(k.kx, k.ky, k.tm, a, self.bbox), P)
                self.core, self.core_kind = g, ("grown" if okk else "union-exact")
        if self.core is None:
            try:
                role = R.Role(name, P)
                kx, ky, a = role.axis
                if a > 0:
                    self.core, self.core_kind = Core(Fr(kx), Fr(ky), Fr(0), Fr(a), self.bbox), "axis-in-K'"
            except Exception:                                    # noqa: BLE001
                pass
        A = np.array([(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in P], dtype=float)
        self.PX0, self.PX1, self.PY0, self.PY1, self.TH0, self.TH1 = (A[:, k] for k in range(6))

    def tilt_mask(self, th_deg):
        m = np.zeros(len(self.PX0), dtype=bool)
        for t in (th_deg, th_deg + 90.0, th_deg - 90.0):
            m |= (self.TH0 - EPS_WT <= t) & (t <= self.TH1 + EPS_WT)
        return m

    def tilt_ok(self, th_deg):
        m = self.tilt_mask(th_deg)
        return list(zip(self.PX0[m], self.PX1[m], self.PY0[m], self.PY1[m]))

    def inside_many(self, C, th_deg):
        """mask over the centres C (m,2): pose in some piece (tilt within EPS_WT, centre within EPS_WC)."""
        m = self.tilt_mask(th_deg)
        if not m.any():
            return np.zeros(len(C), dtype=bool)
        x, y = C[:, 0][:, None], C[:, 1][:, None]
        return ((x >= self.PX0[m][None, :] - EPS_WC) & (x <= self.PX1[m][None, :] + EPS_WC) &
                (y >= self.PY0[m][None, :] - EPS_WC) & (y <= self.PY1[m][None, :] + EPS_WC)).any(1)


class WindowsHyp(Hyp):
    def __init__(self, wroles, n=N):
        self.wroles = list(wroles)
        self.boxes = [w.bbox for w in self.wroles if w.core is not None]
        self.cores = [w.core for w in self.wroles if w.core is not None]
        self.nofams = []
        self.attach = {}
        j = 0
        for i, w in enumerate(self.wroles):
            if w.core is not None:
                self.attach[i] = j
                j += 1
        self.n = n
        self.m, self.r, self.rc = len(self.cores), len(self.wroles), len(self.attach)
        self.budget4 = n - self.m + self.rc
        self.free = n - self.r - (self.m - self.rc)
        self.use_free = self.free > 0

    def keep_window(self, C, theta):
        th_deg = math.degrees(theta) % 90.0
        keep = np.zeros(len(C), dtype=bool)
        for i, w in enumerate(self.wroles):
            inwin = w.inside_many(C, th_deg)
            if not inwin.any():
                continue
            own = self.attach.get(i)
            for j, c in enumerate(self.cores):
                if j != own:
                    inwin &= ~(c.depth_many(C, theta) > EPS_CORE)
            keep |= inwin
        return keep

    def ok_many(self, C, theta):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        keep = Hyp.ok_many(self, C, theta) if self.use_free else np.zeros(len(C), dtype=bool)
        return keep | self.keep_window(C, theta)

    def shell_points(self, theta, s):
        pts = [Hyp.shell_points(self, theta, s)] if self.use_free else []
        th_deg = math.degrees(theta) % 90.0
        for w in self.wroles:
            for (x0, x1, y0, y1) in w.tilt_ok(th_deg):
                nx = max(4, min(40, int((x1 - x0) / 0.01) + 1))
                ny = max(4, min(40, int((y1 - y0) / 0.01) + 1))
                X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny), indexing="ij")
                pts.append(np.stack([X.ravel(), Y.ravel()], 1))
                for d in (1e-4, EPS_WC):
                    xs = np.linspace(x0 - d, x1 + d, nx); ys = np.linspace(y0 - d, y1 + d, ny)
                    pts.append(np.stack([xs, np.full(nx, y0 - d)], 1)); pts.append(np.stack([xs, np.full(nx, y1 + d)], 1))
                    pts.append(np.stack([np.full(ny, x0 - d), ys], 1)); pts.append(np.stack([np.full(ny, x1 + d), ys], 1))
        if not pts:
            return np.zeros((0, 2))
        P = np.vstack(pts)
        lo, hi = centre_range(s, theta)
        return P[(P[:, 0] >= lo) & (P[:, 0] <= hi) & (P[:, 1] >= lo) & (P[:, 1] <= hi)]

    def to_json(self):
        return dict(boxes=[b.to_json() for b in self.boxes], nofams=[], cores=[c.to_json() for c in self.cores],
                    windows=[dict(name=w.name, core=self.attach.get(i), core_kind=w.core_kind, n_pieces=len(w.pieces))
                             for i, w in enumerate(self.wroles)],
                    budget_v4=self.budget4, free=self.free)


# ===================================================================== certificate (v4 fields)
def make_certificate_v4(res, s_rat, hyp, scale=1.03, denom_pos=10 ** 6, denom_w=10 ** 6):
    s = Fr(s_rat)
    seen, atoms, weights = {}, [], []
    for (x, y, w) in res["atoms_all"]:
        if w <= 1e-10:
            continue
        p = (Fr(round(x * denom_pos), denom_pos), Fr(round(y * denom_pos), denom_pos))
        wq = Fr(math.ceil(w * scale * denom_w), denom_w)
        if p in seen:
            weights[seen[p]] += wq
        else:
            seen[p] = len(atoms); atoms.append(p); weights.append(wq)
    total = sum(weights, Fr(0))
    wins = []
    for i, w in enumerate(hyp.wroles):
        # the pieces' float bounds are EXACT binary rationals and are what grow_core / vertex_ok certified
        # the core against; the window carries them verbatim (t via A57's outward t_lo/t_hi, as vertex_ok)
        pieces = [dict(x0=str(Fr(b.x0)), x1=str(Fr(b.x1)), y0=str(Fr(b.y0)), y1=str(Fr(b.y1)),
                       t0=str(t_lo(b.th0)), t1=str(t_hi(b.th1))) for b in w.pieces]
        wins.append(dict(name=w.name, core=hyp.attach.get(i), pieces=pieces, deg=[w.bbox.th0, w.bbox.th1],
                         core_kind=w.core_kind))
    return dict(format="case-measure-certificate-v4-windows", n=hyp.n, s=str(s), budget=hyp.n - hyp.m,
                budget_v4=hyp.budget4, atoms=[[str(p[0]), str(p[1])] for p in atoms],
                weights=[str(x) for x in weights], total=str(total),
                hypotheses=dict(cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                                            box=c.box.to_json() if c.box else None) for c in hyp.cores],
                                nofams=[], windows=wins),
                claim=("Theorem W (docs/proofs/boxed_windows.md): every non-exempt free pose and every non-exempt_i "
                       "pose of each window has mu >= 1 and total < budget_v4 = %d; a PASS of verify_case_v4 kills "
                       "the node [C under v4 ONLY -- the frozen v1 chain does not read `windows`]" % hyp.budget4),
                provenance=dict(method="A185 winlp185 (caselp.solve_node with WindowsHyp), weights x %.4f rounded up "
                                       "to 1/%d, atoms rounded to 1/%d; window pieces = the roles' exact float bounds (t via A57 "
                                       "t_lo/t_hi)" % (scale, denom_w, denom_pos),
                                lp_tau=res["tau"], eps_core=EPS_CORE, eps_wc=EPS_WC, eps_wt=EPS_WT))


def run_v4(cert_path, timeout, depth=56, max_w=64):
    """verify_case_v4 in ONE child process (jobs 1: <= 2 lab pythons in total); the tree is killed on timeout."""
    cmd = [sys.executable, VERIFIER, cert_path, "--jobs", "1", "--depth", str(depth), "--max-witnesses", str(max_w),
           "--report", "--quiet"]
    prio185.wait_mine(limit=2, max_wait=max(60, timeout / 2))      # this process + the child = 2
    prio185.wait_box(own=1, max_wait=max(60, timeout / 2), log=print)   # the child is one more on the box
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    try:
        out, _ = p.communicate(timeout=max(30, timeout))
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        return -9, "verifier timeout %.0fs (process tree killed)" % timeout


def certify_v4(res, hyp, tag, deadline, rounds=1, warm_rows=None):
    out = os.path.join(CERTS, tag + ".json")
    log, extra = [], []
    budget = hyp.budget4
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = max(1.005, min(1.30, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
        cert = make_certificate_v4(res, K.S_RAT, hyp, scale=scale)
        json.dump(cert, open(out, "w"), indent=0)
        tot = float(Fr(cert["total"]))
        if tot >= budget:
            log.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", log, out
        rc, txt = run_v4(out, deadline - time.time())
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "free clause", "window clause", "MALFORMED", "verifier"))]
        log.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:5]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=log, result="PASS", verifier="verify_case_v4 (A185)", label="[C] under v4 only",
                           v1_sha=L.VERIFIER_SHA), open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", log, out
        if rd == rounds or rc == -9 or time.time() > deadline - 60:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            break
        for w in json.load(open(wf))["witnesses"]:
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            extra.append((p["cx_float"], p["cy_float"], th))
            for d in (0.002, 0.005):
                for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                    extra.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
                for dth in (d, -d):
                    extra.append((p["cx_float"], p["cy_float"], th + dth))
        res = solve_node(K.S0, hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                         time_limit=min(240, max(30, deadline - time.time() - 120)), out=None, log=lambda *x: None,
                         extra_rows=extra, neigh_rows=0, col_stop_iter=0, fine_slack=99.0, max_iter=1000)
        if not (res["tau"] < budget - 1e-6):
            log.append(dict(round=rd + 1, tau=res["tau"], result="re-solve lost the kill"))
            break
    json.dump(dict(cert=out, rounds=log, result="FAIL", verifier="verify_case_v4 (A185)"),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log, out


# ===================================================================== one node
def solve_windows(tag, wroles, cap, warm, wall=1500.0, do_cert=True, log=print):
    t0 = time.time()
    deadline = t0 + wall
    H = WindowsHyp(wroles)
    rec = dict(node=tag, n_roles=H.r, n_cores=H.m, budget_v1=N - H.m, budget_v4=H.budget4, free=H.free, cap=cap,
               roles=[w.name for w in wroles], core_kind={w.name: w.core_kind for w in wroles},
               a_core={w.name: (float(w.core.a) if w.core else None) for w in wroles},
               pieces={w.name: len(w.pieces) for w in wroles}, hyp=H.to_json())
    gate = [dict(i=i, j=j, **dict(zip(("disjoint", "gap"), L.cores_disjoint_exact(H.cores[i], H.cores[j]))))
            for i in range(H.m) for j in range(i + 1, H.m)]
    rec["cores_disjoint"] = all(g["disjoint"] for g in gate)
    ok, mem = prio185.wait_box(log=log, own=0, max_wait=6 * 3600)   # this process is already counted
    rec["gate"] = mem
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    try:
        s = solve_node(K.S0, H, H.budget4, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900, out=None,
                       log=lambda *x: None, prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                       max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = s.get("tau")
    # resumable: the next leg warm-starts from these rows and atoms (run185 --resume)
    json.dump(dict(tau=tau, converged=s.get("converged"), atoms_all=s.get("atoms_all"), rows_all=s.get("rows_all"),
                   packing=s.get("packing"), n_rows=s.get("n_rows"), minmass=s.get("minmass"), hyp=s.get("hyp")),
              open(os.path.join(BASE, "results", "lpres_%s.json" % tag), "w"))
    rec.update(tau=tau, eta=(tau - H.budget4) if tau is not None else None, converged=bool(s.get("converged")),
               minmass=s.get("minmass"), maxcov=s.get("maxcov"), n_rows=s.get("n_rows"),
               support=len(s.get("packing") or []), lp_s=round(time.time() - t0, 1),
               kills=bool(tau is not None and tau < H.budget4 - 1e-6),
               kills_converged=bool(s.get("converged") and tau is not None and tau < H.budget4 - 1e-6),
               window_transfer="by dilation (Lemma B.0 + K0-WIDEN: the windows are stated on F = D_lambda P at s0)")
    rec["packing_rows"] = [[p["cx"], p["cy"], p["theta"], p["y"]] for p in (s.get("packing") or [])][:400]
    rec["atoms"] = [a for a in s.get("atoms_all", []) if a[2] > 1e-9]
    if do_cert and rec["kills_converged"]:
        v, lg, path = certify_v4(s, H, tag, deadline)
        rec.update(certified=v, cert_log=lg, cert=os.path.relpath(path, K.ROOT).replace("\\", "/"))
    rec["verdict"] = ("DEAD(LP, v4 certified) [C under v4 ONLY]" if rec.get("certified") == "PASS"
                      else ("DEAD(LP, v4 certificate pending)" if rec["kills_converged"]
                            else ("LP-dead unconverged (kill candidate, v4)" if rec["kills"] else "ALIVE(LP, v4)")))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec
