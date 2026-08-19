"""
A13: LP-based branch-and-bound over the combinatorial structure of a hypothetical packing (I-L6 case-LP).

Node = hypothesis set H (core boxes + NO-families), budget = 11 - #cores.  Node LP (caselp.solve_node): tau < budget => DEAD.
Branch types at an ALIVE node:
  (Z) zone branch on a family F = zone x theta-set (from a fixed list of 9 zones partitioning the centre square, all theta):
        NO child: H + {NO square in F};  YES children: H + {core box B} for every non-vacuous box B of the initial split of F.
        At the root (H = {} , D4-symmetric) the corner family is branched symmetrically: NO child = no square in ANY corner
        zone (D4 LP), YES children = boxes of corner 0 only (WLOG by the D4 symmetry of the container).
  (R) refinement branch: replace one core box by its two halves (bisection of the widest dimension).
Heuristic: y(F) = fractional weight of the node's LP packing inside F; branch (Z) on the unused family with the largest
y(F) if that is >= zmin, else (R) on the core box whose neighbourhood carries the most fractional weight.
Best-first: pending nodes ordered by the parent's slack tau - budget (largest first).  All LP results are saved per node
(results/<tag>/node_<id>.json, warm starts for children); the tree is results/<tag>/tree.json (rewritten after every event).
"""
import argparse, json, math, os, sys, time, heapq, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")          # 8 workers x multithreaded BLAS oversubscribes the machine
import numpy as np
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caselp
from caselp import Box, NoFam, Hyp, solve_node, warm_from_result

HERE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ zones
def make_zones(s, cw=0.6):
    """9 zones partitioning the centre square [0.5, s-0.5]^2: 4 corners (cw x cw), 4 sides, 1 interior.
    Returns dict name -> (x0,x1,y0,y1)."""
    a, b = 0.5, s - 0.5
    c0, c1 = a + cw, b - cw
    Z = {
        "corner0": (a, c0, a, c0), "corner1": (c1, b, a, c0), "corner2": (c1, b, c1, b), "corner3": (a, c0, c1, b),
        "side0": (a, c0, c0, c1),      # left
        "side1": (c0, c1, a, c0),      # bottom
        "side2": (c1, b, c0, c1),      # right
        "side3": (c0, c1, c1, b),      # top
        "interior": (c0, c1, c0, c1),
    }
    return Z


def zone_family(name, rect):
    return NoFam(rect[0], rect[1], rect[2], rect[3], [(0.0, 90.0)])


def initial_boxes(rect, s, nx, ny, nth):
    x0, x1, y0, y1 = rect
    out = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nth):
                b = Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                        y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                        90.0 * k / nth, 90.0 * (k + 1) / nth)
                if not b.vacuous(s) and b.core() is not None:
                    out.append(b)
    return out


def box_in_zone(b, rect):
    return rect[0] - 1e-9 <= b.x0 and b.x1 <= rect[1] + 1e-9 and rect[2] - 1e-9 <= b.y0 and b.y1 <= rect[3] + 1e-9


def rect_weight(rect, packing):
    x0, x1, y0, y1 = rect
    return float(sum(w for (cx, cy, th, w) in packing if x0 <= cx <= x1 and y0 <= cy <= y1))


def boxes_compatible(b1, b2):
    """False if certainly no two DISJOINT unit squares can have centres in b1 and b2 (max centre distance < 1)."""
    dx = max(abs(b1.x0 - b2.x1), abs(b1.x1 - b2.x0)); dy = max(abs(b1.y0 - b2.y1), abs(b1.y1 - b2.y0))
    return math.hypot(dx, dy) >= 1.0 - 1e-9


# ------------------------------------------------------------------ worker
def _run_node(args):
    (nid, s, hyp_json, budget, sym, warm_path, out_path, time_limit, log_path) = args
    t0 = time.time()
    lines = []

    def log(*a):
        msg = " ".join(str(x) for x in a)
        lines.append(msg)
        with open(log_path, "a") as f:
            f.write(msg + "\n")
    try:
        hyp = Hyp.from_json(hyp_json)
        warm = None
        if warm_path and os.path.exists(warm_path):
            warm = warm_from_result(json.load(open(warm_path)))
        log(f"### node {nid} sym={sym} budget={budget} hyp: {hyp.describe()}")
        res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=time_limit, out=out_path, log=log)
        summ = dict(id=nid, tau=res["tau"], converged=res["converged"], minmass=res["minmass"], maxcov=res["maxcov"],
                    n_rows=res["n_rows"], n_atoms=len(res["atoms_all"]), lp_time=time.time() - t0,
                    packing=[list(p) for p in res["packing_images"] if p[3] > 1e-6], error=None)
        return summ
    except Exception as e:
        return dict(id=nid, error=traceback.format_exc(), lp_time=time.time() - t0)


# ------------------------------------------------------------------ driver
class BnB:
    def __init__(self, s, tag, workers=8, node_budget=300, time_limit=150, zmin=0.4, corner_split=(2, 2, 3),
                 side_split=(2, 3, 3), int_split=(3, 3, 3), root_warm=None, cw=0.6, dead_slack=0.03, refine_first=False):
        self.s, self.tag = s, tag
        self.workers, self.node_budget, self.time_limit = workers, node_budget, time_limit
        self.zmin, self.dead_slack = zmin, dead_slack
        self.splits = dict(corner=corner_split, side=side_split, interior=int_split)
        self.zones = make_zones(s, cw)
        self.dir = os.path.join(HERE, "results", tag)
        os.makedirs(self.dir, exist_ok=True)
        self.log_path = os.path.join(self.dir, "bnb.log")
        self.nodes = {}
        self.next_id = 0
        self.pending = []      # heap of (-priority, id)
        self.n_lp = 0
        self.root_warm = root_warm
        self.t0 = time.time()

    def log(self, *a):
        msg = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
        print(msg, flush=True)
        with open(self.log_path, "a") as f:
            f.write(msg + "\n")

    def new_node(self, hyp, parent, branch, prio, depth):
        nid = self.next_id; self.next_id += 1
        sym = "D4" if hyp.is_symmetric_D4(self.s) else "C1"
        rec = dict(id=nid, parent=parent, depth=depth, branch=branch, hyp=hyp.to_json(), budget=11 - hyp.m(), sym=sym,
                   status="pending", tau=None, prio=prio, children=[], hyp_str=hyp.describe())
        self.nodes[nid] = rec
        heapq.heappush(self.pending, (-prio, nid))
        return nid

    def save_tree(self):
        out = dict(s=self.s, tag=self.tag, n_lp=self.n_lp, elapsed=time.time() - self.t0, zones=self.zones,
                   params=dict(time_limit=self.time_limit, zmin=self.zmin, splits=self.splits, dead_slack=self.dead_slack),
                   nodes=[self.nodes[k] for k in sorted(self.nodes)])
        tmp = os.path.join(self.dir, "tree.json.tmp")
        with open(tmp, "w") as f:
            json.dump(out, f, indent=1)
        os.replace(tmp, os.path.join(self.dir, "tree.json"))

    # ---- branching
    def family_used(self, hyp, name, rect):
        for f in hyp.nofams:
            if abs(f.x0 - rect[0]) < 1e-9 and abs(f.x1 - rect[1]) < 1e-9 and abs(f.y0 - rect[2]) < 1e-9 and abs(f.y1 - rect[3]) < 1e-9:
                return True
        for b in hyp.boxes:
            if box_in_zone(b, rect):
                return True
        return False

    def branch(self, rec, packing):
        """create children of an alive node; returns list of child ids"""
        hyp = Hyp.from_json(rec["hyp"])
        s = self.s
        prio = rec["tau"] - rec["budget"]
        depth = rec["depth"] + 1
        kids = []
        # zone weights
        zw = {}
        for name, rect in self.zones.items():
            if not self.family_used(hyp, name, rect):
                zw[name] = rect_weight(rect, packing)
        rec["zone_weights"] = {n: round(w, 4) for n, w in zw.items()}
        # priority classes: corners first, then sides, then interior (Stromquist-style wall-first); within a class max weight
        best = (None, 0.0)
        for cls in ("corner", "side", "interior"):
            cand = [(n, w) for n, w in zw.items() if n.startswith(cls) and w >= self.zmin]
            if cand:
                best = max(cand, key=lambda kv: kv[1])
                break
        # root symmetric corner branch
        if rec["sym"] == "D4" and not hyp.boxes and best[0] is not None and best[0].startswith("corner") and best[1] >= self.zmin:
            # NO child: no square in any corner zone (D4-symmetric)
            nof = list(hyp.nofams) + [zone_family(n, self.zones[n]) for n in ("corner0", "corner1", "corner2", "corner3")]
            kids.append(self.new_node(Hyp(hyp.boxes, nof), rec["id"], "NO(all corners) [D4 WLOG]", prio, depth))
            rect = self.zones["corner0"]
            for b in initial_boxes(rect, s, *self.splits["corner"]):
                kids.append(self.new_node(Hyp(list(hyp.boxes) + [b], hyp.nofams), rec["id"], f"YES corner0 {b!r} [WLOG]", prio, depth))
            rec["branch_on"] = "corners (symmetric)"
        elif best[0] is not None and best[1] >= self.zmin:
            name, rect = best[0], self.zones[best[0]]
            kind = "corner" if name.startswith("corner") else ("side" if name.startswith("side") else "interior")
            nof = list(hyp.nofams) + [zone_family(name, rect)]
            kids.append(self.new_node(Hyp(hyp.boxes, nof), rec["id"], f"NO {name}", prio, depth))
            for b in initial_boxes(rect, s, *self.splits[kind]):
                if all(boxes_compatible(b, b2) for b2 in hyp.boxes):
                    kids.append(self.new_node(Hyp(list(hyp.boxes) + [b], hyp.nofams), rec["id"], f"YES {name} {b!r}", prio, depth))
            rec["branch_on"] = name
        elif hyp.boxes:
            # refinement: the box whose neighbourhood carries the most fractional weight, ties -> largest box
            def nb_weight(b):
                kx, ky = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
                return sum(w for (cx, cy, th, w) in packing if math.hypot(cx - kx, cy - ky) < 1.15)
            scores = [(nb_weight(b), (b.x1 - b.x0) + (b.y1 - b.y0) + (b.th1 - b.th0) / 60, i) for i, b in enumerate(hyp.boxes)]
            _, _, i = max(scores)
            b = hyp.boxes[i]
            for h in b.split():
                if h.vacuous(s) or h.core() is None:
                    continue
                if not all(boxes_compatible(h, b2) for j, b2 in enumerate(hyp.boxes) if j != i):
                    continue
                boxes = list(hyp.boxes); boxes[i] = h
                kids.append(self.new_node(Hyp(boxes, hyp.nofams), rec["id"], f"REFINE box{i} -> {h!r}", prio, depth))
            rec["branch_on"] = f"refine box{i}"
        else:
            rec["branch_on"] = "none (no family with weight >= zmin and no boxes)"
        rec["children"] = kids
        return kids

    # ---- main loop
    def run(self):
        s = self.s
        root = self.new_node(Hyp(), None, "root", 99.0, 0)
        self.log(f"start s={s} tag={self.tag} workers={self.workers} node_budget={self.node_budget} time_limit={self.time_limit}")
        pool = mp.Pool(self.workers)
        running = {}    # nid -> AsyncResult
        launched = 0
        try:
            while True:
                # launch
                while self.pending and len(running) < self.workers and launched < self.node_budget:
                    _, nid = heapq.heappop(self.pending)
                    rec = self.nodes[nid]
                    rec["status"] = "running"
                    par = rec["parent"]
                    if par is None:
                        warm = self.root_warm
                    else:
                        warm = os.path.join(self.dir, f"node_{par}.json")
                    out = os.path.join(self.dir, f"node_{nid}.json")
                    args = (nid, s, rec["hyp"], rec["budget"], rec["sym"], warm, out, self.time_limit,
                            os.path.join(self.dir, f"node_{nid}.log"))
                    running[nid] = pool.apply_async(_run_node, (args,))
                    launched += 1
                    self.log(f"launch node {nid} (depth {rec['depth']}, {rec['sym']}, budget {rec['budget']}, prio {rec['prio']:.3f}): {rec['branch']}")
                if not running:
                    break
                # collect
                done = [nid for nid, ar in running.items() if ar.ready()]
                if not done:
                    time.sleep(2.0)
                    continue
                for nid in done:
                    summ = running.pop(nid).get()
                    rec = self.nodes[nid]
                    self.n_lp += 1
                    if summ.get("error"):
                        rec["status"] = "error"; rec["error"] = summ["error"]
                        self.log(f"node {nid} ERROR: {summ['error'][-500:]}")
                        continue
                    rec.update(tau=summ["tau"], converged=summ["converged"], minmass=summ["minmass"], maxcov=summ["maxcov"],
                               n_rows=summ["n_rows"], n_atoms=summ["n_atoms"], lp_time=summ["lp_time"])
                    slack = summ["tau"] - rec["budget"]
                    packing = summ["packing"]
                    rec["packing_support"] = len(packing)
                    rec["heavy"] = sorted([[round(p[0], 3), round(p[1], 3), round(math.degrees(p[2]) % 90, 2), round(p[3], 4)] for p in packing],
                                          key=lambda p: -p[3])[:12]
                    if summ["converged"] and slack < -1e-6:
                        rec["status"] = "dead"
                    elif slack < -self.dead_slack and summ["minmass"] >= 0.97:
                        rec["status"] = "dead?"
                    elif slack < -1e-6:
                        rec["status"] = "dead??"     # tau below budget but LP not converged: treat as alive-ish? -> branch anyway? no: re-run later
                    else:
                        rec["status"] = "alive"
                    self.log(f"node {nid} done: tau={summ['tau']:.4f} budget={rec['budget']} slack={slack:+.4f} conv={summ['converged']} "
                             f"minmass={summ['minmass']:.3f} maxcov={summ['maxcov']:.3f} rows={summ['n_rows']} t={summ['lp_time']:.0f}s -> {rec['status']}")
                    if rec["status"] in ("alive", "dead??"):
                        kids = self.branch(rec, packing)
                        self.log(f"   branch {rec.get('branch_on')} zone_w={rec.get('zone_weights')} -> {len(kids)} children")
                    self.save_tree()
                if launched >= self.node_budget and not running:
                    break
        finally:
            pool.terminate()
            self.save_tree()
        self.report()

    def report(self):
        st = {}
        for r in self.nodes.values():
            st[r["status"]] = st.get(r["status"], 0) + 1
        self.log(f"FINISHED: {self.n_lp} LPs, elapsed {time.time()-self.t0:.0f}s, status counts {st}")
        by_depth = {}
        for r in self.nodes.values():
            d = by_depth.setdefault(r["depth"], {})
            d[r["status"]] = d.get(r["status"], 0) + 1
        for d in sorted(by_depth):
            self.log(f"  depth {d}: {by_depth[d]}")
        alive = [r for r in self.nodes.values() if r["status"] in ("alive", "pending", "dead??")]
        if alive:
            self.log(f"  frontier: {len(alive)} nodes; slack of solved alive nodes: " +
                     ", ".join(f"{r['id']}:{r['tau']-r['budget']:+.3f}" for r in alive if r.get("tau") is not None))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--node_budget", type=int, default=300)
    ap.add_argument("--time_limit", type=float, default=150)
    ap.add_argument("--zmin", type=float, default=0.4)
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--corner_split", default="2,2,3")
    ap.add_argument("--side_split", default="2,3,3")
    ap.add_argument("--int_split", default="3,3,3")
    ap.add_argument("--root_warm", default=None)
    ap.add_argument("--dead_slack", type=float, default=0.03)
    a = ap.parse_args()
    B = BnB(a.s, a.tag, workers=a.workers, node_budget=a.node_budget, time_limit=a.time_limit, zmin=a.zmin,
            corner_split=tuple(int(x) for x in a.corner_split.split(",")), side_split=tuple(int(x) for x in a.side_split.split(",")),
            int_split=tuple(int(x) for x in a.int_split.split(",")), root_warm=a.root_warm, cw=a.cw, dead_slack=a.dead_slack)
    B.run()
