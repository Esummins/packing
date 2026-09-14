"""A212 -- the TRUMP5 TREE (notes/trump5_tree.md): A211's Tree211 with
  1. the GATE (s.1): every node's record carries `trump_gate` (computed on the pieces the node was branched INTO, before its
     cascade, and again after it); a gated node is never killed -- kill() and a DEAD cascade on a gated node record
     `gate_conflict` and leave the node ALIVE; its leaf rules are only the BRANCHING levers (rows / pairs by Lemma CT,
     Lemma POCKET with no-room run for its cover only, Rule NS, the aligned split);
  2. the TUBE LEAF (s.2): a gated node with all eleven squares named whose pieces fit the tube box is recorded
     TRUMP-TUBE (a uniqueness leaf, not a kill);
  3. the ALIGNED split (s.3): otherwise Lemma ROLE-SPLIT cut at the tube wall, <= TRUMP_SPLIT_CAP cuts on a path.
Ungated nodes run A211's rules unchanged (pad 0: lam = 1)."""
import time

import tree205b as TB
import tree206 as N6
import tree209 as N9
import rsplit211 as RS
import tree211 as N11
import trump212 as TR
import expand212 as EX

TRUMP_SPLIT_CAP = 36


class Tree212(N11.Tree211):
    def __init__(self, pg, **kw):
        N11.Tree211.__init__(self, pg, **kw)
        self.gate_hits, self.gate_conflicts, self.tube_leaves, self.aligned_cuts = 0, 0, 0, 0
        self.tube_depths, self.gate_log = [], []
        self._pre_gate = None

    # ------------------------------------------------------------------ the gate on every node
    def gate_now(self, label, when):
        g = TR.gate(self.pg)
        self.gate_log.append(dict(label=label, when=when, contains=g["contains"], g=g["g"], seconds=g["seconds"]))
        return g

    def aligned_on_path(self, label):
        return sum(1 for s in self.pathof.get(label, ()) if s and s[0] == "rsplit" and len(s) > 5 and s[5] == "aligned")

    def step_key(self, br):
        k = N11.Tree211.step_key(self, br)
        if k[0] == "rsplit" and br.get("aligned"):
            return k + ("aligned",)                       # the same hypothesis; the marker only counts the cuts (s.3)
        return k

    def record(self, label, depth, br, verdict, clip, rnd, t0, reason=None):
        pre, self._pre_gate = self._pre_gate, None
        if verdict == "DEAD" and pre and pre.get("contains"):
            self.gate_conflicts += 1
            why = "GATE-CONFLICT at %s: the pieces this node was branched into contain the image %s, yet the cascade returned DEAD (%s) -- left ALIVE, not a kill (notes/trump5_tree.md s.1)" % (label, pre.get("g"), str(self.pg.dead)[:160])
            self.pg.dead = None
            r = N11.Tree211.record(self, label, depth, br, "ALIVE", None, rnd, t0, reason=why)
            r["gate_conflict"] = dict(rule=clip, pre_gate=pre)
            self.log("   !! " + why[:200])
        else:
            r = N11.Tree211.record(self, label, depth, br, verdict, clip, rnd, t0, reason=reason)
        post = self.gate_now(label, "after-cascade") if verdict != "DEAD" else dict(contains=False, g=None, assignment=None, pins=None, seconds=0.0, checks=[])
        r["trump_gate"] = dict(post, pre=(dict(contains=pre.get("contains"), g=pre.get("g")) if pre else None))
        if post["contains"]:
            self.gate_hits += 1
            self.log("   GATE %s: contains the Trump image %s (%s); no kill rule will be applied here" % (label, post["g"], post["assignment"]))
        return r

    def kill(self, label, depth, clip, leaf, **extra):
        tg = (self.nodes[-1].get("trump_gate") or {})
        if tg.get("contains"):
            self.gate_conflicts += 1
            why = "GATE-CONFLICT at %s: rule %s claims DEAD on a node that contains the image %s -- refused, left ALIVE (notes/trump5_tree.md s.1): %s" % (label, clip, tg.get("g"), leaf[:160])
            self.nodes[-1]["gate_conflict"] = dict(rule=clip, leaf=leaf)
            self.log("   !! " + why[:220])
            return self.alive(why)
        return N11.Tree211.kill(self, label, depth, clip, leaf, **extra)

    def run(self):
        self._pre_gate = self.gate_now(self.root_label, "root-before-cascade")
        return N11.Tree211.run(self)

    # ------------------------------------------------------------------ the tube leaf
    def tube_leaf(self, label, depth, tb):
        pg = self.pg
        n = self.nodes[-1]
        cuts = self.aligned_on_path(label)
        self.tube_leaves += 1
        self.tube_depths.append(cuts)
        leaf = ("TRUMP-TUBE at %s (Lemma TUBE-LEAF, notes/trump5_tree.md s.2): all 11 squares named and every piece inside the tube box "
                "(r_c' = %s, r_theta = %s rad; %s) about the image %s -- every packing at s0 in this node lies within the radii of the image, "
                "and by Theorem T1 on the scale-ray tube every window packing whose dilate satisfies it is the image at s-hat; %d aligned cuts on the path, depth %d" % (
                    tb["r_c_eff_float"], tb["radii"]["r_theta"], tb["radii"]["cert"], tb["g"], cuts, depth))
        n.update(verdict="TRUMP-TUBE", clip="TRUMP-TUBE", leaf=leaf, tube=tb, tube_depth=cuts, reason=None,
                 verifier="[C: exact containment of the node's pieces in the tube box + Theorem T1 (certs/verify_tube.py on %s)]" % tb["radii"]["cert"])
        pg.T.test("TRUMP-TUBE", label=label, g=tb["g"], cuts=cuts, fits=True)
        self.log("   node %-10s d%d: TRUMP-TUBE (image %s; %d aligned cuts)" % (label, depth, tb["g"], cuts))
        if self.on_node:
            self.on_node(self)

    def trump_leaf(self, depth, label, tg):
        """the leaf rules of a GATED fully named node: only branching levers (s.1), the tube check (s.2), the aligned split (s.3)."""
        pg = self.pg
        node = self.nodes[-1]
        caps = self.eff_depth(depth, label) >= self.depth_cap or self.n_nodes >= self.node_cap
        if pg.T.out_of_time():
            self.alive("undecided (wall) at the gated fully named leaf")
            return "ALIVE"
        n_anon = pg.n_free - len(pg.role_cell)
        node["n_anon"] = n_anon
        if n_anon <= 0:
            tb = TR.tube(pg, tg["g"], tg["assignment"], tg["pins"])
            node["tube"] = tb
            if tb["fits"]:
                self.tube_leaf(label, depth, tb)
                return "TUBE"
            cuts = self.aligned_on_path(label)
            sp = TR.aligned_split(pg, tg["g"], tg["assignment"]) if cuts < TRUMP_SPLIT_CAP else None
            node["aligned_candidate"] = None if sp is None else dict(sp, m=str(sp["m"]))
            if sp is not None and self.n_nodes < self.node_cap and not pg.T.out_of_time():
                self._rs = dict(sp, aligned=True)
                return "RSPLIT"
            self.alive("gated node, all 11 named, the tube box NOT fitted (worst %s at %.1f x the radius) and %s" % (
                (tb.get("worst") or ["?"])[0], (tb.get("worst") or [0, 0])[1], "the aligned-cut cap %d reached" % TRUMP_SPLIT_CAP if cuts >= TRUMP_SPLIT_CAP else ("no cut found" if sp is None else "the node cap / wall")))
            return "ALIVE"
        # anonymous squares remain: Lemma POCKET's cover (no-room run for its pockets ONLY), then Rule NS, then the exact cascade
        if len(pg.roles) >= 9 and not node.get("noroom"):
            res = N9.noroom_at(pg, min(pg.T.left() or 0.0, N11.NOROOM_CAP + 30), log=self.log)
            rec = dict(label=label, depth=depth, k=res["k"], m=res["m"], verdict=res["verdict"], clip=res["clip"], bound=res["bound"], cn_bound=res["cn_bound"],
                       n_pockets=len(res["pockets"]), pockets=res["pockets"], seconds=res["seconds"], reason=res["reason"], gated=True, used_for="pocket cover only")
            self.noroom_runs.append(rec)
            node["noroom"] = rec
            if res["verdict"] == "DEAD":
                self.gate_conflicts += 1
                node["gate_conflict"] = dict(rule=res["clip"], leaf=res["reason"])
                self.alive("GATE-CONFLICT at %s: no-room claims DEAD (%s) on a gated node -- refused, ALIVE" % (label, res["clip"]))
                return "ALIVE"
            if res["pockets"] and not caps and not pg.T.out_of_time():
                self.pocket_branches(depth, label, res["pockets"], res)
                return "BRANCHED"
        cands = N6.ns_candidates(pg)
        node["ns_candidates"] = cands
        if cands and not caps and not pg.T.out_of_time():
            self._ns = cands[0]
            return "NS"
        if pg.coarse:
            t0 = time.time()
            pg.set_coarse(False)
            self._pre_gate = tg
            clip, rnd = N6.cascade(pg, N11.EXACT_ROUNDS, log=self.log)
            self.n_nodes += 1
            self.exact_rounds += 1
            r = self.record(label + "x", depth, dict(slot=None, kind="exact", rows=None, named=None), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            return "CONTINUE" if r.get("verdict") == "INTERNAL" else r.get("verdict")
        self.alive("gated node with %d anonymous square(s) left (k = %d): no pocket cover, no Rule-NS sliver, the exact cascade ran -- no lever names the last squares" % (n_anon, len(pg.roles)))
        return "ALIVE"

    def leaf_rules(self, depth, label):
        tg = self.nodes[-1].get("trump_gate") or {}
        if tg.get("contains"):
            return self.trump_leaf(depth, label, tg)
        return N11.Tree211.leaf_rules(self, depth, label)

    def apply_child(self, lab, br):
        return EX.apply_child(self, lab, br)

    def aligned_branches(self, sp):
        return EX.aligned_branches(self, sp)

    def pocket_branches(self, depth, label, pk, res):
        return EX.pocket_branches(self, depth, label, pk, res)

    def run_children(self, depth, label, branches, st, sep="."):
        return EX.run_children(self, depth, label, branches, st, sep)

    def _expand(self, depth, label):
        return EX._expand(self, depth, label)

    def result(self):
        out = N11.Tree211.result(self)
        if out["verdict"] != "DEAD" and self.alive_leaves == 0 and self.tube_leaves > 0:
            out["verdict"] = "TRUMP-TUBE"
        out.update(gate_hits=self.gate_hits, gate_conflicts=self.gate_conflicts, tube_leaves=self.tube_leaves, aligned_cuts=self.aligned_cuts,
                   tube_depths=self.tube_depths, gate_log=self.gate_log[-400:],
                   tube_nodes=[dict(label=n["label"], depth=n.get("depth"), g=(n.get("tube") or {}).get("g"), cuts=n.get("tube_depth")) for n in self.nodes if n.get("verdict") == "TRUMP-TUBE"])
        return out
