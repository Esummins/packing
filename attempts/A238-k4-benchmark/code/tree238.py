"""A238 -- Tree238 = A211's CURRENT coarse tree (the k5 toolkit: A220 exact-first / no-room inherit, A221 pocket
cover, A224 Rule SNAP with the k+1 hand-off, A230 Rule EPS, rule CC, A208 no-room, A207 basin clip, A206 Rule NS,
the exact A204/A205 cascade) with A212's TRUMP-CONTAINMENT GATE and the class TUBE LEAF bolted on.

Why not A212's `tree212.Tree212` directly: A212's attempt directory carries FROZEN COPIES of tree211 / tree206 /
tree209 / coarse211 / leaves211 from 2026-09-11, i.e. BEFORE A220 / A224 / A230.  Running the benchmark on those
would price a toolkit nobody uses.  Tree238 therefore re-applies A212's three rules (notes/trump5_tree.md s.1-s.3)
to A211's live Tree211, which is exactly the class the five running k5 frontier workers use:

  1. the GATE (s.1) on every node, before and after its cascade: a node whose pieces admit an injective assignment of
     its named squares to the squares of a D4 image of z-hat embedded at s0 is NEVER killed -- a rule or a cascade
     claiming DEAD there records `gate_conflict` and the node is left ALIVE.  On a Trump PARENT class the root
     itself is gated (the class's pins ARE four/three of Trump's simple squares), so the gate is the thing that
     separates "the branch that still holds Trump" from "the branch that does not" -- and the second kind is what
     the geometry is being measured on;
  2. the TUBE LEAF (s.2, here Lemma TUBE-LEAF/S of tube238.py): a gated node with all eleven squares named whose
     non-pin pieces lie inside the class direction's tube box is a (D) discharge, recorded TRUMP-TUBE, not a kill;
  3. Rule SNAP is run FIRST at a gated fully named leaf (A224): on a Trump parent the fifth simple square is
     precisely what a near-simple role snaps to, and the target stratum decides -- trump5 (OPEN: a HAND-OFF, the
     branch leaves this class and joins trump5's queue) or a closed k5 class (DEAD by Lemma K1).

A212's ALIGNED split (s.3) is NOT re-applied: A212 s.6 measured that a gated node needs ~36 aligned cuts to reach
the tube box and that its near-Trump siblings do not die inside a wall, so the cuts would burn the whole benchmark
wall on the one cell per class that holds the image.  A gated fully named leaf is instead left ALIVE with its tube
EXCESS recorded (`tube` on the node record), i.e. "tube-pending: the (D) discharge needs the contraction lever of
A60/A83, not more branching" -- which is the honest reading of A212 s.6 and is reported as such.

Nothing in A211 / A212 / A224 is edited."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import path238                                                  # noqa: E402
path238.fix()
import tree211 as N11                                           # noqa: E402  READ-ONLY (A211, the LIVE toolkit)
import tube238 as TU                                            # noqa: E402

BASE = N11.Tree211
SNAP_AT_GATE = (os.environ.get("A238_SNAP_AT_GATE") or "1") == "1"
GATE_ON = (os.environ.get("A238_GATE") or "1") == "1"


class Tree238(BASE):
    def __init__(self, pg, **kw):
        BASE.__init__(self, pg, **kw)
        self.gate_hits, self.gate_conflicts, self.tube_leaves, self.tube_pending = 0, 0, 0, 0
        self.gated_snaps, self.tube_depths, self.gate_log, self.rule_log = 0, [], [], []
        self._pre_gate = None

    # ------------------------------------------------------------------ the gate (A212 s.1)
    def gate_now(self, label, when):
        if not GATE_ON:
            return dict(contains=False, g=None, assignment=None, pins=None, checks=[], seconds=0.0)
        g = TU.gate(self.pg)
        self.gate_log.append(dict(label=label, when=when, contains=g["contains"], g=g["g"], seconds=g["seconds"]))
        return g

    def run(self):
        self._pre_gate = self.gate_now(self.root_label, "root-before-cascade")
        return BASE.run(self)

    def record(self, label, depth, br, verdict, clip, rnd, t0, reason=None):
        pre, self._pre_gate = self._pre_gate, None
        if verdict == "DEAD" and pre and pre.get("contains"):
            self.gate_conflicts += 1
            why = ("GATE-CONFLICT at %s: the pieces this node was branched into contain the image %s, yet the cascade "
                   "returned DEAD (%s) -- left ALIVE, not a kill (A212 notes/trump5_tree.md s.1)" % (label, pre.get("g"), str(self.pg.dead)[:160]))
            self.pg.dead = None
            r = BASE.record(self, label, depth, br, "ALIVE", None, rnd, t0, reason=why)
            r["gate_conflict"] = dict(rule=clip, pre_gate=pre)
            self.log("   !! " + why[:200])
        else:
            r = BASE.record(self, label, depth, br, verdict, clip, rnd, t0, reason=reason)
        post = self.gate_now(label, "after-cascade") if r.get("verdict") != "DEAD" else dict(contains=False, g=None, assignment=None, pins=None, seconds=0.0, checks=[])
        r["trump_gate"] = dict(post, pre=(dict(contains=pre.get("contains"), g=pre.get("g")) if pre else None))
        if post["contains"]:
            self.gate_hits += 1
            self.log("   GATE %s: contains the Trump image %s (%s); no kill rule will be applied here" % (label, post["g"], post["assignment"]))
        r["a238"] = dict(rule=r.get("clip"), verdict=r.get("verdict"), depth=depth, seconds=r.get("seconds"),
                         gated=bool(post.get("contains")), snap=(r.get("snap") or {}).get("verdict"),
                         eps=(r.get("eps") or {}).get("verdict"))
        self.rule_log.append(dict(label=label, **r["a238"]))
        return r

    def kill(self, label, depth, clip, leaf, **extra):
        tg = (self.nodes[-1].get("trump_gate") or {}) if self.nodes else {}
        if tg.get("contains"):
            self.gate_conflicts += 1
            why = ("GATE-CONFLICT at %s: rule %s claims DEAD on a node that contains the image %s -- refused, left "
                   "ALIVE (A212 s.1): %s" % (label, clip, tg.get("g"), leaf[:160]))
            self.nodes[-1]["gate_conflict"] = dict(rule=clip, leaf=leaf)
            self.log("   !! " + why[:220])
            return self.alive(why)
        return BASE.kill(self, label, depth, clip, leaf, **extra)

    # ------------------------------------------------------------------ the leaf of a GATED node
    def tube_leaf(self, label, depth, tb):
        n = self.nodes[-1]
        self.tube_leaves += 1
        self.tube_depths.append(depth)
        leaf = ("TRUMP-TUBE at %s (Lemma TUBE-LEAF/S, attempts/A238-k4-benchmark/code/tube238.py): all 11 squares "
                "named; the %d pins sit on their slots (clause (P): M_S pins those coordinates exactly, so they are "
                "the tube direction's PINNED coordinates) and every piece of every non-pin role lies inside the tube "
                "box (r_c' = %s, r_theta = %s rad) about the image %s in the direction %s (%s).  By Lemma P-TREE "
                "Step 4 + Theorem T1 every window packing satisfying this node's hypothesis is that image at m = "
                "s-hat and none exists below -- a (D) discharge for the stratum, NOT a kill." % (
                    label, len(self.pg.pins), tb["r_c_eff_float"], tb["radii"]["r_theta"], tb["g"], tb["direction"], tb["radii"]["cert"]))
        n.update(verdict="TRUMP-TUBE", clip="TRUMP-TUBE", leaf=leaf, tube=tb, tube_depth=depth, reason=None,
                 verifier="[C: exact containment of the node's pieces in the class tube box + Theorem T1 (certs/verify_tube.py on %s)]" % tb["radii"]["cert"])
        self.pg.T.test("TRUMP-TUBE", label=label, g=tb["g"], depth=depth, fits=True)
        self.log("   node %-10s d%d: TRUMP-TUBE (image %s, direction %s)" % (label, depth, tb["g"], tb["direction"]))
        if self.on_node:
            self.on_node(self)

    def trump_leaf(self, depth, label, tg):
        pg, node = self.pg, self.nodes[-1]
        if pg.T.out_of_time():
            self.alive("undecided (wall) at the gated fully named leaf")
            return "ALIVE"
        if SNAP_AT_GATE:                                          # A224 first: the fifth simple square is the point
            s = self.snap_try(depth, label, "gated-leaf")
            if s != "OK":
                self.gated_snaps += 1
                return s
        n_anon = pg.n_free - len(pg.role_cell)
        node["n_anon"] = n_anon
        if n_anon > 0:
            self.alive("gated node with %d anonymous square(s) left (k = %d roles): it holds the Trump image, so no "
                       "kill rule may be applied; the tube leaf needs every square named" % (n_anon, len(pg.roles)))
            return "ALIVE"
        t0 = time.time()
        tb = TU.tube(pg, tg["g"], tg["assignment"], tg["pins"])
        tb["seconds"] = round(time.time() - t0, 3)
        node["tube"] = tb
        if tb["fits"]:
            self.tube_leaf(label, depth, tb)
            return "TUBE"
        self.tube_pending += 1
        self.alive("TUBE-PENDING: gated, all 11 named, the class tube box NOT fitted (worst %s at %.1f x the radius; "
                   "direction %s).  A212 s.6 measured that aligned cuts need ~36 levels to reach it: the (D) discharge "
                   "needs the contraction lever (A60's LP ladder / A83's basin clip), not more branching." % (
                       (tb.get("worst") or ["?"])[0], (tb.get("worst") or [0, 0])[1], tb["direction"]))
        return "ALIVE"

    def leaf_rules(self, depth, label):
        tg = (self.nodes[-1].get("trump_gate") or {}) if self.nodes else {}
        if tg.get("contains"):
            return self.trump_leaf(depth, label, tg)
        return BASE.leaf_rules(self, depth, label)

    def result(self):
        out = BASE.result(self)
        if out["verdict"] != "DEAD" and self.alive_leaves == 0 and self.tube_leaves > 0:
            out["verdict"] = "TRUMP-TUBE"
        out.update(gate_hits=self.gate_hits, gate_conflicts=self.gate_conflicts, tube_leaves=self.tube_leaves,
                   tube_pending=self.tube_pending, gated_snaps=self.gated_snaps, tube_depths=self.tube_depths,
                   gate_log=self.gate_log[-400:], rule_log=self.rule_log[-600:],
                   tube_nodes=[dict(label=n["label"], depth=n.get("depth"), g=(n.get("tube") or {}).get("g"))
                               for n in self.nodes if n.get("verdict") == "TRUMP-TUBE"])
        return out
