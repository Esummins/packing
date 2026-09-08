"""A151 -- the survivor-count rule at scale for a spec, with NO tree run (A116's sample_check).

    python sample151.py --spec results/spec_B.json --n 100000 --seed 4242

drawn -> tested (all near pairs disjoint) -> hits (a packing of L u P at side <= s0).
A hit would be a counterexample to the certificate.  READ-ONLY on every campaign.
"""
from __future__ import annotations
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
sys.path.insert(0, HERE)
import a116lib as A     # noqa: E402
import a151grow as G    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--n", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--starts", type=int, default=40)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "sample151.json"))
    a = ap.parse_args()
    spec = G.base_spec()
    spec.update(json.load(open(a.spec, encoding="utf-8")))
    bodies, nv, s_sh, P = G.bodies_for(spec)
    t0 = time.time()
    samp = A.sample_check(bodies, nv, n_samples=a.n, seed=a.seed)
    lm = A.local_min(bodies, nv, starts=a.starts, seed=7)
    tr = A.trump_in_N(bodies, pin_slack=A.PIN_SLACK)
    rec = dict(spec=spec, boxes=G.boxlist(spec), sampling=samp, local_min=lm, trump=tr,
               seconds=round(time.time() - t0, 1), s_shadow=s_sh, s0=A.S0)
    prev = []
    if os.path.exists(a.out):
        prev = json.load(open(a.out, encoding="utf-8"))
    prev.append(rec)
    json.dump(prev, open(a.out, "w", encoding="utf-8"), indent=1)
    print("spec %s: drawn %d -> tested %d -> HITS %d ; SLSQP box-min side %.6f (s0 %.6f, s* %.6f); "
          "Trump inside N: %s ; %.0f s"
          % (os.path.basename(a.spec), samp["n_samples"], samp["free_pairs_disjoint"], samp["hits"],
             lm["side"], A.S0, s_sh, tr["inside"], rec["seconds"]))
    if samp["examples"]:
        print("EXAMPLES (counterexamples!):", json.dumps(samp["examples"][:2])[:600])


if __name__ == "__main__":
    main()
