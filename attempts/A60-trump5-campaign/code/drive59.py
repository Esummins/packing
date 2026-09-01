"""A59 pilot driver: the M1-M6 measurements of pilot_design.md v2.  See pilot59.py for the
solve/certify unit and the inherited semantics."""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pilot59 as P
from pilot59 import (BASE, S0F, PINS, SLOTS, FREE, T7, DEEP_OTHERS, rq, core_box, sib_box,
                     no_fam_7, deep_cores, boxes_pairwise_disjoint, run_child, logline, init_warm)
from caselp import Box, NoFam, Hyp, solve_node
from pinguard import classify
from substrat import zones


# ------------------------------------------------------------------ M5: pinguard statistics
def m5(w=0.15, nth=8, a_min=0.34):
    from tree57 import cover
    rect = zones(S0F, 0.6)["interior"]
    boxes, bad, grid = cover(rect, S0F, w, nth, a_min)
    counts = dict(cover=len(boxes), uncoverable=len(bad), contradictory=0, ok=0, parent=0, nocore=0)
    trump_boxes = 0
    Pl = [(x, y, math.degrees(th) % 90.0) for (x, y, th) in FREE.values()]
    for b in boxes:
        st, info = classify(b, PINS, SLOTS)
        counts[st] = counts.get(st, 0) + 1
        if any(b.x0 - 1e-5 <= x <= b.x1 + 1e-5 and b.y0 - 1e-5 <= y <= b.y1 + 1e-5 and
               b.th0 - 1e-4 <= th <= b.th1 + 1e-4 for (x, y, th) in Pl):
            trump_boxes += 1
    counts["boxes_containing_a_trump_free_placement"] = trump_boxes
    counts["grid"] = list(grid)
    counts["a_min_core"] = min(float(b.core().a) for b in boxes)
    counts["a_max_core"] = max(float(b.core().a) for b in boxes)
    dc = deep_cores()
    counts["deep_node_audit"] = dict(
        pinguard=[classify(b, PINS, SLOTS)[0] for b in dc],
        pairwise_overlaps_with_pins=boxes_pairwise_disjoint(dc + PINS),
        core_a=[float(b.core().a) for b in dc])
    json.dump(counts, open(os.path.join(BASE, "results", "m5_pinguard.json"), "w"), indent=1)
    logline("M5 " + json.dumps(counts))
    return counts


# ------------------------------------------------------------------ M3: interior NO child
def m3(lp_time=900.0, cert_time=300.0):
    rect = (1.1, 2.777, 1.1, 2.777)
    hyp = Hyp(PINS, [NoFam(rect[0], rect[1], rect[2], rect[3], [(0.0, 90.0)])])
    return run_child("m3_trump5_interior_NO", hyp, 6, 0, None, None, "NO-zone",
                     "ok", None, dict(rect=list(rect), thetas=[[0.0, 90.0]]),
                     lp_time=lp_time, cert_time=cert_time)


# ------------------------------------------------------------------ M1 ladders
LADDER = [0.075, 0.0375, 0.019, 0.0094, 0.0047, 0.0037]


def m1_shallow(ladder=None, lp_time=300.0, cert_time=240.0):
    out, fails = [], 0
    for a in (ladder or LADDER):
        lvl_pass = False
        for (at, mark) in ((a, "tmatch"), (0.566 * a, "trad")):
            b = sib_box(a, at, "cx")
            st, info = classify(b, PINS, SLOTS)
            r = run_child("m1s_cx_a%g_%s" % (a, mark), Hyp(PINS + [b], []), 5, 1, a, at,
                          "YES-sib", st, info, b.to_json(), lp_time=lp_time, cert_time=cert_time)
            if r:
                out.append(r)
                lvl_pass = lvl_pass or r["verdict"] == "PASS"
        at = 0.566 * a
        b = sib_box(a, at, "t")
        st, info = classify(b, PINS, SLOTS)
        r = run_child("m1s_t_a%g" % a, Hyp(PINS + [b], []), 5, 1, a, at,
                      "YES-sib-theta", st, info, b.to_json(), lp_time=lp_time, cert_time=cert_time)
        if r:
            out.append(r)
            lvl_pass = lvl_pass or r["verdict"] == "PASS"
        fails = 0 if lvl_pass else fails + 1
        if fails >= 2:
            logline("M1-shallow: two consecutive levels FAILed at a=%g -- r_kill bracket reached" % a)
            break
    return out


def m1_mid(alist=(0.019, 0.0094), lp_time=300.0, cert_time=240.0):
    cores = [core_box(n, 0.05, 0.03) for n in ("sq4", "sq6", "sq10")]
    out = []
    for a in alist:
        for (at, mark) in ((a, "tmatch"), (0.566 * a, "trad")):
            b = sib_box(a, at, "cx")
            st, info = classify(b, PINS, SLOTS)
            bad = boxes_pairwise_disjoint(cores + [b] + PINS)
            r = run_child("m1m_cx_a%g_%s" % (a, mark), Hyp(PINS + cores + [b], []), 2, 3, a, at,
                          "YES-sib", st, dict(info=info, box_overlaps=bad), b.to_json(),
                          lp_time=lp_time, cert_time=cert_time)
            if r:
                out.append(r)
    return out


def m1_deep(spec, hw=0.05, ht=0.03, lp_time=300.0, cert_time=300.0, tag_prefix="m1d"):
    """spec = [(a, at)]; at None => full-theta NO-family (confinement in centre coords only)."""
    cores = deep_cores(hw, ht)
    bad = boxes_pairwise_disjoint(cores + PINS)
    if bad:
        logline("ABORT: deep-node core boxes not pairwise witness-disjoint " + str(bad)); sys.exit(9)
    st = [classify(b, PINS, SLOTS) for b in cores]
    if any(s[0] != "ok" for s in st):
        logline("ABORT: a deep-node core box is not pinguard-ok " + str(st)); sys.exit(9)
    out = []
    for (a, at) in spec:
        if at is None:
            cx, cy, _ = FREE["sq7"]
            fam = NoFam(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), [(0.0, 90.0)])
            mark = "fulltheta"
        else:
            fam = no_fam_7(a, at)
            mark = "at%g" % at
        hyp = Hyp(PINS + cores, [fam])
        r = run_child("%s_hw%g_a%g_%s" % (tag_prefix, hw, a, mark), hyp, 1, 5, a, at, "NO-conf",
                      "ok", dict(core_pinguard=[s[0] for s in st]), fam.to_json(),
                      lp_time=lp_time, cert_time=cert_time)
        if r:
            out.append(r)
    return out


def m1_deep_vac(spec, hw=0.05, ht=None, depth=60, tag_prefix="m1v"):
    """M1-deep by the exact vacuity arbiter (vac59): no LP, no EPS_CORE/EPS_ZONE shell.
    spec = [(a, at)]; at None => full-theta NO-family."""
    from vac59 import run_vacuity
    ht = 0.6 * hw if ht is None else ht
    cores = deep_cores(hw, ht)
    bad = boxes_pairwise_disjoint(cores + PINS)
    if bad:
        logline("ABORT: deep-node core boxes not pairwise witness-disjoint " + str(bad)); sys.exit(9)
    st = [classify(b, PINS, SLOTS) for b in cores]
    if any(s[0] != "ok" for s in st):
        logline("ABORT: a deep-node core box is not pinguard-ok " + str(st)); sys.exit(9)
    out = []
    for (a, at) in spec:
        if at is None:
            cx, cy, _ = FREE["sq7"]
            fam = NoFam(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), [(0.0, 90.0)])
            mark = "fulltheta"
        else:
            fam = no_fam_7(a, at)
            mark = "at%g" % at
        hyp = Hyp(PINS + cores, [fam])
        # canary: Trump must NOT realise the child (his sq7 is inside the NO-family)
        from substrat import trump_realizes
        tr = trump_realizes(hyp, SLOTS)
        if tr:
            logline("ABORT: Trump realises the deep NO child -- never certify"); sys.exit(9)
        r = run_vacuity("%s_hw%g_a%g_%s" % (tag_prefix, hw, a, mark), hyp, 1,
                        rec_extra=dict(depth_j=5, a=a, at=at, hw=hw, ht=ht, pinguard="ok",
                                       trump_realized=tr, box=fam.to_json()), depth=depth)
        if r:
            out.append(r)
    return out


def bisect_rkill(hw, ht=None, lo=None, hi=None, tol_rel=0.02, depth=60, tag_prefix="rk"):
    """smallest full-theta NO-family half-width a whose vacuity certificate PASSes, at core
    half-width hw.  lo = known FAIL, hi = known PASS."""
    from vac59 import run_vacuity
    ht = 0.6 * hw if ht is None else ht
    cores = deep_cores(hw, ht)
    if boxes_pairwise_disjoint(cores + PINS) or any(classify(b, PINS, SLOTS)[0] != "ok" for b in cores):
        logline("ABORT: deep node audit failed at hw=%g" % hw); sys.exit(9)
    cx, cy, _ = FREE["sq7"]

    def try_a(a):
        fam = NoFam(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), [(0.0, 90.0)])
        hyp = Hyp(PINS + cores, [fam])
        r = run_vacuity("%s_hw%g_a%.6g_fulltheta" % (tag_prefix, hw, a), hyp, 1,
                        rec_extra=dict(depth_j=5, a=a, at=None, hw=hw, ht=ht, kind="NO-conf-vacuity",
                                       pinguard="ok", trump_realized=False, box=fam.to_json()),
                        depth=depth)
        if r is None:      # already recorded -- read the verdict back
            for line in open(P.JSONL):
                d = json.loads(line)
                if d["tag"] == "%s_hw%g_a%.6g_fulltheta" % (tag_prefix, hw, a):
                    return d["verdict"] == "PASS"
        return r["verdict"] == "PASS"

    hi = hi if hi is not None else max(0.02, 6.0 * hw)
    while not try_a(hi):
        hi *= 1.6
        if hi > 1.0:
            logline("bisect: no PASS up to a=1 at hw=%g" % hw); return None, None
    lo = lo if lo is not None else hi / 8.0
    while try_a(lo):
        lo /= 1.6
        if lo < 1e-4:
            break
    while (hi - lo) > tol_rel * hi:
        mid = 0.5 * (lo + hi)
        if try_a(mid):
            hi = mid
        else:
            lo = mid
    logline("r_kill(hw=%g) in (%.6g, %.6g]" % (hw, lo, hi))
    return lo, hi


TSC = 0.566          # d t / d theta at theta_T: t-halfwidth of a theta-radian ball of radius r


def bisect_rkill_box(hw, tol_rel=0.02, depth=60, tag_prefix="rb"):
    """A36-metric version: both the 5 conditioned cores and the NO-family are sup-norm balls in
    (cx, cy, theta_radians), the coordinates of the A36 basin theorem (h = 3.7e-3).  Returns the
    smallest radius a whose confinement certificate PASSes, at conditioning radius hw."""
    from vac59 import run_vacuity
    ht = TSC * hw
    cores = deep_cores(hw, ht)
    if boxes_pairwise_disjoint(cores + PINS) or any(classify(b, PINS, SLOTS)[0] != "ok" for b in cores):
        logline("ABORT: deep node audit failed at hw=%g" % hw); sys.exit(9)

    def try_a(a):
        fam = no_fam_7(a, TSC * a)
        hyp = Hyp(PINS + cores, [fam])
        tag = "%s_hw%g_a%.6g_box" % (tag_prefix, hw, a)
        r = run_vacuity(tag, hyp, 1,
                        rec_extra=dict(depth_j=5, a=a, at=TSC * a, hw=hw, ht=ht,
                                       kind="NO-conf-vacuity-box", pinguard="ok",
                                       trump_realized=False, box=fam.to_json()), depth=depth)
        if r is None:
            for line in open(P.JSONL):
                d = json.loads(line)
                if d["tag"] == tag:
                    return d["verdict"] == "PASS"
        return r["verdict"] == "PASS"

    hi = max(0.02, 8.0 * hw)
    while not try_a(hi):
        hi *= 1.6
        if hi > 1.5:
            logline("bisect_box: no PASS up to a=1.5 at hw=%g" % hw); return None, None
    lo = hi / 8.0
    while try_a(lo):
        lo /= 1.6
        if lo < 1e-4:
            break
    while (hi - lo) > tol_rel * hi:
        mid = 0.5 * (lo + hi)
        if try_a(mid):
            hi = mid
        else:
            lo = mid
    logline("r_kill_box(hw=%g) in (%.6g, %.6g]" % (hw, lo, hi))
    return lo, hi


# ------------------------------------------------------------------ M4: low-s slab diagnostic
def m4(a=0.02, hw=0.02, ht=None, lp_time=300.0):
    """G-A59-8 reconnaissance (NO soundness claim).  Deep node: 5 pins + 5 cores at Trump's
    other free squares (radius hw) + the NO-family B7(a) around his sq7.  Budget 1, so the LP
    value is tau = 1 exactly when an 11th square still fits outside B7 -- and its ATOMS mark
    where that surviving mass has to sit.  A shrunken-Trump adversary at sigma < s_T - h would
    show up as mass away from the B7 shell; mass hugging the shell means the LP sees only the
    core-relaxation slack."""
    ht = TSC * hw if ht is None else ht
    cores = deep_cores(hw, ht)
    fam = no_fam_7(a, TSC * a)
    hyp = Hyp(PINS + cores, [fam])
    tag = "m4_slab_hw%g_a%g" % (hw, a)
    node_path = os.path.join(BASE, "results", "nodes", tag + ".json")
    t0 = time.time()
    if os.path.exists(node_path):
        res = json.load(open(node_path))
    else:
        res = solve_node(S0F, hyp, 1, sym_kind="C1",
                         warm=dict(atoms=P.PILOT_WARM["atoms"], rows=[]),
                         time_limit=lp_time, max_iter=900, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
        res["child_id"] = tag
        json.dump(res, open(node_path, "w"))
    cx7, cy7, _ = FREE["sq7"]
    atoms = [dict(x=p[0], y=p[1], w=p[2], dinf=max(abs(p[0] - cx7), abs(p[1] - cy7)))
             for p in res.get("atoms_all", []) if p[2] > 1e-10]
    atoms.sort(key=lambda r: r["dinf"])
    dump = os.path.join(BASE, "results", tag + "_atoms.json")
    json.dump(dict(tag=tag, tau=res["tau"], converged=res["converged"], minmass=res["minmass"],
                   maxcov=res["maxcov"], n_rows=res.get("n_rows"),
                   lp_s=round(time.time() - t0, 1),
                   total_weight=sum(A["w"] for A in atoms),
                   w_le_0p05=sum(A["w"] for A in atoms if A["dinf"] <= 0.05),
                   w_le_0p20=sum(A["w"] for A in atoms if A["dinf"] <= 0.20),
                   w_gt_0p20=sum(A["w"] for A in atoms if A["dinf"] > 0.20),
                   atoms=atoms), open(dump, "w"), indent=1)
    logline("M4 tau=%s conv=%s atoms=%d -> %s" % (res["tau"], res["converged"], len(atoms), dump))
    return dump


# ------------------------------------------------------------------ depth-2 refinement (A57 T11)
def deepen_box(tag, box, budget, extra_cores=(), nofams=(), lp_time=300.0, cert_time=240.0,
               depth_j=1, a=None, at=None, kind="YES-sib-D2"):
    """bisect a resister box once (same budget: a refinement of the same disjunction)."""
    subs = box.split()
    out = []
    for i, sb in enumerate(subs):
        st, info = classify(sb, PINS, SLOTS)
        r = run_child("%s_D%d" % (tag, i), Hyp(PINS + list(extra_cores) + [sb], list(nofams)),
                      budget, depth_j, a, at, kind, st, info, sb.to_json(),
                      lp_time=lp_time, cert_time=cert_time)
        if r:
            out.append(r)
    return out


# ------------------------------------------------------------------ cli
def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--hw", type=float, default=0.05)
    ap.add_argument("--ht", type=float, default=0.03)
    ap.add_argument("--spec", default=None, help="deep ladder 'a:at,a:at'; at='f' => full theta")
    ap.add_argument("--ladder", default=None)
    ap.add_argument("--tag_prefix", default="m1d")
    ap.add_argument("--a", type=float, default=0.02)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "results", "nodes"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "certs"), exist_ok=True)
    if args.cmd != "m5":
        init_warm()
    if args.cmd == "m5":
        m5()
    elif args.cmd == "m3":
        m3(lp_time=max(args.lp_time, 900.0))
    elif args.cmd == "m1s":
        m1_shallow([float(v) for v in args.ladder.split(",")] if args.ladder else None,
                   lp_time=args.lp_time, cert_time=args.cert_time)
    elif args.cmd == "m1m":
        m1_mid(lp_time=args.lp_time, cert_time=args.cert_time)
    elif args.cmd == "m1d":
        spec = []
        for tok in args.spec.split(","):
            av, atv = tok.split(":")
            spec.append((float(av), None if atv == "f" else float(atv)))
        m1_deep(spec, hw=args.hw, ht=args.ht, lp_time=args.lp_time, cert_time=args.cert_time,
                tag_prefix=args.tag_prefix)
    elif args.cmd == "m1v":
        spec = []
        for tok in args.spec.split(","):
            av, atv = tok.split(":")
            spec.append((float(av), None if atv == "f" else float(atv)))
        m1_deep_vac(spec, hw=args.hw, ht=args.ht if args.ht > 0 else None,
                    tag_prefix=args.tag_prefix)
    elif args.cmd == "rkill":
        res = {}
        for hw in [float(v) for v in args.spec.split(",")]:
            lo, hi = bisect_rkill(hw)
            res["%g" % hw] = dict(hw=hw, ht=0.6 * hw, fail_at=lo, pass_at=hi,
                                  ratio_to_h=(hi / 3.7e-3 if hi else None))
            json.dump(res, open(os.path.join(BASE, "results", "rkill_deep.json"), "w"), indent=1)
        print(json.dumps(res, indent=1))
    elif args.cmd == "rkillbox":
        res = {}
        for hw in [float(v) for v in args.spec.split(",")]:
            lo, hi = bisect_rkill_box(hw)
            res["%g" % hw] = dict(hw=hw, ht=TSC * hw, fail_at=lo, pass_at=hi,
                                  ratio_to_h=(hi / 3.7e-3 if hi else None))
            json.dump(res, open(os.path.join(BASE, "results", "rkill_box.json"), "w"), indent=1)
        print(json.dumps(res, indent=1))
    elif args.cmd == "m4":
        m4(a=args.a, hw=args.hw, ht=args.ht, lp_time=args.lp_time)
    elif args.cmd == "d2":
        a = args.a
        at = 0.566 * a
        deepen_box("m1s_cx_a%g_trad" % a, sib_box(a, at, "cx"), 5, lp_time=args.lp_time,
                   cert_time=args.cert_time, a=a, at=at)
    else:
        raise SystemExit("unknown cmd " + args.cmd)


if __name__ == "__main__":
    cli()
