"""A212 (fold211 adapted) -- fold every DEAD page verdict (pad 0, lam = 1: the s0 currency of A60's own certificates) into the A60
closure bookkeeping: results/superseded_by_trump5tree_A212.jsonl, one row per killed trump5 node in the supersession-ledger
format A137 / A149 use (id, camp A60, applies_to_tags ['trump5_j0'], prior verdict retained, superseded_by / leaf / cert /
source, recorded).  TRUMP-TUBE verdicts are NOT folded (not kills).  A60's own files are never written.
    python fold212.py                 # rebuild the ledger from results/trump5tree212.jsonl
    python fold212.py --closed <nid>  # exit 0 iff the node is already closed by an A60 ledger (A149 / A137 / this one)"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load212 as L                                            # noqa: E402

RES = os.path.join(HERE, "..", "results", "trump5tree212.jsonl")
LEDGER = L.LEDGER


def kills():
    out = {}
    for d in L.jl(RES):
        if d.get("mode") == "page" and d.get("verdict") == "DEAD" and d.get("nid"):
            out[d["nid"]] = d
    return out


def rebuild():
    first, _ = L.a60_rows()
    rows = []
    for nid, d in sorted(kills().items()):
        r = first.get(nid, {})
        rows.append(dict(id=nid, nid=nid, level=1 + int(r.get("depth_j") or 0), cls="trump5", camp="A60", prior_verdict=str(r.get("verdict")), prior_tau=r.get("tau"),
                         superseded_by="A212 trump5 tree (A211's coarse tree at pad 0 + the Trump-containment gate + the tube leaf; notes/trump5_tree.md) at s0, lam = 1",
                         leaf=("stage 0: %s" % d.get("leaf")) if d.get("stage0_kill") else str(d.get("leaf") or "")[:400],
                         cert=d.get("cert"), source="A212-trump5-tree/results/trump5tree212.jsonl", already_dead=False, applies_to_tags=["trump5_j0"], not_applicable_to_tags=[],
                         kills_by_rule=d.get("kills_by_rule"), gate_hits=d.get("gate_hits"), verifier=d.get("verifier"), recorded=d.get("when") or time.strftime("%Y-%m-%d %H:%M:%S"),
                         note="prior verdict RETAINED; an s0-only kill (lam = 1) in the currency of A60's own s0 certificates; [C: closed-form / library clip trace + the leaf lemma], no verifier clause"))
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")
    return rows


def closed(nid):
    return nid in L.a60_ledger_dead()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--closed":
        sys.exit(0 if closed(sys.argv[2]) else 1)
    rows = rebuild()
    print("ledger: %d kills" % len(rows))
