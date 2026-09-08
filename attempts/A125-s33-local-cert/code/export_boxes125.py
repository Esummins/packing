"""A125 -- export every certified neighbourhood N of S33 / S38 in A119's `N_boxes.json` format
(attempts/A119-local-cert-lean/results/N_boxes.json), i.e. the form A96's caselp / NO-family
machinery quantifies over: ONE axis-aligned box (cx, cy, theta-interval) per square of L in the
CLASS FRAME at side s0, plus the pin cores and (if any) the cut inequality on the tilt.

The hypothesis exported is, verbatim, the one Theorem LOCAL kills:

    s in [s_lo, s_hi];
    for each pin p of the class: some square has tilt 0 and centre in
        (alpha_p + beta_p * s) + [-h, h]^2 ,  h = delta/sqrt2, delta = 1e-2;
    for each l in L: some OTHER square has centre in [cx_lo, cx_hi] x [cy_lo, cy_hi]
        and tilt (mod 90 deg) in [theta_lo, theta_hi];
    all these |P| + |L| squares distinct.

Read-only on A116/A119/A122 and every campaign; writes results/N_boxes.json and
logs/export_boxes.log only.
"""
from __future__ import annotations
import glob, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a125lib as G
import a116lib as A

A107R = os.path.join(A.ROOT, "attempts", "A107-shadow-gallery", "results")


def node_class(rec):
    if rec["src"] == "A57":
        return rec["nid"].split("_interior")[0]
    if rec["src"] == "A60":
        return "trump5"
    return rec["nid"].split(".")[0] if "." in rec["nid"] else rec["nid"].split("_")[0]


def frame_ops_seen():
    """the A107 struct_op of every alive node, by source: A96 must apply the SAME op before
    testing the boxes.  (S33's class k6_07 has no node of its own in the gallery index; the
    consumers are trump5 (A60) and A57 nodes, so the ops are reported over all sources.)"""
    out = {}
    for snf, exf in (("shadow_nodes.json", "extract.json"),
                     ("shadow_nodes_k0.json", "extract_k0.json")):
        sn = json.load(open(os.path.join(A107R, snf), encoding="utf-8"))
        ex = json.load(open(os.path.join(A107R, exf), encoding="utf-8"))["nodes"]
        idx = {(n["src"], n["nid"]): n for n in ex}
        for tag in sn:
            for rec in sn[tag]:
                n = idx.get((rec["src"], rec["nid"]))
                if n is None:
                    continue
                out.setdefault(n.get("struct_op") or "e", []).append(rec["nid"])
    return {k: dict(count=len(v), example=v[0]) for k, v in sorted(out.items())}


def rows_for(tag):
    """every grid row for this shadow (the run is sharded across processes: grid_<tag>*.jsonl),
    de-duplicated on (r, rho, cut) keeping the DEAD row if there is one."""
    best = {}
    for p in sorted(glob.glob(os.path.join(G.RES, "grid_%s*.jsonl" % tag))):
        if "_smoke" in p:
            continue
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            k = (d["r"], d["rho"], d["cut"])
            if k not in best or (d["tree"]["dead"] and not best[k]["tree"]["dead"]):
                best[k] = d
    return [best[k] for k in sorted(best, reverse=True)]


def main():
    logp = os.path.join(G.LOGS, "export_boxes.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    certs = {}
    mp = os.path.join(G.CERTS, "manifest.json")
    if os.path.exists(mp):
        certs = json.load(open(mp, encoding="utf-8"))
    sp = os.path.join(G.RES, "sampling.json")
    samp_extra = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    chk = {}
    cp = os.path.join(G.RES, "check_local.json")
    if os.path.exists(cp):
        for run in json.load(open(cp, encoding="utf-8")).get("runs", []):
            chk[run["id"]] = run
    ops = frame_ops_seen()
    out = dict(
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        source="attempts/A125-s33-local-cert/results/grid_*.jsonl "
               "(minima: attempts/A122-s33-certify/results/exact.json; "
               "machinery: A116 a116lib + A119 a119lib/check_local.py, read-only)",
        s0=G.S0, shat=G.SHAT, s_lo=G.S_LO, s_hi=G.S_HI, pin_slack=G.PIN_SLACK,
        note="A119 attempts/A119-local-cert-lean/notes/n_boxes.md (DROP/COVER: 'a square in each "
             "box' + pins => inside N).  A125 adds the class frames k6_07 (S33, identity) and "
             "k6_21 (S38, D4 element `diag`).",
        d4_ops={"e": "(x, y, t)", "r90": "(s - y, x, t)", "r180": "(s - x, s - y, t)",
                "r270": "(y, s - x, t)", "mx": "(s - x, y, -t)", "my": "(x, s - y, -t)",
                "diag": "(y, x, -t)", "anti": "(s - y, s - x, -t)"},
        d4_ops_note="apply at s = s0 = %r; A107's struct_op per node, then test the boxes" % G.S0,
        N=[])
    n_dead = 0
    for tag in ("S33", "S38"):
        for rec in rows_for(tag):
            if not rec["tree"]["dead"]:
                continue
            n_dead += 1
            r, rho, cut = rec["r"], rec["rho"], rec["cut"]
            cid = "%s_%s_r%.2f_rho%g" % (tag, rec["cls"], r, rho)
            bodies, nv, s_sh, P = G.build_bodies125(tag, r, rho, anchor_side=G.S0,
                                                    pin_slack=G.PIN_SLACK, tilt_floor_deg=cut)
            boxes, pins = [], []
            for b in bodies:
                if b.kind == "free":
                    boxes.append(dict(name=b.name, cx=[b.x0, b.x1], cy=[b.y0, b.y1],
                                      theta_deg=[math.degrees(b.t0), math.degrees(b.t1)],
                                      anchor=[b.anchor[0], b.anchor[1], math.degrees(b.anchor[2])],
                                      tilted=bool(abs(b.anchor[2]) > 1e-9),
                                      half_extent=[0.5 * (b.x1 - b.x0), 0.5 * (b.y1 - b.y0),
                                                   math.degrees(0.5 * (b.t1 - b.t0))]))
                else:
                    pins.append(dict(name=b.name, alpha=[b.ax[0], b.ay[0]],
                                     beta=[b.ax[1], b.ay[1]], halfwidth=b.hh, theta_deg=0.0,
                                     centre_at_s0=[b.ax[0] + b.ax[1] * G.S0,
                                                   b.ay[0] + b.ay[1] * G.S0]))
            tilted = [b["name"] for b in boxes if b["tilted"]]
            cutd = None
            if cut is not None:
                cutd = dict(kind="tilt_floor_deg", value=cut, applies_to=tilted,
                            inequality="theta_l (mod 90 deg) >= %.6f for every l in %s" % (cut, tilted))
            entry = dict(
                id=cid, tag=tag, cls=rec["cls"], frame=rec["frame"], r=r, rho_deg=rho,
                anchor_side=G.S0, window=[G.S_LO, G.S_HI], s_star=rec["s_star"],
                L=[b["name"] for b in boxes], P=[p["name"] for p in pins],
                boxes=boxes, pins=pins, cut=cutd,
                hypothesis=("s in [%r, %r]; for each pin p: a square with tilt 0 and centre in "
                            "(alpha_p + beta_p s) + [-%r, %r]^2; for each l in L: a DISTINCT other "
                            "square with centre in the box and tilt (mod 90 deg) in the interval%s; "
                            "conclusion: no such configuration is a packing at side <= s0."
                            % (G.S_LO, G.S_HI, G.PIN_SLACK, G.PIN_SLACK,
                               "" if cutd is None else " and " + cutd["inequality"])),
                tree_verdict=dict(dead=rec["tree"]["dead"],
                                  certified_min=rec["tree"]["certified_min"],
                                  measured_min=(rec.get("local_min") or {}).get("side"),
                                  nodes=rec["tree"]["stats"]["nodes"],
                                  n_near=rec["tree"]["n_near"],
                                  leaves_after_interval=rec["tree"]["leaves_after_interval"],
                                  seconds=rec["seconds_tree"]),
                trump_canary=dict(inside=rec["trump"]["inside"], ops=rec["trump"]["ops"],
                                  cut_applied=cut,
                                  note="A122 a116_input.json: at S33min the keystone f0 is upright "
                                       "while Trump's nearest square is at 40.182 deg, so f0's box "
                                       "excludes Trump on position alone out to r = 0.2054"),
                sample_check=dict(**{k: (samp_extra.get(cid) or rec.get("sampling") or {}).get(k)
                                     for k in ("drawn", "tested", "hits",
                                               "worst_free_overlap_of_rejects")},
                                  sides_tested=30, side_range=[G.S_LO, G.S0],
                                  source=("results/sampling.json" if cid in samp_extra
                                          else "results/grid_*.jsonl")),
                exact_certificate=certs.get(cid),
                independent_check=chk.get(cid),
                frame_ops=ops)
            out["N"].append(entry)
            log("%-26s L=%s  r=%.2f rho=%.1f cut=%s  sampled %s->%s hits=%s  cert=%s  farkas=%s"
                % (cid, entry["L"], r, rho, cut,
                   entry["sample_check"]["drawn"], entry["sample_check"]["tested"],
                   entry["sample_check"]["hits"], rec["tree"]["certified_min"],
                   "yes" if cid in certs else "-"))
    with open(os.path.join(G.RES, "N_boxes.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    log("wrote results/N_boxes.json (%d neighbourhoods of %d dead rows)" % (len(out["N"]), n_dead))


if __name__ == "__main__":
    main()
