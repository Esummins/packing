"""A120 -- the NO-side runner: shared helpers.

WHAT THIS IS.  A116 certified a neighbourhood N of the S02 minimum (docs/proofs/
local_certificate.md; A119 exported it as per-square boxes in `A119-local-cert-lean/results/
N_boxes.json`).  For an A57 node whose support lies inside N, the tautologous cover

    node  =  YES  u  NO_1  u  NO_2  u  NO_3  u  NO_4
    YES   =  node  &  (for every i, some square of the packing has its pose in F_i)
    NO_i  =  node  &  (no square of the packing has its pose in F_i)

lets the YES leaf be discharged with NO LP AT ALL -- it is contained in A116's N, which is dead --
and leaves only the four NO children for the solver.  This module builds the F_i.

WHY IT IS SOUNDNESS-ADJACENT.  The YES leaf is only inside N if the four boxes it uses are the
A119 boxes carried into the node's own frame by A107's `struct_op`, and if "some square in each
F_i" really produces |L| squares DISTINCT from each other and from the |P| class pins (N's
hypothesis says "a DISTINCT other square").  A wrong frame, or a pair of boxes that share a pose,
would under-constrain every NO LP built on the same boxes and nothing downstream would fail.  So
`map_boxes` records the boxes it produced and `soundness` re-derives and asserts, per node:

  A1  the node's five pin boxes ARE N's pins carried into the node frame (centres to 1e-9,
      half-width = A57's slack PIN_SLACK = 1e-2/sqrt2);
  A2  the four mapped boxes are pairwise POSE-DISJOINT (octagon.boxes_pose_disjoint, tilt mod 90),
      so "a square in each" gives four distinct squares;
  A3  each mapped box is pose-disjoint from every pin box (pinguard's 'parent' case: a pin
      placement inside F_i would let a pin witness it), so the four are distinct from the pins;
  A4  the D4 map is an involution/inverse pair: mapping the boxes BACK by struct_op reproduces
      A119's boxes exactly (<= 1e-12), and a dense pose sample round-trips into the class boxes;
  A5  the node's own A107 configuration lies in the mapped boxes (A116's `inside` test, recomputed
      in the NODE frame), reproducing A116's inside verdict without leaving the node's frame;
  A6  every NO family is built from EXACTLY the mapped box it names -- same centre rectangle
      (clamped only to the admissible strip [1/2, s-1/2], which contains no pose a square could
      have anyway) and the same tilt intervals mod 90.
  A7  every tilt interval fed to a kill is inside [0, 90] and every core half-side is <= 1/2.

Everything else (the LP, the two-stage timeout protocol, the frozen certifier) is A112's code,
imported, not copied: `regiontree.Runner.lp` and `regiontree.certify_leaf` are called directly so
the protocol and the frozen `verify_case.py` are byte-identical by construction.  A112's output
directories are REDIRECTED into this attempt's own results/ before anything runs -- A112, A116,
A119, A57 and A96 are read-only.
"""
from __future__ import annotations

import json, math, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

A112C = os.path.join(ROOT, "attempts", "A112-dual-branching", "code")
A57C = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for p in (A112C, A57C):
    if p not in sys.path:
        sys.path.insert(0, p)

import blas1  # noqa: E402,F401  MUST precede numpy

RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
PROG = os.path.join(BASE, "progress")
for d in (RES, NODES, LOGS, CERTS, PROG):
    os.makedirs(d, exist_ok=True)

import a112lib as L  # noqa: E402
# ---- REDIRECT A112's writable directories into A120 (A112 is read-only for us).
L.RES, L.NODES, L.CERTS, L.RT, L.LOGS = RES, NODES, CERTS, os.path.join(RES, "rt"), LOGS
L.SUF = "_a120"
os.makedirs(L.RT, exist_ok=True)

import octagon as OCT  # noqa: E402
import regiontree as RT  # noqa: E402
from caselp import Box, NoFam, Hyp  # noqa: E402
from pinguard import classify as pin_classify  # noqa: E402

sys.path.insert(0, A57C)
import pausegate  # noqa: E402

S0 = L.S0
S_RAT = L.S_RAT
PIN_SLACK = L.PIN_SLACK

A107R = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A119R = os.path.join(ROOT, "attempts", "A119-local-cert-lean", "results")
A96R = os.path.join(ROOT, "attempts", "A96-a57-parametric", "results")
A112R = os.path.join(ROOT, "attempts", "A112-dual-branching", "results")

N_ID = "S02_k5_11_r0.20_rho10"
YES_CLAIM = ("dead by local certificate A116 %s (pending A119 rational/Lean form)" % N_ID)
# A117 (2026-09-06, via the coordinator): verify_param_v2 (sha 153029ba...) now discharges
# NO-families and is Lean-backed, but a 4-D NO re-verification costs ~10x the four fixed sides.
# Inside this attempt's 15 CPU-h cap every NO certificate stays a FIXED-SIDE certificate at s0.
NO_TAG = ("s0-only, pending window re-verification (v2 available) "
          "[brief tag: s0-only, pending A117 verify_param_v2]")
VERIFY_PARAM_V2 = os.path.join(ROOT, "attempts", "A96-a57-parametric", "code",
                               "verify_param_v2.py")
VERIFY_PARAM_V2_SHA = "153029baddfcb77a2fa5049fc29c4ed8042dc847262e3ecefd5636c77fce1806"


# ------------------------------------------------------------------ inputs (READ-ONLY)
def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def n_entry(nid=N_ID):
    d = jload(os.path.join(A119R, "N_boxes.json"))
    for e in d["N"]:
        if e["id"] == nid:
            return d, e
    raise KeyError(nid)


def targets():
    return jload(os.path.join(A96R, "a116_targets.json"))["targets"]


_EX = None


def extract_index():
    global _EX
    if _EX is None:
        _EX = {n["nid"]: n for n in jload(os.path.join(A107R, "extract.json"))["nodes"]}
    return _EX


def node_src(nid):
    """The campaign's node json, COPIED into this attempt's results/nodes/ before anything reads
    it (A57 is read-only).  Returns (local path, campaign path)."""
    ex = extract_index()[nid]
    src = os.path.join(ROOT, ex["path"].replace("/", os.sep))
    dst = os.path.join(NODES, nid + ".src.json")
    if not os.path.exists(dst):
        with open(src, "rb") as f:
            b = f.read()
        tmp = dst + ".tmp"
        with open(tmp, "wb") as f:
            f.write(b)
        os.replace(tmp, dst)
    return dst, ex["path"]


def node_cls(nid):
    return nid.split("_interior")[0] if "_interior" in nid else nid.split("_")[0]


def node_level(nid):
    """A57 level = 1 + number of _D<digits> suffixes."""
    return 1 + sum(1 for p in nid.split("_")[2:] if p.startswith("D") and p[1:].isdigit())


# ------------------------------------------------------------------ the D4 map, class -> node
def d4(op, s=S0):
    return L.d4_ops(s)[op]


def inv_op(op):
    return L.D4_INV[op]


FLIPS = ("mx", "my", "diag", "anti")


def map_box(b, op, s=S0):
    """One A119 box (dict with cx, cy, theta_deg, in the CLASS frame) carried into the frame of a
    node whose A107 struct_op is `op`, i.e. by the INVERSE of op (A116's consumer maps the node's
    configuration FORWARD by op into the class frame, so the boxes come back by op^-1).

    A D4 element of the container is an isometry that maps axis-aligned centre rectangles to
    axis-aligned centre rectangles, so mapping the four corners and taking the hull is exact, not a
    relaxation.  Reflections negate the tilt (a square at tilt -t is the square at 90 - t)."""
    f = d4(inv_op(op), s)
    xs, ys = [], []
    for (x, y) in ((b["cx"][0], b["cy"][0]), (b["cx"][1], b["cy"][0]),
                   (b["cx"][0], b["cy"][1]), (b["cx"][1], b["cy"][1])):
        X, Y, _ = f(x, y, 0.0)
        xs.append(X)
        ys.append(Y)
    t0, t1 = b["theta_deg"]
    if inv_op(op) in FLIPS:
        t0, t1 = -t1, -t0
    return dict(name=b["name"], x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys),
                th0=t0, th1=t1, thetas=OCT.theta_intervals(t0, t1),
                src=dict(cx=list(b["cx"]), cy=list(b["cy"]), theta_deg=list(b["theta_deg"])))


def map_pin(p, op, s=S0):
    """One A119 pin (centre alpha + beta*s, half-width h, tilt 0) carried into the node frame.
    Kept AFFINE in s so the sampled covering check can move it over the window."""
    ax, ay = p["alpha"]
    bx, by = p["beta"]
    o = inv_op(op)
    # x' = A + B s ; the D4 action on (alpha, beta) coefficients
    def neg(a, b):
        return (-a, 1.0 - b)        # s - (a + b s)
    if o == "e":
        (Ax, Bx), (Ay, By) = (ax, bx), (ay, by)
    elif o == "r90":
        (Ax, Bx), (Ay, By) = neg(ay, by), (ax, bx)
    elif o == "r180":
        (Ax, Bx), (Ay, By) = neg(ax, bx), neg(ay, by)
    elif o == "r270":
        (Ax, Bx), (Ay, By) = (ay, by), neg(ax, bx)
    elif o == "mx":
        (Ax, Bx), (Ay, By) = neg(ax, bx), (ay, by)
    elif o == "my":
        (Ax, Bx), (Ay, By) = (ax, bx), neg(ay, by)
    elif o == "diag":
        (Ax, Bx), (Ay, By) = (ay, by), (ax, bx)
    elif o == "anti":
        (Ax, Bx), (Ay, By) = neg(ay, by), neg(ax, bx)
    else:
        raise ValueError(o)
    return dict(name=p["name"], alpha=[Ax, Ay], beta=[Bx, By], halfwidth=p["halfwidth"],
                theta_deg=0.0, centre_at_s0=[Ax + Bx * s, Ay + By * s])


def as_Box(m):
    return Box(m["x0"], m["x1"], m["y0"], m["y1"], m["th0"], m["th1"])


def nofam_of(m, s=S0):
    """The NO family of a mapped box: the SAME centre rectangle, clamped to the admissible strip
    [1/2, s - 1/2] (which discards no pose a unit square could have: its centre is at least
    w(theta)/2 >= 1/2 from every wall), and the SAME tilt set reduced mod 90.  A112's construction,
    verbatim."""
    F = as_Box(m)
    return NoFam(max(0.5, min(F.x0, s - 0.5)), max(0.5, min(F.x1, s - 0.5)),
                 max(0.5, min(F.y0, s - 0.5)), max(0.5, min(F.y1, s - 0.5)),
                 OCT.theta_intervals(F.th0, F.th1))


# ------------------------------------------------------------------ soundness assertions
def tilt_dev(a_deg, b_deg):
    d = abs(a_deg - b_deg) % 90.0
    return min(d, 90.0 - d)


def soundness(nid, op, mapped, mapped_pins, node_hyp, entry, s=S0, seed=0, nsample=2000):
    """A1..A7 of the module docstring.  Returns a record; ['ok'] is the verdict.  Nothing is run
    on a node whose record is not ok."""
    out = dict(node=nid, struct_op=op, inv_op=inv_op(op), s=s, N=entry["id"], checks={})
    pins, bins = L.split_hyp(Hyp.from_json(node_hyp))
    slots = L.pin_slots(pins)
    r = entry["r"]
    rho = entry["rho_deg"]

    # ---- A1  node pins == mapped N pins
    got = sorted((round(x, 9), round(y, 9)) for (x, y) in slots)
    want = sorted((round(p["centre_at_s0"][0], 9), round(p["centre_at_s0"][1], 9))
                  for p in mapped_pins)
    hw = sorted(round(0.5 * (b.x1 - b.x0), 12) for b in pins)
    out["checks"]["A1_pins_match"] = dict(
        ok=bool(got == want and len(pins) == len(mapped_pins)
                and all(abs(h - PIN_SLACK) < 1e-12 for h in hw)
                and all(b.th0 == 0.0 and b.th1 == 0.0 for b in pins)),
        node_pins=got, mapped_N_pins=want, halfwidths=hw, pin_slack=PIN_SLACK)

    # ---- A2  the four boxes are pairwise pose-disjoint (=> four DISTINCT squares)
    pd, bad = [], []
    for i in range(len(mapped)):
        for j in range(i + 1, len(mapped)):
            ok = OCT.boxes_pose_disjoint(as_Box(mapped[i]), as_Box(mapped[j]))
            pd.append(dict(pair=[mapped[i]["name"], mapped[j]["name"]], disjoint=bool(ok)))
            if not ok:
                bad.append(pd[-1]["pair"])
    out["checks"]["A2_boxes_pose_disjoint"] = dict(ok=not bad, pairs=pd, bad=bad)

    # ---- A3  each box is pose-disjoint from every pin box, and pinguard does not call it 'parent'
    pb, bad3 = [], []
    for m in mapped:
        F = as_Box(m)
        st, info = pin_classify(F, pins, slots)
        dis = all(OCT.boxes_pose_disjoint(F, p) for p in pins)
        pb.append(dict(box=m["name"], pinguard=st, pin_info=info, disjoint_from_all_pins=bool(dis)))
        if st == "parent" or not dis:
            bad3.append(m["name"])
    out["checks"]["A3_boxes_vs_pins"] = dict(ok=not bad3, boxes=pb, bad=bad3)

    # ---- A4  the map is exactly invertible, and a dense pose sample round-trips
    f = d4(op, s)
    back, worst = [], 0.0
    for m, b in zip(mapped, entry["boxes"]):
        xs, ys = [], []
        for (x, y) in ((m["x0"], m["y0"]), (m["x1"], m["y0"]), (m["x0"], m["y1"]), (m["x1"], m["y1"])):
            X, Y, _ = f(x, y, 0.0)
            xs.append(X)
            ys.append(Y)
        t0, t1 = m["th0"], m["th1"]
        if op in FLIPS:
            t0, t1 = -t1, -t0
        e = max(abs(min(xs) - b["cx"][0]), abs(max(xs) - b["cx"][1]),
                abs(min(ys) - b["cy"][0]), abs(max(ys) - b["cy"][1]),
                abs(t0 - b["theta_deg"][0]), abs(t1 - b["theta_deg"][1]))
        worst = max(worst, e)
        back.append(dict(box=m["name"], max_abs_error=e))
    rng = random.Random(seed + 11)
    drawn = tested = inside_n = 0
    for _ in range(nsample):
        for m, b in zip(mapped, entry["boxes"]):
            x = rng.uniform(m["x0"], m["x1"])
            y = rng.uniform(m["y0"], m["y1"])
            t = rng.uniform(m["th0"], m["th1"])
            X, Y, T = f(x, y, t)
            drawn += 1
            okxy = (b["cx"][0] - 1e-9 <= X <= b["cx"][1] + 1e-9
                    and b["cy"][0] - 1e-9 <= Y <= b["cy"][1] + 1e-9)
            anc = b["anchor"][2]
            okt = tilt_dev(T, anc) <= rho + 1e-9
            tested += 1
            inside_n += bool(okxy and okt)
    out["checks"]["A4_map_invertible"] = dict(
        ok=bool(worst < 1e-12 and inside_n == drawn),
        max_abs_roundtrip_error=worst, per_box=back,
        sample=dict(drawn=drawn, tested=tested, inside_class_boxes=inside_n))

    # ---- A5  the node's own A107 configuration lies in the mapped boxes (A116's inside test,
    #          recomputed in the NODE frame)
    ex = extract_index().get(nid)
    a5 = dict(ok=False, note="node not in A107 extract.json")
    if ex is not None and ex.get("cfg"):
        cfg = [(p[0], p[1], math.degrees(p[2])) for p in ex["cfg"]]
        best = None
        import itertools
        for perm in itertools.permutations(range(len(cfg)), len(mapped)):
            dmax = tmax = 0.0
            for m, j in zip(mapped, perm):
                x, y, t = cfg[j]
                anc_src = next(b for b in entry["boxes"] if b["name"] == m["name"])["anchor"]
                AX, AY, AT = f(x, y, t)          # carry the node pose into the class frame
                dmax = max(dmax, abs(AX - anc_src[0]), abs(AY - anc_src[1]))
                tmax = max(tmax, tilt_dev(AT, anc_src[2]))
            if best is None or (dmax, tmax) < best:
                best = (dmax, tmax)
        a5 = dict(ok=bool(best is not None and best[0] <= r + 1e-9 and best[1] <= rho + 1e-9),
                  dmax=round(best[0], 6), tmax=round(best[1], 4), r=r, rho=rho,
                  note="A116 consumer116.inside, recomputed here")
    out["checks"]["A5_node_config_inside_N"] = a5

    # ---- A6  each NO family IS the mapped box (clamp only to the admissible strip)
    a6, bad6 = [], []
    for m in mapped:
        nf = nofam_of(m, s)
        F = as_Box(m)
        clamp = dict(x0=(nf.x0 != F.x0), x1=(nf.x1 != F.x1),
                     y0=(nf.y0 != F.y0), y1=(nf.y1 != F.y1))
        # a clamped edge is only allowed where it moved the edge onto the admissible strip
        legal = ((not clamp["x0"] or F.x0 < 0.5 or F.x0 > s - 0.5)
                 and (not clamp["x1"] or F.x1 < 0.5 or F.x1 > s - 0.5)
                 and (not clamp["y0"] or F.y0 < 0.5 or F.y0 > s - 0.5)
                 and (not clamp["y1"] or F.y1 < 0.5 or F.y1 > s - 0.5))
        same_t = (nf.thetas == [tuple(t) for t in OCT.theta_intervals(F.th0, F.th1)]
                  == [tuple(t) for t in m["thetas"]])
        ok = bool(legal and same_t)
        a6.append(dict(box=m["name"], yes_box=L.box_json(F),
                       no_zone=[nf.x0, nf.x1, nf.y0, nf.y1], no_thetas=nf.thetas,
                       clamped=clamp, clamp_legal=bool(legal), thetas_identical=bool(same_t),
                       ok=ok))
        if not ok:
            bad6.append(m["name"])
    out["checks"]["A6_nofam_is_the_same_box"] = dict(ok=not bad6, boxes=a6, bad=bad6)

    # ---- A7  normalised tilt in [0, 90] and core half-side <= 1/2 on every branch
    a7, bad7 = [], []
    for m in mapped:
        F = as_Box(m)
        try:
            halves = []
            for nb in L.normalise_tilt(F):
                assert 0.0 <= nb.th0 <= nb.th1 <= 90.0 + 1e-9, "tilt outside [0, 90]"
                c = OCT.safe_kill_core(nb)
                halves.append(None if c is None else float(c.a))
            a = L.assert_core_half_side(F)
            a7.append(dict(box=m["name"], branches=len(halves), half_sides=halves, max_half=a))
        except AssertionError as ex:
            a7.append(dict(box=m["name"], error=str(ex)[:120]))
            bad7.append(m["name"])
    out["checks"]["A7_tilt_and_core"] = dict(ok=not bad7, boxes=a7, bad=bad7)

    out["ok"] = all(v.get("ok") for v in out["checks"].values())
    return out


# ------------------------------------------------------------------ the covering check (T2)
def sat_gap(ca, ta, cb, tb):
    return L.sat_gap(ca, ta, cb, tb)


def covering_check(mapped, mapped_pins, n_survivors=10000, seed=1, s_lo=3.82, s_hi=S0,
                   n_side=30, max_draws=4000000):
    """A116's `sample_check`, in the NODE frame, on the MAPPED boxes.  Uniform poses in the four
    boxes and uniform pin offsets; a draw SURVIVES when the free squares are pairwise SAT-disjoint
    (the cheap filter -- almost every draw already has two of the wide boxes overlapping); a
    survivor is TESTED at `n_side` sides spanning [s_lo, s_hi] and is a HIT if it is a packing of
    L u P at that side.  A hit would refute Theorem LOCAL as transcribed AND this frame map.

    Reports drawn -> tested -> hits, and keeps drawing until `n_survivors` survivors are tested."""
    rng = random.Random(seed)
    sides = [s_lo + (s_hi - s_lo) * i / (n_side - 1.0) for i in range(n_side)]
    drawn = tested = hits = 0
    worst_reject = -1e18
    best_pack = -1e18
    examples = []
    while tested < n_survivors and drawn < max_draws:
        drawn += 1
        poses = []
        for m in mapped:
            poses.append((rng.uniform(m["x0"], m["x1"]), rng.uniform(m["y0"], m["y1"]),
                          math.radians(rng.uniform(m["th0"], m["th1"]))))
        g = 1e18
        for i in range(len(poses)):
            for j in range(i + 1, len(poses)):
                g = min(g, sat_gap(poses[i][:2], poses[i][2], poses[j][:2], poses[j][2]))
                if g < -1e-9:
                    break
            if g < -1e-9:
                break
        if g < -1e-9:
            worst_reject = max(worst_reject, g)
            continue
        tested += 1
        offs = [(rng.uniform(-p["halfwidth"], p["halfwidth"]),
                 rng.uniform(-p["halfwidth"], p["halfwidth"])) for p in mapped_pins]
        hit = None
        for s in reversed(sides):
            cfg = list(poses)
            for p, o in zip(mapped_pins, offs):
                cfg.append((p["alpha"][0] + p["beta"][0] * s + o[0],
                            p["alpha"][1] + p["beta"][1] * s + o[1], 0.0))
            wp = 1e18
            for i in range(len(cfg)):
                for j in range(i + 1, len(cfg)):
                    wp = min(wp, sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2]))
            ww = 1e18
            for (x, y, t) in cfg:
                ww = min(ww, min(L.wall_gaps(x, y, t, s).values()))
            best_pack = max(best_pack, min(wp, ww))
            if min(wp, ww) >= -1e-9:
                hit = dict(side=s, worst_pair=wp, worst_wall=ww)
            else:
                break
        if hit is not None:
            hits += 1
            if len(examples) < 3:
                examples.append(hit)
    return dict(drawn=drawn, tested=tested, hits=hits, n_side=n_side,
                side_range=[s_lo, s_hi], seed=seed,
                worst_free_overlap_of_rejects=(None if worst_reject < -1e17 else worst_reject),
                best_packing_margin=(None if best_pack < -1e17 else best_pack),
                examples=examples)


# ------------------------------------------------------------------ the certifier, with a WALL
def certify_leaf_capped(region, ordering, key, node_json, log, cert_time=300.0, depth=56,
                        rounds=3, wall=900.0):
    """`regiontree.certify_leaf` with one addition: a HARD WALL on the certification subprocess.

    Everything else is A112's call, argument for argument -- A57's `certify.py --jobs 1
    --loop_cols` driving the frozen `verify_case.py` -- and the cache file is the same
    `<tag>.json.done`.  The wall exists because the witness-feedback loop has no bound of its own:
    `--time_limit` caps each LP re-solve, not the run, and a child that never becomes coverable
    burns 1900 s before `certify.py` gives up (measured, `Y0973/NO0`, rounds = 3).

    A CAPPED run is recorded as its own result, `CAP`, and is NEVER a verdict: it is treated
    exactly like FAIL (the child stays ALIVE), following A117's rule that a verification cap must
    sit where it can only abort, never decide.  The whole process tree is killed on the wall, so no
    orphaned `verify_case.py` is left behind.
    """
    tag = "%s%s__%s__%s" % (region, L.SUF, ordering, key)
    node = os.path.join(L.NODES, node_json)
    out = os.path.join(L.CERTS, tag + ".json")
    if os.path.exists(out + ".done"):
        return L.jload(out + ".done")
    if not L.gate(log, tag):
        return dict(tag=tag, result="SKIP-GATE")
    cmd = [sys.executable, os.path.join(A112C, "certify.py"), node, "--s_rat", L.S_RAT,
           "--rounds", str(rounds), "--jobs", "1", "--depth", str(depth),
           "--time_limit", str(cert_time), "--out", out, "--scale", "0",
           "--scale_cap", "1.4", "--max_w", "64", "--loop_cols"]
    t0 = time.time()
    capped = False
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        txt = p.communicate(timeout=wall)[0] or ""
        rc = p.returncode
    except subprocess.TimeoutExpired:
        capped = True
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                       capture_output=True)
        try:
            txt = p.communicate(timeout=60)[0] or ""
        except Exception:
            txt = ""
        rc = 124
    tail = [ln for ln in txt.splitlines()
            if ln.startswith(("PASS", "FAIL", "boxes", "[round", "certificate", "CERTIFIED",
                              "NOT certified", "MALFORMED"))]
    r = dict(tag=tag, rc=rc, result=("PASS" if rc == 0 else ("CAP" if capped else "FAIL")),
             capped=capped, wall_cap_s=wall, rounds=rounds, cert_time=cert_time,
             seconds=round(time.time() - t0, 1), verifier=tail[-6:])
    L.jdump(out + ".done", r)
    log("    cert %-46s %s (%.0fs)" % (key, r["result"], r["seconds"]))
    return r


# ------------------------------------------------------------------ misc
def mklog(name):
    return L.mklog(name)


def jdump(p, o):
    L.jdump(p, o)


def key_of(cls, nid):
    return "%s__%s" % (cls, nid)
