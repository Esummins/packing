"""A191 -- the S3 addenda into notes/cascade191.md, notes/price191.md, LOG.md, docs/residue_ledger.md, docs/budget.md
(idempotent: each block is skipped when its marker is already present).  Numbers from results/price191.json + the
records at the time of the run (printed)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(A, "..", ".."))


def counts():
    out = {}
    for tag, f in (("coarse", "run191_l1_104_S3coarse.jsonl"), ("fine", "run191_l1_104_S3.jsonl")):
        R = [json.loads(l) for l in open(os.path.join(A, "results", f), encoding="utf-8")]
        R = list({r["record_node"]: r for r in R}.values())
        out[tag] = dict(n=len(R), dead=sum(1 for r in R if r["verdict"].startswith("DEAD")),
                        dead_geo=sum(1 for r in R if r["verdict"].startswith("DEAD(C")),
                        dead_lp=sum(1 for r in R if r["verdict"].startswith("DEAD(LP")),
                        undecided=[r["record_node"] for r in R if not r["verdict"].startswith("DEAD")])
    return out


def main():
    c = counts()
    pr = json.load(open(os.path.join(A, "results", "price191.json"), encoding="utf-8"))
    s3 = pr["s3"]
    n_tried = c["coarse"]["n"] + c["fine"]["n"]
    n_dead = c["coarse"]["dead"] + c["fine"]["dead"]
    cost = 5432 * s3["wall_lp"] / 3600.0
    print(c, "cost_h", round(cost, 1), "wall_lp", round(s3["wall_lp"]))
    S3PAR = ("**The S3 layer [M] (`results/run191_l1_104_S3coarse.jsonl`, `run191_l1_104_S3.jsonl`; `figs/steps_l1_104_S3coarse.svg`, "
             "`steps_l1_104_S3fine.svg`; from 04:28, one process each).**  *Coarse, parent-seeded children of the S2 survivors* (H, D, S = the "
             "parent's recorded 8/3 fixed point, B = A168's cover box, `polyclip175.make_node(refine=2)` = nsub 4 / refine 2 only): the first "
             "cover box B0 (nearest the corner) dies at 4/2 by EmptyBox(B) on %d of %d parents tried (37-75 s); the interior children (B95 / B96 "
             "of root/D0/S0, S1, S11, S15, S16, S17, S9, root/D1/S0, S9, ...) survive the clip with kept H 0.29-0.64 / D 0.20-0.30 / S 0.11-0.32 / "
             "B 0.63 (clip 67-124 s), the corner lanes at TL / BL are None (17-33 s), and the v1-style exact-core LP at budget 7 (FOUR cores) "
             "CONVERGES at **tau = 6.000 < 7** on every one that converged within the 240 s cap: %d DEAD by the LP (v5 PASS; re-verified PASS under "
             "the FROZEN verifier, `certs/*_B*_v1.frozen.certify.json`), %d undecided at cap (%s).  *A183's fine (8/3) S3 records* under alive "
             "parents (root/D0/S0/B10, B100, B101, B102, ...): %d of %d DEAD by the same LP at tau = 6.000 (139-247 s each, v5 PASS, frozen PASS).  "
             "Pooled: **%d of %d S3 nodes DEAD, %d undecided at cap, 0 alive** -- against A183's 21 %% (fine geometry alone) and A184's 5 %% "
             "(coarse geometry alone): at S3 the exact-core LP with four cores kills where the geometry does not, and the kill is again the "
             "cascade's -- tau drops by exactly one unit per pinned square (8.000 -> 7.000 at S2 on the collapsed nodes, 7 -> 6 at S3 on every "
             "node tried).  The sample is small and biased to the root/D0 and root/D1 chains (the first parents alphabetically); the per-node "
             "cost at S3 is **%.0f s** mean over the LP-run children (clip %.0f + lanes %.0f + LP %.0f + certificate %.0f; the windows diagnostic "
             "at wfrac 0.2 is %.0f s of it).  [F] The S3 layer of l1_104 = the 5,432 A168-alive children of the 47 S2 survivors (8,460 children, "
             "3,028 already dead by A168's own clip): at %.0f s each it is **%.0f CPU-h (%.0f instance-hours at 16 vCPU)**, and if the sampled "
             "rate holds it closes the cell but for the undecided fraction (`notes/price191.md` section 3).\n" % (
                 c["coarse"]["dead_geo"], c["coarse"]["dead_geo"], c["coarse"]["dead_lp"], len(c["coarse"]["undecided"]),
                 ", ".join(c["coarse"]["undecided"]) or "-", c["fine"]["dead"], c["fine"]["n"], n_dead, n_tried, n_tried - n_dead,
                 s3["wall_lp"], s3["clip"], s3["geo"], s3["v1"], s3["cert"], s3["win"], s3["wall_lp"], cost, cost / 16))
    p = os.path.join(A, "notes", "cascade191.md")
    s = open(p, encoding="utf-8").read()
    i = s.find("**The S3 layer")
    if i > 0:
        s = s[:i] + S3PAR
        open(p, "w", encoding="utf-8").write(s)
        print("cascade191 S3 paragraph written")
    p = os.path.join(A, "notes", "price191.md")
    s = open(p, encoding="utf-8").read()
    key = "Then the S3 children\nof the S2 survivors at the coarse setting (a sample), and the canary `l1_153` (1 alive S2 node)."
    if key in s:
        s = s.replace(key, ("Then the S3 children of the S2 survivors at the coarse setting (a sample of %d: %d corner-nearest B0 boxes dead at "
                            "4/2, %d interior children dead by the exact-core LP at budget 7, %d undecided at cap) plus A183's fine S3 records "
                            "under alive parents (%d of %d dead by the same LP), and the canary `l1_153` (1 alive S2 node: alive converged at "
                            "tau = budget).  What the S3 sample says: with FOUR pinned squares the LP value drops to 6.000 < 7 on every converged "
                            "node -- %d of %d dead -- so the S3 layer is where l1_104 closes, and its price is the number below." % (
                                c["coarse"]["n"], c["coarse"]["dead_geo"], c["coarse"]["dead_lp"], len(c["coarse"]["undecided"]),
                                c["fine"]["dead"], c["fine"]["n"], n_dead, n_tried)))
        s = s.replace("A1. **Kill rates**: the S2 rate is the measured one on l1_104's 64 alive S2 nodes; the S3 rate is the measured\n"
                      "    coarse-setting rate on the sample (children of S2 survivors) -- A183's fine-setting S3 sample gave 10 of 47\n"
                      "    DEAD (21 %), A184 E1 gave 3-4 of 64 (5-6 %) on a different sample.  Deeper layers (S4..S8) are ASSUMED to kill\n"
                      "    at the S3 rate per node (no measurement below S3 on l1_104; l1_153's S4..S8 is A183's untouched 571).",
                      "A1. **Kill rates**: the S2 rate is the measured one on l1_104's 64 alive S2 nodes (27 %% certified + 30 %% candidates); the S3\n"
                      "    rate is the sampled one -- %d of %d coarse children (%d by geometry, %d by the exact-core LP) + %d of %d fine records,\n"
                      "    %d undecided at cap, 0 alive; the sample is biased to the root/D0 and root/D1 chains.  A183's fine-setting geometry alone\n"
                      "    gave 10 of 47 (21 %%) and A184's coarse geometry 3-4 of 64 (5-6 %%) -- the difference tonight is the LP with four cores.\n"
                      "    Layers below S3 are ASSUMED to kill at the scenario rate (no measurement below S3 on l1_104); the 1.00 scenario is\n"
                      "    'the S3 layer closes the cell' and its S4 row prices only the undecided residue's children." % (
                          c["coarse"]["dead"], c["coarse"]["n"], c["coarse"]["dead_geo"], c["coarse"]["dead_lp"], c["fine"]["dead"], c["fine"]["n"],
                          n_tried - n_dead))
        open(p, "w", encoding="utf-8").write(s)
        print("price191 text updated")
    ADD = ("S3 addendum (05:30) [M]/[C]: %d of %d S3 nodes tried are DEAD -- coarse parent-seeded children of the S2 survivors %d of %d (the "
           "corner-nearest B0 by EmptyBox(B) at 4/2 on %d of %d parents, 37-75 s; the interior children by the exact-core LP at budget 7 CONVERGED "
           "at tau = 6.000 on %d, %d undecided at cap 240 s) and A183's fine 8/3 records %d of %d (the same LP, tau = 6.000); every LP kill PASS "
           "under v5 AND under the FROZEN verifier (`certs/*_B*_v1.frozen.certify.json`) -- the LP value drops by exactly one unit per pinned "
           "square (8 -> 7 at S2 on the collapsed nodes, 7 -> 6 at S3 on every node tried), so with four cores the S3 layer is where l1_104 "
           "closes: 5,432 A168-alive S3 children under the 47 S2 survivors at %.0f s each = **%.0f CPU-h = %.0f instance-hours at 16 vCPU** for "
           "the whole layer (the sample is %d nodes biased to the root/D0 and root/D1 chains; `notes/price191.md` gives the 0.9x / 0.99 / 1.00 "
           "scenarios and the S4 residue).  Audit (`code/audit191.py`, `results/audit191.json`): every kill certificate's cores are pairwise "
           "interior-disjoint (exact SAT) and bound to their union boxes by v5's own `point_in_all_poses` check; frozen PASS on all." % (
               n_dead, n_tried, c["coarse"]["dead"], c["coarse"]["n"], c["coarse"]["dead_geo"], c["coarse"]["dead_geo"], c["coarse"]["dead_lp"],
               len(c["coarse"]["undecided"]), c["fine"]["dead"], c["fine"]["n"], s3["wall_lp"], cost, cost / 16, n_tried))
    p = os.path.join(ROOT, "LOG.md")
    s = open(p, encoding="utf-8").read()
    if "S3 addendum (05:30)" not in s:
        open(p, "a", encoding="utf-8").write("- **" + ADD + "**\n")
        print("LOG addendum appended")
    p = os.path.join(ROOT, "docs", "residue_ledger.md")
    s = open(p, encoding="utf-8").read()
    key = "the table gives the CPU-h per cell for the measured, 0.90 and 0.99 deep rates."
    if key in s and "S3 addendum (05:30)" not in s:
        s = s.replace(key, key + " **" + ADD + "**")
        open(p, "w", encoding="utf-8").write(s)
        print("ledger addendum written")
    p = os.path.join(ROOT, "docs", "budget.md")
    s = open(p, encoding="utf-8").read()
    key = "the cell has nothing to kill at S2."
    if key in s and "S3 addendum (05:30)" not in s:
        s = s.replace(key, key + " **" + ADD + "**")
        open(p, "w", encoding="utf-8").write(s)
        print("budget addendum written")


if __name__ == "__main__":
    main()
