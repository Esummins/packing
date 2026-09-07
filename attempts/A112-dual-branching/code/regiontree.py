"""A112 T1 -- the REGION TREE: a second cover of a stalled node, with a pluggable branching order.

The PI's design (docs/residue_ledger.md sec 6, A111's addenda): where the first tree stalls, build a
SECOND tree over the same region with a DIFFERENT branching order, and transfer its kills to the old
boxes by containment.  A tree is a cover, so the Lean composition takes unions.

Shape of one node
-----------------
  root      = a stalled node's hypothesis exactly as the campaign emitted it (its class pins + its
              conditioned bin(s)), at the campaign's own side and budget.
  branch    = pick a placement p out of the node's OWN LP dual support with a pluggable ORDER
              function, and put a box  F = [c_p +- r] x [theta_p +- rho]  around it.
  YES child = node + "some square of the packing has its pose in F"     (hyp.boxes + [F], budget-1)
  NO  child = node + "no square of the packing has its pose in F"       (hyp.nofams + [NoFam(F)])
  cover     = YES or NO is a tautology, so the two children cover the node exactly.

At every YES node, BEFORE any LP:
  (1) the OCTAGON BOX-VS-PIN TRIM (A57 T5''/trim57, byte-identical): every tilt sub-interval of a
      box whose whole centre rectangle lies inside one pin's octagon is dead; if a box's surviving
      bin is empty the YES child is dead with no LP and no certificate;
  (2) the FREE PAIR KILL (A111): CORE-MEET (A96's tight common inscribed core) and TC (tilt
      coupling) between EVERY pair of conditioned bins (and bin vs pin), tilt intervals normalised
      into [0, 90] and the core half-side asserted <= 1/2 on every branch (A111 bug B5).
Only then the LP, under the PI's TIMEOUT PROTOCOL (2026-09-06):
  stage 1  A57's `solve_node`, unmodified, warm-started from the parent, at 240 s;
  verdict  a node CLEARLY below budget (eta <= -1e-3) goes STRAIGHT to the frozen
           `verify_case.py` (through A57's `certify.py --jobs 1`), converged or not -- the
           CERTIFICATE is the verdict, never tau, and a FAILing certificate leaves the node ALIVE;
  stage 2  only a node not clearly below budget escalates to the 900 s cap, and only one still on
           the knife edge (|eta| < 1e-6) after that counts as ALIVE.
Every node records the counterfactual wall of a flat 900 s cap (`flat900_s`) so the two regimes can
be compared directly.  NO KILL IS EVER AN LP VERDICT: a leaf is dead only by a certificate, by the
free pair kill / trim, or by the chain LP (which is labelled measured-not-certified).

Radii come from A111's table: (r, rho) = (0.1, 10 deg) at depth 0, halved at every level.  The chain
(Farkas) kill is NOT used above level 4 widths: the fixed-tilt LP bound is exactly s* - r, so the
YES kill certifies only for r < s* - s0 (0.0097 for S02, 0.0085 for S07).

Everything is written per node, so the run can be killed and resumed: a node whose record file
exists is never recomputed.

READ-ONLY on every campaign.  Frozen verifiers byte-identical.  <= 2 processes, BLAS-pinned, and a
commit/physical-memory gate before every LP and every certificate.
"""
from __future__ import annotations

import argparse, json, math, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L
import octagon as OCT
import trim57
from caselp import Box, NoFam, Hyp, solve_node, warm_from_result
from pinguard import classify as pin_classify
from substrat import trump_realizes

EPS_DEAD = 1e-6

# The PI's timeout protocol (2026-09-06): stage 1 at 240 s; eta <= ETA_DEAD goes straight to the
# frozen certifier (the certificate is the verdict, converged or not); only |eta| < ETA_EDGE
# escalates to the 900 s cap, and only a node still on the edge after it counts as ALIVE.
LP_STAGE1 = 240.0
ETA_DEAD = -1e-3
ETA_EDGE = 1e-6


def trump_canary(hyp, slots):
    """A57's canary (substrat.trump_realizes): Trump's own packing must never satisfy a
    hypothesis we declare dead.  Returns True if it DOES (a fatal violation), False if it does
    not, None if Trump's embedding file is unavailable."""
    try:
        return trump_realizes(hyp, slots)
    except Exception:
        return None


# ------------------------------------------------------------------ radii
def radii(depth, r0=0.1, rho0=10.0, floor_r=0.003, floor_rho=0.35):
    r = r0 * (0.5 ** depth)
    rho = rho0 * (0.5 ** depth)
    return max(r, floor_r), max(rho, floor_rho)


# ------------------------------------------------------------------ soundness of a YES child
def yes_sound(F, hyp, pins, slots):
    """A YES child may drop the budget by one only if its box is witnessed by a square DISTINCT
    from every square the hypothesis already accounts for.  Two obligations:
      * pinguard's 'parent' case -- a pin placement lying in F would let a pin witness it;
      * pose-disjointness from every conditioned bin already in the hypothesis -- two boxes that
        share a pose may be witnessed by the SAME square.
    Returns (ok, info).  'contradictory' is not a failure: it is a free kill, reported as such."""
    st, info = "ok", None
    if pins:
        try:
            st, info = pin_classify(F, pins, slots)
        except Exception as ex:
            return False, dict(reason="pin_classify:" + repr(ex)[:80])
    if st == "parent":
        return False, dict(reason="pinguard-parent", info=info)
    _, bins = L.split_hyp(hyp)
    for b in bins:
        if not OCT.boxes_pose_disjoint(F, b):
            return False, dict(reason="shares a pose with an existing bin", bin=L.box_json(b))
    return True, dict(pin=st, pin_info=info)


# ------------------------------------------------------------------ the two LP-free kills
def logic_kill(hyp, s, sample=True, seed=0, nsample=400):
    """(1) trim + (2) free pair kill, on a whole hypothesis.  Returns a dict; ['dead'] is the
    verdict, ['fires'] every rule that fired, with a dense-sampling check attached to each."""
    pins, bins = L.split_hyp(hyp)
    slots = L.pin_slots(pins)
    out = dict(dead=False, rule=None, fires=[], trim=[], pins=len(pins), bins=len(bins))

    # (1) octagon box-vs-pin trim (A57 T5'', byte-identical trim57)
    trimmed = []
    for b in bins:
        subs_all, excl_all = [], []
        for nb in L.normalise_tilt(b):
            try:
                subs, excl = trim57.trim_box(nb, slots)
            except Exception as ex:
                subs, excl = [nb], []
                out["trim"].append(dict(box=L.box_json(nb), error=repr(ex)[:100]))
            subs_all += subs
            excl_all += excl
        out["trim"].append(dict(box=L.box_json(b), subs=len(subs_all), excluded=len(excl_all)))
        if not subs_all:
            out.update(dead=True, rule="TRIM-EMPTY")
            return out
        trimmed.append(subs_all)

    # (2) free pair kill: every pair of conditioned bins, and every bin against every pin
    allb = [(("bin%d" % i), b) for i, b in enumerate(bins)] + \
           [(("pin%d" % i), b) for i, b in enumerate(pins)]
    for i in range(len(allb)):
        for j in range(i + 1, len(allb)):
            na, a = allb[i]
            nb_, b = allb[j]
            if na.startswith("pin") and nb_.startswith("pin"):
                continue                       # both pinned: the class gate keeps them disjoint
            for x in (a, b):
                L.assert_core_half_side(x)     # a <= 1/2 on every normalised tilt branch
            ok, info = OCT.pair_kill(a, b)
            if ok:
                fire = dict(pair=[na, nb_], boxes=[L.box_json(a), L.box_json(b)], **info)
                if sample:
                    worst, bad = L.sample_pair(a, b, n=nsample, seed=seed)
                    fire["sample"] = dict(n=nsample, worst_sat_gap=round(worst, 6),
                                          counterexamples=bad)
                out["fires"].append(fire)
                out.update(dead=True, rule=info.get("rule"))
    return out


# ------------------------------------------------------ the CHAIN kill (A111's GRAIN-LP, at s0)
def chain_kill(hyp, s):
    """A111's chain (Farkas) test, applied to a region-tree node's OWN boxes at the FIXED side s.

    Every conditioned box (pins included, as fixed boxes -- at a single side a pin box IS a fixed
    box, so nothing is lost) is one square of a hypothetical packing.  `t1_yes.selection_census`
    encloses, by outward-rounded interval arithmetic, the eight signed separating-axis selections
    of every pair over the whole box product; a pair with exactly one possible selection gives a
    VALID linear inequality, a pair with several is DROPPED (a relaxation, hence sound), a pair
    with none already closes the cell.  `t1_yes.cell_lp` then minimises s over the box product with
    those rows plus the containment rows at the cell MINIMUM half-width (the minimum, not the
    maximum: the maximum would over-constrain and an infeasibility would prove nothing).

    With s pinned to the node's own side, LP INFEASIBLE  =>  the node's boxes admit no packing at
    that side, i.e. the YES cell is empty.  A111 measured the bound as exactly s* - r, so this
    fires only once the boxes are down to r < s* - s0 (0.0097 for S02) -- level-4 widths and below.

    This is a FLOAT LP: it is a MEASURED kill, not a certified one.  Certifying it is A111's leaf
    (`leaf_shape.md` O1-O4: the selection census, the tilt cover, the affine relaxation and one
    Farkas certificate per cell), which A112 does not attempt.  Recorded as DEAD-CHAIN-LP and
    counted apart from every certified kill.
    """
    import t1_yes as T1
    boxes = list(hyp.boxes)
    if len(boxes) < 2:
        return dict(fired=False, reason="fewer than two boxes")
    # NOTE: no tilt normalisation here, deliberately.  `t1_yes`'s interval arithmetic (iv_cos /
    # iv_sin / w_range) is exact on ANY angle interval -- it is `pinguard.tight_a` and
    # `trim57.dead_by_pin`, used by the octagon rules above, whose |cos|+|sin| envelopes are
    # stated only on [0, 90] and which therefore get the normalised boxes.  Splitting the tilt
    # interval here would need the product over branches, and would prove nothing extra.
    B, names = {}, []
    for i, b in enumerate(boxes):
        n = "b%d" % i
        names.append(n)
        B[n] = dict(x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, th0=b.th0, th1=b.th1)
    try:
        cells = {n: (B[n]["th0"], B[n]["th1"]) for n in names}
        cen = T1.selection_census(B, names, [], s, s, th_cells=cells)
        impossible = [k for k, v in cen.items() if not v]
        val, st, nrows = T1.cell_lp(B, names, [], cells, cen, s, s)
    except Exception as ex:
        return dict(fired=False, error=repr(ex)[:150])
    forced = sum(1 for v in cen.values() if len(v) == 1)
    return dict(fired=bool(impossible or st == "infeasible"),
                status=st, rows=nrows, pairs=len(cen), forced=forced,
                impossible_pairs=len(impossible),
                lb=(None if not math.isfinite(val) else round(val, 8)),
                certified=False,
                note="measured (float LP); the certified form is A111 leaf O1-O4")


# ------------------------------------------------------------------ ORDER functions
def score_candidates(sup, hyp, s, r, rho, ordering, lp_boxes=None, pins=None, slots=None,
                     area=False, wastage=None, lp_rank=None):
    """Score every support placement as a branch candidate.  No LP solve anywhere.

      stranded : (LP row mass the YES core of F strikes out) + (support mass the NO family removes)
      loadpath : the Fritz-John multiplier of the shadow's load path -- the support mass sitting in
                 a load-path box of the node's own matched shadow, mapped into the node frame
      hybrid   : the load-path member that strands the most (loadpath candidates, stranded score)
      wastage  : PIN WASTAGE (PI, 2026-09-06) -- the AREA of the pockets the candidate box creates
                 against the class pins, the walls and the other conditioned boxes: container
                 points that can hold no unit square at any tilt once F's core is in place.  Pure
                 geometry, no LP.
    """
    out = []
    for k, p in enumerate(sup):
        F = L.cand_box(p, r, rho)
        ok, info = yes_sound(F, hyp, pins or [], slots or [])
        rm, rn = L.rows_struck(F, sup)
        nm, nn = L.nofam_mass(F, sup, s)
        lp_hit, lp_name, lp_d = 0.0, None, None
        if lp_boxes:
            for nme, b in lp_boxes.items():
                d = max(abs(p["cx"] - 0.5 * (b.x0 + b.x1)) - 0.5 * (b.x1 - b.x0),
                        abs(p["cy"] - 0.5 * (b.y0 + b.y1)) - 0.5 * (b.y1 - b.y0))
                dth = abs(p["theta_deg"] - 0.5 * (b.th0 + b.th1) % 90.0)
                dth = min(dth, 90.0 - dth) - 0.5 * (b.th1 - b.th0)
                dd = max(d, 0.0) + max(dth, 0.0) / 90.0
                if lp_d is None or dd < lp_d:
                    lp_d, lp_name = dd, nme
            lp_hit = p["y"] if (lp_d is not None and lp_d <= 1e-9) else 0.0
        rec = dict(idx=k, cx=p["cx"], cy=p["cy"], theta_deg=p["theta_deg"], y=p["y"],
                   sound=bool(ok), sound_info=info,
                   rows_struck=round(rm, 6), rows_n=rn,
                   nofam_mass=round(nm, 6), nofam_n=nn,
                   stranded=round(rm + nm, 6),
                   loadpath_box=lp_name, loadpath_dist=(None if lp_d is None else round(lp_d, 6)),
                   loadpath_mult=round(lp_hit, 6),
                   loadpath_rank=list(lp_rank.get(lp_name, (9, 0))) if lp_rank else None)
        if area:
            rec["unusable_area"] = round(L.unusable_area(F), 6)
        if wastage is not None:
            rec["pin_wastage"] = round(wastage.score(F), 6)
        out.append(rec)
    if ordering == "wastage":
        key = lambda c: (-c.get("pin_wastage", 0.0), -c["stranded"], -c["y"], c["idx"])
    elif ordering == "stranded":
        key = lambda c: (-c["stranded"], -c["y"], c["idx"])
    elif ordering == "loadpath":
        # A111's order: inside a load-path box first, the load path proper before the anchors,
        # then by the member's Fritz-John weight (its count of LOADED contacts in the shadow),
        # then by the LP multiplier the support puts on it, then by distance to the member.
        key = lambda c: (0 if c["loadpath_mult"] > 0 else 1,
                         tuple(c["loadpath_rank"] or (9, 0)),
                         -c["loadpath_mult"],
                         c["loadpath_dist"] if c["loadpath_dist"] is not None else 9e9,
                         -c["y"], c["idx"])
    elif ordering == "hybrid":
        key = lambda c: (0 if (c["loadpath_dist"] is not None and c["loadpath_dist"] <= 0.25) else 1,
                         -c["stranded"], -c.get("pin_wastage", 0.0), -c["y"], c["idx"])
    else:
        raise ValueError(ordering)
    out.sort(key=key)
    return out


# ------------------------------------------------------------------ k0: the slot box / crowd row
def slot_cells(s, imax=4):
    """the named slot cells of the container at side s -- A107 `shadowlib.slot_cells` verbatim
    (unit cells stacked into the four corners), with the ones whose centre falls outside the
    admissible strip [0.5, s - 0.5] dropped."""
    out = {}
    for i in range(imax):
        for j in range(imax):
            for n in ("BL(%d,%d)" % (i, j), "BR(%d,%d)" % (i, j),
                      "TL(%d,%d)" % (i, j), "TR(%d,%d)" % (i, j)):
                x, y = L.slot_xy(n, s)
                if 0.5 - 1e-9 <= x <= s - 0.5 + 1e-9 and 0.5 - 1e-9 <= y <= s - 0.5 + 1e-9:
                    out[n] = (x, y)
    return out


def in_slot_cell(F, s, simple_tol_deg=3.0):
    """Which slot CELL contains F's whole centre rectangle, and is F's tilt inside the 'simple'
    tolerance (A107 `shadowlib.snap`: within 3 deg of an axis)?

    IMPORTANT -- this is INFORMATION, not a kill.  A53's stratification counts GRID-LOCKED
    ("simple") squares: doubly flush against the walls and the already-locked squares, wall-
    anchored.  A square whose centre merely lies in a corner cell, even axis-aligned, need not be
    grid-locked, so "some square's pose lies in F, F inside slot cell C" does NOT imply k >= 1 and
    cannot be discharged by the k >= 1 classes being dead at s0.  The brief's k0 YES-side shortcut
    is therefore recorded as AVAILABLE and counted, never taken, unless it is switched on
    deliberately; the sound form of the shortcut is K0-FREE/teleport applied to the LP support, not
    a box containment.  See notes/verdict.md."""
    a = F.th0 % 90.0
    b = a + (F.th1 - F.th0)
    simple = (F.th1 - F.th0 <= 2 * simple_tol_deg) and \
             (min(a, 90.0 - a) <= simple_tol_deg or min(b % 90.0, 90.0 - b % 90.0) <= simple_tol_deg)
    for n, (sx, sy) in slot_cells(s).items():
        if F.x0 >= sx - 0.5 - 1e-12 and F.x1 <= sx + 0.5 + 1e-12 and \
           F.y0 >= sy - 0.5 - 1e-12 and F.y1 <= sy + 0.5 + 1e-12:
            return dict(cell=n, simple_tilt=bool(simple))
    return None


# ------------------------------------------------------------------ one region-tree node
class Runner:
    def __init__(self, region, ordering, s, budget0, log, lp_cap=900.0, stage1=LP_STAGE1,
                 depth_cap=6, node_cap=40, wall=1800.0, kind="a57", area=False,
                 k0_class_clause=False, sample_n=400, wastage_step=0.02,
                 wastage_ntheta=19):
        self.region, self.ordering, self.s = region, ordering, s
        self.log, self.lp_cap, self.stage1 = log, lp_cap, stage1
        self.depth_cap, self.node_cap, self.wall = depth_cap, node_cap, wall
        self.kind, self.area, self.k0_class_clause = kind, area, k0_class_clause
        self.sample_n = sample_n
        self.wastage_step, self.wastage_ntheta = wastage_step, wastage_ntheta
        self.lp_rank = None
        self.dir = os.path.join(L.RT, region, ordering)
        os.makedirs(self.dir, exist_ok=True)
        self.stats = dict(nodes=0, lps=0, lp_wall=0.0, flat900_wall=0.0, logic_kills=0,
                          cert_wall=0.0, certs_pass=0, certs_fail=0, fires=0, sampled_pairs=0,
                          counterexamples=0, class_clause=0, chain_kills=0)
        self.cert_time = 240.0
        self.t0 = time.time()

    # ---------------- per-node persistence
    def path(self, key):
        return os.path.join(self.dir, key + ".json")

    def load(self, key):
        p = self.path(key)
        return L.jload(p) if os.path.exists(p) else None

    def save(self, key, rec):
        L.jdump(self.path(key), rec)

    # ---------------- the LP, under the PI's two-stage timeout protocol (2026-09-06)
    #
    #   stage 1  every node gets 240 s.
    #   verdict  a node CLEARLY below budget (eta <= -1e-3) goes straight to the frozen certifier,
    #            converged or not -- the CERTIFICATE is the verdict, never tau.  A111 measured why:
    #            a child dead-unconverged at 80 s converges DEAD at 900 s, and the exact verifier
    #            PASSes children the LP left unconverged, so waiting for column generation to close
    #            buys nothing the certifier does not already decide.
    #   stage 2  only a node NOT clearly below budget escalates, to the 900 s cap; a node still on
    #            the knife edge (|eta| < 1e-6) after that counts as ALIVE.
    #
    # `flat900_s` is the counterfactual wall of a flat 900 s cap on the same node: the same time if
    # the LP converged inside stage 1, otherwise the full cap (A111's datum: an unconverged child
    # at the 900 s cap ran 938 s and was STILL unconverged).
    def lp(self, hyp, budget, warm, tag):
        if not L.gate(self.log, tag, deadline=self.t0 + self.wall + 600):
            return None, None
        kw = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None, prune=0,
                  prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                  max_rows_add=2000, fine_slack=99.0, alternate=True)
        t0 = time.time()
        rr = solve_node(self.s, hyp, budget, warm=dict(warm), time_limit=self.stage1, **kw)
        s1 = time.time() - t0
        eta1 = rr["tau"] - budget
        conv1 = bool(rr["converged"])
        s2, staged = 0.0, 1
        if eta1 > ETA_DEAD:                       # not clearly dead: escalate to the 900 s cap
            left = self.wall - (time.time() - self.t0)
            if self.lp_cap > self.stage1 + 30 and left > 60:
                t1 = time.time()
                rr = solve_node(self.s, hyp, budget, warm=warm_from_result(rr),
                                time_limit=min(self.lp_cap - self.stage1, left), **kw)
                s2 = time.time() - t1
                staged = 2
        eta = rr["tau"] - budget
        flat900 = s1 if conv1 else (s1 + s2 if staged == 2 else self.lp_cap)
        self.stats["lps"] += 1
        self.stats["lp_wall"] += s1 + s2
        self.stats["flat900_wall"] += flat900
        return rr, dict(stage=staged, stage1_s=round(s1, 1), stage2_s=round(s2, 1),
                        seconds=round(s1 + s2, 1), flat900_s=round(flat900, 1),
                        eta_stage1=eta1, converged_stage1=conv1,
                        tau=rr["tau"], eta=eta, converged=bool(rr["converged"]),
                        minmass=rr.get("minmass"), maxcov=rr.get("maxcov"))

    # ---------------- the tree
    def run(self, root_res, lp_boxes=None, lp_rank=None):
        self.lp_rank = lp_rank
        pins, _ = L.split_hyp(Hyp.from_json(root_res["hyp"]))
        slots = L.pin_slots(pins)
        # BREADTH-FIRST.  With a wall cap a depth-first walk spends the whole budget on one spine
        # (the NO spine, where the kills are) and never processes its YES siblings, so no region can
        # terminate and "nodes to termination" stops comparing the orderings.  A queue keeps the
        # frontier a complete cover of the root at a uniform depth, which is also the object the
        # containment record needs.
        from collections import deque
        stack = deque([dict(key="R", depth=0, kind="root", hyp=root_res["hyp"],
                            budget=root_res["budget"], parent=None, res=root_res)])
        leaves, internal = [], []
        while stack:
            nd = stack.popleft()
            if self.stats["nodes"] >= self.node_cap or time.time() - self.t0 > self.wall:
                rec = self.load(nd["key"]) or dict(
                    key=nd["key"], depth=nd["depth"], kind=nd["kind"], region=self.region,
                    ordering=self.ordering, s=self.s, budget=nd["budget"], hyp=nd["hyp"],
                    parent=nd["parent"], children=[], status="CAP-UNPROCESSED")
                rec.setdefault("status", "CAP-UNPROCESSED")
                self.save(nd["key"], rec)
                leaves.append(rec)
                continue
            rec, kids = self.node(nd, pins, slots, lp_boxes)
            (internal if kids else leaves).append(rec)
            for k in kids:                # YES first: it is the side that can die for free
                stack.append(k)
        return leaves, internal

    def node(self, nd, pins, slots, lp_boxes):
        key = nd["key"]
        cached = self.load(key)
        hyp = Hyp.from_json(nd["hyp"])
        budget = nd["budget"]
        self.stats["nodes"] += 1
        if cached and cached.get("status") not in (None, "CAP-UNPROCESSED"):
            for f in cached.get("logic", {}).get("fires", []):
                self.stats["fires"] += 1
                self.stats["sampled_pairs"] += f.get("sample", {}).get("n", 0)
                self.stats["counterexamples"] += f.get("sample", {}).get("counterexamples", 0)
            if cached.get("lp") and not cached["lp"].get("reused"):
                self.stats["lps"] += 1
                self.stats["lp_wall"] += cached["lp"].get("seconds", 0.0)
                self.stats["flat900_wall"] += cached["lp"].get("flat900_s", 0.0)
            if cached.get("cert"):
                self.stats["cert_wall"] += cached["cert"].get("seconds", 0.0)
                if cached["cert"].get("result") == "PASS":
                    self.stats["certs_pass"] += 1
                else:
                    self.stats["certs_fail"] += 1
            if cached.get("status") in ("DEAD-LOGIC",):
                self.stats["logic_kills"] += 1
            if cached.get("status") == "DEAD-CHAIN-LP":
                self.stats["chain_kills"] += 1
            if cached.get("status") == "DEAD-CLASS":
                self.stats["class_clause"] += 1
            kids = []
            for c in cached.get("children", []):
                kids.append(dict(key=c["key"], depth=c["depth"], kind=c["kind"], hyp=c["hyp"],
                                 budget=c["budget"], parent=key, res=None))
            self.log("  [cache] %-14s %-5s d%d  %s" % (key, cached["kind"], cached["depth"],
                                                       cached["status"]))
            return cached, kids

        rec = dict(key=key, depth=nd["depth"], kind=nd["kind"], region=self.region,
                   ordering=self.ordering, s=self.s, budget=budget, hyp=nd["hyp"],
                   parent=nd["parent"], status=None, children=[])

        # ---- (0) the k0 YES-side clause -- RECORDED, and taken only if switched on deliberately.
        # A53's k counts GRID-LOCKED squares (doubly flush, wall-anchored); a pose inside a corner
        # cell is not that, so the clause is not discharged by a box containment.  The count is
        # kept so the value of proving the sound form (K0-FREE/teleport on the LP support) can be
        # read off directly.
        if self.kind == "k0" and nd.get("in_slot"):
            rec["class_clause"] = dict(
                slot=nd["in_slot"],
                clause="a YES box inside slot cell %s with %s tilt; k >= 1 needs the square to be "
                       "GRID-LOCKED (A53: doubly flush, wall-anchored), which box containment does "
                       "not give -- clause AVAILABLE, not taken"
                       % (nd["in_slot"]["cell"],
                          "simple" if nd["in_slot"]["simple_tilt"] else "non-simple"),
                taken=bool(self.k0_class_clause))
            self.stats["class_clause"] += 1
            if self.k0_class_clause:
                rec["trump_realizes"] = trump_canary(hyp, slots)
                rec["status"] = "DEAD-CLASS"
                self.save(key, rec)
                self.log("  %-14s %-5s d%d  DEAD-CLASS (slot %s)"
                         % (key, rec["kind"], rec["depth"], nd["in_slot"]["cell"]))
                return rec, []

        # ---- (1)+(2) logic, before any LP, at every YES node (and at the root, free)
        if nd["kind"] in ("YES", "root"):
            lg = logic_kill(hyp, self.s, sample=True, seed=abs(hash(key)) % 10 ** 6,
                            nsample=self.sample_n)
            rec["logic"] = lg
            for f in lg["fires"]:
                self.stats["fires"] += 1
                self.stats["sampled_pairs"] += f.get("sample", {}).get("n", 0)
                self.stats["counterexamples"] += f.get("sample", {}).get("counterexamples", 0)
            if lg["dead"]:
                rec["status"] = "DEAD-LOGIC"
                rec["trump_realizes"] = trump_canary(hyp, slots)
                self.stats["logic_kills"] += 1
                self.save(key, rec)
                self.log("  %-14s %-5s d%d  DEAD-LOGIC (%s)" % (key, rec["kind"], rec["depth"],
                                                               lg["rule"]))
                return rec, []
            # ---- (2b) the CHAIN kill (A111's GRAIN-LP at the node's own side).  Sound, cheap,
            # and MEASURED only: it fires once the boxes are inside A111's certified radius.
            ck = chain_kill(hyp, self.s)
            rec["chain"] = ck
            if ck.get("fired"):
                rec["status"] = "DEAD-CHAIN-LP"
                rec["trump_realizes"] = trump_canary(hyp, slots)
                self.stats["chain_kills"] += 1
                self.save(key, rec)
                self.log("  %-14s %-5s d%d  DEAD-CHAIN-LP (%s, %d/%d forced)"
                         % (key, rec["kind"], rec["depth"], ck.get("status"),
                            ck.get("forced", 0), ck.get("pairs", 0)))
                return rec, []

        # ---- (3) the LP, then the CERTIFIER.  Under the PI's protocol tau is never a verdict:
        # a node below budget is handed to the frozen verify_case.py at once and the certificate
        # decides.  A FAILing certificate leaves the node ALIVE and it is branched on.
        res = nd.get("res")
        if res is None:
            warm = nd.get("warm") or dict(atoms=[], rows=[])
            rr, info = self.lp(hyp, budget, warm, key)
            if rr is None:
                rec["status"] = "CAP-GATE"
                self.save(key, rec)
                return rec, []
            res = rr
            rec["lp"] = info
            nj = "%s%s__%s__%s.json" % (self.region, L.SUF, self.ordering, key)
            L.jdump(os.path.join(L.NODES, nj), rr)
            rec["node_json"] = nj
            eta = info["eta"]
            self.log("  %-14s %-5s d%d  LP stage%d tau=%.6f eta=%+.6f conv=%s "
                     "(%.0fs = %.0f+%.0f; flat-900 would be %.0fs)"
                     % (key, rec["kind"], rec["depth"], info["stage"], info["tau"], eta,
                        info["converged"], info["seconds"], info["stage1_s"], info["stage2_s"],
                        info["flat900_s"]))
            if eta <= -ETA_EDGE:
                c = certify_leaf(self.region, self.ordering, key, nj, self.log,
                                 cert_time=self.cert_time)
                rec["cert"] = c
                self.stats["cert_wall"] += c.get("seconds", 0.0)
                rec["trump_realizes"] = trump_canary(hyp, slots)
                if c["result"] == "PASS":
                    self.stats["certs_pass"] += 1
                    rec["status"] = "DEAD-CERT"
                    self.save(key, rec)
                    return rec, []
                self.stats["certs_fail"] += 1
                rec["cert_failed"] = True         # below budget but NOT certified: still alive
                if eta <= ETA_DEAD:
                    rec["note"] = ("LP clearly below budget (eta %.6f) but the frozen verifier "
                                   "refused: the node stays ALIVE and is branched on" % eta)
            self.log("  %-14s %-5s d%d  ALIVE%s"
                     % (key, rec["kind"], rec["depth"],
                        " (knife edge)" if abs(eta) < ETA_EDGE else
                        (" (certificate FAILed)" if rec.get("cert_failed") else "")))
        else:
            rec["lp"] = dict(tau=res["tau"], eta=res["tau"] - budget,
                             converged=bool(res.get("converged")), seconds=0.0, reused="campaign")

        # ---- (4) split
        if nd["depth"] >= self.depth_cap:
            rec["status"] = "CAP-DEPTH"
            self.save(key, rec)
            return rec, []
        sup = L.support(res)
        if not sup:
            rec["status"] = "CAP-NO-SUPPORT"
            self.save(key, rec)
            return rec, []
        r, rho = radii(nd["depth"])
        blockers = []
        for b in hyp.boxes:
            blockers += L._core_of(b)
        W = L.Wastage(self.s, blockers, step=self.wastage_step, ntheta=self.wastage_ntheta)
        cands = score_candidates(sup, hyp, self.s, r, rho, self.ordering, lp_boxes=lp_boxes,
                                 pins=pins, slots=slots, area=self.area, wastage=W,
                                 lp_rank=self.lp_rank)
        pick = next((c for c in cands if c["sound"]), None)
        rec["candidates"] = cands[:12]
        rec["n_candidates"] = len(cands)
        rec["wastage_base_unusable_area"] = round(W.base_unusable_area, 6)
        rec["wastage_vs_rowmass_spearman"] = L.spearman(
            [c.get("pin_wastage", 0.0) for c in cands], [c["rows_struck"] for c in cands])
        rec["wastage_vs_stranded_spearman"] = L.spearman(
            [c.get("pin_wastage", 0.0) for c in cands], [c["stranded"] for c in cands])
        if pick is None:
            rec["status"] = "CAP-NO-SOUND-CANDIDATE"
            self.save(key, rec)
            return rec, []
        F = L.cand_box(pick, r, rho)
        rec.update(status="SPLIT", branch_box=L.box_json(F), branch_choice=pick,
                   branch_r=r, branch_rho=rho,
                   cover=dict(law="tautology: (some square's pose in F) or (no square's pose in F)",
                              F=L.box_json(F), children=[key + "Y", key + "N"]))
        warm = warm_from_result(res)
        warm["rows"] = warm["rows"][:20000]
        yhyp = Hyp(list(hyp.boxes) + [F], list(hyp.nofams))
        nf = NoFam(max(0.5, min(F.x0, self.s - 0.5)), max(0.5, min(F.x1, self.s - 0.5)),
                   max(0.5, min(F.y0, self.s - 0.5)), max(0.5, min(F.y1, self.s - 0.5)),
                   OCT.theta_intervals(F.th0, F.th1))
        nhyp = Hyp(list(hyp.boxes), list(hyp.nofams) + [nf])
        slot_hit = in_slot_cell(F, self.s) if self.kind == "k0" else None
        kids = [
            dict(key=key + "Y", depth=nd["depth"] + 1, kind="YES", hyp=yhyp.to_json(),
                 budget=budget - 1, parent=key, warm=warm, res=None, in_slot=slot_hit),
            dict(key=key + "N", depth=nd["depth"] + 1, kind="NO", hyp=nhyp.to_json(),
                 budget=budget, parent=key, warm=warm, res=None, in_slot=None),
        ]
        rec["children"] = [dict(key=k["key"], depth=k["depth"], kind=k["kind"], hyp=k["hyp"],
                                budget=k["budget"], in_slot=k["in_slot"]) for k in kids]
        self.save(key, rec)
        self.log("  %-14s %-5s d%d  SPLIT on (%.4f, %.4f, %.2f deg) r=%.4f rho=%.2f  "
                 "stranded=%.3f lp=%s%s"
                 % (key, rec["kind"], rec["depth"], pick["cx"], pick["cy"], pick["theta_deg"],
                    r, rho, pick["stranded"], pick["loadpath_box"],
                    ("  slot=%s%s" % (slot_hit["cell"],
                                      "" if slot_hit["simple_tilt"] else " (non-simple tilt)"))
                    if slot_hit else ""))
        return rec, kids


# ------------------------------------------------------------------ certification of the leaves
def certify_leaf(region, ordering, key, node_json, log, cert_time=240.0, depth=56, rounds=1):
    tag = "%s%s__%s__%s" % (region, L.SUF, ordering, key)
    node = os.path.join(L.NODES, node_json)
    out = os.path.join(L.CERTS, tag + ".json")
    if os.path.exists(out + ".done"):
        return L.jload(out + ".done")
    if not L.gate(log, tag):
        return dict(tag=tag, result="SKIP-GATE")
    cmd = [sys.executable, os.path.join(HERE, "certify.py"), node, "--s_rat", L.S_RAT,
           "--rounds", str(rounds), "--jobs", "1", "--depth", str(depth),
           "--time_limit", str(cert_time), "--out", out, "--scale", "0",
           "--scale_cap", "1.4", "--max_w", "64", "--loop_cols"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    txt = p.stdout + p.stderr
    tail = [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "[round", "certificate", "CERTIFIED",
                             "NOT certified", "MALFORMED"))]
    r = dict(tag=tag, rc=p.returncode, result=("PASS" if p.returncode == 0 else "FAIL"),
             seconds=round(time.time() - t0, 1), verifier=tail[-6:])
    L.jdump(out + ".done", r)
    log("    cert %-46s %s (%.0fs)" % (key, r["result"], r["seconds"]))
    return r


# ------------------------------------------------------------------ the containment record
def containment(region, ordering, leaves, internal, root_res, root_src):
    """The kill record: 'old box <region> dead by region tree <ordering>', with the cover written
    out explicitly.  Three obligations, each checked here:
      C1  the root hypothesis IS the old node's hypothesis (same boxes, same nofams, same budget,
          same side) -- so the region tree covers the old box exactly, not a relaxation of it;
      C2  every internal node's two children carry the same branch box F, one as a core box (with
          the budget dropped by one) and one as a NO-family -- a tautologous split, so the union of
          the leaves is the root;
      C3  every leaf is dead.
    The kill transfers iff C1 and C2 and C3."""
    by = {r["key"]: r for r in (leaves + internal)}
    c1 = dict(ok=True, notes=[])
    rh = root_res["hyp"]
    root = by.get("R")
    if root is None:
        c1 = dict(ok=False, notes=["no root record"])
    else:
        same = json.dumps(root["hyp"], sort_keys=True) == json.dumps(rh, sort_keys=True)
        c1 = dict(ok=bool(same and root["budget"] == root_res["budget"]
                          and abs(root["s"] - root_res["s"]) < 1e-12),
                  root_hyp_identical=bool(same), budget=root["budget"],
                  campaign_budget=root_res["budget"], s=root["s"], campaign_s=root_res["s"],
                  source=root_src)
    c2 = dict(ok=True, splits=[], bad=[])
    for r in internal:
        if r.get("status") != "SPLIT":
            continue
        F = r["branch_box"]
        ky, kn = r["cover"]["children"]
        ry, rn = by.get(ky), by.get(kn)
        ok = True
        det = dict(node=r["key"], F=F)
        if ry is None or rn is None or "hyp" not in (ry or {}) or "hyp" not in (rn or {}):
            ok = False
            det["missing"] = [k for k, v in ((ky, ry), (kn, rn))
                              if v is None or "hyp" not in v]
        else:
            ybox = ry["hyp"]["boxes"][-1]
            nfam = rn["hyp"]["nofams"][-1]
            det["yes_box"] = ybox
            det["no_fam"] = nfam
            det["yes_budget"] = ry["budget"]
            det["no_budget"] = rn["budget"]
            bok = (abs(ybox["x0"] - F["x0"]) < 1e-12 and abs(ybox["x1"] - F["x1"]) < 1e-12
                   and abs(ybox["y0"] - F["y0"]) < 1e-12 and abs(ybox["y1"] - F["y1"]) < 1e-12
                   and abs(ybox["th0"] - F["th0"]) < 1e-9 and abs(ybox["th1"] - F["th1"]) < 1e-9)
            zx = (abs(nfam["x0"] - max(0.5, min(F["x0"], root["s"] - 0.5))) < 1e-12
                  and abs(nfam["x1"] - max(0.5, min(F["x1"], root["s"] - 0.5))) < 1e-12)
            ok = bool(bok and zx and ry["budget"] == r["budget"] - 1 and rn["budget"] == r["budget"])
            det.update(box_matches=bok, zone_matches=zx)
        det["ok"] = ok
        c2["splits"].append(det)
        if not ok:
            c2["ok"] = False
            c2["bad"].append(r["key"])
    dead_status = ("DEAD-LOGIC", "DEAD-CERT", "DEAD-CLASS", "DEAD-CHAIN-LP")
    c3 = dict(ok=all(r.get("status") in dead_status for r in leaves),
              leaves=[dict(key=r["key"], status=r.get("status"),
                           cert=(r.get("cert") or {}).get("result")) for r in leaves])
    return dict(region=region, ordering=ordering,
                claim="old box %s dead by region tree %s/%s" % (region, region, ordering),
                C1_root_is_old_hypothesis=c1, C2_tautologous_split=c2, C3_all_leaves_dead=c3,
                transfers=bool(c1["ok"] and c2["ok"] and c3["ok"]))
