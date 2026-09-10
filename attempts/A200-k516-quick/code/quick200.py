"""A200 -- the COMPOSED / QUICK killer over a gallery page (k5_16 first), n-general; built on A198's fastprop.Page
(READ-ONLY import).  Every pruning is one of the exact tests A198 lists (DEAD-CELL, MISS, LONELY, A1, FC, CHORD) plus

  CN      Lemma CN (A153; residue_ledger section 1): two interior-disjoint unit squares have centres at Euclidean
          distance >= 1 (their open inscribed discs of radius 1/2 are disjoint).  If the UNION of a slot's surviving
          free-meeter centre pieces has diameter < 1, the slot has at most ONE free meeter.
  A1-U    Lemma A1 on the union: l-inf diameter < 1/sqrt2 -> at most one free meeter.
  CHORD-U the open-chord row: on a guard line, the fixed squares' (pins, H, instantiated roles) min open chords plus
          TWO copies of the min open chord over the union's pieces > s -> at most one free meeter with a pose in the
          union (the open chords of distinct squares of one packing on a line are disjoint sub-intervals of (0, s)).
  SEAL    A199's corner chain (seal199b.run_corner: F's exact reach, the {pins, H, F, G} node, the (FH) miss tests).

Semantics that make the count sound (the same as A198's): U_p, the per-slot union of A198's per-cell REACH survivors,
is bisected against EVERY role's K' (pins, H, the instantiated roles), so it is a superset of the poses of any free
square DISTINCT FROM THE ROLES that meets p ("anonymous").  Theorem FC: two distinct non-pin meeters of p, taken from
{H} u {instantiated roles} u {anonymous}.  With H_p = [H not provably missing p], R_p = the roles not provably
missing p, cap_p in {0, 1, inf} the anonymous bound from CN / A1-U / CHORD-U / the A1 cell count:
  avail_p = H_p + |R_p| + cap_p < 2  -> DEAD;
  avail_p = 2                        -> every candidate is FORCED: H clipped to the poses meeting p (MISS, per piece);
                                        a role clipped likewise; an anonymous meeter (cap_p = 1) INSTANTIATED as a
                                        new role with box = hull(U_p) (it exists, meets p, and is distinct from every
                                        role and from H by definition of "anonymous").
Rounds re-normalise the node (A171 multibox: the clipped H's K' grows and clips every other reach) to a fixed point
across ALL slots; then A198's joint count (with the per-slot caps), the bar-H forcing, SEAL at both pads, and the
no-room leaf at >= 9 boxed roles.
"""
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A198-fastprop", "code"), os.path.join(ATT, "A199-corner-seal", "code"),
           os.path.join(ATT, "A189-noroom", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fastprop as FP                                          # noqa: E402  READ-ONLY (A198)
import classes178 as CL                                        # noqa: E402  READ-ONLY (A178)

MB, GV, CLN, G = FP.MB, FP.GV, FP.CLN, FP.G
S_RAT, HALF, SQ2H_LO, SQ2H_UP = FP.S_RAT, FP.HALF, FP.SQ2H_LO, FP.SQ2H_UP
LAM_MAX = Fr(969271, 250000) / Fr(382, 100)                    # s0 / 3.82 (Theorem FC's lambda_max: the whole window)
LAM_G1 = Fr(969271, 250000) / Fr(3861637, 1000000)             # s0 / 3.861637: A57's G1 slab (3.861637, s0] -- the k5_16 pages'
PADS = {"window": LAM_MAX, "g1": LAM_G1, "zero": Fr(1)}        # own window (forced_corners.md section 2 remark, section 5(a))
INF = 99


def pad_i(i, lam):
    """Theorem FC's pad on the far sides of the cell at offset i: (lambda - 1)(i + 1 + 1/sqrt2), rounded UP."""
    return (lam - 1) * (i + 1 + SQ2H_UP)


# ----------------------------------------------------------------------------- exact union statistics
def convex_hull(pts):
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def union_stats(pcs):
    """exact: the bounding box, the Euclidean diameter^2 of the union of the centre rects (via the convex hull of
    their corners), the l-inf diameter."""
    corners = []
    for _, r in pcs:
        corners += [(r[0], r[2]), (r[1], r[2]), (r[1], r[3]), (r[0], r[3])]
    hull = convex_hull(corners)
    d2 = Fr(0)
    for i in range(len(hull)):
        for j in range(i + 1, len(hull)):
            dx, dy = hull[i][0] - hull[j][0], hull[i][1] - hull[j][1]
            d2 = max(d2, dx * dx + dy * dy)
    bb = (min(c[0] for c in corners), max(c[0] for c in corners), min(c[1] for c in corners), max(c[1] for c in corners))
    return dict(bbox=bb, diam2=d2, linf=max(bb[1] - bb[0], bb[3] - bb[2]), n_hull=len(hull))


# ----------------------------------------------------------------------------- the count search with per-slot caps
def count_search(slots, free_opts, fixed_opts, n_free, lines, base_chords, s, caps, node_cap=200000, use_chords=True):
    """A198's exact cover search (fastprop.count_search) with `caps[p]` = the maximum number of ANONYMOUS free
    squares that may meet slot p (CN / A1-U / CHORD-U).  Feasible => witness; infeasible => exhaustive unless capped."""
    names = list(fixed_opts)
    nodes = [0]
    capped = [False]
    by_slot = {p: [o for o in free_opts if p in o[1]] for p in slots}

    def chords_ok(ch):
        return (not use_chords) or all(ch[L] <= s for L in lines)

    def add(ch, c):
        return {L: ch[L] + c[L] for L in lines}

    def compat(o, chosen):
        return all(FP.a1_compatible(o[3], c[1][3]) for c in chosen)

    def rec_free(demand, used, ch, left, chosen, anon):
        nodes[0] += 1
        if nodes[0] > node_cap:
            capped[0] = True
            return None
        need = [p for p in slots if demand[p] > 0]
        if not need:
            return list(chosen)
        if left == 0:
            return None
        tot = sum(demand[p] for p in need)
        best, cands = None, None
        for p in need:
            cs = [o for o in by_slot[p] if o[0] not in used and anon[p] < caps[p]
                  and all(anon[q] < caps[q] for q in o[1] if q in anon)]
            if best is None or len(cs) < len(cands):
                best, cands = p, cs
            if not cs:
                return None
        maxS = max(len(o[1]) for o in free_opts) if free_opts else 0
        if left * maxS < tot:
            return None
        for o in cands:
            if not compat(o, chosen):
                continue
            ch2 = add(ch, o[2])
            if not chords_ok(ch2):
                continue
            d2 = dict(demand)
            a2 = dict(anon)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
                    a2[q] += 1
            r = rec_free(d2, used | {o[0]}, ch2, left - 1, chosen + [("free", o)], a2)
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    def rec_fixed(k, demand, used, ch, chosen):
        if k == len(names):
            return rec_free(demand, used, ch, n_free, chosen, {p: 0 for p in slots})
        for o in fixed_opts[names[k]]:
            if o[0] in used or not compat(o, chosen):
                continue
            ch2 = add(ch, o[2])
            if not chords_ok(ch2):
                continue
            d2 = dict(demand)
            for q in o[1]:
                if q in d2:
                    d2[q] -= 1
            r = rec_fixed(k + 1, d2, used | {o[0]}, ch2, chosen + [(names[k], o)])
            if r is not None:
                return r
            if capped[0]:
                return None
        return None

    w = rec_fixed(0, {p: 2 for p in slots}, frozenset(), dict(base_chords), [])
    return FP.CountResult(w is not None or capped[0], w, nodes[0], capped[0])


# ----------------------------------------------------------------------------- the page
def set_pad(items, lam, s=S_RAT):
    """the slot boxes with Theorem FC's pad at dilation lam (lam = LAM_MAX: the whole window [3.82, s0]; LAM_G1: A57's G1
    slab (3.861637, s0], the k5_16 pages' own window; 1: pad 0, a statement at side s0 only -- WINDOW-PENDING)."""
    for it in items:
        c, i, j = it["corner"], it["i"], it["j"]
        xa, ya = CL.frame_to_xy(c, i, j, float(s))
        xb, yb = CL.frame_to_xy(c, i + 1 + float(pad_i(i, lam)), j + 1 + float(pad_i(j, lam)), float(s))
        it["wbox"] = (min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb))
        X0, X1, Y0, Y1 = it["wbox"]
        it["window"] = (max(0.5, X0 - CL.SQ2H), min(float(s) - 0.5, X1 + CL.SQ2H), max(0.5, Y0 - CL.SQ2H), min(float(s) - 0.5, Y1 + CL.SQ2H))
        it["wb"], it["win"] = FP.slot_geometry(it, s)
    return items


class QPage(FP.Page):
    def __init__(self, *a, refine_union=2, pad="window", **kw):
        super().__init__(*a, **kw)
        self.pad = pad
        self.lam = PADS[pad]
        if pad != "window":
            set_pad(self.items, self.lam, self.s)
        self.refine_union = refine_union
        self.role_slots, self.role_corner = {}, {}
        self.caps_last = {}
        self.union_last = {}
        self.witness = None

    # ------------------------------------------------------------------ the union of a slot's anonymous survivors
    def slot_union(self, p, single):
        pcs = []
        for ci in single.get(p, {}):
            pcs += self.reach(ci, frozenset([p]))[1]
        return pcs

    def fixed_chords(self):
        """pins (exact boxes) + every other role's pieces: the min open chord per guard line of the FIXED squares."""
        ch = dict(self.pin_chords)
        for k in self.nd.names:
            if k.startswith("P"):
                continue
            mc = FP.minchord_pieces(self.nd.boxes[k].pieces, self.lines)
            for L in self.lines:
                ch[L] += mc[L]
        return ch

    def union_cap(self, p, pcs, base_ch, refine=True):
        """-> (cap, record): cap = 0 (no anonymous meeter), 1 (at most one: CN / A1-U / CHORD-U), INF."""
        t0 = time.time()
        if not pcs:
            return 0, dict(slot=p, cap=0, why="no surviving piece")
        st = union_stats(pcs)
        mc = FP.minchord_pieces(pcs, self.lines)
        rowsum = {L: base_ch[L] + 2 * mc[L] for L in self.lines}
        Lbest = max(self.lines, key=lambda L: rowsum[L])
        rec = dict(slot=p, n_pieces=len(pcs), bbox=FP.rect_f(st["bbox"]), diam=round(math.sqrt(float(st["diam2"])), 5),
                   linf=round(float(st["linf"]), 5), chord_line="%s=%.4f" % (Lbest[0], float(Lbest[1])),
                   chord_fixed=round(float(base_ch[Lbest]), 4), chord_min=round(float(mc[Lbest]), 4),
                   chord_row=round(float(rowsum[Lbest]), 4), refined=0)
        if st["diam2"] < 1:
            rec.update(cap=1, why="CN: union diameter %.4f < 1" % rec["diam"])
        elif st["linf"] <= SQ2H_LO:
            rec.update(cap=1, why="A1-U: union l-inf diameter %.4f < 1/sqrt2" % rec["linf"])
        elif rowsum[Lbest] > self.s:
            rec.update(cap=1, why="CHORD-U: fixed %.4f + 2 x %.4f > s on %s" % (rec["chord_fixed"], rec["chord_min"], rec["chord_line"]))
        elif refine and self.refine_union > 0 and (st["diam2"] < Fr(169, 100) or st["linf"] < Fr(95, 100) or rowsum[Lbest] > self.s - Fr(1, 4)) \
                and len(pcs) <= 1500:
            # borderline: bisect the union two levels further against every core + MISS (sound: a refinement)
            wbs = [self.item[p]["wb"]]
            corner = self.item[p]["corner"] if self.item[p]["is_corner"] else None
            fr, pcs2, nt = FP.bisect_region(None, self.obstacles_for_free(), wbs, self.s, self.nd.stats, depth=self.refine_union,
                                            corner=corner, seed_pieces=pcs, max_pieces=4000)
            self.T.test("REACH-REFINE", slot=p, n_in=len(pcs), n_out=len(pcs2), frac=round(fr, 6), n_exact=nt,
                        seconds=round(time.time() - t0, 3))
            self.union_last[p] = pcs2
            cap, rec2 = self.union_cap(p, pcs2, base_ch, refine=False)
            rec2["refined"] = self.refine_union
            rec2["seconds"] = round(time.time() - t0, 3)
            return cap, rec2
        else:
            rec.update(cap=INF, why="no union exclusion fires")
        rec["seconds"] = round(time.time() - t0, 3)
        return rec["cap"], rec

    # ------------------------------------------------------------------ one propagation round
    def propagate_round(self, rnd):
        free_opts, fixed_opts, single = self.build_options()
        info = dict(round=rnd, single={p: {ci: round(f, 4) for ci, f in v.items()} for p, v in single.items()},
                    n_free_opts=len(free_opts), fixed={r: [(ci, sorted(S)) for ci, S, _, _ in v] for r, v in fixed_opts.items()},
                    free_opts=[(ci, sorted(S), FP.rect_f(h)) for ci, S, _, h in free_opts])
        roles_reach = {}
        for r in fixed_opts:
            roles_reach[r] = set()
            for ci, S, _, _ in fixed_opts[r]:
                roles_reach[r] |= S
        H_reach = roles_reach[self.H]
        info["H_reach"] = sorted(H_reach)
        # --- (b) the union exclusions per slot
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
                    st = union_stats(pcs)
                    rec.update(bbox=FP.rect_f(st["bbox"]), diam=round(math.sqrt(float(st["diam2"])), 5), linf=round(float(st["linf"]), 5))
            else:
                cap, rec = self.union_cap(p, pcs, base_ch)
            caps[p], urec[p] = cap, rec
            self.T.test("UNION", **rec)
        self.caps_last = dict(caps)
        info["union"] = urec
        info["caps"] = {p: (None if c >= INF else c) for p, c in caps.items()}
        self.T.step("union", time.time() - t0, caps=info["caps"])
        # --- (c) the per-slot forcing (Theorem FC: two distinct non-pin meeters)
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
        # --- (e) the joint count with the caps, H free
        n_anon = self.n_free - len(self.role_cell)
        t0 = time.time()
        r = count_search(self.slots, free_opts, fixed_opts, n_anon, self.lines, self.pin_chords, self.s, caps, use_chords=False)
        info["count_nochord"] = dict(feasible=r.feasible, nodes=r.nodes, capped=r.capped)
        self.T.step("count", time.time() - t0, chords=False, feasible=r.feasible, nodes=r.nodes, capped=r.capped)
        if not r.feasible:
            self.dead = "JOINT COUNT (caps %s): no cover of the %d forced slots by H + %d role(s) + %d anonymous squares" % (
                info["caps"], len(self.slots), len(self.role_cell), n_anon)
            self.T.test("COUNT", chords=False, verdict="DEAD", nodes=r.nodes, n_free_opts=len(free_opts), caps=info["caps"])
            info["dead"] = self.dead
            return info
        t0 = time.time()
        r2 = count_search(self.slots, free_opts, fixed_opts, n_anon, self.lines, self.pin_chords, self.s, caps, use_chords=True)
        info["count_chord"] = dict(feasible=r2.feasible, nodes=r2.nodes, capped=r2.capped)
        self.T.step("count", time.time() - t0, chords=True, feasible=r2.feasible, nodes=r2.nodes, capped=r2.capped)
        if not r2.feasible:
            self.dead = "JOINT COUNT + CHORD ROWS (caps %s): no cover of the %d forced slots" % (info["caps"], len(self.slots))
            self.T.test("COUNT", chords=True, verdict="DEAD", nodes=r2.nodes, n_free_opts=len(free_opts), caps=info["caps"])
            info["dead"] = self.dead
            return info
        self.witness = r2.witness if r2.witness is not None else r.witness
        info["witness"] = [(who, ci, sorted(S)) for who, (ci, S, _, _) in (self.witness or [])]
        # --- bar H from p: infeasible => H forced at p
        for p in self.slots:
            if p in forced_H or p not in H_reach or self.T.out_of_time():
                continue
            fo = dict(fixed_opts)
            fo[self.H] = [o for o in fixed_opts[self.H] if p not in o[1]]
            t0 = time.time()
            rr = count_search(self.slots, free_opts, fo, n_anon, self.lines, self.pin_chords, self.s, caps, use_chords=False)
            if rr.feasible:
                rr = count_search(self.slots, free_opts, fo, n_anon, self.lines, self.pin_chords, self.s, caps, use_chords=True)
            self.T.step("count-barH", time.time() - t0, slot=p, feasible=rr.feasible, nodes=rr.nodes, capped=rr.capped)
            if not rr.feasible:
                forced_H.add(p)
                self.T.test("COUNT", barH=p, verdict="H forced at %s" % p, nodes=rr.nodes)
        info["forced_H"] = sorted(forced_H)
        info["forced_role"] = {r: sorted(v) for r, v in forced_role.items()}
        info["instantiate"] = sorted(instantiate)
        changed = False
        # --- apply: clip H
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
            self.T.test("H-CLIP", slots=sorted(S), frac=round(fr, 6), n_pieces=len(pcs), box_before=FP.rect_f(self.roles[self.H]),
                        box_after=FP.rect_f(newH))
            self.roles[self.H] = newH
            info["H_box"] = FP.rect_f(newH)
            changed = True
        # --- apply: clip the forced roles
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
            self.roles[r] = nb
            self.role_slots[r] = tuple(sorted(S))
            self.T.test("ROLE-CLIP", role=r, slots=sorted(S), box_after=FP.rect_f(nb))
            changed = True
        # --- apply: instantiate the unique anonymous meeter of p (exists and is distinct: see the module docstring)
        for p in sorted(instantiate):
            pcs = self.union_last.get(p) or []
            if not pcs:
                continue
            hull = FP.pieces_hull(pcs)
            role = "F%d" % (len(self.role_cell) + 1)
            box = (FP.fl(hull[0]), FP.fl(hull[1]), FP.fl(hull[2]), FP.fl(hull[3]), MB.deg_of_t(hull[4]), MB.deg_of_t(hull[5]))
            self.roles[role] = box
            self.role_cell[role] = -1                       # not cell-bound: distinct by the anonymous semantics
            self.role_slots[role] = (p,)
            if self.item[p]["is_corner"]:
                self.role_corner[role] = self.item[p]["corner"]
            self.T.test("INSTANTIATE", role=role, slot=p, box=FP.rect_f(box), n_pieces=len(pcs), why=urec[p]["why"])
            changed = True
        info["changed"] = changed
        return info

    @staticmethod
    def _shrink(old, pcs):
        hull = FP.pieces_hull(pcs)
        nb = (FP.fl(hull[0]), FP.fl(hull[1]), FP.fl(hull[2]), FP.fl(hull[3]), MB.deg_of_t(hull[4]), MB.deg_of_t(hull[5]))
        return (max(nb[0], old[0]), min(nb[1], old[1]), max(nb[2], old[2]), min(nb[3], old[3]), max(nb[4], old[4]), min(nb[5], old[5]))

    # ------------------------------------------------------------------ the loop
    def run(self, max_rounds=6):
        if self.normalise("base") is None:
            return self.result()
        for rnd in range(1, max_rounds + 1):
            info = self.propagate_round(rnd)
            self.rounds.append(info)
            if self.dead or not info.get("changed") or self.T.out_of_time():
                break
            if self.normalise("round%d" % rnd) is None:
                break
        return self.result()

    def result(self):
        out = super().result()
        out["caps"] = {p: (None if c >= INF else c) for p, c in self.caps_last.items()}
        out["role_slots"] = {r: list(v) for r, v in self.role_slots.items()}
        return out


# ----------------------------------------------------------------------------- (d) SEAL at every pinned corner with both neighbours forced
def seal_corners(page):
    pins = CL.pins_of(page.cls)
    out = []
    for c in CL.CORNERS:
        if not CL.is_pin(pins, CL.slot_centre(c, 0, 0)):
            continue
        b01, b10 = "%s(0,1)" % c, "%s(1,0)" % c
        if b01 in page.item and b10 in page.item:
            out.append((c, b01, b10))
            out.append((c, b10, b01))
    return out


def seal_leaf(page, wall_left, log=print, lams=None):
    """A199's corner chain with the CLIPPED H (pins + H only: the instantiated roles are dropped -- a relaxation).
    At the window pad first (a kill there is window-valid), then pad 0 (s0-only: WINDOW-PENDING)."""
    import seal199 as S
    import seal199b as SB
    corners = seal_corners(page)
    if not corners or page.nd is None:
        return None
    if lams is None:
        lams = ((page.pad, page.lam),)
    rec = dict(page.rec)
    rec["H"] = [tuple(page.roles[h]) for h in page.hnames]
    pg = dict(page=page.name, record=None, rec=rec, cls=page.cls, items={it["cell"]: it for it in page.items})
    runs = []
    t0 = time.time()
    for tag, lam in lams:
        for (c, B, A) in corners:
            if wall_left is not None and time.time() - t0 > wall_left - 30:
                return dict(runs=runs, verdict="ALIVE", leaf="seal: wall", seconds=round(time.time() - t0, 1))
            t1 = time.time()
            r = SB.run_corner(pg, c, B, A, S.S0, lam, log=lambda *a: None)
            r = dict(corner=c, B=B, A=A, pad=tag, lam=float(lam), verdict=r["verdict"], leaf=r.get("leaf"),
                     steps=r["steps"], seconds=round(time.time() - t1, 1))
            runs.append(r)
            page.T.step("seal", r["seconds"], corner=c, B=B, A=A, pad=tag, verdict=r["verdict"])
            log("   seal %s/%s (%s pad): %s (%.0f s)" % (c, B, tag, r["verdict"], r["seconds"]))
            if r["verdict"] == "DEAD":
                return dict(runs=runs, verdict="DEAD", pad=tag, corner=c, B=B, A=A,
                            leaf="corner seal at %s (F meets %s, %s unmet) at the %s pad" % (c, B, A, tag),
                            seconds=round(time.time() - t0, 1))
    return dict(runs=runs, verdict="ALIVE", seconds=round(time.time() - t0, 1))


# ----------------------------------------------------------------------------- (f) no-room at >= 9 boxed roles
def noroom_leaf(page, log=print):
    if page.nd is None or len(page.roles) < 9:
        return None
    import noroom189 as NR
    t0 = time.time()
    r = NR.noroom(dict(page.roles), name=page.name, nd=page.nd)
    page.T.step("noroom", time.time() - t0, verdict=r.get("verdict"), bound=r.get("bound"), k=r.get("k"))
    log("   no-room (k=%s): %s" % (r.get("k"), r.get("verdict")))
    return r


# ----------------------------------------------------------------------------- (g) the deep path: the fine pair test per slot
def deep_pair(page, wall_left, log=print, nsub=8, refine=4):
    """A178's geo178b.slot_pair_test (H-meets + two-free, Lemma A1 cells, nsub 8 / refine 4) on the clipped node, slot by
    slot from the most constrained unbounded one (smallest union diameter); an instantiated role F_k is passed as a fixed
    obstacle ONLY when it provably misses the slot (then it cannot be the meeter B the test instantiates: sound)."""
    import geo178b as GB
    if page.nd is None:
        return None
    rd = page.rounds[-1] if page.rounds else {}
    urec = rd.get("union") or {}
    order = sorted([p for p in page.slots if page.caps_last.get(p, INF) >= INF],
                   key=lambda p: (urec.get(p, {}).get("diam") or 9, len(rd.get("single", {}).get(p, {}))))
    order += [p for p in page.slots if p not in order and page.caps_last.get(p, INF) > 0]
    t0 = time.time()
    runs = []
    for p in order:
        if wall_left is not None and time.time() - t0 > wall_left - 120:
            break
        it = page.item[p]
        hull = {h: list(page.roles[h]) for h in page.hnames}
        fixed = dict(page.pins)
        for r in page.role_cell:
            if not page.role_reach(r, frozenset([p]))[1]:
                fixed[r] = tuple(page.roles[r])
        t1 = time.time()
        res = GB.slot_pair_test(fixed, list(page.hnames), hull, it, nsub=nsub, refine=refine, log=lambda *a: None, label=page.name,
                                max_pairs=400, max_cells=24)
        r = dict(slot=p, alive=res["alive"], leaf=res.get("leaf"), seconds=round(time.time() - t1, 1), subcases=res.get("subcases"),
                 fixed_roles=sorted(k for k in fixed if not k.startswith("P")))
        runs.append(r)
        page.T.step("pair-test", r["seconds"], slot=p, alive=res["alive"], fixed=r["fixed_roles"])
        log("   pair test on %s (fixed %s): %s (%.0f s)" % (p, r["fixed_roles"], "ALIVE" if res["alive"] else "DEAD", r["seconds"]))
        if not res["alive"]:
            return dict(runs=runs, slot=p, alive=False, leaf="pair test (geo178b, nsub %d / refine %d) at %s: %s" % (nsub, refine, p, res.get("leaf")),
                        seconds=round(time.time() - t0, 1))
    return dict(runs=runs, alive=True, seconds=round(time.time() - t0, 1))


# ----------------------------------------------------------------------------- driver
def run_page(nid, wall=900, depth=5, joint_depth=2, refine_union=2, seal=True, pad="window", log=print):
    T = FP.Trace(wall=wall)
    rec, cls, row = FP.load_page(nid)
    log("== %s (%s) at the %s pad: %d pins, H %s" % (nid, cls, pad, len(rec["pins"]), [round(v, 3) for v in rec["H"][0]]))
    pg = QPage(rec, cls, nid, T, depth=depth, joint_depth=joint_depth, refine_union=refine_union, pad=pad)
    log("   forced cells: %s; grid side %.4f; free squares %d" % ([it["cell"] for it in pg.items], float(pg.side), pg.n_free))
    out = pg.run()
    for rd in out["rounds"]:
        log("   round %d: alive cells %s; caps %s; H reaches %s; forced_H %s; roles %s; instantiate %s; count %s / chords %s%s" % (
            rd["round"], {p: len(v) for p, v in rd["single"].items()}, rd.get("caps"), rd.get("H_reach"), rd.get("forced_H"),
            rd.get("forced_role"), rd.get("instantiate"), (rd.get("count_nochord") or {}).get("feasible"),
            (rd.get("count_chord") or {}).get("feasible"), ("; DEAD: " + rd["dead"]) if rd.get("dead") else ""))
        for p, u in (rd.get("union") or {}).items():
            log("      %-8s cap %s  %s  (n %s, diam %s, linf %s, row %s)" % (p, u.get("cap"), u.get("why"), u.get("n_pieces"), u.get("diam"), u.get("linf"), u.get("chord_row")))
    out["step_killed"] = None
    if out["verdict"] == "DEAD":
        out["step_killed"] = "propagation"
    else:
        nr = noroom_leaf(pg, log)
        out["noroom"] = nr
        if nr and nr.get("verdict") == "DEAD":
            out["verdict"], out["leaf"], out["step_killed"] = "DEAD", "no-room (A189 Lemma 1): %s" % nr.get("reason"), "noroom"
    if out["verdict"] == "ALIVE" and seal:
        sl = seal_leaf(pg, T.left(), log)
        out["seal"] = sl
        if sl and sl["verdict"] == "DEAD":
            out["verdict"], out["leaf"], out["step_killed"] = "DEAD", sl["leaf"], "seal"
    out["pad"] = pad
    out["lam"] = float(PADS[pad])
    out["window_pending"] = (pad == "zero") and out["verdict"] == "DEAD"
    if out["window_pending"]:
        out["leaf"] = (out["leaf"] or "") + " [pad 0: s0-only, WINDOW-PENDING]"
    out["tests"] = T.tests
    out["steps"] = T.steps
    out["seconds"] = round(T.now(), 1)
    out["row"] = dict(family=row.get("family"), camp=row.get("camp"), tau=row.get("tau"))
    log("   => %s in %.1f s (%d exact tests)%s" % (out["verdict"], out["seconds"], len(T.tests), ("; " + out["leaf"]) if out["leaf"] else ""))
    return out, pg


def emit(out, cert, res):
    if cert:
        json.dump(out, open(cert, "w", encoding="utf-8"), indent=1, default=str)
    if res:
        slim = {k: v for k, v in out.items() if k not in ("tests", "steps", "rounds", "seal", "noroom")}
        slim["cert"] = os.path.relpath(cert, ROOT).replace("\\", "/") if cert else None
        slim["n_rounds"] = len(out.get("rounds") or [])
        slim["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(res, "a", encoding="utf-8") as f:
            f.write(json.dumps(slim, default=str) + "\n")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--wall", type=float, default=900)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument("--jdepth", type=int, default=2)
    ap.add_argument("--refine-union", type=int, default=2)
    ap.add_argument("--noseal", action="store_true")
    ap.add_argument("--pad", default="g1", choices=("window", "g1", "zero"))
    ap.add_argument("--chain", action="store_true", help="the quick chain: the g1 pad (the page's window), then (if ALIVE) pad 0 (s0-only)")
    ap.add_argument("--deep", action="store_true", help="if ALIVE after the quick path: the fine pair test (A198's fallback)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cert", default=None)
    ap.add_argument("--svg", default=None)
    a = ap.parse_args()
    pads = ("g1", "zero") if a.chain else (a.pad,)
    outs, pages = [], []
    # the quick chain: propagation at the g1 pad, then at pad 0 (cheap: ~100-200 s each); SEAL (~300-600 s per corner) only
    # if both leave the page alive, at the g1 pad first (window-valid) then at pad 0
    for k, pad in enumerate(pads):
        out, pg = run_page(a.nid, wall=a.wall, depth=a.depth, joint_depth=a.jdepth, refine_union=a.refine_union, seal=False, pad=pad)
        out["path"] = "quick"
        out["chain_done"] = (not a.chain and a.noseal) or out["verdict"] == "DEAD"
        outs.append(out)
        pages.append(pg)
        cert = a.cert if (not a.chain or k == 0) else (a.cert[:-5] + "_pad0.json" if a.cert else None)
        out["cert_path"] = cert
        emit(out, cert, a.out)
        if out["verdict"] == "DEAD":
            break
    if outs[-1]["verdict"] == "ALIVE" and not a.noseal:
        for k, (out, pg) in enumerate(zip(outs, pages)):
            if pg.pad != "zero":
                out["chain_done"] = False                        # SEAL is run at pad 0 only (the corner strip is what it removes;
                continue                                         # at the g1 pad it stayed alive on Y0054 / Y0044 at 300-600 s a corner)
            sl = seal_leaf(pg, a.wall, print)
            out["seal"] = sl
            out["chain_done"] = (k == len(outs) - 1) or (sl is not None and sl["verdict"] == "DEAD")
            if sl and sl["verdict"] == "DEAD":
                out["verdict"], out["leaf"], out["step_killed"] = "DEAD", sl["leaf"], "seal"
                out["window_pending"] = out["pad"] == "zero"
                if out["window_pending"]:
                    out["leaf"] += " [pad 0: s0-only, WINDOW-PENDING]"
            out["tests"], out["steps"], out["seconds"] = pg.T.tests, pg.T.steps, round(pg.T.now(), 1)
            print("   => after SEAL at the %s pad: %s%s" % (out["pad"], out["verdict"], ("; " + out["leaf"]) if out["leaf"] else ""), flush=True)
            emit(out, out["cert_path"], a.out)
            if out["verdict"] == "DEAD":
                break
    out, pg = outs[0], pages[0]                                                        # the g1-pad node is the one the deep path continues
    if out["verdict"] == "ALIVE" and a.deep:
        pr = deep_pair(pg, a.wall, print)
        out["pair_test"] = pr
        out["path"] = "deep"
        out["chain_done"] = True
        if pr is not None and not pr["alive"]:
            out["verdict"], out["leaf"], out["step_killed"] = "DEAD", pr["leaf"], "pair-test"
        out["tests"], out["steps"], out["seconds"] = pg.T.tests, pg.T.steps, round(pg.T.now(), 1)
        emit(out, out["cert_path"], a.out)
    if a.svg and all(o["verdict"] == "ALIVE" for o in outs):
        import fig200
        fig200.draw(pages[-1], outs, a.svg)
