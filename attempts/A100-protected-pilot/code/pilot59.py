"""
A59 leg-(c) pilot: the residual zone-tree on trump5 (theory.md T5', pilot_design.md v2).

PRICING pilot.  Semantics inherited verbatim:
  * A54 S0  -- tau bounds tau* in NEITHER direction; the sole kill arbiter is an exact
    rational certificate accepted by verify_case.py.
  * A57 T2  -- theta windows uniform in t = tan(theta/2), never in degrees.
  * A57 T4  -- columns-only warm starts.
  * A57 T5  -- pinguard.classify on every core box before it is solved or read.
  * A57 T11 -- one depth-2 refinement (bisection of the box, same budget) before giving up.
  * Canary  -- substrat.trump_realizes on every child; a Trump-realizable child is NEVER
    certified, and a PASS on a box containing a Trump placement is an engine bug (abort).

Nothing outside attempts/A59-trump-residual is written.
"""
import argparse, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, HERE)

import caselp
from caselp import Box, NoFam, Hyp, solve_node
from pinguard import classify, cores_meet
from substrat import trump_realizes, zones
from warm57 import merged_warm

S_RAT = "969271/250000"
S0F = float(Fr(S_RAT))                      # 3.877084
SLOTS = [(0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (S0F - 0.5, 0.5), (S0F - 0.5, S0F - 0.5)]
PINS = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in SLOTS]

# Trump's six free squares (A03 float) -- (cx, cy, theta_rad)
TH_T = 0.7013071055461440
FREE = {
    "sq4":  (0.4999999999999994, 2.532558314349611, 0.0),
    "sq6":  (1.536287180312013, 3.172475420161054, TH_T),
    "sq7":  (1.6885587003271723, 1.9596128278917806, TH_T),
    "sq8":  (2.4245254160591565, 1.2722538960439997, TH_T),
    "sq9":  (2.436508704429069, 2.6238338256453235, TH_T),
    "sq10": (3.172475420161054, 1.936474893797542, TH_T),
}
T7 = math.tan(TH_T / 2.0)                   # 0.3658455...
DEEP_OTHERS = ["sq4", "sq6", "sq8", "sq9", "sq10"]

# A84 edit (2 lines + 2 uses): per-class sub-directory for results/nodes and certs, so the
# pilot's two classes never share a namespace.  "" reproduces A59/A60 behaviour exactly.
SUBDIR = ""

GRID = 10 ** 6                              # box corners live on the 1e-6 rational grid
JSONL = os.path.join(BASE, "results", "pilot_zonetree.jsonl")
LOGP = os.path.join(BASE, "logs", "pilot.log")


# ------------------------------------------------------------------ small helpers
def rq(x, den=GRID):
    """snap to the rational grid 1/den (caselp.q is exact at 1e-9, so this IS the corner)"""
    return round(x * den) / den


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(max(0.0, t)))


def tbox_deg(t0, t1):
    return deg_of_t(rq(max(0.0, t0))), deg_of_t(rq(min(1.0, t1)))


def logline(*x):
    s = " ".join(str(v) for v in x)
    print(s, flush=True)
    with open(LOGP, "a") as f:
        f.write(time.strftime("[%H:%M:%S] ") + s + "\n")


def append_rec(rec):
    with open(JSONL, "a") as f:
        f.write(json.dumps(rec) + "\n")


def done_tags():
    if not os.path.exists(JSONL):
        return set()
    out = set()
    for line in open(JSONL):
        try:
            out.add(json.loads(line)["tag"])
        except Exception:
            pass
    return out


# ------------------------------------------------------------------ box builders
def core_box(name, hw, ht):
    """core box around Trump's free square `name`: centre half-width hw, t half-width ht."""
    cx, cy, th = FREE[name]
    t = math.tan(th / 2.0)
    th0, th1 = tbox_deg(t - ht, t + ht)
    return Box(rq(cx - hw), rq(cx + hw), rq(cy - hw), rq(cy + hw), th0, th1)


def sib_box(a, at, kind="cx"):
    """bisection-sibling of the Trump-containing box around sq7.
    kind='cx': displaced by 2a in cx  -> nearest distance from Trump's placement = a
    kind='t' : displaced by 2*at in t -> nearest t-distance from Trump's placement = at"""
    cx, cy, _ = FREE["sq7"]
    if kind == "cx":
        th0, th1 = tbox_deg(T7 - at, T7 + at)
        return Box(rq(cx + a), rq(cx + 3 * a), rq(cy - a), rq(cy + a), th0, th1)
    th0, th1 = tbox_deg(T7 + at, T7 + 3 * at)
    return Box(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), th0, th1)


def no_fam_7(a, at):
    """NO-family B7(a): 'no square centred in the box around Trump's sq7 with tilt in the window'"""
    cx, cy, _ = FREE["sq7"]
    th0, th1 = tbox_deg(T7 - at, T7 + at)
    return NoFam(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), [(th0, th1)])


def deep_cores(hw=0.05, ht=0.03):
    return [core_box(n, hw, ht) for n in DEEP_OTHERS]


def boxes_pairwise_disjoint(boxes):
    """(c, theta) box disjointness with the theta 0/90 identification (A57 T5'.1 distinct
    witnesses).  Two boxes can share a witness only if they intersect in (c, theta)."""
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            b, c = boxes[i], boxes[j]
            cxy = not (b.x1 < c.x0 or c.x1 < b.x0 or b.y1 < c.y0 or c.y1 < b.y0)
            if not cxy:
                continue
            def thov(u, v):
                return not (u.th1 < v.th0 or v.th1 < u.th0)
            wrap = (b.th0 <= 1e-9 and c.th1 >= 90 - 1e-9) or (c.th0 <= 1e-9 and b.th1 >= 90 - 1e-9)
            if thov(b, c) or wrap:
                bad.append((i, j))
    return bad


# ------------------------------------------------------------------ the solve+certify unit
def run_child(tag, hyp, budget, depth_j, a, at, kind, pin_state, pin_info, box_json,
              lp_time=300.0, cert_time=240.0, scale_cap=1.40, rounds=2, jobs=2, depth=56,
              warm_pool=None, force=False):
    """one pilot solve: LP -> (if tau < budget) certify -> verify.  Appends one jsonl record."""
    if not force and tag in done_tags():
        logline(f"  skip {tag} (already recorded)")
        return None
    canary = trump_realizes(hyp, SLOTS)
    rec = dict(tag=tag, depth_j=depth_j, a=a, at=at, kind=kind, budget=budget,
               pinguard=pin_state, pinguard_info=pin_info, trump_realized=canary, box=box_json,
               tau=None, converged=None, minmass=None, maxcov=None, eta=None,
               lp_s=0.0, cert_s=0.0, verdict="not-attempted", cert_path=None,
               ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    if pin_state == "contradictory":
        rec.update(verdict="KILL-BY-LOGIC", lp_s=0.0)
        logline("  " + json.dumps(rec)); append_rec(rec); return rec
    if pin_state == "parent":
        rec.update(verdict="refused (UNSOUND-AT-REDUCED-BUDGET: box realises a pin)")
        logline("  " + json.dumps(rec)); append_rec(rec); return rec

    nodedir = os.path.join(BASE, "results", "nodes", SUBDIR)
    os.makedirs(nodedir, exist_ok=True)
    node_path = os.path.join(nodedir, f"{tag}.json")
    warm = warm_pool if warm_pool is not None else PILOT_WARM
    t0 = time.time()
    if os.path.exists(node_path) and not force:
        res = json.load(open(node_path))
        rec["lp_s"] = 0.0
    else:
        logline(f"[LP] {tag} budget={budget} cols={len(warm['atoms'])} tl={lp_time}s")
        res = solve_node(S0F, hyp, budget, sym_kind="C1",
                         warm=dict(atoms=warm["atoms"], rows=[]),
                         time_limit=lp_time, max_iter=900, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
        res["child_id"] = tag
        json.dump(res, open(node_path, "w"))
        rec["lp_s"] = round(time.time() - t0, 1)
    rec.update(tau=res["tau"], converged=bool(res["converged"]), minmass=res["minmass"],
               maxcov=res["maxcov"], eta=res["tau"] - budget, rows=res.get("n_rows"),
               atoms=len([a_ for a_ in res.get("atoms_all", []) if a_[2] > 1e-10]))
    # fold this child's columns into the shared pool (A57 sibling column folding)
    if warm_pool is None:
        for at_ in res.get("atoms_all", []):
            k = (round(at_[0], 7), round(at_[1], 7))
            if k not in PILOT_SEEN:
                PILOT_SEEN.add(k); PILOT_WARM["atoms"].append((at_[0], at_[1]))

    if canary:
        rec["verdict"] = "refused (CANARY: Trump-realizable, never certified)"
    elif res["tau"] >= budget:
        rec["verdict"] = f"refused (tau {res['tau']:.6f} >= budget {budget})"
    else:
        certdir = os.path.join(BASE, "certs", SUBDIR)
        os.makedirs(certdir, exist_ok=True)
        cert_out = os.path.join(certdir, f"{tag}.json")
        cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_path, "--s_rat", S_RAT,
               "--rounds", str(rounds), "--jobs", str(jobs), "--depth", str(depth),
               "--time_limit", str(cert_time), "--out", cert_out, "--scale", "0",
               "--scale_cap", f"{scale_cap:.5f}", "--max_w", "64", "--loop_cols"]
        t1 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        with open(os.path.join(BASE, "logs", f"cert_{tag}.log"), "w") as f:
            f.write(p.stdout + "\n---stderr---\n" + p.stderr)
        rec["cert_s"] = round(time.time() - t1, 1)
        if p.returncode == 0:
            if canary:
                logline("ENGINE BUG: PASS on a Trump-realizable child " + tag); sys.exit(9)
            open(cert_out + ".PASS", "w").write("ok")
            rec.update(verdict="PASS", cert_path=cert_out)
        else:
            rec["verdict"] = f"FAIL(rc={p.returncode})"
    logline("  " + json.dumps({k: rec[k] for k in
                               ("tag", "budget", "tau", "eta", "converged", "lp_s", "cert_s", "verdict")}))
    append_rec(rec)
    return rec


# shared column pool (A57 T4: columns-only warm starts, sibling folding)
PILOT_WARM = None
PILOT_SEEN = None


def init_warm(max_atoms=0):
    global PILOT_WARM, PILOT_SEEN
    w, used = merged_warm("trump5", atoms_only=True, max_atoms=max_atoms)
    PILOT_WARM = dict(atoms=list(w["atoms"]), rows=[])
    PILOT_SEEN = {(round(p[0], 7), round(p[1], 7)) for p in PILOT_WARM["atoms"]}
    logline(f"warm pool: {len(PILOT_WARM['atoms'])} atoms (columns only) from {used}")
