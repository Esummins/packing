"""A201 -- the PairTable's cover-level operations (mixin): the exhaustive CELL-pair precompute, the witness-refutation
check of a count cover (rule (c) pair by pair), the JOINT clip of a pairwise-verified cover, and the check of a prior
witness cover (A200's).  Split from pairtab201.py for length; the semantics are documented there."""
import time
from fractions import Fraction as Fr

import fastprop as FP                                          # READ-ONLY (A198)
import pairclip201 as PCL


def okey(who, o):
    """the option's identity: (who, cell, slot set).  who = 'free' (anonymous) or a role name."""
    return (who, o[0], frozenset(o[1]))


def key_json(k):
    return [k[0], k[1], sorted(k[2])]



class CoverOps:
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


    def verify_cover(self, witness):
        """(c) on every pair of a count witness [(who, o)]: -> (excluded pairs, all decided?).  The count's DFS runs
        on (a) (b) and the cached (c) results; the exact budget is spent HERE, on the covers the count proposes."""
        keys = [okey(who, o) for who, o in witness]
        excl, decided = [], True
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                pk = frozenset((keys[i], keys[j]))
                if not self.compatible(keys[i], keys[j], exact=True):
                    excl.append(self.cache[pk][1])
                elif pk not in self.cache:
                    decided = False
        self.refutations.append(dict(cover=[key_json(k) for k in keys], excluded=[dict(a=e["a"], b=e["b"], rule=e["rule"]) for e in excl],
                                     decided=decided))
        return excl, decided


    def check_cover(self, witness):
        """the JOINT clip of a pairwise-verified cover (pairclip201.cover_clip): refuted => the cover is FORBIDDEN for
        the next search.  -> (refuted, record).  Budget: an untested cover stands."""
        keys = [okey(who, o) for who, o in witness]
        if self.spent >= self.budget:
            self.n["cover_undecided"] = self.n.get("cover_undecided", 0) + 1
            return False, None
        r = PCL.cover_clip([self.pieces(k) for k in keys], self.page.s, max_iter=self.max_iter, n_coarse=self.n_coarse,
                           stats=self.page.nd.stats, names=["%s@%d" % (k[0], k[1]) for k in keys])
        self.spent += r["seconds"]
        self.n["exact_seconds"] += r["seconds"]
        self.n["cover_tested"] = self.n.get("cover_tested", 0) + 1
        rec = dict(rule="COVER", cover=[key_json(k) for k in keys], excluded=r["excluded"], dead=r.get("dead"), why=r["why"],
                   passes=r.get("passes"), seconds=r["seconds"], kept=r.get("kept"))
        self.refutations.append(dict(cover=rec["cover"], excluded=([dict(rule="COVER", dead=r.get("dead"))] if r["excluded"] else []),
                                     decided=True, joint=rec))
        if r["excluded"]:
            self.n["cover_excl"] = self.n.get("cover_excl", 0) + 1
            self.forbidden.add(frozenset(keys))
            self.excl.append(rec)
        return r["excluded"], rec


    def check_pairs(self, keys, label):
        """run every pair of the given option keys through the table (a prior witness cover, e.g. A200's)."""
        out = []
        ks = [k for k in keys if k in self.hull]
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                ok = self.compatible(ks[i], ks[j], exact=True)
                rec = self.cache.get(frozenset((ks[i], ks[j])), (True, None))[1]
                out.append(dict(a=key_json(ks[i]), b=key_json(ks[j]), compatible=ok,
                                rule=(rec or {}).get("rule"), why=(rec or {}).get("why")))
        return dict(label=label, n_keys=len(keys), n_found=len(ks), pairs=out,
                    dead=any(not p["compatible"] for p in out))
