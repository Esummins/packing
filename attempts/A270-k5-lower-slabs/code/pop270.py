"""A270 -- the POPULATION of the pad-g4 campaign: A57's level-1 cover rebuilt at the g4 pin slack (READ-ONLY on A57).

Why the whole cover (notes/slabs270.md s.3): a pad-g4 DEAD on a record of pin slack 9/400 is a statement on the WHOLE
window (3.82, s0] (pads270: drift 0.0224152 <= 9/400, Corollary B'), so it closes G1 (incl. s-hat), G2, G3 and G4 at
once; and A57's own G1 leaves (LP PASS at cores 49/100, T5 logic at pin cores 49/100) do not reach G3 / G4 at all.  The
root's children are tree57.build_children(cls, 'interior', 0.15, 8, 0.6, 0.34, pin_delta=9/400): the NO child (no free
square centre in the interior zone: an LP obligation, not a page) and the YES boxes.  A YES box that tree57's pinguard
calls 'contradictory' at this slack is a T5 logic kill valid on the window (its core meets a pin core of half-side
1/2 - 9/400, and those cores lie inside the dilated pins for every m in (3.82, s0] by B'); every other YES box is a
chain page, re-emitted by reemit270 as <id>_r270g4.

Priority (the order of the pass-1 queue): 1 = no G1 row at all (cover270 MISSING: open on EVERY slab today) and the
two s0-only pages (Y1117, Y0436); 2 = G1 rows ALIVE / FAIL (closed on G1 by a chain page kill or a ledger only);
3 = G1 PASS rows; 4 = G1 logic-kill rows (logic at 1e-2 but not at 9/400); 5 = anything else.

    python pop270.py      -> results/pop270_g4.json"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"))
G1_S0_ONLY = {"k5_16_interior_Y1117", "k5_16_interior_Y0436"}      # status270: closed only by pad-0 (s0-only) kills


def prio(st, nid):
    if nid in G1_S0_ONLY or st in (None, "MISSING"):
        return 1
    if st.startswith("row:ALIVE") or st.startswith("row:FAIL"):
        return 2
    if st == "row:PASS":
        return 3
    if st in ("row:logic kill", "logic"):
        return 4
    return 5


def main():
    import tree57 as T                                            # READ-ONLY (A57): build_children only
    cov = json.load(open(os.path.join(ATT, "results", "cover270.json"), encoding="utf-8"))["classes"]
    out = dict(pin_delta="9/400", params=dict(w=0.15, nth=8, cw=0.6, a_min=0.34, side="969271/250000"), classes={})
    for cls in ("k5_11", "k5_16"):
        g1 = {r["id"]: r for r in cov[cls]["children_list"]}
        kids, bad, slots, rect, grid = T.build_children(cls, "interior", 0.15, 8, 0.6, 0.34, pin_delta=9 / 400)
        if bad:
            raise SystemExit("A270: %d uncoverable boxes at pin_delta 9/400" % len(bad))
        pages, logic, other, no = [], [], [], None
        for k in kids:
            if k["kind"] == "NO":
                no = k["id"]
                continue
            b = k["box"]
            box = [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]
            r = g1.get(k["id"])
            same = bool(r) and all(abs(u - v) < 1e-12 for u, v in zip(r["box"] or [], box))
            st = r["status"] if same else None
            ent = dict(id=k["id"], box=box, pin=k.get("pin"), g1_status=st if same else ("id differs at 1e-2" if r else "no G1 child"),
                       prio=prio(st, k["id"]), trim_excluded=[list(e) if isinstance(e, (list, tuple)) else str(e) for e in (k.get("trim_excluded") or [])])
            if k.get("pin") == "contradictory":
                logic.append(ent)
            elif k.get("pin") == "ok":
                pages.append(ent)
            else:
                other.append(ent)
        pages.sort(key=lambda e: (e["prio"], e["id"]))
        out["classes"][cls] = dict(no_child=no, n_children=len(kids), pages=pages, logic=logic, other=other,
                                   prio_counts={p: sum(1 for e in pages if e["prio"] == p) for p in (1, 2, 3, 4, 5)})
        print("%s: %d children -> NO child %s; %d chain pages %s; %d logic kills at 9/400; %d other" % (
            cls, len(kids), no, len(pages), out["classes"][cls]["prio_counts"], len(logic), len(other)))
    json.dump(out, open(os.path.join(ATT, "results", "pop270_g4.json"), "w", encoding="utf-8"), indent=0)


if __name__ == "__main__":
    main()
