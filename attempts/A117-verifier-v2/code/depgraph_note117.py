"""A117 -- the depgraph note on the verifier node V.PARAM (and the TC leaf's home), written as a
standalone record beside the live copy in lean/depgraph.json.  Read-only elsewhere."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))


def main():
    acc = json.load(open(os.path.join(RES, "accounting.json")))
    t1, t2 = acc["t1"], acc["t2"]
    eq, rv = t1["equivalence"], t1["reverify"]
    note = {
        "attempt": "A117-verifier-v2",
        "date": "2026-09-06",
        "nodes": {
            "V.PARAM": {
                "change": "NO-families added, as a NEW verifier version",
                "v1_sha256": eq["v1_sha256"],
                "v2_sha256": eq["v2_sha256"],
                "v1_untouched": True,
                "lean": ("lean/PackingCertMathlib/PackingCertMathlib/ParamNoFam.lean: PNoFam, "
                         "cellNoFam (= SCell.nofams_iv), nofamExemptIV (= CaseI.nofamExempt on "
                         "the s-cell worst-case zone), exemptPN (= v2's PVerifier.exempt); "
                         "exemptPN_nil (equivalence with v1) and nofamExemptIV_sound PROVED, "
                         "axioms propext/Classical.choice/Quot.sound only"),
                "equivalence": {
                    "certificates": eq["n"], "identical": eq["identical"],
                    "contract": json.load(open(os.path.join(RES,
                                                            "equivalence.json")))["contract"]},
                "reverification": {k: rv[k] for k in
                                   ("n", "by_result", "window_valid_kills_gained",
                                    "fixed_PASS_now_window_FAIL", "capped",
                                    "window_wall_s", "four_side_wall_s",
                                    "ratio_window_over_four_sides")},
                "open": ("the YES side stays s0-only: a YES branch core is neither a slot nor a "
                         "Q_dy cover coordinate, so A96's core_affine refuses it (3 of 77 "
                         "certificates); a region-tree kill whose tree has a YES child cannot be "
                         "claimed window-valid until a YES-core anchoring exists")
            },
            "C.T5T11": {
                "change": ("Lemma TC named as a leaf: exact rational check "
                           "(attempts/A117-verifier-v2/code/tcleaf.py) + Lean STATEMENTS "
                           "TCSupportMin / TCCentreDist / TCLeaf / TCLeaf_of_TCCentreDist as "
                           "Props ([C], no new axioms)"),
                "replay": {k: t2[k] for k in
                           ("n_fires", "n_exact_fires", "n_not_reproduced",
                            "total_sampled_pairs", "samples_per_fire", "counterexamples",
                            "worst_sat_gap", "min_exact_slack", "by_kind")},
                "open": ("the Lean proof needs the separating-axis theorem for two "
                         "interior-disjoint convex polygons, which Band.lean records as not "
                         "formalised in this development -- so TC is [C] (exact machine check "
                         "with a 10^4-sample control), not a Lean theorem")
            }
        },
        "emission_nondeterminism": (
            "certify.py --loop_cols re-solves the node LP under a time limit before emitting, so "
            "a certificate's atom set is wall-clock dependent -- the frozen VERIFIER is "
            "deterministic, the EMISSION is not; kills are reproduced by replaying certificates, "
            "never by re-emitting.")
    }
    json.dump(note, open(os.path.join(RES, "depgraph_note.json"), "w"), indent=1)
    print(json.dumps(note, indent=1))


if __name__ == "__main__":
    main()
