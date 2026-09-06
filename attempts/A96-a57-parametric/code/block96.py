"""
A96 BLOCK-FIRST pilot (block96) -- PI hypothesis: the mid-tilt certification holes of the k5_11
tree (docs/cert_failures.md C / D / H) are Trump's PINWHEEL, i.e. a flush 2x2 same-tilt block of
four unit squares behaving as ONE rigid body with parameters (cx, cy, theta).

The pilot adds, on top of an A57 level-1 node's own hypothesis (5 pins + the conditioned interior
square's box), the hypothesis

    "four squares of the packing form a flush 2x2 block whose rigid-body parameters lie in B"

for B on a coarse grid of (block centre) x (block tilt).  From B the four squares' individual
parameter boxes are the rigid-body image
        square_i box = { (c + R(th) d_i, th) : (c, th) in B },   d_i = R(0) (+-1/2, +-1/2)
outer-approximated by an axis-aligned centre box (exact interval trig on the arc) with the SAME
tilt interval.  Those four boxes are pinned with A57/A85 core machinery (caselp.Box.core), so
the node hypothesis becomes 5 pin cores + 4 block cores (+ the node box when it is provably a
different square), and the budget drops accordingly.

SOUNDNESS (the only two facts used, both A57's own):
  * distinctness: two core boxes are realised by DIFFERENT squares of the packing as soon as the
    parameter boxes are disjoint in (x, y, theta) -- one square has one (centre, theta).  So
    budget = 11 - #cores is legitimate exactly when the boxes are pairwise disjoint (checked, not
    assumed) and no box realises a pin placement (pinguard.box_realizes_pin).
  * logic kill: if two cores of DISTINCT squares overlap, the hypothesis is contradictory and the
    case is empty with no LP (pinguard.cores_meet), which is A57's KILL-BY-LOGIC.

Two LP levels are used, because the 9-core level is node-independent:
  BLOCK-ONLY   : 5 pins + 4 block boxes,           budget 11 - 9 = 2   (shared by all nodes)
  NODE+BLOCK   : 5 pins + 4 block boxes + node box, budget 11 - 10 = 1 (only when the node box is
                 parameter-disjoint from all four block boxes; otherwise the conditioned square
                 may BE a block square and only the block-only level is sound)
A BLOCK-ONLY kill is a kill for every node, so it is run first and the per-node LP is only run on
the block boxes that survive it.

CANARY: k5_11 carries no Trump image, so substrat.trump_realizes must be False on every hypothesis
we certify; any True is recorded and never certified.

Arbiter: A57 certify.py -> verify_case.py, sha256 521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af
(byte-identical to attempts/A96-a57-parametric/code/verify_case.py, the frozen copy).

Writes only under attempts/A96-a57-parametric/{results/block96,logs,notes}.
"""
import argparse, json, math, os, subprocess, sys, time
from fractions import Fraction as F

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
A96 = os.path.abspath(os.path.join(HERE, ".."))
PACK = os.path.abspath(os.path.join(A96, "..", ".."))
A57C = os.path.join(PACK, "attempts", "A57-shadow-trees", "code")
A53 = os.path.join(PACK, "attempts", "A53-simple-strata")
sys.path.insert(0, A57C)

import caselp                                        # noqa: E402
from caselp import Box, NoFam, Hyp, solve_node        # noqa: E402
from pinguard import classify, cores_meet, box_realizes_pin   # noqa: E402
from substrat import zones, trump_realizes            # noqa: E402

S_RAT = "969271/250000"
S0 = float(F(S_RAT))
PIN_DELTA = 1e-2
RES = os.path.join(A96, "results", "block96")
LOGS = os.path.join(A96, "logs")
CERTS = os.path.join(A96, "certs", "block96")
NODES = os.path.join(RES, "nodes")
TREE_G1 = os.path.join(PACK, "attempts", "A57-shadow-trees", "results")
CERTDIR_A57 = os.path.join(PACK, "attempts", "A57-shadow-trees", "certs", "tree", "k5_11_interior_G1")

R2 = math.sqrt(0.5)          # |(1/2, 1/2)|
PHI = (45.0, 135.0, 225.0, 315.0)


# ------------------------------------------------------------------ geometry
def _iv_cos(a, b):
    """[min, max] of cos over [a, b] radians (b - a <= 2pi)."""
    lo, hi = min(math.cos(a), math.cos(b)), max(math.cos(a), math.cos(b))
    k = math.ceil(a / (2 * math.pi))
    while 2 * math.pi * k <= b + 1e-15:          # cos = +1
        hi = 1.0
        k += 1
    k = math.ceil((a - math.pi) / (2 * math.pi))
    while math.pi + 2 * math.pi * k <= b + 1e-15:  # cos = -1
        lo = -1.0
        k += 1
    return lo, hi


def _iv_sin(a, b):
    return _iv_cos(a - math.pi / 2, b - math.pi / 2)


def block_square_boxes(cx0, cx1, cy0, cy1, th0, th1, pad=1e-9):
    """the four rigid-body image boxes of a flush 2x2 same-tilt block box B."""
    out = []
    for phi in PHI:
        a, b = math.radians(th0 + phi), math.radians(th1 + phi)
        dxl, dxh = _iv_cos(a, b)
        dyl, dyh = _iv_sin(a, b)
        out.append(Box(cx0 + R2 * dxl - pad, cx1 + R2 * dxh + pad,
                       cy0 + R2 * dyl - pad, cy1 + R2 * dyh + pad, th0, th1))
    return out


def boxes_disjoint(b1, b2, eps=0.0):
    """parameter-box disjointness in (x, y, theta): then the two hypotheses are realised by
    DIFFERENT squares (one square has exactly one (centre, theta))."""
    return (b1.x1 < b2.x0 - eps or b2.x1 < b1.x0 - eps or
            b1.y1 < b2.y0 - eps or b2.y1 < b1.y0 - eps or
            b1.th1 < b2.th0 - eps or b2.th1 < b1.th0 - eps)


def pins_at(delta=PIN_DELTA):
    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))["k5_11"]]
    hh = delta / math.sqrt(2.0)
    return [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in slots], slots


# ------------------------------------------------------------------ stage A: enumerate B
def enumerate_blocks(g, dth, a_min, s=S0):
    """coarse grid over the block's (centre, tilt) space.  Block half-extent at tilt th is
    cos th + sin th, so the block centre must lie in [W, s - W] with W = max over the tilt bin."""
    pin_boxes, slots = pins_at()
    out = []
    nth = int(round(90.0 / dth))
    for k in range(nth):
        th0, th1 = k * dth, (k + 1) * dth
        W = max(math.cos(math.radians(t)) + math.sin(math.radians(t)) for t in (th0, th1))
        lo, hi = W, s - W
        if hi <= lo:
            continue
        n = max(1, int(math.ceil((hi - lo) / g)))
        edges = [lo + (hi - lo) * i / n for i in range(n + 1)]
        for i in range(n):
            for j in range(n):
                B = dict(cx0=edges[i], cx1=edges[i + 1], cy0=edges[j], cy1=edges[j + 1],
                         th0=th0, th1=th1)
                sq = block_square_boxes(**B)
                rec = dict(bid="B%02d_%02d_%02d" % (k, i, j), B=B, status="ok",
                           sq=[b.to_json() for b in sq])
                cores = [b.core() for b in sq]
                if any(c is None for c in cores):
                    rec["status"] = "nocore"
                    out.append(rec); continue
                rec["a"] = min(float(c.a) for c in cores)
                if rec["a"] < a_min:
                    rec["status"] = "a_below_min"
                    out.append(rec); continue
                if any(b.vacuous(s) for b in sq):
                    rec["status"] = "vacuous"          # a block square cannot fit: B is empty
                    out.append(rec); continue
                # distinctness of the four block squares from each other
                if not all(boxes_disjoint(sq[p], sq[q]) for p in range(4) for q in range(p + 1, 4)):
                    rec["status"] = "block_boxes_overlap"
                    out.append(rec); continue
                # distinctness from the pins, and the pin logic kill
                bad = None
                for bi, b in enumerate(sq):
                    st, info = classify(b, pin_boxes, slots)
                    if st == "parent":
                        bad = ("realises_pin", bi, info); break
                    if st == "contradictory":
                        bad = ("logic_kill_pin", bi, info); break
                if bad:
                    rec["status"] = bad[0]; rec["why"] = [bad[1], bad[2]]
                    out.append(rec); continue
                hyp = Hyp(pin_boxes + sq, [])
                rec["trump_realizes"] = trump_realizes(hyp, slots)
                if rec["trump_realizes"]:
                    rec["status"] = "canary"
                out.append(rec)
    return out


# ------------------------------------------------------------------ LP + certify
def certify(node_path, cert_out, depth=56, cert_time=240, rounds=1, scale_cap=1.40, tau=None):
    # A57 certify.py's auto scale (--scale 0) divides by tau; a block-first node can have tau = 0
    # exactly (no admissible row survives 10 cores), so pass a fixed scale there.  Nothing in the
    # frozen chain changes: the scale only multiplies an EMPTY weight vector.
    scale_args = ["--scale", "1.03"] if (tau is not None and tau <= 1e-12) else \
                 ["--scale", "0", "--scale_cap", "%.5f" % scale_cap]
    cmd = [sys.executable, os.path.join(A57C, "certify.py"), node_path, "--s_rat", S_RAT,
           "--rounds", str(rounds), "--jobs", "1", "--depth", str(depth),
           "--time_limit", str(cert_time), "--out", cert_out] + scale_args + \
          ["--max_w", "64", "--loop_cols"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, round(time.time() - t0, 1), (p.stdout or "")[-2500:]


def run_case(tag, hyp, budget, slots, time_limit, log, do_cert=True, cert_time=240, depth=56):
    """solve the node LP with A57's kwargs, then certify with the frozen arbiter."""
    node_path = os.path.join(NODES, tag + ".json")
    rec = dict(tag=tag, budget=budget, ncores=len(hyp.boxes))
    canary = trump_realizes(hyp, slots)
    rec["trump_realizes"] = canary
    t0 = time.time()
    if os.path.exists(node_path):
        res = json.load(open(node_path))
        rec["lp_seconds"] = 0.0; rec["cached"] = True
    else:
        res = solve_node(S0, hyp, budget, sym_kind="C1", warm=None,
                         time_limit=time_limit, max_iter=900, out=None, log=log,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
        json.dump(res, open(node_path, "w"))
        rec["lp_seconds"] = round(time.time() - t0, 1)
    rec.update(tau=res["tau"], converged=res["converged"], eta=res["tau"] - budget,
               nrows=len(res.get("rows_all", [])))
    if canary:
        rec["verdict"] = "CANARY (Trump-realizable: never certified)"
        return rec
    if res["tau"] >= budget:
        rec["verdict"] = "ALIVE-at-LP"
        return rec
    rec["verdict"] = "DEAD-at-LP"
    if not do_cert:
        return rec
    cert_out = os.path.join(CERTS, tag + ".json")
    rc, secs, out = certify(node_path, cert_out, depth=depth, cert_time=cert_time, tau=res["tau"])
    rec["cert_seconds"] = secs
    rec["cert"] = "PASS" if rc == 0 else "FAIL(rc=%d)" % rc
    rec["cert_path"] = cert_out if rc == 0 else None
    if rc != 0:
        rec["cert_tail"] = [l for l in out.splitlines() if l.strip().startswith(("PASS", "FAIL", "boxes", "certificate", "no witness"))][-6:]
    return rec


# ------------------------------------------------------------------ stage 3: pinwheel signature
def pinwheel_signature(node_ids, dtilt=3.0, dcentre=1.5, lo=15.0, hi=45.0, kmin=3):
    """do a node's MID-TILT witness placements come in groups of >= kmin with tilts within
    dtilt deg and centres within dcentre?  (a block-shaped fractional adversary)"""
    out = []
    for nid in node_ids:
        files = sorted(f for f in os.listdir(CERTDIR_A57)
                       if f.startswith(nid + ".") or f.startswith(nid + "_"))
        files = [f for f in files if f.endswith("witnesses.json")]
        P = []
        for f in files:
            try:
                W = json.load(open(os.path.join(CERTDIR_A57, f)))["witnesses"]
            except Exception:
                continue
            for w in W:
                p = w.get("placement")
                if not p:
                    continue
                th = float(p["theta_deg"]) % 90.0
                P.append((float(p["cx_float"]), float(p["cy_float"]), th, w.get("kind")))
        # DEDUP: the verifier emits one witness per refined sub-box, so the same placement can
        # appear 8-32 times.  Collapse to DISTINCT placements before asking for "groups of >= 3",
        # otherwise box refinement alone would satisfy the signature.
        uniq, seen = [], []
        for p in P:
            if any(abs(p[2] - q[2]) <= 0.25 and math.hypot(p[0] - q[0], p[1] - q[1]) <= 0.05 for q in seen):
                continue
            seen.append(p); uniq.append(p)
        P_all, P = P, uniq
        mid = [p for p in P if lo <= p[2] <= hi]
        # greedy single-link clustering in (centre, tilt)
        groups = []
        for p in mid:
            hit = None
            for gi, gp in enumerate(groups):
                if any(abs(p[2] - q[2]) <= dtilt and math.hypot(p[0] - q[0], p[1] - q[1]) <= dcentre for q in gp):
                    hit = gi; break
            if hit is None:
                groups.append([p])
            else:
                groups[hit].append(p)
                # merge
                merged = [g for gi, g in enumerate(groups) if gi != hit and
                          any(abs(p[2] - q[2]) <= dtilt and math.hypot(p[0] - q[0], p[1] - q[1]) <= dcentre for q in g)]
                for m in merged:
                    groups[hit].extend(m); groups.remove(m)
        big = [g for g in groups if len(g) >= kmin]
        # a block-shaped group additionally wants pairwise centre separations near 1 or sqrt(2)
        blocky = 0
        for g in big:
            d = [math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(g) for b in g[i + 1:]]
            near1 = sum(1 for x in d if abs(x - 1.0) < 0.25 or abs(x - math.sqrt(2)) < 0.25)
            if near1 >= 1:
                blocky += 1
        out.append(dict(node=nid, n_witness_raw=len(P_all), n_witness=len(P),
                        n_midtilt=len(mid), n_files=len(files),
                        midtilt_pts=[[round(x, 4), round(y, 4), round(t, 3)] for (x, y, t, _) in mid],
                        group_sizes=sorted((len(g) for g in groups), reverse=True),
                        n_groups=len(groups), n_groups_ge_k=len(big),
                        max_group=(max(len(g) for g in groups) if groups else 0),
                        n_blocky_groups=blocky,
                        block_shaped=bool(big),
                        block_shaped_strict=bool(blocky),
                        tilt_spread_midtilt=(round(max(p[2] for p in mid) - min(p[2] for p in mid), 3) if mid else None)))
    return out


# ------------------------------------------------------------------ driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["enum", "blocklp", "nodelp", "pinwheel"])
    ap.add_argument("--g", type=float, default=0.18, help="block-centre grid step")
    ap.add_argument("--dth", type=float, default=5.0, help="tilt bin width (deg)")
    ap.add_argument("--a_min", type=float, default=0.30)
    ap.add_argument("--time_limit", type=float, default=900.0)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--nodes", default=os.path.join(RES, "selection.json"))
    ap.add_argument("--wall", type=float, default=1e9)
    ap.add_argument("--max_cases", type=int, default=10 ** 9)
    ap.add_argument("--no_cert", action="store_true")
    ap.add_argument("--bids", default=None, help="blocklp: json file with a list of bids to run (default: all live)")
    a = ap.parse_args()
    for d in (RES, LOGS, CERTS, NODES):
        os.makedirs(d, exist_ok=True)
    logf = open(os.path.join(LOGS, "block96_%s.log" % a.stage), "a", buffering=1)

    def log(*x):
        s = " ".join(str(y) for y in x)
        logf.write(s + "\n")

    t_start = time.time()
    if a.stage == "enum":
        rows = enumerate_blocks(a.g, a.dth, a.a_min)
        json.dump(dict(g=a.g, dth=a.dth, a_min=a.a_min, s=S_RAT, n=len(rows), rows=rows),
                  open(os.path.join(RES, "blocks.json"), "w"))
        import collections
        c = collections.Counter(r["status"] for r in rows)
        print(json.dumps(dict(total=len(rows), status=dict(c))))
        return

    if a.stage == "pinwheel":
        sel = json.load(open(a.nodes))
        out = pinwheel_signature([n["id"] for n in sel["nodes"] if n.get("has_witness")])
        json.dump(out, open(os.path.join(RES, "pinwheel.json"), "w"), indent=1)
        n = len(out)
        f = sum(1 for r in out if r["block_shaped"]) / n if n else 0
        fs = sum(1 for r in out if r["block_shaped_strict"]) / n if n else 0
        print(json.dumps(dict(nodes=n, frac_block_shaped=round(f, 3), frac_strict=round(fs, 3))))
        return

    blocks = json.load(open(os.path.join(RES, "blocks.json")))["rows"]
    live = [r for r in blocks if r["status"] == "ok"]
    pin_boxes, slots = pins_at()
    out_path = os.path.join(RES, "block96_%s.jsonl" % a.stage)
    done = set()
    if os.path.exists(out_path):
        for l in open(out_path):
            try:
                done.add(json.loads(l)["tag"])
            except Exception:
                pass

    if a.stage == "blocklp":
        want = set(json.load(open(a.bids))) if a.bids else None
        run_list = [r for r in live if want is None or r["bid"] in want]
        log("=== blocklp %s live=%d selected=%d done=%d"
            % (time.strftime("%H:%M:%S"), len(live), len(run_list), len(done)))
        n = 0
        for r in run_list:
            tag = "blk_" + r["bid"]
            if tag in done:
                continue
            if time.time() - t_start > a.wall or n >= a.max_cases:
                log("wall/max reached"); break
            sq = [Box.from_json(d) for d in r["sq"]]
            hyp = Hyp(pin_boxes + sq, [])
            rec = run_case(tag, hyp, 11 - 9, slots, a.time_limit, log,
                           do_cert=not a.no_cert, cert_time=a.cert_time, depth=a.depth)
            rec["bid"] = r["bid"]; rec["B"] = r["B"]; rec["a"] = r.get("a")
            with open(out_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            log("  " + json.dumps(rec))
            n += 1
        print(json.dumps(dict(stage="blocklp", ran=n, elapsed=round(time.time() - t_start, 1))))
        return

    # nodelp: per node x block boxes that SURVIVED blocklp
    sel = json.load(open(a.nodes))["nodes"]
    op = os.path.join(RES, "node_order.json")     # cheapest-first, so partial runs finish nodes
    if os.path.exists(op):
        rank = {k: i for i, k in enumerate(json.load(open(op)))}
        sel.sort(key=lambda d: rank.get(d["id"], 10 ** 6))
    surv = {}
    bp = os.path.join(RES, "block96_blocklp.jsonl")
    if os.path.exists(bp):
        for l in open(bp):
            r = json.loads(l)
            surv[r["bid"]] = r
    # a block box is dropped for every node only if the BLOCK-ONLY level already certified it;
    # block boxes not yet run at that level are carried (sound: the per-node level is stronger).
    alive_bids = [r["bid"] for r in live if surv.get(r["bid"], {}).get("cert") != "PASS"]
    bym = {r["bid"]: r for r in live}
    log("=== nodelp %s nodes=%d alive_block_boxes=%d done=%d"
        % (time.strftime("%H:%M:%S"), len(sel), len(alive_bids), len(done)))
    n = 0
    for nd in sel:
        nb = Box.from_json(nd["box"])
        for bid in sorted(alive_bids):
            tag = "nb_%s_%s" % (nd["id"].replace("k5_11_interior_", ""), bid)
            if tag in done:
                continue
            if time.time() - t_start > a.wall or n >= a.max_cases:
                log("wall/max reached"); break
            sq = [Box.from_json(d) for d in bym[bid]["sq"]]
            disj = all(boxes_disjoint(nb, b) for b in sq)
            rec0 = dict(tag=tag, node=nd["id"], bid=bid, node_box_disjoint=disj)
            if not disj:
                # the conditioned square may BE a block square: only the block-only level is sound
                bo = surv.get(bid, {})
                rec0.update(verdict="SUBSUMED (node box meets a block box; block-only verdict applies)",
                            block_only=(bo.get("cert") or bo.get("verdict") or "block-only level not run"))
                with open(out_path, "a") as f:
                    f.write(json.dumps(rec0) + "\n")
                continue
            # distinct squares: is the hypothesis contradictory?
            nc = nb.core()
            hit = [i for i, b in enumerate(sq) if nc is not None and cores_meet(nc, b.core())]
            if hit:
                rec0.update(verdict="KILL-BY-LOGIC (node core meets block core)", which=hit,
                            lp_seconds=0.0, cert="PASS-BY-LOGIC")
                with open(out_path, "a") as f:
                    f.write(json.dumps(rec0) + "\n")
                log("  " + json.dumps(rec0))
                n += 1
                continue
            hyp = Hyp(pin_boxes + sq + [nb], [])
            rec = run_case(tag, hyp, 11 - 10, slots, a.time_limit, log,
                           do_cert=not a.no_cert, cert_time=a.cert_time, depth=a.depth)
            rec.update(rec0)
            with open(out_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            log("  " + json.dumps(rec))
            n += 1
    print(json.dumps(dict(stage="nodelp", ran=n, elapsed=round(time.time() - t_start, 1))))


if __name__ == "__main__":
    main()
