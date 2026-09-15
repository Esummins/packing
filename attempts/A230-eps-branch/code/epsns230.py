"""A230 -- Rule EPS's verdict over ALL candidates, and the NS-AT-WEDGE split (docs/proofs/lemma_eps.md s.5, s.7 [C]3).

`evaluate(pg, label)` runs eps230's rule at every near-simple (role, forced cell) candidate of the node, smallest
box first, and records all of them: DEAD by FC+EPS as soon as one candidate's cell is left with fewer than two
distinct non-pin meeters (Theorem FC demands two; F is at most one of them, so an empty survivor set with the
anonymous clause certified empty is a contradiction).  Where it does not kill, `pick_wedge` returns the split:

  exactly ONE named role M survives at a candidate (F, C) and no anonymous square meets C  ==>  M IS the second
  meeter, so M has an interior point in one of the targets of (F, C) it can still reach (EPS-3/4/5).  The two
  children "M meets W" / "M misses W" (W = the union of those targets) are exhaustive; the MISSES child is DEAD
  at once by FC+EPS with the wedge certificate and the miss certificates; the MEETS child keeps only the poses of
  M whose square reaches W -- `apply_wedge`, the exact clip: a piece is dropped when A161's separating-axis test
  separates it from EVERY target, and what survives is intersected with the union's bounding box dilated by
  h = (cos + sin)/2 over the piece's bin (EPS-6's box bound, the same family-A axis).  Depth-cap accounting is
  Rule NS's (the split counts as one level); the caller runs the coarse round after the clip, so the option table
  is FRESH before any further branching (Lemma CT's proviso).
"""
from fractions import Fraction as Fr

import poly204 as P                                           # noqa: E402  READ-ONLY (A204)
import snap224 as S                                           # noqa: E402  READ-ONLY (A224)
import eps227 as E                                            # noqa: E402  READ-ONLY (A227)
import eps230 as G                                            # noqa: E402

VERIFIER = ("[T: Lemma EPS (EPS-1..6 + GATE) + Theorem FC + A161 exact miss certificates; docs/proofs/lemma_eps.md, "
            "attempts/A230-eps-branch]")


def _fmt(T):
    return "[%s]" % ",".join(str(round(float(v), 5)) for v in T)


def evaluate(pg, label, log=None, skip=None):
    cands = G.candidates(pg)
    if not cands:
        return None
    rec = dict(label=label, rule="A230", n_cands=len(cands), n_anon=S.n_anon(pg), verdict=None, cands=[],
               n_old=sum(1 for c in cands if c["old"]), n_added=sum(1 for c in cands if not c["old"]),
               taper=dict(strikes=0, targets=0), levers=dict(allcand=G.ALLCAND, taper=G.TAPER, wedge_ns=G.WEDGE_NS))
    bud = [G.MAX_TESTS]
    for c in cands:
        F, p = c["role"], c["slot"]
        C = S.slot_cell(pg, p)
        back = E.backing(pg, C)
        tg, info = G.targets(E.hull_box(pg, F), C, back)
        rec["taper"]["targets"] += info.get("n_taper") or 0
        row = dict(role=F, slot=p, dist=c["dist"], bdist=c["bdist"], only_new=(not c["old"]), tilt=c["tilt"],
                   vol=c["vol"], gate=info["gate"], backed=info["backed"], depths=info["depths"],
                   targets=[(nm, [str(v) for v in T], pl is not None) for nm, T, pl in tg],
                   struck=[], survivors={})
        for M in S.roles_of(pg):
            if M == F:
                continue
            st = G.strike(pg, F, M, C, back, bud)
            rec["taper"]["strikes"] += st.get("taper") or 0
            if st["struck"]:
                row["struck"].append(M)
            else:
                row["survivors"][M] = dict(reach=st["reach"], via=st["via"])
        row["anon_cells"] = E.anon_survivors(pg, p, [(nm, T) for nm, T, _pl in tg])
        row["dead"] = (not row["survivors"]) and row["anon_cells"] == []
        rec["cands"].append(row)
        if row["dead"] and rec["verdict"] is None:
            rec["verdict"] = "DEAD"
            rec["kill"] = row
            rec["leaf"] = (
                "FC+EPS at %s: %s is near-simple in the forced cell %s (centre dist %s, box dist %s, tilt %s); Theorem FC "
                "demands a second distinct non-pin meeter of B_p+, which must have an interior point in a wedge target of "
                "(%s, %s) (Lemma EPS-3/4/5: %s); every other role misses every target exactly (%s) and no anonymous cell "
                "is within 1/sqrt2 of one -- the cell is left with fewer than two meeters, impossible" % (
                    label, F, p, c["dist"], c["bdist"], c["tilt"], F, p,
                    "; ".join("%s=%s" % (nm, _fmt(T)) for nm, T, _pl in tg), ", ".join(row["struck"])))
            rec["verifier"] = VERIFIER
    if rec["verdict"] is None and G.WEDGE_NS:
        w = pick_wedge(rec, label, skip)
        if w:
            rec["wedge_ns"] = w
    if log and rec["verdict"]:
        log("   FC+EPS at %s: %s at %s -- DEAD (%d candidate(s) evaluated)" % (label, rec["kill"]["role"], rec["kill"]["slot"], len(cands)))
    return rec


def pick_wedge(rec, label, skip=None):
    """the first candidate (smallest box first) with exactly one named survivor, a certified-empty anonymous clause
    and a non-empty reachable target list: the NS-at-wedge split.  `skip` holds the (slot, blocker) pairs already
    split to their cap on this path (the caller's per-pair cap: the clip tightens each time but returns diminish)."""
    skip = skip or set()
    for row in rec["cands"]:
        if row["anon_cells"] != [] or len(row["survivors"]) != 1:
            continue
        M, sv = list(row["survivors"].items())[0]
        if (row["slot"], M) in skip:
            continue
        if sv["via"] == "budget" or not sv["reach"]:
            continue
        names = set(sv["reach"])
        tgm = [t for t in row["targets"] if t[0] in names]
        if not tgm:
            continue
        W = "; ".join("%s=%s" % (t[0], _fmt([Fr(v) for v in t[1]])) for t in tgm)
        return dict(role=M, slot=row["slot"], F=row["role"], targets=tgm, n_targets=len(tgm), struck=list(row["struck"]),
                    wedge=W, verifier=VERIFIER,
                    leaf_misses=(
                        "FC+EPS at %s: %s is near-simple in the forced cell %s, so Theorem FC's second non-pin meeter of "
                        "B_p+ must have an interior point in a wedge target of (%s, %s) (Lemma EPS-3/4/5); every other "
                        "role misses every target exactly (%s), no anonymous cell is within 1/sqrt2 of one, so the second "
                        "meeter is %s -- and this branch hypothesises that %s MISSES every target it could reach "
                        "(W = %s): no second meeter is left, impossible" % (
                            label, row["role"], row["slot"], row["role"], row["slot"],
                            ", ".join(row["struck"]) or "(none)", M, M, W)))
    return None


def branches(w):
    """the two children of the NS-at-wedge split, as ordinary branch dicts (kind epsns-meets / epsns-misses)."""
    base = dict(slot=w["slot"], role=w["role"], named=None, F=w["F"], targets=w["targets"], wedge=w["wedge"],
                n_targets=w["n_targets"], verifier=w["verifier"])
    return [dict(base, kind="epsns-meets", rows=["meets W"]),
            dict(base, kind="epsns-misses", rows=["misses W"], leaf=w["leaf_misses"])]


def apply_wedge(pg, br):
    """the MEETS child: the role's pieces restricted to the poses whose square reaches SOME target of W.  A piece is
    dropped when A161's exact test separates it from every target; what survives is clipped to W's bounding box
    dilated by h = max (cos + sin)/2 over the piece's own bin (a centre reaching W is within h of it on each axis).
    Raises ValueError when nothing is left -- the caller records the child DEAD by the clip itself."""
    role = br["role"]
    rects = [tuple(Fr(v) for v in t[1]) for t in br["targets"]]
    U = (min(T[0] for T in rects), max(T[1] for T in rects), min(T[2] for T in rects), max(T[3] for T in rects))
    pcs = pg.pieces.get(role) or []
    if not pcs:
        raise ValueError("role %s carries no pieces" % role)
    cl = S.CL()
    new = []
    for bn, r in pcs:
        bx = (Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), bn.t0, bn.t1)
        if all(S.misses_t(*bx, T)[0] for T in rects):
            continue
        h = cl.cs_max_exact(bn.t0, bn.t1) / 2
        x0, x1 = max(bx[0], U[0] - h), min(bx[1], U[1] + h)
        y0, y1 = max(bx[2], U[2] - h), min(bx[3], U[3] + h)
        if x0 > x1 or y0 > y1:
            continue
        r2 = list(r)
        r2[0], r2[1], r2[2], r2[3] = x0, x1, y0, y1
        new.append((bn, tuple(r2)))
    if not new:
        raise ValueError("no pose of %s reaches the wedge W (%s)" % (role, br["wedge"]))
    pg.pieces[role] = new
    pg.roles[role] = P.hull_box(new)
    pg.T.test("EPS-WEDGE-APPLY", role=role, slot=br["slot"], F=br["F"], n_targets=br["n_targets"],
              n_before=len(pcs), n_after=len(new), box=[round(float(v), 6) for v in pg.roles[role]])
    return len(new)
