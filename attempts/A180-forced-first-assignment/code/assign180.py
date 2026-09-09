"""A180 -- the forced-first ASSIGNMENT search on a gallery page (notes/assignment.md).

A node of the search = (roles, assignment).  roles = pins + H + the instantiated free squares F_k,
each a multibox role (centre rect x tilt bin, normalised with A171's library); assignment = for each
forced cell of the class (forced_corners.md Theorem FC) the <= 2 distinct roles that MEET its widened
box.  A cell with two meeters is CLOSED.  For an open cell the CANDIDATES are the existing non-pin
roles that can still meet it (exact miss test + a restricted node) and "new" (a free square not yet
instantiated, while #F < 5).  The cell's OPTIONS are the admissible completions; ONE option = FORCED
(applied at once); NO option = the node is dead (leaf "no admissible meeter"); otherwise the search
branches on the cell with the fewest options, two-new options LAST.  Soundness: notes/assignment.md.
"""
import itertools
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))
import geo178 as G                                              # noqa: E402  READ-ONLY (A178)
import geo178b as GB                                            # noqa: E402  READ-ONLY (A178)
import classes178 as CL                                         # noqa: E402  READ-ONLY (A178)

SQ2 = 2 ** 0.5
MAXF = 5


def restrict(box, W):
    x0, x1 = max(box[0], W[0]), min(box[1], W[1])
    y0, y1 = max(box[2], W[2]), min(box[3], W[3])
    if x0 > x1 + 1e-12 or y0 > y1 + 1e-12:
        return None
    return (x0, min(x1, max(x0, x1)), y0, max(y0, y1), box[4], box[5])


class Budget(Exception):
    pass


class Search:
    def __init__(self, rec, cls, nsub=4, refine=2, log=print, max_nodes=200, deadline=None, leaf=None,
                 max_cells=6, max_pairs=40, refine_opts=1, side=0.36, max_combos=100):
        self.rec, self.cls = rec, cls
        self.refine_opts, self.side, self.max_combos = refine_opts, side, max_combos
        self.nsub, self.refine, self.log = nsub, refine, log
        self.max_nodes, self.deadline, self.leaf_fn = max_nodes, deadline, leaf
        self.max_cells, self.max_pairs = max_cells, max_pairs
        self.t0 = time.time()
        self.n_nodes = 0
        self.steps = []
        base = G.base_roles(rec)
        self.pins = {k: v for k, v in base.items() if k.startswith("P")}
        self.hnames = [k for k in base if k.startswith("H")]
        self.items = {it["cell"]: it for it in G.forced_items(cls, rec)}
        self.root = dict(roles=dict(base), corners={}, assign={c: [] for c in self.items}, fcells={}, nF=0,
                         label="root", hist=[])

    # ------------------------------------------------------------------ one multibox node
    def node(self, roles, corners, label, kind, **extra):
        if self.n_nodes >= self.max_nodes or (self.deadline and time.time() - self.t0 > self.deadline):
            raise Budget("node budget exhausted (%d nodes, %.0f s)" % (self.n_nodes, time.time() - self.t0))
        self.n_nodes += 1
        nd, info = G.run_node(roles, corners=corners or None, nsub=self.nsub, refine=self.refine, label=label)
        rec = dict(i=self.n_nodes, label=label, kind=kind, roles=list(roles), corners=dict(corners or {}),
                   dead=info.get("dead"), seconds=info.get("seconds"), passes=info.get("passes"),
                   invariant=info.get("invariant"), kept={k: v for k, v in (info.get("kept") or {}).items()
                                                          if not k.startswith("P")},
                   hull=info.get("hull"), **extra)
        self.steps.append(rec)
        return nd, info, rec

    # ------------------------------------------------------------------ geometry helpers
    def can_reach(self, st, r, cell):
        """cheap necessary tests: the sqrt2 rule against r's assigned cells, and A161's exact miss
        test of r's current box against the widened box."""
        it = self.items[cell]
        for q in st["fcells"].get(r, []):
            if CL.box_dist(self.items[q]["wbox"], it["wbox"]) >= SQ2:
                return False, "sqrt2 rule vs %s" % q
        if st.get("nd") is not None and r in st["nd"].boxes:
            m = st["nd"].misses_cell(tuple(it["wbox"]))
            if m.get(r, {}).get("misses"):
                return False, "exact miss test"
        return True, None

    def _roles_with(self, st, members, cell, newnames=None):
        """roles/corners of st with each member restricted to the cell's window ('new' = a fresh F)."""
        it = self.items[cell]
        W = it["window"]
        roles, corners = dict(st["roles"]), dict(st["corners"])
        names, k = [], st["nF"]
        for m in members:
            if m == "new":
                k += 1
                nm = "F%d" % k
                roles[nm] = (W[0], W[1], W[2], W[3], 0.0, 90.0)
            else:
                nm = m
                r = restrict(roles[nm], W)
                if r is None:
                    return None, None, None
                roles[nm] = r
            if it["is_corner"]:
                corners[nm] = it["corner"]
            names.append(nm)
        return roles, corners, names

    def test_members(self, st, members, cell, kind):
        """one node: the members restricted to the cell; alive and none of them provably misses."""
        roles, corners, names = self._roles_with(st, members, cell)
        lab = st["label"] + "/?%s:%s" % (cell, "+".join(members))
        if roles is None:
            self.steps.append(dict(label=lab, kind=kind, dead="window disjoint from the role's box", cell=cell,
                                   members=list(members)))
            return False, None
        nd, info, rec = self.node(roles, corners, lab, kind, cell=cell, members=list(members))
        if info["dead"]:
            return False, rec
        m = nd.misses_cell(tuple(self.items[cell]["wbox"]))
        for nm in names:
            if m.get(nm, {}).get("misses"):
                rec["dead"] = "exact miss test: %s misses %s after the clip" % (nm, cell)
                return False, rec
        rec["hulls"] = {nm: G.hull_of(nd, nm) for nm in names}
        return True, rec

    def test_two_new(self, st, cell, hullB):
        """{new,new}: geo178b's split -- Lemma A2 cells at a corner, cells of side < 1/sqrt2 of the
        one-free hull at a slot; returns the alive sub-options [(kind, spec)]."""
        it = self.items[cell]
        W = it["window"]
        alive = []
        if it["is_corner"]:
            a2 = CL.a2_cells(it["corner"])
            pairs = [(a, b, restrict(hullB, a2[a]), restrict(hullB, a2[b])) for a, b in G.A2_PAIRS]
            pairs = [(a, b, ca, cb) for a, b, ca, cb in pairs if ca is not None and cb is not None]
        else:
            cells = GB._cells(tuple(hullB[:4]))
            if len(cells) > self.max_cells:
                self.steps.append(dict(label=st["label"] + "/?%s:new+new" % cell, kind="pair-split", cell=cell,
                                       dead=None, note="hull too wide (%d cells): {new,new} ALIVE untested" % len(cells)))
                return [("new+new", None)]
            pairs = [("c%d" % i, "c%d" % j, (ci[0], ci[1], ci[2], ci[3], hullB[4], hullB[5]),
                      (cj[0], cj[1], cj[2], cj[3], hullB[4], hullB[5]))
                     for (i, ci), (j, cj) in itertools.combinations(enumerate(cells), 2)]
        for n, (a, b, ca, cb) in enumerate(pairs):
            if n >= self.max_pairs:
                alive.append(("new+new", None))
                break
            roles, corners = dict(st["roles"]), dict(st["corners"])
            n1, n2 = "F%d" % (st["nF"] + 1), "F%d" % (st["nF"] + 2)
            roles[n1], roles[n2] = ca, cb
            if it["is_corner"]:
                corners[n1] = corners[n2] = it["corner"]
            lab = st["label"] + "/?%s:new@%s+new@%s" % (cell, a, b)
            nd, info, rec = self.node(roles, corners, lab, "pair-split", cell=cell, members=["new", "new"], split=[a, b])
            if not info["dead"]:
                alive.append(("new+new", (a, b, G.hull_of(nd, n1), G.hull_of(nd, n2))))
        return alive

    # ------------------------------------------------------------------ refinement of an option
    def _subboxes(self, h):
        """split a hull into centre cells of side <= self.side x tilt halves (when > 30 deg wide)."""
        cells = GB._cells(tuple(h[:4]), side=self.side)
        tb = [(h[4], h[5])] if h[5] - h[4] <= 30 else [(h[4], 0.5 * (h[4] + h[5])), (0.5 * (h[4] + h[5]), h[5])]
        return [(c[0], c[1], c[2], c[3], t0, t1) for c in cells for (t0, t1) in tb]

    def refine_option(self, st, cell, hulls, tag):
        """every combination of sub-boxes of the option's member hulls is a node; the option survives
        iff some combination survives, and then its members are tightened to the union of the alive
        sub-boxes.  Returns the tightened hulls or None (the option is impossible).  [T]: the
        sub-boxes cover the hulls, and a member's pose lies in some sub-box."""
        it = self.items[cell]
        names = list(hulls)
        subs = [self._subboxes(hulls[nm]) for nm in names]
        combos = list(itertools.product(*subs))
        if len(combos) > self.max_combos:
            self.steps.append(dict(label=st["label"] + "/?%s:%s" % (cell, tag), kind="refine", cell=cell,
                                   note="refinement skipped: %d combos > %d" % (len(combos), self.max_combos)))
            return hulls
        alive = []
        for n, cb in enumerate(combos):
            roles, corners = dict(st["roles"]), dict(st["corners"])
            for nm, b in zip(names, cb):
                roles[nm] = b
                if it["is_corner"]:
                    corners[nm] = it["corner"]
            nd, info, rec = self.node(roles, corners, st["label"] + "/?%s:%s#%d" % (cell, tag, n), "refine",
                                      cell=cell, members=names, combo=n)
            if not info["dead"]:
                m = nd.misses_cell(tuple(it["wbox"]))
                if any(m.get(nm, {}).get("misses") for nm in names):
                    rec["dead"] = "exact miss test after the clip"
                    continue
                alive.append({nm: G.hull_of(nd, nm) for nm in names})
        self.steps.append(dict(label=st["label"] + "/?%s:%s" % (cell, tag), kind="refine", cell=cell, members=names,
                               n_combos=len(combos), n_alive=len(alive), dead=(None if alive else "every sub-box combination dead")))
        self.log("      refine %s %s: %d/%d combos alive" % (cell, tag, len(alive), len(combos)))
        if not alive:
            return None
        out = {}
        for nm in names:
            hs = [h[nm] for h in alive]
            out[nm] = (min(h[0] for h in hs), max(h[1] for h in hs), min(h[2] for h in hs), max(h[3] for h in hs),
                       min(h[4] for h in hs), max(h[5] for h in hs))
        return out

    # ------------------------------------------------------------------ options of a cell
    def options(self, st, cell):
        need = 2 - len(st["assign"][cell])
        cand, why = [], {}
        for r in self.hnames + sorted(st["fcells"]):
            if r in st["assign"][cell]:
                continue
            ok, reason = self.can_reach(st, r, cell)
            if not ok:
                why[r] = reason
                continue
            ok, rec = self.test_members(st, [r], cell, "single")
            if ok:
                cand.append(r)
            else:
                why[r] = "restricted node dead" if rec is None or rec.get("dead") is None else rec["dead"]
        hullB = None
        if st["nF"] < MAXF:
            ok, rec = self.test_members(st, ["new"], cell, "single")
            if ok:
                cand.append("new")
                hullB = rec["hulls"]["F%d" % (st["nF"] + 1)]
            else:
                why["new"] = "restricted node dead"
        if need == 1:
            opts = [(c,) for c in cand]
        else:
            opts = []
            for a, b in itertools.combinations([c for c in cand if c != "new"], 2):
                ok, rec = self.test_members(st, [a, b], cell, "pair")
                if ok:
                    opts.append((a, b, None, rec["hulls"]))
            if "new" in cand:
                for a in cand:
                    if a != "new":
                        ok, rec = self.test_members(st, [a, "new"], cell, "pair")
                        if ok:
                            opts.append((a, "new", None, rec["hulls"]))
                if st["nF"] + 2 <= MAXF:
                    for kind, spec in self.test_two_new(st, cell, hullB):
                        opts.append(("new", "new", spec, None))
        if self.refine_opts and 2 <= len(opts) <= 3:
            kept = []
            for o in opts:
                if len(o) < 3 or (o[2] is None and o[3] is None):
                    kept.append(o)                       # a single, or an untested wide pair
                    continue
                n1, n2 = "F%d" % (st["nF"] + 1), "F%d" % (st["nF"] + 2)
                if o[2] is not None:                     # {new,new} with a split
                    hs, tag = {n1: o[2][2], n2: o[2][3]}, "new@%s+new@%s" % tuple(o[2][:2])
                else:
                    hs, tag = o[3], "+".join(o[:2])
                r = self.refine_option(st, cell, hs, tag)
                if r is None:
                    continue
                if o[2] is not None:
                    kept.append(("new", "new", (o[2][0], o[2][1], r[n1], r[n2]), None))
                else:
                    kept.append((o[0], o[1], None, r))
            opts = kept
        self.log("    %s %s need %d: candidates %s -> %d option(s)%s" % (
            st["label"], cell, need, "+".join(cand) or "-", len(opts),
            ("  [" + "; ".join("%s: %s" % kv for kv in why.items()) + "]") if why else ""))
        return dict(cell=cell, need=need, cand=cand, why=why, opts=opts)

    # ------------------------------------------------------------------ apply an option
    def apply(self, st, cell, opt, tag):
        it = self.items[cell]
        new = dict(roles=dict(st["roles"]), corners=dict(st["corners"]), assign={c: list(v) for c, v in st["assign"].items()},
                   fcells={k: list(v) for k, v in st["fcells"].items()}, nF=st["nF"], hist=list(st["hist"]))
        members = [m for m in opt[:2]]
        spec = opt[2] if len(opt) > 2 else None
        tight = opt[3] if len(opt) > 3 else None
        if spec is not None:
            n1, n2 = "F%d" % (st["nF"] + 1), "F%d" % (st["nF"] + 2)
            new["roles"][n1], new["roles"][n2] = spec[2], spec[3]
            names = [n1, n2]
            new["nF"] += 2
            if it["is_corner"]:
                new["corners"][n1] = new["corners"][n2] = it["corner"]
        else:
            roles, corners, names = self._roles_with(new, members, cell)
            new["roles"], new["corners"] = roles, corners
            new["nF"] += members.count("new")
            if tight:
                for nm in names:
                    if nm in tight:
                        new["roles"][nm] = tuple(tight[nm])
        for nm in names:
            new["assign"][cell].append(nm)
            if nm.startswith("F"):
                new["fcells"].setdefault(nm, []).append(cell)
        new["label"] = st["label"] + "/" + tag + cell + "=" + "+".join(names) + (("@%s+%s" % spec[:2]) if spec else "")
        new["hist"].append(dict(cell=cell, members=names, tag=tag, split=(list(spec[:2]) if spec else None)))
        return new

    def normalise(self, st, kind):
        nd, info, rec = self.node(st["roles"], st["corners"], st["label"], kind, assign=dict(st["assign"]))
        if info["dead"]:
            return False
        st["nd"] = nd
        st["roles"] = {k: tuple(v) for k, v in info["hull"].items()}
        st["kept"] = rec["kept"]
        return True

    # ------------------------------------------------------------------ the search
    def propagate(self, st):
        """unit propagation to a fixed point; returns ('dead', cell) | ('complete', None) | ('branch', options)."""
        while True:
            open_cells = [c for c in self.items if len(st["assign"][c]) < 2]
            if not open_cells:
                return "complete", None
            table = [self.options(st, c) for c in open_cells]
            table.sort(key=lambda o: (len(o["opts"]), o["need"]))
            if not table[0]["opts"]:
                st["dead_cell"] = table[0]
                return "dead", table[0]
            if len(table[0]["opts"]) == 1:
                o = table[0]
                st2 = self.apply(st, o["cell"], o["opts"][0], "forced:")
                self.log("  FORCED %s <- %s" % (o["cell"], "+".join(str(m) for m in o["opts"][0][:2])))
                if not self.normalise(st2, "forced"):
                    st["dead_cell"] = dict(cell=o["cell"], forced=o["opts"][0][:2], note="the forced node is dead")
                    return "dead", st["dead_cell"]
                st.clear()
                st.update(st2)
                continue
            return "branch", table[0]

    def search(self, st, depth=0):
        """DFS; returns dict(verdict, leaf, children)."""
        try:
            kind, o = self.propagate(st)
        except Budget as e:
            return dict(label=st["label"], verdict="UNDECIDED", leaf=str(e))
        if kind == "dead":
            return dict(label=st["label"], verdict="DEAD", leaf="no admissible meeter assignment at %s" % o["cell"],
                        detail=o)
        if kind == "complete":
            r = dict(label=st["label"], verdict="ALIVE(geometry)", leaf=None, roles=st["roles"], assign=st["assign"],
                     nF=st["nF"], kept=st.get("kept"))
            if self.leaf_fn is not None:
                r.update(self.leaf_fn(self, st))
            return r
        # branch: options sorted single-existing first, {a,new}, then {new,new}
        opts = sorted(o["opts"], key=lambda t: (t[:2].count("new"), tuple(t[:2])))
        kids = []
        for k, opt in enumerate(opts):
            st2 = self.apply(st, o["cell"], opt, "b%d:" % (k + 1))
            self.log("  BRANCH %s <- %s (%d/%d)" % (o["cell"], "+".join(str(m) for m in opt[:2]), k + 1, len(opts)))
            if not self.normalise(st2, "branch"):
                kids.append(dict(label=st2["label"], verdict="DEAD", leaf="branch node dead (pair leaf)"))
                continue
            kids.append(self.search(st2, depth + 1))
        v = ("DEAD" if all(c["verdict"] == "DEAD" for c in kids) else
             ("ALIVE" if any(c["verdict"].startswith("ALIVE") for c in kids) else "UNDECIDED"))
        return dict(label=st["label"], verdict=v, branch=o["cell"], n_children=len(kids), children=kids)

    def run(self):
        st = self.root
        if not self.normalise(st, "base"):
            return dict(verdict="DEAD", leaf="base node dead (pair leaf)", tree=None)
        tree = self.search(st)
        return dict(verdict=tree["verdict"], leaf=tree.get("leaf"), tree=tree)
