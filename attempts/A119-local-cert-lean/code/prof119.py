"""A119 scratch: profile one A116 tree run to find the hot spot (read-only on A116)."""
from __future__ import annotations
import cProfile, os, pstats, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "A116-local-selection-tree", "code"))
import a116lib as A


def run(r=0.1, rho=5.0):
    bodies, nv, s_sh, P = A.build_bodies("S02", "k5_11", r, rho)
    _, Pe, _, _ = A.anchored("S02", s_sh)
    ss = A.shadow_selections(bodies, Pe)
    T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=2000000,
               time_cap=300.0, target=A.S0, tighten_cap=0)
    v = T.run()
    print(v["dead"], v["stats"]["nodes"], v["certified_min"], v["seconds"])


if __name__ == "__main__":
    cProfile.run("run()", os.path.join(HERE, "..", "logs", "prof.out"))
    p = pstats.Stats(os.path.join(HERE, "..", "logs", "prof.out"))
    p.sort_stats("cumulative").print_stats(28)
