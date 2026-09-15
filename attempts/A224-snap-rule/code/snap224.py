"""A224 -- Rule SNAP (docs/proofs/snap_rule.md): a near-simple role whose slot cell no OTHER square can meet
TELEPORTS into the slot, landing the packing in the extension stratum; if that stratum is closed on the window the
node is DEAD.

Soundness (one line per step, the whole chain already in the repo):
  [T] teleport / Lemma SWAP -- lean Statements/Open/RingSwap.lean `teleport_of_swap`, `swap_packing`: replacing the
      squares of X by unit squares in the container, interior-disjoint from every OTHER square, is a packing at the
      SAME side.  The slot form is Statements/SnapRule.lean (`snap_step`, `snap_dead`, `snap_diag_two`).
  [T] the page -> side-m transfer -- Theorem FC Step 2 (`ForcedCorners.fc_transfer`, docs/proofs/forced_corners.md
      s.2): if the side-m square Q meets int B_p(m) then its dilate meets the WIDENED box B_p+ = pg.item[p]["wb"].
      So "every pose in the role's pieces misses B_p+ exactly" (A161's separating-axis test) certifies the side-m
      miss.  Contrapositive direction only -- never the other way.
  [T] the PINS need no test: every slot of `pg.slots` is UNCLIPPED for the class (A178 classes178.forced_cells ->
      `clipped_by_pin`), i.e. the exact pin squares at side m miss int B_p(m) by construction (Lemma SLOT-CROWD's
      `hunclip`).  Slack pin BOXES on the page would never pass a geometric test and do not have to.
  [T] the ANONYMOUS squares (clause (b)): vacuous at a FULLY NAMED node (all 11 squares are pins, H or instantiated
      roles); at a partially named node the FRESH option table decides it -- `single[p]` is A198's reach of a free
      square into B_p+ clipped against every role's K', so an EMPTY row means no anonymous square meets the cell.
      Where neither holds SNAP makes no claim (counted as `partial`).
  [T] the target stratum: pins(S) + the snapped slot(s) -> a census class name (A53 name_to_slots via
      classes178.class_of) whose scoreboard row is FULL [191/50, 969271/250000] (A56 + A61 + A114 + A146, 52/52).

READ-ONLY on A161 (chordlane), A178 (classes178), A171 (multibox): wrapped, never edited.  Flag A224_SNAP=1.
"""
import os
from fractions import Fraction as Fr

import classes178 as C178                                     # noqa: E402  READ-ONLY (A178) class table + scoreboard
import multibox as MB                                         # noqa: E402  READ-ONLY (A171)
import strata224 as ST                                        # noqa: E402  the target stratum + the leaf text

_CL = [None]


def CL():
    """A161's chordlane, imported on FIRST USE only: with the flag off (or no candidate) this module costs nothing
    beyond a json read, so the OLD behaviour of every runner that imports it is unchanged."""
    if _CL[0] is None:
        import chordlane                                       # READ-ONLY (A161): wrapped, never edited
        _CL[0] = chordlane
    return _CL[0]


ON = (os.environ.get("A224_SNAP") or "").strip().lower() in ("1", "on", "yes")
EPS_C = float(os.environ.get("A224_SNAP_EPS") or 0.06)        # candidate: l-inf centre distance to the slot centre
DEG = float(os.environ.get("A224_SNAP_DEG") or 3.0)           # candidate: the tilt interval within DEG of alignment
MAX_PIECES = int(os.environ.get("A224_SNAP_MAXPIECES") or 4000)
HALF = Fr(1, 2)


# --------------------------------------------------------------------------- the exact miss test, taken in t
def misses_t(x0, x1, y0, y1, t0, t1, cell):
    """A161 `box_misses_cell_exact` with the tilt bin given as t = tan(th/2) directly (the engine's pieces carry t,
    and a round trip through degrees would round the bin INWARD -- unsound).  Same separating axes, same proof."""
    if t0 < 0 or t1 > 1 or t1 < t0:
        return False, None                                     # outside A161's [0, 1] bin: no claim
    X0, X1, Y0, Y1 = cell
    cl = CL()
    hmax = cl.cs_max_exact(t0, t1) / 2                         # family A: the cell's own normals
    for nm, m in (("ex+", x0 - X1), ("ex-", X0 - x1), ("ey+", y0 - Y1), ("ey-", Y0 - y1)):
        if m >= hmax:
            return True, dict(axis=nm, margin=str(m - hmax), radius=str(hmax))
    DX, DY = (x0 - X1, x1 - X0), (y0 - Y1, y1 - Y0)            # family B: the square's own normals, radius 1/2
    for k in (0, 1):
        for sg in (1, -1):
            worst = None
            for dx in DX:
                for dy in DY:
                    ex, ey = (sg * dx, sg * dy)
                    if k == 1:
                        ex, ey = ey, -ex
                    g = cl._proj_min_exact(ex, ey, t0, t1)
                    worst = g if worst is None else min(worst, g)
            if worst >= HALF:
                return True, dict(axis="w%d%s" % (k, "+" if sg > 0 else "-"), margin=str(worst - HALF), radius="1/2")
    return False, None


def role_misses(pg, k, cell):
    """EVERY pose the node still allows for role k gives a square whose interior misses `cell`.  The hull box first
    (cheap and sufficient when it fires), the pieces after (strictly stronger: their union is the hull box clipped)."""
    b = pg.roles[k]
    ok, det = misses_t(Fr(float(b[0])), Fr(float(b[1])), Fr(float(b[2])), Fr(float(b[3])),
                       MB.t_lo(b[4]), MB.t_hi(b[5]), cell)
    if ok:
        return True, dict(det, src="hull box", n_pieces=1)
    pcs = pg.pieces.get(k) or []
    if not pcs or len(pcs) > MAX_PIECES:
        return False, None
    for (bn, r) in pcs:
        ok2, _d = misses_t(Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), bn.t0, bn.t1, cell)
        if not ok2:
            return False, None
    return True, dict(src="pieces", n_pieces=len(pcs), axis="per piece (each piece separated)", margin=None)


# --------------------------------------------------------------------------- candidates
def slot_cell(pg, p):
    return tuple(Fr(v) for v in pg.item[p]["wb"])              # B_p+ : the page's own widened slot box


def slot_centre(pg, p):
    it = pg.item[p]
    return C178.frame_to_xy(it["corner"], it["i"] + 0.5, it["j"] + 0.5, float(pg.s))


def tilt_span(pg, k):
    """the role's tilt as the engine really carries it: the PIECES' bins, not their hull -- a square whose pieces sit
    at 0.3 deg and at 89.6 deg is ALIGNED (same square), while the hull box reads [0, 90]."""
    pcs = pg.pieces.get(k) or []
    if not pcs:
        b = pg.roles[k]
        return [(float(b[4]), float(b[5]))]
    return [(float(MB.deg_of_t(bn.t0)), float(MB.deg_of_t(bn.t1))) for bn, _r in pcs]


def near(pg, k, p):
    """the cheap candidate filter: the role's box centre within EPS_C of the slot centre and EVERY piece's tilt bin
    within DEG of alignment (0 or 90 deg).  Heuristic only -- the CERTIFICATE is the miss tests."""
    b = pg.roles[k]
    sx, sy = slot_centre(pg, p)
    d = max(abs(0.5 * (b[0] + b[1]) - sx), abs(0.5 * (b[2] + b[3]) - sy))
    sp = tilt_span(pg, k)
    al = all(t1 <= DEG or t0 >= 90.0 - DEG for t0, t1 in sp)
    return (d <= EPS_C and al), round(d, 6), (round(min(t for t, _ in sp), 3), round(max(t for _, t in sp), 3), len(sp))


def anon_ok(pg, p):
    """clause (b): no ANONYMOUS square meets the slot cell.  Vacuous at a fully named node (all 11 squares are pins,
    H or instantiated roles).  Otherwise the FRESH option table decides it: `single[p]` is A198's reach of a free
    square into B_p+ clipped against EVERY role's K', so an EMPTY row means no free square meets the cell at all
    (the same object Theorem FC's count consumes; the freshness proviso is Lemma CT's, as for rule CC)."""
    if n_anon(pg) <= 0:
        return True, dict(n_anon=0, why="fully named node: no anonymous square left, clause (b) is vacuous")
    if not getattr(pg, "rounds", None) or pg.rounds[-1].get("instantiated"):
        return False, None                                     # not a fresh table: no claim
    cells = sorted((pg.rounds[-1].get("single") or {}).get(p, {}))
    if cells:
        return False, None
    return True, dict(n_anon=n_anon(pg), n_cells=0, round=len(pg.rounds),
                      why="fresh option table: NO anonymous cell survives at %s (A198 reach clipped against every role's K'), "
                          "so no anonymous square meets B_p+" % p)


def roles_of(pg):
    return [k for k in sorted(pg.roles) if not k.startswith("P")]


def n_anon(pg):
    return pg.n_free - len(pg.role_cell)


def candidates(pg):
    out = []
    for k in roles_of(pg):
        for p in pg.slots:
            ok, d, tilt = near(pg, k, p)
            if ok:
                out.append(dict(role=k, slot=p, dist=d, tilt=tilt, i=pg.item[p]["i"], j=pg.item[p]["j"],
                                corner=pg.item[p]["corner"], extension=pg.item[p].get("extension"),
                                status=pg.item[p].get("status")))
    return out


def blockers(pg, cand):
    """the OTHER roles that cannot be certified to miss the candidate's slot cell.  Pins are not tested: the slot is
    UNCLIPPED for the class, so the exact pin squares at side m miss int B_p(m) (Lemma SLOT-CROWD's hunclip)."""
    cell = slot_cell(pg, cand["slot"])
    bad, certs = [], {}
    for k in roles_of(pg):
        if k == cand["role"]:
            continue
        ok, det = role_misses(pg, k, cell)
        if ok:
            certs[k] = det
        else:
            bad.append(k)
    return bad, certs


def disjoint_cells(pg, slots):
    for a in range(len(slots)):
        for b in range(a + 1, len(slots)):
            A, B = slot_cell(pg, slots[a]), slot_cell(pg, slots[b])
            if not (A[1] <= B[0] or B[1] <= A[0] or A[3] <= B[2] or B[3] <= A[2]):
                return False
    return True


def diag_set(pg, cands):
    """SNAP-DIAG: the largest set of candidates (one slot per role, one role per slot) whose only un-missed roles are
    OTHER members of the set -- each is then blocked only by squares that are themselves snapped into their slots, so
    ONE application of Lemma SWAP replaces them all."""
    best = {}
    for c in cands:
        cur = best.get(c["role"])
        if cur is None or len(c["blockers"]) < len(cur["blockers"]):
            best[c["role"]] = c
    D = dict(best)
    while True:
        rs = set(D)
        drop = [r for r, c in D.items() if not set(c["blockers"]) <= (rs - {r})]
        if not drop:
            break
        for r in drop:
            D.pop(r)
    sel = sorted(D.values(), key=lambda c: c["role"])
    if len({c["slot"] for c in sel}) != len(sel):
        return []
    return sel


# --------------------------------------------------------------------------- the rule
def evaluate(pg, label, log=None):
    """-> None (no claim) or a record dict.  verdict DEAD (SNAP / SNAP-DIAG), HANDOFF (snapped into a stratum that is
    not closed) or None.  Cost: one miss test per other role per candidate slot; nothing at all with no candidate."""
    if not ON:
        return None
    cands = candidates(pg)
    rec = dict(label=label, n_cands=len(cands), n_anon=n_anon(pg), eps=EPS_C, deg=DEG, verdict=None,
               cands=[{k: v for k, v in c.items() if k != "status"} for c in cands][:8])
    if not cands:
        return rec
    for c in cands:
        c["blockers"], c["miss_certs"] = blockers(pg, c)
        ok, c["anon_cert"] = anon_ok(pg, c["slot"])
        c["anon"] = ok
    rec["cands"] = [dict(role=c["role"], slot=c["slot"], dist=c["dist"], tilt=c["tilt"], blockers=c["blockers"], anon=c["anon"]) for c in cands][:8]
    cands = [c for c in cands if c["anon"]]                    # clause (b) failed: no claim at this slot
    if not cands:
        rec["partial"] = True
        return rec
    sel = [c for c in cands if not c["blockers"]]
    kind = "SNAP"
    if not sel:
        sel = diag_set(pg, cands)
        kind = "SNAP-DIAG"
        if len(sel) < 2 or not disjoint_cells(pg, [c["slot"] for c in sel]):
            return rec
    else:
        sel = [sel[0]]
    tg = ST.target(pg, [c["slot"] for c in sel])
    rec.update(kind=kind, snapped=[dict(role=c["role"], slot=c["slot"], dist=c["dist"], tilt=c["tilt"],
                                        cell=[str(v) for v in slot_cell(pg, c["slot"])],
                                        miss_certs=c["miss_certs"], blockers=c["blockers"],
                                        anon_cert=c["anon_cert"]) for c in sel], target=tg)
    rec["verdict"] = "DEAD" if tg["full"] else "HANDOFF"
    rec["leaf"] = ST.leaf_text(pg, rec)
    rec["verifier"] = ST.VERIFIER
    if log:
        log("   %s at %s: %s -> stratum %s (%s)" % (kind, label, ", ".join("%s:=%s" % (c["role"], c["slot"]) for c in sel),
                                                    tg["stratum"], "CLOSED, DEAD" if tg["full"] else "alive: HAND-OFF"))
    return rec


