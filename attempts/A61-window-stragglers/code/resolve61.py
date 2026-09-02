#!/usr/bin/env python3
"""
resolve61.py -- A61: close G-A56-1 (the 12 s0-only stratum-kill certificates).

A56's resolve_margin recipe converted 13/16 rows.  The 12 survivors all failed for one of
two reasons, both of which A61 attacks with banked machinery rather than more depth:

  (R1) the eps_geo schedule was CLAMPED below the conversion threshold.  A56 used
       eps_geo = clamp(0.003 * min(1, (budget - tau0)/1.0), 0.0002, 0.003) with tau0 the
       A53 certificate's own LP value, so a thin row got eps_geo = 0.001 - 0.0013, and
       soundness.md P6(v) measured eps_geo < 0.0015 -> 0/5 conversions.  The fix is to make
       the row AFFORD 0.003, i.e. to DROP tau0.  A55/k3_ext E3 + A57 T4/T13: the progress
       variable is the COLUMN pool, not tau's own dynamics, and A56's own aborted runs left
       4.9k-7.8k generated orbits sitting in `results/nodes/<name>_state.json` checkpoints
       that were never folded back.  Stage A folds every column this lab ever produced for
       the node (warm57 pattern, extended to A56/A61) and re-measures tau0.

  (R2) THE EPS_GEO LEAK (found in A61, see notes/lemmas.md L1).  resolve_margin sets
       lpbox.EPS_GEO in-process for its own solve_node call, then invokes A54 certify.py as
       a SUBPROCESS without --eps_geo -- so every witness-feedback re-solve inside certify
       (and with --loop_cols there are several, regenerating rows AND columns) runs at the
       default EPS_GEO = 1e-4.  The certificate that comes out is therefore built from a
       measure re-optimised at 1e-4 of shrink, i.e. the positional slack the 4D verifier
       needs was spent again inside certify.  A61 passes `--eps_geo <eps> --no_resolve`
       (that flag exists for exactly this: keep the margin, skip the redundant re-solve).

Third, cheaper lever: A56 tried ONLY the `gap` anchoring on these rows.  Anchoring is
completeness, never soundness (P3), and a 4D run costs 10-250 s, so on a 4D FAIL A61 walks
the full ladder gap -> nearest-wall -> mid-band before recording OPEN.

GATE (soundness.md P6(v), the 1500 s lesson).  Stage A measures slack0 = budget - tau0 at
the baseline shrink.  If slack0 < --gate (default 0.5) the row cannot pay for 0.003 of
positional slack (dtau/d eps ~ 1.4e2), and A61 STOPS THERE: no certify round is burnt.
The stage-A cost is bounded by --lp_time; a stall is recorded honestly.

Everything is written under attempts/A61-window-stragglers/.  A53/A54/A55/A56/A57 are
read-only sources; A29 is untouched.

Usage:
  python resolve61.py --name k6_21 [--eps_geo 0.003] [--lp_time 1500] [--gate 0.5]
"""
import os

# A57 T18 / A61 M1: pin every BLAS backend to ONE thread BEFORE numpy or highspy is imported.
# Concurrent workers' BLAS thread arenas fragment the address space, and the failure looks like
# an OOM at ~10 GB free (A57 lost a shard and a deepen job this way; A61 lost k5_05's stage A
# twice to `MemoryError: bad allocation`).  The enrichment LPs -- dense rows x orbits matrices
# at ~2k columns x ~15k rows -- are exactly the vulnerable class.
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse                                                       # noqa: E402
import glob                                                           # noqa: E402
import json                                                           # noqa: E402
import math                                                           # noqa: E402
import subprocess                                                     # noqa: E402
import sys                                                            # noqa: E402
import time                                                           # noqa: E402
from fractions import Fraction as F                                   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A61 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A61, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A54C = os.path.join(ATT, "A54-stragglers", "code")
A56 = os.path.join(ATT, "A56-sparametric")
A56C = os.path.join(A56, "code")
A57C = os.path.join(ATT, "A57-shadow-trees", "code")

# Solver of record: A57's copies of caselp/lpbox.  caselp is byte-identical to A54's; lpbox
# differs ONLY in the oracle chunk constant (A57 T19: `A57_CHUNK`, env `A57_ORACLE_CHUNK`,
# default 2e6), which bounds the numpy temporaries in the two oracle loops from 80/160 MB to
# 16/32 MB.  That edit is result-neutral bit for bit -- each output element is a dot product
# over the full inner dimension and each iteration writes a disjoint output slice, so only the
# loop count changes -- and COMMIT, not RAM, is this machine's binding constraint.
os.environ.setdefault("A57_ORACLE_CHUNK", "2e6")
sys.path.insert(0, A56C)
sys.path.insert(0, A54C)
sys.path.insert(0, A57C)
import sweep as SW                                                    # noqa: E402
from warm57 import merged_warm                                        # noqa: E402
from caselp import solve_node                                         # noqa: E402
from run_skel import hyp_from_slots, S0F                              # noqa: E402

CERTS = os.path.join(A61, "certs")
RESULTS = os.path.join(A61, "results")
NODES = os.path.join(RESULTS, "nodes")
LOGS = os.path.join(A61, "logs")
for _d in (CERTS, RESULTS, NODES, LOGS):
    os.makedirs(_d, exist_ok=True)

S0 = SW.S0
S_LO = SW.S_LO
STENCIL_XY = ((0, 0), (0.003, 0), (-0.003, 0), (0, 0.003), (0, -0.003),
              (0.006, 0.006), (-0.006, -0.006), (0.006, -0.006), (-0.006, 0.006))
STENCIL_TH = (0.0, 0.004, -0.004)
ANCHOR_TAG = {"gap": "gp", "nearest-wall": "nw", "mid-band": "mb"}


# ---------------------------------------------------------------- warm start
def cap_atoms(atoms, n_base, cap):
    """A61 M1 (measured): the guard LP builds a DENSE rows x orbits matrix, so a 7.4k-column
    pool at ~10k rows is ~600 MB before HiGHS copies it -- two concurrent workers OOM'd the
    box on k5_05.  Keep the node's own base columns, then subsample the folded-in generated
    pool UNIFORMLY (it is an accumulated column set, not an ordered one, so a uniform stride
    preserves its spread in placement space) up to `cap`."""
    if not cap or len(atoms) <= cap:
        return atoms, len(atoms)
    base = atoms[:min(n_base, cap)]
    rest = atoms[len(base):]
    room = cap - len(base)
    if room <= 0 or not rest:
        return base, len(atoms)
    step = max(1, len(rest) // room)
    return base + rest[::step][:room], len(atoms)


def lp_robust(name, hyp, budget, warm, eps, tlim, tag, L, rec, save, n_base, a):
    """A61 M1: HiGHS allocates a dense rows x orbits working matrix, so a fat pool at ~12k
    rows can exhaust the box with two concurrent workers.  Walk the pool down on
    MemoryError rather than losing the stratum."""
    caps = [a.max_atoms, a.max_atoms // 2, 900, 350]
    mcs = [a.max_cols_add, a.max_cols_add // 2, 300, 150]
    last = None
    for i, (cap, mc) in enumerate(zip(caps, mcs)):
        at = cap_atoms(list(warm["atoms"]), n_base, cap)[0]
        if last is not None and len(at) >= last:
            continue
        last = len(at)
        try:
            return lp(name, hyp, budget, dict(atoms=at, rows=warm["rows"]), eps, tlim,
                      tag, L, max_cols_add=mc, max_rows_add=(1200 if i == 0 else 800))
        except MemoryError:
            L(f"    MemoryError in stage {tag} at {len(at)} columns; stepping the pool down")
            rec.setdefault("memory_retries", []).append({"stage": tag, "columns": len(at)})
            save(rec)
    raise MemoryError(f"stage {tag}: LP exhausted memory at every pool size")


def enriched_warm(name):
    """Columns: every orbit/atom this lab ever produced for the node, INCLUDING A56's and
    A61's own interrupted-solve checkpoints.  Rows: A53's row set plus the 27-point stencil
    around every 4D witness A56/A61 ever recorded for the node (an LP row is just the demand
    mu(Q) >= 1 at a placement; adding it at s0 can only tighten the measure)."""
    extra = []
    for root in (A56, A61):
        extra += sorted(glob.glob(os.path.join(root, "results", "nodes", f"{name}*.json")))
        extra += sorted(glob.glob(os.path.join(root, "certs", "resolved", f"{name}*.resolve*.json")))
    cols, used_c = merged_warm(name, extra_sources=extra, atoms_only=True)

    atoms, seen_a = [], set()
    for p in cols["atoms"]:
        k = (round(p[0], 7), round(p[1], 7))
        if k not in seen_a:
            seen_a.add(k)
            atoms.append((p[0], p[1]))

    rows, seen_r = [], set()
    n_a53 = 0
    n_base = 0
    src = os.path.join(A53, "results", "nodes", f"{name}.json")
    if os.path.exists(src):
        n_base = len({(round(x[0], 7), round(x[1], 7))
                      for x in json.load(open(src)).get("atoms_all", [])})
        for r in json.load(open(src)).get("rows_all", []):
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k)
                rows.append((r[0], r[1], r[2]))
        n_a53 = len(rows)
    n_wit, used_w = 0, []
    wfs = []
    for root in (A56, A61):
        for pat in ("*.witnesses.json", "*.wit.json"):
            wfs += glob.glob(os.path.join(root, "certs", f"{name}{pat}"))
            wfs += glob.glob(os.path.join(root, "certs", "resolved", f"{name}{pat}"))
    for wf in sorted(set(wfs)):
        try:
            W = json.load(open(wf))["witnesses"]
        except Exception:
            continue
        used_w.append(os.path.basename(wf))
        for w in W:
            p = w.get("placement")
            if not p:
                continue
            n_wit += 1
            th = math.radians(p["theta_deg"])
            for dx, dy in STENCIL_XY:
                for dth in STENCIL_TH:
                    rows.append((p["cx_float"] + dx, p["cy_float"] + dy, th + dth))
    return (dict(atoms=atoms, rows=rows), sorted(set(used_c)) + used_w, n_a53, n_wit, n_base)


def lp(name, hyp, budget, warm, eps, tlim, tag, L, max_iter=4000, max_cols_add=800,
       prune_cols=3, max_rows_add=1200):
    """prune=0 keeps every row (tau monotone across iterations, A56's discipline).
    prune_cols > 0 deletes only ZERO-weight columns with strictly positive reduced cost
    (A14 semantics): they are not in the optimum, they are regenerable by the column
    oracle, and dropping them cannot lower tau -- it is purely a memory bound (A61 M1)."""
    import lpbox
    lpbox.EPS_GEO = eps
    t0 = time.time()
    res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=tlim,
                     max_iter=max_iter, out=None, log=L, prune=0, prune_cols=prune_cols,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=max_cols_add,
                     max_rows_add=max_rows_add, fine_slack=99.0, alternate=True,
                     checkpoint=os.path.join(NODES, f"{name}_{tag}_state.json"))
    res["skeleton_name"] = name
    res["k"] = 11 - budget
    dt = time.time() - t0
    L(f"    [{tag}] eps_geo={eps} tau={res['tau']:.6f} budget={budget} "
      f"slack={budget - res['tau']:.4f} conv={res['converged']} orbits={res['n_orbits']} "
      f"rows={res['n_rows']} ({dt:.0f}s)")
    return res, dt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--eps_geo", type=float, default=0.003)
    ap.add_argument("--gate", type=float, default=0.5,
                    help="soundness.md P6(v) repairability gate on budget - tau0")
    ap.add_argument("--gate_tol", type=float, default=1e-6,
                    help="slack tolerance on the gate (tau lands on exact rationals + noise)")
    ap.add_argument("--gate_b", type=float, default=0.03,
                    help="post-shrink gate on budget - tau(eps_geo) (A61 L5): the MEASURED "
                         "condition for a certificate to exist at all, replacing the "
                         "pre-gate's extrapolation once stage B has priced the shrink")
    ap.add_argument("--lp_time", type=float, default=1500, help="stage-A LP cap (s)")
    ap.add_argument("--lp_time_b", type=float, default=1100, help="stage-B LP cap (s)")
    ap.add_argument("--cert_time", type=float, default=420)
    ap.add_argument("--cert_rounds", type=int, default=4)
    ap.add_argument("--cert_depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.06)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--param_timeout", type=int, default=1200)
    ap.add_argument("--ladder", default="gap,nearest-wall,mid-band")
    ap.add_argument("--max_atoms", type=int, default=3000,
                    help="cap on the initial column pool (A61 M1: the dense LP matrix is "
                         "rows x orbits; 7.4k columns x 10k rows OOM'd two workers)")
    ap.add_argument("--max_cols_add", type=int, default=800)
    ap.add_argument("--force", action="store_true", help="ignore the gate (diagnostic only)")
    a = ap.parse_args(argv)

    name = a.name
    out_rec = os.path.join(RESULTS, f"resolve61_{name}.json")
    log = os.path.join(LOGS, f"resolve61_{name}.log")
    lf = open(log, "a", buffering=1, encoding="utf-8")

    def L(*x):
        print(*x, file=lf, flush=True)
        print(*x, flush=True)

    def save(rec):
        json.dump(rec, open(out_rec, "w"), indent=1)

    slots = [tuple(p) for p in json.load(
        open(os.path.join(A53, "results", "name_to_slots.json")))[name]]
    k = len(slots)
    budget = 11 - k
    hyp = hyp_from_slots(slots)
    rec = {"name": name, "k": k, "budget": budget, "eps_geo": a.eps_geo, "gate": a.gate,
           "recipe": "A61 resolve61: enriched column pool (warm57 + A56/A61 checkpoints) "
                     "-> slack gate -> eps_geo re-solve -> certify WITH --eps_geo "
                     "(A61 L1 leak fix) -> 4D depth 48 with the anchoring ladder",
           "started": time.strftime("%Y-%m-%dT%H:%M:%S")}

    warm, used, n_a53, n_wit, n_base = enriched_warm(name)
    warm["atoms"], n_pool = cap_atoms(warm["atoms"], n_base, a.max_atoms)
    L(f"=== {name}: k={k} budget={budget}; enriched warm = {len(warm['atoms'])} columns "
      f"(pool {n_pool}, base {n_base}, cap {a.max_atoms}), {len(warm['rows'])} rows "
      f"({n_a53} A53 + {n_wit} 4D witnesses x 27)")
    rec.update(warm_atoms=len(warm["atoms"]), warm_pool=n_pool, warm_base=n_base,
               max_atoms=a.max_atoms, warm_rows=len(warm["rows"]),
               warm_rows_from_a53=n_a53, n_4d_witnesses=n_wit, warm_sources=used)
    save(rec)

    # ---------------------------------------------------------------- stage A: tau0
    t_all = time.time()
    resA, dtA = lp_robust(name, hyp, budget, warm, 1e-4, a.lp_time, "A", L, rec, save,
                          n_base, a)
    json.dump(resA, open(os.path.join(NODES, f"{name}.stageA.json"), "w"))
    tau0 = resA["tau"]
    slack0 = budget - tau0
    rec.update(stageA={"eps_geo": 1e-4, "tau0": tau0, "slack0": slack0,
                       "converged": resA["converged"], "n_orbits": resA["n_orbits"],
                       "n_rows": resA["n_rows"], "seconds": round(dtA, 1),
                       "minmass": resA["minmass"], "maxcov": resA["maxcov"]})
    save(rec)
    # P6(v)'s gate is a measured "~0.5", and tau lands on exact rationals plus solver noise
    # (k5_10: tau0 = 5.5 + 4e-13 at budget 6), so the comparison carries a tolerance --
    # otherwise a row sitting EXACTLY on the law is refused on floating-point dust.
    if slack0 < a.gate - a.gate_tol and not a.force:
        rec["verdict"] = "GATE-FAIL (enrichment stalled: budget - tau0 < gate)"
        rec["total_seconds"] = round(time.time() - t_all, 1)
        L(f"    GATE-FAIL: slack0={slack0:.4f} < {a.gate}; no certify round burnt.")
        save(rec)
        return 3

    # ---------------------------------------------------------------- stage B: eps_geo
    bat, seen = [], set()
    for p in [(x[0], x[1]) for x in resA["atoms_all"]] + list(warm["atoms"]):
        kk = (round(p[0], 7), round(p[1], 7))
        if kk not in seen:
            seen.add(kk)
            bat.append(p)
    warmB = dict(atoms=bat, rows=[tuple(r) for r in resA["rows_all"]])
    resB, dtB = lp_robust(name, hyp, budget, warmB, a.eps_geo, a.lp_time_b, "B", L, rec,
                          save, len(resA["atoms_all"]), a)
    node_out = os.path.join(NODES, f"{name}.json")
    resB["skeleton_slots"] = [[x, y] for (x, y) in slots]
    json.dump(resB, open(node_out, "w"))
    rec.update(stageB={"eps_geo": a.eps_geo, "tau": resB["tau"],
                       "slack": budget - resB["tau"], "converged": resB["converged"],
                       "n_orbits": resB["n_orbits"], "n_rows": resB["n_rows"],
                       "seconds": round(dtB, 1), "minmass": resB["minmass"],
                       "maxcov": resB["maxcov"]},
               dtau_deps=((resB["tau"] - tau0) / (a.eps_geo - 1e-4)))
    save(rec)
    # POST-SHRINK GATE (A61 L5).  P6(v)'s pre-gate on slack0 is a PREDICTOR of whether the row
    # can pay for the shrink; stage B has now MEASURED the price, so gate on the measured
    # quantity.  certify builds total = tau_eps * scale with scale >= 1.005, so a kill needs
    # budget - tau_eps > 0.005 * tau_eps (~0.028 here); --gate_b is that with headroom.  This
    # keeps the abort-early property (no certify round is burnt on a row that provably cannot
    # certify) without inheriting the pre-gate's conservatism.
    slack_e = budget - resB["tau"]
    if slack_e < a.gate_b:
        rec["verdict"] = (f"POST-SHRINK GATE-FAIL at eps_geo={a.eps_geo}: "
                          f"budget - tau = {slack_e:.5f} < {a.gate_b}")
        rec["total_seconds"] = round(time.time() - t_all, 1)
        L("    " + rec["verdict"] + "; no certify round burnt.")
        save(rec)
        return 1

    # ---------------------------------------------------------------- certify (L1 fix)
    cert_out = os.path.join(CERTS, f"{name}.json")
    # A57 T19: certify at --jobs 1 -- verify_case then takes its IN-PROCESS branch instead of
    # forking per-job verifiers, saving ~1.3 GB of commit per concurrent certify.  The verifier
    # result is identical; only the parallel decomposition changes.
    cmd = [sys.executable, os.path.join(A54C, "certify.py"), node_out, "--s_rat", str(S0),
           "--rounds", str(a.cert_rounds), "--jobs", "1", "--depth", str(a.cert_depth),
           "--time_limit", str(a.cert_time), "--out", cert_out, "--scale", "0",
           "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "96", "--loop_cols",
           "--eps_geo", str(a.eps_geo), "--no_resolve",          # <-- A61 L1: keep the shrink
           "--warm_state", os.path.join(NODES, f"{name}_B_state.json")]
    L("    " + " ".join(cmd))
    t1 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    L(p.stdout[-8000:])
    rec["certify_seconds"] = round(time.time() - t1, 1)
    rec["certify"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
    save(rec)
    if p.returncode != 0:
        rec["verdict"] = "fixed-s re-certification failed; no base certificate produced"
        rec["total_seconds"] = round(time.time() - t_all, 1)
        save(rec)
        return 1
    cj = json.load(open(cert_out))
    rec["new_cert"] = {"path": cert_out, "atoms": len(cj["atoms"]), "total": cj["total"],
                       "margin": budget - float(F(cj["total"]))}
    save(rec)

    # ---------------------------------------------------------------- 4D + anchoring ladder
    rec["anchoring_tried"] = []
    for anch in a.ladder.split(","):
        tg = ANCHOR_TAG[anch]
        par = os.path.join(CERTS, f"{name}.{tg}.param.json")
        rc, _ = SW.build_param(name, cert_out, par, anch, log)
        if rc != 0:
            rec["anchoring_tried"].append({"anchoring": anch, "result": "MAKE_PARAM_ERROR"})
            continue
        rep = os.path.join(CERTS, f"{name}.{tg}.param.report.json")
        t2 = time.time()
        rc, dt = SW.sh([sys.executable, SW.VERIFY_PARAM, par, "--slo", str(S_LO),
                        "--shi", str(S0), "--depth", str(a.depth), "--sscale", "8",
                        "--jobs", str(a.jobs), "--split", "3", "--report", rep,
                        "--max-witnesses", "20", "--witness-file",
                        os.path.join(CERTS, f"{name}.{tg}.param.wit.json"), "--quiet"],
                       log, timeout=a.param_timeout)
        r = {"anchoring": anch, "seconds": round(dt, 1),
             "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)}
        if os.path.exists(rep):
            d = json.load(open(rep))
            r["stats"] = {q: d.get("stats", {}).get(q) for q in
                          ("boxes", "s_splits", "s_cells", "max_depth", "max_s_depth")}
            r["witness_s_range"] = d.get("witness_s_range")
            r["n_witnesses"] = len(d.get("witnesses", []) or [])
        rec["anchoring_tried"].append(r)
        L(f"    4D[{anch}] {r['result']} {r['seconds']}s")
        save(rec)
        if rc == 0:
            rec["anchoring"] = anch
            rec["param_cert"] = par
            rec["param_report"] = rep
            rec["c2"] = c2(name, par, log, a)
            rec["verdict"] = ("A61 CONVERTS (full window)"
                              if all(x.get("result") == "PASS" for x in rec["c2"])
                              else "C2-DISCREPANCY")
            rec["total_seconds"] = round(time.time() - t_all, 1)
            save(rec)
            L("    " + rec["verdict"])
            return 0
    rec["verdict"] = "recipe did NOT convert (4D still open on every anchoring)"
    rec["total_seconds"] = round(time.time() - t_all, 1)
    save(rec)
    return 1


def c2(name, par, log, a):
    """canary C2: the UNMODIFIED A53 verify_case.py on the specialisations at lo/mid/s0."""
    d = os.path.join(CERTS, "c2")
    os.makedirs(d, exist_ok=True)
    out = []
    for lbl, s in (("lo", S_LO), ("mid", (S_LO + S0) / 2), ("hi", S0)):
        spec = os.path.join(d, f"{name}.{lbl}.json")
        rep = os.path.join(d, f"{name}.{lbl}.report.json")
        rc, _ = SW.sh([sys.executable, SW.SPECIALIZE, par, "--s", str(s), "-o", spec], log)
        if rc != 0:
            out.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = SW.sh([sys.executable, SW.VERIFY_CASE, spec, "--depth", "44",
                        "--jobs", str(a.jobs), "--report", rep, "--max-witnesses", "20",
                        "--witness-file", os.path.join(d, f"{name}.{lbl}.wit.json"),
                        "--quiet"], log, timeout=1800)
        out.append({"s": str(s), "s_float": float(s), "time_s": round(dt, 1),
                    "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)})
        if rc != 0:
            break
    return out


if __name__ == "__main__":
    sys.exit(main())
