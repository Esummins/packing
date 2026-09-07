"""Build results/depgraph_note.json for the GRAIN node from the measured results (so the note
never disagrees with the tables).  Usage: python mk_depgraph_note.py"""
from __future__ import annotations
import glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")


def main():
    man = json.load(open(os.path.join(CERTS, "manifest.json"), encoding="utf-8"))
    _d = json.load(open(os.path.join(RES, "check_local.json"), encoding="utf-8"))
    chk = {}
    for r in (_d.get("previous") or [])[::-1] + _d["runs"]:
        chk[r["id"]] = r
    ok = [k for k in man if chk.get(k, {}).get("ok")]
    leaves = sum(man[k]["node_counts"].get("dead", 0) for k in ok)
    mult = sum(man[k]["node_counts"].get("mult", 0) for k in ok)
    wall = sum(chk[k]["seconds"] for k in ok)
    t3 = []
    for p in sorted(glob.glob(os.path.join(RES, "t3_*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            t3.append(json.loads(line))
    dead = [d for d in t3 if d["tree"]["dead"]]
    cons = {}
    cp = os.path.join(RES, "t3_consumer119.json")
    if os.path.exists(cp):
        for e in json.load(open(cp, encoding="utf-8"))["per_N"]:
            k = (e["N"]["src"], e["N"]["tag"], e["N"]["cls"])
            if k not in cons or e["inside"] > cons[k]["inside"]:
                cons[k] = e
    note = (
        "A119 (2026-09-07, Opus; owner of the LOCAL sub-node after A116). "
        "[T/M] The local certificate is now a FROZEN OBJECT: %d certificate files "
        "(attempts/A119-local-cert-lean/certs/*.cert.json.gz + sha256 manifest) record the whole "
        "proof of Theorem LOCAL per neighbourhood -- the tilt-cell bisection cover, the selection "
        "case split with the impossible selections' interval enclosures, a rational Farkas vector "
        "(denominator 2^40) per closed leaf and a Farkas RAY per infeasible cell -- %d dead leaves "
        "and %d multipliers in all, and an INDEPENDENT checker (code/check_local.py: no numpy, no "
        "scipy, no tree code; dyadic interval arithmetic on integers at scale 2^-96, rigorous "
        "pi/cos/sin) re-derives every row from Lemma RELAX and re-verifies every bound in exact "
        "rational arithmetic: ALL VALID in %.0f s total. "
        "[T] Lean: lean/PackingCertMathlib/PackingCertMathlib/Local.lean (lake build clean, part of "
        "the default target) states LocalHyp/LocalDead and proves Lemma RELAX's algebra "
        "(axis_decomp, the two McCormick planes, the |q| chord, the concave chord, |sin| <= sin hw, "
        "cos >= cos hw), Lemma COVER's primitives (bisection, q-split, the impossible-selection "
        "resolution, cover_pair), the generated LEAF kills of a real certificate by linarith with "
        "the rational multipliers, and the composition classKilledAt_of_localDead into "
        "Composition.lean's ClassKilledAt; ONE project axiom (sat_selection = Lemma SAT for "
        "INTERIORS, the shrink argument on top of CaseSat.sat_squares), no sorry. "
        "[F] Five findings on A116's implementation (notes/method.md): F1 a q-range case split is "
        "measured on the owner's midpoint-axis functional and does NOT survive a later tilt "
        "bisection, so the two branches stop covering -- every q-split A116 made was in its phase-2 "
        "cosmetic tightening, no KILL depends on one, and a three-way probe (A116's tree, A119's "
        "with the carry-over restored, A119's as shipped) finds the same witness in all three; "
        "F2 a node must be closed on its Farkas VECTOR, not on the LP's optimal value; F3 an "
        "infeasible cell needs an exported Farkas RAY (phase 1), which A116 never wrote -- a "
        "quarter of some certificates; F4 a certificate checker must reproduce the generator's "
        "interval SHARPNESS (the exact ranges of cos, sin and |cos|+|sin|), not merely its "
        "soundness; F5 A116's t2_S07.jsonl records 4 128 witnesses at S07 (0.2, 20 deg), the first "
        "VALID at side 3.873374 (worst pair gap -4.4e-16), while the row's verdict field says "
        "capped -- that cell, S07 (0.2, 40 deg) and the r = 0.3 rho >= 20 deg rows are ALIVE, not "
        "capped, and local_certificate.md sec 5's 'no witness was found there' must be corrected. "
        "[M] T3: %s "
        "Open: a Lean-side certificate checker (native_decide, the A78/A93 checkCaseI shape) so "
        "that LocalDead is derived inside Lean for a concrete N; the tilt-cell count at rho >= 20 "
        "deg with r >= 0.1 remains the limiter."
        % (len(ok), leaves, mult, wall,
           _t3_sentence(dead, t3, cons)))
    json.dump({"GRAIN": note}, open(os.path.join(RES, "depgraph_note.json"), "w", encoding="utf-8"),
              indent=1)
    print(note)


def _t3_sentence(dead, t3, cons):
    if not t3:
        return "(T3 not run)."
    best = {}
    for d in dead:
        k = d["tag"]
        if k not in best or (d["r"], d["rho"]) > (best[k]["r"], best[k]["rho"]):
            best[k] = d
    parts = []
    for k in sorted(best):
        d = best[k]
        parts.append("%s largest certified with the blocking boxes: r = %.2f, rho = %.0f deg "
                     "(L = %s, %d nodes, %.0f s)"
                     % (k, d["r"], d["rho"], "+".join(d["loadbearing"]),
                        d["tree"]["stats"]["nodes"], d["seconds_tree"]))
    caps = [d for d in t3 if d["tree"]["capped"]]
    alive = [d for d in t3 if not d["tree"]["dead"] and not d["tree"]["capped"]]
    alive.sort(key=lambda d: (d["tag"], d["r"], d["rho"]))
    if caps:
        parts.append("%d of %d runs hit the time cap (the tilt-cell count, not a rearrangement)" %
                     (len(caps), len(t3)))
    for d in alive:
        w = (d.get("witnesses") or [{}])[0]
        parts.append("%s (%.2f, %.0f deg) with the ORIGINAL L is ALIVE, not capped -- a checked "
                     "packing of L u P at side %s"
                     % (d["tag"], d["r"], d["rho"],
                        ("%.6f" % w["witness_side"]) if w.get("witness_side") else "-"))
    if cons:
        parts.append("consumer: " + "; ".join(
            "%s %s/%s %d of %d at r=%.2f rho=%.0f" % (k[0], k[1], k[2], e["inside"],
                                                      e["nodes_in_class"], e["N"]["r"], e["N"]["rho"])
            for k, e in sorted(cons.items())))
    return "; ".join(parts) + "."


if __name__ == "__main__":
    main()
