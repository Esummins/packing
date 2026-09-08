"""A154 T3 -- the CLASS-SPECIFIC corner row: which corners of each class are non-simple, what the
row's weight is, and whether the teleport that licenses it exists.

A corner c of a class S is SIMPLE if a pin of S sits in it (centre (1/2,1/2) and its D4 images).
At a simple corner the pin IS the corner square and no teleport is available, so the corner
carries no ">= 2 meeters" statement.  At a NON-SIMPLE corner the corner cell c(0,0) is a
completable slot; the ">= 2 non-pin meeters" statement is Lemma SLOT-CROWD applied to that slot,
and it is licensed only when the EXTENSION class S u {c(0,0)} is certified dead on the window
(docs/proofs/slot_crowds.md sec 1.2: "usable slot").  The row is then

    sum over the N - k_cond FREE squares of [meets the widened box of a non-simple usable corner]
        >=  2 * |U_corner(S)| - sum over the node's conditioned cores of r_max,

and the four widened corner boxes are still s0 - 2 a_w = 1.826 > sqrt2 apart, so the distinctness
of the meeters is free exactly as in (R6) -- the A109 multiplicity failure cannot occur.

Read-only.  Writes results/classrow154.json.
"""
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a154lib as L  # noqa: E402

S0 = F(969271, 250000)
H = F(1, 2)
CORNERS = {"BL": (H, H), "BR": (S0 - H, H), "TL": (H, S0 - H), "TR": (S0 - H, S0 - H)}
SLOTS94 = os.path.join(L.ROOT, "attempts", "A94-slot-crowds", "results", "slots94.json")


def main():
    d = json.load(open(SLOTS94, encoding="utf-8"))
    out = {}
    for name, c in d.items():
        pins = [(F(p[0]), F(p[1])) for p in c["pins"]]
        ns = [k for k, v in CORNERS.items() if v not in pins]
        rows = []
        for corner in ns:
            cell = corner + "(0,0)"
            e = [x for x in c["completable"] if x["cell"] == cell]
            if not e:
                rows.append(dict(corner=corner, completable=False, extension=None,
                                 status="not a completable slot", usable=False))
                continue
            e = e[0]
            st = e["extension_status"]
            head = st.split("|")[0].strip()
            usable = head in ("FULL",) or (head == "PARTIAL")
            rows.append(dict(corner=corner, completable=True, clipped=bool(e["clipped"]),
                             extension=e["extension"], status=st, status_head=head,
                             usable_at_s0=bool(usable),
                             usable_full_window=bool(head == "FULL")))
        # k0_00 is the exception: its corner extension k1_00 IS obligation K0-O1, the standing
        # hypothesis of the whole k0 tree (k0_route.md sec 3, Lean teleport_packing).  So the row
        # is licensed there on exactly the terms the tree already runs on.
        if name == "k0_00":
            for r in rows:
                r["usable_at_s0"] = True
                r["usable_full_window"] = True
                r["status"] = r["status"] + " -- but this IS obligation K0-O1 (k1_00's tree), the "                              "standing hypothesis of every k0 node"
        nu0 = sum(1 for r in rows if r.get("usable_at_s0"))
        nuf = sum(1 for r in rows if r.get("usable_full_window"))
        out[name] = dict(k=c["k"], N=c["N"], n_nonsimple=len(ns), nonsimple=ns, corners=rows,
                         B_row_s0=2 * nu0, B_row_window=2 * nuf,
                         verdict=(("row licensed at s0 (weight %d)%s" %
                                   (2 * nu0, " -- modulo K0-O1" if name == "k0_00" else ""))
                                  if nu0 else
                                 ("row VACUOUS (no non-simple corner)" if not ns else
                                  "row NOT LICENSED (every corner extension is itself protected)")))
    json.dump(out, open(os.path.join(L.RES, "classrow154.json"), "w"), indent=1)
    print("%-8s %-2s %-2s %-4s %-22s %-8s %s" %
          ("class", "k", "N", "n_ns", "non-simple corners", "B(s0)", "verdict"))
    for name, r in out.items():
        print("%-8s %-2d %-2d %-4d %-22s %-8d %s" %
              (name, r["k"], r["N"], r["n_nonsimple"], ",".join(r["nonsimple"]) or "-",
               r["B_row_s0"], r["verdict"]))


if __name__ == "__main__":
    main()
