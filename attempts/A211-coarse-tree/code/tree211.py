"""A211 -- the COARSE TREE (notes/coarse_tree.md): A209's composed tree with CHEAP internal nodes (coarse211.CoarsePage:
one cascade round, re-binned pieces, refine 1, no lonely clip, shallow reach) branched at once on the tightest slot
(A205's rule: fewest rows, pairs when no named meeter, unit propagation), and at every FULLY NAMED leaf (every forced
slot has two named meeters on a fresh table) the leaf rules in order, cheapest first:
  (a) rule CC (Lemma CORNER-COVER, leaves211);  (b) NO-ROOM + the pocket CN bound at k >= 9 (A208 / A209: pockets
  branched on at k = 9, Lemma POCKET);  (c) the basin clip (A207, Lemma BASIN);  (d) Rule NS on a soft name (A206,
  slivers only: MAX_FRAC);  (e) the EXACT cascade at the leaf (nsub 4 / refine 2, lonely clip, basins, 3 rounds) then
  the sharp round -- after which the loop re-reads the table: new branches are coarse children again.
A leaf is DEAD iff one rule proves it; a node is DEAD iff every branch is (Lemma CT); undecided = ALIVE."""
import time

import poly204 as P
import tree205b as TB
import tree206 as N6
import tree206b as NB
import tree209 as N9
import leaves211 as L11
import inherit211 as INH

EXACT_ROUNDS = 3
NOROOM_CAP = 120.0                     # seconds for A189's no-room at a leaf (Y0202 test: 300 s UNDECIDED x 3 ate half the wall)


class Tree211(N9.Tree209):
    def __init__(self, pg, dead_paths=None, path0=(), **kw):
        N9.Tree209.__init__(self, pg, **kw)
        self.cc_kills, self.exact_rounds, self.basin_kills = 0, 0, 0
        self._ns = None
        self.dead_paths = dead_paths or {}          # Lemma INHERIT: path -> the certificate that closed it
        self.pathof = {self.root_label: tuple(path0)}
        self.n_inherited = 0

    # ------------------------------------------------------------------ Lemma INHERIT at every depth
    def step_key(self, br):
        """the branch's hypothesis as inherit211's path step (a unit-propagation step adds none: it is derived)."""
        kind = str(br.get("kind") or "row")
        if kind.startswith("ns-"):
            return ("ns", str(br.get("slot")), str(br.get("role")), kind)
        if kind == "pocket":
            return ("pocket", tuple(round(float(v), 6) for v in (br.get("pocket") or ())), tuple(br.get("rows") or ()))
        return ("row", str(br.get("slot")), tuple(br.get("rows") or ()))

    def child_path(self, lab, parent, br):
        p = tuple(self.pathof.get(parent, ())) + (self.step_key(br),)
        self.pathof[lab] = p
        if not self.dead_paths:
            return None, None, p
        info, q = INH.covered(self.dead_paths, p)
        return info, q, p

    def record_inherited(self, lab, depth, br, info, p):
        pg = self.pg
        why = ("Lemma INHERIT: the hypothesis of this branch (%d step(s): %s) is already refuted -- %s closed it as %s in %s [%s]" % (
            len(p), "; ".join("%s<-%s" % (s[1], s[2]) for s in p), info.get("camp"), info.get("label"), info.get("cert"), info.get("rule")))
        self.nodes.append(dict(label=lab, depth=depth, slot=br.get("slot"), kind="inherited", rows=br.get("rows"), named=br.get("named"),
                               verdict="DEAD", clip="INHERIT", killed_round=None, reason="inherited DEAD from %s %s" % (info.get("camp"), info.get("cert")),
                               leaf=why, seconds=0.0, t=round(pg.T.now(), 1), n_rounds=0, snapshot=None,
                               source_cert=info.get("cert"), source_label=info.get("label"), source_camp=info.get("camp"),
                               source_rule=info.get("rule"), source_ledger=info.get("ledger"),
                               verifier="[C: library clip trace] inherited (Lemma INHERIT, notes/coarse_tree.md s.4): %s" % info.get("cert")))
        self.dead_leaves += 1
        self.n_inherited += 1
        self.inherit_hits[lab] = dict(info, path=[list(map(str, s)) for s in p], slot=br.get("slot"), rows=br.get("rows"))
        pg.T.test("INHERIT", label=lab, verdict="DEAD", cert=info.get("cert"), source=info.get("label"), rule=info.get("rule"))
        self.log("   node %-10s d%d %s<-%s: DEAD INHERITED from %s %s (%s)" % (lab, depth, br.get("slot"), br.get("rows"), info.get("camp"), info.get("label"), info.get("cert")))
        if self.on_node:
            self.on_node(self)

    def record(self, label, depth, br, verdict, clip, rnd, t0, reason=None):
        cb, self.on_node = self.on_node, None
        r = NB.Tree206.record(self, label, depth, br, verdict, clip, rnd, t0, reason=reason)
        self.on_node = cb
        pg = self.pg
        r["coarse"] = pg.coarse
        r["n_pieces"] = {k: len(v) for k, v in pg.pieces.items() if not k.startswith("P")}
        r["rebin"] = list(pg.rebin_rep)[-6:]
        if self.on_node:
            self.on_node(self)
        return r

    def fresh_child(self):
        pg = self.pg
        pg.set_coarse(True)
        pg.sharpened, pg.noroom_done, pg.basin_done = False, False, False

    def kill(self, label, depth, clip, leaf, **extra):
        pg = self.pg
        pg.dead = leaf
        self.nodes[-1].update(verdict="DEAD", clip=clip, leaf=leaf, killed_round=len(pg.round_times), reason=None, **extra)
        self.dead_leaves += 1
        pg.T.test(clip, label=label, verdict="DEAD", leaf=leaf[:200])
        self.log("   node %-10s d%d: DEAD by %s -- %s" % (label, depth, clip, leaf[:170]))
        if self.on_node:
            self.on_node(self)

    def alive(self, why):
        NB.Tree206.leaf_alive(self, why)
        self.log("   node %-10s: ALIVE [%s]" % (self.nodes[-1]["label"], why[:150]))

    # ------------------------------------------------------------------ the leaf rules at a fully named node
    def leaf_rules(self, depth, label):
        pg = self.pg
        node = self.nodes[-1]
        caps = depth >= self.depth_cap or self.n_nodes >= self.node_cap
        if pg.T.out_of_time():
            self.alive("undecided (wall) at the fully named leaf before the leaf rules")
            return "ALIVE"
        t0 = time.time()                                                          # (a) rule CC
        rows = L11.cc_rows(pg, label)
        node["cc"] = dict(n_rows=len(rows), seconds=round(time.time() - t0, 3), rows=[{k: v for k, v in r.items() if k != "band"} for r in rows][:8])
        dead = [r for r in rows if r["verdict"] == "DEAD"]
        if dead:
            r = dead[0]
            self.cc_kills += 1
            self.kill(label, depth, "CC", "rule CC at %s (Lemma CORNER-COVER; %s pad, lam %s): %s" % (label, pg.pad, round(float(pg.lam), 6), r["why"]),
                      cc_slot=r["slot"], cc_role=r["role"], verifier=r["verifier"])
            return "DEAD"
        # (b) no-room + pockets: once per k along a path (an NS child adds no role: its boxes are subsets of the parent's,
        #     where the search was already UNDECIDED at the cap; a row / pocket child adds a role and runs it afresh)
        if len(pg.roles) >= 9 and not getattr(pg, "noroom_done", False) and len(pg.roles) != getattr(pg, "noroom_k", None):
            pg.noroom_done = True
            pg.noroom_k = len(pg.roles)
            res = N9.noroom_at(pg, min(pg.T.left() or 0.0, NOROOM_CAP + 30), log=self.log)
            rec = dict(label=label, depth=depth, k=res["k"], m=res["m"], verdict=res["verdict"], clip=res["clip"], bound=res["bound"], cn_bound=res["cn_bound"],
                       n_pockets=len(res["pockets"]), pockets=res["pockets"], seconds=res["seconds"], reason=res["reason"])
            self.noroom_runs.append(rec)
            node["noroom"] = rec
            if res["verdict"] == "DEAD":
                self.kill(label, depth, res["clip"], "no-room at %s (k=%d, m=%d; A189 Lemma 1%s on the role boxes): %s" % (
                    label, res["k"], res["m"], " + Lemma CN" if res["clip"] == "NOROOM-CN" else "", res["reason"]))
                return "DEAD"
            if res["m"] >= 2 and res["pockets"] and not caps and not pg.T.out_of_time():
                self.pocket_branches(depth, label, res["pockets"], res)
                return "BRANCHED"
        if pg.all_basins and not getattr(pg, "basin_done", False):                # (c) the basin clip
            pg.basin_done = True
            pg.basins = list(pg.all_basins)
            ok = pg.basin_clip(label)
            if pg.coarse:
                pg.basins = []
            if not ok:
                self.basin_kills += 1
                self.kill(label, depth, "BASIN", pg.dead)
                return "DEAD"
            for k, pcs in pg.pieces.items():
                if pcs and not k.startswith("P"):
                    pg.roles[k] = P.hull_box(pcs)
        cands = N6.ns_candidates(pg)                                              # (d) Rule NS, slivers only
        node["ns_candidates"] = cands
        if cands and not caps and not pg.T.out_of_time():
            self._ns = cands[0]
            return "NS"
        if pg.coarse:                                                             # (e) the exact cascade at the leaf
            t0 = time.time()
            pg.set_coarse(False)
            clip, rnd = N6.cascade(pg, EXACT_ROUNDS, log=self.log)
            self.n_nodes += 1
            self.exact_rounds += 1
            self.record(label + "x", depth, dict(slot=None, kind="exact", rows=None, named=None), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            return "DEAD" if pg.dead else "CONTINUE"
        if TB.SHARP and not getattr(pg, "sharpened", False):
            t0 = time.time()
            pg.refine_mb, pg.nsub_mb, pg.sharpened = 3, 8, True
            clip, rnd = N6.cascade(pg, 1, log=self.log)
            pg.refine_mb, pg.nsub_mb = 2, 4
            self.n_nodes += 1
            self.record(label + "s", depth, dict(slot=None, kind="sharp", rows=None, named=None), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            return "DEAD" if pg.dead else "CONTINUE"
        if cands:
            why = "depth cap" if depth >= self.depth_cap else ("node cap" if self.n_nodes >= self.node_cap else "wall")
            self.alive("undecided (%s) before Rule NS on %s at %s (frac %s)" % (why, cands[0]["role"], cands[0]["slot"], cands[0]["frac"]))
        else:
            soft = N6.ns_candidates.__globals__["SOFT_ALL"]
            self.alive("every forced slot has two named meeters after the exact cascade and the sharp round; no soft name below MAX_FRAC %s left to split (next lever: LP on the node)" % N6.MAX_FRAC)
        return "ALIVE"

    def pocket_branches(self, depth, label, pk, res):
        pg = self.pg
        self.pocket_splits += 1
        self.nodes[-1].update(branch_slot="pocket", n_branches=len(pk), branch_rows=[[j] for j in range(len(pk))], pockets=pk, verdict="INTERNAL", reason=None)
        self.log("   Lemma POCKET at %s: %d pockets (k=%d, m=%d): the 10th square instantiated in each" % (label, len(pk), res["k"], res["m"]))
        st = N6.save_state(pg)
        for j, pocket in enumerate(pk):
            lab = "%s.p%d" % (label, j + 1)
            br = dict(slot="pocket", kind="pocket", rows=[j], named=None, pocket=[round(v, 6) for v in pocket], diam=round(N9.diam(pocket), 4))
            info, _q, p = self.child_path(lab, label, br)
            if info is not None:
                self.record_inherited(lab, depth + 1, br, info, p)
                continue
            if pg.T.out_of_time() or self.n_nodes >= self.node_cap:
                NB.Tree206.undecided(self, lab, depth + 1, br, "undecided: %s before this pocket branch ran" % ("wall" if pg.T.out_of_time() else "node cap"))
                continue
            N6.restore_state(pg, st)
            self.fresh_child()
            t0 = time.time()
            role = N9.apply_pocket(pg, pocket, j)
            clip, rnd = N6.cascade(pg, self.rounds, log=self.log)
            self.n_nodes += 1
            r = self.record(lab, depth + 1, br, "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            r["pocket_role"] = role
            if not pg.dead:
                self.expand(depth + 1, lab)
        N6.restore_state(pg, st)

    # ------------------------------------------------------------------ the node
    def expand(self, depth, label):
        self._ctx.append((depth, label))
        try:
            return self._expand(depth, label)
        finally:
            self._ctx.pop()

    def _expand(self, depth, label):
        pg = self.pg
        ns = None
        while True:
            ch = TB.candidates(pg)
            n_stale = 0
            while ch == "stale" and n_stale < 4:
                t0 = time.time()
                clip, rnd = N6.cascade(pg, 1, log=self.log)
                self.n_nodes += 1
                n_stale += 1
                self.record(label + "r%d" % n_stale, depth, dict(slot=None, kind="refresh", rows=None, named=None), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
                if pg.dead:
                    return
                ch = TB.candidates(pg)
            if ch == "stale":
                return self.alive("undecided: the option table stayed stale after 4 refresh rounds")
            if ch is None:
                r = self.leaf_rules(depth, label)
                if r == "NS":
                    ns = self._ns
                    break
                if r == "CONTINUE":
                    continue
                return
            if not ch["branches"]:
                self.kill(label, depth, "S-PAIR", "S-PAIR at %s: no rule-S / A1 compatible pair among its %d alive rows %s (Theorem FC needs two anonymous meeters; excluded %s)" % (
                    ch["slot"], len(ch["rows"]), ch["rows"], ch["excluded"]))
                return
            if len(ch["branches"]) > 1:
                break
            br = ch["branches"][0]
            t0 = time.time()
            TB.apply_branch(pg, br)
            self.fresh_child()
            clip, rnd = N6.cascade(pg, self.rounds, log=self.log)
            self.n_nodes += 1
            self.record(label + "u", depth, dict(br, unit=True), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            if pg.dead:
                return
        if ns is not None:
            branches = N6.ns_branches(ns)
            self.ns_splits += 1
            self.nodes[-1].update(branch_slot=ns["slot"], branch_role=ns["role"], n_branches=2, branch_rows=["meets", "misses"], ns=ns, verdict="INTERNAL")
            self.log("   Rule NS at %s: split %s at %s (meeting fraction %s; alive rows %s; named %s)" % (label, ns["role"], ns["slot"], ns["frac"], ns["rows"], ns["named"]))
        else:
            if depth >= self.depth_cap or self.n_nodes >= self.node_cap or pg.T.out_of_time():
                why = "depth cap" if depth >= self.depth_cap else ("node cap" if self.n_nodes >= self.node_cap else "wall")
                return self.alive("undecided (%s) before branching on %s over %s" % (why, ch["slot"], [b["rows"] for b in ch["branches"]]))
            branches = ch["branches"]
            self.nodes[-1].update(branch_slot=ch["slot"], n_branches=len(branches), branch_rows=[b["rows"] for b in branches])
        st = N6.save_state(pg)
        for i, br in enumerate(branches):
            lab = "%s.%d" % (label, i + 1)
            info, _q, p = self.child_path(lab, label, br)
            if info is not None:
                self.record_inherited(lab, depth + 1, br, info, p)
                continue
            if not self.on_path(lab):
                self.undecided(lab, depth + 1, br, "undecided: skipped (not on the requested path %s)" % self.only)
                continue
            if pg.T.out_of_time() or self.n_nodes >= self.node_cap:
                self.undecided(lab, depth + 1, br, "undecided: %s before this branch ran" % ("wall" if pg.T.out_of_time() else "node cap"))
                continue
            N6.restore_state(pg, st)
            self.fresh_child()
            t0 = time.time()
            if str(br.get("kind", "")).startswith("ns-"):
                N6.apply_ns(pg, br)
            else:
                TB.apply_branch(pg, br)
            clip, rnd = N6.cascade(pg, self.rounds, log=self.log)
            self.n_nodes += 1
            self.record(lab, depth + 1, br, "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            if not pg.dead:
                self.expand(depth + 1, lab)
        N6.restore_state(pg, st)

    def result(self):
        out = N9.Tree209.result(self)
        out.update(cc_kills=self.cc_kills, exact_rounds=self.exact_rounds, basin_kills=self.basin_kills, n_inherited=self.n_inherited)
        return out
