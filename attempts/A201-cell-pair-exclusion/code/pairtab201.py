"""A201 -- the CELL-PAIR COMPATIBILITY TABLE of the assignment count ("cell-pair mutual exclusion", the PI, 2026-09-10:
"sections 21/22/23 can only have one centre TOTAL, which means 21/22 isn't a valid centre pair for BR(0,1)").

The count (A198 Theorem COUNT; A200's count_search) places DISTINCT squares on option rows (cell, slot set S) and
tested two rows only by Lemma A1 on their hulls.  Here every pair of rows the search reaches goes through three
rules, in order, each a PROOF that no two interior-disjoint admissible squares realise the pair; a pair no rule
decides stays COMPATIBLE (the sound direction):
  (a) A1     Lemma A1: some pair of centres at l-inf distance >= 1/sqrt2 (as before; FP.a1_compatible);
  (b) CN     Lemma CN (A153): two interior-disjoint unit squares have centres at Euclidean distance >= 1 (the open
             inscribed discs of radius 1/2 are disjoint).  The max distance between the two hulls (attained at
             corners: max x-extent, max y-extent) < 1  =>  EXCLUDED.  Exact in Fractions.
  (c) EXACT  the pair as a multibox node {pins, every other role at its normalised hull, the two rows at the hulls
             of THEIR surviving pieces (centre rect x tilt)} normalised by A171's mutual clip (container, the pins'
             stock boxes, every role's K', the lonely clip at corner slots): EmptyBox => EXCLUDED, with the trace.
             Cached per unordered pair; under a per-page time budget -- an untested pair is COMPATIBLE.
Same-cell pairs are excluded by the count itself (one centre per closed cell of side < 1/sqrt2, Lemma A1); a cell's
Euclidean diameter is < 1 as well, so CN says the same.  Every exclusion the search USES is recorded with its rule.
"""
import math
import time
from fractions import Fraction as Fr

import fastprop as FP                                          # READ-ONLY (A198)

MB = FP.MB
ONE = Fr(1)


def okey(who, o):
    """the option's identity: (who, cell, slot set).  who = 'free' (anonymous) or a role name."""
    return (who, o[0], frozenset(o[1]))


def key_json(k):
    return [k[0], k[1], sorted(k[2])]


def hull_maxdist2(h1, h2):
    """exact max squared Euclidean distance between two centre rects (attained at corners)."""
    dx = max(h1[1] - h2[0], h2[1] - h1[0])
    dy = max(h1[3] - h2[2], h2[3] - h1[2])
    return dx * dx + dy * dy


class PairTable:
    def __init__(self, page, budget=60.0, nsub=2, refine=1, max_iter=4, max_pieces=48, exact=True, log=None):
        self.page = page
        self.budget = budget
        self.nsub, self.refine, self.max_iter, self.max_pieces = nsub, refine, max_iter, max_pieces
        self.exact_on = exact
        self.log = log
        self.hull = {}                 # key -> (x0,x1,y0,y1) Fractions
        self.pieces_of = {}            # key -> pieces (lazy)
        self.cache = {}                # frozenset({k1,k2}) -> (compatible, record | None)
        self.excl = []                 # every exclusion found (rule + numbers)
        self.n = dict(lookups=0, a1=0, cn=0, exact_tested=0, exact_excl=0, undecided_budget=0, exact_seconds=0.0)
        self.hits = set()              # exclusions USED by the current search
        self.spent = 0.0

    # ---------------------------------------------------------------- registration
    def register(self, free_opts, fixed_opts):
        for o in free_opts:
            self.hull[okey("free", o)] = tuple(o[3])
        for r, opts in fixed_opts.items():
            for o in opts:
                self.hull[okey(r, o)] = tuple(o[3])

    def pieces(self, k):
        if k not in self.pieces_of:
            who, ci, S = k
            if who == "free":
                self.pieces_of[k] = self.page.reach(ci, S)[1]
            else:
                self.pieces_of[k] = self.page.role_pieces_in_cell(who, S, ci)
        return self.pieces_of[k]

    # ---------------------------------------------------------------- the lookup
    def compatible(self, k1, k2):
        self.n["lookups"] += 1
        pk = frozenset((k1, k2))
        if pk in self.cache:
            ok, rec = self.cache[pk]
        else:
            ok, rec = self._decide(k1, k2)
            self.cache[pk] = (ok, rec)
            if not ok:
                self.excl.append(rec)
        if not ok:
            self.hits.add(pk)
        return ok

    def _decide(self, k1, k2):
        h1, h2 = self.hull[k1], self.hull[k2]
        base = dict(a=key_json(k1), b=key_json(k2), hull_a=FP.rect_f(h1), hull_b=FP.rect_f(h2))
        if not FP.a1_compatible(h1, h2):
            self.n["a1"] += 1
            mx = max(h1[1] - h2[0], h2[1] - h1[0]); my = max(h1[3] - h2[2], h2[3] - h1[2])
            return False, dict(base, rule="A1", linf_max=round(float(max(mx, my)), 6),
                               why="Lemma A1: max l-inf centre distance %.4f < 1/sqrt2" % float(max(mx, my)))
        d2 = hull_maxdist2(h1, h2)
        if d2 < ONE:
            self.n["cn"] += 1
            return False, dict(base, rule="CN", maxdist=round(math.sqrt(float(d2)), 6),
                               why="Lemma CN: max Euclidean centre distance %.4f < 1 (inscribed discs)" % math.sqrt(float(d2)))
        if not self.exact_on:
            return True, None
        if self.spent >= self.budget:
            self.n["undecided_budget"] += 1
            return True, None
        return self._exact(k1, k2, base)

    # ---------------------------------------------------------------- (c) the exact pair node
    def _node_roles(self, k1, k2):
        pg = self.page
        roles, corners = {}, {}
        for r in pg.nd.names:
            if r.startswith("P"):
                roles[r] = tuple(pg.roles[r])
            else:
                roles[r] = self._hull_box(pg.nd.boxes[r].pieces)
                if r in getattr(pg, "role_corner", {}):
                    corners[r] = pg.role_corner[r]
        for tag, k in (("X1", k1), ("X2", k2)):
            who, ci, S = k
            name = tag if who == "free" else who
            pcs = self.pieces(k)
            if not pcs:
                return None, None, name
            roles[name] = self._hull_box(pcs)
            for p in S:
                if pg.item[p]["is_corner"]:
                    corners[name] = pg.item[p]["corner"]
        return roles, corners, None

    @staticmethod
    def _hull_box(pcs):
        h = FP.pieces_hull(pcs)
        return (FP.fl(h[0]), FP.fl(h[1]), FP.fl(h[2]), FP.fl(h[3]), MB.deg_of_t(h[4]), MB.deg_of_t(h[5]))

    def _exact(self, k1, k2, base):
        t0 = time.time()
        roles, corners, empty = self._node_roles(k1, k2)
        rec = dict(base, rule="EXACT", settings=dict(nsub=self.nsub, refine=self.refine, max_iter=self.max_iter, max_pieces=self.max_pieces))
        if roles is None:
            rec.update(why="no surviving piece for %s" % empty, seconds=0.0)
            self.n["exact_tested"] += 1; self.n["exact_excl"] += 1
            return False, rec
        rec["node"] = {r: FP.rect_f(b) for r, b in roles.items() if not r.startswith("P")}
        rec["corners"] = dict(corners)
        nd = MB.Node(dict(roles), name=self.page.name + "/pair")
        dead = None
        try:
            nd.normalise(nsub=self.nsub, refine=self.refine, max_iter=self.max_iter, mode="poly", kmode="pieces",
                         strict_container=False, corners=corners or None, max_pieces=self.max_pieces, verbose=False)
        except MB.EmptyBox as e:
            dead = e.name
        dt = time.time() - t0
        self.spent += dt
        self.n["exact_tested"] += 1
        self.n["exact_seconds"] += dt
        rec.update(seconds=round(dt, 3), passes=nd.stats.get("passes"),
                   kept={r: round(b.kept_fraction(), 5) for r, b in nd.boxes.items() if not r.startswith("P")})
        if dead is None:
            rec["why"] = "pair node alive: COMPATIBLE"
            rec["hull_after"] = {r: [round(v, 5) for v in self._hull_box(b.pieces)] for r, b in nd.boxes.items()
                                 if b.pieces and not r.startswith("P")}
            return True, rec
        self.n["exact_excl"] += 1
        rec.update(kill_box=dead, why="EXACT: multibox pair node EmptyBox(%s) -- no admissible disjoint pair" % dead,
                   trace=[str(t)[:160] for t in (nd.boxes[dead].trace[-12:] if dead in nd.boxes else [])])
        if self.log:
            self.log("      EXACT exclusion %s | %s: EmptyBox(%s) in %.2f s" % (key_json(k1), key_json(k2), dead, dt))
        return False, rec

    # ---------------------------------------------------------------- reporting
    def begin_search(self):
        self.hits = set()

    def hits_json(self):
        out = []
        for pk in self.hits:
            ok, rec = self.cache[pk]
            out.append(dict(a=rec["a"], b=rec["b"], rule=rec["rule"]))
        return sorted(out, key=lambda d: (d["rule"], str(d["a"]), str(d["b"])))

    def summary(self):
        d = dict(self.n)
        d["exact_seconds"] = round(d["exact_seconds"], 2)
        d.update(budget=self.budget, n_excl=len(self.excl), n_cached=len(self.cache),
                 by_rule={r: sum(1 for e in self.excl if e["rule"] == r) for r in ("A1", "CN", "EXACT")})
        return d

    def check_pairs(self, keys, label):
        """run every pair of the given option keys through the table (a prior witness cover, e.g. A200's)."""
        out = []
        ks = [k for k in keys if k in self.hull]
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                ok = self.compatible(ks[i], ks[j])
                rec = self.cache[frozenset((ks[i], ks[j]))][1]
                out.append(dict(a=key_json(ks[i]), b=key_json(ks[j]), compatible=ok,
                                rule=(rec or {}).get("rule"), why=(rec or {}).get("why")))
        return dict(label=label, n_keys=len(keys), n_found=len(ks), pairs=out,
                    dead=any(not p["compatible"] for p in out))
