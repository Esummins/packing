"""A160 T4 -- the pinwheel's COMMON-TILT CHAIN: cover A106's tilt curve with a chain of boxes.

`f1, f2, f3` are one grain: they share a tilt, and A106 measured the pinwheel's side as a function of
that shared tilt (`docs/residue_map/gen_pinwheel_tilt.py`, `docs/shadows.md` §S02 -- minimum
3.886746 at 48.435 deg, rising on both sides).  A single box with a wide tilt window is the wrong
cover for that curve, because the three CENTRES move with the tilt; the right cover is a CHAIN:

  link k = the selection-tree certificate over the boxes centred on the configuration s*(theta_k)
           -- the three free centres at their s*(theta_k) positions dilated by s0/s*(theta_k), the
           three tilt intervals [theta_k - h, theta_k + h] moved TOGETHER, BR(0,1) at its slot cell,
           f0's slide box inside, and the five A57 slack-core pins.

s*(theta_k) is recomputed here (SLSQP + a Newton polish of the active contact set, `polish160`'s
routine with the common tilt PINNED), so the chain's spine is this attempt's own data, not a read of
A106's picture.  Links are walked OUTWARD from theta* alternately up and down, so the reported tilt
range and the first failure are known on both sides.

    python chain160.py <job>  [--dtheta 2.5] [--half 1.25] [--budget 6600] [--time-cap 600]
      job UP / DOWN / BOTH

A link is CERTIFIED only if the tree returns dead with capped = False and 0 sampling hits.  A link
that caps is CAPPED (a wall-clock limit, no geometric claim); a link with LIVE-LOW witnesses is a
geometric limit and its witnesses are kept.

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                                   # noqa: E402
import a116lib as A                                  # noqa: E402
import numpy as np                                   # noqa: E402
from scipy.optimize import minimize, least_squares   # noqa: E402
from grow160 import F0_COVER                         # noqa: E402

RES, LOGS = L.RES, L.LOGS
FREE3 = ("f1", "f2", "f3")
SLOTS7 = ("BL(0,0)", "BL(0,1)", "BL(1,0)", "BR(0,0)", "BR(0,1)", "TL(0,0)", "TR(0,0)")


# ------------------------------------------------------------------ s*(theta): the spine
def poses_at(z, th, free, slots):
    s = z[0]
    P = {n: (z[1 + 2 * i], z[2 + 2 * i], th) for i, n in enumerate(free)}
    for n in slots:
        x, y = A.slot_xy(n, s)
        P[n] = (x, y, 0.0)
    return s, P


def cons(z, th, free, slots):
    s, P = poses_at(z, th, free, slots)
    names = list(free) + list(slots)
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = P[names[i]], P[names[j]]
            out.append(A.sat_gap(a[:2], a[2], b[:2], b[2]))
    h = 0.5 * A.wfun(th)
    for n in free:
        x, y, _ = P[n]
        out += [x - h, s - h - x, y - h, s - h - y]
    return np.array(out)


def spine(th_deg, free, slots, z0):
    """min side with the common tilt PINNED at th_deg: (s, poses, worst gap)."""
    th = math.radians(th_deg)
    best = None
    for k in range(5):
        z = np.array(z0, dtype=float)
        if k:
            rs = np.random.RandomState(100 + k)
            z[1:] += rs.uniform(-0.03, 0.03, len(z) - 1)
        r = minimize(lambda v: v[0], z, method="SLSQP",
                     constraints=[{"type": "ineq", "fun": lambda v: cons(v, th, free, slots)}],
                     bounds=[(3.5, 4.4)] + [(0.0, 4.4)] * (len(z) - 1),
                     options=dict(maxiter=600, ftol=1e-16))
        g = cons(r.x, th, free, slots)
        if g.min() >= -1e-9 and (best is None or r.x[0] < best[0]):
            best = (float(r.x[0]), r.x.copy())
    if best is None:
        return None
    z1 = best[1]
    act = np.where(cons(z1, th, free, slots) <= 1e-5)[0]
    if len(act):
        meth = "lm" if len(act) >= len(z1) else "trf"
        r = least_squares(lambda v: cons(v, th, free, slots)[act], z1,
                          xtol=1e-15, ftol=1e-15, gtol=1e-15, method=meth, max_nfev=20000)
        if cons(r.x, th, free, slots).min() >= -1e-9:
            z1 = r.x
    s, P = poses_at(z1, th, free, slots)
    return dict(tilt_deg=th_deg, s=float(s), worst_gap=float(cons(z1, th, free, slots).min()),
                poses={n: [float(P[n][0]), float(P[n][1]), math.degrees(P[n][2])] for n in P},
                z=list(map(float, z1)))


# ------------------------------------------------------------------ a link of the chain
def link_spec(half_deg, r_xy=L.R0, use_f0=True, widths="base"):
    """`widths = base` gives every free box the same centre half-width r_xy; `a151B` gives f1 the
    x/y half-widths of A151's largest certified N (x 0.40, y 0.25) and the rest r_xy."""
    sp = {n: dict(dx=0.0, dy=0.0, dt=0.0, x=r_xy, y=r_xy, t=half_deg) for n in FREE3}
    sp["BR(0,1)"] = dict(dx=0.0, dy=0.0, dt=0.0, x=r_xy, y=r_xy, t=L.RHO0)
    if widths == "a151B":
        b = L.a151_spec_B()
        for n in list(FREE3) + ["BR(0,1)"]:
            sp[n]["x"], sp[n]["y"] = b[n]["x"], b[n]["y"]
    if use_f0:
        sp["f0"] = dict(F0_COVER)
    return sp


def link_override(sp_row, use_f0):
    """The link's anchor poses in the s0 frame: the s*(theta_k) configuration DILATED by
    s0/s*(theta_k) for the tilted free squares (A116's anchoring rule), slots left where
    build_bodies puts them (their slot cells at s0)."""
    lam = A.S0 / sp_row["s"]
    th = math.radians(sp_row["tilt_deg"])
    ov = {n: (sp_row["poses"][n][0] * lam, sp_row["poses"][n][1] * lam, th) for n in FREE3}
    if use_f0:
        p = sp_row["poses"]["f0"] if "f0" in sp_row["poses"] else None
        if p is not None:
            ov["f0"] = (p[0] * lam, p[1] * lam, th)
    return ov


def hint_poses(sp_row, use_f0):
    """Poses (in the shadow's own frame at s*(theta_k)) used only to pick the pairs the tree
    branches on first -- A116's `shadow_selections` hint, recomputed for this link."""
    P = {n: (v[0], v[1], math.radians(v[2]) if n in FREE3 or n == "f0" else 0.0)
         for n, v in sp_row["poses"].items()}
    return P


def run_link(sp_row, half_deg, time_cap, samples, use_f0, r_xy, widths="base"):
    spec = link_spec(half_deg, r_xy=r_xy, use_f0=use_f0, widths=widths)
    ov = link_override(sp_row, use_f0)
    t0 = time.time()
    bodies, nv, s_sh, P = L.bodies_for(spec, anchor_override=ov)
    hp = hint_poses(sp_row, use_f0)
    ss = A.shadow_selections(bodies, {b.name: hp.get(b.name, (0, 0, 0.0)) for b in bodies})
    T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=2000000,
               time_cap=time_cap, target=A.S0 + 0.9 * max(1e-6, sp_row["s"] - A.S0), tighten_cap=0)
    v = T.run()
    rec = dict(tilt_deg=sp_row["tilt_deg"], s_star=sp_row["s"], half_deg=half_deg, r_xy=r_xy,
               use_f0=use_f0, widths=widths, tree=v, n_witnesses=len(T.witnesses), n_unresolved=len(T.unresolved),
               witnesses=T.witnesses[:3], unresolved=T.unresolved[:2],
               tilt_window=[sp_row["tilt_deg"] - half_deg, sp_row["tilt_deg"] + half_deg])
    dead = bool(v["dead"]) and not v["capped"]
    if dead and samples:
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=samples, seed=int(10 * half_deg) + 3)
        rec["trump"] = A.trump_in_N(bodies, pin_slack=A.PIN_SLACK)
    rec["dead"] = dead and (rec.get("sampling", {}).get("hits", 0) == 0)
    rec["reason"] = ("certified" if rec["dead"] else
                     ("wall cap" if v["capped"] else
                      ("witness" if len(T.witnesses) else "unresolved/sampling")))
    rec["seconds"] = round(time.time() - t0, 1)
    rec["boxes"] = L.boxlist(spec, anchor_override=ov)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job", choices=("UP", "DOWN", "BOTH", "SPINE"))
    ap.add_argument("--dtheta", type=float, default=2.5)
    ap.add_argument("--half", type=float, default=1.25)
    ap.add_argument("--r-xy", type=float, default=L.R0)
    ap.add_argument("--no-f0", action="store_true")
    ap.add_argument("--widths", default="base", choices=("base", "a151B"))
    ap.add_argument("--label", default=None)
    ap.add_argument("--budget", type=float, default=6600.0)
    ap.add_argument("--time-cap", type=float, default=600.0)
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--max-links", type=int, default=40)
    ap.add_argument("--skip-done", action="store_true",
                    help="skip offsets already CERTIFIED in any results/chain_*.jsonl with the same "
                         "half/r_xy/widths/f0 settings (resumable: kill, add, resume)")
    ap.add_argument("--no-stop-on-fail", action="store_true",
                    help="keep walking outward past a refusal (the refusal is still recorded)")
    a = ap.parse_args()
    use_f0 = not a.no_f0

    lab = a.label or ("%s_%s_r%.2f_h%.2f_%s" % (a.job, a.widths, a.r_xy, a.half,
                                                "f0" if use_f0 else "nof0"))
    logp = os.path.join(LOGS, "chain_%s.log" % lab)
    out = os.path.join(RES, "chain_%s.jsonl" % lab)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    pol = json.load(open(os.path.join(RES, "polish160.json"), encoding="utf-8"))["eleven"]
    free = ["f0"] + list(FREE3) if use_f0 else list(FREE3)
    th0 = pol["tilt_deg"]
    z0 = [pol["s"]] + [v for n in free for v in pol["poses"][n][:2]]

    # ---- the spine: s*(theta) on the schedule, warm-started from the neighbour
    steps = [0.0]
    for i in range(1, a.max_links):
        steps += [i * a.dtheta, -i * a.dtheta]
    # keep every tilt window inside the fundamental domain [0 deg, 90 deg]
    steps = [d for d in steps if 1.0 <= th0 + d <= 89.0]
    if a.job == "UP":
        steps = [v for v in steps if v >= 0]
    elif a.job == "DOWN":
        steps = [v for v in steps if v <= 0]
    cachep = os.path.join(RES, "spine_%s_d%.3f_%s.json" % (a.job, a.dtheta,
                                                           "f0" if use_f0 else "nof0"))
    if os.path.exists(cachep):
        cached = json.load(open(cachep, encoding="utf-8"))["spine"]
        spines = {float(k): v for k, v in cached.items()}
        log("spine loaded from cache: %d tilts" % len(spines))
        if a.job == "SPINE":
            return
        steps = [d for d in steps if round(d, 6) in spines]
    else:
        spines = {}
    zcur = dict(up=list(z0), dn=list(z0))
    for d in ([] if spines else steps):
        key = "up" if d >= 0 else "dn"
        r = spine(th0 + d, free, SLOTS7, zcur[key])
        if r is None:
            log("SPINE FAILED at %+.2f deg" % d)
            continue
        spines[round(d, 6)] = r
        zcur[key] = r["z"]
        log("spine %+7.2f deg -> theta %8.4f  s* = %.9f  worst gap %.2e"
            % (d, r["tilt_deg"], r["s"], r["worst_gap"]))
    json.dump(dict(job=a.job, th0=th0, dtheta=a.dtheta, free=free,
                   spine={str(k): dict(tilt_deg=v["tilt_deg"], s=v["s"],
                                       worst_gap=v["worst_gap"], poses=v["poses"], z=v.get("z"))
                          for k, v in spines.items()}),
              open(cachep, "w", encoding="utf-8"), indent=1)
    if a.job == "SPINE":
        return

    # ---- the links, outward from theta*
    t_start = time.time()
    fail = {}
    certified = []
    done = set()
    if a.skip_done:
        import glob as _g
        for q in _g.glob(os.path.join(RES, "chain_*.jsonl")):
            for line in open(q, encoding="utf-8"):
                r0 = json.loads(line)
                if (r0.get("dead") and abs(r0.get("half_deg", -1) - a.half) < 1e-9
                        and abs(r0.get("r_xy", -1) - a.r_xy) < 1e-9
                        and r0.get("widths", "base") == a.widths
                        and bool(r0.get("use_f0")) == use_f0):
                    done.add(round(r0.get("offset_deg", 0.0), 6))
                    certified.append(round(r0.get("offset_deg", 0.0), 6))
        certified = sorted(set(certified))
        log("skip-done: %d offsets already certified" % len(done))
    for d in steps:
        if round(d, 6) in done:
            continue
        if round(d, 6) not in spines:
            continue
        side = "up" if d > 0 else ("down" if d < 0 else "centre")
        if side in fail and not a.no_stop_on_fail:
            continue
        if time.time() - t_start > a.budget:
            log("BUDGET reached at %+.2f" % d)
            fail.setdefault("budget", d)
            break
        rec = run_link(spines[round(d, 6)], a.half, a.time_cap, a.samples, use_f0, a.r_xy,
                       widths=a.widths)
        rec.update(job=a.job, label=lab, offset_deg=d, side=side, when=time.strftime("%Y-%m-%d %H:%M:%S"))
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        st = rec["tree"]
        log("link %+7.2f (th %8.4f, s* %.6f) %-9s %-12s certmin=%s leaves=%s wit=%d unres=%d hits=%s (%.0fs)"
            % (d, rec["tilt_deg"], rec["s_star"], "CERTIFIED" if rec["dead"] else "REFUSED",
               rec["reason"], ("%.7f" % st["certified_min"]) if st.get("certified_min") else "-",
               st.get("n_leaves") or st.get("leaves"), rec["n_witnesses"], rec["n_unresolved"],
               rec.get("sampling", {}).get("hits"), rec["seconds"]))
        if rec["dead"]:
            certified.append(d)
        else:
            fail[side] = dict(offset_deg=d, tilt_deg=rec["tilt_deg"], reason=rec["reason"],
                              witnesses=rec["n_witnesses"], unresolved=rec["n_unresolved"])
    lo = min(certified) - a.half if certified else None
    hi = max(certified) + a.half if certified else None
    summ = dict(job=a.job, label=lab, widths=a.widths, dtheta=a.dtheta, half_deg=a.half,
                r_xy=a.r_xy, use_f0=use_f0,
                th0=th0, n_certified=len(certified), certified_offsets=sorted(certified),
                covered_tilt_deg=[None if lo is None else th0 + lo, None if hi is None else th0 + hi],
                covered_width_deg=None if lo is None else (hi - lo), first_failures=fail,
                seconds=round(time.time() - t_start, 1))
    json.dump(summ, open(os.path.join(RES, "chain_%s_summary.json" % lab), "w",
                         encoding="utf-8"), indent=1)
    log("CHAIN %s: %d links certified, tilt covered %s (%s deg wide); failures %s"
        % (lab, len(certified), summ["covered_tilt_deg"], summ["covered_width_deg"],
           json.dumps(fail)))


if __name__ == "__main__":
    main()
