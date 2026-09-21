"""A256 -- Tree256: A211's CURRENT Tree211 with the trump5 GATE and the two tube leaves.

  (1) the GATE (A212 notes/trump5_tree.md s.1, extended to the RAY by ray256): every node record carries
      `trump_gate`; a node the gate accepts is never KILLED -- a rule that returns DEAD there is recorded
      `gate_conflict` and the node is left ALIVE.  Skipping a kill proves nothing, so this cannot make an unsound
      DEAD; soundness of the tree never depends on the gate.
  (2) Lemma TUBE-LEAF (A212 s.2, pad 0): the node's pieces localise all eleven squares inside the tube box about a
      D4 image of z-hat embedded at s0 -- the (D) leaf of docs/proofs/k0_route.md s.4.2.
  (3) Lemma TUBE-KILL (NEW, notes/trump5_closure.md s.3): the same localisation at a WINDOW pad, with the pin-slack
      condition of Lemma SEAM, turns Theorem T1 into a KILL for every side m < s-hat plus uniqueness at s-hat.

Tree256 is OFF by default (run256.py --tube).  Its domain on A212's 149 nodes is EMPTY (results/triage256.json:
(a) 149, (b) 0), so the plain chain is what the loop runs; this file exists so that the leaf is there, stated and
implemented, the first time a class-(b) node appears.

NOT ported from A212: the ALIGNED split (tree212.py s.3 / expand212.py), which needs a fork of A211's current
`_expand` (A224 Rule SNAP, A230 Rule EPS and the A220 levers all live in it now).  A gated node here is cut by
A211's own Lemma ROLE-SPLIT instead -- sound, and less targeted; porting the aligned cut is the first thing to do
if a class-(b) node is ever found (notes/trump5_closure.md s.3, open link O4).
"""
import os
import time

import tree211 as N11
import trump256 as TR
import ray256 as RAY

VERIFIER256 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "certs", "verify_tubekill256.py")
SHAT = None


def seam_ok(pad, dpin):
    """Lemma SEAM's (K) condition for the pad's slab: T_K(delta_pin) >= T' = s-hat - s_bot, A = 3/2 for trump5.

    T_K(d) = ((2/3) d s-hat - (s0 - s-hat)) / (1 + (2/3) d)   [contraction_tube.md s.4.1]
    -> dict(ok, T_prime, T_K, s_bot).  A pad-0 node has T' = 0 and the condition is vacuous (the leaf is TUBE-LEAF,
    an s0-only localisation, not a kill)."""
    global SHAT
    if SHAT is None:
        SHAT = TR.shat()
    s0, lam = TR.S0, RAY.PADS[pad]
    s_bot = s0 / lam
    Tp = SHAT - s_bot if lam > 1 else 0 * s0
    d = TR.Fr(str(dpin))
    TK = ((TR.Fr(2, 3) * d * SHAT) - (s0 - SHAT)) / (1 + TR.Fr(2, 3) * d)
    return dict(ok=bool(Tp <= TK), T_prime=float(Tp), T_K=float(TK), s_bot=float(s_bot),
                delta_pin=float(dpin), A="3/2 (trump5 pins ride slots with |alpha| <= 3/2)")


def tube_cert_ok(T_prime, radii):
    """hypothesis (iii): a certified slot-ray tube whose depth covers T' at the node's radii."""
    return bool(TR.Fr(str(radii["T"])) >= TR.Fr(str(T_prime)))


class Tree256(N11.Tree211):
    def __init__(self, pg, **kw):
        N11.Tree211.__init__(self, pg, **kw)
        self.gate_hits, self.gate_conflicts, self.tube_leaves, self.tube_kills = 0, 0, 0, 0
        self.tube_rows, self.gate_log = [], []

    # ------------------------------------------------------------------ the gate on every node
    def gate_now(self, label, when):
        g = TR.gate(self.pg)
        self.gate_log.append(dict(label=label, when=when, contains=g["contains"], g=g["g"], seconds=g["seconds"]))
        return g

    def record(self, label, depth, br, verdict, clip, rnd, t0, reason=None):
        r = N11.Tree211.record(self, label, depth, br, verdict, clip, rnd, t0, reason=reason)
        post = self.gate_now(label, "after-cascade") if verdict != "DEAD" else dict(contains=False, g=None, assignment=None, pins=None, seconds=0.0)
        r["trump_gate"] = dict(post)
        if post.get("contains"):
            self.gate_hits += 1
            self.log("   GATE %s: contains the Trump image %s (%s); no kill rule will be applied here" % (label, post["g"], post["assignment"]))
        return r

    def kill(self, label, depth, clip, leaf, **extra):
        tg = (self.nodes[-1].get("trump_gate") or {}) if self.nodes else {}
        if tg.get("contains"):
            self.gate_conflicts += 1
            why = ("GATE-CONFLICT at %s: rule %s claims DEAD on a node that contains the image %s -- refused, left "
                   "ALIVE (A212 notes/trump5_tree.md s.1): %s" % (label, clip, tg.get("g"), str(leaf)[:160]))
            self.nodes[-1]["gate_conflict"] = dict(rule=clip, leaf=str(leaf)[:400])
            self.log("   !! " + why[:220])
            return self.alive(why)
        return N11.Tree211.kill(self, label, depth, clip, leaf, **extra)

    # ------------------------------------------------------------------ the two tube leaves
    def tube_try(self, depth, label, tg):
        """-> "TUBE" when Lemma TUBE-LEAF (pad 0) or Lemma TUBE-KILL (a window pad) closes the node, else None."""
        pg = self.pg
        node = self.nodes[-1]
        if pg.n_free - len(pg.role_cell) > 0:                      # hypothesis (i): all eleven squares named
            node["tube"] = dict(fits=False, why="anonymous square(s) left: %d" % (pg.n_free - len(pg.role_cell)))
            return None
        pad0 = getattr(pg, "pad", "zero") == "zero"
        ray = "scale" if pad0 else "slot"                          # the WINDOW leaf rides the slot ray (trump256 s.RAY_CERT)
        tb = TR.tube(pg, tg["g"], tg["assignment"], tg["pins"], ray=ray)   # hypothesis (ii): pieces inside the tube box
        node["tube"] = tb
        if not tb["fits"]:
            return None
        pad = getattr(pg, "pad", "zero")
        dpin = max(float(p.get("dpin") or 0.0) for p in pg.rec["pins"])
        seam = seam_ok(pad, dpin)
        node["tube_seam"] = seam
        cert_ok = tube_cert_ok(seam["T_prime"], tb["radii"])       # hypothesis (iii)
        if pad == "zero":
            return self.tube_leaf(depth, label, tb, seam)
        if not (seam["ok"] and cert_ok):                           # hypothesis (iv) fails: NEVER stretch the lemma
            self.alive("gated node, all 11 named, the tube box FITS, but Lemma TUBE-KILL's hypotheses do not hold at "
                       "pad %s: T' = %.5f, T_K(delta_pin = %g) = %.5f, tube certificate T = %s -- the node stays ALIVE "
                       "(the record must be re-emitted with delta_pin >= %.4g; contraction_tube.md s.4.4 item 1)"
                       % (pad, seam["T_prime"], seam["delta_pin"], seam["T_K"], tb["radii"]["T"],
                          1.5 * (seam["T_prime"] + 4.1e-7) / max(1e-9, (float(TR.shat()) - seam["T_prime"]))))
            return "ALIVE"
        return self.tube_kill(depth, label, tb, seam)

    def tube_leaf(self, depth, label, tb, seam):
        self.tube_leaves += 1
        leaf = ("TRUMP-TUBE at %s (Lemma TUBE-LEAF, A212 notes/trump5_tree.md s.2): all 11 squares named and every "
                "piece inside the tube box (r_c' = %s, r_theta = %s; %s) about the image %s -- every packing at s0 in "
                "this node lies within the radii of the image.  s0-only: NOT a kill." % (
                    tb["r_c_eff_float"], tb["radii"]["r_theta"], tb["radii"]["cert"], tb["g"]))
        self.nodes[-1].update(verdict="TRUMP-TUBE", clip="TRUMP-TUBE", leaf=leaf, tube_depth=depth, reason=None,
                              verifier="[C: exact containment of the node's pieces in the tube box + Theorem T1 "
                                       "(certs/verify_tube.py on %s); checked by certs/verify_tubekill256.py]" % tb["radii"]["cert"])
        self.tube_rows.append(dict(label=label, kind="TUBE-LEAF", g=tb["g"], seam=seam))
        self.pg.T.test("TRUMP-TUBE", label=label, g=tb["g"], fits=True)
        self.log("   node %-10s d%d: TRUMP-TUBE (image %s)" % (label, depth, tb["g"]))
        return "TUBE"

    def tube_kill(self, depth, label, tb, seam):
        self.tube_kills += 1
        leaf = ("TUBE-KILL at %s (Lemma TUBE-KILL, notes/trump5_closure.md s.3, on docs/proofs/contraction_tube.md "
                "Theorem T1 + Lemma SEAM s.4.1): all 11 squares named; every piece inside the tube box "
                "(r_c' = %s, r_theta = %s) about the image %s; the class pins ride slots(m) exactly, so the slot-ray "
                "pull-back has w_pin = 0, w_free <= r_c, w_theta <= r_theta, w_s = 0 at depth t = s-hat - m; the slab "
                "needs T' = %.6f and %s certifies T = %s; Lemma SEAM's (K) condition holds "
                "(T_K(delta_pin = %g) = %.6f >= T').  Therefore NO packing satisfying this node exists at any side "
                "m < s-hat, and at m = s-hat the only one is %s . z-hat (T1's equality clause).  The node is NOT "
                "claimed dead for m in (s-hat, s0]: that sliver lies above the target side and is irrelevant to "
                "s(11) >= s-hat." % (tb["r_c_eff_float"], tb["radii"]["r_theta"], tb["g"], seam["T_prime"],
                                     tb["radii"]["cert"], tb["radii"]["T"], seam["delta_pin"], seam["T_K"], tb["g"]))
        self.nodes[-1].update(verdict="TUBE-KILL", clip="TUBE-KILL", leaf=leaf, tube_depth=depth, reason=None,
                              verifier="[V: certs/verify_tubekill256.py -- re-checks hypotheses (i)-(iv) of Lemma "
                                       "TUBE-KILL against this node's snapshot and re-runs certs/verify_tube.py on %s]" % tb["radii"]["cert"])
        self.tube_rows.append(dict(label=label, kind="TUBE-KILL", g=tb["g"], seam=seam, radii=tb["radii"]))
        self.pg.T.test("TUBE-KILL", label=label, g=tb["g"], T_prime=seam["T_prime"], T_K=seam["T_K"])
        self.log("   node %-10s d%d: TUBE-KILL (image %s; T' %.5f <= T_K %.5f)" % (label, depth, tb["g"], seam["T_prime"], seam["T_K"]))
        return "TUBE"

    def leaf_rules(self, depth, label):
        tg = (self.nodes[-1].get("trump_gate") or {}) if self.nodes else {}
        if tg.get("contains"):
            t0 = time.time()
            r = self.tube_try(depth, label, tg)
            if r is not None:
                return "ALIVE" if r == "ALIVE" else "TUBE"
            self.log("   gated leaf %s: no tube leaf (%.1f s) -- A211's branching levers only" % (label, time.time() - t0))
        return N11.Tree211.leaf_rules(self, depth, label)

    def result(self):
        out = N11.Tree211.result(self)
        if out["verdict"] != "DEAD" and self.alive_leaves == 0 and (self.tube_leaves or self.tube_kills):
            out["verdict"] = "TUBE-KILL" if self.tube_kills else "TRUMP-TUBE"
        out.update(gate_hits=self.gate_hits, gate_conflicts=self.gate_conflicts, tube_leaves=self.tube_leaves,
                   tube_kills=self.tube_kills, tube_rows=self.tube_rows, gate_log=self.gate_log[-400:])
        return out
