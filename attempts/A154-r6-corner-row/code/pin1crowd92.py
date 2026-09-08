"""A92 pilot chore `pin1crowd92` -- ONE corner PINNED (A85 blocker pair) + CROWD weights on the
other three corners.

Question: does pinning one corner's blocker pair (so its two cores exist and its stranded region
is EXEMPT, A85's case-LP at budget 11 - 2 = 9) combine with A92's crowd-weighted family on the
remaining three corners to certify at small delta, where the PURE crowd certificate (crowd92,
all four corners weighted, no pins) refuses (delta = 0.1 and 0.05 refused for every e)?

Node (per BL pair (i,j) of A85's REALISABLE census):

  * hypothesis  Hyp([B_i, B_j], [])  -- the two BL reach-cover boxes, cores pinned, rows meeting
    a core are exempt (A85 semantics); #cores = 2, budget = 11 - 2 = 9.
  * LP row rhs   mu(Q) >= 1 + e * [Q in G_3],  G_3 = G_BR u G_TL u G_TR, an OUTER cover of the
    crowd family F_c(a_w(delta)) at the three UNPINNED corners only (crowdfam92's G, with the
    BL frame dropped from the membership test).  Lemma CW-S exemption structure, r_max runs.
  * threshold    tau < 9 + 6e   (2 pinned + 6 crowd squares at 1+e + 3 free at 1).
  * sym C1 (a pinned BL pair breaks D4), exactly as A85's pilot59.run_child.

Certification (frozen verify_case.py, byte-identical to A85's; A92's two-run form):

  run A : cores = the 2 BL cores, nofams = [], n = B + 2, budget = B = floor(9 + 6e).
          PASS => mu(Q) >= 1 for every admissible Q not meeting a core, and mu(total) < B.
  run B : SAME atoms, weights / (1+e), SAME 2 cores, nofams = E_3, n = 1000 + 2 (dummy).
          PASS => mu(Q) >= 1 + e for every Q not meeting a core and not provably in E_3;
          E_3 = crowdfam92's four-corner complement cover E, PLUS the (dilated) BL staircase
          rects, every one of them EXACTLY certified disjoint from F_c(a_w) for c in
          {BR, TL, TR}.  So E_3 is a cover of the complement of G_3.

  INTEGER-BUDGET CAVEAT (recorded, not worked around): verify_case requires integer n and
  budget = n - #cores, so the certified clause is `total < floor(9 + 6e)`, i.e. B = 9 at
  e = 1/8 (no gain over the plain pinned certificate) and B = 10 at e = 1/4.  The LP-level
  threshold 9 + 6e is the exact mathematical one and is what the LP table reports.

Canaries (both refuse before any LP):
  * no image of the k0_00 class realises the three-corner crowd hypothesis at any a_w < 1
    (Trump is not K0-BLOCKED) -- asserted exactly as crowd92 does, per corner;
  * the PLAIN pinned LP must reproduce A85's stored tau on `s2_near_046_619`
    (a85_lp_samples.jsonl: BL pair (46, 619), budget 9, tau = 7.999999999991748).

Resource discipline: ONE process, BLAS pinned (blas1 before numpy), free COMMIT > 6144 MB
checked before every LP and every certification (60 s sleep-and-recheck).  Writes only
attempts/A92-blocked-side/{code,results,notes}/pin1crowd92.*
"""
import argparse, hashlib, json, math, os, random, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import numpy as np
import lpbox92
import caselp92
from caselp92 import Box, Hyp, NoFam, solve_node, q, t_lo, t_hi
from pinguard import cores_meet
import crowdfam92 as CF

A85 = os.path.join(ROOT, "attempts", "A85-k0-route")
A38 = os.path.join(ROOT, "attempts", "A38-root-power")
RES = os.path.join(BASE, "results")
NOTES = os.path.join(BASE, "notes")
os.makedirs(RES, exist_ok=True)

S_RAT = "969271/250000"
S0F = float(Fr(S_RAT))
MIN_FREE_COMMIT_MB = 6144.0
PFX = os.path.join(RES, "pin1crowd92")
LOGP = PFX + ".log"
SINK = PFX + ".jsonl"
CROWD_CORNERS = ("BR", "TL", "TR")
CANARY_PAIR = (46, 619)
CANARY_TAU = 7.999999999991748


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


def wait_for_commit(tag, deadline=None, need=1):
    n, ok = 0, 0
    while True:
        mb = free_commit_mb()
        if mb > MIN_FREE_COMMIT_MB:
            ok += 1
            if ok >= need:
                if n:
                    logline("  commit OK %.0f MB after %d x 60 s (%s)" % (mb, n, tag))
                return mb
        else:
            ok = 0
        if deadline is not None and time.time() > deadline:
            logline("  commit STILL LOW %.0f MB, deadline passed -- SKIP %s" % (mb, tag))
            return None
        logline("  commit %.0f MB (need > %.0f): sleep 60 s (%s)" % (mb, MIN_FREE_COMMIT_MB, tag))
        time.sleep(60)
        n += 1


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if p and os.path.exists(p) else None


def _put(rec):
    with open(SINK, "a") as f:
        f.write(json.dumps(rec) + "\n")


# =============================================================== A85 boxes / realisable pairs
def load_pairs():
    R = json.load(open(os.path.join(A85, "results", "a85_reach_BL.json")))
    rows = [r for r in R["variants"]["sigma_closed_7"]["rows"] if r["sound"]]
    boxes = [Box.from_json(r["box"]) for r in rows]
    B = json.load(open(os.path.join(A85, "results", "realise85.boxes.json")))
    dub = B["depth_ub_wall"]
    assert len(boxes) == len(dub) == 644, (len(boxes), len(dub))
    pairs = [tuple(p) for p in json.load(open(os.path.join(A85, "results",
                                                          "realise85.pairs.json")))["surviving"]]
    return boxes, dub, pairs


def valid_node(boxes, i, j):
    """A85's node admissibility: both cores non-empty and the two cores do NOT meet
    (cores_meet => a (C) leaf, killed by logic, not by an LP)."""
    ci, cj = boxes[i].core(), boxes[j].core()
    if ci is None or cj is None:
        return None
    if cores_meet(ci, cj):
        return None
    return (ci, cj)


STRATA = [("mid", 0.05, 0.2, 10), ("hi", 0.2, 0.3, 5), ("lo", -1e9, 0.05, 5)]


def sample_nodes(boxes, dub, pairs, seed):
    rnd = random.Random(seed)
    buckets = {k: [] for (k, _, _, _) in STRATA}
    for (i, j) in pairs:
        d2 = min(dub[i], dub[j])
        for (k, lo, hi, _) in STRATA:
            if lo <= d2 < hi:
                buckets[k].append((i, j, d2))
                break
    out = []
    for (k, lo, hi, want) in STRATA:
        pool = buckets[k]
        rnd.shuffle(pool)
        took = 0
        for (i, j, d2) in pool:
            if took >= want:
                break
            if valid_node(boxes, i, j) is None:
                continue
            out.append(dict(stratum=k, i=i, j=j, d2_ub=d2,
                            tag="p1c_%s_%03d_%03d" % (k, i, j)))
            took += 1
        if took < want:
            logline("  WARNING stratum %s: only %d of %d wanted (pool %d)"
                    % (k, took, want, len(pool)))
    return out


# =============================================================== the 3-corner crowd family
class GTest3:
    """crowdfam92.GTest restricted to the UNPINNED corners (BR, TL, TR).  Same conservative
    dilation (centre EPS_ZONE_G, theta EPS_TH_G): a pose counts as in G unless it is outside
    every G-rect of every unpinned corner by the margin -- more rows at 1+e, never fewer."""

    def __init__(self, fam, corners=CROWD_CORNERS,
                 eps_zone=CF.EPS_ZONE_G, eps_th=CF.EPS_TH_G):
        self.xs = np.array([float(x) for x in fam["xs"]])
        ys = fam["ys"]
        self.NX = fam["NX"]
        self.ytop = {b: np.array([float(ys[J + 1]) if J >= 0 else -1e18 for J in fam["SC"][b]])
                     for b in fam["SC"]}
        self.bins = list(fam["SC"])
        self.ez, self.et = eps_zone, eps_th
        self.corners = tuple(corners)

    def __call__(self, C, th_deg, extra=0.0):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        out = np.zeros(len(C), dtype=bool)
        th = th_deg % 90.0
        ez = self.ez + extra
        for corner in self.corners:
            u = C[:, 0] if corner in ("BL", "TL") else S0F - C[:, 0]
            v = C[:, 1] if corner in ("BL", "BR") else S0F - C[:, 1]
            thc = th if corner in ("BL", "TR") else 90.0 - th
            uu, vv = u - ez, v - ez
            i0 = np.clip(np.searchsorted(self.xs, uu, side="right") - 1, 0, self.NX - 1)
            inx = uu <= self.xs[-1]
            for b in self.bins:
                if not (b[0] - self.et <= thc <= b[1] + self.et):
                    continue
                out |= inx & (vv <= self.ytop[b][i0])
        return out

    def cells(self, cx, cy, tol, th_deg):
        return self(np.stack([np.asarray(cx, float), np.asarray(cy, float)], 1), th_deg,
                    extra=np.asarray(tol, float))


def install_rhs3(fam, e):
    """set / clear the lpbox92 rhs hooks for the 3-corner crowd family."""
    if e is None:
        lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = None, 1.0, None
        return 1.0
    g = GTest3(fam)
    ef = float(e)
    lpbox92.RHS_MULT = lambda C, th: 1.0 + ef * g(C, th).astype(float)
    lpbox92.RHS_MAX = 1.0 + ef
    lpbox92.RHS_CELL = g.cells
    return lpbox92.RHS_MAX


DIL = CF.GRID          # one centre-grid cell of dilation on the emitted BL rects (seam overlap)


_E3C = {}


def nofams_E3(fam):
    """E_3 = a cover of the complement of G_3 = G_BR u G_TL u G_TR.

    = crowdfam92's four-corner complement cover E (each box already EXACTLY certified disjoint
      from F_c(a_w) at all four corners)
    + the BL staircase rects themselves, DILATED by one grid cell in x and y so that they
      OVERLAP the abutting E boxes (verify_case exempts a box only if it lies inside ONE family,
      so abutting families leave permanently unexemptable seams -- the first crowd92 campaign's
      failure mode).  Each dilated BL rect is EXACTLY certified disjoint from F_c(a_w) for
      c in {BR, TL, TR} (its own corner BL is, of course, not required).
    """
    a = fam["a"]
    if a in _E3C:
        return _E3C[a]
    out = CF.nofams_E(fam)
    n_e4 = len(out)
    bad = []
    n_bl = 0
    for b, rects in fam["G_BL"].items():
        sb = CF.sigma_bin(b)
        for (x0, x1, y0, y1) in rects:
            X0, X1 = max(Fr(0), x0 - DIL), x1 + DIL
            Y0, Y1 = max(Fr(0), y0 - DIL), y1 + DIL
            # BR: (u,v) = (S - x, y), bin sigma(b);  TL: (x, S - y), sigma(b);  TR: (S-x, S-y), b
            ok = (CF.disjoint(CF.S - X1, Y0, sb, a) and CF.disjoint(X0, CF.S - Y1, sb, a)
                  and CF.disjoint(CF.S - X1, CF.S - Y1, b, a))
            if not ok:
                bad.append((float(X0), float(X1), float(Y0), float(Y1), b))
                continue
            out.append(NoFam(float(X0), float(X1), float(Y0), float(Y1), [(b[0], b[1])]))
            n_bl += 1
    assert not bad, "UNSOUND dilated BL rects (not provably disjoint from F_{BR,TL,TR}): %s" % bad[:3]
    _E3C[a] = (out, n_e4, n_bl)
    return _E3C[a]


def crowd_counts_3(a):
    """per-image count of k0_00 placements with f_c <= a at the three UNPINNED corners.
    An image realises the 3-corner crowd hypothesis iff BR, TL and TR all have >= 2."""
    rows = CF.image_crowd_counts(a)
    out = []
    for r in rows:
        c = {k: r[k] for k in CROWD_CORNERS}
        out.append(dict(image=r["image"], BL=r["BL"], realises3=all(c[k] >= 2 for k in c), **c))
    return out


# =============================================================== warm pool (columns only)
WARM = {}


def warm_pool(max_atoms=140000):
    """columns only, EXACTLY A85 lp85.warm85 (so the plain-LP canary sees A85's own pool):
    A38 l1/l2 node columns + A85's stored k0_00 node columns.  Both trees are read-only."""
    if "w" in WARM:
        return WARM["w"]
    import glob
    srcs = sorted(glob.glob(os.path.join(A38, "results", "l1_nodes", "node_*.json")))[:40]
    srcs += sorted(glob.glob(os.path.join(A38, "results", "l2_nodes", "l2_*.json")))[:20]
    srcs += sorted(glob.glob(os.path.join(A85, "results", "nodes", "k0_00", "*.json")))
    atoms, seen, used = [], set(), []
    for p in srcs:
        if p.endswith(".rec.json") or p.endswith("_state.json"):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        used.append(os.path.basename(p))
        for key in ("orbits", "atoms_all"):
            for a_ in d.get(key, []):
                k = (round(a_[0], 7), round(a_[1], 7))
                if k not in seen:
                    seen.add(k)
                    atoms.append((a_[0], a_[1]))
        if len(atoms) >= max_atoms:
            break
    WARM["w"] = dict(atoms=atoms, rows=[])
    logline("  warm pool: %d columns from %d files (A85 lp85.warm85 replica; %s ...)"
            % (len(atoms), len(used), ", ".join(used[:4])))
    return WARM["w"]


# =============================================================== the LP
def run_lp(boxes, node, e, fam, lp_time, deadline, tag, warm=None):
    """one LP: Hyp = the 2 BL cores, budget 9, rhs 1 + e[Q in G_3] (e = None -> plain A85 LP)."""
    hyp = Hyp([boxes[node["i"]], boxes[node["j"]]], [])
    assert len(hyp.boxes) == 2
    budget = 9
    thr = 9.0 + 6.0 * float(e) if e is not None else 9.0
    if wait_for_commit(tag, deadline) is None:
        return None
    rmax = install_rhs3(fam, e)
    t0 = time.time()
    try:
        res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=(warm or warm_pool()),
                         time_limit=lp_time, max_iter=900, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
    finally:
        install_rhs3(None, None)
    res["child_id"] = tag
    res["_lp_s"] = round(time.time() - t0, 1)
    res["_rhs_max"] = rmax
    res["_thr"] = thr
    return res


def lp_record(node, e, delta, res, thr, kind):
    rec = dict(tag=node["tag"], stratum=node["stratum"], i=node["i"], j=node["j"],
               d2_ub=node["d2_ub"], kind=kind, delta=delta, e=(str(e) if e is not None else None),
               budget=9, threshold=thr, tau=res["tau"], eta=res["tau"] - thr,
               converged=bool(res["converged"]), minmass=res["minmass"], maxcov=res["maxcov"],
               rows=res.get("n_rows"), lp_s=res["_lp_s"],
               atoms=len([x for x in res.get("atoms_all", []) if x[2] > 1e-10]),
               verdict=("LP-PASS" if res["tau"] < thr else "refused"),
               ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    return rec


# =============================================================== certification (two runs)
def make_cert(res, scale, n, cores, nofams, wdiv, claim, tagged):
    """caselp92.make_certificate92 + the node's CORES (A85 pinned-core semantics)."""
    s = Fr(S_RAT)
    denom = 10 ** 6
    seen, atoms, weights = {}, [], []
    for (x, y, w) in res["atoms_all"]:
        if w <= 1e-10:
            continue
        p = (Fr(round(x * denom), denom), Fr(round(y * denom), denom))
        wq = Fr(math.ceil(w * scale * denom), denom)
        if p in seen:
            weights[seen[p]] += wq
        else:
            seen[p] = len(atoms)
            atoms.append(p)
            weights.append(wq)
    weights = [w / wdiv for w in weights]
    total = sum(weights, Fr(0))
    return dict(format="case-lp-certificate-v1", n=int(n), s=str(s),
                budget=int(n) - len(cores),
                atoms=[[str(p[0]), str(p[1])] for p in atoms],
                weights=[str(w) for w in weights], total=str(total),
                hypotheses=dict(
                    cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                                box=c.box.to_json()) for c in cores],
                    nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)),
                                 y1=str(q(f.y1)),
                                 t_intervals=[[str(t_lo(u)), str(t_hi(v))] for u, v in f.thetas])
                            for f in nofams]),
                claim=claim, run=tagged,
                provenance=dict(method="A92 pin1crowd92: A85 pinned-pair case-LP with the A92 "
                                       "3-corner crowd rhs; weights x %.6f rounded up to 1/%d "
                                       "then divided by %s" % (scale, denom, str(wdiv)),
                                lp_tau=res["tau"], eps_geo=lpbox92.EPS_GEO,
                                eps_core=caselp92.EPS_CORE))


def run_verifier(cert_path, jobs=1, depth=56, max_w=64):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def certify(res, node, e, fam, tag, deadline, depth=56, scale_cap=1.40):
    """the two frozen-verifier runs.  B = floor(9 + 6e) (verify_case needs an integer budget)."""
    hyp = Hyp([res["_boxes"][0], res["_boxes"][1]], [])
    cores = hyp.cores
    B = int(math.floor(9 + 6 * Fr(e)))
    nA = B + len(cores)
    nofE, n_e4, n_bl = nofams_E3(fam)
    scale = max(1.005, min(scale_cap, (B - 0.005) / res["tau"] - 0.002)) if res["tau"] > 1e-12 else 1.005
    claimA = ("every admissible closed unit square Q in [0,%s]^2 disjoint from both pinned cores "
              "has mu(Q) >= 1, and mu(total) < %d = floor(9 + 6e) with e = %s (9 = 11 - 2 cores)"
              % (S_RAT, B, str(e)))
    claimB = ("every admissible closed unit square Q in [0,%s]^2 disjoint from both pinned cores "
              "and NOT provably in the complement cover E_3 has mu(Q) >= 1 + e, e = %s (the "
              "file's weights are w/(1+e) and its total clause is a dummy); every E_3 box is "
              "exactly certified disjoint from F_c(a_w) for c in {BR,TL,TR}" % (S_RAT, str(e)))
    outA, outB = PFX + ".runA_%s.json" % tag, PFX + ".runB_%s.json" % tag
    certA = make_cert(res, scale, nA, cores, [], Fr(1), claimA, "A")
    certB = make_cert(res, scale, 1000 + len(cores), cores, nofE, Fr(1) + Fr(e), claimB, "B")
    totA = float(Fr(certA["total"]))
    json.dump(certA, open(outA, "w"), indent=0)
    json.dump(certB, open(outB, "w"), indent=0)
    logline("  [cert %s] scale=%.4f totalA=%.5f (< %d) atoms=%d nofamsB=%d (E4 %d + BL %d)"
            % (tag, scale, totA, B, len(certA["atoms"]), len(nofE), n_e4, n_bl))
    if totA >= B:
        return dict(tag=tag, B=B, scale=scale, totalA=totA, verdictA="FAIL(total>=budget)",
                    verdictB=None, cert_s=0.0)
    if wait_for_commit(tag + ":certA", deadline) is None:
        return dict(tag=tag, B=B, verdictA="SKIPPED(commit)", verdictB=None, cert_s=0.0)
    t0 = time.time()
    rcA, txtA = run_verifier(outA, depth=depth)
    tA = round(time.time() - t0, 1)
    logline("  [cert %s] run A rc=%d (%.0f s) :: %s" % (tag, rcA, tA,
            " | ".join(l for l in txtA.splitlines() if l.startswith(("PASS", "FAIL", "MALFORMED")))[:300]))
    if wait_for_commit(tag + ":certB", deadline) is None:
        return dict(tag=tag, B=B, scale=scale, totalA=totA,
                    verdictA=("PASS" if rcA == 0 else "FAIL(rc=%d)" % rcA),
                    verdictB="SKIPPED(commit)", cert_s=tA)
    t1 = time.time()
    rcB, txtB = run_verifier(outB, depth=depth)
    tB = round(time.time() - t1, 1)
    logline("  [cert %s] run B rc=%d (%.0f s) :: %s" % (tag, rcB, tB,
            " | ".join(l for l in txtB.splitlines() if l.startswith(("PASS", "FAIL", "MALFORMED")))[:300]))
    rec = dict(tag=tag, B=B, scale=scale, totalA=totA, n_nofams_B=len(nofE),
               verdictA=("PASS" if rcA == 0 else "FAIL(rc=%d)" % rcA),
               verdictB=("PASS" if rcB == 0 else "FAIL(rc=%d)" % rcB),
               cert_s=round(tA + tB, 1), sha256_A=sha256(outA), sha256_B=sha256(outB),
               pathA=outA, pathB=outB)
    if rcA == 0 and rcB == 0:
        open(PFX + ".%s.PASS" % tag, "w").write(time.strftime("%Y-%m-%d %H:%M:%S\n"))
    return rec


# =============================================================== main
DELTAS = [0.1, 0.05]
ES = [Fr(1, 8), Fr(1, 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=170.0)
    ap.add_argument("--lp_time", type=float, default=70.0)
    ap.add_argument("--canary_lp_time", type=float, default=300.0)
    ap.add_argument("--cert_resolve_time", type=float, default=900.0)
    ap.add_argument("--n_nodes", type=int, default=20)
    ap.add_argument("--seed", type=int, default=920401)
    ap.add_argument("--cert_max", type=int, default=2)
    ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args()
    T_END = time.time() + 60 * a.minutes
    logline("=" * 100)
    logline("A92 pin1crowd92 start; wall %.0f min; lp_time %.0f s; s0 = %s; free commit %.0f MB"
            % (a.minutes, a.lp_time, S_RAT, free_commit_mb()))

    boxes, dub, pairs = load_pairs()
    logline("A85 census: %d sound BL reach boxes, %d realisable surviving pairs" % (len(boxes), len(pairs)))

    # ---- families (cached; delta 0.1 / 0.05 already built by crowd92) + 3-corner canary
    # crowd92's own results/fam_d0.1.json / fam_d0.05.json are the FIRST-campaign (abutting-strip,
    # fam_build = 1) caches -- the A92 follow-up rebuilt only d0.3 / d0.2.  Rebuild ours here, into
    # our own pin1crowd92.* cache; a fam_build = 1 cover would hole run B on every strip seam.
    fams = {}
    for d in DELTAS:
        p = PFX + ".fam_d%g.json" % d
        if os.path.exists(p) and json.load(open(p)).get("fam_build") == CF.FAM_BUILD:
            fam = CF.from_json(json.load(open(p)))
            logline("  fam delta=%g reused from %s" % (d, os.path.basename(p)))
        else:
            t0 = time.time()
            fam = CF.build(d, log=logline)
            json.dump(CF.to_json(fam), open(p, "w"))
            logline("  fam delta=%g built in %.0f s -> %s" % (d, time.time() - t0, os.path.basename(p)))
        fams[d] = fam
        cnt = crowd_counts_3(fam["a"])
        real = [r["image"] for r in cnt if r["realises3"]]
        logline("  CANARY delta=%g a_w=%s (%.6f): per-image [BL|BR TL TR] %s -> realising=%s"
                % (d, str(fam["a"]), float(fam["a"]),
                   ";".join("%s[%d|%d%d%d]" % (r["image"], r["BL"], r["BR"], r["TL"], r["TR"])
                            for r in cnt), real or "NONE"))
        if real:
            logline("REFUSED before any LP: images realise the 3-corner crowd hypothesis at delta=%g" % d)
            sys.exit(1)
        nofE, n_e4, n_bl = nofams_E3(fam)
        logline("  fam delta=%g: G/corner=%d, E_3 = %d (E_4 %d + dilated BL %d), all exactly "
                "disjoint from F_{BR,TL,TR}" % (d, fam["n_g_per_corner"], len(nofE), n_e4, n_bl))

    # ---- canary 2: the plain pinned LP must reproduce A85's stored tau on (46, 619)
    ci, cj = CANARY_PAIR
    cnode = dict(stratum="canary", i=ci, j=cj, d2_ub=min(dub[ci], dub[cj]),
                 tag="p1c_canary_%03d_%03d" % (ci, cj))
    assert valid_node(boxes, ci, cj) is not None, "canary pair has no cores / cores meet"
    # Warm-started from A85's OWN stored node state (atoms + rows of results/nodes/k0_00/
    # s2_near_046_619.json).  A cold 600 s solve of this node reaches only tau = 8.027027
    # (unconverged; A85 spent 900 s and its pool grew by sibling column folding), so a cold
    # canary would measure the LP time cap, not node identity.  Warm from A85's own row/column
    # set, the check is what it is meant to be: same boxes, same cores, same budget, same
    # optimum tau.
    a85n = os.path.join(A85, "results", "nodes", "k0_00", "s2_near_046_619.json")
    cwarm = None
    if os.path.exists(a85n):
        cwarm = caselp92.warm_from_result(json.load(open(a85n)))
        logline("  canary warm start from A85 %s: %d cols, %d rows"
                % (os.path.basename(a85n), len(cwarm["atoms"]), len(cwarm["rows"])))
    res = run_lp(boxes, cnode, None, None, a.canary_lp_time, T_END, cnode["tag"], warm=cwarm)
    rec = lp_record(cnode, None, None, res, 9.0, "canary-plain")
    rec["a85_tau"] = CANARY_TAU
    rec["a85_delta_tau"] = res["tau"] - CANARY_TAU
    _put(rec)
    logline("  CANARY plain LP (46,619) budget 9: tau=%.9f (A85 %.9f, delta %.2e) conv=%s "
            "minmass=%.4f rows=%s %.0fs"
            % (res["tau"], CANARY_TAU, res["tau"] - CANARY_TAU, res["converged"],
               res["minmass"], res.get("n_rows"), res["_lp_s"]))
    dt = res["tau"] - CANARY_TAU
    if abs(dt) > 1e-4:
        logline("CANARY FAIL: plain pinned LP does not reproduce A85's stored tau (dtau=%.3e)" % dt)
        # a GROSS mismatch means the node itself is wrong (box indices, cores, budget): refuse.
        if abs(dt) > 5e-2 and not a.calibrate:
            sys.exit(2)
        logline("  ... |dtau| <= 5e-2: node identity is right, the residue is LP truncation; "
                "continuing with the deviation RECORDED")
    else:
        logline("  CANARY PASS (|dtau| <= 1e-4)")
    if a.calibrate:
        for d in DELTAS:
            for e in ES:
                r2 = run_lp(boxes, cnode, e, fams[d], a.lp_time, T_END,
                            cnode["tag"] + "_d%g_e%s" % (d, str(e).replace("/", "o")))
                logline("  CALIB d=%g e=%s: tau=%.6f thr=%.4f conv=%s minmass=%.4f %.0fs"
                        % (d, str(e), r2["tau"], r2["_thr"], r2["converged"], r2["minmass"],
                           r2["_lp_s"]))
        return

    # ---- the 20 sampled nodes
    nodes = sample_nodes(boxes, dub, pairs, a.seed)[:a.n_nodes]
    logline("sampled %d nodes: %s" % (len(nodes), ", ".join(
        "%s(%d,%d,d2=%.3f)" % (n["stratum"], n["i"], n["j"], n["d2_ub"]) for n in nodes)))
    json.dump(dict(seed=a.seed, strata=[list(s) for s in STRATA], nodes=nodes),
              open(PFX + ".nodes.json", "w"), indent=1)

    done, cand = [], []
    for k, node in enumerate(nodes):
        if time.time() > T_END - 60 * 6:
            logline("WALL: stopping after %d of %d nodes" % (k, len(nodes)))
            break
        rp = run_lp(boxes, node, None, None, a.lp_time, T_END, node["tag"])
        if rp is None:
            break
        recp = lp_record(node, None, None, rp, 9.0, "plain")
        _put(recp)
        logline("[%2d/%d] %s d2=%.4f  PLAIN tau=%.5f thr=9 %s conv=%s mm=%.4f %.0fs"
                % (k + 1, len(nodes), node["tag"], node["d2_ub"], rp["tau"], recp["verdict"],
                   rp["converged"], rp["minmass"], rp["_lp_s"]))
        row = dict(node=node, plain=recp, crowd={})
        for d in DELTAS:
            for e in ES:
                if time.time() > T_END - 60 * 4:
                    break
                key = "d%g_e%s" % (d, str(e).replace("/", "o"))
                rc = run_lp(boxes, node, e, fams[d], a.lp_time, T_END, node["tag"] + "_" + key)
                if rc is None:
                    break
                rr = lp_record(node, e, d, rc, rc["_thr"], "crowd")
                _put(rr)
                row["crowd"][key] = rr
                logline("        %-10s tau=%.5f thr=%.4f %s conv=%s mm=%.4f %.0fs"
                        % (key, rc["tau"], rc["_thr"], rr["verdict"], rc["converged"],
                           rc["minmass"], rc["_lp_s"]))
                if rr["verdict"] == "LP-PASS":
                    prio = 0 if recp["verdict"] != "LP-PASS" else 1   # crowd-only passes first
                    cand.append([prio, rr["eta"], node, e, d, node["tag"] + "_" + key])
        done.append(row)

    json.dump(done, open(PFX + ".table.json", "w"), indent=1)

    # ---- certification: the crowd-only LP passes, best (most negative) eta first
    certs = []
    cand.sort(key=lambda z: (z[0], z[1]))
    n_only = sum(1 for c in cand if c[0] == 0)
    logline("certification candidates: %d crowd LP-PASS (%d of them where the plain LP refuses)"
            % (len(cand), n_only))
    for (prio, eta, node, e, d, tag) in cand[:a.cert_max]:
        if time.time() > T_END - 60 * 8:
            logline("WALL: no time for certification of %s" % tag)
            break
        B = int(math.floor(9 + 6 * Fr(e)))
        # the node LPs above are TRUNCATED (lp_time %.0f s, minmass well below 1): a certificate
        # needs minmass * scale >= 1, so re-solve THIS node properly first.
        logline("  [cert] re-solving %s at %.0f s before certifying (B = floor(9+6e) = %d)"
                % (tag, a.cert_resolve_time, B))
        rc = run_lp(boxes, node, e, fams[d], a.cert_resolve_time, T_END, tag + "_resolve")
        if rc is None:
            break
        rr = lp_record(node, e, d, rc, rc["_thr"], "crowd-resolve")
        _put(rr)
        logline("  [cert] %s re-solved: tau=%.5f thr=%.4f %s conv=%s mm=%.4f %.0fs"
                % (tag, rc["tau"], rc["_thr"], rr["verdict"], rc["converged"], rc["minmass"],
                   rc["_lp_s"]))
        if rc["tau"] >= B:
            logline("  %s: tau %.5f >= B = floor(9 + 6e) = %d -- verify_case needs an INTEGER "
                    "budget (budget = n - #cores), so this LP pass is not certifiable at this e"
                    % (tag, rc["tau"], B))
            certs.append(dict(tag=tag, B=B, verdictA="NOT-ATTEMPTED(tau>=floor(9+6e))",
                              verdictB=None, tau=rc["tau"], e=str(e), delta=d,
                              minmass=rc["minmass"], converged=bool(rc["converged"])))
            continue
        rc["_boxes"] = [boxes[node["i"]], boxes[node["j"]]]
        cr = certify(rc, node, e, fams[d], tag, T_END, depth=56)
        cr.update(tau=rc["tau"], e=str(e), delta=d, minmass=rc["minmass"],
                  converged=bool(rc["converged"]))
        certs.append(cr)
        _put(dict(kind="cert", **cr))
    json.dump(certs, open(PFX + ".certs.json", "w"), indent=1)
    logline("DONE: %d nodes, %d certification attempts" % (len(done), len(certs)))
    open(PFX + ".DONE", "w").write(time.strftime("%Y-%m-%d %H:%M:%S ") +
                                   "nodes=%d certs=%d\n" % (len(done), len(certs)))


if __name__ == "__main__":
    main()
