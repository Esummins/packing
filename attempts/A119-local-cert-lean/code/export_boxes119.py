"""A119 T1(a) -- export every certified neighbourhood N of A116 in the form A96's caselp /
NO-family machinery quantifies over: ONE axis-aligned box (cx, cy, theta-interval) per
load-path square of L, in the CLASS FRAME at side s0, plus the pin cores and the cut
inequality on the tilt.

Why this file exists.  a116lib states two different objects and A96 can only consume one of
them:

  * the STABILITY radii of Lemma STAB (`a116lib.pair_box` / `forced_test`) are 6-dimensional
    PAIR-pose boxes carrying a forced selection -- that is the PI's single-leaf route, not a
    hypothesis A96 can quantify over;
  * the certificate's own hypothesis N (`a116lib.build_bodies`) is already a product of
    per-square axis-aligned boxes: one (centre box) x (tilt interval) per free body, one slack
    core per pin.  THIS is what A96 needs, and this script exports it explicitly.

The hypothesis exported here is, verbatim, the one Theorem LOCAL kills:

    s in [s_lo, s_hi];
    for each pin p of the class: some square has tilt 0 and centre in
        (alpha_p + beta_p * s) + [-h, h]^2 ,  h = delta/sqrt2, delta = 1e-2;
    for each l in L: some OTHER square has centre in [cx_lo, cx_hi] x [cy_lo, cy_hi]
        and tilt (mod 90 deg) in [theta_lo, theta_hi];
    all these |P| + |L| squares distinct.

DROP/COVER (why "a square in each box" + pins => inside N): notes/n_boxes.md.

Read-only on A116; writes results/N_boxes.json and logs/export_boxes.log only.
"""
from __future__ import annotations
import glob, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
A116 = os.path.abspath(os.path.join(HERE, "..", "..", "A116-local-selection-tree", "code"))
sys.path.insert(0, A116)
import a116lib as A  # noqa: E402  (imports blas1 before numpy)

BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
for d in (RES, LOGS):
    os.makedirs(d, exist_ok=True)

# the certified neighbourhoods the coordinator asked for (A116 t2 tables, DEAD + 0 sample hits
# + Trump outside), plus S02 (0.1, 10) which T1's certificate list also covers.
TARGETS = [
    dict(id="S02_k5_11_r0.20_rho10", tag="S02", cls="k5_11", r=0.2, rho=10.0, cut=None, label="grid"),
    dict(id="S02_k5_11_r0.05_rho20", tag="S02", cls="k5_11", r=0.05, rho=20.0, cut=None, label="grid"),
    dict(id="S02_k5_11_r0.10_rho10", tag="S02", cls="k5_11", r=0.1, rho=10.0, cut=None, label="grid"),
    dict(id="S07_trump5_r0.10_rho40", tag="S07", cls="trump5", r=0.1, rho=40.0, cut=41.565, label="cut41.565"),
    dict(id="S07_trump5_r0.20_rho10", tag="S07", cls="trump5", r=0.2, rho=10.0, cut=41.565, label="cut41.565"),
    # A119 T3: the one blocking-box N that closes (six boxes; L gains f0 and TR(0,0))
    dict(id="S02_k5_11_r0.10_rho5_block", tag="S02", cls="k5_11", r=0.1, rho=5.0, cut=None,
         label="block_ladder", loadbearing=("f1", "f2", "f3", "f0", "TR(0,0)")),
]

A107R = os.path.join(A.ROOT, "attempts", "A107-shadow-gallery", "results")


def a116_row(t):
    """the tree record for this N -- A116's t2 row (read-only) or, for the blocking-box N, A119's
    own t3 row -- so the export can carry its verdict."""
    for p in sorted(glob.glob(os.path.join(A.ROOT, "attempts", "A116-local-selection-tree",
                                           "results", "t2_*.jsonl"))) +             sorted(glob.glob(os.path.join(A.ROOT, "attempts", "A119-local-cert-lean",
                                          "results", "t3_*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            if (d["tag"], d["cls"], d["r"], d["rho"], d["cut"], d["label"]) == \
               (t["tag"], t["cls"], t["r"], t["rho"], t["cut"], t["label"]):
                return d
    return None


def node_class(rec):
    if rec["src"] == "A57":
        return rec["nid"].split("_interior")[0]
    if rec["src"] == "A60":
        return "trump5"
    return rec["nid"].split(".")[0] if "." in rec["nid"] else rec["nid"].split("_")[0]


def frame_ops_for(cls):
    """the A107 struct_op of every alive node of this class (the D4 element that carries the
    node's support into the class frame); A96 must apply the SAME op before testing the boxes."""
    sn = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]
    idx = {(n["src"], n["nid"]): n for n in ex}
    out = {}
    for tag in sn:
        for rec in sn[tag]:
            if node_class(rec) != cls:
                continue
            n = idx[(rec["src"], rec["nid"])]
            out.setdefault(n.get("struct_op") or "e", []).append(rec["nid"])
    return {k: dict(count=len(v), example=v[0]) for k, v in sorted(out.items())}


def main():
    logp = os.path.join(LOGS, "export_boxes.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    out = dict(
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        source="attempts/A116-local-selection-tree/results/t2_*.jsonl (read-only) + attempts/A119-local-cert-lean/results/t3_*.jsonl",
        s0=A.S0, shat=A.SHAT, s_lo=A.S_LO, s_hi=A.S_HI_DEFAULT, pin_slack=A.PIN_SLACK,
        note="attempts/A119-local-cert-lean/notes/n_boxes.md (DROP/COVER: 'a square in each box' + pins => inside N)",
        d4_ops={k: v for k, v in {
            "e": "(x, y, t)", "r90": "(s - y, x, t)", "r180": "(s - x, s - y, t)",
            "r270": "(y, s - x, t)", "mx": "(s - x, y, -t)", "my": "(x, s - y, -t)",
            "diag": "(y, x, -t)", "anti": "(s - y, s - x, -t)"}.items()},
        d4_ops_note="apply at s = s0 = %r; A107's struct_op per node, then test the boxes" % A.S0,
        N=[])
    for t in TARGETS:
        bodies, nv, s_sh, P = A.build_bodies(t["tag"], t["cls"], t["r"], t["rho"],
                                             anchor_side=A.S0, pin_slack=A.PIN_SLACK,
                                             tilt_floor_deg=t["cut"],
                                             loadbearing=t.get("loadbearing"))
        boxes, pins = [], []
        for b in bodies:
            if b.kind == "free":
                boxes.append(dict(name=b.name,
                                  cx=[b.x0, b.x1], cy=[b.y0, b.y1],
                                  theta_deg=[math.degrees(b.t0), math.degrees(b.t1)],
                                  anchor=[b.anchor[0], b.anchor[1], math.degrees(b.anchor[2])],
                                  tilted=bool(abs(b.anchor[2]) > 1e-9),
                                  half_extent=[0.5 * (b.x1 - b.x0), 0.5 * (b.y1 - b.y0),
                                               math.degrees(0.5 * (b.t1 - b.t0))]))
            else:
                pins.append(dict(name=b.name, alpha=[b.ax[0], b.ay[0]], beta=[b.ax[1], b.ay[1]],
                                 halfwidth=b.hh, theta_deg=0.0,
                                 centre_at_s0=[b.ax[0] + b.ax[1] * A.S0, b.ay[0] + b.ay[1] * A.S0]))
        rec116 = a116_row(t)
        tilted = [b["name"] for b in boxes if b["tilted"]]
        cut = None
        if t["cut"] is not None:
            cut = dict(kind="tilt_floor_deg", value=t["cut"], applies_to=tilted,
                       inequality="theta_l (mod 90 deg) >= %.6f for every l in %s" % (t["cut"], tilted),
                       reason="A110 grain boundary; F_T(theta) > s0 for theta > theta_T + 6.1e-5 deg "
                              "(theta_T = %.6f)" % A.THETA_T)
        samp = A.sample_check(bodies, nv, n_samples=12000, seed=int(1000 * t["r"] + t["rho"]),
                              s_lo=A.S_LO, s_hi=A.S0, n_side=30)
        entry = dict(
            id=t["id"], tag=t["tag"], cls=t["cls"], r=t["r"], rho_deg=t["rho"],
            anchor_side=A.S0, window=[A.S_LO, A.S_HI_DEFAULT],
            L=[b["name"] for b in boxes], P=[p["name"] for p in pins],
            boxes=boxes, pins=pins, cut=cut,
            hypothesis=("s in [%r, %r]; for each pin p: a square with tilt 0 and centre in "
                        "(alpha_p + beta_p s) + [-%r, %r]^2; for each l in L: a DISTINCT other square "
                        "with centre in the box and tilt (mod 90 deg) in the interval%s; "
                        "conclusion: no such configuration is a packing at side <= s0."
                        % (A.S_LO, A.S_HI_DEFAULT, A.PIN_SLACK, A.PIN_SLACK,
                           "" if cut is None else " and " + cut["inequality"])),
            tree_verdict=(None if rec116 is None else dict(
                dead=rec116["tree"]["dead"], certified_min=rec116["tree"]["certified_min"],
                measured_min=(rec116.get("local_min") or {}).get("side"),
                sample_hits=(rec116.get("sampling") or {}).get("hits"),
                trump_inside=rec116["trump"]["inside"], seconds=rec116["seconds_tree"])),
            sample_check=dict(n_samples=samp["n_samples"], hits=samp["hits"],
                              free_pairs_disjoint=samp["free_pairs_disjoint"],
                              sides_tested=30, side_range=[A.S_LO, A.S0],
                              worst_free_overlap_of_rejects=samp["worst_free_overlap_of_rejects"]),
            frame_ops=frame_ops_for(t["cls"]),
        )
        out["N"].append(entry)
        log("%-24s L=%s  boxes r=%.3f rho=%.1f cut=%s  sampled %d (free-disjoint %d) hits=%d  "
            "tree dead=%s cert=%s" % (t["id"], entry["L"], t["r"], t["rho"], t["cut"],
                                      samp["n_samples"], samp["free_pairs_disjoint"], samp["hits"],
                                      entry["tree_verdict"]["dead"], entry["tree_verdict"]["certified_min"]))
    with open(os.path.join(RES, "N_boxes.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    log("wrote results/N_boxes.json (%d neighbourhoods)" % len(out["N"]))


if __name__ == "__main__":
    main()
