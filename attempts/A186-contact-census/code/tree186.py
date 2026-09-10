"""A186 step 3 (certificate side) -- Theorem LOCAL's selection tree (A116 `Tree`, READ-ONLY) on a boxed
assignment whose free bodies carry PIECES (nodes186.PieceBody): at every tree node the centre box of a
free body is the hull of its pieces meeting the node's tilt cell, so bisecting the tilt cell tightens
the centre boxes for free.  The frame is A57's: s the LP variable in [s0, s0 + 0.05] (s_lo = s0: the
node's pieces are a hypothesis on the dilate at s0, so the relaxation to s >= s0 is exact at s0 and the
value v > s0 is "this leaf needs side v"); pins on their slot lines.

Verdict per assignment: DEAD (every leaf closed with v > s0 -- the contact-census kill of Theorem CC
in the LP form), WITNESS (an exact-tilt LP point that check_packing accepts at side <= s0: a packing of
the boxed squares inside the boxes), or CAPPED/UNRESOLVED [P] with the certified minimum over the closed
leaves and the best open leaf.

    python tree186.py [--budget0] [--only k] [--nodes 20000] [--time 240] [--mincell 0.5]
    -> results/tree186.jsonl (one row per run, appended)
"""
from __future__ import annotations
import argparse, itertools, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodes186 as N                                          # noqa: E402
A, IV, S0 = N.A, N.IV, N.S0

_build_lp0 = A.build_lp


def build_lp_pieces(bodies, nv, s_lo, s_hi, fixed, cells=None, exact_theta=None, qranges=None):
    """A116's build_lp on the bodies SPECIALISED to the tilt cell (hull of the pieces meeting it)."""
    if cells:
        sp = []
        for b in bodies:
            if isinstance(b, N.PieceBody):
                b2 = b.specialise(cells)
                if b2 is None:                       # no piece meets the cell: an empty LP
                    b2 = A.Body(b.name, "free", x0=1.0, x1=0.0, y0=1.0, y1=0.0, t0=cells[b.name][0],
                                t1=cells[b.name][1], vi=b.vi, ti=b.ti, anchor=b.anchor)
                sp.append(b2)
            else:
                sp.append(b)
        bodies = sp
    return _build_lp0(bodies, nv, s_lo, s_hi, fixed, cells=cells, exact_theta=exact_theta, qranges=qranges)


A.build_lp = build_lp_pieces


class PieceTree(A.Tree):
    """A116's Tree with (i) a seeded root stack (cells <= max_root_deg wide: Rows' relaxation needs
    half-width <= 60 deg), (ii) 'no piece meets the cell' as IMPOSSIBLE."""

    def __init__(self, bodies, nv, max_root_deg=45.0, **kw):
        super().__init__(bodies, nv, **kw)
        self.max_root = math.radians(max_root_deg)

    def _census(self, cells):
        for b in self.free:
            if isinstance(b, N.PieceBody) and b.box_for(cells[b.name]) is None:
                return {}, [], [("empty", b.name)]
        return super()._census(cells)

    def root_stack(self):
        per = []
        for b in self.free:
            n = max(1, int(math.ceil((b.t1 - b.t0) / self.max_root - 1e-12)))
            per.append([(b.name, (b.t0 + k * (b.t1 - b.t0) / n, b.t0 + (k + 1) * (b.t1 - b.t0) / n))
                        for k in range(n)])
        stack = []
        for combo in itertools.product(*per):
            stack.append((dict(combo), {}, {}))
        return stack

    def run(self):
        self.reset()
        cells = self.root_cells()
        near, far, imp = A.census(self.bodies, self.s_lo, self.s_hi, cells)   # hull-level, for the record
        self.near_root = dict(near=near, far=far, impossible=imp)
        stack = self.root_stack()
        self.n_root = len(stack)
        self._loop(list(reversed(stack)), tightening=False)
        return self.verdict()


def best_open(T):
    """the lowest relaxed value among the unresolved / witness leaves (the best open leaf)."""
    cands = [(r["value_relaxed"], r) for r in T.unresolved] + [(r["value_relaxed"], r) for r in T.witnesses]
    if not cands:
        return None
    v, r = min(cands, key=lambda t: t[0])
    return r


def run_one(rec, node_cap, time_cap, min_cell_deg, s_hi_extra=0.05, log=print):
    bodies, nv = N.build_bodies(rec)
    T = PieceTree(bodies, nv, s_lo=S0, s_hi=S0 + s_hi_extra, min_cell_deg=min_cell_deg, node_cap=node_cap,
                  time_cap=time_cap, exact_check_deg=2.0)
    v = T.run()
    st = v["stats"]
    lowest = sorted([c for c in T.closed if c["alive"]], key=lambda c: c["value"])[:40]
    leaves = [dict(value=c["value"], cells=T._cells_deg(c["state"][0]), fixed=T._fixed_named(c["state"][1]),
                   qranges={"%s|%s" % (T.bodies[i].name, T.bodies[j].name): list(rg) for (i, j), rg in c["state"][2].items()},
                   nunfixed=c.get("nunfixed"), support=c.get("support")) for c in lowest]
    row = dict(label=rec["label"], short=N.short_label(rec["label"]), budget=11 - len(rec["roles"]), lowest_leaves=leaves,
               n_root=T.n_root, verdict=("DEAD" if v["dead"] else ("WITNESS" if any(w.get("witness_valid") for w in T.witnesses)
                                                                     else ("CAPPED" if v["capped"] else "UNRESOLVED"))),
               tree=v, n_witnesses=len(T.witnesses), n_unresolved=len(T.unresolved),
               witnesses=[w for w in T.witnesses if w.get("witness_valid")][:3],
               best_open=best_open(T), node_cap=node_cap, time_cap=time_cap, min_cell_deg=min_cell_deg,
               when=time.strftime("%Y-%m-%d %H:%M:%S"))
    log("%s: %s  roots %d  near %d  leaves(int) %.3g  nodes %d  lp %d  closed %d  imp %d  branch %d  bisect %d  "
        "live_low %d  unres %d  certmin %s  (%.0fs)" %
        (row["short"], row["verdict"], T.n_root, v["n_near"], v["leaves_after_interval"], st["nodes"], st["lp_calls"],
         v["n_closed"], st["impossible"], st["branch"], st["bisect"], st["live_low"], st["unresolved"],
         ("%.6f" % v["certified_min"]) if v["certified_min"] else "-", v["seconds"]))
    if row["best_open"]:
        bo = row["best_open"]
        log("   best open leaf: relaxed %.6f exact %s width %.3f deg fixed %d" %
            (bo["value_relaxed"], bo.get("value_exact_best"), bo["width_deg"], bo["nfixed"]))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget0", action="store_true")
    ap.add_argument("--only", type=int, default=None, help="index in the sorted assignment list")
    ap.add_argument("--nodes", type=int, default=20000)
    ap.add_argument("--time", type=float, default=240.0)
    ap.add_argument("--mincell", type=float, default=0.5)
    ap.add_argument("--distinct", action="store_true", help="skip assignments whose pieces equal an earlier one")
    args = ap.parse_args()
    recs = N.load_records()
    items = sorted(recs.items(), key=lambda kv: (-len(kv[1]["roles"]), kv[0]))
    seen = set()
    out = open(os.path.join(N.RES, "tree186.jsonl"), "a", encoding="utf-8")
    for k, (lab, r) in enumerate(items):
        if args.budget0 and len(r["roles"]) < 11:
            continue
        if args.only is not None and k != args.only:
            continue
        key = json.dumps({n: r["capture"][n]["pieces"] for n in r["roles"]}, sort_keys=True)
        if args.distinct and key in seen:
            print("%s: same pieces as an earlier assignment, skipped" % N.short_label(lab))
            continue
        seen.add(key)
        row = run_one(r, args.nodes, args.time, args.mincell)
        row["index"] = k
        out.write(json.dumps(row) + "\n"); out.flush()


if __name__ == "__main__":
    main()
