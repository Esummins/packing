"""A268 lever (i) -- Lemma ROLE-SPLIT FORCED at a genuine fixed point (notes/terminal268.md s.3).  Flag A268_FORCE=1.

Where: A211's leaf rules end in ALIVE with "every forced slot has two named meeters after the exact cascade and the
sharp round" -- every rule (CC, no-room, basin, NS, EPS, SNAP, the exact cascade, the sharp round) has run on the
node and none moved it: the node is a FIXED POINT of the rule set (class (b) of the brief).  A211's own ROLE-SPLIT
(rsplit211) did not fire there only because of its STEERING gates (a role must be WIDE: > 0.25 in position or
> 30 deg in tilt, and no-room must have run) -- gates that notes/coarse_tree.md s.5 states are heuristic.

What: bisect the role whose box is widest RELATIVE TO THOSE SAME GATES (x / 0.25, y / 0.25, tilt / 30 deg, the
largest wins; rsplit211.role_spec's score without its > 1 threshold) at the midpoint of that dimension, and hand
the two children back to A211's tree as an ordinary ROLE-SPLIT branch (kind "rsplit", path key
("rsplit", role, dim, m, side) -- Lemma INHERIT applies unchanged).  At most FORCE_CAP forced splits per role along a
path (the tree's rsplit counter, which counts forced and gated splits alike).

Soundness: Lemma ROLE-SPLIT (notes/coarse_tree.md s.5) holds for ANY role, ANY coordinate u in {x, y, t} and ANY m
in the hull: "u <= m" or "u >= m" is exhaustive over the genuine packings of the node, each child's pieces are a
superset of the poses its hypothesis allows (rsplit211.apply_rsplit), and the node is DEAD iff both children are.
The width gate and the choice of role only steer.  The ALIVE mark the leaf rules wrote is withdrawn (the node
becomes INTERNAL with two children) -- a node that is branched is never recorded ALIVE."""
import os

FORCE_CAP = int(os.environ.get("A268_FORCE_CAP") or 8)
FIXED = "every forced slot has two named meeters after the exact cascade and the sharp round"
REP = dict(forced=0, skipped_cap=0, none=0)


def pick(pg, used):
    import rsplit211 as RS
    best = None
    for role, pcs in sorted(pg.pieces.items()):
        if role.startswith("P") or not pcs or used.get(role, 0) >= FORCE_CAP:
            continue
        x0, x1, y0, y1, t0, t1 = RS.hull_of(pcs)
        wx, wy, wt = float(x1 - x0), float(y1 - y0), RS.deg(t1) - RS.deg(t0)
        sc = dict(x=wx / RS.WIDE_POS, y=wy / RS.WIDE_POS, t=wt / RS.WIDE_TILT)
        dim = max(sc, key=lambda k: sc[k])
        if sc[dim] <= 0:
            continue
        if best is None or sc[dim] > best[0]:
            m = {"x": (x0 + x1) / 2, "y": (y0 + y1) / 2, "t": (t0 + t1) / 2}[dim]
            best = (sc[dim], dict(role=role, dim=dim, m=m, score=round(sc[dim], 6), scores={k: round(v, 6) for k, v in sc.items()},
                                  extents=dict(x=round(wx, 7), y=round(wy, 7), tilt=round(wt, 5)),
                                  box=[round(float(v), 6) for v in (x0, x1, y0, y1)] + [round(RS.deg(t0), 4), round(RS.deg(t1), 4)],
                                  core_empty=bool((pg.obst or {}).get(role) is None), n_pieces=len(pcs),
                                  n_splits=used.get(role, 0), forced=True))
    return best[1] if best else None


def install(log=print):
    import tree211 as N11
    if getattr(N11.Tree211, "_a268_force", False):
        return
    orig = N11.Tree211.leaf_rules

    def leaf_rules(self, depth, label):
        r = orig(self, depth, label)
        if r != "ALIVE" or not self.nodes:
            return r
        node = self.nodes[-1]
        why = str(node.get("reason") or "")
        if node.get("verdict") != "ALIVE" or not why.startswith(FIXED):
            return r
        pg = self.pg
        if pg.dead or pg.T.out_of_time() or self.n_nodes >= self.node_cap:
            return r
        sp = pick(pg, self.rsplit_used(label))
        if sp is None:
            REP["none"] += 1
            return r
        node.update(verdict="INTERNAL", reason=None, force268=dict({k: v for k, v in sp.items() if k != "m"}, m=str(sp["m"]), was=why[:160]))
        self.alive_leaves -= 1
        REP["forced"] += 1
        pg.T.test("FORCE-RSPLIT", label=label, role=sp["role"], dim=sp["dim"], score=sp["score"], extents=sp["extents"], n_splits=sp["n_splits"])
        self.log("   A268 FORCED ROLE-SPLIT at %s (fixed point of every rule): bisect %s on %s (extents %s, tilt %s deg; forced split %d of %d)" % (
            label, sp["role"], sp["dim"], (sp["extents"]["x"], sp["extents"]["y"]), sp["extents"]["tilt"], sp["n_splits"] + 1, FORCE_CAP))
        self._rs = sp
        return "RSPLIT"

    N11.Tree211.leaf_rules = leaf_rules
    N11.Tree211._a268_force = True
    log("   A268 FORCED ROLE-SPLIT installed at the fixed-point leaf (cap %d per role per path)" % FORCE_CAP)
