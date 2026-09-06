"""A111 T2 -- the NO side: does excluding the load path kill the parents?

The complement of the YES region is a DISJUNCTION ("for some box i, no square of the packing lies
in F_i"), so it is handled the way A57 handles a NO child: one child per box, each carrying ONE
NO-family (caselp.NoFam = a centre rectangle x a set of tilt intervals), and the parent dies only
if EVERY child dies.  Adding a NO-family removes rows from the node LP (placements inside the
family are exempt), so tau can only FALL: the question is whether it falls below the budget --
which is unchanged, because a NO-family accounts for no square.

Per node: copy the campaign's node json (read-only), map the shadow's boxes into the node's own
frame with the inverse of A107's struct_op, build one NO-family per box, re-solve the node LP warm
from the parent's own atoms/rows, and record tau, eta = tau - budget, converged, dead.  For a child
that does NOT die, the new dual support is descended to a local minimum (A107's structure
minimisation) and matched against A107's shadow table, which is A109's re-pricing question: does
the LP just move to another shadow?

Writes results/t2_runs_s<shard>.jsonl and results/nodes/<tag>.json.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1
import numpy as np
from caselp import Hyp, NoFam, Box, solve_node, warm_from_result

ROOT = L.ROOT
A107R = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A110R = os.path.join(ROOT, "attempts", "A110-grain-flood", "results")
sys.path.insert(0, os.path.join(ROOT, "attempts", "A107-shadow-gallery", "code"))
import shadowlib as SL          # noqa: E402
import minimise as MZ           # noqa: E402


# ------------------------------------------------------------------ boxes -> node frame
def box_image(b, op, s):
    """Image of a caselp-style box under a D4 element (an isometry of [0,s]^2): the centre
    rectangle maps to a rectangle, the tilt interval to +-[th0, th1] reduced mod 90."""
    f = L.d4_ops(s)[op]
    xs, ys = [], []
    for (x, y) in ((b["x0"], b["y0"]), (b["x1"], b["y0"]), (b["x0"], b["y1"]), (b["x1"], b["y1"])):
        X, Y, _ = f(x, y, 0.0)
        xs.append(X); ys.append(Y)
    flip = op in ("mx", "my", "diag", "anti")
    t0, t1 = (-b["th1"], -b["th0"]) if flip else (b["th0"], b["th1"])
    return dict(x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), th0=t0, th1=t1)


def theta_intervals(th0, th1):
    """[th0, th1] (degrees, any offset) as a union of intervals inside [0, 90]."""
    if th1 - th0 >= 90.0:
        return [(0.0, 90.0)]
    a = th0 % 90.0
    b = a + (th1 - th0)
    if b <= 90.0:
        return [(a, b)]
    return [(a, 90.0), (0.0, b - 90.0)]


def nofam_of(b, s):
    x0 = max(0.5, min(b["x0"], s - 0.5)); x1 = max(0.5, min(b["x1"], s - 0.5))
    y0 = max(0.5, min(b["y0"], s - 0.5)); y1 = max(0.5, min(b["y1"], s - 0.5))
    return NoFam(x0, x1, y0, y1, theta_intervals(b["th0"], b["th1"]))


def node_boxes(tag, variant, cls, r, rho, op, s):
    pn = T1.CLASS_PINS.get(cls, tuple(L.shadow(tag)[3]))
    ext = T1.anchors(tag, pn) if variant == "lpa" else ()
    _, _, _, _, _, box_names, B = T1.make_boxes(tag, r, rho, extra=ext)
    inv = L.D4_INV[op]
    return box_names, {n: box_image(B[n], inv, s) for n in box_names}


# ------------------------------------------------------------------ node selection
def load_plan(tag, limit, levels=None, inside=None, srcs=None):
    sn = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))[tag]
    ex = {(n["src"], n["nid"]): n for n in
          json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]}
    t4 = {}
    p4 = os.path.join(A110R, "t4_%s.jsonl" % tag)
    if os.path.exists(p4):
        for line in open(p4, encoding="utf-8"):
            d = json.loads(line)
            t4[(d["src"], d["nid"])] = d
    out = []
    for rec in sn:
        key = (rec["src"], rec["nid"])
        e = ex.get(key)
        if e is None:
            continue
        d4 = t4.get(key, {})
        cls = None
        for c in ("k5_11", "k5_16", "trump5"):
            if rec["nid"].startswith(c) or (rec["src"] in ("A60", "A61") and c == "trump5"):
                cls = c; break
        out.append(dict(shadow=tag, src=rec["src"], nid=rec["nid"], level=rec["level"],
                        cls=cls or "trump5", op=e.get("struct_op") or "e", budget=rec["budget"],
                        tau0=rec["tau"], via=rec["via"],
                        inside_family=bool(d4.get("inside_family")),
                        dmax=d4.get("dmax")))
    if srcs:
        out = [o for o in out if o["src"] in srcs]
    if levels:
        out = [o for o in out if o["level"] in levels]
    if inside is not None:
        out = [o for o in out if o["inside_family"] == inside]
    out.sort(key=lambda o: (not o["inside_family"], o["level"], o["nid"]))
    if limit:
        # stratify: alternate inside/outside and levels
        keep, seen = [], {}
        for o in out:
            k = (o["inside_family"], o["level"], o["cls"])
            seen.setdefault(k, 0)
            keep.append((seen[k], k, o))
            seen[k] += 1
        keep.sort(key=lambda t: (t[0], t[1]))
        out = [t[2] for t in keep[:limit]]
    return out


# ------------------------------------------------------------------ re-pricing: which shadow?
_SH = None


def shadow_table():
    global _SH
    if _SH is None:
        _SH = json.load(open(os.path.join(A107R, "shadows.json"), encoding="utf-8"))
    return _SH


def land(res, tlim=6.0):
    """Descend the node's dual support to a local minimum of the side (A107's structure
    minimisation with the snapped slots fixed) and name the shadow it lands on."""
    try:
        s = res["s"]
        cores = [(float(c["float"]["kx"]), float(c["float"]["ky"]),
                  math.radians(c["float"]["theta_deg"])) for c in res["hyp"]["cores"]]
        frac = [(float(p["cx"]), float(p["cy"]), float(p["theta"]), float(p.get("y", 0.0)))
                for p in res.get("packing", []) if float(p.get("y", 0.0)) > 1e-6]
        frac.sort(key=lambda q: -q[3])
        cfg = list(cores)
        for q in frac:
            if len(cfg) >= 11:
                break
            if all(SL.sat_gap(q[:2], q[2], c[:2], c[2]) >= -0.21 for c in cfg):
                cfg.append(q[:3])
        if len(cfg) < 11:
            return None
        slots, free = [], []
        for q in cfg:
            nm = SL.snap(q[0], q[1], q[2], s)
            (slots if nm else free).append(nm if nm else q)
        cons = MZ.make_cons(tuple(slots), len(free))
        z0 = np.array([s] + [v for q in free for v in q])
        z, sv, feas = MZ.solve(cons, z0, len(free))
        if feas < -1e-7:
            return dict(landed=None, feas=feas)
        best = min(shadow_table(), key=lambda d: abs(d["s"] - sv))
        return dict(landed=round(sv, 6), shadow=(best["id"] if abs(best["s"] - sv) < 2e-4 else None),
                    shadow_s=round(best["s"], 6), nslots=len(slots), nfree=len(free))
    except Exception as ex:
        return dict(error=repr(ex)[:120])


# ------------------------------------------------------------------ one node
def one(plan, tag, variant, r, rho, lp_time, probe_time, log, do_land=True, suffix=""):
    nid, src, cls, op = plan["nid"], plan["src"], plan["cls"], plan["op"]
    p = L.copy_node(nid, src)
    if p is None:
        return [dict(nid=nid, src=src, error="node json not found")]
    res0 = json.load(open(p, encoding="utf-8"))
    s = res0["s"]
    budget = res0["budget"]
    box_names, NB = node_boxes(tag, variant, cls, r, rho, op, s)
    hyp0 = Hyp.from_json(res0["hyp"])
    warm0 = warm_from_result(res0)
    warm0["rows"] = warm0["rows"][:20000]
    recs = []
    for i, n in enumerate(box_names):
        tagid = "%s__%s__%s__r%g_p%g__NO%d%s" % (nid, tag, variant, r, rho, i, suffix)
        outp = os.path.join(L.NODES, tagid + ".json")
        rec = dict(nid=nid, src=src, cls=cls, shadow=tag, variant=variant, r=r, rho=rho,
                   op=op, box=n, box_node_frame=NB[n], level=plan["level"],
                   inside_family=plan["inside_family"], budget=budget,
                   tau0=res0["tau"], conv0=bool(res0.get("converged")),
                   eta0=res0["tau"] - budget, tag=tagid)
        if os.path.exists(outp):
            rr = json.load(open(outp, encoding="utf-8"))
            rec.update(tau=rr["tau"], eta=rr["tau"] - budget, converged=bool(rr["converged"]),
                       minmass=rr["minmass"], maxcov=rr["maxcov"], reused=True,
                       dead=bool(rr["converged"] and rr["tau"] < budget - 1e-6),
                       dead_unconv=bool(rr["tau"] < budget - 1e-6),
                       land=rr.get("a111_land"))
            recs.append(rec)
            continue
        hyp = Hyp(hyp0.boxes, list(hyp0.nofams) + [nofam_of(NB[n], s)])
        t0 = time.time()
        kw = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None, prune=0,
                  prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                  max_rows_add=2000, fine_slack=99.0, alternate=True)
        rr = solve_node(s, hyp, budget, warm=dict(warm0), time_limit=min(probe_time, lp_time), **kw)
        if rr["tau"] >= budget and lp_time > probe_time + 30:
            rr = solve_node(s, hyp, budget, warm=warm_from_result(rr),
                            time_limit=lp_time - probe_time, **kw)
        lp_s = round(time.time() - t0, 1)
        rr["a111"] = dict(nid=nid, shadow=tag, variant=variant, r=r, rho=rho, box=n, op=op)
        if do_land:
            rr["a111_land"] = land(rr)
        rr["a111_lp_s"] = lp_s
        json.dump(rr, open(outp, "w"))
        rec.update(tau=rr["tau"], eta=rr["tau"] - budget, converged=bool(rr["converged"]),
                   minmass=rr["minmass"], maxcov=rr["maxcov"], lp_s=lp_s, reused=False,
                   dead=bool(rr["converged"] and rr["tau"] < budget - 1e-6),
                   dead_unconv=bool(rr["tau"] < budget - 1e-6), land=rr.get("a111_land"))
        recs.append(rec)
        log("    %-58s tau %.4f -> %.4f  eta %+.4f  conv=%s  %s  land=%s  (%ss)"
            % (tagid, rec["tau0"], rec["tau"], rec["eta"], rec["converged"],
               "DEAD" if rec["dead"] else ("dead-unconv" if rec["dead_unconv"] else "alive"),
               (rec["land"] or {}).get("shadow"), lp_s))
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="S02")
    ap.add_argument("--variant", default="lpa")
    ap.add_argument("--r", type=float, default=0.05)
    ap.add_argument("--rho", type=float, default=5.0)
    ap.add_argument("--limit", type=int, default=24)
    ap.add_argument("--levels", default="1,2")
    ap.add_argument("--inside", default="any", choices=["any", "yes", "no"])
    ap.add_argument("--srcs", default="")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--probe_time", type=float, default=110.0)
    ap.add_argument("--minutes", type=float, default=240.0)
    ap.add_argument("--no_land", action="store_true")
    ap.add_argument("--suffix", default="", help="tag suffix: a fresh cache slot, so the same node can be re-solved with a longer LP cap")
    ap.add_argument("--only", default="", help="comma list of nids")
    ap.add_argument("--sink", default=None)
    A = ap.parse_args()
    T_END = time.time() + 60 * A.minutes
    logp = os.path.join(L.LOGS, "t2_s%d.log" % A.shard)

    def log(*x):
        m = " ".join(str(v) for v in x)
        print(m, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + m + "\n")

    inside = {"any": None, "yes": True, "no": False}[A.inside]
    plan = load_plan(A.tag, A.limit, levels=[int(v) for v in A.levels.split(",") if v],
                     inside=inside, srcs=[v for v in A.srcs.split(",") if v])
    if A.only:
        keep = set(v for v in A.only.split(",") if v)
        plan = [p for p in plan if p["nid"] in keep]
    plan = [p for i, p in enumerate(plan) if i % A.nshards == A.shard]
    sink = A.sink or os.path.join(L.RES, "t2_runs_s%d.jsonl" % A.shard)
    log("T2 %s/%s r=%g rho=%g: %d nodes (shard %d/%d)"
        % (A.tag, A.variant, A.r, A.rho, len(plan), A.shard, A.nshards))
    for pl in plan:
        if time.time() > T_END:
            log("wall budget exhausted"); break
        if not L.gate(log, pl["nid"], deadline=T_END):
            continue
        log("  %s/%s L%d cls=%s op=%s inside=%s tau0=%.4f budget=%d"
            % (pl["src"], pl["nid"], pl["level"], pl["cls"], pl["op"],
               pl["inside_family"], pl["tau0"], pl["budget"]))
        try:
            recs = one(pl, A.tag, A.variant, A.r, A.rho, A.lp_time, A.probe_time, log,
                       do_land=not A.no_land, suffix=A.suffix)
        except BaseException as ex:
            import traceback
            log("    ERROR %s: %s" % (pl["nid"], traceback.format_exc()[-500:]))
            recs = [dict(nid=pl["nid"], error=repr(ex)[:200])]
        with open(sink, "a") as f:
            for rr in recs:
                f.write(json.dumps(rr) + "\n")
        ok = [rr for rr in recs if rr.get("dead")]
        log("    -> %d/%d children DEAD, %d dead-unconverged"
            % (len(ok), len(recs), sum(1 for rr in recs if rr.get("dead_unconv"))))
    log("T2 shard %d done" % A.shard)


if __name__ == "__main__":
    main()
