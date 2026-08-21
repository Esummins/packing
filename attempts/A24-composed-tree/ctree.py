#!/usr/bin/env python3
"""
A24 ctree.py -- COMPOSED case tree: every node is attacked by TWO independent
kill tests.

  (T1) coverage LP  (A14 caselp.solve_node):  tau_H < 11 - m   =>  node dead
  (T2) wastage ledger (A23 budget lemma via kill_tests.wastage_test):
       sum of certified interior-disjoint dead areas > s^2 - 11  =>  node dead

BRANCHING (the scientific choice; A14 showed the wall-first tree is barren).
T2 strands ~0 on corner/flush-wall squares and 0.68-0.92 on ONE interior mid-tilt
square at 3.84 (A24 sweep), growing super-additively with the number of interior
mid-tilt cores.  So the tree branches INTERIOR-FIRST and on the MID-TILT
orientation window Theta_mid = [15,75] deg:

  family F(Z) = "some square has centre in zone Z and orientation in [15,75]"
  NO child : H + NoFam(Z, [15,75])          -- drops rows => T1 gets stronger
  YES kids : H + Box(sub-box of Z x [15,75]) -- fixes a core => T2 gets stronger,
                                                budget drops by 1
The dichotomy is exhaustive because the YES boxes are a closed cover of
Z x [15,75] (checked exactly by verify_casetree.py in rationals).

Zone order: interior first, then sides, then corners (reverse of A13/A14).
Within the interior the sub-box with the largest fractional mid-tilt mass in the
parent's LP dual is branched first (best-first by parent slack).
"""
from __future__ import annotations

import argparse, heapq, json, math, os, sys, time, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import multiprocessing as mp
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpbox
import caselp
from caselp import Box, NoFam, Hyp, solve_node, warm_from_result
from kill_tests import wastage_test, budget_rat, check_disjoint, hyp_to_cert_data

TH_MID = (15.0, 75.0)


def make_zones(s, cw=0.6):
    a, b = 0.5, s - 0.5
    c0, c1 = a + cw, b - cw
    return {"interior": (c0, c1, c0, c1),
            "side0": (a, c0, c0, c1), "side1": (c0, c1, a, c0),
            "side2": (c1, b, c0, c1), "side3": (c0, c1, c1, b),
            "corner0": (a, c0, a, c0), "corner1": (c1, b, a, c0),
            "corner2": (c1, b, c1, b), "corner3": (a, c0, c1, b)}


ZONE_ORDER = ["interior", "side0", "side1", "side2", "side3",
              "corner0", "corner1", "corner2", "corner3"]


def cover_boxes(rect, s, nx, ny, th0, th1, nth):
    out = []
    x0, x1, y0, y1 = rect
    for i in range(nx):
        for j in range(ny):
            for k in range(nth):
                b = Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                        y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                        th0 + (th1 - th0) * k / nth, th0 + (th1 - th0) * (k + 1) / nth)
                if not b.vacuous(s) and b.core() is not None:
                    out.append(b)
    return out


def boxes_compatible(b1, b2):
    dx = max(abs(b1.x0 - b2.x1), abs(b1.x1 - b2.x0))
    dy = max(abs(b1.y0 - b2.y1), abs(b1.y1 - b2.y0))
    return math.hypot(dx, dy) >= 1.0 - 1e-9


def mass_in(rect, thr, packing):
    x0, x1, y0, y1 = rect
    t = 0.0
    for (cx, cy, th, w) in packing:
        d = math.degrees(th) % 90.0
        if x0 <= cx <= x1 and y0 <= cy <= y1 and thr[0] <= d <= thr[1]:
            t += w
    return t


def midtilt_cores(hyp):
    """cores whose orientation window meets [15,75] (the ones T2 can use)."""
    return [b for b in hyp.boxes if b.th1 >= TH_MID[0] and b.th0 <= TH_MID[1]]


# ------------------------------------------------------------------ worker
def _work(args):
    (nid, s, hyp_json, budget, sym, warm_path, out_path, tl, eps_geo,
     t2_min_cores, t2_min_cell, t2_cell0, t2_max_boxes) = args
    t_start = time.time()
    rec = dict(id=nid)
    try:
        if eps_geo is not None:
            lpbox.EPS_GEO = eps_geo
        hyp = Hyp.from_json(hyp_json)
        # ---------------- T2 (wastage ledger) -- cheap, run first
        t2 = None
        mt = midtilt_cores(hyp)
        if len(mt) >= t2_min_cores:
            tt = time.time()
            r = wastage_test(F(s).limit_denominator(10 ** 6), hyp=hyp,
                             min_cell=F(1, t2_min_cell), cell0=F(t2_cell0, 100),
                             mode='float', depth_max=24,
                             max_boxes_per_cell=t2_max_boxes, verbose=False)
            dj, _ = check_disjoint(r['cells'])
            t2 = dict(area=r['area_float'], area_rat=r['area'], budget=r['budget_float'],
                      dead=bool(r['dead_node'] and dj), frac=r['fraction_of_budget'],
                      n_cells=len(r['cells']), disjoint=dj, seconds=time.time() - tt)
            json.dump(r, open(out_path.replace('.json', '_t2.json'), 'w'), indent=1)
        rec['t2'] = t2
        if t2 and t2['dead']:
            rec['status'] = 'dead(T2)'
            rec['seconds'] = time.time() - t_start
            return rec
        # ---------------- T1 (coverage LP)
        warm = None
        if warm_path and os.path.exists(warm_path):
            warm = warm_from_result(json.load(open(warm_path)))
        lp = out_path.replace('.json', '.log')

        def log(*a):
            with open(lp, 'a') as f:
                f.write(" ".join(str(x) for x in a) + "\n")
        log(f"### node {nid} sym={sym} budget={budget} hyp: {hyp.describe()}")
        res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=tl, out=out_path,
                         log=log, max_rows_add=1200, max_cols_add=1200, col_stop_iter=10 ** 6,
                         col_stop_cov=1.01, checkpoint=out_path.replace('.json', '_state.json'),
                         prune=6, prune_cols=2, alternate=True)
        rec.update(tau=res['tau'], converged=res['converged'], minmass=res['minmass'],
                   maxcov=res['maxcov'], n_rows=res['n_rows'],
                   packing=[list(p) for p in res['packing_images'] if p[3] > 1e-6])
        rec['seconds'] = time.time() - t_start
        return rec
    except Exception:
        rec['error'] = traceback.format_exc()[-1500:]
        rec['seconds'] = time.time() - t_start
        return rec


# ------------------------------------------------------------------ driver
class CTree:
    def __init__(self, s, tag, workers=6, node_budget=100, time_limit=300, eps_geo=1e-4,
                 zmin=0.25, dead_slack=0.03, int_split=(4, 4, 2), side_split=(2, 3, 2),
                 corner_split=(2, 2, 2), t2_min_cores=2, t2_min_cell=16, t2_cell0=20,
                 t2_max_boxes=1200, root_warm=None, max_depth=6):
        self.s, self.tag = s, tag
        self.workers, self.node_budget, self.time_limit = workers, node_budget, time_limit
        self.eps_geo, self.zmin, self.dead_slack = eps_geo, zmin, dead_slack
        self.splits = dict(interior=int_split, side=side_split, corner=corner_split)
        self.zones = make_zones(s)
        self.t2 = (t2_min_cores, t2_min_cell, t2_cell0, t2_max_boxes)
        self.max_depth = max_depth
        self.dir = os.path.join(HERE, 'results', tag)
        os.makedirs(self.dir, exist_ok=True)
        self.nodes, self.next_id, self.pending = {}, 0, []
        self.n_solved = 0
        self.root_warm = root_warm
        self.t0 = time.time()
        self.logp = os.path.join(self.dir, 'ctree.log')

    def log(self, *a):
        m = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a)
        print(m, flush=True)
        with open(self.logp, 'a') as f:
            f.write(m + '\n')

    def new_node(self, hyp, parent, branch, prio, depth):
        nid = self.next_id
        self.next_id += 1
        sym = 'D4' if hyp.is_symmetric_D4(self.s) else 'C1'
        self.nodes[nid] = dict(id=nid, parent=parent, depth=depth, branch=branch,
                               hyp=hyp.to_json(), budget=11 - hyp.m(), sym=sym,
                               status='pending', prio=prio, children=[],
                               hyp_str=hyp.describe())
        heapq.heappush(self.pending, (-prio, nid))
        return nid

    def save(self):
        out = dict(s=self.s, tag=self.tag, n_solved=self.n_solved,
                   elapsed=time.time() - self.t0, zones=self.zones,
                   budget_area=str(budget_rat(F(self.s).limit_denominator(10 ** 6))),
                   params=dict(time_limit=self.time_limit, eps_geo=self.eps_geo,
                               zmin=self.zmin, splits=self.splits, t2=self.t2,
                               th_mid=TH_MID, max_depth=self.max_depth),
                   nodes=[self.nodes[k] for k in sorted(self.nodes)])
        tmp = os.path.join(self.dir, 'tree.json.tmp')
        json.dump(out, open(tmp, 'w'), indent=1)
        os.replace(tmp, os.path.join(self.dir, 'tree.json'))

    # ---- branching: interior-first, mid-tilt window
    def family_used(self, hyp, rect, thr):
        for f in hyp.nofams:
            if (abs(f.x0 - rect[0]) < 1e-9 and abs(f.x1 - rect[1]) < 1e-9 and
                    abs(f.y0 - rect[2]) < 1e-9 and abs(f.y1 - rect[3]) < 1e-9 and
                    any(abs(a - thr[0]) < 1e-9 and abs(b - thr[1]) < 1e-9 for a, b in f.thetas)):
                return True
        for b in hyp.boxes:
            if (rect[0] - 1e-9 <= b.x0 and b.x1 <= rect[1] + 1e-9 and
                    rect[2] - 1e-9 <= b.y0 and b.y1 <= rect[3] + 1e-9 and
                    thr[0] - 1e-9 <= b.th0 and b.th1 <= thr[1] + 1e-9):
                return True
        return False

    def branch(self, rec, packing):
        hyp = Hyp.from_json(rec['hyp'])
        prio, depth = rec['tau'] - rec['budget'], rec['depth'] + 1
        kids = []
        if depth > self.max_depth:
            rec['branch_on'] = 'none (max depth)'
            return kids
        cand = []
        for name in ZONE_ORDER:
            rect = self.zones[name]
            for thr in (TH_MID, (0.0, 90.0)):
                if self.family_used(hyp, rect, thr):
                    continue
                cand.append((name, rect, thr, mass_in(rect, thr, packing)))
                break
        rec['zone_mass'] = {c[0]: round(c[3], 3) for c in cand}
        # interior-first: take the first zone in ZONE_ORDER whose mass >= zmin
        pick = None
        for (name, rect, thr, w) in cand:
            if w >= self.zmin:
                pick = (name, rect, thr, w)
                break
        if pick is None and cand:
            pick = max(cand, key=lambda c: c[3])
        if pick is None:
            rec['branch_on'] = 'none (all families used)'
            return kids
        name, rect, thr, w = pick
        kind = 'interior' if name == 'interior' else ('side' if name.startswith('side') else 'corner')
        nof = list(hyp.nofams) + [NoFam(rect[0], rect[1], rect[2], rect[3], [thr])]
        kids.append(self.new_node(Hyp(hyp.boxes, nof), rec['id'],
                                  f"NO {name} theta{thr}", prio, depth))
        nx, ny, nth = self.splits[kind]
        for b in cover_boxes(rect, self.s, nx, ny, thr[0], thr[1], nth):
            if all(boxes_compatible(b, b2) for b2 in hyp.boxes):
                kids.append(self.new_node(Hyp(list(hyp.boxes) + [b], hyp.nofams),
                                          rec['id'], f"YES {name} {b!r}", prio, depth))
        rec['branch_on'] = f"{name} x {thr}"
        rec['children'] = kids
        return kids

    def run(self):
        self.new_node(Hyp(), None, 'root', 99.0, 0)
        self.log(f"start s={self.s} tag={self.tag} workers={self.workers} "
                 f"node_budget={self.node_budget} tl={self.time_limit} "
                 f"area_budget={float(budget_rat(F(self.s).limit_denominator(10**6))):.4f}")
        pool = mp.Pool(self.workers)
        running, launched = {}, 0
        try:
            while True:
                while self.pending and len(running) < self.workers and launched < self.node_budget:
                    _, nid = heapq.heappop(self.pending)
                    rec = self.nodes[nid]
                    rec['status'] = 'running'
                    par = rec['parent']
                    warm = self.root_warm if par is None else os.path.join(self.dir, f'node_{par}.json')
                    out = os.path.join(self.dir, f'node_{nid}.json')
                    running[nid] = pool.apply_async(_work, ((nid, self.s, rec['hyp'], rec['budget'],
                                                            rec['sym'], warm, out, self.time_limit,
                                                            self.eps_geo) + self.t2,))
                    launched += 1
                    self.log(f"launch {nid} d{rec['depth']} {rec['sym']} bud{rec['budget']} "
                             f"prio{rec['prio']:+.3f}: {rec['branch']}")
                if not running:
                    break
                done = [n for n, ar in running.items() if ar.ready()]
                if not done:
                    time.sleep(2.0)
                    continue
                for nid in done:
                    r = running.pop(nid).get()
                    rec = self.nodes[nid]
                    self.n_solved += 1
                    if r.get('error'):
                        rec['status'] = 'error'
                        rec['error'] = r['error']
                        self.log(f"node {nid} ERROR {r['error'][-300:]}")
                        continue
                    rec['t2'] = r.get('t2')
                    rec['seconds'] = r['seconds']
                    if r.get('status') == 'dead(T2)':
                        rec['status'] = 'dead(T2)'
                        self.log(f"node {nid} DEAD by T2: area={r['t2']['area']:.4f} > "
                                 f"{r['t2']['budget']:.4f} ({r['t2']['n_cells']} cells)")
                        self.save()
                        continue
                    rec.update(tau=r['tau'], converged=r['converged'], minmass=r['minmass'],
                               maxcov=r['maxcov'], n_rows=r['n_rows'])
                    slack = r['tau'] - rec['budget']
                    pk = r['packing']
                    rec['heavy'] = sorted([[round(p[0], 3), round(p[1], 3),
                                            round(math.degrees(p[2]) % 90, 2), round(p[3], 4)]
                                           for p in pk], key=lambda z: -z[3])[:10]
                    if r['converged'] and slack < -1e-6:
                        rec['status'] = 'dead(T1)'
                    elif slack < -self.dead_slack and r['minmass'] >= 0.97:
                        rec['status'] = 'dead?(T1)'
                    else:
                        rec['status'] = 'alive'
                    t2s = (f" T2={r['t2']['area']:.3f}/{r['t2']['budget']:.3f}"
                           if r.get('t2') else " T2=-")
                    self.log(f"node {nid} tau={r['tau']:.4f} bud={rec['budget']} "
                             f"slack={slack:+.4f} conv={r['converged']} mm={r['minmass']:.3f}"
                             f"{t2s} t={r['seconds']:.0f}s -> {rec['status']}")
                    if rec['status'] in ('alive', 'dead?(T1)'):
                        if rec['status'] == 'alive':
                            kids = self.branch(rec, pk)
                            self.log(f"   branch {rec.get('branch_on')} mass={rec.get('zone_mass')}"
                                     f" -> {len(kids)} children")
                    self.save()
                if launched >= self.node_budget and not running:
                    break
        finally:
            pool.terminate()
            self.save()
        self.report()

    def report(self):
        st = {}
        for r in self.nodes.values():
            st[r['status']] = st.get(r['status'], 0) + 1
        self.log(f"FINISHED {self.n_solved} nodes solved, {time.time()-self.t0:.0f}s, {st}")
        bd = {}
        for r in self.nodes.values():
            bd.setdefault(r['depth'], {})
            bd[r['depth']][r['status']] = bd[r['depth']].get(r['status'], 0) + 1
        for d in sorted(bd):
            self.log(f"  depth {d}: {bd[d]}")
        t2max = max([r['t2']['area'] for r in self.nodes.values()
                     if r.get('t2')] or [0.0])
        self.log(f"  max T2 dead area reached: {t2max:.4f} "
                 f"(budget {float(budget_rat(F(self.s).limit_denominator(10**6))):.4f})")
        alive = [r for r in self.nodes.values() if r['status'] in ('alive', 'pending', 'running')]
        self.log(f"  frontier: {len(alive)} nodes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', type=float, default=3.84)
    ap.add_argument('--tag', default='t384')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--node_budget', type=int, default=100)
    ap.add_argument('--time_limit', type=float, default=300)
    ap.add_argument('--eps_geo', type=float, default=1e-4)
    ap.add_argument('--zmin', type=float, default=0.25)
    ap.add_argument('--max_depth', type=int, default=6)
    ap.add_argument('--t2_min_cell', type=int, default=16)
    ap.add_argument('--t2_min_cores', type=int, default=2)
    ap.add_argument('--root_warm', default=os.path.join(os.path.dirname(HERE),
                                                        'A13-case-lp-bnb', 'results', 't384c', 'node_0.json'))
    a = ap.parse_args()
    CTree(a.s, a.tag, workers=a.workers, node_budget=a.node_budget, time_limit=a.time_limit,
          eps_geo=a.eps_geo, zmin=a.zmin, max_depth=a.max_depth, t2_min_cell=a.t2_min_cell,
          t2_min_cores=a.t2_min_cores, root_warm=a.root_warm).run()


if __name__ == '__main__':
    main()
