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
  (c) EXACT  pairclip201.pair_clip: the two rows' own surviving PIECES (centre rect x tilt sub-bin; already clipped
             by the container, the pins' stock boxes and every role's K' in A198's reach bisection) clipped against
             each other's certified K' (A171/A172 per-piece K' on tilt-quarter hulls, exact dead test) to a fixed
             point; a side with no surviving piece => EXCLUDED, with the pass trace.  Tried first on the CELL pair
             (the union of the two cells' anonymous survivors: one test covers every option pair of the two cells),
             then on the option pair.  Cached; under a per-round time budget -- an untested pair is COMPATIBLE.
             (The full multibox node {pins, roles, hull(X1), hull(X2)} was measured on Y0044 and excluded NOTHING at
             3 s a pair: the box hulls forget the piece structure -- exp201.py, logs/exp201_y0044.log.)
Same-cell pairs are excluded by the count itself (one centre per closed cell of side < 1/sqrt2, Lemma A1); a cell's
Euclidean diameter is < 1 as well, so CN says the same.  Every exclusion the search USES is recorded with its rule.
"""
import math
import time
from fractions import Fraction as Fr

import fastprop as FP                                          # READ-ONLY (A198)
import pairclip201 as PCL

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
    def __init__(self, page, budget=180.0, refine=0, max_iter=3, n_coarse=4, exact=True, log=None):
        self.page = page
        self.budget = budget
        self.refine, self.max_iter, self.n_coarse = refine, max_iter, n_coarse
        self.cell_pcs, self.cell_cache = {}, {}
        self.exact_on = exact
        self.log = log
        self.hull = {}                 # key -> (x0,x1,y0,y1) Fractions
        self.pieces_of = {}            # key -> pieces (lazy)
        self.cache = {}                # frozenset({k1,k2}) -> (compatible, record | None)
        self.excl = []                 # every exclusion found (rule + numbers)
        self.n = dict(lookups=0, a1=0, cn=0, cell_tested=0, cell_excl=0, exact_tested=0, exact_excl=0, undecided_budget=0, exact_seconds=0.0)
        self.hits = set()              # exclusions USED by the current search
        self.undecided = set()         # pairs left COMPATIBLE by the budget (distinct)
        self.spent = 0.0

    # ---------------------------------------------------------------- registration
    def register(self, free_opts, fixed_opts):
        for o in free_opts:
            self.hull[okey("free", o)] = tuple(o[3])
        for r, opts in fixed_opts.items():
            for o in opts:
                self.hull[okey(r, o)] = tuple(o[3])

    def precompute_cells(self, cell_budget):
        """(c1) up front: every pair of DISTINCT cells that host anonymous rows, nearest first, within `cell_budget`
        seconds -- one clip per cell pair decides every option pair of those cells."""
        cells = sorted(set(k[1] for k in self.hull if k[0] == "free"))
        t0 = time.time()
        pairs = []
        for i, a in enumerate(cells):
            for b in cells[i + 1:]:
                ra, rb = self.page.cells[a]["rect"], self.page.cells[b]["rect"]
                dx = max(Fr(0), rb[0] - ra[1], ra[0] - rb[1]); dy = max(Fr(0), rb[2] - ra[3], ra[2] - rb[3])
                if dx * dx + dy * dy < PCL.SQ2 * PCL.SQ2:
                    pairs.append((dx * dx + dy * dy, a, b))
        pairs.sort()
        for _, a, b in pairs:
            if self.spent >= cell_budget:
                break
            ck = frozenset((a, b))
            if ck in self.cell_cache:
                continue
            self.n["cell_tested"] += 1
            self.cell_cache[ck] = self._clip(self.cell_union(a), self.cell_union(b))
            if self.cell_cache[ck]["excluded"]:
                self.n["cell_excl"] += 1
        self.n["cell_pairs_near"] = len(pairs)
        self.n["cell_precompute_seconds"] = round(time.time() - t0, 2)
        return len(pairs)

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
            self.undecided.add(frozenset((k1, k2)))
            return True, None
        return self._exact(k1, k2, base)

    # ---------------------------------------------------------------- (c) the exact pair clip (pairclip201)
    def cell_union(self, ci):
        """every surviving piece of an anonymous meeter with centre in cell ci (over all slots): a superset of the
        poses of any anonymous row at that cell, so an exclusion at cell level covers every option pair there."""
        if ci not in self.cell_pcs:
            pcs = []
            for p in self.page.slots:
                pcs += self.page.reach(ci, frozenset([p]))[1]
            self.cell_pcs[ci] = pcs
        return self.cell_pcs[ci]

    def _clip(self, p1, p2):
        r = PCL.pair_clip(p1, p2, self.page.s, max_iter=self.max_iter, refine=self.refine, n_coarse=self.n_coarse,
                          stats=self.page.nd.stats)
        self.spent += r["seconds"]
        self.n["exact_seconds"] += r["seconds"]
        return r

    def _exact(self, k1, k2, base):
        rec = dict(base, rule="EXACT", settings=dict(max_iter=self.max_iter, refine=self.refine, n_coarse=self.n_coarse))
        if k1[0] == "free" and k2[0] == "free":                 # (c1) the CELL pair first (cached per cell pair)
            ck = frozenset((k1[1], k2[1]))
            if ck not in self.cell_cache:
                self.n["cell_tested"] += 1
                self.cell_cache[ck] = self._clip(self.cell_union(k1[1]), self.cell_union(k2[1]))
            r = self.cell_cache[ck]
            if r["excluded"]:
                self.n["exact_excl"] += 1; self.n["cell_excl"] += 1
                rec.update(level="cell", cells=sorted(ck), why="EXACT (cell pair %s): %s" % (sorted(ck), r["why"]),
                           passes=r.get("passes"), seconds=r["seconds"], n_pieces=[len(self.cell_union(k1[1])), len(self.cell_union(k2[1]))])
                if self.log:
                    self.log("      EXACT cell-pair exclusion %s: %s (%.2f s)" % (sorted(ck), r["why"], r["seconds"]))
                return False, rec
            if self.spent >= self.budget:
                self.undecided.add(frozenset((k1, k2)))
                return True, None
        self.n["exact_tested"] += 1                              # (c2) the option pair on its own pieces
        r = self._clip(self.pieces(k1), self.pieces(k2))
        rec.update(level="option", why="EXACT (option pair): " + r["why"], passes=r.get("passes"), seconds=r["seconds"],
                   kept=[r.get("kept_a"), r.get("kept_b")], n_pieces=[len(self.pieces(k1)), len(self.pieces(k2))])
        if not r["excluded"]:
            return True, rec
        self.n["exact_excl"] += 1
        if self.log:
            self.log("      EXACT exclusion %s | %s: %s (%.2f s)" % (key_json(k1), key_json(k2), r["why"], r["seconds"]))
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
        d["undecided_budget"] = len(self.undecided)
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
