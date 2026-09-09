"""A175 -- cascade168 / coex174 with the POLYGON clip: every `roles168.make_node` call the step
runner, the coexistence cut and the piece-level cut make is routed to `polyclip175.make_node`
(A171 polygon obstacles, per-piece K', A173 lonely clip at every pass, roles168's own K'/axis
rebuild + invariant + OVL as the cross-check).  Nothing else in cascade168 / coex174 changes: the
covers, the R3/R1 prefilters, the labelling prune, the shard/merge bookkeeping and the per-node
wall are theirs.

    python cascade175.py s4 --cell l1_104 --parents all --shard 0/3      (any cascade168 stage)
    python cascade175.py coexcut --cell l1_104 --step S3 --bisect 1 ...  (coex174 `cut`)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import roles168 as R                                             # noqa: E402
import polyclip175 as PX                                         # noqa: E402

REFINE = int(os.environ.get("A175_REFINE", "2"))


def make_node_poly(roles, nsub=4, passes=8):
    """drop-in for roles168.make_node (same signature, same (roles|None, report) contract; the
    report additionally carries leaf / cert / kept_mb / k_area)."""
    return PX.make_node(roles, refine=REFINE)


R.make_node = make_node_poly                                    # every caller reads R.make_node at call time


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "coexcut":
        sys.argv = [sys.argv[0], "cut"] + sys.argv[2:]
        import coex174 as CX
        CX.main()
    else:
        import cascade168 as CS
        CS.main()


if __name__ == "__main__":
    main()
