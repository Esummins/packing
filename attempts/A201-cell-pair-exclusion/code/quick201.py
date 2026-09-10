"""A201 -- A200's quick chain with the assignment count's pairwise test replaced by the CELL-PAIR COMPATIBILITY TABLE
(pairtab201: Lemma A1 / Lemma CN / the exact multibox pair node; "cell-pair mutual exclusion", the PI, 2026-09-10).
A modified copy of attempts/A200-k516-quick/code/quick200.py: A200's module is imported READ-ONLY for everything that
does not change (set_pad, union_cap, seal_leaf, noroom_leaf, PADS); `count_search` and `propagate_round` are the
copies with the table wired in.  Certificates keep A200's fields (nid/verdict/pad/steps/rounds/witness/roles/tests)
and add `pair_excl` (the table's summary, every exclusion with its rule and numbers, the exclusions each search USED).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A200-k516-quick", "code"), os.path.join(ATT, "A198-fastprop", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fastprop as FP                                          # noqa: E402  READ-ONLY (A198)
import quick200 as Q                                           # noqa: E402  READ-ONLY (A200)
import pairtab201 as PT                                        # noqa: E402
import count201                                                # noqa: E402

INF = Q.INF


# ----------------------------------------------------------------------------- the page
class QPage201(Q.QPage):
    def __init__(self, *a, pair_budget=180.0, pair_exact=True, prior_witness=None, **kw):
        super().__init__(*a, **kw)
        self.pair_budget, self.pair_exact = pair_budget, pair_exact
        self.prior_witness = prior_witness          # [(who, ci, [slots])] of an earlier count (A200's certificate)
        self.tables = []

    def _count(self, label, free_opts, fixed_opts, n_anon, caps, table, use_chords):
        t0 = time.time()
        r = count201.count_search(self.slots, free_opts, fixed_opts, n_anon, self.lines, self.pin_chords, self.s, caps, table, use_chords=use_chords)
        st = self.T.step("count", time.time() - t0, chords=use_chords, feasible=r.feasible, nodes=r.nodes, capped=r.capped,
                         label=label, excl_used=len(table.hits), pair_spent=round(table.spent, 2))
        table.used[label] = table.hits_json()
        return r, st

    def propagate_round(self, rnd):
        """A200's round with the table: (b) union caps, (c) FC forcing, (e) the joint count, bar-H, the clips."""
        free_opts, fixed_opts, single = self.build_options()
        info = dict(round=rnd, single={p: {ci: round(f, 4) for ci, f in v.items()} for p, v in single.items()},
                    n_free_opts=len(free_opts), fixed={r: [(ci, sorted(S)) for ci, S, _, _ in v] for r, v in fixed_opts.items()},
                    free_opts=[(ci, sorted(S), FP.rect_f(h)) for ci, S, _, h in free_opts])
        roles_reach = {r: set().union(*[S for _, S, _, _ in fixed_opts[r]]) if fixed_opts[r] else set() for r in fixed_opts}
        H_reach = roles_reach[self.H]
        info["H_reach"] = sorted(H_reach)
        t0 = time.time()
        base_ch = self.fixed_chords()
        caps, urec = {}, {}
        self.union_last = {}
        for p in self.slots:
            pcs = self.slot_union(p, single)
            self.union_last[p] = pcs
            if len(single.get(p, {})) <= 1:
                cap = min(1, len(single.get(p, {})))
                rec = dict(slot=p, cap=cap, why="A1: %d alive cell(s)" % len(single.get(p, {})), n_pieces=len(pcs))
                if pcs:
                    st = Q.union_stats(pcs)
                    rec.update(bbox=FP.rect_f(st["bbox"]), diam=round(float(st["diam2"]) ** 0.5, 5), linf=round(float(st["linf"]), 5))
            else:
                cap, rec = self.union_cap(p, pcs, base_ch)
            caps[p], urec[p] = cap, rec
            self.T.test("UNION", **rec)
        self.caps_last = dict(caps)
        info["union"], info["caps"] = urec, {p: (None if c >= INF else c) for p, c in caps.items()}
        self.T.step("union", time.time() - t0, caps=info["caps"])
        forced_H, forced_role, instantiate = set(), {}, {}
        for p in self.slots:
            R_p = [r for r in roles_reach if r != self.H and p in roles_reach[r]]
            H_p = p in H_reach
            avail = (1 if H_p else 0) + len(R_p) + caps[p]
            rec = dict(slot=p, H=H_p, roles=R_p, cap=(None if caps[p] >= INF else caps[p]))
            if avail < 2:
                self.dead = "FC at %s: at most %d distinct non-pin meeter(s) (H %s; roles %s; anonymous cap %d by %s)" % (
                    p, avail, "reaches" if H_p else "provably misses", R_p, caps[p], urec[p]["why"])
                self.T.test("FC-AVAIL", verdict="DEAD", avail=avail, **rec)
                info["dead"] = self.dead
                return info
            if avail == 2:
                if H_p:
                    forced_H.add(p)
                for r in R_p:
                    forced_role.setdefault(r, set()).add(p)
                if caps[p] == 1:
                    instantiate[p] = True
                self.T.test("FC-AVAIL", verdict="all forced", avail=2, **rec)
        # --- the pair table of this round, then the joint count with the caps
        table = PT.PairTable(self, budget=self.pair_budget, exact=self.pair_exact, log=None)
        table.register(free_opts, fixed_opts)
        table.used = {}
        self.tables.append(table)
        if self.prior_witness and rnd == 1:
            keys = [(who, ci, frozenset(S)) for who, ci, S in self.prior_witness]
            info["witness_check"] = table.check_pairs(keys, "A200 witness cover")
            self.T.test("PAIR-WITNESS", **{k: v for k, v in info["witness_check"].items() if k != "pairs"})
        n_anon = self.n_free - len(self.role_cell)
        r, _ = self._count("nochord", free_opts, fixed_opts, n_anon, caps, table, False)
        info["count_nochord"] = dict(feasible=r.feasible, nodes=r.nodes, capped=r.capped, excl_used=table.used["nochord"])
        if not r.feasible:
            self.dead = "JOINT COUNT + PAIR TABLE (caps %s; exclusions used: %s): no cover of the %d forced slots by H + %d role(s) + %d anonymous squares" % (
                info["caps"], self._rules(table.used["nochord"]), len(self.slots), len(self.role_cell), n_anon)
            self.T.test("COUNT", chords=False, verdict="DEAD", nodes=r.nodes, n_free_opts=len(free_opts), caps=info["caps"], excl_used=table.used["nochord"])
            info["dead"], info["pair_excl"] = self.dead, dict(table.summary(), used=dict(table.used))
            return info
        r2, _ = self._count("chord", free_opts, fixed_opts, n_anon, caps, table, True)
        info["count_chord"] = dict(feasible=r2.feasible, nodes=r2.nodes, capped=r2.capped, excl_used=table.used["chord"])
        if not r2.feasible:
            self.dead = "JOINT COUNT + CHORD ROWS + PAIR TABLE (caps %s; exclusions used: %s): no cover of the %d forced slots" % (
                info["caps"], self._rules(table.used["chord"]), len(self.slots))
            self.T.test("COUNT", chords=True, verdict="DEAD", nodes=r2.nodes, n_free_opts=len(free_opts), caps=info["caps"], excl_used=table.used["chord"])
            info["dead"], info["pair_excl"] = self.dead, dict(table.summary(), used=dict(table.used))
            return info
        self.witness = r2.witness if r2.witness is not None else r.witness
        info["witness"] = [(who, ci, sorted(S)) for who, (ci, S, _, _) in (self.witness or [])]
        for p in self.slots:
            if p in forced_H or p not in H_reach or self.T.out_of_time():
                continue
            fo = dict(fixed_opts)
            fo[self.H] = [o for o in fixed_opts[self.H] if p not in o[1]]
            rr, _ = self._count("barH:" + p, free_opts, fo, n_anon, caps, table, False)
            if rr.feasible:
                rr, _ = self._count("barH+chord:" + p, free_opts, fo, n_anon, caps, table, True)
            if not rr.feasible:
                forced_H.add(p)
                self.T.test("COUNT", barH=p, verdict="H forced at %s" % p, nodes=rr.nodes)
        info["forced_H"], info["forced_role"], info["instantiate"] = sorted(forced_H), {r: sorted(v) for r, v in forced_role.items()}, sorted(instantiate)
        info["pair_excl"] = dict(table.summary(), used={k: v for k, v in table.used.items() if v})
        return self._apply(info, forced_H, forced_role, instantiate, urec)

    @staticmethod
    def _rules(used):
        return sorted(set(u["rule"] for u in used)) or ["none"]

    def _apply(self, info, forced_H, forced_role, instantiate, urec):
        """A200's clips, verbatim: H to its forced slots, the forced roles, the unique anonymous meeter instantiated."""
        changed = False
        if forced_H - self.forced_H:
            self.forced_H |= forced_H
            S = frozenset(self.forced_H)
            fr, pcs, _ = self.role_reach(self.H, S)
            if not pcs:
                self.dead = "H forced at %s but cannot meet them simultaneously (exact MISS test on every piece)" % sorted(S)
                self.T.test("H-JOINT", slots=sorted(S), verdict="DEAD")
                info["dead"] = self.dead
                return info
            newH = self._shrink(self.roles[self.H], pcs)
            self.T.test("H-CLIP", slots=sorted(S), frac=round(fr, 6), n_pieces=len(pcs), box_before=FP.rect_f(self.roles[self.H]), box_after=FP.rect_f(newH))
            self.roles[self.H] = newH
            info["H_box"] = FP.rect_f(newH)
            changed = True
        for r, ps in forced_role.items():
            S = frozenset(ps) | frozenset(self.role_slots.get(r, ()))
            if S == frozenset(self.role_slots.get(r, ())):
                continue
            fr, pcs, _ = self.role_reach(r, S)
            if not pcs:
                self.dead = "%s forced to meet %s: no pose (exact MISS)" % (r, sorted(S))
                self.T.test("ROLE-JOINT", role=r, slots=sorted(S), verdict="DEAD")
                info["dead"] = self.dead
                return info
            nb = self._shrink(self.roles[r], pcs)
            self.roles[r], self.role_slots[r] = nb, tuple(sorted(S))
            self.T.test("ROLE-CLIP", role=r, slots=sorted(S), box_after=FP.rect_f(nb))
            changed = True
        for p in sorted(instantiate):
            pcs = self.union_last.get(p) or []
            if not pcs:
                continue
            hull = FP.pieces_hull(pcs)
            role = "F%d" % (len(self.role_cell) + 1)
            self.roles[role] = (FP.fl(hull[0]), FP.fl(hull[1]), FP.fl(hull[2]), FP.fl(hull[3]), Q.MB.deg_of_t(hull[4]), Q.MB.deg_of_t(hull[5]))
            self.role_cell[role], self.role_slots[role] = -1, (p,)
            if self.item[p]["is_corner"]:
                self.role_corner[role] = self.item[p]["corner"]
            self.T.test("INSTANTIATE", role=role, slot=p, box=FP.rect_f(self.roles[role]), n_pieces=len(pcs), why=urec[p]["why"])
            changed = True
        info["changed"] = changed
        return info

    def result(self):
        out = super().result()
        out["pair_excl"] = dict(rounds=[dict(t.summary(), used={k: v for k, v in getattr(t, "used", {}).items() if v},
                                             excl=t.excl) for t in self.tables])
        return out
