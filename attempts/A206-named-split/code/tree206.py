"""A206 -- Rule NS, the NAMED-OR-ANONYMOUS split at the clip tree's "fully named" leaves (notes/named_split.md).

A205's stop rule counts a role r as a meeter of a forced slot p whenever r is NOT PROVABLY MISSING p -- on k5_11 Y0672's
leaf R.2.3.1 H's box reaches TR(0,0)'s widened box by a 0.02 corner sliver, so TR(0,0) had "two named meeters" (H, F1)
and the anonymous cell 24 the count's own witness used was never instantiated (the PI's reading, 2026-09-11).  The
disjunction is SPLIT here: for a SOFT-named pair (p, r) -- r in named_p but the node does not hypothesise r at p --
  [r meets p]   r is named at p (H: p joins forced_H; F_i: p joins its slots; a corner slot adds the lonely clip), so
                A204's exact reach clips r to its poses meeting B_p+ every round;
  [r misses p]  r's rows containing p leave the option table (r is no meeter of p in the count, Theorem FC must find
                two others: FC instantiates a cap-1 anonymous meeter, or A205's rule branches on the rows), and every
                piece of r all of whose poses meet B_p+ (the open disc of radius 1/2 about a centre at distance < 1/2
                from the closed box) is dropped -- MISS-CLIP when nothing is left.
The two branches cover every pose of r (it meets B_p+ or it does not): the node is DEAD iff both are.  Every other
step is A205's (the copy in this directory): cascade, refresh, branch rule, sharp leaf; every kill [C: library clip trace].
"""
import time
from fractions import Fraction as Fr

import poly204 as P
import tree205 as T5
import tree205b as TB

FP, MB = P.FP, P.MB
QUARTER = Fr(1, 4)
EPS_IN = Fr(1, 10 ** 6)
SOFT_ALL = False         # True: split every soft-named pair (the qualifying ones first); False: only the qualifying ones
MAX_FRAC = 0.5           # a pair qualifies when the role's meeting fraction of the slot is below this (the sliver); Y0672's R.3
                         # subtree spent its hour splitting H at fractions 0.64-0.75 (3 kills, 11 undecided) -- not the lever


def provably_meets(rect, wb):
    """every centre in `rect` is at distance < 1/2 from the CLOSED box wb: the square's open inscribed disc meets the closed
    box, hence its interior meets the open box -- at every tilt (exact rationals)."""
    X0, X1, Y0, Y1 = (Fr(v) for v in wb[:4])
    for x in (Fr(rect[0]), Fr(rect[1])):
        dx = max(X0 - x, x - X1, Fr(0))
        for y in (Fr(rect[2]), Fr(rect[3])):
            dy = max(Y0 - y, y - Y1, Fr(0))
            if dx * dx + dy * dy >= QUARTER:
                return False
    return True


class TreePage206(T5.TreePage):
    def __init__(self, *a, **kw):
        T5.TreePage.__init__(self, *a, **kw)
        self.miss = {}                 # role -> frozenset of slots the node hypothesises the role MISSES (Rule NS)
        self.miss_rep = []

    def miss_clip(self, label):
        for r, S in self.miss.items():
            pcs = self.pieces.get(r)
            if not pcs:
                continue
            # the INNER box (the float widened box shrunk by 1e-6): meeting a smaller closed box implies meeting B_p+ (sound)
            inner = [tuple(Fr(v) + e for v, e in zip(self.item[p]["wbox"], (EPS_IN, -EPS_IN, EPS_IN, -EPS_IN))) for p in S]
            keep = [(bn, rect) for bn, rect in pcs if not any(provably_meets(rect, wi) for wi in inner)]
            n = len(pcs) - len(keep)
            if n:
                self.miss_rep.append(dict(label=label, role=r, slots=sorted(S), dropped=n, n_after=len(keep)))
                self.T.test("MISS-CLIP", role=r, slots=sorted(S), dropped=n, n_after=len(keep), label=label)
                self.pieces[r] = keep
                if not keep:
                    self.dead = "MISS-CLIP(%s) at %s: every piece of %s provably meets a slot the branch hypothesises it misses %s (Rule NS)" % (r, label, r, sorted(S))
                    self.fix_rep = dict(dead=r, detail="missclip", seconds=0.0)
                    self.T.test("MISS-CLIP", role=r, slots=sorted(S), verdict="DEAD", label=label)
                    return False
        return True

    def normalise(self, label):
        if self.miss and not self.miss_clip(label):
            self.T.step("normalise", 0.0, label=label, dead=self.fix_rep["dead"], detail="missclip")
            return None
        return T5.TreePage.normalise(self, label)

    def build_options(self):
        free_opts, fixed_opts, single = T5.TreePage.build_options(self)
        if self.miss:
            for r, S in self.miss.items():
                if r in fixed_opts:
                    n0 = len(fixed_opts[r])
                    fixed_opts[r] = [o for o in fixed_opts[r] if not (o[1] & S)]
                    self.T.step("ns-rows", 0.0, role=r, misses=sorted(S), n_before=n0, n_after=len(fixed_opts[r]))
            self.last_opts = (free_opts, fixed_opts, single)
        return free_opts, fixed_opts, single


def save_state(pg):
    st = T5.save_state(pg)
    st["miss"], st["miss_rep"] = dict(pg.miss), list(pg.miss_rep)
    return st


def restore_state(pg, st):
    T5.restore_state(pg, st)
    pg.miss, pg.miss_rep = dict(st["miss"]), list(st["miss_rep"])


def cascade(pg, rounds, log=print):
    clip, rnd = TB.cascade(pg, rounds, log=log)
    if pg.dead and (pg.fix_rep or {}).get("detail") == "missclip":
        clip = "MISS-CLIP"
    return clip, rnd


def ns_candidates(pg):
    """the SOFT-named (slot, role) pairs of a fully named node, the sliver first: r in named_p (r not provably missing p, or
    instantiated there) that the node does not hypothesise at p (H: p not forced; F_i: p not among its slots)."""
    if not pg.rounds:
        return []
    info = pg.rounds[-1]
    single = info.get("single") or {}
    reach_r = {r: set().union(*[set(S) for _, S in rows]) if rows else set() for r, rows in (info.get("fixed") or {}).items()}
    out = []
    for p in pg.slots:
        rows = sorted(int(c) for c in single.get(p, {}))
        named = [r for r in sorted(reach_r) if p in reach_r[r]]
        for r in named:
            if r == pg.H:
                if p in pg.forced_H:
                    continue
            elif p in pg.role_slots.get(r, ()):
                continue
            t0 = time.time()
            frac = pg.role_reach(r, frozenset([p]))[0]
            q = 0 if frac < MAX_FRAC else 1
            out.append(dict(slot=p, role=r, frac=round(float(frac), 6), rows=rows, named=named, qualifies=(q == 0), seconds=round(time.time() - t0, 2)))
    out.sort(key=lambda d: (0 if d["qualifies"] else 1, d["frac"], -len(d["rows"]), d["slot"], d["role"]))
    if not SOFT_ALL:
        out = [d for d in out if d["qualifies"]]
    return out


def ns_branches(c):
    base = dict(slot=c["slot"], role=c["role"], frac=c["frac"], rows=None, named=c["named"], alive_rows=c["rows"])
    return [dict(base, kind="ns-meets"), dict(base, kind="ns-misses")]


def apply_ns(pg, br):
    p, r = br["slot"], br["role"]
    if br["kind"] == "ns-meets":
        if r == pg.H:
            pg.forced_H.add(p)
        else:
            pg.role_slots[r] = tuple(sorted(set(pg.role_slots.get(r, ())) | {p}))
            if pg.item[p]["is_corner"]:
                pg.role_corner[r] = pg.item[p]["corner"]
        pg.T.test("NS-MEETS", role=r, slot=p, frac=br["frac"], forced_H=sorted(pg.forced_H), role_slots={k: list(v) for k, v in pg.role_slots.items()})
    else:
        pg.miss[r] = frozenset(pg.miss.get(r, frozenset())) | {p}
        pg.T.test("NS-MISSES", role=r, slot=p, frac=br["frac"], miss={k: sorted(v) for k, v in pg.miss.items()})
