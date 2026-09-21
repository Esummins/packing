"""A257 -- Tree257: A256's Tree256 (the trump5 GATE + Lemma TUBE-LEAF + Lemma TUBE-KILL, which is A211's CURRENT
Tree211) with the two things the window pilot needs, and nothing else.

  O4  the **ALIGNED split** (A212 notes/trump5_tree.md s.3) on A211's CURRENT chain.  A256 s.3 records it as
      "NOT ported ... needs a fork of A211's current `_expand`".  **It does not.**  A211's `_expand` turns a leaf
      rule's "RSPLIT" hand-back into children by `RS.branches(self._rs)` and `RS.apply_rsplit`, both of which are
      pure functions of a spec dict (role, dim, m, side, extents, core_empty, box).  So the aligned cut is installed
      by handing back an RS-SHAPED spec whose `m` is the tube wall instead of the midpoint: no fork, every A220 /
      A221 / A224 / A228 / A229 / A230 lever in `_expand` untouched, and Lemma ROLE-SPLIT's own soundness argument
      (any m inside the hull gives two exhaustive children) is the one that licenses it -- unchanged.
  (ii) the **slot-ray tube containment** of `trump257.tube_slot` in place of `trump256.tube` at a window pad: see
      trump257.py -- A256's version boxes the PINS too, which Lemma TUBE-KILL (ii) does not ask and which cannot
      pass once the pins carry the delta_pin = 1e-2 slack the window needs.

Also fixed here, and reported upward: `tree256.tube_try` takes **max** over the pins' delta_pin when it forms Lemma
SEAM's (K) condition.  T_K is increasing in delta_pin and Corollary B' must hold for EVERY pin, so the binding slack
is the **minimum**; max is the unsound direction.  A256 has emitted no TUBE-KILL (its class-(b) domain is empty), so
nothing on disk is affected.  Tree257 uses min.

A gated node here runs A212's `trump_leaf` (branching levers only, never a kill rule), rebased on A211's current
helpers: that is what lets the spine descend to the tube instead of being stopped by rule CC returning DEAD."""
import time

import tree206 as N6
import tree209 as N9
import rsplit211 as RS
import tree211 as N11
import tree256 as N56
import trump257 as TR7

TRUMP_SPLIT_CAP = 36                   # A212 s.3: two cuts per coordinate x 3 coordinates x 6 non-pin roles


def aligned_spec(pg, sp):
    """A212's tube-wall cut as an RS.branches / RS.apply_rsplit spec (Lemma ROLE-SPLIT with m at the wall)."""
    x0, x1, y0, y1, t0, t1 = RS.hull_of(pg.pieces.get(sp["role"]) or [])
    return dict(sp, aligned=True, n_splits=0, n_pieces=len(pg.pieces.get(sp["role"]) or []),
                core_empty=bool((getattr(pg, "obst", None) or {}).get(sp["role"]) is None),
                extents=dict(x=round(float(x1 - x0), 6), y=round(float(y1 - y0), 6),
                             tilt=round(RS.deg(t1) - RS.deg(t0), 4)),
                box=[round(float(v), 6) for v in (x0, x1, y0, y1)] + [round(RS.deg(t0), 4), round(RS.deg(t1), 4)])


class Tree257(N56.Tree256):
    def __init__(self, pg, spine=False, **kw):
        N56.Tree256.__init__(self, pg, **kw)
        self.spine = spine                     # phase A: expand only the child that holds the image
        self.aligned_cuts, self.aligned_at, self.sibling_rows = 0, {}, []
        self.tube_tries = []

    # ------------------------------------------------------------------ bookkeeping for the aligned cuts
    def aligned_on_path(self, label):
        return sum(1 for p in self.aligned_at if label == p or label.startswith(p + "."))

    def on_path(self, lab):
        if self.spine:
            for p, a in self.aligned_at.items():
                if lab == a["sibling"] or lab.startswith(a["sibling"] + "."):
                    return False
        return N56.Tree256.on_path(self, lab)

    def dpin(self):
        """Lemma SEAM's binding pin slack: the MINIMUM over the node's pins (see the module doc)."""
        return min(float(p.get("dpin") or 0.0) for p in self.pg.rec["pins"])

    # ------------------------------------------------------------------ the tube try, slot ray, window pad
    def tube_try257(self, depth, label, tg):
        pg, node = self.pg, self.nodes[-1]
        n_anon = pg.n_free - len(pg.role_cell)
        node["n_anon"] = n_anon
        if n_anon > 0:
            node["tube"] = dict(fits=False, why="anonymous square(s) left: %d" % n_anon)
            return None
        pad = getattr(pg, "pad", "zero")
        if pad == "zero":
            raise SystemExit("A257's pilot is a WINDOW-pad instrument; run pad 0 through A256's run256.py --tube")
        d = self.dpin()
        tb = TR7.tube_slot(pg, tg["g"], tg["assignment"], tg["pins"], d)
        node["tube"] = tb
        seam = N56.seam_ok(pad, d)
        node["tube_seam"] = seam
        self.tube_tries.append(dict(label=label, fits=tb["fits"], worst=tb["worst"], seam=seam,
                                    cuts=self.aligned_on_path(label),
                                    roles={r: [v.get("fits"), v.get("fits_centre"), v.get("fits_tilt"),
                                               round(v.get("dx") or 0, 7), round(v.get("dy") or 0, 7),
                                               round(v.get("dt_deg") or 0, 5)] for r, v in tb["roles"].items()},
                                    pins={p: v["ok"] for p, v in tb["pins"].items()}))
        if not tb["fits"]:
            return None
        if not (seam["ok"] and N56.tube_cert_ok(seam["T_prime"], tb["radii"])):
            self.alive("gated node, all 11 named, the slot-ray tube box FITS, but Lemma TUBE-KILL's hypotheses "
                       "(iii)/(iv) do not hold at pad %s: T' = %.6f, T_K(delta_pin = %g) = %.6f, certificate T = %s "
                       "-- ALIVE, the lemma is never stretched" % (pad, seam["T_prime"], seam["delta_pin"],
                                                                   seam["T_K"], tb["radii"]["T"]))
            return "ALIVE"
        return self.tube_kill257(depth, label, tb, seam)

    def tube_kill257(self, depth, label, tb, seam):
        """A256's `tree256.tube_kill`, whose leaf text is re-emitted here because A256's own `%` tuple omits the
        node LABEL: its format string has ten conversions and nine arguments, so `%.6f` receives the certificate
        PATH and the first TUBE-KILL ever taken raises TypeError.  Same latent bug in `tube_leaf` (five
        conversions, four arguments).  Nothing on disk is affected -- A256's class-(b) domain is empty, so neither
        leaf has ever been taken -- but the window row cannot be run until A256's owner fixes both."""
        cuts = self.aligned_on_path(label)
        self.tube_kills += 1
        leaf = ("TUBE-KILL at %s (Lemma TUBE-KILL, A256 notes/trump5_closure.md s.3, on docs/proofs/"
                "contraction_tube.md Theorem T1 + Lemma SEAM s.4.1): all 11 squares named; every piece of every named "
                "FREE role inside the tube box (r_c' = %s, r_theta = %s) about the image %s, and the five class pins "
                "matched to its pins corner by corner (%d aligned cuts on the path); the class pins ride slots(m) "
                "exactly, so the slot-ray pull-back has w_pin = 0, w_free <= r_c, w_theta <= r_theta, w_s = 0 at "
                "depth t = s-hat - m; the slab (%s, s0] needs T' = %.6f and %s certifies T = %s; Lemma SEAM's (K) "
                "condition holds (T_K(delta_pin = %g) = %.6f >= T').  Therefore NO packing satisfying this node "
                "exists at any side m < s-hat, and at m = s-hat the only one is %s . z-hat (T1's equality clause).  "
                "The node is NOT claimed dead for m in (s-hat, s0]: that sliver lies above the target side and is "
                "irrelevant to s(11) >= s-hat." % (
                    label, tb["r_c_eff_float"], tb["radii"]["r_theta"], tb["g"], cuts, seam["s_bot"],
                    seam["T_prime"], tb["radii"]["cert"], tb["radii"]["T"], seam["delta_pin"], seam["T_K"], tb["g"]))
        self.nodes[-1].update(verdict="TUBE-KILL", clip="TUBE-KILL", leaf=leaf, tube_depth=cuts, reason=None,
                              verifier="[V: certs/verify_tubekill257.py -- re-checks hypotheses (i)-(iv) of Lemma "
                                       "TUBE-KILL against this node's snapshot, with (ii) on the FREE roles and the "
                                       "corner-by-corner pin match of code/trump257.py, and re-runs "
                                       "certs/verify_tube.py on %s]" % tb["radii"]["cert"])
        self.tube_rows.append(dict(label=label, kind="TUBE-KILL", g=tb["g"], seam=seam, radii=tb["radii"], cuts=cuts))
        self.pg.T.test("TUBE-KILL", label=label, g=tb["g"], T_prime=seam["T_prime"], T_K=seam["T_K"], cuts=cuts)
        self.log("   node %-10s d%d: TUBE-KILL (image %s; T' %.5f <= T_K %.5f; %d aligned cuts)"
                 % (label, depth, tb["g"], seam["T_prime"], seam["T_K"], cuts))
        if self.on_node:
            self.on_node(self)
        return "TUBE"

    # ------------------------------------------------------------------ the gated leaf (A212 s.1: branching only)
    def trump_leaf(self, depth, label, tg):
        pg, node = self.pg, self.nodes[-1]
        caps = self.eff_depth(depth, label) >= self.depth_cap or self.n_nodes >= self.node_cap
        if pg.T.out_of_time():
            self.alive("undecided (wall) at the gated fully named leaf")
            return "ALIVE"
        r = self.tube_try257(depth, label, tg)
        if r is not None:
            return "ALIVE" if r == "ALIVE" else "TUBE"
        if (node.get("n_anon") or 0) <= 0:
            cuts = self.aligned_on_path(label)
            sp = TR7.aligned_split(pg, tg["g"], tg["assignment"]) if cuts < TRUMP_SPLIT_CAP else None
            node["aligned_candidate"] = None if sp is None else dict(sp, m=str(sp["m"]))
            if sp is not None and self.n_nodes < self.node_cap and not pg.T.out_of_time():
                self._rs = aligned_spec(pg, sp)
                self.register_cut(label, self._rs)
                return "RSPLIT"
            tb = node.get("tube") or {}
            self.alive("gated node, all 11 named, the tube box NOT fitted (worst %s at %s x the radius) and %s" % (
                (tb.get("worst") or ["?", 0])[0], (tb.get("worst") or ["?", 0])[1],
                ("the aligned-cut cap %d is reached" % TRUMP_SPLIT_CAP) if cuts >= TRUMP_SPLIT_CAP else
                ("no cut found" if sp is None else "the node cap / wall")))
            return "ALIVE"
        # anonymous squares left: Lemma POCKET's COVER only (never its verdict), then Rule NS, then the exact cascade
        if len(pg.roles) >= 9 and not node.get("noroom"):
            res = N9.noroom_at(pg, min(pg.T.left() or 0.0, N11.NOROOM_CAP + 30), log=self.log)
            rec = dict(label=label, depth=depth, k=res["k"], m=res["m"], verdict=res["verdict"], clip=res["clip"],
                       bound=res["bound"], cn_bound=res["cn_bound"], n_pockets=len(res["pockets"]),
                       pockets=res["pockets"], seconds=res["seconds"], reason=res["reason"], gated=True,
                       used_for="pocket cover only (A212 notes/trump5_tree.md s.1)")
            self.noroom_runs.append(rec)
            node["noroom"] = rec
            if res["verdict"] == "DEAD":
                self.gate_conflicts += 1
                node["gate_conflict"] = dict(rule=res["clip"], leaf=res["reason"])
                self.alive("GATE-CONFLICT at %s: no-room claims DEAD (%s) on a gated node -- refused, ALIVE"
                           % (label, res["clip"]))
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
            clip, rnd = N6.cascade(pg, N11.EXACT_ROUNDS, log=self.log)
            self.n_nodes += 1
            self.exact_rounds += 1
            r = self.record(label + "x", depth, dict(slot=None, kind="exact", rows=None, named=None),
                            "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            return "CONTINUE" if r.get("verdict") == "INTERNAL" else r.get("verdict")
        self.alive("gated node with %d anonymous square(s) left (k = %d): no pocket cover, no Rule-NS sliver, the "
                   "exact cascade ran -- no lever names the last squares" % (node["n_anon"], len(pg.roles)))
        return "ALIVE"

    def leaf_rules(self, depth, label):
        tg = (self.nodes[-1].get("trump_gate") or {}) if self.nodes else {}
        if tg.get("contains"):
            return self.trump_leaf(depth, label, tg)
        return N11.Tree211.leaf_rules(self, depth, label)

    # ------------------------------------------------------------------ the cut is recorded as it is issued
    def register_cut(self, label, rs):
        """A211's `_expand` labels the two children `<label>.1` (lo) and `<label>.2` (hi); the gate accepts exactly
        the one on `rs["side"]`, the other is the NEAR-TRUMP SIBLING the seam has to kill by the ordinary rules."""
        if label in self.aligned_at:
            return
        img = "%s.%d" % (label, 1 if rs.get("side") == "lo" else 2)
        sib = "%s.%d" % (label, 2 if rs.get("side") == "lo" else 1)
        md = rs.get("m_f")
        if md is None:
            md = round(RS.deg(rs["m"]), 4) if rs["dim"] == "t" else round(float(rs["m"]), 6)
        self.aligned_cuts += 1
        self.aligned_at[label] = dict(image=img, sibling=sib, cut={k: str(v) for k, v in rs.items()})
        self.sibling_rows.append(dict(parent=label, sibling=sib, image=img, role=rs.get("role"), dim=rs.get("dim"),
                                      m=str(rs.get("m")), m_f=md, side_with_image=rs.get("side"),
                                      excess=rs.get("excess"), square=rs.get("square"), box=rs.get("box"),
                                      cut_index=self.aligned_cuts))
        self.log("   ALIGNED cut %d at %s: %s on %s at %s (excess %s x radius; image on the %s side -> %s, "
                 "near-Trump sibling -> %s)" % (self.aligned_cuts, label, rs.get("role"), rs.get("dim"), md,
                                                rs.get("excess"), rs.get("side"), img, sib))

    def result(self):
        out = N56.Tree256.result(self)
        out.update(aligned_cuts=self.aligned_cuts, sibling_rows=self.sibling_rows, tube_tries=self.tube_tries[-200:],
                   aligned_at={k: dict(v, cut={kk: str(vv) for kk, vv in v["cut"].items()})
                               for k, v in self.aligned_at.items()}, spine=self.spine)
        return out
