"""A111 T1, second instrument (coordinator's addendum): decide the YES region with the OCTAGON
(common-inscribed-core) test and Lemma TC instead of the Lipschitz-relaxed LP + capped B&B.

For each (shadow, class, variant) and each (r, rho): the YES region is
    class pins (A57 slack pin boxes)  +  one square in each box F_i,
and it is EMPTY as soon as ONE pair -- box vs box, or box vs pin -- is killed by
`octagon.pair_kill` (every pose of one overlaps every pose of the other, and the two boxes share no
pose so they cannot be the same square).  That is a certified kill of the leaf with no LP at all.

The class pins are present throughout and are the only thing that can carry the kill for S02: the
S02 load path IS Trump's load path (results/trump_loadpath.json), so a test that looks at the boxes
alone can never be sound there.

When no pair is killed the run reports, per pair, HOW FAR the two tests are from firing:
  * core gap  = the SAT gap between the two tight cores (>0 means the cores are already apart, so
    CORE-MEET can never fire at this radius -- there is genuine room),
  * TC slack  = max centre distance - (1 + cos dtheta_min + sin dtheta_min)/2 (>0 likewise),
so the failure is attributed to GENUINE ROOM rather than to a weak bound.

Writes results/t1_octagon.jsonl.  Read-only, seconds, no LP.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1
import octagon as OC
from caselp import Box
from pinguard import kill_core, cores_meet


def pin_boxes_of(pin_names, slack, s_lo, s_hi=None):
    """A57's slack pin boxes.  With s_hi given the box is the UNION over s in [s_lo, s_hi], which
    is the sound object for a claim about the whole window; with s_hi = None it is the fixed-side
    box, which is what A57's per-grid-side certificate actually needs."""
    out = {}
    for p in pin_names:
        ax, ay = T1.slot_affine(p)
        xs = [ax[0] + ax[1] * s_lo] + ([ax[0] + ax[1] * s_hi] if s_hi is not None else [])
        ys = [ay[0] + ay[1] * s_lo] + ([ay[0] + ay[1] * s_hi] if s_hi is not None else [])
        out[p] = Box(min(xs) - slack, max(xs) + slack, min(ys) - slack, max(ys) + slack, 0.0, 0.0)
    return out


def core_gap(a, b):
    """SAT gap between the two tight cores (negative = they overlap = CORE-MEET fires)."""
    ca, cb = kill_core(OC.as_box(a)), kill_core(OC.as_box(b))
    if ca is None or cb is None:
        return None
    g = -1e9
    for (u, v) in ((ca, cb), (cb, ca)):
        co, si = float(u.cm), float(u.sm)
        for ax in ((co, si), (-si, co)):
            qa = [(float(u.kx) + su * float(u.a) * co - sv * float(u.a) * si,
                   float(u.ky) + su * float(u.a) * si + sv * float(u.a) * co)
                  for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
            qb = [(float(v.kx) + su * float(v.a) * float(v.cm) - sv * float(v.a) * float(v.sm),
                   float(v.ky) + su * float(v.a) * float(v.sm) + sv * float(v.a) * float(v.cm))
                  for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
            p1 = [ax[0] * x + ax[1] * y for (x, y) in qa]
            p2 = [ax[0] * x + ax[1] * y for (x, y) in qb]
            g = max(g, max(min(p2) - max(p1), min(p1) - max(p2)))
    return g


def one(tag, cls, variant, r, rho, slack, log):
    t0 = time.time()
    pin_names = T1.CLASS_PINS[cls]
    ext = T1.anchors(tag, pin_names) if variant == "lpa" else ()
    s_sh, names, cfg, slots, free, box_names, B = T1.make_boxes(tag, r, rho, extra=ext)
    # the pins are placed at the WINDOW's worst side for the pair in question: a right/top-anchored
    # pin is nearest the interior at the smallest side, so s = 3.82 is the conservative choice for
    # "can they be forced to overlap"?  Both ends are tested and the kill must hold at BOTH.
    res_sides = {}
    for nm, args in (("s0", (T1.S0, None)), ("win", (T1.S_WIN_LO, T1.S0)),
                     ("s_lo", (T1.S_WIN_LO, None))):
        pins = pin_boxes_of(pin_names, slack, *args)
        killed, hits = OC.region_kill(B, pins)
        res_sides[nm] = dict(killed=killed, hits=hits)
    killed_all = res_sides["win"]["killed"]          # sound over the whole window
    # diagnostics at the node's own side s0
    pins0 = pin_boxes_of(pin_names, slack, T1.S0)
    diag = []
    items = list(B.items()) + [("pin:" + k, v) for k, v in pins0.items()]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            na, a = items[i]
            nb, b = items[j]
            if na.startswith("pin:") and nb.startswith("pin:"):
                continue
            cg = core_gap(a, b)
            dmin = OC.tilt_dev_min(a, b)
            tcs = OC.centre_dist_max(a, b) - (1.0 + OC._w(dmin)) / 2.0
            diag.append(dict(pair=[na, nb], core_gap=(None if cg is None else round(cg, 6)),
                             dtheta_min_deg=round(dmin, 4), tc_slack=round(tcs, 6)))
    best_core = min((d["core_gap"] for d in diag if d["core_gap"] is not None), default=None)
    best_tc = min((d["tc_slack"] for d in diag), default=None)
    rec = dict(tag=tag, cls=cls, variant=variant, r=r, rho=rho, pin_slack=slack,
               boxes=box_names, anchors=list(ext), killed=killed_all, by_side=res_sides,
               killed_s0=res_sides["s0"]["killed"], killed_slo=res_sides["s_lo"]["killed"],
               n_hits_s0=len(res_sides["s0"]["hits"]),
               closest_core_gap=best_core, closest_tc_slack=best_tc, diag=diag,
               seconds=round(time.time() - t0, 2))
    log("  %-3s/%-6s/%-3s r=%.4f rho=%5.2f  OCTAGON kill window=%-5s s0=%-5s s_lo=%-5s  hits@s0=%d"
        "  min core gap=%s  min TC slack=%s  (%.2fs)"
        % (tag, cls, variant, r, rho, killed_all, rec["killed_s0"], rec["killed_slo"],
           rec["n_hits_s0"],
           ("%.5f" % best_core) if best_core is not None else "-",
           ("%.5f" % best_tc) if best_tc is not None else "-", rec["seconds"]))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="S02:k5_11:lp,S02:k5_11:lpa,S02:k5_16:lpa,"
                                      "S07:trump5:lp,S07:trump5:lpa")
    ap.add_argument("--r", default="0.02,0.05,0.1")
    ap.add_argument("--rho", default="5,10,20")
    ap.add_argument("--extra_r", default="0.0087,0.0175,0.035,0.0699",
                    help="A57's own box half-widths, paired with --extra_rho")
    ap.add_argument("--extra_rho", default="0.61,1.22,2.43,4.87")
    ap.add_argument("--pin_slack", type=float, default=T1.PIN_SLACK)
    ap.add_argument("--out", default=None)
    A = ap.parse_args()
    logp = os.path.join(L.LOGS, "t1_octagon.log")

    def log(*x):
        m = " ".join(str(v) for v in x)
        print(m, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + m + "\n")

    out = A.out or os.path.join(L.RES, "t1_octagon.jsonl")
    grid = [(float(r), float(p)) for r in A.r.split(",") for p in A.rho.split(",")]
    grid += list(zip([float(v) for v in A.extra_r.split(",")],
                     [float(v) for v in A.extra_rho.split(",")]))
    for job in A.jobs.split(","):
        tag, cls, variant = job.split(":")
        log("=== %s / %s / %s  pins %s (slack %.5f)" % (tag, cls, variant,
                                                        T1.CLASS_PINS[cls], A.pin_slack))
        for (r, rho) in grid:
            rec = one(tag, cls, variant, r, rho, A.pin_slack, log)
            with open(out, "a") as f:
                f.write(json.dumps(rec) + "\n")
    log("T1 octagon done")


if __name__ == "__main__":
    main()
