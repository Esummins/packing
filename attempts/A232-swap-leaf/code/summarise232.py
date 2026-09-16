"""A232 -- results/swapleaf232.md from results/swapleaf232.jsonl (stdlib only, no search)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
JS = os.path.join(BASE, "results", "swapleaf232.jsonl")
MD = os.path.join(BASE, "results", "swapleaf232.md")

HEAD = """# A232 -- the SWAP leaf on the eleven converged-alive k0_00 cells

The leaf, its soundness and what it closes: `docs/proofs/swap_leaf.md`.  Verifier
`code/verify_swap232.py` (`swap-leaf-certificate-v1`, stdlib + exact Fractions, a NEW file --
the frozen `verify_case.py` / `verify_case_v4.py` are untouched).  Lean
`lean/.../Statements/SwapLeaf.lean` (`swap_leaf_dead`, a theorem from `cells_swap` + k1-a).
Resume: `bash attempts/A232-swap-leaf/code/run232.sh`.

`need` = |X| = the number of unit cells the leaf must place at that corner (every UNBOXED role
is forced into X -- its reach set is the whole container -- plus every boxed role whose reach
meets the corner slot).  `found` = the best family the search placed and the verifier's exact
tests accepted.  A row is DEAD only on a `verify_swap232` PASS.
"""


def main():
    rows = [json.loads(ln) for ln in open(JS, encoding="utf-8")]
    real = [r for r in rows if not r["node"].startswith("control")]
    ctrl = [r for r in rows if r["node"].startswith("control")]
    o = [HEAD, "", "## The cells", "",
         "| cell | n | boxed roles | unboxed | need (min over corners) | found (best) | best corner |"
         " split children / best | verdict | s |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in real:
        cs = r["corners"]
        best = max(cs, key=lambda c: (c["found"], -c["need"]))
        sp = r.get("split") or {}
        o.append("| `%s` | %d | %s | %d | %d | %d | %s | %s | %s | %.0f |" % (
            r["node"], r["n"], ", ".join(r["boxed"]) or "none", len(r["unboxed"]),
            min(c["need"] for c in cs), max(c["found"] for c in cs), best["corner_name"],
            ("%d / %d" % (sp.get("children", 0), sp.get("best_found", 0))) if sp else "-",
            r["verdict"], r["wall_s"]))
    o += ["", "## Per corner (need / found; reach area of the roles outside X inside [0, 3.82]^2)", "",
          "| cell | BL | BR | TR | TL | roles outside X | reach area |", "|---|---|---|---|---|---|---|"]
    for r in real:
        cs = {c["corner_name"]: c for c in r["corners"]}
        o.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (
            r["node"],
            *["%d / %d" % (cs[k]["need"], cs[k]["found"]) for k in ("BL", "BR", "TR", "TL")],
            ", ".join(cs["BL"]["outside"]) or "none",
            ", ".join("%s %.3f" % (k, v) for k, v in cs["BL"]["blocked_area"].items()) or "-"))
    if ctrl:
        o += ["", "## Controls (n = 5 -- the geometry and the verifier end to end)", "",
              "An |X| = 2 control CANNOT exist at n = 11 inside the window: a passing leaf there is",
              "exactly the theorem s(11) >= s-hat.  The controls are therefore stated at n = 5 and",
              "carry NO k1-a claim.", "",
              "| control | |X| | cells found | verifier |", "|---|---|---|---|"]
        for r in ctrl:
            c0 = r["corners"][0]
            o.append("| `%s` | %d | %d | %s |" % (r["node"], c0["need"], c0["found"],
                                                  c0.get("verified", "-")))
    n_dead = sum(1 for r in real if r["verdict"].startswith("DEAD"))
    o += ["", "## Verdict", "",
          "**%d of %d cells DEAD by SWAP-LEAF.**  %s" % (
              n_dead, len(real),
              "k0_00 is closed by certificates." if n_dead == len(real) else
              "The leaf does not fire on any of them, and the reason is structural, not a search "
              "failure: the k0v4 cells box ONE of the eleven squares, so ten roles are unboxed and "
              "every one of them must go into X.  |X| = 10 asks for a ten-square packing of "
              "[0, 3.82]^2 (s(10) = 3.7071, slack 0.113) with one member at the corner slot and all "
              "of them avoiding the conditioned square's reach set -- see docs/proofs/swap_leaf.md "
              "s.3 for the price of getting |X| down to the PI's 2."), ""]
    open(MD, "w", encoding="utf-8").write("\n".join(o))
    print("wrote", MD, "(%d cells, %d dead)" % (len(real), n_dead))


if __name__ == "__main__":
    main()
