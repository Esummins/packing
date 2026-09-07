"""A112 -- assemble results/depgraph_note.json (the one-line GRAIN note) from the measured t3.json.

Nothing here computes: every number is read back out of results/t3<run>.json and
results/canaries.json so the note cannot drift from the measurement.
"""
from __future__ import annotations

import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L

t3 = L.jload(os.path.join(L.RES, "t3%s.json" % L.SUF))
try:
    can = L.jload(os.path.join(L.RES, "canaries.json"))
except Exception:
    can = {}


def sec(rset):
    a = t3["sets"].get(rset) or {}
    if not a:
        return None
    h = t3["head_to_head"].get(rset) or {}
    parts = []
    for o, g in a.items():
        parts.append("%s %d nodes / %d LP / %.0f s LP / %.0f s cert / %d certified kills "
                     "(%d logic, %d chain)"
                     % (o, g["nodes"], g["lps"], g["lp_wall"], g["cert_wall"],
                        g["leaf_kills"]["cert"], g["leaf_kills"]["logic"],
                        g["leaf_kills"]["chain"]))
    g0 = next(iter(a.values()))
    ot = g0["old_tree"]
    return dict(rset=rset, per_ordering="; ".join(parts),
                old_tree="old tree projected %.0f nodes / %.0f LP / %.0f s" % (ot["nodes"],
                                                                              ot["lps"],
                                                                              ot["wall_s"]),
                wins=h.get("wins"), informative=h.get("informative"),
                regions=h.get("regions"))


out = {}
bits = []
for rset in ("s02", "k0"):
    s = sec(rset)
    if s:
        out[rset] = s
        bits.append("[%s, %s of %s regions informative] %s; %s; wins %s"
                    % (rset, s["informative"], s["regions"], s["per_ordering"], s["old_tree"],
                       s["wins"]))
corr = {k: (v or {}).get("wastage_vs_rowmass") for k, v in (t3.get("correlations") or {}).items()}
out["wastage_vs_rowmass"] = corr
out["canaries"] = dict(
    trump_ok=all((t3["canaries"].get(r) or {}).get("trump_ok", True) for r in ("s02", "k0")),
    resample=can.get("resample"), a111=can.get("a111_reproduction"))

note = ("A112 (dual-guided branching, region tree, four orderings measured): " +
        " || ".join(bits))
out["GRAIN"] = note
L.jdump(os.path.join(L.RES, "depgraph_note.json"), out)
print(note[:3000])
