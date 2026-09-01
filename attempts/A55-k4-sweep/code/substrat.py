"""
A54 rung 3: ONE-LEVEL sub-stratification of a straggler stratum (the A27 zone-branch pattern).

Parent node: the k pinned slot squares of the stratum (cores, budget 11-k).
Branch on a zone Z (rectangle of centres, all orientations):
   NO  child : parent + NO-family (Z x [0,90])                      budget 11-k
   YES_i     : parent + core box B_i, {B_i} a CLOSED COVER of Z x [0,90]   budget 11-k-1
The disjunction "no square centre in Z" OR "some square has (centre,theta) in some B_i"
is exhaustive, so the parent stratum is empty as soon as EVERY child carries an exact
certificate (verify_case.py).  A box with an empty rational core is refused (it would not
be a sound YES node) -- it must be split further; the driver splits such boxes automatically
and reports any it cannot fix.

Canary: a child whose hypotheses are realized by Trump's own packing is NEVER certified
(it must stay alive); the driver checks every child against the A03 Trump coordinates.
"""
import argparse, json, math, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
import caselp
from caselp import Box, NoFam, Hyp, solve_node, warm_from_result
from run_skel import S0F

S_RAT = "969271/250000"
TRUMP = os.path.abspath(os.path.join(BASE, "..", "A03-upper-reconstruct", "trump11_float.json"))


# ------------------------------------------------------------------ zones
def zones(s, cw=0.6):
    a, b = 0.5, s - 0.5
    c0, c1 = a + cw, b - cw
    return {"corner_BL": (a, c0, a, c0), "corner_BR": (c1, b, a, c0), "corner_TR": (c1, b, c1, b),
            "corner_TL": (a, c0, c1, b), "side_L": (a, c0, c0, c1), "side_B": (c0, c1, a, c0),
            "side_R": (c1, b, c0, c1), "side_T": (c0, c1, c1, b), "interior": (c0, c1, c0, c1)}


def cover_boxes(rect, s, nx, ny, nth, depth=0):
    """closed cover of rect x [0,90] by boxes with a non-empty rational core; boxes with an
    empty core are bisected (up to 3 extra levels).  Vacuous boxes (no admissible placement)
    are dropped -- sound, they contain no case."""
    x0, x1, y0, y1 = rect
    out, bad = [], []
    todo = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nth):
                todo.append(Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                                y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                                90.0 * k / nth, 90.0 * (k + 1) / nth))
    for _ in range(4):
        nxt = []
        for b in todo:
            if b.vacuous(s):
                continue
            if b.core() is not None:
                out.append(b)
            else:
                nxt.append(b)
        if not nxt:
            break
        todo = [h for b in nxt for h in b.split()]
    else:
        bad = todo
    return out, bad


# ------------------------------------------------------------------ Trump canary
def trump_realizes(hyp, slots):
    """True if Trump's packing (embedded at s0 as in A53's check_trump_feasible) satisfies
    the node hypotheses: every pin/core occupied by one of his squares and no square in a
    NO-family.  Such a node must never be certified."""
    if not os.path.exists(TRUMP):
        return None
    X = json.load(open(TRUMP))["X"]
    P = [(x, y, th) for (x, y, th) in X]
    tol = 1e-5      # s0 - s_T = 4.1e-7 (the A53 embedding moves the R-family pins outward)
    for b in hyp.boxes:
        # the YES hypothesis is "some square of P has (centre, theta) IN THE BOX" (not: overlaps its core)
        hit = any(b.x0 - tol <= x <= b.x1 + tol and b.y0 - tol <= y <= b.y1 + tol and
                  b.th0 - 1e-4 <= math.degrees(th) % 90.0 <= b.th1 + 1e-4 for (x, y, th) in P)
        if not hit:
            return False
    for f in hyp.nofams:
        for (x, y, th) in P:
            if f.contains(x, y, math.degrees(th) % 90):
                return False
    return True


# ------------------------------------------------------------------ children
def build_children(name, zone, nx, ny, nth, cw):
    slots_map = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    slots = [tuple(p) for p in slots_map[name]]
    pins = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in slots]
    rect = zones(S0F, cw)[zone]
    boxes, bad = cover_boxes(rect, S0F, nx, ny, nth)
    kids = [dict(id=f"{name}_{zone}_NO", kind="NO",
                 hyp=Hyp(pins, [NoFam(rect[0], rect[1], rect[2], rect[3], [(0.0, 90.0)])]),
                 budget=11 - len(slots))]
    for i, b in enumerate(boxes):
        kids.append(dict(id=f"{name}_{zone}_Y{i:02d}", kind="YES", box=b,
                         hyp=Hyp(pins + [b], []), budget=11 - len(slots) - 1))
    return kids, bad, slots, rect


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--zone", required=True)
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--nx", type=int, default=2)
    ap.add_argument("--ny", type=int, default=2)
    ap.add_argument("--nth", type=int, default=3)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--time_limit", type=float, default=420)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--scale_cap", type=float, default=1.06)
    ap.add_argument("--plan_only", action="store_true")
    ap.add_argument("--lp_only", action="store_true", help="rung-3 viability probe: node LP only, no certification")
    a = ap.parse_args()

    kids, bad, slots, rect = build_children(a.name, a.zone, a.nx, a.ny, a.nth, a.cw)
    si, sn = map(int, a.shard.split("/"))
    outdir = os.path.join(BASE, "results", "tree", a.name)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(BASE, "certs", "tree"), exist_ok=True)
    if a.plan_only:
        print(json.dumps(dict(name=a.name, zone=a.zone, rect=rect, children=len(kids),
                              uncoverable=len(bad), ids=[k["id"] for k in kids],
                              canary=[k["id"] for k in kids if trump_realizes(k["hyp"], slots)]), indent=1))
        return
    if bad:
        print(f"WARNING: {len(bad)} boxes with no rational core after 4 splits -- cover NOT complete")
    mine = [k for i, k in enumerate(kids) if i % sn == si]
    logf = open(os.path.join(BASE, "logs", f"substrat_{a.name}_{a.zone}_s{si}.log"), "a", buffering=1)
    def log(*x):
        print(*x, file=logf, flush=True)
    warm_src = os.path.join(BASE, "results", "nodes", f"{a.name}.json")
    if not os.path.exists(warm_src):
        warm_src = os.path.join(A53, "results", "nodes", f"{a.name}.json")
    warm = warm_from_result(json.load(open(warm_src)))
    summary = os.path.join(BASE, "results", f"tree_{a.name}_{a.zone}_s{si}.jsonl")
    for kid in mine:
        node_path = os.path.join(outdir, f"{kid['id']}.json")
        rec = dict(id=kid["id"], kind=kid["kind"], budget=kid["budget"], zone=a.zone)
        if kid["kind"] == "YES":
            rec["box"] = kid["box"].to_json()
        canary = trump_realizes(kid["hyp"], slots)
        rec["trump_realizes"] = canary
        t0 = time.time()
        if os.path.exists(node_path):
            res = json.load(open(node_path))
        else:
            log(f"[{time.strftime('%H:%M:%S')}] LP {kid['id']} budget={kid['budget']}")
            res = solve_node(S0F, kid["hyp"], kid["budget"], sym_kind="C1", warm=warm,
                             time_limit=a.time_limit, max_iter=1200, out=None, log=log,
                             prune=0, prune_cols=0, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                             max_cols_add=800, max_rows_add=2000, fine_slack=99.0, alternate=True)
            res["parent"] = a.name; res["child_id"] = kid["id"]
            json.dump(res, open(node_path, "w"))
        rec.update(tau=res["tau"], converged=res["converged"], minmass=res["minmass"],
                   maxcov=res["maxcov"], eta=res["tau"] - kid["budget"], lp_seconds=time.time() - t0)
        log(f"    tau={res['tau']:.6f} budget={kid['budget']} eta={rec['eta']:+.4f} conv={res['converged']}")
        if a.lp_only:
            rec["cert"] = "not attempted (--lp_only probe)"
            if kid["kind"] == "YES":
                rec["core_a"] = float(kid["box"].core().a)
        elif canary:
            rec["cert"] = "CANARY (Trump-realizable: never certified)"
        elif res["tau"] >= kid["budget"]:
            rec["cert"] = "impossible (tau >= budget)"
        else:
            cert_out = os.path.join(BASE, "certs", "tree", f"{kid['id']}.json")
            cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_path, "--s_rat", S_RAT,
                   "--rounds", str(a.rounds), "--jobs", str(a.jobs), "--depth", "56",
                   "--time_limit", str(a.time_limit), "--out", cert_out, "--scale", "0",
                   "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "64", "--loop_cols"]
            t1 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True)
            log(p.stdout[-4000:])
            rec["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
            rec["cert_seconds"] = time.time() - t1
            rec["cert_path"] = cert_out if p.returncode == 0 else None
        log("    " + json.dumps(rec))
        with open(summary, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
    print("substrat shard done", flush=True)


if __name__ == "__main__":
    main()
