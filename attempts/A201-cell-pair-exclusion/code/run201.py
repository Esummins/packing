"""A201 driver: the quick chain (g1 pad, then pad 0) with the cell-pair table; certificates certs/pe201_<nid>[_pad0].json,
results/pairexcl201.jsonl, the page docs/residue_map/pairexcl201_<nid>.svg drawn from the certificates after the fast steps.
    python run201.py <nid> [--wall 600] [--pad g1|zero|window] [--chain] [--budget 60] [--noexact] [--seal]
"""
import argparse
import json
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")                              # BLAS pinned to one thread (set before numpy loads)
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
try:                                                           # BelowNormal + affinity 0xFFFF (the lab's ops rules)
    import ctypes
    _k = ctypes.windll.kernel32
    _k.SetPriorityClass(_k.GetCurrentProcess(), 0x4000)
    _k.SetProcessAffinityMask(_k.GetCurrentProcess(), ctypes.c_size_t(0xFFFF))
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quick201 as Q1                                          # noqa: E402
import fastprop as FP                                          # noqa: E402  READ-ONLY (A198)
import quick200 as Q                                           # noqa: E402  READ-ONLY (A200)

ROOT = Q1.ROOT
ATT201 = os.path.join(ROOT, "attempts", "A201-cell-pair-exclusion")
CERTS = os.path.join(ATT201, "certs")
RES = os.path.join(ATT201, "results", "pairexcl201.jsonl")
SVGD = os.path.join(ROOT, "docs", "residue_map")
A200C = os.path.join(ROOT, "attempts", "A200-k516-quick", "certs")


def prior_witness(nid, pad):
    """A200's count witness for the page at this pad (the cover the table is asked about first)."""
    f = os.path.join(A200C, "q200_%s%s.json" % (nid, "_pad0" if pad == "zero" else ""))
    if not os.path.exists(f):
        return None, None
    try:
        c = json.load(open(f, encoding="utf-8"))
    except Exception:
        return None, None
    w = [(who, int(ci), list(S)) for who, ci, S, _h in (c.get("witness") or [])]
    return (w or None), os.path.relpath(f, ROOT).replace("\\", "/")


def run_page(nid, wall=600, depth=5, joint_depth=2, refine_union=2, pad="g1", budget=180.0, exact=True, log=print):
    T = FP.Trace(wall=wall)
    rec, cls, row = FP.load_page(nid)
    pw, pwf = prior_witness(nid, pad)
    log("== %s (%s) at the %s pad: %d pins, H %s; pair budget %.0f s (exact %s); prior witness %s" % (
        nid, cls, pad, len(rec["pins"]), [round(v, 3) for v in rec["H"][0]], budget, exact, pwf))
    pg = Q1.QPage201(rec, cls, nid, T, depth=depth, joint_depth=joint_depth, refine_union=refine_union, pad=pad,
                     pair_budget=budget, pair_exact=exact, prior_witness=pw)
    out = pg.run()
    for rd in out["rounds"]:
        log("   round %d: alive cells %s; caps %s; H reaches %s; forced_H %s; roles %s; instantiate %s; count %s / chords %s%s" % (
            rd["round"], {p: len(v) for p, v in rd["single"].items()}, rd.get("caps"), rd.get("H_reach"), rd.get("forced_H"),
            rd.get("forced_role"), rd.get("instantiate"), (rd.get("count_nochord") or {}).get("feasible"),
            (rd.get("count_chord") or {}).get("feasible"), ("; DEAD: " + rd["dead"]) if rd.get("dead") else ""))
        pe = rd.get("pair_excl") or {}
        if pe:
            log("      pair table: %s" % {k: pe.get(k) for k in ("lookups", "a1", "cn", "exact_tested", "exact_excl", "undecided_budget", "exact_seconds", "by_rule")})
        wc = rd.get("witness_check")
        if wc:
            log("      A200 witness cover (%d/%d rows found): %s" % (wc["n_found"], wc["n_keys"], "DEAD -- " + "; ".join(
                "%s|%s %s" % (p["a"], p["b"], p["rule"]) for p in wc["pairs"] if not p["compatible"]) if wc["dead"] else "every pair compatible"))
    out["step_killed"] = "propagation" if out["verdict"] == "DEAD" else None
    out["pad"], out["lam"] = pad, float(Q.PADS[pad])
    out["window_pending"] = (pad == "zero") and out["verdict"] == "DEAD"
    if out["window_pending"]:
        out["leaf"] = (out["leaf"] or "") + " [pad 0: s0-only, WINDOW-PENDING]"
    out["prior_witness_cert"] = pwf
    out["tests"], out["steps"], out["seconds"] = T.tests, T.steps, round(T.now(), 1)
    out["row"] = dict(family=row.get("family"), camp=row.get("camp"), tau=row.get("tau"))
    out["decisive_rules"] = sorted(set(u["rule"] for rd in out["rounds"] for lab, us in ((rd.get("pair_excl") or {}).get("used") or {}).items()
                                       for u in us)) if out["verdict"] == "DEAD" else []
    log("   => %s in %.1f s (%d exact tests)%s%s" % (out["verdict"], out["seconds"], len(T.tests), ("; " + out["leaf"]) if out["leaf"] else "",
                                                     ("; decisive rules %s" % out["decisive_rules"]) if out["decisive_rules"] else ""))
    return out, pg


def emit(out, cert, res):
    if cert:
        json.dump(out, open(cert, "w", encoding="utf-8"), indent=1, default=str)
    if res:
        slim = {k: v for k, v in out.items() if k not in ("tests", "steps", "rounds", "seal", "noroom", "pair_excl")}
        pe = out.get("pair_excl") or {}
        slim["pair_excl"] = [{k: v for k, v in r.items() if k not in ("excl", "used")} for r in pe.get("rounds", [])]
        slim["cert"] = os.path.relpath(cert, ROOT).replace("\\", "/") if cert else None
        slim["n_rounds"] = len(out.get("rounds") or [])
        slim["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(res, "a", encoding="utf-8") as f:
            f.write(json.dumps(slim, default=str) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--wall", type=float, default=600)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument("--jdepth", type=int, default=2)
    ap.add_argument("--refine-union", type=int, default=2)
    ap.add_argument("--pad", default="g1", choices=("window", "g1", "zero"))
    ap.add_argument("--chain", action="store_true", help="g1 pad, then (if ALIVE) pad 0")
    ap.add_argument("--budget", type=float, default=180.0, help="seconds of exact pair nodes per page (rule (c))")
    ap.add_argument("--noexact", action="store_true", help="rules (a)(b) only")
    ap.add_argument("--seal", action="store_true", help="A200's SEAL leaf at pad 0 if still alive")
    ap.add_argument("--nosvg", action="store_true")
    a = ap.parse_args()
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    pads = ("g1", "zero") if a.chain else (a.pad,)
    outs, pages = [], []
    for k, pad in enumerate(pads):
        out, pg = run_page(a.nid, wall=a.wall, depth=a.depth, joint_depth=a.jdepth, refine_union=a.refine_union, pad=pad,
                           budget=a.budget, exact=not a.noexact)
        out["path"], out["chain_done"] = "quick", out["verdict"] == "DEAD" or pad == "zero" or not a.chain
        cert = os.path.join(CERTS, "pe201_%s%s.json" % (a.nid, "_pad0" if pad == "zero" else ""))
        out["cert_path"] = cert
        emit(out, cert, RES)
        outs.append(out); pages.append(pg)
        if not a.nosvg:
            try:
                import fig201
                fig201.render_page(a.nid)
            except Exception as e:
                print("   fig201 failed: %r" % (e,), flush=True)
        if out["verdict"] == "DEAD":
            break
    if a.seal and outs[-1]["verdict"] == "ALIVE" and pages[-1].pad == "zero":
        out, pg = outs[-1], pages[-1]
        sl = Q.seal_leaf(pg, a.wall, print)
        out["seal"] = sl
        if sl and sl["verdict"] == "DEAD":
            out["verdict"], out["leaf"], out["step_killed"] = "DEAD", sl["leaf"] + " [pad 0: s0-only, WINDOW-PENDING]", "seal"
            out["window_pending"] = True
        out["tests"], out["steps"], out["seconds"] = pg.T.tests, pg.T.steps, round(pg.T.now(), 1)
        emit(out, out["cert_path"], RES)
