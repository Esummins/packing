"""A224 -- the TARGET STRATUM of a SNAP: pins(class) + the snapped slot(s) -> a census class name and its closure
record, plus the leaf text and the verifier clause of a SNAP kill.  READ-ONLY on A178 (classes178), which is the
computed form of A53's class table and the A56/A61/A114/A146 scoreboard."""
import classes178 as C178                                     # noqa: E402  READ-ONLY (A178)

FULL_PREFIX = "FULL [191/50, 969271/250000]"
SCOREBOARD = "attempts/A56-sparametric/results/scoreboard.json (A56 + A61 + A114 + A146; 52/52 FULL, docs/residue_ledger.md s.2)"


# --------------------------------------------------------------------------- the target stratum
def _pt(pg, p):
    it = pg.item[p]
    return C178.slot_centre(it["corner"], it["i"], it["j"], C178.S0)


def target(pg, slots):
    """pins(class) + the snapped slots -> the census class name and its scoreboard closure record.

    A53's census names k <= 6 only, so a SNAP-DIAG of two or more slots has no name of its own; Lemma K1 (kills climb
    containment, `Skeleton.lean`) closes it anyway -- the snapped packing contains the pins of EVERY subset, and each
    single snapped slot's extension class is a FULL scoreboard row.  `via` says which form was used."""
    pins = [tuple(q) for q in C178.pins_of(pg.cls)]
    pts = pins + [_pt(pg, p) for p in slots]
    name = C178.class_of(pts)
    st = C178.scoreboard_status(name) if name else None
    if st and str(st.get("status", "")).startswith(FULL_PREFIX):
        return dict(k=len(pts), stratum=name, full=True, status=st.get("status"), result=st.get("result"),
                    via="the extension class itself", witness_slots=list(slots), source=SCOREBOARD)
    for p in slots:                                            # Lemma K1: any closed SUBSET kills the whole
        sub = C178.class_of(pins + [_pt(pg, p)])
        s2 = C178.scoreboard_status(sub) if sub else None
        if s2 and str(s2.get("status", "")).startswith(FULL_PREFIX):
            return dict(k=len(pts), stratum=sub, full=True, status=s2.get("status"), result=s2.get("result"),
                        via="Lemma K1 (kills climb containment): the snapped packing contains the pins of %s" % sub,
                        witness_slots=[p], source=SCOREBOARD)
    return dict(k=len(pts), stratum=name, full=False, status=(st or {}).get("status"), result=(st or {}).get("result"),
                via="no closed subset", witness_slots=[], source=SCOREBOARD)


VERIFIER = ("[C: exact separating-axis miss certificates (A161 box_misses_cell_exact, taken in t) + Lemma SWAP / teleport "
            "(lean Statements/Open/RingSwap.lean `teleport_of_swap`, `swap_packing`: THEOREMS) + Theorem FC Step 2 "
            "(ForcedCorners.fc_transfer: a side-m meeter of int B_p(m) dilates into B_p+) + the class's UNCLIPPED slot census "
            "(A178 classes178) + the A56/A61/A114/A146 scoreboard row of the target stratum] Rule SNAP "
            "(docs/proofs/snap_rule.md, attempts/A224-snap-rule/code/snap224.py); no verifier clause")


def leaf_text(pg, rec):
    sn = rec["snapped"]
    tg = rec["target"]
    body = "; ".join("%s (centre within %s of the slot, tilt %s deg) snaps to %s -- every other role misses B_p+ exactly (%s), "
                     "the pins by the class's UNCLIPPED census, the anonymous squares by [%s]"
                     % (c["role"], c["dist"], c["tilt"], c["slot"],
                        ", ".join("%s %s" % (k, (v or {}).get("axis")) for k, v in sorted(c["miss_certs"].items())),
                        (c.get("anon_cert") or {}).get("why")) for c in sn)
    tail = ("the target stratum %s is CLOSED on the window (%s; %s), so no packing of the node's hypothesis exists"
            % (tg["stratum"], str(tg["status"])[:120], tg["source"])) if tg["full"] else \
           ("the target stratum %s is NOT closed (%s): HAND-OFF, the branch is handed to that stratum's tree"
            % (tg["stratum"], str(tg["status"])[:80]))
    return ("%s at %s (class %s, k %d -> %d): %s; by Lemma SWAP / teleport the packing at the same side contains the pins of "
            "%s, and %s" % (rec["kind"], rec["label"], pg.cls, tg["k"] - len(sn), tg["k"], body, tg["stratum"], tail))
